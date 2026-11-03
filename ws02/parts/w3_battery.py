"""WS-03 battery cradle: a 3 mm floor 9 mm above the base plate on two cross ribs, with end stops, short side lips and two strap slots pairs, screwed down at six tabs.
The 3S 1300 mAh pack (75 x 35 x 25) lies at y -37.5..-2.5, beside the centre drive shaft, so the centreline stays free for the lean servo."""
from manifold3d import Manifold

import layout3wd as LY
import mono_build as MB
from parts.w3_style import MeshPart, _clean

(BX0, BX1), (BY0, BY1), (BZ0, BZ1) = LY.BATT_BOX
Z0 = -23.0                                  # base plate top
T = 2.4                                     # wall
FL = 3.0                                    # floor thickness
RIB_X = (BX0 + 11.0, BX1 - 6.0 - T)                          # first rib clear of the lean tower's feet
TABS = [(rx + T / 2, y) for rx in RIB_X for y in (BY1 + T + 4.0,)]   # (x, y) screw positions in the base plate


def _box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0), center=False).translate((x0, y0, z0))


def tray(p):
    """Assembly frame shifted down by Z0 (the ribs' feet are on the bed)."""
    def fn():
        import parts.w3_frame as FR
        zf0, zf1 = BZ0 - FL - Z0, BZ0 - Z0
        body = _box(BX0 - T, BX1 + T, BY0 - T, BY1 + T, zf0, zf1)
        for rx in RIB_X:
            body = body + (_box(rx, rx + T, BY0 - T, BY1 + T, 0.0, zf0 + 0.3))
            body = body + _box(rx - 4.0, rx + T + 4.0, BY1 + T - 0.3, BY1 + T + 8.0, 0.0, 3.0)         # screw tab on the centreline side
        body = body + _box(BX0 - T, BX0, BY0 - T, BY1 + T, zf1 - 0.3, zf1 + 8.0)                      # end stops
        body = body + _box(BX1, BX1 + T, BY0 - T, BY1 + T, zf1 - 0.3, zf1 + 8.0)
        for x0, x1 in ((BX0, BX0 + 14.0), (BX1 - 14.0, BX1)):                                         # side lips
            for y0, y1 in ((BY0 - T, BY0), (BY1, BY1 + T)):
                body = body + _box(x0, x1, y0, y1, zf1 - 0.3, zf1 + 6.0)
        for xs in (BX0 + 20.0, BX1 - 20.0):                                                            # strap slots, two per strap (3.5 x 12)
            for yc in (BY0 + 7.0, BY1 - 7.0):
                body = body - _box(xs - 1.75, xs + 1.75, yc - 6.0, yc + 6.0, zf0 - 1.0, zf1 + 1.0)
        body = body - (FR.relief() + FR.frame()).translate((0.0, 0.0, -Z0))                                         # grooves around the frame tubes and nodes under the floor
        for tx, ty in TABS:
            body = body - Manifold.cylinder(6.0, 1.3, 1.3, 24).translate((tx, ty, -1.0))               # M2 clear, screw into the base-plate pilots
        return _clean(MB.to_trimesh(body))
    return MeshPart("w3_battery_tray", fn, walls=True, supports=True)


def build(p):
    return [tray(p)]
