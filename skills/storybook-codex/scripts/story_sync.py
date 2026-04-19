#!/usr/bin/env python3
"""Mirror Storybook story structure across frameworks."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


META_RE = re.compile(r"const\s+meta\s*=\s*{", re.MULTILINE)
STORY_EXPORT_RE = re.compile(r"export const (\w+)(?::\s*Story)?\s*=\s*{", re.MULTILINE)
TITLE_RE = re.compile(r"title:\s*['\"]([^'\"]+)['\"]")


def extract_balanced(text: str, start_index: int, opener: str = "{", closer: str = "}") -> tuple[str, int]:
    depth = 0
    in_string: str | None = None
    escaped = False
    for index in range(start_index, len(text)):
        char = text[index]
        if in_string:
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char == in_string:
                in_string = None
            continue
        if char in {"'", '"', "`"}:
            in_string = char
            continue
        if char == opener:
            depth += 1
        elif char == closer:
            depth -= 1
            if depth == 0:
                return text[start_index : index + 1], index + 1
    raise ValueError(f"Unbalanced block starting at index {start_index}")


def extract_expression(block: str, property_name: str) -> str | None:
    match = re.search(rf"\b{re.escape(property_name)}\s*:", block)
    if not match:
        return None
    index = match.end()
    while index < len(block) and block[index].isspace():
        index += 1
    if index >= len(block):
        return None

    start_char = block[index]
    if start_char in "{[(":
        closer = {"{": "}", "[": "]", "(": ")"}[start_char]
        expression, _ = extract_balanced(block, index, start_char, closer)
        return expression

    depth = 0
    in_string: str | None = None
    escaped = False
    for cursor in range(index, len(block)):
        char = block[cursor]
        if in_string:
            if escaped:
                escaped = False
                continue
            if char == "\\":
                escaped = True
                continue
            if char == in_string:
                in_string = None
            continue
        if char in {"'", '"', "`"}:
            in_string = char
            continue
        if char in "{[(":
            depth += 1
        elif char in "}])":
            depth = max(0, depth - 1)
        elif char == "," and depth == 0:
            return block[index:cursor].strip()
    return block[index:].rstrip("}").strip()


def parse_story_source(text: str) -> dict[str, object]:
    meta_match = META_RE.search(text)
    if not meta_match:
        raise ValueError("Could not find meta block in source story")
    meta_block, _ = extract_balanced(text, meta_match.end() - 1)

    stories: list[dict[str, object]] = []
    for match in STORY_EXPORT_RE.finditer(text):
        block, _ = extract_balanced(text, match.end() - 1)
        stories.append(
            {
                "name": match.group(1),
                "block": block,
                "args": extract_expression(block, "args"),
                "play": extract_expression(block, "play"),
                "parameters": extract_expression(block, "parameters"),
            }
        )

    return {
        "title": TITLE_RE.search(text).group(1) if TITLE_RE.search(text) else "",
        "metaArgs": extract_expression(meta_block, "args"),
        "metaArgTypes": extract_expression(meta_block, "argTypes"),
        "hasAutodocs": "autodocs" in text,
        "usesStorybookTest": "storybook/test" in text or any(story["play"] is not None for story in stories),
        "stories": stories,
    }


def default_component_import(component_name: str, target: str) -> str:
    if target == "react":
        return f"./{component_name}"
    if target == "vue":
        return f"./{component_name}.vue"
    return f"./{component_name}.svelte"


def render_story_exports(stories: list[dict[str, object]]) -> str:
    lines: list[str] = []
    for story in stories:
        lines.append(f"export const {story['name']}: Story = {{")
        if story["args"] is not None:
            lines.append(f"  args: {story['args']},")
        if story["parameters"] is not None:
            lines.append(f"  parameters: {story['parameters']},")
        if story["play"] is not None:
            lines.append(f"  play: {story['play']},")
        lines.append("};")
        lines.append("")
    return "\n".join(lines).rstrip()


def render_svelte_stories(stories: list[dict[str, object]]) -> tuple[str, str]:
    script_lines: list[str] = []
    story_lines: list[str] = []

    for story in stories:
        play_name = None
        if story["play"] is not None:
            play_name = f"{story['name']}Play"
            script_lines.append(f"  const {play_name} = {story['play']};")

        attrs = [f'name="{story["name"]}"']
        if story["args"] is not None:
            attrs.append(f"args={{{story['args']}}}")
        if play_name is not None:
            attrs.append(f"play={{{play_name}}}")
        if story["parameters"] is not None:
            attrs.append(f"parameters={{{story['parameters']}}}")
        story_lines.append(f"<Story {' '.join(attrs)} />")

    return "\n".join(script_lines), "\n\n".join(story_lines)


def render_synced_story(
    source: dict[str, object],
    target: str,
    component_name: str,
    component_import: str,
    title: str | None,
) -> str:
    resolved_title = title or str(source["title"]) or f"Synced/{component_name}"
    meta_args = source["metaArgs"] or "{}"
    meta_arg_types = source["metaArgTypes"] or "{}"
    tags_line = "  tags: ['autodocs'],\n" if source["hasAutodocs"] else ""
    test_import = ""
    if source["usesStorybookTest"]:
        test_import = "import { expect, fn, userEvent, within } from 'storybook/test';\n"

    if target == "react":
        story_exports = render_story_exports(list(source["stories"]))
        return (
            "import type { Meta, StoryObj } from '@storybook/react';\n"
            f"{test_import}"
            f"import {{ {component_name} }} from '{component_import}';\n\n"
            "const meta = {\n"
            f"  title: '{resolved_title}',\n"
            f"  component: {component_name},\n"
            f"{tags_line}"
            f"  args: {meta_args},\n"
            f"  argTypes: {meta_arg_types},\n"
            f"}} satisfies Meta<typeof {component_name}>;\n\n"
            "export default meta;\n"
            "type Story = StoryObj<typeof meta>;\n\n"
            f"{story_exports}\n"
        )

    if target == "vue":
        story_exports = render_story_exports(list(source["stories"]))
        return (
            "import type { Meta, StoryObj } from '@storybook/vue3-vite';\n"
            f"{test_import}"
            f"import {component_name} from '{component_import}';\n\n"
            "const meta = {\n"
            f"  title: '{resolved_title}',\n"
            f"  component: {component_name},\n"
            f"{tags_line}"
            f"  args: {meta_args},\n"
            f"  argTypes: {meta_arg_types},\n"
            f"}} satisfies Meta<typeof {component_name}>;\n\n"
            "export default meta;\n"
            "type Story = StoryObj<typeof meta>;\n\n"
            f"{story_exports}\n"
        )

    extra_script, story_markup = render_svelte_stories(list(source["stories"]))
    extra_script_block = f"\n{extra_script}\n" if extra_script else "\n"
    return (
        "<script module lang=\"ts\">\n"
        "  import { defineMeta } from '@storybook/addon-svelte-csf';\n"
        f"  {test_import.replace(chr(10), chr(10) + '  ').rstrip()}\n"
        f"  import {component_name} from '{component_import}';\n\n"
        "  const { Story } = defineMeta({\n"
        f"    title: '{resolved_title}',\n"
        f"    component: {component_name},\n"
        f"{tags_line.replace('  ', '    ')}"
        f"    args: {meta_args},\n"
        f"    argTypes: {meta_arg_types},\n"
        "  });"
        f"{extra_script_block}"
        "</script>\n\n"
        f"{story_markup}\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Mirror story structure across frameworks.")
    parser.add_argument("source_story", help="Existing story file to mirror")
    parser.add_argument("--target", choices=("react", "vue", "svelte"), required=True)
    parser.add_argument("--component-name", help="Target component name")
    parser.add_argument("--component-import", help="Target component import path")
    parser.add_argument("--title", help="Override the target story title")
    parser.add_argument("--out", help="Optional output file path")
    args = parser.parse_args()

    source_path = Path(args.source_story).resolve()
    if not source_path.exists():
        print(f"Source story not found: {source_path}", file=sys.stderr)
        return 1

    text = source_path.read_text(encoding="utf-8")
    source = parse_story_source(text)
    component_name = args.component_name or "Component"
    component_import = args.component_import or default_component_import(component_name, args.target)
    rendered = render_synced_story(source, args.target, component_name, component_import, args.title)

    if args.out:
        Path(args.out).resolve().write_text(rendered, encoding="utf-8")
    else:
        print(rendered)
    return 0


if __name__ == "__main__":
    sys.exit(main())
