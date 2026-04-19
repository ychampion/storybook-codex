import type { Meta, StoryObj } from '@storybook/react';
import { __COMPONENT_NAME__ } from '__COMPONENT_IMPORT_PATH__';
import { __PARENT_SHELL_NAME__ } from '__PARENT_SHELL_IMPORT_PATH__';

const meta = {
  title: '__TITLE__',
  component: __COMPONENT_NAME__,
  tags: ['autodocs'],
} satisfies Meta<typeof __COMPONENT_NAME__>;

export default meta;
type Story = StoryObj<typeof meta>;

export const InParentContext: Story = {
  render: (args) => (
    <__PARENT_SHELL_NAME__>
      <__COMPONENT_NAME__ {...args} />
    </__PARENT_SHELL_NAME__>
  ),
  args: {
    __PRIMARY_PROP__: '__PRIMARY_VALUE__',
  },
};
