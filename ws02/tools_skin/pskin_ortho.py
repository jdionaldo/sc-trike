"""Orthographic overlay of the panel graph (projected panel edges) on the sheet-68 front or rear view, with a 4-parameter affine fit (scale/offset per axis) by
truncated chamfer. usage: python tools_skin/pskin_ortho.py front|rear   -> out/pskin/ortho_<view>.png + stats. Also dot-map of every named corner."""
import sys
import numpy as np, cv2
from scipy.optimize import minimize
from PIL import Image
import pskin_build as B, pskin_core as C
view = sys.argv[1]
BOX = dict(front=(985, 20, 1445, 395), rear=(1495, 20, 1990, 395))[view]
INIT = dict(front=(1 / 0.6, 1212.0, 1 / 0.643, 382.0), rear=(1 / 0.73, 1721.0, 1 / 0.63, 382.0))[view]
sgn = 1.0 if view == "front" else -1.0
m = B.model(); P, pn = m.mirror(); C.orient_panels(P, pn); C.ORIENTED = True
im = np.asarray(Image.open("ref68/sheet68.png").convert("RGB").crop(BOX)); H, W = im.shape[:2]
gray = cv2.cvtColor(im, cv2.COLOR_RGB2GRAY); dark = (gray < 150).astype(np.uint8); dt = cv2.distanceTransform(1 - dark, cv2.DIST_L2, 3)
segs = []
for p in pn:
    Q = np.array([P[i] for i in p["ids"]]); n = C.panel_normal(Q, p["hint"])
    if n[0] * sgn > 0.05:
        for k in range(len(Q)): segs.append((Q[k], Q[(k + 1) % len(Q)]))
segs = np.array(segs)
def pix(par, X):
    a, b, c, d = par
    y = X[..., 1] * (1 if view == "front" else -1)
    return np.stack([a * y + b - BOX[0], c - d * X[..., 2] - BOX[1]], -1)
def score(par, full=False):
    t = np.linspace(0, 1, 8)[None, :, None]
    pts = (segs[:, 0:1] * (1 - t) + segs[:, 1:2] * t).reshape(-1, 3)
    uv = pix(par, pts); ok = (uv[:, 0] >= 0) & (uv[:, 0] < W - 1) & (uv[:, 1] >= 0) & (uv[:, 1] < H - 1)
    d = np.full(len(uv), 25.0); q = uv[ok].astype(int); d[ok] = np.minimum(dt[q[:, 1], q[:, 0]], 25.0)
    return (d, uv) if full else d.mean()
S0 = float(sys.argv[2]) if len(sys.argv) > 2 else 0.60                  # isotropic mm/px (front view: widest body +-94 mm = 157 px, roof z 209 -> py 34)
CX = dict(front=1212.0, rear=1721.0)[view]
class _R: pass
r = _R(); r.x = np.array([1 / S0, CX, 382.0, 1 / S0])
par = r.x; d, uv = score(par, True)
print(view, "affine fit (px/mm y, y0px, py0, px/mm z):", np.round(par, 2).tolist(), "-> mm/px y %.3f z %.3f" % (1 / par[0], 1 / par[3]), "chamfer mean %.1f p95 %.1f px" % (d.mean(), np.percentile(d, 95)))
ov = cv2.resize(im, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
for s in segs:
    a, b = pix(par, s[0]) * 2, pix(par, s[1]) * 2
    cv2.line(ov, tuple(a.astype(int)), tuple(b.astype(int)), (0, 0, 255), 1, cv2.LINE_AA)
Image.fromarray(ov).save(f"out/pskin/ortho_{view}.png")
