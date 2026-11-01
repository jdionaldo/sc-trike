import bpy, sys
a = sys.argv[sys.argv.index("--") + 1:]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=a[0])
o = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = o
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.normals_make_consistent(inside=False)
bpy.ops.object.mode_set(mode="OBJECT")
m = o.modifiers.new("s", "SOLIDIFY")
m.thickness = float(a[2]); m.offset = -1.0; m.use_rim = True
try:
    m.nonmanifold_thickness_mode = "EVEN"
except Exception as e:
    print("mode", e)
bpy.ops.object.modifier_apply(modifier="s")
bpy.ops.wm.stl_export(filepath=a[1])
print("done", len(o.data.polygons))
