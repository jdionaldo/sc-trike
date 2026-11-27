"""PETG cage, one part, built from solid round tubes with balled joints. All members are collected and fused in one go
(sequential booleans on dozens of tangent tubes were unreliable), the holes are cut at the end.

Frame facts (final frame, from tools/probe_xrow.py): front deck plate top z 16.6 (about 20 at the feet), half-width about 40 mm;
frame rail at x = +-52 for y = -180..20 with its top rising from z 20 to 34 and extra parts up to z 51 (hence the beams at z 59);
nothing stands at x >= 42 behind y = 20, the battery stack (x 12..36) reaches z 83.

Layout: front hoop leaning forward with crash bracing, side frames on the rails (lower beam, upper tube copying the shell belt line,
uprights and X bracing), rear legs rising back, A and B pillars, roof rails, supports under the rear shell hump, the rear shock
shock top mount (pin nodes tied to the rear supports and braced to the rear bridge, M6 pin) and the two magnetic light contact bridges.
"""
import cadquery as cq
from parts.params import *
from parts.util import hull
from parts.light_contacts import make_connector, roof_underside

FRONT_LEG_X = param(45.0, 'Cage front legs, half distance (outside the left-side parts on the front deck)', min=42.0, max=48.0, step=0.5, unit='mm', group='Cage')
REAR_LEG_X = param(45.0, 'Cage rear bridge legs, half distance', min=40.0, max=52.0, step=0.5, unit='mm', group='Cage')
REAR_SUP_X = param(30.0, 'Tail tube ends, half distance', min=25.0, max=50.0, step=1.0, unit='mm', group='Cage')
CAGE_BEAM = param(10.0, 'Cage main tube diameter', min=6.0, max=14.0, step=0.5, unit='mm', group='Cage')
PILLAR_D = CAGE_BEAM     # every tube of the cage has the same diameter
PILLAR_IN = param(6.5, 'Pillar tube centre inboard of the shell frame node', min=5.0, max=14.0, step=0.5, unit='mm', group='Cage')
BELT_CLEAR = param(14.0, 'Cage upper tubes below the shell belt line', min=8.0, max=30.0, step=1.0, unit='mm', group='Cage')
# Open cockpit (Yeti exposed cage): the cabin tubes are visible structure on the old canopy outline; the load path (feet, lower rails, front hoop and
# bumper, lean bridge, upper-link lugs, rear shock clevis and its braces) keeps CAGE_BEAM.
CABIN_BEAM = param(7.0, 'Open cockpit: visible cabin tube size (pillars, roof, roof X, windshield V, door diagonals, rear quarter)', min=6.0, max=10.0, step=0.5, unit='mm', group='Cage')
CABIN_INSET = param(2.0, 'Open cockpit: cabin tubes, outer face inside the old canopy outline', min=0.5, max=8.0, step=0.5, unit='mm', group='Cage')
BELT_DROP = param(0.0, 'Open cockpit: upper belt tubes, top face below the body rim', min=0.0, max=10.0, step=0.5, unit='mm', group='Cage')
COWL_SETBACK = 6.0       # mm: open cockpit: cowl corner node further back from the opening's front edge, so the hoop tube rising into it clears the hood
RIM_GAP = 1.0            # mm: cabin tubes beside the cabin opening stay this far off its cut edge
FS_BOSS_DROP = 14.0      # mm: open cockpit: Front shell boss on the B upright this far under the belt (the old upper-rail height, where the skin was matched)
CAGE_RAIL_X = 45.0       # mm: side frames 9.5 mm inboard of deck edge (54.5 mm) while clearing motor plate (x -41.0) and front shell (x 56.1)
CAGE_Z = 85.0            # mm: lower beam centre height, clearing center diff upper housing shelf (z <= 79.5 at x >= 40)
FRONT_FOOT_Y = -195.0    # mm: front feet on the clear front deck (ahead of the battery tray at y -187); vertical front struts
FRONT_FOOT_Z = 19.1 + 0.9      # mm: deck top at the front feet (y -195)
RAIL_FEET = ((-127.0, 23.8), (-48.0, 29.3), (38.0, 35.4))
# Front hoop legs (November 25): the cage's front brace is the upper arms' up stop (lean stop, TPU pad parts/stops.py); its 257 N bent the whole
# front cage to safety 0.5 with the hoop hanging free. A leg from each hoop corner straight down to the front deck, ahead of the wishbones (their
# front edge is at y -199 to -203 there) and inside the deck's chamfered front corner, takes the stop load to the deck. (y, deck top z), x below.
TAIL_FOOT_TIE = True
HOOP_FEET = ((-205.5, 18.3),)
HOOP_FOOT_X = 38.0
HOOP_KNEE_DZ = 12.0     # the foot rises straight up to a knee node this far above the foot end (the deck pocket stays square to it)
HOOP_TIE_X = 20.0       # tie from the knee up to the hoop crossbar at this |x| (triangle leg / crossbar / tie at the hoop corner)    # (y, deck top z): mid-deck feet at y=-48 (clear between motor plate and center diff) and rear feet at y=+38
LOWER_TAIL_BRACE = True   # lower rear tube following the rear quarter cover outline to the tail node (markup 10:15)
TRUSS_Y = -48.0          # mm: central door-truss node on the lower rail (directly above the mid-deck foot at y=-48)
RAIL_START_Y, RAIL_END_Y = -127.0, 38.0      # the rail starts on the front foot post, behind the tie rods (y -150)
CAGE_SCREW_D = 3.4       # mm: M3 clearance hole in each foot (assumed fastening)
FOOT_TAB_T = 3.0         # mm: flat foot tab under each M3 screw head (screw goes from above into a heat-set insert in the deck)
FOOT_TAB_W = 10.0        # mm: tab width (stadium)
RAIL_FOOT_X = 45.0       # mm: rail feet stand 9.5 mm inside the 54.5 mm deck edge (markup 13:41), straight vertical posts to CAGE_RAIL_X
RAIL_FOOT_DY = 8.5       # mm: the foot screw sits behind (+y) the foot, like the front feet
RAIL_HOLE_X = RAIL_FOOT_X
INSERT_POCKET_D, INSERT_POCKET_DEPTH = INSERT_M3_D, 5.0   # M3 heat-set insert pocket (screw comes up from the underside of the deck through a countersunk hole)
FRONT_TAB_DY = 8.5       # mm: front-foot screw sits behind the foot (+y)
FRONT_TAB_Z = 19.5 + 0.9       # mm: deck top at the front foot (y -195) + 0.4 mm lift
RAIL_TAB_LIFT = 0.4      # mm: same for the rail feet (the stand-in deck surface is a slightly sloped mesh)
BOSS_D, BOSS_HOLE = PILLAR_D + 2.0, 1.8   # mm: shell mounting bosses, M2 self-tapping pilot hole (assumed)

FOOT_POST_D=max(CAGE_SCREW_D+6*NOZZLE,CAGE_BEAM-0.6)
# Feet in the tub (November 21): each foot is the square tube section, standing FOOT_SEAT deep in a pocket of the deck, inside a socket
# (a collar on the front deck, a bracket tied into the side wall on the rear deck) cut with FOOT_CLEAR all round; model.py cuts them.
FOOT_SEAT = 3.0          # mm: pocket depth in the deck (the foot end sits on the pocket floor)
FOOT_CLEAR = 0.2         # mm: pocket and socket clearance around the foot
SOCKET_WALL = 2.4        # mm: socket wall around the foot (6 perimeters)
SOCKET_H_FRONT = 4.0     # mm: socket collar height above the front deck (the leg node sits FRONT_NODE_RISE higher, so the collar stays below its underside)
FRONT_NODE_RISE = 4.5    # mm: front leg node raised above the foot-on-deck height, so the front collar can be a real slot-in socket
SOCKET_H_RAIL = 10.0     # mm: socket/bracket height above the rear deck

def _interp(pts, y):
    for (ya, za), (yb, zb) in zip(pts, pts[1:]):
        if ya <= y <= yb: return za + (zb - za) * (y - ya) / (yb - ya)
    return pts[0][1] if y < pts[0][0] else pts[-1][1]

def _simplify(pts, tol):
    """Ramer-Douglas-Peucker on (y, z): keeps the kinks of the shell belt line, so the tubes copy its angles."""
    if len(pts) < 3: return pts
    (y0, z0), (y1, z1) = pts[0], pts[-1]
    d = [abs((z1 - z0) * (y - y0) - (y1 - y0) * (z - z0)) / max(1e-9, ((y1 - y0) ** 2 + (z1 - z0) ** 2) ** 0.5) for y, z in pts]
    i = max(range(len(d)), key=d.__getitem__)
    if d[i] <= tol: return [pts[0], pts[-1]]
    return _simplify(pts[:i + 1], tol)[:-1] + _simplify(pts[i:], tol)

