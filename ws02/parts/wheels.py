"""Rear wheel hex adapter: 12 mm hex drive on the 3 mm axle, retained by an M2 set screw."""
import math

from cad import Part


def rear_hub(p):
    r = p.hex_af / math.sqrt(3)
    pts = [(r * math.cos(math.radians(60 * k)), r * math.sin(math.radians(60 * k))) for k in range(6)]
    part = Part("rear_hub", "hex standing on the bed", "PETG")
    part.prism("XY", 0.0, pts, p.hub_len)
    part.cyl((0.0, 0.0, -1.0), p.axle_dia + p.clr_press, p.hub_len + 2.0, op="cut")
    part.cyl((0.0, 0.0, p.hub_len / 2), p.set_screw_pilot, p.hex_af, axis="X", op="cut")
    return part


def build(p):
    return [rear_hub(p)]
