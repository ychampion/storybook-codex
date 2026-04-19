import { ActionButton } from './ActionButton';

export function ActionButtonUsage() {
  return (
    <>
      <ActionButton onClick={() => undefined} size="lg" tone="brand">
        Publish
      </ActionButton>
      <ActionButton loading tone="danger">
        Delete
      </ActionButton>
      <ActionButton disabled size="sm">
        Retry later
      </ActionButton>
    </>
  );
}
