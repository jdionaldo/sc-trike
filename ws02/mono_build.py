"""Marry the chassis into the body: the watertight shell halves are fused with the tub and cradle halves into two printable
monocoque halves (left +y, right -y). Output: out/mono/mono_left.stl, mono_right.stl"""
import numpy as np
import trimesh
from manifold3d import Manifold, Mesh

import assembly
import mono_shell


def man(m):
    return Manifold(Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32)))


def to_trimesh(m):
    mm = m.to_mesh()
    return trimesh.Trimesh(np.asarray(mm.vert_properties)[:, :3], np.asarray(mm.tri_verts))


def cleanup(m, min_frac=0.02):
    """Drop faces on non-manifold edges, fill the holes, keep only the solid islands that matter."""
    m.merge_vertices()
    for _ in range(4):
        e = m.edges_sorted
        _, inv, c = np.unique(e, axis=0, return_inverse=True, return_counts=True)
        bad = np.where(c > 2)[0]
        if len(bad) == 0:
            break
        keep = np.ones(len(m.faces), bool)
        keep[np.unique(np.repeat(np.arange(len(m.faces)), 3)[np.isin(inv, bad)])] = False
        m = trimesh.Trimesh(m.vertices, m.faces[keep], process=False)
        m.remove_unreferenced_vertices()
        trimesh.repair.fill_holes(m)
    comps = sorted(m.split(only_watertight=False), key=lambda c: -abs(c.volume))
    m = trimesh.util.concatenate([c for c in comps if abs(c.volume) > min_frac * abs(comps[0].volume)])
    m.merge_vertices()
    trimesh.repair.fill_holes(m)
    trimesh.repair.fix_normals(m)
    return m


def prism_xy(pts, z0, z1):
    return man(trimesh.creation.extrude_polygon(__import__("shapely.geometry", fromlist=["Polygon"]).Polygon(pts), z1 - z0).apply_translation((0, 0, z0)))


def prism_xz(pts, y0, y1):
    """Polygon in (x, z) extruded along y from y0 to y1 (proper rotation: print z -> -y)."""
    m = trimesh.creation.extrude_polygon(__import__("shapely.geometry", fromlist=["Polygon"]).Polygon(pts), y1 - y0)
    m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))     # (x, y, z) -> (x, -z, y)
    m.apply_translation((0, y1, 0))
    return man(m)


def tail_cover():
    """Faceted hood over the cradle: a plan taper intersected with a sloping roof, hollowed to a 2.4 mm wall, open below and
    at the front, with a round window for the motor flange and the swingarm plate on the left."""
    plan = [(-195.0, -37.0), (-215.0, -38.0), (-234.0, -35.0), (-234.0, 35.0), (-215.0, 35.8), (-195.0, 35.8)]
    side = [(-195.0, -47.0), (-195.0, 43.0), (-218.0, 41.0), (-234.0, 30.0), (-234.0, -47.0)]
    hull = prism_xy(plan, -60.0, 60.0) ^ prism_xz(side, -60.0, 60.0)
    inner_plan = [(-194.0, -34.6), (-215.0, -35.6), (-231.6, -32.6), (-231.6, 33.2), (-215.0, 33.4), (-194.0, 33.4)]
    inner_side = [(-194.0, -60.0), (-194.0, 40.6), (-218.0, 38.6), (-231.6, 28.0), (-231.6, -60.0)]
    cavity = prism_xy(inner_plan, -70.0, 70.0) ^ prism_xz(inner_side, -70.0, 70.0)
    cover = hull - cavity
    mx, mz = assembly.P.pivot_xz
    window = man(trimesh.creation.cylinder(radius=17.0, height=14.0, sections=48).apply_transform(
        trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])).apply_translation((mx, 36.0, mz)))
    return cover - window


def clipped_skin():
    skin = trimesh.load("out/base_split/ext_final.stl")
    for n, o in (((1, 0, 0), (-195.0, 0, 0)), ((-1, 0, 0), (-40.0, 0, 0))):
        skin = trimesh.intersections.slice_mesh_plane(skin, np.array(n, float), np.array(o, float), cap=False)
    c = skin.triangles_center
    inside = (np.abs(c[:, 1]) < 36.0) & (c[:, 2] < 31.0) & (c[:, 0] < -45.0)      # the base's seat and frame seen through the canopy
    skin = trimesh.Trimesh(skin.vertices, skin.faces[~inside], process=False)
    skin.export("out/mono/skin_clipped.stl")
    return skin


def main():
    clipped_skin()
    shell = mono_shell.build("out/mono/skin_clipped.stl", "out/mono/shell_watertight.stl")
    comps = sorted(shell.split(only_watertight=False), key=lambda c: -c.volume)
    shell = trimesh.util.concatenate([c for c in comps if c.volume > 0.05 * comps[0].volume])
    S = man(shell) + tail_cover()
    # roof hatch over the battery, ESC and receiver bay: a snug lid cut from the same shell (0.25 mm gap all round)
    hx0, hx1, hy, hz = -152.0, -72.0, 34.0, 12.0
    hatch = lambda g: Manifold.cube((hx1 - hx0 + 2 * g, 2 * (hy + g), 200.0), center=False).translate((hx0 - g, -(hy + g), hz - g))
    lid = S ^ hatch(-0.25)
    S = S - hatch(0.25)
    lm = cleanup(to_trimesh(lid))
    lm.export("out/mono/canopy_lid.stl")
    pl = lm.copy(); pl.apply_translation((0, 0, -lm.bounds[0][2])); pl.export("out/stl/canopy_lid.stl")
    print("canopy_lid", len(lm.faces), lm.is_watertight, round(lm.volume), np.round(lm.extents, 1).tolist())
    items = {f"chassis_{k}_{s}": assembly.place(f"chassis_{k}_{s}", assembly.print_to_local(f"chassis_{k}_{s}"))
             for k in ("tub", "cradle") for s in ("left", "right")}
    big = 1000.0
    for side, name in ((1, "mono_left"), (-1, "mono_right")):
        box = Manifold.cube((2 * big, big, 2 * big), center=True).translate((0, side * big / 2 - side * 0.013, 0))
        half = S ^ box                          # manifold3d: ^ is intersection, + union, - difference
        if side > 0:                            # notch for the one-sided swingarm plate outboard of the cradle
            half = half - Manifold.cube((30.0, 60.0, 200.0), center=True).translate((-183.0, 35.5 + 30.0, 0.0))
        parts = [half] + [man(items[f"chassis_{k}_{'left' if side > 0 else 'right'}"]) for k in ("tub", "cradle")]
        u = parts[0]
        for p in parts[1:]:
            u = u + p
        m = cleanup(to_trimesh(u))
        m.export(f"out/mono/{name}.stl")
        pm = m.copy(); pm.apply_translation((0, 0, -m.bounds[0][2]))                  # print frame: lowest point on the bed
        pm.export(f"out/stl/{name}.stl")
        print(name, len(m.faces), m.is_watertight, round(m.volume), np.round(m.extents, 1).tolist())


if __name__ == "__main__":
    main()
