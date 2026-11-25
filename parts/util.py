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
    if id(shape) in NO_CLEAN:
        return obj   # chamfered by chamfer_moving: OCC's clean() can crash on chamfered solids (segmentation fault on the upper arm, November 24)
    if not isinstance(shape,cq.Shape) or not shape.isValid():
        return obj
    try: candidate=shape.clean()
    except Exception: return obj   # OCC can raise on near-tangent faces: register the part uncleaned
    if (candidate.isValid() and len(candidate.Solids())==len(shape.Solids())
            and len(candidate.Shells())==len(shape.Shells())
            and abs(candidate.Volume()-shape.Volume())<max(0.001,shape.Volume()*1e-7)):
        return candidate
    return obj


CHAMFER = 0.5   # mm: uniform edge break on every external convex edge of the printed parts


def chamfer_convex(solid, d=CHAMFER, min_turn=50.0, min_len=3.0, label='', chunk=40):
    """Chamfer every outside (convex) edge of a printed part by d mm.
    Skips edges that turn less than min_turn degrees (soft facet creases and the 45 degree flats of the square tubes, which are already
    chamfered), edges shorter than min_len, and edges on curved faces (holes, bosses, bores). Never touches concave edges.
    Tries all edges together, then in chunks, then one by one; whatever the kernel rejects is left sharp and reported. Returns (solid, n_done, n_total)."""
    import math
    import cadquery as cq
    faces_of = {}
    for f in solid.Faces():
        for e in f.Edges(): faces_of.setdefault(e.hashCode(), []).append(f)
    picked = []
    for e in solid.Edges():
        fs = faces_of.get(e.hashCode(), [])
        if len(fs) != 2 or e.Length() < min_len: continue
        if any(f.geomType() not in ('PLANE',) for f in fs): continue
        mid = e.positionAt(0.5)
        n1, n2 = fs[0].normalAt(mid), fs[1].normalAt(mid)
        turn = math.degrees(math.acos(max(-1.0, min(1.0, n1.dot(n2)))))
        if turn < min_turn: continue
        eps = 0.05
        if solid.isInside(mid + (n1 - n2) * eps) or solid.isInside(mid + (n2 - n1) * eps): continue     # not convex
        picked.append(e)
    total = len(picked); done = 0

    def ok(s): return s is not None and s.isValid() and len(s.Solids()) == 1

    def apply(s, edges):
        try:
            r = s.chamfer(d, None, edges)
            return r if ok(r) else None
        except Exception:
            return None
    # edges of a solid change identity after each chamfer, so re-pick by position when working in chunks
    r = apply(solid, picked)
    if r is not None:
        print('chamfer %s: %d/%d edges at once' % (label, total, total)); return r, total, total
    cur = solid; keys = [(tuple(round(c, 2) for c in e.positionAt(0.5).toTuple()), e.Length()) for e in picked]
    def find(s, key):
        best = None
        for e in s.Edges():
            if abs(e.Length() - key[1]) < 0.01:
                p = e.positionAt(0.5)
                if (abs(p.x - key[0][0]) + abs(p.y - key[0][1]) + abs(p.z - key[0][2])) < 0.03: return e
        return best
    for i in range(0, len(keys), chunk):
        es = [find(cur, k) for k in keys[i:i + chunk]]; es = [e for e in es if e is not None]
        r = apply(cur, es)
        if r is not None: cur = r; done += len(es); continue
        for k in keys[i:i + chunk]:
            e = find(cur, k)
            if e is None: continue
            r = apply(cur, [e])
            if r is not None: cur = r; done += 1
    print('chamfer %s: %d/%d edges (rest left sharp)' % (label, done, total))
    return cur, done, total


# Moving parts and parts that carry a moving joint (owner, November 24: "apply chamfers to them, all except gears"): outside edges and boss / rim
# circles get EDGE_OUT, the entry of every bore, pocket and insert hole EDGE_BORE (fit diameters unchanged, only the first EDGE_BORE mm of a bore
# opens up). Gear and pulley teeth are skipped (circles_only: only full circles of radius >= 2 mm are touched, the tooth slots are open arcs).
EDGE_OUT = 0.6
NO_CLEAN = set()          # ids of chamfered shapes: clean_registered leaves them alone
EDGE_BORE = 0.4
MIN_LAND = 1.5            # a circular edge on a land narrower than this (pocket floor between two bores) stays sharp: a 0.4 break there leaves a sliver


