"""WS-03 mock drivetrain and wheels: simple solids for every bought drivetrain part, placed where the real parts go.

Front pulleys 20T (pivot) and 16T (tip), GT2 3 mm belts in the arm cavities; centre diff with ring gear and 15T motor pinion; bevel pinions;
dogbone joints on the kingpin axes; wheels as tire ring, rim barrel, outer disc and hub; rear belt 20T to 22T on the rear arm.
"""
import math
import numpy as np
import trimesh
from manifold3d import Manifold

import front3wd as F
import layout3wd as LY
from w3_stretch import back, pv
import mono_build as MB
import w3_scene as S
import w3_stock as K
from parts import w3_drive as D, w3_front as W

SY = D.SY
BELT_T = 1.2


def belt(p0, r0, p1, r1, y0, y1):
    """GT2 belt around two pulleys at (x, z) p0 and p1 (pitch radii r0, r1), occupying |y| y0..y1. Returns a trimesh."""
    from shapely.geometry import Point
    o = Point(p0).buffer(r0 + BELT_T, 48).union(Point(p1).buffer(r1 + BELT_T, 48)).convex_hull
    i = Point(p0).buffer(r0, 48).union(Point(p1).buffer(r1, 48)).convex_hull
    oo = list(o.exterior.coords)[:-1]
    ii = list(i.exterior.coords)[:-1]
    m = MB.prism_xz(oo, y0, y1) - MB.prism_xz(ii, y0 - 1, y1 + 1)
    return MB.to_trimesh(m)


def _cx(x, y, z, r, L):
    return LY.cyl((x, y, z), r, L, "x")


def _cy(x, y, z, r, L):
    return LY.cyl((x, y, z), r, L, "y")


def _ring(xc, y, z, ro, ri, L):
    """Annulus along x centred on xc."""
    return MB.to_trimesh(MB.man(_cx(xc, y, z, ro, L)) - MB.man(_cx(xc, y, z, ri, L + 2.0)))


def _ringy(x, yc, z, ro, ri, L):
    return MB.to_trimesh(MB.man(_cy(x, yc, z, ro, L)) - MB.man(_cy(x, yc, z, ri, L + 2.0)))


def drive_mocks():
    """Stock drivetrain parts (see WS03_DRIVETRAIN.md): carriers, rings, pinions, spur gears, locker, bearings."""
    it = []
    xc = 0.5 * (K.C_FACE_A + K.C_FACE_F)
    it.append(("mock_cdiff_carrier", _cx(xc, SY, 0.0, K.CARR_D / 2, K.CARR_L), "bought"))                          # AR45 6-bolt carrier with AXI232002 locker
    it.append(("mock_cdiff_ring", _ring(0.5 * sum(K.C_RING), SY, 0.0, K.od(K.CRING_T) / 2, K.SPUR_BORE[40] / 2, K.SPUR_W), "bought"))   # AXI232034 40T spur
    for tag, t in (("P1", K.PINION_T), ("Pa", K.IDLER_T), ("Pb", K.IDLER_T)):
        y, z = K.XO[tag]
        bore = K.SPUR_BORE[t]
        it.append((f"mock_xover_{'pinion' if tag == 'P1' else 'idler_' + tag}", _ring(0.5 * sum(K.GEAR_X), y, z, K.od(t) / 2, bore / 2, K.SPUR_W), "bought"))
    for tag in ("Pa", "Pb"):                                                                                  # idler pins 5 x 20, bearing to bearing
        y, z = K.XO[tag]
        it.append((f"mock_xover_pin_{tag}", _cx(0.5 * (K.X_BRG_A[0] + K.X_BRG_F[1]), y, z, 2.5, K.X_BRG_F[1] - K.X_BRG_A[0] + 1.0), "bought"))
    it.append(("mock_fdiff_carrier", _cy(D.XD, 0.5 * sum(K.FCARR_Y), 0.0, K.CARR_D / 2, K.FCARR_Y[1] - K.FCARR_Y[0]), "bought"))
    it.append(("mock_bevel_pinion_f", _ring(0.5 * sum(K.F_PIN_X), SY, 0.0, K.PIN_HEAD_D / 2, 2.5, K.PIN_LEN), "bought"))
    it.append(("mock_bevel_pinion_r", _ring(0.5 * sum(K.R_PIN_X), SY, 0.0, K.PIN_HEAD_D / 2, 2.5, K.PIN_LEN), "bought"))
    # bearings 5 x 11 x 4
    for b in K.F_BRG + [K.C_BRG_A, K.C_BRG_F] + K.R_BRG + [(K.PILLOW_X - 2.0, K.PILLOW_X + 2.0)]:
        it.append(("mock_bearing_x", _ring(0.5 * sum(b), SY, 0.0, K.BRG_OD / 2, 2.5, K.BRG_W), "bought"))
    for tag in ("P1", "Pa", "Pb"):
        y, z = K.XO[tag]
        for b in (K.X_BRG_A, K.X_BRG_F):
            it.append(("mock_bearing_x", _ring(0.5 * sum(b), y, z, K.BRG_OD / 2, 2.5, K.BRG_W), "bought"))
    for yb in (-24.05, 32.05):
        it.append(("mock_bearing_fy", _ringy(D.XD, yb, 0.0, K.BRG_OD / 2, 2.5, K.BRG_W), "bought"))
    for yb in (10.0, 36.1):
        it.append(("mock_bearing_ry", _ringy(K.XR, yb, 0.0, K.BRG_OD / 2, 2.5, K.BRG_W), "bought"))
    # bevel rings sit in the layout blocks (b_front_ring, b_rear_ring)
    return it


