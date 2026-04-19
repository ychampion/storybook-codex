export type NoticeProps = {
  title: string;
  message: string;
  tone?: 'info' | 'danger';
  dismissible?: boolean;
  onDismiss?: () => void;
};

export function Notice({
  title,
  message,
  tone = 'info',
  dismissible = false,
  onDismiss,
}: NoticeProps) {
  return (
    <section data-tone={tone}>
      <h2>{title}</h2>
      <p>{message}</p>
      {dismissible ? (
        <button onClick={onDismiss} type="button">
          Dismiss
        </button>
      ) : null}
    </section>
  );
}
