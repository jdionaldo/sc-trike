"""Interference check of the double-wishbone front end (parts/wishbone.py) against the whole built model, at rest and over lean and steer.

Run from the project folder:  python -I tools/front_check.py [output/model.step]
Reads the STEP only (no model rerun, nothing written). Exits 1 if anything overlaps or a boolean fails.

Rest check: every front suspension and steering part, the battery, the receiver, the front wheels and tyres against every other part.
Pose check: body (head) frame, so the body stays put and only the parts that move against it are placed, with the same Locations as
lean_front.build().pose(): arms by psi about their pivot rods, wheel groups by the ball displacement and the kingpin steer, tie rods,
horn, heave shock. Poses: body roll phi x servo horn eta.
Collision threshold: a common volume above MIN_VOL (0.01 mm3) is an overlap.

Swept clearance report (after the overlap checks, does not change the exit code): every moving part against every other part, minimum
distance over lean -10/-5/0/5/10 deg x horn -30/0/30 deg at the current FRONT_BUMP; every pair under CLEAR (1.0 mm: moving parts, shock and
spring to neighbours, printed part to a bought-part envelope) is printed with the pose where it is smallest. Pairs in WHITELIST are designed
contacts (each with its reason and the smallest distance it may reach); STOPS lists the travel stops, which must touch their arm (within
TOUCH) at their end pose and keep CLEAR in every other pose. Bounding boxes grown by CLEAR prefilter every pair, and large static parts are
clipped once to a box CLIP_M around each moving part's swept bounding box (faces of that cut lie at least CLIP_M > CLEAR away, so they
never show up as a distance under CLEAR).
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import math
import cadquery as cq
from soma import import_assembly
from parts import wishbone as wb

V = cq.Vector
MIN_VOL = 0.01          # mm3, collision threshold
GROW = 0.2              # mm, bounding box prefilter
PHIS = (-10.0, 0.0, 10.0)
ETAS = (-30.0, 0.0, 30.0)
import os
BUMP = float(os.environ.get('FRONT_BUMP', '0'))      # extra wheel travel of both wheels, mm (bump +, droop -)
SWEEP_PHIS = (-10.0, -5.0, 0.0, 5.0, 10.0)
CLEAR = 1.0             # mm, swept clearance rule
TOUCH = 0.2             # mm, a stop touches its arm at its end pose when closer than this
CLIP_M = 1.5            # mm, clip box margin around a moving part's swept bounding box
SIDES = (1, -1)
# designed contacts: (part a, part b, reason, smallest distance allowed); {s} is the side 1 / -1
WHITELIST = [
    ('Ball stud {k} {s}', 'Rod end {k} {s}', 'ball stud in its ball cup (socket 0.05 mm over the ball)', 0.0),
    ('Steer stud knuckle {s}', 'Tie rod end knuckle {s}', 'ball stud in its ball cup', 0.0),
    ('Steer stud horn {s}', 'Tie rod end horn {s}', 'ball stud in its ball cup', 0.0),
    ('Pivot rod {k} {s}', '{K} arm {s}', 'pivot rod in the arm bore (0.1 mm running clearance)', 0.05),
    ('Lean head', '{K} arm {s}', "pivot barrel's thrust collars against the head's frames (0.4 mm axial running gap)", 0.35),
    ('Heave shock pin 1', 'Heave shock shaft', 'shock eye on its pin', 0.0),
    ('Heave shock pin -1', 'Heave shock body', 'shock eye on its pin', 0.0),
    ('Upper arm 1', 'Heave shock shaft', 'shock eye between the fork cheeks (0.1 mm each side)', 0.05),
    ('Upper arm -1', 'Heave shock body', 'shock eye between the fork cheeks (0.1 mm each side)', 0.05),
    ('Heave shock body', 'Heave shock shaft', 'shaft in the body bore', 0.1),
    ('Heave shock body', 'Heave bump stop', 'heave bump stop: the TPU sleeve meets the shock body at 12 mm heave + 10 deg lean (designed end of travel)', 0.0),
    ('Steer servo', 'Steer horn', 'horn on the servo spline, hub 0.5 mm above the case', 0.45),
    ('Steer servo', 'Steer servo shaft', 'output shaft of the servo', 0.0),
]
# travel stops: (stop, arm, end pose as (phi, FRONT_BUMP)); a stop is static (body frame)
STOPS = [('Droop stop pad {s}', 'Lower arm {s}', lambda s: (-s * 10.0, -8.0)),
         ('Droop stop {s}', 'Lower arm {s}', None)]


def _expand(entry):
    out = []
    a, b = entry[0], entry[1]
    for s in SIDES:
        for k, K in (('upper', 'Upper'), ('lower', 'Lower')):
            out.append((a.format(s=s, k=k, K=K), b.format(s=s, k=k, K=K)) + tuple(entry[2:]) + (s,))
    return list({(e[0], e[1]): e for e in out}.values())


REST_GROUPS = ('Chassis/Front_suspension/', 'Chassis/Steering/', 'Chassis/Stops/')
REST_LEAVES = ('b_battery', 'mock_receiver')
REST_PREFIX = ('wheel_f_', 'mock_tire_')


def leaf(key):
    return key.rsplit('/', 1)[-1]


def short(key):
    return leaf(key).replace('_', ' ')


def load(path):
    asm = import_assembly(str(path))
    parts = {}
    for key, n in asm.objects.items():
        if n.obj is None:
            continue
        sh = (n.obj.val() if isinstance(n.obj, cq.Workplane) else n.obj).moved(n.loc)
        parts[key] = sh
    return parts


def bb(shape):
    b = shape.BoundingBox()
    return (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)


def bb_hit(a, b):
    return all(a[i] - GROW <= b[i + 1] and b[i] - GROW <= a[i + 1] for i in (0, 2, 4))


def overlap(a, b):
    """(volume, bbox text) of the common solid, or raises."""
    c = a.intersect(b)
    v = c.Volume()
    if v <= MIN_VOL:
        return v, ''
    q = c.BoundingBox()
    return v, 'x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f' % (q.xmin, q.xmax, q.ymin, q.ymax, q.zmin, q.zmax)


def moving_groups():
    """{group id: [part names as in lean_front.py]} of everything that moves against the body."""
    g = {}
    for s in (1, -1):
        g[('wheel', s)] = ['Knuckle %d' % s, 'Axle pin %d' % s, 'Axle nut %d' % s, 'wheel f %d' % s, 'mock tire %d' % s, 'Wheel bearing inner %d' % s, 'Wheel bearing outer %d' % s, 'Axle shim inner %d' % s, 'Axle shim outer %d' % s,
                           'Steer stud knuckle %d' % s, 'Steer stud nut knuckle %d' % s] + \
                          ['Ball stud%s %s %d' % (k, n, s) for k in ('', ' nut') for n in ('upper', 'lower')]
        g[('arm_lo', s)] = ['Lower arm %d' % s, 'Rod end lower %d' % s]
        g[('arm_up', s)] = ['Upper arm %d' % s, 'Rod end upper %d' % s, 'Heave shock pin %d' % s]
        g[('tie', s)] = ['Tie rod %d' % s, 'Tie rod end knuckle %d' % s, 'Tie rod end horn %d' % s]
    g[('horn', 0)] = ['Steer horn', 'Steer servo shaft'] + ['Steer stud%s horn %d' % (k, s) for k in ('', ' nut') for s in (1, -1)]
    g[('shock_b', 0)] = ['Heave shock body']
    g[('shock_s', 0)] = ['Heave shock shaft', 'Heave bump stop']      # the TPU heave stop rides on the shaft (parts/wishbone.py HEAVE_STOP_*)
    return g


def pose_locs(phi, eta):
    """{group id: Location} in the body frame, list of kinematic problems, shock eye distance."""
    locs, bad = {}, []
    psi = {s: wb.solve_psi(s, phi) for s in (1, -1)}
    if BUMP:      # both wheels BUMP mm up (+) or down (-) on top of the lean pose (FRONT_BUMP environment variable)
        psi = {s: psi[s] - s * __import__('math').degrees(__import__('math').asin(BUMP / wb.ARM_L)) for s in (1, -1)}
    for s in (1, -1):
        hinge = lambda z: wb._loc_axis((s * wb.XI, 0, z), (0, 1, 0), psi[s])
        locs[('arm_lo', s)] = hinge(wb.ZL)
        locs[('arm_up', s)] = hinge(wb.ZU)
        dl = wb.steer_solution(s, psi[s], eta)
        if math.isnan(dl):
            bad.append('steer_solution NaN side %+d (psi %.2f)' % (s, psi[s]))
            continue                      # wheel group and tie rod of this side are left out of this pose
        dx, dz = wb.arm_ball(s, psi[s])
        locs[('wheel', s)] = cq.Location(V(dx, 0, dz)) * wb._loc_axis((s * wb.KX, wb.KY, 0), (0, 0, 1), dl)
        locs[('tie', s)] = wb.tie_rod_loc(s, psi[s], dl, eta)[0]
    locs[('horn', 0)] = wb._loc_axis((0, wb.SERVO_SHAFT_Y, 0), (0, 0, 1), eta)
    lb, ls, eye = wb.shock_locs(psi[-1], psi[1])
    locs[('shock_b', 0)] = lb
    locs[('shock_s', 0)] = ls
    return locs, bad, eye, psi


def swept(parts, keys, box, group_of):
    """Swept clearance report: {pair: (min distance, pose tag)} under CLEAR for every moving part against every other part."""
    t0 = time.time()
    leafk = {leaf(k).replace('_', ' '): k for k in keys}
    wl = {}
    for e in WHITELIST:
        for a, b, why, floor, _s in _expand(e):
            if a in leafk and b in leafk:
                wl[frozenset((leafk[a], leafk[b]))] = (why, floor)
    stops = {}
    for st, arm, end in STOPS:
        for s in SIDES:
            a, b = st.format(s=s), arm.format(s=s)
            if a in leafk and b in leafk:
                stops[frozenset((leafk[a], leafk[b]))] = (a, b, end(s) if end else None)
    poses = [(phi, eta) for phi in SWEEP_PHIS for eta in ETAS]
    locs_all = {(phi, eta): pose_locs(phi, eta)[0] for phi, eta in poses}
    mov = [k for k in keys if k in group_of]
    moved = {}            # (pose, key) -> (shape, bbox)
    sbox = {}
    for k in mov:
        bs = []
        for p in poses:
            lc = locs_all[p].get(group_of[k])
            if lc is None:
                continue
            sh = parts[k].moved(lc)
            moved[(p, k)] = (sh, bb(sh))
            bs.append(moved[(p, k)][1])
        sbox[k] = tuple(f(b[i] for b in bs) for i, f in enumerate((min, max) * 3)) if bs else None
    grow = lambda b, g: (b[0] - g, b[1] + g, b[2] - g, b[3] + g, b[4] - g, b[5] + g)
    hit = lambda a, b, g: all(a[i] - g <= b[i + 1] and b[i] - g <= a[i + 1] for i in (0, 2, 4))
    res, ndist, nclip, errs = {}, 0, 0, 0
    stop_d = {}
    for a in mov:
        if sbox[a] is None:
            continue
        for b in keys:
            pair = frozenset((a, b))
            if a == b or pair in res or group_of.get(b) == group_of[a] or (b in group_of and keys.index(b) < keys.index(a) and b in mov):
                continue
            if b in group_of:          # moving against moving: both placed in each pose
                tgt = None
            else:
                if not hit(sbox[a], box[b], CLEAR):
                    continue
                tgt = parts[b]
                big = (box[b][1] - box[b][0]) * (box[b][3] - box[b][2]) * (box[b][5] - box[b][4]) > 8.0 * max(1.0, (sbox[a][1] - sbox[a][0]) * (sbox[a][3] - sbox[a][2]) * (sbox[a][5] - sbox[a][4]))
                if big:
                    g = grow(sbox[a], CLIP_M)
                    try:
                        tgt = tgt.intersect(cq.Solid.makeBox(g[1] - g[0], g[3] - g[2], g[5] - g[4], V(g[0], g[2], g[4])))
                        nclip += 1
                    except Exception as exc:
                        errs += 1
                        print('SWEPT ERROR clip %s <> %s: %s' % (short(a), short(b), exc), flush=True)
                        continue
                    if not tgt.Solids():
                        continue
                tbox = bb(tgt)
            best = None
            for p in poses:
                if (p, a) not in moved:
                    continue
                sa, ba = moved[(p, a)]
                if tgt is None:
                    if (p, b) not in moved:
                        continue
                    sb, bbx = moved[(p, b)]
                else:
                    sb, bbx = tgt, tbox
                if not hit(ba, bbx, CLEAR):
                    if pair in stops:
                        stop_d.setdefault(pair, {})[p] = CLEAR
                    continue
                try:
                    d = sa.distance(sb)
                except Exception as exc:
                    errs += 1
                    print('SWEPT ERROR %s <> %s: %s' % (short(a), short(b), exc), flush=True)
                    continue
                ndist += 1
                if pair in stops:
                    stop_d.setdefault(pair, {})[p] = d
                if best is None or d < best[0]:
                    best = (d, p)
            if best is not None and best[0] < CLEAR:
                res[pair] = best
    print('--- swept clearance (lean %s deg x horn %s deg, FRONT_BUMP %+.1f mm; rule %.1f mm; %d distance calls, %d clipped parts, %d errors, %.0f s)'
          % ('/'.join('%+.0f' % q for q in SWEEP_PHIS), '/'.join('%+.0f' % q for q in ETAS), BUMP, CLEAR, ndist, nclip, errs, time.time() - t0))
    real = 0
    for pair, (d, p) in sorted(res.items(), key=lambda kv: kv[1][0]):
        a, b = sorted(pair, key=keys.index)
        tag = 'phi %+3.0f eta %+3.0f' % p
        if pair in stops:
            continue
        if pair in wl:
            why, floor = wl[pair]
            ok = d >= floor - 1e-6
            print('%s %6.3f mm at %s: %s <> %s  (%s%s)' % ('WHITELIST' if ok else 'WL-BELOW ', d, tag, short(a), short(b), why,
                                                       '' if ok else ', below its %.2f mm' % floor))
            real += 0 if ok else 1
        else:
            real += 1
            print('SWEPT     %6.3f mm at %s: %s <> %s' % (d, tag, short(a), short(b)))
    for pair, (sa, sb, end) in sorted(stops.items(), key=lambda kv: kv[1][0]):
        ds = stop_d.get(pair, {})
        endp = [p for p in poses if end is not None and abs(p[0] - end[0]) < 1e-6 and abs(BUMP - end[1]) < 1e-6]
        at_end = min((ds.get(p, CLEAR) for p in endp), default=None)
        other = min((v for p, v in ds.items() if p not in endp), default=CLEAR)
        ok_end = at_end is None or at_end <= TOUCH
        ok_other = other >= CLEAR - 1e-6
        real += (0 if ok_end else 1) + (0 if ok_other else 1)
        print('STOP      %s <> %s: %s; every other pose %s' % (sa, sb,
              ('end pose phi %+.0f bump %+.0f: %.3f mm (%s)' % (end[0], end[1], at_end, 'touches' if ok_end else 'NOT TOUCHING')) if at_end is not None
              else 'end pose not in this run' if end else 'no end pose (base, must stay clear)',
              ('>= %.1f mm' % CLEAR) if other >= CLEAR else '%.3f mm (UNDER %.1f)' % (other, CLEAR)))
    print('swept: %d pairs under %.1f mm, %d of them whitelisted or stops at their end pose, %d to look at' % (len(res), CLEAR, len(res) - real if real <= len(res) else 0, real))
    return real


def main():
    t0 = time.time()
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'output/model.step'
    parts = load(path)
    if os.environ.get('PRINTED_TIE'):      # option check: the printed tie rods (wb.printed_tie_rod, kit ST3) in place of the steel tubes
        for k in list(parts):
            for s_ in (1, -1):
                if leaf(k) == 'Tie_rod_%d' % s_:
                    from parts.util import chamfer_moving
                    parts[k] = chamfer_moving(wb.printed_tie_rod(s_), 'printed tie rod %d' % s_)
        print('PRINTED_TIE: tie rods replaced by the printed option')
    keys = list(parts)
    box = {k: bb(parts[k]) for k in keys}
    print('front_check: %s, %d parts, loaded in %.0f s' % (path, len(keys), time.time() - t0), flush=True)
    findings, errors = 0, 0

    # ---- rest
    target = [k for k in keys if k.startswith(REST_GROUPS) or leaf(k) in REST_LEAVES or leaf(k).startswith(REST_PREFIX)]
    tset = set(target)
    rest, npair = {}, 0
    for a in target:
        for b in keys:
            if a == b or (b in tset and keys.index(b) < keys.index(a)) or not bb_hit(box[a], box[b]):
                continue
            npair += 1
            try:
                v, where = overlap(parts[a], parts[b])
            except Exception as exc:
                errors += 1
                print('REST ERROR %s <> %s: %s' % (short(a), short(b), exc), flush=True)
                continue
            rest[frozenset((a, b))] = v
            if v > MIN_VOL:
                findings += 1
                print('REST %9.2f mm3  %s <> %s  [%s]' % (v, short(a), short(b), where), flush=True)
    t1 = time.time()
    print('rest: %d of %d parts checked, %d boolean pairs, %d overlaps, %.0f s' % (len(target), len(keys), npair, findings, t1 - t0), flush=True)

    # ---- poses
    by_leaf = {leaf(k): k for k in keys}
    group_of, missing = {}, []
    for gid, names in moving_groups().items():
        for n in names:
            k = by_leaf.get(n.replace(' ', '_'))
            if k is None:
                missing.append(n)
            else:
                group_of[k] = gid
    if missing:
        print('MISSING in the STEP (named in lean_front.py): ' + ', '.join(missing))
    eye0 = wb.shock_locs(0.0, 0.0)[2]
    pose_hits, worst = 0, {}
    for phi in PHIS:
        for eta in ETAS:
            tag = 'phi %+3.0f eta %+3.0f' % (phi, eta)
            locs, bad, eye, psi = pose_locs(phi, eta)
            for msg in bad:
                findings += 1
                print('POSE %s  KINEMATICS %s' % (tag, msg), flush=True)
            print('pose %s: psi %+.2f / %+.2f deg (+x / -x), shock eye distance %.2f mm (rest %.2f, %+.2f)'
                  % (tag, psi[1], psi[-1], eye, eye0, eye - eye0), flush=True)
            shp, bx = dict(parts), dict(box)
            mov = [k for k in keys if group_of.get(k) in locs]
            for k in mov:
                shp[k] = parts[k].moved(locs[group_of[k]])
                bx[k] = bb(shp[k])
            done = set()
            for a in mov:
                for b in keys:
                    pair = frozenset((a, b))
                    if a == b or pair in done or group_of.get(a) == group_of.get(b) or not bb_hit(bx[a], bx[b]):
                        continue
                    if b not in shp:
                        continue
                    done.add(pair)
                    try:
                        v, where = overlap(shp[a], shp[b])
                    except Exception as exc:
                        errors += 1
                        print('POSE %s ERROR %s <> %s: %s' % (tag, short(a), short(b), exc), flush=True)
                        continue
                    r = rest.get(pair, 0.0)
                    if v > MIN_VOL and v > r + max(MIN_VOL, 0.25 * r):      # new, or clearly more than at rest
                        pose_hits += 1
                        print('POSE %s %9.2f mm3 (rest %.2f)  %s <> %s  [%s]' % (tag, v, r, short(a), short(b), where), flush=True)
                        w = worst.get(pair)
                        if w is None or v > w[0]:
                            worst[pair] = (v, tag, short(a), short(b), (w[4] if w else 0) + 1)
                        else:
                            worst[pair] = w[:4] + (w[4] + 1,)
    findings += pose_hits
    print('--- summary')
    for v, tag, a, b, n in sorted(worst.values(), reverse=True):
        print('WORST %9.2f mm3 at %s, in %d of %d poses: %s <> %s' % (v, tag, n, len(PHIS) * len(ETAS), a, b))
    print('rest overlaps %d, pose overlaps %d (%d pairs), boolean errors %d, total %.0f s'
          % (findings - pose_hits, pose_hits, len(worst), errors, time.time() - t0))
    swept(parts, keys, box, group_of)
    print('collision threshold %.2f mm3; exit code from overlaps and boolean errors only' % MIN_VOL)
    sys.exit(1 if findings or errors else 0)


if __name__ == '__main__':
    main()
