# WS-03 bill of materials and cost

Read 2026-11-21. Prices are indicative; nothing was ordered. Covers the current WS-03 3WD build (`ws02/`), not the older 1/18 build in the repo root.

## Totals

| group | cost | basis |
|---|---|---|
| Printed parts, 33 pieces (30 designs), PETG | $140.30 supplier subtotal | kernelCAD FDM estimate, vendor 3DAPI, PETG Black |
| kernelCAD fees if ordered there as one order | about $47 (30 % service fee plus $5 handling) | fee rate from the three estimates |
| Bought parts with a found price | $451.13 + GBP 42.84 + CAD 8.60 | retail listings, see table |
| **Total, priced lines** | **$591.43 + GBP 42.84 + CAD 8.60** (plus about $47 kernelCAD fees if printed there) | currencies left unconverted |
| Bought parts not priced | 13 lines (belts, shafts, pins, ball studs, horns, fasteners, magnets, LEDs, program card) | see below |

Home printing instead: about 672 g of PETG at 1.2 mm walls and 25 % infill (15 % for the body), from `w3_mass.printed_mass` on the rebuilt STLs.

## How the printed prices were made

- All WS-03 printed parts were rebuilt from the repo: mesh parts with `build.run_part`, the ten SolidCraft command-list parts (cases, motor plate, trays, standoff) replayed with manifold3d (only `solid.box` and `solid.cylinder` are used; volumes match `WS03_REPORT.md`), body with `body3_build` and `split_shell3`.
- kernelCAD's hosted server cannot read local STLs, so each part was priced as a proxy: an open-top PETG shell with the part's exact bounding box and solid volume. Vendor FDM pricing is driven by size and material volume, so this tracks the real part, but it is not a quote on the real mesh.
- `price_part` never left the "pricing" state (over 15 minutes on a plain box) and `write_bom` failed on the server (missing output folder), so pricing used `estimate_assembly_manufacturing` and this table and CSV were written locally.

## Printed parts

| part | qty | size mm | solid cm3 | print g | unit $ |
|---|---|---|---|---|---|
| w3_arm_left | 1 | 121.0 x 31.6 x 20.3 | 30.6 | 19.1 | 3.97 |
| w3_arm_right | 1 | 121.0 x 31.6 x 20.3 | 30.6 | 19.1 | 3.98 |
| w3_carrier_left | 1 | 18.0 x 54.5 x 28.3 | 6.3 | 3.9 | 3.26 |
| w3_carrier_right | 1 | 18.0 x 54.5 x 28.3 | 6.3 | 3.9 | 3.26 |
| w3_cdc_lower | 1 | 47.0 x 52.0 x 22.0 | 29.4 | 16.2 | 3.63 |
| w3_cdc_upper | 1 | 47.0 x 52.0 x 22.0 | 28.8 | 15.9 | 3.63 |
| w3_fdc_lower | 1 | 78.0 x 80.5 x 22.0 | 88.6 | 40.3 | 4.66 |
| w3_fdc_upper | 1 | 78.0 x 60.0 x 22.0 | 77.7 | 35.1 | 4.32 |
| w3_knuckle_left | 1 | 22.0 x 43.0 x 26.0 | 5.5 | 3.3 | 3.24 |
| w3_knuckle_right | 1 | 22.0 x 43.0 x 26.0 | 5.5 | 3.3 | 3.24 |
| w3_lean_rod | 2 | 40.4 x 10.4 x 5.0 | 1.1 | 0.9 | 2.86 |
| w3_motor_plate | 1 | 45.0 x 30.0 x 4.0 | 4.9 | 3.6 | 2.96 |
| w3_pod | 2 | 27.0 x 8.0 x 14.3 | 2.3 | 1.7 | 2.91 |
| w3_rbc_lower | 1 | 53.0 x 30.0 x 21.0 | 24.5 | 12.7 | 3.45 |
| w3_rbc_upper | 1 | 53.0 x 30.0 x 21.0 | 24.5 | 12.7 | 3.45 |
| w3_rear_arm | 1 | 114.6 x 40.0 x 30.3 | 44.0 | 26.5 | 4.47 |
| w3_uplink_left | 1 | 109.0 x 9.0 x 6.0 | 3.2 | 2.4 | 2.98 |
| w3_uplink_right | 1 | 109.0 x 9.0 x 6.0 | 3.2 | 2.4 | 2.98 |
| w3_uplink_standoff | 2 | 8.0 x 8.0 x 6.8 | 0.3 | 0.3 | 2.82 |
| w3_deck_front | 1 | 150.5 x 109.0 x 11.0 | 85.2 | 48.0 | 5.51 |
| w3_deck_rear | 1 | 143.0 x 109.0 x 6.0 | 82.0 | 44.4 | 5.11 |
| w3_frame_front | 1 | 204.0 x 125.6 x 99.3 | 104.5 | 62.0 | 8.88 |
| w3_frame_rear | 1 | 92.5 x 127.0 x 94.2 | 62.6 | 34.6 | 6.34 |
| w3_skid | 1 | 59.1 x 80.0 x 13.0 | 12.4 | 9.9 | 3.53 |
| w3_tail_hanger_left | 1 | 88.1 x 31.4 x 10.0 | 5.0 | 4.1 | 3.11 |
| w3_tail_hanger_right | 1 | 88.1 x 31.4 x 10.0 | 5.0 | 4.1 | 3.11 |
| w3_tail_main | 1 | 88.0 x 200.5 x 45.5 | 99.6 | 53.1 | 7.96 |
| w3_tail_right | 1 | 86.5 x 68.5 x 39.5 | 38.5 | 20.7 | 4.93 |
| body3_front | 1 | 195.0 x 145.6 x 104.7 | 84.7 | 64.8 | 7.24 |
| body3_rear | 1 | 183.0 x 147.0 x 123.0 | 126.1 | 99.7 | 9.92 |

