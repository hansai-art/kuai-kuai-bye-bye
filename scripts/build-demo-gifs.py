#!/usr/bin/env python3
"""Build the Illustrator and code-workflow demos used on the project homepage."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "skills/kuai-kuai-bye-bye/assets/kuai-kuai-official-green.webp"
DOCS = ROOT / "docs"
W, H = 1100, 620
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def f(path, size):
    return ImageFont.truetype(path, size)

def base(title, subtitle, accent="#ff9a00"):
    im = Image.new("RGB", (W, H), "#202124")
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, W, 70), fill="#2d2f33")
    d.ellipse((22, 25, 36, 39), fill="#ff5f57")
    d.ellipse((44, 25, 58, 39), fill="#ffbd2e")
    d.ellipse((66, 25, 80, 39), fill="#28c840")
    d.text((105, 19), title, font=f(BOLD, 26), fill="#f4f4f4")
    d.text((105, 79), subtitle, font=f(BOLD, 22), fill=accent)
    return im, d

def package_image(size=150):
    im = Image.open(PACKAGE).convert("RGBA")
    im.thumbnail((size, size), Image.Resampling.LANCZOS)
    return im

def illustrator_frame(progress, final=False):
    im, d = base("Adobe Illustrator", "Drag the official green Kuai Kuai into the bottom layer")
    # Toolbar and artboard.
    d.rectangle((0, 120, 58, H), fill="#35373b")
    for y, label in [(155, "V"), (205, "T"), (255, "R"), (305, "P"), (355, "A")]:
        d.rounded_rectangle((16, y, 42, y + 27), radius=4, fill="#555a60")
        d.text((25, y + 3), label, font=f(BOLD, 16), fill="#ffffff")
    d.rounded_rectangle((86, 130, 765, 565), radius=8, fill="#e9eaec", outline="#555a60", width=2)
    d.rectangle((116, 174, 735, 530), fill="#ffffff", outline="#c0c4c9", width=2)
    d.text((136, 190), "ARTBOARD", font=f(BOLD, 15), fill="#8b9096")
    d.rounded_rectangle((270, 280, 580, 420), radius=16, fill="#d9e8df", outline="#79a88e", width=3)
    d.text((338, 333), "YOUR ARTWORK", font=f(BOLD, 22), fill="#397054")
    # Layers panel.
    x0, y0 = 800, 125
    d.rounded_rectangle((x0, y0, 1070, 565), radius=8, fill="#292b2f", outline="#555a60", width=2)
    d.text((x0 + 22, y0 + 18), "LAYERS", font=f(BOLD, 17), fill="#f0f0f0")
    rows = ["TEXT", "ARTWORK", "BACKGROUND"]
    for i, label in enumerate(rows):
        y = y0 + 62 + i * 56
        d.rectangle((x0 + 16, y, 1054, y + 40), fill="#3a3d42")
        d.text((x0 + 34, y + 10), label, font=f(BOLD, 14), fill="#e9eaec")
    kuai_y = y0 + 62 + 3 * 56
    d.rectangle((x0 + 16, kuai_y, 1054, kuai_y + 40), fill="#24764d" if final else "#3a3d42")
    d.text((x0 + 34, kuai_y + 10), "KUAI KUAI", font=f(BOLD, 14), fill="#ffffff")
    d.text((x0 + 850, kuai_y + 10), "○  🔒" if final else "DROP", font=f(BOLD, 12), fill="#ffffff")
    # Official package moves from the canvas into the Layers panel.
    pkg = package_image(145)
    if final:
        px, py = 874, kuai_y - 58
    else:
        sx, sy = 155, 250
        ex, ey = 874, kuai_y - 58
        px = int(sx + (ex - sx) * progress)
        py = int(sy + (ey - sy) * progress)
    im.paste(pkg, (px, py), pkg)
    if not final and progress > 0.35:
        d.line((px + 70, py + 70, x0 + 10, kuai_y + 18), fill="#ff9a00", width=5)
        d.polygon([(x0 + 10, kuai_y + 18), (x0 + 34, kuai_y + 4), (x0 + 30, kuai_y + 30)], fill="#ff9a00")
    if final:
        d.text((120, 535), "Placed at the bottom  •  hidden  •  locked", font=f(BOLD, 18), fill="#24764d")
    return im

def code_frame(progress, final=False):
    im, d = base("Code Workspace", "Engineer workflow: bless the source file with Kuai Kuai")
    # Terminal panel.
    d.rounded_rectangle((42, 130, 420, 565), radius=8, fill="#111315", outline="#555a60", width=2)
    d.text((65, 153), "TERMINAL", font=f(BOLD, 16), fill="#9da5ad")
    lines = [
        ("$ python3 kuai.py init", "#e6e6e6"),
        ("$ kuai.py bless --file", "#e6e6e6"),
        ("  src/main.ts", "#e6e6e6"),
        ("", "#e6e6e6"),
        ("Talisman installed", "#55d68b"),
    ]
    for i, (txt, color) in enumerate(lines):
        d.text((65, 205 + i * 34), txt, font=f(FONT, 17), fill=color)
    # Code editor.
    x0 = 455
    d.rounded_rectangle((x0, 130, 1060, 565), radius=8, fill="#15191d", outline="#555a60", width=2)
    d.text((x0 + 22, 153), "src/main.ts", font=f(BOLD, 16), fill="#9da5ad")
    code = [
        ("1", "import { app } from './app';", "#d9dee3"),
        ("2", "", "#d9dee3"),
        ("3", "export function start() {", "#d9dee3"),
        ("4", "  return app.run();", "#d9dee3"),
        ("5", "}", "#d9dee3"),
    ]
    if final:
        code = [
            ("1", "/* DIGITAL-KUAI-KUAI BEGIN", "#55d68b"),
            ("2", " * Kuai Kuai talisman: please do not delete", "#55d68b"),
            ("3", " * DIGITAL-KUAI-KUAI END */", "#55d68b"),
        ] + code
    for i, (num, txt, color) in enumerate(code):
        y = 205 + i * 34
        d.text((x0 + 22, y), num, font=f(FONT, 16), fill="#69737d")
        d.text((x0 + 70, y), txt, font=f(FONT, 16), fill=color)
    pkg = package_image(108)
    im.paste(pkg, (930, 20), pkg)
    if not final and progress > 0.45:
        d.line((930, 130, x0 + 215, 200), fill="#55d68b", width=4)
        d.polygon([(x0 + 215, 200), (x0 + 235, 201), (x0 + 223, 218)], fill="#55d68b")
    if final:
        d.text((475, 480), "Comment inserted — no runtime dependency", font=f(BOLD, 18), fill="#55d68b")
    return im

def save_demo(name, maker):
    frames = [maker(i / 12) for i in range(13)] + [maker(1, final=True)] * 8
    gif = DOCS / f"{name}.gif"
    png = DOCS / f"{name}.png"
    frames[-1].save(png, optimize=True)
    frames[0].save(gif, save_all=True, append_images=frames[1:], duration=[110] * 13 + [180] * 7 + [1200], loop=0, optimize=False)

def main():
    DOCS.mkdir(parents=True, exist_ok=True)
    save_demo("demo-illustrator-kuai-kuai", illustrator_frame)
    save_demo("demo-code-kuai-kuai", code_frame)
    print("created Illustrator and code demos")

if __name__ == "__main__":
    main()
