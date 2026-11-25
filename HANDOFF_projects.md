# Handoff: project threads -> "Reverse Trike" session

Written 2026-11-22 from `git log` and the files in this folder. Nothing was built, edited or committed while writing it. Section 7 collects the final status reports of the four project threads as they come in.

## 0. Instructions for the Reverse Trike session

**Read first, in this order**
1. This file, all of it.
2. `AGENTS.md` and the skills it lists as "Always follow" (`.soma/skills/design-workflow.md`, `cadquery.md`, `parametric.md`, `standard-parts.md`, `fem.md`, `drawings.md`).
3. `NOTES.md` from "## Rear wheel drive only, passive lean beam (November 21)" (line ~598) to the end.
4. `BOM_COST.md` (Totals and "Mismatches found").

**Branch**: work on `shell/defect-sweep` (already checked out). Do not create branches or check out old commits (`AGENTS.md`).

**Merging the printability fixes** (no longer a fast-forward: `06452ea` is on `shell/defect-sweep` now)
1. `git status`: the only unfinished model edit left is the cage thread's `parts/cage.py` (section 7). Run `soma build`; if it says "Build ok" and `python tools/collide.py` reports 0 overlaps, commit it (`git add -A && git commit -m "..."`). If not, fix it first; do not discard it.
2. `git branch` to confirm the names, then `git merge printability-merge` (code fixes `657d457` + `c45948b`). `printability-merged-test` is the same plus `b350de9`, which is already here, and a rebuild; merging it instead gives the same code.
3. Expected conflicts: `output/model.step`, `exports/`, `kit/` build outputs (take either side, the rebuild overwrites them) and possibly `NOTES.md` (keep both). The knuckle tie-rod pocket: keep `06452ea`'s fan version; the merge branch deliberately left out the knuckle half of `7919554`.
4. `soma build`, `python tools/collide.py`, then FEM (below), then re-measure the knuckle walls: `soma analyze thickness --parts "knuckle 1,knuckle -1"` (target >= 1.2 mm). Commit the merge only when all pass.

**Open items in priority order**
1. Land the in-progress thread work (section 5 items 1-3 and section 7), then the merge above.
2. Kit regen: `pip install trimesh shapely`, then regenerate the kit (`kit/` scripts); make sure `OPEN_COCKPIT` drops the Canopy (SH2) and CG3. Refresh volumes and totals in `BOM_COST.md`.
3. Audit loads (section 2): front shock motion ratio ~0.21 and the 1.7x shock load (mount geometry), bearings for the lean beam pivot and shock pins, a cornering tilt load case for the lean beam, stops and cage bridge.
4. Bring upper link (SF 1.53) and front arm (~1.5) to SF 2; analyse pivot blocks, motor plate, cage bridge and cabin tubes.
5. Section 5 item 6 (smaller leftovers) and the BOM mismatches in section 3.

**Rules**
- Local only, in this folder on John's Mac. No cloud clones, no push (there is no remote).
- Build in SOMA: `soma build` after every change and read the result; keep the model buildable.
- Before every commit: `soma build` "Build ok", `python tools/collide.py` 0 overlaps, and `soma analyze fem analyses/<part>.py` for every part whose geometry changed (front_arm, rear_arm, tie_rod, uplink, lean_beam, cage). Put the result in the commit message the way earlier commits do ("build ok, 0 overlaps, ... FEM x MPa safety y").
- Record what changed and why in `NOTES.md`.
- Do not edit `inputs/`, `parameters.json`, `output/model.step` by hand; no `reset`, `rebase`, `amend` or force.

## 1. Branches and commits

Current checkout: **`shell/defect-sweep`** at `b350de9`.

