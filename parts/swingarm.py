"""Two-half clamshell swingarm around the 2-in-1 power unit, split on the y = 0 plane.

Swingarm frame: origin on the motor axis (also the swing pivot), x forward, y along the axle (left positive), z up.
Left is +y. The motor tail faces -y (the right side); its leads leave through a radial slot toward +x and the motor
is withdrawn through the hatch opening on the -y arm.
Print frames (proper rotations, outer face on the bed, split face up):
  half B (left block, ends at the tire face): (u, v, w) = (x, z, y_tire_face - y)
  gearbox (left arm plate): same mapping with y_out_b
  half A (right, -y):  (u, v, w) = (x, -z, y + y_out_a)
"""
import math

import numpy as np
from scipy.spatial import ConvexHull

from cad import Frame, Part


def layout(p):
    a1 = p.gear_module * (p.gear_pinion_1 + p.gear_gear_1) / 2
    a2 = p.gear_module * (p.gear_pinion_2 + p.gear_gear_2) / 2
    ang = math.radians(p.swing_arm_angle_deg)
    d = p.swingarm_len
    e = np.array([-math.cos(ang), -math.sin(ang)])
    t = (a1 ** 2 - a2 ** 2 + d ** 2) / (2 * d)
    h = math.sqrt(a1 ** 2 - t ** 2)
    n = np.array([-e[1], e[0]])
    if n[1] < 0:
        n = -n
    return {"M": np.zeros(2), "I": t * e + h * n, "A": d * e,
            "r_pin1": p.gear_module * p.gear_pinion_1 / 2, "r_gear1": p.gear_module * p.gear_gear_1 / 2,
            "r_pin2": p.gear_module * p.gear_pinion_2 / 2, "r_gear2": p.gear_module * p.gear_gear_2 / 2}


def hull_xy(circles, n=24):
    pts = np.array([(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n))
                    for c, r in circles for k in range(n)])
    return pts[ConvexHull(pts).vertices]


def _split_screws(p):
    s = p.sw_split_screw
    return [(sx, sz) for sx in (-s, s) for sz in (-s, s)]


def half_a(p):
    L = layout(p)
    f = Frame(-1, p.sw_y_out_a)
    part = Part("swingarm_a", "outer face on bed, split face up, motor pocket vertical", "PETG-CF")
    b = p.sw_block_half
    f.box(part, (-b, b), (-p.sw_y_out_a, 0.0), (-b, b))
    f.poly(part, hull_xy([(L["M"], p.sw_plate_r_pivot), (L["A"], p.sw_plate_r_axle)]), (-p.sw_y_out_a, -p.sw_y_tire_face))
    ang = math.radians(p.swing_lug_deg)
    lug = (p.swing_lug_r * math.cos(ang), p.swing_lug_r * math.sin(ang))
    f.poly(part, hull_xy([(L["M"], p.sw_plate_r_pivot * 0.6), (lug, 5.0)]), (-p.sw_y_out_a, -p.sw_y_tire_face))

    y_step = -p.sw_y_out_a + p.sw_hatch_depth
    f.cyl(part, 0.0, 0.0, p.pu_dia + p.sw_motor_clr, (y_step, 1.0), op="cut")
    f.cyl(part, 0.0, 0.0, p.sw_hatch_open, (-p.sw_y_out_a - 1.0, y_step), op="cut")
    for k in range(4):
        a = math.radians(45 + 90 * k)
        f.cyl(part, p.sw_screw_r * math.cos(a), p.sw_screw_r * math.sin(a), p.m2_insert_hole,
              (-p.sw_y_out_a - 1.0, -p.sw_y_out_a + 5.0), op="cut")
    for sx, sz in _split_screws(p):
        f.cyl(part, sx, sz, p.m2_clear, (-p.sw_y_out_a - 1.0, 1.0), op="cut")
    f.box(part, (0.0, p.sw_lead_slot_reach), (y_step, -p.pu_len / 2), (-p.sw_lead_slot_w / 2, p.sw_lead_slot_w / 2), op="cut")

    ax, az = L["A"]
    f.cyl(part, ax, az, p.axle_dia + p.clr_slide, (-p.sw_y_out_a - 1.0, -p.sw_y_tire_face + 1.0), op="cut")
    f.cyl(part, ax, az, p.bearing_od + p.clr_press, (-p.sw_y_tire_face - p.bearing_w, -p.sw_y_tire_face + 1.0), op="cut")
    f.cyl(part, lug[0], lug[1], p.pin_dia + p.clr_slide, (-p.sw_y_out_a - 1.0, -p.sw_y_tire_face + 1.0), op="cut")
    return part


