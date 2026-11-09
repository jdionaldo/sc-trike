"""Export the STANDALONE skin (out/skin_alone/skin_front.stl + skin_rear.stl, built by skin_alone.py) as a y-up GLB, two nodes.
The chassis assembly is only exported with the explicit flag --assembly (old rev 9 body on the full WS-03 assembly); there is no silent fallback.
usage: python tools_skin/export_glb.py OUT.glb [--assembly]"""
import sys, hashlib
from pathlib import Path
import numpy as np, trimesh
R = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1.0]])
sc = trimesh.Scene()
if "--assembly" in sys.argv:
    import w3_assembly as A
    for n, m, k in A.assembly(0.0, 0.0):
        m = m.copy(); m.visual.face_colors = [200, 70, 150, 255] if n.startswith("body3") else [150, 150, 155, 255]
        m.apply_transform(R); sc.add_geometry(m, node_name=n)
else:
    for n in ("skin_front", "skin_rear"):
        p = Path("out/skin_alone") / f"{n}.stl"
        if not p.exists():
            sys.exit(f"missing {p}: run skin_alone.py first (no fallback to the chassis assembly)")
        m = trimesh.load(p); m.visual.face_colors = [200, 70, 150, 255]; m.apply_transform(R); sc.add_geometry(m, node_name=n)
    assert len(sc.geometry) == 2
out = sys.argv[1]; sc.export(out)
v = np.vstack([g.vertices for g in sc.geometry.values()])
print("glb nodes", len(sc.geometry), "vertices", len(v), "hash", hashlib.md5(np.round(v, 3).tobytes()).hexdigest()[:8], "bounds", np.round(v.min(0)).tolist(), np.round(v.max(0)).tolist())
