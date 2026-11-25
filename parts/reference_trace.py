"""Manually traced landmarks in Screenshot 2026-11-10 at 2.44.31 PM.png.
Pixel X follows vehicle length, pixel Y points down. A uniform calibration
maps the visible shell from pixel 280 to 1428 onto 278 mm. The rocker is Y=450.
Mechanical parts, mirrors and roof lights are deliberately excluded.
"""
PIXEL_FRONT=280.0
PIXEL_REAR=1428.0
PIXEL_ROCKER=450.0
MM_PER_PIXEL=278.0/(PIXEL_REAR-PIXEL_FRONT)

# Every entry is (image X, image Y, transverse half-width in mm).
SIDE=[(437,219,56),(457,170,50),(622,234,46),(815,204,50),(930,157,44),
      (1082,144,43),(940,286,60),(889,319,56),(943,345,62),
      (836,446,46),(473,435,35),(522,368,48),(510,259,61)]
CREASES=[(674,295,57),(650,359,45),(825,414,45)]
TAIL=[(1082,144,43),(1135,98,31),(1241,33,28),(1428,70,28),
      (1412,100,27),(1316,119,25),(1237,171,24),(1195,232,24),
      (1143,239,25),(1127,220,29),(1165,145,32)]
QUARTER=[(889,319,56),(826,282,66),(928,174,69.5),
         (1082,144,43),(1000,210,54),(940,286,60)]
ROOF=[(660,63,34),(760,33,34),(905,12,34),(1135,98,31)]
HOOD=[(280,214,24),(390,174,42),(457,170,50)]
CHEEK=[(280,214,24),(390,174,42),(457,170,50),(437,219,56),(365,242,35),(280,315,16)]
INTAKES=[[(538,420),(620,394),(720,381),(664,412)],
         [(690,422),(780,415),(865,363)]]
# Lower window sill: one single straight rail, angled up from the A-pillar to the rear canopy corner.
WINDOW_BELT=[(457,170,50),(1082,144,43)]
# Master-surface regularisation (see _regularize_flank at the end of this file): small half-width offsets of the window belt
# line so that the flank fan of triangles along it is exactly planar. Piecewise linear in px, zero at both belt ends.
BELT_DW=[(457,0.0),(1082,0.0)]
def _belt_dw(px):
    for (xa,da),(xb,db) in zip(BELT_DW,BELT_DW[1:]):
        if xa<=px<=xb:
            return da+(db-da)*(px-xa)/(xb-xa)
    return 0.0
def belt_station(px):
    for a,b in zip(WINDOW_BELT,WINDOW_BELT[1:]):
        if a[0] <= px <= b[0]:
            t=(px-a[0])/(b[0]-a[0])
            return (px,a[1]+t*(b[1]-a[1]),a[2]+t*(b[2]-a[2])+_belt_dw(px))
    raise ValueError(f'Belt station {px} is outside the sill')
# Bring the body top up to the same line instead of leaving the old dipped edge.
SIDE=[belt_station(p[0]) if p[0] in (457,622,815,930,1082) else p for p in SIDE]
from parts.params import WHEEL_NOTCH_HALF_WIDTH
SIDE=[(px,py,WHEEL_NOTCH_HALF_WIDTH if px==510 else width) for px,py,width in SIDE]
WING_OPENING=[(870,260),(943,192),(1005,160),(956,230),(914,275)]

def plan_width(y):
    """Transverse width factor at blueprint station y (mm): slims the cabin, full width at nose and tail."""
    from parts.params import PLAN_STATIONS
    if y<=PLAN_STATIONS[0][0]: return PLAN_STATIONS[0][1]
    for (ya,sa),(yb,sb) in zip(PLAN_STATIONS,PLAN_STATIONS[1:]):
        if ya<=y<=yb: return sa+(sb-sa)*(y-ya)/(yb-ya)
    return PLAN_STATIONS[-1][1]

def traced(p,side=1):
    px,py,x=p
    if px==1082 and abs(py-144)<1e-8:
        from parts.params import REAR_SHOULDER_WIDTH,REAR_SHOULDER_PY
        x=REAR_SHOULDER_WIDTH
        py=REAR_SHOULDER_PY
    if px==928 and abs(py-174)<1e-8:
        py=230.0
    y=(px-PIXEL_FRONT)*MM_PER_PIXEL-139
    return (side*x*plan_width(y),y,(PIXEL_ROCKER-py)*MM_PER_PIXEL)