def static_drivetrain():
    """Parts that do not move with lean or steer."""
    it = []
    it += drive_mocks()
    # receiver in the nose bay beside the battery
    it.append(("mock_receiver", LY.box((-56.0, -32.0), (12.0, 27.0), (-14.0, -5.0)), "bought"))
    # rear wheel: tire ring, rim barrel, outer disc, hub and 8 mm axle; one-sided arm with the belt on the left
    ax, az = D.RAXLE
    it.append(("mock_rear_axle", _cy(ax, 26.0, az, 4.0, 100.0), "bought"))
    ring = _cy(ax, 0.0, az, 56.0, 62.0)
    hole = _cy(ax, 0.0, az, 38.0, 64.0)
    it.append(("mock_rear_tire_ring", MB.to_trimesh(MB.man(ring) - MB.man(hole)), "bought"))
    it.append(("mock_rear_rim", MB.to_trimesh(MB.man(_cy(ax, 0.0, az, 38.0, 62.0)) - MB.man(_cy(ax, 0.0, az, 35.0, 64.0))), "bought"))
    it.append(("mock_rear_rim_disc", _cy(ax, -28.5, az, 36.0, 4.0), "bought"))
    it.append(("mock_rear_hub", _cy(ax, -22.0, az, 8.0, 12.0), "bought"))
    RP = {20: 6.1, 22: 6.8}
    r_p, r_a = RP[K.REAR_BELT[0]], RP[K.REAR_BELT[1]]
    it.append(("mock_rear_pulley_pivot", _cy(D.XR, 55.6, 0.0, r_p, 3.5), "bought"))
    it.append(("mock_rear_pulley_axle", _cy(ax, 55.6, az, r_a, 3.5), "bought"))
    it.append(("mock_rear_belt", belt((D.XR, 0.0), r_p, (ax, az), r_a, 54.1, 57.1), "bought"))
    return it


def moving(phi_deg, steer=None):
    """Front belts, pulleys, dogbone joints and wheels for a lean angle."""
    phi = math.radians(phi_deg)
    th = dict(zip((1, -1), F.arm_angles(phi)))
    delta = math.radians(max(-S.STEER_MAX, min(S.STEER_MAX, phi_deg * S.STEER_MAX / S.LEAN_MAX))) if steer is None else math.radians(steer)
    it = []
    xp = -W.ARM_L
    y_pulley = 0.5 * (63.5 + W.YS + W.ARM_Y[1])                      # centre of the belt cavity
    for s in (1, -1):
        t = th[s]
        arm = S.Ry(t, F.P)
        kx, kz = F.P[0] + F.LA * math.cos(t), F.LA * math.sin(t)
        # belt pulleys and belt in the arm cavity (they ride on the arm)
        pivot = _cy(xp, s * y_pulley, 0.0, 6.1, 3.5)
        tip = _cy(0.0, s * y_pulley, 0.0, 5.0, 3.5)
        tip.apply_transform(arm)
        b = belt((xp, 0.0), 6.1, (0.0, 0.0), 5.0, y_pulley - 1.5, y_pulley + 1.5) if s > 0 else belt((xp, 0.0), 6.1, (0.0, 0.0), 5.0, -(y_pulley + 1.5), -(y_pulley - 1.5))
        b.apply_transform(arm)
        it += [(f"mock_fpulley_pivot_{s}", pivot, "bought"), (f"mock_fpulley_tip_{s}", tip, "bought"), (f"mock_fbelt_{s}", b, "bought")]
        # wheel: tire ring, rim barrel, outer disc, hub, axle; steered about the kingpin
        steer_m = S.T(kx, 0, kz) @ S.Rz(delta, (0.0, s * W.KP_Y))
        yc_w = s * F.T
        ring = MB.to_trimesh(MB.man(_cy(0.0, yc_w, 0.0, F.R, F.W)) - MB.man(_cy(0.0, yc_w, 0.0, F.R - 13.5, F.W + 2)))
        rim = MB.to_trimesh(MB.man(_cy(0.0, yc_w, 0.0, F.R - 13.5, F.W)) - MB.man(_cy(0.0, yc_w, 0.0, F.R - 16.0, F.W + 2)))
        disc = _cy(0.0, yc_w + s * (F.W / 2 - 1.5), 0.0, F.R - 14.0, 2.5)
        hub = _cy(0.0, yc_w + s * (F.W / 2 + 0.5 - 3.0), 0.0, 6.0, 8.0)
        axle = _cy(0.0, s * (W.KP_Y + 12.0), 0.0, 2.0, 30.0)
        joint = LY.trimesh.creation.icosphere(subdivisions=2, radius=4.5)
        joint.apply_translation((0.0, s * W.KP_Y, 0.0))
        for n, m_ in (("tire", ring), ("rim", rim), ("rimdisc", disc), ("hub", hub), ("axle", axle), ("joint", joint)):
            m_.apply_transform(steer_m)
            it.append((f"mock_{n}_{s}", m_, "bought"))
    return it


def mock(phi_deg=0.0, steer=None):
    return static_drivetrain() + moving(phi_deg, steer)
