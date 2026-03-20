# netloom v1.9.0

This release adds the first read-only service comparison workflow with
`netloom <module> <service> diff --from=SOURCE --to=TARGET`. It is designed as
the companion to `copy`: same selector model, same match behavior, but focused
on showing what differs before any change is applied.

## Highlights

- added a service-level `diff` action for comparing one service between two
  named profiles
- broad selectors like `--all` and `--filter` now produce symmetric reports
  with `same`, `different`, `only_in_source`, and `only_in_target`
- narrow selectors like `--id` and `--name` stay source-scoped for targeted
  checks
- each diff run writes a timestamped JSON report under `NETLOOM_OUT_DIR`
  unless `--out` is set explicitly
- providers can now normalize objects before comparison so response-only noise
  does not create false diffs

## Examples

```bash
netloom policyelements role diff --from=lab --to=prod --all
netloom policyelements role diff --from=lab --to=prod --name=Guest
netloom policyelements role diff --from=lab --to=prod --filter=name:contains:GUEST
```

## Notes

- `diff` is available as a service action only; there is no built-in
  `netloom diff ...` alias
- `copy` keeps its existing behavior and now shares selector and match helpers
  with `diff`
- ClearPass applies conservative diff normalization to ignore ids, links,
  timestamps, and similar response metadata where that would otherwise create
  false positives
