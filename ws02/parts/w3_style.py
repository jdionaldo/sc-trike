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
    """Round to what the STL holds, drop zero-volume slivers and degenerate faces (unless that opens a hole), merge."""
    t.vertices = np.asarray(t.vertices, np.float32).astype(np.float64)
    t.merge_vertices()
    comps = t.split(only_watertight=False)
    if len(comps) > 1:
        keep = [c for c in comps if abs(c.volume) > 1.0]
        if keep:
            t = trimesh.util.concatenate(keep)
            t.merge_vertices()
    was = t.is_watertight
    u = t.copy()
    u.update_faces(u.nondegenerate_faces())
    u.remove_unreferenced_vertices()
    u.merge_vertices()
    return u if (u.is_watertight or not was) else t


def _to_print(m, side, y0):
    t = trimesh.Trimesh(*[np.asarray(a) for a in (np.asarray(m.to_mesh().vert_properties)[:, :3], np.asarray(m.to_mesh().tri_verts))])
    inv = np.linalg.inv(W.mats(side, y0))
    t.apply_transform(inv)
    return _clean(t)


def _cz(u, v, z0, z1, d):
    return Manifold.cylinder(z1 - z0, d / 2, d / 2, 48).translate((u, v, z0))


def _local_to_print(m, mat):
    t = MB.to_trimesh(m)
    t.apply_transform(np.linalg.inv(mat))
    return _clean(t)


# ---- tubular trellis redesign: swing arm as a 3D box truss, spindle upper link, trellis carrier and knuckle ----
def _tb(a, b, r, r2=None, caps=True):
    """Tube (or cone from radius r to r2) between two assembly-frame points, with round (spherical) ends so no joint is ever open."""
    a, b = np.array(a, float), np.array(b, float)
    d = b - a
    L = float(np.linalg.norm(d))
    T = trimesh.geometry.align_vectors([0.0, 0.0, 1.0], d / L)
    mat = np.array(T[:3, :4])
    mat[:, 3] = a
    r2_ = r if r2 is None else r2
    m = Manifold.cylinder(L, r, r2_, 40).transform(mat)
    if caps:
        m = m + Manifold.sphere(r, 36).translate(tuple(a)) + Manifold.sphere(r2_, 36).translate(tuple(b))
    return m


def _ball(p, r):
    return Manifold.sphere(r, 36).translate(tuple(p))


def _join(ms):
    out = ms[0]
    for m in ms[1:]:
        out = out + m
    return out


REAR_W = (2.4, 24.0)          # rear arm plane centres (w)
RT, RO, RW = 2.4, 4.5, 3.5    # inner rails / outer rails (overbuilt, outside the belt in y) / outer web             # rail radii (inner plane / outer plane)
YO = 15.5                     # outer plane offset from the arm's inner face (belt at +6..+9; the fat outer rails start at +11)
# rail nodes (x, z); the lower rails stay above z = -11.4 so the tie rod passes under the arm at every lean angle
ARM_NODES = {"L0": (-100.0, -9.0), "L1": (-60.0, -9.0), "L2": (0.0, -9.0),
             "U0": (-100.0, 10.5), "U1": (-76.0, 17.5), "U2": (-38.0, 11.5), "U3": (0.0, 9.4)}
ARM_RAILS = [("L0", "L1"), ("L1", "L2"), ("U0", "U1"), ("U1", "U2"), ("U2", "U3")]
ARM_WEB = [("L0", "U1"), ("U1", "L1"), ("L1", "U2"), ("U2", "L2")]          # zigzag in both side planes (the belt is between them)
TIE_R = {"U0": 2.8, "U3": 2.8, "L0": 1.6, "L2": 2.4}              # hub-end ties across the belt gap (limited by the belt hull)
LAT_TOP, LAT_BOT = 2.7, 1.6                                      # X lattice radii, top / bottom faces


# outer-plane rail centres (x, z): fat tubes, bottoms held at z -11.3 so the tie rod still passes under at every lean angle
ARM_OUTER = {"L0": (-100.0, -6.8), "L1": (-60.0, -6.8), "L2": (0.0, -6.8), "U0": (-100.0, 10.0), "U1": (-76.0, 15.5), "U2": (-38.0, 10.0), "U3": (0.0, 7.5)}


