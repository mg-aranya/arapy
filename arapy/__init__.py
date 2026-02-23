# arapy/__init__.py
from importlib.metadata import version as _version, PackageNotFoundError

def get_version() -> str:
    """
    Return the installed package version (from pip metadata).
    Falls back to '0.0.0' when running without installation.
    """
    try:
        return _version("arapy")
    except PackageNotFoundError:
        return "0.0.0"