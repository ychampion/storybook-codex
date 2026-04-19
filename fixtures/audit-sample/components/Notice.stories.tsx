import type { Meta, StoryObj } from '@storybook/react';
import { fn } from 'storybook/test';

import { Notice } from './Notice';

const meta = {
  title: 'AuditSample/Notice',
  component: Notice,
  tags: ['autodocs'],
  args: {
    title: 'Deployment queued',
    message: 'Your release will begin in a few minutes.',
    onDismiss: fn(),
  },
} satisfies Meta<typeof Notice>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Danger: Story = {
  args: {
    tone: 'danger',
    title: 'Deployment failed',
  },
};
