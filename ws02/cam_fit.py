"""Pinhole camera fitting of the scan (frame: x forward, y lateral, z up; centre (0,0,75)) to the reference photo 67.jpg (silhouette IoU) -> scan/cam_photo.json"""
import json, sys
import numpy as np, cv2
from scipy.optimize import differential_evolution
from PIL import Image
KSIZE = 3
CEN = np.array([0.0, 0.0, 75.0])
def cam(par):
    az, el, dist, f, sx, sy = par
    a, e = np.radians(az), np.radians(el)
    c = CEN + dist * np.array([np.cos(e) * np.cos(a), np.cos(e) * np.sin(a), np.sin(e)])
    z = CEN - c; z /= np.linalg.norm(z); x = np.cross(z, [0, 0, -1.0]); x /= np.linalg.norm(x); y = np.cross(z, x)
    return c, np.stack([x, y, z])
def project(par, X, W, H):
    c, R = cam(par); Xc = (X - c) @ R.T
    return np.stack([par[3] * Xc[:, 0] / Xc[:, 2] + W / 2 + par[4], par[3] * Xc[:, 1] / Xc[:, 2] + H / 2 + par[5]], 1), Xc[:, 2]
def splat(par, X, W, H):
    uv, z = project(par, X, W, H); q = np.round(uv).astype(int)
    ok = (q[:, 0] >= 0) & (q[:, 0] < W) & (q[:, 1] >= 0) & (q[:, 1] < H) & (z > 0)
    m = np.zeros((H, W), np.uint8); m[q[ok, 1], q[ok, 0]] = 1
    k = int(KSIZE); m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((k, k), np.uint8))
    ff = m.copy(); msk = np.zeros((H + 2, W + 2), np.uint8); cv2.floodFill(ff, msk, (0, 0), 2)
    out = (ff != 2).astype(np.uint8)
    return out
if __name__ == "__main__":
    W = H = 500
    im = np.asarray(Image.open("/private/tmp/claude-501/-Users-johndionaldo-Library-Application-Support-Claude-scratch-workspaces-8645d517-f4a3-433c-8998-fd7c0e49ba87-a748fb05-e298-40e2-a797-544bc288ae5f-scratch-2026-10-30-ec4193/0d275d42-fddc-4cbd-9c02-604bf37928ec/images/67.jpg").convert("L").resize((W, H), Image.LANCZOS))
    mask = (im < 105).astype(np.uint8); mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, np.ones((7, 7), np.uint8))
    cnt, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE); mm = np.zeros_like(mask); cv2.drawContours(mm, [max(cnt, key=cv2.contourArea)], -1, 1, -1)
    X = np.load("scan/points.npz")["solid"][::2].astype(float); X = X[X[:, 2] > 6]
    def score(p):
        m = splat(p, X, W, H); return 1 - (m & mm).sum() / max((m | mm).sum(), 1)
    best = None
    for sg in (1, -1):
        r = differential_evolution(score, [(15, 70) if sg > 0 else (-70, -15), (0, 30), (350, 1500), (500, 2500), (-150, 150), (-150, 150)], seed=1, popsize=18, maxiter=60, polish=False)
        print("az sign", sg, "IoU %.3f" % (1 - r.fun), np.round(r.x, 1).tolist(), flush=True)
        if best is None or r.fun < best.fun: best = r
    json.dump(dict(par=list(map(float, best.x)), iou=float(1 - best.fun), W=W, H=H), open("scan/cam_photo.json", "w"))
    p = best.x; Xf = np.load("scan/points.npz")["solid"][::2].astype(float); m = splat(p, Xf[Xf[:, 2] > 6], W, H)
    ov = np.stack([np.asarray(Image.open("/private/tmp/claude-501/-Users-johndionaldo-Library-Application-Support-Claude-scratch-workspaces-8645d517-f4a3-433c-8998-fd7c0e49ba87-a748fb05-e298-40e2-a797-544bc288ae5f-scratch-2026-10-30-ec4193/0d275d42-fddc-4cbd-9c02-604bf37928ec/images/67.jpg").convert("RGB").resize((W, H)))] [0:1] * 1)[0].copy()
    ov[m > 0] = (0.6 * ov[m > 0] + 0.4 * np.array([200, 40, 150])).astype(np.uint8); Image.fromarray(ov).save("out/pskin/photo_scan_overlay.png")