Left out: `w3_tie_rod` (envelope only; the real tie rods are steel turnbuckles, see B12), `w3_batt_tray` and `w3_esc_tray` (in `w3_parts` but not placed in `w3_assembly`; with the Fusion SE there is no separate ESC).

## Bought parts (priced)

| ref | item | qty | unit | vendor | note |
|---|---|---|---|---|---|
| B01 | Hobbywing QuicRun Fusion SE 1200KV 2-in-1 motor/ESC (HWI30404318) | 1 | 79.99 USD | havocspeed.com | ESC built in; replaces the 2830 motor + 60 A ESC rows |
| B02 | 12 kg servo (priced: Savox B-12KG standard size) (SAV-B-12KG) | 4 | 16.99 USD | smalladdictionsrc.com | design needs SHORT body 40x20x19.3; B-12KG is standard height: placeholder price |
| B03 | Axial 6-Bolt Heavy Duty Gear Set 30T/8T (front + centre diff) (AXI232003) | 2 | 19.99 USD | 997rcraceway.com |  |
| B04 | Axial 6-Bolt Differential Locker (optional crawl mode) (AXI232002) | 1 | 7.99 USD | nankinhobby.com | out of stock |
| B05 | Axial Input Metal Gears 27T/20T/34T (reduction / cross-over) (AXI232033) | 1 | 15.99 USD | nankinhobby.com | regular price; on sale 10.99 |
| B06 | Tire on wheel about 112 x 62, 12 mm hex (priced: Roapex Tracker MT) (ROPR3002-B0) | 3 | 29.99 USD | store.hobbyetc.com | pack qty not stated; dims unverified |
| B07 | LiPo 3S 1300 mAh (75x35x25 envelope) (T1300.3S.30) | 1 | 10.29 USD | hobbyking.com | out of stock |
| B08 | Radio 6+ ch with mixing (priced: FlySky FS-i6X + FS-iA10B) (TE-328-010) | 1 | 69.99 USD | superdroidrobots.com | listing not available |
| B09 | Bearing 8x16x5 (688), 10-pack (688-2RS) | 1 | 9.99 USD | walmart.com | need 2 |
| B10 | GT2 pulley 20T 5 mm bore (priced: Adafruit, 6 mm belt) (ADA1251) | 6 | 7.95 USD | adafruit.com | need 20T x3, 16T x2, 22T x1 for 3 mm belt; out of stock |
| B11 | CVD / universal drive shaft kit (ebay 356156996883) | 1 | 7.98 USD | ebay.com | plus 2.99 ship; confirm it covers 2 joints |
| B12 | M3 stainless turnbuckle pushrod, 2-pack (Secraft SUS M3) | 1 | 3.30 USD | gator-rc.com | listed to 100 mm; design wants about 105 mm |
| B13 | Bearing 5x11x5 (685ZZ), 10-pack (685-ZZ) | 2 | 21.42 GBP | bearingboys.co.uk | design wants 5x11x4 (MR115), about 14; ex VAT |
| B14 | Bearing 4x8x3 (MR84ZZ), 10-pack (3RB-MR84-ZZ/10) | 1 | 8.60 CAD | rcjaz.ca | need 4 |

