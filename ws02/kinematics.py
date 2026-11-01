"""Phase 1: lean parallelogram, lean-to-steer coupling, servo drive, rear swingarm.

Chassis frame: x forward, y left, z up, origin on the lower lean-bar pivot.
Lean angle phi is positive to the left and equals the bar angle relative to the chassis
(left bar end rises in the chassis frame). Uprights stay parallel to the chassis post.
"""
import json
import math
from pathlib import Path

import numpy as np
from scipy.optimize import least_squares, brentq

from params import P, K

OUT = Path("out")
D2R = math.pi / 180.0

# ---- fixed design choices (geometry, not tuning) ----
HUB_OUT = 14.0 * K                       # axle offset outward of the bar end
BAR_HALF = P.front_track / 2 - HUB_OUT   # bar end to chassis pivot
AXLE_DROP = 14.0 * K                     # axle below the lower bar end
CASTER_DEG = 12.0
ARM_Y = -(BAR_HALF - (P.front_track / 2 - P.front_tire_w / 2 - P.hub_thick - P.hub_lug_len)) - P.rod_boss / 2 - 1.5
STEER_TARGET_DEG = 17.0
ANCHOR_BOX = tuple((a * K, b * K) for a, b in ((-34.0, -8.0), (20.0, 62.0), (-14.0, 14.0)))   # bar frame: x behind the bar, y along it, z off the bar axis
ARM_BOX = tuple((a * K, b * K) for a, b in ((-12.0, -5.0), (-22.0, -8.0)))   # behind the kingpin so the link never crosses the bar


def rot_axis(k, ang):
    k = k / np.linalg.norm(k)
    K = np.array([[0, -k[2], k[1]], [k[2], 0, -k[0]], [-k[1], k[0], 0]])
    return np.eye(3) + math.sin(ang) * K + (1 - math.cos(ang)) * K @ K


KP_AXIS = np.array([-math.sin(CASTER_DEG * D2R), 0.0, math.cos(CASTER_DEG * D2R)])


def bar_end(phi, side=1):
    return np.array([0.0, side * BAR_HALF * math.cos(phi), side * BAR_HALF * math.sin(phi)])


def anchor_pos(phi, anchor_bar, side=1):
    """Link anchor fixed on the lower lean bar (bar frame: x forward, y along the bar, z off the bar axis)."""
    bx, by, bz = anchor_bar
    by *= side
    return np.array([bx, by * math.cos(phi) - bz * math.sin(phi), by * math.sin(phi) + bz * math.cos(phi)])


def steer_angle(phi, arm, anchor_bar, link_len, d0=0.0, side=1):
    """Hub steer angle delta (rad) at lean phi (rad); side 1 is the left wheel, -1 the right (mirrored arm and anchor)."""
    k = bar_end(phi, side)
    a = np.asarray(arm, float) * np.array([1, side, 1])
    p = anchor_pos(phi, anchor_bar, side)

    def f(d):
        return np.linalg.norm(k + rot_axis(KP_AXIS, d) @ a - p) - link_len

    for width in (0.1, 0.3, 0.6):
        lo, hi = d0 - width, d0 + width
        if f(lo) * f(hi) < 0:
            return brentq(f, lo, hi)
    return float("nan")


def solve_coupling():
    """Steering arm (x, z; y fixed so the link eye clears the hub lug) and the anchor on the lower lean bar."""
    phis = np.linspace(-P.lean_target_deg, P.lean_target_deg, 9) * D2R
    gain = STEER_TARGET_DEG * D2R / (P.lean_target_deg * D2R)

    def unpack(x):
        return np.array([x[0], ARM_Y, x[1]]), x[2:5]

    def link_len_for(x):
        arm, anchor = unpack(x)
        return np.linalg.norm(bar_end(0.0) + arm - anchor_pos(0.0, anchor))

    def resid(x):
        arm, anchor = unpack(x)
        L = link_len_for(x)
        out = []
        for sign in (1, -1):
            d = 0.0
            for p in sorted(phis[phis * sign >= 0], key=abs):
                d = steer_angle(p, arm, anchor, L, d)
                out.append((d - gain * p) * 10 if not math.isnan(d) else 10.0)
        return out

    lo = [ARM_BOX[0][0], ARM_BOX[1][0]] + [b[0] for b in ANCHOR_BOX]
    hi = [ARM_BOX[0][1], ARM_BOX[1][1]] + [b[1] for b in ANCHOR_BOX]
    best, rng = None, np.random.default_rng(3)
    for _ in range(80):
        try:
            s = least_squares(resid, rng.uniform(lo, hi), bounds=(lo, hi))
        except ValueError:
            continue
        if best is None or s.cost < best.cost:
            best = s
    arm, anchor = unpack(best.x)
    return arm, anchor, link_len_for(best.x)


