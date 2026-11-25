"""Debris walls on the rear (centre) deck: a low wall along each side edge of the w3 deck rear plate, built in the frame of chassis_ref.step.

Each wall is WALL_T thick, stands on the deck top plane (a 1.5 mm key into the plate so it fuses solid) and rises WALL_H above it, parallel to the deck
slope. Its footprint x = 52.5..54.5 (the outer 2 mm of the plate), y from just behind the front diff case to just short of the tail-deck step, was checked
against every part and the rear arm swept to 50 mm of travel: the column above it is free up to the shell and the cage (z > 140).
"""
import math
import cadquery as cq

WALL_T = 2.0
WALL_H = 26.0
KEY = 1.5
Y0_FROM_FRONT = 6.5      # mm behind the front edge of the plate: clears the front diff case that overlaps the plate corner (case ends 4.9 mm in)
Y1_FROM_REAR = 1.5       # mm short of the rear edge of the plate (the tail deck steps up there)
TAIL_X = 48.2            # half width of the tail deck at its front edge
BEND_Y = 45.2           # world y where the wall turns inward (the user's magenta line); it then runs to the tail wall along a diagonal on the deck
TAIL_JOIN_Y = 60.0       # world y where the bend ends (tail wall starts at 60.2)
CAP_STUB = 1.5           # last piece of the bend, straight and in line with the tail wall
CAP_RUN_IN = 4.5         # the bend leaves the plate edge this far before the stub and runs straight to it
RISE_Y = 20.0            # world y where the rear-deck wall top starts to climb to the shell corner
LINE = ((58.1, 98.5), (99.1, 51.5))   # the user's drawn line (world y, z): from the shell corner down to the swingarm pivot lug
def LINE_Z(y): return LINE[0][1] + (y - LINE[0][0]) * (LINE[1][1] - LINE[0][1]) / (LINE[1][0] - LINE[0][0])


def make_deck_walls(deck):
    """deck: the w3 deck rear solid (ref frame). Returns the two wall solids."""
    top_f = max((f for f in deck.Faces() if f.normalAt(f.Center()).z > 0.9), key=lambda f: f.Area())
    tc, tn = top_f.Center(), top_f.normalAt(top_f.Center())
    bb = deck.BoundingBox()
    xe = max(abs(bb.xmin), abs(bb.xmax))
    zt = lambda x, y: tc.z - (tn.x * (x - tc.x) + tn.y * (y - tc.y)) / tn.z
    from parts.params import CHASSIS_Y as _CY
    y0, y1 = bb.ymin + Y0_FROM_FRONT, BEND_Y - _CY    # the straight wall ends at the bend line
    end_f = max((f for f in deck.Faces() if f.geomType() == 'PLANE' and f.normalAt(f.Center()).y > 0.9 and f.Center().y > bb.ymax - 2.0), key=lambda f: f.Area())
    behind_end = cq.Workplane(cq.Plane(origin=end_f.Center().toTuple(), xDir=(1, 0, 0), normal=end_f.normalAt(end_f.Center()).toTuple())).rect(600, 600).extrude(50.0).val()
    below_top = cq.Workplane(cq.Plane(origin=tc.toTuple(), xDir=(1, 0, 0), normal=(tn * -1.0).toTuple())).rect(600, 600).extrude(50.0).val()
    walls = []
    for sx in (1, -1):
        xa, xb = sorted((sx * (xe - WALL_T), sx * xe))
        xm = (xa + xb) / 2
        # top edge: WALL_H above the deck up to y = RISE_Y, then up the user's drawn line to its start at the shell corner (world y 58.1, z 98.5)
        from parts.params import CHASSIS_Y, CHASSIS_Z
        yr = RISE_Y - CHASSIS_Y
        pts = [(y0, zt(xm, y0) - KEY), (y1, zt(xm, y1) - KEY), (y1, LINE_Z(y1 + CHASSIS_Y) - CHASSIS_Z), (yr, zt(xm, yr) + WALL_H), (y0, zt(xm, y0) + WALL_H)]
        w = cq.Workplane('YZ', origin=(xa, 0, 0)).polyline(pts).close().extrude(xb - xa).val()
        # Bend to the tail wall: the tail deck is narrower (half width 48.2, wall x 46.2..48.2) and starts 1.9 mm further back, which left a step and an open slit
        # between the end of this wall (x 52.5..54.5) and the tail wall. A cap piece bends the wall in along a diagonal (plan view) from its outer end corner to
        # the outer face of the tail wall, ending 0.2 mm short of the tail wall start (the tail deck is a separate part).
        ye = TAIL_JOIN_Y - CHASSIS_Y
        bz0 = lambda y: zt(xm, y) - KEY
        bz1 = lambda y: LINE_Z(y + CHASSIS_Y) - CHASSIS_Z
        cap_prof = [(y1 - 0.5, bz0(y1)), (ye, bz0(ye)), (ye, bz1(ye)), (y1 - 0.5, bz1(y1))]
        cap_prism = cq.Workplane('YZ', origin=(-200, 0, 0)).polyline(cap_prof).close().extrude(400).val()
        # a wall band, not a wedge: its outer face traces the rear deck plate's own edge (measured every 2 mm), ending on the tail wall's outer face
        def hw(y):
            c = deck.intersect(cq.Solid.makeBox(200, 0.02, 400, cq.Vector(-100, y - 0.01, bb.zmin - 100)))   # thin slice: the edge itself
            return c.BoundingBox().xmax if c.Volume() > 0.001 else TAIL_X
        # the trace follows the plate edge up to CAP_RUN_IN before the end, runs straight to the tail wall's line and ends with a stub of
        # CAP_STUB in line with the tail wall, so its end face is square (the diagonal used to meet the end face at 64 degrees)
        yk = ye - CAP_STUB - CAP_RUN_IN
        n_seg = max(2, int((yk - (y1 - 0.5)) / 2.0))
        ys = [(y1 - 0.5) + (yk - (y1 - 0.5)) * k / n_seg for k in range(n_seg + 1)]
        outer = [min(xe, hw(y)) for y in ys] + [TAIL_X, TAIL_X]
        ys += [ye - CAP_STUB, ye]
        cap_plan = [(sx * x, y) for x, y in zip(outer, ys)] + [(sx * (x - WALL_T), y) for x, y in reversed(list(zip(outer, ys)))]
        cap = cap_prism.intersect(cq.Workplane('XY').workplane(offset=-100).polyline(cap_plan).close().extrude(400).val())
        # the bend runs on past the plate's rear end face, over the tail deck: there it stands on the tail deck's top (same plane as this plate's
        # top) instead of reaching KEY into it (it overlapped the tail deck by 1.6 mm3 per side)
        cap = cap.cut(behind_end.intersect(below_top))
        w = w.fuse(cap).clean()
        walls.append(w.chamfer(0.6, None, [e for e in w.Edges() if abs(e.Center().z - max(p[1] for p in pts)) < 3.0 and abs(e.Center().x - (xb if sx > 0 else xa)) < 0.1][:1]) if False else w)
    return walls


