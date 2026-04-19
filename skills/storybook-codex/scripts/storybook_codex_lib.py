#!/usr/bin/env python3
"""Shared zero-dependency analysis helpers for Storybook Codex."""

from __future__ import annotations

import json
import re
from pathlib import Path


PROPS_BLOCK_RE = re.compile(
    r"(?:export\s+)?(?:type|interface)\s+(?P<name>(?:\w+)?Props)\s*(?:=\s*)?{(?P<body>.*?)};?",
    re.DOTALL,
)
DEFINE_PROPS_INLINE_RE = re.compile(
    r"defineProps\s*<\s*{(?P<body>.*?)}\s*>\s*\(",
    re.DOTALL,
)
EXPORT_LET_RE = re.compile(
    r"^\s*export\s+let\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)"
    r"(?:\s*:\s*(?P<type>[^=;]+))?"
    r"(?:\s*=\s*(?P<default>[^;]+))?;",
    re.MULTILINE,
)
STRING_LITERAL_RE = re.compile(r"'([^']+)'|\"([^\"]+)\"")
PROPERTY_RE = re.compile(
    r"(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s*(?P<optional>\?)?\s*:\s*(?P<type>.+)",
    re.DOTALL,
)
WITH_DEFAULTS_RE = re.compile(
    r"withDefaults\s*\(\s*defineProps<[^>]+>\s*\(\s*\)\s*,\s*{(?P<body>.*?)}\s*\)",
    re.DOTALL,
)
REACT_DEFAULTS_RE = re.compile(
    r"(?:function\s+\w+|const\s+\w+\s*=\s*\()\s*\(\s*{(?P<body>.*?)}\s*:\s*[A-Za-z_][A-Za-z0-9_]*Props",
    re.DOTALL,
)
SVELTE_PROPS_RE = re.compile(
    r"let\s*{\s*(?P<body>.*?)}\s*:\s*[A-Za-z_][A-Za-z0-9_]*Props\s*=\s*\$props\(\s*\);",
    re.DOTALL,
)
EVENT_RE = re.compile(r"^on[A-Z]")
STORY_EXPORT_RE = re.compile(r"export const (\w+): Story\b")
SVELTE_STORY_RE = re.compile(r'<Story\s+name="([^"]+)"')
TITLE_RE = re.compile(r"title:\s*['\"]([^'\"]+)['\"]")
COMPONENT_META_RE = re.compile(r"component:\s*([A-Za-z_][A-Za-z0-9_]*)")
IMPORT_FROM_RE = re.compile(r"from ['\"]([^'\"]+)['\"]")
PLAY_RE = re.compile(r"\bplay\s*:")
AUTODOCS_RE = re.compile(r"tags:\s*\[[^\]]*['\"]autodocs['\"]")
ARGTYPES_RE = re.compile(r"\bargTypes\s*:")
CHROMATIC_RE = re.compile(r"\bchromatic\b|toMatchScreenshot|postVisit|preVisit")
A11Y_RE = re.compile(r"\ba11y\b|addon-a11y|wcag|axe")
LEGACY_STORY_RE = re.compile(r"Template\.bind|ComponentStory|ComponentMeta")
PARAMETERS_A11Y_RE = re.compile(r"parameters\s*:\s*{[^}]*a11y", re.DOTALL)
USAGE_ATTR_RE = re.compile(
    r"(?:^|\s)(?P<marker>[:@]?)(?P<name>[A-Za-z_][A-Za-z0-9:_-]*)(?:\s*=\s*(?P<value>\{[^{}]*\}|\"[^\"]*\"|'[^']*'|`[^`]*`))?"
)
DECLARATION_RE = re.compile(
    r"(?:export\s+)?(?:default\s+)?(?:function|const|class)\s+(?P<name>[A-Z][A-Za-z0-9_]*)"
)
JSX_COMPONENT_RE = re.compile(r"<(?P<name>[A-Z][A-Za-z0-9_.]*)\b")
SEMANTIC_CONTAINER_RE = re.compile(
    r"<(?P<name>form|section|article|aside|main|header|footer|nav|fieldset|dialog|table)\b",
    re.IGNORECASE,
)

