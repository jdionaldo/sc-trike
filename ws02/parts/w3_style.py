"""WS-03 styled parts built as meshes (manifold3d): swing arms, covers and links with angular, tapered outlines that echo the body.

Each builder writes an STL in the same print frame as the part it replaces, so placement matrices are unchanged.
"""
import math
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import trimesh
from manifold3d import Manifold

import mono_build as MB
from parts import w3_front as W
from parts import w3_drive as D


@dataclass
class MeshPart:
    name: str
    fn: object
    walls: bool = True
    supports: bool = False
    cmds: list = field(default_factory=list)
    to_chassis: object = None

    def write(self, path):
        m = self.fn()
        m.export(path)


def _cy(x, z, y0, y1, d):
    lo, hi = sorted((y0, y1))
    m = Manifold.cylinder(hi - lo, d / 2, d / 2, 48).rotate((-90.0, 0.0, 0.0))
    return m.translate((x, lo, z))


def _to_print(m, side, y0):
    t = trimesh.Trimesh(*[np.asarray(a) for a in (np.asarray(m.to_mesh().vert_properties)[:, :3], np.asarray(m.to_mesh().tri_verts))])
    inv = np.linalg.inv(W.mats(side, y0))
    t.apply_transform(inv)
    t.merge_vertices()
    return t


ARM_OUT = [(-114, 0), (-112, -8), (-105, -12), (-95, -12.5), (-60, -11.5), (-20, -11), (4, -11), (11, -7), (14, 0), (11, 7), (4, 11),
           (-12, 12.5), (-40, 14), (-62, 17.5), (-76, 20), (-88, 16), (-104, 13), (-112, 8)]
UP_OUT = [(-114, 0), (-109, -7.5), (-96, -7.5), (-20, -5.5), (-4, -6.5), (4, -5), (7, 0), (4, 5), (-4, 6.5), (-20, 5.5), (-96, 7.5), (-109, 7.5)]
COVER_OUT = [(-113, 0), (-111, -7), (-104, -11.5), (-95, -12), (-60, -10.5), (-20, -10), (4, -10), (10, -6.5), (13, 0), (10, 6.5), (4, 10),
             (-12, 11.5), (-40, 13), (-62, 16.5), (-76, 19), (-88, 15), (-104, 12), (-111, 7)]


def arm(p, side):
    s = side
    ya, yb = W.ARM_Y
    def fn():
        yy = lambda a, b: (s * a, s * b)
        body = MB.prism_xz(ARM_OUT, *sorted(yy(ya, yb)))
        cav = MB.prism_xz([(-107.5, -7.5), (7.5, -7.5), (7.5, 7.5), (-107.5, 7.5)], *sorted(yy(63.5 + W.YS, yb + 0.1)))
        body = body - cav
        xp = -W.ARM_L
        for x, d1, d2 in ((xp, 11.15, 5.4), (0.0, 8.15, 4.4)):
            body = body - _cy(x, 0.0, *yy(ya - 0.1, ya + 4.0), d1) if x == xp else body - _cy(x, 0.0, *yy(ya - 0.1, ya + 3.0), d1)
            body = body - _cy(x, 0.0, *yy(ya - 0.1, yb + 0.1), d2)
        body = body - _cy(xp + W.LUG[0], W.LUG[1], *yy(ya - 0.1, yb + 0.1), 2.4)
        for x in (xp - 11.0, 11.0):
            body = body - _cy(x, 0.0, *yy(yb - 5.0, yb + 0.1), 2.2)
        return _to_print(body, s, ya)
    return MeshPart("w3_arm_left" if s > 0 else "w3_arm_right", fn)


def cover(p, side):
    s = side
    ya, yb = W.COVER_Y
    def fn():
        body = MB.prism_xz(COVER_OUT, *sorted((s * ya, s * yb)))
        for x in (-W.ARM_L - 11.0, 11.0):
            body = body - _cy(x, 0.0, s * (ya - 0.1), s * (yb + 0.1), 2.7)
        return _to_print(body, s, ya)
    return MeshPart("w3_arm_cover_left" if s > 0 else "w3_arm_cover_right", fn)


