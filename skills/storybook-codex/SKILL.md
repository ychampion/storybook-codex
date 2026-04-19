---
name: storybook-codex
description: Create or update React, Vue, and Svelte Storybook stories, controls, autodocs tags, and optional Chromatic scaffolding. Use when the task mentions Storybook, `stories`, `.stories.tsx`, `.stories.ts`, `.stories.svelte`, `argTypes`, `CSF`, Storybook component documentation, or migrating older story patterns to modern object stories. Do not use for generic UI design, framework-agnostic styling tasks, or non-Storybook component work.
---

# Storybook Codex

Use this skill for framework-specific Storybook authoring:

- React components and `.stories.tsx`
- Vue single-file components and `.stories.ts`
- Svelte components and `.stories.svelte` when the repo uses native Svelte CSF

## Default behavior

1. Inspect the repo before editing anything.
2. Detect the framework from the component extension and the local Storybook setup before choosing a story format.
3. Detect existing Storybook config, preview tags, story naming/title conventions, and current component story patterns.
4. If you need a quick prop inventory or story shape suggestion, run `python3 skills/storybook-codex/scripts/story_blueprint.py <component-path>` on macOS/Linux, or `python` / `py -3` on Windows.
5. Prefer updating the local convention over imposing a generic template.
6. Keep stories compact and representative.

## Framework routing

- Read [references/react-stories.md](references/react-stories.md) for React components and `.stories.tsx`.
- Read [references/vue-stories.md](references/vue-stories.md) for Vue single-file components and `.stories.ts`.
- Read [references/svelte-stories.md](references/svelte-stories.md) for Svelte components and `.stories.svelte`.
- If the repo already uses a valid local pattern for the same framework, prefer that pattern over the template files.

## Story design lenses

Use these lenses to avoid flat, repetitive story files:

- `Baseline`: the normal default state every component needs.
- `Decision`: visual choices such as size, tone, variant, or theme.
- `State`: disabled, loading, selected, open, error, dismissible, or compact.
- `Boundary`: long labels, dense content, empty-ish content, or edge-sized values when they materially change the UI.
- `Action`: event handlers, play flows, or interaction surfaces that deserve `fn()` or play coverage.

Do not force every lens into every component. Use the smallest set that makes the component legible and reviewable.

## Story rules

- Default to the extension that matches the local framework and repo convention.
- Use stable object stories with `Meta` and `StoryObj` where the framework expects them.
- Prefer:

```ts
import type { Meta, StoryObj } from '@storybook/react';

const meta = {
  component: Button,
  tags: ['autodocs'],
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;
```

- For Svelte repos using `@storybook/addon-svelte-csf`, prefer native `.stories.svelte` files with `defineMeta` and `<Story />`.
- Do not generate `Template.bind({})`, `ComponentStory`, or other older CSF2 patterns for new work.
- Prefer component-level `args` for shared defaults.
- Add a small set of named stories for meaningful states such as default, disabled, loading, tone, size, or theme.
- Avoid prop cartesian products unless the user explicitly asks for exhaustive coverage.
- Preserve existing titles, foldering, and story names when updating an existing file unless they are clearly broken.

## Controls and autodocs

- Let Storybook infer controls when that is sufficient.
- Add explicit `argTypes` only when inference is weak or the UX is poor.
- Use selective controls for enums, options, colors, dates, ranges, and hidden internal props.
- If the component has event handlers, prefer `fn()` from `@storybook/test` for story args instead of exposing raw function controls.
- If preview-level autodocs already exists, do not duplicate it unnecessarily. Otherwise add `tags: ['autodocs']` on the component story meta.

Read [references/controls-and-autodocs.md](references/controls-and-autodocs.md) when you need the detailed rules.

## Existing story migrations

- Read the existing story first and preserve useful local structure.
- Migrate old story syntax incrementally to object stories instead of rewriting the file blindly.
- Keep repo-specific parameters, decorators, play functions, loaders, and docs blocks unless they are clearly obsolete or incompatible.
- If the repo already uses a different but valid object-story style, follow it.
- When migrating, keep the original intent of each exported story and only rename stories when the old names are genuinely misleading.

## Chromatic

- Only scaffold Chromatic when the user explicitly asks for it or the repo already shows Chromatic usage.
- Prefer `chromatic.config.json` plus a simple GitHub Actions workflow scaffold.
- Keep tokens and project IDs as placeholders or secrets references only.

Read [references/chromatic.md](references/chromatic.md) before writing Chromatic files.

## References

- Read [references/react-stories.md](references/react-stories.md) for the baseline React story shape and story selection heuristics.
- Read [references/vue-stories.md](references/vue-stories.md) for Vue story authoring and slot-aware render patterns.
- Read [references/svelte-stories.md](references/svelte-stories.md) for native Svelte CSF guidance and fallback rules.
- Read [references/story-design-lenses.md](references/story-design-lenses.md) when you need help deciding which stories are actually worth generating.
- Read [references/controls-and-autodocs.md](references/controls-and-autodocs.md) for controls, autodocs, and event-handler guidance.
- Read [references/chromatic.md](references/chromatic.md) for opt-in Chromatic scaffolding rules.
- Use the starter files in [assets/templates](assets/templates/) only as templates. Always adapt them to the local repo.
