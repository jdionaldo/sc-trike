"""Measure the scan body (read-only copies of rev_trike_shell_v3/body.npz) and cache height maps in ws02/scan/. Frame: scan x forward, y lateral, z up (0.5 mm voxels)."""
import numpy as np
D = "/Users/johndionaldo/Library/Application Support/Claude/scratch-workspaces/8645d517-f4a3-433c-8998-fd7c0e49ba87/a748fb05-e298-40e2-a797-544bc288ae5f/scratch-2026-10-30-ec4193/rev_trike_shell_v3"
z = np.load(D + "/solid.npz"); lo = z["lo"]; P = float(z["P"])
b = np.load(D + "/body.npz")["body"]
ii, jj, kk = np.nonzero(b)
ext = [(lo[a] + P * v.min(), lo[a] + P * v.max()) for a, v in enumerate((ii, jj, kk))]
print("pitch", P, "lo", lo, "body extents (x,y,z)", [tuple(round(float(t), 1) for t in e) for e in ext])
nx, ny, nz = b.shape
X = lo[0] + P * np.arange(nx); Y = lo[1] + P * np.arange(ny); Z = lo[2] + P * np.arange(nz)
top = np.where(b.any(2), Z[(b * np.arange(nz)).argmax(2) if False else (nz - 1 - np.argmax(b[:, :, ::-1], axis=2))], np.nan)
bot = np.where(b.any(2), Z[np.argmax(b, axis=2)], np.nan)
np.savez_compressed("scan/maps.npz", X=X, Y=Y, Z=Z, top=top, bot=bot, body_x=np.array(ext[0]), sil_side=b.any(1), sil_top=b.any(2), sil_front=b.any(0))
