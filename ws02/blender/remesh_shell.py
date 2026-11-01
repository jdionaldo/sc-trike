"""Make the solidified shell a clean closed manifold: voxel remesh with sharp-edge preservation. -- in.stl out.stl voxel"""
import bpy, sys
src, dst, vox = sys.argv[sys.argv.index("--") + 1:][:3]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=src)
ob = bpy.context.selected_objects[0]
bpy.context.view_layer.objects.active = ob
md = ob.modifiers.new("r", "REMESH"); md.mode = "SHARP"; md.voxel_size = float(vox); md.sharpness = 1.0; md.use_smooth_shade = False
bpy.ops.object.modifier_apply(modifier="r")
bpy.ops.wm.stl_export(filepath=dst, export_selected_objects=True)
print("POLYS", len(ob.data.polygons), tuple(round(v, 1) for v in ob.dimensions))
