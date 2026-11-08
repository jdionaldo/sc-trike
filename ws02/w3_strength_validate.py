"""Validate the review FE solver: re-run the OLD w3_strength.py model (old loads, old restraints, 25 MPa, no stress concentration) with the new FE class
substituted for w3_beamfe.Truss.  The factors of safety must match WS03_STRENGTH's old table (front arm 3.8, rear arm 4.3, frame 2.5)."""
import sys, os, io, contextlib
import numpy as np
import w3_strength_review as R


class Truss2:
    def __init__(self):
        self.fe = R.FE()

    def node(self, n, p):
        self.fe.node(n, p)

    def edge(self, a, b, r):
        self.fe.edge(a, b, r)

    def solve(self, loads, fixed):
        r = self.fe.solve(loads, {n: "all" for n in fixed}, (0, 0, 1))
        return 1.0 / r["fs"], r["member"], r["defl"]          # allow = 1 (SIP = SZ = 1, KT = 1)


def run():
    R.SIP = R.SZ = 1.0; R.KT = 1.0
    import w3_beamfe
    w3_beamfe.Truss = Truss2
    buf = io.StringIO()
    keep = open("WS03_STRENGTH.md").read()
    with contextlib.redirect_stdout(buf):
        import w3_strength as OLD
    open("WS03_STRENGTH.md", "w").write(keep)
    return [(n, v) for n, v in OLD.rows]


if __name__ == "__main__":
    for n, v in run()[:3]:
        print(f"{v:5.2f}  {n[:70]}")
