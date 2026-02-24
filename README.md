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
- `get`

#### auth-method
- `list`
- `add`
- `delete`
- `get`

#### enforcement-profile
- `list`
- `get`

---

### identities

#### endpoint
- `list`
- `get`  
- `add`
- `delete`

#### device
- `list`
- `add`
- `delete`
- `get`

#### user (Guest Users)
- `list`
- `add`
- `delete`
- `get`

#### api-client
- `list`
- `add`
- `delete`
- `get`

---

# 🖥️ CLI Usage

## Network Devices

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

Filter examples:

```bash
# List endpoints that match a simple JSON filter (URL-encode when running in a shell)
arapy identities endpoint list --filter='{"mac_address":"aa:bb:cc:dd:ee:ff"}' --limit=1

# Request server to calculate total count (slower):
arapy identities endpoint list --filter='{"status":"Known"}' --calculate_count=true --limit=25
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

Additional examples:

```bash
# Add endpoint with device insight tags (comma-separated)
arapy identities endpoint add --mac_address=aa:bb:cc:dd:ee:ff --status=Known --device_insight_tags=printer,office

# Add endpoint with randomized_mac flag (true/false)
arapy identities endpoint add --mac_address=aa:bb:cc:dd:ee:ff --status=Known --randomized_mac=true
```

### Delete
```bash
arapy identities endpoint delete --id=1234
```

---

## Device Accounts (Identities > Device)

### List
```bash
arapy identities device list --limit=10
```

### Add
```bash
arapy identities device add --mac=aa:bb:cc:dd:ee:ff --role_id=1
arapy identities device add --file=devices.json
```

### Delete
```bash
arapy identities device delete --id=123
arapy identities device delete --mac_address=aa:bb:cc:dd:ee:ff
```

### Get
```bash
arapy identities device get --id=123
arapy identities device get --mac_address=aa:bb:cc:dd:ee:ff
```

---

## Guest Users (Identities > User)

### List
```bash
arapy identities user list --limit=25
arapy identities user list --filter='{"role_id":2}'
```

### Add
```bash
arapy identities user add --username=guest1 --password=secret123
arapy identities user add --file=users.json
```

### Delete
```bash
arapy identities user delete --id=5001
```

### Get
```bash
arapy identities user get --id=5001
```

---

## API Clients (Identities > API Clients)

### List
```bash
arapy identities api-client list --limit=10
```

### Add
```bash
arapy identities api-client add --client_id=MyClient --client_secret=secret
arapy identities api-client add --file=api_clients.json
```

### Delete
```bash
arapy identities api-client delete --id=MyClient
```

### Get
```bash
arapy identities api-client get --id=MyClient
```

---

## Authentication Methods (Policy Elements > Auth Method)

### List
```bash
arapy policy-elements auth-method list
arapy policy-elements auth-method list --filter='{"method_type":"Internal"}'
```

### Add
```bash
arapy policy-elements auth-method add --name=MyAuthMethod --method_type=Internal
arapy policy-elements auth-method add --file=auth_methods.json
```

### Delete
```bash
arapy policy-elements auth-method delete --id=123
```

### Get
```bash
arapy policy-elements auth-method get --id=123
```

---

## Enforcement Profiles (Policy Elements > Enforcement Profile)

### List
```bash
arapy policy-elements enforcement-profile list
arapy policy-elements enforcement-profile list --limit=50
```

### Get
```bash
arapy policy-elements enforcement-profile get --id=1001
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
| `--filter=` | Server-side JSON filter expression (URL-encoded) |
| `--calculate_count=` | Request server to calculate total count (`true`/`false`) |

Notes:
- `--filter` accepts a JSON expression according to ClearPass API filter syntax. Example: `--filter='{"name":"edge"}'` (URL-encode when necessary).
- `--calculate_count` requests the API to return the total item count; pass `true` or `false`.
- `--limit` must be an integer between 1 and 1000 (per ClearPass API).

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
- `network_device_created.json`
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