<script module lang="ts">
  import { defineMeta } from '@storybook/addon-svelte-csf';

  import StatusPill from './StatusPill.svelte';

  const { Story } = defineMeta({
    title: 'Fixtures/Svelte/StatusPill',
    component: StatusPill,
    tags: ['autodocs'],
    args: {
      label: 'Synced',
      tone: 'neutral',
      selected: false,
      compact: false,
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
    label: 'Ready',
  }}
/>

<Story
  name="Danger"
  args={{
    tone: 'danger',
    label: 'Failed',
  }}
/>

<Story
  name="Selected"
  args={{
    selected: true,
  }}
/>

<Story
  name="Compact"
  args={{
    compact: true,
  }}
/>
