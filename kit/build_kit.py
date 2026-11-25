"""Turn the exported part STLs into the print kit: repair, split to the bed with pin joints, orient, write oriented STLs, manifest.

    kit/venv python kit/build_kit.py <stl_dir> [--out kit/print]

Needs trimesh, shapely, manifold3d, numpy (see kit/README.md). All sizes in mm.
"""
import os, sys, json, math, glob, argparse
import numpy as np, trimesh
from shapely.geometry import Point
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from registry import PARTS, key_of, is_hardware, SUB_ORDER, SUBS
import polish_stls

# FUGU_BED="x,y,z": P2S 256,256,256 (default) or the user's H3C/H2C-class 330,320,325. Conservative square usable area (5 mm margin each side).
_bx, _by, _bz = (float(v) for v in os.environ.get("FUGU_BED", "256,256,256").split(","))
BED = min(_bx, _by)
USABLE = BED - 10.0
ZMAX = _bz - 6.0
PIECE_TARGET = USABLE - 36.0   # target piece length along the cut axis (pins add 2 x PIN_L at most)
PIN_L = 6.0; CLEAR = 0.15
LOG = []


def log(*a):
    s = " ".join(str(x) for x in a); LOG.append(s); print(s)


def repair(m, name):
    m = m.copy(); m.merge_vertices(); m.update_faces(m.nondegenerate_faces()); m.remove_unreferenced_vertices()
    trimesh.repair.fix_normals(m); trimesh.repair.fill_holes(m)
    for it in range(40):   # tiny non-manifold spots: an edge shared by 3 faces -> drop the smallest (sliver) face, re-close
        if m.is_volume: break
        e = m.edges_sorted; u, inv, cnt = np.unique(e, axis=0, return_inverse=True, return_counts=True)
        over = np.where(cnt > 2)[0]
        if len(over) == 0:
            trimesh.repair.fill_holes(m); break
        eid = np.repeat(np.arange(len(m.faces)), 3)
        drop = set()
        for o in over:
            fs = np.unique(eid[inv == o]); drop.add(int(fs[np.argmin(m.area_faces[fs])]))
        keep = np.ones(len(m.faces), bool); keep[list(drop)] = False
        log(f"{name}: non-manifold edge, dropped {len(drop)} sliver face(s) near {np.round(m.vertices[u[over[0]][0]], 1).tolist()}")
        m = trimesh.Trimesh(m.vertices, m.faces[keep], process=True); trimesh.repair.fix_normals(m); trimesh.repair.fill_holes(m)
    if not m.is_volume: log(f"{name}: WARNING still not a clean volume (watertight {m.is_watertight})")
    parts = m.split(only_watertight=False)
    keep = [p for p in parts if p.volume > 0]; dropped = len(parts) - len(keep)
    if dropped:
        log(f"{name}: dropped {dropped} enclosed void shell(s) (negative volume), the void is now solid")
        m = trimesh.util.concatenate(keep)
    return m


def manifold_ok(m):
    try:
        import manifold3d as M
        M.Manifold(M.Mesh(vert_properties=np.asarray(m.vertices, np.float32), tri_verts=np.asarray(m.faces, np.uint32)))
        return True
    except Exception:
        return False


def halfspace(m, ax, c, side):
    ext = m.extents.max() * 3
    size = np.full(3, ext); ctr = m.centroid.copy()
    ctr[ax] = c + side * ext / 2
    box = trimesh.creation.box(extents=size); box.apply_translation(ctr)
    return trimesh.boolean.intersection([m, box], engine="manifold")


def section_area(m, ax, c):
    n = np.zeros(3); n[ax] = 1; o = np.zeros(3); o[ax] = c
    s = m.section(plane_origin=o, plane_normal=n)
    if s is None: return 0.0
    p, _ = s.to_2D()
    return sum(g.area for g in p.polygons_full)


