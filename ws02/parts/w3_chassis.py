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
FRONT_X = (-153.0, 16.0)
REAR_X = (-296.0, -153.0)
HOUSING_BOLTS = [(-88.0, -22.0), (-88.0, 30.0), (-155.0, -22.0), (-155.0, 31.0),
                 (-201.5, -2.5), (-201.5, 44.5), (-161.5, -2.5), (-161.5, 44.5),
                 (-294.0, 8.5), (-294.0, 33.5), (-247.5, 8.5), (-247.5, 33.5)]
RAILS = [(-84.0, -14.0, -8.0), (-84.0, -14.0, 8.0), (-170.0, -115.0, -17.0), (-170.0, -115.0, 17.0)]   # (x0, x1, y) long slots for trays
SLOT_W = 3.4


def _slot(part, x0, x1, y):
    part.box((x0, y - SLOT_W / 2, -1.0), (x1 - x0, SLOT_W, 5.0), op="cut")


def deck(p, name, xr, limit, perimeter):
    """Staircase outline that follows the body's inner plan (3 mm inside the wall), capped at +-limit."""
    from body3_build import hw_in, PAD_X, POST_XY
    part = Part(name, "flat", "PETG")
    x0, x1 = xr
    x = x0
    while x < x1 - 1e-6:
        xe = min(x + 4.0, x1)
        w = min(limit if x < -156.0 else min(limit, 52.0), hw_in(0.5 * (x + xe)) - 3.0)
        part.box((x, -w, 0.0), (xe - x, 2 * w, 3.0))
        x = xe
    for bx, by in HOUSING_BOLTS:
        if x0 < bx < x1:
            _slot(part, bx - 5.0, bx + 5.0, by)
    for a, b, y in RAILS:
        if x0 < (a + b) / 2 < x1:
            _slot(part, max(a, x0 + 4.0), min(b, x1 - 4.0), y)
    if perimeter:                                                         # screws up into the pads on the body skirt
        for px in PAD_X:
            if x0 < px < x1:
                for sgn in (1, -1):
                    part.cyl((px, sgn * (hw_in(px) - 7.0), -1.0), p.m2_clear, 5.0, op="cut")
    elif x0 < POST_XY[0] < x1:                                            # body posts
        for sgn in (1, -1):
            part.cyl((POST_XY[0], sgn * POST_XY[1], -1.0), 2.7, 5.0, op="cut")
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

    box((xa, -110.0), (zl, 14.0), (0.0, 3.0))                                  # plate, low where the body skin is close (x < -110)
    box((-110.0, xb), (zl, zh), (0.0, 3.0))                                    # plate, full height inside the arm window
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


def body_post(p):
    """Standoff from the deck to the roof boss: M2.5 screw from below through the deck and this tube."""
    part = Part("w3_body_post", "standing", "PETG")
    part.cyl((0.0, 0.0, 0.0), 7.6, 50.0)
    part.cyl((0.0, 0.0, -0.1), 2.8, 50.2, op="cut")
    return part


def wing(p, side):
    """Wing fender plate bolted to the inboard face of the knuckle carrier (moves with the wheel). Flat; print frame u = x, v = z."""
    name = "w3_wing_left" if side > 0 else "w3_wing_right"
    part = Part(name, "flat", "PETG")
    pts = [(-50.0, -4.0), (-8.0, 40.0), (34.0, 40.0), (40.0, 10.0), (30.0, -4.0)]
    from shapely.geometry import Polygon
    import numpy as np
    poly = Polygon(pts)
    # stack of 1 mm slabs so the outline stays crisp without a sketch: use a staircase of 2 mm columns
    xs = np.arange(-50.0, 40.0, 2.0)
    for x in xs:
        from shapely.geometry import LineString
        g = LineString([(x + 1.0, -50), (x + 1.0, 80)]).intersection(poly)
        if g.is_empty:
            continue
        z0, z1 = g.bounds[1], g.bounds[3]
        part.box((x, z0 + 4.0, 0.0), (2.0, z1 - z0, 3.0))
    part.cyl((0.0, 4.0, -0.1), 6.4, 3.2, op="cut")                        # lateral shaft passes through
    for x in (-6.0, 6.0):
        part.cyl((x, 4.0 + 16.0, -0.1), p.m2_clear, 3.2, op="cut")
    return part


def skid(p):
    """Nose skid plate with the slot pattern from the reference: flat 3 mm plate under the nose, x -31..16, y +-40. Screws into the deck nose."""
    part = Part("w3_skid", "flat", "PETG")
    part.box((0.0, 0.0, 0.0), (47.0, 72.0, 3.0))
    for y in (10.0, 22.0, 34.0, 46.0, 58.0):
        part.box((8.0, y - 1.7, -1.0), (30.0, 3.4, 5.0), op="cut")
    for x, y in ((25.0, 26.0), (25.0, 46.0), (43.0, 26.0), (43.0, 46.0)):
        part.cyl((x, y, -1.0), p.m2_clear, 5.0, op="cut")
    return part


def rear_fender(p):
    """Arch over the rear tire (r 56): half ring r 59.5..61.9, 76 wide, centre (x -362.2, z -10.7), bolts to bosses on the tail.
    Print frame: u = x + 362.2, v = -(z + 10.7), w = y + 38; the arch is the v <= 0 half, printed lying so the arc extrudes straight up."""
    part = Part("w3_rear_fender", "arch lying on its side", "PETG")
    part.cyl((0.0, 0.0, 0.0), 123.8, 76.0)
    part.cyl((0.0, 0.0, -1.0), 119.0, 78.0, op="cut")
    part.box((-70.0, 0.0, -1.0), (140.0, 70.0, 78.0), op="cut")                 # keep the upper half only
    for w0 in (0.0, 71.0):
        part.box((52.0, 0.0, w0), (10.5, 8.0, 5.0))                           # mounting tabs below the arch front end
        part.cyl((50.0, 4.0, w0 + 2.5), 2.7, 14.0, axis="X", op="cut")
    return part


def build(p):
    return [body_post(p), wing(p, 1), wing(p, -1), skid(p), deck(p, "w3_deck_front", FRONT_X, 33.0, False), deck(p, "w3_deck_rear", REAR_X, 60.0, True), wall(p, 1), wall(p, -1)]
