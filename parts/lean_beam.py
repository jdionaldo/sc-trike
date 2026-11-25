"""Passive lean (November 21): the two front shocks no longer end on the frame. Their upper eyes sit on the two ends of one balance beam that turns
about a vertical bolt under a bridge plate between the cage's lower side rails.

- Both wheels up (bump, braking): both shocks push the beam the same way, it cannot turn, the springs work.
- One wheel up, the other down (lean): the beam turns, no spring is compressed, the body leans freely until the beam meets a stop.

Chassis reference frame (world = ref + (0, CHASSIS_Y, CHASSIS_Z)). The beam lies just under the rails (rail axis ref z 100.3, tube radius 5).
"""
import math
import cadquery as cq
from parts import shock_mount as sm
from parts.params import DECK_SLOPE

# The whole lean assembly (beam, bridge, bolt, stops, springs) is tilted about the lateral axis through the pivot to the deck slope, rising to the rear
# (user request: parallel to the deck). The shock clevis bases stay where base_up puts them: the beam is moved so its clevis base plane meets them.
TILT_DEG = math.degrees(math.atan(DECK_SLOPE))

END_X = 56.0                 # upper clevis base, x (outboard of the rail, inboard of the upper link at 64.5)
BEAM_Z0, BEAM_Z1 = 82.0, 93.5          # beam bottom / top (rail underside 95.3)
BEAM_ZC = (BEAM_Z0 + BEAM_Z1) / 2
BACK = 6.5                   # the beam's centre line lies this far behind the clevis bases
HALF_MID, HALF_END = 17.0, 6.5         # half width (y) at the pivot and at the ends
PIVOT_D = 4.3                # M4 shoulder bolt
BRIDGE_Z0, BRIDGE_T = 95.5, 8.0
BRIDGE_HALF_Y = 21.0
RAIL_X = 45.0
STOP_X, STOP_DEG = 30.0, 3.2           # stop pegs under the bridge: the beam meets them at this angle
STOP_S = 6.0
# Centring: two bought compression springs (5 mm OD, 10 mm free length, about 2 N/mm) behind the beam at x +-SPRING_X, each in a pocket of a post under
# the bridge, pushing on a flat pad of the beam. At rest both are 1.4 mm preloaded and balance; when the beam turns, one is compressed further.
SPRING_X, SPRING_OD, SPRING_FREE = 40.0, 5.0, 10.0
PAD_Y = 9.0                  # flat spring pad on the beam's rear side, this far behind the beam's centre line
SPRING_GAP = 2.6             # post face to pad at rest (the pad moves 2.2 mm at the stops)
POCKET = 6.0                 # spring pocket depth in the post
SHOCK_D = sm.EYE_L + sm.EYE_UP_OFF + 5.17        # base-to-base distance (lower eye offset 5.17 as before)


def base_up(sx, base_low):
    """Upper clevis base on the beam end for the given lower base: same base distance as before, at the beam's mid height."""
    dx, dz = END_X - abs(base_low[0]), BEAM_ZC - base_low[2]
    dy = math.sqrt(SHOCK_D ** 2 - dx ** 2 - dz ** 2)
    return (sx * END_X, base_low[1] + dy, BEAM_ZC)


def pivot(bases):
    """Pivot point (x 0) from the two upper bases {sx: (base_low, base_up)}."""
    y = bases[1][1][1] + BACK
    return (0.0, y, BEAM_ZC)


def _place(shape, bases):
    """Tilt a part built level about the x axis through the level pivot, then shift it so the level clevis base point lands on the real one."""
    p = pivot(bases)
    flat_bu = cq.Vector(0.0, p[1] - BACK, BEAM_ZC)
    r = flat_bu - cq.Vector(*p)
    a = math.radians(TILT_DEG)
    rot = cq.Vector(0.0, r.y * math.cos(a) - r.z * math.sin(a), r.y * math.sin(a) + r.z * math.cos(a))
    d = cq.Vector(*p) + rot
    want = cq.Vector(0.0, bases[1][1][1], BEAM_ZC)
    return shape.rotate(cq.Vector(*p), cq.Vector(p[0] + 1.0, p[1], p[2]), TILT_DEG).translate(want - d)


