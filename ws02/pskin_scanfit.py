"""Scan tie-break for corner heights: for top-layer corners the plan (x,y) stays from the drawing/mask and z is pulled toward the scan's upper surface above that point
(skin->scan affine from scan_align.py). Ridge, outline and floor corners keep the mask values."""
import json, os
import numpy as np
A = json.load(open("scan/align.json"))["p"]
_d = np.load("scan/maps.npz"); X, Y, TOP = _d["X"], _d["Y"], _d["top"]
def scan_top_z(x, y):
    ax, bx, ay, az, bz = A
    xs, ys = ax * x + bx, ay * y
    i = int(round((xs - X[0]) / 0.5)); j = int(round((ys - Y[0]) / 0.5))
    if not (0 <= i < len(X) and 0 <= j < len(Y)): return None
    v = TOP[i, j]
    return None if np.isnan(v) else float((v - bz) / az)
WHITE = ("A", "B", "C", "D", "b2", "S1", "S2", "S5", "S6", "S7", "S8", "E0", "E1", "E2", "E3", "F0", "Sx1", "Sx2", "Sx13", "Sx15", "Sx17")      # hood / fender / rear deck: the scan's upper surface is the panel itself (cabin corners lie under the canopy: excluded)
def apply_scan(m, wz=1.5, blend=1.0):
    deltas = []
    for n in WHITE:
        if n not in m.tg: continue
        t = m.tg[n]; z = scan_top_z(t[0], t[1])
        if z is None: continue
        deltas.append((round(z - t[2], 1), n)); t[2] = (1 - blend) * t[2] + blend * z; m.w[n][2] = wz
    return len(deltas), sorted(deltas)
