#!/usr/bin/env python3
"""Build the README's small instructional GIF from the official package image."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
IMAGE = ROOT / "skills/kuai-kuai-bye-bye/assets/kuai-kuai-official-green.webp"
OUTPUT = ROOT / "docs/demo-drag-kuai-kuai.gif"
W, H = 960, 540
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def font(path, size):
    return ImageFont.truetype(path, size)

def frame(progress, final=False):
    im = Image.new("RGB", (W, H), "#f3f5f7")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 76), fill="#12372d")
    d.text((32, 20), "Kuai Kuai Bye Bye", font=font(BOLD, 30), fill="#ffffff")
    d.text((32, 88), "Drag the official green Kuai Kuai into the bottom layer", font=font(BOLD, 22), fill="#12372d")

    # Mock canvas and layer panel.
    d.rounded_rectangle((32, 132, 650, 490), radius=16, fill="#ffffff", outline="#c7ced3", width=2)
    d.text((58, 154), "PROJECT CANVAS", font=font(BOLD, 16), fill="#71808a")
    d.rounded_rectangle((72, 200, 610, 440), radius=10, fill="#e8edf0", outline="#c7ced3")
    d.text((274, 305), "your artwork", font=font(BOLD, 24), fill="#87949c")

    px, py = 700, 132
    d.rounded_rectangle((px, py, 928, 490), radius=16, fill="#1f252a", outline="#46515a", width=2)
    d.text((px + 20, py + 18), "LAYERS", font=font(BOLD, 16), fill="#c9d2d8")
    rows = [("TEXT", "#38434b"), ("ARTWORK", "#38434b"), ("BACKGROUND", "#38434b")]
    for i, (label, color) in enumerate(rows):
        y = py + 62 + i * 58
        d.rounded_rectangle((px + 14, y, 914, y + 44), radius=5, fill=color)
        d.text((px + 30, y + 12), label, font=font(BOLD, 14), fill="#e6edf0")
    bottom_y = py + 62 + 3 * 58
    d.rounded_rectangle((px + 14, bottom_y, 914, bottom_y + 44), radius=5, fill="#23734e" if final else "#38434b")
    d.text((px + 30, bottom_y + 12), "KUAI KUAI  [hidden] [locked]" if final else "DROP HERE: bottom layer", font=font(BOLD, 12), fill="#ffffff")

    package = Image.open(IMAGE).convert("RGBA")
    package.thumbnail((170, 170), Image.Resampling.LANCZOS)
    if final:
        x, y = 190, 260
    else:
        start = (150, 185)
        end = (px + 35, bottom_y - 55)
        x = int(start[0] + (end[0] - start[0]) * progress)
        y = int(start[1] + (end[1] - start[1]) * progress)
    im.paste(package, (x, y), package)
    if not final:
        d.ellipse((x + 70, y + 140, x + 88, y + 158), fill="#27a36d")
    if progress > 0.45 and not final:
        d.line((x + 85, y + 75, px + 22, bottom_y - 12), fill="#27a36d", width=4)
        d.polygon([(px + 22, bottom_y - 12), (px + 42, bottom_y - 20), (px + 38, bottom_y + 2)], fill="#27a36d")
    if final:
        d.text((58, 462), "Official package selected → placed at the bottom → hidden + locked", font=font(BOLD, 16), fill="#23734e")
    return im

def main():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    frames = [frame(i / 12) for i in range(13)] + [frame(1, final=True)] * 8
    frames[0].save(OUTPUT, save_all=True, append_images=frames[1:], duration=[110] * 13 + [180] * 7 + [1200], loop=0, optimize=False)
    print(OUTPUT)

if __name__ == "__main__":
    main()
