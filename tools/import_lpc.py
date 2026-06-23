#!/usr/bin/env python3
"""Import a Universal LPC spritesheet into the game's SpriteFrames format.

Use the generator at
https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator
to compose a character, then **Download** the sheet (keep the standard/"universal"
animations enabled — see notes below) and run:

    python3 tools/import_lpc.py --sheet ~/Downloads/hero.png --name hero --kind hero
    python3 tools/import_lpc.py --sheet ~/Downloads/zomb.png --name zombie --kind enemy
    godot --headless --import

This copies the sheet to assets/sprites/<name>.png and writes
resources/sprite_frames/<name>_frames.tres referencing it — so the existing
hero/enemy scenes pick up the new art with no scene edits to the texture path.

LICENSING: LPC art is CC-BY-SA 3.0 / GPL 3.0 (NOT CC0). Keep the per-layer credits
the generator gives you on export and add them to CREDITS.md.

------------------------------------------------------------------------------
LPC universal layout (this is what we slice). Frames are 64x64. The classic
animation blocks always sit at the TOP of the sheet in this fixed order, each
spanning 4 direction rows (up, left, down, right); hurt/death is a single row:

    block      base_row  frames   (east/right row = base_row + 3)
    spellcast     0         7
    thrust        4         8
    walk          8         9      (col 0 = standing pose)
    slash        12         6
    shoot        16        13
    hurt/death   20         6      (single row, faces down)

We use the RIGHT-facing row for directional anims and let the engine flip_h for
left. If your download adds extra animations, they appear BELOW row 20, so these
offsets stay valid. If the generator ever reorders the classic blocks, tweak
LPC_ROWS below.
------------------------------------------------------------------------------
"""
import argparse
import os
import shutil
import sys

from PIL import Image

FRAME = 64  # LPC native frame size (px)

# base_row for each classic block; east-facing row = base_row + 3
LPC_ROWS = {
    "spellcast": 0,
    "thrust": 4,
    "walk": 8,
    "slash": 12,
    "shoot": 16,
    "hurt": 20,  # single row, faces down
}

# game-animation -> (block, east_facing?, start_col, frame_count, speed, loop)
# Maps LPC's slash/thrust/shoot onto the three hero weapons.
HERO_ANIMS = [
    ("idle",             "walk",   True,  0, 1,  4.0,  True),
    ("run",              "walk",   True,  1, 8,  10.0, True),
    ("attack_pickaxe",   "slash",  True,  0, 6,  13.0, False),  # vs zombie: overhead chop
    ("attack_whip",      "thrust", True,  0, 8,  13.0, False),  # vs pirate: lunge (mid-range)
    ("attack_glowsword", "shoot",  True,  0, 13, 18.0, False),  # vs robot: firing motion + bolt
    ("hurt",             "hurt",   False, 0, 3,  8.0,  False),
    ("dead",             "hurt",   False, 0, 6,  8.0,  False),
]

ENEMY_ANIMS = [
    ("idle",  "walk",  True,  0, 1, 4.0,  True),
    ("run",   "walk",  True,  1, 8, 10.0, True),
    ("attack","slash", True,  0, 6, 12.0, False),
    ("hurt",  "hurt",  False, 0, 3, 8.0,  False),
    ("dead",  "hurt",  False, 0, 6, 8.0,  False),
]

# Frames per attack block, used to size the single "attack" animation of a
# per-weapon hero sheet (a sheet of the hero with one weapon visible in-hand).
_ATTACK_FRAMES = {"slash": 6, "thrust": 8, "shoot": 13}


def weapon_anims(attack_block):
    """Anim set for an in-hand weapon sheet: standard names, one 'attack'."""
    return [
        ("idle",   "walk",       True, 0, 1,                          4.0,  True),
        ("run",    "walk",       True, 1, 8,                          10.0, True),
        ("attack", attack_block, True, 0, _ATTACK_FRAMES[attack_block], 14.0, False),
        ("hurt",   "hurt",       False, 0, 3,                         8.0,  False),
        ("dead",   "hurt",       False, 0, 6,                         8.0,  False),
    ]

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(PROJECT_ROOT, "assets", "sprites")
FRAMES_DIR = os.path.join(PROJECT_ROOT, "resources", "sprite_frames")


def row_y(block, east):
    base = LPC_ROWS[block]
    return (base + 3 if east else base) * FRAME


