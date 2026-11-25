"""Rear travel check: the rear swing arm group turned about its pivot through bump and droop, against the whole built model.

Run from the project folder:  python -I tools/rear_check.py [output/model.step]
Reads the STEP only. Exits 1 if anything overlaps (common volume above MIN_VOL) in any pose or a boolean fails.

Moving set: every part of the 'Rear swingarm' group (arm, axle, hub, pulleys, belt, wheel), the rear tyre and the lower M6 shock pin.
Pivot axis: x through the centre of the pivot pulley (it sits on the pivot shaft). Poses: wheel travel at the axle REAR_TRAVEL mm
(environment, comma list; + is bump). The shock is a rigid stand-in: it is left out of the overlap check, its eye-to-eye length is
reported per pose instead (the change is the stroke the shock must give). Swept report: every moving part against every static part
whose distance in some pose is under CLEAR, with its pose; designed contacts in WHITELIST are named.
"""
import math
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT / 'tools'))
import cadquery as cq
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
import front_check as fc

MIN_VOL = 0.01
CLEAR = 1.0
TRAVEL = [float(v) for v in os.environ.get('REAR_TRAVEL', '-15,-8,8,15,20').split(',')]
SHOCK = 'Rear_shock__100_mm_class'
MOVING_EXTRA = ('Rear_tire', 'M6_shock_pin__lower')
STATIC_SKIP = (SHOCK,)
# designed contacts between a moving and a static part: (moving leaf, static leaf, reason)
WHITELIST = [('mock_rear_axle', 'w3_rbc_lower', 'pivot shaft area: stand-in axle ends inside the carrier'),
             ('pulley_r_pivot', 'b_rear_shaft', 'pivot pulley on the pivot shaft (turns about the pivot axis itself)'),
             ('b_gt2_belt_r', 'pulley_r_pivot', 'belt on its pulley'),
             ('M6_shock_pin__lower', SHOCK, 'lower shock eye on its pin')]


def dist(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped); d.Perform()
    return d.Value() if d.IsDone() else float('nan')


def main():
    t0 = time.time()
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'output/model.step'
    P = fc.load(path)
    keys = list(P)
    mov = [k for k in keys if '/Rear_swingarm/' in '/' + k + '/' or fc.leaf(k) in MOVING_EXTRA]
    mov = [k for k in mov if fc.leaf(k) != 'Rear_swingarm']
    static = [k for k in keys if k not in mov and fc.leaf(k) not in STATIC_SKIP]
    by = {fc.leaf(k): k for k in keys}
    pc = P[by['pulley_r_pivot']].BoundingBox().center
    ac = P[by['pulley_r_axle']].BoundingBox().center
    R = math.hypot(ac.y - pc.y, ac.z - pc.z)
    piv = cq.Vector(0, pc.y, pc.z)
    sb = P[by[SHOCK]].BoundingBox()
    lo_pin = P[by['M6_shock_pin__lower']].BoundingBox().center
    hi_pin = P[by['M6_shock_pin']].BoundingBox().center
    eye_lo, eye_hi = cq.Vector(0, lo_pin.y, lo_pin.z), cq.Vector(0, hi_pin.y, hi_pin.z)
    L0 = (eye_hi - eye_lo).Length
    print('rear_check: %d parts, %d moving: %s' % (len(keys), len(mov), ', '.join(fc.short(k) for k in mov)))
    print('pivot y %.2f z %.2f, axle y %.2f z %.2f, arm radius %.1f mm, shock eye to eye at rest %.2f mm' % (pc.y, pc.z, ac.y, ac.z, R, L0))
    wl = {}
    for a, b, why in WHITELIST:
        if a in by and b in by: wl[frozenset((by[a], by[b]))] = why
    a0 = math.atan2(ac.z - pc.z, ac.y - pc.y)
    hits, errs, near = 0, 0, {}
    for dz in TRAVEL:
        s = (ac.z - pc.z + dz) / R
        if abs(s) >= 1: print('travel %+.1f out of reach' % dz); errs += 1; continue
        th = math.degrees(math.asin(s) - a0)      # axle behind the pivot (+y): cos(a0) > 0
        loc = cq.Location(piv) * cq.Location(cq.Vector(0, 0, 0), cq.Vector(1, 0, 0), th) * cq.Location(-piv)   # about the pivot axis
        el = cq.Vertex.makeVertex(*eye_lo.toTuple()).moved(loc).Center()
        L = (eye_hi - el).Length
        print('pose travel %+5.1f mm: arm %+6.2f deg, shock %.2f mm (%+.2f against rest)' % (dz, th, L, L - L0), flush=True)
        mv = {k: P[k].moved(loc) for k in mov}
        for a in mov:
            ba = fc.bb(mv[a])
            for b in static:
                pair = frozenset((a, b))
                bbx = fc.bb(P[b])
                if not all(ba[i] - CLEAR <= bbx[i + 1] and bbx[i] - CLEAR <= ba[i + 1] for i in (0, 2, 4)):
                    continue
                try:
                    v, where = fc.overlap(mv[a], P[b])
                except Exception as exc:
                    errs += 1; print('  ERROR %s <> %s: %s' % (fc.short(a), fc.short(b), exc)); continue
                if v > MIN_VOL and pair not in wl:
                    hits += 1
                    print('  OVERLAP %9.2f mm3  %s <> %s  [%s]' % (v, fc.short(a), fc.short(b), where), flush=True)
                    continue
                d = 0.0 if v > MIN_VOL else dist(mv[a], P[b])
                if d < CLEAR and (pair not in near or d < near[pair][0]):
                    near[pair] = (d, dz, fc.short(a), fc.short(b))
    print('--- swept clearance under %.1f mm (travel %s)' % (CLEAR, TRAVEL))
    for pair, (d, dz, a, b) in sorted(near.items(), key=lambda q: q[1][0]):
        print('  %6.3f mm at %+5.1f  %s <> %s%s' % (d, dz, a, b, ('   WHITELIST: ' + wl[pair]) if pair in wl else ''))
    print('rear_check: %d overlaps, %d errors, %.0f s' % (hits, errs, time.time() - t0))
    sys.exit(1 if hits or errs else 0)


if __name__ == '__main__':
    main()
