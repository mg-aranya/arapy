# config.py
"""
Configuration for ClearPass API tool
Keep secrets out of git in real environments (env vars / vault / local override file).
"""

from pathlib import Path

# Package root directory (arapy/)
PACKAGE_DIR = Path(__file__).resolve().parent

# Logs directory inside package
LOG_DIR = PACKAGE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)

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

# ---- NAD files ----
DEFAULT_NAD_CSV = str(LOG_DIR / "network_devices.csv")
DEFAULT_NAD_CREATED_JSON = str(LOG_DIR / "nad_created.json")
DEFAULT_NAD_DELETED_JSON = str(LOG_DIR / "nad_deleted.json")

# ---- Endpoint files ----
DEFAULT_ENDPOINT_CSV = str(LOG_DIR / "endpoints.csv")
DEFAULT_ENDPOINT_CREATED_JSON = str(LOG_DIR / "endpoint_created.json")
DEFAULT_ENDPOINT_DELETED_JSON = str(LOG_DIR / "endpoint_deleted.json")

DEFAULT_CSV_FIELDNAMES = None


PROFILES = {
    "lab": {"SERVER": "192.168.100.30:443", "VERIFY_SSL": False},
    "prod": {"SERVER": "clearpass.company.com:443", "VERIFY_SSL": True},
}
ACTIVE_PROFILE = "lab"