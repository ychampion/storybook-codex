# Interaction stories

Use this file when the component has handlers such as `onClick`, `onChange`, `onSubmit`, `onDismiss`, or `onOpenChange`.

## Default rule

If the component's value comes from user input or stateful interaction, generate one story that proves the interaction, not just one that renders it.

## Preferred imports

Use `storybook/test`:

- `fn()` for action args
- `userEvent` for realistic input
- `within` for scoped queries
- `expect` for assertions

## Sequence heuristics

- `onClick`: click the primary trigger and assert the spy
- `onChange`: type or select a new value and assert the changed UI or handler
- `onSubmit`: complete the happy path and assert the submit call
- `onDismiss`: activate with mouse and keyboard and confirm focus remains sensible
- `onOpenChange`: open, verify visible content, then close if the component supports it

## Keep the play function editorial

- one short user journey
- one or two key assertions
- no giant integration test packed into a story
