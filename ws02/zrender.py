"""Small numpy z-buffer renderer for review images (orthographic or perspective, flat shading, per-mesh colour, two-sided with back faces darker).
Used instead of matplotlib's painter's sort, which mis-orders interior faces of hollow shells.
render(meshes, colors, out, eye, target, up, size, fov_deg=None, ortho_scale=None)"""
import numpy as np


def _look(eye, target, up):
    f = np.asarray(target, float) - np.asarray(eye, float)
    f /= np.linalg.norm(f)
    r = np.cross(f, up)
    r /= np.linalg.norm(r)
    u = np.cross(r, f)
    return r, u, f


def render(meshes, colors, out, eye, target=(0, 0, 0), up=(0, 0, 1), size=(1100, 700), fov_deg=None, ortho_h=None, title=None, bg=(246, 246, 248),
           light=(0.4, -0.5, 0.8), clip_near=1.0):
    W, H = size
    r, u, f = _look(eye, target, up)
    eye = np.asarray(eye, float)
    L = np.asarray(light, float)
    L /= np.linalg.norm(L)
    zb = np.full((H, W), np.inf)
    img = np.empty((H, W, 3), np.float32)
    img[:] = np.array(bg, np.float32)
    for mesh, col in zip(meshes, colors):
        V = np.asarray(mesh.vertices, float)
        F = np.asarray(mesh.faces)
        rel = V - eye
        x, y, z = rel @ r, rel @ u, rel @ f
        if fov_deg is None:
            s = H / ortho_h
            px = W / 2 + x * s
            py = H / 2 - y * s
        else:
            s = (H / 2) / np.tan(np.radians(fov_deg) / 2)
            zz = np.maximum(z, 1e-3)
            px = W / 2 + x / zz * s
            py = H / 2 - y / zz * s
        P3 = np.stack([px, py, z], 1)
        tri = P3[F]
        n = mesh.face_normals
        shade_front = np.clip(n @ L, 0, 1) * 0.62 + 0.32
        facing = (n @ f) < 0            # normal toward the camera
        base = np.array(col, np.float32)
        for k in range(len(F)):
            t = tri[k]
            if (t[:, 2] < clip_near).any():
                continue
            xmin, xmax = int(max(np.floor(t[:, 0].min()), 0)), int(min(np.ceil(t[:, 0].max()), W - 1))
            ymin, ymax = int(max(np.floor(t[:, 1].min()), 0)), int(min(np.ceil(t[:, 1].max()), H - 1))
            if xmin > xmax or ymin > ymax:
                continue
            gx, gy = np.meshgrid(np.arange(xmin, xmax + 1) + 0.5, np.arange(ymin, ymax + 1) + 0.5)
            (x0, y0, z0), (x1, y1, z1), (x2, y2, z2) = t
            den = (y1 - y2) * (x0 - x2) + (x2 - x1) * (y0 - y2)
            if abs(den) < 1e-12:
                continue
            a = ((y1 - y2) * (gx - x2) + (x2 - x1) * (gy - y2)) / den
            b = ((y2 - y0) * (gx - x2) + (x0 - x2) * (gy - y2)) / den
            c = 1 - a - b
            m = (a >= -1e-4) & (b >= -1e-4) & (c >= -1e-4)
            if not m.any():
                continue
            zi = a * z0 + b * z1 + c * z2
            sub = zb[ymin:ymax + 1, xmin:xmax + 1]
            upd = m & (zi < sub)
            if not upd.any():
                continue
            sub[upd] = zi[upd]
            sh = shade_front[k] if facing[k] else 0.18 + 0.2 * shade_front[k]
            img[ymin:ymax + 1, xmin:xmax + 1][upd] = np.clip(base * sh * 255.0, 0, 255)
    im = np.clip(img, 0, 255).astype(np.uint8)
    try:
        from PIL import Image, ImageDraw
        pil = Image.fromarray(im)
        if title:
            ImageDraw.Draw(pil).text((8, 6), title, fill=(30, 30, 30))
        pil.save(out)
    except ImportError:
        import matplotlib.pyplot as plt
        plt.imsave(out, im)
    return out
