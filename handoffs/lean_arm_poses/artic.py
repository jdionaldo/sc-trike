"""Articulated interference check on output/model.step (run with cwd = model root).
Both front arms at travel t (tip shaft z +t), lean beam turned a degrees about its vertical bolt."""
import math, sys, json, itertools
import cadquery as cq
from soma import import_assembly

V = cq.Vector
P_ARM = (-116.8, 47.5); P_TIP = (-216.6, 40.6)       # world (y, z)
P_UL = (-119.4, 97.9)                                 # upper link inner hinge
BEAM_P = V(0, -109.6, 0)
TIE_IN = {1: V(68.75, -95.0, 25.85)}                  # horn ball centre
TIE_OUT = {1: V(106.55, -214.2, 16.1)}                # knuckle ball centre
SH_LO = {1: V(65.0, -154.0, 74.9)}; SH_UP = {1: V(57.4, -121.95, 72.8)}
for d in (TIE_IN, TIE_OUT, SH_LO, SH_UP): d[-1] = V(-d[1].x, d[1].y, d[1].z)
MIN = 0.01

asm = import_assembly('output/model.step')
parts = {}
for n, node in asm.objects.items():
    if node.obj is None: continue
    s = node.obj.val() if isinstance(node.obj, cq.Workplane) else node.obj
    parts[n] = s.moved(node.loc)

def theta(t):
    yr, zr = P_TIP[0] - P_ARM[0], P_TIP[1] - P_ARM[1]
    L = math.hypot(yr, zr); f0 = math.atan2(zr, yr)
    f = math.pi - math.asin((zr + t) / L)              # tip lies toward -y: branch near pi
    return f - f0 if abs(f - f0) < 1 else (f - f0) - 2 * math.pi * round((f - f0) / (2 * math.pi))

def rot_x(p, c, th):  # rotate point p about x axis through (y,z)=c
    y, z = p.y - c[0], p.z - c[1]
    return V(p.x, c[0] + y * math.cos(th) - z * math.sin(th), c[1] + y * math.sin(th) + z * math.cos(th))

def rot_z(p, a):
    x, y = p.x - BEAM_P.x, p.y - BEAM_P.y
    return V(BEAM_P.x + x * math.cos(a) - y * math.sin(a), BEAM_P.y + x * math.sin(a) + y * math.cos(a), p.z)

def align(s, pivot_old, pivot_new, v_old, v_new):
    """translate pivot_old -> pivot_new and rotate v_old direction onto v_new about it"""
    s = s.translate(pivot_new - pivot_old)
    a, b = v_old.normalized(), v_new.normalized()
    ax = a.cross(b)
    if ax.Length < 1e-9: return s
    ang = math.degrees(math.atan2(ax.Length, a.dot(b)))
    return s.rotate(pivot_new, pivot_new + ax.normalized(), ang)

