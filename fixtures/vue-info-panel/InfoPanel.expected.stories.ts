import type { Meta, StoryObj } from '@storybook/vue3-vite';

import InfoPanel from './InfoPanel.vue';

const meta = {
  title: 'Fixtures/Vue/InfoPanel',
  component: InfoPanel,
  tags: ['autodocs'],
  args: {
    title: 'Release notes available',
    tone: 'info',
    compact: false,
  },
  argTypes: {
    tone: {
      control: 'inline-radio',
      options: ['info', 'success', 'danger'],
    },
    className: {
      control: false,
      table: {
        disable: true,
      },
    },
  },
} satisfies Meta<typeof InfoPanel>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Success: Story = {
  args: {
    tone: 'success',
    title: 'Release published',
  },
};

export const Danger: Story = {
  args: {
    tone: 'danger',
    title: 'Release blocked',
  },
};

export const Compact: Story = {
  args: {
    compact: true,
  },
};
