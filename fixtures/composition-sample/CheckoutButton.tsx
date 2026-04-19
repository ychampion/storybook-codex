export interface CheckoutButtonProps {
  tone?: 'brand' | 'danger';
  loading?: boolean;
  disabled?: boolean;
  label?: string;
  onClick?: () => void;
}

export function CheckoutButton({
  tone = 'brand',
  loading = false,
  disabled = false,
  label = 'Pay now',
  onClick,
}: CheckoutButtonProps) {
  const classes = ['checkout-button', `checkout-button--${tone}`];
  if (loading) {
    classes.push('checkout-button--loading');
  }

  return (
    <button className={classes.join(' ')} disabled={disabled || loading} onClick={onClick}>
      {loading ? 'Processing payment...' : label}
    </button>
  );
}
