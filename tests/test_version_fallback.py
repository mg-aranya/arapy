import importlib
from unittest.mock import MagicMock
import pytest

import arapy


def test_get_version_falls_back_when_not_installed(monkeypatch):
    # Simulate PackageNotFoundError from importlib.metadata.version
    class _PNF(Exception):
        pass

    monkeypatch.setattr(arapy, "PackageNotFoundError", _PNF, raising=True)
    monkeypatch.setattr(arapy, "_version", lambda name: (_ for _ in ()).throw(_PNF()))
    assert arapy.get_version() == "0.0.0"
