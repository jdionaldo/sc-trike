"""WS-03 inner structure: 6 mm slotted base plates (front and rear) under the tubular frame (parts/w3_frame.py); z = 0 at the front axle height.

Base plate: 6 mm at z -29..-23 under the gear housings; the housing clamp bolts pass through slots so the housings slide fore/aft
(gear mesh and balance), battery and ESC trays sit on long rail slots, the skin is held by the front hinge and tail magnets (no skirt screws), and the
frame's strut feet screw down into it.  Servo, diff-case and pivot-pin mounts are pads on the tube frame.
"""
from cad import Part
from manifold3d import Manifold

DECK_Z = (-29.0, -23.0)
TD = DECK_Z[1] - DECK_Z[0]                                           # base plate thickness
FRONT_X = (-153.0, -2.5)
SERVO_DROP = 3.0                           # the lean servos' bottoms sit at the base plate's underside: their trays hang 3 mm below it (the front deck prints top-down)
# base plate outline (x, half width), as drawn along the cage: a diagonal out from the nose to the cage's widest tubes, a straight run, then one long diagonal in to the tail;
# both decks read the same table, so the seam at x -153 is flush
PLAN = [(-2.5, 36.0), (-34.0, 54.5), (-210.0, 54.5), (-296.0, 37.5)]
PL = 50.0                                  # grate length along the slope: up to just below the bumper bar
TAB_X = (-13.0, 0.6)                       # the grate's foot tab (assembly x), lies in a rebate under the front base plate
TAB_SCREWS = ((-8.0, 26.0), (-3.0, 12.0))  # (x, |y|) countersunk screws from below, into the base plate
REAR_X = (-296.0, -153.0)
HOUSING_BOLTS = [(-88.0, -22.0), (-88.0, 30.0), (-155.0, -22.0), (-155.0, 31.0),
                 (-201.5, -2.5), (-201.5, 44.5), (-161.5, -2.5), (-161.5, 44.5),
                 (-294.0, 8.5), (-294.0, 33.5), (-247.5, 8.5), (-247.5, 33.5)]
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
    from body3_build import hw_in
    import parts.w3_frame as FR
    import mono_build as MB
    from parts.w3_style import MeshPart, _clean
    x0, x1 = xr
    def fn():
        xs = sorted(set(list(np.arange(x0, x1, 2.0)) + [x1] + [px for px, _ in PLAN if x0 <= px <= x1]))
        up = [(float(x), float(np.interp(x, [px for px, _ in reversed(PLAN)], [pw for _, pw in reversed(PLAN)]))) for x in xs]
        pts = up + [(x, -w) for x, w in reversed(up)]
        body = MB.prism_xy(pts, 0.0, TD)
        if not perimeter:
            for sgn in (1, -1):                                            # servo trays: floor plates with an inner lip (the frame tubes at |y| 55 are the outer wall) under the lean (z -29 bottom) and steering servos
                def side(y0, y1):
                    return (y0, y1) if sgn > 0 else (-y1, -y0)
                for x0_, x1_, zf_, zl_ in ((-79.5, -41.0, -SERVO_DROP, 8.0), (-134.0, -88.0, 0.0, 5.8)):
                    ztop = 0.0 if zf_ < 0 else 4.5
                    body = body + _box(x0_, x1_, *side(31.0, 54.5), zf_, ztop)
                    body = body + _box(x0_, x1_, *side(31.0, 35.0), zf_, zl_)
        cuts = []
        if not perimeter:
            for sgn in (1, -1):                                            # servo pockets: the plate steps down to the tray floor under each servo's footprint
                yy = (35.0, 57.0) if sgn > 0 else (-57.0, -35.0)
                cuts.append(_box(-81.0, -39.0, yy[0], yy[1], 0.0, TD + 0.1))
                cuts.append(_box(-134.0, -88.0, yy[0], yy[1], 4.5, TD + 0.1))
            cuts.append(_box(TAB_X[0] - 0.3, x1 + 1.0, -33.2, 33.2, -1.0, 3.2))                               # rebate for the grate's foot tab: continuous underside
            for tx, ty in TAB_SCREWS:
                for sg in (1, -1):
                    cuts.append(Manifold.cylinder(2.6, 1.1, 1.1, 24).translate((tx, sg * ty, 3.0)))        # pilots in the 3 mm left above the rebate
        for bx, by in HOUSING_BOLTS:
            if x0 < bx < x1:
                cuts += _slot(bx - 5.0, bx + 5.0, by)
        for fx, fy in FR.feet_xy():                                        # screws up into the frame feet
            if x0 < fx < x1:
                cuts += _hole(fx, fy, p.m2_clear + 0.2) + _hole(fx, -fy, p.m2_clear + 0.2)
        for cut in cuts:
            body = body - cut
        if not perimeter:
            body = body.translate((0.0, 0.0, SERVO_DROP))                    # keep the mesh above z = 0 (the assembly shifts it back down)
        return _clean(MB.to_trimesh(body))
    return MeshPart(name, fn, walls=True, supports=True)


