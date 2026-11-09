"""Graft the panel-skin front and rear onto the mid section of rev_trike_shell_full.sc (frame: x forward, y left, z up, mm; extracted meshes in scan/sc_*.stl).
Skin -> shell affine from the cabin: x' = 0.5 + (x + 161.2) KX, y' = KY y, z' = -48 + (z - 52.2) KZ.  Mid = shell between XR and XF (kept as is), ends = skin beyond the cuts (overlap OV)."""
import numpy as np, trimesh, os
from manifold3d import Manifold, Mesh, OpType
import pskin_core as C
KX, KY, KZ = 0.925, 0.96, 0.912
XF, XR, OV = 52.0, -72.0, 6.0
def man(t): return Manifold(Mesh(np.array(t.vertices, np.float32), np.array(t.faces, np.uint32)))
def box(x0, x1): return Manifold.cube((x1 - x0, 400.0, 400.0)).translate((x0, -200.0, -200.0))
sk = trimesh.load("out/pskin/skin_plain.stl", force="mesh")
V = sk.vertices.copy(); V = np.stack([0.5 + (V[:, 0] + 161.2) * KX, KY * V[:, 1], -48.0 + (V[:, 2] - 52.2) * KZ], 1)
sk = trimesh.Trimesh(V, sk.faces, process=False); S = man(sk)
sf, sr = trimesh.load("scan/sc_front.stl"), trimesh.load("scan/sc_rear.stl")
mid_f = man(sf) ^ box(0.0, XF); mid_r = man(sr) ^ box(XR, 0.5)
new_f = S ^ box(XF - OV, 400.0); new_r = S ^ box(-400.0, XR + OV)
parts = dict(end_front=new_f, mid_front=mid_f, mid_rear=mid_r, end_rear=new_r)
sc = trimesh.Scene()
R = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1.0]])
for n, m in parts.items():
    t = C.to_trimesh(m); t.export(f"out/pskin/graft_{n}.stl"); print(n, t.is_watertight, round(t.volume), t.bounds.round(0).tolist())
    t = t.copy(); t.visual.face_colors = [200, 70, 150, 255] if n.startswith("end") else [120, 150, 200, 255]; t.apply_transform(R); sc.add_geometry(t, node_name=n)
for k, nm in (("01c084e8", "pod_a"), ("3fd21f8d", "pod_b"), ("799ca28d", "roof_rack"), ("1713399d", "spoiler")):
    m = trimesh.load(f"scan/sc_{k}.stl"); V = m.vertices / 1000.0; V = np.stack([-V[:, 1], V[:, 0], V[:, 2]], 1)
    t = trimesh.Trimesh(V, m.faces, process=False); t.visual.face_colors = [90, 90, 100, 255]; t.apply_transform(R); sc.add_geometry(t, node_name=nm)
sc.export("out/pskin/WS03_graft_v1.glb")
all_ = trimesh.util.concatenate([trimesh.load(f"out/pskin/graft_{n}.stl") for n in parts]); all_.export("out/pskin/graft_all.stl")
