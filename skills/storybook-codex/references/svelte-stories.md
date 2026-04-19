# Svelte stories

Use this file when creating or updating Storybook stories for Svelte components.

## Preferred shape

If the repo uses `@storybook/addon-svelte-csf`, prefer native `.stories.svelte` files with `defineMeta`.

```svelte
<script module lang="ts">
  import { defineMeta } from '@storybook/addon-svelte-csf';
  import StatusPill from './StatusPill.svelte';

  const { Story } = defineMeta({
    title: 'Components/StatusPill',
    component: StatusPill,
    tags: ['autodocs'],
    args: {
      label: 'Synced',
      tone: 'neutral',
    },
  });
</script>

<Story name="Default" />
<Story name="Brand" args={{ tone: 'brand' }} />
```

## Svelte heuristics

- Follow the repo's current Svelte Storybook setup before introducing `defineMeta`.
- Prefer native `.stories.svelte` when the addon is already installed.
- If the repo already uses `.stories.ts` for Svelte, preserve that pattern instead of forcing a rewrite.
- Keep stories editorial and avoid exhaustive prop permutations.

## Args and interactions

- Keep shared defaults in `defineMeta({ args })`.
- Use named `<Story />` blocks for the states that matter.
- Use explicit `argTypes` for enums or internal props that should be hidden from docs tables.

## Updating existing Svelte stories

- Preserve working decorators, play functions, and story-level docs.
- Replace older Svelte-specific story syntax only when the repo is already moving to native CSF.
- Do not force native Svelte CSF into a repo that is still standardized on `.stories.ts`.
