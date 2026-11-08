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
    from parts import w3_style as S, w3_shock as SK
    old = dict(YO=15.5, RT=2.4, RO=4.5, RW=3.5, LAT_TOP=2.7, LAT_BOT=1.6, CAR_RC=4.5,
               ARM_NODES={"L0": (-100.0, -9.0), "L1": (-60.0, -9.0), "L2": (0.0, -9.0), "U0": (-100.0, 10.5), "U1": (-76.0, 17.5), "U2": (-38.0, 11.5), "U3": (0.0, 9.4)},
               ARM_OUTER={"L0": (-100.0, -6.8), "L1": (-60.0, -6.8), "L2": (0.0, -6.8), "U0": (-100.0, 10.0), "U1": (-76.0, 15.5), "U2": (-38.0, 10.0), "U3": (0.0, 7.5)},
               TIE_R={"U0": 2.8, "U3": 2.8, "L0": 1.6, "L2": 2.4})
    keep_S = {k: getattr(S, k) for k in old}; keep_h = SK.HOOP_R
    for k, v in old.items():
        setattr(S, k, v)
    SK.HOOP_R = 6.5                                  # the validated models are the pre-fix geometry: freeze it while they are evaluated
    sys.modules.pop("w3_strength", None)
    try:
        with contextlib.redirect_stdout(buf):
            import w3_strength as OLD
    finally:
        for k, v in keep_S.items():
            setattr(S, k, v)
        SK.HOOP_R = keep_h
    open("WS03_STRENGTH.md", "w").write(keep)
    return [(n, v) for n, v in OLD.rows]


if __name__ == "__main__":
    for n, v in run()[:3]:
        print(f"{v:5.2f}  {n[:70]}")
