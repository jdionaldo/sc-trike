import json
import math

import kinematics
from params import P


def test_params_match_solver():
    kinematics.main()
    r = json.loads(open("out/kinematics.json").read())
    assert math.isclose(P.bar_half, r["bar_half"], abs_tol=0.01)
    assert math.isclose(P.ssv_rod_len, r["ssv_rod_len"], abs_tol=0.05)
    assert math.isclose(P.steer_at_target_lean_deg, r["steer_at_target_lean_deg"], abs_tol=0.05)
    assert math.isclose(P.servo_deg_at_max_lean, r["servo_deg_at_max_lean"], abs_tol=0.05)
    assert math.isclose(P.swingarm_len, r["rear"]["swingarm_len"], abs_tol=0.01)
    assert math.isclose(P.shock_stroke, r["rear"]["shock_stroke"], abs_tol=0.05)
    assert math.isclose(P.spring_rate_n_per_mm, r["rear"]["spring_rate_n_per_mm"], abs_tol=0.02)


def test_phase1_requirements():
    assert P.steer_at_target_lean_deg >= P.steer_at_full_lean_min_deg
    assert P.servo_deg_at_max_lean <= P.servo_travel_deg / 2
    from params import K
    assert 8.0 * K <= P.rear_travel <= 10.0 * K
