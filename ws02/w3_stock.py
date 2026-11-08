"""WS-03 drivetrain: stock-part dimensions, gear geometry, cross-over layout and the ratio chain.  One source of numbers for the
printed housings (parts/w3_drive.py), the bought mocks (w3_mock.py), the layout blocks (layout3wd.py) and the chassis bolt slots.

Every value tagged A is an ASSUMPTION (typical value, not found in any manufacturer or retailer source); F = found.  See WS03_DRIVETRAIN.md.
Frame: x forward, y left, z up, z = 0 at the front axle height.  Driveline shaft line y = SY.
"""
import math

from w3_stretch import pv

# ---- gears (32 DP = module 0.794, 20 deg pressure angle) ----
DP = 32.0
MOD = 25.4 / DP                                  # A: 32 DP, only confirmed for the 40T spur (AXI232034)
PA = math.radians(20.0)
SY = 21.0                                        # shaft line |y|


def pd(n):                                       # pitch diameter
    return n * MOD


def od(n):
    return pd(n) + 2.0 * MOD


# AXI232003 6-bolt heavy-duty gear set: 30T ring / 8T pinion (F tooth counts), 90 deg straight bevel (A)
RING_T, PIN_T = 30, 8
BEV_R, BEV_r = pd(RING_T) / 2, pd(PIN_T) / 2     # pitch radii 11.906 / 3.175
BEV_DELTA = math.atan2(PIN_T, RING_T)            # pinion pitch cone half angle 14.93 deg
BEV_ADD = BEV_R                                  # apex to pinion pitch circle along the pinion axis (90 deg bevel) = ring pitch radius
BEV_DEPTH = BEV_r                                # apex to ring pitch circle plane along the ring axis = pinion pitch radius
RING_OD, RING_TH = 25.5, 5.5                     # A  ring outside diameter, thickness (tooth face to back)
RING_BORE, RING_BC, RING_BOLT = 11.0, 15.0, 2.0  # A  centre bore, bolt circle (6 bolts), bolt size M2
RING_TIP = 1.0                                   # A  tooth tip above the pitch plane
PIN_FACE, PIN_BACK, PIN_HUB, PIN_HEAD_D, PIN_BORE = 4.5, 1.5, 4.0, 9.0, 5.0       # A  pinion: face width, back cone, hub length, head OD, bore
PIN_LEN = PIN_FACE + PIN_BACK + PIN_HUB          # head length 10 (the 5 mm shaft goes in 7 mm)
BEV_SHIM = 0.8                                   # axial shim behind each bevel pinion: circumferential backlash = 2 shim sin(delta) tan(PA)
BEV_BACKLASH = 2.0 * BEV_SHIM * math.sin(BEV_DELTA) * math.tan(PA)       # 0.15 mm
CD_ADD = 0.20                                    # extra centre distance on every spur mesh: backlash = 2 CD_ADD tan(PA) = 0.146 mm
SPUR_BACKLASH = 2.0 * CD_ADD * math.tan(PA)

# spur gears, bought: AXI232033 27T (A pitch and bore; the 20T and 34T are not used), AXI232034 40T (F 32 pitch, 40T), generic 32 DP 13T pinion (A)
SPUR_W = 6.0                                     # A  face width
SPUR_BORE = {13: 5.0, 27: 5.0, 40: 10.0}         # A  bores (the 40T sits on the printed hub spigot)
PINION_T, IDLER_T, CRING_T = 13, 27, 40          # motor pinion, two idlers, centre-diff ring (spur)

# ---- bearings, shafts ----
BRG_D, BRG_OD, BRG_W = 5.0, 11.0, 4.0            # MR115ZZ 5 x 11 x 4
SEAT = 11.15                                     # printed seat (press fit, 0.15 clearance)
BORE = 5.4                                       # clearance for a 5 mm shaft
BOLT = 2.7                                       # M2.5 clear
SHAFT_D = 5.0
SHAFT_FRONT = SHAFT_REAR = 102.0                 # stock 5 x 102 mm (Arrma ARA330574-class shock shaft); also 5 x 100 fits with 2 mm less in the pinion bore

