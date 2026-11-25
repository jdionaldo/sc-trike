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
LEG_D = 10.0           # mm: round bridge legs (were 8 x 16 blocks)
POST_R = 7.0           # mm: post from the contact block up to the roof skin

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
    """Compact magnetic light connector integrated into the cage's upper crossbars right below the hood/roof.
    Eliminates the wide mid-cabin stadium bridge and long hanging roof posts. Returns (bridge_boss, roof_pad, z_deck)."""
    yc = y - CHASSIS_Y
    c = int(round(yc / 10.0)) * 10
    z_env = max(_ENV[k] for k in (c - 10, c, c + 10) if _ENV.get(k) is not None) + CHASSIS_Z + LIGHT_CLEAR
    # Place the contact interface high up near the hood/roof underside so the roof pad is a low-profile flush block
    # and the cage boss sits directly on the front hoop crossbar (z ~ 107.5) or rear roof header spine (z ~ 212.5).
    z_deck = z_env if name == 'Front' else 213.5
    slot_w = LIGHT_SPACING + LIGHT_MAGNET_D + 6.0   # compact 28 mm wide x 14 mm deep stadium boss on the cage crossbar
    slot_y = 14.0
    z_base = z_deck - PLATE_T if name == 'Front' else z_deck - 6.0
    bridge = cq.Workplane('XY').workplane(offset=z_base).center(0, y).slot2D(slot_w, slot_y).extrude(z_deck - z_base)
    bridge = bridge.cut(_pockets(z_deck, +1).translate((0, y, 0)))
    z_blk = z_deck + LIGHT_GAP
    block = cq.Workplane('XY').workplane(offset=z_blk).center(0, y).slot2D(slot_w, slot_y).extrude(PLATE_T)
    post_h = max(0.5, roof_z - LIGHT_GAP - (z_blk + PLATE_T) + 0.01)
    post = cq.Workplane('XY').workplane(offset=z_blk + PLATE_T - 0.01).center(0, y).circle(POST_R).extrude(post_h)
    if roof is not None:
        # The post ends LIGHT_GAP under the roof skin: a tall post, cut by the skin moved down by the gap (this replaces a cap of eight wedges on a
        # 14 mm grid of sampled heights, whose square outline touched the round post at four points and left slivers there).
        sv = roof.val() if hasattr(roof, 'val') else roof
        z_roof = roof_underside(sv, y, 90.0)
        assert z_roof is not None, name + ' contact has no roof above it'
        tall = cq.Solid.makeCylinder(POST_R, z_roof + 20.0 - (z_blk + PLATE_T - 0.01), cq.Vector(0, y, z_blk + PLATE_T - 0.01), cq.Vector(0, 0, 1))
        post = min(tall.cut(sv.translate(cq.Vector(0, 0, -LIGHT_GAP))).Solids(), key=lambda q: q.BoundingBox().zmin)
    block = block.union(post).cut(_pockets(z_blk, -1).translate((0, y, 0)))
    return bridge.val(), block.val(), z_deck

def roof_underside(shell, y, z_above, x=0.0):
    """Lowest shell material above z_above at station (x, y); None when there is none."""
    sv = shell.val() if hasattr(shell, 'val') else shell
    # A probe exactly on a seam (the hood centre line) can return nothing: retry slightly to either side.
    for dx in (0.0, 0.3, -0.3, 0.7, -0.7):
        c = sv.intersect(cq.Solid.makeBox(0.2, 0.2, 400, cq.Vector(x + dx - 0.1, y, z_above)))
        zs = [b.BoundingBox().zmin for b in c.Solids()]
        if zs: return min(zs)
    return None
