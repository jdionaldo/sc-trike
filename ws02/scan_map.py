"""Scan <-> skin mapping (uniform scale s = 391.14/351 about the nose, sill/floor aligned) and scan surface queries."""
import numpy as np
d = np.load("scan/maps.npz"); X, Y, Z, TOP, BOT = d["X"], d["Y"], d["Z"], d["top"], d["bot"]
S = 391.14 / 351.0
def to_scan(x, y, z):                       # skin -> scan frame
    return 175.5 - (34.3 - x) / S, y / S, 40.0 + (z - 52.2) / S
def from_scan(x, y, z):
    return 34.3 - (175.5 - x) * S, y * S, 52.2 + (z - 40.0) * S
def top_z(x, y):                            # skin-frame (x,y) -> skin-frame z of the scan's upper surface (nan if outside)
    xs, ys, _ = to_scan(x, y, 0.0)
    i = int(round((xs - X[0]) / 0.5)); j = int(round((abs(ys) * np.sign(ys) - Y[0]) / 0.5)) if False else int(round((ys - Y[0]) / 0.5))
    if not (0 <= i < len(X) and 0 <= j < len(Y)): return np.nan
    v = TOP[i, j]
    return np.nan if np.isnan(v) else from_scan(0, 0, v)[2]
def half_width(x, z):                       # skin-frame (x,z) -> outer half width of the scan at that station/height (mean of both sides)
    xs, _, zs = to_scan(x, 0.0, z)
    return None
