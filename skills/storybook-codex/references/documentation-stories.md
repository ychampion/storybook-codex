# Documentation Stories

Use docs mode when autodocs is not enough and the component needs editorial guidance.

Good docs stories should answer:

- what the component is for
- when to use it and when not to use it
- which props are real decisions versus implementation details
- what two or three common usage patterns look like in code

Prefer one of two outputs:

- a dedicated `.stories.mdx` page when the repo already uses Storybook docs blocks or when Svelte needs a framework-neutral docs page
- a docs-tagged CSF story when the repo prefers `.stories.tsx` or `.stories.ts` everywhere

Choose the shape from the repo, not from habit:

- reuse the component's existing Storybook title when possible and add `/Docs`
- prefer MDX when the repo already renders docs blocks such as `Meta`, `Canvas`, `Controls`, and `Source`
- prefer docs-tagged CSF when teams review everything through regular story files and want docs next to `Default`, `Danger`, or similar exports

Docs guidance should stay practical:

- explain the purpose in one short paragraph
- keep `when to use` and `when not to use` to a few bullets each
- focus prop guidance on decision props, state props, and handler contracts
- include only the most common usage snippets, not every possible variant

Prefer mined usage over invented snippets:

- scan the repo for real component invocations before inventing examples
- keep only two or three snippets that represent the most common usage patterns
- if no real usage exists yet, derive examples from default args plus the recommended story set
