"""Faceted body sculpted from the traced reference views (run: Blender -b --python blender/sculpt_body.py).
Rings of vertices per station are built from the traced plan width, roof line and belly line; faces are coloured
yellow where they fall inside the yellow panels traced from the reference side render, black elsewhere."""
import json, math, os, sys
import bpy, bmesh
from mathutils import Vector

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
K = 370.0 / 250.0
X0, Z0 = -337.0, -59.2
S = 0.523
TOP = [(52, 46), (73, 64), (111, 69), (141, 69), (163, 67), (189, 56), (215, 51), (246, 41)]
BOT = [(52, 33), (87, 21), (115, 14), (163, 11.5), (195, 12), (225, 22), (242, 34), (246, 38)]
HW = [(52, 28), (76, 44), (100, 55), (143, 47), (182, 43), (188, 49), (219, 38), (235, 27), (246, 14)]
STATIONS = [52, 62, 76, 100, 120, 141, 163, 182, 189, 205, 219, 235, 246]


def interp(table, d):
    for (d0, v0), (d1, v1) in zip(table, table[1:]):
        if d0 <= d <= d1:
            return v0 + (v1 - v0) * (d - d0) / (d1 - d0)
    return table[-1][1] if d > table[-1][0] else table[0][1]


def ring(d):
    w, zt, zb = K * interp(HW, d), K * interp(TOP, d) + Z0, K * interp(BOT, d) + Z0
    h = zt - zb
    x = K * d + X0
    half = [(0.0, zt), (0.42 * w, zt - 0.02 * h), (0.82 * w, zt - 0.30 * h), (w, zb + 0.46 * h),
            (0.88 * w, zb + 0.16 * h), (0.58 * w, zb), (0.0, zb)]
    left = [(x, -y, z) for y, z in half[1:-1]]
    right = [(x, y, z) for y, z in reversed(half[1:-1])]
    return [(x, 0.0, half[0][1])] + right + [(x, 0.0, half[-1][1])] + left


def inside(poly, px, py):
    c = False
    for (x0, y0), (x1, y1) in zip(poly, poly[1:] + poly[:1]):
        if (y0 > py) != (y1 > py) and px < (x1 - x0) * (py - y0) / (y1 - y0) + x0:
            c = not c
    return c


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    polys = json.load(open(os.path.join(ROOT, "out/yellow_polys_px.json")))
    rings = [ring(d) for d in STATIONS]
    n = len(rings[0])
    verts = [v for r in rings for v in r]
    faces = []
    for i in range(len(rings) - 1):
        for j in range(n):
            a, b = i * n + j, i * n + (j + 1) % n
            faces.append((a, b, b + n, a + n))
    faces.append(tuple(reversed(range(n))))                       # tail cap
    faces.append(tuple(range((len(rings) - 1) * n, len(rings) * n)))   # nose cap
    me = bpy.data.meshes.new("body")
    me.from_pydata(verts, [], faces)
    me.update()
    bm = bmesh.new(); bm.from_mesh(me)
    for pl in polys:                       # cut the shell along every traced panel edge so the colour split is exact
        pts = [(X0 + K * (x - 21) * S, Z0 + K * (830 - y) * S) for x, y in pl]
        for (xa, za), (xb, zb) in zip(pts, pts[1:] + pts[:1]):
            dx, dz = xb - xa, zb - za
            if math.hypot(dx, dz) < 1e-6:
                continue
            geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
            bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(xa, 0.0, za), plane_no=(-dz, 0.0, dx))
    bm.to_mesh(me); bm.free()
    ob = bpy.data.objects.new("body", me)
    bpy.context.collection.objects.link(ob)
    yellow = bpy.data.materials.new("yellow"); yellow.diffuse_color = (0.95, 0.68, 0.02, 1)
    black = bpy.data.materials.new("black"); black.diffuse_color = (0.04, 0.04, 0.045, 1)
    me.materials.append(yellow); me.materials.append(black)
    for p in me.polygons:
        c = p.center
        d, h = (c.x - X0) / K, (c.z - Z0) / K
        px, py = 21 + d / S, 830 - h / S
        n = p.normal
        if abs(n.y) > 0.35:                      # flank: the traced side panels decide
            yel = any(inside(pl, px, py) for pl in polys)
        elif n.z > 0.35:                         # top: yellow hood and rear deck, black glass between
            yel = d >= 192 or d <= 98
        else:                                    # belly and undersides
            yel = False
        p.material_index = 0 if yel else 1
        p.use_smooth = False
    # context: tires (reference sizes at 370 mm)
    def tire(name, x, z, od, w, y):
        bpy.ops.mesh.primitive_cylinder_add(vertices=48, radius=od / 2, depth=w, rotation=(math.pi / 2, 0, 0), location=(x, y, z))
        t = bpy.context.active_object; t.name = name
        m = bpy.data.materials.new(name); m.diffuse_color = (0.08, 0.08, 0.08, 1); t.data.materials.append(m)
    tire("rear", -285.5, -13.2, 92, 59, 0)
    for s in (1, -1):
        tire(f"front{s}", 0.0, -59.2 + 38.5, 77, 24, s * 116)
    return ob


def render(name, loc, rot, ortho=None):
    sc = bpy.context.scene
    cam_d = bpy.data.cameras.new("cam"); cam = bpy.data.objects.new("cam", cam_d)
    sc.collection.objects.link(cam); sc.camera = cam
    cam.location, cam.rotation_euler = loc, rot
    if ortho:
        cam_d.type = "ORTHO"; cam_d.ortho_scale = ortho
    cam_d.clip_end = 5000
    sc.render.engine = "BLENDER_WORKBENCH"
    sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"
    sc.display.shading.show_object_outline = True
    sc.render.resolution_x, sc.render.resolution_y = 1500, 700
    sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.93, 0.93, 0.93)
    sc.render.filepath = os.path.join(ROOT, "out/sculpt", name + ".png")
    bpy.ops.render.render(write_still=True)
    bpy.data.objects.remove(cam)


if __name__ == "__main__":
    build()
    render("side", (-100, -900, -10), (math.pi / 2, 0, 0), ortho=480)
    render("iso", (350, -520, 260), (math.radians(68), 0, math.radians(32)))
    render("top", (-100, 0, 900), (0, 0, 0), ortho=480)
