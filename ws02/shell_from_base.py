"""Exterior skin of base/base.stl: keep only faces that see the outside, drop the arms, wheels and swingarm by region, scale
to 370 mm and move into the chassis frame (x forward, y left, z up, front axle at x = 0, ground at z = GROUND_Z)."""
import numpy as np
import trimesh

S = 370.0 / 1.9                      # mm per model unit
FRONT_AXLE_Y = -0.731                # model y of the front axle
GROUND_Z = -62.3                     # chassis z of the ground (front axle at -20.7)


def to_chassis(v):
    v = np.asarray(v, float)
    return np.stack([(FRONT_AXLE_Y - v[:, 1]) * S, v[:, 0] * S, v[:, 2] * S + GROUND_Z], axis=1)


def exterior_faces(mesh, n_dirs=40, seed=1):
    rng = np.random.default_rng(seed)
    c, n = mesh.triangles_center, mesh.face_normals
    out = np.zeros(len(c), bool)
    far = mesh.bounds.max() * 4
    for _ in range(n_dirs):
        d = rng.normal(size=(len(c), 3)); d /= np.linalg.norm(d, axis=1, keepdims=True)
        d = np.where(((d * n).sum(1) < 0)[:, None], -d, d)            # hemisphere of the outward normal
        d = d * 0.6 + n * 0.4; d /= np.linalg.norm(d, axis=1, keepdims=True)
        hit = mesh.ray.intersects_any(c + d * 1e-4, d)
        out |= ~hit
    return out


def _clip(mesh, xmin, xmax, ymax):
    """The part of mesh inside xmin <= x <= xmax and |y| <= ymax (planes cut the triangles cleanly)."""
    for n, o in (((1, 0, 0), (xmin, 0, 0)), ((-1, 0, 0), (xmax, 0, 0)), ((0, 1, 0), (0, -ymax, 0)), ((0, -1, 0), (0, ymax, 0))):
        if len(mesh.faces) == 0:
            break
        mesh = trimesh.intersections.slice_mesh_plane(mesh, np.array(n, float), np.array(o, float), cap=False)
    return mesh


def load_shell():
    m = trimesh.load("base/base.stl")
    main = max(m.split(only_watertight=False), key=lambda p: len(p.faces))
    ext = exterior_faces(main)
    c = main.triangles_center
    keep = ext & (np.abs(c[:, 0]) < 0.30)
    sub = main.submesh([np.where(keep)[0]], append=True)
    sub.vertices = to_chassis(sub.vertices)
    parts = [_clip(sub, -26.0, -4.0, 22.0),        # nose roof between the front shocks
             _clip(sub, -195.0, -26.0, 80.0),       # the tub
             _clip(sub, -216.0, -195.0, 34.0)]      # the tail, inboard of the swingarm plate
    shell = trimesh.util.concatenate([p for p in parts if len(p.faces)])
    comps = shell.split(only_watertight=False)
    shell = trimesh.util.concatenate([p for p in comps if p.area > 0.004 * shell.area])
    return shell


if __name__ == "__main__":
    s = load_shell()
    print(len(s.faces), np.round(s.bounds, 1).tolist())
    s.export("out/base_split/ext_shell.stl")
