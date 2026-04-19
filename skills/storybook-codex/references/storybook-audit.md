# Storybook audit

Use this file when the task is "review this Storybook repo" instead of "write one more story."

## Run

```sh
python3 skills/storybook-codex/scripts/storybook_audit.py path/to/repo --format markdown
```

## What it checks

- lens coverage
- autodocs usage
- interaction coverage
- accessibility coverage
- visual regression coverage
- legacy syntax drift
- components that still have no story file

## Usage

- use it as a PR gate with `--fail-under`
- run it after large story migrations
- use the output to decide which components deserve new story work first
