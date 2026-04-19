export type BadgeProps = {
  label: string;
  variant?: 'soft' | 'solid';
  rounded?: boolean;
};

export function Badge({
  label,
  variant = 'soft',
  rounded = true,
}: BadgeProps) {
  return (
    <span data-rounded={rounded} data-variant={variant}>
      {label}
    </span>
  );
}

