"""Labelled dot-map of the panel-graph vertices over the sheet-68 orthographic views (top, side, front, rear). usage: python tools_skin/pskin_dotmap.py [prefix]"""
import sys
import numpy as np
from PIL import Image, ImageDraw
import pskin_build as B, pskin_core as C
pre = sys.argv[1] if len(sys.argv) > 1 else "out/pskin/dots_"
SHEET = Image.open("ref68/sheet68.png").convert("RGB")
FR = dict(s=0.60, cx=1212.0, g=382.0); RR = dict(s=0.66, cx=1721.0, g=382.0)
VIEWS = dict(top=(95, 40, 745, 380), side=(85, 440, 750, 720), front=(985, 20, 1445, 395), rear=(1495, 20, 1990, 395))
def to_px(view, p):
    x, y, z = p
    if view == "top": return C.xy_plan(x, y)
    if view == "side": return C.xz_side(x, z)
    if view == "front": return FR["cx"] + y / FR["s"], FR["g"] - z / FR["s"]
    return RR["cx"] - y / RR["s"], RR["g"] - z / RR["s"]
def draw(m, view, out, names=None, scale=3):
    box = VIEWS[view]
    im = SHEET.crop(box).resize(((box[2] - box[0]) * scale, (box[3] - box[1]) * scale), Image.LANCZOS); d = ImageDraw.Draw(im)
    for n, p in m.pos.items():
        if names and n not in names: continue
        if view in ("top", "side") and p[1] < -0.1: continue
        for sg in ((1,) if view in ("top", "side") else (1, -1)):
            q = np.array([p[0], p[1] * sg, p[2]]); a, b = to_px(view, q)
            a, b = (a - box[0]) * scale, (b - box[1]) * scale
            d.ellipse([a - 3, b - 3, a + 3, b + 3], fill=(255, 0, 0)); d.text((a + 4, b - 11), n, fill=(150, 0, 0))
    im.save(out)
if __name__ == "__main__":
    m = B.model()
    for v in VIEWS: draw(m, v, f"{pre}{v}.png")
