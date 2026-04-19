#!/usr/bin/env python3
"""Generate parent-context Storybook composition suggestions."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from storybook_codex_lib import build_blueprint, discover_repo_root, match_story_for_component


def resolve_payload(component_path: Path, repo_root: Path | None) -> dict[str, object]:
    blueprint = build_blueprint(component_path, repo_root)
    story_path = match_story_for_component(component_path)
    suggestions = list(blueprint.get("compositionStories", []))
    notes = [
        "Use the highest-confidence parent context as a real-world wrapper story before adding synthetic layout shells.",
        "Keep literal usage props in args and move expression-only bindings into render decorators or fixture data.",
    ]
    if not suggestions:
        notes.insert(0, "No parent usage sites were found, so compose one deliberate wrapper story manually.")

    return {
        "component": blueprint["component"],
        "componentPath": blueprint["componentPath"],
        "framework": blueprint["framework"],
        "repoRoot": blueprint["repoRoot"],
        "storyPath": str(story_path) if story_path else "",
        "compositionStories": suggestions,
        "notes": notes,
    }


def render_markdown(payload: dict[str, object]) -> str:
    lines = [
        f"# {payload['component']} composition",
        "",
        f"- Framework: {payload['framework']}",
        f"- Repo root: {payload['repoRoot']}",
    ]
    if payload.get("storyPath"):
        lines.append(f"- Story file: {payload['storyPath']}")

    suggestions = list(payload.get("compositionStories", []))
    if suggestions:
        lines.append("")
        lines.append("## Suggested context stories")
        for item in suggestions:
            lines.append(
                f"- {item['storyName']}: {item['layout']} in {item['parentFile']} "
                f"(confidence {item['confidence']})"
            )
            if item.get("args"):
                lines.append(f"  args: {json.dumps(item['args'], sort_keys=True)}")
            if item.get("bindings"):
                lines.append(f"  bindings: {json.dumps(item['bindings'], sort_keys=True)}")
            if item.get("siblingComponents"):
                lines.append(f"  siblings: {', '.join(item['siblingComponents'])}")
            if item.get("wrappers"):
                lines.append(f"  wrappers: {', '.join(item['wrappers'])}")

    notes = list(payload.get("notes", []))
    if notes:
        lines.append("")
        lines.append("## Notes")
        for note in notes:
            lines.append(f"- {note}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Suggest parent-context stories for a component.")
    parser.add_argument("component_path", help="Path to the component file")
    parser.add_argument("--repo-root", help="Optional repo root for context discovery")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    args = parser.parse_args()

    component_path = Path(args.component_path).resolve()
    if not component_path.exists():
        print(json.dumps({"error": f"Component not found: {component_path}"}))
        return 1

    repo_root = discover_repo_root(component_path, args.repo_root)
    payload = resolve_payload(component_path, repo_root)

    if args.format == "markdown":
        print(render_markdown(payload))
    else:
        print(json.dumps(payload, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
