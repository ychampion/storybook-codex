# Component library patterns

Use this file when the repo is built on top of shadcn/ui, Radix UI, or Headless UI.

## shadcn/ui

- Hide `asChild` from controls and docs tables unless the team explicitly documents it.
- Prefer stories that surface `variant`, `size`, icon spacing, and loading states.
- When the component comes from open code in `components/ui`, treat it like app code: inspect the local implementation before assuming upstream defaults.

See the starter in `assets/templates/libraries/shadcn-button.stories.tsx`.

## Radix UI

- Compound primitives need render wrappers, not just raw `component` meta.
- Preserve `asChild` behavior and forward-ref assumptions.
- Use state stories that make `data-state` transitions visible.
- Add keyboard or focus stories for dialogs, popovers, accordions, and menus.

See the starters in `assets/templates/libraries/radix-dialog.stories.tsx`.

## Headless UI

- Stories usually need the actual composed render tree because the primitives are intentionally unstyled.
- Keep focus trap and keyboard navigation explicit in the story set.
- Prefer one stable "open" story and one keyboard story over a matrix of render prop combinations.

See the starter in `assets/templates/libraries/headlessui-dialog.stories.tsx`.