def pose(t, a_deg):
    th = theta(t); thd = math.degrees(th); a = math.radians(a_deg)
    tip0 = V(0, *P_TIP); dvec = rot_x(tip0, P_ARM, th) - tip0
    out, grp = {}, {}
    def put(n, s, g): out[n] = s; grp[n] = g
    for sx in (1, -1):
        k = '%d' % sx
        for n in ('Chassis/Suspension/arm_' + k, 'Chassis/Drivetrain/tip_shaft_' + k, 'Chassis/Front_shocks/Front_shock_pin_lower_' + k):
            put(n, parts[n].rotate(V(0, *P_ARM), V(1, *P_ARM), thd), 'arm' + k)
        for n in ['Chassis/wheel_f_' + k, 'Chassis/Steering/carrier_' + k, 'Chassis/Steering/knuckle_' + k, 'Chassis/Wheels/mock_axle_' + k,
                  'Chassis/Wheels/mock_tire_' + k, 'Chassis/Front_shocks/Uplink_pin_outer_' + k] + \
                 ['Chassis/b_steer_knuckle_end_%s_%s' % (q, k) for q in ('ball', 'stud', 'nut', 'washer')]:
            put(n, parts[n].translate(dvec), 'hub' + k)
        put('Chassis/Suspension/uplink_' + k, parts['Chassis/Suspension/uplink_' + k].rotate(V(0, *P_UL), V(1, *P_UL), thd), 'ul' + k)
        ti, to = TIE_IN[sx], TIE_OUT[sx]
        put('Chassis/Steering/tie_rod_' + k, align(parts['Chassis/Steering/tie_rod_' + k], to, to + dvec, ti - to, ti - (to + dvec)), 'tie' + k)   # outer eye stays on the knuckle stud (no bump steer modelled), rod points at the horn ball
        lo_new, up_new = rot_x(SH_LO[sx], P_ARM, th), rot_z(SH_UP[sx], a)
        # shock split at mid-length into an upper body (rides the beam eye) and a lower shaft end (rides the arm eye), each aligned to the new axis: telescopes
        sh = parts['Chassis/Front_shocks/Front_shock_shock_' + k]
        ax0 = SH_LO[sx] - SH_UP[sx]; mid = SH_UP[sx] + ax0 * 0.5
        half = cq.Solid.makeBox(400, 400, 400, V(-200, -200, 0)).moved(cq.Location(cq.Plane(origin=mid.toTuple(), xDir=ax0.cross(V(0, 0, 1)).normalized().toTuple(), normal=ax0.normalized().toTuple())))
        lo_half, up_half = sh.intersect(half), sh.cut(half)
        up_r = up_half.rotate(BEAM_P, BEAM_P + V(0, 0, 1), a_deg)
        put('Chassis/Front_shocks/Front_shock_shock_up_' + k, align(up_r, up_new, up_new, rot_z(SH_LO[sx], a) - up_new, lo_new - up_new), 'beam')
        lo_r = lo_half.rotate(V(0, *P_ARM), V(1, *P_ARM), thd)
        put('Chassis/Front_shocks/Front_shock_shock_lo_' + k, align(lo_r, lo_new, lo_new, lo_new - rot_x(SH_UP[sx], P_ARM, th), lo_new - up_new), 'arm' + k)
    for n in ['Chassis/Front_shocks/Lean_beam', 'Chassis/Front_shocks/Front_shock_pin_upper_1', 'Chassis/Front_shocks/Front_shock_pin_upper_-1']:
        put(n, parts[n].rotate(BEAM_P, BEAM_P + V(0, 0, 1), a_deg), 'beam')
    return out, grp, dvec

def bb_hit(a, b):
    return all(getattr(a, k + 'max') >= getattr(b, k + 'min') and getattr(b, k + 'max') >= getattr(a, k + 'min') for k in 'xyz')

FOCUS = ('arm_', 'uplink_', 'tie_rod_', 'Front_shock_shock_', 'Lean_beam', 'Lean_centring_spring')
results = []
for t in (-14.0, 10.0, 20.0):
    for a in (-3.2, 0.0, 3.2):
        moved, grp, dvec = pose(t, a)
        cur = {n: v for n, v in parts.items() if 'Front_shock_shock_' not in n}; cur.update(moved)
        bbs = {n: s.BoundingBox() for n, s in cur.items()}
        hits = []
        for an, bn in itertools.combinations(cur, 2):
            if an not in moved and bn not in moved: continue
            if an in moved and bn in moved and grp[an] == grp[bn]: continue
            if not any(f in an or f in bn for f in FOCUS): continue
            if not bb_hit(bbs[an], bbs[bn]): continue
            try:
                ov = cur[an].intersect(cur[bn]); v = ov.Volume()
            except Exception as e:
                hits.append((an, bn, 'FAILED ' + str(e))); continue
            if v > MIN:
                b = ov.BoundingBox()
                hits.append((an, bn, round(v, 3), [round(x, 1) for x in (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)]))
        print('travel %+.0f mm, lean %+.1f deg, theta %.2f deg, hub dz %.2f dy %.2f: %d overlaps' % (t, a, math.degrees(theta(t)), dvec.z, dvec.y, len(hits)), flush=True)
        for h in hits: print('   ', h, flush=True)
        results.append(dict(travel=t, lean=a, hits=hits))
json.dump(results, open(sys.argv[1] if len(sys.argv) > 1 else 'artic.json', 'w'), indent=1, default=str)
