#!/usr/bin/env python3
"""news-image-20261123: draw a newspaper front page summing up the world
news of Monday 23 November 2026 and write it to /output/entry.png.

Pure Python 3.13 standard library (struct, zlib, os, shutil). No network,
no randomness, no time dependence: every run writes identical bytes.
The image is drawn, not copied: a 5x7 bitmap font, vector pictograms and
a front-page layout composed in code.
"""

import binascii
import os
import shutil
import struct
import sys
import zlib

W = 1024
H = 1024

# ---------------------------------------------------------------- palette
PAPER = (247, 243, 232)   # newsprint cream
INK = (18, 18, 18)
NAVY = (14, 42, 71)
RED = (178, 32, 44)
TEAL = (13, 92, 92)
GOLD = (201, 162, 39)
CREAM = (247, 243, 232)
DARK = (10, 38, 58)       # hero panel background
SEA = (18, 110, 130)      # globe ocean
LAND = (86, 140, 90)      # globe land
ORANGE = (214, 106, 24)
SMOKE = (150, 150, 148)
GREY = (96, 96, 96)
LIGHT = (214, 208, 192)   # light rule on dark

# ---------------------------------------------------------------- 5x7 font
# Each glyph is 7 rows of 5 pixels, '#' = on, '.' = off. Uppercase, digits
# and punctuation only; all image text is set in capitals.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '"': ("01010", "01010", "01010", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '+': ("00000", "00100", "00100", "01110", "00100", "00100", "00000"),
    '=': ("00000", "00000", "11111", "00000", "11111", "00000", "00000"),
    '*': ("00000", "10101", "01110", "10101", "00000", "00000", "00000"),
    '#': ("01010", "01010", "11111", "01010", "11111", "01010", "01010"),
    '_': ("00000", "00000", "00000", "00000", "00000", "00000", "11111"),
    '\u2022': ("00000", "00000", "01100", "01100", "01100", "00000", "00000"),
}


def _chunk(tag, data):
    body = struct.pack(">I", len(data)) + tag + data
    return body + struct.pack(">I", binascii.crc32(tag + data) & 0xFFFFFFFF)


def png_bytes(w, h, rgb):
    """Encode an RGB bytearray as a deterministic PNG (filter 0, level 6)."""
    ihdr = struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0)
    raw = bytearray()
    stride = w * 3
    for y in range(h):
        raw.append(0)
        raw += rgb[y * stride:(y + 1) * stride]
    idat = zlib.compress(bytes(raw), 6)
    return (
        b"\x89PNG\r\n\x1a\n"
        + _chunk(b"IHDR", ihdr)
        + _chunk(b"IDAT", idat)
        + _chunk(b"IEND", b"")
    )


