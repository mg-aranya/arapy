import json
import csv
from pathlib import Path
import io
import os

import pytest

from arapy.io_utils import log_to_file


def test_log_to_file_json_writes_file(tmp_path, capfd):
    p = tmp_path / "out.json"
    data = {"a": 1, "b": [1, 2, 3]}

    log_to_file(data, filename=p, data_format="json", also_console=True)

    # file exists and contains JSON
    text = p.read_text(encoding="utf-8")
    obj = json.loads(text)
    assert obj == data

    # console output printed
    captured = capfd.readouterr()
    assert '"a": 1' in captured.out


def test_log_to_file_raw_bytes(tmp_path, capfd):
    p = tmp_path / "raw.out"
    b = b"hello\n"
    log_to_file(b, filename=p, data_format="raw", also_console=True)

    content = p.read_bytes()
    # Normalize Windows CRLF when running on Windows
    if b"\r\n" in content:
        content = content.replace(b"\r\n", b"\n")
    assert content == b
    captured = capfd.readouterr()
    assert "hello" in captured.out


def test_log_to_file_csv_header_and_append(tmp_path):
    p = tmp_path / "rows.csv"
    rows1 = [{"id": "1", "name": "one"}, {"id": "2", "name": "two"}]
    rows2 = [{"id": "3", "name": "three"}]

    # write initial file
    log_to_file(rows1, filename=p, data_format="csv", csv_fieldnames=["id", "name"], csv_include_header=True, mode="w")
    # append more rows
    log_to_file(rows2, filename=p, data_format="csv", csv_fieldnames=["id", "name"], csv_include_header=True, mode="a")

    with p.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        out = list(reader)

    assert len(out) == 3
    assert out[-1]["name"] == "three"


def test_log_to_file_callable_result(tmp_path):
    p = tmp_path / "call.json"

    def produce():
        return {"x": 5}

    res = log_to_file(produce, filename=p, data_format="json")
    assert res == {"x": 5}
    assert json.loads(p.read_text(encoding="utf-8")) == {"x": 5}
