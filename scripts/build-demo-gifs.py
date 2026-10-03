#!/usr/bin/env python3
"""Build the realistic Illustrator and code-drawn Kuai Kuai demos."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "skills/kuai-kuai-bye-bye/assets/kuai-kuai-official-green.webp"
DOCS = ROOT / "docs"
W, H = 1280, 720

REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
MONO_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"


def font(path: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(path, size)


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int,
         fill: str = "#d6d6d6", bold: bool = False, mono: bool = False) -> None:
    path = MONO_BOLD if mono and bold else MONO if mono else BOLD if bold else REGULAR
    draw.text(xy, value, font=font(path, size), fill=fill)


def rounded(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], radius: int,
            fill: str, outline: str | None = None, width: int = 1) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def fit_package(size: int = 130) -> Image.Image:
    package = Image.open(PACKAGE).convert("RGBA")
    package.thumbnail((size, size), Image.Resampling.LANCZOS)
    return package


def draw_mouse(draw: ImageDraw.ImageDraw, x: int, y: int, pressed: bool = False) -> None:
    """Draw an actual pointer, not a decorative direction arrow."""
    pointer = [(x, y), (x + 4, y + 30), (x + 12, y + 22),
               (x + 22, y + 39), (x + 28, y + 35), (x + 18, y + 19),
               (x + 30, y + 16)]
    shadow = [(px + 3, py + 3) for px, py in pointer]
    draw.polygon(shadow, fill="#000000")
    draw.polygon(pointer, fill="#ffffff", outline="#111111")
    draw.line((x + 5, y + 6, x + 8, y + 23), fill="#b8b8b8", width=1)
    if pressed:
        draw.ellipse((x - 9, y - 9, x + 42, y + 42), outline="#5ca8ff", width=2)
        draw.ellipse((x - 4, y - 4, x + 37, y + 37), outline="#5ca8ff", width=1)


def draw_dashed_box(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int],
                    colour: str = "#4da3ff", dash: int = 8) -> None:
    x1, y1, x2, y2 = box
    for x in range(x1, x2, dash * 2):
        draw.line((x, y1, min(x + dash, x2), y1), fill=colour, width=2)
        draw.line((x, y2, min(x + dash, x2), y2), fill=colour, width=2)
    for y in range(y1, y2, dash * 2):
        draw.line((x1, y, x1, min(y + dash, y2)), fill=colour, width=2)
        draw.line((x2, y, x2, min(y + dash, y2)), fill=colour, width=2)


def illustrator_shell() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGB", (W, H), "#252525")
    draw = ImageDraw.Draw(im)

    # Illustrator desktop title bar.
    draw.rectangle((0, 0, W, 31), fill="#242424")
    draw.ellipse((14, 10, 24, 20), fill="#ff5f57")
    draw.ellipse((30, 10, 40, 20), fill="#ffbd2e")
    draw.ellipse((46, 10, 56, 20), fill="#28c840")
    draw.rectangle((78, 6, 101, 26), fill="#ff9a00")
    text(draw, (83, 7), "Ai", 14, "#242424", bold=True)
    text(draw, (112, 7), "kuai-kuai.ai @ 100% (RGB/Preview)", 13, "#d8d8d8")
    text(draw, (1055, 7), "Adobe Illustrator", 13, "#a9a9a9")

    # Application menu and Properties control bar.
    draw.rectangle((0, 31, W, 61), fill="#303030")
    for x, label in [(18, "File"), (58, "Edit"), (98, "Object"), (151, "Type"),
                     (190, "Select"), (244, "Effect"), (294, "View"),
                     (339, "Window"), (405, "Help")]:
        text(draw, (x, 39), label, 12, "#e0e0e0")
    draw.rectangle((0, 61, W, 101), fill="#3a3a3a")
    text(draw, (15, 74), "Selection", 11, "#a9a9a9")
    rounded(draw, (82, 68, 174, 93), 3, "#262626", "#5c5c5c")
    text(draw, (92, 74), "No Selection", 11, "#e0e0e0")
    for x, label, value in [(205, "X:", "—"), (286, "Y:", "—"), (367, "W:", "—"),
                            (448, "H:", "—")]:
        text(draw, (x, 75), label, 11, "#a9a9a9")
        rounded(draw, (x + 18, 68, x + 70, 93), 3, "#262626", "#5c5c5c")
        text(draw, (x + 28, 75), value, 11, "#e0e0e0")
    text(draw, (555, 75), "Transform", 11, "#a9a9a9")
    for x in (620, 647, 674, 701):
        rounded(draw, (x, 70, x + 22, 91), 3, "#292929", "#606060")
    text(draw, (625, 73), "↔", 12, "#e0e0e0")
    text(draw, (652, 73), "↕", 12, "#e0e0e0")
    text(draw, (679, 73), "⌗", 12, "#e0e0e0")
    text(draw, (706, 73), "⊕", 12, "#e0e0e0")

    # Workspace, toolbar and document canvas.
    draw.rectangle((0, 101, W, 686), fill="#2c2c2c")
    draw.rectangle((0, 101, 53, 686), fill="#373737")
    tool_icons = ["↖", "⌗", "T", "▱", "◯", "✒", "⊙", "✋", "⌕"]
    for i, icon in enumerate(tool_icons):
        y = 119 + i * 42
        text(draw, (18, y), icon, 19, "#dedede", bold=icon == "T")
        if i in (0, 3, 6):
            draw.line((11, y + 29, 42, y + 29), fill="#5b5b5b", width=1)
    text(draw, (16, 627), "Fill", 9, "#999999")
    draw.rectangle((13, 643, 30, 660), fill="#ffffff", outline="#161616")
    draw.rectangle((23, 651, 40, 668), fill="#202020", outline="#c4c4c4")

    # Artboard and pasteboard.
    draw.rectangle((53, 101, 1000, 686), fill="#292929")
    text(draw, (74, 119), "kuai-kuai.ai", 11, "#9b9b9b")
    draw.rectangle((150, 155, 895, 635), fill="#1f1f1f", outline="#575757")
    draw.rectangle((180, 180, 865, 610), fill="#ffffff", outline="#b7b7b7")
    text(draw, (201, 195), "ARTBOARD 01", 10, "#b6b6b6")
    rounded(draw, (333, 300, 713, 478), 3, "#f3f0e8", "#d1c5a3", width=2)
    text(draw, (410, 350), "CLIENT ARTWORK", 20, "#5e6b72", bold=True)
    text(draw, (427, 381), "selected document", 12, "#929292")
    draw.line((368, 431, 678, 431), fill="#e0d6bd", width=2)

    # Right-side dock and Layers panel.
    draw.rectangle((1000, 101, W, 686), fill="#363636")
    draw.rectangle((1010, 101, W, 136), fill="#2f2f2f")
    for x, label in [(1020, "Layers"), (1078, "Properties"), (1150, "Libraries")]:
        text(draw, (x, 112), label, 11, "#e5e5e5" if label == "Layers" else "#999999",
             bold=label == "Layers")
    draw.rectangle((1010, 136, W, 176), fill="#404040")
    text(draw, (1020, 147), "Layers", 13, "#eeeeee", bold=True)
    text(draw, (1198, 147), "☰", 15, "#cccccc")
    text(draw, (1225, 147), "＋", 15, "#cccccc")

    return im, draw


def draw_eye(draw: ImageDraw.ImageDraw, x: int, y: int, visible: bool) -> None:
    if visible:
        draw.ellipse((x, y + 7, x + 17, y + 17), outline="#d0d0d0", width=1)
        draw.ellipse((x + 6, y + 10, x + 11, y + 15), fill="#d0d0d0")
    else:
        draw.line((x, y + 5, x + 18, y + 20), fill="#777777", width=2)
        draw.ellipse((x + 4, y + 8, x + 14, y + 18), outline="#777777", width=1)


def draw_lock(draw: ImageDraw.ImageDraw, x: int, y: int, locked: bool) -> None:
    if locked:
        draw.arc((x + 4, y + 2, x + 15, y + 14), 180, 360, fill="#e4e4e4", width=2)
        draw.rectangle((x + 2, y + 9, x + 17, y + 20), fill="#e4e4e4")
        draw.rectangle((x + 8, y + 12, x + 11, y + 17), fill="#4a4a4a")


def draw_layers(draw: ImageDraw.ImageDraw, active: bool, final: bool) -> tuple[int, int]:
    rows = ["TEXT", "ARTWORK", "BACKGROUND", "KUAI_KUAI_TALISMAN"]
    y0 = 192
    row_h = 46
    target_y = y0 + 3 * row_h
    for index, name in enumerate(rows):
        y = y0 + index * row_h
        selected = active and index == 3
        draw.rectangle((1010, y, 1279, y + row_h), fill="#454545" if selected else "#383838")
        text(draw, (1020, y + 15), "▸" if index < 3 else "", 11, "#bbbbbb")
        draw_eye(draw, 1044, y + 10, visible=index < 3)
        draw_lock(draw, 1071, y + 10, locked=final and index == 3)
        text(draw, (1100, y + 14), name, 11, "#ffffff" if selected else "#d4d4d4",
             bold=selected)
        draw.ellipse((1243, y + 15, 1254, y + 26), outline="#a7a7a7")
    text(draw, (1018, 394), "▾  Appearance", 11, "#bcbcbc")
    draw.line((1010, 416, 1280, 416), fill="#505050")
    text(draw, (1018, 430), "▾  Graphic Styles", 11, "#bcbcbc")
    return 1130, target_y + row_h // 2


def illustrator_frame(progress: float, final: bool = False) -> Image.Image:
    im, draw = illustrator_shell()
    target_x, target_y = draw_layers(draw, active=progress > 0.76 or final, final=final)
    source_x, source_y = 520, 389
    package = fit_package(136)
    package_w, package_h = package.size
    start_x, start_y = source_x - package_w // 2, source_y - package_h // 2

    if final:
        text(draw, (73, 656), "Object hidden and locked in the bottom layer", 12, "#6ed19d", bold=True)
        draw_mouse(draw, target_x + 18, target_y - 2)
        return im

    if progress < 0.22:
        cursor_x = int(730 - (730 - source_x) * (progress / 0.22))
        cursor_y = int(230 + (source_y - 230) * (progress / 0.22))
        object_x, object_y = start_x, start_y
        pressed = False
    else:
        drag_progress = min(1.0, (progress - 0.22) / 0.70)
        cursor_x = int(source_x + (target_x - source_x) * drag_progress)
        cursor_y = int(source_y + (target_y - source_y) * drag_progress)
        object_x = cursor_x - package_w // 2 + 10
        object_y = cursor_y - package_h // 2 + 10
        pressed = True

    im.paste(package, (object_x, object_y), package)
    draw_dashed_box(draw, (object_x - 7, object_y - 7, object_x + package_w + 7,
                           object_y + package_h + 7))
    draw_mouse(draw, cursor_x, cursor_y, pressed=pressed)
    if pressed:
        text(draw, (72, 656), "Click and hold — drag the placed object to the bottom layer", 12,
             "#80bfff", bold=True)
    else:
        text(draw, (72, 656), "Place the official green package on the artboard", 12, "#d0d0d0")
    return im


# The code demo follows the event-triggered ASCII-art approach in the
# referenced Vite plug-in. It never reads PACKAGE.
ASCII_ART = (
    "             ███████████",
    "         ███████████████████",
    "      █████████████████████████",
    "    █████████████████████████████",
    "   ███████████████████████████████",
    "  █████████████████████████████████",
    " ███████████████████████████████████",
    " ████████     █████████     ████████",
    " ███████      █████████      ███████",
    " ███████████████████████████████████",
    "  █████████████████████████████████",
    "   ███████████████████████████████",
    "     ███████████████████████████",
    "         ███████████████████",
    "             ███████████",
)


def draw_ascii_preview(draw: ImageDraw.ImageDraw, x: int, y: int, visible: int | None = None) -> None:
    lines = ASCII_ART if visible is None else ASCII_ART[:visible]
    for row, line in enumerate(lines):
        text(draw, (x, y + row * 15), line, 11, "#42c77a", bold=True, mono=True)


def code_shell() -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGB", (W, H), "#1e1e1e")
    draw = ImageDraw.Draw(im)
    # VS Code-like title bar and menus.
    draw.rectangle((0, 0, W, 32), fill="#181818")
    draw.polygon([(16, 8), (24, 4), (33, 8), (33, 23), (24, 28), (16, 23)], fill="#2f8cff")
    text(draw, (48, 8), "main.py — kuai-kuai-demo — Visual Studio Code", 12, "#d0d0d0")
    text(draw, (1110, 8), "—  □  ×", 12, "#a9a9a9")
    draw.rectangle((0, 32, W, 61), fill="#222222")
    for x, label in [(16, "File"), (51, "Edit"), (86, "Selection"), (153, "View"),
                     (194, "Go"), (224, "Run"), (263, "Terminal"), (326, "Help")]:
        text(draw, (x, 40), label, 11, "#d8d8d8")

    # Activity bar and Explorer.
    draw.rectangle((0, 61, 48, 686), fill="#181818")
    for y, icon in [(85, "▱"), (132, "⌕"), (179, "⑂"), (226, "▶"), (273, "□")]:
        text(draw, (16, y), icon, 17, "#b9b9b9")
    draw.rectangle((48, 61, 280, 686), fill="#252526")
    text(draw, (65, 78), "EXPLORER", 11, "#bbbbbb", bold=True)
    text(draw, (66, 111), "KUAI-KUAI-DEMO", 11, "#d8d8d8", bold=True)
    text(draw, (68, 143), "⌄  .kuai-kuai", 12, "#c4c4c4")
    text(draw, (90, 172), "▱  manifest.json", 11, "#aeb4bb")
    text(draw, (90, 199), "▣  code-kuai-kuai.py", 11, "#aeb4bb")
    text(draw, (68, 235), "⌄  src", 12, "#c4c4c4")
    text(draw, (90, 264), "▣  main.py", 11, "#ffffff", bold=True)
    text(draw, (90, 291), "▱  app.py", 11, "#aeb4bb")
    text(draw, (65, 650), "1 unsaved change", 10, "#d7ba7d")

    # Editor and preview panes.
    draw.rectangle((280, 61, 913, 686), fill="#1e1e1e")
    draw.rectangle((913, 61, W, 686), fill="#202124")
    draw.rectangle((280, 61, 913, 96), fill="#252526")
    text(draw, (302, 72), "main.py", 12, "#ffffff", bold=True)
    text(draw, (384, 72), "×", 12, "#999999")
    text(draw, (438, 72), "kuai_kuai.py", 12, "#9d9d9d")
    text(draw, (527, 72), "×", 12, "#777777")
    text(draw, (934, 73), "OUTPUT", 11, "#e0e0e0", bold=True)
    text(draw, (1011, 73), "CODE PREVIEW", 11, "#8d8d8d")
    draw.line((913, 96, W, 96), fill="#424242")
    draw.line((913, 97, 913, 686), fill="#515151", width=2)
    return im, draw


CODE_LINES = [
    ('GREEN = "\\033[32m"', "#ce9178"),
    ('RESET = "\\033[0m"', "#ce9178"),
    ("", "#d4d4d4"),
    ('KUAI_KUAI = r"""', "#569cd6"),
    ("             ███████████", "#42c77a"),
    ("         ███████████████████", "#42c77a"),
    ("      █████████████████████████", "#42c77a"),
    ("    █████████████████████████████", "#42c77a"),
    ("   ███████████████████████████████", "#42c77a"),
    ("  █████████████████████████████████", "#42c77a"),
    (" ███████████████████████████████████", "#42c77a"),
    (" ████████     █████████     ████████", "#42c77a"),
    (" ███████      █████████      ███████", "#42c77a"),
    (" ███████████████████████████████████", "#42c77a"),
    ("  █████████████████████████████████", "#42c77a"),
    ("   ███████████████████████████████", "#42c77a"),
    ("     ███████████████████████████", "#42c77a"),
    ("         ███████████████████", "#42c77a"),
    ("             ███████████", "#42c77a"),
    ('"""', "#569cd6"),
    ("", "#d4d4d4"),
    ("def bless(event, on_build=False, on_dev=False):", "#569cd6"),
    ('    if event == "build" and not on_build:', "#c586c0"),
    ('        return ""', "#ce9178"),
    ("    print(GREEN + KUAI_KUAI + RESET)", "#dcdcaa"),
]


