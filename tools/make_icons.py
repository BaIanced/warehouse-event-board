#!/usr/bin/env python3
"""Draws the app icons (calendar with a flame-orange 'busy' dot)."""
import os
from PIL import Image, ImageDraw

out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "icons")
os.makedirs(out, exist_ok=True)

def icon(size, maskable=False):
    s = size
    im = Image.new("RGBA", (s, s), (17, 20, 24, 255))
    d = ImageDraw.Draw(im)
    pad = int(s * (0.22 if maskable else 0.14))   # maskable keeps art inside the safe zone
    x0, y0, x1, y1 = pad, pad + int(s*0.04), s - pad, s - pad
    r = int(s * 0.06)
    d.rounded_rectangle([x0, y0, x1, y1], r, fill=(34, 41, 52, 255))
    bar = y0 + int((y1 - y0) * 0.24)
    d.rounded_rectangle([x0, y0, x1, bar], r, fill=(255, 122, 26, 255))
    d.rectangle([x0, bar - r, x1, bar], fill=(255, 122, 26, 255))
    # rings
    rw = int(s*0.035)
    for fx in (0.32, 0.68):
        cx = x0 + int((x1-x0)*fx)
        d.rounded_rectangle([cx-rw, y0-int(s*0.05), cx+rw, y0+int(s*0.06)], rw, fill=(238, 242, 246, 255))
    # 3x2 grid of day squares, one highlighted
    gx0, gy0 = x0 + int((x1-x0)*0.12), bar + int((y1-bar)*0.14)
    cw = int((x1-x0)*0.76/3); ch = int((y1-bar)*0.72/2); g = int(s*0.02)
    for row in range(2):
        for col in range(3):
            bx, by = gx0 + col*cw, gy0 + row*ch
            hot = (row, col) == (1, 1)
            d.rounded_rectangle([bx+g, by+g, bx+cw-g, by+ch-g], int(s*0.02),
                                fill=(255, 92, 138, 255) if hot else (60, 72, 88, 255))
    return im

icon(192).save(os.path.join(out, "icon-192.png"))
icon(512).save(os.path.join(out, "icon-512.png"))
icon(512, True).save(os.path.join(out, "icon-maskable-512.png"))
print("icons written")
