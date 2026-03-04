import os
import pytest

from arapy.clearpass import ClearPassClient
from arapy.api_catalog import OAUTH_ENDPOINTS, get_api_paths, load_cached_catalog


def pytest_addoption(parser):
    parser.addoption(
        "--arapy-max-endpoints",
        action="store",
        default="0",
        help="Limit number of list endpoints tested (0 = no limit).",
    )
    parser.addoption(
        "--arapy-deny-regex",
        action="append",
        default=[],
        help="Regex patterns (can repeat) to skip endpoints by route.",
    )


@pytest.fixture(scope="session")
def clearpass_client():
    server = os.environ.get("ARAPY_SERVER")
    if not server:
        pytest.skip("ARAPY_SERVER not set (integration test)")

    verify_ssl = os.environ.get("ARAPY_VERIFY_SSL", "false").lower() in ("1", "true", "yes", "on")
    timeout = int(os.environ.get("ARAPY_TIMEOUT", "30"))

    return ClearPassClient(
        server=server,
        https_prefix="https://",
        verify_ssl=verify_ssl,
        timeout=timeout,
    )


@pytest.fixture(scope="session")
def token(clearpass_client):
    token = os.environ.get("ARAPY_TOKEN")
    if token:
        return token

    user = os.environ.get("ARAPY_USERNAME")
    pw = os.environ.get("ARAPY_PASSWORD")
    if not user or not pw:
        pytest.skip("Set ARAPY_TOKEN or (ARAPY_USERNAME + ARAPY_PASSWORD)")

    grant_type = os.environ.get("ARAPY_GRANT_TYPE", "client_credentials")
    creds = {"grant_type": grant_type, "client_id": user, "client_secret": pw}
    return clearpass_client.login(OAUTH_ENDPOINTS, creds)["access_token"]


@pytest.fixture(scope="session")
def api_paths(clearpass_client, token):
    catalog = load_cached_catalog()
    if catalog and isinstance(catalog.get("flat"), dict):
        return catalog["flat"]
    return get_api_paths(clearpass_client, token=token, force_refresh=True)
