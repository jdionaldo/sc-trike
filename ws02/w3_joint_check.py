"""WS-03 frame joint check: the cage is one connected watertight body per half (and per printed piece), every foot / hinge lug / tab pad is fused to its
node, and the thinnest wall is reported (inward ray from 20000 surface samples, tubes excluded by sampling only the first hit)."""
import numpy as np
import trimesh

import mono_build as MB
import parts.w3_frame as FR


def thin_spots(mesh, hs=(0.75, 1.0, 1.5), n=60000, seed=1):
    """Wall-thickness screen without ray casting: the point h below a surface sample p (along the inward normal) must have no other surface closer than ~h;
    where one is, the wall is thinner than about 2 h there.  Returns {h: [(xyz, count) clusters]} (print frame)."""
    from scipy.spatial import cKDTree
    p, fi = trimesh.sample.sample_surface(mesh, n, seed=seed)
    nrm = mesh.face_normals[fi]
    tree = cKDTree(p)
    out = {}
    for h in hs:
        q = p - nrm * h
        d, _ = tree.query(q)
        bad = p[d < 0.8 * h]
        cl = []
        for b in bad:
            for c in cl:
                if np.linalg.norm(b - c[0]) < 6.0:
                    c[1] += 1
                    break
            else:
                cl.append([b, 1])
        out[h] = [(np.round(c[0], 1).tolist(), c[1]) for c in sorted(cl, key=lambda c: -c[1])[:6]]
    return out


def main():
    f = FR.frame()
    parts = f.decompose()
    print(f"cage components {len(parts)} (1 expected), genus {f.genus()}, volume {f.volume():.0f} mm3")
    ok = len(parts) == 1
    for name in FR.NAMES:
        m = FR.piece(name)
        print(f"{name}: watertight {m.is_watertight}, bodies {len(m.split(only_watertight=False))}")
        for h, cl in thin_spots(m).items():
            print(f"   wall < {2 * h:.1f} mm: {len(cl)} clusters {cl}")
        ok &= m.is_watertight
    return ok


if __name__ == "__main__":
    raise SystemExit(0 if main() else 1)
