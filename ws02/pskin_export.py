"""Finish the standalone panel skin: details, mini spoiler + rails, split at x -165 with dowel pads/holes, clean STLs. usage: python pskin_export.py"""
import sys, time, os
from pathlib import Path
import numpy as np, trimesh
from manifold3d import Manifold
import pskin_build as B, pskin_core as C, pskin_detail as D

OUT = Path("out/pskin"); OUT.mkdir(parents=True, exist_ok=True)
CUT_X = -165.0


def dowels(body_man):
    mesh = C.to_trimesh(body_man)
    adds, cuts = [], []
    for yy in (-24.0, 24.0):
        zs = []
        for xx in (CUT_X - 9.0, CUT_X + 9.0):
            for ya in (yy - 5.0, yy + 5.0):
                zi = D.surf_z(mesh, xx, ya, 1)
                zs.append(zi)
        zi = max(zs)
        top = [(xx, ya, D.surf_z(mesh, xx, ya, 1) + 0.8) for xx in (CUT_X - 9.0, CUT_X + 9.0) for ya in (yy - 5.0, yy + 5.0)]
        adds.append(D.hullm(top + [(a, b, zi - 12.0) for a, b, _ in top]))
        cuts.append(D.man(trimesh.creation.cylinder(1.6, 18.0, sections=24, transform=trimesh.transformations.concatenate_matrices(
            trimesh.transformations.translation_matrix((CUT_X, yy, zi - 6.0)), trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0])))))
    z0 = 72.0
    for sg in (1, -1):
        pts = []
        for xx in (CUT_X - 9.0, CUT_X + 9.0):
            for zz in (z0, z0 + 14.0):
                o = np.array([xx, 0.0, zz]); dr = np.array([0.0, sg, 0.0])
                loc, _, _ = mesh.ray.intersects_location([o], [dr], multiple_hits=True)
                ys = sorted(abs(v) for v in loc[:, 1])
                pts.append((xx, sg * ys[0], zz))                    # first hit from the inside = inner face
        adds.append(D.hullm([(a, b + sg * 0.8, c) for a, b, c in pts] + [(a, b - sg * 8.0, c) for a, b, c in pts]))
        yh = np.mean([p[1] for p in pts]) - sg * 4.0
        cuts.append(D.man(trimesh.creation.cylinder(1.6, 18.0, sections=24, transform=trimesh.transformations.concatenate_matrices(
            trimesh.transformations.translation_matrix((CUT_X, yh, z0 + 7.0)), trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0])))))
    return Manifold.batch_boolean([body_man] + adds, __import__("manifold3d").OpType.Add) - Manifold.batch_boolean(cuts, __import__("manifold3d").OpType.Add)


def build():
    t0 = time.time()
    m = B.model(); P, pn = m.mirror(); C.orient_panels(P, pn); C.ORIENTED = True
    d = D.Detail(P, pn)
    D.apply_details(d)
    import os
    if os.environ.get('WS03_PLAIN') == '1':
        body = d.body                                   # no spoiler / rails / dowel pads (used when the skin ends are grafted onto another mid section)
    else:
        D.spoiler_and_rails(d)
        body = dowels(d.body)
    whole = C.to_trimesh(body)
    whole.export(OUT / ("skin_plain.stl" if os.environ.get("WS03_PLAIN") == "1" else "skin.stl"))
    print("skin", len(whole.faces), whole.is_watertight, round(whole.volume), np.round(whole.bounds, 1).tolist(), f"{time.time()-t0:.1f}s")
    if os.environ.get('WS03_PLAIN') == '1':
        return P, pn
    big = Manifold.cube((2000.0, 2000.0, 2000.0), center=True)
    for n, off in (("front", 1000.0), ("rear", -1000.0)):
        piece = body ^ big.translate((CUT_X + off, 0.0, 0.0))
        t = C.to_trimesh(piece)
        t.export(OUT / f"skin_{n}.stl")
        print(n, len(t.faces), t.is_watertight, np.round(t.extents, 1).tolist(), round(t.volume))
    return P, pn


if __name__ == "__main__":
    build()
