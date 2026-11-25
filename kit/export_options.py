"""Printed options that are not in the default model (run with the SOMA python from the project folder, after `soma export`):
the printed tie rods (kit ST3, option to the steel M3 turnbuckles) as STLs next to the exported parts, with the same edge break as the model's moving parts.
  python kit/export_options.py kit/stl_export_wishbone"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import cadquery as cq
from parts import wishbone as wb
from parts.util import chamfer_moving
out = sys.argv[1]
for s in (1, -1):
    r = chamfer_moving(wb.printed_tie_rod(s), 'printed tie rod %d' % s)
    cq.exporters.export(r, os.path.join(out, 'Tie_rod_printed_%d.stl' % s), tolerance=0.01, angularTolerance=0.1)
    print('Tie_rod_printed_%d.stl' % s, round(r.Volume(), 1), 'mm3')
