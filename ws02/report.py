"""Phase 5 numbers from the exported STL files: print plan, mass and CG, static tip-over, exploded view."""
import json
from pathlib import Path

import numpy as np
import trimesh
from scipy.optimize import fsolve

import assembly
import build
from params import P

OUT = Path("out")
DENSITY = dict(P.density_g_cc)
QTY = dict(P.part_qty)
COSMETIC = ("body_",)


def print_rows():
    rows = []
    for part in build.all_parts():
        m = trimesh.load(OUT / "stl" / f"{part.name}.stl", force="mesh")
        cosmetic = part.name.startswith(COSMETIC)
        infill = P.infill_cosmetic if cosmetic else P.infill_structural
        shell = min(m.volume, m.area * P.perimeters * P.nozzle)
        printed_mm3 = shell + infill * (m.volume - shell)
        mass = printed_mm3 * DENSITY[part.material] / 1000.0
        hours = printed_mm3 / P.flow_mm3_s * P.time_overhead / 3600.0
        rows.append({"name": part.name, "qty": QTY.get(part.name, 1), "material": part.material,
                     "orientation": part.orientation, "infill": infill, "mass_g": mass, "hours": hours,
                     "extent": (m.bounds[1] - m.bounds[0]).round(1).tolist()})
    for name in ("mono_left", "mono_right", "canopy_lid"):          # built by mono_build.py, not from command scripts
        m = trimesh.load(OUT / "stl" / f"{name}.stl", force="mesh")
        shell = min(m.volume, m.area * P.perimeters * P.nozzle)
        printed_mm3 = shell + P.infill_structural * (m.volume - shell)
        rows.append({"name": name, "qty": 1, "material": "PETG", "orientation": "chassis frame, supports, turned on the bed",
                     "infill": P.infill_structural, "mass_g": printed_mm3 * DENSITY["PETG"] / 1000.0,
                     "hours": printed_mm3 / P.flow_mm3_s * P.time_overhead / 3600.0,
                     "extent": (m.bounds[1] - m.bounds[0]).round(1).tolist()})
    return rows


def bought_mass(item):
    name = item.name
    table = {"POWER_UNIT": P.pu_mass_g, "REAR_TIRE_WHEEL": P.rear_tire_mass_g, "SERVO_9G": P.servo_mass_g,
             "SERVO_HORN": P.horn_mass_g, "RECEIVER": P.rx_mass_g, "LIPO_2S": P.lipo_mass_g}
    table.update(dict(P.gears_mass_g))
    if name in table:
        return table[name]
    if name.startswith("FRONT_TIRE_WHEEL"):
        return P.front_tire_mass_g
    if name.startswith("DOWEL"):
        return P.dowel_mass_g
    if name in ("AXLE_REAR", "SHAFT_INTERMEDIATE"):
        return item.mesh.volume * P.steel_density_g_cc / 1000.0
    return 0.0


def mass_points(items, rows):
    by_name = {r["name"]: r for r in rows}
    pts = []
    for it in items:
        if it.kind == "printed":
            key = it.name
            if key.startswith("tie_rod"):
                key = "tie_rod"
            elif key.startswith("upright"):
                key = "upright"
            r = by_name[key]
            pts.append((it.name, r["mass_g"], it.mesh.center_mass))
        else:
            m = bought_mass(it)
            if m:
                pts.append((it.name, m, it.mesh.center_mass))
    centroid = np.mean([c for _, _, c in pts], axis=0)
    pts.append(("HARDWARE", P.hardware_mass_g, centroid))
    pts.append(("SHOCK", P.shock_mass_g, np.array([P.shock_xz[0], 0.0, P.shock_xz[1]])))
    return pts


def cg(items, rows):
    pts = mass_points(items, rows)
    total = sum(m for _, m, _ in pts)
    return total, sum(m * c for _, m, c in pts) / total


