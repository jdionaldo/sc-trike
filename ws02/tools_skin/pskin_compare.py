"""Side-by-side: sheet 68 crop (left) and our render (right) for top / side / front / rear / q34. usage: python tools_skin/pskin_compare.py MESH.stl OUT_PREFIX"""
import sys, io
import numpy as np, trimesh
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
from tools_skin.pskin_render import render
SHEET = Image.open("ref68/sheet68.png").convert("RGB")
CROPS = dict(top=(95, 40, 745, 380), side=(85, 440, 750, 720), front=(985, 20, 1445, 395), rear=(1495, 20, 1990, 395), q34=(1190, 440, 1960, 835))
m = trimesh.load(sys.argv[1], force="mesh")
for v, box in CROPS.items():
    fig, ax = plt.subplots(figsize=(8, 5), dpi=100)
    render(ax, m, "q34" if v == "q34" else v)
    buf = io.BytesIO(); fig.savefig(buf, format="png"); plt.close(fig); buf.seek(0)
    mine = Image.open(buf).convert("RGB")
    ref = SHEET.crop(box)
    h = 520
    ref = ref.resize((int(ref.width * h / ref.height), h)); mine = mine.resize((int(mine.width * h / mine.height), h))
    out = Image.new("RGB", (ref.width + mine.width + 10, h), "white"); out.paste(ref, (0, 0)); out.paste(mine, (ref.width + 10, 0))
    out.save(f"{sys.argv[2]}{v}.png")
print("ok")
