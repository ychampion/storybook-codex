#!/usr/bin/env python3
"""Generate a deterministic story blueprint for a React, Vue, or Svelte component."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path


PROPS_BLOCK_RE = re.compile(
    r"(?:export\s+)?(?:type|interface)\s+(?P<name>(?:\w+)?Props)\s*(?:=\s*)?{(?P<body>.*?)};?",
    re.DOTALL,
)
DEFINE_PROPS_INLINE_RE = re.compile(
    r"defineProps\s*<\s*{(?P<body>.*?)}\s*>\s*\(",
    re.DOTALL,
)
PROP_RE = re.compile(r"^\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\??:\s*(?P<type>[^;]+);")
EXPORT_LET_RE = re.compile(
    r"^\s*export\s+let\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    r"(?:\s*:\s*(?P<type>[^=;]+))?"
    r"(?:\s*=\s*[^;]+)?;",
    re.MULTILINE,
)
STRING_LITERAL_RE = re.compile(r"'([^']+)'|\"([^\"]+)\"")
EVENT_RE = re.compile(r"^on[A-Z]")

VARIANT_NAMES = {"variant", "tone", "size", "theme", "intent", "color"}
STATE_NAMES = {"disabled", "loading", "selected", "open", "error", "dismissible", "compact"}
HIDE_NAMES = {"className", "style", "testId", "dataTestId", "asChild"}
BOUNDARY_TEXT_NAMES = {"label", "title", "message", "children", "text", "description"}
CANONICAL_STORY_NAMES = {
    "sm": "Small",
    "md": "Medium",
    "lg": "Large",
    "xl": "ExtraLarge",
}
PREFERRED_VARIANT_VALUES = (
    "brand",
    "danger",
    "success",
    "warning",
    "dark",
    "light",
    "solid",
    "outline",
    "ghost",
    "lg",
    "xl",
)


def to_story_name(value: str) -> str:
    if value in CANONICAL_STORY_NAMES:
        return CANONICAL_STORY_NAMES[value]
    parts = re.split(r"[^A-Za-z0-9]+", value)
    return "".join(part[:1].upper() + part[1:] for part in parts if part) or "Variant"


def pick_variant_values(prop_name: str, options: list[str]) -> list[str]:
    if prop_name == "size":
        chosen = [value for value in ("sm", "lg", "xl") if value in options]
        if chosen:
            return chosen[:2]

    chosen = [value for value in PREFERRED_VARIANT_VALUES if value in options]
    if chosen:
        return chosen[:2]

    return options[1:3]


def parse_prop_body(body: str) -> list[dict[str, object]]:
    props: list[dict[str, object]] = []
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("//"):
            continue
        prop_match = PROP_RE.match(line)
        if not prop_match:
            continue
        prop_name = prop_match.group("name")
        raw_type = prop_match.group("type").strip()
        options = [
            left or right
            for left, right in STRING_LITERAL_RE.findall(raw_type)
            if (left or right)
        ]
        props.append(
            {
                "name": prop_name,
                "type": raw_type,
                "options": options,
                "isEvent": bool(EVENT_RE.match(prop_name)),
                "isHidden": prop_name in HIDE_NAMES,
            }
        )
    return props


def dedupe_props(props: list[dict[str, object]]) -> list[dict[str, object]]:
    deduped: list[dict[str, object]] = []
    seen: set[str] = set()
    for prop in props:
        name = str(prop["name"])
        if name in seen:
            continue
        deduped.append(prop)
        seen.add(name)
    return deduped


def parse_props(source: str) -> list[dict[str, object]]:
    props: list[dict[str, object]] = []

    for match in PROPS_BLOCK_RE.finditer(source):
        props.extend(parse_prop_body(match.group("body")))

    if props:
        return dedupe_props(props)

    inline_props = DEFINE_PROPS_INLINE_RE.search(source)
    if inline_props:
        props.extend(parse_prop_body(inline_props.group("body")))

    for export_match in EXPORT_LET_RE.finditer(source):
        prop_name = export_match.group("name")
        raw_type = (export_match.group("type") or "unknown").strip()
        options = [
            left or right
            for left, right in STRING_LITERAL_RE.findall(raw_type)
            if (left or right)
        ]
        props.append(
            {
                "name": prop_name,
                "type": raw_type,
                "options": options,
                "isEvent": bool(EVENT_RE.match(prop_name)),
                "isHidden": prop_name in HIDE_NAMES,
            }
        )

    return dedupe_props(props)


def sample_value(prop_name: str, raw_type: str, options: list[str]) -> object | None:
    if options:
        return options[0]
    if "boolean" in raw_type:
        return None
    if prop_name == "children":
        return "Preview"
    if prop_name == "label":
        return "Ready"
    if prop_name == "title":
        return "Component title"
    if prop_name == "message":
        return "Helpful supporting text."
    if prop_name in {"description", "text"}:
        return "Helpful supporting content."
    return None


def recommend_controls(props: list[dict[str, object]]) -> dict[str, dict[str, object]]:
    controls: dict[str, dict[str, object]] = {}
    for prop in props:
        name = str(prop["name"])
        options = list(prop["options"])
        raw_type = str(prop["type"])
        if prop["isEvent"]:
            controls[name] = {"control": False, "useFn": True}
            continue
        if prop["isHidden"]:
            controls[name] = {"control": False, "table": {"disable": True}}
            continue
        if options:
            control = "inline-radio" if len(options) <= 3 else "select"
            if name == "size":
                control = "radio"
            controls[name] = {"control": control, "options": options}
            continue
        lower_name = name.lower()
        if "color" in lower_name:
            controls[name] = {"control": "color"}
        elif "date" in lower_name:
            controls[name] = {"control": "date"}
        elif "number" in raw_type:
            controls[name] = {"control": "number"}
    return controls


def recommend_stories(props: list[dict[str, object]]) -> list[dict[str, str]]:
    stories: list[dict[str, str]] = [{"name": "Default", "lens": "baseline"}]
    seen = {"Default"}

    for prop in props:
        name = str(prop["name"])
        options = list(prop["options"])
        if name in VARIANT_NAMES and options:
            for option in pick_variant_values(name, options):
                story_name = to_story_name(option)
                if story_name not in seen:
                    stories.append({"name": story_name, "lens": "decision"})
                    seen.add(story_name)

    for prop in props:
        name = str(prop["name"])
        if name in STATE_NAMES:
            story_name = to_story_name(name)
            if story_name not in seen:
                stories.append({"name": story_name, "lens": "state"})
                seen.add(story_name)

    if any(str(prop["name"]) in BOUNDARY_TEXT_NAMES for prop in props):
        if "LongContent" not in seen:
            stories.append({"name": "LongContent", "lens": "boundary"})
            seen.add("LongContent")

    return stories


def build_notes(props: list[dict[str, object]]) -> list[str]:
    notes: list[str] = []
    if any(prop["isEvent"] for prop in props):
        notes.append("Use fn() for event handlers and hide direct controls for them.")
    hidden = [str(prop["name"]) for prop in props if prop["isHidden"]]
    if hidden:
        notes.append(f"Hide internal props from docs tables and controls: {', '.join(hidden)}.")
    if any(str(prop["name"]) in VARIANT_NAMES for prop in props):
        notes.append("Prefer one or two decision stories over rendering every enum combination.")
    return notes


def build_blueprint(component_path: Path) -> dict[str, object]:
    source = component_path.read_text(encoding="utf-8")
    props = parse_props(source)
    defaults = {}
    for prop in props:
        value = sample_value(str(prop["name"]), str(prop["type"]), list(prop["options"]))
        if value is not None:
            defaults[str(prop["name"])] = value

    return {
        "component": component_path.stem,
        "componentPath": str(component_path),
        "framework": detect_framework(component_path),
        "props": props,
        "defaultArgs": defaults,
        "controls": recommend_controls(props),
        "stories": recommend_stories(props),
        "notes": build_notes(props),
        "lenses": ["baseline", "decision", "state", "boundary", "action"],
    }


def detect_framework(component_path: Path) -> str:
    suffix = component_path.suffix.lower()
    if suffix == ".vue":
        return "vue"
    if suffix == ".svelte":
        return "svelte"
    return "react"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Storybook story blueprint.")
    parser.add_argument("component_path", help="Path to a React, Vue, or Svelte component file")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args()

    component_path = Path(args.component_path).resolve()
    if not component_path.exists():
        print(json.dumps({"error": f"Component not found: {component_path}"}))
        return 1

    blueprint = build_blueprint(component_path)

    if args.format == "markdown":
        print(f"# {blueprint['component']} blueprint")
        print("\n## Recommended stories")
        for story in blueprint["stories"]:
            print(f"- {story['name']} ({story['lens']})")
        print("\n## Notes")
        for note in blueprint["notes"]:
            print(f"- {note}")
    else:
        print(json.dumps(blueprint, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
