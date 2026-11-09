"""WS-03 panel skin: traced layers.  Layer A = top view (plan) panels, Layer B = side view panels.  All numbers in sheet-68 px unless noted.
Outline of the plan / side silhouettes = the user's masks (mask61.py); every other line is read from sheet 68 (overlays: tools_skin/pskin_overlay.py)."""
import numpy as np
import mask61 as M
import pskin_core as C

_T = M.tables()
PLAN = M.merge(_T["plan"], 15.0, 1.5)            # (x, halfwidth) nose -> tail; a corner under 15 deg is kept when dropping it moves the outline > 1.5 mm
TOP = M.merge(_T["top"], 15.0, 3.0)              # roofline (x, z), wing tab already replaced by a straight line
BOT = M.merge(_T["bot"], 15.0, 2.0)              # floor (x, z)


def _pl(pts, x):
    q = sorted(((float(a), float(b)) for a, b in pts), key=lambda p: p[0])
    return float(np.interp(x, [a for a, _ in q], [b for _, b in q]))


def zr(x):          # mask roofline (centre ridge)
    return _pl(TOP, x)


def zb(x):          # mask floor
    return _pl(BOT, x)


def yo(x):          # mask plan half width (outline)
    return _pl(PLAN, x)


ZSH_T = [(40, 132), (0, 146), (-57, 152), (-100, 151), (-150, 150), (-230, 164), (-255, 167), (-300, 172), (-345, 174), (-360, 165)]


def zsh(x):         # shoulder (belt) height, read from the side view (window sill / fender top)
    return _pl(ZSH_T, x)


def zfl(x):         # floor at x from the station table (ZB_ST, defined below)
    return float(np.interp(x, sorted(ZB_ST), [ZB_ST[k] for k in sorted(ZB_ST)]))


def zol(x):         # outline crease: between shoulder and floor (never within 8 mm of the floor)
    zs, zf = zsh(x), zfl(x)
    return max(0.5 * (zs + zf) if x < -90 else 0.5 * (zs + max(zf, zs - 24.0)), zf + 8.0)


def layer_a(m: C.Model):
    """Top layer: polygons in plan, upper half. Returns the model with vertices/panels (heights from side rules; solved later)."""
    def vr(name, px, py, d=0.0, s=0.0, w=0.7):          # ridge-based height: zr(x) - d - s*|y|
        x, y = C.plan_xy(px, py)
        m.v(name, x, y, zr(x) - d - s * abs(y), w=(3.0, 3.0, 0.5))
        return name

    def vs(name, px, py, w=0.7):                         # on the shoulder (belt) line
        x, y = C.plan_xy(px, py)
        m.v(name, x, y, zsh(x), w=(3.0, 3.0, 0.5))
        return name

    def vc(name, px, w=0.7, d=0.0):                      # on the centre line
        x, _ = C.plan_xy(px, 210.0)
        m.v(name, x, 0.0, zr(x) - d, w=(3.0, 100.0, 4.0))
        return name

    # centre ridge
    vc("c0", 118.5); vc("c2", 258.0); vc("c3", 392.0); vc("c4", 484.0); vc("c5", 525.0); vc("c6", 640.0); vc("c7", 708.0)
    # outline-derived shoulder line S (outline from the mask, inset): nose, flare corner, cowl, rear fender corners, tail
    for k, ((x, hw), ins) in enumerate(zip(PLAN, (0.0, 7.0, 9.0, 9.0, 8.0, 8.0, 8.0, 8.0, 7.0, 3.0, 0.0))):
        last = k == len(PLAN) - 1
        y = 0.0 if last else max(hw - ins, 0.0)
        m.v(f"S{k}", x, y, zsh(x) if k not in (0, len(PLAN) - 1) else zr(x), w=(3.0, 3.0, 1.0) if not last else (3.0, 100.0, 1.0))
    # hood
    vr("A", 176, 168, s=0.12); vr("B", 242, 150, s=0.12); vr("b2", 258, 151, s=0.12)
    vr("D", 204, 128, s=0.20); vr("C", 262, 108, s=0.14)
    # windscreen / roof
    vr("W0", 300, 103, s=0.06); vr("W1", 386, 127, s=0.06)
    vr("R3", 525, 146, s=0.06)
    vs("K", 322, 108); vs("X1", 386, 113); vs("X2", 455, 118); vs("X3", 525, 124); vr("M1", 455, 136.5, s=0.06)             # window base line (belt)
    # rear deck / engine-bay rim
    vr("E0", 525, 176, s=0.05); vr("E1", 548, 150, s=0.05); vr("F0", 640, 150, s=0.05); vr("E2", 662, 150, s=0.05); vr("E3", 692, 172, s=0.05)
    # hood and fender top panels
    m.panel("HC", ["c0", "S0", "A", "B", "b2", "c2"], (0, 0, 1))
    m.panel("FT1", ["S0", "S1", "D", "A"], (0, 1, 1))
    m.panel("FT2", ["S1", "S2", "C", "D"], (0, 1, 1))
    m.panel("HS", ["A", "D", "C", "B"], (0, 1, 1))
    m.panel("CS", ["B", "C", "S2", "W0", "b2"], (0, 1, 1))
    m.panel("WS", ["c2", "b2", "W0", "W1", "c3"], (0, 0, 1))
    m.panel("TA", ["S2", "W0", "K"], (0, 1, 1))
    m.panel("SHD", ["S2", "K", "X1", "X2", "X3", "S5", "S4", "S3"], (0, 1, 1))
    m.panel("G1", ["K", "W0", "W1", "X1"], (0, 1, 0.3))
    m.panel("G2", ["X1", "W1", "M1", "X2"], (0, 1, 0.3))
    m.panel("G3", ["X2", "M1", "R3", "X3"], (0, 1, 0.3))
    m.panel("RF", ["c3", "W1", "M1", "R3", "c5"], (0, 0, 1))
    # rear
    m.panel("GU", ["R3", "E0", "E1"], (0, 1, 1))
    m.panel("Qa", ["X3", "R3", "E1"], (0, 1, 0.5))
    m.panel("Qb", ["X3", "E1", "S5"], (0, 1, 0.8))
    m.panel("Qc", ["S5", "E1", "E2", "S7", "S6"], (0, 1, 1))
    m.panel("DK1", ["c5", "E0", "E1", "F0", "c6"], (0, 0, 1))
    m.panel("DK2", ["c6", "F0", "E2", "E3", "c7"], (0, 0, 1))
    m.panel("FA", ["S7", "S8", "E3", "E2"], (0, 1, 1))
    m.panel("TT", ["E3", "S8", "S9", "S10", "c7"], (-1, 0, 1))
    return m


