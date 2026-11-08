"""WS-03 mass, centre of gravity, weight split and roll-over estimate. Printed mass uses shells plus infill; bought masses are assumptions."""
import json
import numpy as np
import trimesh
import w3_assembly as A
import layout3wd as LY
from parts import w3_balance as BAL

RHO = 1.27e-3                       # g/mm3 PETG
WALL_T = 1.2                        # three perimeters
INFILL = {"body": 0.15, "default": 0.25}
BOUGHT = {   # g, assumptions to verify
    "lean_servo": 55, "lean_ears": 0, "b_lean_shock": 25, "steer_servo": 45, "b_motor": 201, "b_battery": 125, "mock_receiver": 6,
    "mock_tire": 95, "mock_rim": 22, "mock_rimdisc": 14, "mock_hub": 10, "mock_axle": 4, "mock_joint": 6,
    "mock_rear_tire_ring": 95, "mock_rear_rim": 22, "mock_rear_rim_disc": 14, "mock_rear_hub": 10, "mock_rear_axle": 12,
    "mock_cdiff_carrier": 40, "mock_cdiff_ring": 30, "mock_xover_pinion": 4, "mock_xover_idler": 14, "mock_xover_pin": 3, "mock_bearing": 1.5, "mock_fdiff_carrier": 28, "mock_bevel_pinion": 4,
    "mock_fpulley": 3, "mock_xover_pulley": 7, "mock_xover_belt": 4, "mock_xover_shaft": 6, "mock_rear_pulley": 4, "mock_fbelt": 3, "mock_rear_belt": 5, "mock_front_out": 3,
    "b_front_ring": 18, "b_rear_ring": 18, "b_rear_shaft": 16, "b_front_pinion_shaft": 16, "b_motor_shaft": 14,
    "b_rear_shock": 25, "diff_out": 6, "tip_shaft": 5, "lean_horn": 6, "steer_horn": 3,
}
# Small bought masses (screws, inserts, bearings, pins, wiring), 85 g in all, now placed by where they really are (an estimated inventory, weigh to verify).
# Before the balance pass the whole 85 g sat at the mass centroid; this inventory has about the same total and sits a little further forward.
MISC_ITEMS = [   # (what, g, x) ; y 0, z at the item's own level is ignored (placed at the running CG height)
    ("servo leads, horn and rod-end screws, lean and steer links", 14.0, -60.0),
    ("battery lead and ESC / receiver wiring", 12.0, -80.0),
    ("front end screws, inserts, bearings (arms, carriers, knuckles)", 24.0, -55.0),
    ("cage, deck and skin screws, inserts, magnets", 20.0, -230.0),
    ("rear arm pivot, axle hardware, belt tension screws", 15.0, -400.0),
]
MISC_G = sum(g for _, g, _ in MISC_ITEMS)
INFILL_PART = {"w3_tail": 0.08}     # wing and tail: 8 % gyroid is plenty for a cosmetic aero surface (a slicer setting, not geometry)
REAR_TYRE_INSERT_G = 0.0            # option: lighter rear tyre insert, grams saved on mock_rear_tire_ring (0 = stock; -15 is an estimate, weigh first)


def printed_mass(mesh, body, name=""):
    v = abs(mesh.volume)
    a = mesh.area
    shell = min(v, a * WALL_T * 0.5)           # area counts both faces of a thin wall
    inf = INFILL["body" if body else "default"]
    for pre, f in INFILL_PART.items():
        if name.startswith(pre):
            inf = f
    return RHO * (shell + inf * (v - shell)), v


def bought_mass(name):
    hits = [k for k in BOUGHT if name.startswith(k)]
    return BOUGHT[max(hits, key=len)] if hits else None


def summary(rows, M, cg):
    from w3_stretch import WHEELBASE as WB
    return dict(front=100 * (cg[0] + WB) / WB, total=M, cg=[float(x) for x in cg], h=float(cg[2] + 41.5))


