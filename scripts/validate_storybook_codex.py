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
SKILL_SCRIPTS = ROOT / "skills" / "storybook-codex" / "scripts"

REQUIRED_PATHS = [
    ROOT / ".codex-plugin" / "plugin.json",
    ROOT / "README.md",
    ROOT / "skills" / "storybook-codex" / "SKILL.md",
    ROOT / "skills" / "storybook-codex" / "agents" / "openai.yaml",
    ROOT / "skills" / "storybook-codex" / "references" / "react-stories.md",
    ROOT / "skills" / "storybook-codex" / "references" / "vue-stories.md",
    ROOT / "skills" / "storybook-codex" / "references" / "svelte-stories.md",
    ROOT / "skills" / "storybook-codex" / "references" / "story-design-lenses.md",
    ROOT / "skills" / "storybook-codex" / "references" / "controls-and-autodocs.md",
    ROOT / "skills" / "storybook-codex" / "references" / "documentation-stories.md",
    ROOT / "skills" / "storybook-codex" / "references" / "chromatic.md",
    ROOT / "skills" / "storybook-codex" / "references" / "visual-diff.md",
    ROOT / "skills" / "storybook-codex" / "references" / "interaction-stories.md",
    ROOT / "skills" / "storybook-codex" / "references" / "accessibility-stories.md",
    ROOT / "skills" / "storybook-codex" / "references" / "design-tokens.md",
    ROOT / "skills" / "storybook-codex" / "references" / "composition-stories.md",
    ROOT / "skills" / "storybook-codex" / "references" / "change-aware-updates.md",
    ROOT / "skills" / "storybook-codex" / "references" / "global-decorators.md",
    ROOT / "skills" / "storybook-codex" / "references" / "multi-framework-sync.md",
    ROOT / "skills" / "storybook-codex" / "references" / "component-library-patterns.md",
    ROOT / "skills" / "storybook-codex" / "references" / "storybook-9-readiness.md",
    ROOT / "skills" / "storybook-codex" / "references" / "storybook-audit.md",
    SKILL_SCRIPTS / "storybook_codex_lib.py",
    SKILL_SCRIPTS / "story_blueprint.py",
    SKILL_SCRIPTS / "story_docs.py",
    SKILL_SCRIPTS / "story_composition.py",
    SKILL_SCRIPTS / "story_diff_update.py",
    SKILL_SCRIPTS / "storybook_decorators.py",
    SKILL_SCRIPTS / "storybook_audit.py",
    SKILL_SCRIPTS / "story_sync.py",
    SKILL_SCRIPTS / "token_catalog.py",
    ROOT / "skills" / "storybook-codex" / "assets" / "storybook-codex-small.svg",
    ROOT / "skills" / "storybook-codex" / "assets" / "storybook-codex-logo.svg",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / "component.stories.tsx",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / "component.docs.stories.tsx",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / "component.docs.stories.mdx",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / "component.composition.stories.tsx",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / "component.vue.stories.ts",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / "component.svelte.stories.svelte",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / "component.interaction.stories.tsx",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / "visual-regression.spec.ts",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / ".storybook" / "preview.ts",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / ".storybook" / "preview.decorators.tsx",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / ".storybook" / "token-preview.ts",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / "chromatic.config.json",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / "libraries" / "shadcn-button.stories.tsx",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / "libraries" / "radix-dialog.stories.tsx",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / "libraries" / "headlessui-dialog.stories.tsx",
    ROOT / "skills" / "storybook-codex" / "assets" / "templates" / ".github" / "workflows" / "chromatic.yml",
    ROOT / "fixtures" / "docs-sample" / "ActionButton.tsx",
    ROOT / "fixtures" / "docs-sample" / "ActionButtonUsage.tsx",
    ROOT / "fixtures" / "docs-sample" / "ActionButton.stories.tsx",
    ROOT / "tools" / "fixtures-viewer" / "index.html",
    ROOT / "tools" / "fixtures-viewer" / "app.js",
    ROOT / "tools" / "fixtures-viewer" / "styles.css",
    CASES_PATH,
]

STORY_NAME_RE = re.compile(r"export const (\w+): Story\b")
SVELTE_STORY_NAME_RE = re.compile(r'<Story\s+name="([^"]+)"')


def fail(message: str, errors: list[str]) -> None:
    errors.append(message)


