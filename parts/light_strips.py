"""Red light strips as separate printed parts (translucent PETG/PLA) that drop into channels in the shell.

Only a peg (5 mm OD, 3 mm bore for a 3 mm LED) passes through the shell wall into the interior. Positions are final-frame
numbers read from the built shell (tools/bbox_parts.py): the rear face of the tail and the raked nose face above the grille.
"""
import math
import cadquery as cq
from soma import param

STRIP_T = 1.6          # mm: plate thickness, flush with the outer face
STRIP_FIT = 0.15       # mm: clearance per side in the channel
PEG_D = 5.0            # mm: peg outer diameter (through the shell)
PEG_BORE = 3.0         # mm: LED hole
PEG_L = 8.0            # mm: peg length behind the outer face
PEG_HOLE = PEG_D + 0.3 # mm: hole in the shell
SHELL_WALL = 3.0       # mm: printed wall behind the channel

# Tail: rear face from the top edge (y 293.6, z 206.3) down to (y 286.0, z 192.0).
from parts.tail import light_face
TAIL_TOP, TAIL_BOT = light_face()
TAIL_HALF = param(38.0, 'Tail light strip half length', min=20.0, max=42.0, step=1.0, unit='mm', group='Light strips')
TAIL_H = 8.0
TAIL_PEG_X = (-8.0, 8.0)
TAIL_PEG_UP = 4.0
TAIL_SOCKET_LEN = 15.0   # mm behind the lens back: 3 mm wall + about 11 mm into the cavity
LENS_OVER_LED = 1.0      # mm of lens left in front of the LED bore (was 0.6)
# Nose: raked face from the top edge (y -307.8, z 109.9) down to the grille top (y -295.4, z 96.8).
NOSE_TOP = (0.0, -307.8, 109.9); NOSE_BOT = (0.0, -295.4, 96.8)
NOSE_HALF = param(32.0, 'Nose light strip half length', min=15.0, max=38.0, step=1.0, unit='mm', group='Light strips')
NOSE_H = 8.0; NOSE_DIP = -2.0
NOSE_PEG_X = (-22.0, 22.0)
NOSE_PEG_L = 4.0
NOSE_SOCKET_REACH = 20.0
NOSE_SOCKET_CUTTERS = []
NOSE_BACKING_MARGIN = 0.5
NOSE_END_WALL = param(3.0, 'Nose light end wall', min=0.0, max=6.0, step=0.5, unit='mm', group='Light strips')   # solid shell left beyond the channel end, so the bar's end is capped by one clean wall (no patch blocks)


def _frame(top, bot, frac=0.5):
    """Plane at the face between two edge points: x = X, outward normal n, 'up the face' t."""
    top = cq.Vector(*top); bot = cq.Vector(*bot)
    t = (top - bot).normalized()
    n = cq.Vector(1, 0, 0).cross(t)           # perpendicular to X and t
    centre = bot + (top - bot)*frac
    return centre, t, n


def _plane(top, bot, outward):
    c, t, n = _frame(top, bot)
    if n.dot(cq.Vector(*outward)) < 0: n = n*-1.0
    return cq.Plane(origin=c, xDir=(1, 0, 0), normal=n.toTuple()), n


def _bar(plane, half, height, dip, z0, z1):
    """Straight (dip 0) or shallow-V bar in the face plane, from local z0 to z1 (z along the outward normal)."""
    if dip == 0:
        pts = [(-half, -height/2), (half, -height/2), (half, height/2), (-half, height/2)]
    else:   # centre dips by `dip` toward -y (down the face)
        pts = [(-half, height/2), (0, height/2 - dip), (half, height/2), (half, -height/2), (0, -height/2 - dip), (-half, -height/2)]
    return cq.Workplane(plane).workplane(offset=z0).polyline(pts).close().extrude(z1 - z0).val()


def _pegs(plane, xs, dips, length=PEG_L):
    out = []
    for x, dy in zip(xs, dips):
        out.append(cq.Workplane(plane).workplane(offset=-length).center(x, dy).circle(PEG_D/2).extrude(length).val())
    return out


