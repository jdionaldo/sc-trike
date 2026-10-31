"""Builds one SolidCraft design of the assembled model (default pose) from the posed meshes, for native rendering."""
import json
from pathlib import Path

import assembly
import renders
from parts import body as body_parts
from params import P

OUT = Path("out/posed")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    body_colors = body_parts.colors(P)
    cmds, looks = [], []
    for it in assembly.scene(0.0, 0.0, lead=False, body=True):
        path = (OUT / f"{it.name}.stl").resolve()
        it.mesh.export(path)
        cmds.append({"command": "file.insert_mesh", "params": {"path": str(path)}})
        looks.append({"command": "appearance.assign", "params": {"components": [it.name],
                                                                 "color": renders.colour(it, body_colors)}})
    Path("out/commands/_scene.json").write_text(json.dumps(cmds + looks))
    print(len(cmds), "meshes")


if __name__ == "__main__":
    main()
