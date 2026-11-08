"""WS-03 print preparation for the Bambu Lab P2S (256 x 256 x 256 mm, 0.4 mm nozzle).

One command regenerates everything from the current STLs (out/stl, out/mono3):
    python print_prep.py            # analyse, orient, split, nest, write out/print/plate_NN.3mf, PRINT_PLAN.md, overview.png
    python print_prep.py --rebuild  # first re-run build.py / body3_build.py / split_shell3.py (slow)
    python print_prep.py --only w3_deck_front,w3_pod

Nothing here edits part geometry files.  Geometry change requests are only listed in PRINT_PLAN.md.
"""
import argparse
import json
import math
import re
import sys
import zipfile
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import trimesh
from scipy.spatial import ConvexHull
from shapely.affinity import rotate as sh_rotate, translate as sh_translate
from shapely.geometry import MultiPoint, box

import print_checks as PC

OUT = Path("out/print")
STL = Path("out/stl")
MONO = Path("out/mono3")
SKIN_PIECES = ["body3_front", "body3_mid", "body3_rear"]          # current skin split (split_shell3.py)

# ---- printer: Bambu Lab P2S ------------------------------------------------------------------------------------------------
BED = (256.0, 256.0)
MAX_Z = 250.0                  # printable height used here (256 nominal, minus a safety margin)
EDGE = 4.0                     # keep parts this far from the plate edge
SPACING = 6.0                  # between parts
# Bambu's X1/P1 profiles exclude an 18 x 28 mm corner (front left) for the nozzle wipe/purge; the P2S figure could not be found
# in the public pages, so the same corner is assumed and widened a little.  Usable plate = 248 x 248 minus that corner.
EXCLUDE = (0.0, 0.0, 22.0, 32.0)

DENS = {"PETG": 1.27, "PETG-CF": 1.30}
FLOW = {"PETG": 10.0, "PETG-CF": 8.0}      # mm3/s achieved on average (volumetric limit, many small features)
OVERHEAD = 1.35                            # travel, retraction, layer changes, acceleration


# ---- per-part print recipe ------------------------------------------------------------------------------------------------
@dataclass
class Recipe:
    material: str = "PETG"
    layer: float = 0.2
    walls: int = 3
    infill: int = 25
    top: int = 5
    bottom: int = 4
    colour: str = "black"
    note: str = ""
    qty: int = 1


def recipe_for(name):
    n = name.replace("w3_", "")
    R = Recipe
    rules = [
        (r"^body3_", R("PETG", 0.2, 3, 15, 4, 4, "body", "skin: 2.4 mm walls are nearly all perimeters; infill barely matters")),
        (r"^frame_", R("PETG-CF", 0.2, 4, 40, 5, 5, "black", "welded tube cage: tubes are solid, perimeters 4; stiff + heat from the motor")),
        (r"^rear_arm", R("PETG-CF", 0.2, 4, 50, 5, 5, "black", "swing arm with shock hoop and belt run; 50 % where the hoop and lug load it")),
        (r"^arm_(left|right)", R("PETG-CF", 0.2, 4, 45, 5, 5, "black", "lean/steer front arms: highest bending load in the front end")),
        (r"^(fdc|cdc|rbc)_", R("PETG-CF", 0.16, 4, 40, 6, 6, "black", "gear housing halves: 0.16 mm for the 5x11x4 bearing seats, CF keeps them stiff when warm")),
        (r"^motor_plate", R("PETG-CF", 0.2, 4, 50, 6, 6, "black", "motor mount: heat and screw pull-out, solid-ish")),
        (r"^tail_hanger", R("PETG-CF", 0.2, 4, 50, 5, 5, "black", "wing hanger: prongs print flat so layers run along the prong; mostly solid")),
        (r"^(tail_main|tail_right)", R("PETG", 0.2, 3, 20, 5, 5, "body", "wing blade: thin aerofoil, flat on the bed")),
        (r"^deck_", R("PETG", 0.2, 3, 25, 5, 5, "black", "deck plates: flat, layers in the plane of the load")),
        (r"^(carrier|knuckle)_", R("PETG-CF", 0.2, 4, 45, 5, 5, "black", "steering carrier/knuckle: stub axle + bearing loads")),
        (r"^(lean_tower|lean_rocker|uplink_(left|right))", R("PETG", 0.2, 4, 45, 5, 5, "black", "lean linkage part: small, dense")),
        (r"^(tie_rod)", R("PETG", 0.2, 4, 100, 5, 5, "black", "round tube link: print along its axis, solid; qty 2", qty=2)),
        (r"^pod", R("PETG", 0.2, 4, 40, 5, 5, "black", "qty 2 (one per side)", qty=2)),
        (r"^uplink_standoff", R("PETG", 0.2, 4, 100, 5, 5, "black", "tiny spacer, qty 2", qty=2)),
        (r"^(batt_tray|battery_tray|esc_tray|skid)", R("PETG", 0.2, 3, 25, 4, 4, "black", "tray/skid: strap slots and screw bosses")),
    ]
    for pat, rec in rules:
        if re.search(pat, n):
            return rec
    return R()


