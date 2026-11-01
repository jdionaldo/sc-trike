"""RT-1 body shell, printable: hollow (2.4 mm wall), recessed 0.8 mm paint areas where the sheet is dark, split on y = 0
into left and right halves. Blender -b --python blender/sculpt_rt1_shell.py  (STL out in out/rt1_body/)."""
import json, math, os
import bpy, bmesh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(ROOT, "out/rt1_trace.json")))
U, ZT, ZB, HW = T["u"], T["zt"], T["zb"], T["hw"]
XF, XR = T["x_front"], T["x_rear"]
WALL, RECESS = 2.4, 0.8
OUT = os.path.join(ROOT, "out/rt1_body")


def ring(i):
    x = XF + U[i] * (XR - XF)
    w, zt, zb = HW[i], ZT[i], ZB[i]
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


def build_half():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rings = [ring(i) for i in range(len(U))]
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
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("body_right", me); bpy.context.collection.objects.link(ob)
    bpy.context.view_layer.objects.active = ob
    md = ob.modifiers.new("shell", "SOLIDIFY"); md.thickness = WALL; md.offset = -1.0; md.use_rim = True
    bpy.ops.object.modifier_apply(modifier="shell")
    return ob


def mirror_copy(ob):
    cp = ob.copy(); cp.data = ob.data.copy(); cp.name = "body_left"
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
    r = build_half(); l = mirror_copy(r)
    for ob in (r, l):
        bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True)
        bpy.ops.wm.stl_export(filepath=os.path.join(OUT, ob.name + ".stl"), export_selected_objects=True)
        print("DIMS", ob.name, tuple(round(v, 1) for v in ob.dimensions))
    render("shell_iso", (260, -560, 300), (math.radians(66), 0, math.radians(30)))
    render("shell_side", (-120, -900, -10), (math.pi / 2, 0, 0), ortho=480)
