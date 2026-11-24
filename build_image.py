#!/usr/bin/env python3
"""Build-time renderer for the entry image (dev machine only; uses PIL).

The submitted program (main.py) is standard-library only: it copies the
pre-rendered entry.png asset to the output directory, as the competition
rules explicitly allow ("a repository holding the image and a one-line
program that copies it there"). This script is kept in the repository so
the image can be reproduced and revised.

Content: the world's news of Monday 23 November 2026, as reported that day
(UN News, Reuters via Just Security Early Edition, The Japan Times,
Principia's daily record, BBC headline lists).
"""
from PIL import Image, ImageDraw, ImageFont

W = H = 1024
BG = (247, 243, 234)        # newsprint
INK = (24, 28, 38)          # near-black
NAVY = (18, 38, 74)
RED = (178, 34, 44)
GREY = (96, 100, 108)
CARD = (255, 253, 248)
RULE = (24, 28, 38)

FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
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


def text_block(draw, xy, text, fnt, fill, max_w, leading=1.18):
    x, y = xy
    lines = wrap(draw, text, fnt, max_w)
    lh = int(fnt.size * leading)
    for ln in lines:
        draw.text((x, y), ln, font=fnt, fill=fill)
        y += lh
    return y


img = Image.new("RGB", (W, H), BG)
d = ImageDraw.Draw(img)

# ---------- masthead ----------
d.rectangle([0, 0, W, 148], fill=NAVY)
d.text((36, 18), "THE WORLD IN ONE DAY", font=font(FB, 57), fill=(255, 255, 255))
d.text((36, 88), "MONDAY  ·  23 NOVEMBER 2026", font=font(FB, 40), fill=(255, 196, 64))
d.text((W - 36, 96), "make.fun daily news", font=font(FR, 22), fill=(190, 200, 220), anchor="ra")

# ---------- lead story: COP31 ----------
LY = 162
LH = 242
d.rectangle([28, LY, W - 28, LY + LH], fill=CARD, outline=RULE, width=3)
d.rectangle([28, LY, 210, LY + LH], fill=(30, 92, 62))
# simple globe icon
cx, cy, r = 119, LY + 92, 46
d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=(255, 255, 255), width=5)
d.line([cx - r, cy, cx + r, cy], fill=(255, 255, 255), width=3)
d.line([cx, cy - r, cx, cy + r], fill=(255, 255, 255), width=3)
d.ellipse([cx - 20, cy - r, cx + 20, cy + r], outline=(255, 255, 255), width=3)
d.text((119, LY + 158), "CLIMATE", font=font(FB, 25), fill=(255, 255, 255), anchor="ma")
x = 232
d.text((x, LY + 16), "ANTALYA, TÜRKIYE — CLIMATE SUMMIT", font=font(FB, 21), fill=RED)
y = text_block(d, (x, LY + 48), "COP31 ENDS WITHOUT A DEAL",
               font(FB, 44), INK, W - 28 - x - 18, leading=1.1)
text_block(d, (x, y + 6),
           "The longest UN climate summit in history collapses over fossil "
           "fuels and finance. UN chief Guterres: \u201cdeeply disappointed.\u201d",
           font(FR, 24), (52, 56, 66), W - 28 - x - 18, leading=1.15)

# ---------- story cards ----------
stories = [
    ("LIBYA · WAR AT SEA", RED,
     "Ukraine sinks Russian warship off Libya",
     "Seven naval drones hit a Russian vessel at Benghazi; Zelenskyy confirms the strike as the war reaches the Mediterranean."),
    ("KYIV, UKRAINE", RED,
     "Russian strikes kill at least 15 near Kyiv",
     "Overnight bombardment destroys apartment blocks; a boy is pulled alive from the rubble, 14 people missing."),
    ("IRAN · MIDDLE EAST", (176, 96, 16),
     "Iran vows to defy U.S. naval blockade",
     "Tehran says it will use \u201call its tools\u201d; Trump threatens strikes after New Year if no deal is reached."),
    ("KHARTOUM, SUDAN", (176, 96, 16),
     "Drones hit homes and a U.N. building",
     "Strikes on Sudan's capital hit residential areas and a United Nations building, deepening the crisis."),
    ("INDONESIA", (146, 44, 120),
     "Sweets factory fire kills at least 24",
     "Blaze at a factory in Cikande; the search continues for about 30 people still missing."),
    ("SPACE · SCIENCE", (30, 92, 140),
     "Two probes reach Mercury at last",
     "Japan\u2013Europe BepiColombo orbiters enter orbit around Mercury after an eight-year journey."),
]

GX, GY = 28, 418
CW, CH, GAP = 484, 170, 8
for i, (kicker, kc, head, body) in enumerate(stories):
    col, row = i % 2, i // 2
    x0 = GX + col * (CW + GAP)
    y0 = GY + row * (CH + GAP)
    d.rectangle([x0, y0, x0 + CW, y0 + CH], fill=CARD, outline=(178, 172, 158), width=2)
    d.rectangle([x0, y0, x0 + CW, y0 + 32], fill=(238, 232, 218))
    d.text((x0 + 14, y0 + 5), kicker, font=font(FB, 20), fill=kc)
    y = text_block(d, (x0 + 14, y0 + 40), head, font(FB, 26), INK, CW - 28, leading=1.1)
    text_block(d, (x0 + 14, y + 2), body, font(FR, 19), (52, 56, 66), CW - 28, leading=1.12)

# ---------- markets strip ----------
MY = GY + 3 * (CH + GAP) + 4
d.rectangle([28, MY, W - 28, MY + 58], fill=NAVY)
d.text((44, MY + 6), "MARKETS", font=font(FB, 20), fill=(255, 196, 64))
d.text((44, MY + 31),
       "AI sell-off deepens in Asia  ·  Bitcoin rebounds to $61K after plunge to a two-year low",
       font=font(FB, 19), fill=(255, 255, 255))

img.save("entry.png", optimize=True)
print("wrote entry.png", img.size)