def build_tres(name, anims, cols):
    """Return the .tres text referencing assets/sprites/<name>.png."""
    subs = []          # (id, x, y) atlas regions
    anim_entries = []  # (anim_name, [ids], speed, loop)

    for anim_name, block, east, start_col, count, speed, loop in anims:
        y = row_y(block, east)
        if start_col + count > cols:
            print(f"  ! warning: {anim_name} wants cols {start_col}..{start_col+count-1} "
                  f"but sheet only has {cols} columns — clamping", file=sys.stderr)
            count = max(0, cols - start_col)
        ids = []
        for i in range(count):
            sub_id = f"{anim_name}_{i}"
            subs.append((sub_id, (start_col + i) * FRAME, y))
            ids.append(sub_id)
        anim_entries.append((anim_name, ids, speed, loop))

    load_steps = 1 + len(subs) + 1  # ext_resource + sub_resources + [resource]
    out = [f'[gd_resource type="SpriteFrames" load_steps={load_steps} format=3]', ""]
    out.append(f'[ext_resource type="Texture2D" path="res://assets/sprites/{name}.png" id="sheet"]')
    out.append("")
    for sub_id, x, y in subs:
        out.append(f'[sub_resource type="AtlasTexture" id="{sub_id}"]')
        out.append('atlas = ExtResource("sheet")')
        out.append(f'region = Rect2({x}, {y}, {FRAME}, {FRAME})')
        out.append("")

    out.append("[resource]")
    blocks = []
    for anim_name, ids, speed, loop in anim_entries:
        frames = ", ".join(
            '{\n"duration": 1.0,\n"texture": SubResource("%s")\n}' % i for i in ids
        )
        blocks.append(
            '{\n"frames": [%s],\n"loop": %s,\n"name": &"%s",\n"speed": %s\n}'
            % (frames, "true" if loop else "false", anim_name, speed)
        )
    out.append("animations = [" + ", ".join(blocks) + "]")
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser(description="Slice a Universal LPC sheet into game SpriteFrames.")
    ap.add_argument("--sheet", required=True, help="path to the downloaded LPC PNG")
    ap.add_argument("--name", required=True, help="character name, e.g. hero / zombie / robot / pirate")
    ap.add_argument("--kind", choices=["hero", "enemy", "weapon"], default="enemy",
                    help="hero = shared bare-handed sheet (per-weapon attack anims); "
                         "enemy = single attack; weapon = an in-hand weapon sheet "
                         "(idle/run/attack/hurt/dead, attack from --attack)")
    ap.add_argument("--attack", choices=["slash", "thrust", "shoot"], default="slash",
                    help="which body animation is the attack for --kind weapon")
    args = ap.parse_args()

    if not os.path.isfile(args.sheet):
        ap.error(f"sheet not found: {args.sheet}")

    img = Image.open(args.sheet).convert("RGBA")
    w, h = img.size
    cols, rows = w // FRAME, h // FRAME
    print(f"Sheet {args.sheet}: {w}x{h} -> {cols} cols x {rows} rows of {FRAME}px")
    if w % FRAME or h % FRAME:
        print(f"  ! warning: not an exact multiple of {FRAME}px — is this really an LPC sheet?",
              file=sys.stderr)
    if rows < 21:
        print(f"  ! warning: only {rows} rows; expected >=21 for the classic blocks "
              f"(walk/slash/shoot/hurt). Animations may be wrong.", file=sys.stderr)

    os.makedirs(SPRITES_DIR, exist_ok=True)
    os.makedirs(FRAMES_DIR, exist_ok=True)

    png_out = os.path.join(SPRITES_DIR, f"{args.name}.png")
    img.save(png_out)
    print(f"  wrote {os.path.relpath(png_out, PROJECT_ROOT)}")

    if args.kind == "hero":
        anims = HERO_ANIMS
    elif args.kind == "weapon":
        anims = weapon_anims(args.attack)
    else:
        anims = ENEMY_ANIMS
    tres = build_tres(args.name, anims, cols)
    tres_out = os.path.join(FRAMES_DIR, f"{args.name}_frames.tres")
    with open(tres_out, "w") as f:
        f.write(tres)
    print(f"  wrote {os.path.relpath(tres_out, PROJECT_ROOT)}")
    print("Now run: godot --headless --import")


if __name__ == "__main__":
    main()
