"""Deck side bands: widen the stand-in deck plates to the shell's inner wall with a clean, linear faceted outline.

The deck plates (w3 deck front / rear) are 6.06 mm thick sloped plates, half width 54.5. In the cabin the shell sills are wider
(about +-58 to +-68 mm). To avoid jagged steps or spikes protruding past the lower shell facets, each side band uses a single
clean linear taper between the narrowest shell waist and the front/rear deck edges.
"""
import cadquery as cq
from parts.params import CHASSIS_Y, CHASSIS_Z, DECK_REF_Z0, DECK_SLOPE, DECK_THICKNESS

DECK_INNER_X = 54.0      # bands start inside the old deck edge (54.5) for a clean overlap
BAND_MAX_X = 68.0
BAND_GAP = 2.0           # generous clearance inside the shell inner wall so the deck edge is well inboard of lower facets
BAND_Y0, BAND_Y1 = -78.0, 20.0   # world y: from behind the front suspension cutout to the rear quarter termination
SEAM_Y = -62.0           # front / rear deck plate seam (world y)


def deck_top(y):
    """World z of the deck top plane at world y."""
    return DECK_REF_Z0 + DECK_SLOPE * (y - CHASSIS_Y + 189.0) + CHASSIS_Z


def band_pieces(shells, step=4.0):
    """Returns [(solid, 'w3 deck front' | 'w3 deck rear'), ...] in world coordinates.
    Per markup 12:24-2, the deck sides stay straight along the original +-54.5 mm plate edge with no protruding side bands."""
    return []


def _deck_slab(deck):
    """Infinite planar slab bounded by the exact top and bottom planes of a sloped deck plate (in chassis_ref coordinates)."""
    top_f = max((f for f in deck.Faces() if f.normalAt(f.Center()).z > 0.9), key=lambda f: f.Area())
    bot_f = max((f for f in deck.Faces() if f.normalAt(f.Center()).z < -0.9), key=lambda f: f.Area())
    tc, tn = top_f.Center(), top_f.normalAt(top_f.Center())
    bc = bot_f.Center()
    t = abs((tc - bc).dot(tn))
    pl = cq.Plane(origin=tc.toTuple(), normal=tn.toTuple())
    return cq.Workplane(pl).rect(600, 600).extrude(-t).val()


def _unify_deck(shape):
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    for lt, at in ((0.05, 0.01), (0.02, 0.005), (1e-3, 1e-3)):
        u = ShapeUpgrade_UnifySameDomain(shape.wrapped, True, True, True)
        u.SetLinearTolerance(lt); u.SetAngularTolerance(at); u.Build()
        g = cq.Shape.cast(u.Shape()).fix()
        if g.isValid() and len(g.Solids()) == 1:
            return g
    return shape


