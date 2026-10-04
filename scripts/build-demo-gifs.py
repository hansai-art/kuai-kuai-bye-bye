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


def ease_out_quart(amount: float) -> float:
    amount = max(0.0, min(1.0, amount))
    return 1.0 - (1.0 - amount) ** 4


def smoothstep(amount: float) -> float:
    amount = max(0.0, min(1.0, amount))
    return amount * amount * (3.0 - 2.0 * amount)


def draw_mouse(
    draw: ImageDraw.ImageDraw,
    x: int,
    y: int,
    pressed: bool = False,
    click_strength: float = 1.0,
) -> None:
    """Draw a small desktop pointer with restrained press feedback."""
    pointer = [(x, y), (x + 3, y + 27), (x + 11, y + 20),
               (x + 22, y + 37), (x + 28, y + 33), (x + 17, y + 17),
               (x + 28, y + 14)]
    shadow = [(px + 3, py + 3) for px, py in pointer]
    draw.polygon(shadow, fill="#151515")
    draw.polygon(pointer, fill="#ffffff", outline="#121212")
    draw.line((x + 5, y + 5, x + 8, y + 22), fill="#b8b8b8", width=1)
    if pressed:
        strength = max(0.0, min(1.0, click_strength))
        radius = int(round(12 + 7 * strength))
        center_x, center_y = x + 3, y + 3
        draw.ellipse((center_x - radius, center_y - radius,
                      center_x + radius, center_y + radius),
                     outline="#78a7d3", width=2)
        draw.ellipse((center_x - 3, center_y - 3, center_x + 3, center_y + 3),
                     fill="#78a7d3")


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


