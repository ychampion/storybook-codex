#!/usr/bin/env python3
"""Zero-dependency regression tests for demo/build.py parsers.

Run:
    python demo/test_build.py
"""

from __future__ import annotations

import sys
from pathlib import Path

DEMO_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(DEMO_DIR))

from build import extract_csf_stories, extract_svelte_stories  # noqa: E402


def test_empty_body_story_does_not_bleed() -> None:
    """`export const Default: Story = {};` must not swallow the next story."""
    sample = """
const meta = {};
type Story = StoryObj<typeof meta>;

export const Default: Story = {};

export const Brand: Story = {
  args: {
    tone: 'brand',
  },
};
"""
    _, stories = extract_csf_stories(sample)
    names = [story["name"] for story in stories]
    assert names == ["Default", "Brand"], names
    assert stories[0]["args"] == {}, stories[0]
    assert stories[1]["args"] == {"tone": "brand"}, stories[1]


def test_nested_args_key_is_ignored() -> None:
    """A nested `parameters.docs.story.args` must not shadow the top-level
    `args` when reading a story."""
    sample = """
const meta = {};
type Story = StoryObj<typeof meta>;

export const Brand: Story = {
  parameters: {
    docs: {
      story: {
        args: {
          tone: 'danger',
        },
      },
    },
  },
  args: {
    tone: 'brand',
  },
};
"""
    _, stories = extract_csf_stories(sample)
    assert stories[0]["args"] == {"tone": "brand"}, stories[0]


def test_meta_args_parsed() -> None:
    sample = """
const meta = {
  title: 'Fixtures/Button',
  args: {
    children: 'Save changes',
    size: 'md',
    onClick: fn(),
  },
} satisfies Meta<typeof Button>;

type Story = StoryObj<typeof meta>;
export const Default: Story = {};
"""
    meta_args, stories = extract_csf_stories(sample)
    assert meta_args["children"] == "Save changes"
    assert meta_args["size"] == "md"
    assert isinstance(meta_args["onClick"], dict) and meta_args["onClick"]["__event__"] is True
    assert [story["name"] for story in stories] == ["Default"]


def test_svelte_story_args_parsed() -> None:
    # Multi-line args matches the style used in the repo's Svelte fixtures;
    # parse_key_value_body is deliberately line-oriented (see build.py docstring).
    sample = """
<script>
  const { Story } = defineMeta({
    args: {
      label: 'Ready',
      tone: 'neutral',
    },
  });
</script>

<Story name="Default" />
<Story name="Brand" args={{ tone: 'brand' }} />
"""
    meta_args, stories = extract_svelte_stories(sample)
    assert meta_args.get("label") == "Ready", meta_args
    assert meta_args.get("tone") == "neutral", meta_args
    assert [story["name"] for story in stories] == ["Default", "Brand"]
    assert stories[1]["args"] == {"tone": "brand"}


TESTS = [
    test_empty_body_story_does_not_bleed,
    test_nested_args_key_is_ignored,
    test_meta_args_parsed,
    test_svelte_story_args_parsed,
]


def main() -> int:
    failures = 0
    for fn in TESTS:
        try:
            fn()
            print(f"[OK] {fn.__name__}")
        except AssertionError as err:
            failures += 1
            print(f"[FAIL] {fn.__name__}: {err}")
    if failures:
        print(f"\n{failures} test(s) failed.")
        return 1
    print(f"\n{len(TESTS)} tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