# ---- part catalogue ----------------------------------------------------------------------------------------------------------
def catalogue():
    """(name, path) for every printed part + skin pieces.  Returns (found, missing, orphans)."""
    names = []
    try:
        import w3_parts
        names = [p.name for p in w3_parts.all_parts()]
    except Exception as e:                                       # fall back to the files themselves
        print("w3_parts.all_parts() failed:", repr(e)[:120], "- using out/stl/w3_*.stl")
        names = sorted(p.stem for p in STL.glob("w3_*.stl"))
    found, missing = [], []
    for n in names:
        (found if (STL / f"{n}.stl").exists() else missing).append((n, STL / f"{n}.stl"))
    for n in SKIN_PIECES:
        (found if (MONO / f"{n}.stl").exists() else missing).append((n, MONO / f"{n}.stl"))
    known = {n for n, _ in found + missing}
    orphans = sorted(p.stem for p in STL.glob("w3_*.stl") if p.stem not in known)
    return found, missing, orphans


# ---- orientation ----------------------------------------------------------------------------------------------------------------
def _dedupe(dirs, deg=6.0):
    out = []
    c = math.cos(math.radians(deg))
    for d in dirs:
        d = np.asarray(d, float)
        d = d / np.linalg.norm(d)
        if not any(float(d @ o) > c for o in out):
            out.append(d)
    return out


def candidates(m):
    """Up-directions to try: axes, big flat faces (as the bottom), hull faces, tilts about the long axis."""
    dirs = [v * s for v in np.eye(3) for s in (1, -1)]
    if len(m.facets):
        order = np.argsort(-m.facets_area)[:14]
        dirs += [-m.facets_normal[i] for i in order if m.facets_area[i] >= 20.0]
    try:
        h = m.convex_hull
        order = np.argsort(-h.facets_area)[:10]
        dirs += [-h.facets_normal[i] for i in order]
    except Exception:
        pass
    pv, ext = principal(m)
    lax = pv[int(np.argmax(ext))]
    if ext.max() / max(sorted(ext)[1], 1e-6) > 1.4:
        for base in (np.array([0, 0, 1.0]), np.array([0, 0, -1.0])):
            for a in (-45, -30, -15, 15, 30, 45):
                dirs.append(trimesh.transformations.rotation_matrix(math.radians(a), lax)[:3, :3] @ base)
    return _dedupe(dirs)


def principal(m):
    try:
        pv = np.asarray(m.principal_inertia_vectors)
    except Exception:
        pv = np.eye(3)
    ext = np.array([np.ptp(m.vertices @ v) for v in pv])
    return pv, ext


def up_to_matrix(up):
    T = trimesh.geometry.align_vectors(up, [0, 0, 1])
    return np.asarray(T, float)


