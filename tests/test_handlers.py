import pytest
from unittest.mock import MagicMock
from arapy.commands import handle_endpoint_add
from arapy.api_endpoints import API_ENDPOINTS as APIPath


def test_endpoint_add_requires_fields():
    cp = MagicMock()
    args = {
        "verbose": False,
        "module": "identities",
        "service": "endpoint",
        "action": "add",
        # missing mac_address and status
    }

    with pytest.raises(ValueError):
        handle_endpoint_add(cp, "tok", APIPath, args)