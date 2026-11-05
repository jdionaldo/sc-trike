"""WS-03 layout study: every major block of the 3WD lean-steer trike as simple solids, checked for overlaps.

Frame: x forward, y left, z up, z = 0 at the front wheel axle height, front axle at x = 0. Default pose (arms level).
"""
import itertools
import sys

import numpy as np
import trimesh

from w3_stretch import STRETCH, WHEELBASE, back, pv

L = dict(
    track=288.0, tire_od=112.0, tire_w=62.0, rear_od=112.0, rear_w=62.0,
    la=100.0,                      # arm length, pivot to knuckle carrier
    wheelbase=WHEELBASE, rake_deg=4.0,
    tub_in=48.0, tub_wall=2.0,     # widened tub (inner face, wall)
    arm_y=(50.5, 56.5), horn_y=(57.0, 59.5), servo_y=(28.7, 48.0),
    zu=40.0,                       # upper link height above the lower pin
)


MOTOR_C = (-100.0, -21.0, 41.0)       # motor can centre (x, y, z): most forward spot the fit scan (w3_fit.py) leaves free; x -100 collides with the pivot hoop, servos and diff case


def box(x, y, z):
    (x0, x1), (y0, y1), (z0, z1) = x, y, z
    m = trimesh.creation.box(extents=(x1 - x0, y1 - y0, z1 - z0))
    m.apply_translation(((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2))
    return m


def cyl(c, r, length, axis):
    m = trimesh.creation.cylinder(radius=r, height=length, sections=32)
    if axis == "x":
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [0, 1, 0]))
    elif axis == "y":
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    m.apply_translation(c)
    return m


def blocks():
    b = {}
    xp = -L["la"]
    ay0, ay1 = L["arm_y"]
    for tag, s in (("L", 1), ("R", -1)):
        ys = lambda a, c: tuple(sorted((s * a, s * c)))
        b[f"arm_{tag}"] = box((xp - 6, 6), ys(ay0, ay1), (-9, 9))
        b[f"uplink_{tag}"] = box((xp - 6, 6), ys(ay0, ay1), (L["zu"] - 5, L["zu"] + 5))
        b[f"pulley_pivot_{tag}"] = cyl((xp, s * (ay0 + ay1) / 2, 0), 8, ay1 - ay0, "y")
        b[f"pulley_tip_{tag}"] = cyl((0, s * (ay0 + ay1) / 2, 0), 8, ay1 - ay0, "y")
        b[f"diff_out_{tag}"] = cyl((xp, s * 26.0, 0), 2.5, 52.0, "y")
        b[f"tip_shaft_{tag}"] = cyl((0, s * 79.0, 0), 2.0, 46.0, "y")
        b[f"carrier_{tag}"] = box((-10, 10), ys(92, 104), (-20, L["zu"] + 5))
        b[f"tire_{tag}"] = cyl((0, s * (L["track"] / 2), 0), L["tire_od"] / 2, L["tire_w"], "y")
        b[f"lean_servo_{tag}"] = box((-86.0, -46.0), ys(*L["servo_y"]), (-27, -7))
        b[f"steer_servo_{tag}"] = box((-149.4, -109.4), ys(*L["servo_y"]), (-6, 14))
        b[f"lean_horn_{tag}"] = box((-90, -66), ys(*L["horn_y"]), (-20, 8))
        b[f"steer_horn_{tag}"] = box((-128, -108), ys(*L["horn_y"]), (-16, 6))
        b[f"tub_wall_{tag}"] = box((-190, -20), ys(L["tub_in"], L["tub_in"] + L["tub_wall"]), (-44, 34))
    # drivetrain: shafts at axle height; bevel pinion shaft level with the diff axis, engaging the ring on the diff's +y end
    b["front_diff"] = cyl((xp, 0, 0), 17, 34, "y")
    b["front_ring"] = cyl((xp, 21.0, 0), 16, 6, "y")
    b["front_pinion_shaft"] = cyl((-135.0, 21.0, 0), 2.5, 40, "x")             # x -155..-115, pinion at its front end
    b["center_diff"] = cyl((-180.0, 21.0, 0), 19, 30, "x")
    b["rear_shaft"] = cyl((0.5 * (-205.0 + pv(-257.0)), 21.0, 0), 2.5, -205.0 - pv(-257.0), "x")      # x -205 .. pv(-257): from the centre diff to the rear bevel
    b["motor"] = cyl(MOTOR_C, 18, 58.1, "x")                                # Hobbywing Fusion SE (36 x 58.1, ESC built in) opposite the driveline
    b["motor_shaft"] = cyl((MOTOR_C[0] - 29.05 - 8.0, MOTOR_C[1], MOTOR_C[2]), 2, 16, "x")      # output shaft leaves the rear face; the cross-over stage to the centre diff is still to be drawn
    b["battery"] = box((-79, -17), (-10, 10), (-20, -6))
    rear_x = -L["wheelbase"]
    rz = L["rear_od"] / 2 - L["tire_od"] / 2 - L["wheelbase"] * np.tan(np.radians(L["rake_deg"]))   # chassis raked nose-down: rear axle lower in the chassis frame
    b["rear_ring"] = cyl((pv(-272.0), 21.0, 0), 15, 6, "y")
    b["rear_bevel"] = cyl((pv(-257.0), 21.0, 0), 6, 8, "x")
    b["rear_out"] = cyl((pv(-272.0), 48.0, 0), 2.5, 56, "y")
    b["rear_arm"] = box((rear_x - 8, pv(-264)), (46, 76), (min(-9, rz - 9), 9))
    b["rear_tire"] = cyl((rear_x, 0, rz), L["rear_od"] / 2, L["rear_w"], "y")
    return b


