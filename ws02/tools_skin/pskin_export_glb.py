"""Export the STANDALONE panel skin (out/pskin/skin_front.stl + skin_rear.stl) as a y-up GLB, two nodes. usage: python tools_skin/pskin_export_glb.py OUT.glb"""
import sys, hashlib
from pathlib import Path
import numpy as np, trimesh
R = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1.0]])
sc = trimesh.Scene()
for n in ("skin_front", "skin_rear"):
    m = trimesh.load(Path("out/pskin") / f"{n}.stl"); m.visual.face_colors = [200, 70, 150, 255]; m.apply_transform(R); sc.add_geometry(m, node_name=n)
sc.export(sys.argv[1])
v = np.vstack([g.vertices for g in sc.geometry.values()])
print("glb nodes", len(sc.geometry), "vertices", len(v), "hash", hashlib.md5(np.round(v, 3).tobytes()).hexdigest()[:8])
