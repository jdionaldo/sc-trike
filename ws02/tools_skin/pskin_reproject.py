"""Foreshortening + reprojection check. For every panel: true area vs plan-projected area (n_z) and side-projected area (n_y);
for steep panels (|n_z| < 0.7) the traced-vs-built distance of each vertex in the plan (x,y) and side (x,z) views. usage: python tools_skin/pskin_reproject.py"""
import numpy as np
import pskin_build as B, pskin_core as C
def run(verbose=True):
    m = B.model(); P, pn = m.mirror(); C.orient_panels(P, pn)
    rows = []
    for p in m.panels:
        Q = np.array([P[i] for i in p["ids"]]); n = C.newell(Q); A = np.linalg.norm(n) / 2; n = n / np.linalg.norm(n)
        ep = max(np.hypot(*(m.pos[i][:2] - np.array([m.tg[i][0], m.tg[i][1]]))) for i in p["ids"] if m.tg[i][0] is not None and m.tg[i][1] is not None)
        es = max(np.hypot(m.pos[i][0] - m.tg[i][0], m.pos[i][2] - m.tg[i][2]) for i in p["ids"] if m.tg[i][2] is not None)
        rows.append((p["name"], A, abs(n[2]), abs(n[1]), ep, es))
    steep = [r for r in rows if r[2] < 0.7]
    if verbose:
        print("steep panels (|nz|<0.7):", len(steep), "of", len(rows), " true area", round(sum(r[1] for r in steep)), "mm2, plan-projected", round(sum(r[1]*r[2] for r in steep)), "mm2")
        print("worst plan error %.1f mm, worst side error %.1f mm (steep panels); all panels: plan %.1f side %.1f" % (max(r[4] for r in steep), max(r[5] for r in steep), max(r[4] for r in rows), max(r[5] for r in rows)))
        for r in sorted(steep, key=lambda r: -max(r[4], r[5]))[:8]: print("  %-5s area %6.0f nz %.2f plan err %.1f side err %.1f" % (r[0], r[1], r[2], r[4], r[5]))
    return rows
if __name__ == "__main__": run()
