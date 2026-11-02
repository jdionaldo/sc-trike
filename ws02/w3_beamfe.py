"""Small 3D beam FE (round tubes, PETG) used for the strength checks: build a graph, fix nodes, apply nodal forces, read member stresses."""
import numpy as np

E, NU = 1500.0, 0.38                                         # MPa, printed PETG along the tube
G = E / (2 * (1 + NU))


class Truss:
    def __init__(self):
        self.nodes, self.edges = {}, []

    def node(self, name, p):
        self.nodes[name] = np.array(p, float)

    def edge(self, a, b, r):
        self.edges.append((a, b, r))

    def solve(self, loads, fixed):
        keys = list(self.nodes)
        idx = {k: i for i, k in enumerate(keys)}
        n = len(keys)
        K = np.zeros((6 * n, 6 * n))
        elem = []
        for a, b, r in self.edges:
            A = np.pi * r**2; I = np.pi * r**4 / 4; J = 2 * I
            pa, pb = self.nodes[a], self.nodes[b]; L = np.linalg.norm(pb - pa); ex = (pb - pa) / L
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
            dof = list(range(6 * idx[a], 6 * idx[a] + 6)) + list(range(6 * idx[b], 6 * idx[b] + 6))
            K[np.ix_(dof, dof)] += T.T @ k @ T
            elem.append((a, b, r, A, I, J, k, T, dof))
        f = np.zeros(6 * n)
        for name, vec in loads:
            f[6 * idx[name]:6 * idx[name] + len(vec)] += vec
        fix = [d for name in fixed for d in range(6 * idx[name], 6 * idx[name] + 6)]
        free = [d for d in range(6 * n) if d not in set(fix)]
        u = np.zeros(6 * n); u[free] = np.linalg.solve(K[np.ix_(free, free)], f[free])
        worst, wname = 0.0, ""
        for a, b, r, A, I, J, k, T, dof in elem:
            fl = k @ (T @ u[dof])                              # local end forces
            for end in (0, 1):
                F = fl[6 * end:6 * end + 6]
                sig = abs(F[0]) / A + np.hypot(F[4], F[5]) * r / I
                tau = abs(F[3]) * r / J
                vm = np.sqrt(sig**2 + 3 * tau**2)
                if vm > worst:
                    worst, wname = vm, f"{a}-{b}"
        defl = max(np.linalg.norm(u[6 * idx[k_]:6 * idx[k_] + 3]) for k_ in keys)
        return worst, wname, defl
