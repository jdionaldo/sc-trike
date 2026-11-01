"""Clean the extracted skin and give it a 2.4 mm wall (solidify inward). Blender -b --python ... -- in.stl out.stl"""
import bpy, bmesh, sys
src, dst = sys.argv[sys.argv.index("--") + 1:][:2]
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.wm.stl_import(filepath=src)
ob = bpy.context.selected_objects[0]
bm = bmesh.new(); bm.from_mesh(ob.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.05)
bmesh.ops.dissolve_degenerate(bm, edges=bm.edges[:], dist=0.02)
loose = [f for f in bm.faces if f.calc_area() < 0.02]
bmesh.ops.delete(bm, geom=loose, context="FACES")
bm.to_mesh(ob.data); bm.free()
bpy.context.view_layer.objects.active = ob
md = ob.modifiers.new("s", "SOLIDIFY"); md.thickness = 2.4; md.offset = -1.0; md.use_rim = True; md.use_even_offset = False; md.nonmanifold_thickness_mode = "FIXED"; md.nonmanifold_boundary_mode = "FLAT"
bpy.ops.object.modifier_apply(modifier="s")
bpy.ops.wm.stl_export(filepath=dst, export_selected_objects=True)
print("FACES", len(ob.data.polygons), "DIMS", tuple(round(v, 1) for v in ob.dimensions))
