"""Surface audit of output/model.step against the panel-alignment requirements (planarity, creases, corners, seam gaps).
Run: python tools/surface_audit.py   (reads output/model.step; no model rebuild)"""
import cadquery as cq, numpy as np, itertools, collections, sys
from OCP.STEPControl import STEPControl_Reader
r=STEPControl_Reader(); r.ReadFile('output/model.step'); r.TransferRoots()
sh=cq.Shape.cast(r.OneShape())
sol=sorted(sh.Solids(),key=lambda s:-s.Volume())
def pick(f): 
    c=[s for s in sol if f(s.BoundingBox())]; return max(c,key=lambda s:s.Volume())
F=pick(lambda b:b.ymin<-300 and b.xlen>150 and b.zmax<260)
C=max([s for s in sol if len(s.Faces())>300 and -220<s.BoundingBox().ymin<-205 and 100<s.BoundingBox().ymax<125 and 215<s.BoundingBox().zmax<235],key=lambda s:s.Volume())  # the canopy (not the cage tubes)
print('== 1. Facet planarity: curved-type faces whose surface deviates from its best plane')
bad=[];tot=0
for f in F.Faces():
    if f.Area()<30 or f.geomType()=='CYLINDER': continue
    tot+=1
    pts=[]
    for u in (0.1,0.5,0.9):
        for v in (0.1,0.5,0.9):
            try: pts.append(f.positionAt(u,v).toTuple())
            except Exception: pass
    if len(pts)<5: continue
    P=np.array(pts);c=P.mean(0);_,s,vt=np.linalg.svd(P-c);dev=s[-1]/np.sqrt(len(P))*2
    if dev>0.05: bad.append((round(f.Area()),round(dev,2)))
print('  faces >30 mm2:',tot,' with >0.05 mm warp:',len(bad),' worst:',sorted(bad,key=lambda x:-x[1])[:5])
print('== 2. Large facets: count of faces >500 mm2 and their normals pairs differing 0.5-8 deg (near-misses that should be one plane)')
big=[(f,f.normalAt(f.Center())) for f in F.Faces() if f.Area()>500]
near=[]
for (f1,n1),(f2,n2) in itertools.combinations(big,2):
    a=np.degrees(n1.getAngle(n2))
    if 0.3<a<8 and f1.distance(f2)<1e-3: near.append((round(a,2),round(f1.Area()),round(f2.Area())))
print('  large faces:',len(big),' adjacent near-miss pairs (angle deg, areas):',sorted(near))
print('== 3. Seam gaps: Front shell <-> Canopy (distance from each canopy face to the front shell, faces within 2 mm)')
gaps=[]
for f in C.Faces():
    d=F.distance(f)
    if d<2.0: gaps.append(d)
g=np.array(gaps)
if len(g): print('  faces facing the seam:',len(g),' gap min/mean/max: %.3f %.3f %.3f'%(g.min(),g.mean(),g.max()),' target 0.30; outside 0.25-0.35:',int(((g<0.25)|(g>0.35)).sum()))
print('== 4. A-pillar foot flushness (left/right): canopy outer x vs front shell outer x at y=-213..-205, z=126')
for sx in (-1,1):
    row=[]
    for y in (-213,-209,-205):
        res=[]
        for S in (F,C):
            pts=S.intersect(cq.Solid.makeBox(120,0.5,0.5,cq.Vector(0 if sx>0 else -120,y,126))).Vertices()
            xs=[abs(v.X) for v in pts]; res.append(max(xs) if xs else None)
        row.append((y,None if res[0] is None else round(res[0],2),None if res[1] is None else round(res[1],2)))
    print('  side',sx,'(y, front shell |x|, canopy |x|):',row)
