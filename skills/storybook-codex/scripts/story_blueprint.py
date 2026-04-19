#!/usr/bin/env python3
"""Generate deterministic Storybook blueprints and story reviews."""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from storybook_codex_lib import build_blueprint, render_markdown, review_story


def render_payload(payload: dict[str, object], output_format: str) -> str:
    if output_format == "markdown":
        return render_markdown(payload)
    return json.dumps(payload, indent=2)


def resolve_payload(
    component_path: Path,
    repo_root: Path | None,
    review_story_path: Path | None,
) -> dict[str, object]:
    if review_story_path is not None:
        return review_story(component_path, review_story_path, repo_root)

    blueprint = build_blueprint(component_path, repo_root)
    if review_story_path is not None:
        blueprint["review"] = review_story(component_path, review_story_path, repo_root)
    return blueprint


def fingerprint(paths: list[Path]) -> tuple[int, ...]:
    return tuple(path.stat().st_mtime_ns for path in paths if path.exists())


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate a Storybook story blueprint.")
    parser.add_argument("component_path", help="Path to a React, Vue, or Svelte component file")
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    parser.add_argument("--repo-root", help="Optional repo root for usage mining")
    parser.add_argument("--review-story", help="Compare an existing story file against the component blueprint")
    parser.add_argument("--watch", action="store_true", help="Re-run when the component or review story changes")
    parser.add_argument(
        "--poll-interval",
        type=float,
        default=0.75,
        help="Polling interval in seconds for watch mode",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=0,
        help="Stop after N renders in watch mode; 0 means keep watching",
    )
    args = parser.parse_args()

    component_path = Path(args.component_path).resolve()
    repo_root = Path(args.repo_root).resolve() if args.repo_root else None
    review_story_path = Path(args.review_story).resolve() if args.review_story else None

    if not component_path.exists():
        print(json.dumps({"error": f"Component not found: {component_path}"}))
        return 1
    if review_story_path is not None and not review_story_path.exists():
        print(json.dumps({"error": f"Story not found: {review_story_path}"}))
        return 1

    watched_paths = [component_path]
    if review_story_path is not None:
        watched_paths.append(review_story_path)

    renders = 0
    last_stamp: tuple[int, ...] | None = None

    while True:
        current_stamp = fingerprint(watched_paths)
        should_render = not args.watch or last_stamp is None or current_stamp != last_stamp
        if should_render:
            payload = resolve_payload(component_path, repo_root, review_story_path)
            print(render_payload(payload, args.format))
            renders += 1
            last_stamp = current_stamp
            if not args.watch:
                return 0
            if args.max_runs and renders >= args.max_runs:
                return 0
            print("\n--- watching for changes ---", file=sys.stderr)

        time.sleep(max(args.poll_interval, 0.1))


if __name__ == "__main__":
    sys.exit(main())
