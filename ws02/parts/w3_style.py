"""WS-03 styled parts built as meshes (manifold3d): swing arms, covers and links with angular, tapered outlines that echo the body.

Each builder writes an STL in the same print frame as the part it replaces, so placement matrices are unchanged.
"""
import math
from dataclasses import dataclass, field

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


def _clean(t):
    """Round to what the STL holds, drop degenerate faces, merge."""
    t.vertices = np.asarray(t.vertices, np.float32).astype(np.float64)
    t.update_faces(t.nondegenerate_faces())
    t.remove_unreferenced_vertices()
    t.merge_vertices()
    return t


def _to_print(m, side, y0):
    t = trimesh.Trimesh(*[np.asarray(a) for a in (np.asarray(m.to_mesh().vert_properties)[:, :3], np.asarray(m.to_mesh().tri_verts))])
    inv = np.linalg.inv(W.mats(side, y0))
    t.apply_transform(inv)
    return _clean(t)


COVER_OUT = [(-113, 0), (-111, -7), (-104, -11.5), (-95, -12), (-60, -10.5), (-20, -10), (4, -10), (10, -6.5), (13, 0), (10, 6.5), (4, 10),
             (-12, 11.5), (-40, 13), (-62, 16.5), (-76, 19), (-88, 15), (-104, 12), (-111, 7)]


def cover(p, side):
    s = side
    ya, yb = W.COVER_Y
    def fn():
        body = MB.prism_xz(COVER_OUT, *sorted((s * ya, s * yb)))
        for x in (-W.ARM_L - 11.0, 11.0):
            body = body - _cy(x, 0.0, s * (ya - 0.1), s * (yb + 0.1), 2.7)
        return _to_print(body, s, ya)
    return MeshPart("w3_arm_cover_left" if s > 0 else "w3_arm_cover_right", fn)


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



def _cut_edge(body, y, z, s, ang=45.0, size=3.0):
    """Chamfer: remove a square rotated 45 deg about x, centred on the edge at (y, z) in the assembly frame (side s)."""
    c = Manifold.cube((30.0, size * 1.414, size * 1.414), center=True).rotate((ang, 0.0, 0.0)).translate((0.0, s * y, z))
    return body - c


def _local_to_print(m, mat):
    t = MB.to_trimesh(m)
    t.apply_transform(np.linalg.inv(mat))
    return _clean(t)


