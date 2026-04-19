import type { Meta, StoryObj } from '@storybook/react';
import { expect, fn, userEvent, within } from 'storybook/test';

import { CheckoutButton } from './CheckoutButton';

const meta = {
  title: 'AuditSample/CheckoutButton',
  component: CheckoutButton,
  tags: ['autodocs'],
  parameters: {
    a11y: {
      test: 'todo',
    },
    chromatic: {
      disableSnapshot: false,
    },
  },
  args: {
    label: 'Pay now',
    onClick: fn(),
  },
} satisfies Meta<typeof CheckoutButton>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Loading: Story = {
  args: {
    loading: true,
  },
};

export const ClickFlow: Story = {
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole('button', { name: 'Pay now' }));
    await expect(args.onClick).toHaveBeenCalled();
  },
};
