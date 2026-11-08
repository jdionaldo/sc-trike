"""Before/after renders: current skin, concept skin, reference GLB (shell only, scaled to the build). Painter's-algorithm orthographic views -> PNG.
usage: python tools_skin/render_compare.py OUTDIR"""
import sys
from pathlib import Path
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont

REF = "/Users/johndionaldo/Documents/Shapecast/Library/screenshot-2026-11-08-at-8-41-26-am-d2cdbd13/final.glb"


def load_ref(length_mm):
    s = trimesh.load(REF)
    m = list(s.geometry.values())[0].copy()
    v = np.asarray(m.vertices)
    v = np.c_[v[:, 2], -v[:, 0], v[:, 1]]                       # glb (x width, y up, z length, nose +z) -> (fwd, left, up)
    v = v * (length_mm / np.ptp(v[:, 0]))
    m.vertices = v
    return m


def view_basis(kind):
    if kind == "top":
        return np.array([[0, -1, 0], [1, 0, 0], [0, 0, 1.0]])         # screen right = fwd, screen up = left, depth = up
    if kind == "side":
        return np.array([[0, -1, 0], [0, 0, 1], [1, 0, 0.0]]) @ np.eye(3)
    a, e = np.radians(-35.0), np.radians(28.0)                        # iso: rear-left-above
    R1 = np.array([[np.cos(a), -np.sin(a), 0], [np.sin(a), np.cos(a), 0], [0, 0, 1]])
    R2 = np.array([[1, 0, 0], [0, np.cos(e), -np.sin(e)], [0, np.sin(e), np.cos(e)]])
    return R2 @ R1


def render(m, kind, size=(900, 420), col=(120, 150, 200), scale=None, center=None):
    v = np.asarray(m.vertices, float); f = np.asarray(m.faces)
    if kind == "top":
        P = np.c_[v[:, 0], v[:, 1], v[:, 2]]; sx, sy, sd = P[:, 0], P[:, 1], P[:, 2]
    elif kind == "side":
        sx, sy, sd = v[:, 0], v[:, 2], -v[:, 1]
    else:
        B = view_basis("iso"); P = v @ B.T; sx, sy, sd = P[:, 0], P[:, 2], -P[:, 1]
    tri = np.stack([sx, sy, sd], 1)[f]
    sc = scale or 0.92 * min(size[0] / np.ptp(sx), size[1] / np.ptp(sy))
    c = center if center is not None else (0.5 * (sx.min() + sx.max()), 0.5 * (sy.min() + sy.max()))
    X = (tri[:, :, 0] - c[0]) * sc + size[0] / 2; Y = size[1] / 2 - (tri[:, :, 1] - c[1]) * sc
    n = np.cross(v[f[:, 1]] - v[f[:, 0]], v[f[:, 2]] - v[f[:, 0]]); n /= np.linalg.norm(n, axis=1, keepdims=True) + 1e-12
    if kind == "iso":
        n = n @ B.T
        L = np.array([-0.4, -0.5, 0.75])
    elif kind == "top":
        L = np.array([-0.3, 0.2, 0.9])
    else:
        L = np.array([0.3, -0.6, 0.6])
    if kind == "side":
        nn = np.c_[n[:, 0], n[:, 2], -n[:, 1]]; L = np.array([0.3, 0.6, 0.7])
    elif kind == "top":
        nn = n
    else:
        nn = np.c_[n[:, 0], n[:, 2], -n[:, 1]]; L = np.array([-0.4, 0.75, 0.5])
    L = L / np.linalg.norm(L)
    sh = np.clip(np.abs(nn @ L), 0, 1) * 0.75 + 0.25
    order = np.argsort(tri[:, :, 2].mean(1))
    im = Image.new("RGB", size, (255, 255, 255)); d = ImageDraw.Draw(im)
    for i in order:
        d.polygon([(X[i, 0], Y[i, 0]), (X[i, 1], Y[i, 1]), (X[i, 2], Y[i, 2])], fill=tuple(int(sh[i] * k) for k in col))
    return im, sc, c


def outline(im, sc, c, size, pts, mirror=False):
    d = ImageDraw.Draw(im)
    for sgn in ((1, -1) if mirror else (1,)):
        xy = [((x - c[0]) * sc + size[0] / 2, size[1] / 2 - (sgn * v - c[1]) * sc) for x, v in pts]
        d.line(xy, fill=(220, 30, 30), width=3)


def drawing(n, size, crop):
    n = "59"
    im = Image.open(f"/private/tmp/claude-501/-Users-johndionaldo-Library-Application-Support-Claude-scratch-workspaces-8645d517-f4a3-433c-8998-fd7c0e49ba87-a748fb05-e298-40e2-a797-544bc288ae5f-scratch-2026-10-30-ec4193/0d275d42-fddc-4cbd-9c02-604bf37928ec/images/{n}.webp").convert("RGB").crop(crop)
    return im.resize((size[0], int(im.height * size[0] / im.width)))


