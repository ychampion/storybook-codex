<script lang="ts">
  export type StatusPillProps = {
    label: string;
    tone?: 'neutral' | 'brand' | 'danger';
    selected?: boolean;
    compact?: boolean;
  };

  let {
    label,
    tone = 'neutral',
    selected = false,
    compact = false,
  }: StatusPillProps = $props();
</script>

<span data-compact={compact} data-selected={selected} data-tone={tone}>
  {label}
</span>