def _chamfer_edges(solid, keys, d, chunk=40):
    """Chamfer the edges at `keys` [(midpoint, length)] by d: all at once, then in chunks, then one by one. Returns (solid, done, failed keys)."""
    def ok(s): return s is not None and s.isValid() and len(s.Solids()) == 1

    def apply(s, edges):
        try:
            r = s.chamfer(d, None, edges)
            return r if ok(r) else None
        except Exception:
            return None

    def find(s, key):
        """the edge at key, also after neighbouring chamfers trimmed its ends (same line or circle, midpoint within 1 mm, length within 2.5 mm)"""
        mid, ln = key[0], key[1]
        best, bd = None, 1e9
        for e in s.Edges():
            if abs(e.Length() - ln) > 2.5: continue
            m = e.positionAt(0.5); dm = (m - mid).Length
            if dm > 1.0: continue
            if e.geomType() == 'LINE':
                t = e.tangentAt(0.5); off = (mid - m) - t * (mid - m).dot(t)
                if off.Length > 0.02: continue
            elif dm > 0.03: continue
            if dm + abs(e.Length() - ln) < bd: best, bd = e, dm + abs(e.Length() - ln)
        return best
    if not keys: return solid, 0, []
    es = [e for e in (find(solid, k) for k in keys) if e is not None]
    r = apply(solid, es) if len(es) == len(keys) else None
    if r is not None: return r, len(keys), []
    cur, done, failed = solid, 0, []
    for i in range(0, len(keys), chunk):
        part = keys[i:i + chunk]
        es = [find(cur, k) for k in part]
        r = apply(cur, [e for e in es if e is not None]) if all(e is not None for e in es) else None
        if r is not None: cur = r; done += len(part); continue
        for k in part:
            e = find(cur, k)
            r = apply(cur, [e]) if e is not None else None
            if r is not None: cur = r; done += 1
            else: failed.append(k)
    return cur, done, failed


def chamfer_moving(solid, label='', out=EDGE_OUT, bore=EDGE_BORE, circles_only=False, min_turn=50.0, min_len=2.0, keep_sharp_r=()):
    """Edge break of a moving / joint-carrying printed part (see EDGE_OUT). Outside: convex plane-plane edges that turn >= min_turn deg and are
    >= min_len long, and convex full circles where a boss, hub or rim end meets a plane. Bores: full circles where a hole meets a plane.
    circles_only: only full circles of radius >= 2 mm (pulleys: hub, flange and bore, never the teeth). Prints the counts; returns the solid."""
    import math
    faces_of = {}
    for f in solid.Faces():
        for e in f.Edges(): faces_of.setdefault(e.hashCode(), []).append(f)
    outs, bores = [], []
    for e in solid.Edges():
        fs = faces_of.get(e.hashCode(), [])
        if len(fs) != 2: continue
        kinds = sorted(f.geomType() for f in fs)
        if kinds == ['PLANE', 'PLANE'] and not circles_only:
            if e.Length() < min_len: continue
            mid = e.positionAt(0.5)
            n1, n2 = fs[0].normalAt(mid), fs[1].normalAt(mid)
            if math.degrees(math.acos(max(-1.0, min(1.0, n1.dot(n2))))) < min_turn: continue
            if solid.isInside(mid + (n1 - n2) * 0.05) or solid.isInside(mid + (n2 - n1) * 0.05): continue     # concave
            outs.append(e)
        elif kinds == ['CYLINDER', 'PLANE'] and e.geomType() == 'CIRCLE' and e.IsClosed():
            try: r = e.radius()
            except Exception: continue
            if r < (2.0 if circles_only else 1.2): continue
            cyl = fs[0] if fs[0].geomType() == 'CYLINDER' else fs[1]
            c = e.Center(); q = e.positionAt(0.25); n = cyl.normalAt(q)
            n1, n2 = fs[0].normalAt(q), fs[1].normalAt(q)
            if solid.isInside(q + (n1 - n2) * 0.05) or solid.isInside(q + (n2 - n1) * 0.05): continue     # concave: a seat floor or pocket bottom
            pl = fs[0] if fs[0].geomType() == 'PLANE' else fs[1]
            narrow = False
            for e2 in pl.Edges():                     # a step between two concentric bores (pocket floor, seat shoulder) narrower than MIN_LAND: left sharp
                if e2.geomType() == 'CIRCLE' and not e2.isSame(e):
                    try: r2 = e2.radius()
                    except Exception: continue
                    if (e2.Center() - c).Length < 0.05 and 0 < abs(r2 - r) < MIN_LAND: narrow = True
            if narrow: continue
            if any(abs(r - k) < 0.02 for k in keep_sharp_r): continue   # e.g. bearing seats whose full length carries the load
            (bores if (c - q).dot(n) > 0 else outs).append(e)                    # face normal toward the axis: a hole
    n_out, n_bore = len(outs), len(bores)
    key = lambda e: (e.positionAt(0.5), e.Length())
    sizes = {}
    for grp, d0, n in ((outs, out, 'out'), (bores if bore > 0 else [], max(bore, 0.0), 'bore')):     # bore=0: entries left sharp
        left = [key(e) for e in grp]; sizes.setdefault(n, [])
        for d in ((d0, round(d0 * 0.66, 2)) if d0 > 0 else ()):          # edges the kernel rejects at the full size get a smaller break (no smaller: tiny faces distort the FEM mesh)
            solid, done, left = _chamfer_edges(solid, left, d)
            sizes.setdefault(n, []).append('%d at %.2f' % (done, d))
            if not left: break
        sizes[n].append('%d sharp' % len(left))
    NO_CLEAN.add(id(solid))
    print('edge break %s: outside (%d edges) %s; bore entries (%d) %s' % (label, n_out, ', '.join(sizes['out']), n_bore, ', '.join(sizes['bore'])))
    return solid
