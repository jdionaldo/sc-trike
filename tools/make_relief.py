"""Writes parts/relief.json: hull vertices of chassis parts that reach into the shell, and tire cylinders.
Shell frame at 1:1, ground z=0 (same frame as chassis_ref.step)."""
import json, numpy as np
from fit_chassis import chassis
ch=chassis(1.0)
KEEP=('arm_','pod_','uplink_','knuckle_','carrier_','tie_rod_','steer_horn_','steer_servo_','diff_out_','mock_fbelt_','mock_fpulley','b_lean_shock','lean_','mock_joint','w3_uplink_standoff','b_rear_shock')
STEER=('knuckle_','carrier_','mock_hub_','mock_axle_','mock_rim','mock_joint','steer_horn_')
REARSET=lambda n:n in('w3_rear_arm',) or (n.startswith('mock_rear_') and n!='mock_rear_tire_ring')
out={'hulls':[], 'tires':[], 'pivot':None}
pv=ch['mock_rear_pulley_pivot'].bounds; out['pivot']=[round(float((pv[0][i]+pv[1][i])/2),2) for i in range(3)]
out['rear_axle']=[round(float(v),2) for v in ((ch['mock_rear_axle'].bounds[0]+ch['mock_rear_axle'].bounds[1])/2)]
for n,m in ch.items():
    if n.startswith('mock_tire') or n=='mock_rear_tire_ring':
        b=m.bounds; c=(b[0]+b[1])/2; e=b[1]-b[0]
        out['tires'].append(dict(name=n,center=[round(float(v),2) for v in c],r=round(float(max(e[1],e[2]))/2,2),hw=round(float(e[0])/2,2)))
    elif (n.startswith(KEEP) or REARSET(n)) and n!='b_rear_shock':
        h=m.convex_hull
        v=np.round(h.vertices,1).tolist()
        kind='rear' if REARSET(n) else 'steer' if n.startswith(STEER) else 'susp' if n.startswith(('arm_','uplink_','pod_','tie_rod_','diff_out_','mock_fbelt_','mock_fpulley')) else 'fixed'
        out['hulls'].append(dict(name=n,kind=kind,pts=v))
import trimesh
env=[];rail=[]
Pall=np.vstack([trimesh.sample.sample_surface(m,max(20,int(m.area/8)))[0] for n,m in ch.items() if not n.startswith('mock_tire') and n!='mock_rear_tire_ring' and max(m.extents)>3])
Pr=np.vstack([trimesh.sample.sample_surface(ch[n],80000)[0] for n in ('w3_frame_front','w3_frame_rear')])
for y in range(-240,141,10):
    a=Pall[(np.abs(Pall[:,0])<85)&(np.abs(Pall[:,1]-y)<12)]; b=Pr[(np.abs(Pr[:,0])>50)&(np.abs(Pr[:,0])<66)&(np.abs(Pr[:,1]-y)<8)]
    env.append([y,round(float(a[:,2].max()),1) if len(a) else None]); rail.append([y,round(float(b[:,2].max()),1) if len(b) else None])
out['envelope']=env; out['rail']=rail
import os; json.dump(out,open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','parts','relief.json'),'w'))
print(len(out['hulls']),sum(len(h['pts']) for h in out['hulls']),out['tires'])