def arm(p, side):
    """Overbuilt box-truss swing arm, open: slim inner plane (rails + zigzag), the belt, then a fat outer plane (9 mm rails, 7 mm zigzag),
    X lattices in the top and bottom faces, hubs on both planes (bearing seats on the inner face of the inner hub and the outer face of
    the outer hub); lug for the lean rod on the inner plane."""
    s = side
    ya, yb = W.ARM_Y
    yi, yo = s * (ya + 2.5), s * (ya + YO)                # plane centres: 67.0 and 80.0
    yy = lambda a, b: (s * a, s * b)
    ho = ya + 20.0                                         # outer face of the outer hubs
    def fn():
        P = lambda k, y: (ARM_NODES[k][0], y, ARM_NODES[k][1])
        Q = lambda k, y: (ARM_OUTER[k][0], y, ARM_OUTER[k][1])
        parts = []
        for a, b in ARM_RAILS + ARM_WEB:
            parts.append(_tb(P(a, yi), P(b, yi), RT))
        for k in ARM_NODES:
            parts.append(_ball(P(k, yi), RT))
        for a, b in ARM_RAILS:
            parts.append(_tb(Q(a, yo), Q(b, yo), RO))
        for a, b in ARM_WEB:
            parts.append(_tb(Q(a, yo), Q(b, yo), RW))
        for k in ARM_NODES:
            parts.append(_ball(Q(k, yo), RO if k in ("L0", "L1", "L2", "U0", "U1", "U2", "U3") else RW))
        for rails, r in (([("U0", "U1"), ("U1", "U2"), ("U2", "U3")], LAT_TOP), ([("L0", "L1"), ("L1", "L2")], LAT_BOT)):   # lateral X lattices
            for a, b in rails:
                parts += [_tb(P(a, yi), P(b, yo), r), _tb(P(b, yi), P(a, yo), r)]
        for k in ("U0", "L0", "U3", "L2"):                                       # ties at the hub ends
            parts.append(_tb(P(k, yi), P(k, yo), TIE_R[k]))
        xp = -W.ARM_L
        parts += [_cy(xp, 0.0, *yy(ya, ya + 5.5), 20.0), _cy(0.0, 0.0, *yy(ya, ya + 5.5), 18.0)]                    # inner hubs
        parts += [_cy(xp, 0.0, *yy(ya + 11.0, ho), 22.0), _cy(0.0, 0.0, *yy(ya + 11.0, ho), 20.0)]                  # outer hubs (r <= 11: rod clearance)
        parts += [_cy(W.LUG[0] + xp, W.LUG[1], *yy(ya, ya + 5.0), 9.0)]                                             # lean-rod lug
        body = _join(parts)
        for x, d1, d2 in ((xp, 11.15, 5.4), (0.0, 8.15, 4.4)):
            dep = 4.0 if x == xp else 3.0
            body = body - _cy(x, 0.0, *yy(ya - 0.1, ya + dep), d1)                                                  # inner bearing seat
            body = body - _cy(x, 0.0, *yy(ho + 0.1 - dep, ho + 0.1), d1)                                            # outer bearing seat, facing out
            body = body - _cy(x, 0.0, *yy(ya - 0.1, ho + 0.1), d2)
        body = body - _cy(xp + W.LUG[0], W.LUG[1], *yy(ya - 0.1, ya + 5.1), 2.4)
        for x in POD_SCREWS:                                                                    # pilots for the headlight-pod screws
            body = body - Manifold.cylinder(9.0, 0.9, 0.9, 24).translate((x, s * (ya + YO), _rail_top(x) - 8.0))
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


CAR_R0, CAR_R1, CAR_RC, CAR_RB = 6.0, 4.5, 4.5, 3.5          # carrier: post taper, kingpin cantilever, brace radii


