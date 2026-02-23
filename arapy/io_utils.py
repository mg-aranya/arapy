#io_utils.py

#---- standard libs
import sys
import json
import csv
import os

DEFAULT_FILENAME = "out.log"

class Tee:
    def __init__(self, filename, mode="w", also_console=False):
        # newline="" is important for CSV correctness on Windows too
        self.file = open(filename, mode, encoding="utf-8", newline="")
        self.original_stdout = sys.stdout
        self.also_console = also_console

        # Used to avoid writing CSV header twice when appending
        try:
            self.is_empty = (self.file.tell() == 0)
        except Exception:
            self.is_empty = False

    def write(self, message):
        if self.also_console:
            self.original_stdout.write(message)
        self.file.write(message)

    def flush(self):
        if self.also_console:
            self.original_stdout.flush()
        self.file.flush()

    def close(self):
        self.file.close()


def log_to_file(
    thing,
    filename=DEFAULT_FILENAME,
    *args,
    also_console=False,
    mode="w",                    
    data_format="json",          # "json" (default) or "csv"
    csv_fieldnames=None,         # optional list of columns
    csv_include_header=True,     # header for CSV
    items_path=("_embedded", "items"),  # v5: configurable path for list extraction
    **kwargs
):
    """
    - default mode="w" (overwrite)
    - data_format: "json" (default) or "csv"
    - items_path: tuple path used to extract rows when data is a dict container
      default: ("_embedded", "items") for ClearPass list endpoints
    """
    ensure_parent_dir(filename)

    if mode not in ("a", "w"):
        raise ValueError("mode must be 'a' or 'w'")
    if data_format not in ("json", "csv", "raw"):
        raise ValueError("data_format must be 'json', 'csv', or 'raw'")

    tee = Tee(filename, mode=mode, also_console=also_console)
    sys.stdout = tee

    try:
        if callable(thing):
            result = thing(*args, **kwargs)
            if result is not None:
                _write_value(result, data_format, tee, csv_fieldnames, csv_include_header, items_path)
            return result

        _write_value(thing, data_format, tee, csv_fieldnames, csv_include_header, items_path)
        return thing

    finally:
        sys.stdout = tee.original_stdout
        tee.close()


def _write_value(value, data_format, tee, csv_fieldnames, csv_include_header, items_path):
    if data_format == "json":
        _write_json(value)
    elif data_format == "csv":
        _write_csv(value, tee, csv_fieldnames, csv_include_header, items_path)
    elif data_format == "raw":
        _write_raw(value)


def _write_json(value):
    if isinstance(value, (dict, list)):
        print(json.dumps(value, indent=2, ensure_ascii=False))
    else:
        print(str(value))


def _write_raw(value):
    if isinstance(value, bytes):
        # decode safely if needed
        try:
            value = value.decode("utf-8")
        except Exception:
            value = str(value)

    # Write exactly as-is
    print(str(value))


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


def _write_csv(value, tee, fieldnames, include_header, items_path):
    """
    CSV rules:
    - If value is a dict and items_path resolves to a list -> write that list
    - If value is already a list -> write it
    - If value is a dict -> write single row
    - Otherwise -> write single column "value"
    """

    rows = None

    # 1) Dict container with items_path (ClearPass default: _embedded.items)
    if isinstance(value, dict) and items_path:
        extracted = _extract_by_path(value, items_path)
        if isinstance(extracted, list):
            rows = extracted

    # 2) If it's a list already
    if rows is None and isinstance(value, list):
        rows = value

    # 3) Single dict -> single row
    if rows is None and isinstance(value, dict):
        rows = [value]

    # 4) Fallback single value
    if rows is None:
        rows = [{"value": value}]

    if not rows:
        return

    # Dict rows -> DictWriter
    if isinstance(rows[0], dict):
        if fieldnames is None:
            fieldnames = list(rows[0].keys())

        writer = csv.DictWriter(
            sys.stdout,
            fieldnames=fieldnames,
            lineterminator="\n",
            extrasaction="ignore",
        )

        # Write header if requested; if appending, only write if file is empty
        if include_header and (mode_is_overwrite_or_empty(tee)):
            writer.writeheader()

        for r in rows:
            writer.writerow(r)

    else:
        # Non-dict rows -> one column
        writer = csv.writer(sys.stdout, lineterminator="\n")
        if include_header and (mode_is_overwrite_or_empty(tee)):
            writer.writerow(["value"])
        for r in rows:
            writer.writerow([r])


def mode_is_overwrite_or_empty(tee: Tee) -> bool:
    """
    In overwrite mode ("w"), file starts empty.
    In append mode ("a"), only write header if file was empty.
    We can detect emptiness via tee.is_empty.
    """
    return tee.is_empty

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