# ---------------------------------------------------------------------------------------------------------------------------------
# Layer B: side view.  Silhouette = user's side mask (BOT floor polyline below, shoulder S above).  Flank panels hang between the
# shoulder line S (shared with layer A), the outline crease O (plan outline of the mask, y = yo(x)) and the floor B (mask floor).
# ---------------------------------------------------------------------------------------------------------------------------------
STATIONS = [33.9, 28.9, 18.5, 0.5, -42.0, -62.7, -90.1, -97.2, -202.4, -228.2, -238.3, -254.8, -262.6, -267.8, -285.3, -301.9, -340.6, -347.2, -353.9, -356.8]
S_AT = {round(float(x), 1): f"S{k}" for k, (x, _) in enumerate(PLAN)}
DOOR = (-90.1, -228.2)


ZB_ST = {33.9: 131.1, 28.9: 100.7, 18.5: 105.7, 0.5: 134.0, -42.0: 138.8, -62.7: 125.4, -90.1: 52.2, -97.2: 52.2, -202.4: 52.2, -228.2: 52.2, -238.3: 86.0, -254.8: 91.9, -262.6: 107.5,
         -267.8: 108.7, -285.3: 131.2, -301.9: 154.0, -340.6: 160.6, -347.2: 148.0, -353.9: 151.5, -356.8: 155.8}           # mask floor at the stations (steps at x -90 and -228 handled by the sill rail L)


def zl(x):          # sill top (door zone): 65 mm at the front arch edge, 75 mm at the rear notch
    return float(np.interp(x, [DOOR[1], DOOR[0]], [75.2, 65.2]))


