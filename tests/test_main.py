import arapy.cli.completion as completion
import arapy.cli.main as main

TEST_CATALOG = {
    "modules": {
        "identities": {
            "endpoint": {
                "actions": {
                    "list": {"method": "GET", "paths": ["/api/endpoint"]},
                    "get": {"method": "GET", "paths": ["/api/endpoint/{id}"]},
                    "add": {"method": "POST", "paths": ["/api/endpoint"]},
                }
            }
        }
    }
}


def test_parse_cli_basic():
    argv = [
        "arapy",
        "identities",
        "endpoint",
        "list",
        "--limit=10",
        "--console",
        "--log_level=debug",
    ]
    args = main.parse_cli(argv)
    assert args["module"] == "identities"
    assert args["service"] == "endpoint"
    assert args["action"] == "list"
    assert args["limit"] == "10"
    assert args["console"] is True
    assert args["log_level"] == "debug"


def test_parse_cli_ignores_unknown_flags_in_completion_mode():
    argv = ["arapy", "--_complete", "--_cur=ep", "-x", "identities"]
    args = main.parse_cli(argv)
    assert args["_complete"] is True


def test_complete_outputs_modules(capsys, monkeypatch):
    monkeypatch.setattr(main, "load_cached_catalog", lambda settings=None: TEST_CATALOG)
    main.complete(["--_cur="])
    out = capsys.readouterr().out.strip().splitlines()
    assert "identities" in out
    assert "copy" in out


def test_complete_outputs_services_for_module(capsys, monkeypatch):
    monkeypatch.setattr(main, "load_cached_catalog", lambda settings=None: TEST_CATALOG)
    main.complete(["identities", "--_cur="])
    out = capsys.readouterr().out.strip().splitlines()
    assert "endpoint" in out


def test_complete_outputs_actions_for_service(capsys, monkeypatch):
    monkeypatch.setattr(main, "load_cached_catalog", lambda settings=None: TEST_CATALOG)
    main.complete(["identities", "endpoint"])
    out = capsys.readouterr().out.strip().splitlines()
    assert "list" in out
    assert "get" in out


def test_complete_outputs_server_profiles_for_use(capsys, monkeypatch):
    monkeypatch.setattr(main, "load_cached_catalog", lambda settings=None: TEST_CATALOG)
    monkeypatch.setattr(completion, "list_profiles", lambda: ["dev", "prod"])
    main.complete(["server", "use"])
    out = capsys.readouterr().out.strip().splitlines()
    assert "dev" in out
    assert "prod" in out


def test_complete_outputs_services_for_copy_module(capsys, monkeypatch):
    monkeypatch.setattr(main, "load_cached_catalog", lambda settings=None: TEST_CATALOG)
    main.complete(["copy", "identities"])
    out = capsys.readouterr().out.strip().splitlines()
    assert "endpoint" in out


def test_parse_cli_encrypt_disable_and_separator():
    argv = [
        "arapy",
        "policyelements",
        "network-device",
        "list",
        "--console",
        "--",
        "--encrypt=disable",
    ]
    args = main.parse_cli(argv)
    assert args["encrypt"] == "disable"
    assert args["console"] is True


def test_parse_cli_decrypt_flag():
    argv = ["arapy", "policyelements", "network-device", "list", "--decrypt"]
    args = main.parse_cli(argv)
    assert args["decrypt"] is True


def test_parse_cli_copy_command():
    argv = [
        "arapy",
        "copy",
        "policyelements",
        "network-device",
        "--from=dev",
        "--to=prod",
        "--all",
        "--dry-run",
    ]
    args = main.parse_cli(argv)
    assert args["module"] == "copy"
    assert args["copy_module"] == "policyelements"
    assert args["copy_service"] == "network-device"
    assert args["from"] == "dev"
    assert args["to"] == "prod"
    assert args["all"] is True
    assert args["dry_run"] is True
