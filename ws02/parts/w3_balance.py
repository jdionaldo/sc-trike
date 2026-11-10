"""WS-03 nose ballast: a printed carrier on the front deck, beside the battery cradle, holding one tungsten-alloy plate (or lead plate) with a snap-in lid.
Assembly frame (x forward, z = 0 at the front axle). Not part of w3_parts.all_parts yet: the integrator adds `w3_balance.build(P)` there and the carrier to the mock list."""
from manifold3d import Manifold

import mono_build as MB
from parts.w3_style import MeshPart, _clean

DECK_BOT = -29.0                       # w3_deck_front underside; floor of the carrier is against it, lid faces the ground (ground is about 25 mm lower here)
PLATE = (40.0, 20.0, 5.0)              # tungsten alloy (about 17.5 g/cc) 40 x 20 x 5 = 4 cc = 70 g (user's skin: the old rear wing is gone and the skin sits further forward; the plate moved from the nose to the tail deck and is 2 mm thicker: front share 64.5 %); lead (11.3 g/cc) would need 40 x 20 x 6.2
PLATE_RHO = 17.5e-3                    # g/mm3
BALLAST_ON = True
FIT = 0.3                              # clearance each side of the plate
WALL, FLOOR, LID = 2.0, 1.6, 1.5
X0, Y0 = -320.0, -12.6                 # outer corner: hangs UNDER the tail deck (floor against the deck underside z -29), centred on y 0 so it does not move the sideways CG
OUT = (PLATE[0] + 2 * (FIT + WALL), PLATE[1] + 2 * (FIT + WALL), FLOOR + PLATE[2] + 2 * FIT + LID)   # 45.2 x 25.2 x 6.7


def plate_g():
    return PLATE[0] * PLATE[1] * PLATE[2] * PLATE_RHO if BALLAST_ON else 0.0


def box_extent():
    """Outer envelope of the carrier in the assembly frame: (x0, x1), (y0, y1), (z0, z1)."""
    z1 = DECK_BOT - OUT[2]
    return (X0, X0 + OUT[0]), (Y0, Y0 + OUT[1]), (z1, DECK_BOT)


def plate_centre():
    (x0, x1), (y0, y1), (_, z1) = box_extent()
    return ((x0 + x1) / 2, (y0 + y1) / 2, z1 - FLOOR - FIT - PLATE[2] / 2)


def _b(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0), center=False).translate((x0, y0, z0))


def _flip(m):
    """Build in the upright frame (floor at the bottom, z from DECK_BOT) then mirror to hang below the deck."""
    return m.mirror((0.0, 0.0, 1.0)).translate((0.0, 0.0, 2 * DECK_BOT))


def carrier_man():
    return _flip(_carrier_up())


def lid_man():
    return _flip(_lid_up())


def _up_extent():
    (x0, x1), (y0, y1), _z = box_extent()
    return (x0, x1), (y0, y1), (DECK_BOT, DECK_BOT + OUT[2])


def _carrier_up():
    (x0, x1), (y0, y1), (z0, z1) = _up_extent()
    top = z1 - LID
    body = _b(x0, x1, y0, y1, z0, top) - _b(x0 + WALL, x1 - WALL, y0 + WALL, y1 - WALL, z0 + FLOOR, top + 1.0)
    for xs in (x0 + 8.0, x1 - 8.0):                                  # two 3 x 8 zip-tie slots through the floor: tie round the deck's front tubes
        body = body - _b(xs - 1.5, xs + 1.5, y0 + 6.0, y1 - 6.0, z0 - 1.0, z0 + FLOOR + 1.0)
    return body


def _lid_up():
    """Lid prints flat; a 1.5 mm plate with a 0.8 mm tongue that drops into the cavity (0.2 mm gap) and a thumb notch."""
    (x0, x1), (y0, y1), (z0, z1) = _up_extent()
    top = z1 - LID
    lid = _b(x0, x1, y0, y1, top, z1) + _b(x0 + WALL + 0.2, x1 - WALL - 0.2, y0 + WALL + 0.2, y1 - WALL - 0.2, top - 0.8, top + 0.01)
    return lid - _b(x1 - 12.0, x1 - 4.0, y0 - 1.0, y0 + 2.0, top + 0.5, z1 + 1.0)


def carrier(p=None):
    return MeshPart("w3_ballast_carrier", lambda: _clean(MB.to_trimesh(carrier_man())), walls=True, supports=False)


def lid(p=None):
    return MeshPart("w3_ballast_lid", lambda: _clean(MB.to_trimesh(lid_man())), walls=False, supports=False)


def build(p=None):
    return [carrier(p), lid(p)] if BALLAST_ON else []


def check(verbose=True):
    """Clash and bed check of the carrier, lid and plate: volume overlap with every assembly item in three lean/steer poses and with the skin over its 0..35 deg swing (1 deg steps); watertight and bed fit."""
    import numpy as np
    import w3_assembly as A
    import w3_swing as SW
    bad = []
    envelope = _b(*box_extent()[0], *box_extent()[1], *box_extent()[2])
    pc = plate_centre()
    plate = _b(pc[0] - PLATE[0] / 2, pc[0] + PLATE[0] / 2, pc[1] - PLATE[1] / 2, pc[1] + PLATE[1] / 2, pc[2] - PLATE[2] / 2, pc[2] + PLATE[2] / 2)
    mine = carrier_man() + lid_man() + plate
    for lean, steer in ((0.0, 0.0), (20.0, 17.0), (-20.0, -17.0)):
        for n, m, k in A.assembly(lean, steer):
            if n.startswith(("w3_ballast",)) or n.startswith("body3"):
                continue
            v = (MB.man(m) ^ envelope).volume()
            if v > 0.1:
                bad.append((lean, steer, n, round(v, 2)))
    body = SW.load_body()
    for k in range(36):
        v = (SW.rot(body, float(k)) ^ envelope).volume()
        if v > 0.1:
            bad.append(("swing", k, "skin", round(v, 2)))
    parts = [carrier(), lid()]
    for pt in parts:
        m = pt.fn()
        ext = m.extents
        if not m.is_watertight or max(ext[:2]) > 256 or ext[2] > 256:
            bad.append(("part", pt.name, m.is_watertight, ext.tolist()))
    if verbose:
        print("ballast check:", "CLEAN" if not bad else bad)
    return bad


if __name__ == "__main__":
    check()