def ladder():
    """Cumulative balance moves, each reported as the gain in points of front share and the resulting CG (not stored: slow-ish, run on demand)."""
    global MISC_ITEMS, INFILL_PART, REAR_TYRE_INSERT_G
    keep = (dict(BOUGHT), list(MISC_ITEMS), dict(INFILL_PART), REAR_TYRE_INSERT_G, BAL.BALLAST_ON)
    out = []
    try:
        BOUGHT["b_battery"] = 120; MISC_ITEMS = []; INFILL_PART = {}; REAR_TYRE_INSERT_G = 0.0; BAL.BALLAST_ON = False
        out.append(("0 merged baseline (120 g pack, small masses at the centroid)", summary(*run())))
        BOUGHT["b_battery"] = keep[0]["b_battery"]
        out.append(("1 battery: 125 g pack, x unchanged (forward limit is only 1.5 mm)", summary(*run())))
        MISC_ITEMS = keep[1]
        out.append(("2 small masses placed from an inventory (receiver already at x -44)", summary(*run())))
        out.append(("3 sideways CG: no move needed (|y| < 2 mm)", out[-1][1]))
        INFILL_PART = keep[2]
        out.append(("4a wing and tail infill 25 % to 8 %", summary(*run())))
        BAL.BALLAST_ON = keep[4]
        out.append(("5 nose ballast plate 42 g tungsten + 8 g carrier (FINAL BUILD)", summary(*run())))
        REAR_TYRE_INSERT_G = -15.0
        out.append(("option on top: lighter rear tyre insert, -15 g (estimate, not in the build; could replace about 20 g of ballast)", summary(*run())))
    finally:
        BOUGHT.clear(); BOUGHT.update(keep[0]); MISC_ITEMS = keep[1]; INFILL_PART = keep[2]; REAR_TYRE_INSERT_G = keep[3]; BAL.BALLAST_ON = keep[4]
    return out


def run(phi=0.0):
    items = A.assembly(phi)
    rows, M, mom = [], 0.0, np.zeros(3)
    for n, mesh, k in items:
        if k == "printed":
            g, v = printed_mass(mesh, n.startswith(("body3", "lid3")), n)
            c = mesh.center_mass if mesh.is_volume else mesh.centroid
        else:
            g = bought_mass(n)
            if g is None:
                continue
            if n == "mock_rear_tire_ring":
                g += REAR_TYRE_INSERT_G
            c = mesh.centroid
        rows.append((n, k, g, c))
        M += g
        mom += g * np.asarray(c)
    if BAL.BALLAST_ON:                                    # nose ballast (parts/w3_balance.py): plate plus printed carrier and lid
        pc = np.array(BAL.plate_centre())
        rows.append(("ballast plate (tungsten)", "bought", BAL.plate_g(), pc))
        M += BAL.plate_g()
        mom += BAL.plate_g() * pc
        for part in BAL.build():
            m = part.fn()
            g, _ = printed_mass(m, False, part.name)
            rows.append((part.name, "printed", g, m.center_mass if m.is_volume else m.centroid))
            M += g
            mom += g * (m.center_mass if m.is_volume else m.centroid)
    c0 = mom / M
    items = MISC_ITEMS if MISC_ITEMS else [("all small masses at the centroid", MISC_G, c0[0])]
    for what, g, x in items:
        rows.append(("misc: " + what, "misc", g, np.array([x, c0[1] if not MISC_ITEMS else 0.0, c0[2]])))
    mom = mom + sum(g * r[3] for r in rows if r[1] == "misc")
    M2 = M + MISC_G
    cg = mom / M2
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
    lad = ladder()
    prev = None
    ll = ["", "## Balance ladder (cumulative)", "", "| step | front % | gain (points) | total g | CG x, y, z (mm) | CG height above ground |", "|---|---|---|---|---|---|"]
    for name, r in lad:
        gain = "" if prev is None else f"{r['front'] - prev:+.2f}"
        ll.append(f"| {name} | {r['front']:.2f} | {gain} | {r['total']:.0f} | {r['cg'][0]:.1f}, {r['cg'][1]:.1f}, {r['cg'][2]:.1f} | {r['h']:.1f} |")
        prev = r["front"]
    print("\n".join(ll))
    top = sorted(rows, key=lambda r: -r[2])[:10]
    lines = ["# WS-03 mass, CG and roll-over", "", "Printed mass = 1.2 mm walls plus 25% infill (15% for the body); bought masses are assumptions (45 g servos, 62 g motor, 125 g 3S pack).", "",
             "| item | value |", "|---|---|"] + [f"| {k} | {v} |" for k, v in res.items()] + ["", "Heaviest items:", ""] + [f"- {n}: {g:.0f} g" for n, k, g, c in top] + ll
    open("WS03_MASS_CG.md", "w").write("\n".join(lines) + "\n")
    print(res)
