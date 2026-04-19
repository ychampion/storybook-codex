#!/usr/bin/env python3
"""Build the static dataset for the Storybook Codex demo.

For each fixture component, emit:
  - component source text (the INPUT a developer starts from)
  - expected story file text (the OUTCOME the skill produces)
  - parsed list of named stories with their args (so the demo can live-render each state)
  - blueprint JSON + markdown (the skill's deterministic helper output)

The demo uses this dataset to show what a developer actually sees after using
the storybook-codex skill: the generated .stories.* file alongside a live
preview of every exported story.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


TITLE = "Storybook Codex - Story Outcomes"

FIXTURES = (
    {
        "name": "Button",
        "framework": "react",
        "component": Path("fixtures/basic-button/Button.tsx"),
        "story": Path("fixtures/basic-button/Button.expected.stories.tsx"),
    },
    {
        "name": "Alert",
        "framework": "react",
        "component": Path("fixtures/alert/Alert.tsx"),
        "story": Path("fixtures/alert/Alert.expected.stories.tsx"),
    },
    {
        "name": "ThemeBadge",
        "framework": "react",
        "component": Path("fixtures/theme-badge/ThemeBadge.tsx"),
        "story": Path("fixtures/theme-badge/ThemeBadge.expected.stories.tsx"),
    },
    {
        "name": "Badge",
        "framework": "react",
        "component": Path("fixtures/existing-story/Badge.tsx"),
        "story": Path("fixtures/existing-story/Badge.expected.stories.tsx"),
    },
    {
        "name": "InfoPanel",
        "framework": "vue",
        "component": Path("fixtures/vue-info-panel/InfoPanel.vue"),
        "story": Path("fixtures/vue-info-panel/InfoPanel.expected.stories.ts"),
    },
    {
        "name": "StatusPill",
        "framework": "svelte",
        "component": Path("fixtures/svelte-status-pill/StatusPill.svelte"),
        "story": Path("fixtures/svelte-status-pill/StatusPill.expected.stories.svelte"),
    },
)


CSF_STORY_START_RE = re.compile(r"export const (?P<name>\w+)\s*:\s*Story\s*=\s*")
CSF_META_START_RE = re.compile(r"\bconst\s+meta\s*=\s*")
SVELTE_STORY_RE = re.compile(
    r"<Story\s+name=\"(?P<name>[^\"]+)\"(?P<attrs>[^>]*)/?>",
    re.DOTALL,
)
ARGS_KEY_RE = re.compile(r"(^|\n)\s*args\s*:\s*")


def extract_balanced_object(text: str, start: int) -> str | None:
    """Return the substring inside the JS/TS object literal that starts at
    ``text[start]``. ``start`` must index an opening ``{``. Returns the body
    (without the outer braces), or None if the object is malformed.
    Handles nested braces and strings. Does not handle template literals or
    comments (none of the fixtures use them inside stories)."""
    if start >= len(text) or text[start] != "{":
        return None
    depth = 0
    i = start
    in_str: str | None = None
    while i < len(text):
        ch = text[i]
        if in_str:
            if ch == "\\" and i + 1 < len(text):
                i += 2
                continue
            if ch == in_str:
                in_str = None
        else:
            if ch in ("'", '"'):
                in_str = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return text[start + 1 : i]
        i += 1
    return None


def find_args_body(object_body: str) -> str | None:
    """Given the body of an object literal, return the body of its top-level
    ``args`` property (as the inner body of its ``{...}`` value). Skips any
    ``args`` key that appears inside a nested object or array, so things like
    ``parameters.docs.story.args`` do not shadow the real story args."""
    depth = 0
    i = 0
    in_str: str | None = None
    while i < len(object_body):
        ch = object_body[i]
        if in_str:
            if ch == "\\" and i + 1 < len(object_body):
                i += 2
                continue
            if ch == in_str:
                in_str = None
            i += 1
            continue
        if ch in ("'", '"'):
            in_str = ch
            i += 1
            continue
        if ch in "{[":
            depth += 1
            i += 1
            continue
        if ch in "}]":
            depth -= 1
            i += 1
            continue
        if depth == 0 and ch == "a" and object_body.startswith("args", i):
            before_start = i == 0 or not object_body[i - 1].isalnum() and object_body[i - 1] != "_"
            after_end = i + 4 >= len(object_body) or not object_body[i + 4].isalnum() and object_body[i + 4] != "_"
            if before_start and after_end:
                j = i + 4
                while j < len(object_body) and object_body[j].isspace():
                    j += 1
                if j < len(object_body) and object_body[j] == ":":
                    j += 1
                    while j < len(object_body) and object_body[j].isspace():
                        j += 1
                    if j < len(object_body) and object_body[j] == "{":
                        return extract_balanced_object(object_body, j)
                    return None
        i += 1
    return None


def find_repo_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (
            (candidate / ".codex-plugin" / "plugin.json").exists()
            and (candidate / "skills" / "storybook-codex" / "scripts" / "story_blueprint.py").exists()
        ):
            return candidate
    raise RuntimeError("Could not locate the storybook-codex repository root.")


def run_blueprint(script_path: Path, component_path: Path, output_format: str | None) -> str:
    command = [sys.executable, str(script_path), str(component_path)]
    if output_format:
        command.extend(["--format", output_format])
    completed = subprocess.run(command, check=True, capture_output=True, text=True)
    return completed.stdout.strip()


def parse_key_value_body(body: str) -> dict[str, object]:
    """Best-effort parse of a TS/JS args body.

    Recognises scalar string, number, boolean values and `fn()` markers.
    Ignores nested objects/arrays - callers should treat result as advisory
    and the demo falls back to defaults when a key is missing.
    """
    out: dict[str, object] = {}
    for raw in body.splitlines():
        line = raw.strip().rstrip(",")
        if not line or line.startswith("//"):
            continue
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if not key:
            continue
        if value in ("true", "false"):
            out[key] = value == "true"
        elif value == "fn()":
            out[key] = {"__event__": True}
        elif re.fullmatch(r"-?\d+(\.\d+)?", value):
            out[key] = float(value) if "." in value else int(value)
        elif (value.startswith("'") and value.endswith("'")) or (
            value.startswith('"') and value.endswith('"')
        ):
            out[key] = value[1:-1]
        else:
            # Nested objects/arrays/expressions are ignored. The demo renderer
            # falls back to defaults for these keys.
            continue
    return out


def extract_meta_args(story_text: str) -> dict[str, object]:
    match = CSF_META_START_RE.search(story_text)
    if not match:
        return {}
    brace_index = story_text.find("{", match.end() - 1)
    if brace_index == -1:
        return {}
    meta_body = extract_balanced_object(story_text, brace_index)
    if meta_body is None:
        return {}
    args_body = find_args_body(meta_body)
    return parse_key_value_body(args_body) if args_body is not None else {}


def extract_csf_stories(story_text: str) -> tuple[dict[str, object], list[dict[str, object]]]:
    meta_args = extract_meta_args(story_text)

    stories: list[dict[str, object]] = []
    for match in CSF_STORY_START_RE.finditer(story_text):
        brace_index = match.end()
        if brace_index >= len(story_text) or story_text[brace_index] != "{":
            continue
        body = extract_balanced_object(story_text, brace_index)
        if body is None:
            continue
        args_body = find_args_body(body)
        story_args = parse_key_value_body(args_body) if args_body is not None else {}
        stories.append({"name": match.group("name"), "args": story_args})

    return meta_args, stories


def extract_svelte_stories(story_text: str) -> tuple[dict[str, object], list[dict[str, object]]]:
    meta_args: dict[str, object] = {}
    define_meta = re.search(r"defineMeta\(\s*\{", story_text)
    if define_meta:
        brace_index = story_text.rfind("{", 0, define_meta.end())
        meta_body = extract_balanced_object(story_text, brace_index)
        if meta_body:
            args_body = find_args_body(meta_body)
            if args_body is not None:
                meta_args = parse_key_value_body(args_body)

    stories: list[dict[str, object]] = []
    for match in SVELTE_STORY_RE.finditer(story_text):
        story_name = match.group("name")
        attrs = match.group("attrs") or ""
        story_args: dict[str, object] = {}
        args_match = re.search(r"args=\{\{(?P<body>.*?)\}\}", attrs, re.DOTALL)
        if args_match:
            story_args = parse_key_value_body(args_match.group("body"))
        stories.append({"name": story_name, "args": story_args})

    return meta_args, stories


def build_entry(fixture: dict[str, object], script_path: Path, repo_root: Path) -> dict[str, object]:
    component_path = repo_root / fixture["component"]
    story_path = repo_root / fixture["story"]

    if not component_path.exists():
        raise FileNotFoundError(f"Component fixture missing: {component_path}")
    if not story_path.exists():
        raise FileNotFoundError(f"Story fixture missing: {story_path}")

    component_source = component_path.read_text(encoding="utf-8")
    story_source = story_path.read_text(encoding="utf-8")

    if fixture["framework"] == "svelte":
        meta_args, stories = extract_svelte_stories(story_source)
    else:
        meta_args, stories = extract_csf_stories(story_source)

    blueprint_json = json.loads(run_blueprint(script_path, component_path, "json"))
    blueprint_markdown = run_blueprint(script_path, component_path, "markdown")

    return {
        "name": fixture["name"],
        "framework": fixture["framework"],
        "componentPath": fixture["component"].as_posix(),
        "componentSource": component_source,
        "storyPath": fixture["story"].as_posix(),
        "storySource": story_source,
        "metaArgs": meta_args,
        "stories": stories,
        "blueprintJson": blueprint_json,
        "blueprintMarkdown": blueprint_markdown,
    }


def main() -> int:
    demo_dir = Path(__file__).resolve().parent
    repo_root = find_repo_root(demo_dir)
    script_path = repo_root / "skills" / "storybook-codex" / "scripts" / "story_blueprint.py"
    output_path = demo_dir / "data.json"

    components = [build_entry(fixture, script_path, repo_root) for fixture in FIXTURES]

    payload = {
        "title": TITLE,
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "componentCount": len(components),
        "components": components,
    }
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    names = ", ".join(component["name"] for component in components)
    print(f"Wrote {output_path}")
    print(f"Included {len(components)} components: {names}")
    for component in components:
        story_names = [story["name"] for story in component["stories"]]
        print(f"  - {component['name']:<10} stories: {', '.join(story_names)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