def make_strip(top, bot, outward, half, height, dip, peg_xs, peg_length=PEG_L):
    """Returns (strip part with pegs and LED bores, channel + peg-hole cutting tool for the shell)."""
    plane, n = _plane(top, bot, outward)
    g = STRIP_FIT
    dips = [-(dip*(1 - abs(x)/half)) if dip else 0.0 for x in peg_xs]
    plate = _bar(plane, half, height, dip, -STRIP_T, 0.0)
    strip = plate
    for p in _pegs(plane, peg_xs, dips, peg_length): strip = strip.fuse(p)
    for x, dy in zip(peg_xs, dips):
        # Blind LED socket: the full red lens thickness remains over its end.
        strip = strip.cut(cq.Workplane(plane).workplane(offset=-peg_length - 1).center(x, dy).circle(PEG_BORE/2).extrude(peg_length + 1 - STRIP_T).val())
    chan = _bar(plane, half + g, height + 2*g, dip, -STRIP_T - g, 2.0)
    for x, dy in zip(peg_xs, dips):
        chan = chan.fuse(cq.Workplane(plane).workplane(offset=-peg_length - 1).center(x, dy).circle(PEG_HOLE/2).extrude(peg_length + 3).val())
    return strip.clean(), chan.clean()


def make_tail_strip():
    from parts.tail import rear_profile
    from parts.canopy_frame import offset_polygon
    plane,n=_plane(TAIL_TOP,TAIL_BOT,(0,1,-0.3))
    outline=offset_polygon(rear_profile(),-SHELL_WALL)
    # Retain the existing width control while inheriting all eight facets.
    width=max(abs(x) for x,y in outline)
    outline=[(x*TAIL_HALF/width,y) for x,y in outline]
    pocket=offset_polygon(outline,STRIP_FIT)
    def prism(poly,z0,z1):
        return cq.Workplane(plane).workplane(offset=z0).polyline(poly).close().extrude(z1-z0).val()
    strip=prism(outline,-STRIP_T,0)
    chan=prism(pocket,-STRIP_T-STRIP_FIT,2)
    fwd=-cq.Vector(*plane.zDir.toTuple())
    for x in TAIL_PEG_X:
        # Sockets face forward, through the wall behind the lens into the hollow housing.
        base=cq.Vector(*plane.toWorldCoords((x,TAIL_PEG_UP,-STRIP_T)).toTuple())
        peg=cq.Solid.makeCylinder(PEG_D/2,TAIL_SOCKET_LEN,base-fwd*0.2,fwd)
        bore=cq.Solid.makeCylinder(PEG_BORE/2,TAIL_SOCKET_LEN+STRIP_T-LENS_OVER_LED,base+fwd*TAIL_SOCKET_LEN,-fwd)
        hole=cq.Solid.makeCylinder(PEG_HOLE/2,SHELL_WALL+STRIP_FIT+2.0,base-fwd*0.5,fwd)
        strip=strip.fuse(peg).cut(bore)
        chan=chan.fuse(hole)
    strip=strip.clean();chan=chan.clean()
    assert strip.isValid() and len(strip.Solids())==1,'Tail lens must be one solid'
    return strip,chan


NOSE_EDGE_GAP = param(1.0, 'Nose light bar gap below the hood edge', min=0.5, max=4.0, step=0.1, unit='mm', group='Light strips')
NOSE_BAR_H = param(10.0, 'Nose light bar height', min=4.0, max=14.0, step=0.5, unit='mm', group='Light strips')
_NOSE_BACKING = [None]


def nose_path(shell):
    """Hood-top edge chain at the nose (apex at x=0, corners, outer ends) with the outward normal of the face below each segment."""
    hood = [f for f in shell.Faces() if f.normalAt(f.Center()).z > 0.8 and f.Area() > 250 and f.Center().y < -245 and abs(f.Center().x) < 80]
    edges = []
    for f in hood:
        for e in f.Edges():
            if e.Length() < 5 or min(e.startPoint().z, e.endPoint().z) < 104.0: continue
            for g in e.ancestors(shell, 'Face'):
                if g.isSame(f): continue
                n = g.normalAt(g.Center())
                if n.z < 0.6 and n.y < -0.2: edges.append((e, n))
    pts = []
    for e, n in edges:
        for p in (e.startPoint(), e.endPoint()):
            if not any((p - q).Length < 1.5 for q in pts): pts.append(p)
    pts.sort(key=lambda p: p.x)
    segs = []
    for a, b in zip(pts[:-1], pts[1:]):
        mid = (a + b) * 0.5
        best = min(edges, key=lambda en: (en[0].Center() - mid).Length)
        segs.append((a, b, best[1]))
    return pts, segs