# ---- tail deck ---------------------------------------------------------------------------------------------------------------------------------
# The tail deck narrows toward the rear (half width 48.2 at its front edge, 40 at its rear edge). The wall follows that edge. The single-sided rear arm
# (outer plates, +x side) sweeps over the +x edge behind world y 100, so there the +x wall steps down along a 48 deg ramp to a low section that stays
# 1 mm under the swept arm (lowest z 52.7 world at 50 mm bump) and ends at world y 124, before the arm drops below the deck top. The -x wall has the full height.
ARM_SIDE = 1
ARM_RAMP_Y = (88.0, 100.0)     # world y: full height until the first, down to the low section at the second
ARM_LOW_TOP_Z = 51.5           # world z of the top of the low section (swept arm underside 52.7 -> 1.2 mm clear)
ARM_END_Y = 124.0              # world y where the +x wall ends
WALL_END_FROM_FRONT, WALL_END_FROM_REAR = 1.0, 1.0


def make_tail_walls(deck):
    """deck: the w3 deck tail solid (ref frame). Returns the two wall solids."""
    from parts.params import CHASSIS_Y, CHASSIS_Z
    top_f = max((f for f in deck.Faces() if f.normalAt(f.Center()).z > 0.9), key=lambda f: f.Area())
    tc, tn = top_f.Center(), top_f.normalAt(top_f.Center())
    bb = deck.BoundingBox()
    zt = lambda y: tc.z - (tn.y * (y - tc.y)) / tn.z - (tn.x * (0 - tc.x)) / tn.z
    y0, y1 = bb.ymin + WALL_END_FROM_FRONT, bb.ymax - WALL_END_FROM_REAR
    def half(y):
        c = deck.intersect(cq.Solid.makeBox(200, 1.0, 400, cq.Vector(-100, y - 0.5, bb.zmin - 200)))
        return c.BoundingBox().xmax
    ya, yb = bb.ymin + 0.1 * (bb.ymax - bb.ymin), bb.ymin + 0.9 * (bb.ymax - bb.ymin)
    ha, hb = half(ya), half(yb)
    xe = lambda y: ha + (hb - ha) * (y - ya) / (yb - ya)
    wy = lambda yw: yw - CHASSIS_Y            # world y -> ref y
    out = []
    for sx in (1, -1):
        # both walls: top follows the drawn line from the shell corner (y 58.1) down to z 51.5 at y 99.1, then runs level (1.2 mm under the swept arm) to y 124
        ye = wy(ARM_END_Y)
        low = ARM_LOW_TOP_Z - CHASSIS_Z
        ylw = wy(LINE[1][0])
        ya_, yb_ = y0 - 1.0, ye + 1.0           # the side profile runs past both ends, the plan below cuts the end faces
        prof = [(ya_, zt(ya_) - KEY), (yb_, zt(yb_) - KEY), (yb_, low), (ylw, low), (ya_, LINE_Z(ya_ + CHASSIS_Y) - CHASSIS_Z)]
        prism = cq.Workplane('YZ', origin=(-200, 0, 0)).polyline(prof).close().extrude(400).val()
        # plan: WALL_T measured square to the wall, end faces square to it too (ends cut along y left an 84 degree knife corner)
        ux, uy = xe(ye) - xe(y0), ye - y0
        ul = math.hypot(ux, uy); nx, ny = -uy / ul * WALL_T, ux / ul * WALL_T
        plan = [(sx * xe(y0), y0), (sx * xe(ye), ye), (sx * (xe(ye) + nx), ye + ny), (sx * (xe(y0) + nx), y0 + ny)]
        plate = cq.Workplane('XY').workplane(offset=-100).polyline(plan).close().extrude(400).val()
        out.append(prism.intersect(plate))
    return out
