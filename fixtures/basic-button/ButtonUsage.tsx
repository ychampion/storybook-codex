import { Button } from './Button';

export function ButtonUsage() {
  return (
    <>
      <Button onClick={() => undefined} size="lg" tone="brand">
        Publish
      </Button>
      <Button disabled loading tone="danger">
        Saving
      </Button>
    </>
  );
}
