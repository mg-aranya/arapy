# netloom v1.8.2

This release turns the ClearPass privilege-aware cache work into the default
CLI experience. The cache now retains the full discovered vendor catalog, but
normal help, completion, and command discovery use a stricter visible view so
the active API client only sees modules and services that are verified or kept
as baseline-visible.

## Highlights

- the ClearPass cache now stores both a default visible catalog and the full
  discovered catalog in the same cache file
- help, completion, and normal catalog-backed command discovery now use the
  visible catalog by default
- `--catalog-view=full` provides an explicit troubleshooting and validation
  path when you need to inspect the retained unfiltered vendor catalog
- the minimal `discovery` profile now validates the intended UX shift cleanly:
  the default module list collapses to only the access-aware visible modules,
  while the full catalog remains available on demand

## Examples

```bash
netloom server use discovery
netloom cache update
netloom ?
netloom --catalog-view=full ?
```

## Notes

- the full retained catalog is still important for troubleshooting, vendor doc
  comparison, and future mapping expansion, so it remains available by opt-in
- further `v1.8.x` work can now focus on expanding verified mappings and, where
  appropriate, tightening action-level visibility inside already-visible
  services
