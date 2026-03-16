from __future__ import annotations

from typing import Any

from netloom.core.config import SECRET_FIELDS
from netloom.core.resolver import normalize_file_payload_for_action

_SECRET_PAYLOAD_FIELDS = ("radius_secret", "tacacs_secret")
_NETWORK_DEVICE_SNMP_FIELDS = ("snmp_read", "snmp_write")


def restore_secret_fields(result, payload, *, mask_secrets: bool):
    if mask_secrets:
        return result

    if isinstance(result, dict) and isinstance(payload, dict):
        restored = dict(result)
        for field in SECRET_FIELDS:
            incoming = payload.get(field)
            if incoming not in (None, "") and restored.get(field) in (None, ""):
                restored[field] = incoming
        return restored

    return result


def _drop_blank_secret_fields(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in payload.items()
        if key not in _SECRET_PAYLOAD_FIELDS or value not in (None, "")
    }


def normalize_copy_payload(
    cp, api_catalog: dict, args: dict[str, Any], action: str, item: dict[str, Any]
) -> dict[str, Any]:
    payload = normalize_file_payload_for_action(cp, api_catalog, args, action, item)
    return _drop_blank_secret_fields(payload)


def _network_device_credentials_present(payload: dict[str, Any]) -> bool:
    for field in _SECRET_PAYLOAD_FIELDS:
        if payload.get(field) not in (None, ""):
            return True
    for field in _NETWORK_DEVICE_SNMP_FIELDS:
        if payload.get(field) not in (None, {}, []):
            return True
    return False


def preflight_error_for_payload(
    module: str, service: str, action_name: str, payload: dict[str, Any] | None
) -> str | None:
    if (
        action_name == "create"
        and module == "policyelements"
        and service == "network-device"
        and isinstance(payload, dict)
        and not _network_device_credentials_present(payload)
    ):
        return (
            "source response did not include usable RADIUS, TACACS+, or SNMP "
            "credentials for network-device create"
        )
    return None