NOSE_END_TRIM = 9.0     # mm: the ribbon stops this far before the hood-edge corner at each wing end


def _frames(segs):
    out = []
    for a, b, n in segs:
        e = (b - a).normalized()
        d = n.cross(e).normalized()
        if d.z > 0: d = d * -1.0
        out.append((a, b, n.normalized(), d, e))
    return out


def _line_meet(p0, e0, p1, e1):
    """Midpoint of the closest approach of two 3D lines (they meet exactly when the faces are planar and adjacent)."""
    w = p0 - p1
    A, B, C, D, E = e0.dot(e0), e0.dot(e1), e1.dot(e1), e0.dot(w), e1.dot(w)
    den = A * C - B * B
    if abs(den) < 1e-9: return p0
    s = (B * E - C * D) / den; t = (A * E - B * D) / den
    return ((p0 + e0 * s) + (p1 + e1 * t)) * 0.5


def ribbon(segs, d0, h, t_back, t_front, trim=0.0):
    """One continuous band along the hood-top edge chain: its top edge d0 below the edge and its bottom d0+h below it (measured down each
    face), from t_back behind the outer face to t_front in front of it. The top and bottom lines are mitred at every corner, so the outer
    surface is one unbroken skin (no wedges), and the wing ends are pulled back by `trim`."""
    from parts.util import hull
    fr = _frames(segs)
    def line_pts(off):
        pts = []
        for i, (a, b, n, d, e) in enumerate(fr):
            pa = a + d * off; pb = b + d * off
            if i == 0: pa = pa + e * trim
            if i == len(fr) - 1: pb = pb - e * trim
            pts.append((pa, pb))
        v = [pts[0][0]]
        for i in range(len(fr) - 1):
            v.append(_line_meet(pts[i][0], fr[i][4], pts[i + 1][0], fr[i + 1][4]))
        v.append(pts[-1][1])
        return v
    top, bot = line_pts(d0), line_pts(d0 + h)
    pieces = []
    for i, (a, b, n, d, e) in enumerate(fr):
        P = [top[i], top[i + 1], bot[i], bot[i + 1]]
        pieces.append(hull([p.toTuple() for p in P] + [(p - n * t_back + n * 0.0).toTuple() for p in P] + [(p + n * t_front).toTuple() for p in P]))
    for i in range(len(fr) - 1):       # corner filler: both inner offsets at the shared mitre points
        P = [top[i + 1], bot[i + 1]]
        pts = []
        for q in P:
            for k in (i, i + 1): pts += [q.toTuple(), (q - fr[k][2] * t_back).toTuple(), (q + fr[k][2] * t_front).toTuple()]
        try: pieces.append(hull(pts))
        except Exception: pass          # flat corner (both faces coplanar): the segment pieces already meet on the mitre line
    out = pieces[0]
    for pc in pieces[1:]: out = out.fuse(pc)
    return out.clean()


def _path_point(frames, x):
    for a, b, n, d in frames:
        if a.x - 1e-6 <= x <= b.x + 1e-6:
            s = (x - a.x) / (b.x - a.x)
            return a + (b - a) * s, n, d
    raise ValueError('x outside nose path')