def carrier(p, side):
    """Spindle post between the shaft hub and the upper-pin hub, a cantilever to the kingpin boss braced by an angled tube."""
    s = side
    ya, yb = W.CAR_Y
    yc = s * 0.5 * (ya + yb)
    yy = lambda a, b: tuple(sorted((s * a, s * b)))
    def fn():
        kp = W.KP_Y
        parts = [_cy(0.0, 0.0, *yy(ya, yb), 18.0), _cy(0.0, W.ZU, *yy(ya, yb), 11.0),
                 _tb((0.0, yc, 0.0), (0.0, yc, W.ZU), CAR_R0, CAR_R1),                          # tapered post
                 _tb((0.0, yc, 19.0), (0.0, s * kp, 19.0), CAR_RC),                              # cantilever to the kingpin
                 Manifold.cylinder(11.0, 5.5, 5.5, 32).translate((0.0, s * kp, 13.5)),            # kingpin boss
                 _tb((0.0, yc, 34.0), (0.0, s * (kp - 4.0), 20.5), CAR_RB)]                      # angled brace
        body = _join(parts)
        body = body - _cy(0.0, 0.0, *yy(ya - 6.0, yb + 6.0), 8.15)                       # longer than the hub: the rounded tube ends overhang it
        body = body - _cy(0.0, W.ZU, *yy(ya - 6.0, yb + 6.0), p.pin_dia + p.clr_slide)
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
                 _tb((-7.0, kp, -5.0), (W.ARM_A[0], s * y_in, z_stud), 3.0),                      # V of two tubes: the tie-rod pull (along x)
                 _tb((7.0, kp, -5.0), (W.ARM_A[0], s * y_in, z_stud), 3.0),                       # is axial in them, not bending
                 _ball((-7.0, kp, -5.0), 3.0), _ball((7.0, kp, -5.0), 3.0)]
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


def rear_arm(p):
    """Rear swing arm as a wide box truss, open: two side planes (rails + zigzag), the belt between them, X lattices in the top and
    bottom faces, hubs on both planes.  Print frame: u along the arm (pivot 0, axle L), v across it, w = y - 46 (inner face on the bed)."""
    L = math.hypot(D.XR - D.RAXLE[0], D.RAXLE[1])
    wi, wo = REAR_W                                            # inner / outer plane centres (belt at w 8.1..11.1)
    V, VL = 9.5, 12.5                                          # rail offset; lattice offset (clear of the belt hull, r 8 at the axle)
    from parts import w3_shock as SK
    us = SK.caret_stations(L)                                  # stations: pivot, half way to the apex, apex (30 %), 65 %, axle
    rv = lambda sgn, u: sgn * V + (SK.caret_rise(u, L) if sgn > 0 else 0.0)        # rail height: the top rail follows the caret, the bottom rail stays straight (the belt runs between)
    lv = lambda sgn, u: sgn * VL + (SK.caret_rise(u, L) if sgn > 0 else 0.0)
    def fn():
        parts = []
        for w, r, rw in ((wi, 2.4, 2.4), (wo, 4.5, 3.5)):
            for sgn in (1, -1):
                for a, b in zip(us, us[1:]):
                    parts.append(_tb((a, rv(sgn, a), w), (b, rv(sgn, b), w), r))
                for u in us:
                    parts.append(_ball((u, rv(sgn, u), w), r))
            for i, (a, b) in enumerate(zip(us, us[1:])):         # zigzag between the rails
                v0, v1 = (rv(1, a), rv(-1, b)) if i % 2 == 0 else (rv(-1, a), rv(1, b))
                parts.append(_tb((a, v0, w), (b, v1, w), rw))
        for i, (a, b) in enumerate(zip(us, us[1:])):             # lateral X lattices in the top and bottom faces
            for sgn, r in ((1, 3.0), (-1, 3.0)):
                parts += [_tb((a, lv(sgn, a), wi), (b, lv(sgn, b), wo), r), _tb((b, lv(sgn, b), wi), (a, lv(sgn, a), wo), r)]
        for u in (0.0, L):
            for sgn in (1, -1):
                parts.append(_tb((u, sgn * VL, wi), (u, sgn * VL, wo), 3.2))
        for u in (0.0, L):                                                      # second, wider tie pair at each end (carries the wheel's twist)
            for sgn in (1, -1):
                for w in (wi, wo):
                    parts += [_tb((u, sgn * V, w), (u, sgn * 16.0, w), 4.0), _ball((u, sgn * 16.0, w), 4.0)]
                parts.append(_tb((u, sgn * 16.0, wi), (u, sgn * 16.0, wo), 4.0))
        parts += [_cz(0.0, 0.0, 0.0, 7.6, 20.0), _cz(L, 0.0, 0.0, 7.6, 26.0), _cz(0.0, 0.0, wo - 4.4, wo + 4.7, 24.0), _cz(L, 0.0, wo - 4.4, wo + 4.7, 28.0)]    # hubs
        # coilover hoop: two legs from the outer plane's top rail up behind the tyre, a cross tube over the tyre to the lower bolt lug
        sh = lambda m_: m_.translate((0.0, 0.0, SK.WOFF))                         # the whole arm moves up the print frame so the lug boss is the lowest layer
        H = SK.hoop_arm_points()
        A1, A2, B, C = (np.array(H[k]) for k in ("A1", "A2", "B", "C"))
        w1, w2 = SK.PLATE_Y[0] - SK.BOSS_Y[0], SK.PLATE_Y[1] - SK.BOSS_Y[0]
        hoop = [_tb(A1, B, SK.LEG_R), _tb(A2, B, SK.LEG_R), _ball(A1, SK.LEG_R), _ball(A2, SK.LEG_R), _ball(B, SK.HOOP_R), _tb(B, C, SK.HOOP_R, caps=False),
                _cz(B[0], B[1], w1, w2, 2 * SK.HOOP_R), _cz(B[0], B[1], 0.0, w1 + 0.1, 2 * SK.BOSS_R)]
        body = sh(_join(parts)) + _join(hoop)
        body = body - _cz(B[0], B[1], -1.0, w2 + 1.0, SK.PIN_D)
        body = body - sh(_cz(0.0, 0.0, -0.1, D.SEAT_D, D.SEAT)) - sh(_cz(0.0, 0.0, -0.1, wo + 4.9, D.BORE))
        body = body - sh(_cz(L, 0.0, -0.1, 5.1, 16.15)) - sh(_cz(L, 0.0, -0.1, wo + 4.9, 8.4))
        body = body - sh(_cz(0.0, 0.0, wo + 4.8 - D.SEAT_D, wo + 4.8, D.SEAT)) - sh(_cz(L, 0.0, wo + 4.8 - 5.1, wo + 4.8, 16.15))                                       # outer seats
        return _clean(MB.to_trimesh(body))
    return MeshPart("w3_rear_arm", fn, walls=False, supports=True)


