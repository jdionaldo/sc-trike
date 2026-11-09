"""Seam handling for the graft onto rev_trike_shell_full.sc (v4).
1. Piecewise-linear x map skin -> shell frame so the skin's cowl base lands on the shell's door-front edge (XF) and the skin's rear-deck end on the shell's rear-quarter end (XR):
   nodes NODES = [(skin x, shell x)].  y, z use the cabin affine KY, KZ.
2. Section blend: near each cut the skin's cross-section (half width, top, bottom) is morphed to the shell's, fading out over BL mm (smoothstep).
Parameters in scan/warp.json (graft_sc.py writes the measured extents between pass 1 (blend off) and pass 2)."""
import json
import numpy as np
def make():
    w = json.load(open("scan/warp.json"))
    KY, KZ = w["KY"], w["KZ"]; nodes = np.array(w["NODES"]); XR, XF, BL, BF = w["XR"], w["XF"], w["BL"], w["BF"]
    sx, tx = nodes[::-1, 0], nodes[::-1, 1]                        # ascending skin x
    xm = lambda x: float(np.interp(x, sx, tx)); xi = lambda X: float(np.interp(X, tx, sx))
    blend = w.get("blend", True)
    if blend:
        fyR = w["shellR"][0] / w["skinR"][0]; ztsR, zbsR = w["shellR"][1], w["shellR"][2]; ztkR, zbkR = w["skinR"][1], w["skinR"][2]
        fyF = w["shellF"][0] / w["skinF"][0]; ztsF, zbsF = w["shellF"][1], w["shellF"][2]; ztkF, zbkF = w["skinF"][1], w["skinF"][2]
    def fn(p):
        x = xm(p[0]); y = KY * p[1]; z = -48.0 + (p[2] - 52.2) * KZ
        if blend:
            if x < XR:
                t = np.clip((x - (XR - BL)) / BL, 0.0, 1.0); s = t * t * (3 - 2 * t); k = (ztsR - zbsR) / (ztkR - zbkR)
                y = y * (1 + s * (fyR - 1)); z = z + s * ((zbsR + (z - zbkR) * k) - z)
            if x > XF:
                t = np.clip(((XF + BF) - x) / BF, 0.0, 1.0); s = t * t * (3 - 2 * t); k = (ztsF - zbsF) / (ztkF - zbkF)
                y = y * (1 + s * (fyF - 1)); z = z + s * ((zbsF + (z - zbkF) * k) - z)
        return np.array([x, y, z])                                  # SHELL frame
    KX0 = w["KX"]
    back = lambda q: np.array([(q[0] - 0.5) / KX0 - 161.2, q[1] / KY, (q[2] + 48.0) / KZ + 52.2])        # shell frame -> skin frame (inverse of the graft's linear map)
    return lambda p: back(fn(p))
def wx(x):
    """Where a skin-frame x (as read from the sheet) sits after the warp, in skin-frame coordinates (used to place details on the warped panels)."""
    w = json.load(open("scan/warp.json")); nodes = np.array(w["NODES"])
    X = float(np.interp(x, nodes[::-1, 0], nodes[::-1, 1]))
    return (X - 0.5) / w["KX"] - 161.2
