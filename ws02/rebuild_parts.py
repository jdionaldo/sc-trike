"""Rebuild chosen WS-03 printed parts into out/stl: python rebuild_parts.py w3_frame_front w3_frame_rear [...]  (no args: every part)"""
import sys
import build
import w3_parts
names = sys.argv[1:]
for p in w3_parts.all_parts():
    if names and p.name not in names:
        continue
    build.run_part(p)
    print("built", p.name, flush=True)
