"""Height-field cap for the concept skin: the surface height at every plan position follows the contour map of the reference sheet
(image 60; skin_trace.npz from tools_skin/trace_ref.py). z(x,y) = roof(x) - (Hc(x) - H(x,y)) * RANGE, floored at Z_MIN."""
from pathlib import Path
import numpy as np
import trimesh
from scipy import ndimage as ndi

RANGE = 169.0           # mm of height the legend range (blue..orange) stands for
Z_MIN = 20.0            # lowest the cap may drop (sill line)
_d = np.load(Path(__file__).with_name("skin_trace.npz"))
GX, GY = _d["gx"], _d["gy"]
_H = _d["H"]
_H = 0.5 * (_H + _H[:, ::-1])                          # symmetrise about the centre line
_H = ndi.gaussian_filter(_H, 2.5)
_side = _d["side"]
def roof(x):
    o = np.argsort(_side[:, 0]); return np.interp(x, _side[o, 0], _side[o, 1])
_Hc = _H.max(1)
def field():
    z = np.empty_like(_H)
    for i, x in enumerate(GX):
        z[i] = np.maximum(roof(x) - np.maximum(_Hc[i] - _H[i] - 0.04, 0.0) * RANGE, Z_MIN)
    return ndi.gaussian_filter(z, 1.0)
Z0 = field()
_ux = ndi.zoom(Z0, 2, order=3)
Z = _ux[:2 * Z0.shape[0] - 1, :2 * Z0.shape[1] - 1]
GX = np.linspace(GX[0], GX[-1], Z.shape[0]); GY = np.linspace(GY[0], GY[-1], Z.shape[1])

def cap_mesh(inset=0.0, zbot=-80.0):
    """Closed solid under the surface z(x,y) - inset/cos(theta) over the grid (plan clipping is left to the plan prism)."""
    zz = Z.copy()
    gx_, gy_ = np.gradient(zz, GX, GY)
    zz = zz - inset * np.sqrt(1.0 + gx_ ** 2 + gy_ ** 2)
    nx, ny = zz.shape
    V = np.zeros((nx, ny, 2, 3))
    X, Y = np.meshgrid(GX, GY, indexing="ij")
    V[:, :, 0, 0] = X; V[:, :, 0, 1] = Y; V[:, :, 0, 2] = zz
    V[:, :, 1, 0] = X; V[:, :, 1, 1] = Y; V[:, :, 1, 2] = zbot
    idx = lambda i, j, k: (i * ny + j) * 2 + k
    F = []
    for i in range(nx - 1):
        for j in range(ny - 1):
            a, b, c, d = idx(i, j, 0), idx(i + 1, j, 0), idx(i + 1, j + 1, 0), idx(i, j + 1, 0)
            F += [(a, b, c), (a, c, d)]
            a, b, c, d = idx(i, j, 1), idx(i + 1, j, 1), idx(i + 1, j + 1, 1), idx(i, j + 1, 1)
            F += [(a, c, b), (a, d, c)]
    for i in range(nx - 1):                                        # walls at y = min / max
        for j, flip in ((0, True), (ny - 1, False)):
            a, b, c, d = idx(i, j, 0), idx(i + 1, j, 0), idx(i + 1, j, 1), idx(i, j, 1)
            F += [(a, c, b), (a, d, c)] if flip else [(a, b, c), (a, c, d)]
    for j in range(ny - 1):                                        # walls at x = min / max
        for i, flip in ((0, False), (nx - 1, True)):
            a, b, c, d = idx(i, j, 0), idx(i, j + 1, 0), idx(i, j + 1, 1), idx(i, j, 1)
            F += [(a, c, b), (a, d, c)] if flip else [(a, b, c), (a, c, d)]
    m = trimesh.Trimesh(V.reshape(-1, 3), np.array(F), process=False)
    m.fix_normals()
    return m

from scipy.interpolate import RegularGridInterpolator
_zi = RegularGridInterpolator((GX, GY), Z, bounds_error=False, fill_value=None)
def zat(x, y):
    return float(_zi([[x, y]])[0])
