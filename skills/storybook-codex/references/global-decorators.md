# Global Decorators

Use decorator generation when Storybook needs the same provider tree the app already uses.

Detect from the real app entry points first:

- React: `App.tsx`, `main.tsx`, `providers.tsx`
- Vue: `main.ts`, `app.ts`

What to preserve:

- provider order
- provider props such as `client={queryClient}` or `mode="dark"`
- setup values like `const queryClient = new QueryClient()`
- plugin setup for Vue `app.use(...)`

Output goals:

- React: `.storybook/preview.tsx` with `decorators`
- Vue: `.storybook/preview.ts` with `setup((app) => app.use(...))`

Keep the generated preview compact:

- Include only the imports and setup lines required by detected providers.
- Skip wrappers like `StrictMode` unless the repo explicitly needs them in Storybook.
- Default to `tags: ['autodocs']` even when no providers are detected so the preview stays useful.
