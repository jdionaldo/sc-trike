"""Place the scaled chassis GLB in the shell frame and measure collisions with the shell skins."""
import numpy as np, trimesh, sys, itertools, os
HERE=os.path.dirname(os.path.abspath(__file__))
def chassis(k):
    s=trimesh.load(os.path.join(HERE,"..","inputs","WS03_chassis_only.glb")); out={}
    M=np.array([[0,0,-1,0],[-1,0,0,0],[0,1,0,0],[0,0,0,1.0]])
    for n in s.graph.nodes_geometry:
        T,g=s.graph[n]; m=s.geometry[g].copy(); m.apply_transform(M@T); m.apply_scale(k); out[n]=m
    return out
def shell():
    return {n:trimesh.load(os.path.join(HERE,"..","exports",n+".stl")) for n in ["Front_shell","Rear_shell","Canopy"]}
if __name__=="__main__":
    sh=shell(); ch=chassis(1.0)
    for n,m in sh.items(): print(n,np.round(m.bounds,1).tolist(),m.is_watertight)
    allm=trimesh.util.concatenate(list(ch.values())); print('chassis',np.round(allm.bounds,1).tolist())
