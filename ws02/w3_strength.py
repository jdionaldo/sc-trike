"""WS-03 hand-calculation strength checks for the critical parts (worst case: 3 g vertical landing, cornering at mu 1.0).
Assumptions are printed in WS03_STRENGTH.md; PETG 25 MPa across layers (design value), steel pins 400 MPa yield, M2.5 screws in PETG 150 N pull-out."""
import math
from parts import w3_front as W

G = 9.81
M = 1.608                           # kg total (w3_mass.py)
FRONT = 0.606
N_front_wheel = M * G * FRONT / 2 * 3.0     # 3 g landing, one wheel carries half the front load
Fy = 1.0 * N_front_wheel * 0.6              # cornering force at the contact patch, 60% of the dynamic load
LEVER = 41.5 + 12.0                         # contact patch to the kingpin tab (tire radius plus pin offset), mm


def pin_check(d):
    Z = math.pi * d ** 3 / 32
    M_ = Fy * LEVER
    return 400.0 * Z / M_


rows = []
for d in (3.0, 4.0):
    rows.append((f"Kingpin {d:.0f} mm steel, cantilever from the carrier tab, cornering", pin_check(d)))
# lower arm: housing section 9.5 wide x 19 tall with a 4.8 x 15 cavity, tip load = wheel load x arm length
I = (9.5 * 19 ** 3 - 4.8 * 15 ** 3) / 12
Zs = I / 9.5
M_arm = N_front_wheel * 100.0
rows.append(("Lower arm plate bending at the pivot, 3 g landing", 25.0 / (M_arm / Zs)))
# servo wall: two M2.5 screws into the diff-case ears; reaction of the lean servo (12 kg.cm) shared
F_srv = 1177.0 / 49.0
rows.append(("Servo wall screws (pull-out) vs servo reaction, two screws", 2 * 150.0 / (F_srv * 2)))
# tie rod buckling (3 mm thick, 10 wide, 105 long, PETG E 1500 MPa) under the steering load (servo 12 kg.cm at a 12 mm horn)
Fs = 1177.0 / 12.0
Ib = 10 * 3 ** 3 / 12
Pcr = math.pi ** 2 * 1500 * Ib / 105 ** 2
rows.append(("Steer tie rod, printed 3 x 10 PETG bar, buckling at full servo torque", Pcr / Fs))
Ps = math.pi ** 2 * 200000 * (math.pi * 3 ** 4 / 64) / 105 ** 2
rows.append(("Steer tie rod, 3 mm steel turnbuckle (used in the build), buckling", Ps / Fs))
# rear scoop: 78 mm cantilever hollow wedge, 2.4 mm walls, 3 g self weight plus a 20 N tip push
M_sc = 20.0 * 78.0 + 0.05 * G * 3 * 39.0
Zsc = 2 * (80 * 2.4) * 25
rows.append(("Rear scoop cantilever, 20 N tip push", 25.0 / (M_sc / Zsc)))
# carrier tab: 12 x 10 PETG tab holding the kingpin bending load
Zt = 12 * 10 ** 2 / 6
rows.append(("Carrier kingpin tab bending (PETG)", 25.0 / (Fy * 12.0 / Zt)))
lines = ["# WS-03 strength checks (hand calculations)", "",
         f"Loads: 3 g landing, front wheel load {N_front_wheel:.1f} N, cornering force {Fy:.1f} N. Factor of safety below 2 is flagged.", "",
         "| check | factor of safety | verdict |", "|---|---|---|"]
for n, sf in rows:
    lines.append(f"| {n} | {sf:.1f} | {'ok' if sf >= 2 else 'LOW'} |")
open("WS03_STRENGTH.md", "w").write("\n".join(lines) + "\n")
for n, sf in rows:
    print(f"{sf:5.1f}  {n}")
