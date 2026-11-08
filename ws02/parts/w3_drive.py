"""WS-03 drivetrain printed parts: split gear housings around the stock gears (see w3_stock.py), shaft support, ring hubs, slotted motor plate,
battery and ESC trays, rear arm and cover.

Assembly frame: x forward, y left, z up, z = 0 at the front axle height, shafts at z = 0, shaft line y = SY.
Housings are split on the z = 0 plane (every shaft lies in it).  The lower half prints as built (z - z0); the upper half prints rotated 180 deg about x
(print = (x, -y, ZT - z)), split faces on the bed.  Bodies are built in the assembly frame with manifold3d and cut in two.
"""
import math

import numpy as np
from manifold3d import Manifold as Mf

import mono_build as MB
import w3_stock as K
from cad import Part
from w3_stretch import back, pv, STRETCH, RAXLE_Z
from layout3wd import MOTOR_C

SY = K.SY                 # shaft line |y| (pinion shaft, centre diff axis, rear shaft)
XD = K.XD                 # front diff axis x (arm pivots)
XR = K.XR                 # rear bevel apex x (rear arm pivot), 30 mm forward of the stretched position
RAXLE = (back(-360.0), RAXLE_Z)   # rear axle (x, z): wheelbase 450, chassis raked 4 deg nose-down
BORE = K.BORE             # 5 mm shaft
SEAT = K.SEAT             # 5 x 11 x 4 bearing
SEAT_D = K.BRG_W
BOLT = K.BOLT             # M2.5 clear
FDC_Z, CDC_Z, RBC_Z, PIL_Z = (-22.0, 22.0), (-22.0, 52.0), (-21.0, 21.0), (-21.0, 21.0)


def bx(x0, x1, y0, y1, z0, z1):
    return Mf.cube((x1 - x0, y1 - y0, z1 - z0), center=False).translate((x0, y0, z0))


def cx(x0, x1, y, z, d, seg=64):
    return Mf.cylinder(x1 - x0, d / 2, d / 2, seg).rotate((0.0, 90.0, 0.0)).translate((x0, y, z))


def cy(x, y0, y1, z, d, seg=64):
    return Mf.cylinder(y1 - y0, d / 2, d / 2, seg).rotate((-90.0, 0.0, 0.0)).translate((x, y0, z))


def cz(x, y, z0, z1, d, seg=32):
    return Mf.cylinder(z1 - z0, d / 2, d / 2, seg).translate((x, y, z0))


def hole_z(x, y, z0, z1, d=BOLT):
    return cz(x, y, z0 - 1.0, z1 + 1.0, d)


def split(name, body, zs, supports=True):
    """Cut a body at z = 0 into the two print halves (lower as built, upper rotated 180 deg about x), as MeshParts."""
    from parts.w3_style import MeshPart, _clean
    z0, z1 = zs
    lo = (body ^ bx(-1e3, 1e3, -1e3, 1e3, z0 - 1.0, 0.0)).translate((0.0, 0.0, -z0))
    up = (body ^ bx(-1e3, 1e3, -1e3, 1e3, 0.0, z1 + 1.0)).rotate((180.0, 0.0, 0.0)).translate((0.0, 0.0, z1))
    out = []
    for suffix, m in (("lower", lo), ("upper", up)):
        out.append(MeshPart(f"{name}_{suffix}", (lambda m=m: _clean(MB.to_trimesh(m))), walls=True, supports=supports))
    return out


def seat_x(x0, x1, y, z, through=None):
    """Bearing pocket (x0..x1 holds the bearing) plus a 5.4 bore across `through` (x range) when given."""
    c = cx(x0 - 0.2, x1 + 0.2, y, z, SEAT)
    if through:
        c = c + cx(through[0], through[1], y, z, BORE)
    return c


def front_diff_case():
    box = bx(-158.0, -80.0, -26.0, 34.0, FDC_Z[0], FDC_Z[1])
    for xa, xb in ((-156.6, -140.2), (-90.0, -82.0)):                   # ears that hold the servo wall: blocks beside the servos
        box = box + bx(xa, xb, 30.0, 54.5, -22.0, 0.0)
    cuts = [cy(XD, K.FCARR_Y[0] - 0.5, K.FRING_Y[1] + 0.5, 0.0, K.CARR_D + 3.6),                    # carrier and ring cavity
            cy(XD, K.FRING_Y[1], 30.1, 0.0, K.HUB_D + 3.0),                                         # hub clearance past the ring
            cy(XD, -22.1, K.FCARR_Y[0], 0.0, K.HUB_D + 1.0),
            cx(K.F_PIN_X[0] - 0.6, XD + 1.0, SY, 0.0, 15.0)]                                        # pinion tunnel (head + clearance)
    for yy in ((-26.1, -22.0), (30.0, 34.1)):                                                       # output bearing seats
        cuts.append(cy(XD, yy[0], yy[1], 0.0, SEAT))
    cuts.append(cy(XD, -26.1, 34.1, 0.0, BORE))
    for b in K.F_BRG:                                                                               # pinion shaft: bearing behind the head, a second 11 mm back, a third in the aft wall
        cuts.append(seat_x(b[0], b[1], SY, 0.0))
    cuts.append(cx(-158.1, K.F_PIN_X[0] - 0.6, SY, 0.0, BORE))
    for x, y in ((-88.0, -22.0), (-88.0, 30.0), (-155.0, -22.0), (-155.0, 31.0)):
        cuts.append(hole_z(x, y, *FDC_Z))
    for xa, xb in ((-156.6, -140.2), (-90.0, -82.0)):
        cuts.append(cy(0.5 * (xa + xb), 42.0, 54.6, -10.0, 2.2))                                    # M2.5 pilot into the wall
    for c in cuts:
        box = box - c
    return split("w3_fdc", box, FDC_Z, supports=False)


