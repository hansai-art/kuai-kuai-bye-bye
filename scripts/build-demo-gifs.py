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


def faded_package(package: Image.Image, opacity: int) -> Image.Image:
    """Return the placed package at Illustrator's current opacity."""
    opacity = max(0, min(100, opacity))
    if opacity == 100:
        return package
    faded = package.copy()
    faded.putalpha(faded.getchannel("A").point(lambda value: value * opacity // 100))
    return faded


def lerp(start: int, end: int, amount: float) -> int:
    amount = max(0.0, min(1.0, amount))
    return int(round(start + (end - start) * amount))


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
                    colour: str = "#2d7fff", dash: int = 8) -> None:
    """Draw Illustrator's blue bounding box and eight transform handles."""
    x1, y1, x2, y2 = box
    draw.rectangle((x1, y1, x2, y2), outline=colour, width=1)
    handle_size = 6
    points = [
        (x1, y1), ((x1 + x2) // 2, y1), (x2, y1),
        (x1, (y1 + y2) // 2), (x2, (y1 + y2) // 2),
        (x1, y2), ((x1 + x2) // 2, y2), (x2, y2),
    ]
    for x, y in points:
        draw.rectangle((x - handle_size // 2, y - handle_size // 2,
                        x + handle_size // 2, y + handle_size // 2),
                       fill="#ffffff", outline=colour, width=1)


def illustrator_shell(opacity: int = 100, selected: bool = False) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    im = Image.new("RGB", (W, H), "#252525")
    draw = ImageDraw.Draw(im)

    # Illustrator desktop title bar.  The layout deliberately gives the Layers
    # dock enough width to remain legible when the README is viewed on a phone.
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
    text(draw, (92, 74), "Image" if selected else "No Selection", 11, "#e0e0e0")
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
    text(draw, (752, 75), "Opacity:", 11, "#a9a9a9")
    rounded(draw, (811, 68, 878, 93), 3, "#262626", "#5c5c5c")
    text(draw, (824, 75), f"{opacity}%" if selected else "—", 11, "#f0f0f0")

    # Workspace, toolbar and document canvas.
    draw.rectangle((0, 101, W, 686), fill="#2c2c2c")
    draw.rectangle((0, 101, 53, 686), fill="#373737")
    # Small vector glyphs read more like Illustrator's toolbar than a column
    # of decorative arrows or emoji.  The selected tool is highlighted.
    draw.rectangle((7, 111, 46, 145), fill="#4a4a4a")
    draw.line((17, 120, 33, 136), fill="#efefef", width=2)
    draw.line((17, 120, 17, 130), fill="#efefef", width=2)
    draw.line((17, 120, 27, 120), fill="#efefef", width=2)
    draw.rectangle((16, 157, 35, 176), outline="#cfcfcf", width=2)
    text(draw, (19, 193), "T", 20, "#ededed", bold=True)
    draw.line((15, 239, 34, 239), fill="#d6d6d6", width=2)
    draw.line((15, 239, 23, 228), fill="#d6d6d6", width=2)
    draw.ellipse((14, 269, 35, 290), outline="#d6d6d6", width=2)
    draw.line((14, 320, 35, 320), fill="#d6d6d6", width=2)
    draw.line((18, 316, 31, 324), fill="#d6d6d6", width=2)
    draw.arc((14, 361, 34, 381), 215, 500, fill="#d6d6d6", width=2)
    draw.line((22, 368, 35, 380), fill="#d6d6d6", width=2)
    draw.line((15, 411, 34, 411), fill="#d6d6d6", width=2)
    draw.line((15, 411, 15, 430), fill="#d6d6d6", width=2)
    draw.line((34, 411, 34, 430), fill="#d6d6d6", width=2)
    draw.ellipse((17, 459, 33, 475), outline="#d6d6d6", width=2)
    draw.line((33, 474, 40, 481), fill="#d6d6d6", width=2)
    text(draw, (16, 627), "Fill", 9, "#999999")
    draw.rectangle((13, 643, 30, 660), fill="#ffffff", outline="#161616")
    draw.rectangle((23, 651, 40, 668), fill="#202020", outline="#c4c4c4")

    # Artboard and pasteboard.  The centre document is intentionally quiet so
    # the real action—the selected object staying on the artboard while its
    # Layers row moves—remains the visual focus.
    draw.rectangle((53, 101, 900, 686), fill="#292929")
    text(draw, (74, 119), "kuai-kuai.ai", 11, "#9b9b9b")
    draw.rectangle((92, 143, 865, 653), fill="#1f1f1f", outline="#575757")
    draw.rectangle((122, 169, 835, 627), fill="#ffffff", outline="#b7b7b7")
    text(draw, (143, 184), "ARTBOARD 01", 10, "#a6a6a6")
    # A restrained editorial poster gives the mock document a believable
    # designer context without competing with the Layers panel.
    rounded(draw, (278, 242, 680, 548), 2, "#f4f1e9", "#d1c5a3", width=1)
    draw.rectangle((278, 242, 680, 296), fill="#232f40")
    draw.rectangle((278, 296, 344, 548), fill="#232f40")
    draw.ellipse((532, 290, 654, 412), fill="#e97054")
    draw.ellipse((410, 414, 486, 490), fill="#efc65d")
    draw.rectangle((488, 344, 600, 456), outline="#232f40", width=2)
    text(draw, (296, 260), "STUDIO / FORM", 11, "#f6f2e8", bold=True)
    text(draw, (365, 324), "01", 44, "#232f40", bold=True)
    text(draw, (365, 382), "OBJECT", 11, "#232f40", bold=True)
    text(draw, (365, 402), "IMAGE / TYPE", 10, "#6d747d")
    draw.line((365, 476, 628, 476), fill="#232f40", width=1)
    draw.line((365, 488, 520, 488), fill="#b4a991", width=1)
    text(draw, (296, 508), "FORM STUDY", 9, "#f4f1e9", bold=True)

    # Right-side dock and Layers panel.
    draw.rectangle((900, 101, W, 686), fill="#343434")
    draw.rectangle((910, 101, W, 141), fill="#2f2f2f")
    for x, label in [(918, "Properties"), (1018, "Layers"), (1110, "Libraries")]:
        text(draw, (x, 112), label, 12, "#e5e5e5" if label == "Layers" else "#999999",
             bold=label == "Layers")
    draw.rectangle((910, 141, W, 185), fill="#404040")
    text(draw, (922, 153), "Layers", 15, "#eeeeee", bold=True)
    # Panel menu and new-layer icons, drawn as simple UI glyphs.
    draw.line((1197, 153, 1210, 153), fill="#cccccc", width=2)
    draw.line((1197, 158, 1210, 158), fill="#cccccc", width=2)
    draw.line((1197, 163, 1210, 163), fill="#cccccc", width=2)
    draw.rectangle((1230, 151, 1242, 163), outline="#cccccc", width=1)
    draw.line((1236, 147, 1236, 167), fill="#cccccc", width=1)
    draw.line((1227, 157, 1245, 157), fill="#cccccc", width=1)

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


TALISMAN_LAYER = "KUAI_KUAI_TALISMAN"
ARTWORK_LAYERS = ("TEXT", "ARTWORK", "BACKGROUND")


def illustrator_state(progress: float, final: bool = False) -> dict[str, int | bool | str]:
    """Return the Illustrator actions represented by a demo frame.

    The package never travels into the right dock. The selected layer row moves
    to the bottom, then the selected object's Opacity is reduced to 0%.
    """
    p = max(0.0, min(1.0, progress))
    reorder = max(0.0, min(1.0, (p - 0.32) / 0.36))
    opacity_fade = max(0.0, min(1.0, (p - 0.70) / 0.20))
    if final:
        reorder = 1.0
        opacity_fade = 1.0
    opacity = int(round(100 * (1.0 - opacity_fade)))
    if final:
        opacity = 0
    phase = "place"
    if p >= 0.24:
        phase = "drag-layer"
    if p >= 0.70:
        phase = "set-opacity"
    if final:
        phase = "complete"
    return {
        "reorder": reorder,
        "opacity": opacity,
        "placed": final or p >= 0.08,
        "selected": final or p >= 0.14,
        "locked": final or p >= 0.94,
        "layer_dragging": not final and 0.32 <= p < 0.70,
        "opacity_adjusting": not final and 0.70 <= p < 0.92,
        "package_alpha": opacity,
        "phase": phase,
    }


def draw_layers(draw: ImageDraw.ImageDraw, state: dict[str, int | bool | str]) -> dict[str, int]:
    """Draw a Layers panel whose row order changes, not the package position."""
    panel_x = 910
    panel_right = 1279
    y0 = 196
    row_h = 48
    reorder = float(state["reorder"])
    talisman_y = y0

    def render_row(name: str, y: int, selected: bool = False, dragged: bool = False) -> None:
        is_talisman = name == TALISMAN_LAYER
        row_fill = "#4b5d70" if selected else "#383838"
        draw.rectangle((panel_x, y, panel_right, y + row_h), fill=row_fill)
        if dragged:
            draw.rectangle((panel_x + 1, y + 1, panel_right - 1, y + row_h - 1),
                           outline="#62b2ff", width=2)
        text(draw, (920, y + 16), "▸" if not is_talisman else "", 11, "#bbbbbb")
        # The eye stays on. Opacity 0% is the deliberate Illustrator hiding step.
        draw_eye(draw, 944, y + 13, visible=True)
        draw_lock(draw, 973, y + 12, locked=is_talisman and bool(state["locked"]))
        # Layer thumbnails are a small but important realism cue in the real
        # panel; the talisman keeps a green swatch even after Opacity is 0%.
        if is_talisman:
            draw.rectangle((1001, y + 14, 1025, y + 34), fill="#5cab45", outline="#c7d8c0")
            draw.rectangle((1006, y + 18, 1020, y + 30), fill="#d7e6c4")
        else:
            draw.rectangle((1001, y + 14, 1025, y + 34), fill="#777777", outline="#a8a8a8")
            draw.line((1005, y + 29, 1021, y + 18), fill="#d4d4d4", width=1)
        display_name = "KUAI-KUAI / TALISMAN" if is_talisman else name
        text(draw, (1036, y + 15), display_name, 12, "#ffffff" if selected else "#d4d4d4",
             bold=selected)
        if selected:
            draw.ellipse((1243, y + 17, 1254, y + 28), outline="#ff9d00", width=2)
        else:
            draw.ellipse((1244, y + 18, 1253, y + 27), outline="#a7a7a7")

    if bool(state["layer_dragging"]):
        # During a real Layers-panel drag, the selected row floats over the
        # other rows while the blue insertion line marks the final position.
        for index, name in enumerate(ARTWORK_LAYERS):
            render_row(name, y0 + index * row_h)
        talisman_y = int(round(y0 + reorder * 3 * row_h))
        render_row(TALISMAN_LAYER, talisman_y, selected=True, dragged=True)
        drop_y = y0 + 3 * row_h
        draw.line((panel_x + 4, drop_y - 4, panel_right - 4, drop_y - 4),
                  fill="#62b2ff", width=2)
    else:
        rows = (TALISMAN_LAYER,) + ARTWORK_LAYERS if reorder < 1.0 else ARTWORK_LAYERS + (TALISMAN_LAYER,)
        talisman_y = y0 + (3 if reorder >= 1.0 else 0) * row_h
        for index, name in enumerate(rows):
            render_row(name, y0 + index * row_h,
                       selected=name == TALISMAN_LAYER and bool(state["selected"]))

    text(draw, (922, 407), "▾  Appearance", 12, "#bcbcbc")
    draw.line((panel_x, 429, 1280, 429), fill="#505050")
    text(draw, (934, 448), "Opacity", 12, "#d0d0d0")
    rounded(draw, (1032, 440, 1168, 473), 3, "#262626", "#777777")
    text(draw, (1048, 448), f"{int(state['opacity'])}%", 13, "#f0f0f0", bold=bool(state["opacity_adjusting"]))
    text(draw, (1182, 448), "↕", 13, "#9e9e9e")
    text(draw, (922, 507), "▾  Transparency", 12, "#bcbcbc")
    draw.line((panel_x, 529, 1280, 529), fill="#505050")
    text(draw, (934, 546), "Selected object", 11, "#969696")
    text(draw, (1032, 546), "Image", 11, "#d2d2d2")

    return {
        "row_x": 1100,
        "talisman_y": talisman_y + row_h // 2,
        "top_talisman_y": y0 + row_h // 2,
        "bottom_talisman_y": y0 + 3 * row_h + row_h // 2,
        "opacity_x": 1090,
        "opacity_y": 456,
    }


def illustrator_frame(progress: float, final: bool = False) -> Image.Image:
    state = illustrator_state(progress, final=final)
    im, draw = illustrator_shell(opacity=int(state["opacity"]), selected=bool(state["selected"]))
    layer = draw_layers(draw, state)
    source_x, source_y = 510, 392
    package = fit_package(174)
    package_w, package_h = package.size
    object_x, object_y = source_x - package_w // 2, source_y - package_h // 2

    if bool(state["placed"]) and int(state["package_alpha"]) > 0:
        visible_package = faded_package(package, int(state["package_alpha"]))
        im.paste(visible_package, (object_x, object_y), visible_package)
        if bool(state["selected"]):
            draw_dashed_box(draw, (object_x - 7, object_y - 7,
                                   object_x + package_w + 7, object_y + package_h + 7))

    p = max(0.0, min(1.0, progress))
    if p < 0.14:
        amount = p / 0.14
        cursor_x = lerp(730, source_x, amount)
        cursor_y = lerp(230, source_y, amount)
        pressed = False
    elif p < 0.26:
        cursor_x, cursor_y, pressed = source_x, source_y, True
    elif p < 0.70:
        amount = (p - 0.26) / 0.44
        cursor_x = lerp(source_x, layer["row_x"], amount)
        cursor_y = lerp(source_y, layer["top_talisman_y"], amount)
        if p >= 0.32:
            cursor_y = layer["talisman_y"]
        pressed = True
    elif p < 0.82:
        amount = (p - 0.70) / 0.12
        cursor_x = lerp(layer["row_x"], layer["opacity_x"], amount)
        cursor_y = lerp(layer["talisman_y"], layer["opacity_y"], amount)
        pressed = False
    else:
        cursor_x, cursor_y, pressed = layer["opacity_x"], layer["opacity_y"], False

    draw_mouse(draw, cursor_x, cursor_y, pressed=pressed)
    if final:
        text(draw, (73, 656), "Layers: bottom  ·  Opacity 0%  ·  eye on  ·  locked", 13,
             "#6ed19d", bold=True)
    elif p < 0.20:
        text(draw, (73, 656), "1  Place the official green package on the artboard", 13, "#d0d0d0")
    elif p < 0.32:
        text(draw, (73, 656), "2  Select the placed image — keep it on the artboard", 13,
             "#80bfff", bold=True)
    elif p < 0.70:
        text(draw, (73, 656), "3  Drag the selected layer row to the bottom of Layers", 13,
             "#80bfff", bold=True)
    else:
        text(draw, (73, 656), "4  Set Opacity to 0% — keep the eye on", 13, "#dcdcaa", bold=True)
    return im


# The code demo follows the event-triggered, source-embedded ASCII-art approach
# in the referenced Vite plug-in. It never reads PACKAGE.
ASCII_ART = (
    "                               ███████████",
    "                           ████████████████████",
    "                        ████████████████████████████████████▓",
    "                      ██████████████████████████████▓▒░░░▓▓▓██",
    "                    ██████████████████████████████████▓▓▓▓▓▓▓▓▓",
    "        ████       ████████████████████████████████████▓▓▓▓▓▓▓█",
    "     ████████     ██████████████████████████████████████▓▓█▓▓▓█▓",
    "  ████████████   ██████████████████████████████████████████████▓",
    "  █████████████████████████████████████████████████████████████▓",
    "  ████████████████▓▒░░▒▓███▓▒░░░▒▒▒▓██████████████████████ ▓██▓",
    "   ██████████████▓░░░░░▒██▓▒███▒░░░░░░▒████████████████████",
    "    █████████████▒░░▒▒░▒█▓░░▒░░░░░░░░▓▓▒░▒█████████████████",
    "    █████████████▓░░░░▒▓▓░░▓█▓░░░░░░░░▓██░░▒███████████████",
    "     ████████████▓▒▒▒░░░░░░▒▓░░░░░░▒██▒░░░░░███████████████",
    "   ▒░░▒███████████▓░░░░░▓█░░░░░░▒░░▓█▓░░░░░█████████████████",
    " ░░░░░░░▓█████████▒░░░░▒███▒░░░░░░░░░░░░░░██▓▒░░░░▒█████████",
    " ▒░░░░░░░▓██▓░░▒▓█▒░░░░██▓░░░▒▒▒▒▒▒▓█▓▒░░░░▒░░░▒░░░▓█████████      ███",
    "░░░ ░░░░░░░░░░░░▓█▒░░░░███▒░▒▓░░░▓███▒░░░░░░░▒▒▒░░▒▓███████████████████",
    " ░░░ ░░░░    ░░▓██▓░░░░▒▒▒▒▓▓█▓▒▒▓██▒░░░░░░░░░░░░▒██████████████████████",
    "    ░░   ░░  ░▒████▓░░░▒▒▒▒▒▒▒▒▒▒▓▓▒░░░░░░▒▓▓▓▓█████████████████████████",
    "    ▒░░░░░ ░░░▓▓▓███▓░░░▒▒▒▒▒▒▒▒▒▒░░░░░░░▓████▓▓▓████████████████████████",
    "      ▒░░░░░▒▓▓▓▓▓▓▓█▓▒░░░▒▒▒▒▒▒░░░░░░░▒▓████▓░░░▒██████████████████████",
    "       ██▓▒▓▓▓▓▓▓▓▓▓▓░░░▒▒░░░░░░░░░░▒▓███████▒░ ░▒████▓▒░▒▓██████████",
    "       ███▓▓▓▓▓▓▓▓▓▒░░░▒▒░░▓▒▒▒▒▒▒▒▓▓▓██████▓░  ░░░░░░░░░░░▓██████",
    "         ▓█████▓▓█▓░░░░░▓▒▒▒░░░░░▒▓▓▓▓▓▓▓▓▓▓░░░░░░░ ░░░░░░░▒▓",
    "                  █▓▓▓▓▓▓▓▓▓░░░░░░▓▓▓▓▓▓▓▓▓▓░░ ░░░░░ ░░░░░▒░",
    "                  █▓▓▓▓▓▓▓▓█▓▒░░▒▓▓█▓▓▓▓▓▓▓▓▒░░░░░ ░░░░░░▒░",
    "                 ██▓▓▓▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓██▓▓▓▓█▓██▒▒▒░░",
    "                 █▓▓▓▓▓▓▓▓▓█▓▓▓▓▓▓▓▓▓▓▓▓▓█████",
    "                 ██▓▓▓▓▓█████▓▓▓▓▓▓▓▓██▓",
    "                 ▓▓█▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓█",
    "                   ▓▓▓▓▓▓▓▓▓▓█▓▓▓▓▓▓▓▓▓▓█",
    "                    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
    "          ▓▓▓▓▓▓▓    █▓▓▓▓██▓   ▓█▓▓▓▓▓▓▓▓▓     ▓▓▓▓▓▓▓▓",
    "       ▓▓▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▓▓      ▓▓▓▓▓▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▓▓",
    "     ▓▓▒▒▒▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓         ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▒▒▒▒▓▓",
    "   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓         ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
    "    ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓          ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓",
    "        ▓▓▓▓██▓▓▓▓▓    ▓▓                       ▓▓▓▓▓█▓▓▓▓▓",
)


def draw_ascii_preview(draw: ImageDraw.ImageDraw, x: int, y: int, visible: int | None = None) -> None:
    lines = ASCII_ART if visible is None else ASCII_ART[:visible]
    for row, line in enumerate(lines):
        text(draw, (x, y + row * 7), line, 6, "#55c93d", bold=True, mono=True)


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
    text(draw, (934, 73), "TERMINAL", 11, "#e0e0e0", bold=True)
    text(draw, (1011, 73), "ASCII OUTPUT", 11, "#8d8d8d")
    draw.line((913, 96, W, 96), fill="#424242")
    draw.line((913, 97, 913, 686), fill="#515151", width=2)
    return im, draw


CODE_LINES = [
    ('GREEN = "\\033[32m"', "#ce9178"),
    ('RESET = "\\033[0m"', "#ce9178"),
    ("", "#d4d4d4"),
    ('ASCII_ART = r"""', "#569cd6"),
] + [(line, "#55c93d") for line in ASCII_ART] + [
    ('"""', "#569cd6"),
    ("", "#d4d4d4"),
    ("def bless(event, on_build=False, on_dev=False):", "#569cd6"),
    ('    if event == "build" and not on_build:', "#c586c0"),
    ('        return ""', "#ce9178"),
    ('    if event == "dev" and not on_dev:', "#c586c0"),
    ('        return ""', "#ce9178"),
    ("    print(GREEN + ASCII_ART + RESET)", "#dcdcaa"),
]


def code_frame(progress: float, final: bool = False) -> Image.Image:
    im, draw = code_shell()
    editor_x, editor_y = 300, 104
    line_height = 9
    visible = len(CODE_LINES) if final else max(3, min(len(CODE_LINES), int(3 + progress * (len(CODE_LINES) - 3))))
    for index, (line, colour) in enumerate(CODE_LINES[:visible]):
        y = editor_y + index * line_height
        text(draw, (editor_x, y), f"{index + 1:>2}", 8, "#606a73", mono=True)
        text(draw, (editor_x + 28, y), line, 8, colour, mono=True)

    # A blinking caret communicates typing; it replaces the old fake drag arrow.
    if not final:
        last_line = CODE_LINES[visible - 1][0]
        caret_x = editor_x + 28 + len(last_line) * 4.8
        draw.rectangle((caret_x, editor_y + (visible - 1) * line_height, caret_x + 2,
                        editor_y + (visible - 1) * line_height + 10), fill="#aeafad")

    # The preview appears row by row only after the lifecycle hook exists.
    preview_x, preview_y = 922, 111
    if final:
        draw_ascii_preview(draw, preview_x, preview_y)
        text(draw, (924, 410), "Printed from source code", 12, "#6ed19d", bold=True)
        text(draw, (924, 431), "No image asset loaded", 10, "#a6a6a6")
        text(draw, (924, 449), "ANSI green + build hook", 10, "#a6a6a6")
    elif visible > 4:
        rows = min(len(ASCII_ART), visible - 4)
        draw_ascii_preview(draw, preview_x, preview_y, visible=rows)
        text(draw, (924, 410), "Executing build hook…", 11, "#dcdcaa")
    else:
        text(draw, (924, 207), "Waiting for event…", 12, "#777777")
        text(draw, (924, 235), "The talisman is stored", 10, "#777777")
        text(draw, (924, 252), "inside the source code.", 10, "#777777")

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
