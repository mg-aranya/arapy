# netloom v1.7.0

This release establishes the modular `netloom` runtime as the only supported
package layout.

## Highlights

- shared runtime under `netloom/`
- plugin boundary under `netloom/plugins/<plugin>`
- initial ClearPass plugin under `netloom/plugins/clearpass`
- persisted plugin selection with `netloom load <plugin>`
- profile-based server targeting through `~/.config/netloom/`
- packaged completion and manpage assets renamed to `netloom`

## What changed

The CLI is now split into:

- shared logic in `netloom/cli`, `netloom/core`, `netloom/io`, and
  `netloom/logging`
- plugin-specific behavior in `netloom/plugins/clearpass`

The standard workflow is:

```bash
netloom load clearpass
netloom cache update
netloom <module> <service> <action>
```

## Packaging and docs

- updated README for the plugin-based workflow
- updated architecture documentation to reflect the current repo layout
- updated packaged assets to `netloom-completion.bash` and `netloom.1`
- documented `NETLOOM_*` configuration and `~/.config/netloom/`

## Upgrade notes

Recommended setup:

```bash
netloom load clearpass
netloom cache update
```
