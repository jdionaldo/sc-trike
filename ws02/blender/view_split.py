import bpy, math, os, sys
d = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
cols = {"arms": (0.9, 0.2, 0.2, 1), "rear": (0.2, 0.4, 0.9, 1), "nose": (0.2, 0.8, 0.3, 1), "shell": (0.75, 0.75, 0.78, 1)}
for n, c in cols.items():
    bpy.ops.wm.stl_import(filepath=os.path.join(d, n + ".stl"))
    ob = bpy.context.selected_objects[0]; m = bpy.data.materials.new(n); m.diffuse_color = c; ob.data.materials.append(m)
sc = bpy.context.scene
sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "MATERIAL"
sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.93, 0.93, 0.93); sc.render.resolution_x, sc.render.resolution_y = 1400, 800
def shot(name, loc, rot, ortho=None):
    cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location, cam.rotation_euler = loc, rot; cd.clip_end = 100
    if ortho: cd.type = "ORTHO"; cd.ortho_scale = ortho
    sc.render.filepath = os.path.join(d, name + ".png"); bpy.ops.render.render(write_still=True)
shot("s_top", (0, 0, 3), (0, 0, 0), 2.1)
shot("s_iso", (1.6, 1.8, 1.2), (math.radians(60), 0, math.radians(145)))
