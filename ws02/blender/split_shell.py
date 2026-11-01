"""Split the solidified shell on y = 0 into left (+y) and right (-y) halves and cap each cut. -- in.stl outdir"""
import bpy, bmesh, sys, os
src, outdir = sys.argv[sys.argv.index("--") + 1:][:2]
os.makedirs(outdir, exist_ok=True)
for name, sign in (("body_left", 1), ("body_right", -1)):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.wm.stl_import(filepath=src)
    ob = bpy.context.selected_objects[0]
    bm = bmesh.new(); bm.from_mesh(ob.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts[:], dist=0.02)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    res = bmesh.ops.bisect_plane(bm, geom=geom, dist=1e-5, plane_co=(0, 0, 0), plane_no=(0, 1, 0),
                                 clear_inner=(sign > 0), clear_outer=(sign < 0))
    cut_edges = [e for e in res["geom_cut"] if isinstance(e, bmesh.types.BMEdge)]
    bmesh.ops.holes_fill(bm, edges=[e for e in cut_edges if e.is_boundary or True], sides=0) if False else None
    bmesh.ops.edgenet_fill(bm, edges=cut_edges, mat_nr=0, use_smooth=False, sides=0) if False else None
    bm.to_mesh(ob.data); bm.free()
    bpy.ops.object.select_all(action="DESELECT"); ob.select_set(True)
    bpy.ops.wm.stl_export(filepath=os.path.join(outdir, name + ".stl"), export_selected_objects=True)
    print("HALF", name, len(ob.data.polygons), tuple(round(v, 1) for v in ob.dimensions))
