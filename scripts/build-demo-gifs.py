#!/usr/bin/env python3
"""Build the README demos: the Illustrator layer ritual and the code-drawn Kuai Kuai.

Requires Pillow; ffmpeg (optional) gives a much smaller Illustrator GIF.
Fonts: Inter and Noto Sans CJK TC for the Illustrator demo, DejaVu for the code demo.
"""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont


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


# ---------------------------------------------------------------------------
# Illustrator demo
#
# Rendered at 2x and downsampled for clean anti-aliasing, 20 fps, with a
# single timeline (in seconds) driving the UI state, the cursor and the
# captions.  The four captions match the four steps written in README:
# place → drag the Layers row to the bottom → Opacity 0% (eye stays on) → lock.
# ---------------------------------------------------------------------------

S = 2                      # supersampling factor
FPS = 20
ILLUSTRATOR_SECONDS = 10.6  # motion part; the final hold is added on export

FONT_CANDIDATES = {
    "ui": ["/usr/share/fonts/opentype/inter/Inter-Regular.otf", REGULAR],
    "ui_m": ["/usr/share/fonts/opentype/inter/Inter-Medium.otf", REGULAR],
    "ui_sb": ["/usr/share/fonts/opentype/inter/Inter-SemiBold.otf", BOLD],
    "ui_b": ["/usr/share/fonts/opentype/inter/Inter-Bold.otf", BOLD],
    "display": ["/usr/share/fonts/opentype/inter/InterDisplay-Black.otf", BOLD],
    "cjk": [("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 3)],
    "cjk_m": [("/usr/share/fonts/opentype/noto/NotoSansCJK-Medium.ttc", 3),
              ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", 3)],
    "cjk_b": [("/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc", 3)],
}
_FONT_CACHE: dict[tuple[str, float], ImageFont.FreeTypeFont] = {}


def ui_font(kind: str, size: float) -> ImageFont.FreeTypeFont:
    key = (kind, size)
    if key not in _FONT_CACHE:
        for candidate in FONT_CANDIDATES[kind]:
            path, index = candidate if isinstance(candidate, tuple) else (candidate, 0)
            if Path(path).exists():
                _FONT_CACHE[key] = ImageFont.truetype(path, int(round(size * S)), index=index)
                break
        else:
            raise SystemExit(f"Missing font for {kind}: install Inter and Noto Sans CJK TC")
    return _FONT_CACHE[key]


def has_cjk(value: str) -> bool:
    return any(ord(ch) > 0x2E7F for ch in value)


def pick_font(value: str, size: float, weight: str = "") -> ImageFont.FreeTypeFont:
    if has_cjk(value):
        return ui_font({"": "cjk", "m": "cjk_m", "sb": "cjk_m", "b": "cjk_b"}[weight], size)
    return ui_font({"": "ui", "m": "ui_m", "sb": "ui_sb", "b": "ui_b"}[weight], size)


def sc(*values: float) -> tuple[int, ...]:
    return tuple(int(round(v * S)) for v in values)


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def ease_in_out(amount: float) -> float:
    amount = clamp(amount)
    return 4 * amount ** 3 if amount < 0.5 else 1 - (-2 * amount + 2) ** 3 / 2


def ease_out_back(amount: float, overshoot: float = 1.6) -> float:
    amount = clamp(amount)
    c3 = overshoot + 1
    return 1 + c3 * (amount - 1) ** 3 + overshoot * (amount - 1) ** 2


def span(t: float, start: float, end: float) -> float:
    return clamp((t - start) / (end - start))


def hex_rgba(colour: str, alpha: float = 1.0) -> tuple[int, int, int, int]:
    colour = colour.lstrip("#")
    return (int(colour[0:2], 16), int(colour[2:4], 16), int(colour[4:6], 16),
            int(round(255 * clamp(alpha))))


class Pen:
    """ImageDraw wrapper that takes 1x coordinates and paints at S x."""

    def __init__(self, image: Image.Image):
        self.image = image
        self.draw = ImageDraw.Draw(image)

    def rect(self, box, fill=None, outline=None, width=1):
        self.draw.rectangle(sc(*box), fill=fill, outline=outline,
                            width=max(1, int(round(width * S))))

    def rrect(self, box, radius, fill=None, outline=None, width=1):
        self.draw.rounded_rectangle(sc(*box), radius=int(radius * S), fill=fill,
                                    outline=outline, width=max(1, int(round(width * S))))

    def line(self, points, fill, width=1):
        flat = [v for point in points for v in point]
        self.draw.line(sc(*flat), fill=fill, width=max(1, int(round(width * S))),
                       joint="curve")

    def ellipse(self, box, fill=None, outline=None, width=1):
        self.draw.ellipse(sc(*box), fill=fill, outline=outline,
                          width=max(1, int(round(width * S))))

    def circle(self, cx, cy, r, **kw):
        self.ellipse((cx - r, cy - r, cx + r, cy + r), **kw)

    def poly(self, points, fill=None, outline=None, width=1):
        self.draw.polygon([sc(x, y) for x, y in points], fill=fill, outline=outline,
                          width=max(1, int(round(width * S))))

    def text(self, xy, value, size, fill, weight="", font=None, anchor="la"):
        self.draw.text(sc(*xy), value, font=font or pick_font(value, size, weight),
                       fill=fill, anchor=anchor)

    def width(self, value, size, weight="", font=None):
        return self.draw.textlength(value, font=font or pick_font(value, size, weight)) / S


def new_layer() -> tuple[Image.Image, Pen]:
    layer = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    return layer, Pen(layer)


def soft_shadow(base: Image.Image, box, radius: float, blur: float, alpha: float,
                offset: tuple[float, float] = (0, 4)) -> None:
    """Blurred drop shadow drawn into a local patch (cheap at 2x)."""
    pad = blur * 3
    x1, y1, x2, y2 = box
    x1, y1, x2, y2 = x1 + offset[0], y1 + offset[1], x2 + offset[0], y2 + offset[1]
    px, py = int((x1 - pad) * S), int((y1 - pad) * S)
    patch = Image.new("RGBA", (int((x2 - x1 + 2 * pad) * S), int((y2 - y1 + 2 * pad) * S)),
                      (0, 0, 0, 0))
    ImageDraw.Draw(patch).rounded_rectangle(
        (int(pad * S), int(pad * S), int((x2 - x1 + pad) * S), int((y2 - y1 + pad) * S)),
        radius=int(radius * S), fill=(0, 0, 0, int(255 * alpha)))
    patch = patch.filter(ImageFilter.GaussianBlur(blur * S))
    base.alpha_composite(patch, (max(0, px), max(0, py)),
                         (max(0, -px), max(0, -py)))


# ---- Layout constants (1x) -------------------------------------------------

DOC_NAME = "提案_v18_最終版_這次真的最終.ai @ 66% (RGB/預覽)"
PASTE = (44, 92, 900, 720)
ARTBOARD = (172, 128, 772, 548)
DOCK_X = 900
ROW_Y0, ROW_H = 132, 42
OPACITY_FIELD = (1012, 476, 1112, 502)
OPACITY_CHEVRON = (1112, 476, 1136, 502)
SLIDER = (1000, 508, 1188, 550)
SLIDER_TRACK = (1018, 1170)
SLIDER_Y = 532
BAG_CENTER = (432, 332)
BAG_SIZE = 206
CAPTION_CENTER = ((PASTE[0] + PASTE[2]) / 2, 668)

GREEN = "#2fbf5b"
TALISMAN_NAME = "__乖乖拜拜_請勿刪除__"
LAYERS = [  # name, layer colour (Illustrator selection colour)
    ("Type", "#4f8cff"),
    ("Illustration", "#ff5a5a"),
    ("Layout", "#b47cff"),
]

# Kept for the unit test and older callers.
TALISMAN_LAYER = TALISMAN_NAME
ARTWORK_LAYERS = tuple(name for name, _ in LAYERS)

# ---- Timeline (seconds) ----------------------------------------------------

T_PLACE = (0.9, 1.5)        # bag drops onto the artboard, row appears in Layers
T_PRESS_ROW = 2.35
T_DRAG = (2.5, 4.0)         # Layers row travels to the bottom
T_DROP = (4.0, 4.3)
T_POPUP = (5.05, 5.25)      # Opacity slider pop-up opens
T_SCRUB = (5.6, 7.1)        # 100% → 0%
T_POPUP_CLOSE = (7.2, 7.35)
T_LOCK = 8.05
T_DONE = 8.5

CAPTIONS = [
    (0.15, 1, "置入乖乖，留在畫板上"),
    (1.75, 2, "把圖層列拖到 Layers 最底層"),
    (4.45, 3, "Opacity 拉到 0%，眼睛保持開啟"),
    (7.45, 4, "鎖定圖層"),
    (T_DONE, 0, "乖乖已安放｜最底層・0%・眼睛開・已鎖定"),
]

CURSOR_KEYS = [  # time, x, y   (positions are the arrow tip)
    (0.0, 780, 640),
    (0.25, 780, 640),
    (0.85, BAG_CENTER[0] + 24, BAG_CENTER[1] + 30),
    (1.7, BAG_CENTER[0] + 24, BAG_CENTER[1] + 30),
    (2.3, 1062, ROW_Y0 + ROW_H / 2 + 2),
    (T_DRAG[0], 1062, ROW_Y0 + ROW_H / 2 + 2),
    (T_DRAG[1], 1062, ROW_Y0 + 3 * ROW_H + ROW_H / 2 + 2),
    (4.4, 1062, ROW_Y0 + 3 * ROW_H + ROW_H / 2 + 2),
    (5.0, 1124, 489),
    (5.2, 1124, 489),
    (5.5, SLIDER_TRACK[1], SLIDER_Y + 2),
    (T_SCRUB[0], SLIDER_TRACK[1], SLIDER_Y + 2),
    (T_SCRUB[1], SLIDER_TRACK[0], SLIDER_Y + 2),
    (7.4, SLIDER_TRACK[0], SLIDER_Y + 2),
    (7.95, 946, ROW_Y0 + 3 * ROW_H + ROW_H / 2 + 1),
    (8.6, 946, ROW_Y0 + 3 * ROW_H + ROW_H / 2 + 1),
    (9.4, 1010, 640),
    (ILLUSTRATOR_SECONDS, 1010, 640),
]
PRESSES = [(0.88, 1.05), (T_PRESS_ROW, T_DROP[0] + 0.05), (5.0, 5.12),
           (T_SCRUB[0] - 0.08, T_SCRUB[1] + 0.05), (7.98, 8.1)]
# Scrubbing and row dragging move linearly with the hand; other moves ease.
LINEAR_SEGMENTS = {(T_DRAG[0], T_DRAG[1]), (T_SCRUB[0], T_SCRUB[1])}


def cursor_at(t: float) -> tuple[float, float, bool, float]:
    for (t0, x0, y0), (t1, x1, y1) in zip(CURSOR_KEYS, CURSOR_KEYS[1:]):
        if t0 <= t <= t1:
            a = span(t, t0, t1)
            if (t0, t1) in LINEAR_SEGMENTS:
                a = ease_in_out(a) * 0.35 + a * 0.65
                arc = 0.0
            else:
                a = ease_in_out(a)
                arc = min(40.0, ((x1 - x0) ** 2 + (y1 - y0) ** 2) ** 0.5 * 0.08)
            x = x0 + (x1 - x0) * a
            y = y0 + (y1 - y0) * a - arc * 4 * a * (1 - a)
            break
    else:
        _, x, y = CURSOR_KEYS[-1]
    pressed = any(start <= t < end for start, end in PRESSES)
    fade = 1.0 - span(t, 9.2, 9.6)
    return x, y, pressed, fade


def illustrator_state(progress: float, final: bool = False) -> dict[str, float | int | bool | str]:
    """Everything that changes in the Illustrator demo at a given progress."""
    t = ILLUSTRATOR_SECONDS if final else clamp(progress) * ILLUSTRATOR_SECONDS
    place = span(t, *T_PLACE)
    drag = span(t, *T_DRAG)
    reorder = 1.0 if t >= T_DRAG[1] else ease_in_out(drag) * 0.4 + drag * 0.6 if t >= T_DRAG[0] else 0.0
    scrub = span(t, *T_SCRUB)
    opacity = int(round(100 * (1 - (ease_in_out(scrub) * 0.4 + scrub * 0.6))))
    placed = t >= T_PLACE[0]
    locked = t >= T_LOCK
    phase = ("place" if t < 1.75 else "drag-layer" if t < 4.45 else
             "set-opacity" if t < 7.45 else "lock-layer" if t < T_DONE else "complete")
    return {
        "t": t,
        "placed": placed,
        "place": place,
        "selected": t >= 1.15 and not locked,
        "reorder": reorder,
        "layer_dragging": T_DRAG[0] <= t < T_DRAG[1],
        "row_lifted": T_PRESS_ROW <= t < T_DROP[1],
        "at_bottom": t >= T_DRAG[1],
        "opacity": opacity,
        "package_alpha": int(round(opacity * clamp(place * 1.6))) if placed else 0,
        "popup": span(t, *T_POPUP) * (1 - span(t, *T_POPUP_CLOSE)),
        "scrubbing": T_SCRUB[0] <= t < T_SCRUB[1],
        "locked": locked,
        "lock_pop": span(t, T_LOCK, T_LOCK + 0.3),
        "done": span(t, T_DONE, T_DONE + 0.5),
        "phase": phase,
    }


# ---- Static pieces ---------------------------------------------------------

_STATIC: dict[str, Image.Image] = {}


def draw_tool_icons(pen: Pen) -> None:
    icon = "#d7d7d7"
    pen.rrect((7, 100, 37, 130), 5, fill="#4a4a4a")
    pen.poly([(16, 106), (16, 125), (21, 120), (25, 128), (28, 126), (24, 119), (31, 118)],
             fill="#f2f2f2")
    pen.poly([(16, 140), (16, 159), (21, 154), (25, 162), (28, 160), (24, 153), (31, 152)],
             outline=icon, width=1.3)
    pen.line([(13, 186), (22, 172), (31, 186)], icon, 1.6)              # pen
    pen.circle(22, 183, 2.2, fill=icon)
    pen.text((22, 214), "T", 18, icon, "m", anchor="mm")
    pen.rect((13, 238, 31, 256), outline=icon, width=1.6)                # rectangle
    pen.line([(13, 284), (31, 270)], icon, 1.6)                           # brush
    pen.circle(15, 283, 3, fill=icon)
    pen.rrect((13, 302, 31, 318), 3, outline=icon, width=1.6)           # eraser
    pen.line([(19, 302), (25, 318)], icon, 1.3)
    pen.poly([(14, 352), (22, 336), (30, 352)], outline=icon, width=1.6)  # shaper
    pen.circle(20, 380, 7, outline=icon, width=1.6)                     # zoom
    pen.line([(25, 385), (31, 391)], icon, 2)
    pen.rect((12, 650, 26, 664), fill="#ffffff", outline="#111111")
    pen.rect((19, 657, 33, 671), outline="#e8e8e8", width=3)


def static_shell() -> Image.Image:
    if "shell" in _STATIC:
        return _STATIC["shell"]
    im = Image.new("RGBA", (W * S, H * S), hex_rgba("#262626"))
    pen = Pen(im)
    # macOS title bar
    pen.rect((0, 0, W, 30), fill="#1c1c1c")
    for x, colour in [(16, "#ff5f57"), (36, "#febc2e"), (56, "#28c840")]:
        pen.circle(x, 15, 6, fill=colour)
    pen.rrect((82, 6, 102, 24), 4, fill="#330000")
    pen.text((92, 15), "Ai", 11, "#ff9a00", "b", anchor="mm")
    pen.text((W / 2, 15), "Adobe Illustrator 2026", 12, "#a8a8a8", "m", anchor="mm")
    pen.rrect((1196, 6, 1264, 24), 9, fill="#2f6fde")
    pen.text((1230, 15), "Share", 11, "#ffffff", "sb", anchor="mm")
    # Control bar
    pen.rect((0, 30, W, 62), fill="#323232")
    pen.line([(0, 62), (W, 62)], "#1a1a1a", 1)
    # Document tab bar
    pen.rect((0, 62, W, 92), fill="#262626")
    pen.rect((44, 62, 470, 92), fill="#323232")
    pen.text((60, 77), DOC_NAME, 12, "#e6e6e6", anchor="lm")
    pen.text((452, 77), "×", 14, "#9a9a9a", anchor="mm")
    # Toolbar
    pen.rect((0, 62, 44, H), fill="#2c2c2c")
    pen.line([(44, 62), (44, H)], "#191919", 1)
    draw_tool_icons(pen)
    # Pasteboard & artboard
    pen.rect(PASTE, fill="#1e1e1e")
    pen.text((ARTBOARD[0], ARTBOARD[1] - 14), "01 - Pitch", 10, "#8a8a8a", anchor="lm")
    pen.text((60, 705), "66%", 10, "#8a8a8a", anchor="lm")
    pen.text((100, 705), "Selection", 10, "#6d6d6d", anchor="lm")
    soft_shadow(im, ARTBOARD, 0, 10, 0.55, (0, 6))
    pen.rect(ARTBOARD, fill="#fbfaf6")
    # Dock
    pen.rect((DOCK_X, 92, W, H), fill="#2f2f2f")
    pen.line([(DOCK_X, 62), (DOCK_X, H)], "#151515", 2)
    pen.rect((DOCK_X, 92, W, 122), fill="#282828")
    pen.text((918, 107), "Layers", 12, "#f0f0f0", "sb", anchor="lm")
    pen.line([(914, 121), (968, 121)], "#f0f0f0", 2)
    pen.text((988, 107), "Artboards", 12, "#8e8e8e", anchor="lm")
    pen.text((1066, 107), "Asset Export", 12, "#8e8e8e", anchor="lm")
    for y in (102, 107, 112):
        pen.line([(1252, y), (1264, y)], "#9a9a9a", 1.2)
    # Layers footer
    pen.rect((DOCK_X, 304, W, 330), fill="#2a2a2a")
    pen.line([(DOCK_X, 304), (W, 304)], "#1c1c1c", 1)
    pen.text((914, 317), "4 Layers", 11, "#9a9a9a", anchor="lm")
    pen.rect((1214, 311, 1226, 323), outline="#a8a8a8", width=1.2)
    pen.line([(1220, 314), (1220, 320)], "#a8a8a8", 1.2)
    pen.line([(1217, 317), (1223, 317)], "#a8a8a8", 1.2)
    pen.rect((1240, 312, 1252, 324), outline="#a8a8a8", width=1.2)
    pen.line([(1238, 312), (1254, 312)], "#a8a8a8", 1.2)
    # Properties panel
    pen.rect((DOCK_X, 334, W, 364), fill="#282828")
    pen.text((918, 349), "Properties", 12, "#f0f0f0", "sb", anchor="lm")
    pen.line([(914, 363), (994, 363)], "#f0f0f0", 2)
    pen.text((1014, 349), "Libraries", 12, "#8e8e8e", anchor="lm")
    pen.text((918, 384), "Appearance", 12, "#d8d8d8", "sb", anchor="lm")
    pen.text((922, 418), "Fill", 11, "#b4b4b4", anchor="lm")
    pen.rect((1012, 409, 1030, 427), fill="#ffffff", outline="#888888")
    pen.line([(1013, 426), (1029, 410)], "#e0352b", 1.6)
    pen.text((922, 452), "Stroke", 11, "#b4b4b4", anchor="lm")
    pen.rect((1012, 443, 1030, 461), outline="#cccccc", width=1.2)
    pen.line([(1013, 460), (1029, 444)], "#e0352b", 1.6)
    pen.text((922, 489), "Opacity", 11, "#b4b4b4", anchor="lm")
    pen.line([(DOCK_X + 14, 580), (W - 14, 580)], "#3d3d3d", 1)
    pen.text((918, 602), "Quick Actions", 12, "#d8d8d8", "sb", anchor="lm")
    for i, label in enumerate(("Embed", "Crop Image", "Image Trace")):
        x1 = 918 + i * 118
        pen.rrect((x1, 620, x1 + 110, 648), 5, outline="#5a5a5a", width=1)
        pen.text((x1 + 55, 634), label, 11, "#d0d0d0", anchor="mm")
    _STATIC["shell"] = im
    return im


def static_artwork() -> tuple[Image.Image, Image.Image]:
    """Return (behind, front): Layout guides sit behind, Type/Illustration in front."""
    if "art_front" in _STATIC:
        return _STATIC["art_back"], _STATIC["art_front"]
    back, pen = new_layer()
    x1, y1, x2, y2 = ARTBOARD
    pen.text((x1 + 32, y1 + 30), "CLIENT PITCH — ROUND 18", 10, "#7a7f7c", "sb", anchor="lm")
    pen.text((x2 - 32, y1 + 30), "2026.10", 10, "#7a7f7c", "sb", anchor="rm")
    pen.line([(x1 + 32, y1 + 48), (x2 - 32, y1 + 48)], "#1f2421", 1)
    pen.line([(x1 + 32, y2 - 46), (x2 - 32, y2 - 46)], "#1f2421", 1)
    pen.text((x1 + 32, y2 - 26), "提案 v18（客戶說最後一版）", 11, "#5c615e", anchor="lm")
    pen.text((x2 - 32, y2 - 26), "01 / 01", 10, "#7a7f7c", "sb", anchor="rm")

    front, pen = new_layer()
    pen.circle(612, 298, 112, fill="#ff6b3d")
    pen.circle(612, 298, 140, outline="#1f2421", width=1.2)
    display = ui_font("display", 108)
    pen.text((x1 + 30, y1 + 62), "FINAL", 108, "#1d2320", font=display)
    pen.text((x1 + 34, y1 + 196), "final_final", 40, "#1d2320", "sb")
    pen.text((x1 + 34, y1 + 262), "最終版，這次真的。", 26, "#1d2320", "b")
    _STATIC["art_back"], _STATIC["art_front"] = back, front
    return back, front


def bag_image() -> Image.Image:
    if "bag" not in _STATIC:
        bag = Image.open(PACKAGE).convert("RGBA")
        bag.thumbnail((BAG_SIZE * S, BAG_SIZE * S), Image.Resampling.LANCZOS)
        _STATIC["bag"] = bag
        thumb = Image.open(PACKAGE).convert("RGBA")
        thumb.thumbnail((26 * S, 26 * S), Image.Resampling.LANCZOS)
        _STATIC["bag_thumb"] = thumb
    return _STATIC["bag"]


def with_alpha(image: Image.Image, alpha: float) -> Image.Image:
    if alpha >= 1:
        return image
    faded = image.copy()
    faded.putalpha(faded.getchannel("A").point(lambda v: int(v * clamp(alpha))))
    return faded


# ---- Dynamic pieces ---------------------------------------------------------

def bag_box(scale: float = 1.0, dy: float = 0.0) -> tuple[float, float, float, float]:
    bag = bag_image()
    w, h = bag.width / S * scale, bag.height / S * scale
    cx, cy = BAG_CENTER
    return cx - w / 2, cy - h / 2 + dy, cx + w / 2, cy + h / 2 + dy


def paste_bag(im: Image.Image, state) -> None:
    alpha = state["package_alpha"] / 100
    if not state["placed"] or alpha <= 0:
        return
    place = state["place"]
    scale = 0.9 + 0.1 * ease_out_back(place, 1.2)
    dy = -26 * (1 - ease_out_back(place, 1.0))
    bag = bag_image()
    if scale != 1.0:
        bag = bag.resize((max(1, int(bag.width * scale)), max(1, int(bag.height * scale))),
                         Image.Resampling.LANCZOS)
    x1, y1, _, _ = bag_box(scale, dy)
    im.alpha_composite(with_alpha(bag, alpha), (int(x1 * S), int(y1 * S)))


def draw_selection(pen: Pen, state) -> None:
    if not state["selected"]:
        return
    x1, y1, x2, y2 = bag_box()
    x1, y1, x2, y2 = x1 - 2, y1 - 2, x2 + 2, y2 + 2
    pen.rect((x1, y1, x2, y2), outline=GREEN, width=1)
    # Placed (linked) images show an X across their bounds in Illustrator.
    pen.line([(x1, y1), (x2, y2)], GREEN, 0.8)
    pen.line([(x2, y1), (x1, y2)], GREEN, 0.8)
    for x in (x1, (x1 + x2) / 2, x2):
        for y in (y1, (y1 + y2) / 2, y2):
            if x == (x1 + x2) / 2 and y == (y1 + y2) / 2:
                continue
            pen.rect((x - 3, y - 3, x + 3, y + 3), fill="#ffffff", outline=GREEN, width=1)


def draw_eye(pen: Pen, cx: float, cy: float, colour: str = "#cfcfcf") -> None:
    pen.poly([(cx - 8, cy), (cx - 4, cy - 4), (cx + 4, cy - 4), (cx + 8, cy),
              (cx + 4, cy + 4), (cx - 4, cy + 4)], outline=colour, width=1.3)
    pen.circle(cx, cy, 2.2, fill=colour)


def draw_lock(pen: Pen, cx: float, cy: float, scale: float = 1.0, colour: str = "#e6e6e6") -> None:
    s = scale
    pen.draw.arc(sc(cx - 4 * s, cy - 9 * s, cx + 4 * s, cy - 1 * s), 180, 360,
                 fill=colour, width=max(1, int(1.6 * S * s)))
    pen.line([(cx - 4 * s, cy - 5 * s), (cx - 4 * s, cy - 1 * s)], colour, 1.6 * s)
    pen.line([(cx + 4 * s, cy - 5 * s), (cx + 4 * s, cy - 1 * s)], colour, 1.6 * s)
    pen.rrect((cx - 6 * s, cy - 2 * s, cx + 6 * s, cy + 7 * s), 1.5 * s, fill=colour)


def layer_thumb(pen: Pen, im: Image.Image, name: str, x: float, y: float) -> None:
    pen.rect((x, y, x + 30, y + 22), fill="#fbfaf6", outline="#5a5a5a")
    if name == TALISMAN_NAME:
        thumb = _STATIC["bag_thumb"]
        im.alpha_composite(thumb, (int((x + 15) * S - thumb.width / 2),
                                   int((y + 11) * S - thumb.height / 2)))
    elif name == "Type":
        pen.text((x + 15, y + 11), "Aa", 10, "#1d2320", "b", anchor="mm")
    elif name == "Illustration":
        pen.circle(x + 19, y + 11, 6, fill="#ff6b3d")
    else:
        pen.line([(x + 4, y + 6), (x + 26, y + 6)], "#1d2320", 0.8)
        pen.line([(x + 4, y + 17), (x + 26, y + 17)], "#1d2320", 0.8)


def draw_layer_row(im: Image.Image, pen: Pen, name: str, colour: str, y: float, state,
                   selected: bool = False, lifted: float = 0.0, alpha: float = 1.0) -> None:
    is_talisman = name == TALISMAN_NAME
    x1, x2 = DOCK_X + 1, W
    if lifted > 0:
        soft_shadow(im, (x1 + 6, y + 2, x2 - 6, y + ROW_H - 2), 4, 6, 0.6 * lifted, (0, 6))
    row, rp = new_layer()
    bg = "#3c4b5e" if selected else "#2f2f2f"
    rp.rect((x1, y, x2, y + ROW_H), fill=bg)
    if lifted > 0:
        rp.rect((x1, y, x2, y + ROW_H), outline="#6f9fd8", width=1.2 * lifted)
    rp.line([(x1, y + ROW_H), (x2, y + ROW_H)], "#232323", 1)
    cy = y + ROW_H / 2
    draw_eye(rp, 920, cy)
    if is_talisman and state["locked"]:
        pop = state["lock_pop"]
        draw_lock(rp, 946, cy, 0.6 + 0.4 * ease_out_back(pop, 2.2))
    rp.rect((958, y + 6, 961, y + ROW_H - 6), fill=colour)
    rp.poly([(970, cy - 4), (975, cy), (970, cy + 4)], fill="#9a9a9a")
    layer_thumb(rp, row, name, 982, cy - 11)
    rp.text((1022, cy), name, 12, "#ffffff" if selected else "#d6d6d6",
            "m" if selected else "", anchor="lm")
    rp.circle(1244, cy, 5, outline="#b0b0b0", width=1.2)
    if selected:
        rp.circle(1244, cy, 2.5, fill="#b0b0b0")
        rp.rect((1257, cy - 4, 1265, cy + 4), fill=colour)
    if alpha < 1:
        row = with_alpha(row, alpha)
    im.alpha_composite(row)


def draw_layers_panel(im: Image.Image, state) -> dict[str, float]:
    pen = Pen(im)
    t = state["t"]
    place = ease_in_out(span(t, T_PLACE[0], T_PLACE[0] + 0.45)) if state["placed"] else 0.0
    selected = state["selected"]

    # Positions in "slot" units (0 = top row).
    others = []
    if state["layer_dragging"] or state["at_bottom"]:
        d = 3.0 * state["reorder"]
        for i, (name, colour) in enumerate(LAYERS):
            shift = ease_in_out(clamp((d - (i + 0.5)) / 0.7 + 0.5))
            others.append((name, colour, i + 1 - shift))
        talisman_slot = d
    else:
        for i, (name, colour) in enumerate(LAYERS):
            others.append((name, colour, i + place))
        talisman_slot = 0.0

    lift = 0.0
    if state["row_lifted"]:
        lift = min(span(t, T_PRESS_ROW, T_PRESS_ROW + 0.15), 1 - span(t, *T_DROP))
    for name, colour, slot in others:
        draw_layer_row(im, pen, name, colour, ROW_Y0 + slot * ROW_H, state)
    if state["layer_dragging"]:
        drop_y = ROW_Y0 + (round(talisman_slot) + 1) * ROW_H - 1
        pen.line([(DOCK_X + 10, drop_y), (W - 10, drop_y)], "#6f9fd8", 2)
        pen.circle(DOCK_X + 10, drop_y, 3, outline="#6f9fd8", width=1.5)
    if state["placed"]:
        talisman_y = ROW_Y0 + talisman_slot * ROW_H - 3 * lift
        draw_layer_row(im, pen, TALISMAN_NAME, GREEN, talisman_y, state,
                       selected=selected or state["row_lifted"], lifted=lift,
                       alpha=place if not state["at_bottom"] else 1.0)
    # Mask anything that slid under the footer.
    pen.rect((DOCK_X + 1, 304, W, 330), fill="#2a2a2a")
    pen.line([(DOCK_X, 304), (W, 304)], "#1c1c1c", 1)
    pen.text((914, 317), f"{4 if state['placed'] else 3} Layers", 11, "#9a9a9a", anchor="lm")
    return {"talisman_slot": talisman_slot}


def draw_properties(im: Image.Image, state) -> None:
    pen = Pen(im)
    active = state["selected"] or state["locked"]
    focus = state["popup"] > 0 or state["scrubbing"]
    value = f"{state['opacity']}%" if state["placed"] and state["selected"] or state["locked"] else ""
    pen.rrect(OPACITY_FIELD, 3, fill="#1f1f1f",
              outline="#6f9fd8" if focus else "#555555", width=1.2)
    pen.text((OPACITY_FIELD[0] + 10, (OPACITY_FIELD[1] + OPACITY_FIELD[3]) / 2), value,
             12, "#f2f2f2" if active else "#777777", "m", anchor="lm")
    pen.rrect(OPACITY_CHEVRON, 3, fill="#3a3a3a" if focus else "#2a2a2a", outline="#555555", width=1)
    cx, cy = (OPACITY_CHEVRON[0] + OPACITY_CHEVRON[2]) / 2, (OPACITY_CHEVRON[1] + OPACITY_CHEVRON[3]) / 2
    pen.line([(cx - 4, cy - 2), (cx, cy + 2), (cx + 4, cy - 2)], "#d0d0d0", 1.4)

    if state["popup"] > 0:
        a = ease_in_out(state["popup"])
        layer, lp = new_layer()
        x1, y1, x2, y2 = SLIDER
        dy = -6 * (1 - a)
        soft_shadow(layer, (x1, y1 + dy, x2, y2 + dy), 6, 8, 0.7, (0, 6))
        lp.rrect((x1, y1 + dy, x2, y2 + dy), 6, fill="#3a3a3a", outline="#4d4d4d", width=1)
        t0, t1 = SLIDER_TRACK
        ky = SLIDER_Y + dy
        knob = t0 + (t1 - t0) * state["opacity"] / 100
        lp.rrect((t0, ky - 2, t1, ky + 2), 2, fill="#1f1f1f")
        lp.rrect((t0, ky - 2, knob, ky + 2), 2, fill="#8ab4f8")
        lp.circle(knob, ky, 7, fill="#f2f2f2", outline="#1f1f1f", width=1)
        im.alpha_composite(with_alpha(layer, a))

    # Control bar mirrors the selection.
    if state["selected"]:
        pen.text((16, 46), "Image", 11, "#e6e6e6", "sb", anchor="lm")
        pen.text((70, 46), "Linked File", 11, "#9a9a9a", anchor="lm")
        pen.text((140, 46), "kuai-kuai-official-green.webp", 11, "#79a8ff", anchor="lm")
        pen.text((360, 46), "Opacity:", 11, "#9a9a9a", anchor="lm")
        pen.rrect((416, 36, 470, 56), 3, fill="#1f1f1f", outline="#555555", width=1)
        pen.text((426, 46), f"{state['opacity']}%", 11, "#f2f2f2", anchor="lm")
        pen.rrect((496, 36, 556, 56), 3, outline="#555555", width=1)
        pen.text((526, 46), "Embed", 11, "#d0d0d0", anchor="mm")
    else:
        pen.text((16, 46), "No Selection", 11, "#9a9a9a", anchor="lm")


def draw_eye_hint(im: Image.Image, state) -> None:
    """Ring pulse on the talisman eye while Opacity drops: the eye stays on."""
    t = state["t"]
    a = span(t, 6.0, 6.25) * (1 - span(t, 7.2, 7.5))
    if a <= 0 or not state["at_bottom"]:
        return
    layer, pen = new_layer()
    cy = ROW_Y0 + 3 * ROW_H + ROW_H / 2
    pulse = (t * 1.6) % 1.0
    pen.circle(920, cy, 12 + 6 * pulse, outline=hex_rgba("#ffd166", (1 - pulse) * 0.9), width=2)
    pen.circle(920, cy, 12, outline=hex_rgba("#ffd166", 0.95), width=1.6)
    im.alpha_composite(with_alpha(layer, a))


def draw_ghost(im: Image.Image, state) -> None:
    """After locking: a dashed outline pulses where the invisible bag sits."""
    done = state["done"]
    if done <= 0:
        return
    t = state["t"]
    layer, pen = new_layer()
    x1, y1, x2, y2 = bag_box()
    breathe = 0.55 + 0.45 * (0.5 + 0.5 * math.cos((t - T_DONE) * 3.2))
    colour = hex_rgba(GREEN, breathe)
    dash, gap = 9, 6
    for (ax, ay), (bx, by) in [((x1, y1), (x2, y1)), ((x2, y1), (x2, y2)),
                               ((x2, y2), (x1, y2)), ((x1, y2), (x1, y1))]:
        length = abs(bx - ax) + abs(by - ay)
        pos = 0.0
        while pos < length:
            end = min(length, pos + dash)
            fx, fy = (bx - ax) / length, (by - ay) / length
            pen.line([(ax + fx * pos, ay + fy * pos), (ax + fx * end, ay + fy * end)], colour, 2)
            pos += dash + gap
    label = "看不見，但有在保佑"
    lw = pen.width(label, 13, "m") + 24
    lx, ly = (x1 + x2) / 2 - lw / 2, y2 + 10
    pen.rrect((lx, ly, lx + lw, ly + 26), 13, fill=hex_rgba(GREEN, 0.95))
    pen.text(((x1 + x2) / 2, ly + 13), label, 13, "#06210f", "m", anchor="mm")
    im.alpha_composite(with_alpha(layer, ease_in_out(done)))


def draw_caption(im: Image.Image, t: float) -> None:
    current = [c for c in CAPTIONS if t >= c[0]]
    if not current:
        return
    start, step, label = current[-1]
    a = ease_in_out(span(t, start, start + 0.3))
    layer, pen = new_layer()
    cx, cy = CAPTION_CENTER
    cy += 8 * (1 - a)
    final = step == 0
    size = 17
    text_w = pen.width(label, size, "m")
    badge_w = 0 if final else 58
    icon_w = 26 if final else 0
    w = text_w + badge_w + icon_w + 40
    x1 = cx - w / 2
    soft_shadow(layer, (x1, cy - 22, x1 + w, cy + 22), 22, 10, 0.5, (0, 6))
    pen.rrect((x1, cy - 22, x1 + w, cy + 22), 22,
              fill=hex_rgba("#0f2a19" if final else "#101010", 0.94),
              outline=hex_rgba(GREEN if final else "#3a3a3a", 1), width=1.2)
    x = x1 + 18
    if final:
        pen.circle(x + 10, cy, 10, fill=GREEN)
        pen.line([(x + 5, cy), (x + 9, cy + 4), (x + 15, cy - 4)], "#06210f", 2.2)
        x += icon_w
    else:
        pen.rrect((x, cy - 12, x + 46, cy + 12), 12, fill=GREEN)
        pen.text((x + 23, cy), f"{step} / 4", 12, "#06210f", "b", anchor="mm")
        x += badge_w
    pen.text((x, cy), label, size, "#ffffff", "m", anchor="lm")
    im.alpha_composite(with_alpha(layer, a))


def draw_cursor(im: Image.Image, x: float, y: float, pressed: bool, fade: float) -> None:
    if fade <= 0:
        return
    layer, pen = new_layer()
    s = 0.92 if pressed else 1.0
    pts = [(0, 0), (0, 21), (5, 16.5), (8.6, 24.5), (12, 23), (8.5, 15.2), (15, 15)]
    pts = [(x + px * s, y + py * s) for px, py in pts]
    shadow = [(px + 1.2, py + 2) for px, py in pts]
    pen.poly(shadow, fill=(0, 0, 0, 90))
    pen.poly(pts, fill="#ffffff", outline="#111111", width=1.4)
    if pressed:
        pen.circle(x, y, 13, outline=hex_rgba("#8ab4f8", 0.85), width=2)
    im.alpha_composite(with_alpha(layer, fade))


def illustrator_frame(progress: float, final: bool = False) -> Image.Image:
    state = illustrator_state(progress, final=final)
    t = state["t"]
    bag_image()  # also caches the Layers thumbnail, even while the bag is invisible
    im = static_shell().copy()
    back, front = static_artwork()
    # Z-order on the artboard follows the Layers panel: once the row lands at
    # the bottom, every other layer (Layout included) renders above the package.
    if state["at_bottom"]:
        paste_bag(im, state)
        im.alpha_composite(back)
        im.alpha_composite(front)
    else:
        im.alpha_composite(back)
        im.alpha_composite(front)
        paste_bag(im, state)
    draw_selection(Pen(im), state)
    draw_ghost(im, state)
    draw_layers_panel(im, state)
    draw_properties(im, state)
    draw_eye_hint(im, state)
    draw_caption(im, t)
    x, y, pressed, fade = cursor_at(t)
    draw_cursor(im, x, y, pressed, fade)
    return im.convert("RGB").resize((W, H), Image.Resampling.LANCZOS)


def save_illustrator_demo(hold_seconds: float = 2.6) -> None:
    import shutil
    import subprocess
    import tempfile

    name = "demo-illustrator-kuai-kuai"
    motion = int(round(ILLUSTRATOR_SECONDS * FPS))
    gif, png = DOCS / f"{name}.gif", DOCS / f"{name}.png"
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        last = None
        for i in range(motion):
            last = illustrator_frame(i / (motion - 1))
            last.save(tmp_path / f"f{i:04d}.png")
        final = illustrator_frame(1.0, final=True)
        final.save(png, optimize=True)
        for i in range(motion, motion + int(hold_seconds * FPS)):
            shutil.copy(tmp_path / f"f{motion - 1:04d}.png", tmp_path / f"f{i:04d}.png")
        if shutil.which("ffmpeg"):
            subprocess.run([
                "ffmpeg", "-y", "-loglevel", "error", "-framerate", str(FPS),
                "-i", str(tmp_path / "f%04d.png"),
                "-vf", "split[a][b];[a]palettegen=max_colors=256:stats_mode=full[p];"
                       "[b][p]paletteuse=dither=sierra2_4a:diff_mode=rectangle",
                "-loop", "0", str(gif)], check=True)
        else:  # Pillow fallback: larger file, same frames.
            frames = [Image.open(p) for p in sorted(tmp_path.glob("f*.png"))]
            frames[0].save(gif, save_all=True, append_images=frames[1:],
                           duration=1000 // FPS, loop=0)


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
    for y, icon in [(85, "▱"), (226, "▶"), (273, "□")]:
        text(draw, (16, y), icon, 17, "#b9b9b9")
    # DejaVu has no glyphs for ⌕ / ⑂, so the search and branch icons are drawn.
    draw.ellipse((15, 135, 29, 149), outline="#b9b9b9", width=2)
    draw.line((27, 147, 34, 154), fill="#b9b9b9", width=2)
    for cx, cy in [(18, 184), (18, 202), (31, 188)]:
        draw.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), outline="#b9b9b9", width=2)
    draw.line((18, 187, 18, 199), fill="#b9b9b9", width=2)
    draw.line((31, 191, 20, 199), fill="#b9b9b9", width=2)
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
    save_illustrator_demo()
    save_demo("demo-code-kuai-kuai", code_frame)
    print("created realistic Illustrator and code-drawn demos")


if __name__ == "__main__":
    main()
