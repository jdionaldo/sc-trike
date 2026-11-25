"""Lean-steer animation of the double-wishbone front end (parts/wishbone.py), shared by animations/lean_steer.py and animations/lean_steer_front.py.

The body (everything on the head) rolls about the ground line. The wheels lean with the body (parallelogram) and stay on the ground, so the arms turn by
solve_psi(); the knuckles follow the arms and steer about the kingpin; the tie rods follow the horn and the knuckles, the heave shock the two rockers."""
import json
import os
import cadquery as cq
from parts import wishbone as wb

ROLL = 10.0        # degrees of body lean (design range of the linkage)
HORN = 30.0        # degrees of servo horn each way (about 17 degrees of wheel steer)
V = cq.Vector


def _names():
    here = os.path.dirname(__file__)
    return [q["name"] for q in json.load(open(os.path.join(here, ".soma", "model.map.json")))["parts"]]


def build(a):
    """Create the joints on animation `a` and return pose(phi, eta) -> actions."""
    all_names = _names()
    wheel, arm_lo, arm_up, tie = {}, {}, {}, {}
    for s in (1, -1):
        wheel[s] = ["Knuckle %d" % s, "Axle pin %d" % s, "Axle nut %d" % s, "wheel f %d" % s, "mock tire %d" % s, "Wheel bearing inner %d" % s, "Wheel bearing outer %d" % s, "Axle shim inner %d" % s, "Axle shim outer %d" % s,
                    "Steer stud knuckle %d" % s] + ["Ball stud %s %d" % (n, s) for n in ("upper", "lower")]
        arm_lo[s] = ["Lower arm %d" % s, "Rod end lower %d" % s]
        arm_up[s] = ["Upper arm %d" % s, "Rod end upper %d" % s, "Heave shock pin %d" % s]
        tie[s] = ["Tie rod %d" % s, "Tie rod end knuckle %d" % s, "Tie rod end horn %d" % s]
    horn_parts = ["Steer horn", "Steer servo shaft"] + ["Steer stud horn %d" % s for s in (1, -1)]
    shock_b, shock_s = ["Heave shock body"], ["Heave shock shaft"]
    moving = {n for d in (wheel, arm_lo, arm_up, tie) for v in d.values() for n in v} | set(horn_parts) | set(shock_b) | set(shock_s)
    roll = a.hinge([n for n in all_names if n not in moving], (0, -100, wb.GROUND_Z), (0, 100, wb.GROUND_Z))
    lo, up, wh, tr = {}, {}, {}, {}
    for s in (1, -1):
        lo[s] = a.hinge(arm_lo[s], (s * wb.XI, 0, wb.ZL), (s * wb.XI, 1, wb.ZL), parent=roll)
        up[s] = a.hinge(arm_up[s], (s * wb.XI, 0, wb.ZU), (s * wb.XI, 1, wb.ZU), parent=roll)
        wh[s] = a.part(wheel[s])
        tr[s] = a.part(tie[s], parent=roll)
    horn = a.hinge(horn_parts, (0, wb.SERVO_SHAFT_Y, 0), (0, wb.SERVO_SHAFT_Y, 1), parent=roll)
    sb = a.part(shock_b, parent=roll)
    ss = a.part(shock_s, parent=roll)

    def pose(phi, eta):
        acts = [roll.to(phi), horn.to(eta)]
        psi = {s: wb.solve_psi(s, phi) for s in (1, -1)}
        for s in (1, -1):
            dl = wb.steer_solution(s, psi[s], eta)
            dx, dz = wb.arm_ball(s, psi[s])
            kin = wb.roll_loc(phi) * cq.Location(V(dx, 0, dz)) * wb._loc_axis((s * wb.KX, wb.KY, 0), (0, 0, 1), dl)
            tl, _, _ = wb.tie_rod_loc(s, psi[s], dl, eta)
            acts += [lo[s].to(psi[s]), up[s].to(psi[s]), wh[s].to(kin), tr[s].to(tl)]
        lb, ls, _ = wb.shock_locs(psi[-1], psi[1])
        acts += [sb.to(lb), ss.to(ls)]
        return acts

    return pose


def sweep(a, pose, p0, p1, seconds, steps=18):
    """Play the poses from (phi, eta) p0 to p1 in `steps` short linear steps with a smooth start and end."""
    for k in range(1, steps + 1):
        t = k / steps
        e = t * t * (3 - 2 * t)
        t0 = (k - 1) / steps
        e0 = t0 * t0 * (3 - 2 * t0)
        a.play(*pose(p0[0] + (p1[0] - p0[0]) * e, p0[1] + (p1[1] - p0[1]) * e), run_time=seconds / steps, ease="linear")
