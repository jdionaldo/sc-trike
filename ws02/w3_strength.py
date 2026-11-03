"""WS-03 strength checks: worst case 3 g vertical landing plus cornering at mu 1.0.  Beam FE (w3_beamfe.py) on the real tube graphs of the front arm,
rear arm and frame; hand calculations for the link, pins, carrier, knuckle.  PETG 25 MPa design stress (across layers), steel pins 400 MPa yield."""
import math
import numpy as np
from parts import w3_front as W, w3_style as S, w3_drive as D, w3_frame as F
from w3_beamfe import Truss

G = 9.81
M = 1.608                           # kg total (w3_mass.py)
FRONT = 0.606
N_f = M * G * FRONT / 2 * 3.0       # 3 g landing, one front wheel carries half the front load (N)
Fy = 1.0 * N_f * 0.6                # cornering force at the contact patch
N_r = M * G * (1 - FRONT) * 3.0     # rear wheel
Fy_r = 1.0 * N_r * 0.6
SIG = 25.0
rows = []


def sf(sig):
    return SIG / sig


# ---- front arm: pivot nodes fixed, wheel loads at the tip nodes ----
def front_arm():
    t = Truss()
    ya = W.ARM_Y[0]
    yi, yo = ya + 2.5, ya + S.YO
    for k, (x, z) in S.ARM_NODES.items():
        t.node(k + "i", (x, yi, z))
        xo, zo = S.ARM_OUTER[k]
        t.node(k + "o", (xo, yo, zo))
    for a, b in S.ARM_RAILS + S.ARM_WEB:
        t.edge(a + "i", b + "i", S.RT)
    for a, b in S.ARM_RAILS:
        t.edge(a + "o", b + "o", S.RO)
    for a, b in S.ARM_WEB:
        t.edge(a + "o", b + "o", S.RW)
    for rails, r in (([("U0", "U1"), ("U1", "U2"), ("U2", "U3")], S.LAT_TOP), ([("L0", "L1"), ("L1", "L2")], S.LAT_BOT)):
        for a, b in rails:
            t.edge(a + "i", b + "o", r); t.edge(b + "i", a + "o", r)
    for k in ("U0", "L0", "U3", "L2"):
        t.edge(k + "i", k + "o", S.TIE_R[k])
    for p_ in "io":                                         # hubs are stiff: tie the end nodes of each plane with a fat bar
        t.edge("U0" + p_, "L0" + p_, 8.0); t.edge("U3" + p_, "L2" + p_, 8.0)
    dy = S.YO - 2.5
    couple = Fy * 41.5 / dy                                  # torque from the cornering force acting 41.5 mm below the axle
    loads = []
    for p_, sgn in (("i", -1.0), ("o", 1.0)):
        for k in ("U3", "L2"):
            loads.append((k + p_, np.array([0.0, Fy / 4, -N_f / 4 + sgn * couple / 2])))
    return t.solve(loads, ["U0i", "L0i", "U0o", "L0o"])


s_, n_, d_ = front_arm()
rows.append((f"Front arm (truss FE), 3 g landing + cornering; max {s_:.1f} MPa in {n_}, tip deflection {d_:.1f} mm", sf(s_)))


# ---- rear arm: print frame (u along the arm, v vertical-ish, w = lateral) ----
def rear_arm():
    L = math.hypot(D.XR - D.RAXLE[0], D.RAXLE[1])
    us = [0.0, L / 4, L / 2, 3 * L / 4, L]
    V, VL = 9.5, 12.5
    t = Truss()
    planes = {"i": (S.REAR_W[0], 2.4, 2.4), "o": (S.REAR_W[1], 4.5, 3.5)}
    for p_, (w, r, rw) in planes.items():
        for sg in (1, -1):
            for i, u in enumerate(us):
                t.node(f"{i}{'p' if sg > 0 else 'n'}{p_}", (u, sg * V, w))
            for i in range(4):
                t.edge(f"{i}{'p' if sg > 0 else 'n'}{p_}", f"{i+1}{'p' if sg > 0 else 'n'}{p_}", r)
        for i in range(4):
            a, b = ("p", "n") if i % 2 == 0 else ("n", "p")
            t.edge(f"{i}{a}{p_}", f"{i+1}{b}{p_}", rw)
    for i in range(4):
        for sg, r in (("p", 3.0), ("n", 3.0)):
            t.edge(f"{i}{sg}i", f"{i+1}{sg}o", r); t.edge(f"{i+1}{sg}i", f"{i}{sg}o", r)
    for i in (0, 4):
        for sg in "pn":
            t.edge(f"{i}{sg}i", f"{i}{sg}o", 3.2)
        for p_ in "io":
            t.edge(f"{i}p{p_}", f"{i}n{p_}", 8.0)
    for i in (0, 4):
        for sg, sgv in (("p", 1), ("n", -1)):
            for p_, (w, r, rw) in planes.items():
                t.node(f"{i}{sg}x{p_}", (us[i], sgv * 16.0, w))
                t.edge(f"{i}{sg}{p_}", f"{i}{sg}x{p_}", 4.0)
            t.edge(f"{i}{sg}xi", f"{i}{sg}xo", 4.0)
    Mu = N_r * (46.0 + 8.5) + Fy_r * 56.0
    dw = S.REAR_W[1] - S.REAR_W[0]
    loads = []
    for p_, sgn in (("i", -1.0), ("o", 1.0)):
        for sg in "pn":
            loads.append((f"4{sg}{p_}", np.array([0.0, -N_r / 4 + sgn * Mu / dw / 2, Fy_r / 4])))
    return t.solve(loads, ["0pi", "0ni", "0po", "0no"])


