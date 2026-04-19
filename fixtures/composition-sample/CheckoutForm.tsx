import { CheckoutButton } from './CheckoutButton';

function PaymentSummary() {
  return <aside>Total due: $128.40</aside>;
}

export function CheckoutForm() {
  const isSubmitting = true;
  const total = 128.4;

  return (
    <form>
      <PaymentSummary />
      <CheckoutButton
        tone="danger"
        loading={isSubmitting}
        disabled={total === 0}
        label="Submit payment"
      />
    </form>
  );
}