def belt_profile(shells, y0, y1, x=CAGE_RAIL_X, z_above=90.0):
    """Underside of the shell belt line at x (the rail of the shell above the sill) as simplified (y, z) vertices."""
    pts = []
    for y in range(int(y0), int(y1) + 1, 5):
        zs = [z for z in (roof_underside(sh, y, z_above, x) for sh in shells) if z is not None and z < 170.0]
        if zs: pts.append((float(y), min(zs)))
    return _simplify(pts, 0.8)

PIN_FAN = 20.0           # mm: half spacing of the two overhead clevis nodes either side of the shock pin (keeps a 17 mm tool corridor along the pin axis)
PIN_TIE_RISE = 14.0      # mm: tie tubes meet the shock clevis this far above the pin axis
EAR_IN_X = 4.4           # mm: inner face of each shock clevis ear (8.8 mm slot for the 8 mm shock eye)
BRACE_TOP_X = 12.5       # mm: the tail braces end on the overhead cross tubes here, at the clevis ear's outer face, so the shock force goes from the ear
                         # straight down the braces (was 15.0: the cross tube between the ears bent, FEM at 273 N about 1.6); y_f / y_r are 20 mm off the pin axis, clear of the 17 mm tool corridor
EAR_BRIDGES = True       # webs between the two clevis ears ahead of and behind the shock eye (cage rear attempt 2)
EAR_ROOT_DROP = 6.0      # mm: the ear's lower edge drops this far under the front cross tube's rear corner (cage rear attempt 3: the ear root on the outer face
                         # was the low spot, 1.24 / 1.16 at 273 N, the plate only 1.5 mm deep under the tube there)
EAR_OUT_X = 12.0         # mm: outer face of each shock clevis ear plate, flush with the pin boss under the M6 head and nut (was 9.8: FEM at 237 N, safety 1.38 on the 5.4 mm plate)
PIN_HEAD_CLEAR_X = 9.8   # mm: cage material beside the M6 shock pin head/nut stays inside this |x| (head and nut start at |x| 12), except the boss they bear on
TUBE_SQUARE = True      # every _Frame member (cage, front arms, rear swingarm) is a chamfered square tube: flat faces print without support
TUBE_K = 0.88           # square side = TUBE_K x the old round diameter: similar section area and the corner stays inside the old round tube
TUBE_CHAMFER_K = 0.18   # 45 degree chamfer on each long edge, as a share of the side


def _tube_profile(d):
    """Octagon (square of side d*TUBE_K with 45 degree chamfers) as (x, y) points."""
    h = d * TUBE_K / 2.0; c = d * TUBE_K * TUBE_CHAMFER_K
    return [(-h + c, -h), (h - c, -h), (h, -h + c), (h, h - c), (h - c, h), (-h + c, h), (-h, h - c), (-h, -h + c)]


def _tube_solid(A, B, d, ext0=0.0, ext1=0.0):
    """Chamfered square prism from A to B (ends extended by ext0/ext1). One flat face stays horizontal (vertical members: flat to +-x)."""
    V = cq.Vector
    u = (B - A).normalized()
    ref = V(0, 0, 1) if abs(u.z) < 0.99 else V(1, 0, 0)
    w = ref.cross(u).normalized()
    return (cq.Workplane(cq.Plane(origin=A - u * ext0, xDir=w, normal=u)).polyline(_tube_profile(d)).close().extrude((B - A).Length + ext0 + ext1).val())


def _node_block(N, d):
    """Joint block for 3+ tubes meeting at a free corner: chamfered cube of the tube section, axis aligned."""
    q = d * TUBE_K
    blk = cq.Workplane('XY').workplane(offset=N.z - q / 2).center(N.x, N.y).rect(q, q).extrude(q).edges().chamfer(q * TUBE_CHAMFER_K).val()
    if 3.0 < abs(N.x) < 12.0:      # nodes on a shock clevis ear: keep the block inside the ear slab (x 4.4..10.4) so the eye slot and the bolt head stay clear
        lo, hi = (4.4, 10.4) if N.x > 0 else (-10.4, -4.4)
        blk = blk.intersect(cq.Solid.makeBox(hi - lo, 200, 200, cq.Vector(lo, N.y - 100, N.z - 100)))
    return blk


NODE_SNAP = 0.35         # mm: fill corners nearer than this to the node hull's surface or to a corner are snapped onto it (SCX30 same-node rule)
NODE_SNAP_MAX_Y = 100.0  # mm: nodes behind this y (tail joint, shock clevis) keep every fill corner: snapping there moved the governing cage FEM spots
                         # (attempt 2, November 27: tail joint 1.14 / 1.23 in the envelope, one side only)
NODE_FILL = True         # node hulls also take each tube's section at the node point (fills the outer corner). Tried False (SCX30 method, November 27):
                         # faces < 0.1 mm2 38 -> 22, edges < 0.5 mm 122 -> 103, but the cage FEM dropped (envelope 1.51 / 1.45 -> 1.30 / 1.39 at the tail joint)
NODE_E_CAP = 0.45        # share of a tube's length its end may be set back into a hull node
BOSS_INSERT = True           # shell bosses take an M3 heat-set insert (the shell is screwed on with ISO 7380 M3, model.py) instead of an M2 pilot
BOSS_INSERT_DEPTH = 5.0      # mm: insert pocket depth (Adafruit 4255 M3 x 4 + 1 mm)
from parts.params import INSERT_M3_D as INSERT_M3_POCKET_D
BOSS_LOG = []                # (x, y, z, sx, reach) of every boss with an insert, filled by the cage build, read by model.py
BOSS_AS_TUBE = False         # tried True (shell bosses as square members in the node hull): FEM unchanged but edges < 0.5 mm 123 -> 133, faces < 0.1 mm2
                             # 34 -> 38 (a 12 mm member among 10 and 7 mm tubes in one hull adds facets at the B-pillar foot): round bosses kept
TAIL_ANCHOR_ON_ROOF = False  # tried True (tail anchor moved onto the roof rear node B, November 27): edges < 0.5 mm 123 -> 59, but the tail frame re-aims
                             # (volume +6 %, 1 all-pairs overlap) and the cage FEM dropped (shock 1.40, envelope 1.22 at the tail joint): roof peak not converted, load path
NODE_MERGE_FREE_CABIN = 0.0   # tried 4.0 (merge the roof rear node and the tail anchor, 9.4 mm apart, into one hull): edges < 0.5 mm 123 -> 87 but cage volume +3.6 %. Was: (roof rear node and tail anchor,
                              # 9.4 mm apart: two hulls with a short 7 mm stub made 19 edges under 0.5 mm per side)
NODE_MERGE_FREE = 1.0    # mm: two hull nodes whose joining tube has less free length than this become one node


def _section_points(A, u, d):
    """The 8 corners of the chamfered square tube section at point A, normal u, in the same frame as _tube_solid."""
    V = cq.Vector
    ref = V(0, 0, 1) if abs(u.z) < 0.99 else V(1, 0, 0)
    w = ref.cross(u).normalized(); v = u.cross(w)
    return [(A + w * x + v * y).toTuple() for x, y in _tube_profile(d)]


HULL_FALLBACKS = []


def _hull_solid(pts, tol=2e-3):
    """Convex hull as a solid with every facet a single planar face: triangles whose planes agree within tol (mm) are merged, so
    nearly coplanar section corners give one face instead of hairline triangles. Falls back to parts.util.hull."""
    import numpy as np
    from scipy.spatial import ConvexHull
    P = np.array(pts, float)
    h = ConvexHull(P)
    groups = []
    for eq, simp in zip(h.equations, h.simplices):
        for g in groups:
            if np.dot(g[0][:3], eq[:3]) > 1 - 1e-7 and all(abs(np.dot(g[0][:3], P[k]) + g[0][3]) < tol for k in simp):
                g[1].update(int(k) for k in simp); break
        else:
            groups.append([eq, set(int(k) for k in simp)])
    try:
        faces = []
        for eq, idx in groups:
            n = np.array(eq[:3]); Q = P[sorted(idx)]; c = Q.mean(0)
            u = np.cross(n, [0, 0, 1.0] if abs(n[2]) < 0.9 else [1.0, 0, 0]); u /= np.linalg.norm(u); v = np.cross(n, u)
            Q = Q[np.argsort(np.arctan2((Q - c) @ v, (Q - c) @ u))]
            keep = [q for k, q in enumerate(Q) if np.linalg.norm(q - Q[k - 1]) > 1e-6]
            faces.append(cq.Face.makeFromWires(cq.Wire.makePolygon([cq.Vector(*q) for q in keep], close=True)))
        sol = cq.Solid.makeSolid(cq.Shell.makeShell(faces))
        if sol.Volume() < 0: sol = cq.Solid(sol.wrapped.Reversed())
        sol = sol.fix()
        if sol.isValid() and abs(sol.Volume() - h.volume) < 1e-3 * h.volume + 1e-3: return sol.clean()
    except Exception:
        pass
    HULL_FALLBACKS.append(len(pts))
    return hull(pts)


