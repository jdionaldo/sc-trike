"""Rev 15: widths of the reference plan (sheet 61 top view, read from the plan crop, +-3 mm) against our skin before/after the canopy / hood alignment.
usage: WS03_ALONE=1 python tools_skin/width_table.py"""
import numpy as np
import skin_alone, skin7 as K, trace61 as T
ip = lambda x, pts: float(np.interp(x, [p[0] for p in sorted(pts)], [p[1] for p in sorted(pts)]))
PLAN = [(a, b * T.HW) for a, b in T.PLAN]; ROOFW = [(a, b * T.HW) for a, b in T.ROOFW]
HPin = [(178, 45 * T.HW), (242, 63 * T.HW)]; HPout = [(178, 45 * T.HW), (208, 86 * T.HW), (263, 102 * T.HW)]
GLASS_REF = [(277, 37.0), (303, 66.0), (380, 35.0)]
GLASS_OLD = [(262, 24.0), (297, 50.0), (380, 27.0)]; GLASS_NEW = [(262, 33.0), (297, 60.0), (380, 29.0)]
print("| station (sheet px) | body ref | body ours | canopy ref | canopy ours | glass ref | glass v14 | glass v15 | hood panel ref (in..out) | scoop v14 | scoop v15 |")
print("|---|---|---|---|---|---|---|---|---|---|---|")
for name, px in (("nose", 122), ("hood front", 160), ("scoop / hood panel", 215), ("vent", 215), ("windscreen base", 297), ("roof front", 330), ("roof rear", 385)):
    x = K.Xt(px)
    row = [f"{name} ({px})", f"{ip(px, PLAN):.1f}", f"{K.hw(x):.1f}", f"{ip(px, ROOFW):.1f}", f"{K._pl(K.YR, x):.1f}"]
    g = lambda t: f"{ip(px, t):.1f}" if t[0][0] <= px <= t[-1][0] else "-"
    row += [g(GLASS_REF), g(GLASS_OLD), g(GLASS_NEW)]
    if name == "scoop / hood panel":
        hin, hout = ip(px, HPin), ip(px, HPout)
        row += [f"{hin:.0f}..{hout:.0f}", f"{K._pl(K.YR, x) + 3:.0f}..{K._pl(K.YR, x) + 19:.0f}", f"{hin + 1.55:.0f}..{hin + 15.2:.0f}"]
    elif name == "vent":
        row += ["panel centre", "0..9", "0..9"]
    else:
        row += ["-", "-", "-"]
    print("| " + " | ".join(row) + " |")
