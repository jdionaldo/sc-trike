import bpy, math, os, sys
src, outdir = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=src)
ob = bpy.context.selected_objects[0]
sc = bpy.context.scene
d = max(ob.dimensions)
c = ob.location + sum((ob.matrix_world @ __import__("mathutils").Vector(v) for v in ob.bound_box), __import__("mathutils").Vector()) / 8 - ob.location
sc.render.engine = "BLENDER_WORKBENCH"; sc.display.shading.light = "STUDIO"; sc.display.shading.color_type = "SINGLE"
sc.display.shading.single_color = (0.75, 0.75, 0.78); sc.display.shading.show_object_outline = True
sc.world = bpy.data.worlds.new("w"); sc.world.color = (0.93, 0.93, 0.93)
sc.render.resolution_x, sc.render.resolution_y = 1200, 800
def shot(name, off, rot, ortho=None):
    cd = bpy.data.cameras.new("c"); cam = bpy.data.objects.new("c", cd); sc.collection.objects.link(cam); sc.camera = cam
    cam.location = (c.x + off[0] * d, c.y + off[1] * d, c.z + off[2] * d); cam.rotation_euler = rot; cd.clip_end = 100 * d
    if ortho: cd.type = "ORTHO"; cd.ortho_scale = ortho * d
    sc.render.filepath = os.path.join(outdir, name + ".png"); bpy.ops.render.render(write_still=True)
shot("iso", (1.4, -1.6, 1.1), (math.radians(60), 0, math.radians(37)))
shot("top", (0, 0, 3), (0, 0, 0), 1.25)
shot("side", (3, 0, 0), (math.pi / 2, 0, math.pi / 2), 1.25)
shot("front", (0, -3, 0), (math.pi / 2, 0, 0), 1.25)
print("DIMS", tuple(round(v, 3) for v in ob.dimensions))
