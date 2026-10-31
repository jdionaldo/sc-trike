"""Look-first body: solid hexagonal sections whose width, belly and roof lines are traced from the reference views
(side render and blueprint plan), 250 mm units scaled to the 370 mm car. d = distance from the rear tire's back edge."""
import json
import numpy as np

K = 370.0 / 250.0
X0, Z0 = -370.0 + 33.0, -59.2          # chassis frame: x = K d + X0, z = K h + Z0
# side view (d, h): roof and belly lines read from the render
TOP = [(55, 50), (73, 64), (111, 69), (141, 69), (163, 67), (189, 56), (215, 51), (246, 41)]
BOT = [(55, 33), (87, 21), (115, 14), (163, 11.5), (195, 12), (225, 22), (242, 34), (246, 38)]
# plan view (d, half width) from the blueprint
HW = [(55, 30), (76, 44), (100, 55), (143, 47), (182, 43), (188, 49), (219, 38), (235, 27), (246, 14)]


def f(table, d):
    a = np.array(table, float)
    return float(np.interp(d, a[:, 0], a[:, 1]))


def section(d):
    w, zt, zb = K * f(HW, d), K * f(TOP, d) + Z0, K * f(BOT, d) + Z0
    h = zt - zb
    pts = [(-0.70 * w, zb), (-w, zb + 0.30 * h), (-0.80 * w, zb + 0.62 * h), (-0.50 * w, zt)]
    pts = pts + [(-y, z) for y, z in reversed(pts)]
    return K * d + X0, [[round(y, 3), round(z, 3)] for y, z in pts]


def commands(ds):
    cmds = []
    for d in ds:
        x, pts = section(d)
        cmds += [{"command": "sketch.create", "params": {"plane": "YZ", "offset": round(x, 3)}},
                 {"command": "sketch.line", "params": {"points": pts, "closed": True}},
                 {"command": "sketch.finish", "params": {}}]
    cmds.append({"command": "solid.loft", "params": {"sections": [{"sketch": i + 1} for i in range(len(ds))]}})
    return cmds


if __name__ == "__main__":
    ds = [58, 73, 100, 120, 141, 163, 189, 210, 230, 244]
    json.dump(commands(ds), open("out/commands/trace_body.json", "w"))
