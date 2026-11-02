"""WS-03 front end parts: swing arm with belt housing, cover, upper link, carrier, knuckle.

Frame (assembly): x forward, y left, z up, z = 0 at the front axle height, front axle at x = 0, arm pivot (front diff axis) at
x = -ARM_L. Each part is built in its own print frame (u, v, w): u = x, w = |y| - Y0 (outer faces up), v = -z (left) / z (right), a proper rotation.
"""

import numpy as np

from cad import Part

ARM_L = 100.0
ZU = 40.0                  # upper link pin height above the lower pin
YS = 6.5                   # outward shift of the arm / servo / wall stack (clears the front diff case)
ARM_Y = (58.0 + YS, 67.5 + YS)       # arm body |y| (floor 58-63.5, belt cavity 63.5-67.5)
UP_Y = (58.0 + YS, 61.5 + YS)
KP_D = 4.0                 # kingpin diameter (steel, hangs from the carrier tab; 3 mm gave a factor of safety of only 2.3)
KP_Y = 123.0               # kingpin / dogbone joint |y|
CAR_Y = (102.0, 110.0)
KN_Y = (118.0, 130.0)
ARM_A = (0.0, -16.0, -26.0)   # steering arm point from the kingpin axis: dx, dy (inboard negative), dz from axle
LUG = (22.6, 12.0)               # lean link pin on the arm, from the pivot (x, z)


class PF:
    """Print-frame helper for one side: chassis (x, |y|, z) to print (u, v, w)."""

    def __init__(self, part, side, y0):
        self.p, self.s, self.y0 = part, side, y0

    def v(self, z0, z1):
        return (-z1, -z0) if self.s > 0 else (z0, z1)

    def box(self, x, y, z, op="join"):
        v0, v1 = self.v(*z)
        self.p.box((x[0], v0, y[0] - self.y0), (x[1] - x[0], v1 - v0, y[1] - y[0]), op=op)

    def cyl_y(self, x, z, y, d, op="join"):
        v = -z if self.s > 0 else z
        self.p.cyl((x, v, y[0] - self.y0), d, y[1] - y[0], op=op)

    def cyl_z(self, x, yy, z, d, op="cut"):
        v0, v1 = self.v(*z)
        self.p.cyl((x, v0, yy - self.y0), d, v1 - v0, axis="Y", op=op)


def mats(side, y0):
    """Print frame to assembly frame, 4x4."""
    m = np.eye(4)
    if side > 0:
        m[:3, :3] = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]
        m[1, 3] = y0
    else:
        m[:3, :3] = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]
        m[1, 3] = -y0
    return m


def build(p):
    from parts import w3_style
    out = []
    for s in (1, -1):
        out += [w3_style.arm(p, s), w3_style.uplink(p, s), w3_style.carrier(p, s), w3_style.knuckle(p, s)]
    return out