# pairs that are meant to touch or share a bore, not real clashes
OK = [("diff_out_", "pulley_pivot_"), ("diff_out_", "front_diff"), ("diff_out_", "tub_wall_"), ("diff_out_", "arm_"),
      ("tip_shaft_", "pulley_tip_"), ("tip_shaft_", "carrier_"), ("tip_shaft_", "tire_"), ("arm_", "pulley_"),
      ("rear_out", "rear_bevel"), ("rear_out", "rear_arm"), ("motor_shaft", "motor"), ("motor_shaft", "center_diff"),
      ("rear_shaft", "center_diff"), ("front_pinion_shaft", "center_diff"), ("rear_shaft", "rear_bevel"), ("rear_shaft", "rear_ring"),
      ("front_pinion_shaft", "front_diff"), ("front_pinion_shaft", "front_ring"), ("front_ring", "front_diff"), ("rear_ring", "rear_bevel"),
      ("rear_out", "rear_ring"), ("diff_out", "front_ring"), ("rear_shaft", "rear_out"), ("tip_shaft_", "arm_")]


def declared(a, b):
    return any((p in a and q in b) or (q in a and p in b) for p, q in OK)


def check(b):
    import manifold3d as m

    def man(t):
        return m.Manifold(m.Mesh(vert_properties=np.asarray(t.vertices, np.float32), tri_verts=np.asarray(t.faces, np.uint32)))

    mans = {k: man(v) for k, v in b.items()}
    bad = []
    for (a, ma), (c, mc) in itertools.combinations(mans.items(), 2):
        if declared(a, c):
            continue
        va, vb = b[a].bounds, b[c].bounds
        if np.any(va[1] < vb[0]) or np.any(vb[1] < va[0]):
            continue
        v = (ma ^ mc).volume()
        if v > 1.0:
            bad.append((a, c, round(v, 1)))
    return bad


if __name__ == "__main__":
    bl = blocks()
    for a, c, v in check(bl):
        print("overlap", a, c, v)
    if len(sys.argv) > 1:
        sc = trimesh.Scene()
        for k, m in bl.items():
            m = m.copy()
            m.visual.face_colors = [200, 60, 50, 255] if "arm" in k or "uplink" in k else [70, 75, 85, 255]
            if "tire" in k:
                m.visual.face_colors = [30, 30, 30, 255]
            if "servo" in k or "horn" in k:
                m.visual.face_colors = [60, 120, 220, 255]
            sc.add_geometry(m, node_name=k, geom_name=k)
        sc.export(sys.argv[1])
        print("wrote", sys.argv[1])
