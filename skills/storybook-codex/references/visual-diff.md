# Visual diff

Use this file when the task is not just "write stories" but "write stories and prove they stay visually stable."

## Preferred split

- Keep interaction logic inside the story `play()` function.
- Keep screenshot assertions in a dedicated visual harness.
- Use Chromatic when the repo already has it or the user asks for hosted review.
- Use a local Playwright screenshot spec when the team wants fully local baselines.

## Local harness

The repo ships `assets/templates/visual-regression.spec.ts` as the local starting point.

Use it when:

- CI already runs Playwright
- the team wants baselines in git
- the component needs token or theme permutations that are easier to pin locally

## Story selection

Capture the stories that matter most:

- default
- one or two decision stories
- state stories that materially change layout
- boundary stories that stress wrapping, overflow, or density

Do not snapshot every trivial prop permutation.

## Chromatic guidance

- Use `parameters.chromatic` only where story-level overrides matter.
- Keep tokens and project IDs in secrets, not in tracked files.
- If theme and density globals exist, capture both dimensions intentionally instead of relying on accidental defaults.
