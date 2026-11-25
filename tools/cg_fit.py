import numpy as np, trimesh
from scipy.spatial import cKDTree
from fit_chassis import chassis
S=2.17
ch=chassis(1.0)   # shell frame: x lateral, y=-forward, z up, ground z=0
# --- chassis mass model (g): assumed typical hobby masses / printed density, rough
def mass(n,m):
    e=m.extents
    if n=='b_battery': return 190
    if n=='b_motor': return 150
    if 'servo' in n: return 55
    if n.startswith('mock_tire'): return 90
    if n.startswith('mock_rim') or n.startswith('mock_hub'): return 20
    if n.startswith('mock_') or n.startswith('b_'): return 0.0006*m.convex_hull.volume*7.8*0.2 if max(e)>8 else 0.3
    v=m.volume if m.is_watertight else m.convex_hull.volume*0.4
    return abs(v)/1000*1.24*0.35   # printed parts, ~35% effective fill
tot=0;cg=np.zeros(3); masses={}
for n,m in ch.items():
    g=mass(n,m); masses[n]=g; c=m.centroid if m.is_watertight else m.bounds.mean(0); tot+=g; cg+=g*c
print('chassis mass ~%d g'%tot,'CG (lat,y,z above ground)',np.round(cg/tot,1))
for n,g in sorted(masses.items(),key=lambda t:-t[1])[:8]: print(' ',n,round(g))
chm=tot; chcg=cg/tot
# --- shell
vols=dict(front=485372,rear=110313,canopy=233633,grille=16639)  # mm3 from model.step (order guess) -- recompute below
import cadquery as cq
r=cq.importers.importStep("../output/model.step")
sol=[s for s in r.val().Solids() if s.Volume()>80000 and s.BoundingBox().xlen>150]
tv=0;sc=np.zeros(3)
for s in sol[:3]:
    c=s.Center(); v=s.Volume(); tv+=v; sc+=v*np.array([c.x,c.y,c.z]); print('shell solid',round(v/1000),'cm3',np.round([c.x,c.y,c.z]))
sm=tv/1000*1.24; scg=sc/tv
print('shell mass ~%d g'%sm,'CG',np.round(scg,1))
np.save('/tmp/cgs.npy',np.array([chm,*chcg,sm,*scg]))
