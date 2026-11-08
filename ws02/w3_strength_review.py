"""WS-03 strength and robustness review (2.2 kg car).  Re-runnable: reads the live geometry modules (parts/w3_*.py), builds beam-FE models of the cage frame,
front arm and rear arm + shock hoop, runs hand checks for the rest, and returns a list of rows (part, load case, stress, allowable, FS, minimum FS).
`python w3_strength_review.py` prints the table and writes WS03_STRENGTH.md (via w3_strength_report.py).  Analysis only: no geometry is changed.

Material model (printed PETG, conservative; state these numbers wherever the results are quoted):
  SIP  30 MPa  in-plane (along the print line) design stress   (datasheet ~45 MPa yield, x0.67 for print defects, creep, moisture)
  SZ   15 MPa  across layers (50 % of in-plane)
  tube/beam members: allowable follows the angle c between the member axis and the bed normal:  1/sqrt(c^2/SZ^2 + (1-c^2)/SIP^2)
  KT   1.5     stress concentration at every tube/ball node and notch (applied to the FE stress)
  ULT  1.4     ultimate / design stress, used only for the 1 m drop (survival) case
  CREEP 0.4    sustained-load derating (shock spring preload, static weight)
  thread pull-out: 6 MPa shear on d x engagement;  steel pins 400 MPa yield;  E = 1500 MPa along the print line
"""
import math
import numpy as np

G = 9.81
M = 2.2                       # kg, upper end of the 2.0..2.2 kg range
FR = 0.64                     # front weight share
WF, WR = FR * M * G, (1 - FR) * M * G          # static axle loads, N
NF, NR = 1.5 * WF, 3 * WR     # 3 g landing on ONE front wheel = 3 x its static half-axle load (design); the whole-axle landing (2 x NF) is an abuse case / 3 g on the rear wheel
FYF, FYR = 1.5 * WF, 1.5 * WR                  # 1.5 g cornering, outer wheel takes the whole axle's lateral load
FXF = 2 * 0.88 * M * G / 2    # 2 g braking, dynamic front share 88 %, per front wheel
FXR = 2 * 0.12 * M * G
RT, YW = 56.0, 134.55         # tyre radius (112 mm), front half track
SIP, SZ, KT, ULT, CREEP, TAUT = 30.0, 15.0, 1.5, 1.4, 0.4, 6.0
E, NU = 1500.0, 0.38
SERVO_LEAN = 17.7 * 98.1      # N.mm, Injora INJS15 stall at 7.4 V
SERVO_STEER = 12.0 * 98.1     # N.mm, steering servo (12 kg.cm)
MIN = {"frame": 2.0, "arm": 3.0, "wing": 2.5, "hinge": 2.0, "gen": 2.0, "abuse": 1.0, "creep": 1.5}


def allow(c):
    c = min(1.0, max(0.0, c))
    return 1.0 / math.sqrt(c * c / SZ ** 2 + (1 - c * c) / SIP ** 2)


# --------------------------------------------------------------------------------------------- beam FE
class FE:
    """3D Euler-Bernoulli frame, 6 dof per node, round members.  Partial restraints, reactions, per-member utilisation with print-layer-aware allowables."""

    def __init__(self):
        self.nodes, self.edges = {}, []

    def node(self, n, p):
        self.nodes[n] = np.array(p, float)

    def edge(self, a, b, r, rigid=False):
        self.edges.append((a, b, r, rigid))

    def solve(self, loads, fixed, nbed):
        keys = list(self.nodes)
        idx = {k: i for i, k in enumerate(keys)}
        n = len(keys)
        K = np.zeros((6 * n, 6 * n))
        elem = []
        G_ = E / (2 * (1 + NU))
        for a, b, r, rig in self.edges:
            A = math.pi * r ** 2; I = math.pi * r ** 4 / 4; J = 2 * I
            pa, pb = self.nodes[a], self.nodes[b]
            L = float(np.linalg.norm(pb - pa)); ex = (pb - pa) / L
            ref = np.array([0, 0, 1.0]) if abs(ex[2]) < 0.9 else np.array([1.0, 0, 0])
            ey = np.cross(ref, ex); ey /= np.linalg.norm(ey); ez = np.cross(ex, ey)
            T = np.zeros((12, 12))
            for i in range(4):
                T[3 * i:3 * i + 3, 3 * i:3 * i + 3] = np.vstack([ex, ey, ez])
            k = np.zeros((12, 12))
            k[0, 0] = k[6, 6] = E * A / L; k[0, 6] = k[6, 0] = -E * A / L
            k[3, 3] = k[9, 9] = G_ * J / L; k[3, 9] = k[9, 3] = -G_ * J / L
            for (v, th, s) in ((1, 5, 1), (2, 4, -1)):
                c = E * I / L ** 3
                for (i, j, val) in ((v, v, 12), (v, th, 6 * L * s), (v, 6 + v, -12), (v, 6 + th, 6 * L * s), (th, th, 4 * L * L), (th, 6 + v, -6 * L * s), (th, 6 + th, 2 * L * L),
                                    (6 + v, 6 + v, 12), (6 + v, 6 + th, -6 * L * s), (6 + th, 6 + th, 4 * L * L)):
                    k[i, j] = k[j, i] = c * val
            dof = list(range(6 * idx[a], 6 * idx[a] + 6)) + list(range(6 * idx[b], 6 * idx[b] + 6))
            K[np.ix_(dof, dof)] += T.T @ k @ T
            elem.append((a, b, r, A, I, J, k, T, dof, ex, rig))
        f = np.zeros(6 * n)
        for name, vec in loads:
            f[6 * idx[name]:6 * idx[name] + len(vec)] += vec
        fx = set()
        for name, dofs in fixed.items():
            for d in (range(6) if dofs == "all" else dofs):
                fx.add(6 * idx[name] + d)
        free = [d for d in range(6 * n) if d not in fx]
        u = np.zeros(6 * n)
        u[free] = np.linalg.lstsq(K[np.ix_(free, free)], f[free], rcond=None)[0]
        R = K @ u - f
        react = {k_: R[6 * i:6 * i + 6] for k_, i in idx.items() if any(6 * i + d in fx for d in range(6))}
        nb = np.asarray(nbed, float)
        worst = (1e9, "", 0.0, 0.0)
        per = []
        for a, b, r, A, I, J, k, T, dof, ex, rig in elem:
            if rig:
                continue
            fl = k @ (T @ u[dof])
            vm = 0.0
            for end in (0, 1):
                F = fl[6 * end:6 * end + 6]
                sig = abs(F[0]) / A + math.hypot(F[4], F[5]) * r / I
                tau = abs(F[3]) * r / J
                vm = max(vm, math.sqrt(sig ** 2 + 3 * tau ** 2))
            al = allow(abs(float(ex @ nb)))
            fs = al / (KT * vm) if vm > 1e-9 else 1e9
            per.append((fs, f"{a}-{b}", KT * vm, al))
            if fs < worst[0]:
                worst = (fs, f"{a}-{b}", KT * vm, al)
        defl = max(float(np.linalg.norm(u[6 * i:6 * i + 3])) for i in range(n))
        return {"fs": worst[0], "member": worst[1], "stress": worst[2], "allow": worst[3], "defl": defl, "react": react, "per": per}