def clean_deck_plates(assembly):
    """Fill unused leftover holes from the old layout on all three deck plates, widen the rear of w3 deck rear so the
    rear cage foot holes have generous edge margin (markup 13:41), extend w3 deck tail to support w3 rbc lower (markup 13:42),
    and unify coplanar mesh facets."""
    nodes = {n.name: n for n in assembly.objects.values() if getattr(n, 'name', None) in ('w3 deck front', 'w3 deck rear', 'w3 deck tail')}

    if 'w3 deck front' in nodes:
        n = nodes['w3 deck front']
        d = n.obj.val() if isinstance(n.obj, cq.Workplane) else n.obj
        slab = _deck_slab(d)
        # Step wall plane at y ~ -90.24 (normal perpendicular to deck slope) so the rear-corner hole plugs merge seamlessly into the step wall
        step_f = min((f for f in d.Faces() if abs(f.Center().y - (-90.24)) < 0.5 and f.Center().x > 46.0 and f.normalAt(f.Center()).y < -0.9),
                     key=lambda f: abs(f.Center().x - 48.0))
        sc, sn = step_f.Center(), step_f.normalAt(step_f.Center())
        behind_step = cq.Workplane(cq.Plane(origin=sc.toTuple(), normal=(-sn.x, -sn.y, -sn.z))).rect(200, 200).extrude(50.0).val()
        # Plug unused blind pockets along the front nose edge (y_ref = -221.4..-213.0), unused blind pocket at (26.6, -186.0),
        # and unused rear step-corner holes at (+-44.0, -88.2)
        plugs = [
            cq.Solid.makeBox(70.0, 9.5, 100.0, cq.Vector(-35.0, -221.4, -10.0)),
            cq.Solid.makeBox(6.0, 2.2, 100.0, cq.Vector(24.0, -186.8, -10.0)),
            cq.Solid.makeBox(8.0, 8.0, 100.0, cq.Vector(-48.0, -92.0, -10.0)).intersect(behind_step),
            cq.Solid.makeBox(8.0, 8.0, 100.0, cq.Vector(40.0, -92.0, -10.0)).intersect(behind_step),
        ]
        for p in plugs:
            d = d.fuse(slab.intersect(p))
        # Extend the straight +-54.5 mm side edge forward from y_ref = -190.03 to y_ref = -212.0 (y_world = -203.0, 8 mm ahead of the
        # front cage foot holes at y_world = -195.0 / y_ref = -204.0, markup 13:41) before beveling to (+-36.0, -221.45)
        for sx in (-1, 1):
            pts = [
                (sx * 35.0, -221.45),
                (sx * 36.0, -221.45),
                (sx * 54.5, -212.0),
                (sx * 54.5, -189.0),
                (sx * 35.0, -189.0),
            ]
            prism = cq.Workplane('XY').workplane(offset=-10.0).polyline(pts).close().extrude(100.0).val()
            d = d.fuse(slab.intersect(prism))
        n.obj = _unify_deck(d.clean())

    if 'w3 deck rear' in nodes:
        n = nodes['w3 deck rear']
        d = n.obj.val() if isinstance(n.obj, cq.Workplane) else n.obj
        slab = _deck_slab(d)
        # Plug unused side holes at (+-52.5, -24.2) inside the +-54.5 mm side wall
        for sx in (-1, 1):
            x0 = 49.5 if sx > 0 else -54.45
            p = cq.Solid.makeBox(4.95, 7.5, 100.0, cq.Vector(x0, -28.0, -10.0))
            d = d.fuse(slab.intersect(p))
        # Widen the rear side taper (y_ref = -14.46..50.39) so the straight +-54.5 mm edge continues back to y_ref = +39.0
        # (y_world = +48.0, well past the rear cage foot holes at y_world = +38.0, markup 13:41). From there one diagonal runs to the rear end
        # face: it passes through the old plate's rear corner at the underside (48.18, 50.80), so the old outline lies inside the new one
        # everywhere, and the added piece ends on the plane of the plate's own (slanted) rear face. No step, sliver or nub at the corner.
        rear_f = max((f for f in d.Faces() if f.geomType() == 'PLANE' and f.normalAt(f.Center()).y > 0.9 and f.Center().y > d.BoundingBox().ymax - 2.0),
                     key=lambda f: f.Area())
        rc, rn = rear_f.Center(), rear_f.normalAt(rear_f.Center())
        ahead = cq.Workplane(cq.Plane(origin=rc.toTuple(), xDir=(1, 0, 0), normal=(-rn.x, -rn.y, -rn.z))).rect(600, 600).extrude(300.0).val()
        k = (48.18 - 54.5) / (50.80 - 39.0)                      # x per y of the diagonal
        for sx in (-1, 1):
            pts = [
                (sx * 46.0, -15.0),
                (sx * 54.5, -15.0),
                (sx * 54.5, 39.0),
                (sx * (48.18 + k * 1.5), 52.3),
                (sx * 46.0, 52.3),
            ]
            prism = cq.Workplane('XY').workplane(offset=-10.0).polyline(pts).close().extrude(100.0).val()
            d = d.fuse(slab.intersect(prism).intersect(ahead))
        d = _unify_deck(d.clean())
        # Pillow block screw slots (x 5.9..11.1 and 30.9..36.1): the head recess under the plate stopped 0.3..0.5 mm short of the rear end face and
        # left a skin there. The recess now runs out through the end face (the tail deck closes it), the slot travel stays as it was.
        zb = min(f.Center().z for f in d.Faces() if f.geomType() == 'PLANE' and f.normalAt(f.Center()).z < -0.9 and f.Area() > 1000.0)
        floors = [f for f in d.Faces() if f.geomType() == 'PLANE' and f.normalAt(f.Center()).z < -0.9 and f.Area() < 200.0
                  and rc.y - 2.0 < f.BoundingBox().ymax < rc.y and f.Center().z > zb + 1.0]
        assert len(floors) == 2, 'pillow slot recesses not found on the rear deck (%d)' % len(floors)
        for f in floors:
            fb, fc, fn = f.BoundingBox(), f.Center(), f.normalAt(f.Center())
            below = cq.Workplane(cq.Plane(origin=fc.toTuple(), xDir=(1, 0, 0), normal=fn.toTuple())).rect(600, 600).extrude(50.0).val()
            d = d.cut(cq.Solid.makeBox(fb.xlen, 3.0, 100.0, cq.Vector(fb.xmin, fb.ymax - 0.5, -20.0)).intersect(below))
        assert d.isValid() and len(d.Solids()) == 1, 'opening the pillow slot recesses broke the rear deck'
        n.obj = _unify_deck(d.clean())

    if 'w3 deck tail' in nodes:
        n = nodes['w3 deck tail']
        d = n.obj.val() if isinstance(n.obj, cq.Workplane) else n.obj
        slab = _deck_slab(d)
        # Plug unused side holes at (+-41.5, +85.5) inside the tapered side wall (|x| <= 44.55 at y = 88.3)
        for sx in (-1, 1):
            x0 = 38.5 if sx > 0 else -44.3
            p = cq.Solid.makeBox(5.8, 6.5, 100.0, cq.Vector(x0, 82.5, -10.0))
            d = d.fuse(slab.intersect(p))
        # Trim behind y_ref = 139.0 (y_world = 148.0) so the rear belt case (y_ref <= 132.0) and its rear mounting slots
        # (y_ref = 124.2..135.6) are fully enclosed with solid rear margin (markup 13:42)
        d = d.cut(cq.Solid.makeBox(200.0, 100.0, 200.0, cq.Vector(-100.0, 139.0, -50.0)))
        n.obj = _unify_deck(d.clean())
    fill_rbc_lip(assembly)