VARIANT_NAMES = {
    "variant",
    "tone",
    "size",
    "theme",
    "intent",
    "color",
    "mode",
    "density",
}
STATE_NAMES = {
    "disabled",
    "loading",
    "selected",
    "open",
    "error",
    "dismissible",
    "compact",
    "active",
    "checked",
}
HIDE_NAMES = {"className", "style", "testId", "dataTestId", "asChild"}
BOUNDARY_TEXT_NAMES = {
    "label",
    "title",
    "message",
    "children",
    "text",
    "description",
    "helperText",
}
INTERACTION_HANDLER_MAP = {
    "onClick": "Click",
    "onDismiss": "Dismiss",
    "onChange": "Edit",
    "onSubmit": "Submit",
    "onOpenChange": "OpenClose",
    "onSelect": "Select",
}
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
IGNORED_SCAN_DIRS = {
    ".git",
    ".github",
    ".omx",
    ".claude",
    "node_modules",
    "dist",
    "build",
    "coverage",
    "__pycache__",
}
SUPPORTED_SOURCE_SUFFIXES = {".tsx", ".ts", ".jsx", ".js", ".vue", ".svelte", ".mdx"}
COMPONENT_SUFFIXES = (".tsx", ".ts", ".jsx", ".js", ".vue", ".svelte")
STORY_SUFFIXES = (
    ".stories.tsx",
    ".stories.ts",
    ".stories.jsx",
    ".stories.js",
    ".stories.svelte",
)


