import type { Meta, StoryObj } from '@storybook/react';

import { ThemeBadge } from './ThemeBadge';

const meta = {
  title: 'Fixtures/ThemeBadge',
  component: ThemeBadge,
  tags: ['autodocs'],
  args: {
    label: 'Theme ready',
    theme: 'system',
  },
  argTypes: {
    theme: {
      control: 'select',
      options: ['light', 'dark', 'system'],
    },
    className: {
      control: false,
      table: {
        disable: true,
      },
    },
  },
} satisfies Meta<typeof ThemeBadge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const System: Story = {};

export const Light: Story = {
  args: {
    theme: 'light',
  },
};

export const Dark: Story = {
  args: {
    theme: 'dark',
  },
};

export const Selected: Story = {
  args: {
    selected: true,
  },
};

export const Compact: Story = {
  args: {
    compact: true,
  },
};

