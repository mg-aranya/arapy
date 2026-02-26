import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def tmp_log_dir(tmp_path, monkeypatch):
    """Patch arapy.config.LOG_DIR (and commands.config.LOG_DIR) to a tmp dir."""
    import arapy.config as config
    import arapy.commands as commands

    monkeypatch.setattr(config, "LOG_DIR", tmp_path, raising=False)
    monkeypatch.setattr(commands.config, "LOG_DIR", tmp_path, raising=False)
    return tmp_path
