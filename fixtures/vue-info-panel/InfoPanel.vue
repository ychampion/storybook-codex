<script setup lang="ts">
export type InfoPanelProps = {
  title: string;
  tone?: 'info' | 'success' | 'danger';
  compact?: boolean;
  className?: string;
};

withDefaults(defineProps<InfoPanelProps>(), {
  tone: 'info',
  compact: false,
});
</script>

<template>
  <section :class="className" :data-compact="compact" :data-tone="tone">
    <strong>{{ title }}</strong>
    <slot>Helpful supporting detail.</slot>
  </section>
</template>
