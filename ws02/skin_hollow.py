"""Hollow a closed faceted solid into a uniform inward-offset wall without touching the outer surface.

Method (same idea as the panel-skin shell_mesh): every vertex of the kept outer surface moves to the intersection of its incident face planes, each
shifted inward by t (least squares when more than three distinct planes meet, small pull towards the plain normal offset where fewer than three do).
The inner surface has the outer surface's topology, so wall + rim strips along every free edge form a closed, watertight mesh.  Creases stay hard,
panels stay planar (up to the planarity of the source).  Free edges come from removing faces (open underside, open joint ends).
"""
import numpy as np
import trimesh


def _unique_planes(normals, dists, tol_deg=1.5):
    """Merge incident planes whose normals differ by less than tol_deg (triangulated planar panels give many identical planes)."""
    out = []
    c = np.cos(np.radians(tol_deg))
    for n, d in zip(normals, dists):
        for o in out:
            if o[0] @ n > c:
                o[1].append(n)
                o[2].append(d)
                break
        else:
            out.append([n, [n], [d]])
    return [(np.mean(ns, 0) / np.linalg.norm(np.mean(ns, 0)), float(np.mean(ds))) for _, ns, ds in out]


def hollow(mesh, remove_mask, t=2.4, pin_planes=(), lam=1e-3):
    """mesh: closed trimesh (outer surface, outward normals).  remove_mask: bool per face, faces to drop (they open the shell).
    pin_planes: iterable of (normal, offset): boundary vertices lying on such a plane keep their position along its normal (flat joint faces).
    Returns a closed trimesh: outer kept faces + inner (offset) faces + rim strips."""
    V = np.asarray(mesh.vertices, float)
    F = np.asarray(mesh.faces)
    keep = ~np.asarray(remove_mask)
    Fk = F[keep]
    fn = mesh.face_normals[keep]
    fd = np.einsum("ij,ij->i", fn, V[Fk[:, 0]])
    used = np.unique(Fk)
    inc = {v: [] for v in used}
    for k, f in enumerate(Fk):
        for v in f:
            inc[v].append(k)
    # boundary edges of the kept set
    e = np.sort(np.vstack([Fk[:, [0, 1]], Fk[:, [1, 2]], Fk[:, [2, 0]]]), axis=1)
    uniq, cnt = np.unique(e, axis=0, return_counts=True)
    bnd = {tuple(x) for x in uniq[cnt == 1]}
    bverts = {v for ed in bnd for v in ed}
    Fr = F[~keep]
    rn = mesh.face_normals[~keep]
    rd = np.einsum("ij,ij->i", rn, V[Fr[:, 0]]) if len(Fr) else np.zeros(0)
    rinc = {}
    for k, f in enumerate(Fr):
        for v in f:
            rinc.setdefault(v, []).append(k)
    inner = np.zeros_like(V)
    for v in used:
        ks = inc[v]
        pl = _unique_planes(fn[ks], fd[ks])
        A = np.array([p[0] for p in pl])
        b = np.array([p[1] - t for p in pl])
        nbar = fn[ks].sum(0)
        nbar /= np.linalg.norm(nbar)
        x0 = V[v] - t * nbar
        rows, rhs = [A], [b]
        if v in bverts:
            for pn, po in ([]):
                rows.append(1000.0 * pn[None, :])
                rhs.append(np.array([1000.0 * po]))
            for pn, po in pin_planes:
                pn = np.asarray(pn, float)
                if abs(pn @ V[v] - po) < 1e-3:
                    rows.append(1000.0 * pn[None, :])
                    rhs.append(np.array([1000.0 * po]))
        rows.append(np.sqrt(lam) * np.eye(3))
        rhs.append(np.sqrt(lam) * x0)
        inner[v] = np.linalg.lstsq(np.vstack(rows), np.concatenate(rhs), rcond=None)[0]
    n = len(V)
    Vn = np.vstack([V, inner])
    tris = [Fk, Fk[:, ::-1] + n]
    # rim: each boundary edge (a,b) as used by its kept face (a->b in that face's winding); outer winding a->b, so the strip is a,b,b',a' reversed against it
    fe = {}
    for f in Fk:
        for i in range(3):
            fe[(f[i], f[(i + 1) % 3])] = True
    rim = []
    for a, b in bnd:
        if (a, b) in fe:
            p, q = a, b
        else:
            p, q = b, a
        rim.append([p, q + n, q])             # outer edge p->q is in the kept face; the neighbour across it is the strip
        rim.append([p, p + n, q + n])
    if rim:
        tris.append(np.array(rim))
    Fa = np.vstack(tris)
    out = trimesh.Trimesh(Vn, Fa, process=False)
    used_idx = np.unique(Fa)
    out = trimesh.Trimesh(Vn[used_idx], np.searchsorted(used_idx, Fa), process=False)
    return out


def inner_solid(mesh, t=2.4):
    """Closed solid's uniform inward offset (vertex plane intersections): returns the inner surface as a closed trimesh with outward normals (the cavity)."""
    H = hollow(mesh, np.zeros(len(mesh.faces), bool), t)
    n = len(mesh.vertices)
    used = np.unique(mesh.faces)
    k = len(used)
    inner_faces = np.asarray(H.faces)[len(mesh.faces):2 * len(mesh.faces)]      # the reversed inner block
    return trimesh.Trimesh(np.asarray(H.vertices), inner_faces[:, ::-1], process=False), H


