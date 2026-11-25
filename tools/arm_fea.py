"""Beam model of the printed rear swingarm (parts/swingarm.py): every tube of the real arm becomes a beam element.
Loads at the tyre contact patch, wheel path through the 8 mm steel axle, shock force at the shock pin, pivot bosses held.
Run:  soma-python tools/arm_fea.py   (prints stiffness, tyre-plane twist and the worst tube stresses per load case)
Assumptions (ASSUMED, not measured): PETG E 1500 MPa / G 550 MPa across a printed tube, working stress limit 18 MPa (layer lines),
solid octagon section (side 0.88 d, chamfer 18 %), shock force vertical at the pin."""
import sys, math
sys.path.insert(0, '.')
import numpy as np
import parts.swingarm as sw
import parts.cage as cg

E_P, G_P, SIG_LIM = 1500.0, 550.0, 18.0
E_S, G_S = 200000.0, 77000.0
R_TYRE = 70.0


def octagon(d):
    s = 0.88 * d; c = 0.18 * s
    pts = [(-s/2+c, -s/2), (s/2-c, -s/2), (s/2, -s/2+c), (s/2, s/2-c), (s/2-c, s/2), (-s/2+c, s/2), (-s/2, s/2-c), (-s/2, -s/2+c)]
    A = I = 0.0
    for (x0, y0), (x1, y1) in zip(pts, pts[1:] + pts[:1]):
        cr = x0 * y1 - x1 * y0
        A += cr / 2; I += cr * (y0*y0 + y0*y1 + y1*y1) / 12
    return abs(A), abs(I), 0.14 * s ** 4, s / 2 * 1.08, 0.208 * s ** 3     # A, I, J, c, torsion section modulus


def capture():
    got = {}
    orig = cg._Frame.build
    def spy(self, *a, **k):
        self._split_crossings(); got['F'] = self; raise StopIteration
    cg._Frame.build = spy
    try: sw.make_rear_arm()
    except StopIteration: pass
    finally: cg._Frame.build = orig
    return got['F']


def solve(mem, nodes, loads, fixed, springs=()):
    n = len(nodes); K = np.zeros((6 * n, 6 * n)); f = np.zeros(6 * n)
    el = []
    for (i, j, E, G, A, I, J, kind) in mem:
        p, q = np.array(nodes[i]), np.array(nodes[j]); L = np.linalg.norm(q - p); ex = (q - p) / L
        ref = np.array([0, 0, 1.0]) if abs(ex[2]) < 0.99 else np.array([1.0, 0, 0])
        ey = np.cross(ref, ex); ey /= np.linalg.norm(ey); ez = np.cross(ex, ey)
        R = np.array([ex, ey, ez]); T = np.kron(np.eye(4), R)
        k = np.zeros((12, 12)); a = E * A / L; t = G * J / L; b1 = 12 * E * I / L**3; b2 = 6 * E * I / L**2; b3 = 4 * E * I / L; b4 = 2 * E * I / L
        k[0, 0] = k[6, 6] = a; k[0, 6] = k[6, 0] = -a
        k[3, 3] = k[9, 9] = t; k[3, 9] = k[9, 3] = -t
        for (v, th, sgn) in ((1, 5, 1), (2, 4, -1)):
            k[v, v] = k[v+6, v+6] = b1; k[v, v+6] = k[v+6, v] = -b1
            k[v, th] = k[th, v] = sgn * b2; k[v, th+6] = k[th+6, v] = sgn * b2
            k[v+6, th] = k[th, v+6] = -sgn * b2; k[v+6, th+6] = k[th+6, v+6] = -sgn * b2
            k[th, th] = k[th+6, th+6] = b3; k[th, th+6] = k[th+6, th] = b4
        kg = T.T @ k @ T; idx = list(range(6*i, 6*i+6)) + list(range(6*j, 6*j+6))
        K[np.ix_(idx, idx)] += kg; el.append((i, j, T, k, L, idx))
    for nd, v in loads.items(): f[6*nd:6*nd+6] += v
    free = [d for d in range(6 * n) if d not in fixed]
    u = np.zeros(6 * n); u[free] = np.linalg.solve(K[np.ix_(free, free)] + 1e-6 * np.eye(len(free)), f[free])
    react = K @ u - f
    return u, el, react


