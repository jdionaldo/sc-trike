"""Skin vs everything else: volume (mm3) of every assembly item that sits inside the skin's material (walls, accessories), at rest or a lean/steer pose.
usage: python fit_check.py [lean steer]"""
import sys
import numpy as np
import trimesh
import manifold3d as m3
import w3_assembly as A


def man(t):
    return m3.Manifold(m3.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))


def report(lean=0.0, steer=0.0, top=40, min_mm3=0.5):
    items = A.assembly(lean, steer=steer)
    skin = [(n, man(m)) for n, m, k in items if n.startswith("body3_")]
    rows = []
    for n, m, k in items:
        if n.startswith("body3_"):
            continue
        try:
            mm = man(m)
        except Exception:
            continue
        for sn, sm in skin:
            if np.any(m.bounds[1] < trimesh.load(f"out/mono3/{sn}.stl").bounds[0]) and False:
                continue
            v = (mm ^ sm).volume()
            if v > min_mm3:
                rows.append((round(v, 1), n, sn))
    rows.sort(reverse=True)
    return rows[:top]


if __name__ == "__main__":
    lean, steer = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) > 2 else (0.0, 0.0)
    for r in report(lean, steer):
        print(r)