def uplink(p, side):
    s = side
    ya, yb = W.UP_Y
    def fn():
        pts = [(x, W.ZU + z) for x, z in UP_OUT]
        body = MB.prism_xz(pts, *sorted((s * ya, s * yb)))
        for x in (-W.ARM_L, 0.0):
            body = body - _cy(x, W.ZU, s * (ya - 0.1), s * (yb + 0.1), p.pin_dia + p.clr_slide)
        return _to_print(body, s, ya)
    return MeshPart("w3_uplink_left" if s > 0 else "w3_uplink_right", fn)


def build(p):
    out = []
    for s in (1, -1):
        out += [arm(p, s), cover(p, s), uplink(p, s)]
    return out


def _rear_outline(L, inset=0.0):
    i = inset
    top = [(-14 + i, 0), (-10 + i, 9 - i), (0, 13.5 - i), (20, 14 - i), (60, 12.5 - i), (L - 5, 12.5 - i), (L + 8, 12 - i), (L + 13 - i, 8), (L + 14 - i, 0)]
    bot = [(L + 13 - i, -8), (L + 8, -12 + i), (L - 5, -12.5 + i), (60, -12.5 + i), (20, -13.5 + i), (0, -13.5 + i), (-10 + i, -9 + i)]
    return top + bot


def _cz(u, v, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2, d / 2, 48).translate((u, v, z0))


def rear_arm(p):
    L = math.hypot(D.XR - D.RAXLE[0], D.RAXLE[1])
    def fn():
        body = MB.prism_xy(_rear_outline(L), 0.0, 12.0)
        body = body - MB.prism_xy([(-8, -8.5), (L + 8, -8.5), (L + 8, 8.5), (-8, 8.5)], 7.2, 12.1)
        body = body - _cz(0.0, 0.0, -0.1, D.SEAT_D, D.SEAT) - _cz(0.0, 0.0, -0.1, 12.2, D.BORE)
        body = body - _cz(L, 0.0, -0.1, 5.1, 16.15) - _cz(L, 0.0, -0.1, 12.2, 8.4)
        for u in (-11.0, L + 11.0):
            body = body - _cz(u, 0.0, 6.0, 12.1, 2.0)
        m = MB.to_trimesh(body)
        m.merge_vertices()
        return m
    return MeshPart("w3_rear_arm", fn, supports=True)


def rear_arm_cover(p):
    L = math.hypot(D.XR - D.RAXLE[0], D.RAXLE[1])
    def fn():
        body = MB.prism_xy(_rear_outline(L, 0.6), 0.0, 1.5)
        for u in (-11.0, L + 11.0):
            body = body - _cz(u, 0.0, -0.1, 1.7, 2.7)
        m = MB.to_trimesh(body)
        m.merge_vertices()
        return m
    return MeshPart("w3_rear_arm_cover", fn)


WALL_OUT = [(-157, -20), (-150, -28), (-30, -28), (-24, -22), (-24, 28), (-34, 46), (-104, 46), (-110, 40), (-112, 14), (-150, 14), (-157, 8)]