def _section_radius(d):
    h = d * TUBE_K / 2.0; c = d * TUBE_K * TUBE_CHAMFER_K
    return (h * h + (h - c) ** 2) ** 0.5


BOSS_TARGETS = []   # shell solids the boss stubs should reach (set by model.py for the stealth shell)
BOSS_MAX_REACH = 30.0
BOSS_GAP = 0.8


def _reach_to_shell(x, y, z, sx, default):
    """Length of the boss stub: runs along +-x from the node to the first shell skin, BOSS_GAP short of it; default when no target."""
    if not BOSS_TARGETS or z > 210.0:   # roof bosses keep the default: a 9 mm stub there made the cage mesh non-manifold at the roof rail (kit build failed)
        return default
    ray = cq.Solid.makeCylinder(BOSS_D / 2, BOSS_MAX_REACH, cq.Vector(x, y, z), cq.Vector(sx, 0, 0))
    best = None
    for sh in BOSS_TARGETS:
        try:
            hit = sh.intersect(ray)
        except Exception:
            continue
        if hit.Volume() > 1e-6:
            bb = hit.BoundingBox()
            d = (bb.xmin - x) if sx > 0 else (x - bb.xmax)
            best = d if best is None else min(best, d)
    r = round(max(best - BOSS_GAP, 0.5), 2) if best is not None else default
    print('boss at', (round(x, 1), round(y, 1), round(z, 1)), 'sx', sx, 'reach', r, '(default %.1f)' % default)
    return r