def layer_b(m: C.Model):
    """Flank panels.  Nose zone and rear zone: one quad per station (S-O bevel above, O-B below).  Door zone (x -62.7 .. -228.2): panels traced
    from the side view of sheet 68 (door, front pillar band, sill band, rear door corner); the door bottom edge is the widest line (y = mask outline)."""
    sv = {f"S{k}": m.tg[f"S{k}"] for k in range(len(PLAN))}
    chord = sorted(((sv[n][0], sv[n]) for n in sv), reverse=True)

    def s_point(x):
        xs = [c[0] for c in chord][::-1]
        return [float(np.interp(x, xs, [c[1][k] for c in chord][::-1])) for k in range(3)]
    stations = [x for x in STATIONS if x >= -62.7 or x <= -228.2]
    Sn, On, Bn, Ln = {}, {}, {}, {}
    for i, x in enumerate(STATIONS):
        if x not in stations:
            continue
        if round(float(x), 1) in S_AT:
            Sn[x] = S_AT[round(float(x), 1)]
        else:
            xx, yy, zz = s_point(x)
            Sn[x] = m.v(f"Sx{i}", xx, yy, zz, w=(8.0, 8.0, 0.3))
        if x == 33.9:
            On[x] = Bn[x] = Sn[x]
            continue
        last = x == -356.8
        m.v(f"O{i}", x, 0.0 if last else yo(x), zol(x), w=(3.0, 100.0 if last else 3.0, 2.0))
        On[x] = f"O{i}"
        zbx = ZB_ST[x]
        tuck = 3.0 if x == -228.2 else 2.0 + 0.18 * max(zol(x) - zbx, 0.0)
        m.v(f"B{i}", x, 0.0 if last else max(yo(x) - tuck, 0.0), zbx, w=(3.0, 100.0 if last else (3.0 if x == -228.2 else 1.0), 3.0))
        Bn[x] = f"B{i}"
    # door-zone vertices (side-view px from sheet 68)
    def sv_(name, px, py, y, wy=0.4, wz=1.0):
        x, z = C.side_xz(px, py)
        return m.v(name, x, y(x), z, w=(3.0, wy, 3.0))
    Fk = sv_("Fk", 305, 583, lambda x: yo(x) - 3.0, 0.3)
    Fb = sv_("Fb", 345, 663, lambda x: yo(x), 3.0)
    Rb = sv_("Rb", 498, 630, lambda x: yo(x), 3.0)
    A1 = sv_("A1", 310, 678, lambda x: yo(x) - 2.0, 3.0)
    ix = {x: i for i, x in enumerate(STATIONS)}
    # nose + rear station cells
    for a, b in zip(stations[:-1], stations[1:]):
        if a == -62.7 and b == -228.2:
            continue
        i = ix[a]
        m.panel(f"BV{i}", [Sn[a], Sn[b], On[b], On[a]], (0, 1, 0.6), layer="side")
        bb, ba = Bn[b], Bn[a]
        if a == -228.2:                                     # behind the notch the floor is the sill top (z 75.2), vertical wall between
            m.v(f"L{i}", a, yo(a) - 2.0, 75.2, w=(1.0, 1.0, 1.0)); ba = f"L{i}"
        m.panel(f"LW{i}", [On[a], On[b], bb, ba], (0, 1, -0.2), layer="side")
    # door zone
    Dt, S2, B5, O5 = Sn[-228.2], "S2", Bn[-62.7], On[-62.7]
    B6 = m.v("B6", -90.1, yo(-90.1) - 8.0, 52.2, w=(1.0, 0.5, 1.0))
    B9, O9, L9 = Bn[-228.2], On[-228.2], f"L{ix[-228.2]}"
    m.panel("D1", [S2, "S3", Fb, Fk], (0, 1, 0.1), layer="side")
    m.panel("D2", ["S3", "S4", Rb, Fb], (0, 1, 0.1), layer="side")
    m.panel("D3", ["S4", Dt, Rb], (0, 1, 0.1), layer="side")
    m.panel("FPu", [S2, Fk, O5], (0, 1, 0.3), layer="side")
    m.panel("FPl", [O5, Fk, Fb, A1, B5], (0, 1, 0), layer="side")
    m.panel("SBa", [A1, Fb, B6], (0, 1, -0.5), layer="side")
    m.panel("SBb", [Fb, B9, B6], (0, 1, -0.5), layer="side")
    m.panel("SBc", [Fb, Rb, B9], (0, 1, -0.5), layer="side")
    m.panel("RB", [Dt, O9, L9, B9, Rb], (0, 1, 0), layer="side")
    # nose fascia (centre)
    m.v("bc", 28.9, 0.0, ZB_ST[28.9], w=(1.0, 100.0, 1.0))
    m.panel("FF", ["c0", Sn[33.9], Bn[28.9], "bc"], (1, 0, 0), layer="side")
    return m
