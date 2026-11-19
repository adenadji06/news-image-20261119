#!/usr/bin/env python3
"""news-image-20261119: one image summing up the world's news of
Thursday 19 November 2026. Pure Python 3.13 standard library only.

Draws a 1024x1024 newspaper front page: masthead naming the day,
three illustrated lead stories, a world map with numbered pins,
twelve illustrated feature stories and a two-column index of all
36 verified stories of the day. Deterministic: no time, no random,
no network. Two runs write byte-identical output.
"""

import os
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
CREAM = (247, 242, 231)
PAPER = (252, 250, 244)
INK = (24, 24, 22)
NAVY = (18, 38, 66)
RED = (178, 34, 30)
BLUE = (28, 84, 150)
TEAL = (14, 110, 110)
GOLD = (176, 128, 20)
GREEN = (34, 110, 58)
GREY = (110, 108, 100)
LIGHT = (228, 222, 208)
MIDGREY = (190, 184, 170)
SKY = (168, 198, 224)
SEA = (140, 178, 205)
LAND = (232, 224, 200)
LAND2 = (222, 212, 182)

REGION = {
    "ASIA": (178, 34, 30),
    "EUROPE": (28, 84, 150),
    "AMERICAS": (14, 110, 110),
    "MIDDLE EAST": (120, 70, 140),
    "AFRICA": (176, 128, 20),
    "OCEANIA": (34, 110, 58),
    "GLOBAL": (90, 90, 88),
    "SPACE": (60, 60, 120),
}

# ---------------------------------------------------------------- canvas
px = bytearray(W * H * 3)


def put(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i] = c[0]
        px[i + 1] = c[1]
        px[i + 2] = c[2]


def fill_rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = (yy * W + x0) * 3
        for xx in range(x0, x1):
            i = base + (xx - x0) * 3
            px[i] = c[0]
            px[i + 1] = c[1]
            px[i + 2] = c[2]


def hline(x, y, w, c, th=1):
    fill_rect(x, y, w, th, c)


def vline(x, y, h, c, th=1):
    fill_rect(x, y, th, h, c)


def rect(x, y, w, h, c, th=1):
    hline(x, y, w, c, th)
    hline(x, y + h - th, w, c, th)
    vline(x, y, h, c, th)
    vline(x + w - th, y, h, c, th)


def disc(cx, cy, r, c):
    for yy in range(cy - r, cy + r + 1):
        for xx in range(cx - r, cx + r + 1):
            if (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy) <= r * r:
                put(xx, yy, c)


def ring(cx, cy, r, c, th=2):
    for yy in range(cy - r - 1, cy + r + 2):
        for xx in range(cx - r - 1, cx + r + 2):
            d = (xx - cx) * (xx - cx) + (yy - cy) * (yy - cy)
            if (r - th) * (r - th) <= d <= r * r:
                put(xx, yy, c)


def line(x0, y0, x1, y1, c, th=1):
    dx = x1 - x0
    dy = y1 - y0
    steps = max(abs(dx), abs(dy), 1)
    for s in range(steps + 1):
        x = x0 + dx * s // steps
        y = y0 + dy * s // steps
        for a in range(th):
            put(x + a, y, c)
            put(x, y + a, c)


