"""WS-03 inner structure: 6 mm slotted base plates (front and rear) under the tubular frame (parts/w3_frame.py); z = 0 at the front axle height.

Base plate: 6 mm at z -29..-23 under the gear housings; the housing clamp bolts pass through slots so the housings slide fore/aft
(gear mesh and balance), battery and ESC trays sit on long rail slots, perimeter holes screw up into pads on the body skirt, and the
frame's strut feet screw down into it.  Servo, diff-case and pivot-pin mounts are pads on the tube frame.
"""
from cad import Part

DECK_Z = (-29.0, -23.0)
TD = DECK_Z[1] - DECK_Z[0]                                           # base plate thickness
HALF_W = 33.0
FRONT_X = (-153.0, -22.0)
REAR_X = (-296.0, -153.0)
HOUSING_BOLTS = [(-88.0, -22.0), (-88.0, 30.0), (-155.0, -22.0), (-155.0, 31.0),
                 (-201.5, -2.5), (-201.5, 44.5), (-161.5, -2.5), (-161.5, 44.5),
                 (-294.0, 8.5), (-294.0, 33.5), (-247.5, 8.5), (-247.5, 33.5)]
RAILS = [(-84.0, -14.0, -8.0), (-84.0, -14.0, 8.0), (-170.0, -115.0, -17.0), (-170.0, -115.0, 17.0)]   # (x0, x1, y) long slots for trays
SLOT_W = 3.4


HEAD_D, HEAD_DEPTH = 5.2, 2.7        # M2.5 pan head 4.5 x 2.5: sunk into the underside so nothing catches


def _slot(part, x0, x1, y):
    part.box((x0, y - SLOT_W / 2, -1.0), (x1 - x0, SLOT_W, TD + 2.0), op="cut")
    part.box((x0 - 1.0, y - HEAD_D / 2, -1.0), (x1 - x0 + 2.0, HEAD_D, HEAD_DEPTH + 1.0), op="cut")      # channel for the heads along the slot


def _hole(part, x, y, d):
    part.cyl((x, y, -1.0), d, TD + 2.0, op="cut")
    part.cyl((x, y, -1.0), HEAD_D, HEAD_DEPTH + 1.0, op="cut")                                          # counterbore for the head


def deck(p, name, xr, limit, perimeter):
    """Staircase outline that follows the body's inner plan (3 mm inside the wall), capped at +-limit."""
    from body3_build import hw_in, PAD_X
    part = Part(name, "flat", "PETG")
    part.supports = True                                                  # the head channels bridge 5 mm on the bed side (or print it upside down)
    x0, x1 = xr
    x = x0
    while x < x1 - 1e-6:
        xe = min(x + 4.0, x1)
        w = min(limit if x < -156.0 else min(limit, 52.0), hw_in(0.5 * (x + xe)) - 3.0)
        part.box((x, -w, 0.0), (xe - x, 2 * w, TD))
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
                    _hole(part, px, sgn * (hw_in(px) - 7.0), p.m2_clear)
    import parts.w3_frame as FR
    if not perimeter:                                                      # outboard tab that carries the strut foot beside the front diff case
        for sgn in (1, -1):
            part.box((-140.0, 30.0 if sgn > 0 else -48.0, 0.0), (8.0, 18.0, TD))
    for fx, fy in FR.feet_xy():                                            # screws up into the frame feet
        if x0 < fx < x1:
            _hole(part, fx, fy, p.m2_clear + 0.2)
            _hole(part, fx, -fy, p.m2_clear + 0.2)
    return part



def skid(p):
    """Nose skid plate hugging the angled nose underside (45 deg, 40 mm along the slope), 80 wide, 3 thick, slots like the reference.
    Print frame: u along the slope, v across, w outward thickness; screws into the bosses on the nose underside."""
    part = Part("w3_skid", "flat", "PETG")
    part.box((0.0, -40.0, 0.0), (39.6, 80.0, 3.0))
    for v in (-30.0, -18.0, -6.0, 6.0, 18.0, 30.0):
        part.box((6.0, v - 1.7, -1.0), (22.0, 3.4, 5.0), op="cut")
    for u in (10.0, 28.0):
        for v in (-22.0, 22.0):
            part.cyl((u, v, -1.0), p.m2_clear, 5.0, op="cut")
    return part


def standoff(p):
    """Spacer between the servo wall (|y| 57.5) and the upper link (|y| 64.5) on the pivot pin."""
    part = Part("w3_uplink_standoff", "standing", "PETG")
    part.cyl((0.0, 0.0, 0.0), 8.0, 6.8)
    part.cyl((0.0, 0.0, -0.1), 3.4, 7.0, op="cut")
    return part


def build(p):
    return [standoff(p), skid(p), deck(p, "w3_deck_front", FRONT_X, 33.0, False), deck(p, "w3_deck_rear", REAR_X, 60.0, True)] + __import__('parts.w3_frame', fromlist=['build']).build(p)