def stations(m, xs):
    out = []
    for x in xs:
        sec = m.section(plane_origin=(x, 0, 0), plane_normal=(1, 0, 0))
        if sec is None:
            out.append((x, float("nan"), float("nan"))); continue
        v = sec.vertices
        out.append((x, float(np.abs(v[:, 1]).max()), float(v[:, 2].max())))
    return out


def main(out):
    import ref_outline as R
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    cur = trimesh.load("out/mono3/body3.stl"); con = trimesh.load("out/mono3_concept/body3.stl")
    ref = load_ref(float(np.ptp(con.vertices[:, 0])))
    font = ImageFont.load_default()
    C = (-130, 0)
    for kind, size in (("top", (900, 340)), ("side", (900, 360)), ("iso", (900, 480)), ("front", (520, 330))):
        cols = []
        for name, m, colr in (("current skin", cur, (130, 150, 175)), ("NEW concept skin", con, (180, 110, 150))):
            if kind in ("top", "side"):
                sc = 1.42
                im, sc, c = render(m, kind, size, colr, scale=sc, center=(-185.0, 0.0 if kind == "top" else 40.0))
                if kind == "top":
                    outline(im, sc, c, size, R.REF_HALF, mirror=True)
                else:
                    outline(im, sc, c, size, R.REF_TOP)
            elif kind == "front":
                im, sc, c = render(m, "front", size, colr, scale=1.6, center=(0.0, 45.0))
            else:
                im, _, _ = render(m, kind, size, colr)
            ImageDraw.Draw(im).text((8, 6), f"{name} - {kind}" + (" (red = reference outline)" if kind in ("top", "side") else ""), fill=(0, 0, 0), font=font)
            cols.append(im)
        if kind == "top":
            r = drawing("54", (900, 340), (60, 575, 1160, 1050))
        elif kind == "side":
            r = drawing("55", (900, 360), (90, 30, 1160, 545))
        else:
            r, _, _ = render(ref, kind, size, (120, 160, 120))
        ImageDraw.Draw(r).text((8, 6), f"reference - {kind}" + (" (drawing)" if kind in ("top", "side") else " (Shapecast GLB)"), fill=(0, 0, 0), font=font)
        cols.append(r)
        sheet = Image.new("RGB", (size[0], sum(c.height for c in cols)), (255, 255, 255)); y = 0
        for c_ in cols:
            sheet.paste(c_, (0, y)); y += c_.height
        sheet.save(out / f"compare_{kind}.png")
    xs = [30, 0, -52, -105, -200, -290, -350, -400]
    a, b = stations(cur, xs), stations(con, xs)
    rows = ["| x | half-width cur | new | ref | top z cur | new | ref |", "|---|---|---|---|---|---|---|"]
    for (x, hc, zc), (_, hn, zn) in zip(a, b):
        rows.append(f"| {x} | {hc:.0f} | {hn:.0f} | {R.half(x):.0f} | {zc:.0f} | {zn:.0f} | {R.top(x):.0f} |")
    for nm, m in (("current", cur), ("new", con)):
        e = m.bounds; rows.append(f"| bbox {nm} | L {e[1][0]-e[0][0]:.0f} W {e[1][1]-e[0][1]:.0f} H {e[1][2]-e[0][2]:.0f} | | | | | |")
    def summ(m):
        v = m.vertices; k = v[(v[:, 0] < -150) & (v[:, 0] > -290)]; d = v[(v[:, 0] < -380) & (v[:, 0] > -420)]
        return dict(L=np.ptp(v[:, 0]), W=np.ptp(v[:, 1]), H=v[:, 2].max() + 26.0, nose=v[:, 0].max(), canopy=k[:, 2].max(), deck=d[:, 2].max())
    sc_, sn_ = summ(cur), summ(con)
    ref_ = dict(L=55 + 468, W=182, H=130 + 26.0, nose=55, canopy=130, deck=R.top(-400))
    rows += ["", "| dimension (mm) | before | new | reference |", "|---|---|---|---|"]
    for key, nm in (("L", "length"), ("W", "width"), ("H", "height above floor"), ("nose", "nose tip x"), ("canopy", "canopy top z"), ("deck", "deck z at x -400")):
        rows.append(f"| {nm} | {sc_[key]:.0f} | {sn_[key]:.0f} | {ref_[key]:.0f} |")
    open(out / "table.md", "w").write(chr(10).join(rows)); print(chr(10).join(rows))


if __name__ == "__main__":
    main(sys.argv[1])
