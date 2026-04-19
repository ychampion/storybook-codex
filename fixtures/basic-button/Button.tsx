import type { ReactNode } from 'react';

export type ButtonProps = {
  children: ReactNode;
  size?: 'sm' | 'md' | 'lg';
  tone?: 'neutral' | 'brand' | 'danger';
  disabled?: boolean;
  loading?: boolean;
  onClick?: () => void;
};

export function Button({
  children,
  size = 'md',
  tone = 'neutral',
  disabled = false,
  loading = false,
  onClick,
}: ButtonProps) {
  const label = loading ? 'Working...' : children;

  return (
    <button
      data-size={size}
      data-tone={tone}
      disabled={disabled || loading}
      onClick={onClick}
      type="button"
    >
      {label}
    </button>
  );
}