# ---- differential carriers (A) ----
CARR_D = 30.0                                    # carrier OD (ring flange 25.5 sits on it)
CARR_L = 32.0                                    # centre diff carrier length between the bearing shoulders
HUB_D = 11.0                                     # output hub OD where it passes the ring
HD = 10.0                                        # shaft penetration into the carrier hub

# ---- front diff (ring axis along y at XD) ----
XD = -100.0
FY_APEX = SY
FRING_Y = (FY_APEX - BEV_DEPTH - RING_TH + RING_TIP, FY_APEX - BEV_DEPTH + RING_TIP)        # ring back / tooth face y
FCARR_Y = (FRING_Y[0] - 30.0, FRING_Y[0])                                                    # carrier body y
F_PIN_LARGE = XD - BEV_ADD - BEV_SHIM            # pinion pitch circle plane x (large end)
F_PIN_X = (F_PIN_LARGE - PIN_BACK - PIN_HUB, F_PIN_LARGE + PIN_FACE)     # pinion head x range (hub aft, teeth forward)
F_BRG = [(F_PIN_X[0] - 1.0 - BRG_W, F_PIN_X[0] - 1.0),                  # pinion shaft bearings: behind the head, next, then the case aft wall
         (F_PIN_X[0] - 12.0 - BRG_W, F_PIN_X[0] - 12.0), (-158.1, -154.0)]

# ---- centre diff (carrier along x at SY) ----
SHAFT_F_TIP = F_PIN_X[1] - 2.5                   # front shaft forward end, inside the pinion bore
SHAFT_F_AFT = SHAFT_F_TIP - SHAFT_FRONT          # -207 .. aft end inside the carrier hub
C_FACE_F = SHAFT_F_AFT + HD                      # carrier forward flange face x
C_FACE_A = C_FACE_F - CARR_L                     # carrier aft face x
HUB_FL = 4.0                                      # printed ring hub flange, bolted to the carrier's forward face
C_RING = (C_FACE_F + HUB_FL, C_FACE_F + HUB_FL + SPUR_W)   # 40T spur ring plane, on the hub spigot (plane B)
C_BRG_F = (C_RING[1] + 0.5, C_RING[1] + 0.5 + BRG_W)
C_BRG_A = (C_FACE_A - 0.5 - BRG_W, C_FACE_A - 0.5)
GEAR_X = C_RING                                   # all cross-over gears live in this x slab
X_BRG_A = (GEAR_X[0] - 0.5 - BRG_W, GEAR_X[0] - 0.5)       # aft bearings of the cross-over shafts
X_BRG_F = (GEAR_X[1] + 0.5, GEAR_X[1] + 0.5 + BRG_W)       # forward bearings

# ---- motor and cross-over chain (all axes along x) ----
MOTOR_YZ = (-21.0, 41.0)                          # motor axis (y, z)
MOTOR_X = -122.0                                  # can centre x (layout3wd.MOTOR_C)
CARR_YZ = (SY, 0.0)


def xover_layout():
    """Positions (y, z) of motor pinion P1, idlers Pa, Pb and ring P0.  The chain bends upward and inboard."""
    P1, P0 = MOTOR_YZ, CARR_YZ
    d1 = (pd(PINION_T) + pd(IDLER_T)) / 2 + CD_ADD
    d2 = pd(IDLER_T) + CD_ADD
    d3 = (pd(IDLER_T) + pd(CRING_T)) / 2 + CD_ADD
    best = None
    for k in range(0, 3600):
        th = math.radians(k * 0.1)
        pa = (P1[0] + d1 * math.cos(th), P1[1] + d1 * math.sin(th))
        # Pb: intersection of circle (P0, d3) and (pa, d2)
        dx, dy = pa[0] - P0[0], pa[1] - P0[1]
        d = math.hypot(dx, dy)
        if d > d2 + d3 or d < abs(d2 - d3):
            continue
        a = (d3 * d3 - d2 * d2 + d * d) / (2 * d)
        h2 = d3 * d3 - a * a
        if h2 < 0:
            continue
        h = math.sqrt(h2)
        for sg in (1, -1):
            pb = (P0[0] + (a * dx - sg * h * dy) / d, P0[1] + (a * dy + sg * h * dx) / d)
            score = min(pa[1], pb[1]) + 0.3 * (pa[0] + pb[0])     # high and toward +y
            if best is None or score > best[0]:
                best = (score, pa, pb)
    _, pa, pb = best
    return dict(P1=P1, Pa=pa, Pb=pb, P0=P0)


