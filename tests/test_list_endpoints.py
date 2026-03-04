import re
import pytest
from requests import HTTPError

from arapy.api_catalog import load_cached_catalog


def _iter_get_endpoints(catalog: dict):
    modules = catalog.get("modules") or {}
    for module, services in modules.items():
        if not isinstance(services, dict):
            continue
        for service, entry in services.items():
            if not isinstance(entry, dict):
                continue
            methods = [m.upper() for m in (entry.get("methods") or []) if isinstance(m, str)]
            route = entry.get("route")
            if not isinstance(route, str):
                continue
            if "GET" not in methods:
                continue
            yield module, service, route


@pytest.fixture(scope="session")
def catalog():
    cat = load_cached_catalog()
    if not cat:
        pytest.skip("No api_endpoints_cache.json found. Run: arapy identities endpoint list")
    return cat


def _compile_denylist(pytestconfig):
    pats = list(pytestconfig.getoption("--arapy-deny-regex") or [])

    # Endpoints that are GET-able but not listable collections (require params or are actions/singletons/lookups)
    pats += [
        # action / RPC-like
        r"/activate-(online|offline)$",
        r"/export$",
        r"/reject$",
        # lookups / singletons / parameter-required
        r"/user-id$",
        r"/page-name$",
        r"/host-address$",
        r"/server-name$",
        r"/mac-address$",
        r"/username$",
        r"/global-settings$",
        r"/settings$",
        r"/login-audit$",
        r"/system-event$",
        r"/server-cert$",
        r"/name$",  # <-- NEW: many swagger paths end with /{name} and become /name (not listable)
        # path-param artifacts (from older catalogs)
        r"/time-range$",
        r"/ip-range$",
        r"/mac$",
        r"/ip$",
        # known "GET but not list"
        r"^/api/oauth$",
        r"^/api/session-action$",
        r"^/api/device-profiler/device-fingerprint$",
        r"^/api/server/(access-control|service|snmp)$",
    ]
    return [re.compile(p) for p in pats]


def _is_denied(route: str, deny):
    return any(rx.search(route) for rx in deny)


def test_list_endpoints_smoke(clearpass_client, token, api_paths, catalog, pytestconfig):
    deny = _compile_denylist(pytestconfig)
    max_n = int(pytestconfig.getoption("--arapy-max-endpoints"))

    endpoints = []
    for module, service, route in _iter_get_endpoints(catalog):
        if _is_denied(route, deny):
            continue
        endpoints.append((module, service, route))

    endpoints.sort(key=lambda x: (x[0], x[1]))
    if max_n and len(endpoints) > max_n:
        endpoints = endpoints[:max_n]

    failures = []
    by_status = {}

    for module, service, route in endpoints:
        key = f"{module}:{service}"
        try:
            clearpass_client.request(
                api_paths,
                "GET",
                key,
                token=token,
                params={"offset": 0, "limit": 1, "sort": "+id"},
            )
        except HTTPError as e:
            code = getattr(e.response, "status_code", None)
            by_status[code] = by_status.get(code, 0) + 1
            failures.append((key, route, f"{code} {e}"))
        except Exception as e:
            by_status["other"] = by_status.get("other", 0) + 1
            failures.append((key, route, str(e)))

    if failures:
        status_summary = ", ".join(f"{k}:{v}" for k, v in sorted(by_status.items(), key=lambda kv: str(kv[0])))
        msg = "\n".join(f"- {k} ({route}): {err}" for k, route, err in failures[:50])
        pytest.fail(f"{len(failures)} list endpoints failed (status summary: {status_summary}). First failures:\n{msg}")