def make_nose_strip(shell):
    """The nose light is ONE ribbon that follows the hood-top edge around the nose at a constant gap below it (measured down the face).
    Returns (strip, channel); the opaque backing behind it is nose_backing()."""
    pts, segs = nose_path(shell)
    assert len(segs) >= 3, 'hood edge chain not found'
    h, g = NOSE_BAR_H, NOSE_EDGE_GAP
    strip = ribbon(segs, g, h, STRIP_T, 0.0, NOSE_END_TRIM)
    chan = ribbon(segs, g - STRIP_FIT, h + 2 * STRIP_FIT, STRIP_T + STRIP_FIT, 1.5, NOSE_END_TRIM - STRIP_FIT)
    back = ribbon(segs, g - STRIP_FIT - NOSE_BACKING_MARGIN, h + 2 * (STRIP_FIT + NOSE_BACKING_MARGIN),
                  STRIP_T + STRIP_FIT + SHELL_WALL, -(STRIP_T + STRIP_FIT), NOSE_END_TRIM - STRIP_FIT - NOSE_END_WALL)
    # nothing of the backing may stand above the hood skin
    for f in shell.Faces():
        c = f.Center()
        if f.normalAt(c).z > 0.8 and f.Area() > 250 and c.y < -245 and abs(c.x) < 80:
            up = f.normalAt(c)
            back = back.cut(cq.Solid.extrudeLinear(f, up * 60.0).translate(up * -0.3))
    big = [x for x in back.Solids() if x.Volume() > 1.0]
    back = big[0] if len(big) == 1 else cq.Compound.makeCompound(big)
    _NOSE_BACKING[0] = back
    # LED pegs: horizontal cylinders from the back of the bar into sockets in the backing
    NOSE_SOCKET_CUTTERS.clear()
    frames = []
    for a, b, n in segs:
        e = (b - a).normalized(); d = n.cross(e).normalized()
        if d.z > 0: d = d * -1.0
        frames.append((a, b, n.normalized(), d))
    for x in NOSE_PEG_X:
        P, n, d = _path_point(frames, x)
        base = P + d * (g + h / 2) - n * 0.5
        direction = cq.Vector(0, 1, 0)
        peg = cq.Solid.makeCylinder(PEG_D / 2, NOSE_SOCKET_REACH, base, direction)
        bore = cq.Solid.makeCylinder(PEG_BORE / 2, NOSE_SOCKET_REACH, base + direction * STRIP_T, direction)
        hole = cq.Solid.makeCylinder(PEG_HOLE / 2, NOSE_SOCKET_REACH + 3, base - direction, direction)
        strip = strip.fuse(peg, tol=1e-5).cut(bore)
        NOSE_SOCKET_CUTTERS.append(hole)
    from parts.util import weld
    strip = weld(strip.clean(), 'Nose light strip'); chan = chan.clean()
    assert strip.isValid() and len(strip.Solids()) == 1, 'Nose light must be one solid'
    assert chan.isValid(), 'Invalid nose light channel'
    return strip, chan


def nose_backing():
    """Opaque inner wall behind the ribbon; only the LED sockets pierce it."""
    return _NOSE_BACKING[0]


# --- Tail housing screws: two countersunk M3 screws behind the red lens, into heat-set inserts in stubs on the rear cross tube ---
TAIL_SCREW_X = 16.0      # mm from the centre line: clear of the LED sockets (x 8) and the frame saddles (x 22)
TAIL_SCREW_V = -1.0      # mm along the lens face from its centre (+ is down): keeps the stub above the housing floor
SCREW_D = 3.4            # M3 clearance
CSK_D = 6.3              # countersink diameter at the seat floor (M3 flat head 5.7 + clearance)
INSERT_D, INSERT_DEPTH = 4.2, 5.0   # M3 heat-set insert pocket (insert OD 4.6 x 4 mm long)
TAIL_PAD_R, TAIL_PAD_L = 4.5, 3.5   # boss on the inside of the housing wall under the screw head
TAIL_STUB_R = 4.0        # mm: stub on the cross tube
HEAD_UNDER = 0.4         # mm: the screw head's highest point stays this far under the lens seat floor
TAIL_SCREW_INFO = {}


