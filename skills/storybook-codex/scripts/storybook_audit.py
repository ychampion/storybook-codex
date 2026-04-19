#!/usr/bin/env python3
"""Audit Storybook coverage and health for a repository."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from storybook_codex_lib import review_story


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
COMPONENT_SUFFIXES = (".tsx", ".ts", ".jsx", ".js", ".vue", ".svelte")
STORY_SUFFIXES = (
    ".stories.tsx",
    ".stories.ts",
    ".stories.jsx",
    ".stories.js",
    ".stories.svelte",
)


def should_skip(path: Path) -> bool:
    return any(part in IGNORED_DIRS for part in path.parts)


def find_story_files(root: Path) -> list[Path]:
    stories: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or should_skip(path.relative_to(root)):
            continue
        if any(path.name.endswith(suffix) for suffix in STORY_SUFFIXES) and ".expected." not in path.name:
            stories.append(path)
    return sorted(stories)


def find_component_files(root: Path) -> list[Path]:
    components: list[Path] = []
    for path in root.rglob("*"):
        if not path.is_file() or should_skip(path.relative_to(root)):
            continue
        if path.name.endswith(STORY_SUFFIXES) or ".expected." in path.name or ".before." in path.name:
            continue
        if path.suffix.lower() in COMPONENT_SUFFIXES:
            components.append(path)
    return sorted(components)


def match_component_for_story(story_path: Path) -> Path | None:
    base_name = story_path.name.split(".stories", 1)[0]
    for suffix in COMPONENT_SUFFIXES:
        candidate = story_path.with_name(f"{base_name}{suffix}")
        if candidate.exists():
            return candidate
    return None


def audit_repository(root: Path) -> dict[str, object]:
    story_files = find_story_files(root)
    component_files = find_component_files(root)
    story_map = {story: match_component_for_story(story) for story in story_files}
    covered_components = {component.resolve() for component in story_map.values() if component is not None}
    missing_components = [
        component.relative_to(root).as_posix()
        for component in component_files
        if component.resolve() not in covered_components
    ]

    reports: list[dict[str, object]] = []
    for story_path, component_path in story_map.items():
        if component_path is None:
            reports.append(
                {
                    "component": story_path.stem,
                    "componentPath": "",
                    "storyPath": story_path.relative_to(root).as_posix(),
                    "score": 0,
                    "lensCoverage": {},
                    "issues": [
                        {
                            "severity": "high",
                            "code": "unmatched-component",
                            "message": "Story file has no sibling component match.",
                        }
                    ],
                }
            )
            continue
        report = review_story(component_path, story_path, root)
        report["componentPath"] = component_path.relative_to(root).as_posix()
        report["storyPath"] = story_path.relative_to(root).as_posix()
        report.pop("blueprint", None)
        reports.append(report)

    average_score = round(
        sum(report["score"] for report in reports) / len(reports),
        2,
    ) if reports else 0.0

    return {
        "root": str(root),
        "componentCount": len(component_files),
        "storyCount": len(story_files),
        "averageScore": average_score,
        "missingComponents": missing_components,
        "components": sorted(reports, key=lambda report: (report["score"], report["component"])),
    }


def render_markdown(report: dict[str, object]) -> str:
    lines = [
        "# Storybook audit",
        "",
        f"- Components scanned: {report['componentCount']}",
        f"- Story files scanned: {report['storyCount']}",
        f"- Average Story Health Score: {report['averageScore']}",
    ]

    missing = report.get("missingComponents", [])
    if missing:
        lines.append(f"- Missing stories: {len(missing)}")

    lines.append("")
    lines.append("## Components")
    for component in report.get("components", []):
        lines.append(
            f"- {component['component']}: {component['score']} "
            f"({component['storyPath']})"
        )
        for issue in component.get("issues", [])[:3]:
            lines.append(f"  - {issue['severity']}: {issue['message']}")

    if missing:
        lines.append("")
        lines.append("## Missing stories")
        for path in missing:
            lines.append(f"- {path}")

    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit Storybook health for a repo.")
    parser.add_argument("path", help="Repository root or package directory to audit")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument(
        "--fail-under",
        type=float,
        default=0.0,
        help="Exit non-zero when the average score falls below this threshold",
    )
    args = parser.parse_args()

    root = Path(args.path).resolve()
    if not root.exists():
        print(json.dumps({"error": f"Audit path not found: {root}"}))
        return 1

    report = audit_repository(root)

    if args.format == "markdown":
        print(render_markdown(report))
    else:
        print(json.dumps(report, indent=2))

    if report["averageScore"] < args.fail_under:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