def min_rect(points2d):
    """Rotation angle (deg) about z that minimises the bounding rectangle of the footprint, long side along x."""
    try:
        h = points2d[ConvexHull(points2d).vertices]
    except Exception:
        return 0.0
    best, ang = None, 0.0
    e = np.diff(np.vstack([h, h[:1]]), axis=0)
    for a in np.arctan2(e[:, 1], e[:, 0]):
        c, s = math.cos(-a), math.sin(-a)
        r = h @ np.array([[c, -s], [s, c]]).T
        w, d = np.ptp(r[:, 0]), np.ptp(r[:, 1])
        if best is None or w * d < best[0] - 1e-6:
            best = (w * d, math.degrees(a) + (90.0 if d > w else 0.0))
    return -best[1]


def orient_mesh(m, up):
    """Rotate so `up` is +Z, rotate about Z to the smallest footprint rectangle, drop onto z = 0 and centre xy at the origin."""
    T = up_to_matrix(up)
    mm = m.copy()
    mm.apply_transform(T)
    a = min_rect(mm.vertices[:, :2])
    Rz = trimesh.transformations.rotation_matrix(math.radians(a), [0, 0, 1])
    mm.apply_transform(Rz)
    T = Rz @ T
    lo, hi = mm.bounds
    shift = np.array([-(lo[0] + hi[0]) / 2, -(lo[1] + hi[1]) / 2, -lo[2]])
    mm.apply_translation(shift)
    S = np.eye(4)
    S[:3, 3] = shift
    return mm, S @ T


def overhang_stats(m, thresh_deg=45.0, bed_eps=0.15):
    """Overhang area beyond thresh (excluding faces on the bed), bed contact area, per-face mask."""
    nz = m.face_normals[:, 2]
    zc = m.triangles_center[:, 2]
    zmin = m.bounds[0][2]
    on_bed = (zc - zmin < bed_eps) & (nz < -0.9)
    ovh = (nz < -math.cos(math.radians(thresh_deg))) & ~on_bed
    return float(m.area_faces[ovh].sum()), float(m.area_faces[on_bed].sum()), ovh


def support_estimate(m, ovh, n=900, seed=1):
    """Support volume by dropping vertical rays from sampled overhang faces to whatever is below (or the bed)."""
    idx = np.where(ovh)[0]
    if len(idx) == 0:
        return dict(volume=0.0, bed_frac=1.0, mean_gap=0.0, area_proj=0.0)
    w = m.area_faces[idx] * np.abs(m.face_normals[idx, 2])
    rng = np.random.default_rng(seed)
    pick = rng.choice(idx, size=min(n, len(idx) * 3), p=w / w.sum())
    tri = m.triangles[pick]
    r = rng.random((len(pick), 2))
    flip = r.sum(1) > 1
    r[flip] = 1 - r[flip]
    pts = tri[:, 0] + r[:, :1] * (tri[:, 1] - tri[:, 0]) + r[:, 1:] * (tri[:, 2] - tri[:, 0])
    o = pts + np.array([0, 0, -1e-3])
    d = np.tile([0.0, 0.0, -1.0], (len(pts), 1))
    loc, ri, _ = m.ray.intersects_location(o, d, multiple_hits=False)
    gap = pts[:, 2] - m.bounds[0][2]                 # default: down to the bed
    hit = np.zeros(len(pts), bool)
    if len(ri):
        gap[ri] = pts[ri, 2] - np.asarray(loc)[:, 2]
        hit[ri] = True
    keep = gap > 0.4
    proj = float(w.sum())
    mean_gap = float(gap[keep].sum() / len(gap))      # tiny steps count as zero
    return dict(volume=proj * mean_gap, bed_frac=float(1.0 - hit[keep].mean()) if keep.any() else 1.0,
                mean_gap=mean_gap, area_proj=proj)


