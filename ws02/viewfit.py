"""Review renders of the fitted skin: python viewfit.py <outprefix> [lean steer].  Half section (y <= 0) seen from +y, top section (z <= zcut) from above, 3/4 views."""
import sys
import numpy as np
import trimesh
import zrender as Z
import w3_assembly as A

COL = {"skin": (0.82, 0.42, 0.40), "cage": (0.35, 0.55, 0.85), "tyre": (0.25, 0.25, 0.27), "print": (0.80, 0.78, 0.55), "bought": (0.55, 0.75, 0.55)}


def groups(items):
    out = []
    for n, m, k in items:
        if n.startswith("body3_"):
            g = "skin"
        elif n.startswith("w3_frame") or n.startswith("w3_deck") or n.startswith("w3_tail"):
            g = "cage"
        elif "tire" in n or "rim" in n:
            g = "tyre"
        else:
            g = "print" if k == "printed" else "bought"
        out.append((n, m, g))
    return out


def clip(m, origin, normal):
    try:
        c = m.slice_plane(origin, normal, cap=False)
        return c if len(c.faces) else None
    except Exception:
        return None


def make(prefix, lean=0.0, steer=0.0, size=(1400, 760)):
    items = groups(A.assembly(lean, steer=steer))
    views = {}
    # half section: keep y <= 0
    sec = [(clip(m, [0, 0, 0], [0, -1, 0]), g) for n, m, g in items]
    sec = [(m, g) for m, g in sec if m is not None]
    Z.render([m for m, g in sec], [COL[g] for m, g in sec], f"{prefix}_side_section.png", eye=(-190, 900, 30), target=(-190, 0, 30), up=(0, 0, 1), size=size, ortho_h=330, title="side half-section (y<=0 seen from +y)")
    top = [(clip(m, [0, 0, 20.0], [0, 0, -1]), g) for n, m, g in items]
    top = [(m, g) for m, g in top if m is not None]
    Z.render([m for m, g in top], [COL[g] for m, g in top], f"{prefix}_top_section.png", eye=(-190, 0, 900), target=(-190, 0, 0), up=(1, 0, 0), size=(1400, 700), ortho_h=520, title="top section (z<=20)")
    full = [(m, g) for n, m, g in items]
    Z.render([m for m, g in full], [COL[g] for m, g in full], f"{prefix}_q34.png", eye=(250, -700, 400), target=(-190, 0, 20), up=(0, 0, 1), size=size, ortho_h=560, title="3/4 front-left")
    Z.render([m for m, g in full], [COL[g] for m, g in full], f"{prefix}_q34r.png", eye=(-650, 700, 350), target=(-190, 0, 20), up=(0, 0, 1), size=size, ortho_h=560, title="3/4 rear-right")


if __name__ == "__main__":
    make(sys.argv[1])
