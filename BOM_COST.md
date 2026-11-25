# Bill of materials and cost estimate

Snapshot: last successful build of `model.py` (SOMA build `597ca5e8`, 2026-11-21 20:13, HEAD `130b3c3`, 99 parts). Prices gathered 2026-11-21/22. Nothing was ordered. Estimates, not quotes.

## Update November 24: steering, stops, battery and receiver mounts, deck lap, wheel-well liners

Current model (97 parts, 47 printed files, 13 plates). Bambu Studio slice check of every plate: 0 problems, 61.4 h and 1832 g in total (was 54.0 h,
1678 g). Per-part volumes and masses: `kit/bom.md` (regenerated). New printed parts: battery tray, receiver box and lid (PETG), droop stop bases
(PETG) and pads (TPU 95A), heave bump stop sleeve (TPU 95A); the front shell gained the wheel-well liners, lower-arch side panels and arm tunnel
frames. No new supplier quotes were requested; the November 22 estimate line is not re-fitted.

Bought parts added (not priced, ASSUMED part numbers):
| Qty | Part | Where |
|---|---|---|
| 4 | M3x10 countersunk screw (ISO 10642) | deck half lap, from below |
| 4 | M3x4 heat-set insert (ruthex RX-M3x4) | deck half lap |
| 4 | M3x10 socket head screw + 4 M3x4 inserts | droop stops |
| 4 | M3 heat-set insert 4.6 OD x 4 | knuckle arm studs (set from the back) |
| 4 | M3 nylock nut | steering-arm and horn ball studs |
| 2 | M2.5 countersunk screw + 2 M2.5 heat-set inserts | receiver lid |
| 4 | M3 screw + 4 M3 inserts | battery tray legs |
| 2 | M3 screw + 2 M3 inserts | receiver box |
| 2 | hook-and-loop strap, 20 mm | battery |
| 1 | TPU filament (95A), a few grams | stop pads, heave stop |

## Update November 22: wishbone front end, rear wheel drive, open cockpit

This section replaces the printed parts table and the totals below for the current model (commit after `a6a3463`, 84 parts, 39 printed files). The older sections are kept as the record of the November 21 snapshot and its supplier quotes.

### Printed parts now (from `kit/print/parts.json` and the Bambu Studio slice check of all 11 plates)

| Ref | Part | Printed files | Material | Volume cm3 | Supplier estimate USD |
|---|---|---|---|---|---|
| CG1 | Cage | 3 | PETG | 385.8 | 25.96 |
| CG2 | Front light contact block | 1 | PETG | 5.2 | 3.21 |
| SH1 | Front shell | 5 | PLA | 237.8 | 25.39 |
| SH4 | Grille insert | 1 | PLA | 10.3 | 3.44 |
| SU4 | Knuckle | 2 | PETG | 34.0 | 7.46 |
| SU1 | Lean head | 1 | PETG | 47.1 | 5.06 |
| SU3 | Lower wishbone | 2 | PETG | 37.6 | 7.62 |
| LT1 | Nose light strip | 1 | PLA-translucent | 3.0 | 3.11 |
| CG3 | Roof plate | 1 | PETG | 25.0 | 4.08 |
| ST1 | Steering horn | 1 | PETG | 1.9 | 3.07 |
| ST2 | Steering servo cradle | 1 | PETG | 17.2 | 3.74 |
| SH3 | Tail light housing | 1 | PLA | 48.1 | 5.10 |
| LT2 | Tail light strip | 1 | PLA-translucent | 1.8 | 3.06 |
| SU2 | Upper wishbone | 2 | PETG | 69.4 | 9.02 |
| DT15 | Rear axle pulley 30T GT2 (6 mm belt) | 1 | PETG | 2.2 | 3.08 |
| DT14 | Rear pivot pulley 26T GT2 (6 mm belt) | 1 | PETG | 1.8 | 3.06 |
| CH1 | Front deck | 1 | PETG | 96.4 | 7.23 |
| CH2 | Rear deck | 1 | PETG | 98.0 | 7.30 |
| CH3 | Tail deck | 1 | PETG | 52.3 | 5.29 |
| CH5 | Motor plate | 1 | PETG | 15.7 | 3.67 |
| DT5 | Pillow block lower | 1 | PETG | 8.3 | 3.34 |
| DT6 | Pillow block upper | 1 | PETG | 8.3 | 3.34 |
| DT7 | Rear bearing carrier lower | 1 | PETG | 34.3 | 4.49 |
| DT8 | Rear bearing carrier upper | 1 | PETG | 34.3 | 4.49 |
| DT11 | Rear swing arm | 1 | PETG | 135.1 | 8.94 |
| DT10 | Rear ring hub | 1 | PETG | 1.4 | 3.04 |
| CH4 | Skid plate | 1 | PETG | 12.5 | 3.53 |
| DT16 | Front wheel 1.9 in, 6-spoke | 2 | PETG | 43.5 | 7.88 |
| DT17 | Rear wheel 2.2 in, 6-spoke | 1 | PETG | 31.2 | 4.36 |
| | **Total** | **39** | | **1499.3** | **182.34** |

