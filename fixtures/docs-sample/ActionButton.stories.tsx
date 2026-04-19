import type { Meta, StoryObj } from '@storybook/react';
import { fn } from 'storybook/test';

import { ActionButton } from './ActionButton';

const meta = {
  title: 'Docs/ActionButton',
  component: ActionButton,
  tags: ['autodocs'],
  args: {
    children: 'Preview',
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
  },
} satisfies Meta<typeof ActionButton>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Brand: Story = {
  args: {
    tone: 'brand',
  },
};
