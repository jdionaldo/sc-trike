"""Fit a pinhole camera to the sheet-68 front 3/4 drawing from vertex <-> pixel correspondences, render the skin edges, overlay, edge-distance stats.
usage: python tools_skin/pskin_cam34.py [sign]   (sign +1/-1: which flank faces the camera)"""
import sys, io
import numpy as np, cv2, trimesh
from scipy.optimize import least_squares
from PIL import Image
import pskin_build as B
sg = float(sys.argv[1]) if len(sys.argv) > 1 else 1.0
BOX = (1200, 440, 1960, 830); S = 2
m = B.model()
G = {  # vertex -> (gx, gy) in the 2x grid crop of the sheet 3/4 view
 "S0": (248, 245), "W1": (640, 52), "Sx9": (1235, 205), "S8": (1300, 150), "Fb": (945, 437), "Rb": (1150, 380), "B9": (1190, 470),
 "W1'": (878, 38), "c2": (560, 195), "S2": (800, 200)}
names = [n for n in G if (n in m.pos or n.rstrip("'") in m.pos)]
def pos(n):
    p = m.pos[n.rstrip("'")].copy()
    if n.endswith("'"): p[1] = -p[1]
    p[1] *= sg
    return p
X = np.array([pos(n) for n in names]); u = np.array([G[n] for n in names], float)
W, H = (BOX[2] - BOX[0]) * S, (BOX[3] - BOX[1]) * S
def proj(par, X):
    rv, tv, f = par[:3], par[3:6], par[6]
    R, _ = cv2.Rodrigues(rv)
    Xc = X @ R.T + tv
    return np.stack([f * Xc[:, 0] / Xc[:, 2] + W / 2, f * Xc[:, 1] / Xc[:, 2] + H / 2], 1)
best = None
for az in np.linspace(0, 2 * np.pi, 12, endpoint=False):
    for el in (0.2, 0.5):
        c = np.array([-150 + 600 * np.cos(az) * np.cos(el), 600 * np.sin(az) * np.cos(el), 100 + 600 * np.sin(el)])      # camera position guess
        z = (np.array([-150, 0, 120.]) - c); z /= np.linalg.norm(z); x = np.cross(z, [0, 0, -1.0]); x /= np.linalg.norm(x); y = np.cross(z, x)
        R = np.stack([x, y, z]); rv = cv2.Rodrigues(R)[0].ravel(); tv = -R @ c
        r = least_squares(lambda p: (proj(p, X) - u).ravel(), np.r_[rv, tv, 2500.0], max_nfev=400)
        if best is None or r.cost < best.cost: best = r
par = best.x
res = np.linalg.norm(proj(par, X) - u, axis=1)
print("points", len(names), "fit rms px (2x grid)", round(float(np.sqrt((res ** 2).mean())), 1), "focal", round(par[6]), {n: round(float(r), 1) for n, r in zip(names, res)})
# render skin feature edges
mesh = trimesh.load("out/pskin/skin.stl", force="mesh")
mesh.apply_transform(np.diag([1, sg, 1, 1.0]))
if sg < 0: mesh.invert()
ang = np.degrees(mesh.face_adjacency_angles); ed = mesh.face_adjacency_edges[ang > 12]
img = np.full((H, W, 3), 255, np.uint8)
R = cv2.Rodrigues(par[:3])[0]; cam = -R.T @ par[3:6]
mask = np.zeros((H, W), np.uint8)
tris = proj(par, mesh.vertices)
vis = (mesh.face_normals * (cam - mesh.triangles_center)).sum(1) > 0
for f in np.where(vis)[0]: cv2.fillConvexPoly(mask, tris[mesh.faces[f]].astype(np.int32), 255)
cv2.imwrite("out/pskin/q34_mask.png", mask)
ref = np.asarray(Image.open("ref68/sheet68.png").convert("RGB").crop(BOX).resize((W, H), Image.LANCZOS))
ov = ref.copy()
ov[mask > 0] = (0.55 * ov[mask > 0] + 0.45 * np.array([200, 70, 150])).astype(np.uint8)
E3 = mesh.vertices[ed]; mid = E3.mean(1); dirs = mid - cam; hit = mesh.ray.intersects_any(np.tile(cam, (len(mid), 1)), dirs * 0.995)
pts = []
for seg, h in zip(E3, hit):
    if not h:
        a, b = proj(par, seg); cv2.line(ov, tuple(a.astype(int)), tuple(b.astype(int)), (0, 0, 255), 2); pts.append((a, b))
Image.fromarray(ov).save("out/pskin/WS03_panel_q34_overlay.png")
# edge distance: drawing dark strokes vs our edge pixels
gray = cv2.cvtColor(ref, cv2.COLOR_RGB2GRAY); dark = (gray < 140).astype(np.uint8)
dt = cv2.distanceTransform(1 - dark, cv2.DIST_L2, 3)
ours = np.zeros((H, W), np.uint8)
for a, b in pts: cv2.line(ours, tuple(a.astype(int)), tuple(b.astype(int)), 1, 1)
d = dt[ours > 0] / S
print("edge px (sheet px units): mean %.1f  p95 %.1f  (our edges %d px)" % (d.mean(), np.percentile(d, 95), len(d)))
cs, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
print("silhouette area px", int((mask > 0).sum()))
