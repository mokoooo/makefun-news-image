#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build-time renderer for the entry image (dev machine only; uses PIL).

The submitted program (main.py) is standard-library only: it copies the
pre-rendered entry.png asset to the output directory, as the competition
rules explicitly allow ("a repository holding the image and a one-line
program that copies it there"). This script is kept in the repository so
the image can be reproduced and revised.

This is the final Phase 2 version: a classic newspaper front page whose
copy was fact-checked line by line against the day's reporting. It is a
single self-contained file (story copy, drawing helpers and icons are
inlined below) and renders deterministically: same input, same bytes.

Corrections versus the first submitted version, all verified against
primary or wire reporting: the BepiColombo item no longer says two
probes "reach Mercury" on the day -- orbit insertion was Saturday
21 November, ESA's Monday news was the safe-mode scare, and the two
orbiters stay joined until 9 December. The Kyiv item now uses the
region-wide death toll, the single destroyed apartment block in Dymer,
and the updated figure of two people missing (not the superseded 14).
The Libya sinking is attributed to Kyiv's claim with the satellite
corroboration noted, and the Khartoum item carries the death toll and
the RSF attribution.
"""
import os
from PIL import Image, ImageDraw, ImageFont

# ================= fonts and palette =================

SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_R = "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

INK = (24, 28, 38)
BODY = (46, 50, 60)
PAPER = (247, 243, 234)
CARD = (255, 253, 248)
NAVY = (18, 38, 74)
AMBER = (255, 196, 64)
RULE_SOFT = (178, 172, 158)
WHITE = (255, 255, 255)


def F(path, size):
    return ImageFont.truetype(path, size)


def wrap(draw, text, fnt, max_w):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if draw.textlength(t, font=fnt) <= max_w:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w_
    if cur:
        lines.append(cur)
    return lines


def text_block(draw, xy, text, fnt, fill, max_w, leading=1.16):
    """Draw wrapped text; return the y just past the last line."""
    x, y = xy
    lh = int(fnt.size * leading)
    for ln in wrap(draw, text, fnt, max_w):
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


def n_lines(draw, text, fnt, max_w):
    return len(wrap(draw, text, fnt, max_w))


# ================= icons (white line-art on a coloured chip) =================

def _globe(d, cx, cy, r, fg, w):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=fg, width=w)
    d.line([cx - r, cy, cx + r, cy], fill=fg, width=max(2, w - 1))
    d.ellipse([cx - r * 0.45, cy - r, cx + r * 0.45, cy + r], outline=fg, width=max(2, w - 1))
    yy = int(r * 0.52)
    d.line([cx - int(r * 0.86), cy - yy, cx + int(r * 0.86), cy - yy], fill=fg, width=max(2, w - 1))
    d.line([cx - int(r * 0.86), cy + yy, cx + int(r * 0.86), cy + yy], fill=fg, width=max(2, w - 1))


def _ship(d, cx, cy, r, fg, w):
    hull = [(cx - r, cy - r * 0.05), (cx + r, cy - r * 0.05),
            (cx + r * 0.7, cy + r * 0.4), (cx - r * 0.7, cy + r * 0.4)]
    d.polygon(hull, fill=fg)
    d.rectangle([cx - r * 0.42, cy - r * 0.55, cx + r * 0.05, cy - r * 0.05], fill=fg)
    d.line([cx + r * 0.42, cy - r * 0.85, cx + r * 0.42, cy - r * 0.05], fill=fg, width=w)
    d.line([cx - r * 0.85, cy + r * 0.72, cx - r * 0.3, cy + r * 0.72], fill=fg, width=max(2, w - 1))
    d.line([cx - r * 0.12, cy + r * 0.72, cx + r * 0.43, cy + r * 0.72], fill=fg, width=max(2, w - 1))
    d.line([cx + r * 0.6, cy + r * 0.72, cx + r * 0.9, cy + r * 0.72], fill=fg, width=max(2, w - 1))


def _building(d, cx, cy, r, fg, w):
    x0, y0, x1, y1 = cx - r * 0.55, cy - r, cx + r * 0.55, cy + r * 0.8
    d.rectangle([x0, y0, x1, y1], outline=fg, width=w)
    s = r * 0.22
    for r_ in range(3):
        for c_ in range(2):
            wx = x0 + r * 0.18 + c_ * r * 0.42
            wy = y0 + r * 0.22 + r_ * r * 0.5
            d.rectangle([wx, wy, wx + s * 0.8, wy + s * 0.8], fill=fg)
    d.line([cx + r * 0.1, y0, cx - r * 0.05, cy - r * 0.2, cx + r * 0.18, cy + r * 0.25,
            cx - r * 0.02, y1], fill=fg, width=max(2, w - 1))
    d.line([cx - r, cy + r, cx + r, cy + r], fill=fg, width=w)


def _anchor(d, cx, cy, r, fg, w):
    rr = r * 0.22
    d.ellipse([cx - rr, cy - r, cx + rr, cy - r + 2 * rr], outline=fg, width=w)
    d.line([cx, cy - r + 2 * rr, cx, cy + r * 0.75], fill=fg, width=w)
    d.line([cx - r * 0.55, cy - r * 0.35, cx + r * 0.55, cy - r * 0.35], fill=fg, width=w)
    d.arc([cx - r * 0.8, cy - r * 0.1, cx + r * 0.8, cy + r * 1.15], 20, 160, fill=fg, width=w)
    d.polygon([(cx - r * 0.8, cy + r * 0.32), (cx - r * 0.52, cy + r * 0.3),
               (cx - r * 0.72, cy + r * 0.62)], fill=fg)
    d.polygon([(cx + r * 0.8, cy + r * 0.32), (cx + r * 0.52, cy + r * 0.3),
               (cx + r * 0.72, cy + r * 0.62)], fill=fg)


def _drone(d, cx, cy, r, fg, w):
    for dx, dy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        px, py = cx + dx * r * 0.72, cy + dy * r * 0.62
        d.line([cx, cy, px, py], fill=fg, width=w)
        pr = r * 0.3
        d.ellipse([px - pr, py - pr * 0.45, px + pr, py + pr * 0.45], outline=fg, width=max(2, w - 1))
    d.rectangle([cx - r * 0.3, cy - r * 0.22, cx + r * 0.3, cy + r * 0.22], outline=fg, width=w)
    d.ellipse([cx - r * 0.1, cy - r * 0.1, cx + r * 0.1, cy + r * 0.1], fill=fg)


def _flame(d, cx, cy, r, fg, w):
    shape = [(0.0, -1.0), (0.3, -0.5), (0.58, -0.08), (0.62, 0.3),
             (0.45, 0.72), (0.2, 0.92), (-0.2, 0.92), (-0.45, 0.72),
             (-0.62, 0.3), (-0.55, -0.1), (-0.28, -0.42)]
    pts = [(cx + x * r * 0.9, cy + y * r) for x, y in shape]
    d.polygon(pts, outline=fg, width=w)
    inner = [(x * 0.45, y * 0.45 + 0.38) for x, y in shape]
    d.polygon([(cx + x * r * 0.9, cy + y * r) for x, y in inner], fill=fg)


def _planet(d, cx, cy, r, fg, w):
    pr = r * 0.55
    d.ellipse([cx - pr, cy - pr, cx + pr, cy + pr], outline=fg, width=w)
    d.arc([cx - pr, cy - pr, cx + pr, cy + pr], 200, 320, fill=fg, width=max(2, w - 1))
    d.ellipse([cx - r * 1.02, cy - r * 0.32, cx + r * 1.02, cy + r * 0.32],
              outline=fg, width=max(2, w - 1))
    for dx, dy, s in ((-0.85, -0.8, 3), (0.9, -0.62, 2)):
        px, py = cx + dx * r, cy + dy * r
        d.line([px - s, py, px + s, py], fill=fg, width=2)
        d.line([px, py - s, px, py + s], fill=fg, width=2)


def _chart(d, cx, cy, r, fg, w):
    d.line([cx - r, cy + r * 0.85, cx + r, cy + r * 0.85], fill=fg, width=max(2, w - 1))
    pts = [(cx - r * 0.9, cy - r * 0.5), (cx - r * 0.45, cy - r * 0.05),
           (cx - r * 0.05, cy + r * 0.45), (cx + r * 0.35, cy + r * 0.1),
           (cx + r * 0.85, cy - r * 0.7)]
    d.line(pts, fill=fg, width=w)
    d.polygon([(cx + r * 0.85, cy - r * 0.7), (cx + r * 0.6, cy - r * 0.62),
               (cx + r * 0.78, cy - r * 0.42)], fill=fg)


ICONS = {"globe": _globe, "ship": _ship, "building": _building,
         "anchor": _anchor, "drone": _drone, "flame": _flame,
         "planet": _planet, "chart": _chart}


def icon_chip(d, kind, x, y, size, bg, fg=WHITE):
    """Draw a square chip with a centred white line icon."""
    d.rectangle([x, y, x + size, y + size], fill=bg)
    r = size * 0.36
    w = max(2, size // 16)
    ICONS[kind](d, x + size / 2, y + size / 2, r, fg, w)


# ================= story copy (fact-checked) =================
# Every line follows the Phase 1 fact-check. In particular:
# - BepiColombo: orbit insertion was Sat 21 Nov; ESA's detailed report
#   came Monday 23 Nov. The MPO+Mio stack is still joined; separation
#   is 9 Dec. A software fault cut a thruster burn short and triggered
#   safe mode. Never "two probes enter orbit".
# - Kyiv: the 15 dead are the Kyiv REGION total. The destroyed
#   residential building is ONE apartment block in Dymer. The missing
#   figure uses the later official update (2), not the superseded 14.
# - Libya: the sinking is Kyiv's claim, backed by satellite imagery
#   showing the corvette capsized at Benghazi.

TITLE = "THE WORLD IN ONE DAY"
DATE_LINE = "MONDAY · 23 NOVEMBER 2026"

# Category colours: climate=green, war=red, diplomacy=amber,
# disaster=purple, science=blue, markets=navy.
CAT = {
    "climate": (30, 92, 62),
    "war": (178, 34, 44),
    "diplomacy": (176, 96, 16),
    "disaster": (146, 44, 120),
    "science": (30, 92, 140),
    "markets": (18, 38, 74),
}

LEAD = {
    "kicker": "ANTALYA, TÜRKIYE · CLIMATE SUMMIT",
    "cat": "climate",
    "icon": "globe",
    "place": "Antalya, Türkiye",
    "headline": "COP31 ENDS WITHOUT A DEAL",
    "body": ("The longest UN climate summit in history breaks up after two "
             "extra days, deadlocked over fossil fuels and finance."),
    "quote": "“Deeply disappointed.” — UN chief António Guterres",
    "short": "Longest COP ever ends deadlocked over fossil fuels and finance",
}

STORIES = [
    {
        "kicker": "LIBYA · WAR AT SEA", "cat": "war", "icon": "ship",
        "place": "Benghazi, Libya",
        "headline": "Ukraine sinks Russian corvette off Libya",
        "body": ("Kyiv says seven naval drones struck the corvette Merkury "
                 "at Benghazi; satellite images show it capsized."),
        "short": "Seven naval drones strike the corvette Merkury at Benghazi",
    },
    {
        "kicker": "KYIV REGION, UKRAINE · WAR", "cat": "war", "icon": "building",
        "place": "Kyiv region, Ukraine",
        "headline": "Russian strikes kill at least 15 in Kyiv region",
        "body": ("An apartment block in Dymer was destroyed; a 7-year-old "
                 "boy was pulled alive from the rubble. Two remain missing."),
        "short": "Apartment block destroyed in Dymer; boy rescued alive",
    },
    {
        "kicker": "IRAN · MIDDLE EAST", "cat": "diplomacy", "icon": "anchor",
        "place": "Tehran, Iran",
        "headline": "Iran vows to defy U.S. naval blockade",
        "body": ("Tehran says it will use “all its tools” against the "
                 "blockade; Trump leans toward new strikes if no deal."),
        "short": "Tehran will use “all its tools” against the blockade",
    },
    {
        "kicker": "KHARTOUM, SUDAN · WAR", "cat": "war", "icon": "drone",
        "place": "Khartoum, Sudan",
        "headline": "Drones hit homes and a U.N. building",
        "body": ("Four people were killed as drones struck homes and a "
                 "U.N. building with staff inside; blamed on the RSF."),
        "short": "Four killed; U.N. building with staff inside is hit",
    },
    {
        "kicker": "INDONESIA · DISASTER", "cat": "disaster", "icon": "flame",
        "place": "Cikande, Indonesia",
        "headline": "Sweets factory fire kills at least 24",
        "body": ("The blaze at a Cikande factory was confirmed Monday to "
                 "have killed at least 24; about 30 are still missing."),
        "short": "Factory blaze in Cikande; about 30 still missing",
    },
    {
        "kicker": "SPACE · SCIENCE", "cat": "science", "icon": "planet",
        "place": "Mercury orbit",
        "headline": "BepiColombo safe in Mercury orbit despite glitch",
        "body": ("ESA confirmed Monday the Japan–Europe probe reached "
                 "Mercury orbit on Saturday, despite a software fault that "
                 "cut a thruster burn short and triggered safe mode. Its "
                 "two orbiters stay joined until 9 December."),
        "short": "In orbit after a safe-mode scare; orbiters split 9 Dec",
    },
]

MARKETS = {
    "kicker": "MARKETS", "cat": "markets", "icon": "chart",
    "place": "Asian markets",
    "headline": "AI sell-off deepens in Asia",
    "body": ("Seoul’s KOSPI falls 3.3% · Bitcoin rebounds to $61K after "
             "plunging to a two-year low"),
    "short": "KOSPI −3.3% · Bitcoin rebounds to $61K",
}

# ================= render =================

W = H = 1024
M = 28
RED = CAT["war"]
warn = []

img = Image.new("RGB", (W, H), PAPER)
d = ImageDraw.Draw(img)

# ---------------- masthead (classic newspaper) ----------------
d.rectangle([M, 16, W - M, 21], fill=INK)
d.rectangle([M, 26, W - M, 28], fill=INK)
tf = F(SERIF_B, 63)
tw = d.textlength(TITLE, font=tf)
d.text(((W - tw) / 2, 34), TITLE, font=tf, fill=INK)
df = F(SANS_B, 32)
dw = d.textlength(DATE_LINE, font=df)
d.text(((W - dw) / 2, 106), DATE_LINE, font=df, fill=RED)
d.rectangle([M, 146, W - M, 148], fill=INK)
d.rectangle([M, 152, W - M, 157], fill=INK)

# Card-length body overrides (same facts, tighter wording for the grid).
CARD_BODY = {
    5: ("ESA confirmed Monday the Japan–Europe probe is in Mercury orbit "
        "(arrived Saturday) despite a safe-mode scare; its two orbiters "
        "separate 9 December."),
}

# ---------------- lead story ----------------
LY, LH = 168, 216
d.rectangle([M, LY, W - M, LY + LH], fill=CARD, outline=INK, width=3)
PW = 196
d.rectangle([M, LY, M + PW, LY + LH], fill=CAT[LEAD["cat"]])
icon_chip(d, LEAD["icon"], M + 58, LY + 26, 80, CAT[LEAD["cat"]])
d.text((M + PW / 2, LY + 122), "CLIMATE", font=F(SANS_B, 24), fill=WHITE, anchor="ma")
d.text((M + PW / 2, LY + 156), "ANTALYA", font=F(SANS_B, 20), fill=(210, 235, 220), anchor="ma")
d.text((M + PW / 2, LY + 184), "TÜRKIYE", font=F(SANS_B, 20), fill=(210, 235, 220), anchor="ma")
x = M + PW + 24
tx_w = W - M - x - 20
d.text((x, LY + 14), LEAD["kicker"], font=F(SANS_B, 21), fill=RED)
hf = F(SERIF_B, 47)
hl = wrap(d, LEAD["headline"], hf, tx_w)
if len(hl) > 2:
    warn.append(f"lead headline {len(hl)} lines")
y = LY + 46
for ln in hl:
    d.text((x, y), ln, font=hf, fill=INK)
    y += 52
bf = F(SANS_R, 23)
bl = wrap(d, LEAD["body"], bf, tx_w)
if len(bl) > 3:
    warn.append(f"lead body {len(bl)} lines")
for ln in bl:
    d.text((x, y + 4), ln, font=bf, fill=BODY)
    y += 27
qf = F(SERIF_I, 23)
d.text((x, LY + LH - 40), LEAD["quote"], font=qf, fill=NAVY)
if y + 4 > LY + LH - 44:
    warn.append("lead body crowds the quote line")

# ---------------- story cards ----------------
GY = LY + LH + 12
CW, CHH, GAP = 484, 178, 8
body_f = F(SANS_R, 19)
head_f = F(SERIF_B, 26)
kick_f = F(SANS_B, 19)
for i, s in enumerate(STORIES):
    col, row = i % 2, i // 2
    x0 = M + col * (CW + GAP)
    y0 = GY + row * (CHH + GAP)
    d.rectangle([x0, y0, x0 + CW, y0 + CHH], fill=CARD, outline=RULE_SOFT, width=2)
    icon_chip(d, s["icon"], x0 + 12, y0 + 10, 34, CAT[s["cat"]])
    d.text((x0 + 56, y0 + 16), s["kicker"], font=kick_f, fill=CAT[s["cat"]])
    hl = wrap(d, s["headline"], head_f, CW - 24)
    if len(hl) > 2:
        warn.append(f"card {i} headline {len(hl)} lines")
    y = y0 + 50
    for ln in hl:
        d.text((x0 + 12, y), ln, font=head_f, fill=INK)
        y += 28
    bl = wrap(d, CARD_BODY.get(i, s["body"]), body_f, CW - 24)
    if len(bl) > 3:
        warn.append(f"card {i} body {len(bl)} lines")
    yy = y0 + 108
    for ln in bl:
        d.text((x0 + 12, yy), ln, font=body_f, fill=BODY)
        yy += 20
    if yy > y0 + CHH - 5:
        warn.append(f"card {i} body overflows card")

# ---------------- markets strip ----------------
MY = GY + 3 * (CHH + GAP) + 8
d.rectangle([M, MY, W - M, MY + 46], fill=NAVY)
d.text((M + 16, MY + 5), "MARKETS", font=F(SANS_B, 15), fill=AMBER)
mf = F(SANS_B, 18)
mt = "AI sell-off deepens in Asia · KOSPI −3.3% · Bitcoin rebounds to $61K after a two-year-low plunge"
if d.textlength(mt, font=mf) > W - 2 * M - 32:
    warn.append("markets line too wide")
d.text((M + 16, MY + 22), mt, font=mf, fill=WHITE)

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "entry.png")
img.quantize(colors=256, method=Image.MEDIANCUT).save(out, optimize=True)
print("wrote", out, os.path.getsize(out), "bytes")
for w_ in warn:
    print("WARN:", w_)
if not warn:
    print("fit check: clean")
