"""Close-up renders of a mesh cropped to a box (the three pink seam zones). usage: python tools_skin/zones.py MESH.stl OUT_PREFIX"""
import sys, numpy as np, trimesh, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from tools_skin.pskin_render import render
m = trimesh.load(sys.argv[1], force="mesh")
ZONES = {"front_door_sill": ((10, 140), (-110, 110), (-55, 70), ("q34", "side")), "rear_quarter": ((-170, -50), (-110, 110), (-55, 95), ("q34r", "side")), "roof_band": ((-110, 80), (-110, 110), (40, 100), ("q34", "top"))}
for name, (xr, yr, zr, views) in ZONES.items():
    c = m.copy()
    for ax_, (lo, hi) in enumerate((xr, yr, zr)):
        for sgn, v in ((1, lo), (-1, hi)):
            n = np.zeros(3); n[ax_] = sgn; o = np.zeros(3); o[ax_] = v
            c = trimesh.intersections.slice_mesh_plane(c, n, o, cap=False)
    fig, axs = plt.subplots(1, len(views), figsize=(8 * len(views), 6), dpi=90)
    for a, v in zip(np.atleast_1d(axs), views): render(a, c, v)
    fig.savefig(f"{sys.argv[2]}{name}.png"); plt.close(fig)
print("ok")
