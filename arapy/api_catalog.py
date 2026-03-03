# arapy/api_catalog.py
from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from . import config



# Minimal static endpoints needed to obtain a token (login bootstrap).
# Your current dict has these already. :contentReference[oaicite:6]{index=6}
OAUTH_ENDPOINTS: dict[str, str] = {
    "oauth": "/api/oauth",
    "oauth-me": "/api/oauth/me",
    "oauth-privileges": "/api/oauth/privileges",
}


# Keep CLI compatibility with existing typos in api_endpoints.py (optional but recommended).
# Example typos exist today. :contentReference[oaicite:7]{index=7}
ALIASES: dict[str, str] = {
    "certiticate-reject": "certificate-reject",
    "onboard-debice": "onboard-device",
    "genereate-guest-receipt": "generate-guest-receipt",
    "essaging-setup": "messaging-setup",
    "statless-access-control-list": "stateless-access-control-list",
}


def _camel_to_kebab(name: str) -> str:
    # SystemEvents -> system-events, TokenEndpoint -> token-endpoint
    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1-\2", name)
    s2 = re.sub(r"([a-z0-9])([A-Z])", r"\1-\2", s1)
    return s2.replace("_", "-").lower()


def _clean_apigility_route(route: str) -> str:
    """
    Apigility routes look like:
      /login-audit[/:name]
      /insight/endpoint[/:mac]
    For your existing request patterns, we want a stable "base collection" path.
    """
    # Remove bracketed optional segments like [/:name]
    route = re.sub(r"\[.*?\]", "", route)
    return route.rstrip("/") or "/"


def _is_json_content(text: str) -> bool:
    t = text.lstrip()
    return t.startswith("{") or t.startswith("[")


def _extract_module_doc_paths_from_api_docs_html(html: str) -> list[str]:
    """
    Extract module roots from links like:
      /api-docs/Logs-v1
      /api-docs/PolicyElements-v1#!/NetworkDevice
    Return unique module doc URLs: /api-docs/<Module-v1>
    """
    modules = set()

    # Grab anything that looks like /api-docs/<something>-vN (with or without #!/...)
    for m in re.findall(r'(/api-docs/[A-Za-z0-9_-]+-v\d+)', html):
        modules.add(m)

    # Also handle cases where it appears without leading slash
    for m in re.findall(r'(api-docs/[A-Za-z0-9_-]+-v\d+)', html):
        modules.add("/" + m)

    return sorted(modules)


@dataclass(frozen=True)
class EndpointCacheConfig:
    ttl_seconds: int = 24 * 3600
    cache_filename: str = "api_endpoints_cache.json"


