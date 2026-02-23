import unittest
from unittest.mock import MagicMock
from main import handle_endpoint_add

class TestHandlers(unittest.TestCase):
    def test_endpoint_add_requires_fields(self):
        cp = MagicMock()
        args = {
            "verbose": False,
            "module": "identities",
            "service": "endpoint",
            "action": "add",
            # missing mac_address and status
        }
        with self.assertRaises(ValueError):
            handle_endpoint_add(cp, "tok", args)

if __name__ == "__main__":
    unittest.main()