def beam(bases, eye_up):
    """The balance beam with a clevis on each end (one printed part, flat on the bed)."""
    p = pivot(bases)
    xe = END_X + sm.GAP / 2 + sm.PLATE_T + 0.5
    pts = [(-xe, -HALF_END), (-xe + 14, -HALF_END), (0, -HALF_MID), (xe - 14, -HALF_END), (xe, -HALF_END),
           (xe, HALF_END), (xe - 14, HALF_END), (0, HALF_MID), (-xe + 14, HALF_END), (-xe, HALF_END)]
    b = cq.Workplane('XY').workplane(offset=BEAM_Z0).polyline([(x, p[1] + y) for x, y in pts]).close().extrude(BEAM_Z1 - BEAM_Z0).val()
    for sx in (1, -1):       # flat pads for the centring springs
        b = b.fuse(cq.Solid.makeBox(8.0, PAD_Y - 3.0, BEAM_Z1 - BEAM_Z0, cq.Vector(sx * SPRING_X - 4.0, p[1] + 3.0, BEAM_Z0)))
    b = b.clean()
    b = b.cut(cq.Solid.makeCylinder(PIVOT_D / 2, 40, cq.Vector(0, p[1], BEAM_Z0 - 10), cq.Vector(0, 0, 1)))
    b = _place(b, bases)
    for sx in (1, -1):
        bl, bu = bases[sx]
        # nothing of the beam in front of the clevis base plane (the shock's space)
        front = cq.Solid.makeBox(60.0, 60.0, 60.0, cq.Vector(-30.0, -30.0, 0.0)).moved(sm._loc(bu, bl))
        b = b.cut(front)
        b = b.fuse(sm.clevis(bu, bl, eye_up)).clean()
    b = max(b.Solids(), key=lambda q: q.Volume())
    assert b.isValid(), 'lean beam is not valid'
    return b


def half_width(x):
    xe = END_X + sm.GAP / 2 + sm.PLATE_T + 0.5
    return HALF_MID - (HALF_MID - HALF_END) * min(1.0, abs(x) / (xe - 14))


def bridge(bases):
    """Bridge plate between the cage's lower side rails with the pivot boss and four stop pegs under it (fused into the cage)."""
    p = pivot(bases)
    pl = cq.Solid.makeBox(2 * RAIL_X, 2 * BRIDGE_HALF_Y, BRIDGE_T, cq.Vector(-RAIL_X, p[1] - BRIDGE_HALF_Y, BRIDGE_Z0))
    pl = pl.fuse(cq.Solid.makeCylinder(8.0, BRIDGE_Z0 - BEAM_Z1 - 0.3, cq.Vector(0, p[1], BEAM_Z1 + 0.3), cq.Vector(0, 0, 1)))      # thrust boss
    off = half_width(STOP_X) + STOP_X * math.tan(math.radians(STOP_DEG))
    for sx in (1, -1):
        for sy in (1, -1):
            y0 = p[1] + sy * off if sy > 0 else p[1] + sy * off - STOP_S
            pl = pl.fuse(cq.Solid.makeBox(STOP_S, STOP_S, BRIDGE_Z0 - BEAM_ZC + 2.0, cq.Vector(sx * STOP_X - STOP_S / 2, y0, BEAM_ZC - 2.0)))
    for sx in (1, -1):       # spring posts with a pocket facing the beam
        y0 = p[1] + PAD_Y + SPRING_GAP
        post = cq.Solid.makeBox(9.0, 9.0, BRIDGE_Z0 - (BEAM_ZC - 4.5) + 1.0, cq.Vector(sx * SPRING_X - 4.5, y0, BEAM_ZC - 4.5))
        post = post.cut(cq.Solid.makeCylinder(SPRING_OD / 2 + 0.2, POCKET + 1.0, cq.Vector(sx * SPRING_X, y0 - 1.0, BEAM_ZC), cq.Vector(0, 1, 0)))
        pl = pl.fuse(post)
    pl = pl.clean().cut(cq.Solid.makeCylinder(PIVOT_D / 2, 60, cq.Vector(0, p[1], BEAM_Z0 - 10), cq.Vector(0, 0, 1)))
    return _place(pl, bases)


def pivot_bolt(bases):
    """M4 x 35 bolt (head on the bridge) with a lock nut under the beam."""
    p = pivot(bases)
    bolt = cq.Solid.makeCylinder(2.0, BRIDGE_Z0 + BRIDGE_T - BEAM_Z0 + 5.0, cq.Vector(0, p[1], BEAM_Z0 - 5.0), cq.Vector(0, 0, 1))
    bolt = bolt.fuse(cq.Solid.makeCylinder(3.5, 2.8, cq.Vector(0, p[1], BRIDGE_Z0 + BRIDGE_T), cq.Vector(0, 0, 1)))
    bolt = bolt.fuse(cq.Solid.makeCylinder(4.0, 3.2, cq.Vector(0, p[1], BEAM_Z0 - 3.4), cq.Vector(0, 0, 1))).clean()
    return _place(bolt, bases)


def spring(bases, sx):
    """Centring spring stand-in (bought part) at its installed length, from the beam pad to the pocket floor."""
    p = pivot(bases)
    return _place(cq.Solid.makeCylinder(SPRING_OD / 2, SPRING_GAP + POCKET, cq.Vector(sx * SPRING_X, p[1] + PAD_Y, BEAM_ZC), cq.Vector(0, 1, 0)), bases)
