"""Re-evaluate the review with candidate geometry fixes patched in memory (nothing on disk changes).  Used to put expected factors in WS03_STRENGTH_FIXES.md."""
import copy
import w3_strength_review as R
from parts import w3_style as S, w3_shock as SK, w3_frame as F


def fs(part, case):
    R.ROWS.clear(); R.checks()
    return min(r["fs"] for r in R.ROWS if part in r["part"] and case in r["case"])


def trial(label, patch, undo, items):
    patch()
    out = {i: round(fs(*i), 2) for i in items}
    undo()
    print(label, out)
    return out


if __name__ == "__main__":
    base = {"arm": ("Front arm (beam", "3 g bump, one"), "rear": ("Rear swing arm", "3 g bump, rear"), "fr": ("Cage frame", "3 g bump, one front"), "frr": ("Cage frame", "rear wheel"),
            "drive": ("Rear swing arm", "drive"), "sus": ("Rear swing arm", "sustained")}
    items = list(base.values())
    trial("base", lambda: None, lambda: None, items)
    t0 = dict(S.TIE_R)
    trial("tie U0/L0 r5/r3.5", lambda: S.TIE_R.update(U0=5.0, L0=3.5), lambda: S.TIE_R.update(t0), items[:1])
    R_front = R.front_arm
    def two_lugs():
        old = R.front_arm
        def fa():
            t, yi, yo = R.front_arm_model()
            res = {}
            for name, (fx, fy, n) in R.FRONT_CASES.items():
                r = t.solve(R.hub_loads(fx, fy, n, yi, yo), {"Pi": [0, 1, 2], "Po": [0, 1, 2], "U1i": [2], "U1o": [2]}, (0, 1, 0))
                pr = sum(r["react"][k][:3] for k in ("Pi", "Po")); res[name] = (r, pr, r["react"]["U1i"][2], (fx, fy, n))
            return res
        R.front_arm = fa
    trial("second lug on the outer plane", two_lugs, lambda: setattr(R, "front_arm", R_front), items[:1])
    def both():
        two_lugs(); S.TIE_R.update(U0=5.0, L0=3.5)
    trial("two lugs + ties", both, lambda: (setattr(R, "front_arm", R_front), S.TIE_R.update(t0)), items[:1])
    h0, l0 = SK.HOOP_R, SK.LEG_R
    trial("hoop cross tube r8.5", lambda: setattr(SK, "HOOP_R", 8.5), lambda: setattr(SK, "HOOP_R", h0), items[1:2] + items[4:])
    trial("hoop cross tube r10", lambda: setattr(SK, "HOOP_R", 10.0), lambda: setattr(SK, "HOOP_R", h0), items[1:2] + items[4:])
    trial("hoop r8.5 + legs r8", lambda: (setattr(SK, "HOOP_R", 8.5), setattr(SK, "LEG_R", 8.0)), lambda: (setattr(SK, "HOOP_R", h0), setattr(SK, "LEG_R", l0)), items[1:2] + items[4:])
    e0 = list(F.EDGES)
    def thick(names, r):
        F.EDGES[:] = [(a, b, (r if (a, b) in names else rr), ta, tb) for a, b, rr, ta, tb in e0]
    names = {("PS1", "FN"), ("PS2", "PL"), ("PE1", "PL"), ("FN", "PL"), ("PS2", "PM"), ("PM", "PS1"), ("PE1", "PS2")}
    trial("frame PS/FN/PL ring r4.5", lambda: thick(names, 4.5), lambda: F.EDGES.__setitem__(slice(None), e0), [base["fr"], base["frr"]])
    names2 = names | {("B1", "FPB"), ("R1", "FPR"), ("K2", "FPB"), ("R3", "K2"), ("B1", "R1"), ("PE1", "B1")}
    trial("frame + B1/FPB/K2 r5.5", lambda: thick(names2, 5.5), lambda: F.EDGES.__setitem__(slice(None), e0), [base["fr"], base["frr"]])
    sh = R.EAR_SHARE
    trial("ear share 0.1 (diff case bolted to plate)", lambda: setattr(R, "EAR_SHARE", 0.1), lambda: setattr(R, "EAR_SHARE", sh), [base["fr"]])
