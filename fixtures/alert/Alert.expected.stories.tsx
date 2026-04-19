import type { Meta, StoryObj } from '@storybook/react';
import { fn } from '@storybook/test';

import { Alert } from './Alert';

const meta = {
  title: 'Fixtures/Alert',
  component: Alert,
  tags: ['autodocs'],
  args: {
    title: 'Deployment queued',
    message: 'Your release will begin in a few minutes.',
    tone: 'info',
    onDismiss: fn(),
  },
  argTypes: {
    tone: {
      control: 'inline-radio',
      options: ['info', 'success', 'danger'],
    },
    onDismiss: {
      control: false,
    },
    className: {
      control: false,
      table: {
        disable: true,
      },
    },
  },
} satisfies Meta<typeof Alert>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Info: Story = {};

export const Success: Story = {
  args: {
    tone: 'success',
    title: 'Deployment finished',
    message: 'Everything shipped cleanly.',
  },
};

export const Danger: Story = {
  args: {
    tone: 'danger',
    title: 'Deployment failed',
    message: 'Rollback started automatically.',
  },
};

export const Dismissible: Story = {
  args: {
    dismissible: true,
  },
};

