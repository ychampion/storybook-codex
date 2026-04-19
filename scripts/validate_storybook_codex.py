#!/usr/bin/env python3
"""Zero-dependency validator for the Storybook Codex repo."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "fixtures" / "cases.json"

REQUIRED_PATHS = [
    ROOT / ".codex-plugin" / "plugin.json",
    ROOT / "README.md",
    ROOT / "skills" / "storybook-codex" / "SKILL.md",
    ROOT / "skills" / "storybook-codex" / "agents" / "openai.yaml",
    ROOT / "skills" / "storybook-codex" / "references" / "react-stories.md",
    ROOT / "skills" / "storybook-codex" / "references" / "story-design-lenses.md",
    ROOT / "skills" / "storybook-codex" / "references" / "controls-and-autodocs.md",
    ROOT / "skills" / "storybook-codex" / "references" / "chromatic.md",
    ROOT / "skills" / "storybook-codex" / "scripts" / "story_blueprint.py",
    ROOT / "skills" / "storybook-codex" / "assets" / "storybook-codex-small.svg",
    ROOT / "skills" / "storybook-codex" / "assets" / "storybook-codex-logo.svg",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / "component.stories.tsx",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / ".storybook" / "preview.ts",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / "chromatic.config.json",
    ROOT
    / "skills"
    / "storybook-codex"
    / "assets"
    / "templates"
    / ".github"
    / "workflows"
    / "chromatic.yml",
    CASES_PATH,
]

STORY_NAME_RE = re.compile(r"export const (\w+): Story\b")


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def validate_required_paths(errors: list[str]) -> None:
    for path in REQUIRED_PATHS:
        if not path.exists():
            fail(f"Missing required path: {path.relative_to(ROOT)}", errors)


def validate_manifest(errors: list[str]) -> None:
    manifest_path = ROOT / ".codex-plugin" / "plugin.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    if manifest.get("name") != "storybook-codex":
        fail("plugin.json name must be storybook-codex", errors)

    if manifest.get("skills") != "./skills/":
        fail("plugin.json skills path must be ./skills/", errors)

    interface = manifest.get("interface", {})
    if "$storybook-codex" not in " ".join(interface.get("defaultPrompt", [])):
        fail("plugin.json defaultPrompt entries must mention $storybook-codex", errors)
    if interface.get("composerIcon") != "./skills/storybook-codex/assets/storybook-codex-small.svg":
        fail("plugin.json composerIcon path is missing or wrong", errors)
    if interface.get("logo") != "./skills/storybook-codex/assets/storybook-codex-logo.svg":
        fail("plugin.json logo path is missing or wrong", errors)


def validate_skill_metadata(errors: list[str]) -> None:
    skill_path = ROOT / "skills" / "storybook-codex" / "SKILL.md"
    skill_text = skill_path.read_text(encoding="utf-8")

    if "name: storybook-codex" not in skill_text:
        fail("SKILL.md frontmatter must include name: storybook-codex", errors)

    if "Create or update React Storybook stories" not in skill_text:
        fail("SKILL.md description is missing the main trigger intent", errors)

    openai_yaml = (
        ROOT / "skills" / "storybook-codex" / "agents" / "openai.yaml"
    ).read_text(encoding="utf-8")
    if "display_name: \"Storybook Codex\"" not in openai_yaml:
        fail("agents/openai.yaml display_name is missing or wrong", errors)
    if "$storybook-codex" not in openai_yaml:
        fail("agents/openai.yaml default prompt must mention $storybook-codex", errors)
    if "icon_small: \"./assets/storybook-codex-small.svg\"" not in openai_yaml:
        fail("agents/openai.yaml icon_small is missing or wrong", errors)
    if "icon_large: \"./assets/storybook-codex-logo.svg\"" not in openai_yaml:
        fail("agents/openai.yaml icon_large is missing or wrong", errors)


def validate_story_file(
    story_path: Path,
    required_stories: list[str],
    required_markers: list[str],
    errors: list[str],
) -> None:
    text = story_path.read_text(encoding="utf-8")
    found_story_names = STORY_NAME_RE.findall(text)

    for marker in (
        "Meta",
        "StoryObj",
        "export default meta",
        "type Story = StoryObj<typeof meta>;",
    ):
        if marker not in text:
            fail(f"{story_path.relative_to(ROOT)} is missing marker: {marker}", errors)

    if "Template.bind" in text:
        fail(f"{story_path.relative_to(ROOT)} still contains Template.bind", errors)

    if "ComponentStory" in text or "ComponentMeta" in text:
        fail(
            f"{story_path.relative_to(ROOT)} still uses old Storybook utility types",
            errors,
        )

    if not found_story_names:
        fail(f"{story_path.relative_to(ROOT)} exports no named stories", errors)

    for story_name in required_stories:
        if story_name not in found_story_names:
            fail(
                f"{story_path.relative_to(ROOT)} is missing story export: {story_name}",
                errors,
            )

    for marker in required_markers:
        if marker not in text:
            fail(
                f"{story_path.relative_to(ROOT)} is missing expected content: {marker}",
                errors,
            )


def validate_cases(errors: list[str]) -> None:
    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))

    for section_name in ("stories", "templates"):
        for case in cases.get(section_name, []):
            story_path = ROOT / case["story"]
            if not story_path.exists():
                fail(f"Missing story fixture: {case['story']}", errors)
                continue
            validate_story_file(
                story_path=story_path,
                required_stories=case.get("requiredStories", []),
                required_markers=case.get("requiredMarkers", []),
                errors=errors,
            )

    blueprint_script = ROOT / "skills" / "storybook-codex" / "scripts" / "story_blueprint.py"
    for case in cases.get("blueprints", []):
        component_path = ROOT / case["component"]
        result = subprocess.run(
            [sys.executable, str(blueprint_script), str(component_path)],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            fail(f"Blueprint script failed for {case['name']}: {result.stdout}{result.stderr}", errors)
            continue

        try:
            blueprint = json.loads(result.stdout)
        except json.JSONDecodeError as exc:
            fail(f"Blueprint output for {case['name']} is not valid JSON: {exc}", errors)
            continue

        story_names = [story["name"] for story in blueprint.get("stories", [])]
        for expected_story in case.get("expectedStories", []):
            if expected_story not in story_names:
                fail(f"Blueprint {case['name']} is missing story recommendation: {expected_story}", errors)

        notes = "\n".join(blueprint.get("notes", []))
        for expected_note in case.get("expectedNotes", []):
            if expected_note not in notes:
                fail(f"Blueprint {case['name']} is missing note content: {expected_note}", errors)

        controls = blueprint.get("controls", {})
        for hidden_prop in case.get("expectedHiddenProps", []):
            control = controls.get(hidden_prop, {})
            if control.get("table", {}).get("disable") is not True:
                fail(f"Blueprint {case['name']} should hide prop: {hidden_prop}", errors)


def main() -> int:
    errors: list[str] = []

    validate_required_paths(errors)

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1

    validate_manifest(errors)
    validate_skill_metadata(errors)
    validate_cases(errors)

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1

    print("[OK] Storybook Codex repository checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