EAR_SHARE = 0.25              # share of the arm-pivot reaction that enters the cage through the servo-ear plate (rest goes into the base plate through the 12 housing bolts); ASSUMED
ROWS = []
INFO = {}


def add(group, part, case, stress, allow_, minfs, orient, note=""):
    fs = allow_ / stress if stress > 1e-12 else 1e9
    ROWS.append({"group": group, "part": part, "case": case, "stress": stress, "allow": allow_, "fs": fs, "min": minfs, "orient": orient, "note": note})
    return fs


def add_fs(group, part, case, fs, stress, allow_, minfs, orient, note=""):
    ROWS.append({"group": group, "part": part, "case": case, "stress": stress, "allow": allow_, "fs": fs, "min": minfs, "orient": orient, "note": note})
    return fs


# --------------------------------------------------------------------------------------------- front arm
def hub_loads(Fx, Fy, N, yi, yo):
    """Equivalent loads on the arm's two hub nodes from ground forces at the contact patch (braking Fx aft, lateral Fy inward, vertical N).
    The carrier is a parallelogram link with the upper link at z +40: braking torque Fx*RT is reacted by the link, so the hub sees (1 + RT/40) Fx."""
    e = YW - 0.5 * (yi + yo)
    dy = yo - yi
    Gx, Gy, Gz = -Fx, -Fy, N
    Hx = Gx * (1 + RT / 40.0)
    Mx = e * Gz + RT * Gy
    out = []
    for p, sg in (("i", -1.0), ("o", 1.0)):
        out.append((f"T{p}", np.array([Hx / 2 + sg * e * Gx / dy, Gy / 2, Gz / 2 + sg * Mx / dy])))
    return out


def front_arm_model():
    from parts import w3_front as W, w3_style as S
    t = FE()
    ya = W.ARM_Y[0]
    yi, yo = ya + 2.5, ya + S.YO
    for k, (x, z) in S.ARM_NODES.items():
        t.node(k + "i", (x, yi, z))
        xo, zo = S.ARM_OUTER[k]
        t.node(k + "o", (xo, yo, zo))
    for a, b in S.ARM_RAILS + S.ARM_WEB:
        t.edge(a + "i", b + "i", S.inner_r(a, b))
    for a, b in S.ARM_RAILS:
        t.edge(a + "o", b + "o", S.RO)
    for a, b in S.ARM_WEB:
        t.edge(a + "o", b + "o", S.RW)
    for rails, r in (([("U0", "U1"), ("U1", "U2"), ("U2", "U3")], S.LAT_TOP), ([("L0", "L1"), ("L1", "L2")], S.LAT_BOT)):
        for a, b in rails:
            t.edge(a + "i", b + "o", r); t.edge(b + "i", a + "o", r)
    for k in S.TIE_R:
        t.edge(k + "i", k + "o", S.TIE_R[k])
    for p_, y_ in (("i", yi), ("o", yo)):                       # hub centres (pivot at x -100, axle at x 0, both on z = 0), rigid bars to the plane's end nodes
        t.node("P" + p_, (-W.ARM_L, y_, 0.0)); t.node("T" + p_, (0.0, y_, 0.0))
        for k in ("U0", "L0"):
            t.edge("P" + p_, k + p_, 8.0, rigid=True)
        for k in ("U3", "L2"):
            t.edge("T" + p_, k + p_, 8.0, rigid=True)
    return t, yi, yo


FRONT_CASES = {"3 g bump, one front wheel": (0.0, 0.0, NF), "landing on one wheel, whole front axle 3 g (abuse)": (0.0, 0.0, 2 * NF), "3 g bump + 1.5 g lateral (kerb strike)": (0.0, FYF, NF),
               "1.5 g cornering (outer wheel)": (0.0, FYF, 1.4 * WF), "2 g braking": (FXF, 0.0, 0.5 * WF)}


