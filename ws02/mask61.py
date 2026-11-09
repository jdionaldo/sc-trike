"""Silhouette polylines from the user's exact masks (ref/plan_mask.png, ref/side_mask.png), solid red on white/black.
Both masks are normalised to the same body length L (nose tip and tail end line up); plan keeps the top mask's width/length ratio, side keeps the side mask's
height/length ratio; L comes from the uniform sheet-61 scale (112 mm tyre = 176 px), so the physical size is unchanged.
Frame as skin7 / trace61 (ALONE): x forward, front axle x 0, ground z 0. Tables are (x, value) in mm, sorted nose to tail like trace61's polylines.
usage: python mask61.py  (prints vertex counts and turn statistics)"""
import math
import numpy as np
import cv2
from PIL import Image
from pathlib import Path

HERE = Path(__file__).parent
S = 0.636
L_MM = (737.0 - 122.0) * S                       # body length, nose tip to tail end (sheet 61 side view)
X_NOSE = (176.0 - 122.0) * S                     # +34.3
EPS = 1.5                                        # px, polyline tolerance
Z_SILL = (791.0 - 709.0) * S                     # the side mask's flat bottom cut is the sill line (52.2 mm above ground)
WING_X = (1318.0, 1560.0)                        # side-mask px: wing / roll-bar tab above the roofline (the wing is a separate part)


def load(name):
    im = np.asarray(Image.open(HERE / "ref" / f"{name}_mask.png").convert("RGB")).astype(int)
    return ((im[:, :, 0] > 150) & (im[:, :, 1] < 100) & (im[:, :, 2] < 100)).astype(np.uint8)


def edges(m, first_run=False):
    W = m.shape[1]
    top = np.array([np.nonzero(m[:, x])[0].min() for x in range(W)], float)
    def run_end(col):                                                  # end of the first red run from the top (an undercut below it is ignored)
        r = np.nonzero(col)[0]
        gaps = np.nonzero((np.diff(r) > 3) & (r[:-1] > 300))[0]                  # only gaps in the lower half (the tab notch near the top is not an undercut)
        return r[gaps[0]] if len(gaps) else r.max()
    bot = np.array([(run_end(m[:, x]) if first_run else np.nonzero(m[:, x])[0].max()) for x in range(W)], float)
    return top, bot


def poly(vals, x0=0):
    pts = np.array([[x, v] for x, v in enumerate(vals)], np.float32).reshape(-1, 1, 2)
    return cv2.approxPolyDP(pts, EPS, False).reshape(-1, 2)


def tab_free_top(top):
    """Roofline without the wing / roll-bar tab: straight between the tab's two feet."""
    t = top.copy()
    a, b = int(WING_X[0]), int(WING_X[1])
    t[a:b + 1] = np.interp(np.arange(a, b + 1), [a, b], [top[a], top[b]])
    return t


def tables():
    pm, sm = load("plan"), load("side")
    Wp, Hp = pm.shape[1], pm.shape[0]
    Ws, Hs = sm.shape[1], sm.shape[0]
    pt, pb = edges(pm)
    hw = (pb - pt) / 2.0
    cx = lambda px, W: X_NOSE - px * L_MM / (W - 1)
    sp, ss = L_MM / (Wp - 1), L_MM / (Ws - 1)
    plan = [(cx(x, Wp), v * sp) for x, v in poly(hw)]
    plan = [p for p in plan if not any(abs(q[0] - p[0]) < 0.5 and q[1] > p[1] for q in plan)]            # chamfered first column: keep the full-width vertex
    st, sb = edges(sm, True)
    top = [(cx(x, Ws), Z_SILL + (Hs - 1 - v) * ss) for x, v in poly(tab_free_top(st))]
    bot = [(cx(x, Ws), Z_SILL + (Hs - 1 - v) * ss) for x, v in poly(sb)]
    tab = [(cx(x, Ws), Z_SILL + (Hs - 1 - v) * ss) for x, v in poly(st[int(WING_X[0]) - 3:int(WING_X[1]) + 3] if False else st)]
    return dict(plan=plan, top=top, bot=bot, scale=(sp, ss), shape=((Wp, Hp), (Ws, Hs)))


def turns(p):
    q = sorted(p, reverse=True)
    out = []
    for i in range(1, len(q) - 1):
        a = math.atan2(q[i][1] - q[i - 1][1], q[i][0] - q[i - 1][0]); b = math.atan2(q[i + 1][1] - q[i][1], q[i + 1][0] - q[i][0])
        out.append(abs(math.degrees((b - a + math.pi) % (2 * math.pi) - math.pi)))
    return out


def merge(p, min_turn=15.0, max_dev=3.0):
    """Drop vertices whose turn is under min_turn and whose removal moves the outline by less than max_dev mm (smallest turn first)."""
    q = sorted(p, reverse=True)
    while True:
        best = None
        for i in range(1, len(q) - 1):
            a = math.atan2(q[i][1] - q[i - 1][1], q[i][0] - q[i - 1][0]); b = math.atan2(q[i + 1][1] - q[i][1], q[i + 1][0] - q[i][0])
            t = abs(math.degrees((b - a + math.pi) % (2 * math.pi) - math.pi))
            if t >= min_turn:
                continue
            (x0, y0), (x1, y1), (x2, y2) = q[i - 1], q[i], q[i + 1]
            dev = abs((x2 - x0) * (y0 - y1) - (x0 - x1) * (y2 - y0)) / max(math.hypot(x2 - x0, y2 - y0), 1e-9)
            if dev <= max_dev and (best is None or t < best[0]):
                best = (t, i)
        if best is None:
            return q
        q.pop(best[1])


if __name__ == "__main__":
    t = tables()
    print("scale mm/px plan %.4f side %.4f; masks %s" % (*t["scale"], t["shape"]))
    for k in ("plan", "top", "bot"):
        p = t[k]
        tr = turns(p)
        m = merge(p)
        print(f"{k}: {len(p)} vertices, {sum(1 for a in tr if a < 15)} with turn < 15 deg; after merging near-collinear ones (<1 mm): {len(m)}, {sum(1 for a in turns(m) if a < 15)} under 15 deg")
        print("  ", [(round(a), round(b)) for a, b in m])