def detect_framework(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".vue":
        return "vue"
    if suffix == ".svelte":
        return "svelte"
    return "react"


def discover_repo_root(component_path: Path, explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()

    for parent in [component_path.parent, *component_path.parents]:
        if any((parent / marker).exists() for marker in (".git", "package.json", "pnpm-workspace.yaml")):
            return parent
    return component_path.parent


def split_type_members(body: str) -> list[str]:
    members: list[str] = []
    current: list[str] = []
    depth = 0
    for char in body:
        if char in "{[(":
            depth += 1
        elif char in "}])":
            depth = max(0, depth - 1)
        if char == ";" and depth == 0:
            member = "".join(current).strip()
            if member:
                members.append(member)
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        members.append(tail)
    return members


def split_object_members(body: str) -> list[str]:
    members: list[str] = []
    current: list[str] = []
    depth = 0
    for char in body:
        if char in "{[(":
            depth += 1
        elif char in "}])":
            depth = max(0, depth - 1)
        if char == "," and depth == 0:
            member = "".join(current).strip()
            if member:
                members.append(member)
            current = []
            continue
        current.append(char)
    tail = "".join(current).strip()
    if tail:
        members.append(tail)
    return members


def normalize_whitespace(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def parse_literal(value: str) -> object:
    raw = value.strip().rstrip(",")
    if not raw:
        return None
    if raw in {"true", "false"}:
        return raw == "true"
    if raw == "null":
        return None
    if raw.startswith(("'", '"')) and raw.endswith(("'", '"')) and len(raw) >= 2:
        return raw[1:-1]
    if re.fullmatch(r"-?\d+", raw):
        return int(raw)
    if re.fullmatch(r"-?\d+\.\d+", raw):
        return float(raw)
    return normalize_whitespace(raw)


def extract_string_options(raw_type: str) -> list[str]:
    return [left or right for left, right in STRING_LITERAL_RE.findall(raw_type) if left or right]


def parse_prop_body(body: str) -> list[dict[str, object]]:
    props: list[dict[str, object]] = []
    for member in split_type_members(body):
        line = member.strip()
        if not line or line.startswith("//"):
            continue
        match = PROPERTY_RE.match(line)
        if not match:
            continue
        name = match.group("name")
        raw_type = normalize_whitespace(match.group("type"))
        options = extract_string_options(raw_type)
        props.append(
            {
                "name": name,
                "type": raw_type,
                "optional": bool(match.group("optional")),
                "options": options,
                "isEvent": bool(EVENT_RE.match(name)),
                "isHidden": name in HIDE_NAMES,
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
        name = export_match.group("name")
        raw_type = normalize_whitespace((export_match.group("type") or "unknown").strip())
        props.append(
            {
                "name": name,
                "type": raw_type,
                "optional": True,
                "options": extract_string_options(raw_type),
                "isEvent": bool(EVENT_RE.match(name)),
                "isHidden": name in HIDE_NAMES,
            }
        )

    return dedupe_props(props)


def parse_default_mapping(body: str) -> dict[str, object]:
    mapping: dict[str, object] = {}
    for member in split_object_members(body):
        if ":" in member:
            name, raw_value = member.split(":", 1)
        elif "=" in member:
            name, raw_value = member.split("=", 1)
        else:
            continue
        key = name.strip()
        if not key:
            continue
        mapping[key] = parse_literal(raw_value)
    return mapping


def extract_declared_defaults(source: str) -> dict[str, object]:
    defaults: dict[str, object] = {}

    react_match = REACT_DEFAULTS_RE.search(source)
    if react_match:
        defaults.update(parse_default_mapping(react_match.group("body")))

    with_defaults_match = WITH_DEFAULTS_RE.search(source)
    if with_defaults_match:
        defaults.update(parse_default_mapping(with_defaults_match.group("body")))

    svelte_match = SVELTE_PROPS_RE.search(source)
    if svelte_match:
        defaults.update(parse_default_mapping(svelte_match.group("body")))

    for export_match in EXPORT_LET_RE.finditer(source):
        if export_match.group("default"):
            defaults[export_match.group("name")] = parse_literal(export_match.group("default"))

    return defaults


def sample_value(prop_name: str, raw_type: str, options: list[str], declared_defaults: dict[str, object]) -> object | None:
    if prop_name in declared_defaults and declared_defaults[prop_name] is not None:
        return declared_defaults[prop_name]
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
    if prop_name in {"description", "text", "helperText"}:
        return "Helpful supporting content."
    return None


def to_story_name(value: str) -> str:
    if value in CANONICAL_STORY_NAMES:
        return CANONICAL_STORY_NAMES[value]
    parts = re.split(r"[^A-Za-z0-9]+", value)
    return "".join(part[:1].upper() + part[1:] for part in parts if part) or "Variant"


def pick_variant_values(prop_name: str, options: list[str]) -> list[str]:
    if prop_name == "size":
        chosen = [value for value in ("lg", "xl", "sm") if value in options]
        if chosen:
            return chosen[:1]

    if prop_name == "theme":
        chosen = [value for value in ("light", "dark") if value in options]
        if chosen:
            return chosen[:2]

    chosen = [value for value in PREFERRED_VARIANT_VALUES if value in options]
    if chosen:
        return chosen[:1]

    return options[1:2]


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


def should_skip_scan_path(path: Path) -> bool:
    return any(part in IGNORED_SCAN_DIRS for part in path.parts)


def kebab_to_camel(value: str) -> str:
    parts = value.split("-")
    if not parts:
        return value
    return parts[0] + "".join(part[:1].upper() + part[1:] for part in parts[1:])


def extract_usage_attrs(block: str) -> list[str]:
    attrs: list[str] = []
    for match in re.finditer(
        r"(?:^|\s)([:@]?)([A-Za-z_][A-Za-z0-9:_-]*)(?=(?:\s*=|\s|$))",
        block,
    ):
        marker, raw_name = match.groups()
        if marker == "@":
            continue
        if raw_name.startswith("v-") or raw_name in {"class", "slot", "key", "ref"}:
            continue
        attrs.append(kebab_to_camel(raw_name))
    return sorted(set(attrs))


def is_story_path(path: Path) -> bool:
    return any(path.name.endswith(suffix) for suffix in STORY_SUFFIXES)


def match_story_for_component(component_path: Path) -> Path | None:
    base_name = component_path.stem
    for suffix in STORY_SUFFIXES:
        candidate = component_path.with_name(f"{base_name}{suffix}")
        if candidate.exists():
            return candidate
    return None


def extract_component_tag_matches(text: str, component_name: str) -> list[dict[str, object]]:
    matches: list[dict[str, object]] = []
    needle = f"<{component_name}"
    start = 0
    while True:
        index = text.find(needle, start)
        if index == -1:
            return matches
        cursor = index + len(needle)
        depth = 0
        in_string: str | None = None
        escaped = False
        while cursor < len(text):
            char = text[cursor]
            if in_string:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == in_string:
                    in_string = None
                cursor += 1
                continue
            if char in {"'", '"', "`"}:
                in_string = char
            elif char == "{":
                depth += 1
            elif char == "}":
                depth = max(0, depth - 1)
            elif char == ">" and depth == 0:
                matches.append(
                    {
                        "body": text[index + len(needle) : cursor],
                        "start": index,
                        "end": cursor + 1,
                    }
                )
                break
            cursor += 1
        start = cursor + 1


def extract_component_tag_bodies(text: str, component_name: str) -> list[str]:
    return [str(match["body"]) for match in extract_component_tag_matches(text, component_name)]


def is_expression_binding(raw_value: str | None, marker: str) -> bool:
    if raw_value is None:
        return False
    text = raw_value.strip()
    if marker == ":" and not (text.startswith(("'", '"', "`")) and text.endswith(("'", '"', "`"))):
        return True
    if text.startswith("{") and text.endswith("}"):
        inner = text[1:-1].strip()
        if not inner:
            return False
        parsed = parse_literal(inner)
        return isinstance(parsed, str) and parsed == normalize_whitespace(inner) and not inner.startswith(("'", '"', "`"))
    return False


def parse_usage_value(raw_value: str | None, marker: str) -> object | None:
    if raw_value is None:
        return True if marker != ":" else None
    text = raw_value.strip()
    if text.startswith("{") and text.endswith("}"):
        return parse_literal(text[1:-1])
    return parse_literal(text)


def extract_usage_argument_map(block: str) -> dict[str, object]:
    args: dict[str, object] = {}
    bindings: dict[str, str] = {}

    for match in USAGE_ATTR_RE.finditer(block):
        marker = match.group("marker") or ""
        raw_name = match.group("name")
        raw_value = match.group("value")
        if marker == "@":
            continue
        if raw_name.startswith("v-") or raw_name in {"class", "slot", "key", "ref"}:
            continue
        prop_name = kebab_to_camel(raw_name.split(":")[-1])
        value = parse_usage_value(raw_value, marker)
        if value is not None:
            args[prop_name] = value
        if is_expression_binding(raw_value, marker):
            bindings[prop_name] = normalize_whitespace((raw_value or "").strip("{}"))

    return {"args": args, "bindings": bindings}


def find_enclosing_symbol(text: str, index: int, fallback: str) -> str:
    matches = [match.group("name") for match in DECLARATION_RE.finditer(text[:index])]
    if matches:
        return matches[-1]
    return fallback


def collect_context_components(region: str, component_name: str) -> list[str]:
    seen: list[str] = []
    for name in JSX_COMPONENT_RE.findall(region):
        if name == component_name or name in seen:
            continue
        seen.append(name)
    return seen[:5]


def infer_layout_hint(region: str, sibling_components: list[str], semantic_wrappers: list[str]) -> str:
    lowered = region.lower()
    if "onsubmit" in lowered or "form" in semantic_wrappers:
        return "form flow"
    if "grid" in lowered:
        return "grid layout"
    if any(wrapper in {"aside", "section"} for wrapper in semantic_wrappers):
        return "panel composition"
    if "dialog" in lowered or "modal" in lowered:
        return "dialog surface"
    if sibling_components:
        return "composed parent layout"
    return "inline parent context"


def collect_composition_stories(component_name: str, component_path: Path, repo_root: Path) -> list[dict[str, object]]:
    candidates: list[dict[str, object]] = []
    used_story_names: set[str] = set()

    for candidate in repo_root.rglob("*"):
        if not candidate.is_file() or candidate.suffix.lower() not in SUPPORTED_SOURCE_SUFFIXES:
            continue
        if candidate.resolve() == component_path.resolve():
            continue
        if ".expected." in candidate.name or ".before." in candidate.name or is_story_path(candidate):
            continue
        if should_skip_scan_path(candidate.relative_to(repo_root)):
            continue

        text = candidate.read_text(encoding="utf-8", errors="ignore")
        for match in extract_component_tag_matches(text, component_name):
            usage = extract_usage_argument_map(str(match["body"]))
            start = int(match["start"])
            end = int(match["end"])
            region = text[max(0, start - 280) : min(len(text), end + 280)]
            parent_component = find_enclosing_symbol(text, start, candidate.stem)
            sibling_components = collect_context_components(region, component_name)
            semantic_wrappers = [wrapper.lower() for wrapper in SEMANTIC_CONTAINER_RE.findall(region)]
            layout = infer_layout_hint(region, sibling_components, semantic_wrappers)

            story_name = f"In{to_story_name(parent_component)}"
            if story_name in used_story_names:
                story_name = f"{story_name}{to_story_name(candidate.stem)}"
            used_story_names.add(story_name)

            literal_args = {
                name: value
                for name, value in usage["args"].items()
                if name not in usage["bindings"]
            }
            confidence = min(
                95,
                50
                + min(len(literal_args) * 10, 20)
                + min(len(usage["bindings"]) * 5, 10)
                + (10 if sibling_components else 0)
                + (5 if semantic_wrappers else 0),
            )

            candidates.append(
                {
                    "storyName": story_name,
                    "parentComponent": parent_component,
                    "parentFile": candidate.relative_to(repo_root).as_posix(),
                    "layout": layout,
                    "args": literal_args,
                    "bindings": usage["bindings"],
                    "siblingComponents": sibling_components,
                    "wrappers": semantic_wrappers[:3],
                    "confidence": confidence,
                }
            )

    return sorted(
        candidates,
        key=lambda item: (-int(item["confidence"]), str(item["parentFile"]), str(item["storyName"])),
    )[:5]


def collect_usage_signals(component_name: str, component_path: Path, repo_root: Path) -> dict[str, object]:
    prop_counts: dict[str, int] = {}
    pair_counts: dict[str, int] = {}
    matches = 0
    files_scanned = 0
    examples: list[dict[str, object]] = []

    for candidate in repo_root.rglob("*"):
        if not candidate.is_file() or candidate.suffix.lower() not in SUPPORTED_SOURCE_SUFFIXES:
            continue
        if candidate.resolve() == component_path.resolve():
            continue
        if ".stories." in candidate.name or ".expected." in candidate.name or ".before." in candidate.name:
            continue
        if should_skip_scan_path(candidate.relative_to(repo_root)):
            continue
        files_scanned += 1
        text = candidate.read_text(encoding="utf-8", errors="ignore")
        for body in extract_component_tag_bodies(text, component_name):
            attrs = extract_usage_attrs(body)
            if not attrs:
                continue
            matches += 1
            for attr in attrs:
                prop_counts[attr] = prop_counts.get(attr, 0) + 1
            for index, left in enumerate(attrs):
                for right in attrs[index + 1 :]:
                    key = " + ".join(sorted((left, right)))
                    pair_counts[key] = pair_counts.get(key, 0) + 1
            if len(examples) < 5:
                examples.append({"file": candidate.relative_to(repo_root).as_posix(), "props": attrs})

    prop_signals = [
        {"prop": prop, "count": count}
        for prop, count in sorted(prop_counts.items(), key=lambda item: (-item[1], item[0]))
    ]
    cooccurrence = [
        {"pair": pair, "count": count}
        for pair, count in sorted(pair_counts.items(), key=lambda item: (-item[1], item[0]))[:5]
    ]

    return {
        "filesScanned": files_scanned,
        "matches": matches,
        "props": prop_signals,
        "cooccurrence": cooccurrence,
        "examples": examples,
    }


def collect_branch_signals(source: str, props: list[dict[str, object]]) -> list[dict[str, object]]:
    logic_source = PROPS_BLOCK_RE.sub("", source)
    logic_source = DEFINE_PROPS_INLINE_RE.sub("", logic_source)
    signals: list[dict[str, object]] = []
    for prop in props:
        name = str(prop["name"])
        pattern = re.compile(
            rf"(?:if\s*\([^)]*\b{name}\b[^)]*\)|\b{name}\b\s*\?|"
            rf"\b{name}\b\s*&&|!\s*{name}\b|Boolean\(\s*{name}\s*\))"
        )
        count = len(pattern.findall(logic_source))
        if count:
            reason = "conditional branch"
            if name in STATE_NAMES:
                reason = "state gate"
            elif name in VARIANT_NAMES:
                reason = "variant branch"
            signals.append({"prop": name, "count": count, "reason": reason})
    return signals


def recommend_stories(
    props: list[dict[str, object]],
    usage_signals: dict[str, object],
    branch_signals: list[dict[str, object]],
) -> list[dict[str, str]]:
    stories: list[dict[str, str]] = [{"name": "Default", "lens": "baseline"}]
    seen = {"Default"}
    usage_counts = {item["prop"]: item["count"] for item in usage_signals.get("props", [])}
    branch_props = {item["prop"] for item in branch_signals}

    for prop in props:
        name = str(prop["name"])
        options = list(prop["options"])
        if name in VARIANT_NAMES and options:
            ranked = pick_variant_values(name, options)
            ranked = sorted(ranked, key=lambda option: (-usage_counts.get(name, 0), option))
            for option in ranked:
                story_name = to_story_name(option)
                if story_name not in seen:
                    stories.append({"name": story_name, "lens": "decision"})
                    seen.add(story_name)

    for prop in props:
        name = str(prop["name"])
        if name in STATE_NAMES or (
            name in branch_props
            and not prop["isEvent"]
            and not prop["options"]
            and "boolean" in str(prop["type"])
        ):
            story_name = to_story_name(name)
            if story_name not in seen:
                stories.append({"name": story_name, "lens": "state"})
                seen.add(story_name)

    if any(str(prop["name"]) in BOUNDARY_TEXT_NAMES for prop in props):
        if "LongContent" not in seen:
            stories.append({"name": "LongContent", "lens": "boundary"})
            seen.add("LongContent")

    return stories


def build_interaction_recommendations(props: list[dict[str, object]]) -> list[dict[str, object]]:
    interactions: list[dict[str, object]] = []
    for prop in props:
        name = str(prop["name"])
        if not prop["isEvent"]:
            continue
        story_name = INTERACTION_HANDLER_MAP.get(name, to_story_name(name[2:]) if name.startswith("on") else "Action")
        step = "click the primary trigger"
        assertion = f"assert {name} was called"
        if name == "onChange":
            step = "type a changed value with userEvent.type"
            assertion = "assert value-driven UI updates or handler calls"
        elif name == "onSubmit":
            step = "fill required fields, then submit the form"
            assertion = "assert submit handler was called once with valid state"
        elif name == "onDismiss":
            step = "activate the dismiss button with mouse and keyboard"
            assertion = "assert the dismiss handler fires and focus remains sane"
        interactions.append(
            {
                "storyName": f"{story_name}Flow",
                "handler": name,
                "steps": [step],
                "assertion": assertion,
                "import": "storybook/test",
            }
        )
    return interactions


def build_accessibility_recommendations(props: list[dict[str, object]]) -> list[dict[str, object]]:
    recs: list[dict[str, object]] = []
    prop_names = {str(prop["name"]) for prop in props}

    if {"title", "message"} & prop_names:
        recs.append(
            {
                "storyName": "ScreenReaderSummary",
                "focus": "Labeling and message announcement",
                "wcag": ["1.3.1", "4.1.2"],
            }
        )
    if {"dismissible", "onDismiss"} & prop_names:
        recs.append(
            {
                "storyName": "KeyboardDismiss",
                "focus": "Keyboard-only activation and focus order",
                "wcag": ["2.1.1", "2.4.3"],
            }
        )
    if {"disabled", "loading"} & prop_names:
        recs.append(
            {
                "storyName": "BusyAndDisabledStates",
                "focus": "Disabled semantics and busy messaging",
                "wcag": ["4.1.2", "3.3.2"],
            }
        )
    if {"label", "description", "helperText", "error"} & prop_names:
        recs.append(
            {
                "storyName": "FieldNarration",
                "focus": "Visible labels and described-by relationships",
                "wcag": ["1.3.1", "3.3.1"],
            }
        )
    return recs


def build_visual_diff_plan(stories: list[dict[str, str]], interactions: list[dict[str, object]]) -> dict[str, object]:
    capture = [story["name"] for story in stories if story["lens"] in {"baseline", "decision", "state", "boundary"}]
    return {
        "mode": "visual-regression-codex",
        "harnesses": ["Chromatic", "Playwright screenshot test"],
        "captureStories": capture,
        "interactionStories": [item["storyName"] for item in interactions],
        "notes": [
            "Capture the stable default story first, then branch states that change layout or density.",
            "Keep local screenshot thresholds narrow when stories are token-aware or theme-aware.",
        ],
    }


def build_notes(
    props: list[dict[str, object]],
    usage_signals: dict[str, object],
    branch_signals: list[dict[str, object]],
    composition_stories: list[dict[str, object]],
) -> list[str]:
    notes: list[str] = []
    if any(prop["isEvent"] for prop in props):
        notes.append("Use fn() from storybook/test for event handlers and hide direct controls for them.")
    hidden = [str(prop["name"]) for prop in props if prop["isHidden"]]
    if hidden:
        notes.append(f"Hide internal props from docs tables and controls: {', '.join(hidden)}.")
    if any(str(prop["name"]) in VARIANT_NAMES for prop in props):
        notes.append("Prefer one or two decision stories over rendering every enum combination.")
    if usage_signals.get("matches"):
        notes.append("Bias stories toward prop combinations already used together in the app.")
    if branch_signals:
        notes.append("Props that gate conditional branches deserve explicit state or boundary stories.")
    if composition_stories:
        notes.append("Add at least one parent-context story so the component is reviewed where it actually ships.")
    return notes


def build_blueprint(component_path: Path, repo_root: Path | None = None) -> dict[str, object]:
    source = component_path.read_text(encoding="utf-8")
    props = parse_props(source)
    declared_defaults = extract_declared_defaults(source)
    resolved_repo_root = repo_root or discover_repo_root(component_path)
    usage_signals = collect_usage_signals(component_path.stem, component_path, resolved_repo_root)
    composition_stories = collect_composition_stories(component_path.stem, component_path, resolved_repo_root)
    branch_signals = collect_branch_signals(source, props)
    defaults: dict[str, object] = {}

    for prop in props:
        value = sample_value(
            str(prop["name"]),
            str(prop["type"]),
            list(prop["options"]),
            declared_defaults,
        )
        if value is not None:
            defaults[str(prop["name"])] = value

    interactions = build_interaction_recommendations(props)
    stories = recommend_stories(props, usage_signals, branch_signals)
    a11y = build_accessibility_recommendations(props)

    return {
        "component": component_path.stem,
        "componentPath": str(component_path),
        "framework": detect_framework(component_path),
        "repoRoot": str(resolved_repo_root),
        "props": props,
        "defaultArgs": defaults,
        "controls": recommend_controls(props),
        "stories": stories,
        "notes": build_notes(props, usage_signals, branch_signals, composition_stories),
        "lenses": ["baseline", "decision", "state", "boundary", "action", "a11y", "visual"],
        "usageSignals": usage_signals,
        "compositionStories": composition_stories,
        "branchSignals": branch_signals,
        "interactionStories": interactions,
        "accessibilityStories": a11y,
        "visualDiff": build_visual_diff_plan(stories, interactions),
    }


def story_framework_from_text(text: str, story_path: Path) -> str:
    if story_path.suffix.lower() == ".svelte" or "@storybook/addon-svelte-csf" in text:
        return "svelte"
    if "@storybook/vue3" in text or "@storybook/vue3-vite" in text:
        return "vue"
    return "react"


def extract_story_names(text: str, framework: str) -> list[str]:
    if framework == "svelte":
        return SVELTE_STORY_RE.findall(text)
    return STORY_EXPORT_RE.findall(text)


def extract_story_args_for_state(text: str, prop_name: str) -> bool:
    return bool(re.search(rf"\b{re.escape(prop_name)}\s*:\s*(?:true|['\"]\w+['\"])", text))


def extract_story_file_info(story_path: Path) -> dict[str, object]:
    text = story_path.read_text(encoding="utf-8")
    framework = story_framework_from_text(text, story_path)
    imports = IMPORT_FROM_RE.findall(text)
    return {
        "path": str(story_path),
        "framework": framework,
        "title": TITLE_RE.search(text).group(1) if TITLE_RE.search(text) else "",
        "componentName": COMPONENT_META_RE.search(text).group(1) if COMPONENT_META_RE.search(text) else "",
        "storyNames": extract_story_names(text, framework),
        "hasAutodocs": bool(AUTODOCS_RE.search(text)),
        "hasArgTypes": bool(ARGTYPES_RE.search(text)),
        "hasPlay": bool(PLAY_RE.search(text)),
        "hasA11y": bool(A11Y_RE.search(text) or PARAMETERS_A11Y_RE.search(text)),
        "hasVisual": bool(CHROMATIC_RE.search(text)),
        "usesStorybookTest": "storybook/test" in imports or "storybook/test" in text,
        "usesLegacyStorybookTest": "@storybook/test" in text,
        "usesLegacyStorySyntax": bool(LEGACY_STORY_RE.search(text)),
        "text": text,
    }


def infer_lens_coverage(blueprint: dict[str, object], story_info: dict[str, object]) -> dict[str, bool]:
    text = str(story_info["text"])
    story_names = set(story_info["storyNames"])
    prop_names = {str(prop["name"]) for prop in blueprint.get("props", [])}
    variant_props = prop_names & VARIANT_NAMES
    state_props = prop_names & STATE_NAMES

    has_decision = any(
        story["lens"] == "decision" and story["name"] in story_names
        for story in blueprint.get("stories", [])
    )
    has_state = any(extract_story_args_for_state(text, name) for name in prop_names & STATE_NAMES)
    has_boundary = "LongContent" in story_names or bool(re.search(r"Helpful supporting text\.|Helpful supporting content\.|.{24,}", text))
    has_action = bool(blueprint.get("interactionStories")) and (
        story_info["hasPlay"] or "fn()" in text or "storybook/test" in text or "@storybook/test" in text
    )

    return {
        "baseline": bool(story_names),
        "decision": True if not variant_props else has_decision or bool(story_info["hasArgTypes"]),
        "state": True
        if not state_props
        else has_state
        or any(
            story["lens"] == "state" and story["name"] in story_names
            for story in blueprint.get("stories", [])
        ),
        "boundary": has_boundary if prop_names & BOUNDARY_TEXT_NAMES else True,
        "action": has_action if blueprint.get("interactionStories") else True,
        "a11y": bool(story_info["hasA11y"]) if blueprint.get("accessibilityStories") else True,
        "visual": bool(story_info["hasVisual"]),
    }


def review_story(component_path: Path, story_path: Path, repo_root: Path | None = None) -> dict[str, object]:
    blueprint = build_blueprint(component_path, repo_root)
    story_info = extract_story_file_info(story_path)
    lens_coverage = infer_lens_coverage(blueprint, story_info)
    issues: list[dict[str, str]] = []

    def add_issue(severity: str, code: str, message: str) -> None:
        issues.append({"severity": severity, "code": code, "message": message})

    if story_info["usesLegacyStorySyntax"]:
        add_issue("high", "legacy-syntax", "Story file still uses Template.bind or deprecated Storybook utility types.")
    if story_info["usesLegacyStorybookTest"]:
        add_issue("medium", "legacy-test-import", "Replace @storybook/test with storybook/test for Storybook 9 readiness.")
    if not story_info["hasAutodocs"]:
        add_issue("medium", "missing-autodocs", "Add autodocs tags at the preview or meta level.")
    if blueprint.get("interactionStories") and not lens_coverage["action"]:
        add_issue("medium", "missing-interactions", "Event-driven components should ship at least one play() flow or fn() action harness.")
    if blueprint.get("accessibilityStories") and not lens_coverage["a11y"]:
        add_issue("medium", "missing-a11y", "Add addon-a11y parameters or an explicit accessibility story lens.")
    if not lens_coverage["visual"]:
        add_issue("low", "missing-visual-regression", "Add Chromatic or local screenshot coverage for the stable stories.")

    for lens, covered in lens_coverage.items():
        if not covered and lens not in {"a11y", "visual"}:
            add_issue("low", f"missing-{lens}", f"The {lens} lens is not clearly represented in the current story set.")

    score = 100
    for issue in issues:
        penalty = {"high": 20, "medium": 10, "low": 5}[issue["severity"]]
        score -= penalty
    score = max(0, score)

    return {
        "component": blueprint["component"],
        "componentPath": str(component_path),
        "storyPath": str(story_path),
        "storyNames": story_info["storyNames"],
        "framework": story_info["framework"],
        "score": score,
        "lensCoverage": lens_coverage,
        "issues": issues,
        "suggestions": [
            "Mirror the highest-signal branch props first, then add interaction and accessibility flows.",
            "Keep visual baselines aligned with design-token globals so screenshot diffs stay intentional.",
        ],
        "blueprint": blueprint,
    }


def render_markdown(blueprint: dict[str, object]) -> str:
    lines: list[str] = []
    lines.append(f"# {blueprint['component']} blueprint")
    lines.append(f"\n_Framework_: {blueprint['framework']}")

    props = list(blueprint.get("props", []))
    if props:
        lines.append("\n## Props")
        for prop in props:
            flags: list[str] = []
            if prop.get("optional"):
                flags.append("optional")
            if prop.get("isEvent"):
                flags.append("event")
            if prop.get("isHidden"):
                flags.append("hidden")
            suffix = f" _({', '.join(flags)})_" if flags else ""
            lines.append(f"- `{prop['name']}`: `{prop['type']}`{suffix}")

    default_args = blueprint.get("defaultArgs", {}) or {}
    if default_args:
        lines.append("\n## Default args")
        for name, value in default_args.items():
            lines.append(f"- `{name}`: {json.dumps(value)}")

    controls = blueprint.get("controls", {}) or {}
    if controls:
        lines.append("\n## Controls")
        for name, config in controls.items():
            lines.append(f"- `{name}`: {json.dumps(config, sort_keys=True)}")

    stories = list(blueprint.get("stories", []))
    if stories:
        lines.append("\n## Recommended stories")
        for story in stories:
            lines.append(f"- {story['name']} ({story['lens']})")

    usage = blueprint.get("usageSignals", {})
    if usage.get("matches"):
        lines.append("\n## Usage signals")
        lines.append(f"- Matches found: {usage['matches']} across {usage['filesScanned']} scanned files")
        for item in usage.get("props", [])[:5]:
            lines.append(f"- `{item['prop']}` appears in {item['count']} usage sites")
        for pair in usage.get("cooccurrence", [])[:3]:
            lines.append(f"- Co-occurs: `{pair['pair']}` ({pair['count']})")

    composition = blueprint.get("compositionStories", [])
    if composition:
        lines.append("\n## Composition stories")
        for item in composition:
            args = ", ".join(f"{name}={json.dumps(value)}" for name, value in item.get("args", {}).items())
            binding_names = ", ".join(sorted(item.get("bindings", {}).keys()))
            details = [item["layout"], item["parentFile"]]
            if args:
                details.append(args)
            if binding_names:
                details.append(f"bindings: {binding_names}")
            lines.append(f"- {item['storyName']}: {'; '.join(details)}")

    branches = blueprint.get("branchSignals", [])
    if branches:
        lines.append("\n## Branch signals")
        for branch in branches:
            lines.append(f"- `{branch['prop']}`: {branch['reason']} ({branch['count']})")

    interactions = blueprint.get("interactionStories", [])
    if interactions:
        lines.append("\n## Interaction stories")
        for interaction in interactions:
            lines.append(
                f"- {interaction['storyName']}: {interaction['steps'][0]} -> {interaction['assertion']}"
            )

    a11y = blueprint.get("accessibilityStories", [])
    if a11y:
        lines.append("\n## Accessibility stories")
        for item in a11y:
            lines.append(f"- {item['storyName']}: {item['focus']} (WCAG {', '.join(item['wcag'])})")

    visual = blueprint.get("visualDiff", {})
    if visual:
        lines.append("\n## Visual diff plan")
        lines.append(f"- Harnesses: {', '.join(visual.get('harnesses', []))}")
        lines.append(f"- Capture: {', '.join(visual.get('captureStories', []))}")

    notes = list(blueprint.get("notes", []))
    if notes:
        lines.append("\n## Notes")
        for note in notes:
            lines.append(f"- {note}")

    review = blueprint.get("review")
    if isinstance(review, dict):
        lines.append("\n## Review")
        lines.append(f"- Score: {review['score']}")
        for issue in review.get("issues", []):
            lines.append(f"- {issue['severity']}: {issue['message']}")

    return "\n".join(lines)