def stage1(m, up, pv, ext):
    T = up_to_matrix(up)
    N = m.face_normals @ T[:3, :3].T
    zc = m.triangles_center @ T[2, :3]
    zv = m.vertices @ T[2, :3]
    H = float(np.ptp(zv))
    zmin = float(zv.min())
    on_bed = (zc - zmin < 0.15) & (N[:, 2] < -0.9)
    ovh = (N[:, 2] < -0.7071) & ~on_bed
    A = float(m.area)
    ovh_frac = float(m.area_faces[ovh].sum() / A)
    flat = float(m.area_faces[on_bed].sum())
    lax = pv[int(np.argmax(ext))]
    srt = np.sort(ext)
    elong = srt[2] / max(srt[1], 1e-6)
    layer = abs(float(lax @ up)) if elong >= 2.5 else 0.0
    cost = (2.0 * ovh_frac + 0.6 * (1 - min(1.0, flat / 150.0)) + 0.6 * H / MAX_Z + 1.5 * layer + (6.0 if H > MAX_Z else 0.0))
    return cost, dict(ovh_frac=ovh_frac, flat=flat, H=H, layer=layer)


def fits_plate(m):
    w, d = np.ptp(m.vertices[:, 0]), np.ptp(m.vertices[:, 1])
    ux, uy = BED[0] - 2 * EDGE, BED[1] - 2 * EDGE
    return (w <= ux and d <= uy) or (w <= uy and d <= ux)


def choose_orientation(m):
    pv, ext = principal(m)
    cands = candidates(m)
    ranked = sorted(((stage1(m, u, pv, ext), u) for u in cands), key=lambda t: t[0][0])
    scored = []
    for (c1, info), u in ranked[:14]:
        if len(scored) >= 4 and c1 > scored[0][0] + 3:
            break
        om, T = orient_mesh(m, u)
        if not fits_plate(om) or np.ptp(om.vertices[:, 2]) > MAX_Z:
            continue
        a_ovh, a_flat, ovh = overhang_stats(om)
        sup = support_estimate(om, ovh)
        V = max(abs(m.volume), 2000.0)
        hull_a = float(MultiPoint(om.vertices[:, :2]).convex_hull.area)
        cost = (3.0 * sup["volume"] / V + 2.0 * a_ovh / m.area + 0.6 * (1 - min(1.0, a_flat / 150.0))
                + 0.6 * info["H"] / MAX_Z + 1.5 * info["layer"] + 0.3 * info["H"] / math.sqrt(max(hull_a, 1.0)))
        scored.append((cost, u, T, om, dict(info, ovh_area=a_ovh, flat=a_flat, sup=sup, hull_area=hull_a)))
    if not scored:
        return None
    scored.sort(key=lambda t: t[0])
    return scored[0], len(cands)


# ---- splitting ----------------------------------------------------------------------------------------------------------------------
def _manifold(m):
    from manifold3d import Manifold, Mesh
    return Manifold(Mesh(np.asarray(m.vertices, np.float32), np.asarray(m.faces, np.uint32)))


def _tm(man):
    mesh = man.to_mesh()
    return trimesh.Trimesh(np.asarray(mesh.vert_properties)[:, :3].copy(), np.asarray(mesh.tri_verts).copy(), process=True)