def wall(p, side):
    """Servo wall with a chamfered outline and a triangular lightening window. |y| 54.5..57.5, outer face on the bed (w = 51 + YS - |y|)."""
    s = side
    yo = 51.0 + W.YS
    def fn():
        yi, ya = yo - 3.0, yo
        body = MB.prism_xz(WALL_OUT, *sorted((s * yi, s * ya)))
        body = body - MB.prism_xz([(-96, 24), (-52, 24), (-96, 38)], *sorted((s * (yi - 0.1), s * (ya + 0.1))))       # lightening window
        for x, z, d in ((-71.4, -18.8, 8.0), (-100.0, -14.0, 8.0), (-100.0, 0.0, 7.0), (-100.0, 40.0, 3.4)):
            body = body - _cy(x, z, s * (yi - 0.1), s * (ya + 0.1), d)
        for xs, zs in ((-60.0, -18.8), (-111.4, -14.0)):
            for dx in (-24.5, 24.5):
                for dz in (-5.0, 5.0):
                    body = body - _cy(xs + dx, zs + dz, s * (yi - 0.1), s * (ya + 0.1), p.m2_clear)
        for x in (-150.0, -86.0):
            body = body - _cy(x, -10.0, s * (yi - 0.1), s * (ya + 0.1), 2.7)
        body = body - MB.prism_xz([(-108, -29), (-92, -29), (-92, -22), (-108, -22)], *sorted((s * (yi - 0.1), s * (ya + 0.1))))   # rod eye notch
        m = body.to_mesh()
        t = trimesh.Trimesh(np.asarray(m.vert_properties)[:, :3], np.asarray(m.tri_verts))
        mm = np.eye(4)
        if s > 0:
            mm[:3, :3] = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]; mm[1, 3] = yo
        else:
            mm[:3, :3] = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]; mm[1, 3] = -yo
        t.apply_transform(np.linalg.inv(mm))
        t.merge_vertices()
        return t
    return MeshPart("w3_wall_left" if s > 0 else "w3_wall_right", fn)


WING_T = 4.5                                                       # fender plate thickness: stiffer for minor crashes
WING = [(-50, -4), (-34, 16), (-18, 34), (-8, 42), (30, 42), (38, 34), (42, 12), (34, -4)]


def wing_plate(p, side):
    """Wing fender plate on the inboard face of the carrier; print frame u = x, v = z + 4, w = thickness. Crisp angular outline."""
    def fn():
        body = MB.prism_xy([(x, z + 4.0) for x, z in WING], 0.0, WING_T)
        body = body - _cz(0.0, 4.0, -0.1, WING_T + 0.2, 6.4)
        for x in (-6.0, 6.0):
            body = body - _cz(x, 20.0, -0.1, WING_T + 0.2, p.m2_clear)
        m = MB.to_trimesh(body)
        m.merge_vertices()
        return m
    return MeshPart("w3_wing_left" if side > 0 else "w3_wing_right", fn)


CAR_OUT = [(-10, -3), (-6, -7), (6, -7), (10, -3), (10, 6), (5.5, 26), (4.5, 38), (2.5, 45), (-2.5, 45), (-4.5, 38), (-5.5, 26), (-10, 6)]
KN_OUT = [(-6, -29), (6, -29), (6, -14), (10, -9), (10, 10), (5, 13.5), (-8, 13.5), (-12, 9), (-12, -8), (-6, -14)]


def _cut_edge(body, y, z, s, ang=45.0, size=3.0):
    """Chamfer: remove a square rotated 45 deg about x, centred on the edge at (y, z) in the assembly frame (side s)."""
    c = Manifold.cube((30.0, size * 1.414, size * 1.414), center=True).rotate((ang, 0.0, 0.0)).translate((0.0, s * y, z))
    return body - c


def _local_to_print(m, mat):
    t = MB.to_trimesh(m)
    t.apply_transform(np.linalg.inv(mat))
    t.merge_vertices()
    return t


def carrier(p, side):
    s = side
    ya, yb = W.CAR_Y
    def fn():
        yy = lambda a, b: tuple(sorted((s * a, s * b)))
        body = MB.prism_xz(CAR_OUT, *yy(ya, yb))
        tab = MB.prism_xz([(-6, 14), (6, 14), (6, 24), (-6, 24)], *yy(yb - 0.5, W.KN_Y[1] + 4))
        tab = _cut_edge(tab, W.KN_Y[1] + 4, 14.0, s, size=3.0)                    # chamfered outer lower corner
        tab = _cut_edge(tab, W.KN_Y[1] + 4, 24.0, s, size=2.0)
        body = body + tab
        body = body - _cy(0.0, 0.0, *yy(ya - 0.1, yb + 0.1), 8.15)
        body = body - _cy(0.0, W.ZU, *yy(ya - 0.1, yb + 0.1), 3.4)
        kp = Manifold.cylinder(11.0, (W.KP_D + 0.0) / 2 + 0.05, (W.KP_D + 0.0) / 2 + 0.05, 32).translate((0.0, s * W.KP_Y, 13.5))
        body = body - kp
        return _local_to_print(body, W.mats(s, ya))
    return MeshPart("w3_carrier_left" if s > 0 else "w3_carrier_right", fn)


