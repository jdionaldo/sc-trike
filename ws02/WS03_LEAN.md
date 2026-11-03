# WS-03 lean drive: one servo, V rocker, two rods

- Servo: Injora INJS15 on the centreline, shaft along x pointing aft, rocker axis x -88.5, z 30.52.
- Rocker (printed, 4 mm): tips at radius 17.87 mm, V half angle 51.2 deg above horizontal at rest; tips at y +-11.2, z 44.4.
- Rods: two M2 ball-link turnbuckles, 61.06 mm centre to centre, from the rocker tips to the arm lugs (x -74..-89, |y| 61.5).
- Fit over lean +-20 deg: both rod lengths agree to 0.5 mm; servo angle +-22.3 deg for +-20 deg of lean (about 1.12 deg per degree).
- Tower (printed): 2.5 mm plate with the servo window and a portal opening for the battery, two legs screwed to the base plate (4 x M2), ears screwed from the front.
- Why the motor moved aft: the can (x -129..-71, z 23..59) filled the space the rocker needs; a rocker ahead of the motor (x >= -69) gives about 1.2 mm of rod mismatch and barely drives the arms.
- Steering: a single central steering servo was ruled out (best wheel steer error about 7 deg with lean-coupled steer, about 19.5 deg over the whole lean x steer grid) because each tie rod's inner pivot must sit on the arm pivot axis (x -100, z -26), where the front diff is. The two steer servos at x -100 stay: 3 servos in total.
- Torque and strength are not yet computed (see the report).