def make_tail_screws():
    """Returns {'pads': [solids to fuse into the housing], 'cuts': [hole + countersink to cut from it], 'cage': [(stub, insert pocket)]}.
    The lens sits in its seat over the countersunk screw heads (heads HEAD_UNDER below the seat floor)."""
    from parts.params import WALL_PRINT, GLUE_GAP
    from parts.cage import CAGE_BEAM, REAR_SUP_X
    from parts.tail import TUBE_END_SETBACK
    from parts.util import hull
    plane, n = _plane(TAIL_TOP, TAIL_BOT, (0, 1, -0.3))
    end = (REAR_SUP_X, round(TAIL_TOP[1] - TUBE_END_SETBACK, 1), round(TAIL_TOP[2] - WALL_PRINT - CAGE_BEAM/2 - GLUE_GAP, 1))
    floor_w = -(STRIP_T + STRIP_FIT)                   # seat floor (local w, along the outward normal)
    wall_w = floor_w - SHELL_WALL                       # inner face of the housing wall
    out = {'pads': [], 'cuts': [], 'cage': []}
    for sx in (-1, 1):
        S = cq.Vector(*plane.toWorldCoords((sx*TAIL_SCREW_X, TAIL_SCREW_V, floor_w)).toTuple())
        C = cq.Vector(sx*TAIL_SCREW_X, end[1], end[2])   # axis of the rear cross tube
        d = (C - S).normalized()
        t_wall = (wall_w - floor_w) / d.dot(n)           # axial distance from seat floor to the inner wall face
        P0 = S + d*t_wall
        # The screw axis is tilted against the seat floor (about 33 degrees). The boss starts inside the wall, far enough out that its whole start
        # face is in the wall (it used to start square to the axis 0.6 mm inside, which left a wedge-shaped slot between boss and wall above the screw).
        ct = -d.dot(n); st = math.sqrt(1.0 - ct*ct)
        e = TAIL_PAD_R*st/ct
        pad = cq.Solid.makeCylinder(TAIL_PAD_R, e + t_wall + TAIL_PAD_L, S - d*e, d)
        keep = cq.Workplane(plane).workplane(offset=-14.0).rect(400, 400).extrude(14.0 + floor_w - 0.4).val()
        out['pads'].append(pad.intersect(keep))
        # Head pocket: the countersink sits so deep that the whole head is HEAD_UNDER below the seat floor (the lens lies on the floor). Above the
        # head the pocket is the head circle swept from the screw axis round to the floor normal, so its wall meets the floor at 90 degrees or more
        # (the old cone started square to the axis and undercut the floor: a feather of 0 mm).
        r = CSK_D/2
        sink = (r*st + HEAD_UNDER)/ct                       # along the axis, seat floor to the head's top face
        H = S + d*sink
        xv = cq.Vector(1, 0, 0)
        pocket = cq.Solid.makeCylinder(r, 8.0, H, -d).fuse(
            cq.Solid.extrudeLinear(cq.Face.makeFromWires(cq.Wire.makeCircle(r, H, d)), n*8.0),
            hull([(q + xv*(sg*r)).toTuple() for q in (H, H - d*8.0, H + n*8.0) for sg in (-1, 1)])).clean()
        pocket = pocket.intersect(cq.Workplane(plane).workplane(offset=-14.0).rect(400, 400).extrude(14.0 + floor_w + 0.3).val())
        hole = cq.Solid.makeCylinder(SCREW_D/2, t_wall + TAIL_PAD_L + 1.0 - sink, H - d*0.1, d)
        csk = cq.Solid.makeCone(r, SCREW_D/2 - 0.2, r + 0.2 - SCREW_D/2, H - d*0.2, d)   # starts in the pocket: a 0.2 mm ledge rings the cone at the pocket floor
        out['cuts'] += [pocket, hole, csk]
        # stub from the tube to just short of the boss (0.1 mm gap, the screw closes it), insert pocket in its end
        P1 = P0 + d*(TAIL_PAD_L + 0.1)
        stub = cq.Solid.makeCylinder(TAIL_STUB_R, (C - P1).Length, C, -d)           # from the tube axis out to P1
        pocket = cq.Solid.makeCylinder(INSERT_D/2, INSERT_DEPTH, P1 - d*0.01, d)      # insert pocket from the stub end toward the tube
        out['cage'].append((stub, pocket))
        TAIL_SCREW_INFO[sx] = {'seat_point': S.toTuple(), 'axis': d.toTuple(), 'head_sink': round(sink, 2),
                               'screw_axial_to_insert_bottom': round(t_wall + TAIL_PAD_L + 0.1 + INSERT_DEPTH - sink, 1),   # from the head's top face: M3 x 8 countersunk
                               'tilt_deg': round(math.degrees(math.acos(-d.dot(n))), 1)}
    return out
