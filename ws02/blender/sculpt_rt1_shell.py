"""RT-1 body shell, printable: hollow (2.4 mm wall), recessed 0.8 mm paint areas where the sheet is dark, split on y = 0
into left and right halves. Blender -b --python blender/sculpt_rt1_shell.py  (STL out in out/rt1_body/)."""
import json, math, os
import bpy, bmesh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(ROOT, "out/rt1_trace.json")))
U, ZT, ZB, HW = T["u"], T["zt"], T["zb"], T["hw"]
XF, XR = -22.0, -230.0
TUB_TOP = [(-22.0, 18.0), (-57.0, 24.0), (-96.0, 36.0), (-112.0, 38.5), (-236.0, 38.5)]
X_LEFT_END = -182.0           # the left half stops at the swingarm plate


def _ip(tab, x):
    for (a, va), (b, vb) in zip(tab, tab[1:]):
        if b <= x <= a:
            return vb + (va - vb) * (x - b) / (a - b)
    return tab[-1][1]


def _fit():
    """Keep the RT-1 lines but never cut inside the chassis: wide enough over the tub, tall enough over its walls."""
    for i, u in enumerate(U):
        x = XF + u * (XR - XF)
        HW[i] = max(HW[i], 58.0 if x > -176.0 else 40.0)
        ZT[i] = max(ZT[i], _ip(TUB_TOP, x) + 3.5)


_fit()
WALL, RECESS = 2.4, 0.8
OUT = os.path.join(ROOT, "out/rt1_body")


def _at(arr, u):
    for k in range(len(U) - 1):
        if U[k] <= u <= U[k + 1]:
            return arr[k] + (arr[k + 1] - arr[k]) * (u - U[k]) / (U[k + 1] - U[k])
    return arr[-1]


def ring(u):
    x = XF + u * (XR - XF)
    w, zt, zb = _at(HW, u), _at(ZT, u), _at(ZB, u)
    h = zt - zb
    return [(x, 0.0, zb), (x, 0.55 * w, zb), (x, w, zb + 0.22 * h), (x, w, zb + 0.58 * h), (x, 0.62 * w, zt), (x, 0.0, zt)]


def dark_at(c):
    u = (c.x - XF) / (XR - XF)
    j = int(round(u * 119))
    if abs(c.y) > 0:
        pass
    return u, j


def sample(grid, a, a0, j):
    i = int(round((a - a0) / 2.0))
    return bool(grid[i][j]) if 0 <= i < len(grid) and 0 <= j < len(grid[0]) else False


def build_half(x_end=None, name="body_left", flip=False):
    us = list(U)
    if x_end is not None:
        u_end = (x_end - XF) / (XR - XF)
        us = [u for u in U if u < u_end] + [u_end]
    rings = [ring(u) for u in us]
    n = len(rings[0])
    verts = [v for r in rings for v in r]
    faces = [(i * n + j, i * n + j + 1, i * n + j + 1 + n, i * n + j + n) for i in range(len(rings) - 1) for j in range(n - 1)]
    faces += [tuple(reversed(range(n))), tuple(range((len(rings) - 1) * n, len(rings) * n))]
    me = bpy.data.meshes.new("half"); me.from_pydata(verts, [], faces); me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=3, use_grid_fill=True)
    dark = []
    for f in bm.faces:
        c, nrm = f.calc_center_median(), f.normal
        u = (c.x - XF) / (XR - XF); j = int(round(u * 119))
        if abs(nrm.y) > 0.5 and sample(T["side_dark"], c.z, T["z0"], j):
            dark.append(f)
        elif nrm.z > 0.4 and sample(T["top_dark"], c.y, T["y0"], j):
            dark.append(f)
    bmesh.ops.inset_region(bm, faces=dark, thickness=0.0, depth=-RECESS, use_even_offset=True, use_boundary=True)
    if flip:
        bmesh.ops.reverse_faces(bm, faces=bm.faces[:])
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new(name, me); bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    md = ob.modifiers.new("shell", "SOLIDIFY"); md.thickness = WALL; md.offset = -1.0; md.use_rim = True
    bpy.ops.object.modifier_apply(modifier="shell")
    return ob


def cut_swingarm_side(ob):
    """The one-sided swingarm plate lives outboard of the cradle on the left: open the left half behind x = -190."""
    cube = bpy.data.objects.new("cut", bpy.data.meshes.new("cut"))
    bm = bmesh.new(); bmesh.ops.create_cube(bm, size=1.0); bm.to_mesh(cube.data); bm.free()
    bpy.context.collection.objects.link(cube)
    cube.location, cube.scale = (-300.0, 120.0, 0.0), (220.0, 170.0, 200.0)
    md = ob.modifiers.new("cut", "BOOLEAN"); md.operation = "DIFFERENCE"; md.object = cube
    bpy.context.view_layer.objects.active = ob
    bpy.ops.object.modifier_apply(modifier="cut")
    bpy.data.objects.remove(cube)


def mirror_copy(ob):
    cp = ob.copy(); cp.data = ob.data.copy(); cp.name = "body_right"
    bpy.context.collection.objects.link(cp)
    cp.scale.y = -1
    bpy.context.view_layer.objects.active = cp
    bpy.ops.object.transform_apply(scale=True)
    bm = bmesh.new(); bm.from_mesh(cp.data); bmesh.ops.reverse_faces(bm, faces=bm.faces[:]); bm.to_mesh(cp.data); bm.free()
    return cp


def render(name, loc, rot, ortho=None):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam); sc.camera = cam; cam.location, cam.rotation_euler = loc, rot
    if ortho:
        cd.type = "ORTHO"; cd.ortho_scale = ortho
    cd.clip_end = 5000
    sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "SINGLE"
    sc.display.shading.single_color = (0.75, 0.75, 0.78)
    sc.render.resolution_x, sc.render.resolution_y = 1500, 700
    sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.93, 0.93, 0.93)
    sc.render.filepath = os.path.join(ROOT, "out/sculpt", name + ".png")
    bpy.ops.render.render(write_still=True); bpy.data.objects.remove(cam)


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.wm.read_factory_settings(use_empty=True)
    full = build_half(None, "tmp")
    l = mirror_copy(full)                     # right half (-y), named body_right
    bpy.data.objects.remove(full)
    r = build_half(X_LEFT_END, "body_left", flip=False)   # left half (+y), stops at the swingarm plate
    for ob in (r, l):
        bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True)
        bpy.ops.wm.stl_export(filepath=os.path.join(OUT, ob.name + ".stl"), export_selected_objects=True)
        print("DIMS", ob.name, tuple(round(v, 1) for v in ob.dimensions))
    render("shell_iso", (260, -560, 300), (math.radians(66), 0, math.radians(30)))
    render("shell_side", (-120, -900, -10), (math.pi / 2, 0, 0), ortho=480)
