#commands.py

#---- custom libs
from . import config
from .io_utils import log_to_file, load_payload_file

def build_payload_from_args(args, reserved_keys):
    payload = {k: v for k, v in args.items() if k not in reserved_keys}
    return payload

# ---- NAD handlers ----
def handle_nad_list(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    out_path = args.get("out", config.DEFAULT_NAD)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))
    sort = args.get("sort", "+id")

    devices = cp.nad_list(APIPath, token, offset=offset, limit=limit, sort=sort)

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
        filename=out_path + data_format,
        data_format=data_format,
        csv_fieldnames=csv_fieldnames,
        items_path=("_embedded", "items"),
        also_console=verbose,
    )

def handle_nad_add(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    out_path = args.get("out", config.DEFAULT_NAD_CREATED)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)

    # File-based payload
    if "file" in args:
        payload = load_payload_file(args["file"])

        if isinstance(payload, list):
            results = [cp.nad_create(APIPath, token, p) for p in payload]
            log_to_file(
                results,
                filename=out_path + data_format,
                data_format=data_format,
                also_console=verbose)
            return

    else:
        reserved = {"help", "version", "verbose", "module", "service", "action", "out", "file", "csv_fieldnames", "id"}
        payload = build_payload_from_args(args, reserved)

    # Required fields for ClearPass NAD create
    required = ("name", "ip_address", "vendor_name")
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise ValueError(
            "network-device add requires: "
            + ", ".join(f"--{k}=..." for k in required)
            + f". Missing: {', '.join(missing)}"
        )

    created = cp.nad_create(APIPath, token, payload)

    log_to_file(
        created,
        filename=out_path + data_format,
        data_format=data_format,
        also_console=verbose,
    )

def handle_nad_delete(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    out_path = args.get("out", config.DEFAULT_NAD_DELETED)
    data_format = args.get("data_format", config.DEFAULT_FORMAT)

    device_id = args.get("id")
    if not device_id:
        raise ValueError("network-device delete requires --id=<device_id>")

    if not device_id.isdigit():
        raise ValueError("--id must be numeric")

    cp.nad_delete(APIPath, token, int(device_id))

    result = {
        "deleted_id": int(device_id),
        "status": "ok"
    }

    log_to_file(
        result,
        filename=out_path + data_format,
        data_format="json",
        also_console=verbose,
    )
# ---- Endpoint handlers ----
def handle_endpoint_list(cp, token, APIPath, args):
    out_path = args.get("out", config.DEFAULT_ENDPOINT_CSV)
    verbose = args.get("verbose", False)

    offset = int(args.get("offset", 0))
    limit = int(args.get("limit", 25))
    sort = args.get("sort", "+id")

    endpoints = cp.endpoint_list(APIPath, token, offset=offset, limit=limit, sort=sort)

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
    out_path = args.get("out", config.DEFAULT_ENDPOINT_CREATED_JSON)

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

    created = cp.endpoint_add(APIPath, token, payload)
    log_to_file(created, filename=out_path, data_format="json", also_console=verbose)

def handle_endpoint_delete(cp, token, APIPath, args):
    verbose = args.get("verbose", False)
    out_path = args.get("out", config.DEFAULT_ENDPOINT_DELETED_JSON)

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

DISPATCH = {
    "policy-elements": {
        "network-device": {
            "list": handle_nad_list,
            "add": handle_nad_add,
            "delete": handle_nad_delete,
        }
    },
    "identities": {
        "endpoint": {
            "list": handle_endpoint_list,
            "get": handle_endpoint_get,
            "add": handle_endpoint_add,
            "delete": handle_endpoint_delete,
        }
    },
}