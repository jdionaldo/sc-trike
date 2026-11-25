"""Cage feet in the tub (November 21): a pocket in the deck under each cage foot and a socket that the foot slots into before the
M3 screw goes in from under the deck.

- Pocket: the foot's chamfered square section grown by FOOT_CLEAR, down to the foot end (FOOT_SEAT below the deck top).
- Front feet (front deck, no side walls): an octagonal collar SOCKET_WALL thick, SOCKET_H_FRONT above the deck.
- Rail feet (rear deck, inside the debris walls): a bracket block from the foot to the side wall, keyed 1 mm into the wall, so the
  socket is tied to the side of the tub; SOCKET_H_RAIL high.
Everything is built in the deck's own frame (chassis_ref.step), like the screw holes in model.py.
"""
import cadquery as cq
from parts.cage import _tube_profile, CAGE_BEAM, FOOT_CLEAR, SOCKET_WALL, SOCKET_H_FRONT, SOCKET_H_RAIL

WALL_IN_X = 52.5         # inner face of the rear deck's side walls (parts/deck_walls.py: x 52.5..54.5)
WALL_KEY = 1.0           # bracket reaches this far into the wall


def _octagon(x, y, z0, h, grow):
    return cq.Workplane('XY', origin=(0, 0, z0)).polyline([(x + px, y + py) for px, py in _tube_profile(CAGE_BEAM)]).close() \
        .offset2D(grow, 'intersection').extrude(h).val()


def socket(x, y, z_top, z_floor, rail):
    """(solid to add, solid to cut) for the foot at deck position (x, y); z_top is the deck top there, z_floor the foot end (ref frame)."""
    h = SOCKET_H_RAIL if rail else SOCKET_H_FRONT
    grow = FOOT_CLEAR + SOCKET_WALL
    add = _octagon(x, y, z_top - 0.5, h + 0.5, grow)
    if rail:
        r = CAGE_BEAM * 0.88 / 2 + grow
        xa, xb = (x, WALL_IN_X + WALL_KEY) if x > 0 else (-WALL_IN_X - WALL_KEY, x)
        add = add.fuse(cq.Solid.makeBox(xb - xa, 2 * r, h + 0.5, cq.Vector(xa, y - r, z_top - 0.5))).clean()
    cut = _octagon(x, y, z_floor, z_top + h + 1.0 - z_floor, FOOT_CLEAR)
    return add, cut
