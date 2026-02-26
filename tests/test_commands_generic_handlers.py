import pytest
from unittest.mock import MagicMock

import arapy.commands as commands


def test_resolve_out_path_default_uses_log_dir_and_normalizes_service(tmp_log_dir):
    args = {"service": "network-device", "action": "list"}
    out = commands.resolve_out_path(args, "network-device", "list", "json")
    assert str(tmp_log_dir) in out
    assert out.endswith("network_device_list.json")


def test_resolve_out_path_respects_out_arg(tmp_log_dir):
    args = {"out": "/tmp/out.json"}
    assert commands.resolve_out_path(args, "x", "list", "json") == "/tmp/out.json"


def test_build_payload_from_args_drops_reserved():
    args = {"a": 1, "b": 2, "help": True}
    assert commands.build_payload_from_args(args, reserved_keys={"help"}) == {"a": 1, "b": 2}


@pytest.mark.parametrize("calc_in, expected", [("true", True), ("false", False), ("yes", True), ("0", False), (True, True), (None, None)])
def test_list_parses_calculate_count(tmp_log_dir, monkeypatch, calc_in, expected):
    cp = MagicMock()
    cp._list = MagicMock(return_value={"_embedded": {"items": []}})

    # don't actually write files
    monkeypatch.setattr(commands, "log_to_file", lambda *a, **k: None)

    args = {"service": "endpoint", "action": "list", "limit": "10", "offset": "0", "sort": "+id"}
    if calc_in is not None:
        args["calculate_count"] = calc_in

    commands._list(cp, "tok", {"endpoint": "/api/endpoint"}, args)

    kwargs = cp._list.call_args.kwargs
    assert kwargs["limit"] == 10
    if expected is None:
        assert kwargs["calculate_count"] is None
    else:
        assert kwargs["calculate_count"] == expected


def test_list_validates_limit_range(tmp_log_dir, monkeypatch):
    cp = MagicMock()
    monkeypatch.setattr(commands, "log_to_file", lambda *a, **k: None)
    with pytest.raises(ValueError):
        commands._list(cp, "tok", {"endpoint": "/api/endpoint"}, {"service": "endpoint", "action": "list", "limit": "0"})


def test_get_prefers_id_over_name_and_prefixes_name(tmp_log_dir, monkeypatch):
    cp = MagicMock()
    cp._get = MagicMock(return_value={"id": 1})
    monkeypatch.setattr(commands, "log_to_file", lambda *a, **k: None)

    # name path
    args = {"service": "endpoint", "action": "get", "name": "foo"}
    commands._get(cp, "tok", {"endpoint": "/api/endpoint"}, args)
    assert cp._get.call_args.args[3] == "name/foo"

    # id path
    cp._get.reset_mock()
    args = {"service": "endpoint", "action": "get", "id": "123"}
    commands._get(cp, "tok", {"endpoint": "/api/endpoint"}, args)
    assert cp._get.call_args.args[3] == "123"


def test_delete_requires_id_or_name(tmp_log_dir, monkeypatch):
    cp = MagicMock()
    monkeypatch.setattr(commands, "log_to_file", lambda *a, **k: None)
    with pytest.raises(ValueError):
        commands._delete(cp, "tok", {"endpoint": "/api/endpoint"}, {"service": "endpoint", "action": "delete"})
