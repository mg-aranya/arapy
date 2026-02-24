# config.py
"""
Configuration for ClearPass API tool
Keep secrets out of git in real environments (env vars / vault / local override file).
"""

from pathlib import Path
import os

# Package root directory (arapy/)
PACKAGE_DIR = Path(__file__).resolve().parent

# Logs directory; allow override via ARAPY_OUT_DIR env var.
# By default we now log to "<current working dir>/logs" so that running
# "arapy ..." in a project will drop files into ./logs/ next to your command.
_env_out = os.environ.get("ARAPY_OUT_DIR")
if _env_out:
    LOG_DIR = Path(_env_out)
else:
    LOG_DIR = Path.cwd() / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ClearPass connection
SERVER = "192.168.100.30:443"
HTTPS = "https://"
VERIFY_SSL = False
DEFAULT_TIMEOUT = 15

# OAuth client credentials
CREDENTIALS = {
    "grant_type": "client_credentials",
    "client_id": "Client2",
    "client_secret": "h6jXPUUZh/GzktMFw0Sr/Is1WeISEwAQF+k7bTFH7393"
}

# Default CSV behaviour
DEFAULT_CSV_FIELDNAMES = None
DEFAULT_FORMAT = "csv"


# Centralized output path helper (preferred over legacy DEFAULT_* constants)
class OutputPaths:
    """
    Helper to centralize and template default output filenames.

    Use `OUTPUT_PATHS.get(service, action, ext=...)` to get a path string.
    Templates may include a trailing '.' to indicate the caller will append
    a data format (e.g. 'network_devices.'). If a template already includes
    an extension, it will be returned as-is.
    """

    templates = {
        # Network devices
        ("network-device", "list"): "network_devices",
        ("network-device", "add"): "network_device_created",
        ("network-device", "delete"): "network_device_deleted",

        # Endpoints (fixed extensions – ignore ext arg)
        ("endpoint", "list"): "endpoints.csv",
        ("endpoint", "add"): "endpoint_created.json",
        ("endpoint", "delete"): "endpoint_deleted.json",

        # Device accounts
        ("device", "list"): "devices",
        ("device", "add"): "device_created",
        ("device", "delete"): "device_deleted",

        # Guest users
        ("user", "list"): "users",
        ("user", "add"): "user_created",
        ("user", "delete"): "user_deleted",

        # API clients
        ("api-client", "list"): "api_clients",
        ("api-client", "add"): "api_client_created",
        ("api-client", "delete"): "api_client_deleted",

        # Auth methods
        ("auth-method", "list"): "auth_methods",
        ("auth-method", "add"): "auth_method_created",
        ("auth-method", "delete"): "auth_method_deleted",

        # Enforcement profiles
        ("enforcement-profile", "list"): "enforcement_profiles",

        # Network device groups
        ("network-device-group", "list"): "network_device_groups",
        ("network-device-group", "add"): "network_device_group_created",
        ("network-device-group", "delete"): "network_device_group_deleted",
        ("network-device-group", "get"): "network_device_group",
    }

    def __init__(self, log_dir: Path = LOG_DIR):
        self.log_dir = log_dir

    def get(self, service: str, action: str, ext: str | None = None) -> str:
        """
        Return an absolute output path for a given service/action.

        Rules:
        - If a template includes an explicit extension (e.g. 'endpoints.csv'),
          it is used as-is and `ext` is ignored.
        - If a template has no dot and `ext` is provided, we append `.{ext}`.
        - If a template has no dot and `ext` is None, we return the bare name.
        - If no template exists, we fall back to '<service>.<ext>' (if ext)
          or just '<service>'.
        """
        tpl = self.templates.get((service, action))
        if tpl:
            # Template has its own extension => ignore ext
            if "." in tpl:
                return str(self.log_dir / tpl)

            # No extension in template: honor caller-provided ext
            if ext:
                return str(self.log_dir / f"{tpl}.{ext}")
            return str(self.log_dir / tpl)

        # fallback: derive a sensible filename
        base = service.replace("-", "_")
        if ext:
            return str(self.log_dir / f"{base}.{ext}")
        return str(self.log_dir / base)


# Single instance for ease of use
OUTPUT_PATHS = OutputPaths(LOG_DIR)


PROFILES = {
    "lab": {"SERVER": "192.168.100.30:443", "VERIFY_SSL": False},
    "prod": {"SERVER": "clearpass.company.com:443", "VERIFY_SSL": True},
}
ACTIVE_PROFILE = "lab"