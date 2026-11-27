"""Printed travel stops of the wishbone front end (parts/wishbone.py), deck-mounted.

Owner's rule: travel ends on printed stops, never on the shock. What is here:

- Droop stop, one per side: a PETG base screwed to the front deck under the lower arm's root, with a TPU 95A pad bonded into a 1.5 mm
  pocket on top. The pad's top face is the lower arm's underside at that side's droop end pose: lean 10 deg with this side high plus
  8 mm droop on top (tools/front_check.py: psi = wb.solve_psi(s, -s * 10) - s * asin(-8 / ARM_L), i.e. 20.55 deg), 0.05 mm proud of
  contact so a rigid check shows touch without overlap. Two M3 x 10 socket head screws from under the deck into M3 x 4 heat-set inserts
  (ruthex RX-M3x4, pocket 4.0 x 5.0) in the base; model.py makes the 3.4 mm clearance holes in the deck.
- Bump and lean stops: not here. No deck-mounted position exists for them (see the board / NOTES): above the upper arm sit its shock posts
  and the cage brace, and lean (both arms turning the same way) can only be sensed by a part that is joined to both arms.

All shapes are in world coordinates (mm), +x side built and mirrored for -x.
"""
import math
import cadquery as cq
from parts import wishbone as wb

V = cq.Vector
DROOP = -8.0                 # mm of droop on top of full lean, where the shell and cage cuts end
LEAN = 10.0                  # deg
X0, X1 = 28.0, 38.0          # pad along x (13 .. 23 mm from the pivot axis): the lower arm is still 7 .. 11 mm above the deck at droop
PAD_Y = (-186.0, -178.0)     # pad across y: inside the underside of both lower arm legs over the whole x range
PAD_T, PAD_SINK = 3.0, 1.5   # TPU pad thickness, depth of its pocket in the base
RIM = 2.0                    # base wall around the pad pocket
BASE_Y = (-193.5, -170.5)    # base footprint across y: the two insert bores beside the pad keep a 2.5 mm wall
SCREWS = ((33.0, -189.0), (33.0, -175.0))      # +x side (x, y): M3 from below, inserts in the base
INSERT_R, INSERT_L = wb.INSERT_POCKET_D / 2, 5.0
GAP = 0.05                   # pad top below the arm's face at the end pose


def droop_psi(s):
    """Arm angle of side s at its droop end pose (deg, right hand about +y, as tools/front_check.py)."""
    return wb.solve_psi(s, -s * LEAN) - s * math.degrees(math.asin(DROOP / wb.ARM_L))


def _contact_z(x, psi):
    """z of the +x lower arm's underside plane at x with the arm turned by psi (the tube's bottom flat, rotated about the pivot axis)."""
    h = wb.ARM_D_LO * 0.44
    c, sn = math.cos(math.radians(psi)), math.sin(math.radians(psi))
    px, pz = wb.XI + sn * -h, wb.ZL + c * -h           # rotated point of the flat under the pivot axis
    return pz - math.tan(math.radians(psi)) * (x - px)


def _slab(x0, x1, y0, y1, zbot, ztop):
    """Prism over x0..x1, y0..y1 from zbot up to the plane given by ztop(x) (straight in x)."""
    pts = [(x0, zbot), (x1, zbot), (x1, ztop(x1)), (x0, ztop(x0))]
    return cq.Workplane('XZ', origin=(0, y1, 0)).polyline(pts).close().extrude(y1 - y0).val()


def droop_stop(s=1):
    """(base, pad) of side s. The base reaches down to z 10: model.py cuts the deck out of it and keeps the piece on top."""
    psi = droop_psi(1)
    top = lambda x: _contact_z(x, psi) - GAP
    band = lambda x0, x1, y0, y1, hi, lo: _slab(x0, x1, y0, y1, 0.0, hi).cut(_slab(x0 - 1, x1 + 1, y0 - 1, y1 + 1, -1.0, lo))
    pad = band(X0, X1, PAD_Y[0], PAD_Y[1], top, lambda x: top(x) - PAD_T)
    base = _slab(X0 - RIM, X1 + RIM, BASE_Y[0], BASE_Y[1], 10.0, lambda x: top(x) - PAD_T + PAD_SINK)
    base = base.cut(band(X0 - 0.1, X1 + 0.1, PAD_Y[0] - 0.1, PAD_Y[1] + 0.1, lambda x: top(x) + 1.0, lambda x: top(x) - PAD_T))
    if s < 0:
        base, pad = base.mirror('YZ'), pad.mirror('YZ')
    assert base.isValid() and pad.isValid() and len(pad.Solids()) == 1, 'droop stop is not valid'
    return base, pad


def insert_bores(s):
    """Heat-set insert bores (from the base's underside) of side s, world coordinates; model.py cuts them after seating the base on the deck."""
    out = []
    for x, y in SCREWS:
        zb = wb.deck_top(y) - 1.0
        out.append(cq.Solid.makeCylinder(INSERT_R, INSERT_L + 1.0, V(s * x, y, zb), V(0, 0, 1)))
    return out


def screw_points(s):
    return [(s * x, y) for x, y in SCREWS]


def all_parts():
    """[(name, shape, group, colour, seat)] with seat True for the parts model.py seats on the deck."""
    out = []
    for s in (1, -1):
        b, p = droop_stop(s)
        out.append(('Droop stop %d' % s, b, 'Chassis/Stops', (0.16, 0.17, 0.20), True))
        out.append(('Droop stop pad %d' % s, p, 'Chassis/Stops', (0.05, 0.05, 0.05), False))
    return out