def propose_split(m, peg_d=4.0, peg_len=6.0, fit=0.2):
    """Cut across the longest axis at the thinnest-section position near the middle; add alignment pegs and holes.

    Returns (piece_a, piece_b, info)."""
    from manifold3d import Manifold
    ext = m.extents
    ax = int(np.argmax(ext))
    nrm = np.eye(3)[ax]
    lo, hi = m.bounds[0][ax], m.bounds[1][ax]
    best = None
    for f in np.linspace(0.38, 0.62, 13):
        pos = lo + (hi - lo) * f
        sec = m.section(plane_origin=nrm * pos, plane_normal=nrm)
        if sec is None:
            continue
        try:
            p2, T = sec.to_2D()
            area = sum(p.area for p in p2.polygons_full)
        except Exception:
            continue
        if best is None or area < best[0]:
            best = (area, pos, p2, T)
    if best is None:
        pos = (lo + hi) / 2
        pegs = []
    else:
        area, pos, p2, T = best
        pegs = []
        polys = sorted(p2.polygons_full, key=lambda p: -p.area)
        if polys:
            inner = polys[0].buffer(-(peg_d / 2 + 1.5))
            if not inner.is_empty:
                g = inner if inner.geom_type == "Polygon" else max(inner.geoms, key=lambda q: q.area)
                x0, y0, x1, y1 = g.bounds
                trial = [g.representative_point().coords[0]]
                trial += [((x0 * 3 + x1) / 4, (y0 + y1) / 2), ((x0 + x1 * 3) / 4, (y0 + y1) / 2), ((x0 + x1) / 2, (y0 * 3 + y1) / 4), ((x0 + x1) / 2, (y0 + y1 * 3) / 4)]
                from shapely.geometry import Point
                for p in trial:
                    if g.contains(Point(p)) and all(math.dist(p, q) > 3 * peg_d for q in pegs):
                        pegs.append(p)
                    if len(pegs) == 3:
                        break
                pegs = [tuple((T @ np.array([p[0], p[1], 0, 1.0]))[:3]) for p in pegs]
    M = _manifold(m)
    big = 1000.0
    off = np.zeros(3)
    off[ax] = pos
    def half(sign):
        b = Manifold.cube((big, big, big), center=True)
        t = np.zeros(3)
        t[ax] = sign * big / 2
        return M ^ b.translate(tuple(off + t))
    A, B = half(-1), half(+1)
    rot = {0: (0.0, 90.0, 0.0), 1: (-90.0, 0.0, 0.0), 2: (0.0, 0.0, 0.0)}[ax]
    for p in pegs:
        c = np.array(p, float)
        pg = Manifold.cylinder(peg_len, peg_d / 2, peg_d / 2, 32).rotate(rot).translate(tuple(c))
        hole = Manifold.cylinder(peg_len + 0.4, (peg_d + 2 * fit) / 2, (peg_d + 2 * fit) / 2, 32).rotate(rot).translate(tuple(c - nrm * 0.0))
        A = A + pg                              # peg on the low side points to +axis
        B = B - hole
    ma, mb = _tm(A), _tm(B)
    return ma, mb, dict(axis="xyz"[ax], pos=float(pos), pegs=len(pegs), peg_d=peg_d, peg_len=peg_len, fit=fit, section_area=float(best[0]) if best else None)


# ---- plate nesting -----------------------------------------------------------------------------------------------------------------
@dataclass
class Item:
    name: str
    inst: int
    mesh: object                 # oriented mesh (z >= 0, centred on xy origin)
    recipe: Recipe
    info: dict = field(default_factory=dict)
    foot: object = None          # shapely footprint polygon
    T: object = None             # 4x4 transform original -> oriented


REGION = box(EDGE - SPACING / 2, EDGE - SPACING / 2, BED[0] - EDGE + SPACING / 2, BED[1] - EDGE + SPACING / 2)
EXCL = box(*EXCLUDE)


def footprint(mesh):
    return MultiPoint(mesh.vertices[:, :2]).convex_hull


def nest(items, step=3.0):
    """Greedy bottom-left placement of convex-hull footprints (buffered by half the spacing).  Groups never mix.

    Returns list of plates: dict(key, placed=[(item, rot_deg, (dx, dy), polygon)])."""
    groups = {}
    for it in items:
        k = (it.recipe.material, it.recipe.layer, it.recipe.colour)
        groups.setdefault(k, []).append(it)
    plates = []
    for key in sorted(groups):
        its = sorted(groups[key], key=lambda i: -i.foot.area)
        mine = []
        for it in its:
            done = False
            for pl in mine:
                if _try_place(pl, it, step):
                    done = True
                    break
            if not done:
                pl = dict(key=key, placed=[])
                if not _try_place(pl, it, step):
                    raise RuntimeError(f"{it.name} does not fit an empty plate")
                mine.append(pl)
        plates += mine
    return plates


