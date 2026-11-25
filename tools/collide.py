"""Check the built STEP assembly, including every nested component.

Run after `soma build`: python -u tools/collide.py
All pairs: python -u tools/collide.py --all   (every pair of the assembly, not only pairs with a part in OWN_GROUPS; pairs in
WHITELIST are intended contacts, each with its reason, and are listed apart; report in renders/interference-report-all.json)
No model rerun, fake parameters, hidden frame hull, or skipped boolean failures.
"""
from pathlib import Path
import itertools
import json
import sys
from fnmatch import fnmatch
import cadquery as cq
from soma import import_assembly

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
SOURCE = ROOT / 'output/model.step'
REPORT = ROOT / ('renders/interference-report-all.json' if '--all' in sys.argv[1:] else 'renders/interference-report.json')
MIN_VOLUME = 0.01  # mm3: reject numerical contact dust only
ALL = '--all' in sys.argv[1:]
# intended contacts for --all: (pattern a, pattern b, reason); patterns are fnmatch patterns on the full part key, either order
WHITELIST = [
    ('*/mock_rear_axle', '*/mock_rear_hub', 'both are stand-ins of the bought rear hub and axle; the hub stand-in is drawn solid, the real hub has the axle bore (399.5 mm3)'),
    ('*/b_rear_ring', '*/w3_rring_hub', 'the ring gear stand-in is drawn without its bore; the overlap is the hub spigot inside that bore, a 10.8 mm disc on the ring axis (391.4 mm3)'),
    ('*/b_rear_ring', '*/b_rear_shaft', 'two bought stand-ins from the reference mesh: the ring face grazes the shaft end by 0.3 mm (3.75 mm3); gear mesh clearance is set by the bought parts'),
]


def whitelisted(a, b):
    for pa, pb, why in WHITELIST:
        if (fnmatch(a, pa) and fnmatch(b, pb)) or (fnmatch(a, pb) and fnmatch(b, pa)):
            return why
    return None


OWN_GROUPS = ('Print_shell/', 'Lights/', 'Chassis/b_steer', 'Rear_suspension/Rear_shock_bridge', 'Cage_')


def boxes_overlap(a, b):
    return all(getattr(a, axis+'max') >= getattr(b, axis+'min') and
               getattr(b, axis+'max') >= getattr(a, axis+'min') for axis in 'xyz')


def main():
    asm = import_assembly(str(SOURCE))
    parts = []
    for name, node in asm.objects.items():
        if node.obj is None:
            continue
        shape = node.obj.val() if isinstance(node.obj, cq.Workplane) else node.obj
        shape = shape.moved(node.loc)
        parts.append((name, shape, shape.BoundingBox(), name.startswith(OWN_GROUPS)))
    print(f'Checking {len(parts)} components in the built assembly', flush=True)
    hits, errors = [], []
    checked = 0
    for (an, a, ab, own_a), (bn, b, bb, own_b) in itertools.combinations(parts, 2):
        if not (ALL or own_a or own_b) or not boxes_overlap(ab, bb):
            continue
        checked += 1
        try:
            overlap = a.intersect(b)
            volume = overlap.Volume()
            if volume <= MIN_VOLUME:
                continue
            bounds = overlap.BoundingBox()
            hit = dict(a=an, b=bn, volume_mm3=round(volume, 4),
                       bounds_mm=[round(getattr(bounds, k), 3) for k in
                                  ('xmin','xmax','ymin','ymax','zmin','zmax')])
            why = whitelisted(an, bn) if ALL else None
            if why:
                hit['whitelisted'] = why
            hits.append(hit)
            print(f'{volume:.3f} mm3: {an} <> {bn}' + (f'  [whitelisted: {why}]' if why else '') +
                  ('  bbox ' + ' '.join(f'{v:.1f}' for v in hit['bounds_mm']) if ALL else ''), flush=True)
        except Exception as exc:
            errors.append(dict(a=an, b=bn, error=str(exc)))
            print(f'FAILED: {an} <> {bn}: {exc}', flush=True)
    hits.sort(key=lambda h: h['volume_mm3'], reverse=True)
    report = dict(step=str(SOURCE.relative_to(ROOT)), source_mtime=SOURCE.stat().st_mtime,
                  components=len(parts), boolean_pairs=checked,
                  overlap_threshold_mm3=MIN_VOLUME, overlaps=hits, errors=errors,
                  limits='Static ride-position geometry; intended mounting overlaps require review. '
                         'Imported mock wheels and other low-detail donor components remain approximations.')
    REPORT.parent.mkdir(exist_ok=True)
    REPORT.write_text(json.dumps(report, indent=2)+'\n')
    if ALL:
        nw = sum(1 for h in hits if h.get('whitelisted'))
        print(f'all-pairs mode, threshold {MIN_VOLUME} mm3: {len(hits) - nw} real overlaps, {nw} whitelisted contacts', flush=True)
    print(f'{len(hits)} overlapping pairs; {len(errors)} failed checks. Report: {REPORT}', flush=True)
    if errors:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
