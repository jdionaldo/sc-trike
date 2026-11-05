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


def static_drivetrain():
    """Parts that do not move with lean or steer."""
    it = []
    # centre diff: carrier, ring gear and the motor pinion
    it.append(("mock_cdiff_carrier", _cx(-181.0, SY, 0.0, 17.5, 36.0), "bought"))
    it.append(("mock_cdiff_ring", _cx(-196.0, SY, 0.0, 19.0, 6.0), "bought"))
    it.append(("mock_motor_pinion", _cx(-193.0, SY, 24.0, 6.4, 8.0), "bought"))
    it.append(("mock_front_out", _cx(-160.5, SY, 0.0, 2.5, 9.0), "bought"))
    # front diff carrier (the ring is in the layout blocks) and the bevel pinion on the front pinion shaft
    it.append(("mock_fdiff_carrier", _cy(D.XD, 0.0, 0.0, 16.0, 34.0), "bought"))
    it.append(("mock_bevel_pinion_f", _cx(-119.0, SY, 0.0, 6.5, 8.0), "bought"))
    it.append(("mock_bevel_pinion_r", _cx(pv(-257.0), SY, 0.0, 6.5, 8.0), "bought"))
    # receiver in the nose bay beside the battery
    it.append(("mock_receiver", LY.box((-75.0, -51.0), (12.0, 27.0), (-20.0, -11.0)), "bought"))
    # rear wheel: tire ring, rim barrel, outer disc, hub and 8 mm axle; one-sided arm with the belt on the left
    ax, az = D.RAXLE
    it.append(("mock_rear_axle", _cy(ax, 26.0, az, 4.0, 100.0), "bought"))
    ring = _cy(ax, 0.0, az, 56.0, 62.0)
    hole = _cy(ax, 0.0, az, 38.0, 64.0)
    it.append(("mock_rear_tire_ring", MB.to_trimesh(MB.man(ring) - MB.man(hole)), "bought"))
    it.append(("mock_rear_rim", MB.to_trimesh(MB.man(_cy(ax, 0.0, az, 38.0, 62.0)) - MB.man(_cy(ax, 0.0, az, 35.0, 64.0))), "bought"))
    it.append(("mock_rear_rim_disc", _cy(ax, -28.5, az, 36.0, 4.0), "bought"))
    it.append(("mock_rear_hub", _cy(ax, -22.0, az, 8.0, 12.0), "bought"))
    it.append(("mock_rear_pulley_pivot", _cy(D.XR, 55.6, 0.0, 6.1, 3.5), "bought"))
    it.append(("mock_rear_pulley_axle", _cy(ax, 55.6, az, 6.8, 3.5), "bought"))
    it.append(("mock_rear_belt", belt((D.XR, 0.0), 6.1, (ax, az), 6.8, 54.1, 57.1), "bought"))
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
