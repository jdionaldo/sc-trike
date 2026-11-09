"""Seam blend for the graft onto rev_trike_shell_full.sc: in the shell frame the skin's rear end is morphed so its cross-section at the cut matches the shell's
(half width, top, bottom), the correction fading out over BL mm toward the tail (smoothstep).  Parameters in scan/warp.json (written by graft_sc.py)."""
import json
import numpy as np
def make():
    w = json.load(open("scan/warp.json"))
    KX, KY, KZ = w["K"]; XR, BL = w["XR"], w["BL"]
    fy = w["shell"][0] / w["skin"][0]; zt_s, zb_s = w["shell"][1], w["shell"][2]; zt_k, zb_k = w["skin"][1], w["skin"][2]
    XF, BF = w["XF"], w["BF"]; fyF = w["shellF"][0] / w["skinF"][0]; ztsF, zbsF = w["shellF"][1], w["shellF"][2]; ztkF, zbkF = w["skinF"][1], w["skinF"][2]
    def fn(p):
        x = 0.5 + (p[0] + 161.2) * KX; y = KY * p[1]; z = -48.0 + (p[2] - 52.2) * KZ        # skin -> shell frame
        t = np.clip((x - (XR - BL)) / BL, 0.0, 1.0); s = t * t * (3 - 2 * t)                # 1 at the cut, 0 at XR - BL
        if x < XR:
            y2 = y * (1 + s * (fy - 1)); k = (zt_s - zb_s) / (zt_k - zb_k)
            z2 = z + s * ((zb_s + (z - zb_k) * k) - z)
            y, z = y2, z2
        if x > XF:
            t = np.clip(((XF + BF) - x) / BF, 0.0, 1.0); s = t * t * (3 - 2 * t)
            k = (ztsF - zbsF) / (ztkF - zbkF)
            y = y * (1 + s * (fyF - 1)); z = z + s * ((zbsF + (z - zbkF) * k) - z)
        return np.array([(x - 0.5) / KX - 161.2, y / KY, (z + 48.0) / KZ + 52.2])               # back to the skin frame
    return fn
