import type { Meta, StoryObj } from '@storybook/vue3-vite';

import __COMPONENT_NAME__ from '__COMPONENT_IMPORT_PATH__';

const meta = {
  title: '__STORY_TITLE__',
  component: __COMPONENT_NAME__,
  tags: ['autodocs'],
  args: {
    title: 'Release notes available',
  },
  argTypes: {
    tone: {
      control: 'inline-radio',
      options: ['info', 'success', 'danger'],
    },
  },
} satisfies Meta<typeof __COMPONENT_NAME__>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Success: Story = {
  args: {
    tone: 'success',
  },
};
