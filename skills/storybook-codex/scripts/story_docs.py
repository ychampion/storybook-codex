#!/usr/bin/env python3
"""Generate Storybook documentation stories or MDX docs pages."""

from __future__ import annotations

import argparse
import json
import re
import sys
import textwrap
from pathlib import Path

from storybook_codex_lib import STATE_NAMES, VARIANT_NAMES, build_blueprint


TITLE_RE = re.compile(r"title:\s*['\"]([^'\"]+)['\"]")
DEFAULT_EXPORT_RE = re.compile(
    r"export\s+default\s+(?:function\s+)?(?P<name>[A-Za-z_][A-Za-z0-9_]*)?",
)
DEFAULT_ALIAS_RE = re.compile(
    r"export\s*{\s*(?P<name>[A-Za-z_][A-Za-z0-9_]*)\s+as\s+default\s*}",
)
IGNORED_DIRS = {
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
STORY_SUFFIXES = (
    ".stories.tsx",
    ".stories.ts",
    ".stories.jsx",
    ".stories.js",
    ".stories.svelte",
)


def discover_repo_root(component_path: Path, explicit_root: str | None = None) -> Path:
    if explicit_root:
        return Path(explicit_root).resolve()

    for parent in [component_path.parent, *component_path.parents]:
        if any((parent / marker).exists() for marker in (".git", "package.json", "pnpm-workspace.yaml")):
            return parent
    return component_path.parent


def should_skip(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def strip_known_suffixes(path: Path) -> str:
    name = path.name
    for suffix in (".tsx", ".ts", ".jsx", ".js", ".svelte", ".vue", ".mdx"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name


def find_story_path(component_path: Path) -> Path | None:
    base_name = component_path.stem
    for suffix in STORY_SUFFIXES:
        candidate = component_path.with_name(f"{base_name}{suffix}")
        if candidate.exists():
            return candidate
    return None


def component_import_statement(component_name: str, framework: str, component_path: Path) -> str:
    import_path = f"./{strip_known_suffixes(component_path)}"
    source = component_path.read_text(encoding="utf-8", errors="ignore")
    if has_default_export(source, component_name):
        return f"import {component_name} from '{import_path}';"
    if framework == "vue":
        return f"import {component_name} from '{import_path}';"
    return f"import {{ {component_name} }} from '{import_path}';"


def story_import_statement(story_path: Path | None) -> str:
    if story_path is None:
        return ""
    return f"import * as ComponentStories from './{strip_known_suffixes(story_path)}';"


def docs_title(component_name: str, story_path: Path | None, override: str | None = None) -> str:
    if override:
        return override
    if story_path and story_path.exists():
        story_text = story_path.read_text(encoding="utf-8")
        match = TITLE_RE.search(story_text)
        if match:
            return f"{match.group(1)}/Docs"
    return f"Components/{component_name}/Docs"


def humanize_name(value: str) -> str:
    spaced = re.sub(r"(?<!^)([A-Z])", r" \1", value.replace("-", " ").replace("_", " "))
    return re.sub(r"\s+", " ", spaced).strip()


def has_default_export(source: str, component_name: str) -> bool:
    alias_match = DEFAULT_ALIAS_RE.search(source)
    if alias_match:
        return alias_match.group("name") == component_name

    default_match = DEFAULT_EXPORT_RE.search(source)
    if not default_match:
        return False

    exported_name = default_match.group("name")
    return exported_name is None or exported_name == component_name


def docs_purpose(blueprint: dict[str, object]) -> str:
    component_name = humanize_name(str(blueprint["component"]))
    props = list(blueprint.get("props", []))
    prop_names = {str(prop["name"]) for prop in props}
    if any(prop.get("isEvent") for prop in props):
        return (
            f"Use {component_name} when the UI needs a focused action surface with consistent variants, "
            "reviewable state transitions, and a clear handler contract."
        )
    if {"title", "message", "description"} & prop_names:
        return (
            f"Use {component_name} to present a repeatable content or messaging pattern with explicit tone and "
            "copy decisions."
        )
    return (
        f"Use {component_name} as a reusable component when the team wants a small surface with documented "
        "variants, states, and common implementation guidance."
    )


def docs_when_to_use(blueprint: dict[str, object]) -> list[str]:
    props = list(blueprint.get("props", []))
    prop_names = {str(prop["name"]) for prop in props}
    items: list[str] = []
    if any(prop.get("isEvent") for prop in props):
        items.append("Use it when the component owns a user-triggered action that should stay visible and testable in Storybook.")
    if prop_names & VARIANT_NAMES:
        items.append("Use it when design decisions like tone, size, or theme should stay on a constrained prop surface.")
    if prop_names & STATE_NAMES:
        items.append("Use it when disabled, loading, selected, or similar states change behavior and need explicit docs coverage.")
    if not items:
        items.append("Use it when the UI needs a small, repeatable surface with one clear responsibility.")
    return items[:3]


def docs_when_not_to_use(blueprint: dict[str, object]) -> list[str]:
    props = list(blueprint.get("props", []))
    prop_names = {str(prop["name"]) for prop in props}
    items: list[str] = []
    if prop_names & VARIANT_NAMES:
        items.append("Do not create one-off visual treatments when an existing variant already communicates the intent.")
    if prop_names & STATE_NAMES:
        items.append("Do not hide important state transitions outside Storybook if those states change affordance or behavior.")
    if "children" not in prop_names and not (prop_names & {"title", "message", "description", "label"}):
        items.append("Do not stretch it into a broad layout or long-form content primitive.")
    if not items:
        items.append("Do not use it for page structure or parent layout when a dedicated container should own that job.")
    return items[:3]


def docs_prop_guidance(blueprint: dict[str, object]) -> list[dict[str, str]]:
    props = list(blueprint.get("props", []))
    controls = dict(blueprint.get("controls", {}))
    guidance: list[dict[str, str]] = []

    for prop in props:
        name = str(prop["name"])
        if prop.get("isHidden"):
            continue
        if prop.get("isEvent"):
            guidance.append(
                {
                    "prop": name,
                    "guidance": "Treat this as a handler contract. Prefer fn() or a real callback instead of a manual control.",
                }
            )
        elif name in VARIANT_NAMES:
            options = ", ".join(list(prop.get("options", []))[:4]) or "the supported values"
            guidance.append(
                {
                    "prop": name,
                    "guidance": f"Use this to make one semantic visual decision at a time. Preferred values: {options}.",
                }
            )
        elif name in STATE_NAMES:
            guidance.append(
                {
                    "prop": name,
                    "guidance": "Document this explicitly because it changes behavior, affordance, or visual state.",
                }
            )
        elif name in controls:
            guidance.append(
                {
                    "prop": name,
                    "guidance": f"Expose this in docs because Storybook can already control it as {controls[name].get('control', 'a control')}.",
                }
            )

    return guidance[:5]


def extract_component_snippets(text: str, component_name: str) -> list[str]:
    snippets: list[str] = []
    needle = f"<{component_name}"
    start = 0
    while True:
        index = text.find(needle, start)
        if index == -1:
            return snippets
        cursor = index + len(needle)
        depth = 0
        in_string: str | None = None
        escaped = False
        open_end = None
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
                open_end = cursor + 1
                break
            cursor += 1

        if open_end is None:
            return snippets

        open_tag = text[index:open_end]
        if open_tag.rstrip().endswith("/>"):
            snippets.append(textwrap.dedent(open_tag).strip())
            start = open_end
            continue

        closing = f"</{component_name}>"
        close_index = text.find(closing, open_end)
        if close_index == -1:
            snippets.append(textwrap.dedent(open_tag).strip())
            start = open_end
            continue

        full_snippet = text[index : close_index + len(closing)]
        snippets.append(textwrap.dedent(full_snippet).strip())
        start = close_index + len(closing)


def collect_usage_snippets(component_name: str, component_path: Path, repo_root: Path) -> list[dict[str, str]]:
    snippets: list[dict[str, str]] = []
    seen: set[str] = set()

    for candidate in sorted(repo_root.rglob("*")):
        if not candidate.is_file() or candidate.suffix.lower() not in SUPPORTED_SOURCE_SUFFIXES:
            continue
        if candidate.resolve() == component_path.resolve():
            continue
        if ".stories." in candidate.name or ".expected." in candidate.name or should_skip(candidate.relative_to(repo_root)):
            continue

        text = candidate.read_text(encoding="utf-8", errors="ignore")
        for snippet in extract_component_snippets(text, component_name):
            normalized = re.sub(r"\s+", " ", snippet).strip()
            if normalized in seen:
                continue
            seen.add(normalized)
            snippets.append({"file": candidate.relative_to(repo_root).as_posix(), "code": snippet})
            if len(snippets) >= 3:
                return snippets
    return snippets


def js_value(value: object, framework: str) -> str:
    if isinstance(value, bool):
        if framework == "vue":
            return "true" if value else "false"
        return "true" if value else "false"
    if value is None:
        return "null"
    if isinstance(value, (int, float)):
        return str(value)
    return json.dumps(value)


def render_invocation(component_name: str, args: dict[str, object], framework: str) -> str:
    attrs: list[str] = []
    children = None
    for name, value in args.items():
        if name == "children":
            children = value
            continue
        if isinstance(value, bool):
            if framework == "vue":
                attrs.append(f":{name}=\"{'true' if value else 'false'}\"")
            elif value:
                attrs.append(name)
            else:
                attrs.append(f"{name}={{{js_value(value, framework)}}}")
            continue
        attrs.append(f"{name}={js_value(value, framework)}")

    attr_suffix = ""
    if attrs:
        attr_suffix = "\n  " + "\n  ".join(attrs)

    if children is not None:
        return f"<{component_name}{attr_suffix}>\n  {children}\n</{component_name}>"
    if attr_suffix:
        return f"<{component_name}{attr_suffix}\n/>"
    return f"<{component_name} />"


def pattern_name(code: str, index: int) -> str:
    lowered = code.lower()
    if "loading" in lowered:
        return "Busy state"
    if "danger" in lowered or "destructive" in lowered:
        return "Destructive action"
    if "brand" in lowered or "primary" in lowered or "publish" in lowered:
        return "Primary action"
    if "disabled" in lowered:
        return "Disabled action"
    return f"Common pattern {index}"


def build_usage_patterns(blueprint: dict[str, object], component_path: Path, repo_root: Path) -> list[dict[str, str]]:
    component_name = str(blueprint["component"])
    framework = str(blueprint["framework"])
    snippets = collect_usage_snippets(component_name, component_path, repo_root)
    patterns: list[dict[str, str]] = []

    for index, snippet in enumerate(snippets, start=1):
        patterns.append(
            {
                "name": pattern_name(snippet["code"], index),
                "summary": f"Observed in {snippet['file']}.",
                "code": snippet["code"],
            }
        )

    if patterns:
        return patterns[:3]

    fallback_args = dict(blueprint.get("defaultArgs", {}))
    filtered_args = {
        name: value
        for name, value in fallback_args.items()
        if name not in {str(prop["name"]) for prop in blueprint.get("props", []) if prop.get("isEvent") or prop.get("isHidden")}
    }
    patterns.append(
        {
            "name": "Baseline",
            "summary": "Default setup derived from the component API.",
            "code": render_invocation(component_name, filtered_args, framework),
        }
    )

    for story in blueprint.get("stories", []):
        story_name = story["name"]
        if story_name == "Default":
            continue
        args = dict(filtered_args)
        lowered = story_name.lower()
        if lowered in {name.lower() for name in STATE_NAMES}:
            args[lowered] = True
        elif lowered == "longcontent":
            if "children" in filtered_args:
                args["children"] = "Use a longer piece of content here so the boundary behavior stays visible in docs."
            elif "label" in filtered_args:
                args["label"] = "Use a longer piece of content here so the boundary behavior stays visible in docs."
        else:
            for prop in blueprint.get("props", []):
                if str(prop["name"]) in VARIANT_NAMES:
                    for option in prop.get("options", []):
                        if humanize_name(str(option)).replace(" ", "").lower() == story_name.lower():
                            args[str(prop["name"])] = option
        patterns.append(
            {
                "name": humanize_name(story_name),
                "summary": "Docs-oriented example derived from the recommended story set.",
                "code": render_invocation(component_name, args, framework),
            }
        )
        if len(patterns) >= 3:
            break

    return patterns[:3]


def build_docs_plan(component_path: Path, repo_root: Path) -> dict[str, object]:
    blueprint = build_blueprint(component_path, repo_root)
    return {
        "component": blueprint["component"],
        "componentPath": str(component_path),
        "framework": blueprint["framework"],
        "purpose": docs_purpose(blueprint),
        "whenToUse": docs_when_to_use(blueprint),
        "whenNotToUse": docs_when_not_to_use(blueprint),
        "propGuidance": docs_prop_guidance(blueprint),
        "usagePatterns": build_usage_patterns(blueprint, component_path, repo_root),
        "blueprint": blueprint,
    }


def render_docs_markdown(plan: dict[str, object]) -> str:
    lines = ["## Purpose", str(plan["purpose"]), "", "## When to use"]
    for item in plan.get("whenToUse", []):
        lines.append(f"- {item}")
    lines.extend(["", "## When not to use"])
    for item in plan.get("whenNotToUse", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Prop decision guidance"])
    for item in plan.get("propGuidance", []):
        lines.append(f"- `{item['prop']}`: {item['guidance']}")
    lines.extend(["", "## Common usage patterns"])
    for pattern in plan.get("usagePatterns", []):
        lines.extend(
            [
                f"### {pattern['name']}",
                pattern["summary"],
                "```tsx" if plan["framework"] == "react" else ("```vue" if plan["framework"] == "vue" else "```svelte"),
                pattern["code"],
                "```",
            ]
        )
    return "\n".join(lines)


def render_object_property(name: str, value: dict[str, object], indent: str = "  ") -> str:
    rendered = json.dumps(value, indent=2).splitlines()
    if not rendered:
        return f"{indent}{name}: {{}}"
    return "\n".join(
        [f"{indent}{name}: {rendered[0]}", *[f"{indent}{line}" for line in rendered[1:]]]
    )


def render_csf_docs(
    plan: dict[str, object],
    component_path: Path,
    story_path: Path | None,
    title: str,
) -> str:
    framework = str(plan["framework"])
    component_name = str(plan["component"])
    if framework == "vue":
        meta_import = "import type { Meta, StoryObj } from '@storybook/vue3-vite';"
    else:
        meta_import = "import type { Meta, StoryObj } from '@storybook/react';"

    component_markdown = render_docs_markdown(plan)
    story_markdown = "\n".join(
        [
            "## Common usage patterns",
            *[
                "\n".join(
                    [
                        f"### {pattern['name']}",
                        pattern["summary"],
                        "```tsx" if framework == "react" else ("```vue" if framework == "vue" else "```svelte"),
                        pattern["code"],
                        "```",
                    ]
                )
                for pattern in plan.get("usagePatterns", [])
            ],
        ]
    )
    example_code = plan.get("usagePatterns", [{}])[0].get("code", "")
    args = {
        name: value
        for name, value in plan["blueprint"].get("defaultArgs", {}).items()
        if name not in {str(prop["name"]) for prop in plan["blueprint"].get("props", []) if prop.get("isEvent") or prop.get("isHidden")}
    }
    args_property = render_object_property("args", args)

    return "\n".join(
        [
            meta_import,
            component_import_statement(component_name, framework, component_path),
            "",
            "const meta = {",
            f"  title: {json.dumps(title)},",
            f"  component: {component_name},",
            "  tags: ['autodocs'],",
            "  parameters: {",
            "    docs: {",
            "      description: {",
            f"        component: {json.dumps(component_markdown)},",
            "      },",
            "    },",
            "  },",
            f"}} satisfies Meta<typeof {component_name}>;",
            "",
            "export default meta;",
            "type Story = StoryObj<typeof meta>;",
            "",
            "export const Documentation: Story = {",
            "  name: 'Docs',",
            f"{args_property},",
            "  parameters: {",
            "    docs: {",
            "      description: {",
            f"        story: {json.dumps(story_markdown)},",
            "      },",
            "      source: {",
            f"        code: {json.dumps(example_code)},",
            "      },",
            "    },",
            "  },",
            "};",
            "",
        ]
    )


def render_mdx_docs(
    plan: dict[str, object],
    story_path: Path | None,
    title: str,
) -> str:
    framework = str(plan["framework"])
    language = "tsx" if framework == "react" else ("vue" if framework == "vue" else "svelte")
    imports = ["import { Meta, Canvas, Controls, Source } from '@storybook/blocks';"]
    if story_path is not None:
        imports.append(story_import_statement(story_path))

    lines = imports + [""]
    if story_path is not None:
        lines.append(f"<Meta title={json.dumps(title)} of={{ComponentStories}} />")
    else:
        lines.append(f"<Meta title={json.dumps(title)} />")
    lines.extend(
        [
            "",
            f"# {humanize_name(str(plan['component']))}",
            "",
            "## Purpose",
            str(plan["purpose"]),
            "",
            "## When to use",
        ]
    )
    for item in plan.get("whenToUse", []):
        lines.append(f"- {item}")
    lines.extend(["", "## When not to use"])
    for item in plan.get("whenNotToUse", []):
        lines.append(f"- {item}")
    lines.extend(["", "## Prop decision guidance"])
    for item in plan.get("propGuidance", []):
        lines.append(f"- `{item['prop']}`: {item['guidance']}")

    if story_path is not None:
        lines.extend(["", "## Preview", "<Canvas of={ComponentStories.Default} />", "", "## Controls", "<Controls of={ComponentStories.Default} />"])

    lines.extend(["", "## Common usage patterns"])
    for pattern in plan.get("usagePatterns", []):
        lines.extend(
            [
                f"### {pattern['name']}",
                pattern["summary"],
                f"<Source code={{{json.dumps(pattern['code'])}}} language={{{json.dumps(language)}}} />",
                "",
            ]
        )

    return "\n".join(lines).rstrip() + "\n"


def render_markdown_summary(plan: dict[str, object]) -> str:
    lines = [f"# {plan['component']} docs plan", "", f"- Framework: {plan['framework']}", ""]
    lines.append(render_docs_markdown(plan))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate Storybook documentation stories or MDX docs.")
    parser.add_argument("component_path", help="Path to a React, Vue, or Svelte component file")
    parser.add_argument("--repo-root", help="Optional repo root for usage mining")
    parser.add_argument("--story-path", help="Optional existing story file for title and docs blocks")
    parser.add_argument("--style", choices=("auto", "csf", "mdx"), default="auto")
    parser.add_argument("--title", help="Optional docs title override")
    parser.add_argument("--format", choices=("text", "json", "markdown"), default="text")
    parser.add_argument("--out", help="Optional output file path")
    args = parser.parse_args()

    component_path = Path(args.component_path).resolve()
    if not component_path.exists():
        print(json.dumps({"error": f"Component not found: {component_path}"}))
        return 1

    repo_root = discover_repo_root(component_path, args.repo_root)
    plan = build_docs_plan(component_path, repo_root)
    story_path = Path(args.story_path).resolve() if args.story_path else find_story_path(component_path)
    style = args.style
    if style == "auto":
        style = "mdx" if str(plan["framework"]) == "svelte" else "csf"
    if style == "csf" and str(plan["framework"]) == "svelte":
        style = "mdx"

    title = docs_title(str(plan["component"]), story_path, args.title)
    rendered = render_mdx_docs(plan, story_path, title) if style == "mdx" else render_csf_docs(plan, component_path, story_path, title)

    payload = {
        "component": plan["component"],
        "framework": plan["framework"],
        "style": style,
        "title": title,
        "storyPath": str(story_path) if story_path else "",
        "documentation": {
            "purpose": plan["purpose"],
            "whenToUse": plan["whenToUse"],
            "whenNotToUse": plan["whenNotToUse"],
            "propGuidance": plan["propGuidance"],
            "usagePatterns": plan["usagePatterns"],
        },
        "rendered": rendered,
    }

    if args.out:
        Path(args.out).resolve().write_text(rendered, encoding="utf-8")

    if args.format == "json":
        print(json.dumps(payload, indent=2))
    elif args.format == "markdown":
        print(render_markdown_summary(plan))
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
