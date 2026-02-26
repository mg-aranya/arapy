import builtins
import pytest
from unittest.mock import MagicMock

import arapy.main as main_mod


def test_parse_cli_flags_and_positionals():
    argv = ["arapy", "-vvv", "identities", "endpoint", "list", "--limit=5", "--out=x.json"]
    args = main_mod.parse_cli(argv)
    assert args["verbose"] is True
    assert args["module"] == "identities"
    assert args["service"] == "endpoint"
    assert args["action"] == "list"
    assert args["limit"] == "5"
    assert args["out"] == "x.json"


def test_parse_cli_unknown_dash_flag_raises():
    with pytest.raises(ValueError):
        main_mod.parse_cli(["arapy", "-x"])


def test_main_version_prints_and_exits(monkeypatch, capsys):
    monkeypatch.setattr(main_mod, "get_version", lambda: "9.9.9")
    monkeypatch.setattr(main_mod.sys, "argv", ["arapy", "--version"])
    main_mod.main()
    assert capsys.readouterr().out.strip() == "9.9.9"


def test_main_help_calls_print_help(monkeypatch):
    called = {"n": 0}
    monkeypatch.setattr(main_mod, "print_help", lambda args=None: called.__setitem__("n", called["n"] + 1))
    monkeypatch.setattr(main_mod.sys, "argv", ["arapy", "--help"])
    main_mod.main()
    assert called["n"] == 1


def test_main_gui_dispatch(monkeypatch):
    called = {"n": 0}
    monkeypatch.setattr(main_mod, "run_gui", lambda: called.__setitem__("n", called["n"] + 1))
    monkeypatch.setattr(main_mod.sys, "argv", ["arapy", "gui"])
    main_mod.main()
    assert called["n"] == 1


def test_main_unknown_command_prints_help(monkeypatch, capsys):
    # Force FUNCTIONS without the requested action
    monkeypatch.setattr(main_mod.commands, "FUNCTIONS", {"list": lambda *a, **k: None})
    monkeypatch.setattr(main_mod, "print_help", lambda args=None: print("HELP"))
    monkeypatch.setattr(main_mod, "ClearPassClient", MagicMock())
    monkeypatch.setattr(main_mod.sys, "argv", ["arapy", "identities", "endpoint", "nope"])
    main_mod.main()
    out = capsys.readouterr().out
    assert "HELP" in out
    assert "Unknown command: identities endpoint nope" in out


def test_main_happy_path_invokes_commands_function(monkeypatch):
    # Stub CP client + login
    cp = MagicMock()
    cp.login.return_value = {"access_token": "tok"}
    monkeypatch.setattr(main_mod, "ClearPassClient", lambda *a, **k: cp)

    fn = MagicMock()
    monkeypatch.setattr(main_mod.commands, "FUNCTIONS", {"list": fn})

    monkeypatch.setattr(main_mod.sys, "argv", ["arapy", "identities", "endpoint", "list", "--limit=5"])
    main_mod.main()

    fn.assert_called_once()
    # args passed through should contain module/service/action/limit
    passed_args = fn.call_args.args[3]
    assert passed_args["module"] == "identities"
    assert passed_args["service"] == "endpoint"
    assert passed_args["action"] == "list"
    assert passed_args["limit"] == "5"
