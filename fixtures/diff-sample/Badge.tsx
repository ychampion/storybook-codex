export interface BadgeProps {
  variant?: 'brand' | 'danger';
  loading?: boolean;
  compact?: boolean;
  label?: string;
}

export function Badge({
  variant = 'brand',
  loading = false,
  compact = false,
  label = 'Ready',
}: BadgeProps) {
  return (
    <span data-variant={variant} data-compact={compact} data-loading={loading}>
      {loading ? 'Saving...' : label}
    </span>
  );
}
