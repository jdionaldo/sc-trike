import numpy as np, trimesh
from manifold3d import Manifold, Mesh
import assembly
def man(m): return Manifold(Mesh(vert_properties=np.asarray(m.vertices,np.float32),tri_verts=np.asarray(m.faces,np.uint32)))
sh=trimesh.load('out/mono/shell_watertight.stl'); sh.merge_vertices(); M=man(sh)
print('shell volume', round(M.volume()))
for pose in ('default','lean_left','lean_right','travel_up','travel_down'):
    it=assembly.scene(*assembly.POSES[pose], body=False)
    res=[]
    for i in it:
        if i.group in ('chassis',) and i.kind=='printed' and i.name.startswith('chassis'): continue
        try:
            v=(M^man(i.mesh)).volume()
        except Exception: continue
        if v>0.5: res.append((i.name,round(v,1)))
    print(pose,res)
