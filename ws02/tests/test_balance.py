"""WS-03 weight balance: front share 63.5 to 65 %, sideways CG under 2 mm, ballast carrier inside the printable and clash-free envelope."""
import w3_mass
from parts import w3_balance as BAL
from w3_stretch import WHEELBASE


def test_front_share_and_sideways_cg():
    rows, M, cg = w3_mass.run()
    front = 100 * (cg[0] + WHEELBASE) / WHEELBASE
    assert 63.5 <= front <= 65.0, front
    assert abs(cg[1]) < 2.0, cg[1]


def test_ballast_carrier_clean():
    assert BAL.check(verbose=False) == []
