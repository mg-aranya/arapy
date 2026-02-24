import pytest
from arapy.main import parse_cli


def test_parse_module_service_action():
    argv = ["main.py", "identities", "endpoint", "list", "-vvv", "--limit=5", "--out=./x.csv"]
    args = parse_cli(argv)
    assert args["module"] == "identities"
    assert args["service"] == "endpoint"
    assert args["action"] == "list"
    assert args["verbose"]
    assert args["limit"] == "5"
    assert args["out"] == "./x.csv"


def test_unknown_flag_raises():
    argv = ["main.py", "identities", "endpoint", "list", "-x"]
    with pytest.raises(ValueError):
        parse_cli(argv)