import numpy as np
import cadquery as cq
from scipy.spatial import ConvexHull


def hull(pts):
    """Low-poly solid: convex hull of points, coplanar triangles merged into planar facets."""
    P = np.array(pts, float)
    h = ConvexHull(P)
    groups = {}
    for eq, simp in zip(h.equations, h.simplices):
        # Only merge truly coplanar triangles. Coarse rounding merged shallow
        # folds into nonplanar wires and could also distort clearance cutters.
        groups.setdefault(tuple(np.round(eq, 8)), set()).update(int(i) for i in simp)
    faces = []
    for key, idx in groups.items():
        n = np.array(key[:3]); n /= np.linalg.norm(n)
        Q = P[sorted(idx)]
        c = Q.mean(0)
        u = np.cross(n, [0, 0, 1.0] if abs(n[2]) < 0.9 else [1.0, 0, 0]); u /= np.linalg.norm(u)
        v = np.cross(n, u)
        order = np.argsort(np.arctan2((Q - c) @ v, (Q - c) @ u))
        w = cq.Wire.makePolygon([cq.Vector(*q) for q in Q[order]], close=True)
        faces.append(cq.Face.makeFromWires(w))
    solid = cq.Solid.makeSolid(cq.Shell.makeShell(faces))
    if solid.Volume() < 0:
        solid = cq.Solid(solid.wrapped.Reversed())
    return solid.clean()


def beam(a, b, r):
    a, b = cq.Vector(*a), cq.Vector(*b)
    d = b - a
    return cq.Solid.makeCylinder(r, d.Length, a, d.normalized())


def ball(p, r):
    return cq.Workplane("XY").sphere(r).val().translate(p)


def fuse(shapes):
    shapes = list(shapes)
    return shapes[0].fuse(*shapes[1:]).clean() if len(shapes) > 1 else shapes[0]


def tubes(path_pairs, r, joints=True):
    """Tubes between point pairs, with ball joints at the ends."""
    parts = [beam(a, b, r) for a, b in path_pairs]
    if joints:
        seen = set()
        for a, b in path_pairs:
            for p in (a, b):
                if tuple(p) not in seen:
                    seen.add(tuple(p)); parts.append(ball(p, r * 1.15))
    return fuse(parts)


def mx(p):
    return (-p[0], p[1], p[2])


def mirror_x(shape):
    return shape.mirror("YZ")


# Numeric weld tolerance only: intentional armor folds stay separate planes.
WELD_LINEAR = 1e-5
WELD_ANGLE = 1e-6

def weld(s, name):
    """Unify contiguous coplanar faces and verify one closed material body."""
    from OCP.ShapeUpgrade import ShapeUpgrade_UnifySameDomain
    volume=s.Volume()
    unify=ShapeUpgrade_UnifySameDomain(s.copy().wrapped,True,True,True)
    unify.SetLinearTolerance(WELD_LINEAR)
    unify.SetAngularTolerance(WELD_ANGLE)
    unify.Build()
    result=cq.Shape.cast(unify.Shape())
    # OCC can reshape narrow folds while unifying transformed faces. Retain
    # the already fused/cleaned original when that alters the material volume.
    if (not result.isValid() or len(result.Solids())!=len(s.Solids())
            or len(result.Shells())!=len(s.Shells())
            or abs(result.Volume()-volume)>=max(0.001,volume*1e-7)):
        result=s
    assert result.isValid() and len(result.Solids())==1, name+': weld must remain one solid'
    from OCP.BRep import BRep_Tool
    assert len(result.Shells())==len(s.Shells()), name+': weld changed internal voids'
    assert all(BRep_Tool.IsClosed_s(sh.wrapped) for sh in result.Shells()), name+': open boundary shell'
    assert abs(result.Volume()-volume)<max(0.001,volume*1e-7), name+': weld changed material volume'
    return result


def clean_registered(obj):
    """Remove coplanar subdivision seams throughout a part or nested assembly.

    Keep separate bodies and designed folds. Never accept a cleanup that changes
    volume, validity, or body count. Imported hardware keeps its original fit.
    """
    if isinstance(obj,cq.Assembly):
        seen=set()
        for node in obj.objects.values():
            if node.obj is None or id(node) in seen:
                continue
            seen.add(id(node))
            node.obj=clean_registered(node.obj)
        return obj
    shape=obj.val() if isinstance(obj,cq.Workplane) else obj
    if not isinstance(shape,cq.Shape) or not shape.isValid():
        return obj
    candidate=shape.clean()
    if (candidate.isValid() and len(candidate.Solids())==len(shape.Solids())
            and len(candidate.Shells())==len(shape.Shells())
            and abs(candidate.Volume()-shape.Volume())<max(0.001,shape.Volume()*1e-7)):
        return candidate
    return obj
