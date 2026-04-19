# Storybook Codex

`storybook-codex` is a plugin-ready Codex package centered on one reusable skill for React, Vue, and Svelte Storybook work.

It is designed to help Codex:

- create or update `.stories.tsx` files with modern object-story syntax
- create or update Vue `.stories.ts` files with modern object-story syntax
- create or update Svelte `.stories.svelte` files when the repo uses native Svelte CSF
- add representative named stories instead of prop cartesian products
- write `args`, selective `argTypes`, and controls that match current Storybook guidance
- apply autodocs at the right level
- scaffold Chromatic only when asked or when a repo is already using it

## Why this is better than a plain prompt

The skill is opinionated in a few places that matter:

- it thinks in `story design lenses`, so it chooses the smallest useful set of stories instead of dumping prop permutations
- it is migration-aware, so existing story files get upgraded without flattening local conventions
- it is framework-aware, so React, Vue, and Svelte repos each get the story format that fits the local Storybook setup
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
- `references/` guidance split by React, Vue, Svelte, controls/autodocs, story selection, and Chromatic
- `assets/templates/` starter files for React, Vue, and Svelte stories plus preview config and Chromatic
- `skills/storybook-codex/scripts/story_blueprint.py` for deterministic prop-to-story recommendations
- `fixtures/` with representative React components and expected story outputs
- `fixtures/cases.json` as the machine-readable validation contract for expected stories, markers, templates, and blueprint behavior
- `scripts/validate_storybook_codex.py` for zero-dependency validation

## Skill scope

V2 keeps the scope intentional:

- React `.stories.tsx`
- Vue `.stories.ts`
- Svelte `.stories.svelte` when the repo uses `@storybook/addon-svelte-csf`
- TypeScript-first story files
- stable `Meta` + `StoryObj` object stories where the framework expects them
- optional Chromatic setup

It still does not try to be a general frontend skill or a generic design generator. The V2 scope is Storybook authoring for the three frameworks most likely to share design-system components.

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

```sh
python3 skills/storybook-codex/scripts/story_blueprint.py path/to/Component.tsx
```

That produces a deterministic blueprint with:

- prop inventory
- default args suggestions
- control recommendations
- hidden-prop recommendations
- story-name recommendations by lens

The same helper now accepts `.tsx`, `.vue`, and `.svelte` component files when props are expressed in a typed props block or a supported framework-native prop declaration.

## Example prompts

- `Use $storybook-codex to create stories for src/components/Button.tsx.`
- `Use $storybook-codex to create stories for src/components/StatusPanel.vue.`
- `Use $storybook-codex to create native Svelte stories for src/lib/StatusPill.svelte.`
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

```sh
python3 scripts/validate_storybook_codex.py
```

Use `python3` on macOS/Linux. On Windows, use `python` or `py -3`.

The validator checks the plugin/skill shape and the expected story outputs in `fixtures/`.
`fixtures/cases.json` is the contract file that maps each fixture to its required story exports, control markers, template expectations, and blueprint assertions.

A shortened example:

```json
{
  "stories": [
    {
      "name": "basic-button",
      "requiredStories": ["Default", "Brand", "Disabled", "Loading", "Large"]
    },
    {
      "name": "vue-info-panel",
      "requiredStories": ["Default", "Success", "Danger", "Compact"]
    },
    {
      "name": "svelte-status-pill",
      "requiredStories": ["Default", "Brand", "Danger", "Selected", "Compact"]
    }
  ],
  "blueprints": [
    {
      "name": "button-blueprint",
      "expectedStories": ["Default", "Brand", "Disabled", "Loading", "LongContent"]
    }
  ]
}
```

You can also inspect the blueprint helper directly:

```sh
python3 skills/storybook-codex/scripts/story_blueprint.py fixtures/basic-button/Button.tsx
```

## CI

The repo includes a lightweight validation workflow:

```sh
python3 scripts/validate_storybook_codex.py
```

Use `python3` locally on macOS/Linux and `python` or `py -3` on Windows. GitHub Actions runs the same validator inside the workflow environment.
