# Multi-framework sync

Use this file when a design system ships equivalent components in more than one framework and you want story parity instead of story drift.

## Default workflow

1. Pick the source story file, usually the React one.
2. Mirror the story structure with `python3 skills/storybook-codex/scripts/story_sync.py <story> --target <framework>`.
3. Review the synced file for framework-specific rendering details.
4. Keep args, `argTypes`, story names, and `play()` intent aligned even if the final render syntax differs.

## What should stay aligned

- story title structure
- story names
- default args
- controls and hidden props
- interaction intent
- accessibility intent

## What can differ

- component import style
- slot or children syntax
- compound-component render wrappers
- framework-specific setup for dialogs, portals, or transitions
