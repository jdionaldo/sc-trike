"""Surface points of the scan solid (with wheels) and of the body only, in scan frame mm (read-only use of rev_trike_shell_v3)."""
import numpy as np
from scipy import ndimage as ndi
D = "/Users/johndionaldo/Library/Application Support/Claude/scratch-workspaces/8645d517-f4a3-433c-8998-fd7c0e49ba87/a748fb05-e298-40e2-a797-544bc288ae5f/scratch-2026-10-30-ec4193/rev_trike_shell_v3"
z = np.load(D + "/solid.npz"); lo = z["lo"]; P = float(z["P"]); s = z["solid"]
def surf(v):
    e = ndi.binary_erosion(v, iterations=1)
    return np.argwhere(v & ~e)
lab, nl = ndi.label(s); sizes = ndi.sum(s, lab, range(1, nl + 1)); print('components', nl, sorted(map(int, sizes))[-5:]); s = lab == (1 + int(np.argmax(sizes)))
pts = surf(s); pts = lo + P * pts[::2]
b = np.load(D + "/body.npz")["body"]; pb = lo + P * surf(b)[::2]
np.savez_compressed("scan/points.npz", solid=pts.astype(np.float32), body=pb.astype(np.float32))
print(len(pts), len(pb), pts.min(0), pts.max(0))
