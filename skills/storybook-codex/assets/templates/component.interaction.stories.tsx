import type { Meta, StoryObj } from '@storybook/react';
import { expect, fn, userEvent, within } from 'storybook/test';

import { __COMPONENT_NAME__ } from '__COMPONENT_IMPORT_PATH__';

const meta = {
  title: '__STORY_TITLE__',
  component: __COMPONENT_NAME__,
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
    onClick: fn(),
  },
} satisfies Meta<typeof __COMPONENT_NAME__>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const ClickFlow: Story = {
  play: async ({ args, canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole('button'));
    await expect(args.onClick).toHaveBeenCalled();
  },
};
