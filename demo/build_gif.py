#!/usr/bin/env python3
"""Stitch frame-*.png captures into an animated demo GIF.

Usage:
    python demo/build_gif.py <frames_dir> <output_path> [--width 960] [--frame-ms 1400]

The caller is expected to have already captured 1280x720 PNG screenshots
named ``frame-*.png`` using Playwright against the local demo server.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    from PIL import Image
except ImportError as err:  # pragma: no cover - actionable message
    raise SystemExit("Pillow is required: pip install Pillow") from err


def load_frames(frames_dir: Path, target_width: int) -> list[Image.Image]:
    frames: list[Image.Image] = []
    for path in sorted(frames_dir.glob("frame-*.png")):
        image = Image.open(path).convert("RGB")
        if image.width != target_width:
            ratio = target_width / image.width
            new_size = (target_width, round(image.height * ratio))
            image = image.resize(new_size, Image.LANCZOS)
        frames.append(image)
    if not frames:
        raise SystemExit(f"No frame-*.png files under {frames_dir}")
    return frames


def save_gif(frames: list[Image.Image], output_path: Path, frame_ms: int) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Palette-quantized frames keep the GIF compact while preserving accent colours.
    palette_frames = [frame.convert("P", palette=Image.ADAPTIVE, colors=192) for frame in frames]
    palette_frames[0].save(
        output_path,
        save_all=True,
        append_images=palette_frames[1:],
        duration=frame_ms,
        loop=0,
        optimize=True,
        disposal=2,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Build an animated GIF from demo frames.")
    parser.add_argument("frames_dir", type=Path, help="Directory containing frame-*.png files")
    parser.add_argument("output_path", type=Path, help="Where to write the .gif")
    parser.add_argument("--width", type=int, default=960, help="Target width in pixels (default 960)")
    parser.add_argument("--frame-ms", type=int, default=1400, help="Frame duration in ms (default 1400)")
    args = parser.parse_args()

    frames = load_frames(args.frames_dir, args.width)
    save_gif(frames, args.output_path, args.frame_ms)
    size_kb = args.output_path.stat().st_size / 1024
    print(f"Wrote {args.output_path} ({len(frames)} frames, {size_kb:.0f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
