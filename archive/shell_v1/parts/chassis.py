import math
import cadquery as cq
from .params import *
from .util import hull, beam, ball, fuse, tubes, mx


def front_corner(s, Rr_unused=None):
    """Steerable parts of one front corner (knuckle, hub axle), side s = +1 right, -1 left."""
    cx, cz = s * TRACK / 2, FRONT_OD / 2
    xi = TRACK / 2 - FRONT_W / 2                 # inner tire face (|x|)
    xk = s * (xi - 50)
    knuckle = hull([(xk + dx, FRONT_Y + dy, z) for dx in (-30, 30) for dy in (-40, 40)
                    for z in (cz - 250, cz + 260)])
    axle = beam((s * (xi - 20), FRONT_Y, cz), (s * (TRACK / 2 + FRONT_W / 2 - 50), FRONT_Y, cz), 42)
    return knuckle, axle, (xk, cz)


def front_arms(s):
    """Upper and lower A-arms (fixed to the chassis, ends at the ball joints) and the coilover."""
    cz = FRONT_OD / 2
    xi = TRACK / 2 - FRONT_W / 2
    xk = s * (xi - 50)
    ju = (xk, FRONT_Y, cz + 260)
    jl = (xk, FRONT_Y, cz - 230)
    xc = s * 470
    up = [((xc, FRONT_Y - 280, cz + 240), ju), ((xc, FRONT_Y + 280, cz + 240), ju),
          ((xc, FRONT_Y - 280, cz + 240), (xc, FRONT_Y + 280, cz + 240))]
    lo = [((xc, FRONT_Y - 330, 335), jl), ((xc, FRONT_Y + 330, 335), jl),
          ((xc, FRONT_Y - 330, 335), (xc, FRONT_Y + 330, 335))]
    arms_up = tubes(up, TUBE * 0.9)
    arms_lo = tubes(lo, TUBE * 1.05)
    return arms_up, arms_lo, jl


def coilover(a, b, spring_r=40, body_r=26, rod_r=14, coils=9):
    """Red coilover between points a (lower) and b (upper): damper body, rod and spring rings."""
    a, b = cq.Vector(*a), cq.Vector(*b)
    d = b - a
    L = d.Length
    n = d.normalized()
    at = lambda t: a + n * (L * t)
    shock = fuse([beam(at(0.0), at(0.55), rod_r), beam(at(0.30), at(1.0), body_r),
                  ball(at(0.0).toTuple(), 30), ball(at(1.0).toTuple(), 30)])
    rings = []
    for i in range(coils):
        t = 0.12 + 0.76 * i / (coils - 1)
        rings.append(cq.Solid.makeCylinder(spring_r, L * 0.045, at(t), n))
    spring = fuse(rings + [beam(at(0.12), at(0.88), spring_r * 0.78)])
    return shock, spring


def front_coilover(s):
    cz = FRONT_OD / 2
    xi = TRACK / 2 - FRONT_W / 2
    low = (s * (xi - 190), FRONT_Y, 290)
    top = (s * 440, FRONT_Y, 800)
    return coilover(low, top)


def make_swingarm():
    """Single-sided swingarm on the +X side from the pivot to the rear hub."""
    hz = REAR_OD / 2
    x0, x1 = REAR_W / 2 + 15, REAR_W / 2 + 95
    arm = hull([(x, y, z) for x in (x0, x1) for (y, z) in
                [(730, 350), (830, 350), (830, 480), (730, 520),
                 (REAR_Y - 95, hz - 85), (REAR_Y + 95, hz - 85), (REAR_Y + 95, hz + 85), (REAR_Y - 95, hz + 85)]])
    pivot = beam((x1 + 15, 750, 385), (-(x1 + 15), 750, 385), 28)
    axle = beam((x1, REAR_Y, hz), (-(REAR_W / 2 - 60), REAR_Y, hz), 42)
    return fuse([arm, pivot, axle])


def make_rear_shock():
    hz = REAR_OD / 2
    xs = REAR_W / 2 + 55
    return coilover((xs, REAR_Y - 260, hz + 70), (xs - 30, 900, 790), spring_r=44, body_r=28, coils=10)


def make_engine():
    crank = hull([(x, y, z) for x in (-135, 135) for (y, z) in [(790, 430), (960, 430), (960, 600), (790, 600)]])
    cyl = [cq.Solid.makeCylinder(58, 190, cq.Vector(0, 0, 0), cq.Vector(0, 0, 1))]
    for i in range(7):
        cyl.append(cq.Solid.makeCylinder(78, 8, cq.Vector(0, 0, 20 + i * 26), cq.Vector(0, 0, 1)))
    cyl.append(hull([(x, y, z) for x in (-65, 65) for y in (-65, 65) for z in (190, 225)]))
    jug = fuse(cyl)
    parts = [crank]
    for a in (-24, 24):
        parts.append(jug.rotate((0, 0, 0), (0, 1, 0), a).translate((0, 875, 560)))
    return fuse(parts)


def make_exhaust():
    pts = [(-70, 900, 760), (-210, 830, 640), (-255, 880, 540), (-265, 930, 470)]
    pipe = tubes(list(zip(pts[:-1], pts[1:])), 24)
    muffler = beam((-265, 840, 470), (-265, 930, 470), 46)
    return fuse([pipe, muffler])


def make_cage():
    t = []
    for s in (1, -1):
        t += [((s * 385, 700, 400), (s * 385, 1000, 420)),        # lower rail
              ((s * 385, 700, 400), (s * 385, 700, 800)),          # front post
              ((s * 330, 1000, 420), (s * 330, 1000, 710)),        # rear post
              ((s * 385, 700, 800), (s * 330, 1000, 710)),         # top rail
              ((s * 385, 700, 800), (s * 330, 1000, 420)),         # diagonal
              ]
    t += [((-385, 700, 400), (385, 700, 400)), ((-330, 1000, 420), (330, 1000, 420)),
          ((-330, 1000, 710), (330, 1000, 710))]
    return tubes(t, TUBE)


def make_tail_cowl():
    y0, y1 = 700, 1000
    slab = hull([(sx * hw, y, z) for sx in (1, -1)
                 for (y, z, hw) in [(y0, 835, 400), (y0, 870, 400), (y1, 700, 330), (y1, 735, 330)]])
    slots = [cq.Workplane("XY").box(440, 14, 200).val().translate((0, 745 + i * 40, 780 - (745 + i * 40 - 700) * 0.1))
             for i in range(6)]
    return slab.cut(fuse(slots)).clean()