def front_arm():
    t, yi, yo = front_arm_model()
    fixed = {"Pi": [0, 1, 2], "Po": [0, 1, 2], "U1i": [2]}      # pivot pin fixes translations; the lean rod holds the lug vertically
    res = {}
    for name, (fx, fy, n) in FRONT_CASES.items():
        r = t.solve(hub_loads(fx, fy, n, yi, yo), fixed, (0, 1, 0))
        pr = sum(r["react"][k][:3] for k in ("Pi", "Po")) + r["react"]["U1i"][:3] * 0                # force the pivot pins exert on the arm
        rod = r["react"]["U1i"][2]
        res[name] = (r, pr, rod, (fx, fy, n))
    return res


# --------------------------------------------------------------------------------------------- rear arm + shock hoop
def rear_arm():
    from parts import w3_style as S, w3_drive as D, w3_shock as SK
    L = math.hypot(D.XR - D.RAXLE[0], D.RAXLE[1])
    us = SK.caret_stations(L)
    WS = 46.0 - SK.BOSS_Y[0]                   # print frame of the shock-carrying arm: w' = y - BOSS_Y[0]
    V = 9.5
    t = FE()
    planes = {"i": (S.REAR_W[0] + WS, *S.REAR_PL[0]), "o": (S.REAR_W[1] + WS, *S.REAR_PL[1])}
    for p_, (w, r, rw) in planes.items():
        for sg in (1, -1):
            for i, u in enumerate(us):
                t.node(f"{i}{'p' if sg > 0 else 'n'}{p_}", (u, sg * V + (SK.caret_rise(u, L) if sg > 0 else 0.0), w))
            for i in range(4):
                t.edge(f"{i}{'p' if sg > 0 else 'n'}{p_}", f"{i+1}{'p' if sg > 0 else 'n'}{p_}", r)
        for i in range(4):
            a, b = ("p", "n") if i % 2 == 0 else ("n", "p")
            t.edge(f"{i}{a}{p_}", f"{i+1}{b}{p_}", rw)
    for i in range(4):
        for sg in "pn":
            t.edge(f"{i}{sg}i", f"{i+1}{sg}o", S.REAR_LAT); t.edge(f"{i+1}{sg}i", f"{i}{sg}o", S.REAR_LAT)
    for i in (0, 4):
        for sg in "pn":
            t.edge(f"{i}{sg}i", f"{i}{sg}o", S.REAR_TIE)
    for p_, (w, r, rw) in planes.items():                      # pivot and axle hubs
        t.node("P" + p_, (0.0, 0.0, w))
        for sg in "pn":
            t.edge("P" + p_, f"0{sg}{p_}", 8.0, rigid=True)
            t.edge(f"4{sg}{p_}", f"4{'n' if sg == 'p' else 'p'}{p_}", 8.0, rigid=True)
    t.node("H", (L, 0.0, -SK.BOSS_Y[0]))                       # wheel centre, y = 0
    for p_ in "io":
        for sg in "pn":
            t.edge("H", f"4{sg}{p_}", 8.0, rigid=True)
    # shock hoop on the outer plane: legs from the top rail, cross tube to the lug plate
    u_l, v_l = SK._lug_uv()
    wo, wc = planes["o"][0], 0.5 * (SK.PLATE_Y[0] + SK.PLATE_Y[1]) - SK.BOSS_Y[0]
    t.node("B", (u_l, v_l, wo)); t.node("C", (u_l, v_l, wc))
    t.node("A2", (L - 4.0, V + SK.caret_rise(L - 4.0, L), wo))
    t.edge("2po", "B", SK.LEG_R); t.edge("A2", "B", SK.LEG_R); t.edge("A2", "4po", S.REAR_PL[1][0]); t.edge("B", "C", SK.HOOP_R)
    Pm, d, n, _ = SK._geom()
    to_arm = lambda fx, fz: np.array([fx * d[0] + fz * d[1], fx * n[0] + fz * n[1]])
    dn, up = SK.travel_angles()
    lever = min(SK.mount_lever(a_) for a_ in np.linspace(dn, up, 15))
    lug = SK.lug_point(0.0); tab = np.array(SK.tab_xz())
    shock_dir = to_arm(*(tab - lug)) / np.linalg.norm(tab - lug)          # unit vector lower eye -> upper eye in (u, v)
    fixed = {"Pi": [0, 1, 2, 5], "Po": [0, 1, 2]}

    def case(Fx, Fy, N, Fs, extra=None):
        # ground forces on the tyre: vertical N up, lateral Fy inward (-w), braking/drive Fx aft; contact patch RT below the hub
        uv = to_arm(-Fx, N)
        F = np.array([uv[0], uv[1], -Fy])
        mom = np.cross(np.array([0.0, -RT, 0.0]), F)
        loads = [("H", np.concatenate([F, mom]))]
        if extra:                                                  # belt tension: a pair acting on the axle-end nodes, reacted at the pivot hubs
            for nn in ("4pi", "4po", "4ni", "4no"):
                loads.append((nn, np.array([extra / 4.0, 0, 0, 0, 0, 0])))
        fs_vec = -Fs * shock_dir                                           # shock pushes the lower eye away from the upper eye
        loads.append(("C", np.array([fs_vec[0], fs_vec[1], 0, 0, 0, 0])))
        r = t.solve(loads, fixed, (0, 0, 1))
        r["Fs"] = Fs
        return r
    out = {}
    out["3 g bump, rear wheel"] = case(0, 0, NR, NR * lever)
    out["3 g bump + 1.5 g lateral"] = case(0, FYR, NR, NR * lever)
    out["1.5 g cornering"] = case(0, FYR, 1.3 * WR, 1.3 * WR * lever)
    out["2 g braking"] = case(FXR, 0, WR, WR * lever)
    out["drive: 10 N thrust + 80 N belt"] = case(-10.0, 0, WR, WR * lever, extra=-80.0)
    out["sustained: 1 g + spring preload 10 N"] = case(0, 0, WR, WR * lever + 10.0)
    INFO["rear_lever"] = lever
    INFO["rear_shock_dir_world"] = (tab - lug) / np.linalg.norm(tab - lug)
    INFO["rear_Fs3g"] = NR * lever
    return out, lever


