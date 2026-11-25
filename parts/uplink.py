"""Front upper link with both attachments (reference frame, +x side; the -x side is the mirror image).

The link closes the parallelogram with the lower arm: same length (100 mm) and the same slope as the arm, hinge pins along x. Its inner end is pinned to a lug on the cage's
lower side rail, its outer end to the top of the carrier. Each end is a 6 mm wide tongue (along y) in a clevis (two 3 mm plates, 6.4 mm gap, M3 pin), joined to an 8 x 8 mm
chamfered square tube by a short solid bar at the kink (the link angles outward in plan)."""
import cadquery as cq
from parts.params import CHASSIS_Y, CHASSIS_Z
from parts.tubes import square_tube, square_bar
from parts.shock_mount import GAP, PLATE_T, WIDTH, RAIL_REF

H_IN_W = (68.5, -119.4, 97.9)      # world: inner hinge (on the cage lug)
H_OUT_W = (105.0, -219.3, 91.0)    # world: outer hinge (on top of the carrier, x 102..110)
TONGUE, TONGUE_W, TONGUE_H = 12.0, 6.0, 9.0   # 12 mm: at 10 mm (008fbee) the joint sphere sat 0.7 mm past the hinge ring, a sharp neck: FEM 36.4 MPa (safety 0.55) vs 13.0 MPa
RING_R, HOLE_R = 4.5, 1.6
BAR_L = 8.0                        # solid bar at each end of the tube


def _ref(w):
    return cq.Vector(w[0], w[1] - CHASSIS_Y, w[2] - CHASSIS_Z)


def hinges():
    return _ref(H_IN_W), _ref(H_OUT_W)


def _beam(p0, p1):
    d = (p1 - p0).normalized()
    b = cq.Solid.makeBox(TONGUE_W, TONGUE_H, (p1 - p0).Length, cq.Vector(-TONGUE_W / 2, -TONGUE_H / 2, 0))
    return b.moved(cq.Location(cq.Plane(origin=p0.toTuple(), xDir=(1, 0, 0), normal=d.toTuple())))


def _eye(h, toward):
    """Tongue from the hinge toward `toward` (along y) with a round end around the hinge pin."""
    ring = cq.Solid.makeCylinder(RING_R, TONGUE_W, cq.Vector(h.x - TONGUE_W / 2, h.y, h.z), cq.Vector(1, 0, 0))
    d = (toward - h)
    d = cq.Vector(0, d.y, d.z).normalized()
    j = h + d * TONGUE
    return ring.fuse(_beam(h, j)).clean(), j


def link(sx=1):
    hi, ho = hinges()
    ei, ji = _eye(hi, hi + cq.Vector(0, -1, 0))
    eo, jo = _eye(ho, ho + cq.Vector(0, 1, 0))
    u = (jo - ji).normalized()
    parts = [ei, eo,
             cq.Solid.makeSphere(4.8, ji), cq.Solid.makeSphere(4.8, jo),
             square_bar(ji.toTuple(), (ji + u * BAR_L).toTuple()), square_bar((jo - u * BAR_L).toTuple(), jo.toTuple()),
             square_tube((ji + u * (BAR_L - 0.5)).toTuple(), (jo - u * (BAR_L - 0.5)).toTuple())]
    s = parts[0]
    for q in parts[1:]:
        s = s.fuse(q)
    s = s.clean()
    for h in (hi, ho):
        s = s.cut(cq.Solid.makeCylinder(HOLE_R, 10.0, cq.Vector(h.x - 5.0, h.y, h.z), cq.Vector(1, 0, 0)))
    assert s.isValid() and len(s.Solids()) == 1, 'upper link must be one valid solid, got %d' % len(s.Solids())
    return s if sx > 0 else s.mirror('YZ')


def clevis_u(h, sx=1):
    """Two plates (gap GAP) on a floor under the tongue, hinge hole at h: z from 12 mm under the hinge to 5 mm over it."""
    w = GAP + 2 * PLATE_T
    c = cq.Solid.makeBox(w, WIDTH, 3.8, cq.Vector(h.x - w / 2, h.y - WIDTH / 2, h.z - 12.0))   # floor top 8.2 mm under the hinge: room for the tongue to swing +-12 deg
    for x0 in (h.x - w / 2, h.x + GAP / 2):
        c = c.fuse(cq.Solid.makeBox(PLATE_T, WIDTH, 17.0, cq.Vector(x0, h.y - WIDTH / 2, h.z - 12.0)))
    c = c.clean().cut(cq.Solid.makeCylinder(HOLE_R, w + 2, cq.Vector(h.x - w / 2 - 1, h.y, h.z), cq.Vector(1, 0, 0)))
    return c if sx > 0 else c.mirror('YZ')


def rail_lug(sx=1):
    """Lug from the cage's lower side rail out to the inner clevis (ref frame)."""
    hi, _ = hinges()
    w = GAP + 2 * PLATE_T
    x0, x1 = RAIL_REF[0] - 4.0, hi.x + w / 2
    l = cq.Solid.makeBox(x1 - x0, WIDTH, 10.0, cq.Vector(x0, hi.y - WIDTH / 2, RAIL_REF[2] - 5.0))
    return l if sx > 0 else l.mirror('YZ')


def pin(h, sx=1):
    L = GAP + 2 * PLATE_T - 0.2
    p = cq.Solid.makeCylinder(1.5, L, cq.Vector(h.x - L / 2, h.y, h.z), cq.Vector(1, 0, 0))
    return p if sx > 0 else p.mirror('YZ')


def sample_points(step=4.0):
    """Points on the link's outline (ref frame, +x side): cross-section corners every `step` mm along hinge -> bend -> bend -> hinge (used for the swept shell relief)."""
    hi, ho = hinges()
    ji = hi + cq.Vector(0, -1, 0) * TONGUE; jo = ho + cq.Vector(0, 1, 0) * TONGUE
    path = [hi, ji, jo, ho]
    out = []
    for a, b in zip(path[:-1], path[1:]):
        n = max(1, int((b - a).Length / step))
        for k in range(n + 1):
            c = a + (b - a) * (k / n)
            for dx in (-4.5, 4.5):
                for dz in (-4.5, 4.5):
                    out.append((c.x + dx, c.y, c.z + dz))
    return out
