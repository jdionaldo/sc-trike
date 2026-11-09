"""Skin-over-scan silhouette overlays (side, top, front) with the uniform scan->skin mapping; scan clipped below z 45 (scan frame) and skid plate removed (|y|<35, x>150, z<95)."""
import numpy as np, cv2, trimesh, sys
S = 391.14 / 351.0
sb = np.load("scan/points.npz")["body"].astype(float)
keep = ~((np.abs(sb[:, 1]) < 35) & (sb[:, 0] > 150) & (sb[:, 2] < 95)) & (sb[:, 2] >= 45)
import json
PR = json.load(open('scan/profiles.json'))
sb = sb[keep]; sb = np.stack([34.3 - (175.5 - sb[:, 0]) * S, sb[:, 1] * S, 52.2 + (sb[:, 2] - 40) * S], 1)
xs_=[r["x"] for r in PR][::-1]; fl_=[r["floor"] if r["floor"]==r["floor"] else 100.0 for r in PR][::-1]
sb = sb[sb[:, 2] >= np.interp(sb[:, 0], xs_, fl_) - 4.0]       # clip hub / arm / skid remnants below the flank floor
sk = trimesh.load("out/pskin/skin.stl", force="mesh"); V = np.vstack([sk.vertices, sk.sample(80000)])
RES = 1.0; LO = np.array([-380.0, -120.0, 40.0]); HI = np.array([60.0, 120.0, 230.0])
def sil(pts, cols):
    lo, hi = LO[cols], HI[cols]; n = np.ceil((hi - lo) / RES).astype(int); q = ((pts[:, cols] - lo) / RES).astype(int)
    ok = (q >= 0).all(1) & (q < n).all(1); m = np.zeros((n[1], n[0]), np.uint8); m[q[ok, 1], q[ok, 0]] = 1
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((5, 5), np.uint8)); ff = m.copy(); mk = np.zeros((n[1] + 2, n[0] + 2), np.uint8); cv2.floodFill(ff, mk, (0, 0), 2); return (ff != 2).astype(np.uint8)
out = []; res = {}
for name, cols in (("side", [0, 2]), ("top", [0, 1]), ("front", [1, 2])):
    a, b = sil(sb, cols), sil(V, cols); res[name] = float((a & b).sum() / max((a | b).sum(), 1))
    im = np.full(a.shape + (3,), 255, np.uint8); im[a > 0] = (170, 170, 170); im[(b > 0) & (a == 0)] = (60, 60, 255); im[(a > 0) & (b == 0)] = (255, 160, 60)
    im = im[::-1]; im = cv2.resize(im, None, fx=3, fy=3, interpolation=cv2.INTER_NEAREST); cv2.putText(im, f"{name} IoU {res[name]:.3f} (grey both, red skin only, blue scan only)", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 0), 2); out.append(im)
w = max(i.shape[1] for i in out); out = [np.pad(i, ((0, 0), (0, w - i.shape[1]), (0, 0)), constant_values=255) for i in out]
cv2.imwrite("out/pskin/WS03_panel_skin_over_scan.png", np.vstack(out)); print(res)