def _try_place(pl, it, step):
    base = it.foot
    for rot in (0, 90, 180, 270):
        poly = sh_rotate(base, rot, origin=(0, 0))
        poly = poly.buffer(SPACING / 2, join_style=2)
        x0, y0, x1, y1 = poly.bounds
        w, h = x1 - x0, y1 - y0
        xs = np.arange(REGION.bounds[0], REGION.bounds[2] - w + 1e-6, step)
        ys = np.arange(REGION.bounds[1], REGION.bounds[3] - h + 1e-6, step)
        for y in ys:
            for x in xs:
                cand = sh_translate(poly, x - x0, y - y0)
                if cand.intersects(EXCL) and cand.intersection(EXCL).area > 1e-6:
                    continue
                if any(cand.bounds[0] < o[3].bounds[2] and cand.bounds[2] > o[3].bounds[0] and cand.bounds[1] < o[3].bounds[3]
                       and cand.bounds[3] > o[3].bounds[1] and cand.intersection(o[3]).area > 1e-6 for o in pl["placed"]):
                    continue
                pl["placed"].append((it, rot, (x - x0, y - y0), cand))
                return True
    return False


def placed_mesh(it, rot, shift):
    m = it.mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(math.radians(rot), [0, 0, 1]))
    m.apply_translation((shift[0], shift[1], 0.0))
    return m


