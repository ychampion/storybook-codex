---
name: storybook-codex
description: Create, document, compose, update, review, sync, and audit React, Vue, and Svelte Storybook stories with controls, docs pages, docs-tagged story blocks, composition stories, diff-aware updates, play functions, visual diff hooks, design-token globals, provider decorators, and optional Chromatic scaffolding. Use when the task mentions Storybook, stories, `.stories.tsx`, `.stories.ts`, `.stories.svelte`, `.stories.mdx`, `argTypes`, `CSF`, `autodocs`, `parameters.docs.description`, `play()`, addon-a11y, Chromatic, visual regression, story health, story audit, preview decorators, providers, git diff story updates, Storybook component documentation, or syncing stories between frameworks. Do not use for generic UI design, framework-agnostic styling tasks, or non-Storybook component work.
triggers:
  - stories
  - storybook
  - .stories.tsx
  - .stories.ts
  - .stories.svelte
  - .stories.mdx
  - argTypes
  - CSF
  - autodocs
  - parameters.docs.description
  - play()
  - Chromatic
  - visual regression
  - story health
  - preview.tsx
  - decorators
  - providers
  - git diff
---

# Storybook Codex

Create, document, update, review, sync, and audit Storybook work across React, Vue, and Svelte.

Use this skill for Storybook authoring and maintenance across the UI stacks design-system teams actually ship:

- React components and `.stories.tsx`
- Vue single-file components and `.stories.ts`
- Svelte components and `.stories.svelte` when the repo uses native Svelte CSF
- `.stories.mdx` docs pages or docs-tagged CSF stories when autodocs alone is not enough

## Default behavior

1. Inspect the repo before editing anything.
2. Detect the framework, Storybook version, title conventions, preview globals, and existing story style before choosing a format.
3. Detect provider trees, token globals, parent-context usage, and existing docs conventions before generating wrapper stories, docs pages, or preview decorators.
4. If the task needs deterministic analysis before editing, run `story_blueprint.py`.
5. If the task is documentation-heavy, run `story_docs.py`.
6. Prefer updating the local convention over imposing a generic template.
7. Keep stories and docs compact, editorial, and reviewable instead of generating prop cartesian products.
8. Use `storybook/test` for `fn`, `userEvent`, `within`, and `expect` when the story needs action logging or a `play()` flow.

## Built-in modes

### Blueprint mode

Use the blueprint helper when you need deterministic analysis before writing stories.

```sh
python3 skills/storybook-codex/scripts/story_blueprint.py path/to/Component.tsx
```

It can:

- suggest stories by lens
- mine usage signals from the repo
- suggest parent-context composition stories
- detect prop co-occurrence clusters
- detect props that gate UI branches
- suggest interaction stories
- suggest accessibility stories
- propose a `visual-regression-codex` capture set

Useful flags:

- `--repo-root <path>` for usage mining
- `--review-story path/to/Component.stories.tsx` for a deterministic story critique
- `--watch` for active component work

### Docs mode

Use docs mode when autodocs is not enough and the component needs purpose, usage guidance, or implementation snippets.

```sh
python3 skills/storybook-codex/scripts/story_docs.py path/to/Component.tsx
```

Prefer:

- a docs-tagged CSF story when the repo keeps everything in `.stories.tsx` or `.stories.ts`
- a `.stories.mdx` page when the repo already uses docs blocks or when Svelte docs should stay separate from story syntax

Docs mode should:

- reuse the existing story title when possible and append `/Docs`
- mine two or three real usage snippets from the repo before inventing examples
- generate purpose, when-to-use, when-not-to-use, and prop decision guidance
- use `parameters.docs.description` for CSF docs output instead of long comments in the story body

### Composition mode

Use composition mode when the component only makes sense inside a real parent or sibling layout.

```sh
python3 skills/storybook-codex/scripts/story_composition.py path/to/Component.tsx
```

It finds:

- likely parent components that already render the target component
- sibling components that affect spacing or focus order
- literal props that can become `args`
- expression bindings that should move into a render wrapper or fixture state

### Diff mode

Use diff mode when a branch changed component props and the story file should keep up.

```sh
python3 skills/storybook-codex/scripts/story_diff_update.py . --diff --write
```

It can:

- detect changed component files from git diff
- auto-add missing exports for new state or decision props
- append managed diff blocks instead of rewriting the whole file
- flag existing stories that still reference removed or renamed props

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

### Decorator mode

Use decorator mode when Storybook needs the app's provider tree.

```sh
python3 skills/storybook-codex/scripts/storybook_decorators.py path/to/repo --framework react
```

It detects:

- React provider trees from `App.tsx`, `main.tsx`, or `providers.tsx`
- Vue `app.use(...)` plugin chains from `main.ts`
- setup constants like `queryClient` or `pinia`
- preview snippets for `.storybook/preview.tsx` or `.storybook/preview.ts`

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
- Read [references/documentation-stories.md](references/documentation-stories.md) for MDX vs CSF docs decisions and editorial guidance.
- Read [references/interaction-stories.md](references/interaction-stories.md) for `play()` heuristics.
- Read [references/accessibility-stories.md](references/accessibility-stories.md) for a11y stories and WCAG-oriented checks.
- Read [references/visual-diff.md](references/visual-diff.md) for screenshot strategy.
- Read [references/design-tokens.md](references/design-tokens.md) for token-aware toolbars.
- Read [references/composition-stories.md](references/composition-stories.md) for parent-context story heuristics.
- Read [references/change-aware-updates.md](references/change-aware-updates.md) for git diff workflows and managed update blocks.
- Read [references/global-decorators.md](references/global-decorators.md) for provider detection and preview scaffolding.
- Read [references/multi-framework-sync.md](references/multi-framework-sync.md) for cross-framework parity.
- Read [references/component-library-patterns.md](references/component-library-patterns.md) for shadcn/ui, Radix UI, and Headless UI specifics.
- Read [references/storybook-9-readiness.md](references/storybook-9-readiness.md) when migrating or normalizing story syntax.
- Read [references/storybook-audit.md](references/storybook-audit.md) for repo-wide review and PR gates.
- Use the starter files in [assets/templates](assets/templates/) only as templates. Always adapt them to the local repo.