def sweep(solid_mesh, d, length=90.0, min_dot=0.8):
    """Manifold of the solid swept along direction d by `length`: union of the solid and the prisms of its faces that look along d."""
    import manifold3d as m3
    d = np.asarray(d, float) / np.linalg.norm(d)
    V = solid_mesh.vertices
    F = solid_mesh.faces
    fn = solid_mesh.face_normals
    parts = []
    for f in F[fn @ d > min_dot]:
        pts = np.vstack([V[f] - d * 0.15, V[f] + d * length])        # starts 0.15 mm inside the cavity: no membrane left between cavity face and prism
        parts.append(m3.Manifold.hull_points(pts))
    sw = m3.Manifold.batch_boolean(parts, m3.OpType.Add) if parts else None
    return sw


def _tm(M):
    me = M.to_mesh()
    return trimesh.Trimesh(np.asarray(me.vert_properties)[:, :3].astype(float), np.asarray(me.tri_verts), process=False)


def fix_thin(mesh, cav_man, thr, cell=3.0, iters=4, nsamp=150000):
    """Where the cavity surface comes closer than `thr` to the outer surface (a deck between a pocket and the belly, an acute sill edge) the cavity is
    cut back with small blocks, so those places stay solid material instead of a sliver wall.  Returns the cavity Manifold and the number of blocks."""
    import manifold3d as m3
    from trimesh.proximity import closest_point
    blocks = set()
    for it in range(iters):
        ct = _tm(cav_man)
        pts, _ = trimesh.sample.sample_surface(ct, nsamp)
        _, d, _ = closest_point(mesh, pts)
        bad = pts[d < thr]
        if len(bad) == 0:
            break
        cells = {tuple(c) for c in np.floor(bad / cell).astype(int)}
        new = set()
        for c in cells:
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    for dz in (-1, 0, 1):
                        new.add((c[0] + dx, c[1] + dy, c[2] + dz))
        new -= blocks
        blocks |= new
        cubes = [m3.Manifold.cube((cell, cell, cell), center=False).translate((c[0] * cell, c[1] * cell, c[2] * cell)) for c in new]
        cav_man = cav_man - m3.Manifold.batch_boolean(cubes, m3.OpType.Add)
    return cav_man, len(blocks)


def _end_prism(cav_t, x_end, sign, t, ext=1.0):
    """Prism that removes the end cap: the cavity's cross-section just inside the cap (and everything below it), extruded across the cap thickness."""
    import manifold3d as m3
    from shapely.geometry import box
    from shapely.geometry.polygon import orient
    x_sec = x_end - sign * (t + 0.05)
    sec = cav_t.section(plane_origin=[x_sec, 0, 0], plane_normal=[1, 0, 0])
    pl, T = sec.to_planar()
    polys = [p for p in pl.polygons_full if p.area > 1.0]
    from shapely.ops import unary_union
    # planar coordinates -> world (y, z): T maps planar xy to the section plane
    def w(poly):
        pts = np.array(poly.exterior.coords)
        P3 = trimesh.transformations.transform_points(np.c_[pts, np.zeros(len(pts))], T)
        return P3[:, 1], P3[:, 2]
    from shapely.geometry import Polygon
    polyw = []
    for pp in polys:
        y, z = w(pp)
        polyw.append(Polygon(np.c_[y, z]))
    u = unary_union(polyw)
    zmin = u.bounds[1]
    u = unary_union([u, box(u.bounds[0], zmin - 200.0, u.bounds[2], zmin + 1.0)])
    u = u.buffer(0.03, join_style=2)                                   # a hair larger than the cavity: no coplanar faces (they leave pinched edges)
    geoms = list(u.geoms) if hasattr(u, "geoms") else [u]
    out = None
    L = t + 0.05 + ext
    for g in geoms:
        g = orient(g, 1.0)
        cs = m3.CrossSection([[(float(a), float(b)) for a, b in list(g.exterior.coords)[:-1]]])
        pr = m3.Manifold.extrude(cs, L).rotate((90.0, 0.0, 90.0))             # (y,z) section extruded along +x from x = 0
        pr = pr.translate((x_sec - L, 0, 0)) if sign < 0 else pr.translate((x_sec, 0, 0))
        out = pr if out is None else out + pr
    return out


def open_shell(mesh, dirs, t=2.4, length=90.0, thr=2.2):
    """Hollow `mesh` (closed) with uniform wall t and open the sides facing `dirs`: (0,0,-1) the belly (the cavity swept down), (-1,0,0) / (1,0,0) a joint end
    (cap cut away by the cavity's own cross-section).  Returns (trimesh, cavity trimesh)."""
    import manifold3d as m3
    cav, H0 = inner_solid(mesh, t)
    man = lambda tm_: m3.Manifold(m3.Mesh(vert_properties=np.asarray(tm_.vertices, np.float32), tri_verts=np.asarray(tm_.faces, np.uint32)))
    cm, nb = fix_thin(mesh, man(cav), thr)
    cav = _tm(cm)
    cutter = cm
    for d in dirs:
        d = np.asarray(d, float)
        if abs(d[0]) > 0.99:
            sign = np.sign(d[0])
            x_end = mesh.bounds[0][0] if sign < 0 else mesh.bounds[1][0]
            cutter = cutter + _end_prism(cav, x_end, sign, t)
        else:
            c2 = cav.copy()
            c2.vertices = c2.vertices + (c2.vertices - c2.centroid) * 4e-4              # a hair wider than the cavity: no coplanar cutter faces (they leave pinched edges)
            cutter = cutter + sweep(c2, d, length)
    out = man(mesh) - cutter
    return _tm(out), cav
