# Design tokens

Use this file when the repo already has CSS custom properties, Tailwind theme tokens, or Style Dictionary-like outputs and the stories should reflect them.

## Goal

Expose the token dimensions that meaningfully change the component:

- theme
- density
- scale
- color mode

## Workflow

1. Run `python3 skills/storybook-codex/scripts/token_catalog.py <path>` to inventory tokens.
2. Turn the high-signal dimensions into `globalTypes` toolbar controls.
3. Add decorators that read `context.globals` and apply the matching token class or data attribute.
4. Make visual tests cover the token permutations the design system actually supports.

## Good defaults

- `theme`: `light`, `dark`, `system`
- `density`: `comfortable`, `compact`

Do not expose low-level spacing or raw color tokens directly unless the team already wants that UI.
