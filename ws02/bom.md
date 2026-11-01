# Bill of materials (WS-02 spec). All dimensions: verify with calipers on arrival.

## Locked from the WS-02 notes
| Item | Spec | CAD dependency |
|---|---|---|
| Motor | 2830 outrunner, about 1400 KV, 3.17 mm shaft, 28 x 30 mm, 4x M2.5 on 16 mm PCD | `pu_*`, motor flange, cradle pocket |
| ESC | 60 A, 2S-3S, BEC 6 V / 3 A or more, 46 x 38 x 33 mm | `esc_*` envelope (above the battery) |
| Servo | Short-body, 12 kg.cm or more, 40 x 20 x 19.3 mm, ear span 49 mm (drawing) | `servo_*`, tub ear |
| Radio | 6 channels or more, two programmable mixes | none |
| Pinion and gear | 15T 3.17 mm bore pinion, 0.8 module; 60T spur | `gear_*` |
| Belt | GT2, 15T and 30T pulleys, 44 mm centres, 6 mm wide | `belt_*` |
| Battery | 2S-3S LiPo, about 62 x 20 x 14 mm (placeholder) | `lipo_*` |

## Bought parts with CAD dependencies
| Name in CAD | Spec | Depends on |
|---|---|---|
| FRONT_TIRE_WHEEL x2 | about 83 mm OD x 24 mm wide, 12 mm hex or 3 mm axle | `front_tire_*` |
| REAR_TIRE_WHEEL | about 85 mm OD x 50 mm wide, 12 mm hex | `rear_tire_*` |
| Rear axle | 8 mm steel rod, about 90 mm, plus one 8 x 16 x 5 bearing | `rear_axle_dia`, `rear_bearing_*` |
| SPRING_SHOCK | 1/10-class micro coil-over, about 50 mm eye to eye, 10 mm stroke | `shock_*` |
| Steel rods | 3 mm: lean pivots, bar pins, kingpins, front stub axles, intermediate shaft | `pin_dia` |
| Ball ends | M2 ball-link rod ends (5) | rod eyes |
| Fasteners | M2 screws (assorted), M2 heat-set inserts (about 40), M2.5 x 4 for the motor | `m2_*`, `m25_*` |

## Printed
See `print_plan.md`. Body: `mono_left`, `mono_right` (shell fused with the tub and cradle), `canopy_lid`, `swingarm_arm`, `swingarm_cover`, `motor_flange`, front end parts.
