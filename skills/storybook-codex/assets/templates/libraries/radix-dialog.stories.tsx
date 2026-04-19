import type { Meta, StoryObj } from '@storybook/react';
import { expect, userEvent, within } from 'storybook/test';

import * as Dialog from '__COMPONENT_IMPORT_PATH__';

const meta = {
  title: '__STORY_TITLE__',
  tags: ['autodocs'],
  parameters: {
    chromatic: {
      disableSnapshot: false,
    },
  },
  render: () => (
    <Dialog.Root>
      <Dialog.Trigger>Open dialog</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay />
        <Dialog.Content>
          <Dialog.Title>Invite teammate</Dialog.Title>
          <Dialog.Description>Send access to the design system.</Dialog.Description>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  ),
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Opened: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole('button', { name: 'Open dialog' }));
    await expect(canvas.getByText('Invite teammate')).toBeInTheDocument();
  },
};