s_, n_, d_ = rear_arm()
rows.append((f"Rear arm (truss FE), 3 g landing + cornering, wheel 46 mm off the arm; max {s_:.1f} MPa in {n_}, tip deflection {d_:.1f} mm", sf(s_)))


# ---- tube frame: 3 g on both pivot pads, feet fixed ----
def frame_fe():
    N = F.nodes()
    t = Truss()
    mir = lambda p: (p[0], -p[1], p[2])
    for k, p in N.items():
        t.node(k + "+", p); t.node(k + "-", mir(p))
    for a, b, r, ta, tb in F.EDGES:
        t.edge(a + "+", b + "+", r); t.edge(a + "-", b + "-", r)
    loads = [("PL+", np.array([0, 0, -N_f * 2.0])), ("PL-", np.array([0, 0, -N_f * 2.0]))]
    fixed = [k + sg for k in F.FEET for sg in "+-"]
    return t.solve(loads, fixed)


s_, n_, d_ = frame_fe()
rows.append((f"Tube frame (FE), 6 g equivalent on the pivot pads, feet fixed; max {s_:.1f} MPa in {n_}, deflection {d_:.2f} mm", sf(s_)))

# ---- hand calculations ----
LEVER = 41.5 + 12.0
for d in (4.0,):
    Z = math.pi * d ** 3 / 32
    rows.append((f"Kingpin {d:.0f} mm steel, cantilever from the carrier tab, cornering", 400.0 * Z / (Fy * LEVER)))
Fs = 1177.0 / 12.0                                           # steer servo stall (12 kg.cm) at a 12 mm horn
Ps = math.pi ** 2 * 200000 * (math.pi * 3 ** 4 / 64) / 105 ** 2
rows.append(("Steer tie rod, 3 mm steel turnbuckle, buckling at servo stall", Ps / Fs))
# upper link: 6 mm round bar, 100 mm pin to pin, carries the carrier tilt moment (cornering force x 41.5 mm over 40 mm) plus a share of the landing load
P_link = Fy * 41.5 / 40.0 + 0.5 * N_f
Pcr = math.pi ** 2 * 1500 * (math.pi * 3 ** 4 / 4) / 100 ** 2
rows.append((f"Upper link (6 mm bar), buckling under {P_link:.0f} N", Pcr / P_link))
# carrier: kingpin cantilever tube r 4.5, 17 mm long, carries the vertical wheel load (the angled brace shares it; ignored)
sig = N_f * 17.0 / (math.pi * S.CAR_RC ** 3 / 4)
rows.append(("Carrier kingpin cantilever tube (brace ignored), 3 g landing", sf(sig)))
# knuckle steering V: two r 3 tubes, ~28 mm long, pulled by the tie rod at servo stall along x, 20 deg off the y axis
sinA = 7.0 / math.hypot(7.0, 16.0)
sig = (Fs / (2 * sinA)) / (math.pi * 3 ** 2)
rows.append(("Knuckle steering V tubes, axial at servo stall", sf(sig)))

# ---- rear coilover mounts: 3 g wheel load times the worst (smallest) wheel-travel / shock-stroke ratio over the travel ----
from parts import w3_shock as SK
_dn, _up = SK.travel_angles()
lever = min(SK.mount_lever(a_) for a_ in np.linspace(_dn, _up, 15))
Fshock = N_r * lever
sig = Fshock * (0.5 * sum(SK.PLATE_Y) + 4.0 - 38.0) / (math.pi * SK.TAB_TUBE_R ** 3 / 4)          # tab tube, cantilever from node R2 (y 38) to the eye plane
rows.append((f"Rear shock tab tube (13 mm, 46 mm cantilever from the cage), shock force {Fshock:.0f} N at 3 g landing", sf(sig)))
sig = Fshock * 12.0 / (9.0 * 11.0 ** 2 / 6)                                                        # arm lug pillar, 9 x 11 mm section, 12 mm lever
rows.append(("Rear shock lug on the swing arm (pillar bending), 3 g landing", sf(sig)))
lines = ["# WS-03 strength checks", "",
         f"Loads: 3 g landing, front wheel {N_f:.1f} N, rear wheel {N_r:.1f} N, cornering force 0.6 x load. Beam FE on the real tube graphs (PETG E 1500 MPa), "
         f"design stress 25 MPa. Factor of safety below 2 is flagged.", "",
         "| check | factor of safety | verdict |", "|---|---|---|"]
for n, v in rows:
    lines.append(f"| {n} | {v:.1f} | {'ok' if v >= 2 else 'LOW'} |")
open("WS03_STRENGTH.md", "w").write("\n".join(lines) + "\n")
for n, v in rows:
    print(f"{v:6.1f}  {n}")