def code_frame(progress: float, final: bool = False) -> Image.Image:
    im, draw = code_shell()
    editor_x, editor_y = 300, 112
    line_height = 18
    visible = len(CODE_LINES) if final else max(3, min(len(CODE_LINES), int(3 + progress * (len(CODE_LINES) - 3))))
    for index, (line, colour) in enumerate(CODE_LINES[:visible]):
        y = editor_y + index * line_height
        text(draw, (editor_x, y), f"{index + 1:>2}", 11, "#606a73", mono=True)
        text(draw, (editor_x + 38, y), line, 12, colour, mono=True)

    # A blinking caret communicates typing; it replaces the old fake drag arrow.
    if not final:
        last_line = CODE_LINES[visible - 1][0]
        caret_x = editor_x + 38 + len(last_line) * 7
        draw.rectangle((caret_x, editor_y + (visible - 1) * line_height, caret_x + 2,
                        editor_y + (visible - 1) * line_height + 15), fill="#aeafad")

    # The preview appears row by row only after the lifecycle hook exists.
    preview_x, preview_y = 942, 165
    if final:
        draw_ascii_preview(draw, preview_x, preview_y)
        text(draw, (954, 421), "Printed from source code", 13, "#6ed19d", bold=True)
        text(draw, (954, 443), "No image asset loaded", 11, "#a6a6a6")
        text(draw, (954, 466), "ANSI green + build hook", 11, "#a6a6a6")
    elif visible > 4:
        rows = min(len(ASCII_ART), visible - 4)
        draw_ascii_preview(draw, preview_x, preview_y, visible=rows)
        text(draw, (954, 421), "Executing build hook…", 12, "#dcdcaa")
    else:
        text(draw, (954, 207), "Waiting for event…", 13, "#777777")
        text(draw, (954, 235), "The talisman is stored", 11, "#777777")
        text(draw, (954, 253), "inside the source code.", 11, "#777777")

    # Integrated terminal and status bar.
    draw.rectangle((280, 600, 913, 686), fill="#181818")
    text(draw, (300, 612), "TERMINAL", 10, "#e0e0e0", bold=True)
    terminal_lines = [
        "$ python3 code-kuai-kuai.py --event build --on-build",
        "[kuai-kuai] build → printed from source",
    ]
    shown_terminal = terminal_lines if final or progress > 0.72 else terminal_lines[:1]
    for i, line in enumerate(shown_terminal):
        text(draw, (300, 634 + i * 17), line, 10, "#9cdcfe" if i == 0 else "#6ed19d", mono=True)
    draw.rectangle((0, 686, W, H), fill="#007acc")
    text(draw, (15, 696), "main", 10, "#ffffff")
    text(draw, (75, 696), "Ln 18, Col 5", 10, "#ffffff")
    text(draw, (1048, 696), "Python 3  UTF-8", 10, "#ffffff")
    return im


def save_demo(name: str, maker) -> None:
    # More hold frames make the operation readable on GitHub while preserving
    # the pointer movement and the row-by-row code rendering.
    motion = [maker(i / 18) for i in range(19)]
    hold = [maker(1.0, final=True) for _ in range(9)]
    frames = motion + hold
    gif = DOCS / f"{name}.gif"
    png = DOCS / f"{name}.png"
    frames[-1].save(png, optimize=True)
    frames[0].save(gif, save_all=True, append_images=frames[1:],
                   duration=[90] * len(motion) + [170] * 8 + [1200], loop=0, optimize=False)


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    save_demo("demo-illustrator-kuai-kuai", illustrator_frame)
    save_demo("demo-code-kuai-kuai", code_frame)
    print("created realistic Illustrator and code-drawn demos")


if __name__ == "__main__":
    main()
