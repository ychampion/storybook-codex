import type { Meta, StoryObj } from '@storybook/react';

import { __COMPONENT_NAME__ } from '__COMPONENT_IMPORT_PATH__';

const meta = {
  title: '__DOCS_TITLE__',
  component: __COMPONENT_NAME__,
  tags: ['autodocs'],
  parameters: {
    docs: {
      description: {
        component:
          '## Purpose\\nDescribe what the component is for.\\n\\n## When to use\\n- Add a short list of recommended uses.\\n\\n## When not to use\\n- Add a short list of anti-patterns.\\n\\n## Prop decision guidance\\n- `tone`: Explain the decision.',
      },
    },
  },
} satisfies Meta<typeof __COMPONENT_NAME__>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Documentation: Story = {
  name: 'Docs',
  parameters: {
    docs: {
      description: {
        story:
          '## Common usage patterns\\nDescribe the two or three most common implementation patterns here.',
      },
      source: {
        code: '<__COMPONENT_NAME__ />',
      },
    },
  },
};
