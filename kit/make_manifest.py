"""parts.json -> bambu_kit manifest (one plate group per sub-assembly and material)."""
import json, sys, os
from registry import SUB_ORDER, SUBS, PARTS
OPT = {d["id"] for d in PARTS if d.get("option")}   # printed options (ST3 printed tie rod): on the suspension + drivetrain kit's options plate only
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.environ.get("FUGU_OUT", HERE + "/print")
P = json.load(open(OUT + "/parts.json"))["parts"]
SLOT = {"PLA": 3, "PLA-translucent": 3, "PETG": 4, "TPU 95A": 4}   # TPU: no TPU profile in the saved project: sliced on the PETG slot, swap to TPU 95A in Studio   # AMS slots of the saved P2S project: 3 = PLA Basic, 4 = swap to PETG
plates = []
for n, sub in enumerate(SUB_ORDER, 1):
    for mat in ("PLA", "PLA-translucent", "PETG", "TPU 95A"):
        ps = [p for p in P if p["sub"] == sub and p["material"] == mat and p["design"] not in OPT]
        if not ps: continue
        plates.append(dict(name=f"{n:02d}_{sub}_{mat.replace('-', '_').replace(' ', '_')}", title=f"{SUBS[sub]} ({mat})",
                           parts=[dict(stl=f"stl/{p['id']}.stl", name=p["id"], walls=p["walls"], infill=p["infill"], support=p["support"],
                                       slot=SLOT[mat], **({"brim": 3} if max(p["extents"][:2]) > 100 and p["sub"] in ("SH", "CG") else {})) for p in ps]))
man = dict(title="Fugu reverse trike kit", profile=os.environ.get("FUGU_PROFILE", "../p2s_profile.config"), out="bambu", bed=[float(v) for v in os.environ.get("FUGU_BED", "256,256,256").split(",")[:2]], margin=5, gap=22, filament_slot=3,
           supports="easy_peel", plates=plates)
json.dump(man, open(OUT + "/kit_manifest.json", "w"), indent=1); print(len(plates), "plate groups")
