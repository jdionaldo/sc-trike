"""WS-03 frame stiffness: 3D Euler-Bernoulli beam model of the tube graph (PETG, 6 mm solid round), rear nodes held, loads at the pivot pads and servo pads."""
import numpy as np
import parts.w3_frame as F

import os
E, NU, R = 1500.0, 0.38, float(os.environ.get("TR", F.R))                                  # MPa (printed PETG, along the tube), mm
G = E / (2 * (1 + NU)); A = np.pi * R**2; I = np.pi * R**4 / 4; J = 2 * I


def graph():
    N = F.nodes()
    nodes, edges = {}, []
    mir = lambda p: (p[0], -p[1], p[2])
    for k, p in N.items():
        nodes[k + "+"] = np.array(p, float)
        nodes[k + "-"] = np.array(mir(p), float)
    for a, b, r, ta, tb in F.EDGES:
        edges.append((a + "+", b + "+", r)); edges.append((a + "-", b + "-", r))
    return nodes, edges


def solve(loads, fixed):
    nodes, edges = graph()
    keys = []
    for k, p in nodes.items():
        if not any(np.allclose(p, nodes[q]) for q in keys):
            keys.append(k)
    idx = {k: next(i for i, q in enumerate(keys) if np.allclose(nodes[k], nodes[q])) for k in nodes}
    n = len(keys); K = np.zeros((6 * n, 6 * n))
    for a, b, rr in edges:
        A = np.pi * rr**2; I = np.pi * rr**4 / 4; J = 2 * I
        pa, pb = nodes[a], nodes[b]; L = np.linalg.norm(pb - pa); ex = (pb - pa) / L
        ref = np.array([0, 0, 1.0]) if abs(ex[2]) < 0.9 else np.array([1.0, 0, 0])
        ey = np.cross(ref, ex); ey /= np.linalg.norm(ey); ez = np.cross(ex, ey)
        T = np.zeros((12, 12))
        for i in range(4):
            T[3 * i:3 * i + 3, 3 * i:3 * i + 3] = np.vstack([ex, ey, ez])
        k = np.zeros((12, 12))
        k[0, 0] = k[6, 6] = E * A / L; k[0, 6] = k[6, 0] = -E * A / L
        k[3, 3] = k[9, 9] = G * J / L; k[3, 9] = k[9, 3] = -G * J / L
        for (v, th, s) in ((1, 5, 1), (2, 4, -1)):
            c = E * I / L**3
            for (i, j, val) in ((v, v, 12), (v, th, 6 * L * s), (v, 6 + v, -12), (v, 6 + th, 6 * L * s), (th, th, 4 * L * L), (th, 6 + v, -6 * L * s), (th, 6 + th, 2 * L * L),
                                (6 + v, 6 + v, 12), (6 + v, 6 + th, -6 * L * s), (6 + th, 6 + th, 4 * L * L)):
                k[i, j] = k[j, i] = c * val
        Kg = T.T @ k @ T
        ia, ib = idx[a], idx[b]
        dof = list(range(6 * ia, 6 * ia + 6)) + list(range(6 * ib, 6 * ib + 6))
        K[np.ix_(dof, dof)] += Kg
    f = np.zeros(6 * n)
    for name, vec in loads:
        f[6 * idx[name]:6 * idx[name] + 3] += vec
    fix = [d for name in fixed for d in range(6 * idx[name], 6 * idx[name] + 6)]
    free = [d for d in range(6 * n) if d not in fix]
    u = np.zeros(6 * n); u[free] = np.linalg.solve(K[np.ix_(free, free)], f[free])
    return nodes, edges, idx, u, K


if __name__ == "__main__":
    cases = {
        "front 3 g bump (30 N down per pivot pad)": [("PL+", (0, 0, -30.0)), ("PL-", (0, 0, -30.0))],
        "cornering 1 g (16 N sideways per pivot pad, 8 N per servo pad)": [("PL+", (0, -16.0, 0)), ("PL-", (0, -16.0, 0)), ("PM+", (0, -8.0, 0)), ("PM-", (0, -8.0, 0))],
        "front-end impact 2 g (20 N aft per pivot pad)": [("PL+", (-20.0, 0, 0)), ("PL-", (-20.0, 0, 0))],
    }
    for name, loads in cases.items():
        nodes, edges, idx, u, K = solve(loads, os.environ.get("FIX", "FP1+,FP1-,FPB+,FPB-,FPR+,FPR-,FPF+,FPF-").split(","))
        d = {k: np.linalg.norm(u[6 * idx[k]:6 * idx[k] + 3]) for k in nodes}
        k = max(d, key=d.get)
        print(f"{name}: max tip deflection {d[k]:.2f} mm at {k[:-1]}, pivot pad {d['PL+']:.2f} mm")
