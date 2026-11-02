"""WS-03 inner structure: 6 mm slotted base plates (front and rear) under the tubular frame (parts/w3_frame.py); z = 0 at the front axle height.

Base plate: 6 mm at z -29..-23 under the gear housings; the housing clamp bolts pass through slots so the housings slide fore/aft
(gear mesh and balance), battery and ESC trays sit on long rail slots, perimeter holes screw up into pads on the body skirt, and the
frame's strut feet screw down into it.  Servo, diff-case and pivot-pin mounts are pads on the tube frame.
"""
from cad import Part
from manifold3d import Manifold

DECK_Z = (-29.0, -23.0)
TD = DECK_Z[1] - DECK_Z[0]                                           # base plate thickness
HALF_W = 33.0
FRONT_X = (-153.0, -3.0)
REAR_X = (-296.0, -153.0)
HOUSING_BOLTS = [(-88.0, -22.0), (-88.0, 30.0), (-155.0, -22.0), (-155.0, 31.0),
                 (-201.5, -2.5), (-201.5, 44.5), (-161.5, -2.5), (-161.5, 44.5),
                 (-294.0, 8.5), (-294.0, 33.5), (-247.5, 8.5), (-247.5, 33.5)]
RAILS = [(-84.0, -14.0, -8.0), (-84.0, -14.0, 8.0), (-170.0, -115.0, -17.0), (-170.0, -115.0, 17.0)]   # (x0, x1, y) long slots for trays
SLOT_W = 3.4


HEAD_D, HEAD_DEPTH = 5.2, 2.7        # M2.5 pan head 4.5 x 2.5: sunk into the underside so nothing catches


def _box(x0, x1, y0, y1, z0, z1):
    return Manifold.cube((x1 - x0, y1 - y0, z1 - z0), center=False).translate((x0, y0, z0))


def _slot(x0, x1, y):
    return [_box(x0, x1, y - SLOT_W / 2, y + SLOT_W / 2, -1.0, TD + 1.0),
            _box(x0 - 1.0, x1 + 1.0, y - HEAD_D / 2, y + HEAD_D / 2, -1.0, HEAD_DEPTH)]            # channel for the heads along the slot


def _hole(x, y, d):
    return [Manifold.cylinder(TD + 2.0, d / 2, d / 2, 28).translate((x, y, -1.0)),
            Manifold.cylinder(HEAD_DEPTH + 1.0, HEAD_D / 2, HEAD_D / 2, 28).translate((x, y, -1.0))]    # counterbore for the head


def deck(p, name, xr, limit, perimeter):
    """Base plate with a smooth outline (a polyline sampled every 2 mm along the body's inner plan, 3 mm inside the wall), capped at +-limit."""
    import numpy as np
    from body3_build import hw_in, PAD_X
    import parts.w3_frame as FR
    import mono_build as MB
    from parts.w3_style import MeshPart, _clean
    x0, x1 = xr
    def fn():
        xs = list(np.arange(x0, x1, 2.0)) + [x1]
        up = [(float(x), float(min(limit if x < -156.0 else min(limit, 52.0), hw_in(min(max(x, -299.0), 29.0)) - 3.0))) for x in xs]
        pts = up + [(x, -w) for x, w in reversed(up)]
        body = MB.prism_xy(pts, 0.0, TD)
        if not perimeter:                                                  # outboard tab that carries the strut foot beside the front diff case
            for sgn in (1, -1):
                body = body + _box(-140.0, -132.0, 30.0 if sgn > 0 else -48.0, 48.0 if sgn > 0 else -30.0, 0.0, TD)
        cuts = []
        for bx, by in HOUSING_BOLTS:
            if x0 < bx < x1:
                cuts += _slot(bx - 5.0, bx + 5.0, by)
        for a, b, y in RAILS:
            if x0 < (a + b) / 2 < x1:
                cuts += _slot(max(a, x0 + 4.0), min(b, x1 - 4.0), y)
        if perimeter:                                                      # screws up into the pads on the body skirt
            for px in PAD_X:
                if x0 < px < x1:
                    for sgn in (1, -1):
                        cuts += _hole(px, sgn * (hw_in(px) - 7.0), p.m2_clear)
        for fx, fy in FR.feet_xy():                                        # screws up into the frame feet
            if x0 < fx < x1:
                cuts += _hole(fx, fy, p.m2_clear + 0.2) + _hole(fx, -fy, p.m2_clear + 0.2)
        for cut in cuts:
            body = body - cut
        return _clean(MB.to_trimesh(body))
    return MeshPart(name, fn, walls=True, supports=True)


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
    return [standoff(p), skid(p), deck(p, "w3_deck_front", FRONT_X, 33.0, False), deck(p, "w3_deck_rear", REAR_X, 60.0, True)] + __import__('parts.w3_frame', fromlist=['build']).build(p) + __import__('parts.w3_tail', fromlist=['build']).build(p)
