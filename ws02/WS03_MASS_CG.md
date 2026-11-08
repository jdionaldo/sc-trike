# WS-03 mass, CG and roll-over

Printed mass = 1.2 mm walls plus 25% infill (15% for the body); bought masses are assumptions (45 g servos, 62 g motor, 125 g 3S pack).

| item | value |
|---|---|
| printed_g | 848 |
| bought_g | 1367 |
| misc_g | 85.0 |
| total_g | 2300 |
| cg_mm | [-161.1, 1.5, 10.6] |
| front_weight_fraction | 0.642 |
| cg_height_above_ground_mm | 52.1 |
| static_roll_angle_deg | 68.8 |
| rollover_speed_1m_radius_mps | 5.04 |

Heaviest items:

- b_motor: 201 g
- b_battery: 125 g
- mock_rear_tire_ring: 95 g
- mock_tire_1: 95 g
- mock_tire_-1: 95 g
- body3_mid: 71 g
- w3_rear_arm: 62 g
- w3_frame_rear: 61 g
- body3_front: 59 g
- w3_frame_front: 57 g

## Balance ladder (cumulative)

| step | front % | gain (points) | total g | CG x, y, z (mm) | CG height above ground |
|---|---|---|---|---|---|
| 0 merged baseline (120 g pack, small masses at the centroid) | 62.72 |  | 2263 | -167.8, 1.6, 12.6 | 54.1 |
| 1 battery: 125 g pack, x unchanged (forward limit is only 1.5 mm) | 62.79 | +0.07 | 2268 | -167.5, 1.5, 12.5 | 54.0 |
| 2 small masses placed from an inventory (receiver already at x -44) | 62.97 | +0.18 | 2268 | -166.6, 1.5, 12.5 | 54.0 |
| 3 sideways CG: no move needed (|y| < 2 mm) | 62.97 | +0.00 | 2268 | -166.6, 1.5, 12.5 | 54.0 |
| 4a wing and tail infill 25 % to 8 % | 63.52 | +0.55 | 2248 | -164.2, 1.5, 11.6 | 53.1 |
| 5 nose ballast plate 42 g tungsten + 8 g carrier (FINAL BUILD) | 64.20 | +0.68 | 2300 | -161.1, 1.5, 10.6 | 52.1 |
| option on top: lighter rear tyre insert, -15 g (estimate, not in the build; could replace about 20 g of ballast) | 64.62 | +0.42 | 2285 | -159.2, 1.5, 10.8 | 52.3 |