class _Frame:
    """Collects solids to fuse and holes to cut."""
    def __init__(self, hull_nodes=False):
        self.solids = []; self.holes = []; self.tags = {}; self.segs = []
        self.hull_nodes = hull_nodes      # cage: every joint is a convex faceted node (see _hull_tubes); arms keep mitres and copes
        self.max_splits = 200 if hull_nodes else 40
    def tube(self, a, b, d):
        """Records the member; the solid is made in build() once every node is known (mitres, copes, corner balls)."""
        self.segs.append((a, b, d)); self.tags[len(self.solids)] = 'tube (%.1f,%.1f,%.1f)->(%.1f,%.1f,%.1f)' % (tuple(a) + tuple(b))
        self.solids.append(('tube', len(self.segs) - 1))
    def _split_crossings(self):
        """Two tubes that pass through each other mid-span become four tubes meeting at one node (cut and welded, not overlapping)."""
        import numpy as np
        ph = {x[1]: n for n, x in enumerate(self.solids) if isinstance(x, tuple)}     # segment index -> slot in self.solids
        for _ in range(self.max_splits):
            hit = None
            for i in range(len(self.segs)):
                a0, a1 = np.array(self.segs[i][0], float), np.array(self.segs[i][1], float)
                for j in range(i + 1, len(self.segs)):
                    b0, b1 = np.array(self.segs[j][0], float), np.array(self.segs[j][1], float)
                    u, v, w = a1 - a0, b1 - b0, a0 - b0
                    A, B, C, D, E = u @ u, u @ v, v @ v, u @ w, v @ w
                    den = A * C - B * B
                    if den < 1e-9: continue
                    s_ = (B * E - C * D) / den; t_ = (A * E - B * D) / den
                    if not (0.03 < s_ < 0.97 and 0.03 < t_ < 0.97): continue
                    if np.linalg.norm(a0 + s_ * u - (b0 + t_ * v)) < (self.segs[i][2] + self.segs[j][2]) / 2 - 0.3:
                        hit = (i, j, (a0 + s_ * u + b0 + t_ * v) / 2); break
                if hit: break
            if not hit: return
            i, j, p = hit
            p = tuple(round(float(c), 1) for c in p)
            for k in (i, j):
                a, b, d = self.segs[k]
                self.segs[k] = (a, p, d)
                self.segs.append((p, b, d)); n = len(self.segs) - 1
                self.solids.append(('tube', n)); self.tags[len(self.solids) - 1] = self.tags.get(ph[k], 'split tube')
                ph[n] = len(self.solids) - 1
    def _split_endpoints(self):
        """If a tube endpoint lies on the interior of another tube segment, split that through-segment at the endpoint so every
        junction is a true graph node with a shared spherical joint (no short coped T-joints that leave visible gaps)."""
        V = cq.Vector
        for _ in range(80):
            split = None
            for i, (a, b, d) in enumerate(self.segs):
                A, B = V(*a), V(*b); L = (B - A).Length
                if L < 1e-6: continue
                for j, (a2, b2, d2) in enumerate(self.segs):
                    if i == j: continue
                    for p in (a2, b2):
                        N = V(*p)
                        t = (N - A).dot(B - A) / (L * L)
                        if 0.02 < t < 0.98 and (A + (B - A) * t - N).Length < 0.5:
                            split = (i, p); break
                    if split: break
                if split: break
            if not split: return
            i, p = split
            a, b, d = self.segs[i]
            self.segs[i] = (a, p, d)
            self.segs.append((p, b, d)); n = len(self.segs) - 1
            self.solids.append(('tube', n)); self.tags[len(self.solids) - 1] = 'split_through'
    def _hull_tubes(self):
        """Clean joints (cage): every tube is the convex hull of its two end sections, and every node where tubes meet at an angle is
        the convex hull of the incident tubes' sections, taken at the node and at a set-back e_i along each tube. e_i is chosen so the
        end section of each tube is a face of the node hull (e_i >= e_j cos(theta) + R sin(theta) for every other tube j, R = section
        corner radius), so tube and node share that face exactly: no mitre extension, cope or cube corner can stick out of the joint.
        Very short tubes cap e_i at NODE_E_CAP of their length (the tube then enters the node through its faces)."""
        import math
        V = cq.Vector
        key = lambda p: tuple(round(c, 1) for c in p)
        self._split_endpoints()      # first: tubes that end on another tube (a crossing split moves the through tube off those ends)
        self._split_crossings()
        self._split_endpoints()
        ends = {}
        for i, (a, b, d) in enumerate(self.segs):
            if (V(*b) - V(*a)).Length < 0.05: continue
            for k, p in ((0, a), (1, b)): ends.setdefault(key(p), []).append((i, k))
        set_back = {}           # (seg, end) -> e
        nodes = []
        for nk, group in ends.items():
            N = V(*nk)
            dirs = []
            for i, k in group:
                a, b, d = self.segs[i]
                A, B = V(*key(a)), V(*key(b))
                dirs.append(((B - A).normalized() if k == 0 else (A - B).normalized(), (B - A).Length, d))
            if len(group) == 1 or (len(group) == 2 and dirs[0][0].dot(dirs[1][0]) < -0.9995):
                for e in group: set_back[e] = 0.0             # free end or straight run: flat ends meet on the node plane
                continue
            R = [_section_radius(d) for _, _, d in dirs]
            cap = [NODE_E_CAP * L for _, L, _ in dirs]
            e = [min(r, c) for r, c in zip(R, cap)]
            for _ in range(600):                                # fixed point of e_i = max(R_i, max_j e_j cos + R_j sin), capped
                ch = 0.0
                for ii in range(len(dirs)):
                    need = R[ii]
                    for jj in range(len(dirs)):
                        if ii == jj: continue
                        c = max(-1.0, min(1.0, dirs[ii][0].dot(dirs[jj][0])))
                        need = max(need, e[jj] * c + R[jj] * math.sqrt(max(0.0, 1 - c * c)))
                    ne = min(need + 0.05, cap[ii])
                    ch = max(ch, abs(ne - e[ii])); e[ii] = ne
                if ch < 1e-3: break
            for (i, k), ee in zip(group, e): set_back[(i, k)] = ee
            pts = [q for (u, L, d), ee in zip(dirs, e) for q in _section_points(N + u * ee, u, d)]     # tube end faces: exact, shared
            if NODE_FILL and N.y > NODE_SNAP_MAX_Y:   # tail and shock clevis nodes: every fill corner, as before (they carry the governing FEM spots)
                for q in [q for u, L, d in dirs for q in _section_points(N, u, d)]:
                    if all(sum((qa - pa) ** 2 for qa, pa in zip(q, p_)) > 0.5 ** 2 for p_ in pts): pts.append(q)
            elif NODE_FILL:          # fill: each section at the node itself (keeps the outer corner full)
                # a fill corner is taken only where it adds real corner material: at least NODE_SNAP outside the hull of the points taken so far
                # and NODE_SNAP from every point. One closer to the hull surface or a corner is snapped onto it (the corner moves by under
                # NODE_SNAP); one inside the hull adds nothing. Barely-proud fill corners were what made the cage's hairline facets.
                import numpy as _np
                from scipy.spatial import ConvexHull as _CH
                cand = [q for u, L, d in dirs for q in _section_points(N, u, d)]
                P = _np.array(pts, float)
                while cand:
                    try: eq = _CH(P).equations
                    except Exception: break
                    out = [(float(_np.max(eq[:, :3] @ _np.array(q) + eq[:, 3])), q) for q in cand]
                    out.sort(key=lambda t: (-round(t[0], 4), round(abs(t[1][0]), 3), round(t[1][1], 3), round(t[1][2], 3)))   # mirror-symmetric order
                    d_out, q = out[0]
                    if d_out < NODE_SNAP: break                    # every remaining fill corner is inside or within NODE_SNAP of the hull
                    cand = [c for _, c in out[1:]]
                    if _np.min(_np.linalg.norm(P - _np.array(q), axis=1)) < NODE_SNAP: continue
                    P = _np.vstack([P, q]); pts.append(q)
            nodes.append((N, pts))
        # Nodes joined by a tube with less than NODE_MERGE_FREE of free length between its two set-backs become one hull: two convex
        # hulls with a stub between them leave a re-entrant slot (tail joint at y 165, clevis tie nodes at x 7.4 / 15).
        idx = {key(N.toTuple()): k for k, (N, _) in enumerate(nodes)}
        parent = list(range(len(nodes)))
        def find(k):
            while parent[k] != k: k = parent[k]
            return k
        merged = set()
        for i, (a, b, d) in enumerate(self.segs):
            ka, kb = key(a), key(b)
            if ka in idx and kb in idx and ka != kb:
                free = (V(*kb) - V(*ka)).Length - set_back.get((i, 0), 0.0) - set_back.get((i, 1), 0.0)
                if free < NODE_MERGE_FREE or (free < NODE_MERGE_FREE_CABIN and max(V(*ka).y, V(*kb).y) <= NODE_SNAP_MAX_Y):
                    merged.add(i); parent[find(idx[ka])] = find(idx[kb])
        groups = {}
        for k, (N, pts) in enumerate(nodes): groups.setdefault(find(k), []).append((N, pts))
        nodes = [(g[0][0], [q for _, pts in g for q in pts]) for g in groups.values()]
        if merged: print('cage: %d short tubes merged into their nodes:' % len(merged), sorted({key(self.segs[i][0]) for i in merged} | {key(self.segs[i][1]) for i in merged}))
        out = {}
        for i, (a, b, d) in enumerate(self.segs):
            A, B = V(*key(a)), V(*key(b)); L = (B - A).Length      # the node position (rounded key), so tube and node sections coincide exactly
            if L < 0.05 or i in merged: out[i] = None; continue
            u = (B - A) / L
            e0, e1 = set_back.get((i, 0), 0.0), set_back.get((i, 1), 0.0)
            if L - e0 - e1 < 0.3: out[i] = None; continue      # covered by its two nodes
            out[i] = _hull_solid(_section_points(A + u * e0, u, d) + _section_points(B - u * e1, u, d))
        self.node_solids = []
        for N, pts in nodes:
            self.node_solids.append(_hull_solid(pts))      # (clevis-ear nodes at x +-7.4 reach x 10.9 at most: the M6 head and nut sit beyond x 12)
        return out
    def _resolve_tubes(self):
        """Joint rule (cut and welded, never overlapping tubes): a 2-tube bend is mitred on its bisector plane; a tube ending on the side of
        another is coped (cut by the through tube's surface); 3 or more tubes meeting at a free corner share a ball of tube radius."""
        import math
        key = lambda p: tuple(round(c, 1) for c in p)
        V = cq.Vector
        self._split_crossings()
        self._split_endpoints()
        ends = {}
        for i, (a, b, d) in enumerate(self.segs):
            for k, p in ((0, a), (1, b)): ends.setdefault(key(p), []).append((i, k))
        def through(node, skip):
            res = []
            for j, (a, b, d) in enumerate(self.segs):
                if j in skip: continue
                A, B, N = V(*a), V(*b), V(*node)
                L = (B - A).Length
                if L < 1e-6: continue
                t = (N - A).dot(B - A) / (L * L)
                if 0.02 < t < 0.98 and (A + (B - A) * t - N).Length < 0.35 + d / 2 * 0.05: res.append(j)
            return res
        cyl = {}
        def cylinder(i, ext0=0.0, ext1=0.0):
            a, b, d = self.segs[i]; A, B = V(*a), V(*b); u = (B - A).normalized()
            if TUBE_SQUARE: return _tube_solid(A, B, d, ext0, ext1)
            return cq.Solid.makeCylinder(d / 2, (B - A).Length + ext0 + ext1, A - u * ext0, u)
        def halfspace(node, n):
            return cq.Workplane(cq.Plane(origin=V(*node), normal=n.toTuple())).rect(200, 200).extrude(-200).val()
        out = {}
        for i, (a, b, d) in enumerate(self.segs):
            r = d / 2; A, B = V(*a), V(*b)
            if (B - A).Length < 0.05: out[i] = None; continue
            ext = [0.0, 0.0]; cuts = []; balls = []
            for k, (node, other) in enumerate(((a, B), (b, A))):
                N = V(*node); away = (other - N).normalized()
                group = [e for e in ends[key(node)] if e[0] != i]
                th = through(node, {i} | {e[0] for e in group})
                if th:                                              # coped into the through tube
                    for j in th: cuts.append(('cope', j))
                elif len(group) == 0: pass                          # free end: flat
                elif len(group) == 1:                               # mitred bend
                    j, kj = group[0]; a2, b2, d2 = self.segs[j]
                    o2 = V(*(b2 if kj == 0 else a2)); away2 = (o2 - N).normalized()
                    c = max(-1.0, min(1.0, away.dot(away2)))
                    if c > -0.1:
                        balls.append(N); continue                       # acute 2-tube V-junction: spherical node (no protruding mitre spike)
                    theta = math.acos(c)
                    if c < -0.9995: continue                        # straight run
                    ext[k] = min((r * (1.25 if TUBE_SQUARE else 1.0)) / math.tan(theta / 2) + 0.5, 4 * r)
                    n = away - away2
                    if n.Length < 1e-6: continue
                    cuts.append(('plane', node, n.normalized(), k))
                else: balls.append(N)                               # corner of 3+ tubes
            sol = cylinder(i, ext[0], ext[1])
            for c in cuts:
                if c[0] == 'plane': sol = sol.cut(halfspace(c[1], c[2]))
            for N in balls: sol = sol.fuse(_node_block(N, d) if TUBE_SQUARE else cq.Solid.makeSphere(r, N, angleDegrees1=-90, angleDegrees2=90))
            out[i] = (sol, [c[1] for c in cuts if c[0] == 'cope'])
        for i, v in out.items():
            if v is None: continue
            sol, copes = v
            for j in copes:
                try:
                    t = sol.cut(cylinder(j))
                    if t.isValid() and t.Solids(): sol = t
                except Exception: pass
            sol = sol.clean() if sol.isValid() else sol
            out[i] = sol
        return out
    def post(self, x, y, z0, z1, d): self.solids.append(cq.Solid.makeCylinder(d / 2, z1 - z0, cq.Vector(x, y, z0), cq.Vector(0, 0, 1)))
    def boss(self, p, sx, reach):
        """Mounting boss on a pillar node: a short stub towards the shell with a pilot hole."""
        x, y, z = p
        reach = _reach_to_shell(x, y, z, sx, reach)
        if BOSS_AS_TUBE and y <= NODE_SNAP_MAX_Y:   # (tail supports keep their round bosses: load path, not touched) SCX30 joint method (November 27): the boss is a short chamfered-square member from the node, so it joins the node hull like a tube
            # (same axis and pilot hole; the round stub and cone root overlapped the hull as a second solid and left short edges at the B-pillar foot)
            self.tube((x, y, z), (round(x + sx * reach, 1), y, z), BOSS_D / TUBE_K)
            self.holes.append(cq.Solid.makeCylinder(BOSS_HOLE / 2, reach + 1.0, cq.Vector(x, y, z), cq.Vector(sx, 0, 0)))
            return
        stub = cq.Solid.makeCylinder(BOSS_D / 2, reach, cq.Vector(x, y, z), cq.Vector(sx, 0, 0))
        if reach > 6.0:      # a long stub gets a conical root: the plain cylinder met the joint at a sharp inner edge (FEM: a singular spot at the B-pillar foot boss)
            stub = stub.fuse(cq.Solid.makeCone(BOSS_D / 2 + 3.0, BOSS_D / 2, 6.0, cq.Vector(x + sx * 2.0, y, z), cq.Vector(sx, 0, 0)))
        self.solids.append(stub)
        if BOSS_INSERT and y <= NODE_SNAP_MAX_Y:   # shell fixing (November 27): M3 heat-set insert pocket at the boss face (Adafruit 4255, as the kit's other
            # M3 inserts: D3.8 pocket, 5 mm = insert + 1 mm); the screw comes in through the Front shell (model.py, shell fixing)
            face = cq.Vector(x + sx * reach, y, z)
            self.holes.append(cq.Solid.makeCylinder(INSERT_M3_POCKET_D / 2, BOSS_INSERT_DEPTH, face, cq.Vector(-sx, 0, 0)))
            BOSS_LOG.append((x, y, z, sx, reach))
        else:
            self.holes.append(cq.Solid.makeCylinder(BOSS_HOLE / 2, reach + 1.0, cq.Vector(x, y, z), cq.Vector(sx, 0, 0)))
    def foot_tab(self, p0, p1, z):
        """Flat stadium tab from the post/ball at p0=(x,y) to the screw at p1=(x,y), on the deck at height z, with an open M3 hole at p1."""
        a, b = cq.Vector(p0[0], p0[1], z), cq.Vector(p1[0], p1[1], z)
        d = b - a; r = FOOT_TAB_W / 2
        tab = cq.Solid.makeCylinder(r, FOOT_TAB_T, a, cq.Vector(0, 0, 1)).fuse(cq.Solid.makeCylinder(r, FOOT_TAB_T, b, cq.Vector(0, 0, 1)))
        side = cq.Vector(-d.y, d.x, 0).normalized() * r
        quad = cq.Wire.makePolygon([a + side, b + side, b - side, a - side], close=True)
        tab = tab.fuse(cq.Solid.extrudeLinear(cq.Face.makeFromWires(quad), cq.Vector(0, 0, FOOT_TAB_T))).clean()
        self.solids.append(tab)
        self.holes.append(cq.Solid.makeCylinder(CAGE_SCREW_D / 2, FOOT_TAB_T + 2.0, cq.Vector(p1[0], p1[1], z - 1.0), cq.Vector(0, 0, 1)))
    def vhole(self, x, y, z0, ln, d=CAGE_SCREW_D): self.holes.append(cq.Solid.makeCylinder(d / 2, ln, cq.Vector(x, y, z0), cq.Vector(0, 0, 1)))
    def build(self):
        """Fuse one member at a time and check every step (valid, volume grows): OCC fails silently on some tangent tube joints,
        a failed step is retried with the member nudged by tiny amounts, and reported."""
        tubes = self._hull_tubes() if self.hull_nodes else self._resolve_tubes()
        if self.hull_nodes: self.solids += self.node_solids
        seg_of = {n: x[1] for n, x in enumerate(self.solids) if isinstance(x, tuple)}
        self.solids = [tubes[x[1]] if isinstance(x, tuple) else x for x in self.solids]
        keep = [(i, x) for i, x in enumerate(self.solids) if x is not None]
        self._seg_of = {n: seg_of[i] for n, (i, x) in enumerate(keep) if i in seg_of}
        self.tags = {n: self.tags.get(i) for n, (i, x) in enumerate(keep) if i in self.tags}
        self.solids = [x for i, x in keep]
        s = self.solids[0]; bad = 0
        for i, x in enumerate(self.solids[1:], 1):
            ok = False
            for dx, dy, dz in [(0, 0, 0), (0.013, 0.007, 0.011), (-0.017, 0.011, -0.013), (0.031, -0.023, 0.019), (-0.043, -0.037, 0.029)]:
                xm = x if (dx, dy, dz) == (0, 0, 0) else x.translate(cq.Vector(dx, dy, dz))
                try: t = s.fuse(xm)
                except Exception: continue   # OCC can raise on a near-tangent joint: try the next nudge
                volume_tolerance=max(1e-6,s.Volume()*1e-8)
                if t.isValid() and t.Volume() >= s.Volume() - volume_tolerance and len(t.Solids()) <= len(s.Solids()) + 1:
                    s = t; ok = True; break
            if not ok and i in self._seg_of:       # the mitre/cope cut of this member did not fuse: use the plain ball-ended tube instead
                a, b, d = self.segs[self._seg_of[i]]; v0, v1 = cq.Vector(*a), cq.Vector(*b)
                if TUBE_SQUARE: cap = _tube_solid(v0, v1, d).fuse(_node_block(v0, d), _node_block(v1, d)).clean()
                else: cap = cq.Solid.makeCylinder(d / 2, (v1 - v0).Length, v0, v1 - v0).fuse(*[cq.Solid.makeSphere(d / 2, c, angleDegrees1=-90, angleDegrees2=90) for c in (v0, v1)]).clean()
                t = s.fuse(cap)
                if t.isValid() and t.Volume() >= s.Volume() - 1e-6:
                    s = t; ok = True; print('cage: member', self.tags.get(i), 'fell back to a ball-ended tube')
            if not ok:
                raise RuntimeError('Cage member failed to fuse: '+str(i)+' '+self.tags.get(i, self.tags.get(i-1,'joint')))
        if bad: print('cage: %d members could not be fused' % bad)
        if len(s.Solids()) > 1: print('cage: %d separate solids after fusing:' % len(s.Solids()), [(round(q.Volume()), tuple(round(c) for c in q.Center().toTuple())) for q in s.Solids()][:8])
        try:
            t = s.clean()
            if t.isValid(): s = t
        except Exception: pass   # OCC can fail to unify near-tangent tube faces: keep the valid fused cage
        for h in self.holes:
            t = s.cut(h)
            if t.isValid() and t.Volume() < s.Volume(): s = t
        try:
            t = s.clean()
            if t.isValid(): s = t
        except Exception: pass   # OCC can fail to unify near-tangent tube faces: keep the valid fused cage
        return s

