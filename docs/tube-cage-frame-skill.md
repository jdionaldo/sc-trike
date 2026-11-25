---
name: tube-cage-frame
description: Build a printable tube frame (roll cage, exo cage, space frame, truss arm) in code CAD (CadQuery) the way the Project_Fugu cage is built - chamfered square tubes on a node graph, every joint one convex faceted hull, feet slotted into deck pockets, bosses that reach the body skin. Use when asked for a roll cage, tube chassis, exposed "Yeti" style frame, space frame or truss, when a tube frame has messy joints (mitre spikes, gaps, sliver faces, overlapping tubes), or when asked to build a cage "like the trike".
---

# Tube cage frame

The method behind the Project_Fugu cage (`~/GitHub/sc-trike/Project_Fugu/parts/cage.py`), which John called perfect on 2026-11-22. The reusable core is `tubeframe.py` next to this file: copy it into the new project (for a SOMA project, `parts/tubeframe.py`) and build the cage with its `Frame` class. Do not rewrite the joint maths.

## 1. The frame is a graph, not a pile of solids

- Define **named nodes** (points) first, then members as centre lines between nodes. Build no solid until every member is known.
- Two members that should meet must use the **same point** (nodes snap to 0.1 mm). Compute a shared node once and reuse it; never let two tubes "almost" meet.
- Tubes never overlap. A tube that ends on the side of another splits it at that point. Two tubes that cross mid-span become four tubes at one node. `Frame` does both; a design should still aim for zero mid-span crossings and report the count.
- Work on the +x half and mirror the node list, so the frame is exactly symmetric.

## 2. Tube section

- Chamfered square (an octagon), not round: side = 0.88 x the nominal diameter, 45 degree chamfer of 0.18 x the side on each long edge. One flat stays horizontal; on vertical members the flats face +-x. Flat faces print without support and look like fabricated tube.
- One size for the structural frame (Fugu: 10 mm nominal at 1/8 scale) and one smaller size for visible cabin tubes (7 mm). Do not mix more sizes.

## 3. Joints: one convex hull per node

- Each tube is the convex hull of its two end sections.
- Each node where tubes meet at an angle is the convex hull of the incident tubes' sections, taken at the node and at a set-back `e_i` along each tube.
- `e_i` is solved so every tube's end section is exactly a face of the node hull: `e_i >= e_j cos(theta_ij) + R_j sin(theta_ij)` for every other tube j, R = corner radius of the section. Tube and node then share that face, so nothing sticks out: no mitre spike, cope gap or cube corner.
- A set-back is capped at 45 % of the tube's length. Two nodes joined by a tube with under 1 mm of free length are merged into one hull, otherwise the stub between two hulls leaves a re-entrant slot.
- Hull triangles on one plane are merged into one planar face. This is what removes sliver faces (Fugu: tiny faces 266 -> 130) and keeps FEM meshing and STEP export clean.
- Free ends and straight runs get flat ends, no node.

## 4. Fusing

- Fuse one member at a time and check each step: result valid, volume did not shrink, no extra solid. On failure retry with the member nudged by 0.01 to 0.04 mm; if that fails too, raise with the member's name. Never accept a silent failed fuse.
- Cut holes (screws, bores, slots) only after all fusing.
- End with: one valid solid. Anything else means a member is not connected.

## 5. Laying out the cage on a vehicle

- **Follow the body.** The upper side rails copy the body's belt line: sample the skin underside along y, simplify with Ramer-Douglas-Peucker (0.8 mm) so the tubes keep the body's kinks, and run the tube a fixed clearance under it (Fugu: 14 mm closed body; top flush with the rim for an open cockpit).
- **Triangulate every bay**: door bars as a V to a node on the lower rail directly above a foot, roof X, windshield V, diagonals in the rear quarter. No open rectangles.
- **Feet stand on hard points**: straight vertical posts down to the deck at places that are clear of the drivetrain, inside the deck edge. Put truss nodes directly above feet.
- **Load mounts are part of the frame**: a shock top mount is a clevis carried by tubes, with ties that land on the clevis web above the pin axis, not on the axis. Keep a straight tool corridor along every pin and bolt axis (Fugu: 17 mm) and 2 mm all round bolt heads and nuts.
- **Derive, do not type**: positions come from the body, the deck and the mounts through named constants and `param()`, so the cage follows when those move.

## 6. Feet and fastening

- Square foot ends drop into pockets in the deck: 3 mm deep, 0.2 mm clearance all round. Where the deck is thin, a printed socket collar or a bracket keyed into the side wall does the same job (wall 2.4 mm, collar 4 to 10 mm high).
- The screw (M3) comes from below through the deck into the foot, checked clear of everything under the deck. The pocket locates, the screw only clamps.
- The leg node sits high enough above the deck that the socket collar stays under it.

## 7. Bosses to the body

- A boss is a short stub from a pillar node toward the skin with a pilot hole. Its length is measured, not guessed: cast along the stub axis to the first skin and stop 0.8 mm short (cap the reach, Fugu: 30 mm).

## 8. Checks before calling it done

1. One valid solid; zero mid-span crossings reported.
2. Count faces under 0.05 mm2: should be near zero in the frame itself.
3. Collision check against every other part: 0 overlaps, including suspension travel and steering lock.
4. Tool access: a cylinder along each pin and screw axis is free.
5. FEM on the load mounts (shock clevis, link lugs) with the real loads; target safety 2.
6. Look at renders of every joint cluster, especially where four or more tubes meet and at the tail.

## 9. Use of `tubeframe.py`

```python
from parts.tubeframe import Frame
f = Frame()
f.tube(a, b, 10)          # centre line between two nodes, nominal diameter
f.add(solid)              # feet, bosses, gusset plates, clevis ears
f.cut(solid)              # holes, cut after fusing
cage = f.build()          # one valid solid, or an error naming the member
```

Run `python tubeframe.py` for the self-test. It needs cadquery, numpy and scipy.

Known limits: the hull joint assumes straight members; a curved tube must be a chain of short straight ones. Very acute joints (under about 20 degrees) make long nodes: move a node or drop a member.