def skid(p):
    """Nose grate (skid plate) hugging the angled nose underside, 80 wide, 3 thick, with slots; a flat foot tab at its lower end lies in a rebate in
    the underside of the base plate so the underside is continuous (countersunk screws from below).  Print frame: u along the slope, v across, w outward."""
    import math
    import numpy as np
    import mono_build as MB
    from parts.w3_style import MeshPart, _clean
    from body3_build import NOSE_TH, NOSE_LOW
    def fn():
        body = _box(0.0, PL, -40.0, 40.0, 0.0, 3.0)
        body = body - MB.prism_xz([(PL - 2.0, 3.1), (PL + 0.1, 3.1), (PL + 0.1, 0.9)], -41.0, 41.0).rotate((0.0, 0.0, 0.0))          # 2 mm chamfer on the top edge
        for v in (-36.0, -30.0, 30.0, 36.0):                                   # vertical slits at each side
            body = body - _box(6.0, 28.0, v - 1.7, v + 1.7, -1.0, 4.0)
        clip = _box(6.0, 34.0, -18.0, 18.0, -1.0, 4.0)                          # a big X in the middle
        ang = math.degrees(math.atan2(17.0, 14.0))
        for sg in (1, -1):
            bar = Manifold.cube((60.0, 4.6, 5.0), center=True).rotate((0.0, 0.0, sg * ang)).translate((20.0, 0.0, 1.5))
            body = body - (bar ^ clip)
        # foot tab in assembly coordinates (x -13 .. +0.6, z -29 .. -26), then into the print frame
        sk = np.array([[math.cos(NOSE_TH), 0, math.sin(NOSE_TH), NOSE_LOW[0]], [0, -1, 0, 0], [math.sin(NOSE_TH), 0, -math.cos(NOSE_TH), NOSE_LOW[1]], [0, 0, 0, 1.0]])
        tab = _box(TAB_X[0], TAB_X[1], -33.0, 33.0, DECK_Z[0], DECK_Z[0] + 3.0)
        for x_, y_ in TAB_SCREWS:
            for sg in (1, -1):
                tab = tab - Manifold.cylinder(3.2, 1.35, 1.35, 24).translate((x_, sg * y_, DECK_Z[0] - 0.1)) - Manifold.cylinder(1.6, 2.5, 1.35, 24).translate((x_, sg * y_, DECK_Z[0] - 0.1))
        inv = np.linalg.inv(sk)
        body = body + tab.transform(inv[:3, :4])
        j0 = _box(0.0, 2.0, -33.0, 33.0, 0.0, 3.0)                              # smooth join: hull from the grate's lower end to the tab's near edge
        j1 = (tab ^ _box(TAB_X[1] - 1.0, TAB_X[1], -33.0, 33.0, DECK_Z[0], DECK_Z[0] + 3.0)).transform(inv[:3, :4])
        body = body + Manifold.batch_hull([j0, j1])
        m = _clean(MB.to_trimesh(body))
        lift = -float(m.bounds[0][2])
        m.apply_translation((0.0, 0.0, lift))                                   # the tab hangs below the plate in the print frame: lift it onto the bed
        import json, pathlib
        pathlib.Path('out/stl/w3_skid_lift.json').write_text(json.dumps(lift))
        return m
    return MeshPart("w3_skid", fn, walls=False, supports=True)


def standoff(p):
    """Spacer between the servo wall (|y| 57.5) and the upper link (|y| 64.5) on the pivot pin."""
    part = Part("w3_uplink_standoff", "standing", "PETG")
    part.cyl((0.0, 0.0, 0.0), 8.0, 6.8)
    part.cyl((0.0, 0.0, -0.1), 3.4, 7.0, op="cut")
    return part


def build(p):
    return [standoff(p), skid(p), deck(p, "w3_deck_front", FRONT_X, 60.0, False), deck(p, "w3_deck_rear", REAR_X, 60.0, True)] + __import__('parts.w3_frame', fromlist=['build']).build(p) + __import__('parts.w3_tail', fromlist=['build']).build(p)
