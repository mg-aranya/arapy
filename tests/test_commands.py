import pytest

import arapy.commands as commands
import arapy.config as config


@pytest.fixture
def api_catalog():
    return {
        "modules": {
            "identities": {
                "endpoint": {
                    "actions": {
                        "list": {
                            "method": "GET",
                            "paths": ["/api/endpoint"],
                            "params": [
                                "filter",
                                "sort",
                                "offset",
                                "limit",
                                "calculate_count",
                            ],
                        },
                        "get": {
                            "method": "GET",
                            "paths": [
                                "/api/endpoint/{id}",
                                "/api/endpoint/name/{name}",
                            ],
                            "params": ["id", "name"],
                        },
                        "delete": {
                            "method": "DELETE",
                            "paths": [
                                "/api/endpoint/{id}",
                                "/api/endpoint/name/{name}",
                            ],
                        },
                        "add": {
                            "method": "POST",
                            "paths": ["/api/endpoint"],
                            "params": ["name", "description", "foo"],
                        },
                    }
                }
            }
        }
    }


def test_resolve_out_path_uses_out_arg(tmp_path):
    args = {"out": str(tmp_path / "custom.json")}
    assert commands.resolve_out_path(args, "svc", "list", "json") == str(
        tmp_path / "custom.json"
    )


def test_resolve_out_path_default_uses_log_dir_and_normalizes_service(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(config, "LOG_DIR", tmp_path)
    args = {}
    out = commands.resolve_out_path(args, "network-device", "list", "json")
    assert out == str(tmp_path / "network_device_list.json")


def test_payload_from_args_strips_reserved():
    args = {"name": "x", "id": "1", "console": True, "module": "m", "foo": "bar"}
    payload = commands._payload_from_args(args, {"console", "module"})
    assert payload == {"name": "x", "id": "1", "foo": "bar"}


def test_list_handler_validates_limit_range(api_catalog):
    class CP:
        def get_action_definition(self, api_catalog, module, service, action):
            return api_catalog["modules"][module][service]["actions"][action]

        def _list(self, *args, **kwargs):
            return {}

    with pytest.raises(ValueError, match="--limit must be between 1 and 1000"):
        commands.list_handler(
            CP(),
            "t",
            api_catalog,
            {
                "module": "identities",
                "service": "endpoint",
                "action": "list",
                "limit": "0",
            },
        )


def test_list_handler_calls_cp_and_logs(monkeypatch, api_catalog):
    calls = {}

    class CP:
        def get_action_definition(self, api_catalog, module, service, action):
            return api_catalog["modules"][module][service]["actions"][action]

        def _list(self, api_catalog, token, args, *, params=None):
            calls["api_catalog"] = api_catalog
            calls["token"] = token
            calls["args"] = args
            calls["params"] = params
            return {"_embedded": {"items": [{"id": 1}]}, "count": 1}

    def fake_log_to_file(thing, filename, **kwargs):
        calls["logged"] = {"thing": thing, "filename": str(filename), "kwargs": kwargs}
        return thing

    monkeypatch.setattr(commands, "log_to_file", fake_log_to_file)

    args = {
        "module": "identities",
        "service": "endpoint",
        "action": "list",
        "offset": "10",
        "limit": "25",
        "sort": "-id",
        "filter": '{"name":"x"}',
        "calculate_count": True,
        "data_format": "json",
        "console": False,
    }

    commands.list_handler(CP(), "tok", api_catalog, args)

    assert calls["params"] == {
        "offset": 10,
        "limit": 25,
        "sort": "-id",
        "filter": '{"name":"x"}',
        "calculate_count": True,
    }
    assert calls["logged"]["thing"]["count"] == 1
    assert calls["logged"]["filename"].endswith("endpoint_list.json")


def test_get_handler_calls_cp_and_logs(monkeypatch, api_catalog):
    logged = {}

    class CP:
        def get_action_definition(self, api_catalog, module, service, action):
            return api_catalog["modules"][module][service]["actions"][action]

        def _get(self, api_catalog, token, args, *, params=None):
            logged["call"] = {
                "api_catalog": api_catalog,
                "token": token,
                "args": args,
                "params": params,
            }
            return {"name": "bob", "id": 2}

    def fake_log_to_file(thing, filename, **kwargs):
        logged["thing"] = thing
        logged["filename"] = str(filename)

    monkeypatch.setattr(commands, "log_to_file", fake_log_to_file)

    commands.get_handler(
        CP(),
        "tok",
        api_catalog,
        {"module": "identities", "service": "endpoint", "action": "get", "name": "bob"},
    )
    assert logged["call"]["params"] == {"name": "bob"}
    assert logged["thing"]["id"] == 2
    assert logged["filename"].endswith("endpoint_get.json")


def test_delete_handler_calls_delete(monkeypatch, api_catalog):
    logged = {}

    class CP:
        def _delete(self, api_catalog, token, args):
            logged["delete_call"] = {
                "api_catalog": api_catalog,
                "token": token,
                "args": args,
            }
            return {"deleted": args["id"]}

    def fake_log_to_file(thing, filename, **kwargs):
        logged["thing"] = thing
        logged["filename"] = str(filename)

    monkeypatch.setattr(commands, "log_to_file", fake_log_to_file)

    cp = CP()
    commands.delete_handler(
        cp,
        "tok",
        api_catalog,
        {
            "module": "identities",
            "service": "endpoint",
            "action": "delete",
            "id": "123",
        },
    )
    assert logged["delete_call"]["args"]["id"] == "123"
    assert logged["thing"]["deleted"] == "123"
    assert logged["filename"].endswith("endpoint_delete.json")


def test_add_handler_builds_payload_from_args(monkeypatch, api_catalog):
    logged = {}

    class CP:
        def resolve_action(self, api_catalog, module, service, action, args):
            return (
                api_catalog["modules"][module][service]["actions"][action],
                "/api/endpoint",
                [],
            )

        def _add(self, api_catalog, token, args, payload):
            logged["add_call"] = {
                "api_catalog": api_catalog,
                "token": token,
                "args": args,
                "payload": payload,
            }
            return {"id": 7, **payload}

    monkeypatch.setattr(
        commands,
        "log_to_file",
        lambda thing, filename, **kwargs: logged.update(
            {"thing": thing, "filename": str(filename)}
        ),
    )

    commands.add_handler(
        CP(),
        "tok",
        api_catalog,
        {
            "module": "identities",
            "service": "endpoint",
            "action": "add",
            "name": "alice",
            "description": "demo",
            "foo": "bar",
            "console": False,
        },
    )

    assert logged["add_call"]["payload"] == {
        "name": "alice",
        "description": "demo",
        "foo": "bar",
    }
    assert logged["thing"]["id"] == 7
