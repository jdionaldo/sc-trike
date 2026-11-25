import numpy as np, trimesh, itertools
from fit_chassis import chassis, shell
P=1.0
sh=shell()
vox=[ (m.voxelized(P)) for m in sh.values()]
def hit(pts):
    h=np.zeros(len(pts),bool)
    for v in vox:
        idx=np.round((pts-v.transform[:3,3])/P).astype(int)
        ok=np.all((idx>=0)&(idx<v.shape),axis=1)
        m=np.zeros(len(pts),bool); m[ok]=v.matrix[tuple(idx[ok].T)]
        h|=m
    return h
base=chassis(1.0)
groups={'tire':[],'body':[]}
for n,m in base.items():
    g='tire' if ('tire' in n) else 'body'
    pts,_=trimesh.sample.sample_surface(m,max(50,int(m.area/6)))
    groups[g].append(pts)
G={g:np.vstack(v) for g,v in groups.items()}
print({g:len(v) for g,v in G.items()})


import sys
for k in (0.5,0.55):
  print('k',k)
  for dy in range(-20,21,10):
    row=[]
    for dz in range(-64,-19,6):
        t=np.array([0,dy,dz]); b=hit(G['body']*k+t).sum(); w=hit(G['tire']*k+t).sum(); row.append(f"{dz}:{b}/{w}")
    print(dy,' '.join(row))
