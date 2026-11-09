"""Overlay the built skin silhouette (red fill outline) on sheet 61 per view. usage: python tools_skin/overlay61.py SHEET OUT_PREFIX [STL]"""
import sys, math
import numpy as np, trimesh
from PIL import Image, ImageDraw
import trace61 as T
SHEET, PRE = sys.argv[1], sys.argv[2]
STL = sys.argv[3] if len(sys.argv) > 3 else "out/mono3_facet/body3.stl"
m = trimesh.load(STL)
im = Image.open(SHEET).convert("RGB")
c, s = math.cos(T.RAKE), math.sin(T.RAKE)


def side_px(x, z):
    u, v = x * c + z * s, z * c - x * s
    if u >= T.u_of(T.XA):
        px = T.FAX_PX - u / T.S
    elif u >= T.u_of(T.XB):
        px = T.XA + (T.u_of(T.XA) - u) / (T.S * T.K)
    else:
        px = T.FAX_PX - (u + T.EXTRA) / T.S
    return px, T.FAX_PY - v / T.S


def top_px(x, y):
    sp, _ = side_px(x, 0.0)
    tx = T.TNOSE + (sp - T.NOSE_PX) * (T.TTAIL - T.TNOSE) / (T.TAIL_PX - T.NOSE_PX)
    return tx, 211.0 - y / T.HW


def polys(normal):
    p = m.projected(normal=normal, origin=[0, 0, 0], ignore_sign=True)
    return p.geoms if hasattr(p, "geoms") else [p]


def draw(box, name, fn, normal, scale=2.0):
    cr = im.crop(box).resize((int((box[2] - box[0]) * scale), int((box[3] - box[1]) * scale)), Image.LANCZOS)
    ov = Image.new("RGBA", cr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    p3 = m.projected(normal=normal, origin=[0, 0, 0], ignore_sign=True)
    for g in (p3.geoms if hasattr(p3, "geoms") else [p3]):
        for ring in [g.exterior] + list(g.interiors):
            pts = []
            for a, b in ring.coords:
                x, y = fn(a, b)
                pts.append(((x - box[0]) * scale, (y - box[1]) * scale))
            if ring is g.exterior:
                d.polygon(pts, fill=(255, 40, 40, 70))
            d.line(pts + [pts[0]], fill=(200, 0, 0, 255), width=2)
    out = Image.alpha_composite(cr.convert("RGBA"), ov).convert("RGB")
    out.save(PRE + name + ".png")


# projected(normal) returns 2D coords in an arbitrary frame: use explicit projections instead
def proj(axis_drop):
    return axis_drop
from shapely.geometry import MultiPolygon, Polygon
from shapely.ops import unary_union


def silhouette(cols):
    v = m.vertices[:, cols]
    tris = [Polygon(v[f]) for f in m.faces if abs((v[f[1]][0]-v[f[0]][0])*(v[f[2]][1]-v[f[0]][1])-(v[f[1]][1]-v[f[0]][1])*(v[f[2]][0]-v[f[0]][0])) > 1e-9]
    return unary_union([t.buffer(0.01) for t in tris])


def draw2(box, name, cols, fn, scale=2.0):
    cr = im.crop(box).resize((int((box[2] - box[0]) * scale), int((box[3] - box[1]) * scale)), Image.LANCZOS)
    ov = Image.new("RGBA", cr.size, (0, 0, 0, 0)); d = ImageDraw.Draw(ov)
    g = silhouette(cols)
    for gg in (g.geoms if hasattr(g, "geoms") else [g]):
        pts = [((fn(a, b)[0] - box[0]) * scale, (fn(a, b)[1] - box[1]) * scale) for a, b in gg.exterior.coords]
        d.polygon(pts, fill=(255, 40, 40, 80)); d.line(pts, fill=(200, 0, 0, 255), width=2)
    Image.alpha_composite(cr.convert("RGBA"), ov).convert("RGB").save(PRE + name + ".png")


draw2((60, 430, 880, 800), "side", [0, 2], side_px)
draw2((90, 20, 860, 380), "top", [0, 1], top_px)
# front / rear: scale to the sheet's body height and width (sheet views are not at the side view scale)
zmax, zmin, ymax = m.bounds[1][2], m.bounds[0][2], m.bounds[1][1]
def front_px(y, z, cx, top=45.0, hwpx=158.0):
    k = hwpx / ymax
    return cx + y * k, top + (zmax - z) * (338.0 / (zmax + 56.0 + 0.0)) * 1.0
draw2((990, 20, 1440, 400), "front", [1, 2], lambda y, z: front_px(y, z, 1216.0), 2.2)
draw2((1490, 20, 1940, 400), "rear", [1, 2], lambda y, z: front_px(y, z, 1717.0), 2.2)
print("ok")
