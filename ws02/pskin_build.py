"""Panel skin build entry. usage: python pskin_build.py [layer]"""
import sys
import numpy as np
import pskin_core as C
import pskin_trace as T


def model(layers="AB"):
    m = C.Model()
    T.layer_a(m)
    if 'B' in layers:
        T.layer_b(m)
    import os
    if os.environ.get('WS03_SCAN') == '1':
        import pskin_scanfit as SF
        print('scan tie-break:', SF.apply_scan(m, float(os.environ.get('WS03_SCANW', '1.5')), float(os.environ.get('WS03_SCANB', '1.0'))))
    m.tjunctions()
    m.solve(verbose=True)
    import os
    if os.environ.get('WS03_WARP') == '1':
        import pskin_warp as W
        m.warp_positions(W.make())
    return m


if __name__ == "__main__":
    m = model()
    P, panels = m.mirror()
    print("T-junctions:", m.tj)
    print("worst planarity:", [(round(a, 3), n) for a, n in m.planarity()[:6]])
    from tools_skin import pskin_overlay as O
    O.draw(P, panels, "plan", "out/pskin/A_plan_overlay.png")


def moved(m, top=8):
    out = []
    for n, t in m.tg.items():
        p = m.pos[n]
        d = [abs(p[i] - t[i]) if t[i] is not None else 0.0 for i in range(3)]
        out.append((round(max(d), 1), n, [round(float(v), 1) for v in d]))
    return sorted(out, reverse=True)[:top]
