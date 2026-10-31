# Print plan

Slicer defaults: 0.4 mm nozzle, 0.2 mm layers, 3 perimeters (1.2 mm walls), no supports, no brim unless a part lifts. Structural parts 30% gyroid, body panels 15%. Times and masses are estimates from part volume (9 mm3/s, x1.35 overhead).

| Part | Qty | Material | Orientation | Extent mm | Infill | Mass g (each) | Est. time h (each) |
|---|---|---|---|---|---|---|---|
| hub_left | 1 | PETG | stub axle up, inboard face on bed, kingpin bore horizontal | 18.0 x 16.0 x 31.8 | 30% | 4.3 | 0.1 |
| hub_right | 1 | PETG | stub axle up, inboard face on bed, kingpin bore horizontal | 18.0 x 16.0 x 31.8 | 30% | 4.3 | 0.1 |
| lean_bar_upper | 1 | PETG | flat on its side, pivot bores vertical | 135.1 x 6.0 x 10.0 | 30% | 7.2 | 0.2 |
| lean_bar_lower | 1 | PETG | flat on its side, pivot bores vertical | 135.1 x 16.0 x 10.0 | 30% | 7.6 | 0.3 |
| upright | 2 | PETG | on its side, pivot bores vertical, kingpin socket near-horizontal | 6.0 x 38.0 x 7.9 | 30% | 2.0 | 0.1 |
| rod_drive | 1 | PETG | flat, bores vertical | 15.4 x 5.4 x 3.5 | 30% | 0.3 | 0.0 |
| link_steer | 2 | PETG | flat, bores vertical | 48.2 x 7.0 x 3.5 | 30% | 1.0 | 0.0 |
| link_bracket_left | 1 | PETG | plate on bed, standoffs up | 42.8 x 16.8 x 11.4 | 30% | 1.7 | 0.1 |
| link_bracket_right | 1 | PETG | plate on bed, standoffs up | 42.8 x 16.8 x 11.4 | 30% | 1.7 | 0.1 |
| swingarm_a | 1 | PETG-CF | outer face on bed, split face up, motor pocket vertical | 82.0 x 63.5 x 36.5 | 30% | 32.1 | 1.0 |
| swingarm_b | 1 | PETG-CF | gearbox end face on bed, split face up, motor pocket vertical | 28.4 x 28.4 x 22.5 | 30% | 9.9 | 0.3 |
| swingarm_gearbox | 1 | PETG-CF | outer face on bed, gear cavity open upward | 87.9 x 54.0 x 15.5 | 30% | 26.7 | 0.9 |
| swingarm_hatch | 1 | PETG-CF | disc down, counterbore up | 39.6 x 39.6 x 13.0 | 30% | 8.6 | 0.3 |
| chassis_tub_left | 1 | PETG | outer wall on bed, split face up | 108.1 x 70.0 x 40.0 | 30% | 40.6 | 1.3 |
| chassis_tub_right | 1 | PETG | outer wall on bed, split face up | 108.1 x 70.0 x 37.0 | 30% | 38.4 | 1.3 |
| front_yoke | 1 | PETG | front face on the bed, beams up | 48.0 x 69.6 x 16.6 | 30% | 20.8 | 0.7 |
| chassis_cradle_left | 1 | PETG | outer wall on bed, split face up | 76.4 x 65.0 x 49.5 | 30% | 25.5 | 0.8 |
| chassis_cradle_right | 1 | PETG | outer wall on bed, split face up | 76.4 x 65.0 x 46.5 | 30% | 22.4 | 0.7 |
| pivot_plate | 1 | PETG | plate on bed, boss up | 54.0 x 54.0 x 7.6 | 30% | 8.3 | 0.3 |
| rx_mount | 1 | PETG | flat | 25.4 x 16.4 x 6.0 | 30% | 1.3 | 0.0 |
| battery_mount | 1 | PETG | flat | 65.4 x 23.4 x 8.0 | 30% | 4.7 | 0.2 |
| rear_hub | 1 | PETG | hex standing on the bed | 13.9 x 12.0 x 12.0 | 30% | 1.5 | 0.0 |
| body_windscreen | 1 | PETG | roof down on the bed, open side up | 31.0 x 80.0 x 8.3 | 15% | 5.0 | 0.2 |
| body_roof | 1 | PETG | roof down on the bed, open side up | 51.0 x 80.0 x 27.5 | 15% | 12.1 | 0.4 |
| body_rear_window | 1 | PETG | roof down on the bed, open side up | 16.0 x 80.0 x 27.5 | 15% | 4.0 | 0.1 |
| body_pods | 1 | PETG | roof down on the bed, open side up | 114.6 x 116.7 x 65.5 | 15% | 34.1 | 1.1 |
| body_side_lower_left | 1 | PETG | outer face on the bed, pins up | 67.0 x 26.0 x 8.3 | 15% | 3.6 | 0.1 |
| body_side_lower_right | 1 | PETG | outer face on the bed, pins up | 67.0 x 26.0 x 8.3 | 15% | 3.6 | 0.1 |
| body_rear_bumper | 1 | PETG | outer face on the bed | 119.2 x 44.0 x 1.6 | 15% | 10.7 | 0.3 |
| body_bumper_cage | 1 | PETG | rear face on the bed, front up | 76.0 x 36.0 x 4.0 | 15% | 7.4 | 0.2 |

Totals: 32 printed pieces, about 354 g of filament and 12 printer-hours.

Materials: PETG-CF for the swingarm halves, gearbox and hatch (heat); PETG elsewhere. ASA or PC are acceptable substitutes for the swingarm; never PLA near the power unit.
