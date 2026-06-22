#!/usr/bin/env python3
"""Generate original CC0 placeholder pixel-art sprite sheets + Godot SpriteFrames.

All art here is procedurally drawn from scratch, so it is original work released
into the public domain (CC0). Swap in a "real" pack later by replacing the PNGs
and regenerating the .tres (or re-slicing in the editor).

The hero gets a distinct attack animation per weapon:
  attack        -> shovel  (overhead chop)
  attack_laser  -> laser   (point forward, muzzle flash)
  attack_sabre  -> sabre   (horizontal slash)
Enemies only need a generic "attack".

Run from the project root:  python3 tools/generate_sprites.py
"""
import math
import os
from PIL import Image, ImageDraw

W, H = 32, 48
SPRITES_DIR = "assets/sprites"
FRAMES_DIR = "resources/sprite_frames"

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

SHOVEL = (150, 100, 60)
LASER = (60, 220, 255)
BLADE = (240, 240, 255)


def rect(d, x0, y0, x1, y1, color):
    d.rectangle([x0, y0, x1, y1], fill=color)


def draw_pose(pal, legA_lift=0, legB_lift=0, body_dy=0, lean=0, hurt=False,
              arm_pose="down", arm_ext=0.0, weapon_color=None, weapon_len=4,
              weapon_h=2, flash=False):
    """Draw one humanoid frame, feet anchored at the bottom row."""
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    lx = lean
    wcol = weapon_color if weapon_color else pal["accent"]

    # Legs (feet only ever lift upward, keeping coords valid)
    botA, botB = 47 - legA_lift, 47 - legB_lift
    rect(d, 12, 36, 15, botA, pal["pants"])
    rect(d, 17, 36, 20, botB, pal["pants"])
    rect(d, 11, botA - 1, 16, botA, (30, 30, 36))
    rect(d, 16, botB - 1, 21, botB, (30, 30, 36))

    by = body_dy
    rect(d, 10 + lx, 20 + by, 22 + lx, 36 + by, pal["shirt"])     # torso
    rect(d, 7 + lx, 21 + by, 10 + lx, 32 + by, pal["arm"])        # back arm

    # Front arm + weapon, varying by pose
    sx = 21 + lx
    if arm_pose == "down":
        rect(d, 22 + lx, 21 + by, 25 + lx, 32 + by, pal["arm"])
    elif arm_pose == "fwd":
        reach = int(round(arm_ext * 9))
        rect(d, sx, 22 + by, 24 + lx + reach, 26 + by, pal["arm"])
        wx = 25 + lx + reach
        rect(d, wx, 24 - weapon_h // 2 + by, wx + weapon_len, 24 + (weapon_h + 1) // 2 + by, wcol)
        if flash:
            rect(d, wx + weapon_len - 1, 21 + by, wx + weapon_len + 2, 27 + by, (255, 255, 210))
    elif arm_pose == "up":
        rect(d, 22 + lx, 10 + by, 25 + lx, 24 + by, pal["arm"])   # raised arm
        rect(d, 20 + lx, 3 + by, 20 + lx + weapon_len, 3 + weapon_h + by, wcol)  # weapon overhead
    elif arm_pose == "slash":
        rect(d, sx, 20 + by, 26 + lx, 24 + by, pal["arm"])
        rect(d, 26 + lx, 18 + by, 26 + lx + weapon_len, 20 + by, wcol)  # wide blade
        rect(d, 26 + lx, 22 + by, 26 + lx + weapon_len, 24 + by, wcol)

    rect(d, 11 + lx, 8 + by, 21 + lx, 20 + by, pal["skin"])       # head
    if hurt:
        d.point([(14 + lx, 13 + by), (15 + lx, 14 + by), (18 + lx, 13 + by), (19 + lx, 14 + by),
                 (15 + lx, 13 + by), (14 + lx, 14 + by), (19 + lx, 13 + by), (18 + lx, 14 + by)],
                fill=(20, 20, 24))
    else:
        rect(d, 14 + lx, 13 + by, 15 + lx, 14 + by, (20, 20, 24))
        rect(d, 18 + lx, 13 + by, 19 + lx, 14 + by, (20, 20, 24))

    style = pal["head_style"]
    if style == "cap":
        rect(d, 10 + lx, 5 + by, 21 + lx, 9 + by, pal["hat"])
        rect(d, 21 + lx, 7 + by, 26 + lx, 9 + by, pal["hat"])
    elif style == "hat":
        rect(d, 9 + lx, 4 + by, 23 + lx, 7 + by, pal["hat"])
        rect(d, 14 + lx, 1 + by, 18 + lx, 4 + by, pal["hat"])
        rect(d, 15 + lx, 4 + by, 17 + lx, 6 + by, pal["accent"])
    elif style == "antenna":
        rect(d, 15 + lx, 8 + by, 17 + lx, 19 + by, pal["accent"])
        rect(d, 15 + lx, 1 + by, 16 + lx, 5 + by, (90, 90, 100))
        rect(d, 14 + lx, 0 + by, 17 + lx, 1 + by, pal["accent"])

    return img


def _idle(pal):
    return [draw_pose(pal), draw_pose(pal, body_dy=-1)]


def _run(pal):
    out = []
    for i in range(4):
        phase = i / 4.0 * 2 * math.pi
        la = max(0, int(round(3 * math.sin(phase))))
        lb = max(0, int(round(3 * math.sin(phase + math.pi))))
        out.append(draw_pose(pal, legA_lift=la, legB_lift=lb, body_dy=(-1 if i % 2 else 0)))
    return out


def _hurt(pal):
    return [draw_pose(pal, lean=-3, body_dy=1, hurt=True)]


def _dead(pal):
    base = draw_pose(pal, hurt=True)
    return [base.rotate(a, expand=False, center=(16, 44)) for a in (28, 60, 88)]


def _att_generic(pal):
    return [draw_pose(pal, arm_pose="fwd", arm_ext=e, weapon_len=3, weapon_h=2)
            for e in (0.2, 1.0, 0.5)]


def _att_shovel(pal):
    return [
        draw_pose(pal, arm_pose="up", weapon_color=SHOVEL, weapon_len=6, weapon_h=2),
        draw_pose(pal, arm_pose="fwd", arm_ext=1.0, weapon_color=SHOVEL, weapon_len=6, weapon_h=3),
        draw_pose(pal, arm_pose="fwd", arm_ext=0.5, weapon_color=SHOVEL, weapon_len=5, weapon_h=3),
    ]


def _att_laser(pal):
    return [
        draw_pose(pal, arm_pose="fwd", arm_ext=1.0, weapon_color=LASER, weapon_len=6, weapon_h=4, flash=True),
        draw_pose(pal, arm_pose="fwd", arm_ext=0.85, lean=-1, weapon_color=LASER, weapon_len=5, weapon_h=4),
    ]


def _att_sabre(pal):
    return [
        draw_pose(pal, arm_pose="up", weapon_color=BLADE, weapon_len=6, weapon_h=2),
        draw_pose(pal, arm_pose="slash", weapon_color=BLADE, weapon_len=7),
        draw_pose(pal, arm_pose="fwd", arm_ext=0.4, weapon_color=BLADE, weapon_len=5, weapon_h=2),
    ]


def anims_for(name, pal):
    """Return ordered list of (anim_name, fps, loop, [frame images])."""
    a = [("idle", 4, True, _idle(pal)), ("run", 10, True, _run(pal))]
    if name == "hero":
        a.append(("attack", 13, False, _att_shovel(pal)))
        a.append(("attack_laser", 16, False, _att_laser(pal)))
        a.append(("attack_sabre", 14, False, _att_sabre(pal)))
    else:
        a.append(("attack", 13, False, _att_generic(pal)))
    a.append(("hurt", 6, False, _hurt(pal)))
    a.append(("dead", 8, False, _dead(pal)))
    return a


def write_sheet_and_tres(name, pal):
    anims = anims_for(name, pal)
    flat = [img for (_, _, _, imgs) in anims for img in imgs]
    sheet = Image.new("RGBA", (W * len(flat), H), (0, 0, 0, 0))
    for i, img in enumerate(flat):
        sheet.paste(img, (i * W, 0))
    png_path = f"{SPRITES_DIR}/{name}.png"
    sheet.save(png_path)

    sub_blocks, anim_entries, idx = [], [], 0
    for (anim_name, fps, loop, imgs) in anims:
        refs = []
        for _ in imgs:
            sid = f"{anim_name}_{idx}"
            sub_blocks.append(
                f'[sub_resource type="AtlasTexture" id="{sid}"]\n'
                f'atlas = ExtResource("sheet")\nregion = Rect2({idx * W}, 0, {W}, {H})\n'
            )
            refs.append('{\n"duration": 1.0,\n"texture": SubResource("%s")\n}' % sid)
            idx += 1
        anim_entries.append(
            '{\n"frames": [%s],\n"loop": %s,\n"name": &"%s",\n"speed": %s\n}'
            % (", ".join(refs), "true" if loop else "false", anim_name, float(fps))
        )

    tres = (
        f'[gd_resource type="SpriteFrames" load_steps={idx + 2} format=3]\n\n'
        f'[ext_resource type="Texture2D" path="res://{png_path}" id="sheet"]\n\n'
        + "\n".join(sub_blocks)
        + "\n[resource]\nanimations = [" + ", ".join(anim_entries) + "]\n"
    )
    with open(f"{FRAMES_DIR}/{name}_frames.tres", "w") as f:
        f.write(tres)
    print(f"  {name}: {len(flat)} frames, {len(anims)} anims")


def main():
    os.makedirs(SPRITES_DIR, exist_ok=True)
    os.makedirs(FRAMES_DIR, exist_ok=True)
    print("Generating CC0 sprite sheets:")
    for name, pal in PALETTES.items():
        write_sheet_and_tres(name, pal)


if __name__ == "__main__":
    main()
