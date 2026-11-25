"""Suspension + drivetrain kit: the printed parts of the front suspension (SU), steering (ST), drivetrain (DT) and the motor plate (CH5) out of
kit/print/parts.json (run build_kit.py first), their own Bambu plates, and kit/susp_drive/README.md (parts list with prices, print list, plates with
the slicer's time and grams, assembly steps, open items).

  python kit/make_susp_drive.py            -> copies STLs, writes kit_manifest.json
  cd kit/susp_drive && python ../bambu_kit.py kit_manifest.json --check
  python kit/make_susp_drive.py --docs     -> README.md (reads bambu/slice_check.json)
"""
import json, os, shutil, sys
from registry import PARTS
from hardware import HW, table as hw_table, SRC_DATE

HERE = os.path.dirname(os.path.abspath(__file__))
SRC, OUT = HERE + "/print", HERE + "/susp_drive"
SUBS = ("SU", "ST", "DT")
EXTRA = ("CH5",)                                   # motor plate: the motor / ESC mount belongs to the drivetrain kit
SLOT = {"PETG": 4, "TPU 95A": 4}
FACE = ["+x", "-x", "+y", "-y", "+z", "-z"]        # build_kit orient_face: the model face that lies on the bed
P = [p for p in json.load(open(SRC + "/parts.json"))["parts"] if p["sub"] in SUBS or p["design"] in EXTRA]
D = {d["id"]: d for d in PARTS}


def manifest():
    os.makedirs(OUT + "/stl", exist_ok=True)
    for p in P: shutil.copy(f"{SRC}/stl/{p['id']}.stl", f"{OUT}/stl/{p['id']}.stl")
    plates = []
    opt = lambda p: D[p["design"]].get("option", False)
    for n, (title, sel) in enumerate((("Front suspension and steering (PETG)", lambda p: p["sub"] in ("SU", "ST") and p["material"] == "PETG" and not opt(p)),
                                      ("Drivetrain and wheels (PETG)", lambda p: (p["sub"] == "DT" or p["design"] in EXTRA) and p["material"] == "PETG"),
                                      ("Stops (TPU 95A)", lambda p: p["material"] == "TPU 95A"),
                                      ("Options (PETG, print only if you take the printed path)", opt)), 1):
        ps = [p for p in P if sel(p)]
        if ps:
            plates.append(dict(name=f"{n:02d}_" + title.split(" (")[0].replace(" ", "_").replace(",", ""), title=title,
                               parts=[dict(stl=f"stl/{p['id']}.stl", name=p["id"], walls=p["walls"], infill=p["infill"], support=p["support"], slot=SLOT[p["material"]]) for p in ps]))
    man = dict(title="Fugu suspension + drivetrain kit", profile="../p2s_profile.config", out="bambu", bed=[256.0, 256.0], margin=5, gap=22, filament_slot=4,
               supports="easy_peel", plates=plates)
    json.dump(man, open(OUT + "/kit_manifest.json", "w"), indent=1)
    print(len(P), "printed files,", len(plates), "plate groups")