XO = xover_layout()
XO_R = {"P1": od(PINION_T) / 2, "Pa": od(IDLER_T) / 2, "Pb": od(IDLER_T) / 2, "P0": od(CRING_T) / 2}
RATIO_XO = CRING_T / PINION_T                      # idlers cancel

# ---- rear bevel (ring axis along y at XR) ----
XR = pv(-272.0)
RY_APEX = SY
RRING_Y = (RY_APEX + BEV_DEPTH - RING_TIP, RY_APEX + BEV_DEPTH - RING_TIP + RING_TH)       # tooth face / back y (body toward +y)
R_PIN_LARGE = XR + BEV_ADD + BEV_SHIM
R_PIN_X = (R_PIN_LARGE - PIN_FACE, R_PIN_LARGE + PIN_BACK + PIN_HUB)       # head x range (teeth aft, hub forward)
R_BRG = [(R_PIN_X[1] + 1.0, R_PIN_X[1] + 1.0 + BRG_W), (R_PIN_X[1] + 12.0, R_PIN_X[1] + 12.0 + BRG_W)]
SHAFT_R_FWD = C_FACE_A + HD                      # rear shaft forward end, inside the carrier hub
SHAFT_R_AFT = SHAFT_R_FWD - SHAFT_REAR
REAR_OUT_Y = (8.0, 76.0)                         # rear output shaft (5 x 68): inboard bearing at the ring, through the arm, 76 out
PILLOW_X = 0.5 * (C_BRG_A[0] + R_BRG[1][1])      # shaft support midway between the centre diff and the rear bevel case

# ---- front-to-rear ratio chain ----
FRONT_BELT = (20, 16)                              # pivot pulley drives the tip pulley
REAR_BELT = (22, 20)                               # pivot pulley drives the axle pulley (was 20 / 22)
KV, VOLT, LOAD = 1800.0, 11.1, 0.85
TYRE_D = 112.0


def ratios():
    front = (RING_T / PIN_T) * FRONT_BELT[1] / FRONT_BELT[0]           # centre-diff output shaft to wheel (reduction)
    rear = (RING_T / PIN_T) * REAR_BELT[1] / REAR_BELT[0]
    total = RATIO_XO * front
    rpm_m = KV * VOLT
    rpm_w = rpm_m / total
    v = rpm_w * math.pi * TYRE_D / 1000.0 / 60.0                       # m/s unloaded
    return dict(xover=RATIO_XO, front_path=front, rear_path=rear, total=total, motor_rpm=rpm_m, wheel_rpm=rpm_w,
                kmh_unloaded=v * 3.6, kmh_loaded=v * 3.6 * LOAD, mismatch=rear / front,
                torque_front=front / (front + rear), torque_rear=rear / (front + rear))


# ---- housing bolt positions on the base plate (x, y); slots 10 long give +-5 mm of mesh adjustment ----
CASE_C = (C_BRG_A[0] - 5.0, C_BRG_F[1] + 5.0)               # centre case x extent (aft wall .. forward tower plate)
BOLTS = [(-88.0, -22.0), (-88.0, 30.0), (-155.0, -22.0), (-155.0, 31.0),
         (CASE_C[0] + 4.0, -2.5), (CASE_C[0] + 4.0, 44.5), (CASE_C[1] - 4.0, -2.5), (CASE_C[1] - 4.0, 44.5),
         (PILLOW_X, 8.5), (PILLOW_X, 33.5),
         (XR - 5.0 - 17.0, 8.5), (XR - 5.0 - 17.0, 33.5), (XR + 31.0, 8.5), (XR + 31.0, 33.5)]


if __name__ == "__main__":
    import json
    for k, v in sorted(globals().items()):
        if k.isupper() and not k.startswith("_") and not callable(v):
            print(k, "=", v if not isinstance(v, float) else round(v, 3))
    print(json.dumps({k: round(v, 3) for k, v in ratios().items()}))
