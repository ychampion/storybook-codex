import type { Meta, StoryObj } from '@storybook/react';

import { Badge } from './Badge';

const meta = {
  title: 'Legacy/Badge',
  component: Badge,
  tags: ['autodocs'],
  args: {
    label: 'Queued',
    variant: 'soft',
    rounded: true,
  },
  argTypes: {
    variant: {
      control: 'inline-radio',
      options: ['soft', 'solid'],
    },
  },
} satisfies Meta<typeof Badge>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Solid: Story = {
  args: {
    label: 'Live',
    variant: 'solid',
  },
};

export const RoundedOff: Story = {
  args: {
    rounded: false,
  },
};

