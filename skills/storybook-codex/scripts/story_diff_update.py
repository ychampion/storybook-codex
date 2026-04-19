#!/usr/bin/env python3
"""Update affected Storybook stories from git diff signals."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from difflib import SequenceMatcher
from pathlib import Path

from storybook_codex_lib import (
    BOUNDARY_TEXT_NAMES,
    COMPONENT_SUFFIXES,
    STATE_NAMES,
    STORY_SUFFIXES,
    VARIANT_NAMES,
    build_blueprint,
    detect_framework,
    discover_repo_root,
    match_story_for_component,
    normalize_whitespace,
    parse_props,
    pick_variant_values,
    to_story_name,
)


FILE_HEADER_RE = re.compile(r"^diff --git a/(?P<old>.+?) b/(?P<new>.+)$", re.MULTILINE)
PROP_LINE_RE = re.compile(
    r"^\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*(?P<optional>\?)?\s*:\s*(?P<type>[^=,;]+)"
)
EXPORT_LET_RE = re.compile(
    r"^\s*export\s+let\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    r"(?:\s*:\s*(?P<type>[^=;]+))?"
)
STORY_EXPORT_RE = re.compile(r"^export const (?P<name>\w+)(?::\s*Story)?\s*=\s*{", re.MULTILINE)
MANAGED_EXPORTS_RE = re.compile(
    r"\n?/\* storybook-codex diff exports:start \*/.*?/\* storybook-codex diff exports:end \*/\n?",
    re.DOTALL,
)
MANAGED_NOTES_RE = re.compile(
    r"\n?/\* storybook-codex diff notes:start \*/.*?/\* storybook-codex diff notes:end \*/\n?",
    re.DOTALL,
)
INLINE_NOTE_RE = re.compile(r"^\s*// storybook-codex diff: .*\n", re.MULTILINE)


def extract_balanced(text: str, start_index: int) -> tuple[str, int]:
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
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start_index : index + 1], index + 1
    raise ValueError(f"Unbalanced story block starting at index {start_index}")


def find_story_blocks(text: str) -> list[dict[str, object]]:
    blocks: list[dict[str, object]] = []
    for match in STORY_EXPORT_RE.finditer(text):
        block, end_index = extract_balanced(text, match.end() - 1)
        blocks.append(
            {
                "name": match.group("name"),
                "block": block,
                "start": match.start(),
                "end": end_index,
            }
        )
    return blocks


def parse_patch_prop(line: str) -> tuple[str, str] | None:
    stripped = line.strip()
    if not stripped or stripped.startswith(("//", "*", "/*", "@@", "interface ", "type ")):
        return None
    export_match = EXPORT_LET_RE.match(stripped)
    if export_match:
        return export_match.group("name"), normalize_whitespace(export_match.group("type") or "unknown")
    property_match = PROP_LINE_RE.match(stripped)
    if property_match:
        return property_match.group("name"), normalize_whitespace(property_match.group("type"))
    return None


def parse_diff_sections(diff_text: str) -> list[dict[str, object]]:
    headers = list(FILE_HEADER_RE.finditer(diff_text))
    sections: list[dict[str, object]] = []
    for index, header in enumerate(headers):
        start = header.start()
        end = headers[index + 1].start() if index + 1 < len(headers) else len(diff_text)
        path = header.group("new")
        body = diff_text[start:end]
        sections.append({"path": path, "body": body})
    return sections


def extract_prop_changes(diff_text: str) -> list[dict[str, object]]:
    changes: list[dict[str, object]] = []
    for section in parse_diff_sections(diff_text):
        path = str(section["path"])
        if not path.endswith(COMPONENT_SUFFIXES) or any(path.endswith(suffix) for suffix in STORY_SUFFIXES):
            continue

        added: dict[str, str] = {}
        removed: dict[str, str] = {}
        for line in str(section["body"]).splitlines():
            if line.startswith("+++") or line.startswith("---"):
                continue
            if line.startswith("+"):
                parsed = parse_patch_prop(line[1:])
                if parsed is not None:
                    added[parsed[0]] = parsed[1]
            elif line.startswith("-"):
                parsed = parse_patch_prop(line[1:])
                if parsed is not None:
                    removed[parsed[0]] = parsed[1]

        renames: list[dict[str, object]] = []
        for old_name, old_type in list(removed.items()):
            best_name = ""
            best_ratio = 0.0
            for new_name, new_type in added.items():
                if normalize_whitespace(new_type) != normalize_whitespace(old_type):
                    continue
                ratio = SequenceMatcher(None, old_name.lower(), new_name.lower()).ratio()
                same_story_kind = old_name in VARIANT_NAMES and new_name in VARIANT_NAMES
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_name = new_name
                if same_story_kind and ratio >= 0.15:
                    best_ratio = max(best_ratio, 0.4)
                    best_name = new_name
            if best_name and best_ratio >= 0.35:
                renames.append(
                    {
                        "from": old_name,
                        "to": best_name,
                        "type": old_type,
                        "similarity": round(best_ratio, 2),
                    }
                )
                removed.pop(old_name, None)
                added.pop(best_name, None)

        if added or removed or renames:
            changes.append(
                {
                    "path": path,
                    "addedProps": [{"name": name, "type": prop_type} for name, prop_type in sorted(added.items())],
                    "removedProps": [{"name": name, "type": prop_type} for name, prop_type in sorted(removed.items())],
                    "renamedProps": renames,
                }
            )
    return changes


def load_git_diff(repo_root: Path, staged: bool, base: str | None, head: str | None) -> str:
    command = ["git", "diff", "--unified=0"]
    if staged:
        command.append("--cached")
    if base and head:
        command.extend([base, head])
    elif base:
        command.append(base)

    result = subprocess.run(
        command,
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "git diff failed")
    return result.stdout


def current_story_names(story_path: Path) -> list[str]:
    if not story_path.exists():
        return []
    return [block["name"] for block in find_story_blocks(story_path.read_text(encoding="utf-8"))]


def story_candidates_for_prop(prop: dict[str, object]) -> list[str]:
    name = str(prop["name"])
    options = list(prop.get("options", []))
    raw_type = str(prop.get("type", ""))

    if name in VARIANT_NAMES and options:
        return [to_story_name(value) for value in pick_variant_values(name, options)]
    if name in STATE_NAMES or "boolean" in raw_type:
        return [to_story_name(name)]
    if name in BOUNDARY_TEXT_NAMES:
        return ["LongContent"]
    return []


def build_story_args(story_name: str, blueprint: dict[str, object]) -> dict[str, object]:
    props = list(blueprint.get("props", []))
    for prop in props:
        name = str(prop["name"])
        options = list(prop.get("options", []))
        if name in VARIANT_NAMES:
            for option in options:
                if to_story_name(option) == story_name:
                    return {name: option}
        if story_name == to_story_name(name):
            raw_type = str(prop.get("type", ""))
            if "boolean" in raw_type or name in STATE_NAMES:
                return {name: True}

    if story_name == "LongContent":
        for name in BOUNDARY_TEXT_NAMES:
            if any(str(prop["name"]) == name for prop in props):
                return {name: "This is intentionally longer content so layout branches show up in review."}
    return {}


def render_story_export(story_name: str, args: dict[str, object], component_path: Path) -> str:
    lines = [f"export const {story_name}: Story = {{"]  # Story type already exists in managed files.
    if args:
        lines.append("  args: {")
        for name, value in args.items():
            lines.append(f"    {name}: {json.dumps(value)},")
        lines.append("  },")
    lines.extend(
        [
            "  parameters: {",
            "    docs: {",
            "      description: {",
            f"        story: 'Auto-added by Storybook Codex from the latest diff for {component_path.name}.',",
            "      },",
            "    },",
            "  },",
            "};",
        ]
    )
    return "\n".join(lines)


def annotate_story_file(
    story_text: str,
    deprecated_notes: dict[str, list[str]],
    managed_exports: str,
    managed_notes: str,
) -> str:
    cleaned = MANAGED_EXPORTS_RE.sub("\n", story_text)
    cleaned = MANAGED_NOTES_RE.sub("\n", cleaned)
    cleaned = INLINE_NOTE_RE.sub("", cleaned)

    for block in reversed(find_story_blocks(cleaned)):
        notes = deprecated_notes.get(str(block["name"]))
        if not notes:
            continue
        comment_lines = [f"// storybook-codex diff: {note}" for note in notes]
        cleaned = cleaned[: int(block["start"])] + "\n".join(comment_lines) + "\n" + cleaned[int(block["start"]) :]

    cleaned = cleaned.rstrip() + "\n"
    if managed_exports:
        cleaned += "\n/* storybook-codex diff exports:start */\n"
        cleaned += managed_exports.rstrip() + "\n"
        cleaned += "/* storybook-codex diff exports:end */\n"
    if managed_notes:
        cleaned += "\n/* storybook-codex diff notes:start */\n"
        cleaned += managed_notes.rstrip() + "\n"
        cleaned += "/* storybook-codex diff notes:end */\n"
    return cleaned


def build_update_report(
    repo_root: Path,
    diff_changes: list[dict[str, object]],
    write: bool,
) -> dict[str, object]:
    results: list[dict[str, object]] = []

    for change in diff_changes:
        component_path = (repo_root / str(change["path"])).resolve()
        if not component_path.exists():
            results.append(
                {
                    "componentPath": str(change["path"]),
                    "storyPath": "",
                    "status": "missing-component",
                    "change": change,
                }
            )
            continue

        story_path = match_story_for_component(component_path)
        blueprint = build_blueprint(component_path, repo_root)
        current_names = current_story_names(story_path) if story_path else []
        prop_lookup = {str(prop["name"]): prop for prop in blueprint.get("props", [])}

        candidate_story_names: list[str] = []
        for item in change.get("addedProps", []):
            prop = prop_lookup.get(str(item["name"]))
            if prop is None:
                continue
            for story_name in story_candidates_for_prop(prop):
                if story_name not in candidate_story_names and story_name not in current_names:
                    candidate_story_names.append(story_name)

        managed_exports = "\n\n".join(
            render_story_export(story_name, build_story_args(story_name, blueprint), component_path)
            for story_name in candidate_story_names
        )

        deprecated_notes: dict[str, list[str]] = {}
        report_lines: list[str] = []
        if story_path and story_path.exists():
            story_text = story_path.read_text(encoding="utf-8")
            for block in find_story_blocks(story_text):
                block_text = str(block["block"])
                block_notes: list[str] = []
                for removed in change.get("removedProps", []):
                    removed_name = str(removed["name"])
                    if re.search(rf"\b{re.escape(removed_name)}\b", block_text):
                        block_notes.append(f"deprecated `{block['name']}` because `{removed_name}` was removed")
                        report_lines.append(f"- `{block['name']}` still references removed prop `{removed_name}`.")
                for rename in change.get("renamedProps", []):
                    old_name = str(rename["from"])
                    if re.search(rf"\b{re.escape(old_name)}\b", block_text):
                        block_notes.append(
                            f"rename warning for `{block['name']}`: `{old_name}` likely became `{rename['to']}`"
                        )
                        report_lines.append(
                            f"- `{block['name']}` still references `{old_name}`; likely rename target is `{rename['to']}`."
                        )
                if block_notes:
                    deprecated_notes[str(block["name"])] = block_notes

            if candidate_story_names:
                report_lines.insert(
                    0,
                    "- Added story exports: " + ", ".join(f"`{name}`" for name in candidate_story_names) + ".",
                )

            if write:
                updated_text = annotate_story_file(story_text, deprecated_notes, managed_exports, "\n".join(report_lines))
                story_path.write_text(updated_text, encoding="utf-8")

        framework = detect_framework(component_path)
        results.append(
            {
                "componentPath": component_path.relative_to(repo_root).as_posix(),
                "storyPath": story_path.relative_to(repo_root).as_posix() if story_path else "",
                "framework": framework,
                "status": "updated" if write and story_path else ("report-only" if story_path else "missing-story"),
                "change": change,
                "addedStoryExports": candidate_story_names,
                "deprecatedStories": deprecated_notes,
                "notes": report_lines,
            }
        )

    return {
        "repoRoot": str(repo_root),
        "write": write,
        "changedComponents": results,
    }


def render_markdown(report: dict[str, object]) -> str:
    lines = ["# Story diff update", ""]
    for item in report.get("changedComponents", []):
        lines.append(f"- {item['componentPath']}: {item['status']}")
        if item.get("storyPath"):
            lines.append(f"  story: {item['storyPath']}")
        for note in item.get("notes", []):
            lines.append(f"  {note}")
        for rename in item.get("change", {}).get("renamedProps", []):
            lines.append(
                f"  - rename signal: `{rename['from']}` -> `{rename['to']}` "
                f"(similarity {rename['similarity']})"
            )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Update affected Storybook stories from git diff signals.")
    parser.add_argument("path", help="Repo root or component directory")
    parser.add_argument("--diff", action="store_true", help="Read the current git diff for the repo")
    parser.add_argument("--diff-file", help="Read a saved unified diff from disk")
    parser.add_argument("--staged", action="store_true", help="Read the staged diff instead of the working tree diff")
    parser.add_argument("--base", help="Optional base revision for git diff")
    parser.add_argument("--head", help="Optional head revision for git diff")
    parser.add_argument("--write", action="store_true", help="Write updates into affected story files")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args()

    target_path = Path(args.path).resolve()
    if not target_path.exists():
        print(json.dumps({"error": f"Path not found: {target_path}"}))
        return 1

    repo_root = target_path if target_path.is_dir() else discover_repo_root(target_path)

    if args.diff_file:
        diff_text = Path(args.diff_file).resolve().read_text(encoding="utf-8")
    elif args.diff or not args.diff_file:
        try:
            diff_text = load_git_diff(repo_root, args.staged, args.base, args.head)
        except RuntimeError as exc:
            print(json.dumps({"error": str(exc)}))
            return 1
    else:
        print(json.dumps({"error": "Provide --diff or --diff-file to load changes."}))
        return 1

    diff_changes = extract_prop_changes(diff_text)
    report = build_update_report(repo_root, diff_changes, args.write)

    if args.format == "markdown":
        print(render_markdown(report))
    else:
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