### On `shell/defect-sweep` (newest last, all "build ok, 0 overlaps")
| Commit | Change |
|---|---|
| `6d8e7a6` | Rear wheel drive only: front belts, pulleys, front and centre diffs removed; front arms on one fixed 5 mm axle in two deck blocks; motor + one spur stage on the rear shaft; passive lean balance beam under a cage bridge carries both shock tops. 113 -> 97 parts |
| `588c9ea` | Lean beam: lower shock clevis on the arm's U1 node, beam widened, stops at 3.2 deg. Arm FEM safety 1.61, beam 1.89 |
| `c48a64d` | Lean beam centring springs (two compression springs under the bridge) |
| `130b3c3` | Cage feet seated in the tub: deck pockets, rear brackets keyed into the side walls, front collars; M3 countersunk from below; cage joints as convex hull nodes (tiny faces 266 -> 130), tail crossings share nodes |
| `7db4bf3` | Tie rod knuckle eye 5.0 x 7.0, bar r 4.3, tapered collar; tie rod FEM 9.8 MPa, **SF 2.05** |
| `5364ebc` | Yeti exposed cage, open cockpit (`OPEN_COCKPIT = True`): canopy off, 7 mm belt rim, `CABIN_BEAM` 7 mm cabin tubes (roof X, windshield V, door diagonals); rear light contact dropped. 97 parts |
| `b350de9` | Upper link `TONGUE` back to 12 mm (10 mm from `008fbee` gave SF 0.55); uplink FEM 13.1 MPa, **SF 1.53** |
| `06452ea` | Knuckle tie-rod pocket as a +-11 deg fan with 1.6 mm boss and sleeve and M3 stud hole; front arm 3 mm crotch radius (`CROTCH_R`). Build ok, 97 parts, 0 overlaps. **Unfinished**: tie rod still hits the knuckle (17.9 / 17.8 / 24.3 mm3 at -14 / +10 / +20 mm); FEM not re-run |

(The uncommitted `model.py` and `parts/frontarm.py` edits described below were committed as `06452ea`.)

### Printability branches (not merged into `shell/defect-sweep` or `main`)
- **`printability-fixes`**: branched at `5364ebc`, adds
  - `657d457` rear bearing carrier lip 0.3 -> 1.5 mm, pivot block insert pockets 1.5 mm from faces, rear arm chords flush; kit registry brought up to the model (lean beam, pivot blocks added, removed designs dropped). Rear arm FEM SF 2.68.
  - `7919554` knuckle tie-rod pocket boss and sleeve (skins 0.01 -> 1.5 mm), carrier 0.3 mm ring sliver trimmed, kit: CG3 dropped, SH2 canopy optional.
- **`printability-merge`**: `657d457` + `c45948b` (the non-knuckle half of `7919554`).
- **`printability-merged-test`**: `b350de9` + merge of `printability-merge` (`4e0a528`) + rebuild `891efd9` ("build ok, 0 overlaps"). This is the candidate to fast-forward `shell/defect-sweep` to. The knuckle-pocket half of `7919554` is deliberately left out; it is being redone in the working tree (see open items).
- `kit/printable-release-pack` and `main` (`131af50`) are older lines; `main` does not contain any of the above.

### Uncommitted in the working tree (other threads, mid-edit: do not discard)
- `model.py`: knuckle tie-rod pocket as an 11 deg fan with boss and sleeve (tie rod tilt at +20 / -14 mm travel).
- `parts/cage.py`, `parts/frontarm.py`: cage and front arm edits in progress (collars / tail / arm edge radius).
- `exports/Front_shell.step`, `output/model.step`, `.soma/project.json`: build outputs.
- Untracked: `BOM_COST.md`, `BOM_COST.csv`, `analyses/cage.py`, `out/`, and old 1/18 files (`README.md`, `bom.md`, `print_plan.md`, `params.py`, ...) that do not describe this model.

## 2. Findings (audit and FEM)
Load and strength audit of the current design:
- Front shock load is about **1.7x** the earlier figure: the shock lies almost level and pushes along the arm (268 N for a 65 N bump, was 168 N).
- Front shock motion ratio about **0.21** (0.21-0.24 mm stroke per mm of wheel travel) through the lean beam. Very low: the spring/damper sees large force, little stroke.
- **Beam pivot (M4) and shock pin bearings are overloaded** at these forces; no bearings are modelled yet (see BOM mismatches).
- **Cornering tilt load is not covered** by any analysis: FEM cases are bump and side load only; the lean beam, stops and cage bridge have no cornering/tilt case.
- Upper link SF **1.53** (`analyses/uplink.py`), front arm SF **about 1.5** (1.61 at `588c9ea`, `analyses/front_arm.py`), lean beam 1.89, tie rod 2.05, rear arm 2.68. Target is 2.
- Not analysed: pivot blocks, motor plate, cage bridge, new cabin tubes (`analyses/cage.py` is new and uncommitted).