def _plate(x0, x1, pts, r=9.5):
    """Tower plate: hull of boss cylinders at the (y, z) points with a base strip at z = 0."""
    parts = [cx(x0, x1, y, z, 2 * r) for y, z in pts]
    parts.append(bx(x0, x1, -30.0, 47.0, 0.0, 2.0))
    return Mf.batch_hull(parts)


def center_diff_case():
    x0, x1 = K.CASE_C
    xo = K.XO
    gx0, gx1 = K.GEAR_X[0], K.C_BRG_F[0]                      # gear slab between the two plates
    pa0 = K.X_BRG_A[0] - 5.0                                   # aft plate slab
    pf1 = K.C_BRG_F[1] + 5.0                                   # forward plate slab (= case forward wall)
    box = bx(x0, x1, -5.0, 47.0, CDC_Z[0], 22.0)
    box = box - bx(K.X_BRG_A[1], gx1, -1.0, 48.0, 0.0, 23.0)  # window: the gear slab is open above the split face ...
    box = box + bx(K.X_BRG_A[1], gx1, -5.0, -1.0, 0.0, 22.0) + bx(K.X_BRG_A[1], gx1, 43.0, 47.0, 0.0, 22.0)      # ... except two posts at the edges
    pts = [xo["P1"], xo["Pa"], xo["Pb"]]
    box = box + _plate(pa0, K.X_BRG_A[1], pts) + _plate(gx1, pf1, pts)
    cuts = [cx(K.C_BRG_A[1], gx1, SY, 0.0, 36.2),                                              # carrier + spur ring cavity
            seat_x(*K.C_BRG_A, SY, 0.0, through=(x0 - 1.0, K.C_BRG_A[1])),
            seat_x(*K.C_BRG_F, SY, 0.0, through=(K.C_BRG_F[0], pf1 + 1.0))]
    for tag in ("P1", "Pa", "Pb"):
        y, z = xo[tag]
        cuts.append(cx(K.X_BRG_A[0] - 0.2, K.X_BRG_A[1] + 0.5, y, z, SEAT))
        cuts.append(cx(K.X_BRG_A[0] - 5.0, K.X_BRG_A[0], y, z, BORE))                        # blind 5 mm bore behind the bearing
        cuts.append(cx(K.X_BRG_F[0], K.X_BRG_F[1] + 0.2, y, z, SEAT))
        cuts.append(cx(K.X_BRG_F[1] - 1.0, pf1 + (1.0 if tag == "P1" else -1.5), y, z, BORE))   # P1: the motor shaft runs forward through the plate
    for x, y in ((x0 + 4.0, -2.5), (x0 + 4.0, 44.5), (pf1 - 4.0, -2.5), (pf1 - 4.0, 44.5)):
        cuts.append(hole_z(x, y, CDC_Z[0], 22.0))
    for c in cuts:
        box = box - c
    return split("w3_cdc", box, CDC_Z)


def rear_bevel_case():
    x0, x1 = XR - 25.0, K.R_BRG[1][1] + 5.0
    box = bx(x0, x1, 6.0, 37.2, RBC_Z[0], RBC_Z[1]) + cy(XR, 37.0, 40.1, 0.0, 16.0)       # boss for the outboard bearing: the frame tubes pass at y 37.5 beside it
    cuts = [cy(XR, 15.0, 32.6, 0.0, 30.0),                                                          # ring cavity (ring OD 25.5)
            cx(XR, K.R_PIN_X[1] + 0.5, SY, 0.0, 15.0),                                              # pinion tunnel
            cy(XR, 5.9, 40.1, 0.0, BORE),
            cy(XR, 7.9, 12.2, 0.0, SEAT),                                                           # inboard bearing
            cy(XR, 34.0, 38.2, 0.0, SEAT),                                                          # outboard bearing
            cx(K.R_PIN_X[1] + 0.5, x1 + 1.0, SY, 0.0, BORE)]
    for b in K.R_BRG:
        cuts.append(seat_x(b[0], b[1], SY, 0.0))
    for x, y in ((XR - 22.0, 8.5), (XR - 22.0, 33.5), (XR + 31.0, 8.5), (XR + 31.0, 33.5)):
        cuts.append(hole_z(x, y, *RBC_Z))
    for c in cuts:
        box = box - c
    return split("w3_rbc", box, RBC_Z, supports=False)


