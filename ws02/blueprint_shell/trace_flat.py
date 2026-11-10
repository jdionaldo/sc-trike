"""Trace every flat pattern of sheet 71: red cut line -> outline polygon, blue lines -> fold segments (solid=mountain, dashed=valley).
Output flat_patterns.json (pixel coords in the 4x crop frame) and flat_<P>.png overlays."""
import json, sys
import numpy as np, cv2
from PIL import Image
im = Image.open('sheet71.png').convert('RGB')
R = json.load(open('crops.json'))
S = 4
out = {}
for k, b in R.items():
    c = np.array(im.crop(b).resize(((b[2]-b[0])*S, (b[3]-b[1])*S), Image.LANCZOS)).astype(int)
    r, g, bl = c[..., 0], c[..., 1], c[..., 2]
    red = (((r - g) > 60) & ((r - bl) > 60)).astype(np.uint8)
    blue = ((bl > 150) & (r < 110) & (g < 150) & (bl - r > 80)).astype(np.uint8)
    h, w = red.shape
    red[:int(h*0.17), :] = 0              # drop the title chip / x1 label
    blue[:int(h*0.17), :] = 0
    # drop the thin frame of the cell
    red[:, :6] = 0; red[:, -6:] = 0; red[-6:, :] = 0
    k5 = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (25, 25))
    cl = cv2.morphologyEx(red, cv2.MORPH_CLOSE, k5)
    cnts, hier = cv2.findContours(cl, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    polys = []
    for i, cn in enumerate(cnts):
        if cv2.contourArea(cn) < 400: continue
        eps = 0.008 * cv2.arcLength(cn, True)
        ap = cv2.approxPolyDP(cn, eps, True)[:, 0, :]
        polys.append({'outer': True, 'pts': ap.tolist(), 'area': float(cv2.contourArea(cn))})
    lines = cv2.HoughLinesP(cv2.dilate(blue, np.ones((3, 3), np.uint8)), 1, np.pi/180, 40, minLineLength=40, maxLineGap=14)
    segs = [] if lines is None else np.asarray(lines).reshape(-1, 4).tolist()
    out[k] = {'crop': b, 'scale': S, 'size': [w, h], 'polys': polys, 'folds': segs}
    vis = c.astype(np.uint8).copy()
    for p in polys:
        cv2.polylines(vis, [np.array(p['pts'], np.int32)], True, (0, 200, 0) if p['outer'] else (255, 0, 255), 2)
        for q in p['pts']: cv2.circle(vis, tuple(map(int, q)), 4, (255, 160, 0), -1)
    for s in segs: cv2.line(vis, (s[0], s[1]), (s[2], s[3]), (0, 0, 0), 1)
    Image.fromarray(vis).save(f'flat_{k}.png')
    print(k, len(polys), [len(p['pts']) for p in polys], len(segs))
json.dump(out, open('flat_patterns.json', 'w'))
