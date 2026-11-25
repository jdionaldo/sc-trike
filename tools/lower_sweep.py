import numpy as np, trimesh, cadquery as cq
from scipy.spatial import cKDTree
from fit_chassis import chassis
r=cq.importers.importStep("../output/model.step")
pts=[]
for s in r.val().Solids():
    b=s.BoundingBox()
    if s.Volume()>80000 and b.xlen>150 and b.zmin>-5:
        v,f=s.tessellate(1.0); m=trimesh.Trimesh([x.toTuple() for x in v],f)
        pts.append(trimesh.sample.sample_surface(m,int(m.area/4))[0])
S=np.vstack(pts); print('shell pts',len(S),S.min(0).round(),S.max(0).round()); np.save('/tmp/shellpts.npy',S)
tree=cKDTree(S)
ch=chassis(1.0)
P=[];N=[]
for n,m in ch.items():
    if max(m.extents)<12: continue
    p=trimesh.sample.sample_surface(m,max(10,int(m.area/80)))[0]; P.append(p); N+= [n]*len(p)
P=np.vstack(P); N=np.array(N); np.save('/tmp/chp.npy',P); np.save('/tmp/chn.npy',N)
for g in range(100,19,-10):
    d,_=tree.query(P+np.array([0,0,-g]))
    bad=d<8
    from collections import Counter
    c=Counter(N[bad]); print(g,'min',round(d.min(),1),'n<8mm',bad.sum(),dict(c.most_common(5)))