def pin_sites(m, ax, c):
    """Points (in 3D) and radius for pins on the cut plane: eroded section polygons, farthest-first, max 6 per island."""
    n = np.zeros(3); n[ax] = 1; o = np.zeros(3); o[ax] = c
    s = m.section(plane_origin=o, plane_normal=n)
    if s is None: return []
    p, T = s.to_2D()
    out = []
    for g in p.polygons_full:
        if g.area < 6: continue
        # inradius estimate: largest erosion that leaves something
        r = 0.0
        for e in (4.0, 3.0, 2.4, 1.8, 1.4, 1.0, 0.8):
            if not g.buffer(-(e + 0.35)).is_empty: r = e; break
        if r == 0: continue
        core = g.buffer(-(r + 0.35))
        pts = []
        geoms = list(core.geoms) if hasattr(core, "geoms") else [core]
        cand = []
        for q in geoms:
            minx, miny, maxx, maxy = q.bounds
            for x in np.arange(minx, maxx + 1e-6, 10.0):
                for y in np.arange(miny, maxy + 1e-6, 10.0):
                    if q.contains(Point(x, y)): cand.append((x, y))
            cand.append((q.representative_point().x, q.representative_point().y))
            rings = [q.exterior] + list(q.interiors)
            for rg in rings:
                for dist in np.arange(0, rg.length, 8.0):
                    pt = rg.interpolate(dist); cand.append((pt.x, pt.y))
        if not cand: continue
        pts = [cand[0]]
        maxn = 14 if r < 2 else 6
        spacing = 15 if r < 2 else 12
        while len(pts) < maxn and len(pts) < len(cand):
            far = max(cand, key=lambda c_: min((c_[0] - a[0]) ** 2 + (c_[1] - a[1]) ** 2 for a in pts))
            if min(math.hypot(far[0] - a[0], far[1] - a[1]) for a in pts) < spacing: break
            pts.append(far)
        for x, y in pts:
            P = T @ np.array([x, y, 0.0, 1.0])
            out.append((P[:3], r))
    return out


def cyl(P, ax, r, length, off):
    c = trimesh.creation.cylinder(radius=r, height=length, sections=24)
    R = np.eye(4)
    if ax == 0: R[:3, :3] = trimesh.transformations.rotation_matrix(math.pi / 2, [0, 1, 0])[:3, :3]
    if ax == 1: R[:3, :3] = trimesh.transformations.rotation_matrix(-math.pi / 2, [1, 0, 0])[:3, :3]
    c.apply_transform(R)
    d = np.zeros(3); d[ax] = off
    c.apply_translation(np.asarray(P) + d)
    return c


def split_part(m, name):
    """Return list of (suffix, mesh, info) pieces, each one cut at a low-section plane and joined by pins/holes."""
    ex = m.extents; order = np.argsort(-ex)
    ax = int(order[0])
    need = ex[ax] > ZMAX or ex[order[1]] > USABLE
    if not need: return [("", m, {})]
    L = ex[ax]; n = int(math.ceil(L / PIECE_TARGET)); lo = m.bounds[0][ax]
    cuts = []
    for i in range(1, n):
        ideal = lo + L * i / n; best = None
        for dc in np.linspace(-0.07 * L, 0.07 * L, 15):
            a = section_area(m, ax, ideal + dc)
            if best is None or a < best[0]: best = (a, ideal + dc)
        cuts.append(best[1])
    log(f"{name}: extents {np.round(ex).tolist()} -> {n} pieces along {'xyz'[ax]} at {[round(c, 1) for c in cuts]}")
    edges = [-1e9] + cuts + [1e9]
    pieces = []
    rest = m
    for i in range(n):
        p = m
        if i > 0: p = halfspace(p, ax, edges[i], +1)
        if i < n - 1: p = halfspace(p, ax, edges[i + 1], -1)
        pieces.append(p)
    # pins: piece i carries pins sticking toward i+1; piece i+1 gets holes
    info = [dict() for _ in pieces]
    for i, c in enumerate(cuts):
        sites = pin_sites(m, ax, c)
        if not sites:
            log(f"  cut {i + 1}: no section wide enough for a pin: butt joint, glue + external alignment"); continue
        for P, r in sites:
            pin = cyl(P, ax, r, PIN_L * 2, +PIN_L - 0.0)
            hole = cyl(P, ax, r + CLEAR, PIN_L * 2 + 0.6, +PIN_L + 0.3)
            pieces[i] = trimesh.boolean.union([pieces[i], pin], engine="manifold")
            pieces[i + 1] = trimesh.boolean.difference([pieces[i + 1], hole], engine="manifold")
        info[i]["pins_out"] = len(sites); info[i + 1]["holes_in"] = len(sites)
        log(f"  cut {i + 1}: {len(sites)} pins dia {[round(2 * r, 1) for _, r in sites][:6]}")
    return [("abcdefgh"[i], pieces[i], info[i]) for i in range(n)]


