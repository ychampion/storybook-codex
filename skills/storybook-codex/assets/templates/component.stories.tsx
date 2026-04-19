import type { Meta, StoryObj } from '@storybook/react';
import { fn } from 'storybook/test';

import { __COMPONENT_NAME__ } from '__COMPONENT_IMPORT_PATH__';

const meta = {
  title: '__STORY_TITLE__',
  component: __COMPONENT_NAME__,
  tags: ['autodocs'],
  args: {
    onClick: fn(),
  },
  argTypes: {
    size: {
      control: 'radio',
      options: ['sm', 'md', 'lg'],
    },
  },
} satisfies Meta<typeof __COMPONENT_NAME__>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Disabled: Story = {
  args: {
    disabled: true,
  },
};