# ---- up stops (lean stops) ----
# Lean is bounded by a stop on each arm in each direction: the droop stops above bound the arm going down, these up stops bound it going up.
# With heave free between them, the largest lean is half the sum of the two arm angles. The up stop is a TPU 95A saddle bonded under the cage's
# front brace, where the upper arm's post diagonal comes 1.1 mm from the brace at the end of the checked travel (lean 10 deg with this side up
# plus 12 mm bump): without the pad the cage brace is the hard stop. On the lean head the lever to the pivot is only about 7 mm (stop force over
# 1000 N), at the brace it is about 33 mm.
UP_LEAN, UP_BUMP = 10.0, 12.0     # end pose of side s: lean s * UP_LEAN (this side up) plus UP_BUMP mm of bump on top
UP_PAD_T = 2.5                    # pad thickness under the brace (pad = the brace moved down by UP_PAD_T, minus the brace and the arm)
UP_SCREW_L, UP_SCREW_HEAD, UP_SCREW_PILOT, UP_SCREW_CLEAR_D = 8.0, (3.8, 1.3), 1.6, 2.4   # M2 x 8 pan head self-tapping (ISO 7049 ST2.2): head D3.8 x 1.3 sunk into the pad
UP_SCREW_CLEAR = 1.5              # the screw head's seat keeps this distance from the arm at its end pose
UP_PAD_BOX = 12.0                 # pad footprint: a cube of this size around the arm's closest point to the brace at the end pose


def up_psi(s):
    """Arm angle of side s at its up end pose (deg, as tools/front_check.py)."""
    return wb.solve_psi(s, s * UP_LEAN) - s * math.degrees(math.asin(UP_BUMP / wb.ARM_L))


def up_stop_pad(s, upper_arm, cage):
    """TPU pad of side s under the cage brace. upper_arm: the registered upper arm of side s at rest, cage: the cage solid (world)."""
    from OCP.BRepExtrema import BRepExtrema_DistShapeShape
    ae = upper_arm.moved(wb._loc_axis((s * wb.XI, 0, wb.ZU), (0, 1, 0), up_psi(s)))
    d = BRepExtrema_DistShapeShape(ae.wrapped, cage.wrapped); d.Perform()
    assert d.IsDone() and d.Value() < UP_PAD_T - 0.3, 'up stop: the arm at its end pose is %.2f mm from the cage (pad %.1f)' % (d.Value(), UP_PAD_T)
    p = d.PointOnShape2(1); h = UP_PAD_BOX / 2
    reg = cq.Solid.makeBox(UP_PAD_BOX, UP_PAD_BOX, UP_PAD_BOX, V(p.X() - h, p.Y() - h, p.Z() - UP_PAD_BOX + 3.0))
    pad = cage.moved(cq.Location(V(0, 0, -UP_PAD_T))).intersect(reg).cut(cage).cut(ae.moved(cq.Location(V(0, 0, GAP))))
    pad = max(pad.Solids(), key=lambda q: q.Volume()).clean()
    assert pad.isValid() and pad.Volume() > 50.0, 'up stop pad of side %d failed (%.1f mm3)' % (s, pad.Volume())
    # mechanical key: one M2 x 8 self-tapping screw, vertical, through the pad's thickest spot clear of the arm, into a pilot hole in the cage
    best = None
    for i in range(-5, 6):
        for j in range(-5, 6):
            x, y = p.X() + i * 1.0, p.Y() + j * 1.0
            line = pad.intersect(cq.Solid.makeBox(0.3, 0.3, 40.0, V(x - 0.15, y - 0.15, p.Z() - 20.0)))
            if not line.Solids():
                continue
            b = line.BoundingBox()
            dd = BRepExtrema_DistShapeShape(cq.Vertex.makeVertex(x, y, b.zmin).wrapped, ae.wrapped); dd.Perform()
            if dd.Value() < UP_SCREW_CLEAR:
                continue
            if best is None or b.zlen > best[2]:
                best = (x, y, b.zlen, b.zmin, b.zmax)
    assert best is not None and best[2] >= 2.0, 'up stop pad of side %d: no screw spot (%s)' % (s, best)
    x, y, t, zb, zt = best
    hole = cq.Solid.makeCylinder(UP_SCREW_CLEAR_D / 2, t + 2.0, V(x, y, zb - 1.0), V(0, 0, 1))
    head = cq.Solid.makeCylinder(UP_SCREW_HEAD[0] / 2 + 0.2, UP_SCREW_HEAD[1] + 1.0, V(x, y, zb - 1.0), V(0, 0, 1))
    cut = pad.cut(hole).cut(head)
    keep = max(cut.Solids(), key=lambda q: q.Volume())
    assert keep.Volume() > 0.9 * cut.Volume(), 'up stop pad of side %d split at the screw (%s mm3)' % (s, [round(q.Volume(), 1) for q in cut.Solids()])
    pad = keep.clean()
    pilot = cq.Solid.makeCylinder(UP_SCREW_PILOT / 2, UP_SCREW_L - (zt - zb - UP_SCREW_HEAD[1]) + 1.0, V(x, y, zt - 0.5), V(0, 0, 1))
    assert pad.isValid() and len(pad.Solids()) == 1, 'up stop pad of side %d broke at the screw' % s
    return pad, (p.X(), p.Y(), p.Z()), d.Value(), pilot, (x, y, zb + UP_SCREW_HEAD[1], t)
