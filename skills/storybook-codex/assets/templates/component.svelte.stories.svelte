<script module lang="ts">
  import { defineMeta } from '@storybook/addon-svelte-csf';

  import __COMPONENT_NAME__ from '__COMPONENT_IMPORT_PATH__';

  const { Story } = defineMeta({
    title: '__STORY_TITLE__',
    component: __COMPONENT_NAME__,
    tags: ['autodocs'],
    args: {
      label: 'Synced',
      tone: 'neutral',
    },
    argTypes: {
      tone: {
        control: 'inline-radio',
        options: ['neutral', 'brand', 'danger'],
      },
    },
  });
</script>

<Story name="Default" />

<Story
  name="Brand"
  args={{
    tone: 'brand',
  }}
/>
