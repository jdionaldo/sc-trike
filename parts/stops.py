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
INSERT_R, INSERT_L = 2.0, 5.0
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
