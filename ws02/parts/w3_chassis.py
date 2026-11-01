"""WS-03 inner structure: slotted decks (front and rear), servo/pivot walls, assembly frame (z = 0 at the front axle height).

Deck: 3 mm plate at z -26..-23 under the gear housings; the housing clamp bolts pass through slots so the housings slide fore/aft
(gear mesh and balance), battery and ESC trays sit on long rail slots, perimeter holes screw up into pads on the body skirt.
Wall: 3 mm plate at |y| 54.5..57.5 carrying both servos (flange screws through the plate), the diff output shaft hole and the
upper-link pivot boss; two screws into ears on the front diff case hold it.
"""
from cad import Part
from parts.w3_front import YS

DECK_Z = (-26.0, -23.0)
HALF_W = 33.0
FRONT_X = (-150.0, 8.0)
REAR_X = (-296.0, -150.0)
HOUSING_BOLTS = [(-88.0, -22.0), (-88.0, 30.0), (-155.0, -22.0), (-155.0, 31.0),
                 (-201.5, -2.5), (-201.5, 44.5), (-161.5, -2.5), (-161.5, 44.5),
                 (-294.0, 8.5), (-294.0, 33.5), (-247.5, 8.5), (-247.5, 33.5)]
RAILS = [(-84.0, -14.0, -8.0), (-84.0, -14.0, 8.0), (-170.0, -115.0, -17.0), (-170.0, -115.0, 17.0)]   # (x0, x1, y) long slots for trays
SLOT_W = 3.4


def _slot(part, x0, x1, y):
    part.box((x0, y - SLOT_W / 2, -1.0), (x1 - x0, SLOT_W, 5.0), op="cut")


def deck(p, name, xr, hw):
    part = Part(name, "flat", "PETG")
    x0, x1 = xr
    part.box((x0, -hw, 0.0), (x1 - x0, 2 * hw, 3.0))
    for x, y in HOUSING_BOLTS:
        if x0 < x < x1:
            _slot(part, x - 5.0, x + 5.0, y)
    for a, b, y in RAILS:
        if x0 < (a + b) / 2 < x1:
            _slot(part, max(a, x0 + 4.0), min(b, x1 - 4.0), y)
    n = max(2, int((x1 - x0) // 40))                                          # perimeter screws into the pads on the body skirt
    for i in range(n + 1):
        x = x0 + 8.0 + (x1 - x0 - 16.0) * i / n
        for y in (-hw + 4.0, hw - 4.0):
            part.cyl((x, y, -1.0), p.m2_clear, 5.0, op="cut")
    return part


def wall(p, side):
    """Plate in the x-z plane, |y| 48..51, outer face on the bed. Print frame: u = x, v = z (left) or -z (right), w = 51 - |y|."""
    name = "w3_wall_left" if side > 0 else "w3_wall_right"
    part = Part(name, "outer face on the bed", "PETG")
    zl, zh = -26.0, 46.0
    xa, xb = -155.0, -35.0
    vv = (lambda a, b: (a, b)) if side > 0 else (lambda a, b: (-b, -a))

    def box(x, z, w, op="join"):
        v0, v1 = vv(*z)
        part.box((x[0], v0, w[0]), (x[1] - x[0], v1 - v0, w[1] - w[0]), op=op)

    def cyl(x, z, w0, h, d, op="cut"):
        v = z if side > 0 else -z
        part.cyl((x, v, w0), d, h, op=op)

    box((xa, xb), (zl, zh), (0.0, 3.0))                                       # plate
    boss_z = 40.0
    cyl(-100.0, boss_z, 3.0 - 0.1, 7.1, 8.0, op="join")                       # upper-link pivot boss (the link sits 7 mm off the wall)
    cyl(-100.0, boss_z, -0.1, 10.2, 3.4)                                      # pivot pin
    cyl(-100.0, 0.0, -0.1, 3.2, 7.0)                                          # diff output shaft
    for xc, zc, d in ((-71.4, -18.8, 8.0), (-100.0, -14.0, 8.0)):             # servo horn shafts: (-71.4, -18.8) lean, (-100, -14) steer
        cyl(xc, zc, -0.1, 3.2, d)
    for xs, zs in ((-60.0, -18.8), (-111.4, -14.0)):                          # servo flange screws, 49 mm apart along x
        for dx in (-24.5, 24.5):
            for dz in (-5.0, 5.0):
                cyl(xs + dx, zs + dz, -0.1, 3.2, p.m2_clear)
    v0, v1 = vv(zl - 1.0, -22.0)
    part.box((-108.0, v0, -0.1), (16.0, v1 - v0, 3.2), op="cut")             # notch for the steer rod eye
    for x in (-150.0, -86.0):                                                 # screws into the front diff case ears
        cyl(x, -10.0, -0.1, 3.2, 2.7)
    return part


def build(p):
    return [deck(p, "w3_deck_front", FRONT_X, 33.0), deck(p, "w3_deck_rear", REAR_X, 48.0), wall(p, 1), wall(p, -1)]
