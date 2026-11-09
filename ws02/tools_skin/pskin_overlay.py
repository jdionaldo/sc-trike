"""Overlay of the panel graph on sheet 68. usage: python tools_skin/pskin_overlay.py plan|side OUT.png  (reads the model built by pskin_build.model())"""
import sys
import numpy as np
from PIL import Image, ImageDraw
import pskin_core as C
SHEET = "ref68/sheet68.png"
BOX = dict(plan=(95, 40, 745, 380), side=(85, 440, 750, 720))


def draw(P, panels, view, out, scale=2, names=True, maskpoly=None):
    im = Image.open(SHEET).convert("RGB")
    box = BOX[view]
    im = im.crop(box).resize(((box[2] - box[0]) * scale, (box[3] - box[1]) * scale), Image.LANCZOS)
    d = ImageDraw.Draw(im, "RGBA")
    f = (lambda p: C.xy_plan(p[0], p[1])) if view == "plan" else (lambda p: C.xz_side(p[0], p[2]))
    def pt(p):
        a, b = f(p)
        return ((a - box[0]) * scale, (b - box[1]) * scale)
    for k, pn in enumerate(panels):
        pts = [pt(P[i]) for i in pn["ids"]]
        col = [(255, 0, 0), (0, 120, 255), (0, 170, 0), (200, 0, 200), (255, 140, 0)][k % 5]
        d.polygon(pts, fill=col + (28,), outline=col + (255,))
        if names:
            cx = sum(p[0] for p in pts) / len(pts); cy = sum(p[1] for p in pts) / len(pts)
            d.text((cx - 8, cy - 4), pn["name"], fill=(0, 0, 0, 255))
    if names:
        for n, p in P.items():
            a, b = pt(p)
            d.ellipse([a - 2, b - 2, a + 2, b + 2], fill=(255, 0, 0, 255))
            d.text((a + 3, b - 10), n, fill=(120, 0, 0, 255))
    if maskpoly is not None:
        d.line([pt(q) for q in maskpoly], fill=(0, 200, 0, 255), width=2)
    im.save(out)
