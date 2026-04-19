#!/usr/bin/env python3
"""Generate Storybook preview decorators or setup hooks from repo providers."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from storybook_codex_lib import IGNORED_SCAN_DIRS, normalize_whitespace


IMPORT_RE = re.compile(r"^\s*import\s+(.+?)\s+from\s+['\"]([^'\"]+)['\"]\s*;?", re.MULTILINE)
CONST_RE = re.compile(r"const\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*=\s*(?P<value>.*?);", re.DOTALL)
JSX_OPEN_RE = re.compile(r"<(?P<name>[A-Z][A-Za-z0-9_.]*)\b(?P<body>[^<>]*)>")
USE_RE = re.compile(r"(?:\.\s*use|app\.use)\((?P<expr>[^)]+)\)")
IDENTIFIER_RE = re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\b")

REACT_ENTRY_NAMES = {
    "App.tsx",
    "App.jsx",
    "main.tsx",
    "main.jsx",
    "providers.tsx",
    "providers.jsx",
}
VUE_ENTRY_NAMES = {"main.ts", "main.js", "app.ts", "app.js"}
REACT_PROVIDER_NAMES = {
    "ThemeProvider",
    "QueryClientProvider",
    "I18nextProvider",
    "IntlProvider",
    "ApolloProvider",
    "RouterProvider",
    "Provider",
    "StoreProvider",
    "ColorModeProvider",
}
IGNORED_REACT_WRAPPERS = {"App", "StrictMode", "Fragment", "Suspense"}


def should_skip(path: Path) -> bool:
    return any(part in IGNORED_SCAN_DIRS for part in path.parts)


def collect_candidate_files(root: Path, names: set[str], suffixes: set[str]) -> list[Path]:
    direct_matches: list[Path] = []
    fallback_matches: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or should_skip(path.relative_to(root)):
            continue
        if path.suffix.lower() not in suffixes:
            continue
        if path.name in names:
            direct_matches.append(path)
        elif path.name.lower().startswith(("app.", "main.", "provider")):
            fallback_matches.append(path)
    return sorted(direct_matches) or sorted(fallback_matches)


def parse_import_lines(text: str) -> tuple[dict[str, str], dict[str, str]]:
    symbols: dict[str, str] = {}
    lines: dict[str, str] = {}

    for match in IMPORT_RE.finditer(text):
        clause = normalize_whitespace(match.group(1))
        source = match.group(2)
        line = normalize_whitespace(match.group(0))
        lines[source] = line

        default_part = clause
        named_part = ""
        if "{" in clause and "}" in clause:
            before, brace_and_rest = clause.split("{", 1)
            default_part = before.rstrip(", ").strip()
            named_part = brace_and_rest.split("}", 1)[0]

        if default_part and not default_part.startswith("* as "):
            default_name = default_part.split(",", 1)[0].strip()
            if default_name:
                symbols[default_name] = line

        if clause.startswith("* as "):
            namespace_name = clause[len("* as ") :].strip()
            if namespace_name:
                symbols[namespace_name] = line

        for part in named_part.split(","):
            name = part.strip()
            if not name:
                continue
            local_name = name.split(" as ")[-1].strip()
            symbols[local_name] = line

    return symbols, lines


def parse_const_statements(text: str) -> dict[str, str]:
    statements: dict[str, str] = {}
    for match in CONST_RE.finditer(text):
        name = match.group("name")
        statement = normalize_whitespace(f"const {name} = {match.group('value')};")
        statements[name] = statement
    return statements


def extract_identifiers(text: str) -> set[str]:
    keywords = {
        "true",
        "false",
        "null",
        "undefined",
        "return",
        "const",
        "className",
        "children",
    }
    return {match.group(0) for match in IDENTIFIER_RE.finditer(text) if match.group(0) not in keywords}


def is_react_provider(name: str) -> bool:
    simple_name = name.split(".")[-1]
    return simple_name.endswith("Provider") or simple_name in REACT_PROVIDER_NAMES


def detect_react_payload(root: Path) -> dict[str, object]:
    entry_files = collect_candidate_files(root, REACT_ENTRY_NAMES, {".tsx", ".jsx"})
    providers: list[dict[str, str]] = []
    import_lines: list[str] = []
    setup_lines: list[str] = []
    notes: list[str] = []

    for path in entry_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        imports, _ = parse_import_lines(text)
        consts = parse_const_statements(text)
        app_index = text.find("<App")
        scan_scope = text[:app_index] if app_index != -1 else text

        local_providers: list[dict[str, str]] = []
        required_symbols: set[str] = set()
        for match in JSX_OPEN_RE.finditer(scan_scope):
            name = match.group("name")
            simple_name = name.split(".")[-1]
            if simple_name in IGNORED_REACT_WRAPPERS or not is_react_provider(name):
                continue
            attrs = match.group("body").strip()
            local_providers.append({"name": simple_name, "attrs": normalize_whitespace(attrs)})
            required_symbols.add(simple_name)
            required_symbols.update(extract_identifiers(attrs))

        if not local_providers:
            continue

        providers = local_providers
        import_lines = [imports[symbol] for symbol in sorted(required_symbols) if symbol in imports]
        setup_lines = [consts[symbol] for symbol in sorted(required_symbols) if symbol in consts]
        setup_identifiers = set().union(*(extract_identifiers(line) for line in setup_lines)) if setup_lines else set()
        for symbol in sorted(setup_identifiers):
            if symbol in imports and imports[symbol] not in import_lines:
                import_lines.append(imports[symbol])
        notes.append(f"Detected provider tree in {path.relative_to(root).as_posix()}.")
        break

    preview_lines = ["import type { Preview } from '@storybook/react';"]
    if import_lines:
        preview_lines.extend(import_lines)
    if setup_lines:
        preview_lines.extend(["", *setup_lines])

    preview_lines.extend(["", "const preview: Preview = {", "  tags: ['autodocs'],"]
    )
    if providers:
        preview_lines.extend(["  decorators: [", "    (Story) => ("])
        for index, provider in enumerate(providers):
            attrs = f" {provider['attrs']}" if provider["attrs"] else ""
            preview_lines.append(f"{'      ' + '  ' * index}<{provider['name']}{attrs}>")
        preview_lines.append(f"{'      ' + '  ' * len(providers)}<Story />")
        for index, provider in enumerate(reversed(providers)):
            indent = "      " + "  " * (len(providers) - index - 1)
            preview_lines.append(f"{indent}</{provider['name']}>")
        preview_lines.extend(["    ),", "  ],"])
    preview_lines.extend(["};", "", "export default preview;"])

    if not providers:
        notes.append("No React providers were detected; keep the preview minimal and add wrappers manually if needed.")

    return {
        "framework": "react",
        "entryFiles": [path.relative_to(root).as_posix() for path in entry_files],
        "providers": providers,
        "imports": import_lines,
        "setupLines": setup_lines,
        "previewSnippet": "\n".join(preview_lines).strip() + "\n",
        "notes": notes,
    }


def detect_vue_payload(root: Path) -> dict[str, object]:
    entry_files = collect_candidate_files(root, VUE_ENTRY_NAMES, {".ts", ".js"})
    plugins: list[str] = []
    import_lines: list[str] = []
    setup_lines: list[str] = []
    notes: list[str] = []

    for path in entry_files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        imports, _ = parse_import_lines(text)
        consts = parse_const_statements(text)
        local_plugins = [normalize_whitespace(match.group("expr")) for match in USE_RE.finditer(text)]
        if not local_plugins:
            continue

        plugins = []
        required_symbols: set[str] = set()
        for plugin in local_plugins:
            if plugin in plugins:
                continue
            plugins.append(plugin)
            required_symbols.update(extract_identifiers(plugin))

        setup_lines = [consts[symbol] for symbol in sorted(required_symbols) if symbol in consts]
        setup_identifiers = set().union(*(extract_identifiers(line) for line in setup_lines)) if setup_lines else set()
        required_symbols.update(setup_identifiers)
        import_lines = [imports[symbol] for symbol in sorted(required_symbols) if symbol in imports]
        notes.append(f"Detected Vue app.use() chain in {path.relative_to(root).as_posix()}.")
        break

    preview_lines = [
        "import type { Preview } from '@storybook/vue3-vite';",
        "import { setup } from '@storybook/vue3-vite';",
    ]
    if import_lines:
        preview_lines.extend(import_lines)
    if setup_lines:
        preview_lines.extend(["", *setup_lines])

    if plugins:
        preview_lines.extend(["", "setup((app) => {"])
        for plugin in plugins:
            preview_lines.append(f"  app.use({plugin});")
        preview_lines.append("});")

    preview_lines.extend(["", "const preview: Preview = {", "  tags: ['autodocs'],", "};", "", "export default preview;"])

    if not plugins:
        notes.append("No Vue plugins were detected; keep the preview minimal and add setup(app => ...) hooks manually if needed.")

    return {
        "framework": "vue",
        "entryFiles": [path.relative_to(root).as_posix() for path in entry_files],
        "plugins": plugins,
        "imports": import_lines,
        "setupLines": setup_lines,
        "previewSnippet": "\n".join(preview_lines).strip() + "\n",
        "notes": notes,
    }


def choose_payload(root: Path, framework: str) -> dict[str, object]:
    if framework == "react":
        return detect_react_payload(root)
    if framework == "vue":
        return detect_vue_payload(root)

    react_payload = detect_react_payload(root)
    vue_payload = detect_vue_payload(root)
    react_score = len(react_payload.get("providers", []))
    vue_score = len(vue_payload.get("plugins", []))
    return react_payload if react_score >= vue_score else vue_payload


def render_markdown(payload: dict[str, object]) -> str:
    lines = [f"# {payload['framework']} Storybook decorators", ""]
    entry_files = list(payload.get("entryFiles", []))
    if entry_files:
        lines.append(f"- Entry files scanned: {', '.join(entry_files)}")
    if payload["framework"] == "react":
        providers = list(payload.get("providers", []))
        lines.append(f"- Providers detected: {len(providers)}")
        for provider in providers:
            attrs = provider["attrs"] or "no props"
            lines.append(f"  - {provider['name']}: {attrs}")
    else:
        plugins = list(payload.get("plugins", []))
        lines.append(f"- Plugins detected: {len(plugins)}")
        for plugin in plugins:
            lines.append(f"  - {plugin}")

    lines.append("")
    lines.append("## Preview snippet")
    lines.append("```ts")
    lines.append(str(payload["previewSnippet"]).rstrip())
    lines.append("```")

    notes = list(payload.get("notes", []))
    if notes:
        lines.append("")
        lines.append("## Notes")
        for note in notes:
            lines.append(f"- {note}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Storybook preview decorators from app providers.")
    parser.add_argument("path", help="Repo root or entry file")
    parser.add_argument("--framework", choices=("auto", "react", "vue"), default="auto")
    parser.add_argument("--format", choices=("json", "markdown", "preview"), default="json")
    parser.add_argument("--out", help="Optional output path for the generated preview snippet")
    args = parser.parse_args()

    target_path = Path(args.path).resolve()
    if not target_path.exists():
        print(json.dumps({"error": f"Path not found: {target_path}"}))
        return 1

    root = target_path if target_path.is_dir() else target_path.parent
    payload = choose_payload(root, args.framework)

    if args.out:
        Path(args.out).resolve().write_text(str(payload["previewSnippet"]), encoding="utf-8")

    if args.format == "preview":
        print(payload["previewSnippet"], end="")
    elif args.format == "markdown":
        print(render_markdown(payload))
    else:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
