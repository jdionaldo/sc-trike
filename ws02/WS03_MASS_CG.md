# WS-03 mass, CG and roll-over

Printed mass = 1.2 mm walls plus 25% infill (15% for the body); bought masses are assumptions (45 g servos, 62 g motor, 125 g 3S pack).

| item | value |
|---|---|
| printed_g | 842 |
| bought_g | 1367 |
| misc_g | 85.0 |
| total_g | 2294 |
| cg_mm | [-160.4, 1.1, 10.8] |
| front_weight_fraction | 0.644 |
| cg_height_above_ground_mm | 52.3 |
| static_roll_angle_deg | 68.8 |
| rollover_speed_1m_radius_mps | 5.02 |

Heaviest items:

- b_motor: 201 g
- b_battery: 125 g
- mock_rear_tire_ring: 95 g
- mock_tire_1: 95 g
- mock_tire_-1: 95 g
- body3_mid: 71 g
- body3_front: 66 g
- w3_frame_rear: 61 g
- w3_frame_front: 58 g
- body3_rear: 56 g

## Balance ladder (cumulative)

| step | front % | gain (points) | total g | CG x, y, z (mm) | CG height above ground |
|---|---|---|---|---|---|
| 0 merged baseline (120 g pack, small masses at the centroid) | 62.95 |  | 2262 | -166.7, 1.2, 12.7 | 54.2 |
| 1 battery: 125 g pack, x unchanged (forward limit is only 1.5 mm) | 63.02 | +0.06 | 2267 | -166.4, 1.1, 12.7 | 54.2 |
| 2 small masses placed from an inventory (receiver already at x -44) | 63.19 | +0.17 | 2267 | -165.6, 1.1, 12.6 | 54.1 |
| 3 sideways CG: no move needed (|y| < 2 mm) | 63.19 | +0.00 | 2267 | -165.6, 1.1, 12.6 | 54.1 |
| 4a wing and tail infill 25 % to 8 % | 63.75 | +0.55 | 2247 | -163.1, 1.1, 11.7 | 53.2 |
| 5 nose ballast plate 42 g tungsten + 8 g carrier (FINAL BUILD) | 64.36 | +0.61 | 2294 | -160.4, 1.1, 10.8 | 52.3 |
| option on top: lighter rear tyre insert, -15 g (estimate, not in the build; lets the ballast shrink to 0) | 64.78 | +0.42 | 2279 | -158.5, 1.1, 11.1 | 52.6 |
