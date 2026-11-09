"""Semi-pinned 3/4 camera: camera on the car's right-front (az -50..-20), el 8..25, 24..70 mm-equivalent, roll 0; fitted: az, el, f, dist, shift."""
import numpy as np, cv2, json
from scipy.optimize import differential_evolution
from PIL import Image
import tools_skin.pskin_autocam as A
f = lambda p: A.score([p[0], p[1], 0.0, p[2], p[3] / 36 * A.W, p[4], p[5]])
r = differential_evolution(f, [(-80, -30), (5, 25), (350, 1500), (24, 70), (-150, 150), (-150, 150)], seed=2, popsize=20, maxiter=60, polish=False)
p = r.x; par = [p[0], p[1], 0.0, p[2], p[3] / 36 * A.W, p[4], p[5]]
sc, d, iou, pts, uv, m, E = A.score(par, True)
print("SEMI az %.1f el %.1f dist %.0f f %.0f mm-eq shift %.0f,%.0f : chamfer mean %.1f p95 %.1f px, body-mask IoU %.3f" % (p[0], p[1], p[2], p[3], p[4], p[5], d.mean(), np.percentile(d, 95), iou))
ov = cv2.resize(A.ref, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)
t = cv2.resize(m, None, fx=2, fy=2, interpolation=cv2.INTER_NEAREST) > 0
ov[t] = (0.65 * ov[t] + 0.35 * np.array([200, 70, 150])).astype(np.uint8)
for a, b in E: cv2.line(ov, tuple((uv[a] * 2).astype(int)), tuple((uv[b] * 2).astype(int)), (0, 0, 255), 1, cv2.LINE_AA)
cv2.polylines(ov, [(A.BODY * 2).astype(np.int32)], True, (0, 160, 0), 1)
Image.fromarray(ov).save("out/pskin/WS03_panel_q34_overlay_semi.png"); json.dump(dict(par=list(map(float, par)), mean=float(d.mean()), p95=float(np.percentile(d, 95)), iou=float(iou)), open("out/pskin/cam_semi.json", "w"))
