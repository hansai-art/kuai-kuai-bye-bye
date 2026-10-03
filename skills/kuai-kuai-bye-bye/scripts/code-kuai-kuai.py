#!/usr/bin/env python3
"""Render a tiny Kuai Kuai talisman from code, not from an image asset.

The drawing is deliberately simple: a colour matrix becomes an SVG made of
rectangles.  It is useful for terminal demos, README examples, and projects
that want a code-native talisman without adding a runtime image dependency.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


PALETTE = {
    "G": "#0c8b55",  # package green
    "g": "#075a39",  # wrapper shadow
    "R": "#e3133b",  # red mark
    "C": "#fff7df",  # cream label
    "Y": "#f2c84b",  # corn / seal
    "W": "#ffffff",
}

# One character is one square.  The image is intentionally a recipe in code:
# changing a character changes the rendered pixel, and no source image is read.
PIXELS = (
    ".....gggggggggggg.....",
    "....gGGGGGGGGGGGGg....",
    "...gGGGGGGGGGGGGGGg...",
    "...gGGGGGGGGGGGGGGg...",
    "..gGGGGGGGGGGGGGGGGg..",
    "..gGGGGGGGGGGGGGGGGg..",
    ".gGGGGGGGGGGGGGGGGGGg.",
    ".gGGGGGGGGGGGGGGGGGGg.",
    ".gGGGGGGGGGGGGGGGGGGg.",
    ".gGGGGGGGGGGGGGGGGGGg.",
    ".gGGGGGGGGGGGGGGGGGGg.",
    ".gGGGGGGGGGGGGGGGGGGg.",
    ".gGGGGGGGGGGGGGGGGGGg.",
    ".gGGGGGGGGGGGGGGGGGGg.",
    ".gGGGGGGGGGGGGGGGGGGg.",
    ".gGGGGGGGGGGGGGGGGGGg.",
    ".gGGGGGGGGGGGGGGGGGGg.",
    ".gGGGGGGGGGGGGGGGGGGg.",
    ".gGGGGGGGGGGGGGGGGGGg.",
    ".gGGGGGGGGGGGGGGGGGGg.",
    "..gGGGGGGGGGGGGGGGGg..",
    "..gGGGGGGGGGGGGGGGGg..",
    "...gGGGGGGGGGGGGGGg...",
    "....gggggggggggggg....",
)


def _rectangles(scale: int) -> Iterable[str]:
    for row, line in enumerate(PIXELS):
        for col, pixel in enumerate(line):
            colour = PALETTE.get(pixel)
            if colour:
                yield (
                    f'<rect x="{col * scale}" y="{row * scale}" '
                    f'width="{scale}" height="{scale}" fill="{colour}" />'
                )


def build_svg(scale: int = 10) -> str:
    """Return an SVG whose visible pixels are generated from ``PIXELS``."""
    if scale < 2:
        raise ValueError("scale must be at least 2")

    width = len(PIXELS[0]) * scale
    height = len(PIXELS) * scale
    label_x = width // 2
    label_y = height // 2 + scale * 2
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" '
        f'height="{height}" viewBox="0 0 {width} {height}" role="img" '
        'aria-label="Code-drawn green Kuai Kuai package">',
        '<rect width="100%" height="100%" fill="#075a39" />',
        *list(_rectangles(scale)),
        f'<rect x="{scale * 3}" y="{scale * 8}" width="{width - scale * 6}" '
        f'height="{scale * 8}" rx="{scale}" fill="#fff7df" />',
        f'<text x="{label_x}" y="{label_y}" text-anchor="middle" '
        f'font-family="sans-serif" font-size="{scale * 2.2}" font-weight="700" '
        'fill="#e3133b">KK</text>',
        f'<text x="{label_x}" y="{height - scale * 3}" text-anchor="middle" '
        f'font-family="sans-serif" font-size="{scale * 1.25}" fill="#f2c84b">'
        'GREEN LUCK</text>',
        '</svg>',
    ]
    return "\n".join(parts) + "\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="write the generated SVG here")
    parser.add_argument("--scale", type=int, default=10)
    args = parser.parse_args()
    svg = build_svg(args.scale)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(svg, encoding="utf-8")
        print(f"drew {sum(pixel != '.' for row in PIXELS for pixel in row)} pixels -> {args.output}")
    else:
        print(svg, end="")


if __name__ == "__main__":
    main()
