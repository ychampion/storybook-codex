# Storybook Codex — Story Outcomes demo

Static, zero-build demo that shows what a developer actually gets after running the `storybook-codex` skill on a component:

- **Live stories** — every named `Story` export rendered with its `args`.
- **Generated story file** — the `.stories.*` file the skill writes into the repo.
- **Component source** — the input the skill reads.
- **Blueprint** — output of `story_blueprint.py --format markdown` (props, defaults, controls, recommended stories).

## Build and view

From the repo root:

```sh
python demo/build.py
python -m http.server 8765 --directory demo
```

Then open http://localhost:8765.

`build.py` locates the repo root automatically, so it works from other
working directories too.

## Coverage

The demo covers all six repo fixtures: Button, Alert, ThemeBadge, Badge (React), InfoPanel (Vue), and StatusPill (Svelte).