# ---- headlight pod: sits on the top of each front arm's outer rail (arm-local frame), screwed down into the rail ----
def _rail_top(x):
    (x0, z0), (x1, z1) = ARM_OUTER["U2"], ARM_OUTER["U3"]
    return z0 + (z1 - z0) * (x - x0) / (x1 - x0) + RO


POD_X = (-40.0, -13.0)
POD_Z0 = _rail_top(POD_X[1]) + 0.1                              # lowest point of the pod bottom: the STL is shifted so this sits on the bed
POD_SCREWS = (-35.0, -20.0)


def pod(p):
    """Angular headlight pod for the top of a front arm: wedge housing, 7 mm lens recess on the front face, 5 mm LED hole, two screws
    down into the rail.  Symmetric in y (same part both sides); built in arm-local coordinates, y centred, z shifted so the bottom is on the bed."""
    def fn():
        x0, x1 = POD_X
        zb0, zb1 = _rail_top(x0) + 0.1, _rail_top(x1) + 0.1
        poly = [(x0, zb0), (x1, zb1), (x1, zb1 + 9.0), (x1 - 4.0, zb1 + 13.0), (x0, zb0 + 12.5)]
        body = MB.prism_xz(poly, -4.0, 4.0)
        lens = Manifold.cylinder(1.6, 3.5, 3.5, 40).rotate((0.0, 90.0, 0.0)).translate((x1 - 1.5, 0.0, zb1 + 5.5))
        led = Manifold.cylinder(14.0, 2.5, 2.5, 32).rotate((0.0, 90.0, 0.0)).translate((x1 - 14.0, 0.0, zb1 + 5.5))
        body = body - lens - led
        for x in POD_SCREWS:
            body = body - Manifold.cylinder(30.0, 1.1, 1.1, 24).translate((x, 0.0, zb0 - 2.0))
        m = MB.to_trimesh(body)
        m.apply_translation((0.0, 0.0, -POD_Z0))
        return _clean(m)
    return MeshPart("w3_pod", fn, walls=False, supports=True)
