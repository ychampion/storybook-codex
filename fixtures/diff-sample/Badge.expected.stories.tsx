import type { Meta, StoryObj } from '@storybook/react';
import { Badge } from './Badge';

const meta = {
  title: 'Diff/Badge',
  component: Badge,
  tags: ['autodocs'],
  args: {
    label: 'Ready',
  },
} satisfies Meta<typeof Badge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

// storybook-codex diff: rename warning for `Danger`: `tone` likely became `variant`
export const Danger: Story = {
  args: {
    tone: 'danger',
    label: 'Risky',
  },
};

// storybook-codex diff: deprecated `Selected` because `selected` was removed
export const Selected: Story = {
  args: {
    selected: true,
    label: 'Chosen',
  },
};

/* storybook-codex diff exports:start */
export const Loading: Story = {
  args: {
    loading: true,
  },
  parameters: {
    docs: {
      description: {
        story: 'Auto-added by Storybook Codex from the latest diff for Badge.tsx.',
      },
    },
  },
};
/* storybook-codex diff exports:end */

/* storybook-codex diff notes:start */
- Added story exports: `Loading`.
- `Danger` still references `tone`; likely rename target is `variant`.
- `Selected` still references removed prop `selected`.
/* storybook-codex diff notes:end */
