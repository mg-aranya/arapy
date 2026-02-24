import pytest
from unittest.mock import MagicMock
from arapy.clearpass import ClearPassClient

API = {"endpoint": "/api/endpoint"}


def test_endpoint_get_by_id_url():
    cp = ClearPassClient("example:443")
    cp.session.request = MagicMock()

    # fake response
    resp = MagicMock()
    resp.raise_for_status.return_value = None
    resp.status_code = 200
    resp.content = b'{"ok": true}'
    resp.json.return_value = {"ok": True}
    cp.session.request.return_value = resp

    cp.endpoint_get(API, "tok", endpoint_id=123)

    cp.session.request.assert_called_once()
    kwargs = cp.session.request.call_args.kwargs
    assert kwargs["method"] == "GET"
    assert kwargs["url"] == "https://example:443/api/endpoint/123"
    assert "Authorization" in kwargs["headers"]
    assert kwargs["headers"]["Authorization"] == "Bearer tok"