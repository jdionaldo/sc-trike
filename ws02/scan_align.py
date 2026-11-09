"""Affine alignment skin -> scan frame (x' = ax*x+bx, y' = ay*y, z' = az*z+bz) maximising mean silhouette IoU (side, top, front) between the skin surface mesh and the scan body."""
import json
import numpy as np, cv2, trimesh
from scipy.optimize import minimize
RES = 1.0
sk = trimesh.load("out/pskin/skin.stl", force="mesh")
sb = np.load("scan/points.npz")["body"].astype(float)
def sil(pts, cols, lo, hi):
    n = np.ceil((hi - lo) / RES).astype(int); q = ((pts[:, cols] - lo) / RES).astype(int)
    ok = (q >= 0).all(1) & (q < n).all(1); m = np.zeros((n[1], n[0]), np.uint8); m[q[ok, 1], q[ok, 0]] = 1
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)); cnt, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    o = np.zeros_like(m); cv2.drawContours(o, cnt, -1, 1, -1); return o
LO = np.array([-200.0, -120.0, 0.0]); HI = np.array([200.0, 120.0, 200.0])
V = np.vstack([sk.vertices, sk.sample(60000)])
VIEWS = dict(side=(0, 2), top=(0, 1), front=(1, 2))
SC = {k: sil(sb, list(c), LO[list(c)], HI[list(c)]) for k, c in VIEWS.items()}
def ious(p, parts=False):
    ax, bx, ay, az, bz = p
    A = np.stack([ax * V[:, 0] + bx, ay * V[:, 1], az * V[:, 2] + bz], 1)
    r = {}
    for k, c in VIEWS.items():
        m = sil(A, list(c), LO[list(c)], HI[list(c)]); r[k] = (m & SC[k]).sum() / max((m | SC[k]).sum(), 1)
    return r if parts else -np.mean(list(r.values()))
if __name__ == "__main__":
    s0 = 351.0 / 391.14
    p0 = [s0, 175.5 - 34.3 * s0, s0, s0, 40.0 - 52.2 * s0]
    print("uniform scale start", {k: round(v, 3) for k, v in ious(p0, True).items()})
    r = minimize(ious, p0, method="Nelder-Mead", options=dict(maxiter=300, xatol=1e-3, fatol=1e-5))
    print("fitted", np.round(r.x, 4).tolist(), {k: round(v, 3) for k, v in ious(r.x, True).items()})
    json.dump(dict(p=list(map(float, r.x)), p0=list(map(float, p0)), iou=ious(r.x, True)), open("scan/align.json", "w"))
