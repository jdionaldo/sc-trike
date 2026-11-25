"""Printed GT2 (2 mm pitch) timing pulleys and the closed-loop belt envelopes for the front and rear swing arms.

The belts are bought parts: 6 mm wide GT2 closed loops (2GT-240 front, 2GT-300 rear, both common stock lengths). The pulleys are printed in PETG
with the axis vertical. The tooth gaps are round slots (r 0.70 mm, 0.75 mm deep: the GT2 tooth height), the outside diameter is the pitch diameter
minus 0.76 mm, as for a real GT2 pulley.

Belt length of two pulleys with pitch diameters D1, D2 at centre distance d:  L = 2 d + pi (D1 + D2) / 2 + (D2 - D1)^2 / (4 d).
"""
import math
import numpy as np
import cadquery as cq

PITCH = 2.0
BELT_W = 6.0                 # mm, belt width
TOOTH_W = BELT_W + 0.6       # toothed length: 0.3 mm each side of the belt
FLANGE_T = 1.2
FLANGE_EXTRA = 2.4           # flange diameter = tooth OD + this
BELT_T = 1.38                # GT2 belt thickness
TOOTH_H = 0.75
GRUB_END_WALL = 0.9          # mm of hub left between the grub screw pilot and the hub's free end


def pitch_dia(teeth): return teeth * PITCH / math.pi
def tooth_od(teeth): return pitch_dia(teeth) - 0.76


def belt_length(t1, t2, d):
    D1, D2 = pitch_dia(t1), pitch_dia(t2)
    return 2 * d + math.pi * (D1 + D2) / 2 + (D2 - D1) ** 2 / (4 * d)


def make_pulley(teeth, bore, hub_len=4.0, hub_od=None, side=1, setscrew=True):
    """Pulley on the x axis, toothed part centred on x = 0; the hub grows toward `side` (+1 or -1) behind the outer flange.
    Returns a solid. Bore gets 0.15 mm clearance; the hub carries an M3 grub screw (D2.8 self-tapping pilot) when setscrew."""
    od = tooth_od(teeth)
    hub_od = hub_od or max(bore + 5.0, 9.0)
    hub_od = min(hub_od, od - 1.5)
    ax = cq.Vector(1, 0, 0)
    L = TOOTH_W + 2 * FLANGE_T
    body = cq.Solid.makeCylinder(od / 2, TOOTH_W, cq.Vector(-TOOTH_W / 2, 0, 0), ax)
    for k in range(teeth):
        a = 2 * math.pi * k / teeth
        c = cq.Vector(-TOOTH_W / 2 - 0.1, (od / 2 - 0.05) * math.cos(a), (od / 2 - 0.05) * math.sin(a))
        body = body.cut(cq.Solid.makeCylinder(0.70, TOOTH_W + 0.2, c, ax))
    for s in (-1, 1):
        x0 = s * TOOTH_W / 2 if s > 0 else -TOOTH_W / 2 - FLANGE_T
        body = body.fuse(cq.Solid.makeCylinder((od + FLANGE_EXTRA) / 2, FLANGE_T, cq.Vector(x0, 0, 0), ax))
    xh = L / 2 if side > 0 else -L / 2 - hub_len
    body = body.fuse(cq.Solid.makeCylinder(hub_od / 2, hub_len, cq.Vector(xh, 0, 0), ax))
    body = body.cut(cq.Solid.makeCylinder((bore + 0.2) / 2, L + 2 * hub_len + 2, cq.Vector(-L / 2 - hub_len - 1, 0, 0), ax))
    if setscrew:
        xs = side * (L / 2 + hub_len - GRUB_END_WALL - 1.4)   # off centre toward the flange: the wall to the hub end was 0.6 mm in a 4 mm hub
        body = body.cut(cq.Solid.makeCylinder(1.4, hub_od, cq.Vector(xs, 0, 0), cq.Vector(0, 0, 1)))
    body = body.clean()
    assert body.isValid() and len(body.Solids()) == 1, 'pulley is not one valid solid'
    return body


def _circle_pts(cy, cz, r, n=72):
    return [(cy + r * math.cos(2 * math.pi * i / n), cz + r * math.sin(2 * math.pi * i / n)) for i in range(n)]


def _hull2(pts):
    from scipy.spatial import ConvexHull
    p = np.array(pts); h = ConvexHull(p)
    return [tuple(p[i]) for i in h.vertices]


def belt_loop(c1, t1, c2, t2, x_mid):
    """Closed-loop belt envelope around two pulleys (axis x, centres c = (y, z)), belt width BELT_W centred on x_mid. A solid ring between the pitch-line
    envelopes: inside radius pitch radius - 0.30 (the teeth are in mesh, 0.08 mm clear of the pulley tooth tips), outside radius + 1.0."""
    r1, r2 = pitch_dia(t1) / 2, pitch_dia(t2) / 2
    outer = _hull2(_circle_pts(*c1, r1 + 1.0) + _circle_pts(*c2, r2 + 1.0))
    inner = _hull2(_circle_pts(*c1, r1 - 0.30) + _circle_pts(*c2, r2 - 0.30))
    wp = cq.Workplane('YZ', origin=(x_mid - BELT_W / 2, 0, 0))
    o = wp.polyline(outer).close().extrude(BELT_W)
    i = cq.Workplane('YZ', origin=(x_mid - BELT_W / 2, 0, 0)).polyline(inner).close().extrude(BELT_W)
    return o.cut(i).val()
