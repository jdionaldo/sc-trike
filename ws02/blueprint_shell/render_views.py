"""Render the assembled shell in the sheet's five views and overlay the silhouette on sheet 71. usage: python render_views.py [meshdir-or-none]"""
import sys, os, json
sys.path.insert(0, '..')
import numpy as np, cv2
from PIL import Image
import zrender
import shell71 as B

COL = {'P1': (190, 60, 60), 'P2': (60, 110, 200), 'P3': (60, 170, 220), 'P4': (130, 70, 170), 'P5': (110, 60, 150), 'P6': (150, 100, 200),
       'P7': (120, 60, 180), 'P8': (50, 150, 70), 'P9': (240, 140, 40), 'P10': (230, 120, 30), 'P11': (230, 200, 40)}
VIEWS = {  # name: eye dir, up
    'side': ((0, 1, 0), (0, 0, 1)), 'top': ((0, 0, 1), (0, -1, 0)), 'front': ((1, 0, 0), (0, 0, 1)), 'rear': ((-1, 0, 0), (0, 0, 1)),
    'persp': ((0.9, 0.75, 0.55), (0, 0, 1))}


def sheet_mask(name, V):
    im = Image.open('sheet71.png').convert('RGB')
    b = V[name]; c = np.array(im.crop(b).resize(((b[2]-b[0])*5, (b[3]-b[1])*5), Image.LANCZOS))
    m = (c.min(2) < 175).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_CLOSE, np.ones((9, 9), np.uint8))
    n, lab, st, _ = cv2.connectedComponentsWithStats(m)
    if n > 1:
        keep = 1 + int(np.argmax(st[1:, cv2.CC_STAT_AREA])); m = (lab == keep).astype(np.uint8)
    return c, m


def main(meshes, tag='v1'):
    V = json.load(open('views.json'))
    names = list(meshes)
    cols = [COL.get(n.rstrip('LR') if n[:3] != 'P10' else 'P10', (150, 150, 150)) for n in names]
    cols = [tuple(c / 255.0 for c in COL[n[:3] if n.startswith('P10') or n.startswith('P11') else n[:2]]) for n in names]
    allv = np.vstack([m.vertices for m in meshes.values()]); ctr = allv.mean(0)
    figs = []
    for vn, (d, up) in VIEWS.items():
        sc, sm = sheet_mask(vn, V)
        eye = ctr + np.array(d) / np.linalg.norm(d) * 1500
        H = sc.shape[0]; W = sc.shape[1]
        hmm = 2.0 * max(np.ptp(allv, 0)) * 1.0
        print(vn, 'sheet bbox', None)
        # first pass: big canvas to measure the bbox
        zrender.render(list(meshes.values()), cols, f'_tmp.png', eye, ctr, up, size=(1600, 1000), ortho_h=hmm * 0.8)
        r = np.array(Image.open('_tmp.png').convert('RGB'))
        rm = (np.abs(r.astype(int) - np.array([246, 246, 248])).sum(2) > 12).astype(np.uint8)
        ys, xs = np.nonzero(rm); ys2, xs2 = np.nonzero(sm)
        if len(xs) == 0: continue
        bx = (xs.min(), xs.max(), ys.min(), ys.max()); sx = (xs2.min(), xs2.max(), ys2.min(), ys2.max())
        # similarity fit (uniform scale by width, centre on the bbox centre)
        k = (sx[1]-sx[0]) / max(bx[1]-bx[0], 1)
        k = min(k, (sx[3]-sx[2]) / max(bx[3]-bx[2], 1)) if vn in ('front', 'rear') else k
        M = np.array([[k, 0, (sx[0]+sx[1])/2 - k*(bx[0]+bx[1])/2], [0, k, (sx[2]+sx[3])/2 - k*(bx[2]+bx[3])/2]])
        rr = cv2.warpAffine(r, M, (W, H), borderValue=(246, 246, 248)); rmm = cv2.warpAffine(rm, M, (W, H), flags=cv2.INTER_NEAREST)
        ov = sc.copy()
        cn, _ = cv2.findContours(rmm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); cv2.drawContours(ov, cn, -1, (255, 0, 0), 3)
        cn, _ = cv2.findContours(sm, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE); cv2.drawContours(ov, cn, -1, (0, 160, 0), 2)
        iou = (rmm & sm).sum() / max((rmm | sm).sum(), 1)
        row = np.hstack([sc, rr, ov]); cv2.putText(row, f'{vn} silhouette IoU {iou:.2f}', (10, 30), 0, 0.9, (0, 0, 0), 2)
        figs.append(row); print(vn, 'IoU', round(float(iou), 2), 'scale px/mm', round(k * H / hmm, 2))
        Image.fromarray(rr).save(f'render_{tag}_{vn}.png')
    w = max(f.shape[1] for f in figs)
    pad = [np.pad(f, ((0, 0), (0, w - f.shape[1]), (0, 0)), constant_values=255) for f in figs]
    Image.fromarray(np.vstack(pad)).save(f'overlay_{tag}.png')
    os.remove('_tmp.png')


if __name__ == '__main__':
    import glob, trimesh
    M = {os.path.basename(f)[:-4]: trimesh.load(f) for f in sorted(glob.glob('stl/*.stl'))}
    main(M, sys.argv[1] if len(sys.argv) > 1 else 'final')
