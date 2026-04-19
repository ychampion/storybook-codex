export type AlertProps = {
  title: string;
  message: string;
  tone?: 'info' | 'success' | 'danger';
  dismissible?: boolean;
  onDismiss?: () => void;
  className?: string;
};

export function Alert({
  title,
  message,
  tone = 'info',
  dismissible = false,
  onDismiss,
  className,
}: AlertProps) {
  return (
    <section className={className} data-tone={tone}>
      <strong>{title}</strong>
      <p>{message}</p>
      {dismissible ? (
        <button onClick={onDismiss} type="button">
          Dismiss
        </button>
      ) : null}
    </section>
  );
}

