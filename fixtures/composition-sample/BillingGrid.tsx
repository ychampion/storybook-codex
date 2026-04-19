import { CheckoutButton } from './CheckoutButton';

function InvoiceCard() {
  return <section>Invoice #402</section>;
}

export function BillingGrid() {
  return (
    <section className="billing-grid">
      <InvoiceCard />
      <CheckoutButton tone="brand" label="Review invoice" />
    </section>
  );
}
