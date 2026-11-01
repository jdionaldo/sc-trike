"""RT-1 unibody shell: a faceted hull whose plan, roof and belly lines are traced from refs/ref4_rt1_hammerhead.webp
(out/rt1_trace.json), grey with dark glass and inset panels sampled from the sheet's dark areas. Blender -b --python."""
import json, math, os
import bpy, bmesh

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
T = json.load(open(os.path.join(ROOT, "out/rt1_trace.json")))
U, ZT, ZB, HW = T["u"], T["zt"], T["zb"], T["hw"]
XF, XR = T["x_front"], T["x_rear"]


def ring(i):
    x = XF + U[i] * (XR - XF)
    w, zt, zb = HW[i], ZT[i], ZB[i]
    h = zt - zb
    half = [(0.55 * w, zb), (w, zb + 0.22 * h), (w, zb + 0.58 * h), (0.62 * w, zt)]
    return [(x, y, z) for y, z in reversed(half)] + [(x, -y, z) for y, z in half]


def sample(grid, a, b, a0, da, nb):
    i, j = int(round((a - a0) / da)), int(round(b * (nb - 1)))
    return bool(grid[i][j]) if 0 <= i < len(grid) and 0 <= j < len(grid[0]) else False


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    rings = [ring(i) for i in range(len(U))]
    n = len(rings[0])
    verts = [v for r in rings for v in r]
    faces = [(i * n + j, i * n + (j + 1) % n, i * n + (j + 1) % n + n, i * n + j + n)
             for i in range(len(rings) - 1) for j in range(n) if j != n - 1 or True]
    # open polyline ring: close only the roof (top) and belly by joining first/last vertices
    faces = [(i * n + j, i * n + (j + 1) % n, i * n + (j + 1) % n + n, i * n + j + n) for i in range(len(rings) - 1) for j in range(n)]
    faces += [tuple(reversed(range(n))), tuple(range((len(rings) - 1) * n, len(rings) * n))]
    me = bpy.data.meshes.new("body"); me.from_pydata(verts, [], faces); me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=3, use_grid_fill=True)
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("body", me); bpy.context.collection.objects.link(ob)
    gm = bpy.data.materials.new("grey"); gm.diffuse_color = (0.72, 0.72, 0.74, 1)
    dm = bpy.data.materials.new("dark"); dm.diffuse_color = (0.12, 0.12, 0.13, 1)
    me.materials.append(gm); me.materials.append(dm)
    for p in me.polygons:
        c, nrm = p.center, p.normal
        u = (c.x - XF) / (XR - XF)
        dark = False
        if abs(nrm.y) > 0.5:
            dark = sample(T["side_dark"], c.z, u, T["z0"], 2.0, 120)
        elif nrm.z > 0.4:
            dark = sample(T["top_dark"], c.y, u, T["y0"], 2.0, 120)
        p.material_index = 1 if dark else 0
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
    render("rt1_side", (-120, -900, -10), (math.pi / 2, 0, 0), ortho=480)
    render("rt1_iso", (260, -560, 300), (math.radians(66), 0, math.radians(30)))
    render("rt1_top", (-120, 0, 900), (0, 0, 0), ortho=480)
