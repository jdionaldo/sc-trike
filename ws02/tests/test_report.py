import report
from params import P


def test_mass_matches_assumption_and_cg_is_balanced():
    for key, r in {"default": report.tip_over(0.0)}.items():
        assert abs(r["mass_g"] - P.mass_total_g) < 0.1 * P.mass_total_g, r["mass_g"]
        front_share = 1 - r["cg_chassis"][0] / P.axle_xz[0]
        assert 0.35 < front_share < 0.65, front_share


def test_static_tip_over_margin_at_full_lean():
    for lean in (P.lean_target_deg, -P.lean_target_deg):
        assert report.tip_over(lean)["min_margin_mm"] > 10.0