- Supplier estimate: no new quotes were requested. The figure applies the straight line fitted to the November 21 quotes (USD 2.98 + 0.0441 per cm3 per printed file); with the 30 % service fee and USD 5 handling that is about **USD 242**. Indicative only.
- Printing it yourself: the slice check gives **1678 g** of filament and **54.0 h** of print time over 11 plates (PETG and PLA, supports included). At about USD 20 to 25 per kg that is USD 34 to 42 of filament.

| Plate | Hours | Grams |
|---|---|---|
| plate_01_CH_PETG.3mf | 7.5 | 284.1 |
| plate_02_SU_PETG.3mf | 6.4 | 211.7 |
| plate_03_ST_PETG.3mf | 0.6 | 15.3 |
| plate_04_DT_PETG_1.3mf | 10.4 | 321.0 |
| plate_04_DT_PETG_2.3mf | 0.7 | 21.3 |
| plate_05_CG_PETG_1.3mf | 7.7 | 211.9 |
| plate_05_CG_PETG_2.3mf | 11.4 | 278.5 |
| plate_06_SH_PLA_1.3mf | 4.8 | 169.0 |
| plate_06_SH_PLA_2.3mf | 4.1 | 158.0 |
| plate_07_LT_PLA_translucent.3mf | 0.4 | 7.3 |

### Bought parts: changes against the priced list below

| Change | Line | Effect |
|---|---|---|
| removed | B4 front shocks, 33 mm (Pro-Line PRO638700) | - USD 49.99 |
| removed | B14 centring springs for the lean beam | - USD 3.99 |
| removed | B15 steel rod 5 mm (front pivot axle of the old swing arms) | - USD 9.99 |
| reduced | B2 steering servo: 1 instead of 2 (one servo steers both wheels) | - USD 44.95 |
| open | B8 LiPo: the battery tray and stand-in were removed; a battery is still needed but has no place or hold-down in this version | unchanged, flagged |
| added, unpriced | 8 x ball stud 6.8 mm M3 with ball cup (4 wishbone joints, 4 tie rod ends) | not priced |
| added, unpriced | 1 x front heave shock, 68 mm eye to eye, about 10 mm stroke, about 30 N/mm | not selected |
| added, unpriced | 4 x shoulder screw or rod D6 x 48 (wishbone pivots), 2 x axle pin D6 x 47 with 12 mm hex hub and M6 nut | not priced |
| added, unpriced | 2 x tie rod / turnbuckle M3, 93 mm ball to ball; 4 x M3 rod about 25 mm for the arm tip cups | not priced |

**Bought parts, priced, after these changes: USD 359.41 + CAD 8.32** (was USD 468.33 + CAD 8.32). Prices are the November 21 listings, not re-checked.

### Mismatches closed and still open

- Closed: the old 1/18 files (`README.md`, `bom.md`, `print_plan.md`) are deleted; `kit/bom.md`, `kit/registry.py` and the assembly manual now match the model.
- Open: no bearings are modelled at the wishbone pivots or the front stub axles (plain 6 mm rods in printed bores); the rear tyre is still 140 mm in the model; receiver and battery have no designed mounts.

## Totals

