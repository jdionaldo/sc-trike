"""Plain front deck: one flat slab in the plane of the old front deck, without its mounting holes, pockets, sockets, ears and recesses.

The slab keeps the old deck's top and bottom planes (found as the planes carrying the most face area with a normal close to +-z) and its plan outline
(sampled along y, so the bevelled front corners stay). make_flat_deck ends it on the plane of the rear deck's front face; lap_decks then turns that
seam into a full-thickness half lap with four M3 screws (front deck on top, rear deck underneath). The skid is screwed under its front edge with
a stepped lap (lap_skid). Frame: whatever frame the given deck solids are in.
"""
import cadquery as cq
from parts.params import INSERT_M3_D

V = cq.Vector

SKID_SCREWS = ((26.0, 6.05), (-26.0, 6.05))   # M3 self-tapping screws from below through the flange (x, y behind the deck's front edge)
SKID_SCREW_D, SKID_PILOT_D = 3.4, 2.6

# Front / rear deck seam: full-thickness half lap. Distances along the deck plane from the rear deck's old front face (+ toward the rear).
# Lap from 7.4 ahead of the old face (world y -69.5: clear of the servo screw holes at y -74.9) to 5.6 behind it (world y -56.5: ahead of the rear
# deck's side walls at -55.8 and rail foot brackets at -55.0). The front deck carries the upper half, the rear deck the lower half.
LAP_AHEAD, LAP_BEHIND = 7.4, 5.6
LAP_END_GAP = 0.25        # mm: at each tongue end (tongue end to shoulder)
LAP_FACE_GAP = 0.2        # mm: between the two lap faces (the ledge under the front deck's tongue prints on support)
# M3 x 10 countersunk (ISO 10642) from below, head flush in the rear deck's tongue, into a ruthex M3 x 4 insert in a boss on the front deck's tongue
LAP_SCREW_AHEAD = 0.9     # screw axis 0.9 ahead of the old face (world y -63.0): 6.25 mm (2 d) to both tongue ends
LAP_SCREW_X = (-46.0, -26.0, 26.0, 46.0)   # clear of the motor (x -19.5..16.5 above the deck), receiver box (x -50.5..-30.9, y <= -68) and rail brackets
LAP_SCREW = ('ISO 10642', 'M3x10')
LAP_INSERT = 'M3x4'
LAP_BOSS_D, LAP_BOSS_H = 8.0, 4.5        # boss above the deck top: insert pocket 5 deep leaves a 2.4 mm floor over the lap face, screw tip 0.5 below the top


def _half_space(n, c, big=400.0):
    """A thick slab on the material side of the plane through c whose outward normal is n."""
    return cq.Workplane(cq.Plane(origin=c, xDir=V(1, 0, 0), normal=n * -1.0)).rect(big, big).extrude(big).val()


def _main_plane(deck, sign):
    """(normal, point) of the plane with the largest total face area whose normal points to sign * z."""
    bins = {}
    for f in deck.Faces():
        c = f.Center()
        try:
            n = f.normalAt(c)
        except Exception:
            continue
        if n.z * sign < 0.98: continue
        key = (round(n.x, 2), round(n.y, 2), round(n.dot(c), 0))
        a, _, _ = bins.get(key, (0.0, None, None))
        bins[key] = (a + f.Area(), n, c)
    assert bins, 'front deck has no flat face toward %+d z' % sign
    a, n, c = max(bins.values(), key=lambda q: q[0])
    return n, c


def make_flat_deck(deck, rear=None):
    """rear: the rear deck solid. The slab then ends on the plane of its front face (a butt seam; cutting the rear deck out of a slab with a
    vertical end left a 0.4 mm lip over the seam, because the front deck lies 0.9 mm higher)."""
    bb = deck.BoundingBox()
    nt, ct = _main_plane(deck, 1)
    nb, cb = _main_plane(deck, -1)
    # plan outline: half width at stations along y (1 mm steps over the first and last 20 mm, where the corners are bevelled)
    ys = [bb.ymin + 0.05] + [bb.ymin + k for k in range(1, 21)] + [bb.ymax - k for k in range(20, 0, -1)] + [bb.ymax - 0.05]
    half = []
    for y in ys:
        sec = deck.intersect(cq.Solid.makeBox(bb.xlen + 2, 0.1, bb.zlen + 2, V(bb.xmin - 1, y - 0.05, bb.zmin - 1)))
        if sec.Volume() > 1e-6:
            sb = sec.BoundingBox(); half.append((min(max(abs(sb.xmin), abs(sb.xmax)), 54.5), y))
    if rear is not None: half.append((half[-1][0], bb.ymax + 3.0))       # runs past the seam plane, which cuts the end face
    pts = half + [(-x, y) for x, y in reversed(half)]
    prism = cq.Workplane('XY', origin=(0, 0, bb.zmin - 20)).polyline(pts).close().extrude(bb.zlen + 40).val()
    slab = prism.intersect(_half_space(nt, ct)).intersect(_half_space(nb, cb)).clean()
    if rear is not None:
        ff = max((f for f in rear.Faces() if f.geomType() == 'PLANE' and f.normalAt(f.Center()).y < -0.9 and f.Center().y < rear.BoundingBox().ymin + 2.0),
                 key=lambda f: f.Area())
        slab = slab.intersect(_half_space(ff.normalAt(ff.Center()) * -1.0, ff.Center())).clean()
        assert slab.intersect(rear).Volume() < 0.01, 'flat front deck overlaps the rear deck'
    assert slab.isValid() and len(slab.Solids()) == 1, 'flat front deck is not one valid solid'
    t = (ct - cb).dot(nt)
    print('flat front deck: thickness %.2f mm, top normal (%.3f, %.3f, %.3f), volume %.0f -> %.0f mm3' % (t, nt.x, nt.y, nt.z, deck.Volume(), slab.Volume()))
    assert 2.0 < t < 20.0, 'front deck planes not found (thickness %.2f)' % t
    return slab