def _report_crossings(segs):
    """Print every pair of tubes whose centrelines pass through each other mid-span (not a welded node): those would be overlaps."""
    import numpy as np
    bad = []
    for i in range(len(segs)):
        a0, a1 = np.array(segs[i][0], float), np.array(segs[i][1], float)
        for j in range(i + 1, len(segs)):
            b0, b1 = np.array(segs[j][0], float), np.array(segs[j][1], float)
            u, v, w = a1 - a0, b1 - b0, a0 - b0
            A, B, C, D, E = u @ u, u @ v, v @ v, u @ w, v @ w
            den = A * C - B * B
            if den < 1e-9: continue
            s_ = min(1, max(0, (B * E - C * D) / den)); t_ = min(1, max(0, (A * E - B * D) / den))
            if not (0.03 < s_ < 0.97 and 0.03 < t_ < 0.97): continue          # meets at an end: a node
            if np.linalg.norm(a0 + s_ * u - (b0 + t_ * v)) < (segs[i][2] + segs[j][2]) / 2 - 0.3:
                bad.append((tuple(round(c, 1) for c in segs[i][0]), tuple(round(c, 1) for c in segs[i][1]), tuple(round(c, 1) for c in segs[j][0]), tuple(round(c, 1) for c in segs[j][1])))
    print('cage: %d mid-span tube crossings' % len(bad))
    for b in bad[:12]: print('   crossing', b)


def tail_tube_starts(b1, end):
    """Shared start nodes (b1, mid_q, n_tip) for the three tail tube pairs converging at `end`,
    aligned to the exact -1.3012 YZ slope of the Canopy rear quarter cover (markup 12:55)."""
    y_tip = 82.4
    z_tip = round(b1[2] - 1.3012 * (y_tip - b1[1]), 1)
    x_tip = round(b1[0] + (end[0] - b1[0]) * (y_tip - b1[1]) / (end[1] - b1[1]), 1)
    n_tip = (x_tip, y_tip, z_tip)
    t_mid = 0.58
    mid_q = tuple(round(b1[i] + t_mid * (n_tip[i] - b1[i]), 1) for i in range(3))
    return b1, mid_q, n_tip


