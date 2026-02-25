#commands.py

#---- standard libs
import re
#---- custom libs
from . import config
from .io_utils import log_to_file, load_payload_file


def resolve_out_path(args: dict, service: str, action: str, data_format: str) -> str:
    out_arg = args.get("out")
    if out_arg:
        return out_arg
    # Use centralized output paths; pass ext so templates with trailing '.' get proper extension
    return config.OUTPUT_PATHS.get(service, action, ext=data_format)

def build_payload_from_args(args, reserved_keys):
    payload = {k: v for k, v in args.items() if k not in reserved_keys}
    return payload


# ---- Platform Certificate handlers ----

def handle_cert_sign_request_list(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", "json")
    out_path = resolve_out_path(args, "cert-sign-request", "list", data_format)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))

    csrs = cp.cert_sign_request_list(APIPath, token, offset=offset, limit=limit)

    log_to_file(
        csrs,
        filename=out_path,
        data_format=data_format,
        also_console=verbose,
    )


def handle_cert_trust_list_list(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", "json")
    out_path = resolve_out_path(args, "cert-trust-list", "list", data_format)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))

    items = cp.cert_trust_list_list(APIPath, token, offset=offset, limit=limit)

    log_to_file(
        items,
        filename=out_path,
        data_format=data_format,
        also_console=verbose,
    )


def handle_client_cert_list(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", "json")
    out_path = resolve_out_path(args, "client-cert", "list", data_format)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))

    items = cp.client_cert_list(APIPath, token, offset=offset, limit=limit)

    log_to_file(
        items,
        filename=out_path,
        data_format=data_format,
        also_console=verbose,
    )


def handle_revocation_list_list(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", "json")
    out_path = resolve_out_path(args, "revocation-list", "list", data_format)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))

    items = cp.revocation_list_list(APIPath, token, offset=offset, limit=limit)

    log_to_file(
        items,
        filename=out_path,
        data_format=data_format,
        also_console=verbose,
    )


def handle_self_signed_cert_list(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", "json")
    out_path = resolve_out_path(args, "self-signed-cert", "list", data_format)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))

    items = cp.self_signed_cert_list(APIPath, token, offset=offset, limit=limit)

    log_to_file(
        items,
        filename=out_path,
        data_format=data_format,
        also_console=verbose,
    )


def handle_server_cert_list(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", "json")
    out_path = resolve_out_path(args, "server-cert", "list", data_format)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))

    items = cp.server_cert_list(APIPath, token, offset=offset, limit=limit)

    log_to_file(
        items,
        filename=out_path,
        data_format=data_format,
        also_console=verbose,
    )


def handle_service_cert_list(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", "json")
    out_path = resolve_out_path(args, "service-cert", "list", data_format)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))

    items = cp.service_cert_list(APIPath, token, offset=offset, limit=limit)

    log_to_file(
        items,
        filename=out_path,
        data_format=data_format,
        also_console=verbose,
    )

# ---- Network-device handlers (Policy Elements > Network Device---
def handle_network_device_list(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "network-device", "list", data_format)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))
    sort = args.get("sort", "+id")

    # Validate limit range per API docs (1-1000)
    if limit < 1 or limit > 1000:
        raise ValueError("--limit must be between 1 and 1000")

    # Optional filter and calculate_count
    filter_expr = args.get("filter")
    calc_count_arg = args.get("calculate_count")
    if isinstance(calc_count_arg, str):
        calc_count = calc_count_arg.lower() in ("1", "true", "yes")
    else:
        calc_count = bool(calc_count_arg) if calc_count_arg is not None else None

    devices = cp.network_device_list(APIPath, token, offset=offset, limit=limit, sort=sort, filter=filter_expr, calculate_count=calc_count)

    # Determine CSV fieldnames
    cli_fieldnames = args.get("csv_fieldnames")
    if cli_fieldnames:
        csv_fieldnames = [x.strip() for x in cli_fieldnames.split(",")]
    elif config.DEFAULT_CSV_FIELDNAMES:
        csv_fieldnames = config.DEFAULT_CSV_FIELDNAMES
    else:
        csv_fieldnames = None

    log_to_file(
        devices,
        filename=out_path,
        data_format=data_format,
        csv_fieldnames=csv_fieldnames,
        items_path=("_embedded", "items"),
        also_console=verbose,
    )

