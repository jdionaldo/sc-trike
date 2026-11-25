# Amazon sourcing scan (2026-11-18)

A web search of Amazon listings only. Nothing here was bought, measured or checked for stock or price, and no listing was fitted against the model.
"Candidate" means the listing text matches the spec in `bom.md`. It does not mean the part is proven to fit.

## SCX10 III donor parts (drivetrain)

The model's drivetrain parts are stand-ins (`mock_*`, `w3_*`). No exact Axial part numbers could be confirmed. The numbers I guessed (AXI232000, AXI232001, AXI232008, AXI232018) did not match what I assumed.

| Need | Finding | Candidate listing |
|---|---|---|
| Portal gears, stock 12T/23T | AXI232007 is listed as the Axial 32P 23T/12T set | [Axial portal gear set AXI232007](https://www.amazon.com/clp/B07XZ8SNNK) |
| Ring and pinion (steel) | 8T/24T set, for SCX10 III | [AMK ring and pinion set](https://www.amazon.com/AMK-Pinion-Differential-Crawler-Upgrades/dp/B0CLPBLFFL) |
| Heavy duty 30T/8T gear set | Listed as replacing AXI232003 | [RCAWD 6-bolt gear set](https://www.amazon.com/RCAWD-Heavy-Axial-SCX10-Upgrade/dp/B0CT7ZJPGK) |
| Front portal axle | RCAWD lists it as replacing AXI232022 | [RCAWD front axle assembly](https://www.amazon.com/RCAWD-Assembly-SCX10III-AXI03030-AXI03006B/dp/B0D2RJVL6Q) |
| 12 mm wheel hex | AXI232018 is the 12 mm hex hub and spacer | [RCAWD 12 mm hex hub](https://www.amazon.com/RCAWD-Alloy-Spacer-AXI232018-Upgrades/dp/B0CVZVM5TV) |
| Steering knuckles | brass knuckles for SCX10 III | [Hobbypark brass knuckles](https://us.amazon.com/Hobbypark-Steering-Knuckles-Counterweight-Upgrades/dp/B08V4VR2CC) |
| Belt pulley kit | only SCX10 / SCX10 II kits found, none for the III | [belt drive system 3.17 mm](https://www.amazon.com/Drive-Gears-System-Crawler-Axial/dp/B0B31G9RWZ) |

Open: the belts, pulleys and diff carriers in the model are custom. No listing was confirmed to match them.

## Generic and other parts

| Need | Candidate listing | Check before buying |
|---|---|---|
| M3 x 5.7 brass heat-set inserts | [MroMax 140 pcs](https://www.amazon.com/Threaded-Inserts-knurled-Printing-Components/dp/B0DDWS7BTS) | the model pocket is D4.2 x 5 deep; OD 4.6 inserts fit |
| M3 ball-joint rod ends | [QUE-T 10 pcs](https://www.amazon.com/clp/B08J4479YG) | the model has a D6 ball and a 16 mm stud, a separate stud is needed |
| 6 x 3 mm magnets | [rhinocats 30 pcs](https://www.amazon.com/rhinocats-n52-Small-Magnets-6x3mm/dp/B0HNW8KJRX) | some listings are N42 or 6 x 2.6 mm |
| 1.9 in wheels, 12 mm hex | [Rchobbytop beadlock set](https://www.amazon.com/Rchobbytop-Aluminum-Beadlock-Crawler-Wrangler/dp/B09LXX9C52) | its tyre spec (2.2 in, 140 mm) conflicts with the 1.9 in wheel |
| Motor and ESC, Hobbywing Fusion SE 1800KV | the Amazon listings are mostly clones; the genuine one is at [chinahobbyline](https://www.amazon.com/hobbywing-fusion-se-1800kv-2-1/s?k=hobbywing+fusion+se+1800kv+2+in+1) | clones are not Hobbywing |
| Steering servo (low profile, chosen) | [AGFRC B44BLS V2 15.5 kg](https://www.amazon.com/AGFRC-Profile-Servo-High-Speed/dp/B07L83M8SM), listed 40.8 x 20.2 x 26.5 mm, 48 g; alternates [INJORA INJS014 14 kg](https://www.amazon.com/INJORA-INJS014-Metal-Digital-Profile/dp/B0HH65ZM2R) (40 x 20 x 28.8) and [INJORA INJS022 22 kg](https://www.amazon.com/clp/B0DB8KZXBS) (size not checked) | model stand-in resized to 40.8 x 20.2 x 26.5 mm and the servos, horns and tie rod horn ends moved 6 mm outboard (STEER_OUT) to clear the front diff housing; no overlaps in the collision gate |
| Standard 25 kg servos (e.g. [ZOSKAY](https://www.amazon.com/ZOSKAY-Waterproof-Standard-Digital-Control/dp/B07GLMDJQ7)) | listed 40 x 20 x 40.5 mm | will not fit |

## Problems found

1. **Servo size:** the model's servo envelope (19.3 x 41.5 x 22.7 mm) does not match the common 25 kg metal-gear servo (40 x 20 x 40.5 mm). Either the model needs a bigger pocket, or a low-profile servo must be sourced.
2. **Rear tyre:** about 140 mm OD is the Rchobbytop 2.2 in set, but its listing mixes 1.9 in wheels with 2.2 in tyre specs.
3. **Drivetrain:** every donor part is unconfirmed until the real axial part numbers are checked against Axial's parts diagram.