| Group | Amount | Notes |
|---|---|---|
| Printed parts, supplier subtotal (36 of 39 instances priced) | **USD 145.96** | 3DAPI PETG via kernelCAD, proxy geometry |
| kernelCAD service fee (30 %) | USD 43.79 | as quoted per batch (885/2947, 1130/3764, 1036/3451 cents) |
| kernelCAD order handling | USD 5.00 | per order; each of my 4 estimate calls carried it, one combined order would pay it once |
| **Printed, priced total** | **USD 194.75** | |
| Printed, not priced (Front shell, Canopy, Cage) | about USD 43.89 + 30 % | linear extrapolation (2.98 + 0.0441 x cm3), indicative only; the supplier returned no price (bbox 324-457 mm) |
| Bought parts, priced | **USD 468.33** + **CAD 8.32** | 16 lines, pack prices |
| Bought parts, unpriced | 15 lines | see below |
| Print mass (all 39 instances) | 1452 g PETG | 1.2 mm walls, 25 % infill (15 % body/shell), 1.27 g/cc |

Open-cockpit edit: `model.py` has an uncommitted change (after this build) that adds `OPEN_COCKPIT = True`, which drops the Canopy and the Rear light contact block (and its 2 magnets) and adds cabin tubes to the cage. If it lands: printed priced subtotal USD 143.08 (fee 42.92), mass 1349 g plus the cage's new tubes (not measured). The cage volume will change; re-measure after the next build.

## Method
- Geometry: per-part volume and surface area computed from the build's BREP cache (`.soma/geometry/597ca5e8....brep`) and bboxes from `.soma/model.map.json`, read-only (no build run: another session was running `soma analyze fem analyses/tie_rod.py` and a sweep check in this folder). The `exports/` STLs are from Nov 11-12 and stale; not used.
- Print mass = 1.27 x (min(V, A x 1.2 mm) + infill x remainder). Body/shell parts (Front shell, Canopy, Tail light housing, Grille insert) 15 %, everything else 25 %. Light strips are translucent PLA in `kit/registry.py`; costed as PETG here.
- Pricing: kernelCAD `estimate_assembly_manufacturing`, 5 calls of 3-8 parts. Each part is an open-top shell proxy with the part's exact bbox (assembly axes, not print orientation) and the same solid volume; the server's masses (density 1.38) match the part volumes. One instance priced per design; mirror pairs multiplied by 2 by hand.
- Bought: retail listings from web search on 2026-11-21. Stock was confirmed only where noted. Pack price is the line total.

