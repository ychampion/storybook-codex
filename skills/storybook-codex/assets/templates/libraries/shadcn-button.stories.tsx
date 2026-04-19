import type { Meta, StoryObj } from '@storybook/react';
import { expect, fn, userEvent, within } from 'storybook/test';

import { Button } from '__COMPONENT_IMPORT_PATH__';

const meta = {
  title: '__STORY_TITLE__',
  component: Button,
  tags: ['autodocs'],
  args: {
    children: 'Continue',
    asChild: false,
    onClick: fn(),
  },
  argTypes: {
    asChild: {
      control: false,
      table: {
        disable: true,
      },
    },
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Pressed: Story = {
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole('button', { name: 'Continue' }));
    await expect(args.onClick).toHaveBeenCalled();
  },
};
