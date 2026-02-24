import pytest
from unittest.mock import MagicMock
from arapy.commands import handle_endpoint_add, handle_endpoint_list, handle_network_device_get
from arapy.api_endpoints import API_ENDPOINTS as APIPath


def test_endpoint_mac_normalization_and_randomized_mac():
    cp = MagicMock()
    cp.endpoint_add = MagicMock(return_value={"id": 1})

    args = {
        "mac_address": "AA-BB-CC-DD-EE-FF",
        "status": "Known",
        "randomized_mac": "yes",
        "device_insight_tags": "tag1, tag2",
        "verbose": False,
        "module": "identities",
        "service": "endpoint",
        "action": "add",
    }

    handle_endpoint_add(cp, "tok", APIPath, args)

    # inspect payload passed to cp.endpoint_add
    assert cp.endpoint_add.called
    called_payload = cp.endpoint_add.call_args[0][2]
    assert called_payload["mac_address"] == "aa:bb:cc:dd:ee:ff"
    assert called_payload["randomized_mac"] is True
    assert isinstance(called_payload["device_insight_tags"], list)
    assert called_payload["device_insight_tags"] == ["tag1", "tag2"]


def test_endpoint_add_invalid_mac_raises():
    cp = MagicMock()
    args = {
        "mac_address": "invalid-mac",
        "status": "Known",
        "verbose": False,
        "module": "identities",
        "service": "endpoint",
        "action": "add",
    }

    with pytest.raises(ValueError):
        handle_endpoint_add(cp, "tok", APIPath, args)


def test_endpoint_list_passes_filter_and_calculate_count():
    cp = MagicMock()
    cp.endpoint_list = MagicMock(return_value={})

    args = {
        "filter": '{"status":"Known"}',
        "calculate_count": "true",
        "limit": "10",
        "offset": "0",
        "sort": "+id",
        "out": "./logs/endpoints.csv",
        "verbose": False,
        "module": "identities",
        "service": "endpoint",
        "action": "list",
    }

    handle_endpoint_list(cp, "tok", APIPath, args)

    assert cp.endpoint_list.called
    kwargs = cp.endpoint_list.call_args[1]
    assert kwargs.get("filter") == args["filter"]
    assert kwargs.get("calculate_count") is True


def test_nad_get_passes_id_and_logs():
    cp = MagicMock()
    cp.network_device_get = MagicMock(return_value={"id": 123, "name": "nad1"})

    args = {
        "id": "123",
        "out": "./logs/network_devices.",
        "verbose": False,
        "module": "policy-elements",
        "service": "network-device",
        "action": "get",
    }

    handle_network_device_get(cp, "tok", APIPath, args)

    assert cp.network_device_get.called
    # support keyword or positional invocation
    called_kwargs = cp.network_device_get.call_args.kwargs
    if 'device_id' in called_kwargs:
        called_id = called_kwargs['device_id']
    else:
        called_id = cp.network_device_get.call_args.args[2]
    assert called_id == 123
