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
OAUTH_ENDPOINTS: dict[str, str] = {
    "oauth": "/api/oauth",
    "oauth-me": "/api/oauth/me",
    "oauth-privileges": "/api/oauth/privileges",
}

# Keep CLI compatibility with existing typos in older versions (optional but recommended).
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
    For request patterns, we want a stable "base collection" path.
    """
    route = re.sub(r"\[.*?\]", "", route)  # remove bracketed optional segments like [/:name]
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
    for m in re.findall(r"(/api-docs/[A-Za-z0-9_-]+-v\d+)", html):
        modules.add(m)
    for m in re.findall(r"(api-docs/[A-Za-z0-9_-]+-v\d+)", html):
        modules.add("/" + m)
    return sorted(modules)


@dataclass(frozen=True)
class EndpointCacheConfig:
    ttl_seconds: int = 24 * 3600
    cache_filename: str = "api_endpoints_cache.json"


class ApiEndpointCache:
    """
    Cache format (v1):
      {
        "version": 1,
        "generated_at": "2026-03-03T19:59:08Z",
        "server": "192.168.100.30:443",
        "modules": { "<module>": { "<service>": {"route": "...", "methods":[...], "actions":[...]} } },
        "flat": { "<service>": "/api/..." }
      }

    Backwards compatible with older flat dict cache (service->route).
    """

    def __init__(self, cp_client, *, token: str, cfg: EndpointCacheConfig | None = None):
        self.cp = cp_client
        self.token = token
        self.cfg = cfg or EndpointCacheConfig()

        cache_dir = Path(getattr(config, "CACHE_DIR", Path("./cache")))
        cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_path = cache_dir / self.cfg.cache_filename

    def get_api_paths(self, *, force_refresh: bool = False) -> dict[str, str]:
        if not force_refresh:
            catalog = self._load_if_fresh()
            if catalog:
                return catalog["flat"]

        catalog = self._build_catalog_from_clearpass()
        self._save(catalog)
        return catalog["flat"]

    def get_catalog(self, *, force_refresh: bool = False) -> dict[str, Any]:
        if not force_refresh:
            catalog = self._load_if_fresh()
            if catalog:
                return catalog
        catalog = self._build_catalog_from_clearpass()
        self._save(catalog)
        return catalog

    def _load_if_fresh(self) -> dict[str, Any] | None:
        try:
            st = self.cache_path.stat()
        except FileNotFoundError:
            return None

        age = time.time() - st.st_mtime
        if age > self.cfg.ttl_seconds:
            return None

        try:
            data = json.loads(self.cache_path.read_text(encoding="utf-8"))
        except Exception:
            return None

        # NEW format: dict with "flat"
        if isinstance(data, dict) and isinstance(data.get("flat"), dict):
            return data

        # OLD format: flat dict[str,str] (service->route)
        if isinstance(data, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
            return {"version": 0, "generated_at": None, "server": None, "modules": {}, "flat": data}

        return None

    def _save(self, api_catalog: dict[str, Any]) -> None:
        tmp = self.cache_path.with_suffix(".tmp")
        tmp.write_text(json.dumps(api_catalog, indent=2, sort_keys=True), encoding="utf-8")
        os.replace(tmp, self.cache_path)

    def _raw_get_text(self, path: str) -> str:
        """
        Uses the same server/SSL/session settings as ClearPassClient.request()
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

    def _build_catalog_from_clearpass(self) -> dict[str, Any]:
        """
        ClearPass /api/apigility/documentation/<Module-v1> often returns a Swagger 1.2 "resource listing":
            {"apiVersion": "...", "swaggerVersion": "...", "apis": [{"path": "/PolicyElements-v1/NetworkDevice", ...}, ...]}

        We:
        1) discover modules from /api-docs
        2) fetch module listing JSON
        3) follow each listing apis[].path to fetch the sub-doc
        4) extract resource paths + supported HTTP methods into a module/service catalog
        5) also build a flat service->route map for request() compatibility
        """
        from .logger import AppLogger

        log = AppLogger().get_logger(__name__)

        def _clean_swagger_path(p: str) -> str:
            # "/network-device/{id}" -> "/network-device"
            p = re.sub(r"\{[^}]+\}", "", p)
            return p.rstrip("/") or "/"

        def _add_flat(flat: dict[str, str], key: str, route: str, *, namespace: str | None = None) -> str:
            """
            Add a route to the flat map, and (when namespace is provided) also add a namespaced key
            to prevent collisions across modules (e.g. identities:endpoint vs insight:endpoint).
            Returns the resolved route value stored in the flat map.
            """
            key = key.strip()
            if not key:
                return ""

            base_route = _clean_apigility_route(route)
            if base_route.startswith("/api/"):
                value = base_route
            elif base_route.startswith("/"):
                value = "/api" + base_route
            else:
                value = "/api/" + base_route

            flat[key] = value
            if namespace:
                flat[f"{namespace}:{key}"] = value
            return value

        def _module_to_cli(module_name: str) -> str:
            base = re.sub(r"-v\d+$", "", module_name)  # "PolicyElements-v1" -> "PolicyElements"
            return base.replace("_", "-").lower()

        def _derive_actions(methods: set[str]) -> list[str]:
            m = {x.upper() for x in methods}
            actions: list[str] = []
            if "GET" in m:
                actions += ["list", "get"]
            if "POST" in m:
                actions += ["add"]
            if "DELETE" in m:
                actions += ["delete"]
            return actions

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
            return _extract_module_doc_paths_from_api_docs_html(text)

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

        flat: dict[str, str] = {}
        modules: dict[str, dict[str, dict[str, Any]]] = {}

        # --- Step 2: for each module, fetch listing and follow apis[]
        for module_path in module_doc_paths:
            module_name = module_path.rsplit("/", 1)[-1]  # "PolicyElements-v1"
            cli_module = _module_to_cli(module_name)
            modules.setdefault(cli_module, {})

            listing_path = f"/api/apigility/documentation/{module_name}"
            listing = _load_json(listing_path)

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

            # Case A: Apigility services[]
            services = listing.get("services")
            if isinstance(services, list) and services:
                for svc in services:
                    if not isinstance(svc, dict):
                        continue
                    name = svc.get("name")
                    route = svc.get("route")
                    if not isinstance(name, str) or not isinstance(route, str):
                        continue
                    service_key = _camel_to_kebab(name)
                    _add_flat(flat, service_key, route, namespace=cli_module)

                    # methods/actions not exposed in this format without extra requests
                    modules[cli_module].setdefault(
                        service_key,
                        {"route": flat[service_key], "methods": [], "actions": ["list", "get", "add", "delete"]},
                    )
                    added += 1

                log.info("[api_catalog] %s: added %d endpoints (apigility services)", module_name, added)
                continue

            # Case B: Swagger 1.2 resource listing
            apis = listing.get("apis")
            if isinstance(apis, list) and apis:
                for item in apis:
                    if not isinstance(item, dict):
                        continue
                    p = item.get("path")
                    if not isinstance(p, str):
                        continue

                    # Normalize to a full API doc path
                    if p.startswith("/api/"):
                        sub_path = p
                    elif p.startswith(f"/{module_name}/"):
                        sub_path = f"/api/apigility/documentation{p}"
                    elif p.startswith("/"):
                        sub_path = f"/api/apigility/documentation/{module_name}{p}"
                    else:
                        sub_path = f"/api/apigility/documentation/{module_name}/{p}"

                    sub = _load_json(sub_path)
                    if not sub:
                        continue

                    sub_apis = sub.get("apis")
                    if isinstance(sub_apis, list) and sub_apis:
                        for a in sub_apis:
                            if not isinstance(a, dict):
                                continue
                            sp = a.get("path")
                            if not isinstance(sp, str):
                                continue

                            route = _clean_swagger_path(sp)
                            service_key = route.strip("/").split("/")[-1].lower()
                            if not service_key:
                                continue

                            # Collect methods from operations
                            methods: set[str] = set()
                            ops = a.get("operations")
                            if isinstance(ops, list):
                                for op in ops:
                                    if isinstance(op, dict) and isinstance(op.get("method"), str):
                                        methods.add(op["method"].upper())

                            _add_flat(flat, service_key, route, namespace=cli_module)

                            entry = modules[cli_module].get(service_key)
                            if entry is None:
                                modules[cli_module][service_key] = {
                                    "route": flat[service_key],
                                    "methods": sorted(methods),
                                    "actions": _derive_actions(methods),
                                }
                            else:
                                merged = set(entry.get("methods", [])) | methods
                                entry["methods"] = sorted(merged)
                                entry["actions"] = _derive_actions(merged)
                                entry["route"] = flat[service_key]

                            added += 1

                    # Fallback if api declaration uses resourcePath only
                    elif isinstance(sub.get("resourcePath"), str):
                        route = _clean_swagger_path(sub["resourcePath"])
                        service_key = route.strip("/").split("/")[-1].lower()
                        if service_key:
                            _add_flat(flat, service_key, route, namespace=cli_module)
                            modules[cli_module].setdefault(
                                service_key,
                                {"route": flat[service_key], "methods": [], "actions": ["list", "get", "add", "delete"]},
                            )
                            added += 1

                log.info("[api_catalog] %s: added %d endpoints (swagger 1.2 listing)", module_name, added)
                continue

            log.warning(
                "[api_catalog] %s: JSON docs contained neither usable 'services' nor usable 'apis' (keys=%s, source=%s)",
                module_name,
                list(listing.keys())[:30],
                listing_path,
            )

        # --- Step 3: add OAuth bootstrap endpoints and aliases
        for k, v in OAUTH_ENDPOINTS.items():
            flat[k] = v

        modules.setdefault("oauth", {})
        for k, v in OAUTH_ENDPOINTS.items():
            modules["oauth"].setdefault(k, {"route": v, "methods": [], "actions": ["list", "get", "add", "delete"]})

        for bad, good in ALIASES.items():
            if good in flat and bad not in flat:
                flat[bad] = flat[good]
                for mod_services in modules.values():
                    if good in mod_services and bad not in mod_services:
                        mod_services[bad] = dict(mod_services[good])

        catalog: dict[str, Any] = {
            "version": 1,
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "server": getattr(self.cp, "server", None),
            "modules": modules,
            "flat": flat,
        }

        log.info("[api_catalog] Total endpoints (including oauth): %d", len(flat))
        return catalog


def get_api_paths(cp_client, *, token: str, force_refresh: bool = False) -> dict[str, str]:
    return ApiEndpointCache(cp_client, token=token).get_api_paths(force_refresh=force_refresh)


def get_api_catalog(cp_client, *, token: str, force_refresh: bool = False) -> dict[str, Any]:
    return ApiEndpointCache(cp_client, token=token).get_catalog(force_refresh=force_refresh)


def get_cache_file_path() -> Path:
    cache_dir = Path(getattr(config, "CACHE_DIR", Path("./cache")))
    return cache_dir / EndpointCacheConfig().cache_filename


def load_cached_catalog() -> dict[str, Any] | None:
    p = get_cache_file_path()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except Exception:
        return None

    if isinstance(data, dict) and isinstance(data.get("flat"), dict):
        return data

    if isinstance(data, dict) and all(isinstance(k, str) and isinstance(v, str) for k, v in data.items()):
        return {"version": 0, "generated_at": None, "server": None, "modules": {}, "flat": data}

    return None


def clear_api_cache() -> bool:
    """Returns True if a cache file was removed, False if it didn't exist."""
    p = get_cache_file_path()
    try:
        p.unlink()
        return True
    except FileNotFoundError:
        return False