def handle_network_device_add(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "network-device", "add", data_format)

    # File-based payload
    if "file" in args:
        payload = load_payload_file(args["file"])

        if isinstance(payload, list):
            results = [cp.network_device_create(APIPath, token, p) for p in payload]
            log_to_file(result, filename=out_path, data_format=data_format, also_console=verbose)
            return

    else:
        reserved = {"help", "version", "verbose", "module", "service", "action", "out", "file", "csv_fieldnames", "id"}
        payload = build_payload_from_args(args, reserved)

    # Required fields for ClearPass network device create (vendor_name optional per API)
    required = ("name", "ip_address")
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise ValueError(
            "network-device add requires: "
            + ", ".join(f"--{k}=..." for k in required)
            + f". Missing: {', '.join(missing)}"
        )

    created = cp.network_device_create(APIPath, token, payload)

    log_to_file(
        created,
        filename=out_path,
        data_format=data_format,
        also_console=verbose,
    )

def handle_network_device_delete(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "network-device", "delete", data_format)

    device_id = args.get("id")
    if not device_id:
        raise ValueError("network-device delete requires --id=<device_id>")

    if not device_id.isdigit():
        raise ValueError("--id must be numeric")

    cp.network_device_delete(APIPath, token, int(device_id))

    result = {
        "deleted_id": int(device_id),
        "status": "ok"
    }

    log_to_file(
        result,
        filename=out_path,
        data_format="json",
        also_console=verbose,
    )

def handle_network_device_get(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", "json")
    out_path = resolve_out_path(args, "network-device", "get", data_format)

    device_id = args.get("id")
    if not device_id:
        raise ValueError("network-device get requires --id=<device_id>")

    if not device_id.isdigit():
        raise ValueError("--id must be numeric")

    result = cp.network_device_get(APIPath, token, device_id=int(device_id))

    log_to_file(
        result,
        filename=out_path,
        data_format="json",
        also_console=verbose,
    )

# ---- Network Device Group handlers (Policy Elements > Network Device Groups) ----
def handle_network_device_group_list(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "network-device-group", "list", data_format)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))
    sort = args.get("sort", "+id")

    if limit < 1 or limit > 1000:
        raise ValueError("--limit must be between 1 and 1000")

    filter_expr = args.get("filter")
    calc_count_arg = args.get("calculate_count")
    if isinstance(calc_count_arg, str):
        calc_count = calc_count_arg.lower() in ("1", "true", "yes")
    else:
        calc_count = bool(calc_count_arg) if calc_count_arg is not None else None

    groups = cp.network_device_group_list(APIPath, token, offset=offset, limit=limit, sort=sort, filter=filter_expr, calculate_count=calc_count)

    cli_fieldnames = args.get("csv_fieldnames")
    if cli_fieldnames:
        csv_fieldnames = [x.strip() for x in cli_fieldnames.split(",")]
    elif config.DEFAULT_CSV_FIELDNAMES:
        csv_fieldnames = config.DEFAULT_CSV_FIELDNAMES
    else:
        csv_fieldnames = None

    log_to_file(
        groups,
        filename=out_path,
        data_format=data_format,
        csv_fieldnames=csv_fieldnames,
        items_path=("_embedded", "items"),
        also_console=verbose,
    )

