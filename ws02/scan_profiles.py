"""Scan body profiles in the skin frame (uniform S = 391.14/351 about the nose; x_s = 34.3-(175.5-x)S, y_s = y S, z_s = 52.2+(z-40)S) -> scan/profiles.json
ridge (centre-line top), outline half width, flank floor (lowest z for |y| > 30), belt (top of the flank band at the fender apex line) at 26 stations."""
import json, numpy as np
D = "/Users/johndionaldo/Library/Application Support/Claude/scratch-workspaces/8645d517-f4a3-433c-8998-fd7c0e49ba87/a748fb05-e298-40e2-a797-544bc288ae5f/scratch-2026-10-30-ec4193/rev_trike_shell_v3"
z = np.load(D + "/solid.npz"); lo = z["lo"]; P = 0.5
b = np.load(D + "/body.npz")["body"]
nx, ny, nz = b.shape
X = lo[0] + P * np.arange(nx); Y = lo[1] + P * np.arange(ny); Z = lo[2] + P * np.arange(nz)
S = 391.14 / 351.0
rows = []
for t in np.linspace(0, 1, 27):
    xs = 175.0 - t * 350.0; i = int(round((xs - X[0]) / P)); sl = b[i]            # (ny, nz)
    if not sl.any(): continue
    jy, kz = np.nonzero(sl); yy, zz = Y[jy], Z[kz]
    ridge = zz[np.abs(yy) < 5].max() if (np.abs(yy) < 5).any() else np.nan
    hw = np.abs(yy).max()
    flank = zz[np.abs(yy) > 30]; fl = flank.min() if len(flank) else np.nan
    zhw = zz[np.abs(yy) > hw - 3].mean()                                              # height of the widest line (fender apex / shoulder)
    top_side = zz[(np.abs(yy) > hw - 12)].max()
    rows.append(dict(t=float(t), x=float(34.3 - (175.5 - xs) * S), ridge=float(52.2 + (ridge - 40) * S), hw=float(hw * S), floor=float(52.2 + (fl - 40) * S), z_apex=float(52.2 + (zhw - 40) * S), z_shoulder=float(52.2 + (top_side - 40) * S)))
json.dump(rows, open("scan/profiles.json", "w"), indent=0)
print(" t     x_s   ridge  halfw  floor  apex_z shoulder_z")
for r in rows: print("%.2f %7.1f %6.1f %6.1f %6.1f %6.1f %6.1f" % (r["t"], r["x"], r["ridge"], r["hw"], r["floor"], r["z_apex"], r["z_shoulder"]))
