export type ThemeBadgeProps = {
  label: string;
  theme?: 'light' | 'dark' | 'system';
  selected?: boolean;
  compact?: boolean;
  className?: string;
};

export function ThemeBadge({
  label,
  theme = 'system',
  selected = false,
  compact = false,
  className,
}: ThemeBadgeProps) {
  return (
    <span
      aria-pressed={selected}
      className={className}
      data-compact={compact}
      data-theme={theme}
    >
      {label}
    </span>
  );
}

