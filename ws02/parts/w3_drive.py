"""WS-03 drivetrain printed parts: split gear housings, slotted motor plate, battery and ESC trays, rear arm and cover.

Assembly frame: x forward, y left, z up, z = 0 at the front axle height, shafts at z = 0, shaft line y = SY.
Housings are split on the z = 0 plane (every shaft lies in it). The lower half prints as built; the upper half prints flipped
(print = assembly rotated 180 deg about x), split faces on the bed.
"""
import math

from cad import Part

SY = 21.0                 # shaft line |y| (pinion shaft, centre diff axis, rear shaft)
XD = -100.0               # front diff axis x (arm pivots)
XR = -272.0               # rear bevel apex x (rear arm pivot)
RAXLE = (-360.0, -10.7)   # rear axle (x, z): wheelbase 360, chassis raked 4 deg nose-down
BORE = 5.4                # 5 mm shaft
SEAT = 11.15              # 5 x 11 x 4 bearing
SEAT_D = 4.0
BOLT = 2.7                # M2.5 clear
M25 = 2.2                 # M2.5 tap


class H:
    """One half of a split housing, authored in print coordinates."""

    def __init__(self, name, upper, zspan):
        self.upper, self.zspan = upper, zspan
        self.p = Part(name, "split face on the bed", "PETG")

    def _v(self, y0, y1):
        return (-y1, -y0) if self.upper else (y0, y1)

    def _w(self, z0, z1):
        # split face up for both halves: the lower half prints as built, the upper half rotated 180 deg about x
        return (self.zspan[1] - z1, self.zspan[1] - z0) if self.upper else (z0 - self.zspan[0], z1 - self.zspan[0])

    def box(self, x, y, z, op="join"):
        v0, v1 = self._v(*y)
        w0, w1 = self._w(*z)
        self.p.box((x[0], v0, w0), (x[1] - x[0], v1 - v0, w1 - w0), op=op)

    def cyl_x(self, x, y, z, d, op="cut"):
        v = -y if self.upper else y
        w = self.zspan[1] - z if self.upper else z - self.zspan[0]
        self.p.cyl((x[0], v, w), d, x[1] - x[0], axis="X", op=op)

    def cyl_y(self, x, y, z, d, op="cut"):
        w = self.zspan[1] - z if self.upper else z - self.zspan[0]
        if self.upper:
            self.p.cyl((x, -y[1], w), d, y[1] - y[0], axis="Y", op=op)
        else:
            self.p.cyl((x, y[0], w), d, y[1] - y[0], axis="Y", op=op)

    def hole_z(self, x, y, d, op="cut"):
        v = -y if self.upper else y
        self.p.cyl((x, v, -1.0), d, self.zspan[1] - self.zspan[0] + 2.0, op=op)


def _halves(name, box, build):
    out = []
    for upper in (False, True):
        z0, z1 = box[2]
        h = H(f"{name}_{'upper' if upper else 'lower'}", upper, (z0, z1))
        h.box(box[0], box[1], (0.0, z1) if upper else (z0, 0.0))
        build(h)
        out.append(h.p)
    return out


def front_diff_case(p):
    box = ((-158.0, -80.0), (-26.0, 34.0), (-22.0, 22.0))

    def build(h):
        if not h.upper:                                                    # ears that hold the servo wall: blocks beside the servos
            for xa, xb in ((-156.6, -140.2), (-90.0, -82.0)):
                h.box((xa, xb), (30.0, 54.5), (-22.0, 0.0))
        h.cyl_y(XD, (-17.0, 25.0), 0.0, 35.6)                              # carrier and ring cavity
        h.cyl_x((-150.0, XD + 1.0), SY, 0.0, 15.0)                         # pinion tunnel
        for yy in ((-26.1, -22.0), (30.0, 34.1)):                          # output bearing seats
            h.cyl_y(XD, yy, 0.0, SEAT)
        h.cyl_y(XD, (-26.1, 34.1), 0.0, BORE)
        h.cyl_x((-158.1, -154.0), SY, 0.0, SEAT)                           # pinion shaft bearing
        h.cyl_x((-158.1, -146.0), SY, 0.0, BORE)
        for x, y in ((-88.0, -22.0), (-88.0, 30.0), (-155.0, -22.0), (-155.0, 31.0)):
            h.hole_z(x, y, BOLT)
        if not h.upper:
            for xa, xb in ((-156.6, -140.2), (-90.0, -82.0)):
                h.cyl_y(0.5 * (xa + xb), (42.0, 54.6), -10.0, 2.2)           # M2.5 pilot into the wall
    return _halves("w3_fdc", box, build)


