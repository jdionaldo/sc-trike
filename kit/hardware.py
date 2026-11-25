"""Bought parts of the Fugu kit, one row per item: the single source for kit/bom.md (make_docs.py) and the suspension + drivetrain kit (make_susp_drive.py).

Fields: grp (SU front suspension, ST steering, DT drivetrain, CH chassis/electronics, CG cage, SH shell, LT lights), item, qty (counted from the model,
see `where`), where, part (brand + part number, retailer URL), unit (USD per pack as listed), pack (pieces per pack), status, note.
Status: VERIFIED = listing opened and its spec read on SRC_DATE; ASSUMED = listing opened but a spec is missing, or a generic part whose size is
taken from the model and whose price is an estimate (marked "est."); UNKNOWN = no purchasable part chosen. Packs to buy = ceil(qty / pack).
Sourcing notes with every URL: kit/sourcing_2026-11-24.md.
"""
import math

SRC_DATE = "2026-11-24"
H = lambda **k: k
HW = [
    # --- front suspension ---------------------------------------------------------------------------------------------------------------------------
    H(grp="SU", item="Heave shock 70 mm (one shock between the upper wishbones)", qty=1, where="Heave shock pins in the forks of SU2 (model: 68 mm eye to eye, about 10 mm stroke, about 250 N at full bump)",
      part="RC4WD Ultimate Scale Shock 70 mm RC4Z-D0004, Hobby ETC https://store.hobbyetc.com/parts/view/29506 (alt. RC4WD King 70 mm RC4ZD0037, AMain)", unit=20.99, pack=2,
      status="VERIFIED", note="listing: 72.5 mm extended / 55.1 compressed, stroke 17.4 mm, eye bore 3.0 mm, body 8.8 mm; DISCONTINUED, not oil filled, very soft spring: no listing gives a spring rate (30 N/mm needed); 4.5 mm longer than the model's 68 mm, eye bore 3.0 against the model's 4.1 mm pin hole"),
    H(grp="SU", item="Heave shock pin: M3 x 20 socket screw + M3 nylock (eye bore 3.0 of the chosen shock)", qty=2, where="shock eyes in the forks of SU2 (model hole D4.1 for an M4 pin)",
      part="generic ISO 4762 M3 x 20 + DIN 985 M3", unit=0.30, pack=1, status="ASSUMED", note="est. price; with an M3 pin the fork hole D4.1 is 1.1 mm loose: sleeve 4 x 3 mm or shrink the hole when the shock is chosen"),
    H(grp="SU", item="Wishbone pivot: shoulder screw ISO 7379, D6 x 45 shoulder, M5 thread", qty=4, where="Pivot rod upper/lower x 2 sides through the lean head SU1 and the arms SU2/SU3 (model rod D6 x 48.7)",
      part="Zoro ZR1846-303H (6 x 45, M5, 18-8 SS) https://www.zoro.com/ampg-smooth-hd-skt-shld-scrw-6m5x45-18-8ss-zr1846-303h/i/G0819452", unit=15.39, pack=1,
      status="ASSUMED", note="page refused automated fetch (price from the search result); FIXING OPEN: the M5 end would thread into the printed front post (no printed threads below M6): an M5 nylock in front of the post needs about 6 mm of free space that is not checked"),
    H(grp="SU", item="Ball joint: M3 rod end with its own 6.8 mm steel ball (matched pair), the ball held by an M3 screw", qty=4, where="Ball stud upper/lower x 2 (ball on the knuckle plate) + Rod end upper/lower x 2 (cup on the wishbone tips)",
      part="Gmade GMA20216 M3 Rod End w/ 6.8mm Steel Ball (10), Hobby Recreation Products https://www.hobbyrecreationproducts.com/collections/gmade-komodo-kit/products/gma20216-m3-rod-end-w-6-8mm-steel-ball", unit=12.00, pack=10,
      status="VERIFIED", note="listing opened 2026-11-25: M3 rod end and 6.8 mm steel ball sold together (OUT OF STOCK); one pack covers all 8 joints (4 arm, 4 steering). Replaces the separate stud + cup rows (the cups found earlier took 6.92 mm balls). Alt.: Xray 352659 6.8 mm M3 studs with Xray 352664 / 352665 6.8 mm composite ball joints, both VERIFIED on xray / redrc pages, but those cups are M4: arm tips and tie rods would need M4"),
    H(grp="SU", item="M3 x 16 socket screw (through the hollow 6.8 mm ball into the knuckle insert)", qty=4, where="Ball stud upper/lower x 2", part="generic ISO 4762", unit=0.10, pack=1, status="ASSUMED", note="est.; length to suit the ball height (not stated on the listing): thread 8-12 mm into the insert set 7.5 mm behind the plate face"),
    H(grp="SU", item="M3 threaded rod 25 mm (or M3 x 25 set screw) for the arm tip cups", qty=4, where="apex boss of each wishbone SU2/SU3", part="generic", unit=0.20, pack=1, status="ASSUMED", note="est."),
    H(grp="SU", item="Heat-set insert M3, OD 4.6 x 4 mm", qty=16, where="knuckles 2 x 2 (arm studs, set from the back), arm tips 4, lean head base 4, droop stops 2 x 2",
      part="Adafruit 4255 M3 x 4 brass (OD 4.2), 50 pack https://www.adafruit.com/products/4255", unit=5.95, pack=50, status="VERIFIED",
      note="listing OD 4.2 mm: the model pockets are D4.2 for OD 4.6 inserts, so with this insert shrink the pockets to D3.8 or buy OD 4.6 (RS PRO 204-0616, not opened); arm tip bores are D4.1"),
    H(grp="SU", item="Countersunk screw M3 x 10 (ISO 10642)", qty=8, where="lean head SU1 to the front deck 4, droop stops SU5 to the deck 2 x 2, all from below into inserts", part="generic", unit=0.10, pack=1, status="ASSUMED", note="est."),
    H(grp="SU", item="Front wheel bearing 6x12x4 (MR126)", qty=4, where="Wheel bearing inner/outer x 2 in the printed front wheels DT16 (seats D12.1 x 4)",
      part="MR126-2RS 10 pack, Hobby ETC https://store.hobbyetc.com/parts/view/131896", unit=10.99, pack=10, status="VERIFIED", note="rubber sealed"),
    H(grp="SU", item="Shim 6 x 8 x 0.5 mm (inner race only)", qty=4, where="Axle shim inner/outer x 2: knuckle boss face and under the axle nut", part="generic RC shim 6 x 8", unit=0.25, pack=1, status="UNKNOWN", note="est.; no listing found"),
    H(grp="SU", item="Front stub axle: M6 x 60 hex bolt ISO 4014 (18 mm thread) cut to 48 mm + M6 nylock DIN 985", qty=2, where="Axle pin x 2: x 118.6..166 in the knuckle boss SU4, the bearings on the shank",
      part="generic", unit=0.60, pack=1, status="ASSUMED", note="est.; room for the bolt head inboard of the knuckle boss is not checked; snug the nylock only until the wheel turns freely with no play"),
    # --- steering -------------------------------------------------------------------------------------------------------------------------------------
    H(grp="ST", item="Low-profile steering servo 40.8 x 20.2 x 26.5 mm, 25T", qty=1, where="Steer servo in ST2", part="AGFRC B44BLS V2, Amazon B07L83M8SM", unit=44.95, pack=1,
      status="ASSUMED", note="page not opened today (503/429): price and backorder from the search result; size VERIFIED on 2026-11-18"),
    H(grp="ST", item="Servo horn screw (with the servo)", qty=1, where="ST1 on the servo shaft", part="supplied with the servo", unit=0.0, pack=1, status="ASSUMED", note="HORN_METAL option (metal 25T horn) is prepared in the model, off"),
    H(grp="ST", item="Ball joint for the steering (in the same Gmade GMA20216 pack as the arm joints) + M3 x 20 screw through the ball, nylock", qty=4, where="Steer stud knuckle x 2, Steer stud horn x 2", part="Gmade GMA20216 (pack counted in the SU row); M3 x 20 ISO 4762", unit=0.10, pack=1, status="ASSUMED", note="screw est.; the 6.8 mm ball sits on the steering arm / horn, the screw passes through (D3.3) and takes the nylock"),
    H(grp="ST", item="M3 nylock nut DIN 985", qty=4, where="Steer stud nut knuckle x 2, Steer stud nut horn x 2", part="generic", unit=0.05, pack=1, status="ASSUMED", note="est."),
    H(grp="ST", item="Tie rod M3 turnbuckle with two ball cups, 93 mm ball to ball", qty=2, where="Tie rod x 2, horn to knuckle", part="generic M3 turnbuckle 1/10 RC", unit=3.00, pack=1, status="UNKNOWN", note="est.; no listing opened"),
    H(grp="ST", item="Self-tapping screw M2.5 x 10 (servo ears)", qty=4, where="servo ears into the ST2 pillars", part="generic", unit=0.05, pack=1, status="ASSUMED", note="est."),
    # --- drivetrain -------------------------------------------------------------------------------------------------------------------------------------
    H(grp="DT", item="Motor + ESC 2-in-1, 540, 1800KV", qty=1, where="b motor on the motor plate CH5", part="Hobbywing QuicRun Fusion SE HWI30404317, Horizon Hobby https://www.horizonhobby.com/product/quicrun-fusion-se-for-crawler-540spec-1800kv/HWI30404317.html", unit=89.99, pack=1, status="VERIFIED", note="in stock on the listing"),
    H(grp="DT", item="Motor pinion 32P 15T, 1/8 in (3.175 mm) bore, steel", qty=1, where="b motor pinion", part="ServoCity 15T 1/8 in bore 32P steel https://www.servocity.com/15t-0-125-1-8-bore-32p-shaft-mount-pinion-gear-steel", unit=5.99, pack=1, status="VERIFIED", note="set screw not listed"),
    H(grp="DT", item="Spur gear 32P 40T, 5 mm bore", qty=1, where="b spur gear on the front end of the rear shaft (model D33)", part="Yeah Racing AXSC-034 40T hardened steel (5 mm shaft), alt. Axial AXI-3860 40T", unit=14.99, pack=1,
      status="ASSUMED", note="both DISCONTINUED; 15T/40T meshes at 21.8 mm: the motor plate slots (MESH_SLOT +-1 mm) cover 21.5..23.5; a 42T 5 mm-bore spur was not found"),
    H(grp="DT", item="Ring and pinion, steel (90 deg drive, rear shaft to cross shaft)", qty=1, where="b rear ring on the ring hub DT10, pinion on the rear shaft end", part="Axial AXI232003 30T / 8T, https://www.axialadventure.com/product/AXI232003.html", unit=19.99, pack=1,
      status="ASSUMED", note="DISCONTINUED, bores not listed; MISMATCH: the model's ring stand-in is 25.6 mm OD, a 30T SCX10 ring is larger: the carrier DT7/DT8 cavity must be checked against the real ring"),
    H(grp="DT", item="Rear drive shaft, 5 mm hardened steel, 112 mm", qty=1, where="b rear shaft front + b rear shaft (y -2.5..109.4), in 3 bearings", part="generic 5 mm linear shaft (McMaster / Misumi, cut)", unit=8.00, pack=1, status="UNKNOWN", note="est.; listing not readable here"),
    H(grp="DT", item="Cross (pivot) shaft, 5 mm hardened steel, 88 mm", qty=1, where="x -10..78 through the carriers DT7/DT8, ring hub DT10, pivot pulley DT14 and the 3 pivot plates of DT11", part="generic 5 mm linear shaft (cut)", unit=8.00, pack=1, status="UNKNOWN", note="est.; no stand-in in the model (bore line probed)"),
    H(grp="DT", item="Rear axle, 8 mm hardened steel, 100 mm", qty=1, where="mock rear axle (x -24..76) in DT11, axle pulley DT15, rear hub", part="VXB 8 x 100 mm HRC60, 5 pcs https://vxb.com/products/8mm-100mm-hardened-linear-motion-shafts", unit=49.93, pack=5, status="VERIFIED", note="price label ambiguous on the page (49.93 / 80.00)"),
    H(grp="DT", item="Bearing 5x11x4 (MR115)", qty=8, where="rear shaft: pillow block DT5/DT6 1, carrier DT7/DT8 2; cross shaft: carrier 2, swing arm pivot plates 3", part="MR115-2RS 10 pack, Hobby ETC https://store.hobbyetc.com/parts/view/130884", unit=11.49, pack=10, status="VERIFIED", note="seat D11.1"),
    H(grp="DT", item="Bearing 8x16x5 (688)", qty=2, where="rear axle in the swing arm DT11 (seats D16.1 x 5)", part="688-2RS 10 pack, Hobby ETC https://store.hobbyetc.com/parts/view/131894", unit=10.99, pack=10, status="VERIFIED", note=""),
    H(grp="DT", item="Retaining ring DIN 471, 5 mm and 8 mm", qty=6, where="2 on the cross shaft, 2 on the rear shaft, 2 on the rear axle", part="generic assortment", unit=6.00, pack=100, status="UNKNOWN", note="est.; no listing opened"),
    H(grp="DT", item="Rear hub, 12 mm hex, 8 mm bore", qty=1, where="mock rear hub: axle to the rear wheel DT17", part="Axial AXI232046 12 mm hex hub (bore not listed) https://store.hobbyetc.com/parts/view/159353", unit=11.99, pack=1,
      status="UNKNOWN", note="no 8 mm-bore 12 mm hex hub found: bore a 12 mm hex hub out to 8 mm (2 mm wall) with a grub on an axle flat, or redesign the hub"),
    H(grp="DT", item="GT2 closed-loop belt 2GT-300, 6 mm wide (150 teeth)", qty=1, where="b gt2 belt r: pivot pulley DT14 26T to axle pulley DT15 30T", part="generic 2GT-300-6", unit=7.50, pack=1, status="ASSUMED", note="est.; listing 404; centre distance 122.1 gives 300.2 mm: no slack"),
    H(grp="DT", item="Grub screw M3 x 4", qty=2, where="one in each printed pulley hub DT14, DT15", part="generic ISO 4029", unit=0.10, pack=1, status="ASSUMED", note="est."),
    H(grp="DT", item="Rear shock 100 mm class, oil", qty=1, where="Rear shock between the cage clevis and the arm bridge", part="Integy C26651RED (pair) https://integy.shop/products/rock-crawlers-hop-up-parts-c26651red", unit=36.99, pack=2, status="ASSUMED", note="page refused (429): price from search; eye-to-eye, stroke and eye bore not read; model eye bore M6"),
    H(grp="DT", item="Shock bolt M6 + M6 nylock: M6 x 30 (lower), M6 x 35 (upper)", qty=2, where="M6 shock pin (lower), M6 shock pin", part="generic ISO 4762 + DIN 985", unit=0.50, pack=1, status="ASSUMED", note="est.; lengths from the model clevis spans 20.8 / 24.0 mm"),
    H(grp="DT", item="Socket screw M3 x 6 (motor face) and M3 x 10 (plate to deck)", qty=4, where="2 into the motor on a 25 mm pattern, 2 through the plate gussets into the deck", part="generic", unit=0.10, pack=1, status="ASSUMED", note="est."),
    H(grp="DT", item="Screws for the pillow block and bearing carrier halves", qty=0, where="DT5/DT6 and DT7/DT8 to the decks", part="generic M3", unit=0.10, pack=1, status="UNKNOWN", note="count not taken from the traced carrier meshes"),
    H(grp="DT", item="Front tyre 1.9 in, about 112 mm OD", qty=2, where="mock tire x 2 on the printed wheels DT16 (bead seat 48.3)", part="Pro-Line Toyo Open Country R/T G8 1.9 PRO1021114 (pair) https://www.axialadventure.com/product/1-10-toyo-open-country-r-t-g8-f-r-1.9-rock-crawling-tires-2/PRO1021114.html", unit=24.99, pack=2,
      status="VERIFIED", note="113 x 38 mm; DISCONTINUED; alt. RC4WD Scrambler RC4ZT0144 104 x 43 (backorder); the model's tyre envelope is 62 mm wide"),
    H(grp="DT", item="Rear tyre 2.2 in, about 140 mm OD", qty=1, where="Rear tire on the printed wheel DT17 (bead seat 55.9)", part="RC4WD Mud Slinger 2 XL 2.2 RC4ZT0122 (pair, with foams) https://www.amainhobbies.com/rc4wd-mud-slinger-2-xl-2.2-scale-crawler-tires-2-rc4zt0122/p-qtqrtarqbc2xactz", unit=29.99, pack=2,
      status="VERIFIED", note="139.7 x 53.5 mm, ID 55.5 (0.4 mm tight on the bead seat); backorder; the model's tyre envelope is 62 mm wide"),
    # --- chassis, electronics, cage, shell, lights (outside the suspension + drivetrain kit) ------------------------------------------------------------
    H(grp="CH", item="2S-3S LiPo, fits the tray CH6", qty=1, where="Battery tray CH6 over the steering servo (b battery stand-in)", part="any 2S-3S pack within the tray", unit=0.0, pack=1, status="UNKNOWN", note="pack not chosen"),
    H(grp="CH", item="Hook-and-loop battery strap", qty=2, where="CH6 strap slots", part="generic", unit=1.00, pack=1, status="ASSUMED", note="est."),
    H(grp="CH", item="Heat-set insert M3 + M3 x 10 countersunk", qty=12, where="tray CH6 4, receiver box CH7 2, deck half lap 4, skid plate 2", part="generic", unit=0.20, pack=1, status="ASSUMED", note="est."),
    H(grp="CH", item="M2.5 countersunk screw + M2.5 insert", qty=2, where="receiver lid CH8", part="generic", unit=0.20, pack=1, status="ASSUMED", note="est.; the FS-iA6B receiver no longer fits the bay (open)"),
    H(grp="CG", item="Heat-set insert M3 x 4 + countersunk M3 x 10 / x 8", qty=8, where="6 cage feet, 2 tail-housing stubs", part="generic", unit=0.20, pack=1, status="ASSUMED", note="est."),
    H(grp="SH", item="Self-tapping screw M2 x 6", qty=6, where="shell to cage bosses", part="generic", unit=0.05, pack=1, status="ASSUMED", note="est."),
    H(grp="LT", item="Neodymium magnet 6 x 3 mm N52", qty=8, where="light contacts front and rear", part="generic", unit=0.30, pack=1, status="ASSUMED", note="est."),
    H(grp="LT", item="LED 3 mm red + resistor", qty=4, where="2 tail, 2 nose", part="generic", unit=0.20, pack=1, status="ASSUMED", note="est.; wiring not designed"),
]


def cost(r):
    """(packs, line total) for one row."""
    packs = math.ceil(r["qty"] / r["pack"]) if r["qty"] else 0
    return packs, round(packs * r["unit"], 2)


def table(rows):
    L = ["| Item | Qty | Where (model) | Part / retailer | Unit USD (pack) | Packs | Total USD | Status | Note |", "|---|---|---|---|---|---|---|---|---|"]
    tot = 0.0
    for r in rows:
        n, t = cost(r); tot += t
        L.append(f"| {r['item']} | {r['qty'] or '?'} | {r['where']} | {r['part']} | {r['unit']:.2f} ({r['pack']}) | {n} | {t:.2f} | {r['status']} | {r['note']} |")
    L.append(f"| **Total** | | | | | | **{tot:.2f}** | | |")
    return L, round(tot, 2)
