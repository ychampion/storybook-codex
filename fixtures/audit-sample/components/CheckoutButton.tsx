export type CheckoutButtonProps = {
  label: string;
  loading?: boolean;
  disabled?: boolean;
  onClick?: () => void;
};

export function CheckoutButton({
  label,
  loading = false,
  disabled = false,
  onClick,
}: CheckoutButtonProps) {
  return (
    <button disabled={disabled || loading} onClick={onClick} type="button">
      {loading ? 'Processing…' : label}
    </button>
  );
}
