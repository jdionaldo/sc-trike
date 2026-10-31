# Bill of materials

Every dimension below is "verify with calipers on arrival". No Amazon ASIN was confirmed during research, so every Amazon item is UNVERIFIED and gives the exact spec to search for; no listing is invented. Quantities for fasteners and pins are estimates from the CAD and should be counted against `out/commands/` before ordering.

## Locked: power unit (VERIFIED against Hobbywing manual HW-SMC337DUL02, 2024-11-08)
Source: https://www.hobbywing.com/en/products/quicrunfusionmini16 and the Manuals PDF linked there.

| Item | Value | CAD dependency |
|---|---|---|
| Model | QuicRun Fusion Mini16 3000KV 2-in-1, PN 30120403 (Amazon availability UNVERIFIED; search "Hobbywing 30120403") | name `POWER_UNIT` |
| Size / weight | 24 mm dia x 42 mm, 72 g with wires | swingarm pocket, mass |
| Shaft | 2.3 mm dia, 13.5 mm exposed | pinion bore |
| Mount | 4x M2.5 on 16 mm PCD, 2x M3 on 17 mm, holes 4 mm deep | not used: the motor is held by its pocket |
| Input | 2-3S LiPo, EC2, 18AWG x 150 mm | lead length and slack |
| Current | 30 A continuous / 80 A peak | ratio check (about 1.9 A estimated) |
| BEC | 6 V / 7.4 V selectable, 4 A switch mode, on the red throttle wire | no separate BEC |
| Programming | Yellow signal wire plus Hobbywing LED or LCD G2/Pro program box. No button programming of parameters (SET only calibrates throttle and pairs the motor). | lead routing |
| Thermal | External system temperature must not exceed 90 C; ESC overheat protection defaults to 105 C (option 125 C); IP66 | README thermal section |
| Gear guidance | None for 1/18. Product page: 1/14-1/10 lightweight models, <= 1.8 kg, ratio >= 60. | README risk note |

Drivetrain: 12/60 x 15/37 = 12.33:1 at 32 pitch (module 0.794), 62 mm rear tire, 4.97 m/s on 2S.

## Bought parts (UNVERIFIED listings; search specs)
| Name in CAD | Search for | Dimension the CAD depends on |
|---|---|---|
| REAR_TIRE_WHEEL | Wide rear tire on a 12 mm hex wheel, about 62 mm OD x 38-42 mm wide | rear_tire_od, rear_tire_w, rear_hex |
| FRONT_TIRE_WHEEL x2 | Slim front tire on a 12 mm hex or 3 mm bore wheel, about 52 mm OD x 14-18 mm wide | front_tire_od, front_tire_w |
| SERVO_9G | 9 g metal-gear servo, **at least 3.0 kg.cm stall at 6 V** (a 2.2 kg.cm MG90S would leave about 10 % margin; 3.0 gives 30 %; 3.5 is safer), 22.8 x 12.2 x 28.5 mm, ear span 32.5 mm | servo_l/w/h, torque margin |
| SERVO horn | Metal or nylon single-arm horn with a 15 mm hole radius | servo_horn_r |
| RECEIVER and transmitter | 2.4 GHz 2-channel or better set | rx_l/w/h |
| LIPO_2S | 2S 7.4 V LiPo about 450 mAh, EC2 connector or EC2 adapter, no larger than 62 x 20 x 14 mm | lipo_l/w/h |
| Program box | Hobbywing LED program box (not modelled) | none |
| GEARS | Mod 0.794 (32 pitch) steel: 12T pinion with 2.3 mm bore, 60T gear, 15T pinion, 37T gear, 3 mm bores | gear_* in params |
| SPRING_SHOCK | 1/18 aluminium micro coil-over, yellow spring, about 34 mm eye to eye ride length, at least 7 mm stroke, spring rate about 1.15 N/mm | shock_len_ride, shock_stroke |
| HEAT_SHIM | Copper or aluminium strip 11 mm wide x 0.8 mm | sw_shim_w |
| BALL_ENDS | M2 ball-link rod ends (5 needed: 2 per steering link, 1 for the drive rod) | rod eyes |
| DOWEL_2x18 | 2 mm x 18 mm steel dowel pins, 2 | body cage keys |
| STEEL RODS | 3 mm steel rod: 2 x 24 mm (lean pivots), 4 x 14 mm (bar to upright pins), 2 x 26 mm (kingpins), 2 x 30 mm (front stub axles), 1 x about 72 mm (rear axle), 1 x about 13 mm (intermediate shaft) | pin_dia, kingpin_len |
| BEARINGS | MR63ZZ (3 x 6 x 2.5), 1 minimum | bearing_od |
| FASTENERS | M2 screws (8-55 mm, assorted, about 60), M2 heat-set inserts (about 40), self-tapping M2 for the servo | m2_* sizes |
| LED_INSERTS | 3 mm LEDs for the Y-shaped nose pockets (optional) | cage pockets |

## Printed (see print_plan.md)
See `print_plan.md` for material, orientation, infill, mass and time per part.