# ---- 3MF ----------------------------------------------------------------------------------------------------------------------------
def write_3mf(path, objs, settings):
    """objs: list of (name, trimesh in plate coordinates).  Minimal 3MF + Bambu per-object settings."""
    ns = "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"
    xml = ['<?xml version="1.0" encoding="UTF-8"?>', f'<model unit="millimeter" xml:lang="en-US" xmlns="{ns}">',
           '<metadata name="Application">print_prep.py (WS03)</metadata><resources>']
    cfg = ['<?xml version="1.0" encoding="UTF-8"?>', "<config>"]
    for i, (name, m) in enumerate(objs, 1):
        xml.append(f'<object id="{i}" name="{name}" type="model"><mesh><vertices>')
        xml += [f'<vertex x="{v[0]:.4f}" y="{v[1]:.4f}" z="{v[2]:.4f}"/>' for v in m.vertices]
        xml.append("</vertices><triangles>")
        xml += [f'<triangle v1="{f[0]}" v2="{f[1]}" v3="{f[2]}"/>' for f in m.faces]
        xml.append("</triangles></mesh></object>")
        cfg.append(f'<object id="{i}"><metadata key="name" value="{name}"/>')
        for k, v in settings[i - 1].items():
            cfg.append(f'<metadata key="{k}" value="{v}"/>')
        cfg.append(f'<part id="1" subtype="normal_part"><metadata key="name" value="{name}"/></part></object>')
    xml.append("</resources><build>")
    xml += [f'<item objectid="{i}"/>' for i in range(1, len(objs) + 1)]
    xml.append("</build></model>")
    cfg.append('<plate><metadata key="plater_id" value="1"/>')
    cfg += [f'<model_instance><metadata key="object_id" value="{i}"/><metadata key="instance_id" value="0"/></model_instance>' for i in range(1, len(objs) + 1)]
    cfg.append("</plate></config>")
    ct = ('<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>'
          '<Default Extension="config" ContentType="text/xml"/></Types>')
    rels = ('<?xml version="1.0" encoding="UTF-8"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Target="/3D/3dmodel.model" Id="rel0" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/></Relationships>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("3D/3dmodel.model", "\n".join(xml))
        z.writestr("Metadata/model_settings.config", "\n".join(cfg))


def read_3mf_objects(path):
    """Read back (name, vertices, faces) with the stdlib only (trimesh needs lxml for 3MF)."""
    import xml.etree.ElementTree as ET
    with zipfile.ZipFile(path) as z:
        root = ET.fromstring(z.read("3D/3dmodel.model"))
    ns = {"m": "http://schemas.microsoft.com/3dmanufacturing/core/2015/02"}
    out = []
    for o in root.findall(".//m:object", ns):
        v = np.array([[float(x.get(k)) for k in "xyz"] for x in o.findall(".//m:vertex", ns)])
        f = np.array([[int(t.get(k)) for k in ("v1", "v2", "v3")] for t in o.findall(".//m:triangle", ns)])
        out.append((o.get("name"), v, f))
    return out


# ---- estimates -----------------------------------------------------------------------------------------------------------------------
def estimate(m, rec, sup_vol):
    """Mass (g) and time (h): perimeter/top/bottom shell + sparse infill + supports at 15 % density."""
    V = abs(float(m.volume))
    t_shell = rec.walls * 0.42 + 0.35                       # side walls plus a share of the top/bottom skins
    shell = min(V, float(m.area) * t_shell * 0.55)
    infill = max(0.0, V - shell) * rec.infill / 100.0
    part_v = shell + infill
    sup_v = sup_vol * 0.15
    mass = (part_v + sup_v) * DENS[rec.material] / 1000.0
    hours = (part_v + sup_v) / FLOW[rec.material] * OVERHEAD / 3600.0
    return dict(mass_g=mass, hours=hours, part_v=part_v, sup_v=sup_v)


def support_recipe(it, sup):
    """Strategy string for one part from the oriented analysis."""
    rec = it.recipe
    zgap = 0.2 if rec.material == "PETG-CF" else 0.25
    vol = sup["volume"]
    if vol < 60:
        return dict(kind="none", text="none (overhangs < 45 deg or bridges under 10 mm)", zgap=zgap)
    organic = it.info.get("truss", False)
    plate_only = sup["bed_frac"] > 0.85
    kind = "tree (slim)" if organic else "normal (snug)"
    where = "build plate only" if plate_only else "everywhere (supports land on part faces)"
    text = f"{kind}, {where}, threshold 45 deg"
    return dict(kind=kind, text=text, zgap=zgap, plate_only=plate_only)


def is_truss(m):
    """Many thin tubes: low volume against the hull volume."""
    try:
        return abs(m.volume) / max(m.convex_hull.volume, 1.0) < 0.2
    except Exception:
        return False


# ---- geometry suggestions -------------------------------------------------------------------------------------------------------------
def suggestions(it, holes):
    """Geometry changes that would remove supports or fix fit; the part files themselves are not touched."""
    out = []
    om = it.mesh
    nz = om.face_normals[:, 2]
    _, _, ovh = overhang_stats(om)
    idx = np.where(ovh)[0]
    if len(idx):
        import networkx as nx
        g = nx.Graph()
        g.add_nodes_from(idx.tolist())
        sub = {int(i) for i in idx}
        for a, b in om.face_adjacency:
            if int(a) in sub and int(b) in sub:
                g.add_edge(int(a), int(b))
        comps = sorted(nx.connected_components(g), key=lambda c: -om.area_faces[list(c)].sum())[:3]
        for c in comps:
            f = list(c)
            area = float(om.area_faces[f].sum())
            if area < 25:
                continue
            ctr = om.triangles_center[f].mean(0)
            flat = float(np.mean(nz[f]) < -0.95)
            ext = np.ptp(om.vertices[np.unique(om.faces[f])], axis=0)
            how = ("flat underside: add a 45 deg chamfer to the underside edge, or if it is a hole roof turn it into a teardrop/diamond"
                   if flat else "sloped underside: steepen to 45 deg or more (chamfer instead of a horizontal step)")
            out.append(f"{it.name}: overhang {area:.0f} mm2 near x{ctr[0]:+.0f} y{ctr[1]:+.0f} z{ctr[2]:.0f} in print frame ({ext[0]:.0f}x{ext[1]:.0f}x{ext[2]:.0f}): {how}")
    R = it.T[:3, :3]
    for h in holes:
        ax = R @ np.array(h["axis"])
        if h["kind"] == "hole" and abs(ax[2]) < 0.3 and h["dia"] >= 4.0 and h["cover"] >= 260:
            out.append(f"{it.name}: horizontal hole d{h['dia']:.1f} ({h['class'] or 'unclassified'}) at {h['centre']}: teardrop top (point up, 45 deg) saves its support")
        if h["kind"] == "peg" and abs(ax[2]) < 0.3 and h["length"] > 2.5 * h["dia"]:
            out.append(f"{it.name}: sideways peg d{h['dia']:.1f} x {h['length']:.1f} mm at {h['centre']}: unsupported overhang; add a 45 deg gusset or print the peg upright")
    return out


# ---- driver --------------------------------------------------------------------------------------------------------------------------------
def rebuild():
    import build, body3_build, split_shell3
    build.main()
    body3_build.main()
    split_shell3.main()


def analyse(only=None):
    found, missing, orphans = catalogue()
    rows, items, failed = [], [], []
    for name, path in found:
        if only and name not in only:
            continue
        try:
            m0 = trimesh.load(path, force="mesh")
            topo = PC.topology(m0)
            fixed = []
            if topo["problems"]:
                m0, fixed = PC.repair(m0)
                topo2 = PC.topology(m0)
            else:
                topo2 = topo
            rec = recipe_for(name)
            split = None
            ch = choose_orientation(m0)
            pieces = [(name, m0)]
            if ch is None:                                         # does not fit any way up: split it
                a, b, split = propose_split(m0)
                pieces = [(name + "_A", a), (name + "_B", b)]
            for pn, pm in pieces:
                c = choose_orientation(pm) if pm is not m0 or ch is None else ch
                if c is None:
                    raise RuntimeError("no orientation fits even after the split")
                (cost, up, T, om, info), ncand = c
                th = PC.thickness_profile(pm)
                holes = PC.hole_report(pm)
                it = Item(pn, 0, om, rec, info, footprint(om), T)
                info["truss"] = is_truss(pm)
                sup = info["sup"]
                est = estimate(om, rec, sup["volume"])
                srec = support_recipe(it, sup)
                row = dict(name=pn, source=name, path=str(path), qty=rec.qty, material=rec.material, layer=rec.layer, walls=rec.walls,
                           infill=rec.infill, top=rec.top, bottom=rec.bottom, colour=rec.colour, note=rec.note,
                           bbox=np.round(om.extents, 1).tolist(), height=round(info["H"], 1), cost=round(cost, 3),
                           ncand=ncand, up=np.round(up, 3).tolist(), T=T.tolist(), flat_mm2=round(info["flat"], 1),
                           overhang_pct=round(100 * info["ovh_area"] / om.area, 1), support_mm3=round(sup["volume"]),
                           support_bed_frac=round(sup["bed_frac"], 2), layer_axis=round(info["layer"], 2),
                           mass_g=round(est["mass_g"], 1), hours=round(est["hours"], 2), volume_cm3=round(abs(pm.volume) / 1000, 1),
                           support=srec, topo=topo, topo_after=topo2, repaired=fixed, thickness=th,
                           holes=holes, split=split, fits_unsplit=split is None, truss=info["truss"])
                row["suggestions"] = suggestions(it, holes)
                row["pegs"] = [h for h in PC.peg_report(holes)]
                rows.append(row)
                for k in range(rec.qty):
                    items.append(Item(pn, k, om, rec, info, it.foot, T))
        except Exception as e:
            failed.append((name, repr(e)[:200]))
            print("FAILED", name, repr(e)[:200])
    return rows, items, failed, missing, orphans


def strength_note(r):
    n = r["note"]
    lay = r["layer_axis"]
    bits = [n] if n else []
    if r["truss"]:
        bits.append("truss: tubes in many directions, so one orientation cannot align them all; long axis kept in the XY plane" if lay < 0.3 else "truss with long axis tilted: check layer lines")
    elif lay < 0.3:
        bits.append("long axis in the bed plane: layers run across the load path")
    else:
        bits.append(f"long axis tilted {math.degrees(math.acos(min(1.0, lay))):.0f} deg from vertical: weak across layers")
    return "; ".join(bits)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--rebuild", action="store_true")
    ap.add_argument("--only", default="")
    a = ap.parse_args(argv)
    if a.rebuild:
        rebuild()
    OUT.mkdir(parents=True, exist_ok=True)
    only = set(filter(None, a.only.split(",")))
    rows, items, failed, missing, orphans = analyse(only or None)
    plates = nest(items)
    import print_report
    print_report.write_all(rows, plates, failed, missing, orphans)
    return rows, plates, failed, missing, orphans


if __name__ == "__main__":
    main()