# --------------------------------------------------------------------------------------------- cage frame
def frame():
    from parts import w3_frame as F, w3_shock as SK
    N = F.nodes()
    nm = {}
    t = FE()
    for k, p in N.items():
        t.node(k + "+", p)
        if abs(p[1]) < 1e-6:
            nm[k + "-"] = k + "+"
        else:
            t.node(k + "-", (p[0], -p[1], p[2])); nm[k + "-"] = k + "-"
        nm[k + "+"] = k + "+"
    removed = []
    try:                                                          # the motor can opens the -y half of the pivot hoop
        from layout3wd import MOTOR_C
        mx, my, mz = MOTOR_C
        def inside(p):
            can = (mx - 29.05 - 10.5 <= p[0] <= mx + 58.1 + 2.5 - 29.05) and math.hypot(p[1] - my, p[2] - mz) <= 20.5
            plate = (mx - 29.05 - 12.0 <= p[0] <= mx - 29.05) and abs(p[1] - my) <= 24.0 and abs(p[2] - mz) <= 17.0
            return can or plate
    except Exception:
        inside = lambda p: False
    seen = set()
    for a, b, r, ta, tb in F.EDGES:
        for sg in "+-":
            if sg == "-" and (a, b) in getattr(F, "NEG_DROP_EDGES", ()):
                continue
            na, nb = nm[a + sg], nm[b + sg]
            key = frozenset((na, nb))
            if key in seen or na == nb:
                continue
            seen.add(key)
            pa, pb = t.nodes[na], t.nodes[nb]
            frac = np.mean([inside(pa + (pb - pa) * s) for s in np.linspace(0, 1, 21)])
            if frac > 0.3:
                removed.append(f"{a}-{b}{sg}")
                continue
            t.edge(na, nb, r)
    for k, p_ in F.NODES_NEG.items():                              # bypass nodes and tubes outboard of the motor can (-y side only)
        t.node(k + "-", p_); nm[k + "-"] = k + "-"
    for a, b, r, ta, tb in F.EDGES_NEG:
        t.edge(nm[a + "-"], nm[b + "-"], r)
    INFO["frame_removed"] = removed

    def split(a, b, name, frac):
        for i, (x, y, r, rig) in enumerate(t.edges):
            if {x, y} == {a, b}:
                p = t.nodes[a] + (t.nodes[b] - t.nodes[a]) * frac
                t.node(name, p); t.edges.pop(i); t.edge(a, name, r); t.edge(name, b, r)
                return
    y_sh = 0.5 * (SK.PLATE_Y[0] + SK.PLATE_Y[1])
    split("R2+", "C262+", "SH", y_sh / N["R2"][1])
    yh = 0.5 * (F.HINGE_LUG[0] + F.HINGE_LUG[1])
    split("BT+", "CBT+", "HGp", yh / N["BT"][1])
    split("BT-", "CBT+", "HGn", yh / N["BT"][1]) if "BT-" in t.nodes else None
    fixed = {k + sg: [0, 1, 2] for k in F.FEET for sg in "+-" if k + sg in t.nodes}
    return t, fixed, F, SK, N


def frame_cases(front, rear):
    t, fixed, F, SK, N = frame()
    out = {}
    nb = (0, 0, 1)
    ear = EAR_SHARE                                              # share of the front-arm pivot reaction that goes through the servo-ear plate (PM) and not the base-plate housing bolts
    for name, (r, pr, rod, (fx, fy, n)) in front.items():
        if name.startswith("3 g bump, one"):
            nm_ = "3 g bump, one front wheel (arm pivot reaction via ear plate)"
        else:
            nm_ = name + " (arm pivot reaction via ear plate)"
        f_on_frame = -pr * ear
        link = np.array([FXF * RT / 40.0 if "braking" in name else 0.0, 0, 0])
        out[nm_] = t.solve([("PM+", np.concatenate([f_on_frame, [0, 0, 0]])), ("PL+", np.concatenate([link, [0, 0, 0]]))], fixed, nb)
    # rear shock: force on the cage tab (upper eye) at the 3 g landing
    d = INFO["rear_shock_dir_world"] * INFO["rear_Fs3g"]
    out["3 g bump, rear wheel (shock tab on R2 cross tube)"] = t.solve([("SH", np.array([d[0], 0, d[1], 0, 0, 0]))], fixed, nb)
    sus = INFO["rear_shock_dir_world"] * (WR * INFO["rear_lever"] + 10.0)
    r = t.solve([("SH", np.array([sus[0], 0, sus[1], 0, 0, 0]))], fixed, nb)
    out["sustained: 1 g + spring preload (shock tab)"] = r
    fh = 0.25 * 10 * G * 0.5 * 1.0                       # skin 0.25 kg, 10 g nose hit: 24.5 N over two lugs
    hl = [("HGp", np.array([-fh, 0, fh, 0, 0, 0]))] + ([("HGn", np.array([-fh, 0, fh, 0, 0, 0]))] if "HGn" in t.nodes else [])
    out["skin flipped / nose impact 10 g (hinge lugs on the bumper bar)"] = t.solve(hl, fixed, nb)
    out["wing pull-off 20 N on the hood tab"] = t.solve([("R2+", np.array([0, 0, 20.0, 0, 0, 0]))], fixed, nb)
    return out, t, fixed


