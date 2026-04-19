export type UncoveredCardProps = {
  title: string;
};

export function UncoveredCard({ title }: UncoveredCardProps) {
  return <article>{title}</article>;
}
