# React stories

Use this file when creating a new React Storybook story file or when normalizing an existing one.

## Preferred shape

Use object stories with `Meta` and `StoryObj` from `@storybook/react`.

```ts
import type { Meta, StoryObj } from '@storybook/react';

import { Button } from './Button';

const meta = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
  args: {
    children: 'Press me',
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const Disabled: Story = {
  args: {
    disabled: true,
  },
};
```

## Default heuristics

- Prefer `satisfies Meta<typeof Component>` for type-safe meta objects.
- Use `type Story = StoryObj<typeof meta>`.
- Keep shared defaults in `meta.args`.
- Keep named stories small and legible.
- Favor 3 to 6 good stories over exhaustive matrices.
- Prefer `storybook/test` for `fn`, `userEvent`, `within`, and `expect` when the story needs actions or a `play()` flow.

## Story selection

Use the component API to decide which stories matter:

- one baseline story
- one or two visual variants such as size, tone, or theme
- one or two state variants such as disabled, loading, selected, error, or dismissible
- one interaction story when the component has a meaningful event flow

Avoid generating stories for:

- internal plumbing props
- pass-through DOM props unless the repo already documents them in stories
- every possible prop combination

## Updating existing stories

- Preserve the repo's existing `title` if it fits the local naming convention.
- Preserve useful `parameters`, `decorators`, `play`, and `loaders`.
- Replace `Template.bind({})` only when you are already touching the file.
- Do not delete working docs blocks or test hooks just to make the file look generic.
