"""Clean closed shell that carries the base model's facets: a parametric ring hull sized from the extracted skin is
shrinkwrapped onto it, then given a 2.4 mm wall. Blender -b --python ... -- skin.stl out.stl"""
import bpy, bmesh, sys, math
import numpy as np
from mathutils import Vector

src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=src)
skin = bpy.context.selected_objects[0]
V = np.array([skin.matrix_world @ v.co for v in skin.data.vertices])
X0, X1, STEP = -214.0, -36.0, 5.0


def env(x):
    r = 4.0
    s = V[np.abs(V[:, 0] - x) < r]
    while len(s) < 6:
        r += 4.0
        s = V[np.abs(V[:, 0] - x) < r]
    return float(np.abs(s[:, 1]).max()), float(s[:, 2].max()), float(s[:, 2].min())


rings = []
for x in np.arange(X1, X0 - 0.1, -STEP):
    w, zt, zb = env(x)
    h = zt - zb
    half = [(0.0, zt), (0.40 * w, zt), (0.80 * w, zt - 0.22 * h), (w, zt - 0.45 * h), (0.92 * w, zb + 0.15 * h), (0.55 * w, zb), (0.0, zb)]
    right = half[1:-1]
    rings.append([(x, 0.0, half[0][1])] + [(x, y, z) for y, z in right] + [(x, 0.0, half[-1][1])] + [(x, -y, z) for y, z in reversed(right)])
n = len(rings[0])
verts = [v for r in rings for v in r]
faces = [(i * n + j, i * n + (j + 1) % n, i * n + (j + 1) % n + n, i * n + j + n) for i in range(len(rings) - 1) for j in range(n)]
faces += [tuple(reversed(range(n))), tuple(range((len(rings) - 1) * n, len(rings) * n))]
me = bpy.data.meshes.new("hull"); me.from_pydata(verts, [], faces); me.update()
bm = bmesh.new(); bm.from_mesh(me)
bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=3, use_grid_fill=True)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
bm.to_mesh(me); bm.free()
hull = bpy.data.objects.new("hull", me); bpy.context.collection.objects.link(hull)
bpy.context.view_layer.objects.active = hull
for _ in range(2):
    md = hull.modifiers.new("w", "SHRINKWRAP"); md.target = skin; md.wrap_method = "NEAREST_SURFACEPOINT"; md.wrap_mode = "ON_SURFACE"
    bpy.ops.object.modifier_apply(modifier="w")
sd = hull.modifiers.new("s", "SOLIDIFY"); sd.thickness = 2.4; sd.offset = -1.0
bpy.ops.object.modifier_apply(modifier="s")
bpy.ops.object.select_all(action="DESELECT"); hull.select_set(True)
bpy.ops.wm.stl_export(filepath=dst, export_selected_objects=True)
print("POLYS", len(hull.data.polygons), tuple(round(v, 1) for v in hull.dimensions))
