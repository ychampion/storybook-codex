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

export const Danger: Story = {
  args: {
    tone: 'danger',
    label: 'Risky',
  },
};

export const Selected: Story = {
  args: {
    selected: true,
    label: 'Chosen',
  },
};