def run_json(command: list[str], errors: list[str], context: str) -> dict[str, object] | None:
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        fail(f"{context} failed: {result.stdout}{result.stderr}", errors)
        return None
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        fail(f"{context} returned invalid JSON: {exc}", errors)
        return None


def validate_required_paths(errors: list[str]) -> None:
    for path in REQUIRED_PATHS:
        if not path.exists():
            fail(f"Missing required path: {path.relative_to(ROOT)}", errors)


def validate_manifest(errors: list[str]) -> None:
    manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))

    if manifest.get("name") != "storybook-codex":
        fail("plugin.json name must be storybook-codex", errors)
    if manifest.get("skills") != "./skills/":
        fail("plugin.json skills path must be ./skills/", errors)

    keywords = set(manifest.get("keywords", []))
    for keyword in ("react", "vue", "svelte", "storybook", "chromatic"):
        if keyword not in keywords:
            fail(f"plugin.json keywords must include {keyword}", errors)

    interface = manifest.get("interface", {})
    if "$storybook-codex" not in " ".join(interface.get("defaultPrompt", [])):
        fail("plugin.json defaultPrompt entries must mention $storybook-codex", errors)
    if interface.get("composerIcon") != "./skills/storybook-codex/assets/storybook-codex-small.svg":
        fail("plugin.json composerIcon path is missing or wrong", errors)
    if interface.get("logo") != "./skills/storybook-codex/assets/storybook-codex-logo.svg":
        fail("plugin.json logo path is missing or wrong", errors)


def validate_skill_metadata(errors: list[str]) -> None:
    skill_text = (ROOT / "skills" / "storybook-codex" / "SKILL.md").read_text(encoding="utf-8")

    for phrase in (
        "name: storybook-codex",
        "Create, document, compose, update, review, sync, and audit React, Vue, and Svelte Storybook stories",
        "triggers:",
        ".stories.tsx",
        ".stories.svelte",
        ".stories.mdx",
        "parameters.docs.description",
        "story_blueprint.py",
        "story_docs.py",
        "story_composition.py",
        "story_diff_update.py",
        "storybook_decorators.py",
        "storybook_audit.py",
        "story_sync.py",
        "token_catalog.py",
        "visual-regression-codex",
    ):
        if phrase not in skill_text:
            fail(f"SKILL.md is missing required guidance: {phrase}", errors)

    openai_yaml = (ROOT / "skills" / "storybook-codex" / "agents" / "openai.yaml").read_text(encoding="utf-8")
    for phrase in (
        'display_name: "Storybook Codex"',
        "$storybook-codex",
        "React, Vue, and Svelte",
        ".stories.mdx",
        "parameters.docs.description",
        'icon_small: "./assets/storybook-codex-small.svg"',
        'icon_large: "./assets/storybook-codex-logo.svg"',
    ):
        if phrase not in openai_yaml:
            fail(f"agents/openai.yaml is missing required content: {phrase}", errors)


