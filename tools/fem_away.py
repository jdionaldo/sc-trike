"""FEM read-out away from the supports and loads: the highest von Mises stress over the result surface, only at points farther than D mm from
every fixed or loaded face (the bc meshes in the result GLB), so the singular peaks at rigid supports and loaded faces are left out.

  python tools/fem_away.py .soma/results/<study>.glb D [strength_MPa]
Prints the maximum (MPa), its position, the safety (strength / stress) and, for reference, the global maximum. Reads the GLB written by
`soma analyze fem` (part meshes carry _STRESS per vertex in MPa; meshes named bc<i> are the held and loaded faces).
"""
import json, struct, sys
import numpy as np
from scipy.spatial import cKDTree


def load(path):
    b = open(path, 'rb').read()
    n = struct.unpack('<I', b[12:16])[0]
    j = json.loads(b[20:20 + n])
    off = 20 + n
    bin0 = off + 8                                     # BIN chunk header (length, type)
    def acc(i):
        a = j['accessors'][i]; v = j['bufferViews'][a['bufferView']]
        start = bin0 + v.get('byteOffset', 0) + a.get('byteOffset', 0)
        k = {'SCALAR': 1, 'VEC3': 3}[a['type']]
        return np.frombuffer(b, dtype=np.float32, count=a['count'] * k, offset=start).reshape(-1, k) if k > 1 else \
            np.frombuffer(b, dtype=np.float32, count=a['count'], offset=start)
    parts, bcs = [], []
    for m in j['meshes']:
        for p in m['primitives']:
            at = p['attributes']
            if m.get('name', '').startswith('bc'):
                bcs.append(acc(at['POSITION']))
            elif '_STRESS' in at:
                parts.append((m.get('name'), acc(at['POSITION']), acc(at['_STRESS'])))
    return parts, bcs


def main():
    path, D = sys.argv[1], float(sys.argv[2])
    strength = float(sys.argv[3]) if len(sys.argv) > 3 else 20.0
    parts, bcs = load(path)
    tree = cKDTree(np.vstack(bcs))
    for name, P, S in parts:
        d, _ = tree.query(P)
        ok = d > D
        i = int(np.argmax(np.where(ok, S, -1)))
        g = int(np.argmax(S))
        print('%s: away from supports and loads (> %.1f mm, %d of %d points): %.2f MPa at (%.1f, %.1f, %.1f), safety %.2f; global max %.2f MPa at (%.1f, %.1f, %.1f), %.1f mm from a bc face'
              % (name, D, ok.sum(), len(P), S[i], *P[i], strength / S[i], S[g], *P[g], d[g]))


if __name__ == '__main__':
    main()