def rot_to_down(m, k):
    """k in 0..5: bring the +x,-x,+y,-y,+z,-z face down; returns rotated copy, 4x4."""
    dirs = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    T = trimesh.geometry.align_vectors(dirs[k], (0, 0, -1))
    r = m.copy(); r.apply_transform(T)
    return r, T


# Strength-first orientation (see print_strength_plan.md): these designs may only stand on the listed model-axis faces (0 +x, 1 -x, 2 +y, 3 -y, 4 +z, 5 -z),
# so the pivot / pin axis is vertical (round bores, continuous perimeters) and the load plane of the plates and links lies in the layer plane.
STRENGTH_FACES = {'SU1': (0, 1),     # front swing arm: plates flat, pivots vertical (was standing on its edge, in-plane bending across the layers)
                  'DT11': (0, 1),    # rear swing arm: same
                  'ST3': (4, 5)}     # tie rod: lies flat (was standing on its edge, 47 mm tall)
# Fixed print faces where the automatic choice was stale or poor (printability review 11-22): rear deck on its +y face (1752 mm2 overhang
# instead of 6292 on +x), front light contact block on its -z face (bed 289 mm2 instead of 1 mm2 on +z).
KIT_FACES = {'CH2': (2,), 'CG2': (5,)}


def best_orientation(m, name, allowed=None):
    import mesh_audit
    cands = []
    for k in (allowed if allowed else range(6)):
        r, T = rot_to_down(m, k)
        for spin in (0, 1):
            q = r.copy()
            if spin: q.apply_transform(trimesh.transformations.rotation_matrix(math.pi / 2, [0, 0, 1]))
            e = q.extents
            if max(e[:2]) > USABLE or e[2] > ZMAX: continue
            fp = e[0] * e[1]
            q.apply_translation(-q.bounds[0])
            oh = mesh_audit.overhang(q)
            # contact patch: area of faces lying on the bed
            bed = float(q.area_faces[(q.face_normals[:, 2] < -0.99) & (q.triangles_center[:, 2] < 0.3)].sum())
            tall = max(0.0, e[2] / math.sqrt(max(fp, 1.0)) - 2.0) * 1500
            score = oh * 1.0 + tall - 2.0 * bed
            cands.append((score, k, spin, q, oh, bed))
            break  # first spin that fits is enough
    if not cands: raise SystemExit(f"{name}: no orientation fits the bed")
    cands.sort(key=lambda c: c[0])
    best = None
    for c in cands[:3]:
        fl = mesh_audit.floating(c[3]) if c[3].volume > 0 else 0.0
        sc = c[0] + 3.0 * fl
        if best is None or sc < best[0]: best = (sc, c, fl)
    c = best[1]
    return (best[0],) + c[1:] + (best[2],)


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("stl_dir"); ap.add_argument("--out", default=os.path.join(HERE, "print"))
    ap.add_argument("--no-polish", action="store_true", help="skip the shell-part mesh polish (polish_stls.py)")
    a = ap.parse_args()
    out = a.out; os.makedirs(out + "/stl", exist_ok=True)
    stems = sorted(os.path.basename(f)[:-4] for f in glob.glob(a.stl_dir + "/*.stl"))
    skipped, unknown = [], []
    parts_json = []
    import mesh_audit
    for stem in stems:
        did = key_of(stem)
        if did is None and is_hardware(stem): skipped.append(stem); continue      # a printed stem wins over a hardware prefix
        if not did: unknown.append(stem); log("skip", stem); continue
        d = next(p for p in PARTS if p["id"] == did)
        side = "" if not d.get("mirrored") else ("L" if stem.endswith("_-1") else "R")
        m = repair(trimesh.load(os.path.join(a.stl_dir, stem + ".stl"), process=False), stem)
        if not manifold_ok(m):
            log(f"{stem}: still not manifold after repair; trying vertex merge at 1e-3")
            m.merge_vertices(merge_tex=True, merge_norm=True, digits_vertex=3); trimesh.repair.fill_holes(m)
        if not a.no_polish and stem in polish_stls.SHELL_STEMS:   # print-mesh cleanup only; the CAD is unchanged (decision E3)
            m, rep = polish_stls.polish_part(m)
            b, af = rep.get("before", {}), rep.get("after", {})
            log(f"{stem}: polish {'accepted' if rep['accepted'] else 'KEPT ORIGINAL (' + str(rep.get('error', 'checks failed: dvol %s%%' % rep.get('dvol_pct')) ) + ')'}; faces {b.get('faces')} -> {af.get('faces')}, "
                f"tri <0.05 mm2 {b.get('area_lt_0.05mm2')} -> {af.get('area_lt_0.05mm2')}, dvol {rep.get('dvol_pct')} %")
        pieces = []
        for suf, pm, info in split_part(m, stem):
            _all = pm.split(only_watertight=False)
            bodies = [b for b in _all if b.volume >= 2.0]
            _dust = [b for b in _all if 0 < b.volume < 2.0]
            if _dust and bodies:        # shards (< 2 mm3) left by the split cut: not printable features, dropped
                log(f"{stem}{suf}: dropped {len(_dust)} sub-2 mm3 shard(s) left by the split cut, largest {max(b.volume for b in _dust):.2f} mm3")
                pm = bodies[0] if len(bodies) == 1 else trimesh.util.concatenate(bodies)
            if len(bodies) > 1:
                log(f"{stem}{suf}: {len(bodies)} separate bodies (e.g. left/right sides) -> printed as separate files")
                pieces += [(suf + str(i + 1), b, info) for i, b in enumerate(bodies)]
            else:
                pieces.append((suf, pm, info))
        for _i, (suf, pm, info) in enumerate(pieces):        # a split cut can leave a hairline crack (2 edges): weld and fill it
            if not pm.is_watertight:
                _v0 = pm.volume
                for _dig in (3, 2):
                    _q = pm.copy(); _q.merge_vertices(merge_tex=True, merge_norm=True, digits_vertex=_dig); _q.update_faces(_q.nondegenerate_faces()); _q.remove_unreferenced_vertices()
                    trimesh.repair.fill_holes(_q); trimesh.repair.fix_normals(_q)
                    if _q.is_watertight and abs(_q.volume - _v0) < 0.001 * abs(_v0): pm = _q; break
                log(f"{stem}{suf}: split piece was not watertight; {'welded and closed' if pm.is_watertight else 'STILL OPEN'}")
                pieces[_i] = (suf, pm, info)
        for suf, pm, info in pieces:
            pid = f"{did}{side}{suf}"
            score, k, spin, q, oh, bed, fl = best_orientation(pm, pid, STRENGTH_FACES.get(did) or KIT_FACES.get(did))
            # STL stores float32: round to it first, then weld, so what is written is the mesh that is checked (a split-cut hairline can open up on rounding)
            _q = q.copy(); _q.vertices = _q.vertices.astype(np.float32).astype(np.float64)
            _q.merge_vertices(merge_tex=True, merge_norm=True, digits_vertex=4); _q.update_faces(_q.nondegenerate_faces()); _q.remove_unreferenced_vertices()
            if not _q.is_watertight: trimesh.repair.fill_holes(_q)
            if _q.is_watertight and abs(_q.volume - q.volume) < 0.001 * abs(q.volume): q = _q
            else: log(f"{pid}: WARNING float32-rounded mesh not clean (watertight {_q.is_watertight})")
            q.export(f"{out}/stl/{pid}.stl")
            parts_json.append(dict(id=pid, design=did, stem=stem, name=d["name"] + (f" ({side})" if side else "") + (f" piece {suf.upper()}" if suf else ""),
                                   material=d["material"], sub=d["sub"], walls=d["walls"], infill=d["infill"], support=d["support"],
                                   extents=[round(float(x), 1) for x in q.extents], volume_cm3=round(float(q.volume) / 1000, 2), overhang_mm2=round(oh, 1),
                                   floating_mm2=round(float(fl), 2), bed_contact_mm2=round(bed, 1), orient_face=k, spin=spin, pieces_info=info))
            log(f"{pid}: {np.round(q.extents).tolist()} overhang {oh:.0f} floating {fl:.1f} vol {q.volume / 1000:.1f} cm3")
    json.dump(dict(parts=parts_json, skipped_hardware=skipped, unknown=unknown, log=LOG), open(out + "/parts.json", "w"), indent=1)
    if unknown:
        print("FAIL: unknown stems", unknown); sys.exit(1)
    # every registry design must have been exported
    got = {p["design"] for p in parts_json}
    missing = [p["id"] for p in PARTS if p["id"] not in got and not p.get("optional")]   # optional: only built with a model switch (SH2 canopy: OPEN_COCKPIT off)
    if missing: print("FAIL: registry designs without STL:", missing); sys.exit(1)
    print("OK", len(parts_json), "printed files")


if __name__ == "__main__":
    main()
