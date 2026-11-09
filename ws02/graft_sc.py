"""Graft the panel-skin front and rear onto the mid section of rev_trike_shell_full.sc (frame: x forward, y left, z up, mm; extracted meshes in scan/sc_*.stl).
Skin -> shell affine from the cabin: x' = 0.5 + (x + 161.2) KX, y' = KY y, z' = -48 + (z - 52.2) KZ.  Mid = shell between XR and XF (kept as is), ends = skin beyond the cuts (overlap OV)."""
import numpy as np, trimesh, os
from manifold3d import Manifold, Mesh, OpType
import pskin_core as C
KX, KY, KZ = 0.925, 0.96, 0.912
XF, XR, OV = 72.0, -92.0, 6.0
def man(t): return Manifold(Mesh(np.array(t.vertices, np.float32), np.array(t.faces, np.uint32)))
def box(x0, x1): return Manifold.cube((x1 - x0, 400.0, 400.0)).translate((x0, -200.0, -200.0))
sk = trimesh.load("out/pskin/skin_plain.stl", force="mesh")
V = sk.vertices.copy(); V = np.stack([0.5 + (V[:, 0] + 161.2) * KX, KY * V[:, 1], -48.0 + (V[:, 2] - 52.2) * KZ], 1)
sk = trimesh.Trimesh(V, sk.faces, process=False); S = man(sk)
sf, sr = trimesh.load("scan/sc_front.stl"), trimesh.load("scan/sc_rear.stl")
TRIM = Manifold.cube((60.0, 400.0, 40.0)).translate((XF - 14.0, -200.0, -78.0))       # trims the shell's sill-plate tongue (x 58..72, z < -38) so the new fender skirt is not butted against a flat plate
CH = []
for sg in (1, -1):                                                                 # chamfer the door-front panel's top/front corner down into the fender line (moves only this corner of the mid)
    pts = [(XF + 1, sg * y, z) for y in (58.0, 100.0) for z in (46.0, 90.0)] + [(XF - 34, sg * y, 90.0) for y in (58.0, 100.0)]
    CH.append(man(trimesh.convex.convex_hull(np.array(pts))))
mid_f = (man(sf) ^ box(0.0, XF)) - TRIM - Manifold.batch_boolean(CH, OpType.Add); mid_r = man(sr) ^ box(XR, 0.5)
new_f = S ^ box(XF - OV, 400.0); new_r = S ^ box(-400.0, XR + OV)
# front: planar sill-skirt wedge per side carries the fender skirt down to the door sill (z -48) instead of ending in a step
wed = []
for sg in (1, -1):
    yo, yi = 93.0, 90.0
    pts = [(XF + 2, sg * y, z) for y in (yo, yi) for z in (-48.0, -3.0)] + [(XF + 44, sg * y, -3.0) for y in (yo - 3.0, yi - 3.0)]
    wed.append(man(trimesh.convex.convex_hull(np.array(pts))))
new_f = Manifold.batch_boolean([new_f] + wed, OpType.Add)
# rear: remove the thin skirt leg hanging below the arch edge
new_r = new_r - Manifold.cube((60.0, 400.0, 70.0)).translate((XR - 55.0, -200.0, -75.0))
parts = dict(end_front=new_f, mid_front=mid_f, mid_rear=mid_r, end_rear=new_r)
sc = trimesh.Scene()
R = np.array([[1, 0, 0, 0], [0, 0, 1, 0], [0, -1, 0, 0], [0, 0, 0, 1.0]])
for n, m in parts.items():
    t = C.to_trimesh(m); t.export(f"out/pskin/graft_{n}.stl"); print(n, t.is_watertight, round(t.volume), t.bounds.round(0).tolist())
    t = t.copy(); t.visual.face_colors = [200, 70, 150, 255] if n.startswith("end") else [120, 150, 200, 255]; t.apply_transform(R); sc.add_geometry(t, node_name=n)
for k, nm in (("01c084e8", "pod_a"), ("3fd21f8d", "pod_b"), ("799ca28d", "roof_rack"), ("1713399d", "spoiler")):
    m = trimesh.load(f"scan/sc_{k}.stl"); V = m.vertices / 1000.0; V = np.stack([-V[:, 1], V[:, 0], V[:, 2]], 1)
    t = trimesh.Trimesh(V, m.faces, process=False); t.visual.face_colors = [90, 90, 100, 255]; t.apply_transform(R); sc.add_geometry(t, node_name=nm)
sc.export("out/pskin/WS03_graft_v5.glb")
all_ = trimesh.util.concatenate([trimesh.load(f"out/pskin/graft_{n}.stl") for n in parts]); all_.export("out/pskin/graft_all5.stl")