# ---- tubular trellis redesign: swing arm as a 3D box truss, spindle upper link, trellis carrier and knuckle ----
def _tb(a, b, r, r2=None):
    """Tube (or cone from radius r to r2) between two assembly-frame points."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = float(np.linalg.norm(d))
    T = trimesh.geometry.align_vectors([0.0, 0.0, 1.0], d / L)
    mat = np.array(T[:3, :4])
    mat[:, 3] = a
    return Manifold.cylinder(L, r, r if r2 is None else r2, 28).transform(mat)


def _ball(p, r):
    return Manifold.sphere(r, 28).translate(tuple(p))


def _join(ms):
    out = ms[0]
    for m in ms[1:]:
        out = out + m
    return out


RT = 2.4                      # arm rail radius (0.1 clear of the print-frame planes)
ARM_NODES = {"L0": (-100.0, -10.3), "L1": (-60.0, -9.3), "L2": (0.0, -9.3),
             "U0": (-100.0, 10.5), "U1": (-76.0, 17.5), "U2": (-38.0, 11.5), "U3": (0.0, 9.4)}
ARM_RAILS = [("L0", "L1"), ("L1", "L2"), ("U0", "U1"), ("U1", "U2"), ("U2", "U3")]
ARM_WEB = [("L0", "U1"), ("U1", "L1"), ("L1", "U2"), ("U2", "L2")]          # zigzag in the inner plane


def arm(p, side):
    """Box-truss swing arm: inner plane = rails + zigzag, outer plane = rails only (the belt runs between, clear of the diagonals),
    ties across; hubs with the bearing seats on the inner face; lug for the lean rod."""
    s = side
    ya, yb = W.ARM_Y
    yi, yo = s * (ya + 2.5), s * (ya + 7.0)               # inner / outer plane centres (67.0, 71.5)
    yy = lambda a, b: (s * a, s * b)
    def fn():
        P = lambda k, y: (ARM_NODES[k][0], y, ARM_NODES[k][1])
        parts = []
        for a, b in ARM_RAILS:
            parts += [_tb(P(a, yi), P(b, yi), RT), _tb(P(a, yo), P(b, yo), RT)]
        for a, b in ARM_WEB:
            parts.append(_tb(P(a, yi), P(b, yi), RT))
        for k in ARM_NODES:                                # ties across the belt gap, outside the belt hull
            parts += [_tb(P(k, yi), P(k, yo), RT), _ball(P(k, yi), RT), _ball(P(k, yo), RT)]
        xp = -W.ARM_L
        parts += [_cy(xp, 0.0, *yy(ya, ya + 5.5), 20.0), _cy(0.0, 0.0, *yy(ya, ya + 5.5), 18.0)]          # hubs
        parts += [_cy(W.LUG[0] + xp, W.LUG[1], *yy(ya, ya + 5.0), 9.0)]                                    # lean-rod lug
        parts += [_cy(xp - 11.0, 0.0, *yy(ya + 5.0, yb), 6.4), _cy(11.0, 0.0, *yy(ya + 5.0, yb), 6.4)]       # cover screw posts
        body = _join(parts)
        for x, d1, d2 in ((xp, 11.15, 5.4), (0.0, 8.15, 4.4)):
            body = body - _cy(x, 0.0, *yy(ya - 0.1, ya + (4.0 if x == xp else 3.0)), d1)
            body = body - _cy(x, 0.0, *yy(ya - 0.1, yb + 0.1), d2)
        body = body - _cy(xp + W.LUG[0], W.LUG[1], *yy(ya - 0.1, ya + 5.1), 2.4)
        for x in (xp - 11.0, 11.0):
            body = body - _cy(x, 0.0, *yy(yb - 5.0, yb + 0.1), 2.2)
        return _to_print(body, s, ya)
    return MeshPart("w3_arm_left" if s > 0 else "w3_arm_right", fn, walls=False, supports=True)


def uplink(p, side):
    """Spindle link: 6 mm round bar between two 9 mm pin bosses."""
    s = side
    ya = W.UP_Y[0]
    yc = s * (ya + 3.0)
    def fn():
        xp = -W.ARM_L
        parts = [_tb((xp, yc, W.ZU), (0.0, yc, W.ZU), 3.0), _cy(xp, W.ZU, *sorted((s * ya, s * (ya + 6.0))), 9.0), _cy(0.0, W.ZU, *sorted((s * ya, s * (ya + 6.0))), 9.0)]
        body = _join(parts)
        for x in (xp, 0.0):
            body = body - _cy(x, W.ZU, *sorted((s * (ya - 0.1), s * (ya + 6.1))), p.pin_dia + p.clr_slide)
        return _to_print(body, s, ya)
    return MeshPart("w3_uplink_left" if s > 0 else "w3_uplink_right", fn, walls=False, supports=True)


def carrier(p, side):
    """Spindle post between the shaft hub and the upper-pin hub, a cantilever to the kingpin boss braced by an angled tube."""
    s = side
    ya, yb = W.CAR_Y
    yc = s * 0.5 * (ya + yb)
    yy = lambda a, b: tuple(sorted((s * a, s * b)))
    def fn():
        kp = W.KP_Y
        parts = [_cy(0.0, 0.0, *yy(ya, yb), 18.0), _cy(0.0, W.ZU, *yy(ya, yb), 11.0),
                 _tb((0.0, yc, 0.0), (0.0, yc, W.ZU), 4.5, 3.0),                                  # tapered post
                 _tb((0.0, yc, 19.0), (0.0, s * kp, 19.0), 3.0),                                  # cantilever to the kingpin
                 Manifold.cylinder(11.0, 5.5, 5.5, 32).translate((0.0, s * kp, 13.5)),            # kingpin boss
                 _tb((0.0, yc, 34.0), (0.0, s * (kp - 4.0), 20.5), 2.5)]                           # angled brace
        body = _join(parts)
        body = body - _cy(0.0, 0.0, *yy(ya - 0.1, yb + 0.1), 8.15)
        body = body - _cy(0.0, W.ZU, *yy(ya - 0.1, yb + 0.1), p.pin_dia + p.clr_slide)
        body = body - Manifold.cylinder(12.0, (W.KP_D + p.clr_press) / 2, (W.KP_D + p.clr_press) / 2, 32).translate((0.0, s * kp, 13.0))
        return _local_to_print(body, W.mats(s, ya))
    return MeshPart("w3_carrier_left" if s > 0 else "w3_carrier_right", fn, walls=False, supports=True)


def knuckle(p, side):
    """Round axle hub on the kingpin, steering arm as two angled tubes meeting at the ball-stud pad."""
    s = side
    y0, y1 = W.KN_Y[0] + 0.5, W.KN_Y[1]
    y_in = W.KP_Y + W.ARM_A[1]
    yy = lambda a, b: tuple(sorted((s * a, s * b)))
    def fn():
        kp = s * W.KP_Y
        z_stud = W.ARM_A[2]
        parts = [Manifold.cylinder(y1 - y0, 11.0, 11.0, 40).rotate((-90.0, 0.0, 0.0)).translate((-1.0, min(s * y0, s * y1), 1.0)),
                 _cy(W.ARM_A[0], z_stud, *yy(y_in - 3.0, y_in + 3.0), 10.0),                       # ball-stud pad
                 _tb((0.0, kp, -6.0), (W.ARM_A[0], s * y_in, z_stud), 3.0),
                 _tb((0.0, s * (W.KP_Y + 5.0), -6.0), (W.ARM_A[0], s * y_in, z_stud), 3.0),
                 _ball((0.0, kp, -6.0), 3.0)]
        body = _join(parts)
        body = body - _cy(0.0, 0.0, *yy(W.KN_Y[0], y1 + 0.1), p.axle_dia + p.clr_slide + 0.6)
        body = body - Manifold.cylinder(26.0, (W.KP_D + p.clr_slide) / 2, (W.KP_D + p.clr_slide) / 2, 32).translate((0.0, kp, -12.0))
        body = body - _cy(W.ARM_A[0], z_stud, *yy(y_in - 3.1, y_in + 3.0), p.ball_stud_dia + p.clr_press * 2)
        km = np.eye(4)
        if s > 0:
            km[:3, :3] = [[1, 0, 0], [0, 0, -1], [0, 1, 0]]; km[1, 3] = W.KN_Y[1]
        else:
            km[:3, :3] = [[1, 0, 0], [0, 0, 1], [0, -1, 0]]; km[1, 3] = -W.KN_Y[1]
        return _local_to_print(body, km)
    return MeshPart("w3_knuckle_left" if s > 0 else "w3_knuckle_right", fn, walls=False, supports=True)
