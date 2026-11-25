"""Bambu Studio project 3MFs for a printed kit: one file per plate plus one file holding every plate, with per-part settings.

    python bambu_kit.py kit.json [--check]

kit.json (paths relative to the manifest):
{
  "profile": "my_saved_P2S_project.3mf",      a project the user saved in Bambu Studio for this printer (or its extracted project_settings.config)
  "out": "print/bambu",
  "bed": [256, 256], "margin": 5, "gap": 10,   gap 10: brims and tree supports of neighbours need it (3-6 mm gave path conflicts)
  "filament_slot": 3,                          AMS slot of the PLA in that project (1-based)
  "process": {"wall_generator": "arachne"},    optional global overrides on top of the profile
  "supports": "easy_peel",                     easy_peel (default) | none: per-object support preset for parts that need support
  "plates": [
    {"name": "01_frame", "title": "Plate 1 - frame",
     "parts": [{"stl": "stl/FR1_rail.stl", "name": "FR1_rail_L", "qty": 1, "walls": 6, "infill": "40%", "pattern": "gyroid",
                "support": "auto", "brim": 3, "slot": 3}]}
  ]
}
STLs must already be oriented for printing (z up). support: auto (on when overhang > 50 mm2 or a floating region exists), on, off.
Parts that do not fit one plate spill onto <name>_2, <name>_3... --check slices every plate file with the Bambu Studio CLI and exits 1
on floating regions, path conflicts or a failed slice; it writes slice_check.json with time and grams per plate.
"""
import os, sys, json, glob, math, uuid, zipfile, subprocess, tempfile
import numpy as np
import trimesh

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from mesh_audit import overhang, floating            # noqa: E402

STUDIO = "/Applications/BambuStudio.app/Contents/MacOS/BambuStudio"
SUPPORT_MM2 = 15.0
EASY_PEEL = dict(enable_support="1", support_type="tree(auto)", support_style="default", support_on_build_plate_only="1", support_threshold_angle="30",
                 support_top_z_distance="0.2", support_bottom_z_distance="0.2", support_object_xy_distance="0.5", support_interface_top_layers="2",
                 support_interface_bottom_layers="0", support_interface_spacing="0.5", support_interface_pattern="rectilinear",
                 support_object_first_layer_gap="0.2", tree_support_branch_diameter="2")
GLOBAL = dict(enable_support="0", wall_generator="arachne", elefant_foot_compensation="0.15", seam_position="aligned", brim_type="auto_brim")


def load_profile(path):
    if path.endswith(".3mf"):
        return json.loads(zipfile.ZipFile(path).read("Metadata/project_settings.config"))
    return json.load(open(path))


def shelf_pack(items, bw, bh, margin, gap):
    """items [(key, w, h)] -> plates [[(key, x, y)]]: tallest first, shelves left to right."""
    plates = []
    for k, w, h in sorted(items, key=lambda r: (-r[2], -r[1])):
        if w > bw - 2 * margin or h > bh - 2 * margin:
            if h <= bw - 2 * margin and w <= bh - 2 * margin:
                raise ValueError(f"{k}: rotate it 90 deg in the STL (it fits only turned)")
            raise ValueError(f"{k}: {w:.0f} x {h:.0f} mm does not fit the bed")
        done = False
        for pl in plates:
            for sh in pl["shelves"]:
                if sh["x"] + w <= bw - 2 * margin and h <= sh["h"]:
                    pl["items"].append((k, margin + sh["x"], margin + sh["y"])); sh["x"] += w + gap; done = True
                    break
            if done:
                break
            y = pl["shelves"][-1]["y"] + pl["shelves"][-1]["h"] + gap
            if y + h <= bh - 2 * margin:
                pl["shelves"].append(dict(x=w + gap, y=y, h=h)); pl["items"].append((k, margin, margin + y)); done = True
                break
        if not done:
            plates.append(dict(items=[(k, margin, margin)], shelves=[dict(x=w + gap, y=0.0, h=h)]))
    return [p["items"] for p in plates]