## Bought parts (not priced)

| ref | item | qty |
|---|---|---|
| U01 | GT2 3 mm closed belts (front x2, rear x1, spare) | 4 |
| U02 | Shafts 5 mm (about 40, 55, 52 mm) and output stubs | 5 |
| U03 | Rear axle 8 mm | 1 |
| U04 | Front axles / tip shafts 4 mm | 4 |
| U05 | Kingpins 4 mm steel about 30 mm | 2 |
| U06 | Steel pins 3 mm (link pivots) | 8 |
| U07 | M2 ball studs / rod ends | 8 |
| U08 | Servo horns aluminium 28 mm (lean) + 12 mm (steer) | 4 |
| U09 | Screws M2, M2.5 and heat-set inserts | 1 |
| U10 | Disc magnets 6 x 2 mm (hood pads) | 4 |
| U11 | LEDs 3 mm (nose light bar) | 3 |
| U12 | Hinge pin 3 mm | 1 |
| U13 | Program card for Fusion SE | 1 |

## Mismatches found while building this

- `WS03_BOM.md` still lists a 2830 motor, a 60 A ESC, module 0.8 spurs and module 1.0 bevel sets. The 2026-11-02 decisions replace these with the Fusion SE (ESC built in) and Axial gear sets; this BOM follows the decisions. `w3_assembly` still places a `b_esc` block.
- `WS03_BOM.md` lists 83 x 24 front tyres; commit c9e2886 made all three tyres 112 x 62 (`front3wd.R = 56`, `W = 62`). Priced as three 112 x 62 wheels.
- The servo pocket is drawn for a short-body 40 x 20 x 19.3 servo. The cheapest 12 kg servo found (Savox B-12KG) is standard height, so B02 is a price placeholder, not a fit.
- 5 x 11 x 4 bearings (about 14) were not found priced; B13 is 685ZZ (5 x 11 x 5). The Axial parts list also uses 5 x 11 x 4.
- The longest priced M3 turnbuckle is 100 mm; the design wants about 105 mm.
- Several listings were out of stock or discontinued (noted per line). Dimensions of every bought part are still unverified, as `WS03_BOM.md` already says.

## Sources

Havoc Speed (Fusion SE), 997 RC Raceway (AXI232003), Nankin Hobby (AXI232002, AXI232033), Small Addictions RC (Savox B-12KG), HobbyEtc (Roapex Tracker wheels), HobbyKing (Turnigy 3S 1300), SuperDroid Robots (FS-i6X), Walmart (688-2RS), Adafruit (GT2 20T pulley), eBay 356156996883 (CVD kit), Gator RC (Secraft M3 turnbuckles), Bearing Boys (685ZZ), RCJaz (3RB-MR84-ZZ/10). Machine-readable rows: `WS03_BOM_COST.csv`.