def validate_text_file(path: Path, required_markers: list[str], errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    for marker in required_markers:
        if marker not in text:
            fail(f"{path.relative_to(ROOT)} is missing expected content: {marker}", errors)


def validate_csf_story_text(
    label: str,
    text: str,
    required_stories: list[str],
    required_markers: list[str],
    errors: list[str],
) -> None:
    found_story_names = STORY_NAME_RE.findall(text)

    for marker in ("Meta", "StoryObj", "export default meta", "type Story = StoryObj<typeof meta>;"):
        if marker not in text:
            fail(f"{label} is missing marker: {marker}", errors)

    if "Template.bind" in text or "ComponentStory" in text or "ComponentMeta" in text:
        fail(f"{label} still uses legacy Storybook syntax", errors)
    if "@storybook/test" in text:
        fail(f"{label} still imports @storybook/test", errors)

    if required_stories and not found_story_names:
        fail(f"{label} exports no named stories", errors)

    for story_name in required_stories:
        if story_name not in found_story_names:
            fail(f"{label} is missing story export: {story_name}", errors)

    for marker in required_markers:
        if marker not in text:
            fail(f"{label} is missing expected content: {marker}", errors)


def validate_csf_story_file(path: Path, required_stories: list[str], required_markers: list[str], errors: list[str]) -> None:
    validate_csf_story_text(
        str(path.relative_to(ROOT)),
        path.read_text(encoding="utf-8"),
        required_stories,
        required_markers,
        errors,
    )


def validate_svelte_story_file(path: Path, required_stories: list[str], required_markers: list[str], errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    found_story_names = SVELTE_STORY_NAME_RE.findall(text)

    for marker in ("defineMeta", "<Story", "tags: ['autodocs']"):
        if marker not in text:
            fail(f"{path.relative_to(ROOT)} is missing marker: {marker}", errors)
    if "<Meta" in text or "<Template" in text:
        fail(f"{path.relative_to(ROOT)} still uses deprecated Svelte story blocks", errors)

    for story_name in required_stories:
        if story_name not in found_story_names:
            fail(f"{path.relative_to(ROOT)} is missing story export: {story_name}", errors)

    validate_text_file(path, required_markers, errors)


def validate_mdx_story_file(path: Path, required_markers: list[str], errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    label = str(path.relative_to(ROOT))

    for marker in ("@storybook/blocks", "<Meta"):
        if marker not in text:
            fail(f"{label} is missing marker: {marker}", errors)

    for marker in required_markers:
        if marker not in text:
            fail(f"{label} is missing expected content: {marker}", errors)


def validate_story_like_cases(cases: dict[str, object], errors: list[str]) -> None:
    for section_name in ("stories", "templates"):
        for case in cases.get(section_name, []):
            path = ROOT / case["story"]
            if not path.exists():
                fail(f"Missing artifact: {case['story']}", errors)
                continue
            format_name = case.get("format", "csf")
            if format_name == "csf":
                validate_csf_story_file(path, case.get("requiredStories", []), case.get("requiredMarkers", []), errors)
            elif format_name == "svelte-csf":
                validate_svelte_story_file(path, case.get("requiredStories", []), case.get("requiredMarkers", []), errors)
            elif format_name == "mdx":
                validate_mdx_story_file(path, case.get("requiredMarkers", []), errors)
            elif format_name == "text":
                validate_text_file(path, case.get("requiredMarkers", []), errors)
            else:
                fail(f"Unknown validation format: {format_name}", errors)


def validate_blueprints(cases: dict[str, object], errors: list[str]) -> None:
    blueprint_script = SKILL_SCRIPTS / "story_blueprint.py"
    for case in cases.get("blueprints", []):
        command = [sys.executable, str(blueprint_script), str(ROOT / case["component"])]
        if case.get("repoRoot"):
            command.extend(["--repo-root", str(ROOT / case["repoRoot"])])
        blueprint = run_json(command, errors, f"Blueprint {case['name']}")
        if blueprint is None:
            continue

        story_names = [story["name"] for story in blueprint.get("stories", [])]
        notes = "\n".join(blueprint.get("notes", []))
        controls = blueprint.get("controls", {})
        usage_props = [item["prop"] for item in blueprint.get("usageSignals", {}).get("props", [])]
        interaction_names = [item["storyName"] for item in blueprint.get("interactionStories", [])]
        a11y_names = [item["storyName"] for item in blueprint.get("accessibilityStories", [])]
        visual_stories = blueprint.get("visualDiff", {}).get("captureStories", [])
        composition_names = [item["storyName"] for item in blueprint.get("compositionStories", [])]
        composition_layouts = [item["layout"] for item in blueprint.get("compositionStories", [])]
        composition_bindings = {
            binding_name
            for item in blueprint.get("compositionStories", [])
            for binding_name in item.get("bindings", {}).keys()
        }

        for expected_story in case.get("expectedStories", []):
            if expected_story not in story_names:
                fail(f"Blueprint {case['name']} is missing story recommendation: {expected_story}", errors)
        for expected_note in case.get("expectedNotes", []):
            if expected_note not in notes:
                fail(f"Blueprint {case['name']} is missing note content: {expected_note}", errors)
        for hidden_prop in case.get("expectedHiddenProps", []):
            if controls.get(hidden_prop, {}).get("table", {}).get("disable") is not True:
                fail(f"Blueprint {case['name']} should hide prop: {hidden_prop}", errors)
        for usage_prop in case.get("expectedUsageProps", []):
            if usage_prop not in usage_props:
                fail(f"Blueprint {case['name']} is missing usage signal: {usage_prop}", errors)
        for story_name in case.get("expectedInteractionStories", []):
            if story_name not in interaction_names:
                fail(f"Blueprint {case['name']} is missing interaction story: {story_name}", errors)
        for story_name in case.get("expectedA11yStories", []):
            if story_name not in a11y_names:
                fail(f"Blueprint {case['name']} is missing accessibility story: {story_name}", errors)
        for story_name in case.get("expectedVisualStories", []):
            if story_name not in visual_stories:
                fail(f"Blueprint {case['name']} is missing visual capture story: {story_name}", errors)
        for story_name in case.get("expectedCompositionStories", []):
            if story_name not in composition_names:
                fail(f"Blueprint {case['name']} is missing composition story: {story_name}", errors)
        for layout in case.get("expectedCompositionLayouts", []):
            if layout not in composition_layouts:
                fail(f"Blueprint {case['name']} is missing composition layout: {layout}", errors)
        for binding_name in case.get("expectedCompositionBindings", []):
            if binding_name not in composition_bindings:
                fail(f"Blueprint {case['name']} is missing composition binding: {binding_name}", errors)


def validate_reviews(cases: dict[str, object], errors: list[str]) -> None:
    blueprint_script = SKILL_SCRIPTS / "story_blueprint.py"
    for case in cases.get("reviews", []):
        review = run_json(
            [
                sys.executable,
                str(blueprint_script),
                str(ROOT / case["component"]),
                "--review-story",
                str(ROOT / case["story"]),
            ],
            errors,
            f"Review {case['name']}",
        )
        if review is None:
            continue

        if review.get("score", 0) < case.get("minimumScore", 0):
            fail(f"Review {case['name']} scored below the minimum threshold", errors)
        issue_codes = {issue["code"] for issue in review.get("issues", [])}
        for expected_code in case.get("expectedIssueCodes", []):
            if expected_code not in issue_codes:
                fail(f"Review {case['name']} is missing issue code: {expected_code}", errors)


def validate_audits(cases: dict[str, object], errors: list[str]) -> None:
    audit_script = SKILL_SCRIPTS / "storybook_audit.py"
    for case in cases.get("audits", []):
        audit = run_json(
            [sys.executable, str(audit_script), str(ROOT / case["path"])],
            errors,
            f"Audit {case['name']}",
        )
        if audit is None:
            continue

        if audit.get("averageScore", 0) < case.get("minimumAverageScore", 0):
            fail(f"Audit {case['name']} average score is below the minimum threshold", errors)
        missing = set(audit.get("missingComponents", []))
        for expected in case.get("expectedMissingComponents", []):
            if expected not in missing:
                fail(f"Audit {case['name']} is missing uncovered component: {expected}", errors)
        component_names = {component["component"] for component in audit.get("components", [])}
        for expected in case.get("expectedComponents", []):
            if expected not in component_names:
                fail(f"Audit {case['name']} is missing component report: {expected}", errors)


def validate_token_catalogs(cases: dict[str, object], errors: list[str]) -> None:
    token_script = SKILL_SCRIPTS / "token_catalog.py"
    for case in cases.get("tokenCatalogs", []):
        catalog = run_json(
            [sys.executable, str(token_script), str(ROOT / case["path"])],
            errors,
            f"Token catalog {case['name']}",
        )
        if catalog is None:
            continue

        token_names = {token["name"] for token in catalog.get("tokens", [])}
        global_names = {item["name"] for item in catalog.get("globals", [])}
        preview_snippet = str(catalog.get("previewSnippet", ""))

        for expected in case.get("expectedTokenNames", []):
            if expected not in token_names:
                fail(f"Token catalog {case['name']} is missing token: {expected}", errors)
        for expected in case.get("expectedGlobals", []):
            if expected not in global_names:
                fail(f"Token catalog {case['name']} is missing global: {expected}", errors)
        for expected in case.get("expectedPreviewMarkers", []):
            if expected not in preview_snippet:
                fail(f"Token catalog {case['name']} preview snippet is missing: {expected}", errors)


def validate_syncs(cases: dict[str, object], errors: list[str]) -> None:
    sync_script = SKILL_SCRIPTS / "story_sync.py"
    for case in cases.get("syncs", []):
        result = subprocess.run(
            [
                sys.executable,
                str(sync_script),
                str(ROOT / case["source"]),
                "--target",
                case["target"],
                "--component-name",
                case["componentName"],
                "--component-import",
                case["componentImport"],
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            fail(f"Sync {case['name']} failed: {result.stdout}{result.stderr}", errors)
            continue
        for marker in case.get("requiredMarkers", []):
            if marker not in result.stdout:
                fail(f"Sync {case['name']} is missing expected content: {marker}", errors)


def validate_compositions(cases: dict[str, object], errors: list[str]) -> None:
    composition_script = SKILL_SCRIPTS / "story_composition.py"
    for case in cases.get("compositions", []):
        command = [sys.executable, str(composition_script), str(ROOT / case["component"])]
        if case.get("repoRoot"):
            command.extend(["--repo-root", str(ROOT / case["repoRoot"])])
        payload = run_json(command, errors, f"Composition {case['name']}")
        if payload is None:
            continue

        suggestions = list(payload.get("compositionStories", []))
        story_names = [item["storyName"] for item in suggestions]
        layouts = [item["layout"] for item in suggestions]
        parent_files = [item["parentFile"] for item in suggestions]
        binding_names = {
            binding_name
            for item in suggestions
            for binding_name in item.get("bindings", {}).keys()
        }

        for expected in case.get("expectedStoryNames", []):
            if expected not in story_names:
                fail(f"Composition {case['name']} is missing story: {expected}", errors)
        for expected in case.get("expectedLayouts", []):
            if expected not in layouts:
                fail(f"Composition {case['name']} is missing layout: {expected}", errors)
        for expected in case.get("expectedParentFiles", []):
            if expected not in parent_files:
                fail(f"Composition {case['name']} is missing parent file: {expected}", errors)
        for expected in case.get("expectedBindingProps", []):
            if expected not in binding_names:
                fail(f"Composition {case['name']} is missing binding prop: {expected}", errors)


def validate_decorators(cases: dict[str, object], errors: list[str]) -> None:
    decorator_script = SKILL_SCRIPTS / "storybook_decorators.py"
    for case in cases.get("decorators", []):
        payload = run_json(
            [
                sys.executable,
                str(decorator_script),
                str(ROOT / case["path"]),
                "--framework",
                case["framework"],
            ],
            errors,
            f"Decorators {case['name']}",
        )
        if payload is None:
            continue

        preview_snippet = str(payload.get("previewSnippet", ""))
        providers = [item["name"] for item in payload.get("providers", [])]
        plugins = list(payload.get("plugins", []))

        for expected in case.get("expectedProviders", []):
            if expected not in providers:
                fail(f"Decorators {case['name']} is missing provider: {expected}", errors)
        for expected in case.get("expectedPlugins", []):
            if expected not in plugins:
                fail(f"Decorators {case['name']} is missing plugin: {expected}", errors)
        for expected in case.get("expectedPreviewMarkers", []):
            if expected not in preview_snippet:
                fail(f"Decorators {case['name']} preview is missing: {expected}", errors)


def validate_diff_updates(cases: dict[str, object], errors: list[str]) -> None:
    diff_script = SKILL_SCRIPTS / "story_diff_update.py"
    for case in cases.get("diffUpdates", []):
        story_path = ROOT / case["story"]
        expected_path = ROOT / case["expectedStory"]
        original_story = story_path.read_text(encoding="utf-8")

        try:
            payload = run_json(
                [
                    sys.executable,
                    str(diff_script),
                    str(ROOT / case["path"]),
                    "--diff-file",
                    str(ROOT / case["diffFile"]),
                    "--write",
                ],
                errors,
                f"Diff update {case['name']}",
            )
            if payload is None:
                continue

            if not payload.get("changedComponents"):
                fail(f"Diff update {case['name']} produced no changed components", errors)
                continue

            item = payload["changedComponents"][0]
            for expected in case.get("expectedAddedStories", []):
                if expected not in item.get("addedStoryExports", []):
                    fail(f"Diff update {case['name']} is missing added story export: {expected}", errors)
            notes = "\n".join(item.get("notes", []))
            for expected in case.get("expectedRemovedWarnings", []):
                if expected not in notes:
                    fail(f"Diff update {case['name']} is missing removed warning: {expected}", errors)
            for expected in case.get("expectedRenameWarnings", []):
                if expected not in notes:
                    fail(f"Diff update {case['name']} is missing rename warning: {expected}", errors)

            updated_story = story_path.read_text(encoding="utf-8")
            expected_story = expected_path.read_text(encoding="utf-8")
            if updated_story != expected_story:
                fail(f"Diff update {case['name']} story output does not match expected fixture", errors)
        finally:
            story_path.write_text(original_story, encoding="utf-8")


def validate_docs(cases: dict[str, object], errors: list[str]) -> None:
    docs_script = SKILL_SCRIPTS / "story_docs.py"
    for case in cases.get("docs", []):
        component_path = ROOT / case["component"]
        if not component_path.exists():
            fail(f"Missing docs component fixture: {case['component']}", errors)
            continue

        command = [
            sys.executable,
            str(docs_script),
            str(component_path),
            "--format",
            "json",
            "--style",
            case.get("style", "auto"),
        ]
        if case.get("repoRoot"):
            command.extend(["--repo-root", str(ROOT / case["repoRoot"])])
        if case.get("storyPath"):
            command.extend(["--story-path", str(ROOT / case["storyPath"])])

        payload = run_json(command, errors, f"Docs {case['name']}")
        if payload is None:
            continue

        expected_style = case.get("style")
        if expected_style and payload.get("style") != expected_style:
            fail(
                f"Docs {case['name']} returned style {payload.get('style')} instead of {expected_style}",
                errors,
            )

        expected_title = case.get("expectedTitle")
        if expected_title and payload.get("title") != expected_title:
            fail(
                f"Docs {case['name']} returned title {payload.get('title')} instead of {expected_title}",
                errors,
            )

        documentation = payload.get("documentation", {})
        pattern_names = [pattern.get("name") for pattern in documentation.get("usagePatterns", [])]
        for pattern_name in case.get("expectedPatternNames", []):
            if pattern_name not in pattern_names:
                fail(f"Docs {case['name']} is missing usage pattern: {pattern_name}", errors)

        rendered = str(payload.get("rendered", ""))
        if payload.get("style") == "csf":
            validate_csf_story_text(
                f"docs output {case['name']}",
                rendered,
                case.get("requiredStories", []),
                case.get("requiredMarkers", []),
                errors,
            )
        elif payload.get("style") == "mdx":
            for marker in ("@storybook/blocks", "<Meta"):
                if marker not in rendered:
                    fail(f"docs output {case['name']} is missing marker: {marker}", errors)
            for marker in case.get("requiredMarkers", []):
                if marker not in rendered:
                    fail(f"docs output {case['name']} is missing expected content: {marker}", errors)
        else:
            fail(f"Docs {case['name']} returned unknown style: {payload.get('style')}", errors)

        markdown_markers = case.get("expectedMarkdownMarkers", [])
        if markdown_markers:
            md_command = [
                sys.executable,
                str(docs_script),
                str(component_path),
                "--format",
                "markdown",
                "--style",
                case.get("style", "auto"),
            ]
            if case.get("repoRoot"):
                md_command.extend(["--repo-root", str(ROOT / case["repoRoot"])])
            if case.get("storyPath"):
                md_command.extend(["--story-path", str(ROOT / case["storyPath"])])

            md_result = subprocess.run(md_command, capture_output=True, text=True, check=False)
            if md_result.returncode != 0:
                fail(f"Docs markdown run failed for {case['name']}: {md_result.stdout}{md_result.stderr}", errors)
                continue

            for marker in markdown_markers:
                if marker not in md_result.stdout:
                    fail(f"Docs {case['name']} markdown is missing marker: {marker}", errors)


def validate_viewer(errors: list[str]) -> None:
    viewer_js = (ROOT / "tools" / "fixtures-viewer" / "app.js").read_text(encoding="utf-8")
    viewer_html = (ROOT / "tools" / "fixtures-viewer" / "index.html").read_text(encoding="utf-8")
    for marker in ("fixtures/cases.json", "Load local JSON", "renderContract"):
        if marker not in viewer_js and marker not in viewer_html:
            fail(f"Fixtures viewer is missing expected content: {marker}", errors)


def validate_watch_mode(errors: list[str]) -> None:
    blueprint_script = SKILL_SCRIPTS / "story_blueprint.py"
    result = subprocess.run(
        [
            sys.executable,
            str(blueprint_script),
            str(ROOT / "fixtures" / "basic-button" / "Button.tsx"),
            "--watch",
            "--max-runs",
            "1",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        fail(f"Watch mode failed: {result.stdout}{result.stderr}", errors)
        return
    if '"component": "Button"' not in result.stdout:
        fail("Watch mode did not emit the expected initial blueprint payload", errors)


def main() -> int:
    errors: list[str] = []
    validate_required_paths(errors)
    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1

    validate_manifest(errors)
    validate_skill_metadata(errors)

    cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
    validate_story_like_cases(cases, errors)
    validate_blueprints(cases, errors)
    validate_reviews(cases, errors)
    validate_audits(cases, errors)
    validate_token_catalogs(cases, errors)
    validate_syncs(cases, errors)
    validate_compositions(cases, errors)
    validate_decorators(cases, errors)
    validate_diff_updates(cases, errors)
    validate_docs(cases, errors)
    validate_viewer(errors)
    validate_watch_mode(errors)

    if errors:
        for error in errors:
            print(f"[FAIL] {error}")
        return 1

    print("[OK] Storybook Codex repository checks passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