# --------------------------------------------------------------------------------------------- hand checks
def poly_props(pgs, h=0.2):
    """Area, centroid, Ixx, Iyy (about the centroid) of a union of shapely polygons (holes respected), by rasterising at h mm."""
    import shapely
    x0, y0 = min(p.bounds[0] for p in pgs), min(p.bounds[1] for p in pgs)
    x1, y1 = max(p.bounds[2] for p in pgs), max(p.bounds[3] for p in pgs)
    X, Y = np.meshgrid(np.arange(x0 + h / 2, x1, h), np.arange(y0 + h / 2, y1, h))
    m = np.zeros(X.shape, bool)
    for p in pgs:
        m |= shapely.contains_xy(p, X, Y)
    dA = h * h
    xc, yc = X[m].mean(), Y[m].mean()
    return m.sum() * dA, xc, yc, float(((Y[m] - yc) ** 2).sum() * dA), float(((X[m] - xc) ** 2).sum() * dA)


def wing_hanger():
    from parts import w3_tail as TL
    import mono_build as MB
    m = MB.to_trimesh(TL._hanger_left())
    zlo, zhi = float(m.bounds[0, 2]), float(m.bounds[1, 2])
    x_cp = TL.X_LE - 0.25 * TL.CHORD
    z_cp = zhi - 5.0
    rho, V = 1.2, 40 / 3.6
    q = 0.5 * rho * V * V
    S = 2 * TL.SPAN * TL.CHORD * 1e-6
    Lift, Drag = q * S * 1.3, q * S * 0.3
    mw = 0.07                                                   # kg, blade ~47 g + two hangers
    cases = {"1.5 g aero + handling at 40 km/h (downforce, drag, 3 g vertical, 1.5 g lateral)":
             dict(Fz=-(1.5 * Lift + 3 * mw * G) / 2, Fx=-(1.5 * Drag) / 2, Fy=1.5 * mw * G / 2, Fy_tip=0.0, tip=0.0),
             "abuse: 10 N press on the blade tip": dict(Fz=-10.0, Fx=0.0, Fy=0.0, tip=10.0, Fy_tip=0.0),
             "abuse: 10 N side knock on the blade tip": dict(Fz=0.0, Fx=0.0, Fy=10.0, tip=0.0, Fy_tip=0.0)}
    res = {}
    zs = np.linspace(zlo + 2.0, zhi - 8.0, 14)
    secs = []
    for z in zs:
        sec = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
        if sec is None:
            continue
        p2, _ = sec.to_planar(to_2D=np.eye(4), check=False)
        pgs = [pg for pg in p2.polygons_full if pg.area > 1.0]
        if not pgs:
            continue
        A, xc, yc, Ixx, Iyy = poly_props(pgs)
        b = np.array([pg.bounds for pg in pgs])
        cx = max(b[:, 2].max() - xc, xc - b[:, 0].min()); cy = max(b[:, 3].max() - yc, yc - b[:, 1].min())
        secs.append((z, A, xc, yc, Ixx, Iyy, cx, cy))
    for name, c in cases.items():
        worst = (1e9, 0, 0)
        for z, A, xc, yc, Ixx, Iyy, cx, cy in secs:
            lz = z_cp - z
            Mx = c["Fy"] * lz + c["tip"] * (TL.SPAN - TL.LEG_Y) + 0.0       # about x: lateral force x lever, plus the tip press acting at the blade tip
            My = c["Fx"] * lz + c["Fz"] * (x_cp - xc)
            sig = (abs(c["Fz"]) / A + abs(Mx) * cy / Ixx + abs(My) * cx / Iyy) * 2.0       # x2: stress concentration at the fillets / prong roots
            fs = SIP / sig
            if fs < worst[0]:
                worst = (fs, z, sig, A)
        res[name] = worst
    # foot screws: overturning about the foot's outer / front edges; N screws share the pull (the inner screw carries the y couple, all share the x couple)
    foot = {}
    ns = len(TL.FOOT_SCR)
    arm_y = TL.FOOT_Y[1] - min(TL.FOOT_SCR)                        # outer foot edge to the inner screw
    arm_x = 0.5 * (TL.FOOT_X[1] - TL.FOOT_X[0])
    for name, c in cases.items():
        z0 = zlo
        Mx = c["Fy"] * (z_cp - z0) + c["tip"] * (TL.SPAN - TL.LEG_Y)
        My = c["Fx"] * (z_cp - z0) + c["Fz"] * (x_cp - 0.5 * sum(TL.FOOT_X))
        T = max(0.0, abs(Mx) / arm_y + abs(My) / arm_x / ns + c["Fz"] / ns)        # tension in the worst screw; downforce (Fz < 0) relieves it
        foot[name] = T
    INFO["wing"] = {"lift_N": Lift, "drag_N": Drag, "q_Pa": q, "area_m2": S, "z_cp": z_cp, "zlo": zlo, "mass_kg": mw}
    return res, foot, secs


