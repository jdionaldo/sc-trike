"""Fit the scan (with wheels) to the sheet-68 front 3/4 DRAWING: chamfer of the scan's projected outline (+ internal depth discontinuities skipped) to the drawing's dark lines. -> scan/cam_drawing.json"""
import json
import numpy as np, cv2
from scipy.optimize import differential_evolution
from PIL import Image
import cam_fit as CF
CF.KSIZE = 11
BOX = (1200, 440, 1960, 830); W, H = 760, 390
ref = np.asarray(Image.open("ref68/sheet68.png").convert("RGB").crop(BOX)); gray = cv2.cvtColor(ref, cv2.COLOR_RGB2GRAY)
dark = (gray < 150).astype(np.uint8); dt = cv2.distanceTransform(1 - dark, cv2.DIST_L2, 3)
X = np.load("scan/points.npz")["solid"][::3].astype(float)
def contour_pts(p, X):
    m = CF.splat(p, X, W, H)
    cnt, _ = cv2.findContours(m, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    return m, (np.vstack([c[:, 0, :] for c in cnt]) if cnt else np.zeros((0, 2), int))
def score(p):
    m, c = contour_pts(p, X)
    if len(c) < 200: return 5.0
    d = np.minimum(dt[np.clip(c[:, 1], 0, H - 1), np.clip(c[:, 0], 0, W - 1)], 25.0)
    area = (m > 0).sum() / (W * H)
    return d.mean() / 25.0 + (3.0 if area < 0.30 else 0.0) + (0.5 if area > 0.7 else 0.0)
if __name__ == "__main__":
    best = None
    for sg in (1, -1):
        r = differential_evolution(score, [(15, 75) if sg > 0 else (-75, -15), (3, 30), (350, 1500), (500, 2500), (-200, 200), (-200, 200)], seed=3, popsize=18, maxiter=60, polish=False)
        print("sign", sg, "score %.3f" % r.fun, np.round(r.x, 1).tolist(), flush=True)
        if best is None or r.fun < best.fun: best = r
    json.dump(dict(par=list(map(float, best.x)), score=float(best.fun), W=W, H=H), open("scan/cam_drawing.json", "w"))
    Xa = np.load("scan/points.npz")["solid"][::2].astype(float); m, c = contour_pts(best.x, Xa)
    ov = cv2.resize(ref, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC); cv2.polylines(ov, [(c * 2).astype(np.int32).reshape(-1, 1, 2)], False, (255, 0, 0), 1)
    Image.fromarray(ov).save("out/pskin/drawing_scan_overlay.png")