STEPS = [
    ("0. Test fit (do this first)", "Print knuckle SU4R and the steering horn ST1 alone. Press an MR126 bearing into the wheel DT16 hub with a vise and a socket on the outer race (seat D12.1): it must go in with firm hand pressure; if it falls in, the seat is loose (print the wheel 0.1 mm smaller in X/Y compensation); if it cracks the hub, stop. Press one M3 insert, screw a ball stud in, snap a cup on.",
     "1 x MR126, 1 x M3 insert, 1 ball stud + cup", "Check: bearing flush and square, stud tight, cup turns 20 deg without binding."),
    ("1. Lean head on the deck", "Insert 4 M3 inserts into the base tubes of the lean head SU1 (soldering iron, 220 C, straight). Screw SU1 to the front deck from below.",
     "4 x M3 insert, 4 x M3 x 10 countersunk", "Check: head sits flat, no rocking."),
    ("2. Wishbones", "Ream the arm pivot bores (D6.2) of SU2 L/R and SU3 L/R with a 6 mm drill by hand until a 6 mm shoulder screw slides through without play. Push the four shoulder screws in from the rear through the head's rear post, the arm barrel and the front post. Insert M3 inserts in the arm tips (D4.1 bore: heat the insert slowly) and screw the M3 rods and ball cups on.",
     "4 x shoulder screw 6 x 45 M5, 4 x M3 insert, 4 x M3 rod 25, 4 x ball cup", "Check: each arm swings 10 deg up and down by its own weight. OPEN: the M5 end of the shoulder screw has no designed nut seat (see open items)."),
    ("3. Knuckles", "Set 2 M3 inserts from the back into each knuckle SU4 L/R (pockets 7.5 mm deep behind the boss face). Screw the ball studs into them from the front. Snap the arm cups onto the studs (upper arm to the upper stud).",
     "4 x M3 insert, 4 x ball stud", "Check: the knuckle turns 25 deg each way and rises with the arms without binding."),
    ("4. Front wheels", "Press two MR126 bearings into each wheel DT16 (one from each end, outer race only). Slide a 6x8 shim onto the stub axle bolt, push the bolt through the knuckle boss from the inside, put the wheel on, the second shim, and the M6 nylock. Tighten the nylock only until the wheel has no play and still spins freely (about 1/4 turn after contact). Fit the tyre (glue or beadlock as the tyre requires).",
     "4 x MR126, 4 x shim 6x8x0.5, 2 x M6 x 60 cut to 48 + nylock, 2 x front tyre", "Check: wheel spins 3 s or more from a flick; no axial play."),
    ("5. Heave shock and stops", "Push the TPU bump stop SU7 over the heave shock shaft onto the eye neck. Mount the shock between the forks of SU2 with M3 x 20 + nylock (snug, the eye must turn). Glue the TPU pads SU6 L/R into the droop stops SU5 L/R (CA for TPU or contact cement), press 2 inserts in each stop and screw them under the lower arm roots from below.",
     "1 heave shock, 2 x M3 x 20 + nylock, 4 x M3 insert, 4 x M3 x 10", "Check: push one wheel up 12 mm with the body leaned 10 deg: the bump stop meets the shock body; let it drop 8 mm: the lower arm meets the pad."),
    ("6. Steering", "Screw the servo mount ST2 to the deck, stand the servo in it (4 x M2.5 self tapping into the pillars), centre the servo (1500 us) and fit the horn ST1 straight across. Put the ball studs through the horn ends (from below, nylock on top) and through the knuckle steering arms (from below, nylock under). Tie rods, steel path (default): Secraft SEC349 M3 turnbuckle 80 mm with a ball cup on each end; printed path: tie rod ST3L / ST3R from the options plate, one M3 insert pressed into each end collar, a ball cup screwed into each insert. Set both to 93 mm ball to ball and snap them on.",
     "1 servo, 4 x M2.5 x 10, 4 x ball stud, 4 x M3 nylock, 2 x tie rod", "Check: at full servo throw the wheels steer about 22.5 deg inside / 19 deg outside, the same both ways; nothing touches the arch liners."),
    ("7. Rear drive shaft and carriers", "Press MR115 bearings into the lower halves of the pillow block DT5 (1) and the rear bearing carrier DT7 (2 on the rear shaft, 2 on the cross shaft). Slide the spur gear onto the front end and the 8T pinion onto the rear end of the 5 mm rear shaft, lay it into the bearings; lay the cross shaft with the ring gear on the ring hub DT10 into its two bearings; check the mesh (slight backlash), then close with the upper halves DT6 / DT8.",
     "5 x MR115, rear shaft 5 x 112, cross shaft 5 x 88, spur 40T, ring and pinion, ring hub DT10, 2 x DIN 471 5 mm", "Check: turning the spur by hand turns the cross shaft smoothly with no tight spot over a full ring turn."),
    ("8. Motor", "Screw the motor to the motor plate CH5 (2 x M3 x 6, 25 mm pattern) with the 15T pinion (grub on the shaft flat). Set the mesh with a strip of paper between the gears, slide the motor in its slots, tighten. Screw the plate gussets to the deck (2 x M3).",
     "Fusion SE motor/ESC, 15T pinion, 4 x M3", "Check: paper strip comes out with a gear-tooth print but not torn; gears turn with a little backlash."),
    ("9. Rear swing arm", "Press MR115 bearings into the three pivot plates of DT11 (faces toward the drive block) and the two 688 bearings into the axle plates (faces toward the pulley). Fit the 26T pulley DT14 on the cross shaft between the arm plates and slide the arm onto the cross shaft; DIN 471 rings at both ends. Put the 8 mm axle through the outer plate, the 30T pulley DT15 (belt on both pulleys first) and the inner plate; ring it. Fit the rear hub and the wheel DT17 with the rear tyre.",
     "3 x MR115, 2 x 688, axle 8 x 100, belt 2GT-300, 2 x M3 x 4 grub, 4 x DIN 471, rear hub, rear tyre", "Check: arm swings freely through its full travel with the belt on; belt deflects about 3 mm under a finger; wheel turns when the spur is turned."),
    ("10. Rear shock", "Bolt the shock between the cage clevis (M6 x 35) and the arm bridge (M6 x 30), nylocks snug.", "rear shock, M6 x 30, M6 x 35, 2 x M6 nylock", "Check: compress the rear by hand to the bump stop of the shock: the tyre does not touch the shell or the cage."),
]
FITS = [
    "Bearing seats are printed at OD + 0.1 mm (D11.1 for 5x11x4, D12.1 for 6x12x4, D16.1 for 8x16x5): a light press fit in PETG. Press on the outer race only, never on the shield.",
    "Pin and rod bores: arms D6.2 on 6 mm shoulder screws (0.2 mm running clearance, ream by hand); lean head posts D6.1; knuckle axle boss D6.1 on the 6 mm stub axle; arm and carrier bores beside a bearing D5.4-5.6 (shaft does not touch).",
    "Heat-set inserts: pockets D4.2 x 5 for OD 4.6 x 4 inserts (Adafruit 4255 is OD 4.2: use OD 4.6 inserts or shrink the pockets).",
    "Torque: printed parts take snug-plus-a-quarter-turn, not a torque value: M3 into inserts about 0.5 N m, M3 nylocks on ball studs until the stud stops turning, M6 axle nylock until the play is gone (the wheel must still spin), M6 shock bolts snug (eyes must turn). Thread locker (blue, medium) on metal-to-metal threads only (grubs on shaft flats, ball studs in metal), never on threads in PETG or PLA.",
]
OPEN = [
    "Cage boss spots at safety 1.48 (target 2): OPEN, outside this kit but the cage carries the rear shock top.",
    "No lean stop: lean turns both arms at once, so a stop on one arm cannot sense it; it needs a lean link or a balance beam (owner decision).",
    "Rear travel: now pose-checked by `tools/rear_check.py` from -15 mm droop to +20 mm bump at the axle (arm -7.1 to +9.4 deg): 0 overlaps; the arm comes within 0.05 mm of the tail deck at -15 mm (it would act as the droop stop, not designed as one). The shock changes length -6.5 / +5.9 mm over that range; the chosen rear shock's stroke is not read from its listing.",
    "Not printed: nothing in this kit has been printed, fitted or driven. Every fit above comes from the model.",
    "Wishbone pivot shoulder screws: the M5 end has no designed nut seat; an M5 into the printed front post would break the no-printed-threads-below-M6 rule.",
    "Heave shock: the chosen RC4WD 70 mm is discontinued, 4.5 mm longer than the model's 68 mm, has a 3.0 mm eye (model pin hole D4.1) and no stated spring rate (about 30 N/mm needed).",
    "Ring and pinion: the model's ring stand-in (25.6 mm OD) is smaller than a 30T SCX10 ring: check the carrier cavity against the real ring before printing DT7/DT8.",
    "Rear hub: no 12 mm hex hub with an 8 mm bore was found.",
    "Generic hardware (ball studs, cups, tie rods, shafts, rings, shims) has estimated prices; McMaster / Misumi pages could not be read by the sourcing run.",
    "TPU parts are sliced with the PETG profile of the saved project (no TPU profile in it): their time and grams are ASSUMED; switch the filament to TPU 95A in Studio.",
]


