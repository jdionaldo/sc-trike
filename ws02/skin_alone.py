"""Rev 10: standalone faceted skin, traced from sheet 61 at a single uniform scale (112 mm tyre = sketch tyre), no frame, hardware, hinge, wheelbase or bed fitted.
Frame: x forward (front axle at x 0), y left, z up from the ground. Output: out/skin_alone/{skin.stl, skin_front.stl, skin_rear.stl, wing.stl}.
usage: python skin_alone.py"""
import os
os.environ["WS03_ALONE"] = "1"
import math
from pathlib import Path
import numpy as np
import trimesh
from manifold3d import Manifold
from scipy.spatial import cKDTree

import mono_build as MB
import skin7 as K

OUT = Path("out/skin_alone")
WALL = 2.4
CUT_X = -165.0
GROOVE_D, GROOVE_W = 0.7, 1.6


def band(p, q, w):
    d = np.array(q, float) - np.array(p, float)
    d /= np.linalg.norm(d)
    n = np.array([-d[1], d[0]]) * w / 2.0
    return [tuple(np.array(p) + n), tuple(np.array(q) + n), tuple(np.array(q) - n), tuple(np.array(p) - n)]


def pink():
    """Red accent lines of the sketch as shallow grooves: door-sill diagonals, rear fender rail, roof stripes."""
    layer = K.solid(0.0) - K.solid(GROOVE_D)
    flank = []
    for (a, b) in (((352, 668), (502, 632)), ((395, 660), (502, 640)), ((580, 625), (640, 535)), ((640, 535), (700, 508))):
        flank.append(tuple(T_xz(*p) for p in (a, b)))
    cut = None
    for p, q in flank:
        for y0, y1 in ((40.0, 130.0), (-130.0, -40.0)):
            c = MB.prism_xz(band(p, q, GROOVE_W), y0, y1)
            cut = c if cut is None else cut + c
    x0, x1 = K.Xt(387.0), K.Xt(525.0)
    for s_ in (1, -1):
        for yy in (28.0, 31.5):
            c = MB.prism_xy(band((x0, s_ * yy), (x1, s_ * yy), GROOVE_W), 30.0, 300.0)
            cut = c if cut is None else cut + c
    return layer ^ cut


def T_xz(px, py):
    return K.T.to_xz(px, py)


def cyl_x(x, y, z, r, L):
    return Manifold.cylinder(L, r, r, 24).rotate((0.0, 90.0, 0.0)).translate((x - L / 2.0, y, z))


def dowels(body):
    cx = CUT_X
    for yy in (-24.0, 24.0):
        zin = min(K.surf(cx - 9.0, yy), K.surf(cx + 9.0, yy), K.surf(cx, yy)) - WALL * 1.4
        pad = Manifold.cube((18.0, 10.0, 12.0), center=False).translate((cx - 9.0, yy - 5.0, zin - 9.0))
        body = body + (pad ^ K.solid(1.0)) - cyl_x(cx, yy, zin - 4.0, 1.6, 18.0)
    zb = K._pl(K.ZB, cx)
    for sg in (-1, 1):
        hy = (K.hw(cx, WALL) - 5.5) * sg
        pad = Manifold.cube((18.0, 8.0, 14.0), center=False).translate((cx - 9.0, hy - 4.0, zb + 1.0))
        body = body + (pad ^ K.solid(1.0)) - cyl_x(cx, hy, zb + 8.0, 1.6, 18.0)
    return body


def clean(m):
    """Manifold -> watertight trimesh after float32 welding (separate coincident non-edge vertex pairs, drop degenerate faces)."""
    mm = m.to_mesh()
    V = np.array(mm.vert_properties, float)[:, :3]
    Tr = np.array(mm.tri_verts)
    t = trimesh.Trimesh(V.copy(), Tr, process=False)
    edges = set(map(tuple, np.sort(t.edges, axis=1)))
    vn = t.vertex_normals
    for i, j in sorted(cKDTree(V).query_pairs(3e-4)):
        if (i, j) in edges:
            continue
        d = V[j] - V[i]
        d = d / np.linalg.norm(d) if np.linalg.norm(d) > 1e-9 else vn[j]
        V[j] = V[j] + d * 0.012
    V = V.astype(np.float32).astype(float)
    t = trimesh.Trimesh(V, Tr, process=False)
    t.merge_vertices()
    t.update_faces(t.nondegenerate_faces())
    t.remove_unreferenced_vertices()
    return max(t.split(only_watertight=False), key=lambda c: abs(c.volume))


def wing():
    """Our stepped wing and its hangers, moved onto the sketch's rear deck (leading hump, px 542-602)."""
    import w3_assembly as A
    ms = [(n, m) for n, m, k in A.assembly(0.0, 0.0) if n.startswith("w3_tail")]
    allv = np.vstack([m.vertices for n, m in ms])
    cx = 0.5 * (allv[:, 0].min() + allv[:, 0].max())
    xt = K.Xp(572.0)
    hang = np.vstack([m.vertices for n, m in ms if "hanger" in n])
    zdeck = K.tz(xt)
    import mask61 as _M
    dz = (_M.Z_SILL + 832 * _M.L_MM / 1951.0) - allv[:, 2].max()                        # wing top on the side mask's peak (sheet tab, z 219)
    xt = _M.X_NOSE - 1425.0 * _M.L_MM / 1951.0                                        # centre of the mask's wing tab
    parts = []
    for n, m in ms:
        t = m.copy()
        t.apply_translation((xt - cx, 0.0, dz))
        parts.append(t)
    return trimesh.util.concatenate(parts), (xt - cx, dz)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    S0 = K.solid(0.0)
    body = S0 - K.solid(WALL, belly=True)
    body = K.features(body, S0, K.solid, pink)
    w = None                                                              # rev 13: no wing, hangers or recess for now
    body = dowels(body)
    whole = clean(body)
    whole.export(OUT / "skin.stl")
    print("skin", len(whole.faces), whole.is_watertight, round(whole.volume), np.round(whole.bounds, 1).tolist())
    big = Manifold.cube((2000.0, 2000.0, 2000.0), center=True)
    fr = body ^ big.translate((CUT_X + 1000.0, 0.0, 0.0))
    rr = body ^ big.translate((CUT_X - 1000.0, 0.0, 0.0))
    for n, p in (("front", fr), ("rear", rr)):
        t = clean(p)
        t.export(OUT / f"skin_{n}.stl")
        print(n, len(t.faces), t.is_watertight, np.round(t.extents, 1).tolist())
    (OUT / "wing.stl").unlink(missing_ok=True)
    print("details:"); [print("  ", d) for d in K.DETAILS]


if __name__ == "__main__":
    main()
