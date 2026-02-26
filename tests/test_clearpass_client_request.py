import pytest
import requests
from unittest.mock import MagicMock

from arapy.clearpass import ClearPassClient


def _resp(*, status=200, headers=None, content=b'{"ok": true}', text=None, reason="OK", url="https://s/api/x", json_obj=None):
    r = MagicMock()
    r.status_code = status
    r.headers = headers or {"content-type": "application/json"}
    r.content = content if content is not None else b""
    if text is None:
        text = (content or b"").decode("utf-8", errors="replace")
    r.text = text
    r.reason = reason
    r.url = url
    if json_obj is None:
        json_obj = {"ok": True} if r.content else None
    r.json.return_value = json_obj
    r.raise_for_status.return_value = None
    return r


def test_request_builds_url_and_auth_header():
    cp = ClearPassClient("example:443", https_prefix="https://", verify_ssl=False, timeout=7)
    cp.session.request = MagicMock(return_value=_resp(url="https://example:443/api/endpoint/123"))

    api = {"endpoint": "/api/endpoint"}
    out = cp.request(api, "GET", "endpoint", token="tok", path_suffix="/123", params={"x": "1"})

    assert out == {"ok": True}
    kwargs = cp.session.request.call_args.kwargs
    assert kwargs["method"] == "GET"
    assert kwargs["url"] == "https://example:443/api/endpoint/123"
    assert kwargs["params"] == {"x": "1"}
    assert kwargs["verify"] is False
    assert kwargs["timeout"] == 7
    assert kwargs["headers"]["Authorization"] == "Bearer tok"


def test_request_omits_headers_when_no_token():
    cp = ClearPassClient("example:443", https_prefix="https://", verify_ssl=True, timeout=15)
    cp.session.request = MagicMock(return_value=_resp(url="https://example:443/api/endpoint"))

    api = {"endpoint": "/api/endpoint"}
    cp.request(api, "GET", "endpoint")

    kwargs = cp.session.request.call_args.kwargs
    assert kwargs["headers"] is None


def test_request_returns_none_on_204_or_empty_body():
    cp = ClearPassClient("example:443", https_prefix="https://")
    r = _resp(status=204, content=b"", json_obj=None, url="https://example:443/api/endpoint")
    cp.session.request = MagicMock(return_value=r)

    api = {"endpoint": "/api/endpoint"}
    assert cp.request(api, "DELETE", "endpoint", token="t") is None


def test_request_returns_text_when_json_decode_fails():
    cp = ClearPassClient("example:443", https_prefix="https://")
    r = _resp(headers={"content-type": "text/plain"}, content=b"plain", url="https://example:443/api/txt")
    r.json.side_effect = ValueError("no json")
    cp.session.request = MagicMock(return_value=r)

    api = {"txt": "/api/txt"}
    assert cp.request(api, "GET", "txt", token="t") == "plain"


def test_request_http_error_masks_secrets_and_truncates_body():
    cp = ClearPassClient("example:443", https_prefix="https://")
    big = ("X" * 5000).encode("utf-8")
    r = _resp(status=400, reason="Bad Request", content=big, url="https://example:443/api/oauth")
    r.raise_for_status.side_effect = requests.HTTPError("boom")
    cp.session.request = MagicMock(return_value=r)

    api = {"oauth": "/api/oauth"}
    with pytest.raises(requests.HTTPError) as ei:
        cp.request(
            api,
            "POST",
            "oauth",
            json_body={
                "client_id": "id",
                "client_secret": "secret",
                "password": "pw",
                "radius_secret": "r",
                "tacacs_secret": "t",
                "enable_password": "e",
            },
        )

    msg = str(ei.value)
    assert "HTTP 400" in msg
    assert "URL: https://example:443/api/oauth" in msg
    assert "... (truncated)" in msg
    # Don't check for substring "secret" because key names include e.g. "radius_secret".
    # Instead, ensure the *values* are masked.
    assert "client_secret': 'secret" not in msg and 'client_secret": "secret' not in msg
    assert "password': 'pw" not in msg and 'password": "pw' not in msg
    assert "'client_secret': '***'" in msg or '"client_secret": "***"' in msg


def test_login_builds_payload_from_credentials_and_calls_request():
    cp = ClearPassClient("example:443", https_prefix="https://")
    cp.request = MagicMock(return_value={"access_token": "tok"})

    creds = {"grant_type": "client_credentials", "client_id": "Client2", "client_secret": "Secret"}
    api = {"oauth": "/api/oauth"}

    out = cp.login(api, creds)
    assert out == {"access_token": "tok"}

    cp.request.assert_called_once()
    args, kwargs = cp.request.call_args
    assert args[1] == "POST"
    assert args[2] == "oauth"
    assert kwargs["json_body"] == {"grant_type": "client_credentials", "client_id": "Client2", "client_secret": "Secret"}