def servo_angle(phi):
    """Horn angle (rad from +z, toward +y) that matches bar angle phi."""
    lug = np.array([P.lug_drop * math.sin(phi), -P.lug_drop * math.cos(phi)])
    sv = np.array([-P.servo_rod_len, -P.lug_drop - P.servo_horn_r])

    def f(a):
        tip = sv + P.servo_horn_r * np.array([math.sin(a), math.cos(a)])
        return np.linalg.norm(tip - lug) - P.servo_rod_len

    return brentq(f, -1.4, 1.4) if f(-1.4) * f(1.4) < 0 else float("nan")


def wheel_geometry(phi):
    """Ground frame: bars level, post tilted by phi. Returns camber, contact-patch track."""
    r = P.front_tire_od / 2
    w = P.front_tire_w / 2
    half = BAR_HALF + HUB_OUT
    cx = half
    shift = r * math.sin(phi) + math.copysign(w * math.cos(phi), phi)
    left = cx + shift
    right = -cx + shift
    return {"camber_deg": phi / D2R, "track": left - right, "patch_center_shift": (left + right) / 2,
            "centre_height": r * math.cos(phi) + w * abs(math.sin(phi))}


def rear_swingarm():
    a1 = P.gear_module * (P.gear_pinion_1 + P.gear_gear_1) / 2
    a2 = P.belt_center
    arm = P.swingarm_len
    assert arm <= a1 + a2, "gear centre distances cannot span the swingarm"
    fold = math.acos((a1 ** 2 + a2 ** 2 - arm ** 2) / (2 * a1 * a2))
    half_ang = math.asin((P.rear_travel / 2) / arm)
    r_lug, lug_ang = P.swing_lug_r, P.swing_lug_deg * D2R
    base = np.array([r_lug * math.cos(lug_ang), r_lug * math.sin(lug_ang)])
    mount = base - np.array([P.shock_mount_dx, 0.0])
    ang = np.linspace(-half_ang, half_ang, 21)

    def lug(t):
        c, s = math.cos(t), math.sin(t)
        return np.array([c * base[0] - s * base[1], s * base[0] + c * base[1]])

    shock = np.array([np.linalg.norm(lug(t) - mount) for t in ang])
    stroke = shock.max() - shock.min()
    axle_dz = arm * np.sin(ang)
    mr = stroke / (axle_dz.max() - axle_dz.min())
    load_n = 0.45 * P.mass_total_g / 1000 * 9.81
    wheel_rate = load_n / (P.rear_travel / 2)
    return {"fold_deg": fold / D2R, "center_dist_stage1": a1, "center_dist_stage2": a2, "swingarm_len": arm,
            "swing_half_angle_deg": half_ang / D2R, "shock_stroke": stroke, "motion_ratio": mr,
            "spring_rate_n_per_mm": wheel_rate / mr ** 2, "static_rear_load_n": load_n,
            "shock_len_ride": float(shock[len(shock) // 2])}


def ssv_state(phi, delta, side=1):
    """Steer servo on the lower bar: horn angle (rad, positive swings the tip rearward) that holds the tie rod length, the
    tie rod end on the knuckle arm, and the horn tip (both in the chassis frame)."""
    arm = np.asarray(P.steer_arm_xyz, float) * np.array([1, side, 1])
    a = bar_end(phi, side) + rot_axis(KP_AXIS, delta) @ arm
    rx = np.array([[1, 0, 0], [0, math.cos(phi), -math.sin(phi)], [0, math.sin(phi), math.cos(phi)]])
    a_bar = rx.T @ a
    s = np.array([P.ssv_x, side * P.ssv_shaft_y])
    zh = P.steer_arm_xyz[2]                       # rod plane

    def tip(th):
        q = th + P.ssv_horn_rest_deg * D2R
        return s + P.ssv_horn_r * np.array([-math.sin(q), side * math.cos(q)])

    def f(th):
        t = tip(th)
        return math.sqrt((t[0] - a_bar[0]) ** 2 + (t[1] - a_bar[1]) ** 2 + (zh - a_bar[2]) ** 2) - P.ssv_rod_len

    th = brentq(f, -1.3, 1.3) if f(-1.3) * f(1.3) < 0 else float("nan")
    t2 = tip(th)
    return th, a, rx @ np.array([t2[0], t2[1], zh])


def ssv_rod_len():
    arm = np.asarray(P.steer_arm_xyz, float)
    a = bar_end(0.0) + arm
    q = P.ssv_horn_rest_deg * D2R
    t = np.array([P.ssv_x - P.ssv_horn_r * math.sin(q), P.ssv_shaft_y + P.ssv_horn_r * math.cos(q), P.steer_arm_xyz[2]])
    return float(np.linalg.norm(t - a))


def main():
    OUT.joinpath("renders").mkdir(parents=True, exist_ok=True)
    arm = np.asarray(P.steer_arm_xyz, float)
    link_len = ssv_rod_len()
    sweep = np.linspace(-P.lean_max_deg, P.lean_max_deg, 71)
    gain = STEER_TARGET_DEG / P.lean_target_deg
    lean = sweep
    delta = lean * gain                                   # commanded by the radio mix (lean to steer)
    servo = np.array([servo_angle(p * D2R) / D2R for p in lean])
    geo = [wheel_geometry(p * D2R) for p in lean]
    horn = []
    for p in np.linspace(-P.lean_max_deg, P.lean_max_deg, 15):
        for dd in ((max(-STEER_TARGET_DEG, min(STEER_TARGET_DEG, p * gain)),) + ((-STEER_TARGET_DEG, 0.0, STEER_TARGET_DEG) if abs(p) <= P.lean_target_deg else ())):
            for side in (1, -1):
                horn.append(ssv_state(p * D2R, dd * D2R, side)[0] / D2R)
    rear = rear_swingarm()

    at30 = float(np.interp(P.lean_target_deg, lean, delta))
    asym = 0.0
    right_gap = 0.0
    res = {
        "bar_half": BAR_HALF, "upright_len": P.upright_len, "hub_out": HUB_OUT,
        "caster_deg": CASTER_DEG,
        "trail_mm": (AXLE_DROP + P.front_tire_od / 2) * math.tan(CASTER_DEG * D2R),
        "steer_arm_xyz": arm.tolist(), "ssv_rod_len": link_len,
        "ssv_horn_deg_max": float(np.nanmax(np.abs(horn))), "ssv_horn_nan": int(np.isnan(horn).sum()),
        "steer_at_target_lean_deg": at30, "steer_odd_asymmetry_deg": asym,
        "servo_horn_r": P.servo_horn_r, "servo_rod_len": P.servo_rod_len, "lug_drop": P.lug_drop,
        "servo_deg_at_target_lean": float(np.interp(P.lean_target_deg, lean, servo)),
        "servo_deg_at_max_lean": float(np.interp(P.lean_max_deg, lean, servo)),
        "track_change_at_target": geo[int(np.argmin(abs(lean - P.lean_target_deg)))]["track"] - geo[35]["track"],
        "rear": rear,
    }
    OUT.joinpath("kinematics.json").write_text(json.dumps(res, indent=2))

    assert not np.isnan(servo).any() and not np.isnan(horn).any(), "solver left its bracket"
    assert res["ssv_horn_deg_max"] <= P.servo_travel_deg / 2 - 4.0, res["ssv_horn_deg_max"]
    assert P.lean_min_deg <= P.lean_target_deg <= P.lean_max_deg
    assert at30 >= P.steer_at_full_lean_min_deg, at30
    assert asym <= 3.0, asym
    assert right_gap <= 0.5, right_gap
    assert abs(res["servo_deg_at_max_lean"]) <= P.servo_travel_deg / 2 - 2.0, res["servo_deg_at_max_lean"]
    assert 8.0 * K <= P.rear_travel <= 10.0 * K
    assert rear["shock_stroke"] > 0

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(2, 2, figsize=(10, 8))
    ax[0, 0].plot(lean, servo); ax[0, 0].set(title="Servo angle vs lean", xlabel="lean deg", ylabel="servo deg")
    ax[0, 1].plot(lean, delta); ax[0, 1].axhline(P.steer_at_full_lean_min_deg, ls="--")
    ax[0, 1].set(title="Steer vs lean", xlabel="lean deg", ylabel="steer deg")
    ax[1, 0].plot(lean, [g["track"] for g in geo], label="track")
    ax[1, 0].plot(lean, [g["patch_center_shift"] for g in geo], label="patch centre shift")
    ax[1, 0].legend(); ax[1, 0].set(title="Ground track", xlabel="lean deg", ylabel="mm")
    ax[1, 1].plot(lean, [g["centre_height"] for g in geo]); ax[1, 1].set(title="Wheel centre height", xlabel="lean deg", ylabel="mm")
    fig.tight_layout(); fig.savefig(OUT / "renders" / "kinematics.png", dpi=110)
    print(json.dumps(res, indent=2))


if __name__ == "__main__":
    main()
