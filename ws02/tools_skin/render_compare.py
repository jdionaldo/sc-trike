"""Before/after renders: current skin, concept skin, reference GLB (shell only, scaled to the build). Painter's-algorithm orthographic views -> PNG.
usage: python tools_skin/render_compare.py OUTDIR"""
import sys
from pathlib import Path
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

REF = "/Users/johndionaldo/Documents/Shapecast/Library/screenshot-2026-11-08-at-8-41-26-am-d2cdbd13/final.glb"


def load_ref(length_mm):
    s = trimesh.load(REF)
    m = list(s.geometry.values())[0].copy()
    v = np.asarray(m.vertices)
    v = np.c_[v[:, 2], -v[:, 0], v[:, 1]]                       # glb (x width, y up, z length, nose +z) -> (fwd, left, up)
    v = v * (length_mm / np.ptp(v[:, 0]))
    m.vertices = v
    return m


def view_basis(kind):
    if kind == "top":
        return np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1.0]])         # screen right = fwd, screen up = left, depth = up
    if kind == "side":
        return np.array([[0, -1, 0], [0, 0, 1], [1, 0, 0.0]]) @ np.eye(3)
    a, e = np.radians(-35.0), np.radians(28.0)                        # iso: rear-left-above
    R1 = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    R2 = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    return R2 @ R1


def render(m, kind, size=(900, 420), col=(120, 150, 200), scale=None, center=None):
    v = np.asarray(m.vertices, float); f = np.asarray(m.faces)
    if kind == "top":
        P = np.c_[v[:, 0], v[:, 1], v[:, 2]]; sx, sy, sd = P[:, 0], P[:, 1], P[:, 2]
    elif kind == "side":
        sx, sy, sd = v[:, 0], v[:, 2], -v[:, 1]
    else:
        B = view_basis("iso"); P = v @ B.T; sx, sy, sd = P[:, 0], P[:, 2], -P[:, 1]
    tri = np.stack([sx, sy, sd], 1)[f]
    sc = scale or 0.92 * min(size[0] / np.ptp(sx), size[1] / np.ptp(sy))
    c = center if center is not None else (0.5 * (sx.min() + sx.max()), 0.5 * (sy.min() + sy.max()))
    X = (tri[:, :, 0] - c[0]) * sc + size[0] / 2; Y = size[1] / 2 - (tri[:, :, 1] - c[1]) * sc
    n = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    if kind == "iso":
        n = n @ B.T
        L = np.array([-0.4, -0.5, 0.75])
    elif kind == "top":
        L = np.array([-0.3, 0.2, 0.9])
    else:
        L = np.array([0.3, -0.6, 0.6])
    if kind == "side":
        nn = np.c_[n[:, 0], n[:, 2], -n[:, 1]]; L = np.array([0.3, 0.6, 0.7])
    elif kind == "top":
        nn = n
    else:
        nn = np.c_[n[:, 0], n[:, 2], -n[:, 1]]; L = np.array([-0.4, 0.75, 0.5])
    L = L / np.linalg.norm(L)
    sh = np.clip(np.abs(nn @ L), 0, 1) * 0.75 + 0.25
    order = np.argsort(tri[:, :, 2].mean(1))
    im = Image.new("RGB", size, (255, 255, 255)); d = ImageDraw.Draw(im)
    for i in order:
        d.polygon([(X[i, 0], Y[i, 0]), (X[i, 1], Y[i, 1]), (X[i, 2], Y[i, 2])], fill=tuple(int(sh[i] * k) for k in col))
    return im, sc, c


def main(out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    cur = trimesh.load("out/mono3/body3.stl"); con = trimesh.load("out/mono3_concept/body3.stl")
    ref = load_ref(float(np.ptp(con.vertices[:, 0])))
    font = ImageFont.load_default()
    for kind, size in (("top", (900, 330)), ("side", (900, 330)), ("iso", (900, 480))):
        cols = []
        for name, m, colr in (("current skin", cur, (130, 150, 175)), ("concept skin", con, (180, 110, 150)), ("reference (Shapecast GLB, shell + wheels)", ref, (120, 160, 120))):
            im, _, _ = render(m, kind, size, colr)
            ImageDraw.Draw(im).text((8, 6), f"{name} - {kind}", fill=(0, 0, 0), font=font)
            cols.append(im)
        sheet = Image.new("RGB", (size[0], sum(c.height for c in cols)), (255, 255, 255)); y = 0
        for c in cols:
            sheet.paste(c, (0, y)); y += c.height
        sheet.save(out / f"compare_{kind}.png")
    print("ok")


if __name__ == "__main__":
    main(sys.argv[1])
