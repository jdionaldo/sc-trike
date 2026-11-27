"""Generate bom.md, hardware list and assembly_manual.md from the registry, parts.json and the Bambu slice check."""
import json, os, collections
from registry import PARTS, SUBS, SUB_ORDER
HERE = os.path.dirname(os.path.abspath(__file__))
P = json.load(open(HERE + "/print/parts.json"))["parts"]
try:
    SC = json.load(open(HERE + "/print/bambu/slice_check.json"))
except Exception:
    SC = {}
DENS = {"PLA": 1.24, "PLA-translucent": 1.24, "PETG": 1.27, "TPU 95A": 1.21}

from hardware import HW, table as hw_table, SRC_DATE   # bought parts: kit/hardware.py (one source for this file and make_susp_drive.py)
TOOLS = ["Soldering iron (heat-set inserts, LED and magnet wiring)", "Hex drivers 1.5 / 2.0 / 2.5, small Phillips", "CA glue + activator (shell seams), PETG-safe", "Side cutters and deburring knife (support removal)", "Fine sandpaper 220-400 and filler primer if painting"]


def plate_rows():
    rows = []
    for name, v in sorted(SC.items()):
        rows.append((name, v))
    return rows


def main():
    byd = collections.OrderedDict()
    for p in P: byd.setdefault(p["design"], []).append(p)
    L = ["# BOM and print list (generated)", "", "Mass = volume x density (PLA 1.24, PETG 1.27, TPU 1.21 g/cm3) at 100 % fill: an upper bound, ASSUMED. The Bambu slice numbers in the manual replace it.", "",
         "| ID | Part | Qty | Material | Walls | Infill | Support | Extents mm (oriented) | Volume cm3 | Mass g (max) |", "|---|---|---|---|---|---|---|---|---|---|"]
    tot = collections.Counter()
    for p in P:
        m = p["volume_cm3"] * DENS[p["material"]]; tot[p["material"]] += m
        L.append(f"| {p['id']} | {p['name']} | 1 | {p['material']} | {p['walls']} | {p['infill']} | {p['support']} | {' x '.join(str(int(e)) for e in p['extents'])} | {p['volume_cm3']} | {m:.0f} |")
    L += ["", "Upper-bound filament: " + ", ".join(f"{k} {v / 1000:.2f} kg" for k, v in tot.items()), ""]
    _t, _tot = hw_table(HW)
    L += ["## Hardware list (bought parts)", "", f"Quantities are counted from the model (`where` names the stand-in parts). Prices as listed on {SRC_DATE}, nothing bought. Retailer notes: `sourcing_2026-11-24.md`.", ""] + _t
    L += ["", "Status words: VERIFIED = listing opened and its spec read; ASSUMED = listing opened but a spec is missing, or a generic part sized from the model with an estimated price (est.); UNKNOWN = no purchasable part chosen yet. Total = packs to buy x pack price.", ""]
    open(HERE + "/bom.md", "w").write("\n".join(L))

    M = ["# Fugu reverse trike: assembly manual", "", "Print-only kit. Target printer: Bambu Lab P2S (256 x 256 x 256 mm), 0.4 mm nozzle, PLA for the shell and lights, PETG for the structure. "
         "Everything also fits the larger H2C-class bed. **Do not auto-orient or auto-arrange in Bambu Studio**: every file is already oriented and packed.", "",
         "## 1. Print plates", "", "Open `kit/print/bambu/all_plates.3mf` (every plate) or one plate file. Slot 3 = PLA, slot 4 = PETG (put PETG in AMS slot 4 or reassign in Studio).", "",
         "| Plate file | Filament | Time | Grams (Bambu slice) | Notes |", "|---|---|---|---|---|"]
    for name, v in plate_rows():
        fil = 'TPU 95A' if 'TPU' in name else ('PETG' if 'PETG' in name else 'PLA')
        M.append(f"| {name} | {fil} | {v.get('minutes', 0):.0f} min | {v.get('grams', 0):.0f} | {'; '.join(v.get('problems', [])) or 'sliced clean'} |")
    M += ["", "## 2. Printed parts", "", "| ID | Part | Plate group | Material | Joins |", "|---|---|---|---|---|"]
    for d in PARTS:
        pcs = ", ".join(p["id"] for p in byd.get(d["id"], []))
        M.append(f"| {pcs} | {d['name']} | {SUBS[d['sub']]} | {d['material']} | {d['mates']} |")
    M += ["", "Parts longer than the bed are printed in pieces (suffix a, b, c): the Front shell (SH1a/b), the Cage (CG1a/b/c) and, only with the closed cockpit, the Canopy (SH2a/b). Pin joints: pins on piece `a` go into the holes of piece `b`. Glue with CA, hold flat until set.", "",
          "## 3. Hardware to buy", "", "See `bom.md` for counts, part numbers and which are only ASSUMED.", "", "## 4. Tools", ""] + [f"- {t}" for t in TOOLS]
    steps = [
        ("Step 0: test fit", "Print the steering horn ST1 and one knuckle SU4 first. Press an M3 insert into a scrap, screw a 6.8 mm ball stud into the knuckle plate and snap a ball cup on. Test one 1.6 mm pin in a 1.75 mm hole on a Cage joint. Stop and tell the designer if a stud does not thread or a pin does not enter."),
        ("Step 1: chassis frame (CH1-CH5)", "Join decks CH1/CH2/CH3 to the donor chassis hardware, screw the skid CH4 under the front deck's front edge (2 x M3) and fit the motor plate CH5. Check: decks sit flat, no rocking."),
        ("Step 2: lean head and wishbones (SU1-SU4)", "Press M3 inserts into the four base tube bores of the lean head SU1 and screw it to the front deck from below, right behind the skid. Push the four 6 mm pivot rods in from the rear through the head and the pivot barrels of the upper wishbones SU2 (with the shock posts) and lower wishbones SU3. Screw the ball studs into the knuckle plates SU4, thread a ball cup into each wishbone tip and snap the cups onto the studs. Hang the heave shock between the two posts of the upper wishbones (M4 pins). Check: both wheels move up and down together against the shock, the body leans freely about 10 degrees each way with the shock length unchanged, nothing touches the deck or the head."),
        ("Step 3: steering (ST1-ST2)", "Screw the servo mount ST2 to the front deck behind the head (4 x M3 from below into inserts in its pillars), stand the low-profile servo between the pillars with the shaft up and screw its ears down (2 screws per ear), fit the printed T horn ST1 on the shaft and hang a ball stud from each end of it, and connect each horn ball to the ball stud on the knuckle's steering arm with a tie rod. Set both tie rods to the same length (93 mm ball to ball). Check: full lock both ways at full lean without rubbing; the tie rods pass 1.5 mm behind the pivot rod heads."),
        ("Step 4: drivetrain (DT5-DT17)", "Rear wheel drive only: assemble the bearing blocks DT5-DT8 and the ring hub DT10 on the rear shaft, fit the motor with its pinion to the motor plate against the spur gear, the single-sided rear arm DT11 with its pulleys DT14/DT15 and the 300 mm belt, the rear wheel DT17 and the rear shock. Fit the front wheels DT16 on the stub axles. Check: wheels turn by hand, belt tight, rear arm swings with no contact."),
        ("Step 5: cage (CG1a/b/c, CG3)", "Glue the three cage pieces on their pins (a to b to c), let cure 30 min. Press M3 inserts into the six feet, drop the feet into their deck pockets (front pair at y -127, behind the tie rods) and screw them from under the decks. Lay the roof plate CG3 on the roof frame. Fit the shock top bolt through the cage clevis. Check: full steering lock and full lean with the cage on: tie rods and shock posts clear the front tubes."),
        ("Step 6: shell (SH1a/b, SH4)", "Glue SH1a to SH1b on their pins, then the grille SH4 from inside the nose. Dry-fit over the cage first. Press an M3 insert into each of the two cage shell bosses (B upright), press M3 inserts into the three sill tabs inside the shell (two on the right, one on the left), set the shell over the cage and fix it with two ISO 7380 M3 x 8 through the counterbores in the flanks (heads sit below the skin) and three ISO 10642 M3 x 10 from under the deck into the sill tabs. Check: both front wheels at full lean and full lock clear the arches."),
        ("Step 7: lights (LT1, LT2, SH3, CG2)", "Press magnets (alternate polarity) into CG2 and the cage pad, fit LEDs in the pegs, push the strips into their channels, screw SH3 to the cage with two countersunk M3 x 8. Check: contacts meet with a 0.3 mm gap, strips sit flush."),
    ]
    for t, b in steps: M += ["", f"### {t}", "", b]
    M += ["", "## Known risks (not verified on a printed kit)", "",
          "- Nothing in this kit has been printed or assembled yet. Fits (ball studs, pivot rods, inserts) are from the model only.",
          "- Front end strength from FEM (target safety 2): upper wishbone 2.65, lower wishbone 2.30, lean head 2.12, knuckle 2.32, rear arm 2.56 (on its bearing seats). Cage 1.48 next to the shell screw bosses (OPEN, below 2). See NOTES.md.",
          "- Bought parts: bom.md gives the chosen part, retailer, price and status of each row; several chosen parts are discontinued or on backorder, and the generic hardware (ball studs, tie rods, shafts, rings, shims) has estimated prices.",
          "- No lean stop: lean turns both arms at once, a stop needs a lean link or a balance beam (owner decision). Rear travel is checked by tools/rear_check.py with a rigid shock stand-in.",
          "- Pin joints in the 3 mm shell walls are 1.6-2.0 mm pins: glue joint strength is unmeasured.",
          "- Chassis parts marked in the model as stand-ins (decks, plates) may not match the real printable parts. Check CH1-CH5, DT5-DT10 against your real chassis files.",
          "- Printer: NOTES.md says H3C (H2C-class, 330 x 320 mm); the saved projects are P2S. The kit is sized for P2S.",
          "- Front and rear tyres are chosen (bom.md); the model tyre envelopes are 62 mm wide, the chosen tyres 38 and 53.5 mm.", ""]
    open(HERE + "/assembly_manual.md", "w").write("\n".join(M))
    print("docs written")


if __name__ == "__main__":
    main()
