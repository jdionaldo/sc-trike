"""Skin (aligned to the scan frame by scan/align.json) rendered through the scan-derived cameras: photo 67 (cam_photo.json) and the sheet-68 3/4 drawing (cam_drawing.json)."""
import json, sys
import numpy as np, cv2
from PIL import Image
import cam_fit as CF
import tools_skin.pskin_autocam as A
al = json.load(open("scan/align.json"))["p"]
V = A.V.copy(); V = np.stack([al[0] * V[:, 0] + al[1], al[2] * V[:, 1], al[3] * V[:, 2] + al[4]], 1)
def draw(par, img, W, H, scale, chamfer=None, tint=True):
    uv, z = CF.project(par, V, W, H)
    c, R = CF.cam(par)
    front = ((c - V[A.tris].mean(1)) * (A.NRM * np.array([1 / al[0], 1 / al[2], 1 / al[3]]))).sum(1) > 0
    ov = cv2.resize(img, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    if tint:
        m = np.zeros((H * scale, W * scale), np.uint8)
        for t in A.tris[front]: cv2.fillConvexPoly(m, (uv[t] * scale).astype(np.int32), 1)
        ov[m > 0] = (0.7 * ov[m > 0] + 0.3 * np.array([200, 70, 150])).astype(np.uint8)
    fe = set()
    for t in A.tris[front]:
        for k in range(3): fe.add(tuple(sorted((t[k], t[(k + 1) % 3]))))
    ds = []
    for a, b in A.edges:
        if (a, b) in fe:
            cv2.line(ov, tuple((uv[a] * scale).astype(int)), tuple((uv[b] * scale).astype(int)), (0, 0, 255), 1, cv2.LINE_AA)
            if chamfer is not None:
                for t in np.linspace(0, 1, 6):
                    p = (uv[a] * (1 - t) + uv[b] * t).astype(int)
                    if 0 <= p[0] < W and 0 <= p[1] < H: ds.append(min(chamfer[p[1], p[0]], 25.0))
    return ov, ds
if __name__ == "__main__":
    cp = json.load(open("scan/cam_photo.json")); I = "/private/tmp/claude-501/-Users-johndionaldo-Library-Application-Support-Claude-scratch-workspaces-8645d517-f4a3-433c-8998-fd7c0e49ba87-a748fb05-e298-40e2-a797-544bc288ae5f-scratch-2026-10-30-ec4193/0d275d42-fddc-4cbd-9c02-604bf37928ec/images/67.jpg"
    img = np.asarray(Image.open(I).convert("RGB").resize((cp["W"], cp["H"])))
    ov, _ = draw(cp["par"], img, cp["W"], cp["H"], 2); Image.fromarray(ov).save("out/pskin/WS03_panel_skin_on_photo.png")
    cd = json.load(open("scan/cam_drawing.json"))
    ov, ds = draw(cd["par"], A.ref, A.W, A.H, 2, A.dt, tint=True); Image.fromarray(ov).save("out/pskin/WS03_panel_skin_on_drawing.png")
    print("drawing 3/4 skin-edge deviation mean %.1f p95 %.1f px" % (np.mean(ds), np.percentile(ds, 95)))
