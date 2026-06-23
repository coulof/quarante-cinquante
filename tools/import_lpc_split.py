#!/usr/bin/env python3
"""Import a SPLIT-by-animation LPC export into a game SpriteFrames .tres.

The generator's "split by animation" export gives one PNG per animation:
  <variant>/standard/*.png  -> 64px frames, 4 directions, padded to 13 cols
  <variant>/custom/*.png    -> oversize attacks (slash_128, slash_oversize, tool_whip)

This is cleaner than slicing the giant universal sheet: each animation is its own
correctly-sized grid, so the oversize whip/glowsword "just work". We slice the
EAST-facing row (up/left/down/right -> row 3) of each into idle/run/attack/hurt/dead
and write resources/sprite_frames/<name>_frames.tres, copying the PNGs it needs into
assets/sprites/<name>/.

    python3 tools/import_lpc_split.py --dir assets/sprites/lpc_src/hero_whip \
        --name hero_whip --attack custom/tool_whip.png
    # base hero (bare-handed, slash attack):
    python3 tools/import_lpc_split.py --dir assets/sprites/lpc_src/hero \
        --name hero --attack standard/slash.png
    godot --headless --import

LPC art is CC-BY-SA 3.0 / GPL — keep each variant's credits/ in CREDITS.md.
"""
import argparse
import os
import shutil
import sys

from PIL import Image

DIRS = 4          # up, left, down, right
EAST = 3          # right-facing row; engine flip_h handles left
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(PROJECT_ROOT, "assets", "sprites")
FRAMES_DIR = os.path.join(PROJECT_ROOT, "resources", "sprite_frames")


def slice_row(path, single_dir, max_frames=None):
    """Return (frame_size, y, n_frames) for the east row, auto-detecting the real
    frame count (standard files are right-padded with transparent cells)."""
    im = Image.open(path).convert("RGBA")
    w, h = im.size
    if single_dir:
        fs, y = h, 0
    else:
        fs, y = h // DIRS, EAST * (h // DIRS)
    cols = w // fs
    n = 0
    for c in range(cols):
        if im.crop((c * fs, y, c * fs + fs, y + fs)).getbbox() is None:
            break  # first fully-transparent cell = end of the real animation
        n += 1
    if max_frames is not None:
        n = min(n, max_frames)
    return fs, y, max(n, 1)


def main():
    ap = argparse.ArgumentParser(description="Import a split-by-animation LPC export.")
    ap.add_argument("--dir", required=True, help="variant folder (has standard/ + custom/)")
    ap.add_argument("--name", required=True, help="output name, e.g. hero / hero_whip / zombie")
    ap.add_argument("--attack", default="standard/slash.png",
                    help="attack PNG relative to --dir (e.g. custom/tool_whip.png)")
    ap.add_argument("--from-walk", action="store_true",
                    help="source idle/run from walk.png (for bodies like Skeleton that have "
                         "no idle/run anims — otherwise those frames show only the head)")
    args = ap.parse_args()

    src = os.path.join(PROJECT_ROOT, args.dir) if not os.path.isabs(args.dir) else args.dir
    if not os.path.isdir(src):
        ap.error(f"not a folder: {src}")

    # Some bodies (e.g. Skeleton) have no idle/run animations, so those export files
    # contain only the head — fall back to the walk cycle for locomotion.
    idle_src = "standard/walk.png" if args.from_walk else "standard/idle.png"
    run_src = "standard/walk.png" if args.from_walk else "standard/run.png"
    idle_max = 2 if args.from_walk else None

    # (anim, source rel path, single_dir, max_frames, speed, loop)
    plan = [
        ("idle",   idle_src,            False, idle_max, 5.0,  True),
        ("run",    run_src,             False, None,     12.0, True),
        ("attack", args.attack,         False, None,     13.0, False),
        ("hurt",   "standard/hurt.png", True,  3,        8.0,  False),
        ("dead",   "standard/hurt.png", True,  None,     8.0,  False),
    ]

    out_dir = os.path.join(SPRITES_DIR, args.name)
    os.makedirs(out_dir, exist_ok=True)
    os.makedirs(FRAMES_DIR, exist_ok=True)

    # Copy each distinct source PNG into assets/sprites/<name>/ and record its res:// path.
    textures = {}   # src rel -> (ext_id, res_path)
    anim_specs = []  # (anim, ext_id, fs, y, n, speed, loop)
    for anim, rel, single, maxf, speed, loop in plan:
        srcfile = os.path.join(src, rel)
        if not os.path.isfile(srcfile):
            print(f"  ! missing {rel} — skipping {anim}", file=sys.stderr)
            continue
        if rel not in textures:
            dest_name = os.path.basename(rel)
            shutil.copyfile(srcfile, os.path.join(out_dir, dest_name))
            textures[rel] = (f"t{len(textures)}", f"res://assets/sprites/{args.name}/{dest_name}")
        ext_id, _ = textures[rel]
        fs, y, n = slice_row(srcfile, single, maxf)
        anim_specs.append((anim, ext_id, fs, y, n, speed, loop))
        print(f"  {anim:7s} <- {rel:28s} {n} frames @ {fs}px (y={y})")

    # Emit the .tres (multiple ext textures, one AtlasTexture per frame).
    subs = []  # (sub_id, ext_id, x, y, fs)
    entries = []
    for anim, ext_id, fs, y, n, speed, loop in anim_specs:
        ids = []
        for i in range(n):
            sid = f"{anim}_{i}"
            subs.append((sid, ext_id, i * fs, y, fs))
            ids.append(sid)
        entries.append((anim, ids, speed, loop))

    load_steps = len(textures) + len(subs) + 1
    out = [f'[gd_resource type="SpriteFrames" load_steps={load_steps} format=3]', ""]
    for rel, (ext_id, res_path) in textures.items():
        out.append(f'[ext_resource type="Texture2D" path="{res_path}" id="{ext_id}"]')
    out.append("")
    for sid, ext_id, x, y, fs in subs:
        out.append(f'[sub_resource type="AtlasTexture" id="{sid}"]')
        out.append(f'atlas = ExtResource("{ext_id}")')
        out.append(f'region = Rect2({x}, {y}, {fs}, {fs})')
        out.append("")
    out.append("[resource]")
    blocks = []
    for anim, ids, speed, loop in entries:
        frames = ", ".join('{\n"duration": 1.0,\n"texture": SubResource("%s")\n}' % i for i in ids)
        blocks.append('{\n"frames": [%s],\n"loop": %s,\n"name": &"%s",\n"speed": %s\n}'
                      % (frames, "true" if loop else "false", anim, speed))
    out.append("animations = [" + ", ".join(blocks) + "]")

    tres = os.path.join(FRAMES_DIR, f"{args.name}_frames.tres")
    with open(tres, "w") as f:
        f.write("\n".join(out) + "\n")
    print(f"  wrote {os.path.relpath(tres, PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