def _half(d):
    return d * TUBE_K / 2.0      # half the side of the square tube: centre to flat face


def _ring_x(ring, y):
    """x of the cabin opening edge (+x side) at y."""
    for (xa, ya), (xb, yb) in zip(ring, ring[1:]):
        if ya <= y <= yb: return xa + (xb - xa) * (y - ya) / (yb - ya)
    return ring[0][0] if y < ring[0][1] else ring[-1][0]


def cabin_nodes(cabin):
    """Open cockpit cabin nodes (+x side, tube centres): K cowl corner in the cabin opening (tube top flush with the rim), A roof front corner,
    B roof rear corner (B-pillar top). A and B sit on the old canopy outline (side glass plane, roof edge), outer faces CABIN_INSET inside it."""
    h = _half(CABIN_BEAM); ring = cabin['ring']
    ky = ring[0][1] + RIM_GAP + h + COWL_SETBACK
    kx = _ring_x(ring, ky) - RIM_GAP - h
    kz = cabin['rim_z'](kx, ring[0][1] - 1.5) - BELT_DROP - h
    rf, rp = cabin['roof_front'], cabin['roof_peak']
    a = (rf[0] - CABIN_INSET - h, rf[1] + CABIN_INSET + h, rf[2] - CABIN_INSET - h)
    b = (rp[0] - CABIN_INSET - h, rp[1], rp[2] - CABIN_INSET - h)
    r = lambda p: tuple(round(float(c), 1) for c in p)
    return r((kx, ky, kz)), r(a), r(b)


