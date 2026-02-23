import unittest
from unittest.mock import MagicMock
from clearpass import ClearPassClient

API = {"endpoint": "/api/endpoint"}

class TestClearPassClient(unittest.TestCase):
    def test_endpoint_get_by_id_url(self):
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
        self.assertEqual(kwargs["method"], "GET")
        self.assertEqual(kwargs["url"], "https://example:443/api/endpoint/123")
        self.assertIn("Authorization", kwargs["headers"])
        self.assertEqual(kwargs["headers"]["Authorization"], "Bearer tok")

if __name__ == "__main__":
    unittest.main()