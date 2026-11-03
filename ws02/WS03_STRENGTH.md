# WS-03 strength checks

Loads: 3 g landing, front wheel 14.3 N, rear wheel 18.6 N, cornering force 0.6 x load. Beam FE on the real tube graphs (PETG E 1500 MPa), design stress 25 MPa. Factor of safety below 2 is flagged.

| check | factor of safety | verdict |
|---|---|---|
| Front arm (truss FE), 3 g landing + cornering; max 6.6 MPa in L2i-L2o, tip deflection 0.9 mm | 3.8 | ok |
| Rear arm (truss FE), 3 g landing + cornering, wheel 46 mm off the arm; max 4.8 MPa in 3pi-4pi, tip deflection 0.7 mm | 5.2 | ok |
| Tube frame (FE), 6 g equivalent on the pivot pads, feet fixed; max 9.8 MPa in PS2+-FP1+, deflection 1.26 mm | 2.5 | ok |
| Kingpin 4 mm steel, cantilever from the carrier tab, cornering | 5.5 | ok |
| Steer tie rod, 3 mm steel turnbuckle, buckling at servo stall | 7.3 | ok |
| Upper link (6 mm bar), buckling under 16 N | 5.9 | ok |
| Carrier kingpin cantilever tube (brace ignored), 3 g landing | 7.3 | ok |
| Knuckle steering V tubes, axial at servo stall | 5.8 | ok |
| Rear shock hoop cross tube (13 mm, 48 mm cantilever), shock force 43 N at 3 g landing | 2.6 | ok |
| Rear shock hoop leg (13 mm, two legs share), bending over 59 mm plus twist from the 48 mm cross tube | 3.4 | ok |
| Rear shock upper lug plate (bending), 3 g landing | 4.3 | ok |