def poly(points, c):
    """Scanline fill of a polygon given as [(x, y), ...]."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    for y in range(min(ys), max(ys) + 1):
        xs = []
        n = len(points)
        for i in range(n):
            x0, y0 = points[i]
            x1, y1 = points[(i + 1) % n]
            if (y0 <= y < y1) or (y1 <= y < y0):
                x = x0 + (y - y0) * (x1 - x0) // (y1 - y0)
                xs.append(x)
        xs.sort()
        for k in range(0, len(xs) - 1, 2):
            for x in range(xs[k], xs[k + 1] + 1):
                put(x, y, c)


def shade(c, f):
    """Scale a colour by factor f (0..1 darkens, >1 lightens, clamped)."""
    return tuple(max(0, min(255, int(v * f))) for v in c)


def blend(c1, c2, t):
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3))


def vgrad(x, y, w, h, top, bot):
    for yy in range(h):
        t = yy / max(1, h - 1)
        fill_rect(x, y + yy, w, 1, blend(top, bot, t))


# ---------------------------------------------------------------- PNG out
def _chunk(kind, data):
    out = struct.pack(">I", len(data)) + kind + data
    out += struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)
    return out


def write_png(path):
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += px[y * W * 3:(y + 1) * W * 3]
    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += _chunk(b"IHDR", ihdr)
    data += _chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    data += _chunk(b"IEND", b"")
    with open(path, "wb") as f:
        f.write(data)
    return len(data)


# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 cells; '#' is ink, '.' is blank.
FONT = {}


def _g(ch, rows):
    FONT[ch] = rows


_g("A", ["01110", "10001", "10001", "11111", "10001", "10001", "10001"])
_g("B", ["11110", "10001", "10001", "11110", "10001", "10001", "11110"])
_g("C", ["01110", "10001", "10000", "10000", "10000", "10001", "01110"])
_g("D", ["11110", "10001", "10001", "10001", "10001", "10001", "11110"])
_g("E", ["11111", "10000", "10000", "11110", "10000", "10000", "11111"])
_g("F", ["11111", "10000", "10000", "11110", "10000", "10000", "10000"])
_g("G", ["01110", "10001", "10000", "10111", "10001", "10001", "01111"])
_g("H", ["10001", "10001", "10001", "11111", "10001", "10001", "10001"])
_g("I", ["01110", "00100", "00100", "00100", "00100", "00100", "01110"])
_g("J", ["00111", "00010", "00010", "00010", "00010", "10010", "01100"])
_g("K", ["10001", "10010", "10100", "11000", "10100", "10010", "10001"])
_g("L", ["10000", "10000", "10000", "10000", "10000", "10000", "11111"])
_g("M", ["10001", "11011", "10101", "10101", "10001", "10001", "10001"])
_g("N", ["10001", "11001", "10101", "10011", "10001", "10001", "10001"])
_g("O", ["01110", "10001", "10001", "10001", "10001", "10001", "01110"])
_g("P", ["11110", "10001", "10001", "11110", "10000", "10000", "10000"])
_g("Q", ["01110", "10001", "10001", "10001", "10101", "10010", "01101"])
_g("R", ["11110", "10001", "10001", "11110", "10100", "10010", "10001"])
_g("S", ["01111", "10000", "10000", "01110", "00001", "00001", "11110"])
_g("T", ["11111", "00100", "00100", "00100", "00100", "00100", "00100"])
_g("U", ["10001", "10001", "10001", "10001", "10001", "10001", "01110"])
_g("V", ["10001", "10001", "10001", "10001", "10001", "01010", "00100"])
_g("W", ["10001", "10001", "10001", "10101", "10101", "11011", "10001"])
_g("X", ["10001", "10001", "01010", "00100", "01010", "10001", "10001"])
_g("Y", ["10001", "10001", "01010", "00100", "00100", "00100", "00100"])
_g("Z", ["11111", "00001", "00010", "00100", "01000", "10000", "11111"])
_g("0", ["01110", "10001", "10011", "10101", "11001", "10001", "01110"])
_g("1", ["00100", "01100", "00100", "00100", "00100", "00100", "01110"])
_g("2", ["01110", "10001", "00001", "00110", "01000", "10000", "11111"])
_g("3", ["11110", "00001", "00001", "01110", "00001", "00001", "11110"])
_g("4", ["00010", "00110", "01010", "10010", "11111", "00010", "00010"])
_g("5", ["11111", "10000", "11110", "00001", "00001", "10001", "01110"])
_g("6", ["00110", "01000", "10000", "11110", "10001", "10001", "01110"])
_g("7", ["11111", "00001", "00010", "00100", "01000", "01000", "01000"])
_g("8", ["01110", "10001", "10001", "01110", "10001", "10001", "01110"])
_g("9", ["01110", "10001", "10001", "01111", "00001", "00010", "01100"])
_g("a", ["00000", "00000", "01110", "00001", "01111", "10001", "01111"])
_g("b", ["10000", "10000", "11110", "10001", "10001", "10001", "11110"])
_g("c", ["00000", "00000", "01110", "10001", "10000", "10001", "01110"])
_g("d", ["00001", "00001", "01111", "10001", "10001", "10001", "01111"])
_g("e", ["00000", "00000", "01110", "10001", "11111", "10000", "01110"])
_g("f", ["00110", "01001", "01000", "11110", "01000", "01000", "01000"])
_g("g", ["00000", "01111", "10001", "10001", "01111", "00001", "01110"])
_g("h", ["10000", "10000", "11110", "10001", "10001", "10001", "10001"])
_g("i", ["00100", "00000", "01100", "00100", "00100", "00100", "01110"])
_g("j", ["00010", "00000", "00110", "00010", "00010", "10010", "01100"])
_g("k", ["10000", "10000", "10010", "10100", "11000", "10100", "10010"])
_g("l", ["01100", "00100", "00100", "00100", "00100", "00100", "01110"])
_g("m", ["00000", "00000", "11010", "10101", "10101", "10101", "10101"])
_g("n", ["00000", "00000", "11110", "10001", "10001", "10001", "10001"])
_g("o", ["00000", "00000", "01110", "10001", "10001", "10001", "01110"])
_g("p", ["00000", "11110", "10001", "10001", "11110", "10000", "10000"])
_g("q", ["00000", "01111", "10001", "10001", "01111", "00001", "00001"])
_g("r", ["00000", "00000", "10110", "11001", "10000", "10000", "10000"])
_g("s", ["00000", "00000", "01111", "10000", "01110", "00001", "11110"])
_g("t", ["01000", "01000", "11110", "01000", "01000", "01001", "00110"])
_g("u", ["00000", "00000", "10001", "10001", "10001", "10011", "01101"])
_g("v", ["00000", "00000", "10001", "10001", "10001", "01010", "00100"])
_g("w", ["00000", "00000", "10001", "10101", "10101", "10101", "01010"])
_g("x", ["00000", "00000", "10001", "01010", "00100", "01010", "10001"])
_g("y", ["00000", "00000", "10001", "10001", "01111", "00001", "01110"])
_g("z", ["00000", "00000", "11111", "00010", "00100", "01000", "11111"])
_g(" ", ["00000", "00000", "00000", "00000", "00000", "00000", "00000"])
_g(".", ["00000", "00000", "00000", "00000", "00000", "01100", "01100"])
_g(",", ["00000", "00000", "00000", "00000", "01100", "00100", "01000"])
_g(":", ["00000", "01100", "01100", "00000", "01100", "01100", "00000"])
_g(";", ["00000", "01100", "01100", "00000", "01100", "00100", "01000"])
_g("!", ["00100", "00100", "00100", "00100", "00100", "00000", "00100"])
_g("?", ["01110", "10001", "00001", "00110", "00100", "00000", "00100"])
_g("-", ["00000", "00000", "00000", "01110", "00000", "00000", "00000"])
_g("'", ["00100", "00100", "01000", "00000", "00000", "00000", "00000"])
_g('"', ["01010", "01010", "00000", "00000", "00000", "00000", "00000"])
_g("(", ["00010", "00100", "01000", "01000", "01000", "00100", "00010"])
_g(")", ["01000", "00100", "00010", "00010", "00010", "00100", "01000"])
_g("/", ["00001", "00010", "00010", "00100", "01000", "01000", "10000"])
_g("%", ["11001", "11010", "00010", "00100", "01000", "01011", "10011"])
_g("$", ["00100", "01111", "10100", "01110", "00101", "11110", "00100"])
_g("&", ["01100", "10010", "10100", "01000", "10101", "10010", "01101"])
_g("+", ["00000", "00100", "00100", "11111", "00100", "00100", "00000"])
_g("=", ["00000", "00000", "11111", "00000", "11111", "00000", "00000"])
_g("#", ["01010", "01010", "11111", "01010", "11111", "01010", "01010"])
_g("*", ["00000", "10101", "01110", "11111", "01110", "10101", "00000"])
_g("_", ["00000", "00000", "00000", "00000", "00000", "00000", "11111"])
_g("@", ["01110", "10001", "10111", "10101", "10110", "10000", "01110"])
_g("[", ["01110", "01000", "01000", "01000", "01000", "01000", "01110"])
_g("]", ["01110", "00010", "00010", "00010", "00010", "00010", "01110"])
_g(">", ["10000", "01000", "00100", "00010", "00100", "01000", "10000"])
_g("<", ["00001", "00010", "00100", "01000", "00100", "00010", "00001"])

BLANK = ["00000"] * 7


def glyph(ch):
    return FONT.get(ch, BLANK)


def text_w(s, scale):
    """Pixel width of s at integer scale (6 units per char incl. spacing)."""
    return len(s) * 6 * scale - scale


def text_h(scale):
    return 7 * scale


def draw_text(x, y, s, scale, c, bold=False):
    """Draw s with top-left at (x, y). Returns width in pixels."""
    cx = x
    for ch in s:
        rows = glyph(ch)
        for ry in range(7):
            row = rows[ry]
            for rx in range(5):
                if row[rx] == "1":
                    fill_rect(cx + rx * scale, y + ry * scale,
                              scale, scale, c)
                    if bold and scale >= 2:
                        fill_rect(cx + rx * scale + 1, y + ry * scale,
                                  scale, scale, c)
        cx += 6 * scale
    return cx - x - scale


def draw_text_c(x, y, w, s, scale, c, bold=False):
    tw = text_w(s, scale)
    return draw_text(x + (w - tw) // 2, y, s, scale, c, bold)


def wrap(s, max_w, scale):
    """Greedy word wrap; returns list of lines, each fitting max_w px."""
    lines = []
    for para in s.split("\n"):
        words = para.split(" ")
        cur = ""
        for wd in words:
            trial = wd if not cur else cur + " " + wd
            if text_w(trial, scale) <= max_w or not cur:
                cur = trial
            else:
                lines.append(cur)
                cur = wd
        if cur:
            lines.append(cur)
    return lines


def block_h(lines, scale, gap):
    if not lines:
        return 0
    return len(lines) * text_h(scale) + (len(lines) - 1) * gap


# ---------------------------------------------------------------- scenes
def skyline(x, y, w, h, c):
    """Simple city skyline silhouette inside a box."""
    base = y + h
    heights = [0.55, 0.8, 0.45, 0.95, 0.65, 0.75, 0.5, 0.9, 0.6, 0.4,
               0.85, 0.55, 0.7, 0.45, 0.8, 0.6]
    bw = max(6, w // len(heights))
    for i, f in enumerate(heights):
        bh = int(h * f)
        fill_rect(x + i * bw, base - bh, bw - 2, bh, c)


def flag(x, y, w, h, kind):
    """Small flag on a pole at (x, y); kind: us / cn / ru."""
    vline(x, y, h + 26, INK, 2)
    if kind == "us":
        fill_rect(x + 2, y, w, h, (178, 34, 30))
        for i in range(7):
            fill_rect(x + 2, y + i * (h // 7), w, h // 14,
                      (252, 250, 244) if i % 2 else (178, 34, 30))
        fill_rect(x + 2, y, w // 2, h // 2, (18, 38, 66))
        for r in range(3):
            for cc in range(4):
                put(x + 4 + cc * 6, y + 3 + r * 5, (252, 250, 244))
    elif kind == "cn":
        fill_rect(x + 2, y, w, h, (205, 30, 25))
        disc(x + 10, y + 8, 3, (250, 220, 60))
        put(x + 20, y + 4, (250, 220, 60))
        put(x + 24, y + 8, (250, 220, 60))
        put(x + 20, y + 12, (250, 220, 60))
    else:
        fill_rect(x + 2, y, w, h // 3 + 1, (252, 250, 244))
        fill_rect(x + 2, y + h // 3, w, h // 3 + 1, (20, 60, 160))
        fill_rect(x + 2, y + 2 * h // 3, w, h // 3 + 1, (200, 30, 25))


def hero_summit(x, y, w, h):
    vgrad(x, y, w, h, (214, 228, 240), (240, 232, 210))
    disc(x + w - 40, y + 26, 18, (250, 220, 120))
    skyline(x, y + h - 58, w, 58, shade(NAVY, 0.75))
    skyline(x, y + h - 34, w, 34, NAVY)
    flag(x + 52, y + 18, 46, 30, "us")
    flag(x + w // 2 - 10, y + 10, 46, 30, "cn")
    flag(x + w - 100, y + 18, 46, 30, "ru")
    # meeting table
    fill_rect(x + 40, y + h - 30, w - 80, 8, (120, 72, 40))
    for tx in (x + 70, x + w // 2 - 8, x + w - 90):
        disc(tx + 8, y + h - 42, 8, INK)
        fill_rect(tx, y + h - 34, 16, 10, INK)


def hero_court(x, y, w, h):
    vgrad(x, y, w, h, (228, 222, 208), (206, 196, 172))
    # courthouse pediment and columns
    poly([(x + 20, y + 46), (x + w // 2, y + 8), (x + w - 20, y + 46)],
         (200, 188, 158))
    fill_rect(x + 14, y + 46, w - 28, 8, (160, 146, 118))
    for i in range(5):
        cx = x + 34 + i * ((w - 68) // 4)
        fill_rect(cx, y + 54, 12, h - 74, (238, 232, 216))
        fill_rect(cx - 2, y + 54, 16, 4, (160, 146, 118))
        fill_rect(cx - 2, y + h - 24, 16, 4, (160, 146, 118))
    fill_rect(x + 14, y + h - 20, w - 28, 8, (160, 146, 118))
    # scales of justice in the pediment
    disc(x + w // 2, y + 26, 4, INK)
    line(x + w // 2 - 18, y + 30, x + w // 2 + 18, y + 30, INK, 2)
    line(x + w // 2 - 18, y + 30, x + w // 2 - 24, y + 42, INK, 1)
    line(x + w // 2 + 18, y + 30, x + w // 2 + 24, y + 42, INK, 1)
    poly([(x + w // 2 - 30, y + 42), (x + w // 2 - 18, y + 42),
          (x + w // 2 - 24, y + 36)], INK)
    poly([(x + w // 2 + 18, y + 42), (x + w // 2 + 30, y + 42),
          (x + w // 2 + 24, y + 36)], INK)


def hero_ipo(x, y, w, h):
    vgrad(x, y, w, h, (18, 38, 66), (28, 84, 150))
    # rising chart line with arrow
    pts = [(x + 16, y + h - 30), (x + 70, y + int(h * 0.62)),
           (x + 120, y + int(h * 0.68)), (x + 180, y + int(h * 0.42)),
           (x + 240, y + int(h * 0.28)), (x + w - 24, y + int(h * 0.12))]
    for a, b in zip(pts, pts[1:]):
        line(a[0], a[1], b[0], b[1], (120, 220, 140), 4)
    line(pts[-1][0], pts[-1][1], pts[-1][0] - 16, pts[-1][1] + 2,
         (120, 220, 140), 4)
    line(pts[-1][0], pts[-1][1], pts[-1][0] - 2, pts[-1][1] + 16,
         (120, 220, 140), 4)
    # candlesticks
    for i, (cx, top, bot) in enumerate([(x + 40, h - 48, h - 28),
                                        (x + 90, h - 58, h - 38),
                                        (x + 150, h - 68, h - 48),
                                        (x + 210, h - 78, h - 58)]):
        fill_rect(cx, y + top, 10, bot - top, (250, 220, 60))
        vline(cx + 5, y + top - 8, bot - top + 16, (250, 220, 60), 2)
    # ticker tape
    fill_rect(x, y + h - 26, w, 26, (247, 242, 231))
    draw_text(x + 10, y + h - 20, "ANT $83  +$81.3bn", 2, NAVY, True)


def icon_bridge(x, y, s):
    # suspension bridge: deck, two towers, one sagging cable
    fill_rect(x + 2, y + s - 12, s - 4, 4, INK)
    for tx in (x + 8, x + s - 14):
        fill_rect(tx, y + 4, 5, s - 16, INK)
    mid = x + s // 2
    half = s // 2 - 10
    prev = None
    for cx in range(x + 10, x + s - 10):
        d = (cx - mid) * 100 // half
        sag = 16 * (10000 - d * d) // 10000
        cy = y + 6 + sag
        if prev is not None:
            line(prev[0], prev[1], cx, cy, INK, 1)
        prev = (cx, cy)
    fill_rect(x + s // 2 - 10, y + s - 18, 20, 6, RED)


def icon_missile(x, y, s):
    fill_rect(x + s // 2 - 8, y + 4, 16, 16, TEAL)
    poly([(x + s // 2 - 8, y + 4), (x + s // 2 + 8, y + 4),
          (x + s // 2, y - 2)], TEAL)
    line(x + s // 2 - 4, y + 20, x + s // 2 - 8, y + 30, RED, 2)
    line(x + s // 2 + 4, y + 20, x + s // 2 + 8, y + 30, RED, 2)
    disc(x + s // 2, y + s - 6, 5, GOLD)


def icon_globe(x, y, s):
    disc(x + s // 2, y + s // 2, s // 2 - 2, BLUE)
    ring(x + s // 2, y + s // 2, s // 2 - 2, INK, 1)
    hline(x + 2, y + s // 2, s - 4, INK, 1)
    for dx in (-10, 0, 10):
        line(x + s // 2 + dx, y + 4, x + s // 2 - dx, y + s - 4, INK, 1)
    fill_rect(x + 6, y + 8, 10, 8, GREEN)
    fill_rect(x + s - 18, y + s - 16, 12, 8, GREEN)


def icon_cyclone(x, y, s):
    c = s // 2
    for r in range(4, s // 2, 4):
        ring(x + c, y + c, r, TEAL, 2)
    line(x + c, y + c, x + s - 4, y + 6, INK, 2)
    disc(x + c, y + c, 4, RED)


def icon_frame(x, y, s):
    rect(x + 4, y + 4, s - 8, s - 8, GOLD, 3)
    fill_rect(x + 8, y + 8, s - 16, s - 16, (250, 220, 120))
    disc(x + s // 2, y + s // 2 - 4, 7, (200, 90, 40))
    poly([(x + 10, y + s - 10), (x + s // 2, y + s // 2),
          (x + s - 10, y + s - 10)], GREEN)


def icon_euro(x, y, s):
    disc(x + s // 2, y + s // 2, s // 2 - 2, GOLD)
    ring(x + s // 2, y + s // 2, s // 2 - 2, INK, 1)
    draw_text(x + s // 2 - 9, y + s // 2 - 10, "E", 3, INK, True)


def icon_handshake(x, y, s):
    line(x + 6, y + s // 2, x + s // 2, y + s - 8, INK, 3)
    line(x + s - 6, y + s // 2, x + s // 2, y + s - 8, INK, 3)
    disc(x + 6, y + s // 2, 5, BLUE)
    disc(x + s - 6, y + s // 2, 5, RED)
    fill_rect(x + s // 2 - 12, y + s // 2 - 2, 24, 6, INK)


def icon_cricket(x, y, s):
    line(x + 8, y + 8, x + s - 14, y + s - 10, (150, 100, 50), 5)
    disc(x + s - 12, y + 10, 7, RED)
    ring(x + s - 12, y + 10, 7, INK, 1)
    fill_rect(x + 6, y + s - 8, s - 12, 4, GREEN)


def icon_controller(x, y, s):
    fill_rect(x + 4, y + s // 2 - 8, s - 8, 18, INK)
    disc(x + 12, y + s // 2 + 2, 5, (250, 250, 250))
    disc(x + s - 12, y + s // 2 + 2, 5, RED)
    put(x + 14, y + s // 2 - 4, (120, 220, 140))
    put(x + s - 14, y + s // 2 - 4, (250, 220, 60))


def icon_virus(x, y, s):
    c = s // 2
    disc(x + c, y + c, 10, RED)
    for a in range(8):
        ang = a * 3.14159 / 4
        dx = int(13 * (1 if abs(ang) < 0.01 else 1))
        ex = x + c + int(14 * _cos(a))
        ey = y + c + int(14 * _sin(a))
        line(x + c, y + c, ex, ey, RED, 2)
    disc(x + c - 3, y + c - 3, 2, (250, 250, 250))
    disc(x + c + 4, y + c + 3, 2, (250, 250, 250))


def _cos(a):
    table = [1, 0.7071, 0, -0.7071, -1, -0.7071, 0, 0.7071]
    return table[a % 8]


def _sin(a):
    table = [0, 0.7071, 1, 0.7071, 0, -0.7071, -1, -0.7071]
    return table[a % 8]


def icon_flame(x, y, s):
    poly([(x + s // 2, y + 2), (x + s - 6, y + s // 2),
          (x + s - 8, y + s - 6), (x + 8, y + s - 6),
          (x + 6, y + s // 2)], (230, 90, 30))
    poly([(x + s // 2, y + 14), (x + s - 12, y + s // 2 + 4),
          (x + s // 2, y + s - 8), (x + 12, y + s // 2 + 4)],
         (250, 200, 40))


def icon_troops(x, y, s):
    for i, cx in enumerate((x + 10, x + s // 2, x + s - 10)):
        disc(cx, y + 10, 5, INK)
        fill_rect(cx - 5, y + 16, 10, s - 22, (90, 90, 88) if i != 1 else RED)
    hline(x + 4, y + s - 4, s - 8, INK, 2)


ICONS = {
    "bridge": icon_bridge, "missile": icon_missile, "globe": icon_globe,
    "cyclone": icon_cyclone, "frame": icon_frame, "euro": icon_euro,
    "handshake": icon_handshake, "cricket": icon_cricket,
    "controller": icon_controller, "virus": icon_virus,
    "flame": icon_flame, "troops": icon_troops,
}


# ---------------------------------------------------------------- world map
def lonlat_to_xy(lon, lat, mx, my, mw, mh):
    x = mx + int((lon + 170.0) / 360.0 * mw)
    y = my + int((75.0 - lat) / 130.0 * mh)
    return x, y


CONTINENTS = [
    # North America
    [(-168, 66), (-140, 70), (-125, 71), (-110, 68), (-95, 69),
     (-85, 66), (-75, 62), (-65, 60), (-55, 52), (-60, 47),
     (-70, 44), (-75, 38), (-80, 32), (-81, 26), (-90, 21),
     (-97, 16), (-105, 20), (-115, 28), (-125, 40), (-125, 49),
     (-140, 60), (-155, 58), (-168, 66)],
    # South America
    [(-79, 9), (-72, 12), (-62, 10), (-52, 5), (-44, -3), (-35, -8),
     (-40, -20), (-48, -28), (-57, -38), (-65, -45), (-68, -52),
     (-70, -40), (-72, -25), (-77, -12), (-81, -4), (-79, 9)],
    # Africa
    [(-17, 15), (-10, 31), (0, 36), (10, 37), (20, 32), (30, 31),
     (35, 28), (43, 12), (51, 11), (51, -2), (40, -10), (35, -20),
     (32, -29), (20, -35), (16, -28), (12, -18), (9, -1), (9, 4),
     (-8, 5), (-17, 15)],
    # Europe
    [(-10, 36), (-9, 43), (-2, 48), (-5, 50), (0, 51), (5, 53),
     (8, 57), (10, 59), (5, 60), (10, 62), (18, 69), (30, 70),
     (40, 68), (45, 60), (40, 55), (35, 50), (30, 46), (28, 41),
     (23, 36), (19, 40), (12, 44), (3, 43), (-10, 36)],
    # Asia
    [(40, 68), (55, 68), (70, 72), (90, 75), (110, 76), (130, 72),
     (150, 70), (170, 67), (178, 65), (170, 60), (162, 56),
     (158, 52), (142, 50), (140, 40), (130, 35), (122, 30),
     (120, 22), (110, 20), (105, 10), (100, 8), (98, 16),
     (92, 21), (88, 22), (80, 13), (77, 8), (72, 20), (66, 25),
     (60, 25), (52, 27), (48, 30), (44, 29), (40, 31), (36, 36),
     (35, 42), (40, 47), (40, 55), (45, 60), (40, 68)],
    # Australia
    [(113, -22), (122, -14), (132, -12), (142, -11), (146, -19),
     (150, -23), (153, -27), (150, -37), (140, -38), (135, -35),
     (129, -32), (122, -34), (115, -35), (113, -22)],
    # SE Asia islands
    [(95, 5), (104, 1), (110, -2), (114, -4), (120, -2), (125, 2),
     (130, -1), (135, -4), (138, -8), (130, -8), (120, -10),
     (114, -8), (106, -6), (100, -2), (95, 5)],
]


def draw_map(mx, my, mw, mh):
    fill_rect(mx, my, mw, mh, (214, 230, 238))
    # latitude grid
    for lat in (-60, -30, 0, 30, 60):
        _, gy = lonlat_to_xy(0, lat, mx, my, mw, mh)
        for gx in range(mx, mx + mw, 6):
            put(gx, gy, (190, 205, 218))
    for lon in (-120, -60, 0, 60, 120):
        gx, _ = lonlat_to_xy(lon, 0, mx, my, mw, mh)
        for gy in range(my, my + mh, 6):
            put(gx, gy, (190, 205, 218))
    for cont in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, mx, my, mw, mh) for lon, lat in cont]
        poly(pts, LAND)
        for a, b in zip(pts, pts[1:] + pts[:1]):
            line(a[0], a[1], b[0], b[1], shade(LAND, 0.82), 1)
    # equator label
    _, eq = lonlat_to_xy(0, 0, mx, my, mw, mh)
    draw_text(mx + 4, eq + 3, "EQUATOR", 1, GREY)


# ---------------------------------------------------------------- stories
# All 36 events happened or were first reported on Thursday 19 Nov 2026.
# Sources: AP, Reuters, BBC, Horizon, One Turn, The Hindu, ANI, IMD,
# Sotheby's, Nasdaq, Plus500, Techzim, Inshorts, Cricinfo, ScoreZaap.

HEROES = [
    dict(num=1, place="SHENZHEN", region="ASIA", scene="summit",
         head="TRUMP, XI, PUTIN\nMEET IN SHENZHEN",
         deck="First three-way summit of the three nuclear powers, on the APEC sidelines."),
    dict(num=2, place="THE HAGUE", region="EUROPE", scene="court",
         head="THE ROHINGYA\nGENOCIDE VERDICT",
         deck="Gambia's case against Myanmar is decided at the world court."),
    dict(num=3, place="NEW YORK", region="AMERICAS", scene="ipo",
         head="RECORD $81.3BN\nIPO DEBUTS",
         deck="Claude maker Anthropic lists on Nasdaq at $83 a share, valued at $1.5tn."),
]

FEATURES = [
    dict(num=4, place="CRIMEA", region="EUROPE", icon="bridge",
         head="CRIMEA BRIDGE HIT AGAIN",
         deck="Road traffic halted again"),
    dict(num=5, place="GULF", region="MIDDLE EAST", icon="missile",
         head="IRAN HITS GULF STATES",
         deck="Kuwait repels attack"),
    dict(num=6, place="ANTALYA", region="EUROPE", icon="globe",
         head="COP31 TALKS STUCK",
         deck="Ministers hunt a final text"),
    dict(num=7, place="ODISHA", region="ASIA", icon="cyclone",
         head="CYCLONE AKVAN NEARS INDIA",
         deck="80,000 evacuated in Odisha"),
    dict(num=8, place="NEW YORK", region="AMERICAS", icon="frame",
         head="VAN GOGH SELLS FOR $190.4M",
         deck="Artist record at Sotheby's"),
    dict(num=9, place="BRUSSELS", region="EUROPE", icon="euro",
         head="EU'S EUR 45BN UKRAINE LOAN",
         deck="New loan for 2027"),
    dict(num=10, place="CARACAS", region="AMERICAS", icon="handshake",
         head="US-VENEZUELA MILITARY PACT",
         deck="Hegseth signs in Caracas"),
    dict(num=11, place="JOHANNESBURG", region="AFRICA", icon="cricket",
         head="SOUTH AFRICA WIN FIRST TEST",
         deck="Nine wickets over Bangladesh"),
    dict(num=12, place="MIAMI", region="AMERICAS", icon="controller",
         head="GTA VI GOES ON SALE",
         deck="After a 13-year wait"),
    dict(num=13, place="WASHINGTON", region="AMERICAS", icon="virus",
         head="MEASLES-FREE STATUS LOST",
         deck="Ends 26 years of elimination"),
    dict(num=14, place="DHAKA", region="ASIA", icon="flame",
         head="BANGLADESH IN TURMOIL",
         deck="Violence in 28 districts"),
    dict(num=15, place="HORN OF AFRICA", region="AFRICA", icon="troops",
         head="HORN TENSIONS RISE",
         deck="Troops mass at the border"),
]

# index items: (num, place, region, line1, line2)
INDEX = [
    (16, "HORMUZ", "MIDDLE EAST",
     "IEA warns of worst threat",
     "to global energy security"),
    (17, "GAZA", "MIDDLE EAST",
     "Israel raids past yellow line",
     "Hamas calls it a ceasefire breach"),
    (18, "RIYADH", "MIDDLE EAST",
     "Houthi debris hits PIF tower",
     "Saudi wealth fund tower damaged"),
    (19, "FIJI", "OCEANIA",
     "Drought disaster declared",
     "El Nino drains water supplies"),
    (20, "INDONESIA", "ASIA",
     "Fires burn 3m hectares",
     "one of the worst seasons on record"),
    (21, "CHINA", "ASIA",
     "Homo erectus teeth found",
     "in Guangxi, challenge evolution theory"),
    (22, "N KOREA", "ASIA",
     "Enrichment expanded",
     "IAEA cites Yongbyon site"),
    (23, "WASHINGTON", "AMERICAS",
     "Jeffries for Speaker",
     "a first for a Black House leader"),
    (24, "MIAMI", "AMERICAS",
     "Pastor guilty in Moise killing",
     "2021 assassination of Haiti's president"),
    (25, "IMF", "GLOBAL",
     "Public debt nears 100% of GDP",
     "a post-war high, Georgieva warns"),
    (26, "SEOUL", "ASIA",
     "Exports pass $1tn first time",
     "driven by chip demand"),
    (27, "LONDON", "EUROPE",
     "Energy bills up GBP 443 a year",
     "from January; inflation at a one-year high"),
    (28, "CANBERRA", "OCEANIA",
     "Jobless rate jumps to 4.9%",
     "Australia sheds 43,500 jobs"),
    (29, "KIGALI", "AFRICA",
     "Five EU states eye Rwanda plan",
     "to send asylum seekers there"),
    (30, "ANKARA", "EUROPE",
     "Imamoglu sentenced in CHP case",
     "eight others sentenced with him"),
    (31, "PEW", "GLOBAL",
     "Muslims pass Christians by 2035",
     "worldwide, study projects"),
    (32, "SEOUL", "ASIA",
     "Exam held under AI cheat curbs",
     "college test tightens rules"),
    (33, "LONDON", "EUROPE",
     "Chelsea beat PSG 1-0",
     "in the Women's Champions League"),
    (34, "TURIN", "EUROPE",
     "Alcaraz beats Medvedev",
     "at the ATP Finals"),
    (35, "CAMBRIDGE", "EUROPE",
     "'human' is word of the year",
     "dictionary's pick for 2026"),
    (36, "DEEP SPACE", "SPACE",
     "Voyager 1 a light-day out",
     "from Earth, farther than any craft"),
]

# pin positions: num -> (lon, lat, nudge_dx, nudge_dy)
PINS = {
    1: (114, 22.5, 0, 0), 2: (4.3, 52, -30, -12), 3: (-74, 40.7, 0, 0),
    4: (34, 45, 10, -12), 5: (48, 29.5, -10, 10), 6: (30.7, 36.9, -16, 2),
    7: (85.5, 20, -12, 8), 8: (-74, 40.7, 16, -12), 9: (4.35, 50.8, -6, -20),
    10: (-66.9, 10.5, 0, 0), 11: (28, -26.2, 0, 0), 12: (-80.2, 25.8, 0, 0),
    13: (-77, 38.9, 16, 6), 14: (90.4, 23.8, 14, -8), 15: (38.7, 9, 0, 0),
    16: (56.5, 26.5, 10, 8), 17: (34.5, 31.5, -14, 12), 18: (46.7, 24.6, 12, -10),
    19: (178, -17.7, 0, 0), 20: (113, -2, 10, 10), 21: (108.3, 22.8, -14, -10),
    22: (126.5, 39.8, 0, -12), 23: (-77, 38.9, -14, -10), 24: (-80.2, 25.8, -14, 14),
    25: (-77, 38.9, 0, -20), 26: (127, 37.5, -14, 10), 27: (-0.1, 51.5, 16, -4),
    28: (149.1, -35.3, 0, 0), 29: (30.1, -1.9, 0, 0), 30: (32.9, 39.9, 14, 8),
    31: (-77, 38.9, 0, 18), 32: (127, 37.5, 16, -6), 33: (-0.1, 51.5, -24, 8),
    34: (7.7, 45.1, -14, 18), 35: (0.12, 52.2, 28, 10),
}

ALL_REGIONS = {}
for _s in HEROES + FEATURES:
    ALL_REGIONS[_s["num"]] = _s["region"]
for _n, _p, _r, _a, _b in INDEX:
    ALL_REGIONS[_n] = _r


# ---------------------------------------------------------------- layout
def section_head(x, y, w, title, right=""):
    draw_text(x, y, title, 2, INK, True)
    if right:
        tw = text_w(right, 1)
        draw_text(x + w - tw, y + 4, right, 1, GREY)
    hline(x, y + 18, w, INK, 2)


def draw_masthead():
    fill_rect(0, 0, W, 112, CREAM)
    draw_text_c(0, 8, W, "T H E   W O R L D   I N   O N E   D A Y", 2,
                RED, True)
    draw_text_c(0, 30, W, "THURSDAY 19 NOVEMBER 2026", 5, INK, True)
    draw_text_c(0, 74, W,
                "TRUMP, XI AND PUTIN MEET  -  THE HAGUE RULES  -  RECORD IPO",
                2, NAVY, True)
    hline(16, 98, W - 32, INK, 2)
    hline(16, 102, W - 32, INK, 1)
    draw_text_c(0, 106, W, "", 1, INK)


def draw_heroes():
    y0 = 118
    ph = 218
    pw = 322
    for i, h in enumerate(HEROES):
        x = 16 + i * (pw + 8)
        fill_rect(x, y0, pw, ph, PAPER)
        rect(x, y0, pw, ph, MIDGREY, 1)
        ih = 88
        if h["scene"] == "summit":
            hero_summit(x + 1, y0 + 1, pw - 2, ih)
        elif h["scene"] == "court":
            hero_court(x + 1, y0 + 1, pw - 2, ih)
        else:
            hero_ipo(x + 1, y0 + 1, pw - 2, ih)
        ky = y0 + ih + 8
        rc = REGION[h["region"]]
        kw = text_w(h["place"], 2) + 12
        fill_rect(x + 10, ky, kw, 16, rc)
        draw_text(x + 16, ky + 1, h["place"], 2, (255, 255, 255), True)
        draw_text(x + 10 + kw + 8, ky + 1,
                  "No. %d" % h["num"], 2, GREY, True)
        hy = ky + 22
        for ln in h["head"].split("\n"):
            draw_text(x + 10, hy, ln, 3, INK, True)
            hy += text_h(3) + 2
        dy = hy + 4
        for ln in wrap(h["deck"], pw - 20, 2):
            draw_text(x + 10, dy, ln, 2, (60, 58, 52))
            dy += text_h(2) + 2


def draw_map_section():
    y0 = 344
    section_head(16, y0, W - 32, "WHERE IT HAPPENED",
                 "36 STORIES, NUMBERED ON THE MAP")
    mx, my, mw, mh = 16, y0 + 26, W - 32, 108
    draw_map(mx, my, mw, mh)
    rect(mx, my, mw, mh, MIDGREY, 1)
    for num, (lon, lat, dx, dy) in PINS.items():
        bx, by = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        px2, py2 = bx + dx, by + dy
        if dx or dy:
            line(bx, by, px2, py2, INK, 1)
            disc(bx, by, 2, INK)
        rc = REGION[ALL_REGIONS[num]]
        disc(px2, py2, 8, rc)
        ring(px2, py2, 8, (255, 255, 255), 2)
        ns = str(num)
        draw_text(px2 - text_w(ns, 1) // 2, py2 - 3, ns, 1,
                  (255, 255, 255), True)
    # story 36: deep space star at the map's top right
    sx, sy = mx + mw - 26, my + 14
    disc(sx, sy, 8, REGION["SPACE"])
    ring(sx, sy, 8, (255, 255, 255), 2)
    draw_text(sx - 5, sy - 3, "36", 1, (255, 255, 255), True)
    draw_text(sx - 34, sy + 12, "DEEP SPACE", 1, GREY)
    # region legend
    lx = mx + 8
    ly = my + mh - 16
    for name in ("ASIA", "EUROPE", "AMERICAS", "MIDDLE EAST",
                 "AFRICA", "OCEANIA", "GLOBAL"):
        fill_rect(lx, ly, 8, 8, REGION[name])
        draw_text(lx + 11, ly, name, 1, INK)
        lx += 11 + text_w(name, 1) + 12


def draw_features():
    y0 = 486
    section_head(16, y0, W - 32, "THE DAY IN PICTURES",
                 "12 STORIES, DRAWN")
    fy = y0 + 26
    cw = 242
    ch = 61
    for i, f in enumerate(FEATURES):
        col = i % 4
        row = i // 4
        x = 16 + col * (cw + 8)
        y = fy + row * (ch + 4)
        fill_rect(x, y, cw, ch, PAPER)
        rect(x, y, cw, ch, LIGHT, 1)
        ICONS[f["icon"]](x + 6, y + 8, 44)
        vline(x + 56, y + 6, ch - 12, LIGHT, 1)
        tx = x + 64
        tw = cw - 72
        rc = REGION[f["region"]]
        draw_text(tx, y + 5, "%d  %s" % (f["num"], f["place"]), 1, rc, True)
        hy = y + 16
        for ln in wrap(f["head"], tw, 2):
            if text_w(ln, 2) > tw:
                raise SystemExit("feature %d head too wide: %s"
                                 % (f["num"], ln))
            draw_text(tx, hy, ln, 2, INK, True)
            hy += text_h(2) + 1
        dy = hy + 1
        for ln in wrap(f["deck"], tw, 1):
            draw_text(tx, dy, ln, 1, (70, 68, 62))
            dy += text_h(1) + 1
        if dy > y + ch + 1:
            raise SystemExit("feature %d overflows its box" % f["num"])


def draw_index():
    y0 = 709
    section_head(16, y0, W - 32, "ALSO ON 19 NOVEMBER",
                 "STORIES 16-36")
    iy = y0 + 26
    colw = 492
    rowh = 25
    for i, (num, place, region, l1, l2) in enumerate(INDEX):
        col = i % 2
        row = i // 2
        x = 16 + col * (colw + 8)
        y = iy + row * rowh
        rc = REGION[region]
        fill_rect(x, y + 1, 26, 14, rc)
        ns = str(num)
        draw_text(x + (26 - text_w(ns, 1)) // 2, y + 4, ns, 1,
                  (255, 255, 255), True)
        head = "%s: %s" % (place, l1)
        if text_w(head, 2) > colw - 34:
            raise SystemExit("index %d line 1 too wide: %s" % (num, head))
        draw_text(x + 32, y, head, 2, INK, True)
        draw_text(x + 32, y + text_h(2) + 2, l2, 1, (70, 68, 62))


def draw_footer():
    draw_text_c(0, 1014, W,
                "Sources: AP, Reuters, BBC, Horizon, One Turn, The Hindu, ANI, IMD, Sotheby's, Nasdaq.",
                1, GREY)


def render():
    fill_rect(0, 0, W, H, CREAM)
    draw_masthead()
    draw_heroes()
    draw_map_section()
    draw_features()
    draw_index()
    draw_footer()


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    render()
    path = os.path.join(out_dir, "entry.png")
    size = write_png(path)
    print("wrote %s (%d bytes)" % (path, size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
