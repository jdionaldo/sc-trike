"""GLBs of the fitted skin: python export_fit_glb.py OUTDIR  ->  WS03_skin_fit_assembly.glb (full assembly, y-up, ground at y = 0) and WS03_skin_fit_skin_only.glb (the three hollow pieces
in the chassis frame, y-up).  Skin-only keeps the chassis frame so it can be laid over the assembly."""
import sys
from pathlib import Path
import numpy as np
import trimesh
import w3_paint

out = Path(sys.argv[1] if len(sys.argv) > 1 else "out")
out.mkdir(parents=True, exist_ok=True)
w3_paint.build(str(out / "WS03_skin_fit_assembly.glb"), yup=True)
R = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1.0]])
cols = {"tail": [190, 45, 35, 255], "front": [200, 52, 40, 255], "mid": [226, 122, 40, 255], "rear": [168, 36, 30, 255]}
sc = trimesh.Scene()
for k in ("front", "mid", "rear", "tail"):
    m = trimesh.load(f"out/mono3/body3_{k}.stl")
    m.visual.face_colors = cols[k]
    m.apply_transform(R)
    sc.add_geometry(m, node_name=f"skin_{k}", geom_name=f"skin_{k}")
sc.export(str(out / "WS03_skin_fit_skin_only.glb"))
print("exported", [p.name for p in out.glob("WS03_skin_fit_*.glb")])
