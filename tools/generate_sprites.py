#!/usr/bin/env python3
"""Generate original CC0 placeholder pixel-art sprite sheets + Godot SpriteFrames.

All art here is procedurally drawn from scratch, so it is original work released
into the public domain (CC0). Swap in a "real" pack later by replacing the PNGs
and regenerating the .tres (or re-slicing in the editor).

Run from the project root:  python3 tools/generate_sprites.py
"""
import math
import os
from PIL import Image, ImageDraw

W, H = 32, 48
SPRITES_DIR = "assets/sprites"
FRAMES_DIR = "resources/sprite_frames"

# (name, frame_count, fps, loop)
ANIMS = [
    ("idle", 2, 4, True),
    ("run", 4, 10, True),
    ("attack", 3, 13, False),
    ("hurt", 1, 6, False),
    ("dead", 3, 8, False),
]

PALETTES = {
    "hero":   dict(head_style="cap",     hat=(242, 210, 58),  skin=(240, 200, 160),
                   shirt=(60, 120, 210), pants=(40, 60, 120),  arm=(240, 200, 160),
                   accent=(190, 190, 200)),
    "zombie": dict(head_style="none",    hat=None,            skin=(120, 185, 95),
                   shirt=(78, 110, 70),  pants=(58, 72, 54),   arm=(110, 172, 88),
                   accent=(70, 120, 60)),
    "robot":  dict(head_style="antenna", hat=(120, 130, 150), skin=(150, 162, 178),
                   shirt=(110, 122, 142),pants=(92, 100, 116), arm=(132, 142, 162),
                   accent=(60, 220, 255)),
    "pirate": dict(head_style="hat",     hat=(38, 38, 44),    skin=(222, 182, 150),
                   shirt=(165, 62, 62),  pants=(72, 52, 42),   arm=(222, 182, 150),
                   accent=(235, 235, 235)),
}


def rect(d, x0, y0, x1, y1, color):
    d.rectangle([x0, y0, x1, y1], fill=color)


def draw_pose(pal, legA_lift=0, legB_lift=0, body_dy=0, arm_ext=0.0, lean=0, hurt=False):
    """Draw one standing humanoid frame, feet anchored at the bottom row.

    legA_lift / legB_lift raise a foot off the ground (0..3) for the run cycle.
    """
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lx = lean  # horizontal lean for head/torso

    # Legs (drawn first, behind torso); feet lift upward only.
    botA = 47 - legA_lift
    botB = 47 - legB_lift
    rect(d, 12, 36, 15, botA, pal["pants"])
    rect(d, 17, 36, 20, botB, pal["pants"])
    rect(d, 11, botA - 1, 16, botA, (30, 30, 36))
    rect(d, 16, botB - 1, 21, botB, (30, 30, 36))

    by = body_dy
    # Torso
    rect(d, 10 + lx, 20 + by, 22 + lx, 36 + by, pal["shirt"])
    # Back arm
    rect(d, 7 + lx, 21 + by, 10 + lx, 32 + by, pal["arm"])

    # Front arm: extends forward during attack and holds the accent (weapon).
    reach = int(arm_ext * 9)
    if reach > 0:
        rect(d, 21 + lx, 22 + by, 24 + lx + reach, 26 + by, pal["arm"])
        rect(d, 24 + lx + reach, 20 + by, 27 + lx + reach, 28 + by, pal["accent"])
    else:
        rect(d, 22 + lx, 21 + by, 25 + lx, 32 + by, pal["arm"])

    # Head
    rect(d, 11 + lx, 8 + by, 21 + lx, 20 + by, pal["skin"])
    # Eyes
    if hurt:
        d.point([(14 + lx, 13 + by), (15 + lx, 14 + by),
                 (18 + lx, 13 + by), (19 + lx, 14 + by)], fill=(20, 20, 24))
        d.point([(15 + lx, 13 + by), (14 + lx, 14 + by),
                 (19 + lx, 13 + by), (18 + lx, 14 + by)], fill=(20, 20, 24))
    else:
        rect(d, 14 + lx, 13 + by, 15 + lx, 14 + by, (20, 20, 24))
        rect(d, 18 + lx, 13 + by, 19 + lx, 14 + by, (20, 20, 24))

    # Headgear
    style = pal["head_style"]
    if style == "cap":
        rect(d, 10 + lx, 5 + by, 21 + lx, 9 + by, pal["hat"])      # cap crown
        rect(d, 21 + lx, 7 + by, 26 + lx, 9 + by, pal["hat"])      # brim
    elif style == "hat":
        rect(d, 9 + lx, 4 + by, 23 + lx, 7 + by, pal["hat"])       # pirate hat
        rect(d, 14 + lx, 1 + by, 18 + lx, 4 + by, pal["hat"])
        rect(d, 15 + lx, 4 + by, 17 + lx, 6 + by, pal["accent"])   # skull dot
    elif style == "antenna":
        rect(d, 15 + lx, 8 + by, 17 + lx, 19 + by, pal["accent"])  # visor band
        rect(d, 15 + lx, 1 + by, 16 + lx, 5 + by, (90, 90, 100))   # antenna
        rect(d, 14 + lx, 0 + by, 17 + lx, 1 + by, pal["accent"])

    return img


