"""WS-03 mass, centre of gravity, weight split and roll-over estimate. Printed mass uses shells plus infill; bought masses are assumptions."""
import json
import numpy as np
import trimesh
import w3_assembly as A
import layout3wd as LY

RHO = 1.27e-3                       # g/mm3 PETG
WALL_T = 1.2                        # three perimeters
INFILL = {"body": 0.15, "default": 0.25}
BOUGHT = {   # g, assumptions to verify
    "lean_servo": 45, "steer_servo": 45, "b_motor": 201, "b_battery": 120, "mock_receiver": 6,
    "mock_tire": 38, "mock_rim": 14, "mock_rimdisc": 8, "mock_hub": 6, "mock_axle": 4, "mock_joint": 6,
    "mock_rear_tire_ring": 95, "mock_rear_rim": 22, "mock_rear_rim_disc": 14, "mock_rear_hub": 10, "mock_rear_axle": 12,
    "mock_cdiff_carrier": 38, "mock_cdiff_ring": 12, "mock_motor_pinion": 3, "mock_fdiff_carrier": 28, "mock_bevel_pinion": 4,
    "mock_fpulley": 3, "mock_rear_pulley": 4, "mock_fbelt": 3, "mock_rear_belt": 5, "mock_front_out": 3,
    "b_front_ring": 8, "b_rear_ring": 8, "b_rear_shaft": 22, "b_front_pinion_shaft": 5, "b_motor_shaft": 2,
    "diff_out": 6, "tip_shaft": 5, "lean_horn": 4, "steer_horn": 3,
}
MISC_G = 110.0                      # screws, inserts, bearings, pins, wiring (placed at the centroid)


def printed_mass(mesh, body):
    v = abs(mesh.volume)
    a = mesh.area
    shell = min(v, a * WALL_T * 0.5)           # area counts both faces of a thin wall
    inf = INFILL["body" if body else "default"]
    return RHO * (shell + inf * (v - shell)), v


def bought_mass(name):
    hits = [k for k in BOUGHT if name.startswith(k)]
    return BOUGHT[max(hits, key=len)] if hits else None


def run(phi=0.0):
    items = A.assembly(phi)
    rows, M, mom = [], 0.0, np.zeros(3)
    for n, mesh, k in items:
        if k == "printed":
            g, v = printed_mass(mesh, n.startswith(("body3", "lid3")))
            c = mesh.center_mass if mesh.is_volume else mesh.centroid
        else:
            g = bought_mass(n)
            if g is None:
                continue
            c = mesh.centroid
        rows.append((n, k, g, c))
        M += g
        mom += g * np.asarray(c)
    c0 = mom / M
    M2 = M + MISC_G
    cg = (mom + MISC_G * c0) / M2
    return rows, M2, cg


if __name__ == "__main__":
    rows, M, cg = run()
    pr = sum(g for n, k, g, c in rows if k == "printed")
    bg = sum(g for n, k, g, c in rows if k == "bought")
    from w3_stretch import WHEELBASE as WB
    front = (cg[0] + WB) / WB
    h = cg[2] + 41.5
    T = 134.55
    tip = float(np.degrees(np.arctan(T / h)))
    res = {"printed_g": round(pr), "bought_g": round(bg), "misc_g": MISC_G, "total_g": round(M),
           "cg_mm": [round(float(x), 1) for x in cg], "front_weight_fraction": round(float(front), 3),
           "cg_height_above_ground_mm": round(float(h), 1), "static_roll_angle_deg": round(tip, 1),
           "rollover_speed_1m_radius_mps": round(float(np.sqrt(9.81 * 1.0 * (T / 1000) / (h / 1000))), 2)}
    json.dump(res, open("out/mass_cg_w3.json", "w"), indent=1)
    top = sorted(rows, key=lambda r: -r[2])[:10]
    lines = ["# WS-03 mass, CG and roll-over", "", "Printed mass = 1.2 mm walls plus 25% infill (15% for the body); bought masses are assumptions (45 g servos, 62 g motor, 120 g 3S pack).", "",
             "| item | value |", "|---|---|"] + [f"| {k} | {v} |" for k, v in res.items()] + ["", "Heaviest items:", ""] + [f"- {n}: {g:.0f} g" for n, k, g, c in top]
    open("WS03_MASS_CG.md", "w").write("\n".join(lines) + "\n")
    print(res)
