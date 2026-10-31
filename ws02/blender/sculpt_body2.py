"""Body shell from the panel-kit sheet (refs/ref3_panels.webp): envelopes and yellow areas traced from its side and
top views (out/ref3_trace.json), scaled 370/410. Run: Blender -b --python blender/sculpt_body2.py"""
import json, math, os
import bpy, bmesh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(ROOT, "out/ref3_trace.json")))
SC = 370.0 / 410.0
X0, Z0 = -337.0, -59.2
RW = [(0, .55), (180, .55), (190, .30), (278, .30), (290, .62), (420, .62)]
SD = [(0, .22), (180, .22), (190, .40), (278, .40), (290, .20), (420, .18)]


def ip(tab, d):
    for (a, va), (b, vb) in zip(tab, tab[1:]):
        if a <= d <= b:
            return va + (vb - va) * (d - a) / (b - a)
    return tab[-1][1]


def env(d):
    D = T["d"]
    return (SC * float(__import__("numpy").interp(d, D, T["hw"])), SC * float(__import__("numpy").interp(d, D, T["zt"])),
            SC * float(__import__("numpy").interp(d, D, T["zb"])))


def ring(d):
    w, zt, zb = env(d)
    h = zt - zb
    x = SC * d + X0
    rw, sd = ip(RW, d), ip(SD, d)
    half = [(0.0, zt), (rw * w, zt - 0.015 * h), (0.86 * w, zt - sd * h), (w, zb + 0.44 * h),
            (0.88 * w, zb + 0.16 * h), (0.58 * w, zb), (0.0, zb)]
    z = lambda v: v + Z0
    left = [(x, -y, z(v)) for y, v in half[1:-1]]
    right = [(x, y, z(v)) for y, v in reversed(half[1:-1])]
    return [(x, 0.0, z(half[0][1]))] + right + [(x, 0.0, z(half[-1][1]))] + left


def grid(name, a, b):
    g = T[name]
    i, j = int(round(a)), int(round(b))
    return bool(g[i][j]) if 0 <= i < len(g) and 0 <= j < len(g[0]) else False


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    ds = T["d"][::2]
    rings = [ring(d) for d in ds]
    n = len(rings[0])
    verts = [v for r in rings for v in r]
    faces = [(i * n + j, i * n + (j + 1) % n, i * n + (j + 1) % n + n, i * n + j + n) for i in range(len(rings) - 1) for j in range(n)]
    faces += [tuple(reversed(range(n))), tuple(range((len(rings) - 1) * n, len(rings) * n))]
    me = bpy.data.meshes.new("body"); me.from_pydata(verts, [], faces); me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=2, use_grid_fill=True)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("body", me); bpy.context.collection.objects.link(ob)
    ym = bpy.data.materials.new("yellow"); ym.diffuse_color = (0.95, 0.68, 0.02, 1)
    km = bpy.data.materials.new("black"); km.diffuse_color = (0.04, 0.04, 0.045, 1)
    me.materials.append(ym); me.materials.append(km)
    for p in me.polygons:
        c, nrm = p.center, p.normal
        d, h, y = (c.x - X0) / SC, (c.z - Z0) / SC, c.y / SC
        if abs(nrm.y) > 0.5:
            yel = grid("side_yellow", h / 3, (d - 40) / 3)
        elif nrm.z > 0.5:
            yel = grid("top_yellow", (y + 120) / 3, (d - 40) / 3)
        else:
            yel = False
        p.material_index = 0 if yel else 1
        p.use_smooth = False
    def tire(name, x, z, od, w, y):
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=od / 2, depth=w, rotation=(math.pi / 2, 0, 0), location=(x, y, z))
        t = bpy.context.active_object; t.name = name
        m = bpy.data.materials.new(name); m.diffuse_color = (0.08, 0.08, 0.08, 1); t.data.materials.append(m)
    tire("rear", -285.5, -13.2, 92, 59, 0)
    for s in (1, -1):
        tire(f"front{s}", 0.0, -59.2 + 38.5, 77, 24, s * 116)


def render(name, loc, rot, ortho=None):
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam); sc.camera = cam; cam.location, cam.rotation_euler = loc, rot
    if ortho:
        cd.type = "ORTHO"; cd.ortho_scale = ortho
    cd.clip_end = 5000
    sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"
    sc.render.resolution_x, sc.render.resolution_y = 1500, 700
    sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.93, 0.93, 0.93)
    sc.render.filepath = os.path.join(ROOT, "out/sculpt", name + ".png")
    bpy.ops.render.render(write_still=True); bpy.data.objects.remove(cam)


if __name__ == "__main__":
    build()
    render("v2_side", (-100, -900, -10), (math.pi / 2, 0, 0), ortho=480)
    render("v2_iso", (350, -520, 260), (math.radians(68), 0, math.radians(32)))
    render("v2_top", (-100, 0, 900), (0, 0, 0), ortho=480)
