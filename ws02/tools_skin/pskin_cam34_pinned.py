"""Pinned 3/4 camera: az +-35 deg, el 15 deg, 60 mm-equivalent focal length fixed; only distance and 2D shift fitted (3 params). Overlay + stats."""
import numpy as np, cv2
from scipy.optimize import differential_evolution
from PIL import Image
import tools_skin.pskin_autocam as A
best = None
for az in (-35.0,):
    f = lambda p: A.score([az, 15.0, 0.0, p[0], 60 / 36 * A.W, p[1], p[2]])
    r = differential_evolution(f, [(500, 1600), (-150, 150), (-150, 150)], seed=1, popsize=15, maxiter=40, polish=False)
    print("az", az, "score %.3f" % r.fun, np.round(r.x, 1).tolist(), flush=True)
    if best is None or r.fun < best[0]: best = (r.fun, az, r.x)
_, az, x = best
par = [az, 15.0, 0.0, x[0], 60 / 36 * A.W, x[1], x[2]]
sc, d, iou, pts, uv, m, E = A.score(par, True)
print("PINNED az %.0f el 15 f 60mm: chamfer mean %.1f p95 %.1f px (sheet px), silhouette IoU %.3f" % (az, d.mean(), np.percentile(d, 95), iou))
ov = cv2.resize(A.ref, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
t = cv2.resize(m, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST) > 0
ov[t] = (0.65 * ov[t] + 0.35 * np.array([200, 70, 150])).astype(np.uint8)
for a, b in E: cv2.line(ov, tuple((uv[a] * 2).astype(int)), tuple((uv[b] * 2).astype(int)), (0, 0, 255), 1, cv2.LINE_AA)
cv2.polylines(ov, [(A.BODY * 2).astype(np.int32)], True, (0, 160, 0), 1)
Image.fromarray(ov).save("out/pskin/WS03_panel_q34_overlay_pinned.png")
