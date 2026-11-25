"""Beam model of the printed front swingarm (parts/frontarm.py, +x side). Same method and assumptions as tools/arm_fea.py.
Loads at the tyre contact patch (x 144, y -216.4, z -15.6: tyre centre x 144, OD 112), wheel carrier on the 4 mm steel tip shaft,
suspension pod force down on the outer plate at the pod nodes (equilibrium about the pivot), pivot bosses held.
Run:  soma-python tools/front_arm_fea.py"""
import sys, math
sys.path.insert(0, '.')
import numpy as np
import parts.frontarm as fa
import parts.cage as cg
from tools.arm_fea import octagon, solve, E_P, G_P, E_S, G_S, SIG_LIM

LAST = []
CONTACT = (144.0, -216.4, -15.6)


def capture():
    got = {}; orig = cg._Frame.build
    def spy(self, *a, **k):
        self._split_crossings(); got['F'] = self; raise StopIteration
    cg._Frame.build = spy
    try: fa.make_front_arm()
    except StopIteration: pass
    finally: cg._Frame.build = orig
    return got['F']


def run(var=None, cases=None):
    var = var or {}
    F = capture(); nodes = []; key = {}
    def N(p):
        k = tuple(round(float(c), 1) for c in p)
        if k not in key: key[k] = len(nodes); nodes.append(k)
        return key[k]
    mem = []; meta = []
    def add(p, q, d, kind, mat='P'):
        i, j = N(p), N(q)
        if i == j: return
        E, G = (E_S, G_S) if mat == 'S' else (E_P, G_P)
        if d is None: A, I, J = 1e4, 1e8, 1e8; c = 1; sm = 1
        else: A, I, J, c, sm = octagon(d)
        mem.append((i, j, E, G, A, I, J, kind)); meta.append((p, q, d, c, sm, kind, mat))
    for a, b, d in F.segs: add(a, b, d, 'tube')
    xi, xo = fa.PLATE_X; P, T = fa.PIVOT_YZ, fa.TIP_YZ
    U0, U3, L0, L3 = (-139.0, 75.5), (-214.0, 67.6), (-139.0, 49.4), (-214.0, 45.8)
    U2 = (-194.0, 67.6)
    for x in (xi, xo):
        for q in (U0, L0): add((x, P[0], P[1]), (x, q[0], q[1]), 9.0, 'web')
        for q in (U3, L3): add((x, T[0], T[1]), (x, q[0], q[1]), 9.0, 'neck')
    xm = (xi + xo) / 2
    add((xi, T[0], T[1]), (xm, T[0], T[1]), 4.0 / 0.88, 'shaft', 'S'); add((xm, T[0], T[1]), (xo, T[0], T[1]), 4.0 / 0.88, 'shaft', 'S')
    cn = N(CONTACT); add((xm, T[0], T[1]), (xm, CONTACT[1], CONTACT[2]), None, 'rigid'); add((xm, CONTACT[1], CONTACT[2]), CONTACT, None, 'rigid')
    for k, v in var.items(): v(add, N)
    piv = [N((x, P[0], P[1])) for x in (xi, xo)]
    fixed = set()
    for nd in piv: fixed |= {6*nd, 6*nd+1, 6*nd+2}
    fixed.add(6*piv[0] + 3)
    lever_w = abs(T[0] - P[0]); lever_p = abs((U2[0] + U3[0]) / 2 - P[0])
    cases = cases or {'bump 50 N': (0, 0, 50.0), 'side 30 N': (30.0, 0, 0), 'bump 50 + side 30': (30.0, 0, 50.0)}
    print('nodes %d members %d; wheel lever %.1f, pod lever %.1f' % (len(nodes), len(mem), lever_w, lever_p))
    pods = [N((xo, U2[0], U2[1])), N((xo, U3[0], U3[1]))]
    out = {}
    for name, (fx, fy, fz) in cases.items():
        loads = {cn: np.array([fx, fy, fz, 0, 0, 0])}
        fp = fz * lever_w / lever_p
        for nd in pods: loads[nd] = np.array([0, 0, -fp / 2, 0, 0, 0])
        u, el, react = solve(mem, nodes, loads, fixed)
        LAST[:] = [nodes, u]
        worst = []
        for m, (i, j, T_, k, L, idx) in enumerate(el):
            p, q, d, c, sm, kind, mat = meta[m]
            if d is None or mat == 'S' or kind != 'tube': continue
            fl = k @ (T_ @ u[idx]); A, I, J, c_, sm_ = octagon(d)
            sg = max(abs(fl[0]), abs(fl[6])) / A + max(math.hypot(fl[4], fl[5]), math.hypot(fl[10], fl[11])) * c_ / I
            tau = max(abs(fl[3]), abs(fl[9])) / sm_
            worst.append((math.sqrt(sg**2 + 3 * tau**2), p, q, d))
        worst.sort(reverse=True); uc = u[6*cn:6*cn+6]
        print('\n== %s  pod force %.0f N  roll reaction %.1f N.mm' % (name, fp, react[6*piv[0]+3]))
        print('   contact patch move  x %.2f  y %.2f  z %.2f mm;  carrier roll %.2f deg' % (uc[0], uc[1], uc[2], math.degrees(u[6*N((xm, T[0], T[1]))+4])))
        for v, p, q, d in worst[:5]:
            print('   %.1f MPa (%.0f %% of %.0f)  d%.1f  (%.0f,%.0f,%.0f)->(%.0f,%.0f,%.0f)' % (v, 100 * v / SIG_LIM, SIG_LIM, d, *p, *q))
        out[name] = (uc, worst[0][0])
    return out


if __name__ == '__main__':
    run()
