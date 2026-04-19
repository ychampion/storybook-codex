---
name: storybook-codex
description: Create, review, sync, and audit React, Vue, and Svelte Storybook stories with controls, play functions, visual diff hooks, design-token globals, and optional Chromatic scaffolding. Use when the task mentions Storybook, stories, `.stories.tsx`, `.stories.ts`, `.stories.svelte`, `argTypes`, `CSF`, `play()`, addon-a11y, Chromatic, visual regression, story health, story audit, or syncing stories between frameworks. Do not use for generic UI design, framework-agnostic styling tasks, or non-Storybook component work.
triggers:
  - stories
  - storybook
  - .stories.tsx
  - .stories.ts
  - .stories.svelte
  - argTypes
  - CSF
  - play()
  - Chromatic
  - visual regression
  - story health
---

# Storybook Codex

Create or update React, Vue, and Svelte Storybook stories, then review or audit them when the repo already has Storybook coverage.

Use this skill for Storybook authoring and maintenance across React, Vue, and Svelte:

- React components and `.stories.tsx`
- Vue single-file components and `.stories.ts`
- Svelte components and `.stories.svelte` when the repo uses native Svelte CSF

## Default behavior

1. Inspect the repo before editing anything.
2. Detect the framework, Storybook version, title conventions, preview globals, and existing story style before choosing a format.
3. Prefer updating the local convention over imposing a generic template.
4. Keep stories compact and editorial instead of generating prop cartesian products.
5. Use `storybook/test` for `fn`, `userEvent`, `within`, and `expect` when the story needs action logging or a `play()` flow.

## Built-in modes

### Blueprint mode

Use the blueprint helper when you need deterministic analysis before writing stories.

```sh
python3 skills/storybook-codex/scripts/story_blueprint.py path/to/Component.tsx
```

It can now do more than prop inventory:

- suggest stories by lens
- mine usage signals from the repo
- detect prop co-occurrence clusters
- detect props that gate UI branches
- suggest interaction stories
- suggest accessibility stories
- propose a `visual-regression-codex` capture set

Useful flags:

- `--repo-root <path>` for usage mining
- `--review-story path/to/Component.stories.tsx` for a deterministic story critique
- `--watch` for active component work

### Audit mode

Use the audit helper when the task is "review this Storybook repo" or "gate this PR."

```sh
python3 skills/storybook-codex/scripts/storybook_audit.py path/to/repo --format markdown
```

It reports a Story Health Score and flags:

- missing lens coverage
- missing interaction coverage
- missing accessibility coverage
- missing visual regression coverage
- legacy story syntax
- components that still have no story file

### Token-aware mode

Use the token helper when stories should reflect design tokens or toolbar globals.

```sh
python3 skills/storybook-codex/scripts/token_catalog.py path/to/repo
```

It detects CSS custom properties and Tailwind-style theme tokens, then suggests `globalTypes` for theme and density controls.

### Sync mode

Use story sync when the same component exists in more than one framework.

```sh
python3 skills/storybook-codex/scripts/story_sync.py src/Button.stories.tsx --target vue
```

Mirror the story structure, then adapt only the framework-specific render details.

## Story design lenses

Use these lenses to avoid flat, repetitive story files:

- `Baseline`: the normal default state every component needs.
- `Decision`: size, tone, theme, density, variant, or similar choices.
- `State`: disabled, loading, selected, open, error, dismissible, compact.
- `Boundary`: long content, dense content, empty-ish content, awkward wrapping, or overflow.
- `Action`: `fn()` handlers and `play()` flows.
- `A11y`: keyboard, focus, labeling, and screen-reader-sensitive states.
- `Visual`: stable stories worth snapshotting in Chromatic or Playwright.

Do not force every lens into every component. Use the smallest set that makes the component legible and reviewable.

## Story rules

- Default to the extension that matches the local framework and repo convention.
- Use object stories with `Meta` and `StoryObj` where the framework expects them.
- For Svelte repos using `@storybook/addon-svelte-csf`, prefer native `.stories.svelte` files with `defineMeta` and `<Story />`.
- Do not generate `Template.bind({})`, `ComponentStory`, or other older CSF2 patterns for new work.
- Prefer component-level `args` for shared defaults.
- Add named stories for meaningful states and one interaction story when the component has a real event surface.
- Preserve existing titles, foldering, decorators, loaders, play functions, and docs blocks unless they are clearly obsolete.

## Visual regression and Chromatic

- Only scaffold Chromatic when the user explicitly asks for it or the repo already shows Chromatic usage.
- If the repo wants local baselines, use the Playwright visual template in `assets/templates/visual-regression.spec.ts`.
- Treat `visual-regression-codex` as the mode where story writing and screenshot verification happen together.

## Component library heuristics

- shadcn/ui: hide `asChild`, focus on the local implementation, and keep stories close to the app's real variants.
- Radix UI: write render wrappers for compound primitives and cover `data-state`, keyboard, and focus flows.
- Headless UI: use real composed render trees and explicit focus-trap stories.

## References

- Read [references/react-stories.md](references/react-stories.md) for React story shapes.
- Read [references/vue-stories.md](references/vue-stories.md) for Vue story authoring.
- Read [references/svelte-stories.md](references/svelte-stories.md) for native Svelte CSF.
- Read [references/story-design-lenses.md](references/story-design-lenses.md) when deciding which stories matter.
- Read [references/controls-and-autodocs.md](references/controls-and-autodocs.md) for controls, autodocs, and action args.
- Read [references/interaction-stories.md](references/interaction-stories.md) for `play()` heuristics.
- Read [references/accessibility-stories.md](references/accessibility-stories.md) for a11y stories and WCAG-oriented checks.
- Read [references/visual-diff.md](references/visual-diff.md) for screenshot strategy.
- Read [references/design-tokens.md](references/design-tokens.md) for token-aware toolbars.
- Read [references/multi-framework-sync.md](references/multi-framework-sync.md) for cross-framework parity.
- Read [references/component-library-patterns.md](references/component-library-patterns.md) for shadcn/ui, Radix UI, and Headless UI specifics.
- Read [references/storybook-9-readiness.md](references/storybook-9-readiness.md) when migrating or normalizing story syntax.
- Read [references/storybook-audit.md](references/storybook-audit.md) for repo-wide review and PR gates.
- Use the starter files in [assets/templates](assets/templates/) only as templates. Always adapt them to the local repo.
