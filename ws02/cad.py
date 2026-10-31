"""Command-list builder. Every method appends SolidCraft commands; geometry exists only as commands.

Parts are authored in their print frame: Z up, bed contact at z = 0.
"""
from dataclasses import dataclass, field

OVERLAP = 0.4   # joins overlap the host body; flush joins are refused by the kernel


@dataclass
class Part:
    name: str
    orientation: str
    material: str
    cmds: list = field(default_factory=list)
    _made: bool = False
    walls: bool = True                      # min-wall rule applies
    press_fit_with: tuple = ()               # declared interference allowances
    supports: bool = False                   # printed with supports (body shells only)
    to_chassis: object = None                # 4x4 from print frame to the chassis frame, when not hand-placed

    def _op(self, op):
        if not self._made:
            self._made = True
            return {"operation": "new", "body_name": self.name}
        return {"operation": op, "targets": [self.name]}

    def add(self, command, **params):
        self.cmds.append({"command": command, "params": params})

    def box(self, corner, size, op="join"):
        self.add("solid.box", length=size[0], width=size[1], height=size[2], corner=list(corner), **self._op(op))
        return self

    def box_c(self, center, size, op="join"):
        self.add("solid.box", length=size[0], width=size[1], height=size[2], center=list(center), **self._op(op))
        return self

    def cyl(self, base, d, h, axis="Z", op="join"):
        self.add("solid.cylinder", diameter=d, height=h, base=list(base), axis=axis, **self._op(op))
        return self

    def cyl_c(self, center, d, h, axis="Z", op="join"):
        """Cylinder centred on `center` along `axis` (X, Y or Z)."""
        i = "XYZ".index(axis)
        base = list(center)
        base[i] -= h / 2
        return self.cyl(base, d, h, axis, op)

    def cone(self, base, r_base, r_top, h, op="join"):
        self.add("solid.cone", radius=r_base, top_radius=r_top, height=h, base=list(base), axis="Z", **self._op(op))
        return self

    def revolve(self, plane, pts, axis="Z"):
        """Revolve a closed (radius, world height) profile on the XZ plane, whose sketch y runs toward -Z."""
        self.add("sketch.create", plane=plane)
        self.add("sketch.line", points=[[r, -h] for r, h in pts], closed=True)
        self.add("sketch.finish")
        self.add("solid.revolve", axis=axis, angle=360, **self._op("join"))
        return self

    def prism(self, plane, offset, pts, dist, op="join", direction=None):
        self.add("sketch.create", plane=plane, offset=offset)
        self.add("sketch.line", points=[list(p) for p in pts], closed=True)
        self.add("sketch.finish")
        extra = {"direction": direction} if direction else {}
        self.add("solid.extrude", distance=dist, **extra, **self._op(op))
        return self

    def chamfer(self, edges, distance):
        self.add("solid.chamfer", edges=[list(e) for e in edges], distance=distance, body=self.name)
        return self

    def fillet(self, edges, radius):
        self.add("solid.fillet", edges=[list(e) for e in edges], radius=radius, body=self.name)
        return self

    def prism_xz(self, pts, op="cut"):
        """Cut a polygon given as (x, z) points through the whole body along y (sketched on XZ, whose y runs toward -Z)."""
        self.add("sketch.create", plane="XZ")
        self.add("sketch.line", points=[[x, -z] for x, z in pts], closed=True)
        self.add("sketch.finish")
        self.add("solid.extrude", distance=400.0, direction="symmetric", **self._op(op))
        return self

    def orient(self, angle_deg, tz):
        """Rotate the finished body about the chassis x axis, then lift it by tz so its lowest point is on the bed."""
        import numpy as np
        self.add("solid.move", bodies=[self.name], axis=[1, 0, 0], angle=angle_deg, copy=False)
        self.add("solid.move", bodies=[self.name], translate=[0, 0, tz], copy=False)
        a = np.radians(angle_deg)
        r = np.eye(4)
        r[1, 1], r[1, 2], r[2, 1], r[2, 2] = np.cos(a), -np.sin(a), np.sin(a), np.cos(a)
        t = np.eye(4)
        t[2, 3] = tz
        self.to_chassis = np.linalg.inv(t @ r)
        return self

    def mirror(self, plane):
        self.add("solid.mirror", bodies=[self.name], plane=plane, combine=True)
        return self


class Frame:
    """Maps chassis-frame geometry into a half's print frame. Both handednesses are proper rotations.

    side > 0: (u, v, w) = (x, z, y_out - y).  side < 0: (u, v, w) = (x, -z, y + y_out).
    With abs_y the caller passes |y| and w = y_out - |y| for either side (a mirrored half sharing one description).
    """

    def __init__(self, side, y_out, abs_y=False):
        self.side, self.y_out, self.abs_y = side, y_out, abs_y

    def w(self, y):
        return self.y_out - y if (self.side > 0 or self.abs_y) else y + self.y_out

    def v(self, z):
        return z if self.side > 0 else -z

    def box(self, part, xr, yr, zr, op="join"):
        w0, w1 = sorted((self.w(yr[0]), self.w(yr[1])))
        v0, v1 = sorted((self.v(zr[0]), self.v(zr[1])))
        part.box((xr[0], v0, w0), (xr[1] - xr[0], v1 - v0, w1 - w0), op=op)

    def cyl(self, part, x, z, d, yr, op="join"):
        w0, w1 = sorted((self.w(yr[0]), self.w(yr[1])))
        part.cyl((x, self.v(z), w0), d, w1 - w0, op=op)

    def cyl_z(self, part, x, y, d, zr, op="join"):
        """Cylinder along the chassis z axis (a print-frame v axis)."""
        v0, v1 = sorted((self.v(zr[0]), self.v(zr[1])))
        part.cyl((x, v0, self.w(y)), d, v1 - v0, axis="Y", op=op)

    def cyl_x(self, part, y, z, d, xr, op="join"):
        """Cylinder along the chassis x axis (a print-frame u axis)."""
        part.cyl((xr[0], self.v(z), self.w(y)), d, xr[1] - xr[0], axis="X", op=op)

    def poly(self, part, pts, yr, op="join"):
        w0, w1 = sorted((self.w(yr[0]), self.w(yr[1])))
        part.prism("XY", w0, [(float(x), float(self.v(z))) for x, z in pts], w1 - w0, op=op)
