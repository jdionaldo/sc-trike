"""WS-03 strength regression: every row of the review must stay above its minimum factor of safety (frame 2.0, arms 3.0, wing hangers 2.5, hinge lugs 2.0, others 2.0;
abuse cases 1.0; sustained loads 1.5).  Rows that are known to be below their minimum today (see WS03_STRENGTH_FIXES.md) are xfail on the minimum but may never get worse
than 90 % of the recorded baseline (tests/strength_baseline.json).  Run `python w3_strength_report.py` after a deliberate geometry change to re-record the baseline."""
import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import w3_strength_review as R

HERE = os.path.dirname(__file__)
BASE = json.load(open(os.path.join(HERE, "strength_baseline.json")))
ROWS = R.run()
KEYS = [R.row_key(r) for r in ROWS]


@pytest.mark.parametrize("r,key", list(zip(ROWS, KEYS)), ids=[k[:90] for k in KEYS])
def test_minimum(r, key, request):
    if BASE.get(key, 1e9) < r["min"]:
        why = "accepted abuse case: no printed arm survives a 1 m drop on the rear wheel (7.8 J vs under 1 J absorbed), see WS03_STRENGTH_FIXES.md" if "1 m drop" in key else "known below minimum, see WS03_STRENGTH_FIXES.md"
        request.applymarker(pytest.mark.xfail(reason=why, strict=False))
    assert r["fs"] >= r["min"], f"{key}: FS {r['fs']:.2f} < {r['min']}"


@pytest.mark.parametrize("r,key", list(zip(ROWS, KEYS)), ids=[k[:90] for k in KEYS])
def test_no_regression(r, key):
    assert key in BASE, "new row: run w3_strength_report.py to record it"
    assert r["fs"] >= 0.9 * BASE[key], f"{key}: FS {r['fs']:.2f} fell below 90 % of the baseline {BASE[key]:.2f}"


def test_solver_reproduces_old_factors():
    import w3_strength_validate as V
    got = [v for _, v in V.run()[:3]]
    for g, want in zip(got, (3.8, 4.3, 2.95)):
        assert abs(g - want) < 0.1
