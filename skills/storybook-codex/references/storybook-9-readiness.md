# Storybook 9 readiness

Use this file when the repo is on Storybook 8 today but should be ready for Storybook 9-era conventions.

## Current defaults to prefer

- `storybook/test` instead of `@storybook/test`
- object stories with `Meta` and `StoryObj`
- `globalTypes` for toolbar-driven globals
- native Svelte CSF with `defineMeta` when the repo already uses `@storybook/addon-svelte-csf`

## Migration posture

- Do not rewrite working stories just to chase new syntax.
- If you are already touching a story, remove legacy `Template.bind` patterns.
- Keep Storybook config small and framework-local.

## Verification

- make sure imports resolve from the local Storybook version
- ensure play functions still run after migration
- verify addon-a11y and visual test hooks still attach to the right stories
