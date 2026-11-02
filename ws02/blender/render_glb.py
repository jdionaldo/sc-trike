import bpy, sys, math
a = sys.argv[sys.argv.index("--") + 1:]
src, outbase = a[0], a[1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=src)
imported = [o for o in bpy.context.scene.objects]
emp = bpy.data.objects.new("fix", None); bpy.context.scene.collection.objects.link(emp)
for o in imported:
    if o.parent is None:
        o.parent = emp
emp.rotation_euler = (math.radians(-90), 0, 0)
bpy.context.view_layer.update()
sc = bpy.context.scene
sc.render.engine = "CYCLES"
sc.cycles.samples = 40
sc.cycles.device = "CPU"
sc.render.resolution_x, sc.render.resolution_y = 1500, 850
# world and ground
w = bpy.data.worlds.new("w"); sc.world = w; w.use_nodes = True
w.node_tree.nodes["Background"].inputs[0].default_value = (0.82, 0.85, 0.9, 1)
w.node_tree.nodes["Background"].inputs[1].default_value = 0.7
bpy.ops.mesh.primitive_plane_add(size=3000, location=(0, 0, -41.5))
mat = bpy.data.materials.new("g"); mat.use_nodes = True
mat.node_tree.nodes["Principled BSDF"].inputs[0].default_value = (0.55, 0.55, 0.57, 1)
bpy.context.object.data.materials.append(mat)
for o in bpy.data.objects:
    if o.type == "MESH" and o.name != "Plane":
        if o.data.vertex_colors if hasattr(o.data, "vertex_colors") else False:
            pass
bpy.ops.object.light_add(type="SUN", location=(300, -300, 500)); bpy.context.object.data.energy = 2.2
bpy.context.object.rotation_euler = (math.radians(45), 0, math.radians(35))
cam_data = bpy.data.cameras.new("c"); cam_data.clip_end = 20000; cam_data.clip_start = 1; cam = bpy.data.objects.new("c", cam_data); sc.collection.objects.link(cam); sc.camera = cam
views = {"iso": ((380, 760, 430), (-170, 0, 10)), "side": ((-170, 950, 40), (-170, 0, 30)), "top": ((-170, 0, 950), (-170, 0, 0)), "front": ((800, 120, 160), (-170, 0, 30))}
import mathutils
for name, (loc, tgt) in views.items():
    cam.location = loc
    d = mathutils.Vector(tgt) - mathutils.Vector(loc)
    cam.rotation_euler = d.to_track_quat("-Z", "Y").to_euler()
    cam_data.lens = 40 if name != "top" else 45
    sc.render.filepath = f"{outbase}_{name}.png"
    bpy.ops.render.render(write_still=True)
print("rendered")
