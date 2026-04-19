# Storybook Codex

`storybook-codex` is a plugin-ready Codex package centered on one reusable skill for React Storybook work.

It is designed to help Codex:

- create or update `.stories.tsx` files with modern object-story syntax
- add representative named stories instead of prop cartesian products
- write `args`, selective `argTypes`, and controls that match current Storybook guidance
- apply autodocs at the right level
- scaffold Chromatic only when asked or when a repo is already using it

## Why this is better than a plain prompt

The skill is opinionated in a few places that matter:

- it thinks in `story design lenses`, so it chooses the smallest useful set of stories instead of dumping prop permutations
- it is migration-aware, so existing story files get upgraded without flattening local conventions
- it includes a deterministic `story_blueprint.py` helper to inventory props and suggest controls, docs exposure, and story names before writing files
- it packages plugin metadata and icons so it already looks like a real Codex artifact instead of a loose markdown note

## Public release checklist

This repo is set up to be publishable:

- plugin manifest present
- skill metadata present
- icons present
- deterministic validator present
- CI workflow present
- MIT license present

## What ships in this repo

- `.codex-plugin/plugin.json` for plugin packaging
- `skills/storybook-codex/` with the actual Codex skill
- `references/` guidance split by story authoring, controls/autodocs, and Chromatic
- `assets/templates/` starter files for stories, preview config, and Chromatic
- `skills/storybook-codex/scripts/story_blueprint.py` for deterministic prop-to-story recommendations
- `fixtures/` with representative React components and expected story outputs
- `scripts/validate_storybook_codex.py` for zero-dependency validation

## Skill scope

V1 is intentionally narrow:

- React only
- TypeScript-first `.stories.tsx`
- stable `Meta` + `StoryObj` object stories
- optional Chromatic setup

It does not try to be a general frontend skill or a multi-framework Storybook generator.

## Unique touches

### Story design lenses

The skill explicitly chooses among five lenses:

- baseline
- decision
- state
- boundary
- action

That keeps generated stories more editorial and less robotic.

### Blueprint-first workflow

When a component API is large, the skill can run:

```powershell
python skills/storybook-codex/scripts/story_blueprint.py path/to/Component.tsx
```

That produces a deterministic blueprint with:

- prop inventory
- default args suggestions
- control recommendations
- hidden-prop recommendations
- story-name recommendations by lens

## Example prompts

- `Use $storybook-codex to create stories for src/components/Button.tsx.`
- `Use $storybook-codex to convert src/components/Badge.stories.tsx away from Template.bind and add autodocs.`
- `Use $storybook-codex to add controls for size and tone, but hide internal props.`
- `Use $storybook-codex to scaffold Chromatic for this Storybook repo.`

## Install locally

Clone the repo and either copy or symlink `skills/storybook-codex` into your Codex skills directory.

Common locations:

- repo-scoped: `.agents/skills/storybook-codex`
- user-scoped: `%USERPROFILE%\\.agents\\skills\\storybook-codex`

If you want the whole plugin package, keep the repository intact so `.codex-plugin/plugin.json` and the bundled assets stay together.

## Validation

Run the repository validator from the repo root:

```powershell
python scripts/validate_storybook_codex.py
```

The validator checks the plugin/skill shape and the expected story outputs in `fixtures/`.

You can also inspect the blueprint helper directly:

```powershell
python skills/storybook-codex/scripts/story_blueprint.py fixtures/basic-button/Button.tsx
```

## CI

The repo includes a lightweight validation workflow:

```powershell
python scripts/validate_storybook_codex.py
```

That is the same command used in GitHub Actions.