def handle_network_device_group_get(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", "json")
    out_path = resolve_out_path(args, "network-device-group", "get", data_format)

    group_id = args.get("id")
    if not group_id:
        raise ValueError("network-device-group get requires --id=<group_id>")

    if not group_id.isdigit():
        raise ValueError("--id must be numeric")

    result = cp.network_device_group_get(APIPath, token, group_id=int(group_id))

    log_to_file(
        result,
        filename=out_path,
        data_format="json",
        also_console=verbose,
    )

def handle_network_device_group_add(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = "json"
    out_path = resolve_out_path(args, "network-device-group", "add", data_format)

    if "file" in args:
        payload = load_payload_file(args["file"])
        if isinstance(payload, list):
            results = [cp.network_device_group_create(APIPath, token, p) for p in payload]
            log_to_file(results, filename=out_path, data_format="json", also_console=verbose)
            return
    else:
        reserved = {"help", "version", "verbose", "module", "service", "action", "out", "file"}
        payload = build_payload_from_args(args, reserved)

    required = ("name",)
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise ValueError(f"network-device-group add requires: {', '.join(f'--{k}=...' for k in required)}")

    created = cp.network_device_group_create(APIPath, token, payload)
    log_to_file(created, filename=out_path, data_format="json", also_console=verbose)

def handle_network_device_group_delete(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = "json"
    out_path = resolve_out_path(args, "network-device-group", "delete", data_format)

    group_id = args.get("id")
    if not group_id:
        raise ValueError("network-device-group delete requires --id=<group_id>")

    if not group_id.isdigit():
        raise ValueError("--id must be numeric")

    cp.network_device_group_delete(APIPath, token, int(group_id))

    result = {"deleted_id": int(group_id), "status": "ok"}

    log_to_file(result, filename=out_path, data_format=data_format, also_console=verbose)
# ---- Endpoint handlers ----
def handle_endpoint_list(cp, token, APIPath, args):
    data_format = args.get("data_format", "csv")
    out_path = resolve_out_path(args, "endpoint", "list", data_format)
    verbose = args.get("verbose", False)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))
    sort = args.get("sort", "+id")

    # Validate limit range per API docs (1-1000)
    if limit < 1 or limit > 1000:
        raise ValueError("--limit must be between 1 and 1000")

    filter_expr = args.get("filter")
    calc_count_arg = args.get("calculate_count")
    if isinstance(calc_count_arg, str):
        calc_count = calc_count_arg.lower() in ("1", "true", "yes")
    else:
        calc_count = bool(calc_count_arg) if calc_count_arg is not None else None

    endpoints = cp.endpoint_list(APIPath, token, offset=offset, limit=limit, sort=sort, filter=filter_expr, calculate_count=calc_count)

    cli_fieldnames = args.get("csv_fieldnames")
    if cli_fieldnames:
        csv_fieldnames = [x.strip() for x in cli_fieldnames.split(",")]
    elif config.DEFAULT_CSV_FIELDNAMES:
        csv_fieldnames = config.DEFAULT_CSV_FIELDNAMES
    else:
        csv_fieldnames = None

    log_to_file(
        endpoints,
        filename=out_path,
        data_format="csv",
        csv_fieldnames=csv_fieldnames,
        items_path=("_embedded", "items"),
        also_console=verbose,
    )

def handle_endpoint_get(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    out_path = args.get("out", "./logs/endpoint.json")

    endpoint_id = args.get("id")
    mac = args.get("mac_address")

    if endpoint_id:
        result = cp.endpoint_get(APIPath, token, endpoint_id=int(endpoint_id))
    elif mac:
        result = cp.endpoint_get(APIPath, token, mac_address=mac)
    else:
        raise ValueError("endpoint get requires --id=<id> OR --mac_address=<mac>")

    log_to_file(result, filename=out_path, data_format="json", also_console=verbose)

def handle_endpoint_add(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", "json")
    out_path = resolve_out_path(args, "endpoint", "add", data_format)
    
    if "file" in args:
        payload = load_payload_file(args["file"])
        # allow list or dict
        if isinstance(payload, list):
            results = [cp.endpoint_add(APIPath, token, p) for p in payload]
            log_to_file(results, filename=out_path, data_format="json", also_console=verbose)
            return
    else:
        reserved = {"help", "version", "verbose", "module", "service", "action", "out", "file"}
        payload = build_payload_from_args(args, reserved)

    # Required fields
    required = ("mac_address", "status")
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise ValueError("endpoint add requires " + ", ".join(f"--{k}=..." for k in required))

    # Optional: enforce allowed status values
    allowed = {"Known", "Unknown", "Disabled"}
    if payload["status"] not in allowed:
        raise ValueError(f"status must be one of {sorted(allowed)}")

    # Normalize and validate mac_address format (accept XX:XX:XX:XX:XX:XX, XX-XX-XX-XX-XX-XX, XXXXXXXXXXXX)
    mac = payload.get("mac_address")
    if mac:
        mac_clean = re.sub(r"[^0-9a-fA-F]", "", mac)
        if len(mac_clean) != 12:
            raise ValueError("mac_address must be 12 hex digits (e.g. aa:bb:cc:dd:ee:ff)")
        payload["mac_address"] = ":".join(mac_clean[i : i + 2] for i in range(0, 12, 2)).lower()

    # Parse boolean-like CLI values for randomized_mac if provided
    if "randomized_mac" in payload:
        val = payload["randomized_mac"]
        if isinstance(val, str):
            payload["randomized_mac"] = val.lower() in ("1", "true", "yes", "y")
        else:
            payload["randomized_mac"] = bool(val)

    # Allow device_insight_tags as comma-separated string -> convert to list
    if "device_insight_tags" in payload and isinstance(payload["device_insight_tags"], str):
        tags = [t.strip() for t in payload["device_insight_tags"].split(",") if t.strip()]
        payload["device_insight_tags"] = tags

    created = cp.endpoint_add(APIPath, token, payload)
    log_to_file(created, filename=out_path, data_format="json", also_console=verbose)

def handle_endpoint_delete(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", "json")
    out_path = resolve_out_path(args, "endpoint", "delete", data_format)
    
    endpoint_id = args.get("id")
    mac = args.get("mac_address")

    if endpoint_id:
        cp.endpoint_delete(APIPath, token, endpoint_id=int(endpoint_id))
        result = {"deleted_id": int(endpoint_id), "status": "ok"}
    elif mac:
        cp.endpoint_delete(APIPath, token, mac_address=mac)
        result = {"deleted_mac_address": mac, "status": "ok"}
    else:
        raise ValueError("endpoint delete requires --id=<id> OR --mac_address=<mac>")

    log_to_file(result, filename=out_path, data_format="json", also_console=verbose)

# ---- Device handlers (Identities > Device Accounts) ----

def handle_device_list(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "device", "list", data_format)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))
    sort = args.get("sort", "-id")
    filter_expr = args.get("filter")
    calc_count_arg = args.get("calculate_count")
    if isinstance(calc_count_arg, str):
        calc_count = calc_count_arg.lower() in ("1", "true", "yes")
    else:
        calc_count = bool(calc_count_arg) if calc_count_arg is not None else None

    if limit < 1 or limit > 1000:
        raise ValueError("--limit must be between 1 and 1000")

    devices = cp.device_list(APIPath, token, offset=offset, limit=limit, sort=sort, filter=filter_expr, calculate_count=calc_count)

    cli_fieldnames = args.get("csv_fieldnames")
    csv_fieldnames = [x.strip() for x in cli_fieldnames.split(",")] if cli_fieldnames else None

    log_to_file(devices, filename=out_path, data_format=data_format, csv_fieldnames=csv_fieldnames, also_console=verbose)

def handle_device_add(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "device", "add", data_format)

    if "file" in args:
        payload = load_payload_file(args["file"])
        if isinstance(payload, list):
            results = [cp.device_create(APIPath, token, p) for p in payload]
            log_to_file(results, filename=out_path, data_format=data_format, also_console=verbose)
            return
    else:
        reserved = {"help", "version", "verbose", "module", "service", "action", "out", "file", "csv_fieldnames"}
        payload = build_payload_from_args(args, reserved)

    required = ("mac",)
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise ValueError(f"device add requires: {', '.join(f'--{k}=...' for k in required)}")

    created = cp.device_create(APIPath, token, payload)
    log_to_file(created, filename=out_path, data_format=data_format, also_console=verbose)

def handle_device_delete(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "device", "delete", data_format)

    device_id = args.get("id")
    mac = args.get("mac_address")

    if device_id and device_id.isdigit():
        cp.device_delete(APIPath, token, int(device_id))
        result = {"deleted_id": int(device_id), "status": "ok"}
    elif mac:
        cp.device_delete_by_mac(APIPath, token, mac)
        result = {"deleted_mac": mac, "status": "ok"}
    else:
        raise ValueError("device delete requires --id=<id> OR --mac_address=<mac>")

    log_to_file(result, filename=out_path, data_format=data_format, also_console=verbose)

def handle_device_get(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = "json"
    out_path = resolve_out_path(args, "device", "get", data_format)

    device_id = args.get("id")
    mac = args.get("mac_address")

    if device_id and device_id.isdigit():
        result = cp.device_get(APIPath, token, device_id=int(device_id))
    elif mac:
        result = cp.device_get_by_mac(APIPath, token, mac_address=mac)
    else:
        raise ValueError("device get requires --id=<id> OR --mac_address=<mac>")

    log_to_file(result, filename=out_path, data_format=data_format, also_console=verbose)

# ---- User handlers (Identities > Guest Users) ----

def handle_user_list(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "user", "list", data_format)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))
    sort = args.get("sort", "+id")
    filter_expr = args.get("filter")
    calc_count_arg = args.get("calculate_count")
    if isinstance(calc_count_arg, str):
        calc_count = calc_count_arg.lower() in ("1", "true", "yes")
    else:
        calc_count = bool(calc_count_arg) if calc_count_arg is not None else None

    if limit < 1 or limit > 1000:
        raise ValueError("--limit must be between 1 and 1000")

    users = cp.user_list(APIPath, token, offset=offset, limit=limit, sort=sort, filter=filter_expr, calculate_count=calc_count)
    log_to_file(users, filename=out_path, data_format=data_format, also_console=verbose)

def handle_user_add(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "user", "add", data_format)

    if "file" in args:
        payload = load_payload_file(args["file"])
        if isinstance(payload, list):
            results = [cp.user_create(APIPath, token, p) for p in payload]
            log_to_file(results, filename=out_path, data_format=data_format, also_console=verbose)
            return
    else:
        reserved = {"help", "version", "verbose", "module", "service", "action", "out", "file"}
        payload = build_payload_from_args(args, reserved)

    created = cp.user_create(APIPath, token, payload)
    log_to_file(created, filename=out_path, data_format=data_format, also_console=verbose)

def handle_user_delete(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "user", "delete", data_format)

    user_id = args.get("id")
    if not user_id or not user_id.isdigit():
        raise ValueError("user delete requires --id=<user_id>")

    cp.user_delete(APIPath, token, int(user_id))
    result = {"deleted_id": int(user_id), "status": "ok"}
    log_to_file(result, filename=out_path, data_format=data_format, also_console=verbose)

def handle_user_get(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = "json"
    out_path = resolve_out_path(args, "user", "get", data_format)

    user_id = args.get("id")
    if not user_id or not user_id.isdigit():
        raise ValueError("user get requires --id=<user_id>")

    result = cp.user_get(APIPath, token, int(user_id))
    log_to_file(result, filename=out_path, data_format=data_format, also_console=verbose)

# ---- API Client handlers (Identities > API Clients) ----

def handle_api_client_list(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "api-client", "list", data_format)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))
    sort = args.get("sort", "+id")
    filter_expr = args.get("filter")
    calc_count_arg = args.get("calculate_count")
    if isinstance(calc_count_arg, str):
        calc_count = calc_count_arg.lower() in ("1", "true", "yes")
    else:
        calc_count = bool(calc_count_arg) if calc_count_arg is not None else None

    if limit < 1 or limit > 1000:
        raise ValueError("--limit must be between 1 and 1000")

    clients = cp.api_client_list(APIPath, token, offset=offset, limit=limit, sort=sort, filter=filter_expr, calculate_count=calc_count)
    log_to_file(clients, filename=out_path, data_format=data_format, also_console=verbose)

