import logging

from arapy.logging.setup import AppLogger, LoggerConfig, build_logger_from_env


def test_applogger_is_not_singleton():
    a = AppLogger(LoggerConfig(root_name="t1", console=False))
    b = AppLogger(LoggerConfig(root_name="t2", console=False))
    assert a is not b


def test_get_logger_prefix_and_inheritance():
    mgr = AppLogger(LoggerConfig(root_name="arapytest", console=False))
    child = mgr.get_logger("module")
    assert child.name == "arapytest.module"
    assert child.level == logging.NOTSET
    assert child.propagate is True


def test_set_level_updates_handlers():
    mgr = AppLogger(LoggerConfig(root_name="arapytest2", console=True))
    assert any(
        isinstance(handler, logging.StreamHandler) for handler in mgr.root.handlers
    )
    mgr.set_level(logging.DEBUG)
    assert mgr.root.level == logging.DEBUG
    for handler in mgr.root.handlers:
        assert handler.level == logging.DEBUG


def test_build_logger_from_env_debug_and_file(tmp_path, monkeypatch):
    monkeypatch.setenv("DEBUG", "1")
    log_file = tmp_path / "app.log"
    monkeypatch.setenv("LOG_FILE", str(log_file))

    mgr = build_logger_from_env(root_name="envtest")
    assert mgr.root.level == logging.DEBUG
    assert any(
        isinstance(handler, logging.FileHandler) for handler in mgr.root.handlers
    )
