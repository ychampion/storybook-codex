#!/usr/bin/env python3
"""Detect design tokens and emit Storybook globals suggestions."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


CSS_VAR_RE = re.compile(r"--(?P<name>[A-Za-z0-9-_]+)\s*:\s*(?P<value>[^;]+);")
TAILWIND_PAIR_RE = re.compile(
    r"(?:(?P<quote>['\"])(?P<quoted_name>[A-Za-z0-9-_]+)(?P=quote)|(?P<bare_name>[A-Za-z0-9-_]+))"
    r"\s*:\s*(?P<value>['\"][^'\"]+['\"]|#[A-Fa-f0-9]{3,8}|\d+(?:\.\d+)?(?:px|rem))",
)
IGNORED_DIRS = {".git", ".github", ".omx", ".claude", "node_modules", "dist", "build", "__pycache__"}
SUPPORTED_SUFFIXES = {".css", ".scss", ".sass", ".less", ".ts", ".js", ".cjs", ".mjs", ".json"}


def should_skip(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def categorize_token(name: str) -> str:
    lowered = name.lower()
    if any(part in lowered for part in ("color", "surface", "bg", "text", "border")):
        return "color"
    if any(part in lowered for part in ("radius", "round")):
        return "radius"
    if any(part in lowered for part in ("space", "gap", "padding", "margin")):
        return "spacing"
    if any(part in lowered for part in ("font", "type", "leading", "tracking")):
        return "typography"
    if any(part in lowered for part in ("theme", "mode")):
        return "theme"
    if "density" in lowered:
        return "density"
    return "other"


def collect_tokens(root: Path) -> list[dict[str, str]]:
    tokens: list[dict[str, str]] = []
    seen: set[tuple[str, str, str]] = set()

    for path in root.rglob("*"):
        if not path.is_file() or should_skip(path.relative_to(root)):
            continue
        if path.suffix.lower() not in SUPPORTED_SUFFIXES:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")

        for match in CSS_VAR_RE.finditer(text):
            token = {
                "name": match.group("name"),
                "value": match.group("value").strip(),
                "kind": categorize_token(match.group("name")),
                "source": str(path.relative_to(root)),
                "format": "css-var",
            }
            key = (token["name"], token["source"], token["format"])
            if key not in seen:
                tokens.append(token)
                seen.add(key)

        if "tailwind" in path.name.lower() or "theme" in path.name.lower():
            for match in TAILWIND_PAIR_RE.finditer(text):
                name = match.group("quoted_name") or match.group("bare_name")
                token = {
                    "name": name,
                    "value": match.group("value").strip("'\""),
                    "kind": categorize_token(name),
                    "source": str(path.relative_to(root)),
                    "format": "config",
                }
                key = (token["name"], token["source"], token["format"])
                if key not in seen:
                    tokens.append(token)
                    seen.add(key)

    return sorted(tokens, key=lambda token: (token["kind"], token["name"], token["source"]))


def build_globals(tokens: list[dict[str, str]]) -> list[dict[str, object]]:
    globals_list: list[dict[str, object]] = []
    names = {token["name"] for token in tokens}

    theme_values = sorted(
        {
            name.split("-")[-1]
            for name in names
            if categorize_token(name) in {"theme", "color"} and any(key in name for key in ("theme-", "mode-", "-dark", "-light"))
        }
    )
    density_values = sorted(
        {
            name.split("-")[-1]
            for name in names
            if "density" in name
        }
    )

    if theme_values:
        globals_list.append(
            {
                "name": "theme",
                "items": theme_values,
                "toolbar": "theme switcher",
            }
        )
    if density_values:
        globals_list.append(
            {
                "name": "density",
                "items": density_values,
                "toolbar": "density switcher",
            }
        )

    return globals_list


def preview_snippet(globals_list: list[dict[str, object]]) -> str:
    if not globals_list:
        return "const preview = { tags: ['autodocs'] };"

    lines = ["const preview = {", "  tags: ['autodocs'],", "  globalTypes: {"]
    for item in globals_list:
        items = ", ".join(f"'{value}'" for value in item["items"])
        lines.extend(
            [
                f"    {item['name']}: {{",
                "      toolbar: {",
                f"        items: [{items}],",
                "      },",
                "    },",
            ]
        )
    lines.extend(["  },", "};", "", "export default preview;"])
    return "\n".join(lines)


def render_markdown(tokens: list[dict[str, str]], globals_list: list[dict[str, object]]) -> str:
    lines = ["# Token catalog", ""]
    for token in tokens:
        lines.append(
            f"- `{token['name']}`: `{token['value']}` "
            f"({token['kind']}, {token['source']})"
        )
    if globals_list:
        lines.append("")
        lines.append("## Suggested globals")
        for item in globals_list:
            lines.append(f"- `{item['name']}`: {', '.join(item['items'])}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Detect design tokens and toolbar globals.")
    parser.add_argument("path", help="Path to a repo, package, or token directory")
    parser.add_argument("--format", choices=("json", "markdown", "preview"), default="json")
    parser.add_argument("--preview", action="store_true", help="Alias for --format preview")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(json.dumps({"error": f"Token path not found: {root}"}))
        return 1

    tokens = collect_tokens(root if root.is_dir() else root.parent)
    globals_list = build_globals(tokens)

    output_format = "preview" if args.preview else args.format

    if output_format == "json":
        print(json.dumps({"tokens": tokens, "globals": globals_list, "previewSnippet": preview_snippet(globals_list)}, indent=2))
    elif output_format == "preview":
        print(preview_snippet(globals_list))
    else:
        print(render_markdown(tokens, globals_list))
    return 0


if __name__ == "__main__":
    sys.exit(main())