def handle_api_client_add(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "api-client", "add", data_format)

    if "file" in args:
        payload = load_payload_file(args["file"])
        if isinstance(payload, list):
            results = [cp.api_client_create(APIPath, token, p) for p in payload]
            log_to_file(results, filename=out_path, data_format=data_format, also_console=verbose)
            return
    else:
        reserved = {"help", "version", "verbose", "module", "service", "action", "out", "file"}
        payload = build_payload_from_args(args, reserved)

    required = ("client_id",)
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise ValueError(f"api-client add requires: {', '.join(f'--{k}=...' for k in required)}")

    created = cp.api_client_create(APIPath, token, payload)
    log_to_file(created, filename=out_path, data_format=data_format, also_console=verbose)

def handle_api_client_delete(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "api-client", "delete", data_format)

    client_id = args.get("id")
    if not client_id:
        raise ValueError("api-client delete requires --id=<client_id>")

    cp.api_client_delete(APIPath, token, client_id)
    result = {"deleted_id": client_id, "status": "ok"}
    log_to_file(result, filename=out_path, data_format=data_format, also_console=verbose)

def handle_api_client_get(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "api-client", "get", data_format)

    client_id = args.get("id")
    if not client_id:
        raise ValueError("api-client get requires --id=<client_id>")

    result = cp.api_client_get(APIPath, token, client_id)
    log_to_file(result, filename=out_path, data_format=data_format, also_console=verbose)