def pillow_block():
    """Mid-span support for the 5 mm rear shaft (one 5 x 11 x 4 bearing)."""
    x = K.PILLOW_X
    box = bx(x - 7.0, x + 7.0, 6.0, 36.0, PIL_Z[0], PIL_Z[1])
    cuts = [seat_x(x - 2.0, x + 2.0, SY, 0.0, through=(x - 8.0, x + 8.0)), hole_z(x, 8.5, *PIL_Z), hole_z(x, 33.5, *PIL_Z)]
    for c in cuts:
        box = box - c
    return split("w3_pillow", box, PIL_Z, supports=False)


def ring_hubs():
    """Printed hubs that carry a stock gear on a 5 mm shaft or the carrier flange: spigot into the gear bore, 6-bolt flange (M2 on a 15 mm circle)."""
    from parts.w3_style import MeshPart, _clean
    out = []

    def hub(name, spigot_d, spigot_l, flange_d, flange_t, bore):
        def fn():
            m = Mf.cylinder(flange_t, flange_d / 2, flange_d / 2, 64) + Mf.cylinder(flange_t + spigot_l, spigot_d / 2, spigot_d / 2, 64)
            m = m - Mf.cylinder(flange_t + spigot_l + 2.0, bore / 2, bore / 2, 32).translate((0.0, 0.0, -1.0))
            for k in range(6):
                a = math.radians(60.0 * k)
                m = m - Mf.cylinder(flange_t + 2.0, 1.1, 1.1, 16).translate((K.RING_BC / 2 * math.cos(a), K.RING_BC / 2 * math.sin(a), -1.0))
            return _clean(MB.to_trimesh(m))
        return MeshPart(name, fn, walls=True, supports=False)

    out.append(hub("w3_rring_hub", K.RING_BORE - 0.2, 6.0, 22.0, 3.0, K.SHAFT_D + 0.1))                    # rear bevel ring: spigot 10.8, set screw in the spigot
    out.append(hub("w3_cring_hub", K.SPUR_BORE[40] - 0.2, K.SPUR_W + 0.3, 24.0, 4.0, K.SHAFT_D + 0.1))      # 40T spur ring on the centre carrier
    return out


def motor_plate(p):
    """Vertical plate behind the motor with vertical slots (mesh adjustment) and a slotted foot.
    Print frame: u = y, v = -z, w = -x + MOTOR_C x - 29 (plate thickness up); a proper rotation to the assembly frame."""
    part = Part("w3_motor_plate", "plate on its back", "PETG")
    t = 4.0
    part.box((-41.0, -(MOTOR_C[2] + 15.0), 0.0), (45.0, 30.0, t))            # plate, y -41..4, 30 high around the motor axis
    for dy in (-8.0, 8.0):
        for z in (16.0, 32.0):
            part.box((MOTOR_C[1] + dy - 1.7, -(MOTOR_C[2] + z - 24.0) - 4.0, -1.0), (3.4, 8.0, t + 2.0), op="cut")   # motor screw slots, 8 long
    part.cyl((MOTOR_C[1], -MOTOR_C[2], -1.0), 8.0, t + 2.0, op="cut")          # clearance for the output shaft
    for y in (-2.0, -35.0):                                                  # screws from behind through the body bulkhead
        part.cyl((y, -(MOTOR_C[2] + 3.0), -1.0), 2.2, 3.0, op="cut")
    return part


def tray(name, size, rails, strap=False):
    """Slotted tray: floor with slots along x for fore/aft adjustment, side walls."""
    lx, ly = size
    part = Part(name, "floor on the bed", "PETG")
    part.box((0.0, 0.0, 0.0), (lx, ly, 3.0))
    part.box((0.0, 0.0, 0.0), (lx, 2.4, 16.0))
    part.box((0.0, ly - 2.4, 0.0), (lx, 2.4, 16.0))
    for x in (8.0, lx - 8.0 - 12.0):
        for y in rails:
            part.box((x, y - 1.7, -1.0), (12.0, 3.4, 5.0), op="cut")
    return part


def _rear_styled(p):
    from parts import w3_style
    return [w3_style.rear_arm(p)]


def build(p):
    return (front_diff_case() + center_diff_case() + rear_bevel_case() + pillow_block() + ring_hubs() + [motor_plate(p)] + _rear_styled(p)
            + [tray("w3_batt_tray", (66.0, 24.0), (6.0, 18.0)), tray("w3_esc_tray", (50.0, 42.0), (8.0, 34.0))])
