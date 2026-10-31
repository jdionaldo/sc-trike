import bpy, math, os, sys
src = sys.argv[sys.argv.index("--") + 1]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.obj_import(filepath=src)
ob = bpy.context.selected_objects[0]
sc = bpy.context.scene
print("DIMS", tuple(round(v, 3) for v in ob.dimensions))
sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "VERTEX"
sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.93, 0.93, 0.93)
sc.render.resolution_x, sc.render.resolution_y = 1200, 800
def shot(name, loc, rot):
    cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location, cam.rotation_euler = loc, rot; cd.clip_end = 100
    sc.render.filepath = f"/private/tmp/claude-501/triposr/{name}.png"; bpy.ops.render.render(write_still=True)
shot("m_iso", (1.6, -1.6, 1.0), (math.radians(65), 0, math.radians(45)))
shot("m_side", (0, -2.4, 0), (math.pi / 2, 0, 0))
shot("m_top", (0, 0, 2.6), (0, 0, 0))
