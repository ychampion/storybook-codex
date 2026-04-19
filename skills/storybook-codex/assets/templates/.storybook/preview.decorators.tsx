import type { Preview } from '@storybook/react';
import { __PROVIDER_ONE__ } from '__PROVIDER_ONE_IMPORT__';
import { __PROVIDER_TWO__ } from '__PROVIDER_TWO_IMPORT__';

const preview: Preview = {
  tags: ['autodocs'],
  decorators: [
    (Story) => (
      <__PROVIDER_ONE__>
        <__PROVIDER_TWO__>
          <Story />
        </__PROVIDER_TWO__>
      </__PROVIDER_ONE__>
    ),
  ],
};

export default preview;
