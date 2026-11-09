"""Our skin's top-view creases (cyan) over the sheet 61 plan. usage: WS03_ALONE=1 python tools_skin/overlay_top.py OUT.png"""
import sys, numpy as np, trimesh
from PIL import Image, ImageDraw
import skin_alone, skin7 as K, trace61 as T
m = trimesh.load("out/skin_alone/skin.stl"); m.merge_vertices()
x0, x1 = K.Xt(120.0), K.Xt(720.0); a = 600.0 / (x1 - x0)
px = lambda x: 120.0 + (x - x0) * a
Z = 3; im = Image.open("/tmp/sheet61_new.png").convert("RGB"); c = im.crop((100, 60, 760, 345)).resize((660 * Z, 285 * Z), Image.LANCZOS); d = ImageDraw.Draw(c)
ang = np.degrees(m.face_adjacency_angles); fa = m.face_adjacency; up = m.face_normals[:, 2] > 0.05
for e, an, f in zip(m.face_adjacency_edges, ang, fa):
    if an < 20 or not (up[f[0]] or up[f[1]]): continue
    p = m.vertices[e]
    if np.linalg.norm(p[0] - p[1]) < 4: continue
    pts = [((px(q[0]) - 100) * Z, (211.7 - q[1] / T.HW - 60) * Z) for q in p]
    d.line(pts, fill=(0, 170, 255), width=2)
    d.line([(pts[0][0], 2 * 211.7 * Z - 120 * Z - pts[0][1] + 0), (pts[1][0], 2 * 211.7 * Z - 120 * Z - pts[1][1])], fill=(0, 170, 255), width=2) if False else None
c.save(sys.argv[1]); print(c.size)
