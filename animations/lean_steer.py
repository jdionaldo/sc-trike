"""Lean steer in action: the double-wishbone front end after the reference build video (parts/wishbone.py, parts/lean_anim.py)."""
from soma.anim import Animation
from parts import lean_anim as lf

a = Animation("Lean steer")
pose = lf.build(a)
a.camera.set(view=(0.9, -1.0, 0.6), fit=["Lean head", "mock tire 1", "mock tire -1"], zoom=1.05)
a.ghost("Print shell")
a.title("Lean steer", subtitle="Body leans, the wishbones keep both wheels on the ground", duration=1.5)
a.caption("Lean only: the body rolls, both wheels lean with it and stay on the ground, every joint stays connected")
lf.sweep(a, pose, (0, 0), (lf.ROLL, 0), 2.0)
lf.sweep(a, pose, (lf.ROLL, 0), (-lf.ROLL, 0), 3.0)
lf.sweep(a, pose, (-lf.ROLL, 0), (0, 0), 2.0)
a.wait(0.4)
a.caption("Lean and steer left: both arm sets turn, the knuckles follow, the tie rods move with the horn")
lf.sweep(a, pose, (0, 0), (lf.ROLL, -lf.HORN), 2.5)
a.wait(0.5)
a.caption("Back to centre")
lf.sweep(a, pose, (lf.ROLL, -lf.HORN), (0, 0), 2.0)
a.caption("Lean and steer right")
lf.sweep(a, pose, (0, 0), (-lf.ROLL, lf.HORN), 2.5)
a.wait(0.5)
lf.sweep(a, pose, (-lf.ROLL, lf.HORN), (0, 0), 2.0)
