# Story design lenses

Use this file when a component has many props and you need to decide which stories are worth keeping.

The goal is not "maximum story count". The goal is "minimum set that explains the component quickly".

## Lens 1: Baseline

Every component gets one clean default story.

Ask:

- what is the normal intended state?
- what label or content makes the component readable at a glance?

## Lens 2: Decision

Use this when the component has visual choices that product teams actually compare:

- `size`
- `variant`
- `tone`
- `theme`
- `intent`

Good output:

- `Brand`
- `Danger`
- `Large`
- `Dark`

Bad output:

- one story per every low-value enum if the difference is invisible or redundant

## Lens 3: State

Use this when booleans or status props materially change behavior or appearance:

- `disabled`
- `loading`
- `selected`
- `open`
- `error`
- `dismissible`
- `compact`

These are often better stories than raw prop permutations.

## Lens 4: Boundary

Use this only when the boundary teaches something:

- long labels that wrap
- crowded content
- empty or near-empty content
- extreme numeric values

If the boundary looks identical to the baseline, skip it.

Suggested names:

- `LongContent`
- `Dense`
- `Empty`

## Lens 5: Action

Use this when the interaction surface matters:

- button clicks
- dismiss handlers
- toggles
- menu opening

Prefer `fn()` for event handlers. Add `play` only when the story truly benefits from an interaction demonstration.

## Compact decision order

When unsure, choose in this order:

1. Baseline
2. Highest-value decision variant
3. Highest-value state variant
4. Boundary only if it reveals something new
5. Action support only if interaction matters

Most components should stop at 3 to 5 stories.

