"""Export the concept skin on the full WS-03 assembly as a y-up GLB (skin pieces tinted, rest grey). usage: WS03_SKIN=concept python tools_skin/export_glb.py OUT.glb"""
import sys
import numpy as np, trimesh
import w3_assembly as A
sc = trimesh.Scene()
R = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1.0]])
for n, m, k in A.assembly(0.0, 0.0):
    m = m.copy() if hasattr(m, "copy") else m
    if n.startswith("body3"):
        c = [200, 70, 150, 255]
    elif n.startswith("w3_tail"):
        c = [230, 200, 60, 255]
    else:
        c = [150, 150, 155, 255]
    m.visual.face_colors = c
    m.apply_transform(R)
    sc.add_geometry(m, node_name=n)
sc.export(sys.argv[1]); print("glb", len(sc.geometry))