def make_cage(front_y, rear_y, belt=None, nodes=None, supports=None, tie=None, tower_foot_z=None, tail=None, tail_screws=None, cabin=None):
    """cabin: None = closed canopy (cabin tubes under the canopy, as before); a dict from model.py = open cockpit (exposed cabin frame)."""
    BOSS_LOG.clear()
    F = _Frame(hull_nodes=True)
    fb, _, zf = make_connector(front_y, 200.0, 'Front', FRONT_LEG_X, FRONT_FOOT_Z, legs=False)
    rb, _, zr = make_connector(rear_y, 200.0, 'Rear', REAR_LEG_X, CAGE_Z, legs=False)
    F.solids += [fb] if cabin else [fb, rb]      # open cockpit: no roof over the rear light contact, it is dropped
    zft, zrt = zf - 4.2, zr - 5.5            # tube centres sit inside the contact bosses so tube tops stay below z_deck; the front hoop 1.3 mm higher than
    # the rear: the upper arm's shock post came within 0.094 mm of its corner at 12 mm bump + 10 deg lean
    fz0 = FRONT_FOOT_Z + CAGE_BEAM / 2 + FRONT_NODE_RISE     # leg node centre, raised so the deck collar fits under it
    y_bump = front_y - 14.0                  # crash bumper tube in front of the contact plate
    z_x = 66.0                               # cross tube above the left-side front parts (they reach z 55)
    y_x = FRONT_FOOT_Y + (front_y - FRONT_FOOT_Y) * (z_x - fz0) / (zft - fz0)
    upper = [(y, z - BELT_CLEAR) for y, z in belt] if belt else None
    if cabin and belt:   # open cockpit: the upper belt tubes come up so their top face is flush with the body rim (BELT_DROP below it)
        ring = cabin['ring']
        upper = [(y, round(cabin['rim_z'](_ring_x(ring, y) + 2.0, y) - BELT_DROP - _half(CAGE_BEAM), 1)) for y in (RAIL_START_Y, TRUSS_Y, RAIL_END_Y)]
        print('cage (open cockpit): upper belt nodes (y, z)', upper)
    for sx in (-1, 1):
        fx, rx, px = sx * FRONT_LEG_X, sx * REAR_LEG_X, sx * CAGE_RAIL_X
        zs = round(_interp(upper, RAIL_START_Y), 1) if upper else 119.9
        ze = round(_interp(upper, RAIL_END_Y), 1) if upper else 119.9
        zt = round(_interp(upper, TRUSS_Y), 1) if upper else 119.9
        # --- front hoop and outriggers (matching reference image1.jpg.png, zero mid-span crossings)
        # Wishbone front end (November 22): the old front feet at y -195 stood in the middle of the new arms. The front hoop now hangs from the
        # upper belt start and the cowl corner; the frame stands on a third pair of rail feet at y -135, behind the tie rods (RAIL_FEET).
        for y, zr_top in HOOP_FEET:      # front hoop leg: hoop corner straight down to a foot in the front deck (stop load path, HOOP_FEET)
            zb = round(zr_top + RAIL_TAB_LIFT - FOOT_SEAT, 2); hx = sx * HOOP_FOOT_X
            knee = (hx, y, round(zb + HOOP_KNEE_DZ, 1))
            F.tube((hx, y, zb), knee, CAGE_BEAM)                                            # foot, square in its deck pocket
            F.tube(knee, (fx, front_y, round(zft, 1)), CAGE_BEAM)                           # leg to the hoop corner
            F.tube(knee, (sx * HOOP_TIE_X, front_y, round(zft, 1)), CAGE_BEAM)              # tie to the hoop crossbar
            F.holes.append(cq.Solid.makeCylinder(INSERT_POCKET_D / 2, INSERT_POCKET_DEPTH + 0.5, cq.Vector(hx, y, zb - 0.5), cq.Vector(0, 0, 1)))
        for a, b in [((fx, front_y, round(zft, 1)), (fx, y_bump, round(zft, 1))),                  # upper forward outrigger
                     ((fx, front_y, round(zft, 1)), (px, RAIL_START_Y, zs))]:                      # front hoop top to upper belt start
            F.tube(a, b, CAGE_BEAM)
        # --- lower beam on the rail
        F.tube((px, RAIL_START_Y, CAGE_Z), (px, TRUSS_Y, CAGE_Z), CAGE_BEAM)
        F.tube((px, TRUSS_Y, CAGE_Z), (px, RAIL_END_Y, CAGE_Z), CAGE_BEAM)
        for y, zr_top in RAIL_FEET:
            zb = round(zr_top + RAIL_TAB_LIFT - FOOT_SEAT, 2); fx2 = sx * RAIL_FOOT_X
            F.tube((fx2, y, zb), (px, y, CAGE_Z), CAGE_BEAM)                                   # square foot leg, its end sits FOOT_SEAT deep in the deck socket
            F.holes.append(cq.Solid.makeCylinder(INSERT_POCKET_D / 2, INSERT_POCKET_DEPTH + 0.5, cq.Vector(fx2, y, zb - 0.5), cq.Vector(0, 0, 1)))   # M3 heat-set insert, screwed up from under the deck
        # --- upper tubes copy the shell belt line, uprights, V-truss door bars with 3-hole gusset plate
        if upper:
            # Explicit belt nodes so every upright and truss diagonal shares the exact same (x, y, z) node on the upper belt rail
            u_nodes = [
                (px, RAIL_START_Y, zs),
                (px, TRUSS_Y, zt),
                (px, RAIL_END_Y, ze),
            ]
            for a, b in zip(u_nodes, u_nodes[1:]): F.tube(a, b, CAGE_BEAM)
            F.tube((px, RAIL_START_Y, CAGE_Z), (px, RAIL_START_Y, zs), CAGE_BEAM)
            F.tube((px, RAIL_END_Y, CAGE_Z), (px, RAIL_END_Y, ze), CAGE_BEAM)
            # Side panel door-bar V-truss and 3-hole gusset plate (matching reference image1.jpg.png and markup 12:24)
            F.tube((px, RAIL_START_Y, CAGE_Z), (px, TRUSS_Y, zt), CAGE_BEAM)
            F.tube((px, TRUSS_Y, zt), (px, RAIL_END_Y, CAGE_Z), CAGE_BEAM)
            F.tube((px, TRUSS_Y, CAGE_Z), (px, TRUSS_Y, zt), CAGE_BEAM)
            # 3-hole side door gusset plate along the lower rail at TRUSS_Y
            g_plate = cq.Workplane('YZ', origin=(px - 2.0, 0, 0)).polyline([
                (TRUSS_Y - 26.0, CAGE_Z), (TRUSS_Y - 26.0, CAGE_Z + 14.0),
                (TRUSS_Y, CAGE_Z + 9.0), (TRUSS_Y + 26.0, CAGE_Z + 14.0),
                (TRUSS_Y + 26.0, CAGE_Z)
            ]).close().extrude(4.0).val()
            F.solids.append(g_plate)
            for hy, hz in ((TRUSS_Y - 16.0, CAGE_Z + 6.5), (TRUSS_Y, CAGE_Z + 4.5), (TRUSS_Y + 16.0, CAGE_Z + 6.5)):
                F.holes.append(cq.Solid.makeCylinder(2.5, 12.0, cq.Vector(px - 6.0, hy, hz), cq.Vector(1, 0, 0)))
    if upper:   # cross tubes between the upper rails at the uprights: under the belt skin and above the componentry
        for y in (RAIL_START_Y, RAIL_END_Y):
            zu = round(_interp(upper, y), 1)
            F.tube((-CAGE_RAIL_X, y, zu), (CAGE_RAIL_X, y, zu), CAGE_BEAM)
    F.tube((-FRONT_LEG_X, front_y, round(zft, 1)), (FRONT_LEG_X, front_y, round(zft, 1)), CAGE_BEAM)   # front hoop top crossbar (carries front magnet boss)
    F.tube((-FRONT_LEG_X, y_bump, zft), (FRONT_LEG_X, y_bump, zft), CAGE_BEAM)            # crash bumper tube
    if nodes and upper:
        n = nodes
        def inb(p): return (max(0.0, p[0] - PILLAR_IN), p[1], p[2] - PILLAR_D / 2)
        a0, b1, r_n = inb(n['roof0']), inb(n['roof2']), inb(n['roofN'])
        # Roof V-diagonals meeting at the front roof header midpoint (matching reference image1.jpg.png)
        roof_mid_front = (0.0, a0[1], a0[2])
        if cabin:
            # Open cockpit: b1 (traced roof node, PILLAR_IN inboard) stays the anchor of the tail frame, so the tail tubes, the shock clevis
            # nodes and the tail housing fit are unchanged; the cabin frame is new, on the old canopy outline, and ties into b1.
            K, A, B = cabin_nodes(cabin)
            if TAIL_ANCHOR_ON_ROOF:   # roof peak, SCX30 one-node rule (November 27): the tail anchor sat 9.4 mm from the roof rear node B on a short 7 mm stub
                b1 = B                # (two busy hulls: 19 edges < 0.5 mm per side); the tail tubes now start at B, which does not move
            print('cage (open cockpit): cowl corner', K, 'roof front', A, 'roof rear', B, 'tail anchor', b1)
        else:
            # Short roof spine from B-pillar header crossbar to the flush rear magnet boss under the Canopy roof
            F.tube((0.0, b1[1], round(zrt, 1)), (0.0, rear_y, round(zrt, 1)), PILLAR_D)
            F.tube((0.0, b1[1], b1[2]), (0.0, b1[1], round(zrt, 1)), PILLAR_D)
        QD = PILLAR_D     # rear quarter tubes: main tube size. They were CABIN_BEAM (7) with the open cockpit, but they carry the tail frame: the middle tail
        # rail ends on them and the rear shock's 135 N comes down through it (FEM: safety 1.39 at the tail joints, 1.60 at the B-pillar foot)
        for sx in (-1, 1):
            f = lambda p: (sx * p[0], p[1], p[2])
            ze = round(_interp(upper, RAIL_END_Y), 1)
            zs = round(_interp(upper, RAIL_START_Y), 1)
            b_base = (CAGE_RAIL_X, RAIL_END_Y, ze)
            if cabin:
                u_s = (CAGE_RAIL_X, RAIL_START_Y, zs)
                b_in = b_base                  # rear quarter front node = B-pillar foot on the upper belt
                for a, b, d in [((FRONT_LEG_X, front_y, round(zft, 1)), K, CAGE_BEAM),   # front hoop top out to the cowl corner (load path into the A pillar)
                                (tuple(round((FRONT_LEG_X, front_y, round(zft, 1))[i_] * 0.5 + K[i_] * 0.5, 1) for i_ in range(3)), (CAGE_RAIL_X, RAIL_START_Y, 112.0), CAGE_BEAM),   # brace from the middle of the hoop-to-cowl tube back to the front upright at z 112 (above the tie rods' highest travel, z 100; landing it on the upper belt node instead was worse, FEM 1.13):
                                ((CAGE_RAIL_X, RAIL_START_Y, 112.0), (CAGE_RAIL_X, RAIL_START_Y + 32.0, CAGE_Z), CAGE_BEAM),      # tie from the brace's landing point down and back to the lower rail, so the brace does not bend the upright (FEM 1.61 there without it)
                                # (the hoop has no legs of its own: FEM 5.7 mm at the bumper without the brace; it passes outboard of the wishbones' travel)
                                (K, u_s, CABIN_BEAM),                                       # sill step: cowl corner back to the upper belt
                                (K, A, CABIN_BEAM),                                         # A pillar on the old canopy A-pillar line
                                (A, B, CABIN_BEAM),                                         # roof side rail on the old roof edge
                                (b_base, B, CABIN_BEAM),                                    # B pillar
                                (K, B, CABIN_BEAM),                                         # door diagonal: low front belt node to the B-pillar top
                                (B, b1, CABIN_BEAM)]:                                       # B-pillar top into the tail frame anchor
                    F.tube(f(a), f(b), d)
                F.boss(f((CAGE_RAIL_X, RAIL_END_Y, round(_interp(belt, RAIL_END_Y) - FS_BOSS_DROP, 1))), sx, 3.0)   # Front shell screw boss (the canopy bosses are gone)
            else:
                F.tube(f(b1), roof_mid_front, PILLAR_D)
                b_in = (b1[0], RAIL_END_Y, ze)     # align inboard B-pillar root with b1[0] so rear-quarter and B-pillar tubes never cross mid-span
                for a, b in ([((FRONT_LEG_X, front_y, round(zft, 1)), a0),              # outer A pillar
                              ((CAGE_RAIL_X, RAIL_START_Y, zs), a0)] +                  # inner A-pillar triangulation strut from belt corner to roof0
                             [(b_base, b_in), (b_in, b1),                               # B pillar
                              (a0, inb(n['roof1'])), (inb(n['roof1']), b1)]):           # roof side rail (removed obsolete mid-cabin bridge diagonals)
                    F.tube(f(a), f(b), PILLAR_D)
                for p, reach in [(a0, PILLAR_IN - 2.0), (b1, PILLAR_IN - 2.0), (b_in, PILLAR_IN - 2.0)]: F.boss(f(p), sx, reach)
            if tail:
                end=tail
                start=(b1[0], RAIL_END_Y, n['belt930'][2])
                def at_y(a,b,y):
                    t=(y-a[1])/(b[1]-a[1])
                    return tuple(round(a[i]+t*(b[i]-a[i]), 1) for i in range(3))
                if LOWER_TAIL_BRACE:   # Rear quarter cover outline + lower tail tube to tail node (markup 10:15, 12:24 & 12:55)
                    # Node n_cov is b_in = (b1[0], RAIL_END_Y, ze), so B-pillar (b_in -> b1) is the vertical front edge of the rear quarter
                    n_cov = b_in
                    _, mid_q, n_tip = tail_tube_starts(b1, end)
                    # 1. Upper and mid-tail tubes to end
                    F.tube(f(mid_q), f(end), PILLAR_D)
                    F.tube(f(b1), f(end), PILLAR_D)
                    # 2. Rear-quarter sloping top edge from B-pillar roof top (b1) through mid_q to rear tip (n_tip), following Canopy slope
                    F.tube(f(b1), f(mid_q), QD)
                    F.tube(f(mid_q), f(n_tip), QD)
                    # 3. Rear-quarter bottom edge from n_cov to n_tip, then rising along the lower tail line to the tail node (end)
                    F.tube(f(n_cov), f(n_tip), QD)
                    F.tube(f(n_tip), f(end), PILLAR_D)
                    # 4. Internal diagonal strut from n_cov up to mid_q (markup 12:24)
                    F.tube(f(n_cov), f(mid_q), QD)
                    # 5. Tail-to-foot tie (November 26): the rear shock's 135 N reached the feet only round the cabin (FEM, shock alone: 1.42 at the roof
                    # corner and the B-pillar foot); from the rear quarter's bottom rear node down and forward to the rail end node over the y 38 foot
                    if TAIL_FOOT_TIE:
                        F.tube(f(n_tip), f((CAGE_RAIL_X, RAIL_END_Y, CAGE_Z)), PILLAR_D)
                else:
                    F.tube(f(b_in),f(start),PILLAR_D)
                    F.tube(f(start),f(end),PILLAR_D)
                    F.tube(f(b1),f(end),PILLAR_D)
                if tie:
                    from parts.util import hull
                    ty, tz = tie
                    y_f, y_r = round(ty - PIN_FAN, 1), round(ty + PIN_FAN, 1)
                    p_f = at_y(b1, end, y_f)
                    p_top = at_y(b1, end, ty)
                    p_r = at_y(b1, end, y_r)
                    p_mid = at_y(mid_q, end, ty) if LOWER_TAIL_BRACE else at_y(start, end, ty)
                    # Overhead ladder bridge at the upper tail rail plane (z ~ 187..192 mm, above the shock eye at tz = 180.2 mm)
                    # so the lateral corridor along the shock pin axis (y = ty, z = tz) is 100% open on both sides for bolt/nut access.
                    # Diagonal brace from the lower tail rail (p_mid) up to the front/rear overhead cross-tubes (at x = BRACE_TOP_X, on the ear outer face, clear of the pin axis)
                    # each brace stands in its own plane y = y_f / y_r (nodes straight under the overhead nodes), so nothing crosses the pin corridor
                    _lo = mid_q if LOWER_TAIL_BRACE else start
                    F.tube(f(at_y(_lo, end, y_f)), f((BRACE_TOP_X, p_f[1], p_f[2])), PILLAR_D)
                    F.tube(f(at_y(_lo, end, y_r)), f((BRACE_TOP_X, p_r[1], p_r[2])), PILLAR_D)
                    if LOWER_TAIL_BRACE:   # web under the front brace: middle tail rail down to the lower tail rail, so the brace does not bend the middle rail
                        F.tube(f(at_y(mid_q, end, y_f)), f(at_y(n_tip, end, y_f)), PILLAR_D)
                        # diagonal of the bay before the web (November 26): rear quarter bottom node up to the web top, so the brace's lift goes
                        # straight to n_tip and the tail-to-foot tie instead of bending the lower tail rail (FEM, shock alone: 2.04 there without it)
                        if TAIL_FOOT_TIE:
                            F.tube(f(n_tip), f(at_y(mid_q, end, y_f)), PILLAR_D)
                    # Clevis ear: one plate per side, |x| 4.4 .. EAR_OUT_X, a convex hull from the pin lug up into the two overhead cross tubes
                    # (it ends on their centre lines, full tube height). It replaces a tube between the cross tubes at x 7.4 that was wider than the
                    # ear on both sides and had to be shaved by the eye slot and by a head clearance box: those cuts left feather edges of 0.2 to
                    # 0.5 mm on the tube and nicked the upper tail tube. Only the pin boss (r 6.8 to |x| 12, under the M6 head and the nut)
                    # stands outboard of the plate; a 17 mm tool cylinder on the pin axis is free out to |x| 27.7, where the tail tube joint begins
                    # (a corridor cut out to |x| 30, square or round, leaves feather edges on the tail tubes).
                    x0, x1 = sorted((sx * EAR_IN_X, sx * EAR_OUT_X))
                    hh = _half(PILLAR_D)
                    ear_cyl = cq.Solid.makeCylinder(9.0, x1 - x0, cq.Vector(x0, ty, tz), cq.Vector(1, 0, 0))
                    ear_boss = cq.Solid.makeCylinder(6.8, 12.0 - EAR_IN_X, cq.Vector(min(sx * EAR_IN_X, sx * 12.0), ty, tz), cq.Vector(1, 0, 0))
                    ear_web = hull([(x, y, z) for x in (x0, x1) for y, z in (
                        (ty - 9.0, tz), (ty + 9.0, tz), (p_f[1] + hh, p_f[2] - hh - EAR_ROOT_DROP), (p_f[1], p_f[2] - hh), (p_f[1], p_f[2] + hh), (p_r[1], p_r[2] - hh), (p_r[1], p_r[2] + hh))])
                    F.solids.append(ear_cyl.fuse(ear_boss).fuse(ear_web))
                    if sx == 1:
                        F.tube((-p_f[0], p_f[1], p_f[2]), (p_f[0], p_f[1], p_f[2]), PILLAR_D)
                        F.tube((-p_r[0], p_r[1], p_r[2]), (p_r[0], p_r[1], p_r[2]), PILLAR_D)
                        if EAR_BRIDGES:   # cage rear attempt 2 (November 26): the two ears joined across the slot, ahead of and behind the shock eye
                            # (FEM at 273 N: ear root 1.39..1.63 and the rear cross tube between the ears 1.62 bent as two loose plates). Each web is the
                            # hull of the cross tube's centre section and a chord 9.5 mm from the pin, so the eye (r 7) turns free and the damper body
                            # (r 9, from 10.5 mm under the eye, down and aft) stays clear; every point lies inside the ear outline (no step at the ear face).
                            import math
                            for (py, pz), up, lo in ((p_f[1:], 4.0, -3.0), (p_r[1:], 4.5, 1.0)):
                                dy, dz = py - ty, pz - tz; L = math.hypot(dy, dz); dy, dz = dy / L, dz / L
                                ny, nz = (-dz, dy) if dy > 0 else (dz, -dy)       # normal pointing up
                                pts = [(ty + 9.5 * dy + k * ny, tz + 9.5 * dz + k * nz) for k in (lo, up)] + [(py, pz - hh), (py, pz + hh)]
                                F.solids.append(hull([(x, y, z) for x in (-EAR_IN_X - 1.0, EAR_IN_X + 1.0) for y, z in pts]))
                        # Through-bore (D6.4 mm) all the way through both clevis ears and outer hardware bosses
                        F.holes.append(cq.Solid.makeCylinder(3.2, 40.0, cq.Vector(-20.0, ty, tz), cq.Vector(1, 0, 0)))
            # supports under the rear shell hump, above the rear tire
            prev = (REAR_LEG_X, rear_y, zrt)
            for y, z in (supports or []):
                pt = (REAR_SUP_X, y, z); F.tube(f(prev), f(pt), PILLAR_D); prev = pt; F.boss(f(pt), sx, 3.0)
            if tie and supports:
                # shock top mount carried by the tube frame, no separate tower: the pin node is held by a tie to the first rear support
                # and by a brace down and forward to the rear bridge corner (the shock pushes the pin up and forward, the brace takes it in tension)
                y0, z0 = supports[0]; ty, tz = tie
                print('cage tie: support0 (y %.1f z %.1f) pin (y %.1f z %.1f) leg (y %.1f z %.1f) REAR_SUP_X %.1f LEG_X %.1f' % (y0, z0, ty, tz, rear_y, zrt, REAR_SUP_X, REAR_LEG_X))
                # the ties land on the clevis web 14 mm above the pin axis (not on the axis), so the bolt head and nut have a free tool cylinder
                F.tube(f((REAR_SUP_X, y0, z0)), f((9.5, ty, tz + PIN_TIE_RISE)), PILLAR_D)
                F.tube(f((9.5, ty, tz + PIN_TIE_RISE)), f((REAR_LEG_X, rear_y, zrt)), CAGE_BEAM)
                if sx == 1: F.holes.append(cq.Solid.makeCylinder(3.2, 30.0, cq.Vector(-15.0, ty, tz), cq.Vector(1, 0, 0)))   # M6 pin through both pin nodes
        if cabin:
            m = lambda p: (-p[0], p[1], p[2])
            X0 = (0.0, round((A[1] + B[1]) / 2, 1), round((A[2] + B[2]) / 2, 1))      # roof X: both diagonals meet at one node on the centre line
            C0 = (0.0, K[1], K[2])                                                    # cowl centre node: root of the windshield V
            for a, b in [(m(K), C0), (C0, K),                                         # cowl bar along the front edge of the cabin opening
                         (C0, A), (C0, m(A)),                                         # windshield V up to the roof front corners
                         (m(A), A), (m(B), B),                                        # front and rear roof headers
                         (A, X0), (X0, m(B)), (m(A), X0), (X0, B)]:                   # roof X
                F.tube(a, b, CABIN_BEAM)
        else:
            for k in ('roof0', 'roof2'):
                p = inb(n[k]); F.tube((-p[0], p[1], p[2]), (p[0], p[1], p[2]), PILLAR_D)
        if supports and len(supports) > 1:
            y, z = supports[1]; F.tube((-REAR_SUP_X, y, z), (REAR_SUP_X, y, z), PILLAR_D)
        if tail:
            x,y,z=tail
            F.tube((-x,y,z),(x,y,z),PILLAR_D)
            for stub, pocket in (tail_screws or []):      # M3 insert stubs on the rear cross tube for the tail housing screws
                F.solids.append(stub); F.holes.append(pocket)
    cage = F.build()
    _report_crossings(F.segs)      # after the joints are resolved: crossings left over (tubes passing through each other without a node)
    return cage, zf, zr