def docs():
    sc = json.load(open(OUT + "/bambu/slice_check.json"))
    rows = [r for r in HW if r["grp"] in SUBS]
    t, tot = hw_table(rows)
    n = {s: sum(1 for r in rows if r["status"] == s) for s in ("VERIFIED", "ASSUMED", "UNKNOWN")}
    mins, grams = sum(v["minutes"] for v in sc.values()), sum(v["grams"] for v in sc.values())
    probs = sum(len(v["problems"]) for v in sc.values())
    L = ["# Fugu suspension + drivetrain kit (Version 1, wishbone front end)", "",
         f"Front wishbone suspension, lean head, knuckles, steering, stops, rear swing arm, belt drive, motor plate, bearings, axles, wheels and tyres. "
         f"{len(P)} printed files on {len(sc)} plates, {mins / 60:.1f} h and {grams:.0f} g by the Bambu Studio slice check ({probs} problems; the options plate, printed tie rods ST3L/R, is included: skip it on the steel path). "
         f"Bought parts {tot:.2f} USD as listed on {SRC_DATE} ({n['VERIFIED']} rows VERIFIED, {n['ASSUMED']} ASSUMED, {n['UNKNOWN']} UNKNOWN). Nothing bought.", "",
         "## Stated openly", ""] + [f"- {o}" for o in OPEN] + ["",
         "## 1. Bought parts", "", "Quantities are counted from the model (`Where` names its stand-in parts). Total = packs to buy x pack price. Retailer notes: `../sourcing_2026-11-24.md`.", ""] + t + ["",
         "## 2. Printed parts", "", "Every file is oriented and packed: do not auto-orient in Bambu Studio. L/R parts have their own IDs (L = -x side, the left seen from behind).", "",
         "| ID | Part | Material | Walls | Infill | Support | Face on the bed | Size mm | Plate |", "|---|---|---|---|---|---|---|---|---|"]
    man = json.load(open(OUT + "/kit_manifest.json"))
    plate_of = {pp["name"]: pl["title"] for pl in man["plates"] for pp in pl["parts"]}
    for p in P:
        L.append(f"| {p['id']} | {p['name']} | {p['material']} | {p['walls']} | {p['infill']} | {p['support']} | model {FACE[p['orient_face']]} down | {' x '.join(str(round(e)) for e in p['extents'])} | {plate_of.get(p['id'], '?')} |")
    L += ["", "Print or buy: every mechanical part has a printed version, a metal version or both: `print_or_buy.md`. Machinable interfaces of the parts with no stock metal version: `interfaces.md`.",
          "Edge breaks: every part above that moves or carries a moving joint has 0.6 mm chamfers on its outside edges and 0.4 mm on every bore, pocket and insert entry (gear and pulley teeth excepted, CHAMFER_MOVING in model.py)."]
    L += ["", "## 3. Plates (Bambu Studio slice check, P2S profile of the saved project, 0.4 mm nozzle)", "",
          "Open `bambu/all_plates.3mf` or one plate file. PETG in AMS slot 4; the TPU plate needs TPU 95A (external spool, not through the AMS).", "",
          "| Plate file | Time | Grams | Slice check |", "|---|---|---|---|"]
    for k, v in sorted(sc.items()):
        L.append(f"| {k} | {v['minutes'] / 60:.1f} h | {v['grams']:.0f} | {'; '.join(v['problems']) or 'OK'} |")
    L += [f"| **Total** | **{mins / 60:.1f} h** | **{grams:.0f}** | {probs} problems |", "",
          "## 4. Tools", "", "- Soldering iron with an insert tip (heat-set inserts)", "- Bench vise or arbor press and sockets 11 / 12 / 16 mm (bearings, outer race only)",
          "- Hex keys 1.5 / 2 / 2.5 / 3 / 4 mm, 5.5 and 10 mm nut drivers, 6 mm drill (hand reaming)", "- Circlip pliers (DIN 471 5 and 8 mm), hacksaw and file (cut the axle bolt and shafts)",
          "- Blue thread locker (metal threads only), CA glue for TPU", "",
          "## 5. Fits and torque", ""] + [f"- {f}" for f in FITS] + ["", "## 6. Assembly (in this order)"]
    for title, body, hw, chk in STEPS:
        L += ["", f"### {title}", "", body, "", f"Hardware: {hw}.", "", chk]
    open(OUT + "/README.md", "w").write("\n".join(L) + "\n")
    print("README written:", len(P), "files,", len(sc), "plates,", f"{mins / 60:.1f} h, {grams:.0f} g, {tot:.2f} USD")


if __name__ == "__main__":
    docs() if "--docs" in sys.argv else manifest()
