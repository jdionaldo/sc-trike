"""Tube-size optimiser for the printed arms: minimise tyre-patch deflection under bump + side load at the current tube volume,
keeping every tube at or below 80 % of the working stress and every diameter inside its clearance cap.
Run:  soma-python tools/arm_opt.py rear|front"""
import sys, io, math, contextlib
sys.path.insert(0, '.')
import numpy as np
from scipy.optimize import differential_evolution
from tools.arm_fea import octagon


def volume(F): return sum(octagon(d)[0] * math.dist(a, b) for a, b, d in F.segs)


def make_eval(mod, fea, names, case):
    def ev(x):
        for n, v in zip(names, x): setattr(mod, n, float(v))
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            out = fea.run('0', quiet=True) if fea.__name__ == 'tools.arm_fea' else fea.run(cases={case: CASES[case]})
        uc, s = out[case]
        return uc, s, volume(fea.capture())
    return ev


CASES = {'bump 50 + side 30': (30.0, 0, 50.0)}


def optimise(mod, fea, groups, case='bump 50 + side 30', stress_cap=0.80):
    names = list(groups); lo_hi = [groups[n] for n in names]
    ev = make_eval(mod, fea, names, case)
    x0 = [getattr(mod, n) for n in names]
    uc0, s0, v0 = ev(x0)
    print('current', dict(zip(names, x0)), 'deflection x %.2f z %.2f mm, stress %.1f MPa (%.0f %%), tube volume %.0f mm3' % (uc0[0], uc0[2], s0, 100 * s0 / 18, v0), flush=True)
    def cost(x):
        uc, s, v = ev(x)
        defl = math.hypot(uc[0], uc[2])
        return defl + 40.0 * max(0.0, v / v0 - 1.0) + 40.0 * max(0.0, s / 18.0 - stress_cap)
    r = differential_evolution(cost, lo_hi, seed=1, maxiter=18, popsize=9, tol=1e-3, polish=False, x0=np.array(x0))
    x = [round(float(v) * 2) / 2 for v in r.x]            # round to the nearest 0.5 mm (printable, orderable steps)
    uc, s, v = ev(x)
    print('best   ', dict(zip(names, x)), 'deflection x %.2f z %.2f mm, stress %.1f MPa (%.0f %%), tube volume %.0f mm3 (%+.0f %%)' % (uc[0], uc[2], s, 100 * s / 18, v, 100 * (v / v0 - 1)))
    for n, v_ in zip(names, x0): setattr(mod, n, v_)
    return x


if __name__ == '__main__':
    which = sys.argv[1]
    if which == 'rear':
        import parts.swingarm as sw, tools.arm_fea as fea
        optimise(sw, fea, {'CHORD_D': (8, 13), 'STRUT_D': (6, 11), 'ARCH_D': (8, 14)})
    else:
        import parts.frontarm as fa, tools.front_arm_fea as fea
        optimise(fa, fea, {'CHORD_D': (6, 9), 'STRUT_D': (5, 8), 'ROOT_TIE_D': (6, 9.5), 'ROOT_TIE_D_LOW': (6, 8.6), 'DIAG_D': (4, 6)})
