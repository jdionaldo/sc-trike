"""Strict trace of sheet 61 (rev 9). All tables are pixel coordinates read off the 2000x848 sheet, converted to chassis-frame mm here.

Side view : front axle (176, 706) px, tyre radius 88 px (sheet) = 56 mm -> S = 0.636 mm/px; rear axle is 450 mm behind the front axle.
Top view  : stretched affinely onto the side view's nose/tail px, so both views share one x.
Stretch   : the sheet's wheelbase is 579 px = 368 mm, ours is 450 mm. Only the MIDDLE (roof and doors, px XA..XB) is stretched, uniformly in x; nose/hood/cowl/windscreen and the
            tail/rear fender keep the traced shape.  Chassis frame is the sheet rotated by the 4 deg ground rake (rear axle 31.5 mm lower), front axle at (0, 0).
"""
import math

import numpy as np

S = 0.636
FAX_PX, FAX_PY = 176.0, 706.0
WB = 450.0
XA, XB = 375.0, 560.0                                  # stretch region (side-view px)
WB_SHEET = (755.0 - FAX_PX) * S
EXTRA = WB - WB_SHEET                                  # how much the middle must grow
K = 1.0 + EXTRA / ((XB - XA) * S)                      # uniform x stretch of the middle
RAKE = math.radians(4.0)

NOSE_PX, TAIL_PX = 122.0, 737.0                        # side view nose/tail
TNOSE, TTAIL = 120.0, 721.0                            # top view nose/tail


def u_of(px):
    """Forward distance from the front axle (mm, +forward) with the middle stretched."""
    if px <= XA:
        return (FAX_PX - px) * S
    if px <= XB:
        return (FAX_PX - XA) * S - (px - XA) * S * K
    return (FAX_PX - px) * S - EXTRA


def to_xz(px, py):
    u, v = u_of(px), (FAX_PY - py) * S
    c, s_ = math.cos(RAKE), math.sin(RAKE)
    return (u * c - v * s_, v * c + u * s_)


def top_to_side_px(tx):
    return NOSE_PX + (tx - TNOSE) * (TAIL_PX - NOSE_PX) / (TTAIL - TNOSE)


def hw_mm(hw_px):
    return hw_px * 0.624


# ---- side view silhouette (px) ------------------------------------------------------------------------------------------------------------------
TOP = [(124, 586), (131, 577), (180, 554), (225, 541), (267, 535), (380, 475), (400, 472), (500, 463), (548, 466), (610, 470), (702, 505), (730, 509), (737, 509)]
FLOOR = [(124, 622), (160, 598), (265, 598), (300, 709), (555, 709), (560, 664), (580, 625), (610, 590), (640, 553), (702, 540), (737, 552)]
BELT = [(124, 586), (131, 577), (180, 554), (225, 541), (267, 537), (365, 549), (485, 535), (548, 530), (556, 498), (610, 498), (640, 505), (702, 518), (737, 530)]   # shoulder crease (hood top where no cabin)
# ---- plan (top view px, half width px) ----------------------------------------------------------------------------------------------------------
PLAN = [(120, 28), (276, 132), (320, 141), (520, 128), (560, 141.5), (610, 141.5), (700, 92.5), (721, 31)]
ROOFW = [(120, 0), (262, 50), (297, 100), (385, 54), (548, 54), (560, 70), (610, 70), (700, 40), (721, 14)]           # roof / hump ridge half width (px, top view)


def mm_polyline(pts, key="side"):
    """px polyline -> [(x, value)] mm, sorted by x descending. side: value = z; plan: value = half-width mm."""
    out = []
    for px, v in pts:
        if key == "side":
            x, z = to_xz(px, v)
            out.append((x, z))
        else:
            ps = top_to_side_px(px)
            out.append((to_xz(ps, 706.0)[0], hw_mm(v)))
    return out


def simplify(pts, min_turn=15.0):
    """Drop vertices whose turn (in true mm) is under min_turn degrees, repeatedly dropping the smallest."""
    p = sorted(pts, reverse=True)
    while True:
        best, bi = 1e9, None
        for i in range(1, len(p) - 1):
            a = math.atan2(p[i][1] - p[i - 1][1], p[i][0] - p[i - 1][0])
            b = math.atan2(p[i + 1][1] - p[i][1], p[i + 1][0] - p[i][0])
            t = abs(math.degrees((b - a + math.pi) % (2 * math.pi) - math.pi))
            if t < best:
                best, bi = t, i
        if bi is None or best >= min_turn:
            return p
        p.pop(bi)


if __name__ == "__main__":
    print("EXTRA", round(EXTRA, 1), "K", round(K, 3))
    for n, pts, k in (("TOP", TOP, "side"), ("FLOOR", FLOOR, "side"), ("BELT", BELT, "side"), ("PLAN", PLAN, "plan"), ("ROOFW", ROOFW, "plan")):
        m = mm_polyline(pts, k)
        print(n, [(round(a), round(b)) for a, b in m])
