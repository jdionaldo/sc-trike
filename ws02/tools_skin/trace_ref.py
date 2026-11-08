"""Trace image 60 (6-view sheet with height contours) into numeric tables for the concept skin.
Writes ws02/skin_trace.npz: side top profile z(x), plan half width y(x), front-view section (half width vs z), and a height field Hn(x,y) from the contour colours.
Scales: x from the side view wheelbase (front axle px 200 -> x 0, 0.862 mm/px), nose clamped; top view mapped affinely onto the same x extent;
z: body height 256 px -> 169 mm above the frame floor (z -26); y: top-view body width -> 170 mm."""
import numpy as np, sys
from PIL import Image
from scipy import ndimage as ndi
SRC = sys.argv[1]
im = np.asarray(Image.open(SRC).convert("RGB")).astype(float)
sat = im.max(2) - im.min(2)
M = sat > 14
def clean(mask):
    mask = ndi.binary_closing(mask, iterations=3); mask = ndi.binary_fill_holes(mask)
    lab, n = ndi.label(mask); 
    if n > 1:
        sz = ndi.sum(mask, lab, range(1, n + 1)); mask = lab == (1 + int(np.argmax(sz)))
    return mask
# ---- side
sx0, sx1, sy0, sy1 = 100, 860, 30, 390
S = np.zeros_like(M); S[sy0:sy1, sx0:sx1] = M[sy0:sy1, sx0:sx1]; S = clean(S)
cols = np.nonzero(S.any(0))[0]; xl, xr = cols.min(), cols.max()
ztop_px = {c: np.nonzero(S[:, c])[0].min() for c in cols}
floor_px = np.nonzero(S)[0].max()
XS = 0.862; ZS = 169.0 / (floor_px - np.nonzero(S)[0].min())
X_NOSE = 45.0
def sx(px): return (200 - px) * XS
side = []
for c in range(xl, xr + 1, 8):
    if c in ztop_px: side.append((sx(c), -26.0 + (floor_px - ztop_px[c]) * ZS))
side.append((sx(xr), side[-1][1]))
# ---- top
tx0, tx1, ty0, ty1 = 880, 1450, 50, 350
T = np.zeros_like(M); T[ty0:ty1, tx0:tx1] = M[ty0:ty1, tx0:tx1]; T = clean(T)
cols = np.nonzero(T.any(0))[0]; tl, tr = cols.min(), cols.max()
rows = np.nonzero(T.any(1))[0]; cy = 0.5 * (rows.min() + rows.max()); YS = 170.0 / (rows.max() - rows.min())
x_front, x_rear = sx(xl), sx(xr); x_front = max(x_front, X_NOSE) if False else x_front
def tx(px): return x_front + (px - tl) / (tr - tl) * (x_rear - x_front)
half = []
for c in range(tl, tr + 1, 8):
    r = np.nonzero(T[:, c])[0]
    half.append((tx(c), 0.5 * (r.max() - r.min()) * YS))
# ---- front (rows -> half width), rear likewise
fx0, fx1, fy0, fy1 = 250, 720, 440, 800
F = np.zeros_like(M); F[fy0:fy1, fx0:fx1] = M[fy0:fy1, fx0:fx1]; F = clean(F)
rr = np.nonzero(F.any(1))[0]; ftop, fbot = rr.min(), rr.max(); FZ = 169.0 / (fbot - ftop); FY = 170.0 / (np.ptp(np.nonzero(F.any(0))[0]))
front = []
for r in range(ftop, fbot + 1, 6):
    c = np.nonzero(F[r])[0]; front.append((-26.0 + (fbot - r) * FZ, 0.5 * (c.max() - c.min()) * FY))
# ---- height field from top view colours: legend bar colours -> normalised height
LX, LY0, LY1 = 1750, 472, 780
leg = im[LY0:LY1, LX]                       # top = max (orange) .. bottom = baseline (blue)
legn = np.linspace(1.0, 0.0, len(leg))
rgb = im[ty0:ty1, tx0:tx1]
valid = T[ty0:ty1, tx0:tx1] & (sat[ty0:ty1, tx0:tx1] > 35)
d = ((rgb[:, :, None, :] - leg[None, None, ::3, :]) ** 2).sum(-1)
idx = d.argmin(2); err = d.min(2)
H = legn[::3][idx]; valid &= err < 1500
H = np.where(valid, H, np.nan)
# fill holes (line art) by nearest, smooth
mask = T[ty0:ty1, tx0:tx1]
ii = ndi.distance_transform_edt(np.isnan(H), return_distances=False, return_indices=True)
Hf = H[tuple(ii)]; Hf = ndi.gaussian_filter(Hf, 5); Hf[~mask] = 0
# resample onto a mm grid
gx = np.arange(-470, 61, 5.0); gy = np.arange(-100, 101, 5.0)
Hg = np.zeros((len(gx), len(gy)))
for i, x in enumerate(gx):
    p = (x - x_front) / (x_rear - x_front) * (tr - tl) + tl - tx0
    for j, y in enumerate(gy):
        q = cy - ty0 - y / YS
        Hg[i, j] = ndi.map_coordinates(Hf, [[q], [p]], order=1, mode="nearest")[0] if 0 <= p < Hf.shape[1] else 0
np.savez("skin_trace.npz", side=np.array(side), half=np.array(half), front=np.array(front), gx=gx, gy=gy, H=Hg, x_front=x_front, x_rear=x_rear)
print("x extent", x_front, x_rear, "side max z", max(z for _, z in side), "half max", max(h for _, h in half), "front max half", max(h for _, h in front))
print("side", [(round(a), round(b)) for a, b in side[::6]])
print("half", [(round(a), round(b)) for a, b in half[::6]])
print("front", [(round(a), round(b)) for a, b in front[::5]])
