"""Constant-normal-thickness faceted panels with bounded, local edge mitres."""
from collections import defaultdict
import numpy as np
from parts.util import hull


def printed_thickness(normal,thickness):
    """Model-frame offset along `normal` that prints as thickness*SHELL_SCALE. The shell is stretched after it is built
    (x by the width match, y by SHELL_SCALE, z by SHELL_SCALE*SHELL_Z), so a wall of one model thickness printed 2.3 mm on
    side-facing facets, 2.7 mm on top-facing ones and 3.0 mm only on facets facing forward. Two parallel planes a distance t
    apart along n end up t/|S^-1 n| apart after the stretch S; solve that for the printed wall."""
    from parts.params import SHELL_SCALE,SHELL_Z,SHELL_HALF_WIDTH,BASE_HALF_WIDTH
    stretch=np.array([SHELL_SCALE*SHELL_HALF_WIDTH/BASE_HALF_WIDTH,SHELL_SCALE,SHELL_SCALE*SHELL_Z])
    return thickness*SHELL_SCALE*float(np.linalg.norm(np.asarray(normal,float)/stretch))


def panel_prisms(triangles,direction,thickness,final_frame=False):
    """Each broad inner face is parallel to its outer face, exactly one printed wall away.

    Edge and corner connectors stay local. Very acute folds get an inner bevel
    rather than an arbitrarily deep intersection of several offset planes.
    final_frame: the triangles are already in printed coordinates, so `thickness` is used as it is.
    """
    def wall(n):
        return thickness if final_frame else printed_thickness(n,thickness)
    plates=[]; edges=defaultdict(list); corners=defaultdict(list)
    for tri in triangles:
        pts=np.array(tri,float)
        n=np.cross(pts[1]-pts[0],pts[2]-pts[0]); n/=np.linalg.norm(n)
        if np.dot(n,direction)<0:
            n=-n
        off=n*wall(n)
        plates.append(hull(list(pts)+list(pts+off)))
        for p in tri:
            corners[tuple(p)].append(off)
        for a,b in zip(tri,tri[1:]+tri[:1]):
            edges[tuple(sorted((tuple(a),tuple(b))))].append(n)
    for (a,b),normals in edges.items():
        if len(normals)<2 or np.linalg.norm(np.cross(normals[0],normals[1]))<1e-7:
            continue
        vertices=[np.array(p) for p in (a,b)]
        t0,t1=wall(normals[0]),wall(normals[1])
        points=vertices+[p+n*t for p in vertices for n,t in ((normals[0],t0),(normals[1],t1))]
        dot=float(normals[0]@normals[1])
        if dot>-.5:  # Limit the internal mitre to twice the wall thickness.
            # The point where both offset planes meet, in the plane of the two normals.
            mitre=(normals[0]*(t0-t1*dot)+normals[1]*(t1-t0*dot))/(1-dot*dot)
            points.extend(p+mitre for p in vertices)
            for p in (a,b):
                corners[p].append(mitre)
        plates.append(hull(points))
    for p,offsets in corners.items():
        vertex=np.array(p); points=[vertex]+[vertex+o for o in offsets]
        if np.linalg.matrix_rank(np.array(points)-vertex,tol=1e-8)==3:
            plates.append(hull(points))
    return plates


def panel_solid(triangles, direction, thickness, max_uneven=0.12):
    """The whole faceted panel as ONE closed polyhedron (not a union of prisms): outer skin = the triangles, inner skin = the same
    triangles with every vertex moved to the point where its incident offset planes meet (least squares, exact for the usual 3-plane
    vertex), plus a wall along every free boundary edge. Because no plates overlap, no connector hulls are needed and there are no
    chord strips, bevel slivers or notches at the corners. Returns None when a vertex fan is too uneven to offset cleanly (the caller
    then keeps panel_prisms)."""
    import cadquery as cq
    P=[]; idx={}
    def vid(p):
        k=tuple(np.round(np.array(p,float),6))
        if k not in idx: idx[k]=len(P); P.append(np.array(p,float))
        return idx[k]
    T=[]; N=[]
    for tri in triangles:
        a,b,c=[vid(p) for p in tri]
        n=np.cross(P[b]-P[a],P[c]-P[a]); L=np.linalg.norm(n)
        if L<1e-9: continue
        n/=L
        T.append((a,b,c)); N.append(n)
    # Wind every facet consistently by walking across shared edges (a facet folded more than 90 deg away from `direction` would
    # get the wrong side from a per-facet test); the seed is the facet that faces `direction` best.
    dirv=np.array(direction,float); dirv/=np.linalg.norm(dirv)
    seed=int(np.argmax([abs(n@dirv) for n in N]))
    if N[seed]@dirv<0: a0,b0,c0=T[seed]; T[seed]=(a0,c0,b0); N[seed]=-N[seed]
    by_edge={}
    for i,t in enumerate(T):
        for u,w in ((t[0],t[1]),(t[1],t[2]),(t[2],t[0])): by_edge.setdefault((min(u,w),max(u,w)),[]).append(i)
    done={seed}; todo=[seed]
    while todo:
        i=todo.pop(); t=T[i]; mine={(t[0],t[1]),(t[1],t[2]),(t[2],t[0])}
        for (u,w) in list(mine):
            for j in by_edge[(min(u,w),max(u,w))]:
                if j in done: continue
                tj=T[j]
                if (u,w) in {(tj[0],tj[1]),(tj[1],tj[2]),(tj[2],tj[0])}:      # same direction along the shared edge: flip j
                    T[j]=(tj[0],tj[2],tj[1]); N[j]=-N[j]
                done.add(j); todo.append(j)
    if len(done)!=len(T): return None                      # not one edge-connected panel
    fan={}
    for t,n in zip(T,N):
        for v in t: fan.setdefault(v,[]).append(n)
    Q={}; worst=0.0
    for v,ns in fan.items():
        A=np.array(ns); d,_,_,_=np.linalg.lstsq(A,np.full(len(A),float(thickness)),rcond=None)
        worst=max(worst,float(np.abs(A@d-thickness).max())/thickness)
        Q[v]=P[v]+d
    import os
    if os.environ.get('FUGU_SKIN_DEBUG'): print('panel_solid',len(T),'facets, worst vertex miss',round(worst,3),'limit',max_uneven,flush=True)
    if worst>max_uneven: return None   # share of the wall by which one inner vertex misses its offset planes
    edges={}
    for t in T:
        for u,w in ((t[0],t[1]),(t[1],t[2]),(t[2],t[0])): edges.setdefault((min(u,w),max(u,w)),[]).append((u,w))
    def face(*pts):
        return cq.Face.makeFromWires(cq.Wire.makePolygon([cq.Vector(*p) for p in pts],close=True))
    faces=[]
    for (a,b,c) in T:
        faces.append(face(P[a],P[c],P[b]))                 # outer skin: normal -n (away from the body)
        faces.append(face(Q[a],Q[b],Q[c]))                 # inner skin: normal +n
    for key,use in edges.items():
        if len(use)!=1: continue
        u,w=use[0]                                          # the triangle runs u->w along this free edge
        faces.append(face(P[u],Q[u],Q[w])); faces.append(face(P[u],Q[w],P[w]))
    shell=cq.Shell.makeShell(faces)
    s=cq.Solid.makeSolid(shell).fix()
    if s.Volume()<0:
        s=cq.Solid(s.wrapped.Reversed())
    if not s.isValid() or s.Volume()<=0: return None
    return s.clean()
