"""Sheet 62 crops (top, side, rear, q34) next to the zoomed renders of the build. usage: python tools_skin/compare62.py ZOOM.png OUT.png"""
import sys
from PIL import Image, ImageDraw
z = Image.open(sys.argv[1]).convert("RGB")
boxes = {"side": (0, 60, 905, 552), "top": (1020, 60, 1600, 565), "rear": (40, 640, 880, 1040), "q34": (1000, 590, 1630, 1090)}
refs = {"side": "side", "top": "top", "rear": "rear", "q34": "q34"}
H = 420
rows = []
for k in ("top", "side", "rear", "q34"):
    a = Image.open(f"out/ref62/{refs[k]}.png").convert("RGB"); b = z.crop(boxes[k])
    a = a.resize((int(a.width * H / a.height), H)); b = b.resize((int(b.width * H / b.height), H))
    row = Image.new("RGB", (a.width + b.width + 30, H + 24), "white"); row.paste(a, (0, 24)); row.paste(b, (a.width + 30, 24))
    d = ImageDraw.Draw(row); d.text((4, 4), f"{k}: sheet 62 crop (left) / build rev 14 (right)", fill="black")
    rows.append(row)
W = max(r.width for r in rows); out = Image.new("RGB", (W, sum(r.height for r in rows)), "white"); y = 0
for r in rows: out.paste(r, (0, y)); y += r.height
out.save(sys.argv[2]); print(out.size)
