"""Lean steer from the front: same motion as lean_steer.py, camera fixed in front of the nose."""
from soma.anim import Animation
import lean_front as lf

a = Animation("Lean steer front")
pose = lf.build(a)
a.camera.set(view="front", fit=["Lean head", "mock tire 1", "mock tire -1"], zoom=1.0)
a.ghost("Print shell")
a.title("Lean steer, front view", subtitle="Wheels lean with the body, arms and knuckles follow", duration=1.5)
a.caption("Lean and steer left")
lf.sweep(a, pose, (0, 0), (lf.ROLL, -lf.HORN), 2.5)
a.wait(0.5)
a.caption("Back to centre")
lf.sweep(a, pose, (lf.ROLL, -lf.HORN), (0, 0), 2.0)
a.caption("Lean and steer right")
lf.sweep(a, pose, (0, 0), (-lf.ROLL, lf.HORN), 2.5)
a.wait(0.5)
lf.sweep(a, pose, (-lf.ROLL, lf.HORN), (0, 0), 2.0)
