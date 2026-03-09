# Changelog

## 1.4.1 - 2026-03-09

### Changed
- removed transitional top-level compatibility wrapper modules
- moved command handlers into `arapy.cli.commands` so the package layout is now fully aligned with the `cli/core/io/logging` split
- cleaned the source release to exclude `.git`, `.env`, cache directories, Python bytecode, and `*.egg-info` artifacts
- updated tests and documentation to target only the v1.4.x module layout

## 1.4.0 - 2026-03-09

### Added
- environment-driven settings loader with XDG-style cache/state/output directories
- new package structure under `cli`, `core`, `io`, and `logging`
- `.env.example` for local configuration
- Ruff linting and formatting baseline in `pyproject.toml`

### Changed
- entrypoint now lives in `arapy.cli.main`
- help rendering moved to `arapy.cli.help`
- completion logic moved to `arapy.cli.completion`
- resolver and request/payload building moved into `arapy.core.resolver`
- response output and file loading split into `arapy.io.output` and `arapy.io.files`
- logger setup is deterministic and no longer depends on singleton initialization order
- cache and response output defaults moved out of the repository tree
- tests now target the action-aware v1.3.1+ API catalog structure

### Removed
- hardcoded ClearPass server and credential values from source control
- in-tree cache/log directory assumptions as the default runtime behavior

## 1.3.1

- action-aware API catalog cache
- parameterized Swagger endpoints preserved in cache
- normalized single `*_id` placeholders to `{id}`
- dynamic help and `list` alias for `get --all`
- configurable secret masking in output