## Printed parts
| Ref | Part | Qty | Instances | BBox mm (assembly axes) | Vol cm3 | Infill | Mass g each | Supplier $ each | Line $ |
|---|---|---|---|---|---|---|---|---|---|
| SH1 | Front shell | 1 | Front shell | 185.5 x 422.7 x 148.7 | 244.38 | 15% | 268.1 | unpriced (~13.76 extrap.) |  |
| SH2 | Canopy (open-cockpit: removed) | 1 | Canopy | 178.6 x 324.4 x 89.9 | 83.58 | 15% | 101.6 | unpriced (~6.66 extrap.) |  |
| SH3 | Tail light housing | 1 | Tail light housing | 92.8 x 57.3 x 47.8 | 48.03 | 15% | 39.6 | 5.16 | 5.16 |
| SH4 | Grille insert | 1 | Grille insert | 81.3 x 24.6 x 32.3 | 10.34 | 15% | 11.0 | 3.55 | 3.55 |
| LT1 | Nose light strip | 1 | Nose light strip | 114.7 x 45.8 x 24.4 | 2.91 | 25% | 3.7 | 2.82 | 2.82 |
| LT2 | Tail light strip | 1 | Tail light strip | 76.0 x 21.0 x 15.2 | 1.80 | 25% | 2.3 | 2.79 | 2.79 |
| CG1 | Cage | 1 | Cage | 149.4 x 457.1 x 203.3 | 464.28 | 25% | 350.7 | unpriced (~23.47 extrap.) |  |
| CG2 | Front light contact block | 1 | Front light contact block | 28.0 x 14.0 x 29.3 | 5.14 | 25% | 4.1 | 3.31 | 3.31 |
| CG3 | Rear light contact block (open-cockpit: removed) | 1 | Rear light contact block | 28.0 x 14.0 x 6.5 | 1.56 | 25% | 1.8 | 2.88 | 2.88 |
| CH1 | Front deck | 1 | w3 deck front | 109.0 x 150.6 x 16.5 | 92.15 | 25% | 71.9 | 5.86 | 5.86 |
| CH2 | Rear deck | 1 | w3 deck rear | 109.0 x 122.3 x 91.0 | 98.06 | 25% | 89.1 | 8.49 | 8.49 |
| CH3 | Tail deck | 1 | w3 deck tail | 96.5 x 88.6 x 65.3 | 52.26 | 25% | 45.4 | 5.78 | 5.78 |
| CH4 | Skid plate | 1 | w3 skid | 80.0 x 43.8 x 42.8 | 12.43 | 25% | 15.8 | 3.81 | 3.81 |
| CH5 | Motor plate | 1 | w3 motor plate | 60.0 x 21.1 x 46.4 | 15.65 | 25% | 14.4 | 3.91 | 3.91 |
| CH6 | Battery tray | 1 | battery tray c | 47.8 x 80.4 x 25.2 | 13.43 | 25% | 17.0 | 3.64 | 3.64 |
| CH7 | Front arm pivot block (L/R) | 2 | w3 arm pivot block -1, w3 arm pivot block 1 | 14.5 x 15.0 x 31.2 | 6.23 | 25% | 4.9 | 3.27 | 6.54 |
| SU1 | Front swing arm (L/R) | 2 | arm -1, arm 1 | 35.8 x 116.3 x 54.8 | 50.22 | 25% | 43.0 | 5.29 | 10.58 |
| SU2 | Upper link (L/R) | 2 | uplink -1, uplink 1 | 46.1 x 108.9 x 16.2 | 5.13 | 25% | 6.5 | 3.27 | 6.54 |
| SU8 | Lean beam | 1 | Lean beam | 129.3 x 36.0 x 12.9 | 31.98 | 25% | 21.7 | 3.86 | 3.86 |
| ST1 | Steering carrier (L/R) | 2 | carrier -1, carrier 1 | 31.7 x 18.0 x 64.4 | 8.94 | 25% | 7.9 | 3.88 | 7.76 |
| ST2 | Knuckle (L/R) | 2 | knuckle -1, knuckle 1 | 26.0 x 22.0 x 43.0 | 5.34 | 25% | 5.0 | 3.49 | 6.98 |
| ST3 | Tie rod (L/R) | 2 | tie rod -1, tie rod 1 | 48.0 x 130.1 x 18.3 | 5.89 | 25% | 7.5 | 3.30 | 6.60 |
| DT5 | Pillow block lower | 1 | w3 pillow lower | 30.0 x 15.4 x 21.9 | 8.26 | 25% | 6.2 | 3.19 | 3.19 |
| DT6 | Pillow block upper | 1 | w3 pillow upper | 30.0 x 15.4 x 21.9 | 8.26 | 25% | 6.2 | 3.19 | 3.19 |
| DT7 | Rear bearing carrier lower | 1 | w3 rbc lower | 34.1 x 65.5 x 25.4 | 34.17 | 25% | 22.6 | 3.71 | 3.71 |
| DT8 | Rear bearing carrier upper | 1 | w3 rbc upper | 34.1 x 65.5 x 25.4 | 34.17 | 25% | 22.6 | 3.71 | 3.71 |
| DT10 | Rear ring hub | 1 | w3 rring hub | 9.0 x 22.0 x 22.0 | 1.44 | 25% | 1.8 | 3.08 | 3.08 |
| DT11 | Rear swing arm | 1 | w3 rear arm | 90.4 x 149.8 x 78.7 | 136.32 | 25% | 97.2 | 8.99 | 8.99 |
| DT14 | Rear pivot pulley 26T GT2 | 1 | pulley r pivot | 13.0 x 18.2 x 18.2 | 1.80 | 25% | 2.3 | 3.05 | 3.05 |
| DT15 | Rear axle pulley 30T GT2 | 1 | pulley r axle | 13.0 x 20.7 x 20.7 | 2.22 | 25% | 2.8 | 3.10 | 3.10 |
| DT16 | Front wheel 1.9in (L/R) | 2 | wheel f -1, wheel f 1 | 34.0 x 53.3 x 53.3 | 21.37 | 25% | 24.1 | 4.21 | 8.42 |
| DT17 | Rear wheel 2.2in | 1 | wheel r | 46.0 x 60.9 x 60.9 | 31.18 | 25% | 34.7 | 4.66 | 4.66 |