# ---- Auth Method handlers (Policy Elements > Auth Methods) ----

def handle_auth_method_list(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "auth-method", "list", data_format)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))
    sort = args.get("sort", "+id")
    filter_expr = args.get("filter")
    calc_count_arg = args.get("calculate_count")
    if isinstance(calc_count_arg, str):
        calc_count = calc_count_arg.lower() in ("1", "true", "yes")
    else:
        calc_count = bool(calc_count_arg) if calc_count_arg is not None else None

    if limit < 1 or limit > 1000:
        raise ValueError("--limit must be between 1 and 1000")

    methods = cp.auth_method_list(APIPath, token, offset=offset, limit=limit, sort=sort, filter=filter_expr, calculate_count=calc_count)
    log_to_file(methods, filename=out_path, data_format=data_format, also_console=verbose)

def handle_auth_method_add(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "auth-method", "add", data_format)

    if "file" in args:
        payload = load_payload_file(args["file"])
        if isinstance(payload, list):
            results = [cp.auth_method_create(APIPath, token, p) for p in payload]
            log_to_file(results, filename=out_path, data_format=data_format, also_console=verbose)
            return
    else:
        reserved = {"help", "version", "verbose", "module", "service", "action", "out", "file"}
        payload = build_payload_from_args(args, reserved)

    required = ("name", "method_type")
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise ValueError(f"auth-method add requires: {', '.join(f'--{k}=...' for k in required)}")

    created = cp.auth_method_create(APIPath, token, payload)
    log_to_file(created, filename=out_path, data_format=data_format, also_console=verbose)

