# Vue stories

Use this file when creating or updating Storybook stories for Vue single-file components.

## Preferred shape

Use object stories with `Meta` and `StoryObj` from `@storybook/vue3-vite`.

```ts
import type { Meta, StoryObj } from '@storybook/vue3-vite';

import NoticePanel from './NoticePanel.vue';

const meta = {
  title: 'Components/NoticePanel',
  component: NoticePanel,
  tags: ['autodocs'],
  args: {
    title: 'Release notes available',
    tone: 'info',
  },
} satisfies Meta<typeof NoticePanel>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};
export const Success: Story = {
  args: {
    tone: 'success',
  },
};
```

## Vue heuristics

- Prefer direct `component` stories first.
- Add `render` only when slots, wrappers, or compound props make the default render unclear.
- Keep defaults in `meta.args`.
- Use explicit `argTypes` for union props and hidden internal props.

## Slots and wrappers

When the component relies on slots, use `render` to pass them deliberately instead of burying slot content in ad-hoc decorators.

```ts
render: (args) => ({
  components: { NoticePanel },
  setup() {
    return { args };
  },
  template: '<NoticePanel v-bind="args">Preview body</NoticePanel>',
}),
```

## Updating existing Vue stories

- Preserve existing titles, parameters, and decorators when they fit the repo.
- Migrate old CSF2 or custom render wrappers only when you are already touching the file.
- Do not convert slot-heavy stories into generic arg matrices.