def half_b(p):
    f = Frame(+1, p.sw_y_tire_face)
    part = Part("swingarm_b", "gearbox end face on bed, split face up, motor pocket vertical", "PETG-CF")
    b = p.sw_block_half
    f.box(part, (-b, b), (0.0, p.sw_y_tire_face), (-b, b))
    f.cyl(part, 0.0, 0.0, p.pu_dia + p.sw_motor_clr, (-1.0, p.pu_len / 2), op="cut")
    f.cyl(part, 0.0, 0.0, p.pu_shaft_dia + 1.1, (p.pu_len / 2 - 1.0, p.sw_y_tire_face + 1.0), op="cut")
    for sx, sz in _split_screws(p):
        f.cyl(part, sx, sz, p.m2_insert_hole, (-1.0, 7.0), op="cut")
    for sx in (p.sw_split_screw,):
        for sz in (-p.sw_split_screw, p.sw_split_screw):
            f.cyl(part, sx, sz, p.m2_insert_hole, (p.sw_y_tire_face - 7.0, p.sw_y_tire_face + 1.0), op="cut")
    return part


def gearbox(p):
    L = layout(p)
    f = Frame(+1, p.sw_y_out_b)
    part = Part("swingarm_gearbox", "outer face on bed, gear cavity open upward", "PETG-CF")
    r_i = L["r_gear1"] + p.sw_gear_clr
    r_a = L["r_gear2"] + p.sw_gear_clr
    r_m = L["r_pin1"] + p.sw_gear_clr + 1.0
    f.poly(part, hull_xy([(L["M"], p.sw_plate_r_pivot), (L["I"], r_i + p.sw_rim), (L["A"], r_a + p.sw_rim)]),
           (p.sw_y_tire_face, p.sw_y_out_b))
    for c, r in ((L["I"], r_i), (L["A"], r_a), (L["M"], r_m)):
        f.cyl(part, c[0], c[1], 2 * r, (p.sw_y_tire_face - 1.0, p.sw_y_cavity_out), op="cut")
    wall = p.sw_y_cavity_out + 1.5
    f.cyl(part, L["I"][0], L["I"][1], p.pin_dia + p.clr_press, (p.sw_y_tire_face, wall), op="cut")
    f.cyl(part, L["A"][0], L["A"][1], p.axle_dia + p.clr_slide, (p.sw_y_tire_face, wall), op="cut")
    for sz in (-p.sw_split_screw, p.sw_split_screw):
        f.cyl(part, p.sw_split_screw, sz, p.m2_clear, (p.sw_y_tire_face - 1.0, p.sw_y_out_b + 1.0), op="cut")
    f.cyl(part, 0.0, 0.0, p.sw_cup_dia, (p.sw_y_out_b - p.sw_cup_depth, p.sw_y_out_b + 1.0), op="cut")
    return part


def hatch(p):
    r_disc = (p.sw_hatch_open - 2 * p.clr_slide) / 2
    r_flange = p.sw_hatch_flange / 2
    r_cb = (p.sw_tube_od + p.clr_slide) / 2
    z_cone = p.sw_hatch_depth
    top = z_cone + p.sw_hatch_flange_t
    part = Part("swingarm_hatch", "disc down, counterbore up", "PETG-CF")
    part.revolve("XZ", [(0.0, 0.0), (r_disc, 0.0), (r_disc, z_cone), (r_flange, z_cone + p.sw_hatch_cone_h),
                        (r_flange, top), (r_cb, top), (r_cb, top - p.sw_cbore_depth), (0.0, top - p.sw_cbore_depth)])
    for k in range(4):
        a = math.radians(45 + 90 * k)
        part.cyl((p.sw_screw_r * math.cos(a), p.sw_screw_r * math.sin(a), z_cone - 1.0),
                 p.m2_clear, p.sw_hatch_flange_t + 2.0, op="cut")
        part.cyl((p.sw_vent_r * math.cos(a), p.sw_vent_r * math.sin(a), -1.0),
                 p.sw_vent_dia, top + 2.0, op="cut")
    part.box_c((0.0, p.sw_shim_y, top / 2), (p.sw_shim_w, p.sw_shim_slot_t, top + 2.0), op="cut")
    return part


def build(p):
    return [half_a(p), half_b(p), gearbox(p), hatch(p)]
