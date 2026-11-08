"""Rev 6 comparison sheets: previous skin (rev 5), new skin and the reference (image 60 crop) per view, with the traced reference outline in red.
usage: python tools_skin/render_rev6.py REF_IMAGE OUT_DIR PREV_GLB"""
import sys
from pathlib import Path
import numpy as np, trimesh
from PIL import Image, ImageDraw, ImageFont
REF, OUT, PREV = sys.argv[1], Path(sys.argv[2]), sys.argv[3]
OUT.mkdir(parents=True, exist_ok=True)
tr = np.load("skin_trace.npz")
Rz = np.array([[1, 0, 0, 0], [0, 0, -1, 0], [0, 1, 0, 0], [0, 0, 0, 1.0]])           # inverse of the glb y-up transform


def prev_mesh():
    s = trimesh.load(PREV)
    parts = []
    for n in s.graph.nodes_geometry:
        if n.startswith("body3"):
            T, g = s.graph[n]
            m = s.geometry[g].copy(); m.apply_transform(T); m.apply_transform(Rz); parts.append(m)
    return trimesh.util.concatenate(parts)


IDIR = np.array([0.62, 0.50, 0.60]); IDIR /= np.linalg.norm(IDIR)
IR = np.cross((0, 0, 1.0), IDIR); IR /= np.linalg.norm(IR); IU = np.cross(IDIR, IR)


def project(v, kind):
    if kind == "iso": return v @ IR, v @ IU, v @ IDIR
    if kind == "side": return -v[:, 0], v[:, 2], -v[:, 1]
    if kind == "top": return -v[:, 0], v[:, 1], v[:, 2]
    if kind == "front": return -v[:, 1], v[:, 2], v[:, 0]
    return v[:, 1], v[:, 2], -v[:, 0]                                                    # rear


CEN = {"iso": (float(np.array([-195.0, 0, 50.0]) @ IR), float(np.array([-195.0, 0, 50.0]) @ IU)), "side": (200.0, 50.0), "top": (210.0, 0.0), "front": (0.0, 50.0), "rear": (0.0, 50.0)}


def render(m, kind, size, sc, col):
    v, f = np.asarray(m.vertices), np.asarray(m.faces)
    a, b, d = project(v, kind)
    cx, cy = CEN[kind]
    X = (a - cx) * sc + size[0] / 2; Y = size[1] / 2 - (b - cy) * sc
    n = m.face_normals
    L = np.array([-0.35, 0.45, 0.8]) / np.linalg.norm([-0.35, 0.45, 0.8])
    sh = np.clip(np.abs(n @ L), 0, 1) * 0.7 + 0.3
    D = {"iso": tuple(IDIR), "side": (0, -1, 0), "top": (0, 0, 1), "front": (1, 0, 0), "rear": (-1, 0, 0)}[kind]
    vis = (n @ np.array(D, float)) > 0.02
    order = [i for i in np.argsort((d[f]).mean(1)) if vis[i]]
    im = Image.new("RGB", size, (252, 250, 250)); dr = ImageDraw.Draw(im)
    for i in order:
        t = f[i]; dr.polygon([(X[t[0]], Y[t[0]]), (X[t[1]], Y[t[1]]), (X[t[2]], Y[t[2]])], fill=tuple(int(sh[i] * c) for c in col))
    return im, (cx, cy)


def outline(im, kind, size, sc, cen):
    dr = ImageDraw.Draw(im)
    def P(a, b): return ((a - cen[0]) * sc + size[0] / 2, size[1] / 2 - (b - cen[1]) * sc)
    if kind == "side":
        pts = [P(-x, z) for x, z in tr["side"]]; dr.line(pts, fill=(220, 30, 30), width=2)
    elif kind == "top":
        for s in (1, -1):
            pts = [P(-x, s * h) for x, h in tr["half"]]; dr.line(pts, fill=(220, 30, 30), width=2)
    else:
        fr = tr["front"]
        for s in (1, -1):
            pts = [P(s * h, z) for z, h in fr]; dr.line(pts, fill=(220, 30, 30), width=2)


CROP = {"iso": (1460, 30, 1990, 400), "side": (100, 30, 860, 390), "top": (880, 50, 1450, 350), "front": (250, 440, 720, 800), "rear": (950, 440, 1350, 800)}
new = trimesh.util.concatenate([trimesh.load(f"out/mono3_concept/body3_{p}.stl") for p in ("front", "mid", "rear")])
old = prev_mesh()
ref = Image.open(REF).convert("RGB")
font = ImageFont.load_default()
sizes = {"iso": (900, 480), "side": (900, 380), "top": (900, 340), "front": (520, 420), "rear": (520, 420)}
SC = {"iso": 1.45, "side": 1.5, "top": 1.5, "front": 2.0, "rear": 2.0}
for kind in ("iso", "side", "top", "front", "rear"):
    size, sc = sizes[kind], SC[kind]
    ims = []
    for name, m, col in (("previous skin (rev 5)", old, (130, 150, 175)), ("NEW skin (rev 6)", new, (190, 100, 150))):
        im, cen = render(m, kind, size, sc, col)
        if kind != "iso": outline(im, kind, size, sc, cen)
        ImageDraw.Draw(im).text((8, 6), f"{name} - {kind}  (red = traced reference outline)", fill=(0, 0, 0), font=font); ims.append(im)
    c = ref.crop(CROP.get(kind, (1460, 30, 1990, 400))); c = c.resize((size[0], int(c.height * size[0] / c.width))); r = Image.new("RGB", size, (255, 255, 255)); r.paste(c, (0, 0))
    ImageDraw.Draw(r).text((8, 6), f"reference (image 60) - {kind}", fill=(0, 0, 0), font=font); ims.append(r)
    sheet = Image.new("RGB", (size[0], sum(i.height for i in ims)), (255, 255, 255)); y = 0
    for i in ims: sheet.paste(i, (0, y)); y += i.height
    sheet.save(OUT / f"WS03_rev6_{kind}.png")
print("ok")
