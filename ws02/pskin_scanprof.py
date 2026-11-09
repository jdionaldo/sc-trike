"""Scan-driven profiles (scan/profiles.json, skin frame, uniform scale about the nose) installed into pskin_trace: ridge (TOP), plan half width (PLAN, RATIO),
flank floor (ZB_ST), shoulder (ZSH_T).  Topology and drawing-traced corner positions stay; heights/widths follow the scan."""
import json
import numpy as np
R = json.load(open("scan/profiles.json"))
def _interp(key, x):
    xs = [r["x"] for r in R][::-1]; v = [r[key] for r in R][::-1]
    ok = [k for k in range(len(v)) if not np.isnan(v[k])]
    return float(np.interp(x, [xs[k] for k in ok], [v[k] for k in ok]))
def install(T):
    hw0 = {float(x): float(h) for x, h in T.PLAN}
    plan0 = [(float(x), float(h)) for x, h in T.PLAN]
    def hw_m(x):
        q = sorted(plan0); return float(np.interp(x, [a for a, _ in q], [b for _, b in q]))
    T.PLAN = [(x, (0.0 if i in (0, len(plan0) - 1) and False else _interp("hw", x))) for i, (x, h) in enumerate(plan0)]
    T.PLAN[0] = (plan0[0][0], max(_interp("hw", plan0[0][0]), 18.0)); T.PLAN[-1] = (plan0[-1][0], 2.0)
    T.RATIO = lambda x: float(np.clip(_interp("hw", x) / max(hw_m(x), 1.0), 0.8, 1.8))
    top = [(r["x"], r["ridge"]) for r in R]; top[0] = (34.3, max(131.7, top[0][1])); top[-1] = (-356.8, top[-1][1])
    T.TOP = top
    T.ZSH_T = [(r["x"], min(r["z_shoulder"], r["ridge"] - 6.0)) for r in R][::-1]
    T.ZSH_T = sorted([(x, z) for x, z in T.ZSH_T], key=lambda p: p[0])
    for x in list(T.ZB_ST):
        if x in (33.9, 28.9): continue
        f = _interp("floor", x)
        T.ZB_ST[x] = max(f, 52.2) if x < -90 else f
    T.ZB_ST[-90.1] = 60.0; T.ZB_ST[-97.2] = 54.0
