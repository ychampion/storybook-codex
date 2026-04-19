# Storybook Codex

`storybook-codex` is a plugin-ready Codex package for Storybook work that goes well beyond "write a `.stories.tsx` file."

It gives Codex one focused skill that can:

- create or update React, Vue, and Svelte Storybook stories
- generate dedicated docs pages in `.stories.mdx`
- generate docs-tagged CSF stories with `parameters.docs.description`
- suggest parent-context stories from real component usage
- update only affected stories from git diff signals
- generate Storybook preview decorators from app providers
- generate `args`, selective `argTypes`, controls, and autodocs tags
- scaffold interaction stories with `play()` and `storybook/test`
- suggest accessibility stories instead of treating a11y as an afterthought
- wire visual regression hooks for Chromatic or a local Playwright harness
- detect design tokens and expose theme or density globals
- review existing stories and score Storybook health across a repo
- mirror story structure between frameworks

## What makes this useful

Most Storybook prompts stop at "make a story file." This skill pushes further:

- `story_blueprint.py` is repo-aware, not just prop-aware. It mines usage, co-occurrence, branchy props, interaction flows, a11y lenses, and visual baselines.
- `story_docs.py` turns component APIs and real usage into practical docs pages or docs-tagged stories instead of leaving documentation to hand-written prose.
- `story_composition.py` finds the parent contexts components actually ship inside, then turns those into wrapper-story suggestions.
- `story_diff_update.py` reads git diff output and updates only the stories that were affected by a component API change.
- `storybook_decorators.py` inspects app providers and emits preview decorators or Vue setup hooks instead of forcing teams to hand-roll them again.
- `storybook_audit.py` turns the skill into an ongoing quality system with a Story Health Score.
- `story_sync.py` keeps React, Vue, and Svelte story structures aligned for multi-framework design systems.
- `token_catalog.py` finds CSS-variable and Tailwind-style tokens and suggests Storybook globals for theme and density.
- `tools/fixtures-viewer/` makes the validation contract browsable instead of leaving it buried in JSON.

## What ships

- `.codex-plugin/plugin.json` for plugin packaging
- `skills/storybook-codex/` with the actual Codex skill
- `skills/storybook-codex/scripts/story_blueprint.py` for blueprinting, review mode, and watch mode
- `skills/storybook-codex/scripts/story_docs.py` for docs-mode generation
- `skills/storybook-codex/scripts/story_composition.py` for parent-context story discovery
- `skills/storybook-codex/scripts/story_diff_update.py` for change-aware story maintenance from git diff
- `skills/storybook-codex/scripts/storybook_decorators.py` for `.storybook/preview` scaffolding from provider trees
- `skills/storybook-codex/scripts/storybook_audit.py` for repo-wide Storybook scoring
- `skills/storybook-codex/scripts/story_sync.py` for multi-framework story mirroring
- `skills/storybook-codex/scripts/token_catalog.py` for token-aware globals
- `skills/storybook-codex/references/` for framework rules, docs mode, visual diff, interaction, a11y, token, audit, and Storybook 9 guidance
- `skills/storybook-codex/assets/templates/` for standard stories, docs stories, interaction stories, visual regression specs, token preview config, and library-specific starters
- `fixtures/cases.json` as the machine-readable validation contract
- `fixtures/docs-sample/` as docs-mode sample fixtures
- `tools/fixtures-viewer/` as a browsable UI for that contract
- `scripts/validate_storybook_codex.py` for zero-dependency validation

## Core workflows

### Blueprint a component

```sh
python3 skills/storybook-codex/scripts/story_blueprint.py path/to/Component.tsx
```

Useful flags:

- `--repo-root <path>` to mine usage in the local app
- `--review-story path/to/Component.stories.tsx` to critique an existing story file
- `--watch` to rerun the blueprint while the component changes

### Generate documentation stories

```sh
python3 skills/storybook-codex/scripts/story_docs.py path/to/Component.tsx --style csf
```

or:

```sh
python3 skills/storybook-codex/scripts/story_docs.py path/to/Component.tsx --style mdx
```

Use this when autodocs is too thin and the component needs:

- purpose and anti-pattern guidance
- prop decision guidance
- two or three common usage snippets
- a docs-tagged CSF story or a dedicated `.stories.mdx` page

### Suggest composition stories

```sh
python3 skills/storybook-codex/scripts/story_composition.py path/to/Component.tsx --repo-root path/to/repo
```

Use this when the component only makes sense inside a form, grid, card, dialog, or sidebar context.

### Update stories from git diff

