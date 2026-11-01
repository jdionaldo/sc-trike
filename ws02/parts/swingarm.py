"""Single-sided swingarm: one left-hand plate that carries the gear and belt train and the cantilevered rear axle.

The 2830 motor is fixed in the cradle; the arm pivots about the motor shaft axis on a boss that stands out of the cradle's
left wall. Swingarm frame: origin on the motor axis, x forward, y along the axle (left positive), z up.
Print frame (proper rotation, outer face on the bed, gear cavity open upward): (u, v, w) = (x, z, y_out - y).
"""
import math

import numpy as np
from scipy.spatial import ConvexHull

from cad import Frame, Part


def layout(p):
    a1 = p.gear_module * (p.gear_pinion_1 + p.gear_gear_1) / 2
    a2 = p.belt_center
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
            "r_pin2": p.belt_pitch * p.gear_pinion_2 / (2 * math.pi) + 1.0, "r_gear2": p.belt_pitch * p.gear_gear_2 / (2 * math.pi) + 1.0}


def hull_xy(circles, n=24):
    pts = np.array([(c[0] + r * math.cos(2 * math.pi * k / n), c[1] + r * math.sin(2 * math.pi * k / n))
                    for c, r in circles for k in range(n)])
    return pts[ConvexHull(pts).vertices]


def gear_planes(p):
    """y ranges of the spur plane (pinion and 60T) and the belt plane (pulleys), outboard of the cradle wall."""
    y0 = p.sw_y_tire_face + 2.6
    return (y0, y0 + 4.0), (y0 + 4.5, y0 + 8.5)


def arm(p):
    L = layout(p)
    f = Frame(+1, p.sw_y_out_b)
    part = Part("swingarm_arm", "outer face on bed, gear cavity open upward", "PETG-CF")
    r_i = L["r_gear1"] + p.sw_gear_clr
    r_a = L["r_gear2"] + p.sw_gear_clr
    r_m = L["r_pin1"] + p.sw_gear_clr + 1.0
    yr = (p.sw_y_tire_face, p.sw_y_out_b)
    f.poly(part, hull_xy([(L["M"], p.sw_plate_r_pivot), (L["I"], r_i + p.sw_rim), (L["A"], r_a + p.sw_rim + 4.0)]), yr)
    ang = math.radians(p.swing_lug_deg)
    lug = (p.swing_lug_r * math.cos(ang), p.swing_lug_r * math.sin(ang))
    f.poly(part, hull_xy([(L["M"], p.sw_plate_r_pivot * 0.6), (lug, 5.0)]), yr)
    (s0, s1), (b0, b1) = gear_planes(p)
    y_step = s0 - 0.5                                   # the boss bore ends here; the pinion pocket opens beyond
    for c, r in ((L["I"], r_i), (L["A"], r_a)):
        f.cyl(part, c[0], c[1], 2 * r, (p.sw_y_tire_face - 1.0, p.sw_y_cavity_out), op="cut")
    f.cyl(part, 0.0, 0.0, 2 * r_m, (y_step, p.sw_y_cavity_out), op="cut")
    f.cyl(part, 0.0, 0.0, p.ch_boss_dia + 0.4, (p.sw_y_tire_face - 1.0, y_step + 0.1), op="cut")   # rides on the cradle boss
    wall = p.sw_y_cavity_out + 1.5
    f.cyl(part, L["I"][0], L["I"][1], p.pin_dia + p.clr_press, (p.sw_y_tire_face, wall), op="cut")
    ax, az = L["A"]
    f.cyl(part, ax, az, p.rear_axle_dia + p.clr_slide, (p.sw_y_tire_face - 1.0, p.sw_y_out_b + 1.0), op="cut")
    f.cyl(part, ax, az, p.rear_bearing_od + p.clr_press, (p.sw_y_out_b - p.rear_bearing_w, p.sw_y_out_b + 1.0), op="cut")
    f.cyl(part, lug[0], lug[1], p.pin_dia + p.clr_slide, (p.sw_y_tire_face - 1.0, p.sw_y_out_b + 1.0), op="cut")
    for x, z in cover_screws(p):
        f.cyl(part, x, z, p.m2_insert_hole, (p.sw_y_out_b - 4.5, p.sw_y_out_b + 1.0), op="cut")
    return part


COVER_DEPTH = 8.0


def cover_screws(p):
    L = layout(p)
    return [(L["I"][0], L["I"][1] + 17.0), (L["A"][0] + 18.0, L["A"][1] + 2.0), (L["M"][0] + 2.0, L["M"][1] - 17.0)]


def cover_outline(p, grow=0.0):
    L = layout(p)
    return hull_xy([(L["M"], 24.0 + grow), (L["I"], 20.0 + grow), (L["A"], 24.0 + grow)])


def cover(p):
    """Small shroud over the arm's outboard face (gears and belt side): a hollow faceted cap on three M2 screws."""
    f = Frame(+1, p.sw_y_out_b + COVER_DEPTH)
    part = Part("swingarm_cover", "outer face on the bed, open side up", "PETG")
    y0, y1 = p.sw_y_out_b, p.sw_y_out_b + COVER_DEPTH
    f.poly(part, cover_outline(p), (y0, y1))
    f.poly(part, cover_outline(p, -2.6), (y0 - 1.0, y1 - 2.4), op="cut")  # hollow, open toward the arm
    for x, z in cover_screws(p):
        f.cyl(part, x, z, p.m2_clear, (y0 - 1.0, y1 + 1.0), op="cut")
    return part


def build(p):
    return [arm(p), cover(p)]