def handle_auth_method_delete(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "auth-method", "delete", data_format)

    method_id = args.get("id")
    if not method_id or not method_id.isdigit():
        raise ValueError("auth-method delete requires --id=<method_id>")

    cp.auth_method_delete(APIPath, token, int(method_id))
    result = {"deleted_id": int(method_id), "status": "ok"}
    log_to_file(result, filename=out_path, data_format=data_format, also_console=verbose)

def handle_auth_method_get(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "auth-method", "get", data_format)

    method_id = args.get("id")
    if not method_id or not method_id.isdigit():
        raise ValueError("auth-method get requires --id=<method_id>")

    result = cp.auth_method_get(APIPath, token, int(method_id))
    log_to_file(result, filename=out_path, data_format=data_format, also_console=verbose)

# ---- Enforcement Profile handlers (Policy Elements > Enforcement Profiles) ----

def handle_enforcement_profile_list(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "enforcement-profile", "list", data_format)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))
    sort = args.get("sort", "+id")
    filter_expr = args.get("filter")
    calc_count_arg = args.get("calculate_count")
    if isinstance(calc_count_arg, str):
        calc_count = calc_count_arg.lower() in ("1", "true", "yes")
    else:
        calc_count = bool(calc_count_arg) if calc_count_arg is not None else None

    if limit < 1 or limit > 1000:
        raise ValueError("--limit must be between 1 and 1000")

    profiles = cp.enforcement_profile_list(APIPath, token, offset=offset, limit=limit, sort=sort, filter=filter_expr, calculate_count=calc_count)
    log_to_file(profiles, filename=out_path, data_format=data_format, also_console=verbose)

