"""Two-tone traced body: a hull from the traced plan/side lines, split by the yellow panels traced from the reference
side view (yellow = hull inside the traced prisms, black = the rest)."""
import json
import trace_body as tb

S = 0.523          # mm per reference pixel (250 mm car)


def px_to_mm(px, py):
    d, h = (px - 21) * S, (830 - py) * S
    return round(tb.K * d + tb.X0, 3), round(tb.K * h + tb.Z0, 3)


def build(ds=(58, 73, 100, 120, 141, 163, 189, 210, 230, 244)):
    polys = json.load(open("out/yellow_polys_px.json"))
    cmds, nid = [], 0                  # sketches and features share one id counter
    for name in ("hull_yellow", "hull_black"):
        first = nid
        for d in ds:
            x, pts = tb.section(d)
            nid += 1
            cmds += [{"command": "sketch.create", "params": {"plane": "YZ", "offset": round(x, 3)}},
                     {"command": "sketch.line", "params": {"points": pts, "closed": True}},
                     {"command": "sketch.finish", "params": {}}]
        cmds.append({"command": "solid.loft", "params": {"sections": [{"sketch": first + i + 1} for i in range(len(ds))],
                                                         "body_name": name}})
        nid += 1
    cmds.append({"command": "sketch.create", "params": {"plane": "XZ"}})
    for p in polys:
        pts = [list(px_to_mm(x, y)) for x, y in p]
        pts = [[x, z] for x, z in pts]
        cmds.append({"command": "sketch.line", "params": {"points": pts, "closed": True}})
    cmds.append({"command": "sketch.finish", "params": {}})
    sk = nid + 1
    cmds.append({"command": "solid.extrude", "params": {"sketch": sk, "distance": 400, "direction": "symmetric",
                                                        "operation": "new", "body_names": ["pa", "pb"]}})
    cmds += [{"command": "solid.combine", "params": {"target": "pa", "tools": ["pb"], "operation": "join"}},
             {"command": "solid.combine", "params": {"target": "hull_yellow", "tools": ["pa"], "operation": "intersect",
                                                     "keep_tools": True}},
             {"command": "solid.combine", "params": {"target": "hull_black", "tools": ["pa"], "operation": "cut"}}]
    cmds += [{"command": "appearance.assign", "params": {"components": ["hull_yellow"], "color": "#f2b705"}},
             {"command": "appearance.assign", "params": {"components": ["hull_black"], "color": "#151515"}}]
    return cmds


if __name__ == "__main__":
    json.dump(build(), open("out/commands/two_tone.json", "w"))
