import numpy as np, trimesh, cadquery as cq
from fit_chassis import chassis
ch=chassis(1.0)
# flat upward faces of frame plates (shell frame, ground z=0)
rows=[]
for n in ('w3_frame_front','w3_frame_rear','w3_deck_front','w3_deck_rear','w3_deck_tail','w3_motor_plate','w3_cdc_upper','b_battery'):
    m=ch[n]; nz=m.face_normals[:,2]; sel=nz>0.97
    if not sel.any(): continue
    a=m.area_faces[sel]; c=m.triangles_center[sel]
    print(n,'up-area',round(a.sum()),'z range',np.round([c[:,2].min(),c[:,2].max()],1),'x',np.round([c[:,0].min(),c[:,0].max()],0),'y',np.round([c[:,1].min(),c[:,1].max()],0))
