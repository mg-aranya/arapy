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

# ---- Network device files ----
DEFAULT_NETWORK_DEVICE = str(LOG_DIR / "network_devices.")
DEFAULT_NETWORK_DEVICE_CREATED = str(LOG_DIR / "network_device_created.")
DEFAULT_NETWORK_DEVICE_DELETED = str(LOG_DIR / "network_device_deleted.")

# ---- Endpoint files ----
DEFAULT_ENDPOINT_CSV = str(LOG_DIR / "endpoints.csv")
DEFAULT_ENDPOINT_CREATED_JSON = str(LOG_DIR / "endpoint_created.json")
DEFAULT_ENDPOINT_DELETED_JSON = str(LOG_DIR / "endpoint_deleted.json")

# ---- Device files ----
DEFAULT_DEVICE = str(LOG_DIR / "devices.")
DEFAULT_DEVICE_CREATED = str(LOG_DIR / "device_created.")
DEFAULT_DEVICE_DELETED = str(LOG_DIR / "device_deleted.")

# ---- User files ----
DEFAULT_USER = str(LOG_DIR / "users.")
DEFAULT_USER_CREATED = str(LOG_DIR / "user_created.")
DEFAULT_USER_DELETED = str(LOG_DIR / "user_deleted.")

# ---- API Client files ----
DEFAULT_API_CLIENT = str(LOG_DIR / "api_clients.")
DEFAULT_API_CLIENT_CREATED = str(LOG_DIR / "api_client_created.")
DEFAULT_API_CLIENT_DELETED = str(LOG_DIR / "api_client_deleted.")

# ---- Auth Method files ----
DEFAULT_AUTH_METHOD = str(LOG_DIR / "auth_methods.")
DEFAULT_AUTH_METHOD_CREATED = str(LOG_DIR / "auth_method_created.")
DEFAULT_AUTH_METHOD_DELETED = str(LOG_DIR / "auth_method_deleted.")

# ---- Enforcement Profile files ----
DEFAULT_ENFORCEMENT_PROFILE = str(LOG_DIR / "enforcement_profiles.")

DEFAULT_CSV_FIELDNAMES = None
DEFAULT_FORMAT = "csv"


PROFILES = {
    "lab": {"SERVER": "192.168.100.30:443", "VERIFY_SSL": False},
    "prod": {"SERVER": "clearpass.company.com:443", "VERIFY_SSL": True},
}
ACTIVE_PROFILE = "lab"