def lap_skid(deck, skid):
    """Stepped lap between the skid and the flat deck. The skid stand-in has a 3 mm mounting flange that runs under the deck's front edge. The deck
    lies 0.9 mm above the flange's underside, so cutting the plain slab out of the skid left a 0.9 mm sheet with four old holes under the deck.
    The flange is rebuilt as a plain plate with the old footprint, underside and top, let into the underside of the deck by its upper 2.1 mm, with
    two M3 screws from below (clearance holes in the flange, pilot holes through the deck). Returns (deck, skid)."""
    nb, cb = _main_plane(deck, -1)
    yf = deck.BoundingBox().ymin
    sb = skid.BoundingBox()
    behind = cq.Solid.makeBox(sb.xlen + 2, sb.ymax - yf + 1.0, sb.zlen + 2, V(sb.xmin - 1, yf, sb.zmin - 1))
    old = skid.intersect(cq.Solid.makeBox(sb.xlen + 2, sb.ymax - yf, sb.zlen + 2, V(sb.xmin - 1, yf + 0.5, sb.zmin - 1)))
    assert old.Volume() > 10.0, 'skid has no flange behind the front edge of the deck'
    ob = old.BoundingBox(); hx = min(abs(ob.xmin), abs(ob.xmax))
    ns, cs = _main_plane(old, -1)                                  # underside and top of the flange
    nu, cu = _main_plane(old, 1)
    body = max(skid.cut(behind).Solids(), key=lambda q: q.Volume())
    # from 2.5 mm ahead of the deck's front edge (inside the root of the nose plate; also closes what is left there of two old holes on the edge)
    flange = cq.Solid.makeBox(2 * hx, ob.ymax - yf + 2.5, sb.zlen + 40, V(-hx, yf - 2.5, sb.zmin - 20)).intersect(_half_space(ns, cs)).intersect(_half_space(nu, cu))
    skid2 = body.fuse(flange).clean()
    deck2 = deck.cut(skid2).clean()                                # recess for the plain flange, before the holes are drilled
    for x, dy in SKID_SCREWS:
        skid2 = skid2.cut(cq.Solid.makeCylinder(SKID_SCREW_D / 2, sb.zlen + 40, V(x, yf + dy, sb.zmin - 20), V(0, 0, 1)))
    assert skid2.isValid() and len(skid2.Solids()) == 1, 'skid flange is not one valid solid'
    for x, dy in SKID_SCREWS:
        deck2 = deck2.cut(cq.Solid.makeCylinder(SKID_PILOT_D / 2, sb.zlen + 40, V(x, yf + dy, sb.zmin - 20), V(0, 0, 1)))
    assert deck2.isValid() and len(deck2.Solids()) == 1, 'skid lap broke the flat deck'
    t, lap = (cs - cu).dot(ns), (cb - cu).dot(nb)
    assert t > 2.0 and 1.0 < lap < t and (deck.Volume() - deck2.Volume()) > 500.0, 'skid flange does not lap the deck (flange %.2f, lap %.2f)' % (t, lap)
    print('skid lap: flange %.1f x %.1f mm, %.2f mm thick, %.2f mm of it in the deck; skid mm3 %.0f -> %.0f' % (2 * hx, ob.ymax - yf, t, lap, skid.Volume(), skid2.Volume()))
    return deck2, skid2


