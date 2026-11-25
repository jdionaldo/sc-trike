"""Magnetic power connection for the front and rear lights (lights themselves are not modelled yet).

Per end: a PETG contact bridge spans the frame rails above all the componentry, the shell carries a matching
contact block hung from its roof. Two 6 x 3 mm magnets per end (plus and minus) sit on the centre line, one each side of x = 0,
and touch face to face with a 0.3 mm glue-gap-sized clearance (assumed, the lighting wires are soldered to the magnets
or to contact pads: magnet polarity must alternate so the blocks can only be joined one way round).
"""
import json, os
import cadquery as cq
from parts.params import *

_RAIL = dict((y, z) for y, z in json.load(open(os.path.join(os.path.dirname(__file__), 'relief.json')))['rail'])
_ENV = dict((y, z) for y, z in json.load(open(os.path.join(os.path.dirname(__file__), 'relief.json')))['envelope'])

LIGHT_FRONT_Y = param(-215.0, 'Front light connector, Y position', min=-245.0, max=-180.0, step=1.0, unit='mm', group='Light connectors')
LIGHT_REAR_Y = param(2.0, 'Rear light connector, Y position (under the B-pillar roof)', min=-10.0, max=4.0, step=1.0, unit='mm', group='Light connectors')
LIGHT_MAGNET_D = param(6.0, 'Magnet diameter', min=4.0, max=10.0, step=1.0, unit='mm', group='Light connectors')
LIGHT_MAGNET_T = param(3.0, 'Magnet thickness', min=2.0, max=5.0, step=0.5, unit='mm', group='Light connectors')
LIGHT_SPACING = param(16.0, 'Distance between plus and minus magnet', min=10.0, max=30.0, step=1.0, unit='mm', group='Light connectors')
LIGHT_CLEAR = 12.0     # mm: bridge deck above the highest chassis part at that station
LIGHT_GAP = 0.3        # mm: gap between the two contact blocks
POCKET_CLEAR = 0.2     # mm: pocket diameter above the magnet
PLATE_T, PLATE_Y = 5.0, 16.0

def _at(table, y):
    k = int(round(y / 10.0)) * 10
    return table[k]

def _pockets(z_face, direction):
    """Two magnet pockets, opening at z_face; direction +1 = open upward, -1 = open downward."""
    out = None
    for sx in (-1, 1):
        d = LIGHT_MAGNET_D + POCKET_CLEAR
        z0 = z_face - LIGHT_MAGNET_T if direction > 0 else z_face
        p = cq.Workplane('XY').workplane(offset=z0).center(sx * LIGHT_SPACING / 2, 0).circle(d / 2).extrude(LIGHT_MAGNET_T)
        out = p if out is None else out.union(p)
    return out

def make_connector(y, roof_z, name, leg_x, z_foot, legs=True, roof=None):
    """y: final frame. Bridge legs stand at x = +-leg_x from z_foot up to the contact deck. Returns (bridge, block, z_deck)."""
    yc = y - CHASSIS_Y
    c = int(round(yc / 10.0)) * 10
    z_deck = max(_ENV[k] for k in (c - 10, c, c + 10) if _ENV.get(k) is not None) + CHASSIS_Z + LIGHT_CLEAR   # top face of the bridge plate
    w = leg_x + 4.0
    bridge = cq.Workplane('XY').box(2 * w, PLATE_Y, PLATE_T, centered=(True, True, False)).translate((0, y, z_deck - PLATE_T))
    for sx in ((-1, 1) if legs else ()):
        leg = cq.Workplane('XY').box(8, PLATE_Y, z_deck - z_foot, centered=(True, True, False)).translate((sx * leg_x, y, z_foot))
        bridge = bridge.union(leg)
    bridge = bridge.cut(_pockets(z_deck, +1).translate((0, y, 0)))
    z_blk = z_deck + LIGHT_GAP
    block = cq.Workplane('XY').box(LIGHT_SPACING + LIGHT_MAGNET_D + 8, PLATE_Y, PLATE_T, centered=(True, True, False)).translate((0, y, z_blk))
    cap=[]
    if roof is not None:
        from parts.util import hull
        heights={(x,dy):roof_underside(roof,y+dy,90.0,x) for x in (-6,0,6) for dy in (-6,0,6)}
        assert all(z is not None for z in heights.values()), name+' contact extends beyond roof'
        roof_z=min(heights.values())
        bottom=roof_z-LIGHT_GAP-0.25
        for x in (-6,0):
            for dy in (-6,0):
                q=[(x,dy),(x+6,dy),(x+6,dy+6),(x,dy+6)]
                for tri in ((q[0],q[1],q[2]),(q[0],q[2],q[3])):
                    cap.append(hull([(a,y+b,heights[a,b]-LIGHT_GAP) for a,b in tri]+
                                    [(a,y+b,bottom) for a,b in tri]))
    post = cq.Workplane('XY').box(12, 12, roof_z - LIGHT_GAP - (z_blk + PLATE_T) + 0.01, centered=(True, True, False)).translate((0, y, z_blk + PLATE_T - 0.01))
    for wedge in cap:
        post=post.union(wedge)
    block = block.union(post).cut(_pockets(z_blk, -1).translate((0, y, 0)))
    return bridge.val(), block.val(), z_deck

def roof_underside(shell, y, z_above, x=0.0):
    """Lowest shell material above z_above at station (x, y); None when there is none."""
    sv = shell.val() if hasattr(shell, 'val') else shell
    c = sv.intersect(cq.Solid.makeBox(0.2, 0.2, 400, cq.Vector(x - 0.1, y, z_above)))
    zs = [b.BoundingBox().zmin for b in c.Solids()]
    return min(zs) if zs else None
