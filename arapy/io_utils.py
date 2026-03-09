#io_utils.py

#---- standard libs
import json
import csv
import os
from pathlib import Path

#---- custom libs
from . import config
from .logger import AppLogger
log = AppLogger().get_logger(__name__)

def should_mask_secrets(args: dict | None = None) -> bool:
    if not args:
        return bool(config.ENCRYPT_SECRETS)

    if args.get("decrypt"):
        return False

    encrypt = args.get("encrypt")
    if encrypt is None:
        return bool(config.ENCRYPT_SECRETS)

    value = str(encrypt).strip().lower()
    if value in {"enable", "enabled", "true", "1", "yes", "on"}:
        return True
    if value in {"disable", "disabled", "false", "0", "no", "off"}:
        return False
    raise ValueError("--encrypt must be enable or disable")

def sanitize_secrets(value, mask_secrets: bool = True):
    if not mask_secrets:
        return value

    if isinstance(value, dict):
        sanitized = {}
        for key, item in value.items():
            if key in config.SECRETS:
                sanitized[key] = ""
            else:
                sanitized[key] = sanitize_secrets(item, mask_secrets=mask_secrets)
        return sanitized

    if isinstance(value, list):
        return [sanitize_secrets(item, mask_secrets=mask_secrets) for item in value]

    return value

def log_to_file(
    thing,
    filename: str | Path | None = None,
    *args,
    also_console: bool = False,
    mode: str = "w",
    data_format: str = "json",  # "json" (default) or "csv" or "raw"
    csv_fieldnames=None,  # optional list of columns
    csv_include_header: bool = True,  # header for CSV
    items_path=("_embedded", "items"),  # v5: configurable path for list extraction
    mask_secrets: bool = True,
    **kwargs
):
    """
    - default mode="w" (overwrite)
    - data_format: "json" (default) or "csv"
    - items_path: tuple path used to extract rows when data is a dict container
      default: ("_embedded", "items") for ClearPass list endpoints
    """

    if mode not in ("a", "w"):
        raise ValueError("mode must be 'a' or 'w'")
    if data_format not in ("json", "csv", "raw"):
        raise ValueError("data_format must be 'json', 'csv', or 'raw'")

    if filename is None:
        raise ValueError("filename must be provided")

    path = Path(filename)
    ensure_parent_dir(str(path))
    if callable(thing):
        result = thing(*args, **kwargs)
        if result is not None:
            _write_value_to_file(result, path, mode, data_format, csv_fieldnames, csv_include_header, items_path, also_console, mask_secrets)
        return result

    _write_value_to_file(thing, path, mode, data_format, csv_fieldnames, csv_include_header, items_path, also_console, mask_secrets)
    return thing

def _write_value_to_file(value, path: Path, mode: str, data_format: str, csv_fieldnames, csv_include_header, items_path, also_console: bool, mask_secrets: bool):
    path.parent.mkdir(parents=True, exist_ok=True)
    safe_value = sanitize_secrets(value, mask_secrets=mask_secrets)

    if data_format == "json":
        with path.open(mode, encoding="utf-8") as f:
            if isinstance(safe_value, (dict, list)):
                json.dump(safe_value, f, indent=2, ensure_ascii=False)
                f.write("\n")
            else:
                f.write(str(safe_value) + "\n")
            if also_console:
                print(json.dumps(safe_value, indent=2, ensure_ascii=False))

    elif data_format == "raw":
        with path.open(mode, encoding="utf-8") as f:
            if isinstance(safe_value, bytes):
                try:
                    s = safe_value.decode("utf-8")
                except Exception:
                    s = str(safe_value)
            else:
                s = str(safe_value)
            f.write(s)
            if also_console:
                print(s)

    elif data_format == "csv":
        rows = None
        if isinstance(safe_value, dict) and items_path:
            extracted = _extract_by_path(safe_value, items_path)
            if isinstance(extracted, list):
                rows = extracted

        if rows is None and isinstance(safe_value, list):
            rows = safe_value
        if rows is None and isinstance(safe_value, dict):
            rows = [safe_value]
        if rows is None:
            rows = [{"value": safe_value}]

        if not rows:
            return

        append_mode = mode == "a"
        need_header = csv_include_header and (not append_mode or (append_mode and path.stat().st_size == 0))

        with path.open(mode, encoding="utf-8", newline="") as f:
            if isinstance(rows[0], dict):
                fieldnames = csv_fieldnames or list(rows[0].keys())
                writer = csv.DictWriter(
                    f,
                    fieldnames=fieldnames,
                    lineterminator="\n",
                    extrasaction="ignore",
                )

                if need_header:
                    writer.writeheader()
                    if also_console:
                        print(",".join(fieldnames))

                for r in rows:
                    writer.writerow(r)
                    if also_console:
                        print(",".join("" if r.get(k) is None else str(r.get(k)) for k in fieldnames))

            else:
                writer = csv.writer(f, lineterminator="\n")

                if need_header:
                    writer.writerow(["value"])
                    if also_console:
                        print("value")

                for r in rows:
                    writer.writerow([r])
                    if also_console:
                        print(r)
    log.debug(f"Wrote file to {path}")

def _extract_by_path(data, path):
    """
    Extract nested content using a path of keys (strings) and/or indexes (ints).
    Returns None if the path can't be fully resolved.
    """
    cur = data
    for step in path:
        try:
            if isinstance(step, int):
                cur = cur[step]
            else:
                cur = cur[step]
        except (KeyError, IndexError, TypeError):
            return None
    return cur

def ensure_parent_dir(path: str) -> None:
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)

def load_payload_file(filename: str):
    """
    Load a JSON or CSV file and return:
      - dict (single payload) OR
      - list[dict] (multiple payloads)
    """
    ext = os.path.splitext(filename)[1].lower()

    if ext == ".json":
        with open(filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            return data
        if isinstance(data, list) and all(isinstance(x, dict) for x in data):
            return data
        raise ValueError("JSON must contain a dict or a list of dicts.")

    if ext == ".csv":
        with open(filename, "r", encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            return list(reader)

    raise ValueError("Unsupported file type. Use .json or .csv")