class ApiEndpointCache:
    def __init__(self, cp_client, *, token: str, cfg: EndpointCacheConfig | None = None):
        self.cp = cp_client
        self.token = token
        self.cfg = cfg or EndpointCacheConfig()

        cache_dir = Path(getattr(config, "CACHE_DIR", Path("./cache")))
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = cache_dir / self.cfg.cache_filename

    def get_api_paths(self, *, force_refresh: bool = False) -> dict[str, str]:
        if not force_refresh:
            cached = self._load_if_fresh()
            if cached:
                return cached

        api_paths = self._build_from_clearpass()
        self._save(api_paths)
        return api_paths

    def _load_if_fresh(self) -> dict[str, str] | None:
        try:
            st = self.cache_path.stat()
        except FileNotFoundError:
            return None

        age = time.time() - st.st_mtime
        if age > self.cfg.ttl_seconds:
            return None

        try:
            data = json.loads(self.cache_path.read_text(encoding="utf-8"))
            if isinstance(data, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
                return data
        except Exception:
            return None

        return None

    def _save(self, api_paths: dict[str, str]) -> None:
        tmp = self.cache_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(api_paths, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(tmp, self.cache_path)

    def _raw_get_text(self, path: str) -> str:
        """
        Uses the same server/SSL/session settings as your existing request() method :contentReference[oaicite:9]{index=9}
        but without needing api_paths.
        """
        base = self.cp.https_prefix + self.cp.server
        url = base + path

        headers = {
            "Accept": "application/json, application/vnd.swagger+json, */*",
            "Authorization": f"Bearer {self.token}",
        }
        resp = self.cp.session.get(url, headers=headers, verify=self.cp.verify_ssl, timeout=self.cp.timeout)
        resp.raise_for_status()
        return resp.text

    def _build_from_clearpass(self) -> dict[str, str]:
        """
        ClearPass /api/apigility/documentation/<Module-v1> often returns a Swagger 1.2 "resource listing":
            {"apiVersion": "...", "swaggerVersion": "...", "apis": [{"path": "/PolicyElements-v1/NetworkDevice", ...}, ...]}

        We must:
        1) discover modules from /api-docs
        2) fetch module listing JSON
        3) follow each listing apis[].path to fetch the sub-doc
        4) extract resource paths and build api_paths entries
        5) add OAuth endpoints + aliases
        """
        import json
        import re
        from typing import Any

        from .logger import AppLogger

        log = AppLogger().get_logger(__name__)

        def _clean_swagger_path(p: str) -> str:
            # "/network-device/{id}" -> "/network-device"
            p = re.sub(r"\{[^}]+\}", "", p)
            return p.rstrip("/") or "/"

        def _add_endpoint(api_paths: dict[str, str], key: str, route: str) -> None:
            key = key.strip()
            if not key:
                return
            base_route = _clean_apigility_route(route)

            if base_route.startswith("/api/"):
                api_paths[key] = base_route
            elif base_route.startswith("/"):
                api_paths[key] = "/api" + base_route
            else:
                api_paths[key] = "/api/" + base_route

        def _extract_modules_from_api_docs(text: str) -> list[str]:
            if _is_json_content(text):
                try:
                    data = json.loads(text)
                except Exception:
                    return []
                out: list[str] = []
                if isinstance(data, dict):
                    apis = data.get("apis")
                    if isinstance(apis, list):
                        for a in apis:
                            p = a.get("path")
                            if isinstance(p, str):
                                m = re.search(r"(/api-docs/[A-Za-z0-9_-]+-v\d+)", p)
                                if m:
                                    out.append(m.group(1))
                return sorted(set(out))
            else:
                # HTML API explorer
                return sorted(set(re.findall(r'(/api-docs/[A-Za-z0-9_-]+-v\d+)', text)))

        def _load_json(path: str) -> dict[str, Any] | None:
            try:
                text = self._raw_get_text(path)
            except Exception as e:
                log.debug("[api_catalog] fetch %s failed: %s", path, e)
                return None
            if not _is_json_content(text):
                return None
            try:
                parsed = json.loads(text)
            except Exception as e:
                log.debug("[api_catalog] parse %s failed: %s", path, e)
                return None
            return parsed if isinstance(parsed, dict) else None

        # --- Step 1: discover modules from /api-docs
        api_docs_text = self._raw_get_text("/api-docs")
        module_doc_paths = _extract_modules_from_api_docs(api_docs_text)

        log.info("[api_catalog] Discovered %d modules from /api-docs", len(module_doc_paths))
        if module_doc_paths:
            log.info("[api_catalog] First modules: %s", module_doc_paths[:10])

        api_paths: dict[str, str] = {}

        # --- Step 2: for each module, fetch the documentation listing and follow its apis[]
        for module_path in module_doc_paths:
            module_name = module_path.rsplit("/", 1)[-1]  # "PolicyElements-v1"

            # Primary: Swagger 1.2 resource listing
            listing_path = f"/api/apigility/documentation/{module_name}"
            listing = _load_json(listing_path)

            # Fallback to other candidates if needed
            if listing is None:
                for alt in (
                    f"/api/apigility/documentation/{module_name}/swagger",
                    module_path,
                    f"{module_path}.json",
                ):
                    listing = _load_json(alt)
                    if listing is not None:
                        listing_path = alt
                        break

            if listing is None:
                log.warning("[api_catalog] %s: no JSON docs found", module_name)
                continue

            added = 0

            # Case A: Apigility services[] (older file you shared had this)
            services = listing.get("services")
            if isinstance(services, list) and services:
                for svc in services:
                    if not isinstance(svc, dict):
                        continue
                    name = svc.get("name")
                    route = svc.get("route")
                    if isinstance(name, str) and isinstance(route, str):
                        key = _camel_to_kebab(name)
                        _add_endpoint(api_paths, key, route)
                        added += 1
                log.info("[api_catalog] %s: added %d endpoints (apigility services)", module_name, added)
                continue

            # Case B: Swagger 1.2 resource listing: keys apiVersion/swaggerVersion/apis
            apis = listing.get("apis")
            if isinstance(apis, list) and apis:
                # The listing's "apis[].path" can be absolute or relative.
                # We'll normalize it to a full path under /api/apigility/documentation/<Module-v1>/...
                for item in apis:
                    if not isinstance(item, dict):
                        continue
                    p = item.get("path")
                    if not isinstance(p, str):
                        continue

                    # Normalize:
                    # - sometimes p is "/NetworkDevice"
                    # - sometimes p is "/PolicyElements-v1/NetworkDevice"
                    # - sometimes p is already "/api/apigility/documentation/PolicyElements-v1/NetworkDevice"
                    if p.startswith("/api/"):
                        sub_path = p
                    elif p.startswith(f"/{module_name}/"):
                        sub_path = f"/api/apigility/documentation{p}"
                    elif p.startswith("/"):
                        # assume "/NetworkDevice" style
                        sub_path = f"/api/apigility/documentation/{module_name}{p}"
                    else:
                        sub_path = f"/api/apigility/documentation/{module_name}/{p}"

                    sub = _load_json(sub_path)
                    if not sub:
                        continue

                    # Swagger 1.2 API declaration often has:
                    #   - basePath (sometimes)
                    #   - resourcePath (often)
                    #   - apis: [{path: "/network-device", operations:[...]}]
                    resource_path = sub.get("resourcePath")
                    base_path = sub.get("basePath")

                    # Prefer the actual REST resource routes from "apis[].path"
                    sub_apis = sub.get("apis")
                    if isinstance(sub_apis, list) and sub_apis:
                        for a in sub_apis:
                            if not isinstance(a, dict):
                                continue
                            sp = a.get("path")
                            if not isinstance(sp, str):
                                continue

                            # Build a base route. For ClearPass, these are usually already like "/network-device"
                            route = _clean_swagger_path(sp)

                            # Derive a key:
                            # If route ends with "/network-device", key = "network-device"
                            key = route.strip("/").split("/")[-1].lower()
                            if key:
                                _add_endpoint(api_paths, key, route)
                                added += 1
                    elif isinstance(resource_path, str):
                        # Fallback: use resourcePath if apis[] missing
                        route = _clean_swagger_path(resource_path)
                        key = route.strip("/").split("/")[-1].lower()
                        if key:
                            _add_endpoint(api_paths, key, route)
                            added += 1
                    else:
                        # If we only got basePath and nothing else, there isn't enough to map endpoints.
                        # Keep going.
                        _ = base_path  # unused, but kept for debugging if you want to log

                log.info("[api_catalog] %s: added %d endpoints (swagger 1.2 listing)", module_name, added)
                continue

            # If neither worked, log keys for visibility
            log.warning(
                "[api_catalog] %s: JSON docs contained neither usable 'services' nor usable 'apis' (keys=%s, source=%s)",
                module_name,
                list(listing.keys())[:30],
                listing_path,
            )

        # --- Step 3: add OAuth bootstrap endpoints and aliases
        api_paths.update(OAUTH_ENDPOINTS)

        for bad, good in ALIASES.items():
            if good in api_paths and bad not in api_paths:
                api_paths[bad] = api_paths[good]

        log.info("[api_catalog] Total endpoints (including oauth): %d", len(api_paths))
        return api_paths

def get_api_paths(cp_client, *, token: str, force_refresh: bool = False) -> dict[str, str]:
    return ApiEndpointCache(cp_client, token=token).get_api_paths(force_refresh=force_refresh)

def get_cache_file_path() -> Path:
    cache_dir = Path(getattr(config, "CACHE_DIR", Path("./cache")))
    return cache_dir / EndpointCacheConfig().cache_filename

def clear_api_cache() -> bool:
    """
    Returns True if a cache file was removed, False if it didn't exist.
    """
    p = get_cache_file_path()
    try:
        p.unlink()
        return True
    except FileNotFoundError:
        return False