def checks():
    ROWS.clear()
    from parts import w3_front as W, w3_style as S, w3_drive as D, w3_frame as F, w3_shock as SK, w3_lean as LN, w3_tail as TL
    # ---------------- (c) front arm
    front = front_arm()
    worst = min(front.items(), key=lambda kv: kv[1][0]["fs"])
    for name, (r, pr, rod, ld) in front.items():
        add_fs("abuse" if "abuse" in name else "arm", "Front arm (beam FE, 4 tubes/plane, X lattice)", name, r["fs"], r["stress"], r["allow"], 1.0 if "abuse" in name else MIN["arm"], "plates up = outer face on the bed (as now); lattice tubes across the planes are the weak direction",
               f"worst member {r['member']}; tip deflection {r['defl']:.1f} mm; lean-rod force {abs(rod):.0f} N")
    r0, pr0, rod0, _ = front["3 g bump, one front wheel"]
    _t, _yi, _yo = front_arm_model()
    _l = [(n_, v_ * np.array([1, 1, 0])) for n_, v_ in hub_loads(0, 0, NF, _yi, _yo)]
    _l = [("Ti", np.array([0, 0, NF / 2])), ("To", np.array([0, 0, NF / 2]))]
    INFO["front_bump_no_couple_fs"] = _t.solve(_l, {"Pi": [0, 1, 2], "Po": [0, 1, 2], "U1i": [2]}, (0, 1, 0))["fs"]
    INFO["lean_rod_bump"] = abs(rod0)
    # hub bearing seat (5x11x4 bearings in the 22 mm outer hub), radial load from the vertical-load couple
    fz = max(abs(v) for v in [hub_loads(0, 0, NF, W.ARM_Y[0] + 2.5, W.ARM_Y[0] + S.YO)[1][1][2], hub_loads(0, 0, NF, W.ARM_Y[0] + 2.5, W.ARM_Y[0] + S.YO)[0][1][2]])
    p = fz / (11.0 * 4.0); ro, ri = 11.0, 5.575
    hoop = p * (ro ** 2 + ri ** 2) / (ro ** 2 - ri ** 2)
    add("arm", "Front arm hub, 11 mm bearing seat (22 mm hub)", f"3 g bump, radial bearing load {fz:.0f} N", KT * hoop, SIP, MIN["arm"], "ring in the layer plane: in-plane hoop stress, good")
    # upper link buckling
    Pcr = math.pi ** 2 * E * (math.pi * 4.5 * 3 ** 3 / 4) / 100.0 ** 2            # elliptical bar 6 mm thick (y) x 9 mm deep (z): the weaker axis governs
    P_l = FXF * RT / 40.0 + FYF * RT / 40.0
    add_fs("gen", "Upper link (6 x 9 mm elliptical bar, 100 mm)", f"2 g braking + 1.5 g cornering, {P_l:.0f} N compression", Pcr / P_l, P_l, Pcr, MIN["gen"], "print flat; buckling, not material, limits it")
    # carrier kingpin cantilever tube (tube axis along y = print stacking direction)
    Mb = NF * 17.0; Tw = FXF * RT
    sb = Mb / (math.pi * S.CAR_RC ** 3 / 4); tau = Tw * S.CAR_RC / (math.pi * S.CAR_RC ** 4 / 2)
    add("arm", f"Carrier kingpin cantilever tube (R {S.CAR_RC:g}, 17 mm)", "3 g bump (bending) + 2 g braking torque", KT * math.sqrt(sb ** 2 + 3 * tau ** 2), allow(1.0), MIN["arm"],
        "tube axis is the bed normal now (stress across layers, 15 MPa): print the carrier on its side", f"bending {sb:.1f} MPa, torsion {tau:.1f} MPa before KT")
    # kingpin
    Fh = math.hypot(FYF, FXF)
    add("gen", f"Kingpin {W.KP_D:g} mm steel (cantilever from the carrier tab)", f"1.5 g cornering + 2 g braking ({Fh:.0f} N horizontal at {RT + 12:.0f} mm)", Fh * (RT + 12.0) / (math.pi * W.KP_D ** 3 / 32), 400.0, MIN["gen"], "steel; no print direction")
    # knuckle V tubes (stud force from the steering servo stall; geometry hypot(7, 16, 21) = 27.2)
    Fs_ = SERVO_STEER / 12.0
    Lt = math.hypot(7.0, 16.0, 21.0); Fa = Fs_ / (2 * 7.0 / Lt)
    ca = 16.0 / Lt                                                       # direction cosine with the print stacking direction (y)
    add("gen", "Knuckle steering V (2 x R 3 tubes, 27 mm)", f"steering servo stall ({Fs_:.0f} N tie rod): {Fa:.0f} N axial per tube", KT * Fa / (math.pi * 9.0), allow(ca), MIN["gen"],
        "tubes run mostly along y = across the layers; print the knuckle on its side (hub axis horizontal)")
    Ps = math.pi ** 2 * 200000 * (math.pi * 3 ** 4 / 64) / 105 ** 2
    add_fs("gen", "Steering tie rod, 3 mm steel turnbuckle, 105 mm", "steering servo stall, Euler buckling", Ps / Fs_, Fs_, Ps, MIN["gen"], "steel")
    # ---------------- (b) rear arm + hoop
    rear, lever = rear_arm()
    for name, r in rear.items():
        if name.startswith("sustained"):
            add_fs("creep", "Rear swing arm + shock hoop (beam FE, caret top rail)", name + f" (creep x{CREEP})", CREEP * r["fs"], r["stress"], CREEP * r["allow"], MIN["creep"],
                   "plane normal (y) up, as now", f"worst member {r['member']}; shock force {r['Fs']:.0f} N")
        else:
            add_fs("arm", "Rear swing arm + shock hoop (beam FE, caret top rail)", name, r["fs"], r["stress"], r["allow"], MIN["arm"], "plane normal (y) up, as now: tube axes in the layer plane except the lattice and the hoop cross tube (axis along the bed normal: weak)",
                   f"worst member {r['member']}; tip deflection {r['defl']:.1f} mm; shock force {r['Fs']:.0f} N")
    # rear drop: stress scales with the wheel force; F = m g (1 + h / s)
    rb = rear["3 g bump, rear wheel"]
    s_eff = 25.0 / lever * 0 + 33.0                                      # 25 mm of shock stroke at the wheel is ~25 mm; + 8 mm tyre squash
    Fdrop = WR * (1 + 1000.0 / s_eff)
    fs_drop = rb["fs"] * ULT * NR / Fdrop
    INFO["drop"] = {"F": Fdrop, "g_equiv": Fdrop / WR, "h_safe_mm": s_eff * (rb["fs"] * ULT * NR / WR - 1.0), "s_eff": s_eff}
    add_fs("abuse", "Rear swing arm + shock hoop (beam FE, caret top rail)", f"1 m drop onto the rear wheel (rear share 0.79 kg, {Fdrop:.0f} N peak, vs ultimate)", fs_drop, rb["stress"] * Fdrop / NR, rb["allow"] * ULT, 1.0,
           "plane normal (y) up", f"survives a flat drop from about {INFO['drop']['h_safe_mm']/1000:.2f} m before the worst member passes ultimate")
    # rear shock upper lug plate (4.5 x 13 mm, 17 mm from the eye), flat on the bed
    Fs3 = NR * lever
    add("hinge", "Rear shock upper lug plate (4.5 x 13 mm)", f"3 g bump, shock force {Fs3:.0f} N", KT * Fs3 * 17.0 / (4.5 * 13.0 ** 2 / 6), SIP, MIN["hinge"], "plate flat on the bed: in-plane bending, good")
    Fsu = WR * lever + 10.0
    add("creep", "Rear shock upper lug plate (4.5 x 13 mm)", f"sustained spring preload + 1 g, {Fsu:.0f} N (creep x{CREEP})", KT * Fsu * 17.0 / (4.5 * 13.0 ** 2 / 6), CREEP * SIP, MIN["creep"], "as above")
    # ---------------- (a) cage frame
    cases, t, fixed = frame_cases(front, rear)
    for name, r in cases.items():
        grp = "hinge" if "hinge" in name else ("abuse" if "abuse" in name else "frame")
        mn = MIN["hinge"] if grp == "hinge" else (1.0 if grp == "abuse" else MIN["frame"])
        if name.startswith("sustained"):
            add_fs("creep", "Cage frame (beam FE, motor opening cut)", name + f" (creep x{CREEP})", CREEP * r["fs"], r["stress"], CREEP * r["allow"], MIN["creep"], "pieces print z up: vertical tubes load across layers", f"worst member {r['member']}")
        else:
            add_fs(grp, "Cage frame (beam FE, motor opening cut)", name, r["fs"], r["stress"], r["allow"], mn, "pieces print z up: vertical and steep tubes load across layers",
                   f"worst member {r['member']}; deflection {r['defl']:.2f} mm")
    foot = 0.0
    for r in cases.values():
        for k, v in r["react"].items():
            foot = max(foot, float(np.linalg.norm(v[:3])))
    INFO["foot_max"] = foot
    cap = TAUT * math.pi * 2.5 * 3.0
    add("frame", "Frame foot screws (M2.5 self-tapping, 3 mm of foot disc)", f"worst foot reaction {foot:.0f} N (resultant)", foot, cap, MIN["frame"], "screw axis vertical", "thread shear 6 MPa x d x 3 mm engagement")
    # hinge: pin shear, lug bearing, hood tab pad
    Fp = 0.25 * 10 * G / 2
    Hx0, Hx1 = F.HINGE[0]; Hz0, Hz1 = F.HINGE[1]
    t_l = F.HINGE_LUG[1] - F.HINGE_LUG[0]
    edge = (Hz1 - F.HINGE_PIN[1]) - F.HINGE_D / 2
    add("hinge", "Hinge lug plate (4.5 mm, 3.2 hole) - shear-out above the pin", f"skin weight/nose impact 10 g, {Fp:.0f} N per lug", KT * Fp / (2 * edge * t_l), 0.577 * SIP, MIN["hinge"], "lug stands up from the cross bar: shear is in the layer plane if the frame is printed z up")
    add("hinge", "Hinge lug plate (4.5 x 10.8 mm) - root bending", f"{Fp:.0f} N at {Hz1 - 22.0 - 2.0:.0f} mm", KT * Fp * (F.HINGE_PIN[1] - 22.0) / (t_l * (Hx1 - Hx0) ** 2 / 6), SIP, MIN["hinge"], "lug stands vertical: bending stress along z = across layers (use 15 MPa)")
    ROWS[-1]["allow"] = SZ; ROWS[-1]["fs"] = SZ / ROWS[-1]["stress"]
    add("hinge", "Hinge pin (3 mm steel) in double shear", f"{2*Fp:.0f} N", 2 * Fp / (2 * math.pi * 1.5 ** 2), 240.0, MIN["hinge"], "steel")
    magF = 20.0
    Zring = math.pi / 32 * (10.4 ** 4 - 6.3 ** 4) / 10.4
    add("hinge", "Hood tab magnet pad (10.4 mm, 6.3 mm pocket)", f"{magF:.0f} N peel at 5 mm lever, stress across layers", KT * (magF * 5.0 / Zring + magF / (math.pi / 4 * (10.4 ** 2 - 6.3 ** 2))), SZ, MIN["hinge"], "pad is vertical: across layers")
    # ---------------- (d) lean rocker + servo tower
    Rr = LN.R; bet = LN.BETA; w_root, tpl = 11.0, LN.PLATE
    for case, Ft in (("lean servo stall (17.7 kg.cm, 7.4 V)", SERVO_LEAN / Rr), ("3 g bump drives the rod (rod force)", INFO["lean_rod_bump"])):
        Mrt = Ft * math.cos(bet) * (Rr - 6.5); sax = Ft * math.sin(bet) / (w_root * tpl)
        add("gen" if "stall" in case else "abuse", f"Lean rocker V arm ({tpl:g} mm plate, root of the arm)", f"{case}: {Ft:.0f} N at the tip", KT * (Mrt / (tpl * w_root ** 2 / 6) + sax), SIP,
            MIN["gen"] if "stall" in case else 1.0, "plate flat on the bed (as now): loads in the layer plane, best direction")
    Ft = SERVO_LEAN / Rr
    add("gen", "Lean rocker horn screws (4 x M2 at r 5.5)", f"servo stall, bearing in the {tpl:g} mm plate", SERVO_LEAN / (4 * 5.5) / (2.0 * tpl), SIP, MIN["gen"], "in-plane bearing")
    Fe = SERVO_LEAN / 28.0
    add("gen", f"Servo tower plate ({LN.TWR_X[1] - LN.TWR_X[0]:g} mm), ear screw bearing (2 x M2, 28 mm pitch)", f"lean servo stall, {Fe:.0f} N per screw along z", Fe / (1.9 * (LN.TWR_X[1] - LN.TWR_X[0])), SZ, MIN["gen"], "plate stands vertical: z loads are ACROSS the layers; print the tower on its back (x axis up)")
    Rb = INFO["lean_rod_bump"]
    pull = TAUT * math.pi * 2.0 * 4.5
    add("gen", "Servo tower feet (4 x M2 into the base plate, 4.5 mm engagement)", f"3 g bump rod reaction {Rb:.0f} N pulling up", Rb / 4.0, pull, MIN["gen"], "screws vertical", "thread shear 6 MPa x d x engagement")
    # ---------------- (f) base plate
    Rp = abs(front["3 g bump, one front wheel"][1][2])
    Zd = (108.0 - 4 * 3.4) * 6.0 ** 2 / 6.0
    add("gen", "Base plate deck 6 mm (slotted, 108 mm wide)", f"3 g bump: tower pulls up {Rb:.0f} N, diff case pushes down {Rp:.0f} N, 15 mm apart (40 mm effective width)", 2.0 * Rp * 15.0 / (40.0 * 36.0 / 6.0), SIP,
        MIN["gen"], "deck prints flat: layers carry the bending (best), screw pull-out is across layers")
    add("gen", "Base plate deck 6 mm - battery + motor + servo inertia", "3 g bump, 125 g pack + 201 g motor + 55 g servo over a 100 mm span (simply supported strip, 40 mm wide)", 2.0 * (0.381 * 3 * G) * 100.0 / 8.0 / (40.0 * 36.0 / 6.0), SIP, MIN["gen"], "flat")
    # ---------------- (e) wing
    wres, foot_t, secs = wing_hanger()
    for name, (fs, z, sig, A) in wres.items():
        abuse = name.startswith("abuse")
        add_fs("abuse" if abuse else "wing", "Wing hanger (one piece, 10 mm wide web)", name, fs, sig, SIP, 1.0 if abuse else MIN["wing"], "printed on its side (current): web plane = layer plane, best direction",
               f"worst section at z {z:.0f}, area {A:.0f} mm2 (stress incl. x2 fillet factor)")
    Tcap = min(TAUT * math.pi * 2.5 * TL.PILOT_L, SZ * math.pi / 4 * (6.0 ** 2 - 3.2 ** 2))
    for name, T in foot_t.items():
        abuse = name.startswith("abuse")
        add_fs("abuse" if abuse else "wing", "Wing foot screw + hood boss (M2.5, one per hanger)", name, Tcap / max(T, 1e-6), T, Tcap, 1.0 if abuse else MIN["wing"], "boss is across layers: head + M2.5 flat washer (OD 6) bearing 15 MPa x 20 mm2", f"screw tension {T:.0f} N vs {Tcap:.0f} N")
    # blade at the groove edge and prong screws, 10 N tip press
    Mtip = 10.0 * (TL.SPAN - TL.LEG_Y - 5.0)
    add("abuse", "Wing blade (6 mm sheet) at the hanger groove edge", "10 N press on the blade tip (core 2 mm inside the groove: 72 x 2 mm)", KT * Mtip / (TL.CHORD * 2.0 ** 2 / 6) / 3.0, SIP, 1.0, "blade printed flat: layers carry the bending", "/3: prongs fill the groove and share the section")
    Tscrew = Mtip / 10.0 / 3.0
    add("abuse", "Wing prong screws (3 x M2.5 through the lower prong)", "10 N press on the blade tip, overturning about the groove edge (10 mm arm)", Tscrew, TAUT * math.pi * 2.5 * 4.0, 1.0, "screw axis across the blade layers", "4 mm engagement into the blade core")
    return ROWS


def row_key(r):
    """Regression key of a row: part | case with load magnitudes ("62 N") removed, so a changed load does not rename the row."""
    import re
    return re.sub(r"\d+(?:\.\d+)? N\b", "N", f"{r['part']} | {r['case']}")


def run():
    if not ROWS:
        checks()
    return ROWS


if __name__ == "__main__":
    for r in run():
        flag = "ok " if r["fs"] >= r["min"] else "LOW"
        print(f"{flag} {r['fs']:7.2f} (min {r['min']:.1f})  {r['part'][:48]:48s} | {r['case'][:70]}")
    print({k: (v if not isinstance(v, (np.ndarray, dict)) else str(v)[:80]) for k, v in INFO.items()})