## 3. Parts list (`BOM_COST.md`, `BOM_COST.csv`)
Snapshot at build `597ca5e8` (HEAD `130b3c3`, 99 parts). Estimates, nothing ordered.
- Printed, priced (36 of 39 instances): USD 145.96 + 30 % fee 43.79 + 5.00 handling = **USD 194.75**. Front shell, Canopy and Cage unpriced (too big for the supplier), about USD 43.89 + 30 % extrapolated.
- Open cockpit drops Canopy and CG3: printed priced subtotal USD 143.08, mass 1349 g plus new cabin tubes (re-measure).
- Bought, priced: **USD 468.33 + CAD 8.32** (16 lines); 15 lines unpriced.
- Print mass: 1452 g PETG (before open cockpit).
- Misfits / mismatches:
  - `README.md`, `bom.md`, `print_plan.md` describe an older 1/18 design.
  - `kit/bom.md` and `kit/registry.py` on this branch still list the removed front/centre diffs, lean mount, pods, front pulleys and the Canopy (fixed on `printability-fixes` by `657d457`/`7919554`).
  - Motor: kit says Fusion SE 1800KV, reference list had 1200KV (same body).
  - Battery tray 35 x 76.6 x 30 mm: 2S 2200 hardcase (93 mm) does not fit, 3S 1300 does. Receiver envelope smaller than an FS-iA6B.
  - No bearings modelled; bearing sizes and counts are assumptions. Decks and carriers are still hull stand-ins.
  - Rear tyre 140 mm OD in the model vs 138 mm max in NOTES (Nov 11).
  - NOTES hardware table (cage feet screwed from the top) is out of date; M3 from below is current.

## 4. Renders
`renders/yeti_iso.png`, `yeti_side.png`, `yeti_front.png`, `yeti_top.png`, and `renders/yeti_old_canopy_*.png` for comparison (VTK from `output/model.step`, the app was not running).

