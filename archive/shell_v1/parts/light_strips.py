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
# Nose: raked face from the top edge (y -307.8, z 109.9) down to the grille top (y -295.4, z 96.8).
NOSE_TOP = (0.0, -307.8, 109.9); NOSE_BOT = (0.0, -295.4, 96.8)
NOSE_HALF = param(32.0, 'Nose light strip half length', min=15.0, max=38.0, step=1.0, unit='mm', group='Light strips')
NOSE_H = 8.0; NOSE_DIP = -2.0
NOSE_PEG_X = (-22.0, 22.0)
NOSE_PEG_L = 4.0
NOSE_SOCKET_REACH = 20.0
NOSE_SOCKET_CUTTERS = []
NOSE_BACKING_MARGIN = 0.5


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
        bore=cq.Solid.makeCylinder(PEG_BORE/2,TAIL_SOCKET_LEN+1,base+fwd*TAIL_SOCKET_LEN,-fwd)
        hole=cq.Solid.makeCylinder(PEG_HOLE/2,SHELL_WALL+STRIP_FIT+2.0,base-fwd*0.5,fwd)
        strip=strip.fuse(peg).cut(bore)
        chan=chan.fuse(hole)
    strip=strip.clean();chan=chan.clean()
    assert strip.isValid() and len(strip.Solids())==1,'Tail lens must be one solid'
    return strip,chan


def make_nose_strip(cap_edges=None):
    strip,chan=make_strip(NOSE_TOP, NOSE_BOT, (0, -1, -0.3), NOSE_HALF, NOSE_H, NOSE_DIP, (), NOSE_PEG_L)
    NOSE_SOCKET_CUTTERS.clear()
    # Short face-normal roots turn into horizontal sockets below the hood.
    # Long inclined pegs would break through the sloping hood exterior.
    socket_plane,outward=_plane(NOSE_TOP,NOSE_BOT,(0,-1,-0.3))
    for x in NOSE_PEG_X:
        dy=-NOSE_DIP*(1-abs(x)/NOSE_HALF)
        base=socket_plane.toWorldCoords((x,dy,-1.0))
        direction=cq.Vector(0,1,0)
        peg=cq.Solid.makeCylinder(PEG_D/2,NOSE_SOCKET_REACH,base,direction)
        bore=cq.Solid.makeCylinder(PEG_BORE/2,NOSE_SOCKET_REACH,base+direction*STRIP_T,direction)
        hole=cq.Solid.makeCylinder(PEG_HOLE/2,NOSE_SOCKET_REACH+3,base-direction,direction)
        strip=strip.fuse(peg,tol=1e-5).cut(bore)
        NOSE_SOCKET_CUTTERS.append(hole)
    behind_face=cq.Workplane(socket_plane).rect(500,500).extrude(-200).val()
    strip=strip.intersect(behind_face).clean()
    if cap_edges:
        from parts.util import hull
        from parts.shell_geometry import clearance_hull
        plane,n=_plane(NOSE_TOP,NOSE_BOT,(0,-1,-0.3))
        for side,(corner,outer) in cap_edges.items():
            # Follow the real closing-panel upper edge, below its hood seam.
            upper=[cq.Vector(*plane.toWorldCoords((side*NOSE_HALF,NOSE_H/2,0)).toTuple()),
                   corner-cq.Vector(0,0,1.2),outer-cq.Vector(0,0,1.2)]
            lower=[upper[0]-cq.Vector(*plane.yDir.toTuple())*NOSE_H,
                   upper[1]-cq.Vector(0,0,NOSE_H),upper[2]-cq.Vector(0,0,NOSE_H)]
            # One convex piece per wing: both facets, their inner faces and the root hull together, so no slivers or knuckle seams remain.
            allp=[]
            for i in range(2):
                points=[upper[i],upper[i+1],lower[i],lower[i+1]]
                normal=(upper[i+1]-upper[i]).cross(lower[i]-upper[i]).normalized()
                if normal.dot(cq.Vector(-side,1,0))<0:normal=normal*-1
                allp.extend(points+[p+normal*STRIP_T for p in points])
            # Overlap the front lens on both sides of the corner so the wing is one printable solid with it.
            root=[]
            for p in (upper[0],lower[0]):
                root.extend([p-cq.Vector(side,0,0),p-cq.Vector(side,0,0)-n*STRIP_T])
            root.extend(q for q in allp[:8] if min((q-upper[0]).Length,(q-lower[0]).Length)<STRIP_T+0.1)
            root.extend([upper[0]+(upper[1]-upper[0])*0.05,lower[0]+(lower[1]-lower[0])*0.05])
            blocks=[hull([p.toTuple() for p in allp+root])]
            for block in blocks:
                strip=strip.fuse(block,tol=1e-5)
                chan=chan.fuse(clearance_hull([v.toTuple() for v in block.Vertices()],STRIP_FIT),tol=1e-5)
    from parts.util import weld
    strip=weld(strip.clean(),'Nose light strip');chan=chan.clean()
    assert strip.isValid() and len(strip.Solids())==1,'Nose light must be one solid'
    assert chan.isValid(),'Invalid nose light channel'
    return strip,chan


def nose_backing():
    """Opaque inner wall behind the chevron; only the LED sockets pierce it."""
    plane,n=_plane(NOSE_TOP,NOSE_BOT,(0,-1,-0.3))
    return _bar(plane,NOSE_HALF+NOSE_BACKING_MARGIN,NOSE_H+2*NOSE_BACKING_MARGIN,
                NOSE_DIP,-STRIP_T-STRIP_FIT-SHELL_WALL,-STRIP_T-STRIP_FIT)
