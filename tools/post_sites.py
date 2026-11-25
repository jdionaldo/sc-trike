import numpy as np, trimesh
from scipy.spatial import cKDTree
from fit_chassis import chassis
ch=chassis(1.0); OFF=np.array([0,0,-45.0])
P=np.vstack([trimesh.sample.sample_surface(m,max(10,int(m.area/6)))[0] for n,m in ch.items() if not n.startswith('mock_tire') and n!='mock_rear_tire_ring' and 'w3_deck' not in n and max(m.extents)>3])+OFF
tree=cKDTree(P[:,:2])
def deck(y): return (38 if y<-72 else 48 if y<50 else 56)-45.0
def free(x,y,h=40,r=9):
    z0=deck(y)+1
    idx=tree.query_ball_point([x,y],r)
    return not any(z0<P[i,2]<z0+h for i in idx)
for y in range(-230,171,10):
    xs=[x for x in range(0,56,4) if free(x,y)]
    print(y,'deck z',deck(y),'free |x| for post (Ø18 col, 40 high):',xs)