## Bought parts, priced

| Ref | Need | Part | MPN | Unit | Cur | Line | Vendor | Notes |
|---|---|---|---|---|---|---|---|---|
| B1 | 1 | Motor + ESC 2-in-1, Hobbywing QuicRun Fusion SE 1800KV (540, FOC) | HWI30404317 | 79.99 | USD | 79.99 | [Horizon Hobby](https://www.horizonhobby.com/product/quicrun-fusion-se-for-crawler-540spec-1800kv/HWI30404317.html) | Model b motor 36 x 62 mm. Also $89.99 at Horizon/BeachRC; 1200KV is HWI30404318. Stock not confirmed. |
| B2 | 2 | Steering servo, low profile 40.8 x 20.2 x 26.5 mm, AGFRC B44BLS V2 15.5 kg | B44BLS V2 | 44.95 | USD | 89.90 | [Island Hobby Nut](https://islandhobbynut.com/products/agfrc-b44bls-v2-titanium-gear-15-5kg-0-060sec-high-speed-brushless-low-profile-servo) | BACKORDERED. eBay in stock at $77.55/ea. Horns and horn screws come with the servo. |
| B3 | 1 | Rear shock 100 mm piggyback (sold as pair, 1 used) | Integy C26651RED | 36.99 | USD | 36.99 | [Integy](https://integy.shop/products/rock-crawlers-hop-up-parts-c26651red) | In stock. Pack of 2; eye-to-eye length vs model 90.6 mm bbox not measured. |
| B4 | 2 | Front shocks, about 33 mm eye to eye, 9 mm body, M3 eyes (1/24 set of 4) | Pro-Line PRO638700 | 49.99 | USD | 49.99 | [Horizon Hobby](https://horizonhobby.com/product/1-24-big-bore-scaler-shocks-4-scx24/PRO638700.html) | Candidate: 34 mm extended vs model 33 mm. Hot Racing SXTF326R01 (32.5 mm) closer, price not found. |
| B5 | 1 | GT2 closed-loop belt 300 mm x 6 mm (2GT-300, rear arm drive) | Olimex GT2-BELT300-6MM | 3.22 | USD | 3.22 | [DigiKey](https://www.digikey.com/en/products/detail/olimex-ltd/GT2-BELT300-6MM/22078288) | 5-week lead time listed. Model asserts 300 mm length for 26T/30T pulleys. |
| B6 | 2 | Front tyre 1.9 in, about 112 mm (4.40 in) OD (pair) | Pro-Line Grunt 1.9 G8 10172-14 | 34.95 | USD | 34.95 | [Pro-Line Racing](https://www.prolineracing.com/tires/grunt-1.9-g8-rock-terrain-truck-tires.asp) | In stock, pair. Model tyre is 112 x 62 mm wide: tread width not checked. |
| B7 | 1 | Rear tyre 2.2 in, about 140 mm OD (pair, 1 used) | RC4WD Rock Crusher X/T 2.2 (Z-T0052 class) | 20.99 | USD | 20.99 | [HobbyEtc](https://store.hobbyetc.com/parts/view/26413) | 139 mm OD. Model tyre is 140 x 62 mm wide: width not checked. NOTES ask for a real tyre of 138 mm or less actual OD. |
| B8 | 1 | LiPo 3S 1300 mAh (fits model battery envelope 35 x 76.6 x 30 mm) | Turnigy nano-tech 1300 3S 45-90C | 10.43 | USD | 10.43 | [HobbyKing](https://hobbyking.com/en_us/turnigy-nano-tech-1300mah-3s-45-90c-lipo-pack.html) | Cached price, stock unknown. A 2S 2200 hardcase (93 mm long) does NOT fit the 76.6 mm tray. Connector to match ESC (XT60 vs ESC plug) not checked. |
| B9 | 1 | Radio: FlySky FS-i6X transmitter + FS-iA6B receiver | FS-i6X + FS-iA6B | 71.03 | USD | 71.03 | [Walmart](https://www.walmart.com/ip/403571177) | iA6B is about 40 x 22.6 x 13 mm vs model receiver 15 x 24.6 x 10.7: check the receiver bay or use a smaller receiver. |
| B10 | 2 | Bearing 8 x 16 x 5 (rear axle, 8 mm) 10-pack | 688-2RS | 9.99 | USD | 9.99 | [Walmart](https://www.walmart.com/ip/688-2RS-Ball-Bearing-8x16x5mm-Double-Sealed-Chrome-Steel-Bearings-10-Pack/314908247) | Size and count ASSUMED: no bearing is modelled; rear bearing carrier and pillow blocks have no bearing seats yet. |
| B11 | 4 | Bearing 5 x 11 x 4 (5 mm rear shaft) 10-pack | 3RACING MR115ZZ | 8.32 | CAD | 8.32 | [RC Jaz](https://www.rcjaz.ca/3racing-double-metal-shield-bearing-11-mm-10-pcs-3rbmr115zz10-p-90002051.html) | Size from kit/bom.md (5x11x4), count ASSUMED. Bearing Boys GBP 9.40 ex VAT alternative. |
| B12 | 20 | Heat-set insert M3 brass 100 pcs | M3 x 5 heat-set, 100 pcs | 12.64 | USD | 12.64 | [eBay](https://www.ebay.com/itm/156772193702) | Needed about 20 (6 cage feet, 2 tail stubs, 4 arm pivot blocks, deck/motor plate). Pocket 4.2 x 5-5.5 deep: check OD. |
| B13 | 1 | Screw kit M3-M6 stainless button head + nuts + washers, 900 pcs | MYWISH SF-TZ00001 | 26.74 | USD | 26.74 | [Home Depot](https://www.homedepot.com/p/MYWISH-900-Piece-Stainless-Steel-Button-Head-Hex-Socket-Screw-Kit-M3-M4-M5-M6-Assortment-with-Nuts-and-Washers-SF-TZ00001/334334770) | Covers M3 x 8 button, M6 shock pins (28/35 mm length not confirmed), nuts. No countersunk screws: see unpriced. |
| B14 | 2 | Compression spring 5 mm OD x 10 mm free, about 2 N/mm (10 pcs) | generic 5 x 10 mm lot | 3.99 | USD | 3.99 | [eBay](https://www.ebay.com/itm/226503234535) | Lean centring springs. Rate not stated in listing. |
| B15 | 2 | Steel rod 5 mm x 200 mm, 304 stainless, 5 pcs | 5 x 200 mm rod 5-pack | 9.99 | USD | 9.99 | [Newegg](https://www.newegg.com/p/1SW-00JE-00ZR1) | Front pivot axle 5 x 172 mm, rear shaft 5 x 102 + 10 mm. Stainless craft stock, not hardened. |
| B16 | 1 | Steel rod 8 mm x 100 mm, 304 stainless, 2 pcs | 8 x 100 mm rod 2-pack | 7.49 | USD | 7.49 | [Newegg Business](https://www.neweggbusiness.com/p/9B-1SW-00JE-014J4) | Rear axle 8 x 100 mm. Not hardened. |

## Bought parts, unpriced

| Ref | Qty | Part | Why unpriced |
|---|---|---|---|
| U1 | 1 | Motor pinion, about 12 mm OD, 3.175 mm (1/8 in) bore | tooth count and pitch not chosen (parts/rwd.py PINION_D 12) |
| U2 | 1 | Spur gear, about 33 mm OD, 5 mm bore | tooth count and pitch not chosen (SPUR_D 33) |
| U3 | 1 | Rear ring gear (b rear ring, 25.6 mm) and matching bevel pinion | donor SCX10 III-class part, no part number chosen |
| U4 | 1 | 12 mm hex hub, rear (mock rear hub) | SCX10 III-class; candidate AXI232018-replacement in kit/sourcing_amazon.md, not priced |
| U5 | 4 | Steel pins 4 mm: 2 x 54.5 mm (tip shafts), 2 x 30 mm (front stub axles) | no rod listing priced |
| U6 | 4 | M3 ball stud, D6 ball, 16 mm stud + M3 nut + washer | steering ends; ball studs not found as a priced pack |
| U7 | 8 | Pins/bolts M3 x 12.6 mm (front shock pins x4, upper-link pins x4) | could come from the screw kit if M3 x 12 bolts work as pins |
| U8 | 1 | M4 shoulder bolt (lean beam pivot, bore 4.3, 29 mm) | not priced |
| U9 | 8 | Countersunk M3: 6 x M3 x 8 (cage feet from under the deck), 2 x M3 x 12 (tail housing) | not in the button-head kit |
| U10 | 6 | Self-tapping M2 x 6 (shell to cage bosses) | not priced |
| U11 | 8 | Neodymium disc magnet 6 x 3 mm N52 | no exact 6x3 pack price found |
| U12 | 4 | LED 3 mm red + resistors and wire | not priced |
| U13 | 2 | Zip ties (shock bridge) | not priced |
| U14 | 1 | Wheel retaining hardware for printed wheels (hex pocket screws) | not modelled |
| U15 | 1 | Battery charger, Hobbywing program box (optional) | not in the model, not priced |
Excluded from the printed list: `Rear shell` and `Rear shock bridge` (old exports, not placed in the current assembly); the old lean mount/rocker/ears/horn, pods, front and centre diff cases, centre ring hub and front pulleys (removed by the RWD change, `parts/rwd.py` REMOVE); `steer horn ±1` (servo horns, bought with the servo per `kit/registry.py`); all `b ...`/`mock ...` parts (bought).

## Mismatches found
- `README.md`, `bom.md` and `print_plan.md` (untracked, dated Nov 19) describe a different, older 1/18 design (250 mm, Hobbywing Mini16 30120403, 9 g servo, MR63ZZ). They do not match `model.py`.
- `kit/bom.md` and `kit/registry.py` (Nov 18-20) still list the front/centre diff cases, lean mount set, pods and front GT2 pulleys, all removed in the Nov 21 RWD change; they miss the arm pivot blocks, the lean beam and the new motor plate.
- `kit/bom.md` lists Fusion SE 1800KV; the reference list given to me had the 1200KV (HWI30404318). Both fit the same 36 x 58 mm body; I priced the 1800KV the kit names.
- The reference list had bought Roapex wheels and an Adafruit GT2 20T pulley; Project_Fugu prints the wheels (DT16/DT17, 6-spoke, 12 mm hex) and the GT2 pulleys (26T/30T). The tie rods are printed tubes here (no turnbuckle), so nothing was excluded as envelope-only. Savox B-12KG, AXI232002/003/033, 685ZZ, MR84ZZ, CVD kit and the M3 turnbuckle are not called for by this model and were not included.
- The NOTES hardware table says cage feet are screwed from the top with tabs; the Nov 21 section says M3 countersunk from under the deck into inserts in the feet (newer, used here).
- Battery: the model's 35 x 76.6 x 30 mm envelope does not fit common 2S 2200 hardcase packs (93 mm); a 3S 1300 fits. Receiver: the 15 x 24.6 x 10.7 mm envelope is smaller than the FS-iA6B.
- No bearings are modelled; the rear bearing carrier and pillow blocks have no seats yet, so bearing sizes and counts are assumptions. The chassis decks and carriers are still convex-hull stand-ins (NOTES), so their printed cost will change when they are designed.
- The NOTES (Nov 11) say the rear tyre should be 138 mm actual OD or less; the model uses 140 mm.

## Sources
kernelCAD estimate request ids: 5791824f (batch 1), 0ec94c1e (2), 1a74188c (3), 9903ac78 (4), b33ec8b8 (oversize retry, unavailable). Vendor links are in the bought table and `BOM_COST.csv`.
