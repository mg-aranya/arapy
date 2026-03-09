from __future__ import annotations

from pathlib import Path

import arapy.config as legacy_config
from arapy.core.config import Settings, load_settings
from arapy.core.resolver import (
    output_settings,
    payload_for_write_action,
    payload_from_args,
    query_params_for_action,
)
from arapy.core.resolver import (
    resolve_out_path as _resolve_out_path,
)
from arapy.io.output import log_to_file, should_mask_secrets


def _legacy_settings() -> Settings:
    return load_settings()


def resolve_out_path(
    args: dict,
    service: str,
    action: str,
    data_format: str,
    settings: Settings | None = None,
) -> str:
    if args.get("out"):
        return str(Path(args["out"]))

    if settings is not None:
        return _resolve_out_path(args, service, action, data_format, settings)

    log_dir = getattr(legacy_config, "LOG_DIR", None)
    if log_dir is not None:
        base = service.replace("-", "_")
        return str(Path(log_dir) / f"{base}_{action}.{data_format}")

    active_settings = _legacy_settings()
    return _resolve_out_path(args, service, action, data_format, active_settings)


def _payload_from_args(args: dict, excluded_keys: set[str]) -> dict:
    return payload_from_args(args, excluded_keys)


def _call_client_action(cp, action_name: str, *call_args, **call_kwargs):
    modern = getattr(cp, action_name, None)
    if callable(modern):
        return modern(*call_args, **call_kwargs)
    legacy = getattr(cp, f"_{action_name}", None)
    if callable(legacy):
        return legacy(*call_args, **call_kwargs)
    raise AttributeError(f"Client does not implement action '{action_name}'")


def add_handler(cp, token, api_catalog, args, settings: Settings | None = None):
    active_settings = settings or _legacy_settings()
    console, data_format, out_path, csv_fieldnames = output_settings(
        args, active_settings
    )
    mask_secrets = should_mask_secrets(args, active_settings)
    payload = payload_for_write_action(cp, api_catalog, args, "add")

    if isinstance(payload, list):
        result = [
            _call_client_action(cp, "add", api_catalog, token, {**args, **item}, item)
            for item in payload
        ]
    else:
        result = _call_client_action(cp, "add", api_catalog, token, args, payload)

    return log_to_file(
        result,
        filename=out_path,
        data_format=data_format,
        csv_fieldnames=csv_fieldnames,
        also_console=console,
        mask_secrets=mask_secrets,
    )


def delete_handler(cp, token, api_catalog, args, settings: Settings | None = None):
    active_settings = settings or _legacy_settings()
    console, data_format, out_path, csv_fieldnames = output_settings(
        args, active_settings
    )
    mask_secrets = should_mask_secrets(args, active_settings)
    result = _call_client_action(cp, "delete", api_catalog, token, args)
    return log_to_file(
        result,
        filename=out_path,
        data_format=data_format,
        csv_fieldnames=csv_fieldnames,
        also_console=console,
        mask_secrets=mask_secrets,
    )


def get_handler(cp, token, api_catalog, args, settings: Settings | None = None):
    active_settings = settings or _legacy_settings()
    console, data_format, out_path, csv_fieldnames = output_settings(
        args, active_settings
    )
    mask_secrets = should_mask_secrets(args, active_settings)

    if args.get("all"):
        params = query_params_for_action(cp, api_catalog, args, "list")
        result = _call_client_action(
            cp, "list", api_catalog, token, args, params=params
        )
    else:
        params = query_params_for_action(cp, api_catalog, args, "get")
        result = _call_client_action(cp, "get", api_catalog, token, args, params=params)

    return log_to_file(
        result,
        filename=out_path,
        data_format=data_format,
        csv_fieldnames=csv_fieldnames,
        also_console=console,
        mask_secrets=mask_secrets,
    )


def list_handler(cp, token, api_catalog, args, settings: Settings | None = None):
    alias_args = dict(args)
    alias_args["all"] = True
    alias_args["action"] = "list"
    return get_handler(cp, token, api_catalog, alias_args, settings=settings)


def replace_handler(cp, token, api_catalog, args, settings: Settings | None = None):
    active_settings = settings or _legacy_settings()
    console, data_format, out_path, csv_fieldnames = output_settings(
        args, active_settings
    )
    mask_secrets = should_mask_secrets(args, active_settings)
    payload = payload_for_write_action(cp, api_catalog, args, "replace")

    if isinstance(payload, list):
        result = [
            _call_client_action(
                cp, "replace", api_catalog, token, {**args, **item}, item
            )
            for item in payload
        ]
    else:
        result = _call_client_action(cp, "replace", api_catalog, token, args, payload)

    return log_to_file(
        result,
        filename=out_path,
        data_format=data_format,
        csv_fieldnames=csv_fieldnames,
        also_console=console,
        mask_secrets=mask_secrets,
    )


def update_handler(cp, token, api_catalog, args, settings: Settings | None = None):
    active_settings = settings or _legacy_settings()
    console, data_format, out_path, csv_fieldnames = output_settings(
        args, active_settings
    )
    mask_secrets = should_mask_secrets(args, active_settings)
    payload = payload_for_write_action(cp, api_catalog, args, "update")

    if isinstance(payload, list):
        result = [
            _call_client_action(
                cp, "update", api_catalog, token, {**args, **item}, item
            )
            for item in payload
        ]
    else:
        result = _call_client_action(cp, "update", api_catalog, token, args, payload)

    return log_to_file(
        result,
        filename=out_path,
        data_format=data_format,
        csv_fieldnames=csv_fieldnames,
        also_console=console,
        mask_secrets=mask_secrets,
    )


ACTIONS = {
    "add": add_handler,
    "delete": delete_handler,
    "get": get_handler,
    "list": list_handler,
    "replace": replace_handler,
    "update": update_handler,
}

__all__ = [
    "ACTIONS",
    "_payload_from_args",
    "add_handler",
    "delete_handler",
    "get_handler",
    "list_handler",
    "payload_from_args",
    "query_params_for_action",
    "replace_handler",
    "resolve_out_path",
    "update_handler",
]
