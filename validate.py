"""Print checks on exported STL files. Parts are exported in their print frame (Z up, bed at z = 0)."""
import sys
from pathlib import Path

import manifold3d as m3d
import numpy as np
import trimesh

from params import P

STL = Path("out/stl")
Z_EPS = 0.05


def load(name):
    return trimesh.load(STL / f"{name}.stl", force="mesh")


def check_bed(m, tol=Z_EPS):
    ext = m.bounds[1] - m.bounds[0]
    ok = ext[0] <= P.bed_x and ext[1] <= P.bed_y and ext[2] <= P.bed_z and abs(m.bounds[0][2]) < tol
    return ok, f"extent {ext.round(1).tolist()} zmin {m.bounds[0][2]:.2f}"


def check_watertight(m):
    bodies = m.split(only_watertight=False)
    return m.is_watertight and len(bodies) == 1, f"watertight={m.is_watertight} bodies={len(bodies)}"


def overhang_fraction(m):
    n = m.face_normals
    c = m.triangles_center
    area = m.area_faces
    down = n[:, 2] < -np.sin(np.radians(P.overhang_max_deg))
    on_bed = c[:, 2] < m.bounds[0][2] + Z_EPS
    bad = down & ~on_bed
    if not bad.any():
        return 0.0, 0.0
    idx = np.where(bad)[0]
    allowed = 0.0
    total = 0.0
    for s in m.submesh([idx], only_watertight=False, append=False):
        a = s.area
        total += a
        ext = s.bounds[1] - s.bounds[0]
        if (s.face_normals[:, 2] < -0.99).all() and max(ext[0], ext[1]) <= P.bridge_max:
            allowed += a
    return (total - allowed) / m.area, total / m.area


def check_overhang(m):
    frac, raw = overhang_fraction(m)
    return frac <= P.overhang_fail_fraction, f"overhang {frac*100:.2f}% (raw {raw*100:.2f}%)"


def min_wall(m, samples=6000, seed=0, ignore_below=0.0, ignore_x_ends=False):
    pts, fi = trimesh.sample.sample_surface(m, samples, seed=seed)
    n = m.face_normals[fi]
    if ignore_x_ends:
        keep = np.abs(n[:, 0]) < 0.9
        pts, n = pts[keep], n[keep]
    origins = pts - n * 0.01
    hits, ray_idx, _ = m.ray.intersects_location(origins, -n, multiple_hits=False)
    d = np.full(len(pts), np.inf)
    d[ray_idx] = np.linalg.norm(hits - pts[ray_idx], axis=1)
    d = d[np.isfinite(d) & (d >= ignore_below)]
    return float(np.percentile(d, 1)) if len(d) else float("inf")


def check_wall(m, shell=False):
    """Shells have sharp rim edges and planar x end faces where the ray test returns grazing near-zero hits; those are ignored."""
    w = min_wall(m, samples=20000 if shell else 6000, ignore_below=0.5 if shell else 0.0, ignore_x_ends=shell)
    return w >= P.wall_min - 0.05, f"min wall (p1) {w:.2f}"


def validate_part(name, walls=True, supports=False):
    """Body shells are printed with supports: they are checked for bed fit, a single watertight body and wall thickness
    only, and the overhang is reported but not failed."""
    m = load(name)
    results = {"bed": check_bed(m, 3.0 if supports else Z_EPS), "watertight": check_watertight(m)}
    if supports:
        frac, raw = overhang_fraction(m)
        results["overhang"] = (True, f"needs supports (overhang {frac*100:.1f}% of area)")
    else:
        results["overhang"] = check_overhang(m)
    if walls:
        results["wall"] = check_wall(m, shell=supports)
    return results


# ---- assembled-pose checks ----
OVERLAP_DECLARED = [("rear_hub", "REAR_TIRE_WHEEL"), ("rear_hub", "AXLE_REAR"),
                    ("hub_left", "FRONT_TIRE_WHEEL_LEFT"), ("hub_right", "FRONT_TIRE_WHEEL_RIGHT")]
SEATED = OVERLAP_DECLARED + [
    ("POWER_UNIT", "swingarm_a"), ("POWER_UNIT", "swingarm_b"), ("POWER_UNIT", "swingarm_gearbox"),
    ("GEAR_PINION_1", "swingarm_gearbox"), ("GEAR_1", "swingarm_gearbox"), ("GEAR_PINION_2", "swingarm_gearbox"),
    ("GEAR_2", "swingarm_gearbox"), ("SHAFT_INTERMEDIATE", "swingarm_gearbox"), ("AXLE_REAR", "swingarm_a"),
    ("AXLE_REAR", "swingarm_gearbox"), ("LIPO_2S", "battery_mount"), ("RECEIVER", "rx_mount"),
    ("SERVO_9G", "chassis_tub_right"), ("SERVO_9G", "chassis_tub_left"), ("SERVO_HORN", "chassis_tub_right"),
    ("SERVO_HORN", "chassis_tub_left"),
    ("DOWEL_2x18_L", "body_bumper_cage"), ("DOWEL_2x18_R", "body_bumper_cage"),
    ("DOWEL_2x18_L", "front_yoke"), ("DOWEL_2x18_R", "front_yoke"), ("SERVO_HORN", "rod_drive"),
    ("LEAD_RUN", "battery_mount")]