## 5. Open items
1. **Tie rod pocket for ~10 deg tilt plus front arm edge radius** (lean-arm thread, in progress): uncommitted fan pocket in `model.py`, arm edits in `parts/frontarm.py`. Then re-run `analyses/tie_rod.py` and `analyses/front_arm.py`.
2. **Shell panel lines follow the cage lower rail and the A-pillar kink** (not started; see section 7: belt edge follows the tube from the front hoop top to cowl corner K (77.7, -193.9, 133.9), then kinks down at the A-pillar foot; break the cage's dependence on `cabin['rim_z']` in `model.py` first).
3. **Cage**: front socket collars (only 1.4 mm high), tail node crevice at y 165, tail shock clevis vs M6 bolt head clearance (nodes reach x 10.9, head starts at 12), cage FEM incl. the cabin tubes (`analyses/cage.py`) (in progress).
4. **Kit regen**: `kit/` scripts need `trimesh` and `shapely`, which are not installed (`pip install trimesh shapely`). Run after merging `printability-merged-test`, since that branch carries the registry fixes.
5. From the audit: front shock motion ratio / mount geometry, bearings for the beam pivot and shock pins, a cornering tilt load case, and lifting upper link and front arm to SF 2.
6. Smaller: tail light wiring route along the cage (rear contact gone), front arms still carry the old belt pocket and pod seat, shell still has front belt relief cuts, `parts/lean_linkage.py` unused, spur/pinion tooth counts not chosen.

## 6. Suggested order
1. Let the in-progress edits land (items 1-3) and commit them on `shell/defect-sweep`.
2. Merge `printability-merged-test` (or rebase onto it), rebuild, check 0 overlaps.
3. Install trimesh/shapely, regenerate the kit, refresh `BOM_COST.md` volumes.
4. Work the audit items (item 5).

## 7. Final status of the project threads
(Filled in as each thread reports. If a thread is missing here, treat its working-tree edits as unfinished: build and check them before committing.)

Housekeeping: `~/GitHub/sc-trike/fugu_cageline` is a detached worktree at `b350de9` with only build outputs changed; it can be removed (`git worktree remove --force ../fugu_cageline`). A second detached worktree `wt_print` (at `891efd9`) lives in a /tmp scratchpad and will vanish on its own (`git worktree prune` afterwards).

| Thread | Status | Files | Committed? |
|---|---|---|---|
| Cage (collars, tail crevice, shock bolt clearance, cage FEM) | **final status pending.** Uncommitted in `parts/cage.py` now: front collar `SOCKET_H_FRONT` 1.4 -> 4.0 with leg node raised `FRONT_NODE_RISE` 4.5; short tubes merged into their hull nodes (`NODE_MERGE_FREE`, for the tail crevice at y 165); M6 shock pin head/nut clearance box (`PIN_HEAD_CLEAR_X` 9.8). `analyses/cage.py` untracked. Not yet built/checked as far as this doc knows. (No `_dbg_nodes` line was found in the tree on 03:59Z.) | `parts/cage.py`, `analyses/cage.py` | no |
| Lean arm (tie rod pocket ~10 deg tilt, arm edge radius) | **stopped, committed `06452ea`** (fan pocket + 3 mm `CROTCH_R`; earlier `588c9ea` buttress). Verified at `5364ebc`: 9 poses clear, arm SF 1.50, beam SF 1.89. Open: (1) tie rod still hits the knuckle 14-18 mm along the bar past the fan end (17.9 / 17.8 / 24.3 mm3 at -14 / +10 / +20 mm): lengthen the fan to ~20 mm or flare the sleeve mouth; the joint needs a **ball end**, a plain eye on an M3 stud cannot tilt 10 deg. (2) Re-run FEM on front arm, lean beam and tie rod after `06452ea`; measure knuckle wall with `soma analyze thickness --parts "knuckle 1,knuckle -1"`. (3) Arm still below SF 2 at the crotch edge. Pose script and logs copied to `handoffs/lean_arm_poses/` (`artic.py`, `logs/`) | `model.py`, `parts/frontarm.py` | yes |
| Printability | **done, not merged.** Fixes on `printability-fixes` and `printability-merged-test` (current head `b350de9` + fixes, builds with 0 collisions). Take them with `git merge --ff-only printability-merged-test`; if `shell/defect-sweep` has moved, use a plain `git merge printability-merged-test` instead (no rebase, per `AGENTS.md`). Knuckle boss is on hold until the lean arm pocket widening lands; afterwards re-check the knuckle for 1.2 mm walls. Kit regen needs `trimesh` and `shapely` in SOMA's Python (`pip install trimesh shapely`). The thread's `ec90141` is an earlier copy of `657d457` (same message) on no branch: ignore it. Full note: `handoffs/printability-handoff.md` in the project files (cloud side, may not be on the Mac) | branches `printability-*` | yes, on its own branches |
| Yeti shell (panel lines to cage lower rail and A-pillar kink) | **stopped, nothing uncommitted.** `5364ebc` (Yeti cage, open cockpit) and `b350de9` (upper link tongue 12 mm, SF 1.53) are committed. The shell-lines change from John's markup is **not started**: markup `renders/markup_cage_line.png`, before renders `renders/cageline_before_{markup,close,iso,side}.png`. Caveat: the cage takes its cowl corner from the shell rim (`cabin_ring()` in `parts/stealth_shell.py` feeds `make_cage(..., cabin=...)`), so break that link first, then make the shell edge follow the cage tube. Also open: tail light wire route along the cage (rear light contact removed), no FEM of the 7 mm cabin tubes, the print kit still lists the canopy (fixed on `printability-merged-test`) | `parts/stealth_shell.py`, `parts/cage.py` | yes (nothing pending) |
