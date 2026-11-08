"""WS-03 drivetrain checks: stock gear geometry, backlash window, shaft spans, ratio chain (numbers from w3_stock.py)."""
import math

import w3_stock as K


def test_backlash_window():
    assert 0.1 <= K.SPUR_BACKLASH <= 0.3
    assert 0.1 <= K.BEV_BACKLASH <= 0.3


def test_crossover_meshes_at_centre_distance():
    xo = K.XO
    dist = lambda a, b: math.hypot(xo[a][0] - xo[b][0], xo[a][1] - xo[b][1])
    assert abs(dist("P1", "Pa") - ((K.pd(13) + K.pd(27)) / 2 + K.CD_ADD)) < 1e-6
    assert abs(dist("Pa", "Pb") - (K.pd(27) + K.CD_ADD)) < 1e-6
    assert abs(dist("Pb", "P0") - ((K.pd(27) + K.pd(40)) / 2 + K.CD_ADD)) < 1e-6
    for a, b in (("P1", "Pb"), ("P1", "P0"), ("Pa", "P0")):          # gears that must not touch
        assert dist(a, b) > K.XO_R[a] + K.XO_R[b] + 1.0


def test_shaft_spans_under_40mm():
    f = sorted(0.5 * (b[0] + b[1]) for b in K.F_BRG) + [0.5 * sum(K.C_BRG_F)]
    assert max(b - a for a, b in zip(f, f[1:])) < 40.0
    r = [0.5 * sum(K.C_BRG_A), K.PILLOW_X, 0.5 * sum(K.R_BRG[1]), 0.5 * sum(K.R_BRG[0])]
    assert max(a - b for a, b in zip(r, r[1:])) < 40.0, r


def test_ratio_chain():
    r = K.ratios()
    assert 8.5 <= r["total"] <= 9.5
    assert 38.0 <= r["kmh_loaded"] <= 46.0
    assert abs(r["mismatch"] - 1.0) < 0.2


def test_stock_shaft_lengths():
    assert K.SHAFT_FRONT == K.SHAFT_REAR == 102.0