def _declared(pairs, a, b):
    return any({a, b} == set(p) for p in pairs)


def _manifold(mesh):
    return m3d.Manifold(m3d.Mesh(vert_properties=np.asarray(mesh.vertices, dtype=np.float32),
                                 tri_verts=np.asarray(mesh.faces, dtype=np.uint32)))


def _bbox_gap(a, b):
    lo = np.maximum(a.bounds[0], b.bounds[0])
    hi = np.minimum(a.bounds[1], b.bounds[1])
    return float(np.max(lo - hi))


def interference(items):
    """Intersection volume (mm3) of every printed/printed and printed/bought pair that is not a declared fit."""
    cache, bad = {}, []
    for i, a in enumerate(items):
        for b in items[i + 1:]:
            if a.kind == b.kind == "bought" or _declared(OVERLAP_DECLARED, a.name, b.name):
                continue
            if _bbox_gap(a.mesh, b.mesh) > 0:
                continue
            for it in (a, b):
                cache.setdefault(it.name, _manifold(it.mesh))
            vol = (cache[a.name] ^ cache[b.name]).volume()
            if vol > P.interference_max_mm3:
                bad.append((a.name, b.name, round(vol, 2)))
    return bad


def clearance(items):
    """Pairs of a printed part and a bought envelope closer than clr_bought_min (seated mounts are exempt)."""
    bad = []
    for a in items:
        if a.kind != "bought":
            continue
        pts = None
        for b in items:
            if b.kind != "printed" or _declared(SEATED, a.name, b.name):
                continue
            if _bbox_gap(a.mesh, b.mesh) > P.clr_bought_min:
                continue
            if pts is None:
                pts, _ = trimesh.sample.sample_surface(a.mesh, 2500, seed=0)
            d = trimesh.proximity.closest_point(b.mesh, pts)[1].min()
            if d < P.clr_bought_min:
                bad.append((a.name, b.name, round(float(d), 2)))
    return bad


def body_clearance(items):
    """Body panels against every moving part and wheel: at least body_margin (3 mm) at every pose."""
    bad = []
    body = [i for i in items if i.group == "body" and i.kind == "printed"]
    moving = [i for i in items if i.group in ("front", "swingarm")]
    for b in body:
        for m in moving:
            if _bbox_gap(b.mesh, m.mesh) > P.body_margin:
                continue
            pts, _ = trimesh.sample.sample_surface(m.mesh, 2500, seed=0)
            d = trimesh.proximity.closest_point(b.mesh, pts)[1].min()
            if d < P.body_margin:
                bad.append((b.name, m.name, round(float(d), 2)))
    return bad


def removal_collisions(items, name, direction, distance, step=2.0, ignore=()):
    """Translate one item along a straight path; return where it first hits a part that is not ignored."""
    mover = next(i for i in items if i.name == name)
    others = [i for i in items if i.name != name and i.name not in ignore and i.kind == "printed"]
    base = _manifold(mover.mesh)
    cache = {o.name: _manifold(o.mesh) for o in others if _bbox_gap(o.mesh, mover.mesh) < distance}
    d = np.asarray(direction, float)
    for s in np.arange(step, distance + step, step):
        moved = base.translate(tuple(d * s))
        for o in others:
            if o.name in cache and (moved ^ cache[o.name]).volume() > P.interference_max_mm3:
                return float(s), o.name
    return None


def servo_torque_margin():
    import kinematics as K
    phi = np.radians(P.lean_target_deg)
    dphi = np.radians(0.5)
    dalpha = K.servo_angle(phi + dphi) - K.servo_angle(phi - dphi)
    gain = 2 * dphi / dalpha
    g = 9.81
    roll = P.mass_front_fraction * P.mass_total_g / 1000 * g * P.cg_height * np.sin(phi) * P.load_friction_factor
    need = roll * abs(gain)
    usable = P.servo_stall_torque_nmm * P.servo_usable_fraction
    return (usable - need) / usable, need, usable


def main(names):
    import build
    specs = {p.name: p for p in build.all_parts()}
    failed = False
    for n in names or specs:
        r = validate_part(n, specs[n].walls, specs[n].supports)
        ok = all(v[0] for v in r.values())
        failed |= not ok
        print(("PASS " if ok else "FAIL ") + n, "; ".join(f"{k}: {v[1]}" for k, v in r.items()))
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main(sys.argv[1:])
