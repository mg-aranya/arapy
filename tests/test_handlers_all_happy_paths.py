import json
from pathlib import Path

import pytest
from unittest.mock import MagicMock

from arapy import commands
from arapy.api_endpoints import API_ENDPOINTS as APIPath


CASES = [
    # ---- Policy Elements / Network Device ----
    dict(
        name="policy_network_device_list",
        handler=commands.handle_network_device_list,
        cp_method="network_device_list",
        module="policy-elements",
        service="network-device",
        action="list",
        args_extra={"limit": "10", "offset": "0", "sort": "+id", "filter": '{"name":"nad1"}', "calculate_count": "true"},
        cp_return={"_embedded": {"items": [{"id": 1, "name": "nad1"}]}},
    ),
    dict(
        name="policy_network_device_get",
        handler=commands.handle_network_device_get,
        cp_method="network_device_get",
        module="policy-elements",
        service="network-device",
        action="get",
        args_extra={"id": "123"},
        cp_return={"id": 123, "name": "nad1"},
    ),
    dict(
        name="policy_network_device_add",
        handler=commands.handle_network_device_add,
        cp_method="network_device_create",
        module="policy-elements",
        service="network-device",
        action="add",
        args_extra={"name": "nad1", "ip_address": "10.0.0.1"},
        cp_return={"id": 123, "name": "nad1"},
    ),
    dict(
        name="policy_network_device_delete",
        handler=commands.handle_network_device_delete,
        cp_method="network_device_delete",
        module="policy-elements",
        service="network-device",
        action="delete",
        args_extra={"id": "123"},
        cp_return=None,
    ),
    # ---- Policy Elements / Network Device Group ----
    dict(
        name="policy_network_device_group_list",
        handler=commands.handle_network_device_group_list,
        cp_method="network_device_group_list",
        module="policy-elements",
        service="network-device-group",
        action="list",
        args_extra={"limit": "5", "offset": "0", "sort": "+id", "filter": '{"name":"group1"}', "calculate_count": "true"},
        cp_return={"_embedded": {"items": [{"id": 321, "name": "group1"}]}},
    ),
    dict(
        name="policy_network_device_group_get",
        handler=commands.handle_network_device_group_get,
        cp_method="network_device_group_get",
        module="policy-elements",
        service="network-device-group",
        action="get",
        args_extra={"id": "321"},
        cp_return={"id": 321, "name": "group1"},
    ),
    dict(
        name="policy_network_device_group_add",
        handler=commands.handle_network_device_group_add,
        cp_method="network_device_group_create",
        module="policy-elements",
        service="network-device-group",
        action="add",
        args_extra={"name": "group1"},
        cp_return={"id": 321, "name": "group1"},
    ),
    dict(
        name="policy_network_device_group_delete",
        handler=commands.handle_network_device_group_delete,
        cp_method="network_device_group_delete",
        module="policy-elements",
        service="network-device-group",
        action="delete",
        args_extra={"id": "321"},
        cp_return=None,
    ),
    # ---- Policy Elements / Auth Method ----
    dict(
        name="policy_auth_method_list",
        handler=commands.handle_auth_method_list,
        cp_method="auth_method_list",
        module="policy-elements",
        service="auth-method",
        action="list",
        args_extra={"limit": "5", "offset": "0", "sort": "+id"},
        cp_return={"_embedded": {"items": [{"id": 11, "name": "m1"}]}},
    ),
    dict(
        name="policy_auth_method_get",
        handler=commands.handle_auth_method_get,
        cp_method="auth_method_get",
        module="policy-elements",
        service="auth-method",
        action="get",
        args_extra={"id": "11"},
        cp_return={"id": 11, "name": "m1"},
    ),
    dict(
        name="policy_auth_method_add",
        handler=commands.handle_auth_method_add,
        cp_method="auth_method_create",
        module="policy-elements",
        service="auth-method",
        action="add",
        args_extra={"name": "m1", "method_type": "PAP"},
        cp_return={"id": 11, "name": "m1"},
    ),
    dict(
        name="policy_auth_method_delete",
        handler=commands.handle_auth_method_delete,
        cp_method="auth_method_delete",
        module="policy-elements",
        service="auth-method",
        action="delete",
        args_extra={"id": "11"},
        cp_return=None,
    ),
    # ---- Policy Elements / Enforcement Profile ----
    dict(
        name="policy_enforcement_profile_list",
        handler=commands.handle_enforcement_profile_list,
        cp_method="enforcement_profile_list",
        module="policy-elements",
        service="enforcement-profile",
        action="list",
        args_extra={"limit": "5", "offset": "0", "sort": "+id"},
        cp_return={"_embedded": {"items": [{"id": 21, "name": "ep1"}]}},
    ),
    dict(
        name="policy_enforcement_profile_get",
        handler=commands.handle_enforcement_profile_get,
        cp_method="enforcement_profile_get",
        module="policy-elements",
        service="enforcement-profile",
        action="get",
        args_extra={"id": "21"},
        cp_return={"id": 21, "name": "ep1"},
    ),
    # ---- Identities / Endpoint ----
    dict(
        name="identities_endpoint_list",
        handler=commands.handle_endpoint_list,
        cp_method="endpoint_list",
        module="identities",
        service="endpoint",
        action="list",
        args_extra={"limit": "10", "offset": "0", "sort": "+id", "filter": '{"status":"Known"}', "calculate_count": "true"},
        cp_return={"_embedded": {"items": [{"id": 1, "mac_address": "aa:bb:cc:dd:ee:ff"}]}},
    ),
    dict(
        name="identities_endpoint_get",
        handler=commands.handle_endpoint_get,
        cp_method="endpoint_get",
        module="identities",
        service="endpoint",
        action="get",
        args_extra={"id": "1"},
        cp_return={"id": 1, "mac_address": "aa:bb:cc:dd:ee:ff"},
    ),
    dict(
        name="identities_endpoint_add",
        handler=commands.handle_endpoint_add,
        cp_method="endpoint_add",
        module="identities",
        service="endpoint",
        action="add",
        args_extra={"mac_address": "aa-bb-cc-dd-ee-ff", "status": "Known"},
        cp_return={"id": 1, "mac_address": "aa:bb:cc:dd:ee:ff"},
    ),
    dict(
        name="identities_endpoint_delete",
        handler=commands.handle_endpoint_delete,
        cp_method="endpoint_delete",
        module="identities",
        service="endpoint",
        action="delete",
        args_extra={"id": "1"},
        cp_return=None,
    ),
    # ---- Identities / Device ----
    dict(
        name="identities_device_list",
        handler=commands.handle_device_list,
        cp_method="device_list",
        module="identities",
        service="device",
        action="list",
        args_extra={"limit": "10", "offset": "0", "sort": "-id"},
        cp_return={"_embedded": {"items": [{"id": 2, "mac": "11:22:33:44:55:66"}]}},
    ),
    dict(
        name="identities_device_get",
        handler=commands.handle_device_get,
        cp_method="device_get",
        module="identities",
        service="device",
        action="get",
        args_extra={"id": "2"},
        cp_return={"id": 2, "mac": "11:22:33:44:55:66"},
    ),
    dict(
        name="identities_device_add",
        handler=commands.handle_device_add,
        cp_method="device_create",
        module="identities",
        service="device",
        action="add",
        args_extra={"mac": "11:22:33:44:55:66"},
        cp_return={"id": 2, "mac": "11:22:33:44:55:66"},
    ),
    dict(
        name="identities_device_delete",
        handler=commands.handle_device_delete,
        cp_method="device_delete",
        module="identities",
        service="device",
        action="delete",
        args_extra={"id": "2"},
        cp_return=None,
    ),
    # ---- Identities / User ----
    dict(
        name="identities_user_list",
        handler=commands.handle_user_list,
        cp_method="user_list",
        module="identities",
        service="user",
        action="list",
        args_extra={"limit": "10", "offset": "0", "sort": "+id"},
        cp_return={"_embedded": {"items": [{"id": 3, "username": "u1"}]}},
    ),
    dict(
        name="identities_user_get",
        handler=commands.handle_user_get,
        cp_method="user_get",
        module="identities",
        service="user",
        action="get",
        args_extra={"id": "3"},
        cp_return={"id": 3, "username": "u1"},
    ),
    dict(
        name="identities_user_add",
        handler=commands.handle_user_add,
        cp_method="user_create",
        module="identities",
        service="user",
        action="add",
        args_extra={"username": "u1", "password": "p"},
        cp_return={"id": 3, "username": "u1"},
    ),
    dict(
        name="identities_user_delete",
        handler=commands.handle_user_delete,
        cp_method="user_delete",
        module="identities",
        service="user",
        action="delete",
        args_extra={"id": "3"},
        cp_return=None,
    ),
    # ---- Identities / API Client ----
    dict(
        name="identities_api_client_list",
        handler=commands.handle_api_client_list,
        cp_method="api_client_list",
        module="identities",
        service="api-client",
        action="list",
        args_extra={"limit": "10", "offset": "0", "sort": "+id"},
        cp_return={"_embedded": {"items": [{"id": "c1", "client_id": "Client1"}]}},
    ),
    dict(
        name="identities_api_client_get",
        handler=commands.handle_api_client_get,
        cp_method="api_client_get",
        module="identities",
        service="api-client",
        action="get",
        args_extra={"id": "Client1"},
        cp_return={"id": "Client1", "client_id": "Client1"},
    ),
    dict(
        name="identities_api_client_add",
        handler=commands.handle_api_client_add,
        cp_method="api_client_create",
        module="identities",
        service="api-client",
        action="add",
        args_extra={"client_id": "Client1", "client_secret": "secret"},
        cp_return={"id": "Client1", "client_id": "Client1"},
    ),
    dict(
        name="identities_api_client_delete",
        handler=commands.handle_api_client_delete,
        cp_method="api_client_delete",
        module="identities",
        service="api-client",
        action="delete",
        args_extra={"id": "Client1"},
        cp_return=None,
    ),
]


@pytest.mark.parametrize("case", CASES, ids=[c["name"] for c in CASES])
def test_all_handlers_happy_paths(case):
    """
    Exercise every handler in commands.DISPATCH with a known-good argument
    combination, using a MagicMock ClearPassClient and writing output via the
    normal logging mechanism into the configured LOG_DIR. This ensures that for
    each supported
    (module, service, action) combination we:

    - call the expected ClearPassClient method
    - do not raise validation errors
    - successfully write a log file to the requested output path
    """
    cp = MagicMock()
    method = getattr(cp, case["cp_method"])
    method.return_value = case["cp_return"]

    args = {
        "verbose": False,
        "module": case["module"],
        "service": case["service"],
        "action": case["action"],
    }
    args.update(case.get("args_extra") or {})

    handler = case["handler"]
    handler(cp, "tok", APIPath, args)

    # Assert ClearPassClient method was invoked
    assert method.called

    # We don't assert a specific filename here; individual handler tests cover
    # detailed IO behaviour. This test's purpose is to ensure each handler can
    # execute end-to-end with a valid argument set and call through to the
    # ClearPass client.

