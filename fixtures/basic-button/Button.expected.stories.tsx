import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';

import { Button } from './Button';

const meta = {
  title: 'Fixtures/Button',
  component: Button,
  tags: ['autodocs'],
  args: {
    children: 'Save changes',
    size: 'md',
    tone: 'neutral',
    onClick: fn(),
  },
  argTypes: {
    size: {
      control: 'radio',
      options: ['sm', 'md', 'lg'],
    },
    tone: {
      control: 'inline-radio',
      options: ['neutral', 'brand', 'danger'],
    },
    onClick: {
      control: false,
    },
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Brand: Story = {
  args: {
    tone: 'brand',
  },
};

export const Disabled: Story = {
  args: {
    disabled: true,
  },
};

export const Loading: Story = {
  args: {
    loading: true,
  },
};

export const Large: Story = {
  args: {
    size: 'lg',
  },
};

