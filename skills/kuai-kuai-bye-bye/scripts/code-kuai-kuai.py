#!/usr/bin/env python3
"""Print a code-defined Kuai Kuai talisman at selected project events.

The useful idea is deliberately small: keep the drawing in the source code,
then print it in green when a chosen lifecycle event happens.  No image file,
Pillow, SVG renderer, or runtime asset is required.
"""

from __future__ import annotations

import argparse


GREEN = "\033[32m"
RESET = "\033[0m"

# Inspired by the event-triggered ASCII-art approach in:
# https://github.com/unickhow/vite-plugin-kuaikuai
ASCII_ART = r"""
             ███████████
         ███████████████████
      █████████████████████████
    █████████████████████████████
   ███████████████████████████████
  █████████████████████████████████
 ███████████████████████████████████
 ████████     █████████     ████████
 ███████      █████████      ███████
 ███████████████████████████████████
  █████████████████████████████████
   ███████████████████████████████
     ███████████████████████████
         ███████████████████
             ███████████
""".strip("\n")


def should_bless(event: str, *, on_build: bool = False, on_dev: bool = False) -> bool:
    """Match the reference plugin's opt-in build and dev hooks."""
    if event == "build":
        return on_build
    if event == "dev":
        return on_dev
    return event == "manual"


def bless(event: str = "manual", *, on_build: bool = False, on_dev: bool = False,
          color: bool = True) -> str:
    """Return the talisman output, or an empty string when the hook is disabled."""
    if not should_bless(event, on_build=on_build, on_dev=on_dev):
        return ""
    art = f"{GREEN}{ASCII_ART}{RESET}" if color else ASCII_ART
    return f"[kuai-kuai] {event}\n{art}\n"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--event", choices=("manual", "dev", "build"), default="manual")
    parser.add_argument("--on-build", action="store_true", help="enable the build hook")
    parser.add_argument("--on-dev", action="store_true", help="enable the dev hook")
    parser.add_argument("--plain", action="store_true", help="disable ANSI colour codes")
    args = parser.parse_args()
    output = bless(args.event, on_build=args.on_build, on_dev=args.on_dev, color=not args.plain)
    if output:
        print(output, end="")


if __name__ == "__main__":
    main()
