"""Project Fugu, 1/8 reverse trike with wishbone lean-steer front end: assembly drawings.

Plan
- Sheet "Fugu general arrangement" (A3, 1:5): side view, top view under it, front view beside it. Assembly drawing: only overall and
  connecting dimensions (wheelbase from the wheel centres; overall size as a note computed from the built model's bounding box).
- Sheet "Fugu front end" (A3, 1:2): front suspension and steering on the front deck, front view and top view. Connecting dimensions:
  pivot rod spacing, kingpin spacing (ball joint to ball joint), ball joint spacing on the knuckle. Item numbers and a parts list.
"""
import json
import os
from soma.drawing import Sheet
from parts import wishbone as wb

_map = json.load(open(os.path.join(os.path.dirname(__file__), "..", ".soma", "model.map.json")))["parts"]
_lo = [min(p["bbox"][0][i] for p in _map) for i in range(3)]
_hi = [max(p["bbox"][1][i] for p in _map) for i in range(3)]
_rear = next(p for p in _map if p["name"] == "wheel r")["bbox"]
REAR_AXLE = (0.0, (_rear[0][1] + _rear[1][1]) / 2, (_rear[0][2] + _rear[1][2]) / 2)

ga = Sheet("Fugu general arrangement", size="A3", scale="1:5", number="FUGU-000", material="PETG, PLA, bought",
           tolerance="ISO 2768-m", projection="first", language="en")
side = ga.view("*", "left", at=(140, 205), hidden=False)
top = ga.view("*", "top", at=(140, 100), hidden=False)
front = ga.view("*", "front", at=(320, 205), hidden=False)
side.dim((0, wb.KY, wb.ZC), REAR_AXLE, offset=-18, text="<> wheelbase")
ga.text("Overall %.0f x %.0f x %.0f (length x width x height, from the model)" % (_hi[1] - _lo[1], _hi[0] - _lo[0], _hi[2] - _lo[2]), (215, 100))
ga.text("Front track %.0f, front tyre 112, rear tyre 140" % (2 * 144.0), (215, 93))

FE = ["Chassis/Front suspension/", "Chassis/Steering/", "w3 deck front", "w3 skid", "wheel f 1", "wheel f -1", "mock tire 1", "mock tire -1"]
fe = Sheet("Fugu front end", size="A3", scale="1:2", number="FUGU-100", material="PETG, bought parts",
           tolerance="ISO 2768-m", projection="first", language="en")
ff = fe.view(FE, "front", at=(150, 215), hidden=False)
ft = fe.view(FE, "top", at=(150, 110), hidden=False)
ff.dim((-wb.XI, wb.HY1, wb.ZU), (wb.XI, wb.HY1, wb.ZU), offset=32, text="<> pivots")
ff.dim((-wb.KX, wb.KY, wb.ZU), (wb.KX, wb.KY, wb.ZU), offset=45, text="<> kingpins")
ff.dim((-wb.KX, wb.KY, wb.ZL), (-wb.KX, wb.KY, wb.ZU), offset=-60, text="<>")
ITEMS = [("1", "Lean head", 1, "PETG, printed", (0, wb.HY0, wb.HEAD_TOP - 3)),
         ("2", "Upper wishbone", 2, "PETG, printed", (60, wb.KY + 10, wb.ZU)),
         ("3", "Lower wishbone", 2, "PETG, printed", (60, wb.KY + 10, wb.ZL)),
         ("4", "Knuckle", 2, "PETG, printed", (wb.KX + 2, wb.TAB_Y0 + 5, wb.ZU - 14)),
         ("5", "Heave shock, 68 mm", 1, "bought", (-10, wb.SHOCK_EYE[1], wb.SHOCK_EYE[2])),
         ("6", "Pivot rod D6 x 48", 4, "steel", (wb.XI, wb.HY1, wb.ZL)),
         ("7", "Ball stud 6.8 M3 and cup", 8, "bought", (wb.KX, wb.KY, wb.ZL)),
         ("8", "Tie rod, M3 turnbuckle", 2, "bought", (55, wb.STEER_ARM_XY[1], wb.ZT)),
         ("9", "Steering horn", 1, "PETG, printed", (0, wb.SERVO_SHAFT_Y - 20, wb.HORN_Z0)),
         ("10", "Servo, low profile, cradle", 1, "bought / PETG", (0, wb.SERVO_SHAFT_Y + 15, wb.SERVO_Z0 + 10))]
for k, (no, name, qty, mat, p) in enumerate(ITEMS):
    v = ft if no in ("8", "9", "10") else ff
    v.leader(p, no, at=(262, 262 - 11 * k) if v is ff else (262, 150 - 11 * (k - 7)), end="dot")
fe.table([["Item", "Name", "Qty", "Material"]] + [[no, name, str(qty), mat] for no, name, qty, mat, p in ITEMS], at=(272, 122), widths=[13, 64, 11, 44])