def frame_belt(p,side=1):
    """Virtual straight window rail is independent of the lowered shoulder tip."""
    px,py,width=p
    if px==1082:
        y=(px-PIXEL_FRONT)*MM_PER_PIXEL-139
        from parts.params import REAR_SHOULDER_WIDTH
        return (side*REAR_SHOULDER_WIDTH*plan_width(y),y,(PIXEL_ROCKER-144)*MM_PER_PIXEL)
    return traced(p,side)


def shoulder_station(px):
    """The body shoulder drops after the B-pillar, while the main window stays straight."""
    if px<=930:
        return belt_station(px)
    from parts.params import REAR_SHOULDER_WIDTH,REAR_SHOULDER_PY
    a=belt_station(930);t=(px-930)/(1082-930)
    return (px,a[1]+t*(REAR_SHOULDER_PY-a[1]),a[2]+t*(REAR_SHOULDER_WIDTH-a[2]))

def cross(a,b,c):
    return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def inside(p,a,b,c):
    q=[cross(a,b,p),cross(b,c,p),cross(c,a,p)]
    return min(q)>=-1e-7 or max(q)<=1e-7

def triangulate(poly,interior=()):
    """Ear clipping keeps concave traced panel boundaries exact."""
    poly=list(poly)
    area=sum(a[0]*b[1]-a[1]*b[0] for a,b in zip(poly,poly[1:]+poly[:1]))
    orientation=1 if area>0 else -1
    remaining=list(range(len(poly))); result=[]
    while len(remaining)>3:
        for k,i in enumerate(remaining):
            a,b,c=[poly[j] for j in (remaining[k-1],i,remaining[(k+1)%len(remaining)])]
            if cross(a,b,c)*orientation<=1e-8: continue
            if any(inside(poly[j],a,b,c) for j in remaining if poly[j] not in (a,b,c)): continue
            result.append([a,b,c]);remaining.pop(k);break
        else: raise ValueError('Trace polygon cannot be triangulated')
    result.append([poly[i] for i in remaining])
    for p in interior:
        for k,(a,b,c) in enumerate(result):
            if inside(p,a,b,c):
                result[k:k+1]=[[a,b,p],[b,c,p],[c,a,p]];break
    return result

def mesh(poly,side=1,interior=()):
    return [[traced(p,side) for p in tri] for tri in triangulate(poly,interior)]


# ---------------------------------------------------------------------------------------------------------------------
# Master-surface regularisation of the flank.
# Neighbouring flank triangles that are 0.3-9 degrees apart are near-misses of one plane. The half-widths of the free
# traced points (the only free direction: y and z come from the side-view trace) are shifted by the smallest amount that
# makes every such neighbouring pair exactly coplanar, so the flank merges into larger true planes with straight creases.
# Coplanarity of four points is linear in their x values, so this is a plain least-squares solve.
REGULARIZE_MAX_ANGLE = 9.0
REGULARIZE_MIN_ANGLE = 0.3
REGULARIZE_MAX_SHIFT = 5.0      # trace mm of half-width; larger moves are left out of the solve
REGULARIZE_REPORT = {}


