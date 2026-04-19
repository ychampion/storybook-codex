# Accessibility stories

Use this file when a story should deliberately surface accessibility risks instead of leaving them to chance.

## High-value accessibility lenses

- keyboard-only navigation
- visible label and description pairing
- error and helper text association
- focus trapping for dialogs, sheets, menus, and popovers
- disabled and busy semantics

## Storybook guidance

- Add `@storybook/addon-a11y` when the repo uses accessibility checks in Storybook.
- Pair addon checks with a story that makes the relevant UI state obvious.
- Use keyboard interactions inside `play()` for dialog, menu, and dismiss flows.

## WCAG-oriented prompts

- `1.3.1`: labels, descriptions, relationships
- `2.1.1`: keyboard access
- `2.4.3`: focus order
- `3.3.1`: error identification
- `4.1.2`: name, role, value

## Pattern rule

If the component owns focus, opens a layer, or changes live content, give it an explicit accessibility story. Do not assume the default story is enough.
