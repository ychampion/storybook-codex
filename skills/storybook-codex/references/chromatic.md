# Chromatic

Use this file only when the user explicitly asks for Chromatic or when the repo already contains Chromatic usage.

## Default files

- `chromatic.config.json`
- `.github/workflows/chromatic.yml`

## Rules

- Keep Chromatic opt-in.
- Use placeholders or GitHub secrets references for tokens and project IDs.
- Do not commit real tokens.
- Keep the scaffold minimal and easy to adapt to the repo's package manager and CI conventions.

## Config defaults

Start with a small config and avoid repo-specific assumptions:

```json
{
  "$schema": "https://www.chromatic.com/config-file.schema.json",
  "projectId": "Project:..."
}
```

Add options like `onlyChanged` only when the repo's CI history and fetch depth make that reasonable.

## Workflow defaults

- Check out full git history when using changed-only optimizations.
- Use the repo's package manager if one already exists.
- Prefer a single Chromatic job instead of a complex workflow on first setup.

