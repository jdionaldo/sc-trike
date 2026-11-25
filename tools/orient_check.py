"""Print orientation candidates for the printed articulating parts: for each of the six axis-aligned down faces the build height, the overhang area (faces
steeper than 45 degrees under the part, excluding the bed face) and the bed contact area. Strength rule: the pivot / pin axis stands vertical, so the bores
print round with continuous perimeters and the load plane (arm plates, links, horns) lies in the layer plane.
Run:  python tools/orient_check.py"""
import sys
sys.path.insert(0, '.')
import numpy as np
import cadquery as cq
from soma import import_assembly

PARTS = {   # name: (pin axis that should stand vertical, kit orient_face now (0 +x down, 1 -x, 2 +y, 3 -y, 4 +z, 5 -z))
    'Chassis/Suspension/arm_1': ('x', 5), 'Chassis/Suspension/arm_-1': ('x', 5),
    'Rear_swingarm/w3_rear_arm': ('x', 3),
    'Chassis/Steering/tie_rod_1': ('z', 0), 'Chassis/Suspension/uplink_1': ('z', 1), 'Chassis/Steering/steer_horn_1': ('x', 0),
    'Chassis/Steering/knuckle_1': ('z', 0), 'Chassis/Steering/carrier_1': ('z', 1),
    'Chassis/Suspension/lean_rocker_c': ('x', 3), 'Chassis/Suspension/lean_horn_c': ('x', 2), 'Chassis/Suspension/lean_mount_c': ('z', 0),
}
DIRS = {'+x': (1, 0, 0), '-x': (-1, 0, 0), '+y': (0, 1, 0), '-y': (0, -1, 0), '+z': (0, 0, 1), '-z': (0, 0, -1)}
ORDER = ['+x', '-x', '+y', '-y', '+z', '-z']


def tri(shape):
    v, t = shape.tessellate(0.05, 0.1)
    V = np.array([(p.x, p.y, p.z) for p in v]); T = np.array(t)
    return V, T


def metrics(V, T, down):
    d = np.array(DIRS[down], float)                 # this model axis points down
    h = V @ (-d)                                     # height above the bed
    p0, p1, p2 = V[T[:, 0]], V[T[:, 1]], V[T[:, 2]]
    n = np.cross(p1 - p0, p2 - p0); a = np.linalg.norm(n, axis=1) / 2; n = n / np.maximum(np.linalg.norm(n, axis=1)[:, None], 1e-12)
    hc = (h[T[:, 0]] + h[T[:, 1]] + h[T[:, 2]]) / 3
    facing_down = n @ d
    bed = a[(facing_down > 0.99) & (hc < h.min() + 0.3)].sum()
    over = a[(facing_down > 0.7071) & ~((facing_down > 0.99) & (hc < h.min() + 0.3))].sum()
    return h.max() - h.min(), over, bed


def main():
    asm = import_assembly('output/model.step')
    print('part | now | candidate (pin axis up) | height mm | overhang mm2 | bed mm2')
    for n, (axis, now) in PARTS.items():
        nd = asm.objects[n]; s = (nd.obj.val() if isinstance(nd.obj, cq.Workplane) else nd.obj).moved(nd.loc)
        V, T = tri(s)
        rows = {k: metrics(V, T, k) for k in ORDER}
        cands = [k for k in ORDER if k[1] == axis]       # pin axis vertical: +axis or -axis down
        best = min(cands, key=lambda k: rows[k][1] - 2 * rows[k][2])
        f = lambda k: '%s h%.0f ov%.0f bed%.0f' % ((k,) + tuple(rows[k]))
        print(n, '| now', f(ORDER[now]), '| strength', f(best))


main()