def illustrator_shell(
    opacity: int = 100,
    selected: bool = False,
) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    """Draw a restrained Illustrator-like workspace around the demo action."""
    im = Image.new("RGB", (W, H), "#242424")
    draw = ImageDraw.Draw(im)

    # Application bar, menu bar, and Control panel follow Illustrator's
    # horizontal workspace hierarchy.  The dark surfaces are neutral charcoal,
    # with blue only reserved for selection feedback.
    draw.rectangle((0, 0, W, 28), fill="#252525")
    draw.ellipse((14, 9, 24, 19), fill="#ff5f57")
    draw.ellipse((30, 9, 40, 19), fill="#ffbd2e")
    draw.ellipse((46, 9, 56, 19), fill="#28c840")
    draw.rectangle((78, 5, 102, 25), fill="#ff9a00")
    text(draw, (83, 6), "Ai", 14, "#242424", bold=True)
    text(draw, (113, 6), "kuai-kuai.ai @ 100% (RGB/Preview)", 13, "#d8d8d8")
    text(draw, (1008, 6), "Essentials", 12, "#bdbdbd")
    text(draw, (1108, 6), "Adobe Illustrator", 12, "#8f8f8f")

    draw.rectangle((0, 28, W, 59), fill="#303030")
    for x, label in [(18, "File"), (57, "Edit"), (98, "Object"), (151, "Type"),
                     (190, "Select"), (244, "Effect"), (294, "View"),
                     (340, "Window"), (406, "Help")]:
        text(draw, (x, 37), label, 12, "#e0e0e0")

    draw.rectangle((0, 59, W, 100), fill="#3a3a3a")
    text(draw, (15, 72), "Selection", 11, "#a9a9a9")
    rounded(draw, (82, 66, 175, 92), 3, "#262626", "#5c5c5c")
    text(draw, (92, 73), "Image" if selected else "No Selection", 11, "#e0e0e0")
    for x, label in [(205, "X:"), (286, "Y:"), (367, "W:"), (448, "H:")]:
        text(draw, (x, 73), label, 11, "#a9a9a9")
        rounded(draw, (x + 18, 66, x + 70, 92), 3, "#262626", "#5c5c5c")
        text(draw, (x + 29, 73), "—", 11, "#e0e0e0")
    text(draw, (555, 73), "Transform", 11, "#a9a9a9")
    for x in (620, 649, 678, 707):
        rounded(draw, (x, 68, x + 23, 90), 3, "#292929", "#606060")
    # Four small vector controls, avoiding mismatched text glyphs.
    draw.line((626, 79, 637, 79), fill="#e0e0e0", width=1)
    draw.line((628, 76, 625, 79), fill="#e0e0e0", width=1)
    draw.line((635, 76, 638, 79), fill="#e0e0e0", width=1)
    draw.line((655, 74, 655, 84), fill="#e0e0e0", width=1)
    draw.line((652, 77, 655, 74), fill="#e0e0e0", width=1)
    draw.line((658, 77, 655, 74), fill="#e0e0e0", width=1)
    draw.rectangle((684, 74, 695, 85), outline="#e0e0e0", width=1)
    draw.line((711, 79, 725, 79), fill="#e0e0e0", width=1)
    draw.line((718, 73, 718, 85), fill="#e0e0e0", width=1)
    text(draw, (752, 73), "Opacity:", 11, "#a9a9a9")
    rounded(draw, (811, 66, 878, 92), 3, "#262626", "#5c5c5c")
    text(draw, (824, 73), f"{opacity}%" if selected else "—", 11, "#f0f0f0")

    # Main workspace.
    draw.rectangle((0, 100, W, 686), fill="#292929")
    draw.rectangle((0, 100, 55, 686), fill="#353535")
    draw.rectangle((55, 100, 900, 686), fill="#282828")

    # Tools panel: deliberately drawn as a single consistent line-icon set.
    draw.rectangle((7, 109, 48, 143), fill="#4a4a4a")
    draw.line((17, 119, 34, 136), fill="#efefef", width=2)
    draw.line((17, 119, 17, 130), fill="#efefef", width=2)
    draw.line((17, 119, 28, 119), fill="#efefef", width=2)
    draw.rectangle((16, 156, 35, 175), outline="#cfcfcf", width=2)
    text(draw, (19, 191), "T", 20, "#ededed", bold=True)
    draw.line((15, 236, 35, 236), fill="#d6d6d6", width=2)
    draw.line((15, 236, 23, 226), fill="#d6d6d6", width=2)
    draw.ellipse((14, 266, 35, 287), outline="#d6d6d6", width=2)
    draw.line((14, 316, 35, 316), fill="#d6d6d6", width=2)
    draw.line((18, 312, 31, 320), fill="#d6d6d6", width=2)
    draw.arc((14, 356, 34, 376), 215, 500, fill="#d6d6d6", width=2)
    draw.line((22, 363, 35, 375), fill="#d6d6d6", width=2)
    draw.line((15, 406, 34, 406), fill="#d6d6d6", width=2)
    draw.line((15, 406, 15, 425), fill="#d6d6d6", width=2)
    draw.line((34, 406, 34, 425), fill="#d6d6d6", width=2)
    draw.ellipse((17, 454, 33, 470), outline="#d6d6d6", width=2)
    draw.line((33, 469, 40, 476), fill="#d6d6d6", width=2)
    text(draw, (16, 624), "Fill", 9, "#999999")
    draw.rectangle((13, 641, 30, 658), fill="#ffffff", outline="#161616")
    draw.rectangle((23, 649, 40, 666), fill="#202020", outline="#c4c4c4")

    # Canvas and rulers.  These quiet structural cues make the mockup read as
    # a real design-tool workspace instead of a dashboard illustration.
    draw.rectangle((55, 100, 900, 122), fill="#353535")
    draw.rectangle((55, 122, 77, 686), fill="#353535")
    for x in range(88, 900, 50):
        tick = 10 if x % 100 == 88 else 6
        draw.line((x, 122, x, 122 + tick), fill="#888888", width=1)
        if x % 100 == 88:
            text(draw, (x - 4, 104), str((x - 88) // 10), 8, "#9f9f9f")
    for y in range(139, 686, 50):
        tick = 10 if y % 100 == 39 else 6
        draw.line((67, y, 67 + tick, y), fill="#888888", width=1)
        if y % 100 == 39:
            text(draw, (57, y - 4), str((y - 139) // 10), 8, "#9f9f9f")
    text(draw, (84, 108), "kuai-kuai.ai", 11, "#a6a6a6")

    # A clean typographic artboard gives the placed image a believable context
    # without inventing a noisy poster or competing with the Layers action.
    art_x1, art_y1, art_x2, art_y2 = 160, 171, 865, 649
    draw.rectangle((art_x1 - 7, art_y1 - 7, art_x2 + 7, art_y2 + 7),
                   fill="#1f1f1f", outline="#5b5b5b")
    draw.rectangle((art_x1, art_y1, art_x2, art_y2),
                   fill="#f7f6f2", outline="#d8d6d0")
    text(draw, (207, 199), "KUAI-KUAI / WORKFLOW 01", 11, "#535957", bold=True)
    draw.rectangle((793, 196, 818, 221), fill="#5c9948")
    draw.line((207, 230, 818, 230), fill="#202624", width=1)
    text(draw, (207, 254), "SAFE", 64, "#202624", bold=True)
    text(draw, (207, 324), "MODE", 64, "#202624", bold=True)
    text(draw, (211, 403), "A small ritual for stable builds.", 14, "#626864")
    draw.rectangle((705, 257, 808, 461), fill="#222a27")
    draw.rectangle((729, 281, 784, 336), fill="#5c9948")
    draw.rectangle((729, 361, 784, 416), outline="#dfe8dd", width=2)
    draw.line((729, 439, 784, 439), fill="#dfe8dd", width=2)
    draw.line((207, 540, 818, 540), fill="#202624", width=1)
    text(draw, (207, 560), "OBJECT / IMAGE / TYPE", 11, "#202624", bold=True)
    text(draw, (207, 581), "Keep the working file calm.", 12, "#626864")
    text(draw, (703, 560), "01", 11, "#202624", bold=True)
    text(draw, (748, 560), "VECTOR STUDY", 11, "#626864")

    # Right-side dock and Layers panel.
    draw.rectangle((900, 100, W, 686), fill="#343434")
    draw.line((900, 100, 900, 686), fill="#161616", width=2)
    draw.rectangle((910, 100, W, 140), fill="#2f2f2f")
    for x, label in [(918, "Properties"), (1018, "Layers"), (1110, "Libraries")]:
        text(draw, (x, 111), label, 12,
             "#e5e5e5" if label == "Layers" else "#999999",
             bold=label == "Layers")
    draw.line((1016, 137, 1080, 137), fill="#d8d8d8", width=2)
    draw.rectangle((910, 140, W, 183), fill="#404040")
    text(draw, (922, 151), "Layers", 15, "#eeeeee", bold=True)
    draw.line((1197, 151, 1210, 151), fill="#cccccc", width=2)
    draw.line((1197, 156, 1210, 156), fill="#cccccc", width=2)
    draw.line((1197, 161, 1210, 161), fill="#cccccc", width=2)
    draw.rectangle((1230, 149, 1242, 161), outline="#cccccc", width=1)
    draw.line((1236, 145, 1236, 165), fill="#cccccc", width=1)
    draw.line((1227, 155, 1245, 155), fill="#cccccc", width=1)

    # Persistent status bar at the bottom of the application frame.
    draw.rectangle((0, 686, W, H), fill="#242424")
    draw.line((55, 686, 55, H), fill="#111111", width=1)
    text(draw, (70, 697), "Selection Tool", 11, "#bcbcbc")
    text(draw, (202, 697), "RGB/Preview", 11, "#8e8e8e")
    text(draw, (1105, 697), "100%", 11, "#d0d0d0")
    draw.line((1151, 693, 1151, 705), fill="#666666", width=1)
    text(draw, (1172, 697), "01 / 01", 11, "#8e8e8e")

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


def illustrator_state(progress: float, final: bool = False) -> dict[str, int | float | bool | str]:
    """Return the Illustrator actions represented by a demo frame.

    The package never travels into the right dock. The selected layer row moves
    to the bottom, then the selected object's Opacity is reduced to 0%.
    """
    p = max(0.0, min(1.0, progress))
    reorder = max(0.0, min(1.0, (p - 0.34) / 0.22))
    # Opacity is adjusted as a continuous action.  The numeric control and
    # the placed image change together, so the viewer can read 100% → 0%
    # instead of seeing an instant value swap.
    opacity_fade = max(0.0, min(1.0, (p - 0.70) / 0.20))
    if final:
        reorder = 1.0
        opacity_fade = 1.0
    opacity = int(round(100 * (1.0 - smoothstep(opacity_fade))))
    if final:
        opacity = 0
    phase = "place"
    if p >= 0.22:
        phase = "drag-layer"
    if p >= 0.62:
        phase = "set-opacity"
    if p >= 0.90:
        phase = "lock-layer"
    if final:
        phase = "complete"
    return {
        "reorder": reorder,
        "opacity": opacity,
        "placed": final or p >= 0.06,
        "selected": final or p >= 0.13,
        "locked": final or p >= 0.98,
        "layer_dragging": not final and 0.34 <= p < 0.56,
        "drop_feedback": not final and 0.56 <= p < 0.62,
        "opacity_adjusting": not final and 0.70 <= p < 0.90,
        "opacity_focus": not final and 0.68 <= p < 0.90,
        "opacity_entry": final or p >= 0.70,
        "lock_adjusting": not final and 0.95 <= p < 0.99,
        "package_alpha": opacity,
        "phase": phase,
    }


def draw_layers(draw: ImageDraw.ImageDraw, state: dict[str, int | bool | str]) -> dict[str, int]:
    """Draw a Layers panel whose row order changes, not the package position."""
    panel_x = 910
    panel_right = 1279
    y0 = 184
    row_h = 49
    reorder = float(state["reorder"])
    talisman_y = y0

    def render_row(name: str, y: int, selected: bool = False, dragged: bool = False) -> None:
        is_talisman = name == TALISMAN_LAYER
        row_fill = "#4b6075" if selected else "#363636"
        if dragged:
            draw.rectangle((panel_x + 5, y + 5, panel_right - 2, y + row_h + 3),
                           fill="#1f1f1f")
        draw.rectangle((panel_x, y, panel_right, y + row_h), fill=row_fill)
        draw.line((panel_x, y + row_h, panel_right, y + row_h),
                  fill="#494949", width=1)
        if selected:
            draw.rectangle((panel_x, y, panel_x + 3, y + row_h), fill="#f0a23a")
        if dragged:
            draw.rectangle((panel_x + 1, y + 1, panel_right - 1, y + row_h - 1),
                           outline="#77a9d6", width=2)
        if not is_talisman:
            draw.polygon([(921, y + 21), (926, y + 25), (921, y + 29)],
                         fill="#bdbdbd")
        draw_eye(draw, 939, y + 13, visible=True)
        draw_lock(draw, 963, y + 12, locked=is_talisman and bool(state["locked"]))
        # The package keeps its green thumbnail even after Opacity reaches 0%.
        if is_talisman:
            draw.rectangle((990, y + 13, 1016, y + 35), fill="#5cab45", outline="#c7d8c0")
            draw.rectangle((995, y + 17, 1011, y + 31), fill="#d7e6c4")
        else:
            draw.rectangle((990, y + 13, 1016, y + 35), fill="#777777", outline="#a8a8a8")
            draw.line((994, y + 30, 1012, y + 18), fill="#d4d4d4", width=1)
        display_name = "KUAI-KUAI / TALISMAN" if is_talisman else name
        text(draw, (1028, y + 15), display_name, 12, "#ffffff" if selected else "#d4d4d4",
             bold=selected)
        if selected:
            draw.ellipse((1243, y + 18, 1254, y + 29), outline="#f2a13a", width=2)
        else:
            draw.ellipse((1244, y + 19, 1253, y + 28), outline="#a7a7a7")

    if bool(state["layer_dragging"]):
        # During a real Layers-panel drag, the selected row floats over the
        # other rows while the blue insertion line marks the final position.
        for index, name in enumerate(ARTWORK_LAYERS):
            render_row(name, y0 + index * row_h)
        talisman_y = int(round(y0 + reorder * 3 * row_h))
        render_row(TALISMAN_LAYER, talisman_y, selected=True, dragged=True)
        drop_y = y0 + 3 * row_h
        draw.line((panel_x + 4, drop_y - 4, panel_right - 4, drop_y - 4),
                  fill="#77a9d6", width=2)
    else:
        rows = ((TALISMAN_LAYER,) + ARTWORK_LAYERS
                if reorder < 1.0 else ARTWORK_LAYERS + (TALISMAN_LAYER,))
        talisman_y = y0 + (3 if reorder >= 1.0 else 0) * row_h
        for index, name in enumerate(rows):
            render_row(name, y0 + index * row_h,
                       selected=name == TALISMAN_LAYER and bool(state["selected"]))
        if bool(state["drop_feedback"]):
            drop_y = y0 + 3 * row_h
            draw.line((panel_x + 4, drop_y - 4, panel_right - 4, drop_y - 4),
                      fill="#77a9d6", width=2)

    text(draw, (922, 397), "Appearance", 12, "#bcbcbc")
    draw.line((panel_x, 416, 1280, 416), fill="#505050")
    text(draw, (934, 435), "Opacity", 12, "#d0d0d0")
    field_outline = "#73a8d6" if bool(state["opacity_focus"]) else "#777777"
    rounded(draw, (1018, 426, 1180, 462), 3, "#262626", field_outline,
            width=2 if bool(state["opacity_focus"]) else 1)
    value = f"{int(state['opacity'])}%"
    if bool(state["opacity_focus"]):
        highlight_width = 10 + len(value) * 8
        draw.rectangle((1038, 432, 1038 + highlight_width, 455), fill="#40617d")
    text(draw, (1040, 435), value, 13, "#f0f0f0",
         bold=bool(state["opacity_adjusting"]))
    draw.line((1193, 434, 1193, 454), fill="#9e9e9e", width=1)
    draw.line((1190, 437, 1193, 434), fill="#9e9e9e", width=1)
    draw.line((1196, 437, 1193, 434), fill="#9e9e9e", width=1)
    draw.line((1190, 451, 1193, 454), fill="#9e9e9e", width=1)
    draw.line((1196, 451, 1193, 454), fill="#9e9e9e", width=1)
    text(draw, (934, 478), "Blending Mode", 12, "#d0d0d0")
    rounded(draw, (1018, 469, 1180, 501), 3, "#262626", "#777777")
    text(draw, (1034, 477), "Normal", 12, "#d0d0d0")
    text(draw, (922, 529), "Transparency", 12, "#bcbcbc")
    draw.line((panel_x, 548, 1280, 548), fill="#505050")
    text(draw, (934, 567), "Selected object", 11, "#969696")
    text(draw, (1032, 567), "Image", 11, "#d2d2d2")

    return {
        "row_x": 1100,
        "talisman_y": talisman_y + row_h // 2,
        "top_talisman_y": y0 + row_h // 2,
        "bottom_talisman_y": y0 + 3 * row_h + row_h // 2,
        "opacity_x": 1098,
        "opacity_y": 444,
        "opacity_drag_end_x": 1040,
        "lock_x": 971,
        "lock_y": y0 + 3 * row_h + row_h // 2,
    }


def illustrator_frame(progress: float, final: bool = False) -> Image.Image:
    state = illustrator_state(progress, final=final)
    im, draw = illustrator_shell(opacity=int(state["opacity"]), selected=bool(state["selected"]))
    layer = draw_layers(draw, state)
    source_x, source_y = 510, 405
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
    if p < 0.12:
        amount = ease_out_quart(p / 0.12)
        cursor_x = lerp(760, source_x, amount)
        cursor_y = lerp(222, source_y, amount)
        pressed = False
        click_strength = 0.0
    elif p < 0.22:
        cursor_x, cursor_y = source_x, source_y
        pressed = True
        click_strength = smoothstep((p - 0.12) / 0.10)
    elif p < 0.36:
        amount = smoothstep((p - 0.22) / 0.14)
        cursor_x = lerp(source_x, layer["row_x"], amount)
        cursor_y = lerp(source_y, layer["top_talisman_y"], amount)
        pressed = False
        click_strength = 0.0
    elif p < 0.56:
        amount = smoothstep((p - 0.36) / 0.25)
        cursor_x = layer["row_x"]
        cursor_y = layer["talisman_y"]
        pressed = True
        click_strength = 1.0 - abs(amount - 0.5) * 0.18
    elif p < 0.62:
        cursor_x, cursor_y = layer["row_x"], layer["bottom_talisman_y"]
        pressed = p < 0.585
        click_strength = 1.0
    elif p < 0.68:
        amount = ease_out_quart((p - 0.62) / 0.06)
        cursor_x = lerp(layer["row_x"], layer["opacity_x"], amount)
        cursor_y = lerp(layer["bottom_talisman_y"], layer["opacity_y"], amount)
        pressed = False
        click_strength = 0.0
    elif p < 0.90:
        amount = smoothstep((p - 0.68) / 0.22)
        cursor_x = lerp(layer["opacity_x"], layer["opacity_drag_end_x"], amount)
        cursor_y = layer["opacity_y"]
        pressed = True
        click_strength = 1.0
    elif p < 0.95:
        amount = smoothstep((p - 0.90) / 0.05)
        cursor_x = lerp(layer["opacity_x"], layer["lock_x"], amount)
        cursor_y = lerp(layer["opacity_y"], layer["lock_y"], amount)
        pressed = False
        click_strength = 0.0
    elif p < 1.0:
        cursor_x, cursor_y = layer["lock_x"], layer["lock_y"]
        pressed = p < 0.975
        click_strength = 1.0
    else:
        cursor_x, cursor_y, pressed, click_strength = layer["lock_x"], layer["lock_y"], False, 0.0

    draw_mouse(draw, cursor_x, cursor_y, pressed=pressed, click_strength=click_strength)
    if final:
        text(draw, (73, 661), "Layers: bottom  ·  Opacity 0%  ·  eye on  ·  locked", 13,
             "#6ed19d", bold=True)
    elif p < 0.12:
        text(draw, (73, 661), "1  Move to the placed package", 13, "#d0d0d0")
    elif p < 0.22:
        text(draw, (73, 661), "2  Click the package to select its layer", 13,
             "#80bfff", bold=True)
    elif p < 0.36:
        text(draw, (73, 661), "3  Follow the selected row in Layers", 13,
             "#80bfff", bold=True)
    elif p < 0.56:
        text(draw, (73, 661), "4  Hold and drag the layer row to the bottom", 13,
             "#80bfff", bold=True)
    elif p < 0.62:
        text(draw, (73, 661), "5  Release at the bottom; the package stays on the artboard", 13,
             "#d0d0d0")
    elif p < 0.68:
        text(draw, (73, 661), "6  Select Opacity", 13,
             "#dcdcaa", bold=True)
    elif p < 0.90:
        text(draw, (73, 661), "6  Drag Opacity 100% → 0% — keep the eye on", 13,
             "#dcdcaa", bold=True)
    elif p < 0.95:
        text(draw, (73, 661), "7  Keep the eye on; move to the lock column", 13,
             "#d0d0d0")
    else:
        text(draw, (73, 661), "8  Lock the bottom layer", 13,
             "#6ed19d" if state["locked"] else "#d0d0d0", bold=bool(state["locked"]))
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


def save_demo(
    name: str,
    maker,
    motion_count: int = 19,
    motion_duration: int = 90,
    final_duration: int = 1200,
) -> None:
    # More hold frames make the operation readable on GitHub while preserving
    # the pointer movement and the row-by-row code rendering.
    motion = [maker(i / (motion_count - 1)) for i in range(motion_count)]
    hold = [maker(1.0, final=True) for _ in range(9)]
    frames = motion + hold
    gif = DOCS / f"{name}.gif"
    png = DOCS / f"{name}.png"
    frames[-1].save(png, optimize=True)
    frames[0].save(gif, save_all=True, append_images=frames[1:],
                   duration=[motion_duration] * len(motion) + [motion_duration] * 8 + [final_duration],
                   loop=0, optimize=False)


def main() -> None:
    DOCS.mkdir(parents=True, exist_ok=True)
    save_demo("demo-illustrator-kuai-kuai", illustrator_frame,
              motion_count=45, motion_duration=145, final_duration=2400)
    save_demo("demo-code-kuai-kuai", code_frame)
    print("created realistic Illustrator and code-drawn demos")


if __name__ == "__main__":
    main()