def tip_over(lean_deg):
    """Ground plane through the three tire contacts of the pose; margin of the CG projection inside the triangle."""
    items = assembly.scene(lean_deg, 0.0, body=True)
    rows = print_rows()
    total, centre = cg(items, rows)
    tires = {i.name: i.mesh.vertices for i in items if "TIRE" in i.name}
    names = sorted(tires)

    def normal(rp):
        r, p = rp
        return np.array([-np.sin(p) * np.cos(r), np.sin(r), np.cos(p) * np.cos(r)]) / 1.0

    def heights(rp):
        n = normal(rp)
        n = n / np.linalg.norm(n)
        return np.array([(tires[k] @ n).min() for k in names])

    sol = fsolve(lambda rp: (heights(rp)[:2] - heights(rp)[2]), [0.0, 0.0])
    n = normal(sol)
    n /= np.linalg.norm(n)
    contacts = np.array([tires[k][np.argmin(tires[k] @ n)] for k in names])
    c0 = contacts[0]
    e1 = np.cross(n, [1.0, 0.0, 0.0])
    e1 /= np.linalg.norm(e1)
    e2 = np.cross(n, e1)
    proj = lambda q: np.array([(q - c0) @ e1, (q - c0) @ e2])
    tri = np.array([proj(c) for c in contacts])
    g = proj(centre - ((centre - c0) @ n) * n)
    margins = []
    for a, b in ((0, 1), (1, 2), (2, 0)):
        edge = tri[b] - tri[a]
        nrm = np.array([-edge[1], edge[0]]) / np.linalg.norm(edge)
        if nrm @ (tri.mean(0) - tri[a]) < 0:
            nrm = -nrm
        margins.append(float(nrm @ (g - tri[a])))
    height = float((centre - c0) @ n)
    return {"lean_deg": lean_deg, "mass_g": total, "cg_chassis": centre.round(1).tolist(), "cg_height_mm": height,
            "ground_roll_deg": float(np.degrees(np.arccos(n @ np.array([0, 0, 1])))),
            "edge_margins_mm": [round(x, 1) for x in margins], "min_margin_mm": min(margins),
            "tip_lateral_g": min(margins) / height, "contacts": names}


def write_print_plan(rows):
    lines = ["# Print plan", "",
             f"Slicer defaults: {P.nozzle} mm nozzle, {P.layer} mm layers, {P.perimeters} perimeters "
             f"({P.perimeters * P.nozzle:.1f} mm walls), no supports except the three monocoque parts (supports on, shell halves turned about 40 degrees on the bed), no brim unless a part lifts. Structural parts "
             f"{P.infill_structural:.0%} gyroid, body panels {P.infill_cosmetic:.0%}. Times and masses are estimates "
             f"from part volume ({P.flow_mm3_s:.0f} mm3/s, x{P.time_overhead} overhead).", "",
             "| Part | Qty | Material | Orientation | Extent mm | Infill | Mass g (each) | Est. time h (each) |",
             "|---|---|---|---|---|---|---|---|"]
    for r in rows:
        lines.append(f"| {r['name']} | {r['qty']} | {r['material']} | {r['orientation']} | "
                     f"{r['extent'][0]} x {r['extent'][1]} x {r['extent'][2]} | {r['infill']:.0%} | "
                     f"{r['mass_g']:.1f} | {r['hours']:.1f} |")
    total_h = sum(r["hours"] * r["qty"] for r in rows)
    total_g = sum(r["mass_g"] * r["qty"] for r in rows)
    lines += ["", f"Totals: {sum(r['qty'] for r in rows)} printed pieces, about {total_g:.0f} g of filament and "
              f"{total_h:.0f} printer-hours.", "",
              "Materials: PETG-CF for the swingarm halves, gearbox and hatch (heat); PETG elsewhere. ASA or PC are "
              "acceptable substitutes for the swingarm; never PLA near the power unit."]
    Path("print_plan.md").write_text("\n".join(lines) + "\n")


def main():
    rows = print_rows()
    write_print_plan(rows)
    result = {"default": tip_over(0.0), "full_lean_left": tip_over(P.lean_target_deg),
              "full_lean_right": tip_over(-P.lean_target_deg)}
    (OUT / "mass_cg.json").write_text(json.dumps(result, indent=2))
    print(json.dumps({k: {a: v[a] for a in ("mass_g", "cg_chassis", "cg_height_mm", "ground_roll_deg",
                                            "edge_margins_mm", "tip_lateral_g")} for k, v in result.items()}, indent=1))


if __name__ == "__main__":
    main()
