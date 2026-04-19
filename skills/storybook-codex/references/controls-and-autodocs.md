# Controls and autodocs

Use this file when the story needs explicit controls, better docs behavior, or cleaner prop exposure.

## Controls

Prefer inference first. Add `argTypes` only when one of these is true:

- union props need explicit selectable options
- control inference is noisy or wrong
- internal props should be hidden from tables and controls
- a prop needs a specific control such as `color`, `date`, `range`, `radio`, or `inline-radio`

Example:

```ts
argTypes: {
  size: {
    control: 'radio',
    options: ['sm', 'md', 'lg'],
  },
  tone: {
    control: 'inline-radio',
    options: ['neutral', 'brand', 'danger'],
  },
  className: {
    control: false,
    table: {
      disable: true,
    },
  },
},
```

## Event handlers

Prefer `fn()` from `@storybook/test` for function props that should be callable in the canvas.

Example:

```ts
import { fn } from '@storybook/test';

args: {
  onClick: fn(),
},
argTypes: {
  onClick: {
    control: false,
  },
},
```

Do not expose raw function props as editable text-like controls.

## Autodocs

- If `.storybook/preview.ts` or `.storybook/preview.tsx` already sets `tags: ['autodocs']`, keep using the preview-level configuration.
- Otherwise add `tags: ['autodocs']` at the story meta level.
- Do not add duplicate autodocs declarations in multiple places unless the repo already follows that pattern.

## Prop filtering

Hide props that make the docs table worse instead of better:

- `className`
- raw `style`
- test IDs
- internal render hooks
- props the component inherits but the team does not document

