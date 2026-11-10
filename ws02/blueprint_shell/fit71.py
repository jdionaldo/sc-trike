"""Fit the blueprint shell to the WS-03 cage/chassis: cut the swing / relief channels, then measure overlap with every assembly item over the lean and steer poses.
usage (from ws02/): python blueprint_shell/fit71.py"""
import os, sys, json, time
sys.path.insert(0, os.getcwd()); sys.path.insert(0, os.path.join(os.getcwd(), 'blueprint_shell'))
import numpy as np, trimesh
import manifold3d as m3
import shell71 as B

def man(t): return B.man(t)
def tm(M): return B.tm(M)

def cut_channels(panels):
    import w3_swing as SW
    import parts.w3_frame as FR
    env = SW.rear_travel_channels()
    ch = SW.swing_channels()
    out = {}
    for k, t in panels.items():
        M = man(t) - env.translate((0.0037, 0.0029, -0.0011))
        M = M - ch.translate((0.0071, 0.0043, -0.0059))
        out[k] = tm(M)
    return out

def overlaps(panels, poses=((0, 0), (20, 0), (-20, 0), (0, 17), (0, -17), (20, 17), (-20, -17)), min_mm3=0.5):
    import w3_assembly as A
    P = {k: man(t) for k, t in panels.items()}
    rows = {}
    for lean, steer in poses:
        for n, m, kind in A.assembly(float(lean), steer=float(steer)):
            if n.startswith('body3_'): continue
            try: mm = man(m)
            except Exception: continue
            for pk, pm in P.items():
                v = (mm ^ pm).volume()
                if v > min_mm3:
                    key = f'{n}|{pk}'
                    rows[key] = max(rows.get(key, (0,))[0], round(v, 1)), lean, steer
    return rows

LEANS = (-20, -10, 0, 10, 20)
STEERS = (-17, 0, 17)


def hardware_relief(panels, margin=1.5, min_mm3=0.5):
    """for every assembly item that overlaps a panel at any pose: convex hull of the item over all poses, grown by `margin`, cut out of the panels."""
    import w3_assembly as A
    P = {k: man(t) for k, t in panels.items()}
    verts = {}
    for lean in LEANS:
        for steer in STEERS:
            for n, m, kind in A.assembly(float(lean), steer=float(steer)):
                if n.startswith('body3_'): continue
                verts.setdefault(n, []).append(np.asarray(m.vertices))
    hit = set()
    # one pass over poses to find the items that touch a panel at all
    for lean in LEANS:
        for steer in STEERS:
            for n, m, kind in A.assembly(float(lean), steer=float(steer)):
                if n.startswith('body3_'): continue
                b = m.bounds
                for pk, t in panels.items():
                    if (b[1] < t.bounds[0]).any() or (b[0] > t.bounds[1]).any(): continue
                    try:
                        if (man(m) ^ P[pk]).volume() > min_mm3: hit.add(n)
                    except Exception: pass
    cutters = {}
    for n in sorted(hit):
        V = np.unique(np.round(np.vstack(verts[n]), 2), axis=0)
        pts = np.vstack([V + d for d in ([0, 0, 0], [margin, 0, 0], [-margin, 0, 0], [0, margin, 0], [0, -margin, 0], [0, 0, margin], [0, 0, -margin])])
        cutters[n] = man(trimesh.convex.convex_hull(pts))
    allc = m3.Manifold.batch_boolean(list(cutters.values()), m3.OpType.Add)
    out = {}
    removed = {}
    for k, t in panels.items():
        M = man(t); v0 = M.volume(); M = M - allc
        out[k] = tm(M); removed[k] = round(v0 - M.volume(), 0)
    return out, sorted(hit), removed


if __name__ == '__main__':
    t0 = time.time()
    panels = B.build_all()
    pre = overlaps(panels, poses=((0, 0),))
    print('before cuts: overlaps at rest', len(pre), 'sum mm3', round(sum(v[0] for v in pre.values()), 0), 'time', round(time.time() - t0))
    fitted = cut_channels(panels)
    fitted, hit, removed = hardware_relief(fitted)
    print('relieved items', hit); print('volume removed per panel (mm3)', removed)
    post = overlaps(fitted)
    print('after cuts: overlaps over poses', len(post), 'sum mm3', round(sum(v[0] for v in post.values()), 0))
    for k, v in sorted(post.items(), key=lambda kv: -kv[1][0])[:25]: print(k, v)
    os.makedirs('out/bp71', exist_ok=True)
    for k, t in fitted.items(): t.export(f'out/bp71/{k}.stl')
    json.dump({'before': pre, 'after': post, 'relieved': hit, 'removed_mm3': removed}, open('out/bp71/fit.json', 'w'))
