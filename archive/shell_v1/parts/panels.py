"""Constant-normal-thickness faceted panels with bounded, local edge mitres."""
from collections import defaultdict
import numpy as np
from parts.util import hull


def panel_prisms(triangles,direction,thickness):
    """Each broad inner face is parallel to its outer face, exactly thickness away.

    Edge and corner connectors stay local. Very acute folds get an inner bevel
    rather than an arbitrarily deep intersection of several offset planes.
    """
    plates=[]; edges=defaultdict(list); corners=defaultdict(list)
    for tri in triangles:
        pts=np.array(tri,float)
        n=np.cross(pts[1]-pts[0],pts[2]-pts[0]); n/=np.linalg.norm(n)
        if np.dot(n,direction)<0:
            n=-n
        plates.append(hull(list(pts)+list(pts+n*thickness)))
        for p in tri:
            corners[tuple(p)].append(n)
        for a,b in zip(tri,tri[1:]+tri[:1]):
            edges[tuple(sorted((tuple(a),tuple(b))))].append(n)
    for (a,b),normals in edges.items():
        if len(normals)<2 or np.linalg.norm(np.cross(normals[0],normals[1]))<1e-7:
            continue
        vertices=[np.array(p) for p in (a,b)]
        points=vertices+[p+n*thickness for p in vertices for n in normals]
        dot=float(normals[0]@normals[1])
        if dot>-.5:  # Limit the internal mitre to twice the wall thickness.
            mitre=(normals[0]+normals[1])*thickness/(1+dot)
            points.extend(p+mitre for p in vertices)
            for p in (a,b):
                corners[p].append(mitre/thickness)
        plates.append(hull(points))
    for p,normals in corners.items():
        vertex=np.array(p); points=[vertex]+[vertex+n*thickness for n in normals]
        if np.linalg.matrix_rank(np.array(points)-vertex,tol=1e-8)==3:
            plates.append(hull(points))
    return plates