def make_frames(pal):
    frames = []
    # idle: gentle breathing bob
    frames.append(("idle", draw_pose(pal, body_dy=0)))
    frames.append(("idle", draw_pose(pal, body_dy=-1)))
    # run: alternating legs + body bob
    for i in range(4):
        phase = i / 4.0 * 2 * math.pi
        la = max(0, int(round(3 * math.sin(phase))))
        lb = max(0, int(round(3 * math.sin(phase + math.pi))))
        bob = -1 if i % 2 == 1 else 0
        frames.append(("run", draw_pose(pal, legA_lift=la, legB_lift=lb, body_dy=bob)))
    # attack: wind up, strike, recover
    for ext in (0.0, 1.0, 0.55):
        frames.append(("attack", draw_pose(pal, arm_ext=ext)))
    # hurt: knocked back
    frames.append(("hurt", draw_pose(pal, lean=-3, body_dy=1, hurt=True)))
    # dead: topple over
    base = draw_pose(pal, hurt=True)
    for ang in (28, 60, 88):
        toppled = base.rotate(ang, expand=False, center=(16, 44))
        frames.append(("dead", toppled))
    return frames


def write_sheet_and_tres(name, pal):
    frames = make_frames(pal)
    sheet = Image.new("RGBA", (W * len(frames), H), (0, 0, 0, 0))
    for i, (_, fimg) in enumerate(frames):
        sheet.paste(fimg, (i * W, 0))
    png_path = f"{SPRITES_DIR}/{name}.png"
    sheet.save(png_path)

    # Build SpriteFrames .tres referencing regions of the sheet via AtlasTexture.
    sub_blocks = []
    anim_entries = []
    idx = 0
    for (anim_name, count, fps, loop) in ANIMS:
        frame_refs = []
        for _ in range(count):
            sub_id = f"{anim_name}_{idx}"
            sub_blocks.append(
                f'[sub_resource type="AtlasTexture" id="{sub_id}"]\n'
                f'atlas = ExtResource("sheet")\n'
                f'region = Rect2({idx * W}, 0, {W}, {H})\n'
            )
            frame_refs.append(
                '{\n"duration": 1.0,\n"texture": SubResource("%s")\n}' % sub_id
            )
            idx += 1
        anim_entries.append(
            '{\n"frames": [%s],\n"loop": %s,\n"name": &"%s",\n"speed": %s\n}'
            % (", ".join(frame_refs), "true" if loop else "false", anim_name, float(fps))
        )

    load_steps = idx + 2  # ext_resource + all sub_resources + 1
    tres = (
        f'[gd_resource type="SpriteFrames" load_steps={load_steps} format=3]\n\n'
        f'[ext_resource type="Texture2D" path="res://{png_path}" id="sheet"]\n\n'
        + "\n".join(sub_blocks)
        + '\n[resource]\nanimations = ['
        + ", ".join(anim_entries)
        + "]\n"
    )
    with open(f"{FRAMES_DIR}/{name}_frames.tres", "w") as f:
        f.write(tres)
    print(f"  {name}: {len(frames)} frames -> {png_path} + {name}_frames.tres")


def main():
    os.makedirs(SPRITES_DIR, exist_ok=True)
    os.makedirs(FRAMES_DIR, exist_ok=True)
    print("Generating CC0 sprite sheets:")
    for name, pal in PALETTES.items():
        write_sheet_and_tres(name, pal)


if __name__ == "__main__":
    main()
