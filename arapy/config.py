from __future__ import annotations

from arapy.core.config import RESERVED_ARGS, SECRET_FIELDS, load_settings


def refresh_settings():
    settings = load_settings()
    globals().update(
        {
            "SETTINGS": settings,
            "SERVER": settings.server,
            "HTTPS": settings.https_prefix,
            "VERIFY_SSL": settings.verify_ssl,
            "DEFAULT_TIMEOUT": settings.timeout,
            "CONSOLE": settings.console,
            "ENCRYPT_SECRETS": settings.encrypt_secrets,
            "DEFAULT_CSV_FIELDNAMES": settings.default_csv_fieldnames,
            "DEFAULT_FORMAT": settings.default_format,
            "CACHE_DIR": settings.paths.cache_dir,
            "LOG_DIR": settings.paths.response_dir,
            "STATE_DIR": settings.paths.state_dir,
            "APP_LOG_DIR": settings.paths.app_log_dir,
            "RESERVED": RESERVED_ARGS,
            "SECRETS": SECRET_FIELDS,
            "CREDENTIALS": settings.credentials
            if settings.client_id and settings.client_secret
            else {},
        }
    )
    return settings


SETTINGS = refresh_settings()
PROFILES = {}
ACTIVE_PROFILE = None
