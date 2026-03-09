# ruff: noqa: E402

import os
import sys
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from arapy.core.catalog import OAUTH_ENDPOINTS, get_api_catalog, load_cached_catalog
from arapy.core.client import ClearPassClient


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

    verify_ssl = os.environ.get("ARAPY_VERIFY_SSL", "false").lower() in (
        "1",
        "true",
        "yes",
        "on",
    )
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

    client_id = os.environ.get("ARAPY_CLIENT_ID")
    client_secret = os.environ.get("ARAPY_CLIENT_SECRET")
    if not client_id or not client_secret:
        pytest.skip("Set ARAPY_TOKEN or (ARAPY_CLIENT_ID + ARAPY_CLIENT_SECRET)")

    grant_type = os.environ.get("ARAPY_GRANT_TYPE", "client_credentials")
    creds = {
        "grant_type": grant_type,
        "client_id": client_id,
        "client_secret": client_secret,
    }
    return clearpass_client.login(OAUTH_ENDPOINTS, creds)["access_token"]


@pytest.fixture(scope="session")
def api_catalog(clearpass_client, token):
    catalog = load_cached_catalog()
    if catalog and isinstance(catalog.get("modules"), dict):
        return catalog
    return get_api_catalog(clearpass_client, token=token, force_refresh=True)
