import { ThemeBadge } from './ThemeBadge';

export function ThemeBadgeUsage() {
  return (
    <>
      <ThemeBadge label="System" theme="system" />
      <ThemeBadge label="Light" selected theme="light" />
      <ThemeBadge compact label="Dark" selected theme="dark" />
    </>
  );
}
