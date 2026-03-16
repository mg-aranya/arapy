```text
 _   _      _   _
| \ | | ___| |_| | ___   ___  _ __ ___
|  \| |/ _ \ __| |/ _ \ / _ \| '_ ` _ \
| |\  |  __/ |_| | (_) | (_) | | | | | |
|_| \_|\___|\__|_|\___/ \___/|_| |_| |_|
```

**Weave your network APIs into one CLI.**

[![Version](https://img.shields.io/badge/version-1.6.4-blue.svg)]()
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)]()
[![Platform](https://img.shields.io/badge/platform-linux%20%7C%20macOS-lightgrey.svg)]()

---

## About netloom

**netloom** is a spec-driven network API CLI for operators and automation engineers. It discovers available API actions from vendor documentation, turns them into a practical command-line interface, and keeps the workflow centered around real operational tasks like listing objects, exporting data, replaying payloads, and copying configuration between environments.

Today, netloom is built first and foremost for **HPE Aruba ClearPass Policy Manager**, with strong support for dynamic API discovery, context-aware help, structured output, profile-based server switching, and cross-environment copy workflows. The longer-term direction is broader: a reusable, spec-driven network API CLI that can grow beyond a single vendor without losing the operator-friendly UX that makes it useful day to day.

## Highlights

- dynamic API discovery through ClearPass `/api-docs`
- a script-friendly CLI for `get`, `list`, `add`, `delete`, `update`, and `replace`
- built-in cross-profile `copy` workflows for migration and dry-run planning
- structured file output for JSON, CSV, or raw responses
- safe handling of secrets in output and logs
- shell completion and context-aware help
- profile-based switching between environments like `dev` and `prod`

Version: **1.6.4**

---

## Recent changes

- introduced a real modular `netloom/` runtime package with shared CLI/core code and plugin-specific code under `netloom/plugins/<plugin>`
- added `netloom load <plugin>` so you can select the active plugin once and then keep using the regular `netloom <module> <service> <action>` syntax
- added the initial `netloom/plugins/clearpass` plugin path for the ClearPass client/copy runtime
- `netloom` now uses `NETLOOM_*` environment/config names by default while still accepting the legacy `ARAPY_*` names during the transition
- added concise inline comments around the less obvious request resolution, catalog discovery, copy planning, and output-handling code paths to make maintenance easier without adding noise to straightforward code
- shell completion now falls back cleanly between `netloom` and `arapy`, which fixes tab completion in setups where only one of the installed executables is directly discoverable by the shell
- hyphenated server profile names such as `qa-edge` now round-trip correctly through profile-scoped config keys like `ARAPY_SERVER_QA_EDGE`
- session tokens are no longer written to debug logs
- Ruff checks now run in CI alongside the existing test/build validation
- `netloom-tool` packaging is now ready for Trusted Publishing to PyPI, including a tagged GitHub Actions publish workflow and an in-repo release checklist
- added the `netloom-install-manpage` helper command while keeping `arapy-install-manpage` available during the transition
- package metadata now uses the modern Python packaging license fields for cleaner builds and PyPI validation
- the project is now branded as `netloom`, with `netloom-tool` as the PyPI package name and `netloom` as the primary CLI command
- the legacy `arapy` command remains available as a compatibility alias during the transition
- the repository and project links now point to `netloom.se` and `github.com/mathias-granlund/netloom`
- explicit `--limit` values on `list`, `get --all`, and `copy` are now honored as requested instead of being overridden by automatic paging
- the bundled Bash completion script now registers completion for both `netloom` and `arapy`

Full release history is kept in [CHANGELOG.md](CHANGELOG.md).

---

## Installation

### Development install

```bash
pip install -e .[dev]
```

If `pip` performs a user install on Linux or macOS, the `netloom` and
`netloom-install-manpage` commands are typically written to `~/.local/bin`.
Make sure that directory is on your `PATH`:

```bash
export PATH="$HOME/.local/bin:$PATH"
```

### Standard install

```bash
pip install netloom-tool
```

Or install directly from GitHub:

```bash
pip install git+https://github.com/mathias-granlund/netloom
```

To build release artifacts locally:

```bash
python -m build
python -m twine check dist/*
```

---

## Required environment variables

Use per-user profile files under `~/.config/netloom/`, or export environment
variables directly in your shell.

```bash
export NETLOOM_SERVER="clearpass.example.com:443"
export NETLOOM_CLIENT_ID="your-client-id"
export NETLOOM_CLIENT_SECRET="your-client-secret"
```

Optional settings:

```bash
export NETLOOM_VERIFY_SSL="true"
export NETLOOM_TIMEOUT="30"
export NETLOOM_LOG_LEVEL="INFO"
export NETLOOM_ENCRYPT_SECRETS="true"
export NETLOOM_API_TOKEN="optional-access-token"
export NETLOOM_API_TOKEN_FILE="/path/to/token.json"
```

Example files are included as `profiles.env.example` and
`credentials.env.example`.

Per-user profile files under `~/.config/netloom/` are the recommended way to
switch between environments like `prod` and `dev` without re-exporting shell
variables on each run.

The preferred naming now uses `netloom` / `NETLOOM_*`, while the legacy
`arapy` / `ARAPY_*` names are still accepted for compatibility during the
transition.

Example `~/.config/netloom/profiles.env`:

```bash
NETLOOM_ACTIVE_PLUGIN=clearpass
NETLOOM_ACTIVE_PROFILE=prod
NETLOOM_PLUGIN_PROD=clearpass
NETLOOM_PLUGIN_DEV=clearpass
NETLOOM_SERVER_PROD="clearpass-prod.example.com:443"
NETLOOM_SERVER_DEV="clearpass-dev.example.com:443"
```

Example `~/.config/netloom/credentials.env`:

```bash
NETLOOM_CLIENT_ID_PROD="prod-client-id"
NETLOOM_CLIENT_SECRET_PROD="prod-client-secret"
NETLOOM_CLIENT_ID_DEV="dev-client-id"
NETLOOM_CLIENT_SECRET_DEV="dev-client-secret"
```

Direct environment variables such as `NETLOOM_SERVER` and `NETLOOM_CLIENT_ID`
still override the profile files when they are set in the current shell.
Legacy `ARAPY_*` variables are still accepted as fallback inputs.

---

## CLI syntax

```bash
netloom <module> <service> list [--key=value] [options]
netloom <module> <service> get [--all] [--key=value] [options]
netloom <module> <service> add|delete|update|replace [--key=value] [options]
netloom copy <module> <service> --from=<profile> --to=<profile> [options]
netloom cache clear|update
netloom load <plugin>
netloom server list|show
netloom server use <profile>
```

Before using vendor-specific modules for the first time, select a plugin:

```bash
netloom load clearpass
```

Examples:

```bash
netloom load clearpass
netloom identities endpoint list --limit=10
netloom policyelements network-device get --all --limit=25
netloom policyelements network-device get --id=1001
netloom policyelements network-device delete --name=switch-01
netloom policyelements network-device update --id=1001 --description="Core switch"
netloom copy policyelements network-device --from=dev --to=prod --all --dry-run
netloom server use prod
netloom server show
```

Both `--log-level` and the legacy `--log_level` style are accepted. The same applies to flags like `--csv-fieldnames` / `--csv_fieldnames`.

Authentication can also be provided per command with:

```bash
netloom identities endpoint list --api-token=your-token
netloom identities endpoint list --token-file=./token.json
```

The legacy `arapy` command still works during the transition, but new examples
and docs use `netloom`.

---

## Global options

| Option | Description |
|---|---|
| `--log-level=LEVEL` | Set logging level |
| `--console` | Print API response to terminal |
| `--limit=N` | Page size for list/get --all requests (1-1000 per request) |
| `--offset=N` | Pagination offset |
| `--sort=+field` | Sort results |
| `--filter=JSON` | Server-side filter applied across all fetched pages |
| `--calculate-count=true/false` | Request total count |
| `--csv-fieldnames=a,b,c` | Fields and order for CSV output |
| `--file=FILE` | Bulk import JSON/CSV |
| `--out=FILE` | Override output file |
| `--api-token=TOKEN` | Use an existing bearer token instead of logging in |
| `--token-file=FILE` | Load a bearer token from JSON or plain text |
| `--help` | Context-aware help |
| `--version` | Show version |
| `--encrypt=enable/disable` | Mask or show secret fields |
| `--decrypt` | Shortcut for showing secrets |

---

## Dynamic API discovery

The active plugin discovers available modules and services at runtime. Today,
the first plugin is ClearPass, which uses:

- `/api-docs`
- `/api/apigility/documentation/<Module-v1>`

The generated cache stores actions as:

```text
module -> service -> action -> {method, paths, params, response metadata, body hints}
```

When the ClearPass docs include Swagger model details, `netloom --help` now renders:

- operation summaries and notes
- response-code lists
- response content types
- generated request body examples and top-level body field descriptions

Download-style endpoints that advertise binary response types are written as raw files automatically, and `netloom` will use the server-provided filename when one is supplied.

To refresh the cache:

```bash
netloom cache clear
netloom cache update
```

---

## Default cache and output locations

v1.4.0 no longer writes cache and response files into the project tree by default.

On Linux/macOS the defaults are:

```text
cache:     ~/.cache/netloom/
state:     ~/.local/state/netloom/
responses: ~/.local/state/netloom/responses/
app logs:  ~/.local/state/netloom/logs/
```

These can be overridden with environment variables such as `NETLOOM_CACHE_DIR`,
`NETLOOM_STATE_DIR`, `NETLOOM_OUT_DIR`, and `NETLOOM_APP_LOG_DIR`. Legacy
`ARAPY_*` path overrides are still accepted during the transition.

---

## Enable tab completion (Bash)
The bundled completion script currently supports both `netloom` and `arapy`.

Run once per session:

```bash
source /path/to/your/repo/scripts/arapy-completion.bash
```

Or to enable permanently, add to `~/.bashrc` then reload terminal:

```bash
mkdir -p ~/.bash_completion.d
cat > ~/.bash_completion.d/netloom <<'EOF'
#!/usr/bin/env bash
source "$HOME/Desktop/Scripts/netloom-main/scripts/arapy-completion.bash"
EOF

if [ -d "$HOME/.bash_completion.d" ]; then
  for f in "$HOME"/.bash_completion.d/*; do
    [ -r "$f" ] && source "$f"
  done
fi

```

For zsh:

```zsh
autoload -Uz bashcompinit
bashcompinit
source /path/to/your/repo/scripts/arapy-completion.bash
```

---

## Architecture

The repository currently keeps both the new modular `netloom/` runtime and the
legacy `arapy/` compatibility package side by side. The high-level source
layout is:

```text
.
|-- CHANGELOG.md
|-- README.md
|-- pyproject.toml
|-- scripts/
|   `-- arapy-completion.bash
|-- examples/
|   |-- network_device_groups_import.json
|   |-- network_devices_import.csv
|   `-- network_devices_import.json
|-- tests/
|   |-- conftest.py
|   |-- test_catalog.py
|   |-- test_clearpass.py
|   |-- test_commands.py
|   |-- test_copy.py
|   |-- test_fuzz.py
|   |-- test_help.py
|   |-- test_integration_cli.py
|   |-- test_io_utils.py
|   |-- test_list_endpoints.py
|   |-- test_logger.py
|   |-- test_main.py
|   |-- test_manpage.py
|   `-- test_profiles.py
|-- netloom/
|   |-- __init__.py
|   |-- __main__.py
|   |-- install_manpage.py
|   |-- cli/
|   |   |-- commands.py
|   |   |-- completion.py
|   |   |-- copy.py
|   |   |-- help.py
|   |   |-- load.py
|   |   |-- main.py
|   |   |-- parser.py
|   |   `-- server.py
|   |-- core/
|   |   |-- config.py
|   |   |-- pagination.py
|   |   |-- plugin.py
|   |   `-- resolver.py
|   |-- io/
|   |   |-- files.py
|   |   `-- output.py
|   |-- logging/
|   |   `-- setup.py
|   `-- plugins/
|       `-- clearpass/
|           |-- catalog.py
|           |-- client.py
|           |-- copy_hooks.py
|           `-- plugin.py
`-- arapy/
    |-- __init__.py
    |-- __main__.py
    |-- install_manpage.py
    |-- cli/
    |   |-- commands.py
    |   |-- completion.py
    |   |-- copy.py
    |   |-- help.py
    |   |-- main.py
    |   |-- parser.py
    |   `-- server.py
    |-- core/
    |   |-- catalog.py
    |   |-- client.py
    |   |-- config.py
    |   |-- pagination.py
    |   `-- resolver.py
    |-- io/
    |   |-- files.py
    |   `-- output.py
    |-- logging/
    |   `-- setup.py
    `-- data/
        `-- man/
            `-- arapy.1
```

---

## Development

Run tests:

```bash
pytest -q
```

Property-based fuzz tests are included in the pytest suite via `hypothesis`,
which is installed as part of:

```bash
pip install -e '.[dev]'
```

Static operator documentation is also available as a bundled man page:

```bash
man -l man/arapy.1
```

To install the bundled man page for normal `man arapy` usage:

```bash
netloom-install-manpage
man arapy
```

The legacy `arapy-install-manpage` helper still works, and the bundled manpage
name remains `arapy` during this first transition stage.

If your system does not already search `~/.local/share/man`, add it to `MANPATH`.

## Server profiles

Use the built-in server profile commands to inspect and switch the active
plugin/profile target:

```bash
netloom load clearpass
netloom server list
netloom server show
netloom server use prod
netloom server use dev
```

`netloom load <plugin>` updates `NETLOOM_ACTIVE_PLUGIN` in
`~/.config/netloom/profiles.env`. `netloom server use <profile>` updates
`NETLOOM_ACTIVE_PROFILE`. The next `netloom` command then resolves
profile-scoped values such as `NETLOOM_PLUGIN_PROD`, `NETLOOM_SERVER_PROD`, and
`NETLOOM_CLIENT_SECRET_PROD` automatically.

---

## Packaging

`netloom` now includes the baseline pieces expected from a releasable Python package:

- explicit project metadata, classifiers, and project URLs in `pyproject.toml`
- a packaged license file
- wheel and sdist support for the bundled man page
- a `MANIFEST.in` for predictable source distributions
- build validation via `python -m build` and `python -m twine check`
- CI coverage for tests and distribution validation on supported Python versions
- Trusted Publishing-ready GitHub Actions for tagged PyPI releases

Run lint and formatting:

```bash
ruff check .
ruff format .
```

For the release checklist and Trusted Publishing setup steps, see
[RELEASING.md](RELEASING.md).

---

## License

Proprietary / Internal Use  
See [LICENSE](LICENSE).