def run(variant='0', quiet=False):
    F = capture()
    nodes = []; key = {}
    def N(p):
        k = tuple(round(float(c), 1) for c in p)
        if k not in key: key[k] = len(nodes); nodes.append(k)
        return key[k]
    mem = []; meta = []
    def add(p, q, d, kind, mat='P', rect=None):
        i, j = N(p), N(q)
        if i == j: return
        if mat == 'S': E, G = E_S, G_S
        else: E, G = E_P, G_P
        if d is None: A, I, J = 1e4, 1e8, 1e8; c = 1; sm = 1
        else: A, I, J, c, sm = octagon(d)
        mem.append((i, j, E, G, A, I, J, kind)); meta.append((p, q, d, c, sm, kind, mat))
    for a, b, d in F.segs: add(a, b, d, 'tube')
    P, Ax, AF, AR = sw.PIVOT_YZ, sw.AXLE_YZ, sw.APEX_YZ, sw.SHOCK_EYE_YZ
    xi, xo = sw.PLATE_X; xc = sw.EAR_GAP / 2 + sw.EAR_T / 2
    # solid webs and necks: stiff links (pivot to chord roots, axle hub to chord ends)
    U0, L0, U2, L2 = (122.0, 95.0), (122.0, 55.0), (218.0, 64.0), (218.0, 41.0)
    for x in (xi, xo):
        for q in (U0, L0): add((x, P[0], P[1]), (x, q[0], q[1]), 14.0, 'web')
        for q in (U2, L2): add((x, Ax[0], Ax[1]), (x, q[0], q[1]), 14.0, 'neck')
    # axle: steel 8 mm from the wheel centre plane through both ladder plates
    add((0, Ax[0], Ax[1]), (xi, Ax[0], Ax[1]), 8.0 / 0.88, 'axle', 'S'); add((xi, Ax[0], Ax[1]), (xo, Ax[0], Ax[1]), 8.0 / 0.88, 'axle', 'S')
    # tyre contact link (rigid)
    cnt = (0, Ax[0], Ax[1] - R_TYRE); add((0, Ax[0], Ax[1]), cnt, None, 'rigid')
    # shock: pin (steel M6) across both ears, ears, barrel at the front eye
    for yz in (AF, AR):
        add((-xc, yz[0], yz[1]), (xc, yz[0], yz[1]), 6.0 / 0.88, 'pin', 'S')
    add((xc, AF[0], AF[1]), (xc, AR[0], AR[1]), 11.0, 'lug'); add((-xc, AF[0], AF[1]), (-xc, AR[0], AR[1]), 11.0, 'lug')
    add((xc, AF[0], AF[1]), (xc, AF[0], AF[1] + sw.EAR_R - 3.0), 11.0, 'ear'); add((xc, AR[0], AR[1]), (xc, AR[0], AR[1] + sw.EAR_R - 3.0), 11.0, 'ear')
    # the -x ear is tied to the +x ear only through the pin and the barrel; the arch tubes meet the +x ear only
    add((-xc, AF[0], AF[1]), (xc, AF[0], AF[1]), (sw.ARCH_D + 2.0) / 0.88, 'barrel')
    # trial changes to the arm (variant letters), added to the real tube list
    if variant != '0':
        zb = 80.0
        S3 = (204.56, 68.34); S2b = (179.6, 78.9)
        if 'A' in variant:                    # bridge over the belt at the outboard end
            for x in (xi, xo): add((x, S3[0], S3[1]), (x, S3[0], zb), sw.STRUT_D, 'tube')
            add((xi, S3[0], zb), (xo, S3[0], zb), sw.STRUT_D, 'tube')
        if 'B' in variant:                    # Warren diagonals in the top plane from the root box to the bridge
            add((xi, S2b[0], S2b[1]), (xo, S3[0], zb), sw.STRUT_D, 'tube'); add((xo, S2b[0], S2b[1]), (xi, S3[0], zb), sw.STRUT_D, 'tube')
    if 'L' in variant:                        # lower tie plane under the belt: closes the open box
        zl = 41.0
        lows = [(122.0, 63.0), sw._lerp(L0, L2, 0.18), sw._lerp(L0, L2, 0.50), sw._lerp(L0, L2, 0.80)] + ([L2] if 'E' in variant else [])
        for q in lows:
            for x in (xi, xo): add((x, q[0], q[1]), (x, q[0], zl), sw.STRUT_D, 'tube')
            add((xi, q[0], zl), (xo, q[0], zl), sw.STRUT_D, 'tube')
        for q0, q1 in zip(lows, lows[1:]):
            add((xi, q0[0], zl), (xo, q1[0], zl), sw.STRUT_D, 'tube'); add((xo, q0[0], zl), (xi, q1[0], zl), sw.STRUT_D, 'tube')
    if 'M' in variant:                        # monocoque floor slab under the belt: stiff shear panel between the lower chords (modelled as stiff members)
        lows = [(122.0, 63.0), sw._lerp(L0, L2, 0.18), sw._lerp(L0, L2, 0.50), sw._lerp(L0, L2, 0.80), L2]
        zf = lambda q: q[1] - 5.5
        for q in lows:
            for x in (xi, xo): add((x, q[0], q[1]), (x, q[0], zf(q)), 14.0, 'web')
            add((xi, q[0], zf(q)), (xo, q[0], zf(q)), 14.0, 'web')
        for q0, q1 in zip(lows, lows[1:]):
            add((xi, q0[0], zf(q0)), (xo, q1[0], zf(q1)), 14.0, 'web'); add((xo, q0[0], zf(q0)), (xi, q1[0], zf(q1)), 14.0, 'web')
    if 'M' in variant:                        # shock bridge: riser blade on the inner plate and a beam to the +x ear (stiff members, d 18 ~ 24 mm deep beam)
        U0_, S1T_ = (122.0, 95.0), sw._lerp((122.0, 95.0), (218.0, 64.0), 0.27)
        add((xi, U0_[0], U0_[1]), (xi, AF[0], AF[1]), 18.0, 'web'); add((xi, S1T_[0], S1T_[1]), (xi, AR[0], AR[1]), 18.0, 'web')
        add((xi, AF[0], AF[1]), (xc, AF[0], AF[1]), 18.0, 'web'); add((xi, AR[0], AR[1]), (xc, AR[0], AR[1]), 18.0, 'web')
        add((xi, AF[0], AF[1]), (xi, AR[0], AR[1]), 18.0, 'web')
        for x in (xi, xo): add((x, U0_[0], U0_[1]), (x, S1T_[0], S1T_[1]), 11.0, 'web')   # top chords already in tubes; harmless duplicate stiff link at the root
        add((xi, 122.0, 90.0), (xo, 122.0, 90.0), 12.0, 'web')                              # root top web slab
    if 'M' in variant:                        # plate rails: window rails 14 wide x 11 thick (I 2500 mm^4 ~ d 17 octagon) run along every in-plane tube line
        for a, b, d in F.segs:
            if abs(a[0] - b[0]) < 1e-6 and round(a[0]) in (round(xi), round(xo)) and d in (sw.CHORD_D, sw.STRUT_D) and min(a[1], b[1]) >= 121.0:
                add(a, b, 17.0, 'tube')
    # pivot bosses to the plates' web nodes are the support nodes
    piv = [N((x, P[0], P[1])) for x in (xi, xo)]
    pin = N((0, AR[0], AR[1])); add((-xc, AR[0], AR[1]), (0, AR[0], AR[1]), 6.0 / 0.88, 'pin', 'S'); add((0, AR[0], AR[1]), (xc, AR[0], AR[1]), 6.0 / 0.88, 'pin', 'S')
    wheel = N((0, Ax[0], Ax[1])); cn = N(cnt)
    xp = sw.INNER_PIVOT_X
    add((xp, P[0], P[1]), (xp, P[0], P[1] + 4.0), 14.0, 'web')
    add((xp, AF[0], AF[1] - 2.0), (xp, AF[0], AF[1]), 14.0, 'web')
    add((xp, AF[0], AF[1]), (-xc, AF[0], AF[1]), 14.0, 'web'); add((xp, AF[0], AF[1]), (xc, AF[0], AF[1]), 14.0, 'web')
    if 'I' in variant: piv.append(N((xp, P[0], P[1])))     # second pivot support (A-frame)
    fixed = set()
    for k, nd in enumerate(piv):
        fixed |= ({6*nd+1, 6*nd+2} if (k == 2 and 'X' in variant) else {6*nd, 6*nd+1, 6*nd+2})   # 'X': inner pivot floats in x (axial location on the outer pair)
    fixed.add(6*piv[0] + 3)        # one pivot holds the roll about x (reaction reported: should stay near zero)
    lever_w = Ax[0] - P[0]; lever_s = AR[0] - P[0]
    cases = {'bump 50 N': (0, 0, 50.0), 'side 30 N': (30.0, 0, 0), 'drive 40 N': (0, 40.0, 0), 'bump 50 + side 30': (30.0, 0, 50.0)}
    if quiet: cases = {'side 30 N': cases['side 30 N'], 'bump 50 + side 30': cases['bump 50 + side 30']}
    print('nodes %d members %d; axle lever %.1f, shock lever %.1f' % (len(nodes), len(mem), lever_w, lever_s))
    out = {}
    for name, (fx, fy, fz) in cases.items():
        loads = {cn: np.array([fx, fy, fz, 0, 0, 0])}
        shock = fz * lever_w / lever_s + (fy * (Ax[1] - R_TYRE - P[1]) / lever_s if False else 0.0)
        # shock force (down on the pin, compressive when the wheel is pushed up)
        loads[pin] = np.array([0, 0, -shock, 0, 0, 0])
        u, el, react = solve(mem, nodes, loads, fixed)
        if 'I' in variant: print('   inner pivot reaction (N): x %.1f y %.1f z %.1f' % tuple(react[6*piv[2]:6*piv[2]+3]))
        # stresses
        worst = []
        for m, (i, j, T, k, L, idx) in zip(range(len(el)), el):
            p, q, d, c, sm, kind, mat = meta[m]
            if d is None or mat == 'S' or kind != 'tube': continue
            fl = k @ (T @ u[idx])
            N_ = max(abs(fl[0]), abs(fl[6])); Mt = max(abs(fl[3]), abs(fl[9]))
            M = max(math.hypot(fl[4], fl[5]), math.hypot(fl[10], fl[11]))
            A, I, J, c_, sm_ = octagon(d)
            sg = N_ / A + M * c_ / I; tau = Mt / sm_
            worst.append((math.sqrt(sg**2 + 3 * tau**2), m, p, q, d))
        worst.sort(reverse=True)
        uc = u[6*cn:6*cn+6]; uw = u[6*wheel:6*wheel+6]
        print('\n== %s  shock %.0f N  pivot roll reaction %.1f N.mm' % (name, shock, react[6*piv[0]+3]))
        print('   contact patch move  x %.2f  y %.2f  z %.2f mm;  wheel plane roll (camber) %.2f deg' % (uc[0], uc[1], uc[2], math.degrees(uw[4]) if abs(uw[4]) > 0 else 0.0))
        for v, m, p, q, d in worst[:5]:
            print('   %.1f MPa (%.0f %% of %.0f)  d%.1f  (%.0f,%.0f,%.0f)->(%.0f,%.0f,%.0f)' % (v, 100 * v / SIG_LIM, SIG_LIM, d, *p, *q))
        out[name] = (uc, worst[0][0])
    return out


if __name__ == '__main__':
    for v in (sys.argv[1:] or ['0']): print('\n######## variant', v); run(v, quiet=len(sys.argv) > 2)
