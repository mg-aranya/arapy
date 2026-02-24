import pytest
from unittest.mock import MagicMock
from arapy.commands import handle_network_device_group_get, handle_network_device_group_list
from arapy.api_endpoints import API_ENDPOINTS as APIPath


def test_network_device_group_get_passes_id_and_logs():
    cp = MagicMock()
    cp.network_device_group_get = MagicMock(return_value={"id": 321, "name": "group1"})

    args = {
        "id": "321",
        "out": "./logs/network_device_groups.",
        "verbose": False,
        "module": "policy-elements",
        "service": "network-device-group",
        "action": "get",
    }

    handle_network_device_group_get(cp, "tok", APIPath, args)

    assert cp.network_device_group_get.called
    called_kwargs = cp.network_device_group_get.call_args.kwargs
    if 'group_id' in called_kwargs:
        called_id = called_kwargs['group_id']
    else:
        # positional style: (api_paths, token, group_id)
        called_id = cp.network_device_group_get.call_args.args[2]
    assert called_id == 321


def test_network_device_group_list_passes_filter_and_calculate_count():
    cp = MagicMock()
    cp.network_device_group_list = MagicMock(return_value={})

    args = {
        "filter": '{"name":"group1"}',
        "calculate_count": "true",
        "limit": "10",
        "offset": "0",
        "sort": "+id",
        "out": "./logs/network_device_groups.",
        "verbose": False,
        "module": "policy-elements",
        "service": "network-device-group",
        "action": "list",
    }

    handle_network_device_group_list(cp, "tok", APIPath, args)

    assert cp.network_device_group_list.called
    kwargs = cp.network_device_group_list.call_args[1]
    assert kwargs.get("filter") == args["filter"]
    assert kwargs.get("calculate_count") is True