def lap_decks(front, rear):
    """Full-thickness half lap between the flat front deck (ending on the plane of the rear deck's front face, make_flat_deck) and the rear deck.
    Both decks share their top and bottom planes. The front deck keeps its upper half back to LAP_BEHIND behind the old face, the rear deck grows
    its lower half forward to LAP_AHEAD ahead of it; LAP_END_GAP at both tongue ends, LAP_FACE_GAP between the lap faces. The decks were held only
    by the cage feet, so the lap gets four M3 countersunk screws from below into heat-set inserts in bosses on top of the front deck's tongue.
    The rear deck's two leftover open-ended slots of the old layout at its front edge (x -22 and +31, through slot with a head recess from below,
    nothing uses them) lie in the lap: the front 8.4 mm of the rear deck is filled to the plain slab first. Returns (front, rear)."""
    from soma.fasteners import Screw, HeatSetInsert
    from parts.deck import _unify_deck
    nt, ct = _main_plane(front, 1)
    nb, cb = _main_plane(front, -1)
    nt2, ct2 = _main_plane(rear, 1)
    nb2, cb2 = _main_plane(rear, -1)
    t = (ct - cb).dot(nt)
    assert (nt - nt2).Length < 1e-3 and abs((ct2 - ct).dot(nt)) < 0.02 and abs((cb2 - cb).dot(nt)) < 0.02, 'front and rear deck do not share their planes'
    rb = rear.BoundingBox()
    ff = max((f for f in rear.Faces() if f.geomType() == 'PLANE' and f.normalAt(f.Center()).y < -0.9 and f.Center().y < rb.ymin + 2.0), key=lambda f: f.Area())
    d = V(0, nt.z, -nt.y).normalized()                              # along the deck plane toward the rear
    assert (ff.normalAt(ff.Center()) + d).Length < 1e-2, 'rear deck front face is not square to the deck plane'
    fc = ff.Center()
    c0 = V(0, fc.y, fc.z) - nt * ((fc - ct).dot(nt) + t / 2)        # on the mid plane, on the old seam, x 0
    at = lambda a: c0 + d * a
    hx = min(-front.BoundingBox().xmin, front.BoundingBox().xmax, -rb.xmin, rb.xmax)
    slab = cq.Solid.makeBox(2 * hx, 600, 200, V(-hx, -300, -100)).intersect(_half_space(nt, ct)).intersect(_half_space(nb, cb))
    s_le = lambda a: _half_space(d, at(a))                         # s <= a
    s_ge = lambda a: _half_space(d * -1.0, at(a))                  # s >= a
    above = lambda h: _half_space(nt * -1.0, c0 + nt * h)          # above the plane h over the mid plane
    below = lambda h: _half_space(nt, c0 + nt * h)
    a0, a1, g, gh = -LAP_AHEAD, LAP_BEHIND, LAP_END_GAP, LAP_FACE_GAP
    # rear deck: front 8.4 mm filled to the plain slab (the old slots end 8.2 behind the face), lower tongue forward to a0 + g, upper half cut back to a1
    v_r0 = rear.Volume()
    r = rear.fuse(slab.intersect(s_ge(0.0)).intersect(s_le(8.4))).clean()
    plug = r.Volume() - v_r0
    assert 250.0 < plug < 600.0, 'rear deck front edge fill is not the two old slots (%.0f mm3)' % plug
    r = r.fuse(slab.intersect(s_ge(a0 + g)).intersect(s_le(0.5)).intersect(below(-gh / 2))).clean()
    r = r.cut(s_le(a1).intersect(above(-gh / 2))).clean()
    # front deck: lower half cut back to a0, upper tongue back to a1 - g
    f = front.cut(s_ge(a0).intersect(below(gh / 2))).clean()
    f = f.fuse(slab.intersect(s_ge(-0.5)).intersect(s_le(a1 - g)).intersect(above(gh / 2))).clean()
    # screws: axis square to the deck plane; local frame z 0 on the deck top, +z up
    for x in LAP_SCREW_X:
        loc = cq.Location(cq.Plane(origin=(at(-LAP_SCREW_AHEAD) + nt * (t / 2) + V(x, 0, 0)).toTuple(), xDir=(1, 0, 0), normal=nt.toTuple()))
        boss = cq.Solid.makeCylinder(LAP_BOSS_D / 2, LAP_BOSS_H + 0.5, V(0, 0, -0.5), V(0, 0, 1)).moved(loc)
        f = f.fuse(boss).clean()
        f = f.cut(cq.Solid.makeCylinder(INSERT_M3_D / 2, 6.5, V(0, 0, LAP_BOSS_H - 6.0), V(0, 0, 1)).moved(loc))   # M3 x 4 insert (OD 4.2), 6 deep as before
        sc = Screw(LAP_SCREW[0], LAP_SCREW[1], at=(0, 0, -t), direction='+Z')
        assert t + 2.0 <= sc.length <= t + LAP_BOSS_H, 'lap screw length does not suit the insert'
        hole = sc.clearance_hole().moved(loc)
        f, r = f.cut(hole), r.cut(hole)
    f, r = _unify_deck(f.clean()), _unify_deck(r.clean())
    for nm, q in (('front', f), ('rear', r)):
        assert q.isValid() and len(q.Solids()) == 1, 'deck lap broke the %s deck' % nm
    assert f.intersect(r).Volume() < 0.01, 'lapped decks overlap'
    gap = f.distance(r)
    assert gap > 0.15, 'lapped decks touch (%.3f mm)' % gap
    print('deck lap: %.1f mm long (%.1f overlap), tongues %.2f mm, gaps %.2f end / %.2f face (min %.3f), %d x %s %s + insert %s, rear slots filled %.0f mm3; '
          'front mm3 %.0f -> %.0f, rear %.0f -> %.0f' % (a1 - a0, a1 - a0 - 2 * g, (t - gh) / 2, g, gh, gap, len(LAP_SCREW_X), LAP_SCREW[0], LAP_SCREW[1],
                                                          LAP_INSERT, plug, front.Volume(), f.Volume(), v_r0, r.Volume()))
    return f, r