```sh
python3 skills/storybook-codex/scripts/story_diff_update.py . --diff --write
```

Use `--diff-file` in CI or validation when you want the updater to read a saved patch instead of the live repo diff.

### Generate preview decorators

```sh
python3 skills/storybook-codex/scripts/storybook_decorators.py path/to/repo --framework react --format preview
```

This inspects `App.tsx`, `main.tsx`, or `main.ts` and emits the provider tree Storybook needs.

### Audit a Storybook repo

```sh
python3 skills/storybook-codex/scripts/storybook_audit.py path/to/repo --format markdown
```

Use `--fail-under` to turn it into a PR gate.

### Detect design tokens

```sh
python3 skills/storybook-codex/scripts/token_catalog.py path/to/repo
```

### Mirror stories across frameworks

```sh
python3 skills/storybook-codex/scripts/story_sync.py src/Button.stories.tsx --target vue
```

## Fixtures contract

`fixtures/cases.json` is the validation contract for the repo. It covers:

- expected story exports and markers
- template markers
- blueprint expectations
- docs-generator expectations
- composition-story expectations
- decorator preview expectations
- diff-update expectations
- review expectations
- audit expectations
- token catalog expectations
- story sync expectations

The viewer at `tools/fixtures-viewer/index.html` reads that contract and turns it into a quick QA dashboard.

## Roadmap signal

The current release already covers React, Vue, and Svelte story generation. The next layer is deeper parity for docs, composition, diff, and global-decorator flows across Vue and Svelte packages so multi-framework design systems can keep one review standard.

## Example prompts

- `Use $storybook-codex to create stories for src/components/Button.tsx.`
- `Use $storybook-codex to review src/components/Dialog.stories.tsx and raise story health.`
- `Use $storybook-codex to add interaction stories and visual regression coverage for the modal.`
- `Use $storybook-codex to generate a `.stories.mdx` docs page for src/components/ActionButton.tsx.`
- `Use $storybook-codex to add a docs-only story with parameters.docs.description for src/components/InfoPanel.vue.`
- `Use $storybook-codex to suggest composition stories for CheckoutButton from the real checkout flow.`
- `Use $storybook-codex to update stories for changed components from git diff on this branch.`
- `Use $storybook-codex to generate .storybook/preview.tsx decorators from our app providers.`
- `Use $storybook-codex to sync the React stories for Button into the Vue package.`
- `Use $storybook-codex to expose theme and density globals from our design tokens.`
- `Use $storybook-codex to audit this Storybook repo and tell me which components are weak.`

## Library-specific starters

The repo includes focused templates for common design-system stacks:

- shadcn/ui
- Radix UI
- Headless UI

Those templates intentionally cover the awkward parts that generic story generators miss, like `asChild`, compound primitives, focus traps, and render-wrapper stories.

## Storybook 9 posture

The repo now defaults to `storybook/test` instead of `@storybook/test`, keeps object stories first, and includes explicit Storybook 9 readiness guidance so migrations happen while touching real files, not as busywork.

## Try the demo locally

A zero-build demo under [`demo/`](demo/) shows what a developer actually sees after running the skill — live rendered stories, the generated `.stories.*` file, the component source, and the blueprint report, for all six repo fixtures (React, Vue, Svelte).

```sh
python demo/build.py
python -m http.server 8765 --directory demo
```

Open http://localhost:8765. See [demo/README.md](demo/README.md) for details.

## Install locally

Clone the repo and either copy or symlink `skills/storybook-codex` into your Codex skills directory.

Common locations:

- repo-scoped: `.agents/skills/storybook-codex`
- user-scoped: `%USERPROFILE%\\.agents\\skills\\storybook-codex`

If you want the whole plugin package, keep the repository intact so `.codex-plugin/plugin.json`, assets, scripts, and viewer stay together.

## Validation

Run the repository validator from the repo root:

```sh
python3 scripts/validate_storybook_codex.py
```

Platform notes:

- macOS and Linux: use `python3`
- Windows: use `python` or `py -3`

GitHub Actions runs the same validator in CI.

You can inspect docs mode directly:

```sh
python3 skills/storybook-codex/scripts/story_docs.py fixtures/docs-sample/ActionButton.tsx --repo-root fixtures/docs-sample --story-path fixtures/docs-sample/ActionButton.stories.tsx --style mdx
```

## Scope

This repo is intentionally narrow. It is not a generic frontend design skill and it is not a framework-agnostic styling assistant.

It is for Storybook authoring, documentation, review, migration, visual QA, and automation across the UI stacks most design-system teams actually ship today: React, Vue, and Svelte.
