# Composition Stories

Use composition mode when a component is only meaningful inside a parent flow.

What to capture:

- the real parent component or page section where the child is mounted
- sibling components that change spacing, alignment, or focus order
- literal prop values taken directly from usage sites
- bound props that should become fixture data or render-wrapper state

Heuristics:

- Prefer `InParentName` story names for parent-context stories.
- Keep only one or two high-confidence contexts; do not mirror every usage site.
- Preserve literal usage props as `args`, but move expression-driven bindings into the story `render` function or a wrapper component.
- Treat form, grid, panel, dialog, and sidebar contexts as first-class visual states because they change spacing and affordances.

Story shape:

```tsx
export const InCheckoutForm: Story = {
  render: (args) => (
    <CheckoutFormShell>
      <CheckoutButton {...args} />
    </CheckoutFormShell>
  ),
  args: {
    tone: 'danger',
    label: 'Submit payment',
  },
};
```

When composition mode finds multiple viable parents, pick the highest-confidence one first and keep the others in notes for future regression coverage.