def _regularize_flank():
    import itertools
    import numpy as np
    global SIDE, CREASES, HOOD, CHEEK
    belt_px = (622, 815)
    fixed_px = {280, 457, 930, 1082, 510}   # nose corner, belt ends, B-pillar foot, wheel notch stay put
    key = lambda p: (p[0], p[1])
    FOLD = (1000, 210)

    def xyz(p):
        x, y, z = traced(p, 1)
        return np.array([x, y, z])

    def normal(t):
        a, b, c = [xyz(p) for p in t]
        n = np.cross(b - a, c - a)
        return n / np.linalg.norm(n)

    def pw_of(p):
        return traced((p[0], p[1], 1.0), 1)[0]          # d x / d width at this point

    # Surface x at the fold point, as a barycentric combination of the full side mesh (exactly what make_shell evaluates).
    full = triangulate(list(SIDE), CREASES)
    qy, qz = traced((1000, 210, 54))[1:]
    lam = None
    for t in full:
        pts = np.array([xyz(p) for p in t])
        wts = np.linalg.solve(np.vstack((pts[:, 1], pts[:, 2], np.ones(3))), [qy, qz, 1.0])
        if wts.min() >= -1e-7:
            lam = [(key(p), float(w)) for p, w in zip(t, wts)]
            fold_w = float(sum(w * xyz(p)[0] for p, w in zip(t, wts)))
            break
    assert lam, 'fold point outside the side mesh'
    corner = next(i for i, p in enumerate(SIDE) if p[0] == 1082)
    outline = [p for p in SIDE if p[0] != 943]
    outline.insert(next(i for i, p in enumerate(outline) if p[0] == 1082) + 1, (FOLD[0], FOLD[1], fold_w))
    tri_sets = [triangulate(outline, CREASES), [[traced_tri for traced_tri in t] for t in triangulate(list(CHEEK), [])]]

    table = {key(p): p for ts in tri_sets for t in ts for p in t}
    free = [k for k in table if k[0] not in fixed_px and k != (928, 174)]
    col = {k: i for i, k in enumerate(free)}
    rows, rhs = [], []
    for tris in tri_sets:
        for t1, t2 in itertools.combinations(tris, 2):
            k2 = {key(q) for q in t2}
            shared = [p for p in t1 if key(p) in k2]
            if len(shared) != 2:
                continue
            ang = np.degrees(np.arccos(min(1.0, abs(float(normal(t1) @ normal(t2))))))
            if not (REGULARIZE_MIN_ANGLE < ang < REGULARIZE_MAX_ANGLE):
                continue
            ks = {key(q) for q in shared}
            quad = shared + [p for p in t1 if key(p) not in ks] + [p for p in t2 if key(p) not in ks]
            pts = [xyz(p) for p in quad]
            row = np.zeros(len(free)); const = 0.0
            for i, p in enumerate(quad):
                others = [pts[j] for j in range(4) if j != i]
                cof = ((-1) ** i) * np.linalg.det(np.array([[o[1], o[2], 1.0] for o in others]))
                if key(p) in col:
                    row[col[key(p)]] += cof * pw_of(p)
                const += cof * pts[i][0]
            rows.append(row); rhs.append(-const)
    npairs = len(rows)
    # The fold width is not free: make_shell takes it from the side mesh, so it must follow its three neighbours.
    if FOLD in col:
        row = np.zeros(len(free)); row[col[FOLD]] = 1.0
        for k, w in lam:
            if k in col:
                row[col[k]] -= w * pw_of(table[k])
        rows.append(row * 1000.0); rhs.append(0.0)
    A = np.array(rows); b = np.array(rhs)
    keep = np.ones(len(free), bool)
    for _ in range(2):
        d, *_ = np.linalg.lstsq(A * keep[None, :], b, rcond=None)
        d = d * keep
        big = np.abs(d) > REGULARIZE_MAX_SHIFT
        if not big.any(): break
        keep &= ~big
    REGULARIZE_REPORT.update(pairs=npairs, max_shift=float(np.abs(d).max()), residual=float(np.abs(A @ d - b).max()))
    dw = {k: float(d[col[k]]) for k in free if k != FOLD}
    nodes = [(457, 0.0)] + [(px, sum(v for k, v in dw.items() if k[0] == px)) for px in belt_px] + [(930, 0.0), (1082, 0.0)]
    BELT_DW[:] = nodes
    new_side = []
    for p in SIDE:
        if p[0] in belt_px or p[0] in (457, 930, 1082):
            new_side.append(belt_station(p[0]) if p[0] in belt_px else p)
        else:
            new_side.append((p[0], p[1], p[2] + dw.get(key(p), 0.0)))
    SIDE = new_side
    CREASES = [(p[0], p[1], p[2] + dw.get(key(p), 0.0)) for p in CREASES]
    HOOD = [(p[0], p[1], p[2] + dw.get(key(p), 0.0)) for p in HOOD]
    CHEEK = [(p[0], p[1], p[2] + dw.get(key(p), 0.0)) for p in CHEEK]


import os as _os
if _os.environ.get('SOMA_NO_REGULARIZE') != '1':
    _regularize_flank()
    print('flank regularization:', {k: round(v, 3) if isinstance(v, float) else v for k, v in REGULARIZE_REPORT.items()}, 'belt dw', [(a, round(b, 2)) for a, b in BELT_DW])
