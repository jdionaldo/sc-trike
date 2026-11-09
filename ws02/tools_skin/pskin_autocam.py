"""Automatic perspective-camera fit of the skin to the sheet-68 FRONT 3/4 drawing (no hand-picked points).
score = truncated chamfer of the skin's projected panel edges to the drawing's dark lines + silhouette (1 - IoU) against a hand-painted body mask.
usage: python tools_skin/pskin_autocam.py [mesh_source=panels]   -> out/pskin/cam34.json, WS03_panel_q34_overlay.png"""
import sys, json
import numpy as np, cv2
from scipy.optimize import differential_evolution, minimize
from PIL import Image
import pskin_build as B, pskin_core as C
BOX = (1200, 440, 1960, 830); W, H = 760, 390
ref = np.asarray(Image.open("ref68/sheet68.png").convert("RGB").crop(BOX))
gray = cv2.cvtColor(ref, cv2.COLOR_RGB2GRAY)
dark = (gray < 150).astype(np.uint8)
dt = cv2.distanceTransform(1 - dark, cv2.DIST_L2, 3)
BODY = np.array([(248,250),(300,208),(400,175),(612,62),(860,20),(1030,12),(1100,35),(1180,95),(1300,140),(1316,165),(1290,215),(1250,300),(1200,380),(1200,470),(950,505),(940,440),(870,350),(800,300),(700,290),(620,320),(560,340),(500,330),(440,300),(310,300),(250,300)]) / 2.0
bmask = np.zeros((H, W), np.uint8); cv2.fillPoly(bmask, [BODY.astype(np.int32)], 1)
def load():
    m = B.model(); P, pn = m.mirror(); C.orient_panels(P, pn); C.ORIENTED = True
    return P, pn
P, pn = load()
names = sorted({i for p in pn for i in p["ids"]}); idx = {n: k for k, n in enumerate(names)}
V = np.array([P[n] for n in names])
tris = []; edges = set(); panel_tris = []
for p in pn:
    Q = np.array([P[i] for i in p["ids"]]); nrm = C.panel_normal(Q, p["hint"])
    for a, b, c in C.ear_triangles(Q, nrm): tris.append([idx[p["ids"][a]], idx[p["ids"][b]], idx[p["ids"][c]]]); panel_tris.append(nrm)
    for k in range(len(p["ids"])): edges.add(tuple(sorted((idx[p["ids"][k]], idx[p["ids"][(k + 1) % len(p["ids"])]]))))
tris = np.array(tris); NRM = np.array(panel_tris); edges = np.array(sorted(edges))
CEN = np.array([-160.0, 0.0, 125.0])
def cam(par):
    az, el, roll, dist, f, sx, sy = par
    az, el, roll = np.radians([az, el, roll])
    c = CEN + dist * np.array([np.cos(el) * np.cos(az), np.cos(el) * np.sin(az), np.sin(el)])
    z = CEN - c; z /= np.linalg.norm(z); x = np.cross(z, [0, 0, -1.0]); x /= np.linalg.norm(x); y = np.cross(z, x)
    cr, sr = np.cos(roll), np.sin(roll); x, y = cr * x + sr * y, -sr * x + cr * y
    return c, np.stack([x, y, z])
def project(par, X):
    c, R = cam(par); Xc = (X - c) @ R.T
    return np.stack([par[4] * Xc[:, 0] / Xc[:, 2] + W / 2 + par[5], par[4] * Xc[:, 1] / Xc[:, 2] + H / 2 + par[6]], 1), Xc[:, 2]
def render(par):
    uv, z = project(par, V); c, R = cam(par)
    front = ((c - V[tris].mean(1)) * NRM).sum(1) > 0
    m = np.zeros((H, W), np.uint8)
    for t in tris[front]: cv2.fillConvexPoly(m, uv[t].astype(np.int32), 1)
    vf = np.zeros(len(V), bool)
    # an edge is drawn if it belongs to a front-facing triangle
    fe = set()
    for t in tris[front]:
        for k in range(3): fe.add(tuple(sorted((t[k], t[(k + 1) % 3]))))
    E = np.array([e for e in map(tuple, edges) if e in fe])
    return uv, m, E
def score(par, full=False):
    uv, m, E = render(par)
    if len(E) < 20 or (m > 0).sum() < 2000: return 5.0
    s = 0.0; n = 0
    pts = []
    for a, b in E:
        for t in np.linspace(0, 1, 6): pts.append(uv[a] * (1 - t) + uv[b] * t)
    pts = np.array(pts); ok = (pts[:, 0] >= 0) & (pts[:, 0] < W - 1) & (pts[:, 1] >= 0) & (pts[:, 1] < H - 1)
    d = np.full(len(pts), 30.0); q = pts[ok].astype(int); d[ok] = np.minimum(dt[q[:, 1], q[:, 0]], 30.0)
    inter = (m & bmask).sum(); uni = (m | bmask).sum(); iou = inter / uni
    sc = d.mean() / 30.0 + 3.0 * (1 - iou)
    return (sc, d, iou, pts, uv, m, E) if full else sc
if __name__ == "__main__":
    AZ = (float(sys.argv[1]), float(sys.argv[2])) if len(sys.argv) > 2 else (0, 360)
    OUTN = sys.argv[3] if len(sys.argv) > 3 else 'q34'
    bounds = [AZ, (5, 28), (-6, 6), (500, 1500), (700, 2600), (-150, 150), (-150, 150)]
    best = None
    for seed in range(3):
        r = differential_evolution(score, bounds, seed=seed, popsize=18, maxiter=70, tol=1e-4, polish=False)
        r2 = minimize(score, r.x, method="Nelder-Mead", options=dict(maxiter=600, xatol=1e-3, fatol=1e-5))
        x = r2.x if r2.fun < r.fun else r.x; f = min(r.fun, r2.fun)
        print("start", seed, "score %.4f" % f, np.round(x, 1).tolist(), flush=True)
        if best is None or f < best[0]: best = (f, x)
    f, x = best
    sc, d, iou, pts, uv, m, E = score(x, True)
    print("BEST", np.round(x, 2).tolist(), "chamfer mean %.1f p95 %.1f px, silhouette IoU %.3f" % (d.mean(), np.percentile(d, 95), iou), "focal 35mm-equiv %.0f" % (x[4] / W * 36))
    json.dump(dict(par=list(map(float, x)), mean=float(d.mean()), p95=float(np.percentile(d, 95)), iou=float(iou)), open(f"out/pskin/cam_{OUTN}.json", "w"))
    ov = ref.copy(); ov = cv2.resize(ov, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
    tint = cv2.resize(m, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST) > 0
    ov[tint] = (0.65 * ov[tint] + 0.35 * np.array([200, 70, 150])).astype(np.uint8)
    for a, b in E: cv2.line(ov, tuple((uv[a] * 2).astype(int)), tuple((uv[b] * 2).astype(int)), (0, 0, 255), 1, cv2.LINE_AA)
    cv2.polylines(ov, [(BODY * 2).astype(np.int32)], True, (0, 160, 0), 1)
    Image.fromarray(ov).save(f"out/pskin/ov_{OUTN}.png"); print("saved")
