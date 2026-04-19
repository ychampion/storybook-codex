# Change-Aware Story Updates

Use diff mode when the repo already has story files and a component changed on a branch or in a pull request.

Primary workflow:

1. Read the git diff or a saved unified diff.
2. Detect changed component files and prop-level additions, removals, and likely renames.
3. Update only sibling story files that map to those changed components.
4. Auto-add missing exports for new state, decision, or boundary props.
5. Flag existing exports that still reference removed or renamed props.

Diff mode is intentionally conservative:

- It appends new stories inside a managed `storybook-codex diff exports` block.
- It adds inline comments for removed-prop or renamed-prop warnings instead of rewriting existing story args.
- It does not rewrite render functions, loaders, or play functions blindly.

Good uses:

- pre-commit hooks
- CI reports on pull requests
- branch hygiene when a design system API changes

Prefer `--write` only when the repository already uses object-story CSF. For native Svelte CSF or heavily customized story files, use report mode first.