class Canvas:
    def __init__(self, w, h, bg):
        self.w = w
        self.h = h
        self.buf = bytearray(w * h * 3)
        r, g, b = bg
        for i in range(0, len(self.buf), 3):
            self.buf[i] = r
            self.buf[i + 1] = g
            self.buf[i + 2] = b

    def px(self, x, y, c):
        if 0 <= x < self.w and 0 <= y < self.h:
            i = (y * self.w + x) * 3
            self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def rect(self, x, y, w, h, c):
        x0, y0 = max(0, x), max(0, y)
        x1, y1 = min(self.w, x + w), min(self.h, y + h)
        for yy in range(y0, y1):
            base = (yy * self.w + x0) * 3
            for xx in range(x0, x1):
                i = base + (xx - x0) * 3
                self.buf[i], self.buf[i + 1], self.buf[i + 2] = c

    def border(self, x, y, w, h, c, t=2):
        self.rect(x, y, w, t, c)
        self.rect(x, y + h - t, w, t, c)
        self.rect(x, y, t, h, c)
        self.rect(x + w - t, y, t, h, c)

    def hline(self, x, y, w, c, t=1):
        self.rect(x, y, w, t, c)

    def circle(self, cx, cy, r, c):
        for yy in range(cy - r, cy + r + 1):
            dy = yy - cy
            dx = int((r * r - dy * dy) ** 0.5) if abs(dy) <= r else 0
            for xx in range(cx - dx, cx + dx + 1):
                self.px(xx, yy, c)

    def ring(self, cx, cy, r, c, t=3):
        for yy in range(cy - r, cy + r + 1):
            for xx in range(cx - r, cx + r + 1):
                d2 = (xx - cx) ** 2 + (yy - cy) ** 2
                if (r - t) ** 2 <= d2 <= r * r:
                    self.px(xx, yy, c)

    def line(self, x0, y0, x1, y1, c, t=1):
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            if t <= 1:
                self.px(x, y, c)
            else:
                self.circle(x, y, t // 2, c)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def polyline(self, pts, c, t=1):
        for a, b in zip(pts, pts[1:]):
            self.line(a[0], a[1], b[0], b[1], c, t)

    def triangle(self, p0, p1, p2, c):
        xs = [p0[0], p1[0], p2[0]]
        ys = [p0[1], p1[1], p2[1]]
        x0, x1 = min(xs), max(xs)
        y0, y1 = min(ys), max(ys)

        def sign(ax, ay, bx, by, cx, cy):
            return (ax - cx) * (by - cy) - (bx - cx) * (ay - cy)

        d = sign(p0[0], p0[1], p1[0], p1[1], p2[0], p2[1])
        if d == 0:
            return
        for yy in range(y0, y1 + 1):
            for xx in range(x0, x1 + 1):
                d0 = sign(xx, yy, p0[0], p0[1], p1[0], p1[1])
                d1 = sign(xx, yy, p1[0], p1[1], p2[0], p2[1])
                d2 = sign(xx, yy, p2[0], p2[1], p0[0], p0[1])
                neg = (d0 < 0) or (d1 < 0) or (d2 < 0)
                pos = (d0 > 0) or (d1 > 0) or (d2 > 0)
                if not (neg and pos):
                    self.px(xx, yy, c)


# ---------------------------------------------------------------- text
def text_width(s, text):
    """Pixel width of text at scale s (advance 6*s per glyph)."""
    return len(text) * 6 * s - s if text else 0


def draw_text(cv, x, y, s, text, color, align="left"):
    """Draw text with its top-left at (x, y); align left/center/right."""
    if align == "center":
        x -= text_width(s, text) // 2
    elif align == "right":
        x -= text_width(s, text)
    cx = x
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == "1":
                    cv.rect(cx + col * s, y + row * s, s, s, color)
        cx += 6 * s
    return cx


def wrap_text(text, s, max_w):
    """Greedy word wrap to lines no wider than max_w at scale s."""
    words = text.split(" ")
    lines, cur = [], ""
    for word in words:
        trial = word if not cur else cur + " " + word
        if text_width(s, trial) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def para(cv, x, y, s, text, color, max_w, line_h, align="left"):
    """Draw a wrapped paragraph; return the y below the last line."""
    for line in wrap_text(text, s, max_w):
        draw_text(cv, x, y, s, line, color, align=align)
        y += line_h
    return y


# ---------------------------------------------------------------- pictograms
def draw_globe(cv, cx, cy, r):
    """Cracked globe: ocean disc, land blobs, gold ring, orange crack."""
    cv.circle(cx, cy, r, SEA)
    # land masses as overlapping discs
    for (lx, ly, lr) in [
        (cx - 42, cy - 38, 30), (cx - 18, cy - 52, 22), (cx + 40, cy - 30, 26),
        (cx + 55, cy + 5, 20), (cx - 55, cy + 25, 24), (cx + 5, cy + 48, 26),
        (cx - 8, cy + 8, 18), (cx + 28, cy + 55, 16),
    ]:
        cv.circle(lx, ly, lr, LAND)
    # re-clip land to the disc: paint the ring band back over spillover
    cv.ring(cx, cy, r + 2, DARK, 4)
    cv.ring(cx, cy, r, GOLD, 3)
    # crack: jagged orange line from top to bottom of the disc
    crack = [
        (cx - 6, cy - r + 6), (cx + 14, cy - 62), (cx - 10, cy - 34),
        (cx + 18, cy - 8), (cx - 14, cy + 20), (cx + 10, cy + 48),
        (cx - 4, cy + 72), (cx + 8, cy + r - 4),
    ]
    cv.polyline(crack, ORANGE, 4)
    cv.polyline([(cx - 6, cy - r + 6), (cx + 14, cy - 62)], (255, 190, 90), 2)
    # heat rays above the globe
    for dx, ln in [(-70, 22), (-35, 30), (0, 34), (35, 30), (70, 22)]:
        cv.line(cx + dx, cy - r - 12, cx + dx, cy - r - 12 - ln, ORANGE, 3)


def draw_tanker(cv, x, y, w, h):
    """Small oil tanker with smoke and missile streaks, inside (x, y, w, h)."""
    # sky streaks: two missiles arcing in
    cv.line(x + 8, y + 6, x + 60, y + 26, ORANGE, 2)
    cv.line(x + 30, y + 2, x + 78, y + 22, RED, 2)
    # smoke puffs
    for (sx, sy, sr) in [(x + w - 60, y + 14, 7), (x + w - 46, y + 8, 9),
                         (x + w - 30, y + 14, 6)]:
        cv.circle(sx, sy, sr, SMOKE)
    # hull
    hull_top = y + h - 16
    cv.rect(x + 6, hull_top, w - 12, 12, INK)
    cv.triangle((x + 6, hull_top), (x + 6, hull_top + 12),
                (x + 26, hull_top + 12), INK)
    # containers
    cv.rect(x + 34, hull_top - 12, 44, 12, RED)
    cv.rect(x + 82, hull_top - 12, 44, 12, NAVY)
    cv.rect(x + 130, hull_top - 12, 44, 12, GOLD)
    # bridge tower
    cv.rect(x + w - 34, hull_top - 26, 22, 26, INK)
    cv.rect(x + w - 30, hull_top - 22, 14, 4, CREAM)
    # waves
    for wx in range(x, x + w, 26):
        cv.line(wx, y + h - 2, wx + 12, y + h - 2, TEAL, 2)


def draw_factory(cv, x, y, w, h):
    """Factory with sawtooth roof, flames and smoke, inside (x, y, w, h)."""
    base = y + h - 8
    # smoke
    for (sx, sy, sr) in [(x + 30, y + 10, 10), (x + 48, y + 4, 12),
                         (x + 68, y + 12, 8)]:
        cv.circle(sx, sy, sr, SMOKE)
    # chimney
    cv.rect(x + 22, y + 22, 14, base - (y + 22), INK)
    cv.rect(x + 18, y + 18, 22, 6, INK)
    # main block
    bx = x + 44
    bw = w - 60
    cv.rect(bx, y + 44, bw, base - (y + 44), NAVY)
    # sawtooth roof: three teeth across the block
    tooth = bw // 3
    for i in range(3):
        tx = bx + i * tooth
        cv.triangle((tx, y + 44), (tx + tooth, y + 44),
                    (tx + tooth // 2, y + 22), NAVY)
    # windows
    for wx in range(bx + 10, bx + bw - 18, 34):
        cv.rect(wx, base - 18, 18, 12, GOLD)
    # flames licking the roofline
    for fx in (bx + bw // 4, bx + bw // 2, bx + 3 * bw // 4):
        cv.triangle((fx, y + 46), (fx + 12, y + 46), (fx + 6, y + 26), ORANGE)
        cv.triangle((fx + 3, y + 46), (fx + 9, y + 46), (fx + 6, y + 34), RED)


def draw_flags(cv, x, y):
    """India tricolour and Nepal crimson pennant on poles."""
    # India: saffron / white / green with navy wheel dot
    cv.rect(x, y, 4, 64, INK)
    cv.rect(x + 4, y, 66, 12, (255, 153, 51))
    cv.rect(x + 4, y + 12, 66, 12, CREAM)
    cv.rect(x + 4, y + 24, 66, 12, (19, 136, 8))
    cv.circle(x + 37, y + 18, 5, NAVY)
    # Nepal: crimson double pennant
    cv.rect(x + 110, y, 4, 64, INK)
    cv.triangle((x + 114, y), (x + 114, y + 20), (x + 164, y + 14), RED)
    cv.triangle((x + 114, y + 20), (x + 114, y + 40), (x + 158, y + 34), RED)
    cv.circle(x + 126, y + 10, 3, CREAM)
    cv.circle(x + 126, y + 30, 3, CREAM)


# ---------------------------------------------------------------- the page
def compose():
    cv = Canvas(W, H, PAPER)
    # masthead
    cv.rect(28, 24, 968, 80, NAVY)
    draw_text(cv, 512, 40, 7, "THE WORLD", CREAM, align="center")
    draw_text(cv, 44, 62, 2, "WORLD NEWS", CREAM)
    draw_text(cv, 980, 62, 2, "ONE IMAGE", CREAM, align="right")
    # red rule + date line
    cv.rect(28, 108, 968, 4, RED)
    draw_text(cv, 512, 122, 3, "MONDAY, 23 NOVEMBER 2026", RED, align="center")
    cv.hline(28, 152, 968, INK, 2)
    # main headline + deck
    draw_text(cv, 512, 166, 9, "COP31 COLLAPSES", INK, align="center")
    para(cv, 512, 240, 3,
         "NO DEAL IN ANTALYA AS THE FOSSIL-FUEL ROW SINKS TWO WEEKS "
         "OF CLIMATE TALKS", INK, 900, 26, align="center")
    # hero panel: cracked globe, NO DEAL banner, caption
    cv.rect(28, 296, 612, 308, DARK)
    cv.border(28, 296, 612, 308, INK, 2)
    draw_text(cv, 44, 308, 2, "ANTALYA, TURKIYE", GOLD)
    draw_globe(cv, 334, 448, 100)
    cv.rect(234, 428, 200, 44, RED)
    draw_text(cv, 334, 436, 4, "NO DEAL", CREAM, align="center")
    cv.rect(28, 556, 612, 48, NAVY)
    draw_text(cv, 334, 566, 2, "THE ANTALYA PACT REJECTED", CREAM, align="center")
    draw_text(cv, 334, 584, 2, "AS EU AND ALLIES SAY NO", CREAM, align="center")
    # right column, panel A: Gulf war widens
    cv.rect(656, 296, 340, 160, PAPER)
    cv.border(656, 296, 340, 160, INK, 2)
    draw_text(cv, 672, 304, 4, "GULF WAR", INK)
    draw_text(cv, 672, 332, 4, "WIDENS", INK)
    draw_tanker(cv, 668, 362, 316, 42)
    para(cv, 672, 410, 2,
         "IRAN HITS U.S. BASES IN BAHRAIN; TANKERS STRUCK IN HORMUZ",
         INK, 308, 15)
    # right column, panel B: Democrats win 258 seats
    cv.rect(656, 464, 340, 140, PAPER)
    cv.border(656, 464, 340, 140, INK, 2)
    draw_text(cv, 672, 470, 4, "DEMOCRATS WIN", INK)
    draw_text(cv, 672, 498, 4, "258 SEATS", INK)
    cv.rect(672, 530, 152, 34, NAVY)
    draw_text(cv, 748, 540, 3, "DEM 258", CREAM, align="center")
    cv.rect(832, 530, 152, 34, RED)
    draw_text(cv, 908, 540, 3, "GOP 173", CREAM, align="center")
    draw_text(cv, 672, 570, 2, "BIGGEST MAJORITY", INK)
    draw_text(cv, 672, 584, 2, "SINCE 1992", INK)
    # mid row, panel C: factory fire in Indonesia
    cv.rect(28, 620, 472, 172, PAPER)
    cv.border(28, 620, 472, 172, INK, 2)
    draw_text(cv, 44, 632, 4, "FACTORY FIRE", INK)
    draw_text(cv, 44, 660, 4, "IN INDONESIA", INK)
    draw_factory(cv, 336, 632, 148, 76)
    para(cv, 44, 716, 2,
         "DOZENS OF WORKERS MISSING AFTER BLAZE AT CANDY PLANT. "
         "AT LEAST THREE DEAD.", INK, 440, 15)
    # mid row, panel D: Nepal PM meets Modi
    cv.rect(524, 620, 472, 172, PAPER)
    cv.border(524, 620, 472, 172, INK, 2)
    draw_text(cv, 540, 632, 4, "NEPAL PM MEETS MODI", INK)
    draw_flags(cv, 540, 676)
    para(cv, 540, 748, 2,
         "BALENDRA SHAH IN DELHI FOR TALKS ON TRADE AND TIES",
         INK, 440, 15)
    # in brief
    draw_text(cv, 28, 812, 3, "IN BRIEF", RED)
    cv.hline(28, 836, 968, INK, 2)
    briefs_left = [
        "U.N. TO KEEP TALKING ON LETHAL AI WEAPONS",
        "S. KOREA MINISTER QUITS OVER AI EXAM CHEATING",
        "ANTHROPIC MAKES RECORD NASDAQ DEBUT",
    ]
    briefs_right = [
        "'SUNRISE ON THE REAPING' TOPS BOX OFFICE, $120M",
        "RUSSIAN SHIP STILL BURNING OFF FINLAND",
        "14 MISSING AFTER DRONE HIT NEAR KYIV",
    ]
    for col_x, items in ((28, briefs_left), (524, briefs_right)):
        y = 848
        for item in items:
            draw_text(cv, col_x, y, 2, "\u2022", RED)
            para(cv, col_x + 16, y, 2, item, INK, 440, 15)
            y += 40
    # footer
    cv.hline(28, 976, 968, INK, 2)
    draw_text(cv, 512, 984, 2,
              "THE WORLD \u2022 23 NOVEMBER 2026 \u2022 ALL STORIES VERIFIED "
              "FROM THE DAY'S REPORTING", GREY, align="center")
    return cv


def write_output(data):
    """Write entry.png into the output dir, clearing only its contents."""
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    for name in os.listdir(out_dir):
        path = os.path.join(out_dir, name)
        try:
            if os.path.isdir(path) and not os.path.islink(path):
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)
        except OSError:
            pass  # a stray foreign-owned file must not fail the run
    target = os.path.join(out_dir, "entry.png")
    with open(target, "wb") as f:
        f.write(data)
    return target


def main():
    cv = compose()
    data = png_bytes(W, H, cv.buf)
    if len(data) > 1048576:
        print("entry.png too large: %d bytes" % len(data), file=sys.stderr)
        return 1
    target = write_output(data)
    print("wrote %s (%d bytes, %dx%d)" % (target, len(data), W, H))
    return 0


if __name__ == "__main__":
    sys.exit(main())
