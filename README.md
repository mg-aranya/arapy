# arapy

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)]()
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS-lightgrey.svg)]()
[![License](https://img.shields.io/badge/license-Internal-orange.svg)]()

A modular Python CLI and GUI tool for interacting with the  
**Aruba ClearPass Policy Manager REST API**.

---

## 🚀 Overview

**arapy** provides:

- 🖥️ A powerful **command-line interface** for automation and scripting
- 🧩 A clean, modular architecture for extending ClearPass API support
- 🪟 A lightweight **Tkinter-based GUI** for operators
- 📂 Structured logging with configurable output
- 🔎 Clear and detailed API error reporting

Version: **1.0.0**

---

# ✨ Features (v1.0.0)

## 🔧 Modular Command Architecture

Command structure:

```bash
arapy <module> <service> <action> [--key=value] [-flags]
```

Example:

```bash
arapy policy-elements network-device list --csv_filenames=id,name,ip_address
arapy identities endpoint list --limit=5
```

Internally powered by a centralized `DISPATCH` routing table.

---

## 📦 Supported Modules

### policy-elements

#### network-device
- `list`
- `add`
- `delete`

---

### identities

#### endpoint
- `list`
- `get`
- `add`
- `delete`

---

# 🖥️ CLI Usage

## Network Devices (NAD)

### List
```bash
arapy policy-elements network-device list --limit=10
```

### Add
```bash
arapy policy-elements network-device add \
    --name=nad1 \
    --ip_address=1.2.3.4 \
    --vendor_name=Aruba
```

### Add from file
```bash
arapy policy-elements network-device add --file=devices.csv
arapy policy-elements network-device add --file=devices.json
```

### Delete
```bash
arapy policy-elements network-device delete --id=1234
```

---

## Endpoints

### List
```bash
arapy identities endpoint list --limit=5
```

### Get
```bash
arapy identities endpoint get --id=1234
arapy identities endpoint get --mac_address=aa:bb:cc:dd:ee:ff
```

### Add
```bash
arapy identities endpoint add \
    --mac_address=aa:bb:cc:dd:ee:ff \
    --status=Known
```

### Delete
```bash
arapy identities endpoint delete --id=1234
```

---

# ⚙️ Global Options

| Option | Description |
|--------|------------|
| `--limit=` | Limit API results |
| `--offset=` | Pagination offset |
| `--sort=` | Sorting (e.g. `+id`) |
| `--out=` | Override output file |
| `--file=` | Load payload from JSON or CSV |
| `-vvv` | Verbose mode (print to console) |
| `--help` | Context-aware help |
| `--version` | Show version |

---

# 🪟 GUI Mode

Launch GUI:

```bash
arapy-gui
```

Or:

```bash
arapy gui
```

### GUI Features

- Dropdown selection of:
  - Module
  - Service
  - Action
- Space-separated argument input (`--key=value`)
- Built-in **file picker button** for `--file=`
- Live command output display
- Verbose toggle
- Uses same backend as CLI
- Logs still written to disk

### If Tkinter is missing

```bash
sudo apt install python3-tk
```

---

# 📂 Logging

All commands log output to disk by default.

Default log directory:

```
arapy/arapy/logs/
```

Examples:
- `network_devices.csv`
- `nad_created.json`
- `endpoints.csv`
- `endpoint_deleted.json`

Override output:

```bash
--out=./custom_file.json
```

---

# 🛠 Installation

## Development (editable)
```bash
pip install -e .
```

## Standard install
```bash
pip install .
```

## With GUI support
```bash
pip install .[gui]
```

---

# 🧠 Error Handling

arapy provides detailed HTTP error visibility:

- Status code
- URL
- Method
- Response body
- Request payload (sensitive fields masked)

Example:

```
HTTP 422 Unprocessable Entity
Vendor name is missing
```

---

# 🏗 Architecture

```
arapy/
├── api_endpoints.py
├── clearpass.py
├── commands.py
├── config.py
├── gui.py
├── io_utils.py
├── main.py
├── logs/
└── tests/
```

### Design Principles

- Clean separation of concerns
- Shared handler logic (CLI + GUI)
- Minimal dependencies
- Extensible module/service/action structure
- Production-safe error reporting

---

# 🛣 Roadmap

Future ideas:

- Token caching
- Auto-pagination handling
- Dynamic GUI forms per action
- Expanded ClearPass API coverage
- Standalone binary packaging
- Extended automated testing

---

# 📄 License

Internal / Custom Use  
© Mathias Granlund

---

**arapy v1.0.0**  
A clean, modular ClearPass API toolkit built for automation and operators alike.