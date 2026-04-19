import type { Meta, StoryObj } from '@storybook/react';
import { expect, userEvent, within } from 'storybook/test';

import { Dialog, DialogBackdrop, DialogPanel, DialogTitle } from '__COMPONENT_IMPORT_PATH__';

const meta = {
  title: '__STORY_TITLE__',
  tags: ['autodocs'],
  render: () => (
    <Dialog open onClose={() => undefined}>
      <DialogBackdrop className="fixed inset-0 bg-black/20" />
      <div className="fixed inset-0 flex items-center justify-center">
        <DialogPanel className="rounded-2xl bg-white p-6 shadow-xl">
          <DialogTitle>Leave page?</DialogTitle>
          <p>You have unsaved changes.</p>
          <button type="button">Close</button>
        </DialogPanel>
      </div>
    </Dialog>
  ),
} satisfies Meta;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const FocusTrap: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.tab();
    await expect(canvas.getByRole('button', { name: 'Close' })).toHaveFocus();
  },
};
