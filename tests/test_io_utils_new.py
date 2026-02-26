import json
import csv
from pathlib import Path
import pytest

from arapy.io_utils import log_to_file, load_payload_file, _extract_by_path


def test_log_to_file_requires_filename(tmp_path):
    with pytest.raises(ValueError):
        log_to_file({"a": 1}, filename=None)


def test_log_to_file_callable_is_invoked_and_returned(tmp_path):
    out = tmp_path / "x.json"

    def fn(a, b):
        return {"sum": a + b}

    result = log_to_file(fn, out, 2, 3, data_format="json")
    assert result == {"sum": 5}
    data = json.loads(out.read_text(encoding="utf-8"))
    assert data == {"sum": 5}


@pytest.mark.parametrize("mode", ["w", "a"])
def test_log_to_file_json_writes_newline(tmp_path, mode):
    out = tmp_path / "x.json"
    log_to_file({"a": 1}, filename=out, data_format="json", mode=mode)
    text = out.read_text(encoding="utf-8")
    assert text.endswith("\n")


def test_log_to_file_raw_bytes_decodes(tmp_path):
    out = tmp_path / "x.txt"
    log_to_file(b"hello", filename=out, data_format="raw")
    assert out.read_text(encoding="utf-8") == "hello"


def test_log_to_file_csv_extracts_items_path(tmp_path):
    out = tmp_path / "x.csv"
    value = {"_embedded": {"items": [{"id": 1, "name": "a"}, {"id": 2, "name": "b"}]}}
    log_to_file(value, filename=out, data_format="csv", items_path=("_embedded", "items"))

    with out.open("r", encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    assert [r["name"] for r in rows] == ["a", "b"]


def test_log_to_file_csv_append_writes_header_only_once(tmp_path):
    out = tmp_path / "x.csv"
    log_to_file([{"id": 1}], filename=out, data_format="csv", mode="a", csv_include_header=True)
    log_to_file([{"id": 2}], filename=out, data_format="csv", mode="a", csv_include_header=True)

    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0].strip() == "id"
    assert lines.count("id") == 1


def test_extract_by_path_returns_none_on_missing():
    assert _extract_by_path({"a": {"b": 1}}, ("a", "c")) is None
    assert _extract_by_path({"a": [1, 2]}, ("a", 5)) is None


def test_load_payload_file_json_dict(tmp_path):
    p = tmp_path / "p.json"
    p.write_text(json.dumps({"a": 1}), encoding="utf-8")
    assert load_payload_file(str(p)) == {"a": 1}


def test_load_payload_file_json_list_of_dicts(tmp_path):
    p = tmp_path / "p.json"
    p.write_text(json.dumps([{"a": 1}, {"a": 2}]), encoding="utf-8")
    assert load_payload_file(str(p)) == [{"a": 1}, {"a": 2}]


def test_load_payload_file_json_rejects_bad_shape(tmp_path):
    p = tmp_path / "p.json"
    p.write_text(json.dumps([1, 2, 3]), encoding="utf-8")
    with pytest.raises(ValueError):
        load_payload_file(str(p))


def test_load_payload_file_csv(tmp_path):
    p = tmp_path / "p.csv"
    p.write_text("id,name\n1,a\n2,b\n", encoding="utf-8")
    assert load_payload_file(str(p)) == [{"id": "1", "name": "a"}, {"id": "2", "name": "b"}]