def handle_enforcement_profile_get(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)
    out_path = resolve_out_path(args, "enforcement-profile", "get", data_format)

    profile_id = args.get("id")
    if not profile_id or not profile_id.isdigit():
        raise ValueError("enforcement-profile get requires --id=<profile_id>")

    result = cp.enforcement_profile_get(APIPath, token, int(profile_id))
    log_to_file(result, filename=out_path, data_format=data_format, also_console=verbose)

DISPATCH = {
    "policy-elements": {
        "network-device": {
            "list": handle_network_device_list,
            "get": handle_network_device_get,
            "add": handle_network_device_add,
            "delete": handle_network_device_delete,
        },
        "network-device-group": {
            "list": handle_network_device_group_list,
            "get": handle_network_device_group_get,
            "add": handle_network_device_group_add,
            "delete": handle_network_device_group_delete,
        },
        "auth-method": {
            "list": handle_auth_method_list,
            "add": handle_auth_method_add,
            "delete": handle_auth_method_delete,
            "get": handle_auth_method_get,
        },
        "enforcement-profile": {
            "list": handle_enforcement_profile_list,
            "get": handle_enforcement_profile_get,
        },
    },
    "platform-certificates": {
        "cert-sign-request": {
            "list": handle_cert_sign_request_list,
        },
        "cert-trust-list": {
            "list": handle_cert_trust_list_list,
        },
        "client-cert": {
            "list": handle_client_cert_list,
        },
        "revocation-list": {
            "list": handle_revocation_list_list,
        },
        "self-signed-cert": {
            "list": handle_self_signed_cert_list,
        },
        "server-cert": {
            "list": handle_server_cert_list,
        },
        "service-cert": {
            "list": handle_service_cert_list,
        },
    },
    "identities": {
        "endpoint": {
            "list": handle_endpoint_list,
            "get": handle_endpoint_get,
            "add": handle_endpoint_add,
            "delete": handle_endpoint_delete,
        },
        "device": {
            "list": handle_device_list,
            "add": handle_device_add,
            "delete": handle_device_delete,
            "get": handle_device_get,
        },
        "user": {
            "list": handle_user_list,
            "add": handle_user_add,
            "delete": handle_user_delete,
            "get": handle_user_get,
        },
        "api-client": {
            "list": handle_api_client_list,
            "add": handle_api_client_add,
            "delete": handle_api_client_delete,
            "get": handle_api_client_get,
        },
    },
}