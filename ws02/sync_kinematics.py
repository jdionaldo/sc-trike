"""Copy the solved lean/steer/rear numbers from out/kinematics.json into the overrides block of params.py."""
import json
import re

r = json.load(open("out/kinematics.json"))
s = open("params.py").read()
tup = lambda v: tuple(round(x, 3) for x in v)
print("sync by hand: see the steer_arm_xyz block in params.py (regex sync removed: it mangled tuples)")
