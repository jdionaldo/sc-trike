# WS-03 mass, CG and roll-over

Printed mass = 1.2 mm walls plus 25% infill (15% for the body); bought masses are assumptions (45 g servos, 62 g motor, 125 g 3S pack).

| item | value |
|---|---|
| printed_g | 842 |
| bought_g | 1367 |
| misc_g | 85.0 |
| total_g | 2294 |
| cg_mm | [-161.2, 1.2, 10.5] |
| front_weight_fraction | 0.642 |
| cg_height_above_ground_mm | 52.0 |
| static_roll_angle_deg | 68.9 |
| rollover_speed_1m_radius_mps | 5.04 |

Heaviest items:

- b_motor: 201 g
- b_battery: 125 g
- mock_rear_tire_ring: 95 g
- mock_tire_1: 95 g
- mock_tire_-1: 95 g
- body3_mid: 71 g
- w3_frame_rear: 63 g
- w3_rear_arm: 62 g
- w3_frame_front: 57 g
- body3_rear: 56 g

## Balance ladder (cumulative)

| step | front % | gain (points) | total g | CG x, y, z (mm) | CG height above ground |
|---|---|---|---|---|---|
| 0 merged baseline (120 g pack, small masses at the centroid) | 62.69 |  | 2258 | -167.9, 1.3, 12.5 | 54.0 |
| 1 battery: 125 g pack, x unchanged (forward limit is only 1.5 mm) | 62.75 | +0.07 | 2263 | -167.6, 1.3, 12.5 | 54.0 |
| 2 small masses placed from an inventory (receiver already at x -44) | 62.94 | +0.18 | 2263 | -166.8, 1.2, 12.4 | 53.9 |
| 3 sideways CG: no move needed (|y| < 2 mm) | 62.94 | +0.00 | 2263 | -166.8, 1.2, 12.4 | 53.9 |
| 4a wing and tail infill 25 % to 8 % | 63.49 | +0.55 | 2243 | -164.3, 1.3, 11.5 | 53.0 |
| 5 nose ballast plate 42 g tungsten + 8 g carrier (FINAL BUILD) | 64.17 | +0.68 | 2294 | -161.2, 1.2, 10.5 | 52.0 |
| option on top: lighter rear tyre insert, -15 g (estimate, not in the build; could replace about 20 g of ballast) | 64.59 | +0.42 | 2279 | -159.3, 1.2, 10.8 | 52.3 |