def knuckle(p, side):
    s = side
    y0, y1 = W.KN_Y[0] + 0.5, W.KN_Y[1]
    y_in = W.KP_Y + W.ARM_A[1]
    def fn():
        yy = lambda a, b: tuple(sorted((s * a, s * b)))
        body = MB.prism_xz(KN_OUT[:], *yy(y0, y1))
        beam = MB.prism_xz([(-6, W.ARM_A[2] - 3), (6, W.ARM_A[2] - 3), (6, W.ARM_A[2] + 3), (-6, W.ARM_A[2] + 3)], *yy(y_in - 3.0, y1))
        beam = _cut_edge(beam, y_in - 3.0, W.ARM_A[2] + 3, s, size=2.5)           # chamfered inner end
        beam = _cut_edge(beam, y_in - 3.0, W.ARM_A[2] - 3, s, size=2.5)
        body = body + beam
        body = body - _cy(0.0, 0.0, *yy(W.KN_Y[0], y1 + 0.1), p.axle_dia + p.clr_slide + 0.6)
        body = body - Manifold.cylinder(26.0, (W.KP_D + p.clr_slide) / 2, (W.KP_D + p.clr_slide) / 2, 32).translate((0.0, s * W.KP_Y, -12.0))
        body = body - _cy(W.ARM_A[0], W.ARM_A[2], *yy(y_in - 3.1, y_in + 3.0), p.ball_stud_dia + p.clr_press * 2)
        km = np.eye(4)
        if s > 0:
            km[:3, :3] = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]; km[1, 3] = W.KN_Y[1]
        else:
            km[:3, :3] = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]; km[1, 3] = -W.KN_Y[1]
        return _local_to_print(body, km)
    return MeshPart("w3_knuckle_left" if s > 0 else "w3_knuckle_right", fn)


def wing(p, side):
    """Tubular wing fender: an angular loop of 4.5 mm tube following the old plate outline, three spokes to a small mount block on the carrier.
    Same envelope as the plate (w 0..4.5); print frame u = x, v = z + 4, w = thickness."""
    from parts.w3_frame import tube, ball
    def fn():
        r = WING_T / 2
        pts = [(x, z + 4.0) for x, z in WING]
        P = lambda q: (q[0], q[1], r)
        parts = []
        for a, b in zip(pts, pts[1:] + pts[:1]):
            parts += [tube(P(a), P(b), r), ball(P(b), r)]
        for q in (pts[0], pts[3], pts[6]):                                  # spokes: tail, top shoulder, nose from the mount
            parts.append(tube(P((0.0, 12.0)), P(q), r))
        mount = MB.prism_xy([(-8.0, -4.0 + 4.0 - 4.0), (8.0, 0.0), (8.0, 28.0), (-8.0, 28.0)], 0.0, WING_T)
        body = parts[0]
        for q in parts[1:] + [mount]:
            body = body + q
        body = body - _cz(0.0, 4.0, -0.1, WING_T + 0.2, 6.4)
        for x in (-6.0, 6.0):
            body = body - _cz(x, 20.0, -0.1, WING_T + 0.2, p.m2_clear)
        m = MB.to_trimesh(body)
        m.merge_vertices()
        return m
    return MeshPart("w3_wing_left" if side > 0 else "w3_wing_right", fn, walls=False, supports=True)
