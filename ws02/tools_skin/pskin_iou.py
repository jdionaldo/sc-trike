"""Pixel IoU of a panel-skin mesh silhouette (top / side) against the user's masks + overlays. usage: python tools_skin/pskin_iou.py MESH.stl OUT_PREFIX (TABFREE=1: mask without the wing tab)"""
import sys
import numpy as np, trimesh, cv2
from shapely.geometry import Polygon
from shapely.ops import unary_union
import mask61 as M
pre = sys.argv[2]
meshes = [trimesh.load(sys.argv[1], force="mesh")]
def sil(cols):
    polys = []
    for m in meshes:
        v = m.vertices[:, cols]
        for f in m.faces:
            t = v[f]
            a = (t[1, 0] - t[0, 0]) * (t[2, 1] - t[0, 1]) - (t[1, 1] - t[0, 1]) * (t[2, 0] - t[0, 0])
            if abs(a) > 1e-9: polys.append(Polygon(t).buffer(0.02))
    return unary_union(polys)
def raster(g, shape, fn):
    img = np.zeros(shape, np.uint8)
    for gg in (g.geoms if hasattr(g, "geoms") else [g]):
        cv2.fillPoly(img, [np.array([fn(a, b) for a, b in gg.exterior.coords], np.int32)], 1)           # holes filled: the mask is a solid silhouette
    return img
import os
pm, sm = M.load("plan"), M.load("side")
if os.environ.get("TABFREE") == "1":                                   # mask without the wing / roll-bar tab (the wing is left out)
    _t = M.tab_free_top(M.edges(sm)[0])
    for _x in range(int(M.WING_X[0]), int(M.WING_X[1]) + 1):
        sm[:int(_t[_x]), _x] = 0
Hp, Wp = pm.shape; Hs, Ws = sm.shape
sp, ss = M.L_MM / (Wp - 1), M.L_MM / (Ws - 1)
pm = cv2.morphologyEx(pm, cv2.MORPH_CLOSE, np.ones((1, 7), np.uint8)); pm = cv2.morphologyEx(pm, cv2.MORPH_CLOSE, np.ones((5, 1), np.uint8))      # hairline gap at the centre line
res = {}
for name, cols, mk, fn, shape in (("plan", [0, 1], pm, lambda x, y: ((M.X_NOSE - x) / sp, Hp / 2.0 - y / sp), (Hp, Wp)), ("side", [0, 2], sm, lambda x, z: ((M.X_NOSE - x) / ss, Hs - 1 - (z - M.Z_SILL) / ss), (Hs, Ws))):
    g = sil(cols)
    if name == "plan":
        g = unary_union([g, __import__("shapely.affinity", fromlist=["x"]).scale(g, 1, -1, origin=(0, 0))])      # mirror: the mask is symmetric
    b = raster(g, shape, fn)
    inter = int((b & mk).sum()); uni = int((b | mk).sum())
    res[name] = inter / uni
    ov = np.zeros(shape + (3,), np.uint8); ov[mk > 0] = (255, 40, 40)                      # mask: red
    ov[(b > 0) & (mk == 0)] = (255, 255, 0)                                                # built outside the mask: yellow
    ov[(mk > 0) & (b == 0)] = (60, 60, 160)                                                # mask not covered: blue
    cs, _ = cv2.findContours(b, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    cv2.drawContours(ov, cs, -1, (255, 255, 255), 2)                                       # built outline: white
    sc = 1400.0 / ov.shape[1]; ov = cv2.resize(ov, None, fx=sc, fy=sc, interpolation=cv2.INTER_AREA)
    cv2.imwrite(f"{pre}{name}.png", ov[:, :, ::-1])
    print(f"{name}: IoU {res[name]:.4f}  (built {int(b.sum())} px, mask {int(mk.sum())} px, outside {int(((b>0)&(mk==0)).sum())}, missing {int(((mk>0)&(b==0)).sum())})")