def center_diff_case(p):
    box = ((-205.0, -158.0), (-5.0, 47.0), (-22.0, 22.0))

    def build(h):
        h.cyl_x((-200.0, -161.0), SY, 0.0, 39.2)                           # carrier cavity
        for xx in ((-205.1, -201.0), (-162.0, -157.9)):
            h.cyl_x(xx, SY, 0.0, SEAT)
        h.cyl_x((-205.1, -157.9), SY, 0.0, BORE)
        if h.upper:
            h.box((-198.0, -186.0), (SY - 8.0, SY + 8.0), (-1.0, 23.0), op="cut")   # window for the motor pinion
        for x, y in ((-201.5, -2.5), (-201.5, 44.5), (-161.5, -2.5), (-161.5, 44.5)):
            h.hole_z(x, y, BOLT)
    return _halves("w3_cdc", box, build)


def rear_bevel_case(p):
    box = ((-297.0, -244.0), (6.0, 36.0), (-21.0, 21.0))

    def build(h):
        h.cyl_y(XR, (13.0, 29.0), 0.0, 33.6)                               # ring cavity
        h.cyl_x((XR, -248.0), SY, 0.0, 15.0)                               # pinion tunnel
        h.cyl_x((-248.1, -244.0), SY, 0.0, SEAT)
        h.cyl_x((-248.1, -243.9), SY, 0.0, BORE)
        h.cyl_y(XR, (5.9, 10.0), 0.0, SEAT)                                # shaft end bearing
        h.cyl_y(XR, (32.0, 36.1), 0.0, SEAT)                               # output bearing
        h.cyl_y(XR, (5.9, 36.1), 0.0, BORE)
        for x, y in ((-294.0, 8.5), (-294.0, 33.5), (-247.5, 8.5), (-247.5, 33.5)):
            h.hole_z(x, y, BOLT)
    return _halves("w3_rbc", box, build)


def motor_plate(p):
    """Vertical plate behind the motor with vertical slots (mesh adjustment) and a slotted foot.
    Print frame: u = y, v = -z, w = -x - 232 (plate thickness up); a proper rotation to the assembly frame."""
    part = Part("w3_motor_plate", "plate on its back", "PETG")
    t = 4.0
    part.box((-4.0, -46.0, 0.0), (45.0, 38.0, t))                            # plate, y -4..41, z 8..46 (clear of the shaft line)
    for dy in (-8.0, 8.0):
        for z in (16.0, 32.0):
            part.box((SY + dy - 1.7, -z - 4.0, -1.0), (3.4, 8.0, t + 2.0), op="cut")   # motor screw slots, 8 long
    for y in (2.0, 35.0):                                                    # screws from behind through the body bulkhead
        part.cyl((y, -27.0, -1.0), 2.2, 3.0, op="cut")
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


def rear_arm(p):
    """Single-sided rear swingarm housing, straight along u (pivot at u = 0, axle at u = L). Inner face on the bed (w = 0)."""
    L = math.hypot(XR - RAXLE[0], RAXLE[1])
    part = Part("w3_rear_arm", "inner face on the bed, belt cavity up", "PETG")
    hh = 11.0
    part.supports = True                                                        # bearing seat ledge bridges 16 mm
    part.box((-14.0, -hh, 0.0), (L + 28.0, 2 * hh, 12.0))
    part.box((-8.0, -8.5, 7.2), (L + 16.0, 17.0, 4.9), op="cut")               # belt cavity (floor 7.2, depth 4.8)
    part.cyl((0.0, 0.0, -0.1), SEAT, SEAT_D + 0.1, op="cut")                    # pivot bearing seat on the inner face
    part.cyl((0.0, 0.0, -0.1), BORE, 12.2, op="cut")
    part.cyl((L, 0.0, -0.1), 16.15, 5.1, op="cut")                              # axle bearing 8 x 16 x 5
    part.cyl((L, 0.0, -0.1), 8.4, 12.2, op="cut")
    for u in (-11.0, L + 11.0):
        part.cyl((u, 0.0, 6.0), 2.0, 6.1, op="cut")                             # cover screws
    return part


def rear_arm_cover(p):
    L = math.hypot(XR - RAXLE[0], RAXLE[1])
    part = Part("w3_rear_arm_cover", "flat", "PETG")
    part.box((-14.0, -11.0, 0.0), (L + 28.0, 22.0, 1.5))
    for u in (-11.0, L + 11.0):
        part.cyl((u, 0.0, -0.1), 2.7, 1.7, op="cut")
    return part


def build(p):
    return (front_diff_case(p) + center_diff_case(p) + rear_bevel_case(p) + [motor_plate(p), rear_arm(p), rear_arm_cover(p)]
            + [tray("w3_batt_tray", (66.0, 24.0), (6.0, 18.0)), tray("w3_esc_tray", (50.0, 42.0), (8.0, 34.0))])