def fill_rbc_lip(assembly):
    """Rear bearing carrier halves (w3 rbc lower / upper): the outboard D11.1 bearing seat was separated from the D15 counterbore by a 0.3 mm lip
    (s -37.59..-37.29 along the rear shaft axis). A ring (D5.4..D15.2) fills the counterbore floor so 1.5 mm remains between seat and counterbore.
    Ref frame of chassis_ref.step; each half gets the part of the ring on its side of the split plane (through the shaft axis)."""
    O = cq.Vector(21.0, 49.485, 75.096)                      # rear shaft axis point (ref frame) and direction toward the front
    A = cq.Vector(0.0, -0.9976, -0.0698).normalized()
    s0, s1 = -38.79, -37.45                                    # new counterbore floor 1.5 mm from the seat face (s -37.29); ends inside the old lip
    s_seat = -37.29
    ring = cq.Solid.makeCylinder(7.6, s1 - s0, O + A * s0, A)
    # one clean shaft bore (D5.5, shaft D5) through the ring and the rest of the old lip: the lip's own bore is a 64-sided polygon of the mesh
    # stand-in, a round D5.4 bore in the ring left slivers between circle and polygon
    bore = cq.Solid.makeCylinder(2.75, (s_seat + 0.3) - (s0 - 0.5), O + A * (s0 - 0.5), A)
    up = A.cross(cq.Vector(1, 0, 0)).normalized()             # split plane normal, toward the upper half
    q = cq.Vertex.makeVertex(*(O + A * s0 + cq.Vector(-5.0, 0, 0)).toTuple())
    for name, side in (('w3 rbc lower', -1.0), ('w3 rbc upper', 1.0)):
        node = [n for n in assembly.objects.values() if getattr(n, 'name', None) == name]
        if not node: continue
        node = node[0]
        d = node.obj.val() if isinstance(node.obj, cq.Workplane) else node.obj
        # the ring half ends exactly on the plane of the half's own split face beside the bore (that mesh face lies a few thousandths off the
        # plane through the shaft axis, which left films and steps of that height on the split face)
        split = min((f for f in d.Faces() if f.geomType() == 'PLANE' and f.Area() > 50.0 and f.normalAt(f.Center()).dot(up) * side < -0.999
                     and abs((f.Center() - O).dot(up)) < 0.05), key=lambda f: f.distance(q))
        half = cq.Workplane(cq.Plane(origin=split.Center().toTuple(), xDir=(1, 0, 0), normal=(split.normalAt(split.Center()) * -1.0).toTuple())).rect(200, 200).extrude(60.0).val()
        d2 = d.fuse(ring.intersect(half)).clean().cut(bore).clean()
        assert d2.isValid() and len(d2.Solids()) == 1, 'rbc lip fill broke ' + name
        node.obj = d2
