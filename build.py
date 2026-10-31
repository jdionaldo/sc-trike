"""Runs every part's command list through solidcraft-cli, exporting STL and STEP."""
import importlib
import json
import subprocess
import sys
from pathlib import Path

from params import P

OUT = Path("out")
MODULES = ["parts.hubs", "parts.lean_linkage", "parts.swingarm", "parts.chassis", "parts.mounts", "parts.wheels", "parts.body"]


def all_parts():
    parts = []
    for m in MODULES:
        try:
            mod = importlib.import_module(m)
        except ModuleNotFoundError as e:
            if e.name == m:
                continue
            raise
        parts.extend(mod.build(P))
    return parts


def run_part(part):
    for d in ("commands", "stl", "step"):
        (OUT / d).mkdir(parents=True, exist_ok=True)
    script = OUT / "commands" / f"{part.name}.json"
    script.write_text(json.dumps(part.cmds, indent=1))
    r = subprocess.run(["solidcraft-cli", "run", str(script), "--out", str(OUT / "stl" / f"{part.name}.stl"),
                        "--out", str(OUT / "step" / f"{part.name}.step")], capture_output=True, text=True)
    if r.returncode:
        raise RuntimeError(f"{part.name}: {r.stderr.strip()[-600:]}")


def main(names=None):
    parts = all_parts()
    for part in parts:
        if names and part.name not in names:
            continue
        run_part(part)
        print("built", part.name)
    return parts


if __name__ == "__main__":
    main(sys.argv[1:] or None)
