"""Sketch ratio against built, per station (sheet 61). Ratios are relative to the body length L so they are independent of scale.
usage: WS03_ALONE=1 python tools_skin/proportions.py [STL]"""
import sys
import numpy as np, trimesh
import trace61 as T
m = trimesh.load(sys.argv[1] if len(sys.argv) > 1 else "out/skin_alone/skin.stl")
LS = T.TAIL_PX - T.NOSE_PX            # sketch body length in the side view, px
GROUND = T.FAX_PY
Lb = abs(T.to_xz(T.TAIL_PX, 706.0)[0] - T.to_xz(T.NOSE_PX, 706.0)[0])        # body length without the bull bar
print(f"L (sketch side) {LS:.0f} px = {LS*T.S:.0f} mm; L built {Lb:.0f} mm; uniform scale {T.S} mm/px (112 mm tyre = 176 px)")
top = dict(T.TOP); plan = T.PLAN
def ipx(pts, x):
    q = sorted(pts)
    return float(np.interp(x, [a for a, _ in q], [b for _, b in q]))
print("| station | x/L from nose | roof h/L sketch | roof h/L built | half width/L sketch | half width/L built |")
print("|---|---:|---:|---:|---:|---:|")
errs = []
for px in (130, 150, 180, 225, 267, 320, 380, 450, 520, 560, 610, 660, 700, 730):
    x, _ = T.to_xz(px, 706.0)
    rs = (GROUND - ipx(T.TOP, px)) / LS
    tx = T.TNOSE + (px - T.NOSE_PX) * (T.TTAIL - T.TNOSE) / (T.TAIL_PX - T.NOSE_PX)
    hs = ipx(T.PLAN, tx) * (LS / (T.TTAIL - T.TNOSE)) / LS * (T.HW / T.S) * ((T.TTAIL - T.TNOSE) / LS) / (T.HW / T.S) if False else (ipx(T.PLAN, tx) * T.HW) / (LS * T.S)
    sec = m.section(plane_origin=[x, 0, 0], plane_normal=[1, 0, 0])
    if sec is None:
        continue
    v = sec.vertices
    rb, hb = v[:, 2].max() / Lb, np.abs(v[:, 1]).max() / Lb
    errs.append((rb - rs, hb - hs))
    print(f"| px {px} | {(px - T.NOSE_PX) / LS:.2f} | {rs:.3f} | {rb:.3f} | {hs:.3f} | {hb:.3f} |")
e = np.array(errs); print(f"\nratio error built - sketch (x L): roof mean {e[:,0].mean():+.3f}, max {np.abs(e[:,0]).max():.3f}; half width mean {e[:,1].mean():+.3f}, max {np.abs(e[:,1]).max():.3f}")
roof = m.bounds[1][2]; wid = 2 * np.abs(m.vertices[:, 1]).max()
print(f"overall L:W:H built = 1 : {wid/Lb:.3f} : {roof/Lb:.3f}   (sketch top view W/L = {2*max(b for _,b in T.PLAN)*T.HW/(LS*T.S):.3f}, side view H/L = {(GROUND-463)/LS:.3f}, front view W/H = {316/338:.3f} -> W/L via H = {316/338*(GROUND-463)/LS:.3f})")