def plate_origins(n, bw, bh):
    v = math.sqrt(n)
    cols = int(round(v) + 1 if v > round(v) else round(v))
    return [((i % cols) * bw * 1.2, -(i // cols) * bh * 1.2) for i in range(n)]


def obj_settings(p, m, cfg):
    s = {"wall_loops": str(p["walls"])} if "walls" in p else {}
    if "infill" in p:
        s["sparse_infill_density"] = str(p["infill"]).replace(" ", "")
    if "pattern" in p:
        s["sparse_infill_pattern"] = p["pattern"]
    sup = p.get("support", "auto")
    if sup == "on" or (sup == "auto" and (overhang(m) > SUPPORT_MM2 or floating(m) > 0.02)):
        s.update(EASY_PEEL if cfg.get("supports", "easy_peel") == "easy_peel" else dict(enable_support="1", support_type="tree(auto)", support_on_build_plate_only="1"))
    if p.get("brim"):
        s.update(brim_type="outer_only", brim_width=str(p["brim"]))
    return s


def write_project(fn, plates, profile, cfg):
    """plates: [(title, [(label, part_cfg, mesh placed on the bed)])]."""
    bw, bh = cfg.get("bed", [256, 256])
    hdr = ('<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
           'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p">\n')
    objs, mcfg, pcfg, oid = [], [], [], 0
    for n_pl, ((title, items), (ox, oy)) in enumerate(zip(plates, plate_origins(len(plates), bw, bh)), start=1):
        inst = []
        for label, p, m in items:
            oid += 1
            c = (m.bounds[0] + m.bounds[1]) / 2
            objs.append((oid, m.vertices - c, m.faces, (c[0] + ox, c[1] + oy, c[2])))
            meta = "".join(f'\n    <metadata key="{k}" value="{v}"/>' for k, v in obj_settings(p, m, cfg).items())
            mcfg.append(f'  <object id="{2 * oid}">\n    <metadata key="name" value="{label}"/>\n    <metadata key="extruder" value="{p.get("slot", cfg.get("filament_slot", 1))}"/>{meta}\n'
                        f'    <part id="1" subtype="normal_part">\n      <metadata key="name" value="{label}"/>\n'
                        f'      <metadata key="matrix" value="1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"/>\n    </part>\n  </object>\n')
            inst.append(f'    <model_instance>\n      <metadata key="object_id" value="{2 * oid}"/>\n      <metadata key="instance_id" value="0"/>\n'
                        f'      <metadata key="identify_id" value="{100 + oid}"/>\n    </model_instance>\n')
        pcfg.append(f'  <plate>\n    <metadata key="plater_id" value="{n_pl}"/>\n    <metadata key="plater_name" value="{title}"/>\n'
                    f'    <metadata key="locked" value="false"/>\n' + "".join(inst) + "  </plate>\n")
    res, build = [], []
    with zipfile.ZipFile(fn, "w", zipfile.ZIP_DEFLATED) as z:
        for oid, V, F, (tx, ty, tz) in objs:
            v = "".join(f'<vertex x="{a:.4f}" y="{b:.4f}" z="{c:.4f}"/>' for a, b, c in V)
            t = "".join(f'<triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in F)
            z.writestr(f"3D/Objects/object_{oid}.model", hdr + ' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n'
                       f'  <object id="{2 * oid - 1}" p:UUID="{uuid.uuid4()}" type="model"><mesh><vertices>{v}</vertices><triangles>{t}</triangles></mesh></object>\n'
                       ' </resources>\n <build/>\n</model>\n')
            res.append(f'  <object id="{2 * oid}" p:UUID="{uuid.uuid4()}" type="model"><components><component p:path="/3D/Objects/object_{oid}.model" '
                       f'objectid="{2 * oid - 1}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 0 0 0"/></components></object>\n')
            build.append(f'  <item objectid="{2 * oid}" p:UUID="{uuid.uuid4()}" transform="1 0 0 0 1 0 0 0 1 {tx:.4f} {ty:.4f} {tz:.4f}" printable="1"/>\n')
        ver = profile.get("version", "02.08.03.66")
        z.writestr("3D/3dmodel.model", hdr + f' <metadata name="Application">BambuStudio-{ver}</metadata>\n <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
                   f' <metadata name="Title">{cfg.get("title", "kit")}</metadata>\n <resources>\n' + "".join(res) + f' </resources>\n <build p:UUID="{uuid.uuid4()}">\n'
                   + "".join(build) + " </build>\n</model>\n")
        z.writestr("3D/_rels/3dmodel.model.rels", '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                   + "".join(f' <Relationship Target="/3D/Objects/object_{o[0]}.model" Id="rel-{o[0]}" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n' for o in objs)
                   + "</Relationships>\n")
        z.writestr("Metadata/model_settings.config", '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + "".join(mcfg) + "".join(pcfg) + "</config>\n")
        z.writestr("Metadata/project_settings.config", json.dumps(profile, indent=4))
        z.writestr("Metadata/slice_info.config", '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n  <header>\n    <header_item key="X-BBL-Client-Type" value="slicer"/>\n'
                   f'    <header_item key="X-BBL-Client-Version" value="{ver}"/>\n  </header>\n</config>\n')
        z.writestr("[Content_Types].xml", '<?xml version="1.0" encoding="UTF-8"?>\n<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
                   ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
                   ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
                   ' <Default Extension="png" ContentType="image/png"/>\n</Types>\n')
        z.writestr("_rels/.rels", '<?xml version="1.0" encoding="UTF-8"?>\n<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
                   ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>\n')


def slice_check(fn):
    """(minutes, grams, [problems]) from the Bambu Studio CLI."""
    d = tempfile.mkdtemp()
    log = subprocess.run([STUDIO, "--debug", "2", "--slice", "0", "--outputdir", d, fn], capture_output=True, text=True, timeout=1800).stdout
    bad = sorted({l.split("warnings: ")[-1] if "warnings: " in l else l.split("] ")[-1] for l in log.splitlines()
                  if ("floating regions" in l and "object T" not in l) or "path conflicts" in l or "result conflict" in l})       # coupon tiles (T*_) float on purpose: they test bridges and overhangs
    try:
        r = json.load(open(os.path.join(d, "result.json")))
        sp = r["sliced_plates"][0]
        if r["return_code"] != 0:
            bad.append(r["error_string"])
        return sp["main_predication"] / 60.0, sum(f["total_used_g"] for f in sp["filaments"]), bad
    except Exception as e:
        return 0.0, 0.0, bad + [f"no slice result ({e})"]


def main():
    man = os.path.abspath(sys.argv[1])
    base = os.path.dirname(man)
    cfg = json.load(open(man))
    rel = lambda p: p if os.path.isabs(p) else os.path.join(base, p)
    profile = load_profile(rel(cfg["profile"]))
    profile.update(GLOBAL, **cfg.get("process", {}))
    bw, bh = cfg.get("bed", [256, 256])
    out = rel(cfg.get("out", "bambu"))
    os.makedirs(out, exist_ok=True)
    for f in glob.glob(os.path.join(out, "*.3mf")):
        os.remove(f)
    every = []
    for pl in cfg["plates"]:
        meshes = {}
        for p in pl["parts"]:
            m = trimesh.load(rel(p["stl"]))
            m.apply_translation(-m.bounds[0])
            if not m.is_watertight:
                sys.exit(f"{p['stl']}: mesh is not watertight; fix the export first")
            for c in range(p.get("qty", 1)):
                meshes[p["name"] + (f"_{c + 1}" if p.get("qty", 1) > 1 else "")] = (p, m)
        packed = shelf_pack([(k, m.extents[0], m.extents[1]) for k, (_, m) in meshes.items()], bw, bh, cfg.get("margin", 5), cfg.get("gap", 10))
        for i, items in enumerate(packed):
            name = pl["name"] + (f"_{i + 1}" if len(packed) > 1 else "")
            title = pl.get("title", name) + (f" ({i + 1}/{len(packed)})" if len(packed) > 1 else "")
            placed = [(k, meshes[k][0], meshes[k][1].copy().apply_translation((x, y, 0))) for k, x, y in items]
            write_project(os.path.join(out, f"plate_{name}.3mf"), [(title, placed)], profile, cfg)
            every.append((title, placed))
            print(f"plate_{name}.3mf  {len(placed)} parts", flush=True)
    write_project(os.path.join(out, "all_plates.3mf"), every, profile, cfg)
    print(f"all_plates.3mf  {len(every)} plates  {sum(len(i) for _, i in every)} parts")
    if "--check" in sys.argv:
        res, fails = {}, 0
        for fn in sorted(glob.glob(os.path.join(out, "plate_*.3mf"))):
            mins, g, bad = slice_check(fn)
            res[os.path.basename(fn)] = dict(minutes=round(mins), grams=round(g, 1), problems=bad)
            fails += len(bad)
            print(f"  slice {os.path.basename(fn):34s} {mins / 60:5.1f} h {g:6.1f} g  {'OK' if not bad else bad}", flush=True)
        json.dump(res, open(os.path.join(out, "slice_check.json"), "w"), indent=1)
        print(f"Bambu Studio slice check: {fails} problems; {sum(r['minutes'] for r in res.values()) / 60:.1f} h, {sum(r['grams'] for r in res.values()):.0f} g")
        sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
