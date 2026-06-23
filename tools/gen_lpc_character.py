#!/usr/bin/env python3
"""Compose characters from Universal LPC layer assets, then slice via import_lpc.py.

This pulls the open LPC layer spritesheets (CC-BY-SA 3.0 / GPL 3.0) straight from the
generator's asset repo and alpha-stacks them into a universal sheet, so we don't have
to drive the browser generator. Each character is a z-ordered list of layer paths
(under the repo's `spritesheets/`). Missing layers/animations are skipped gracefully.

    python3 tools/gen_lpc_character.py            # build all
    python3 tools/gen_lpc_character.py hero       # build one
    godot --headless --import

Output: assets/sprites/<name>.png (+ resources/sprite_frames/<name>_frames.tres via
import_lpc.py). Credit every layer in CREDITS.md — share-alike.
"""
import io
import os
import subprocess
import sys
import urllib.request

from PIL import Image, ImageOps

REPO = "LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator"
RAW = f"https://raw.githubusercontent.com/{REPO}/master/spritesheets"
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SPRITES_DIR = os.path.join(PROJECT_ROOT, "assets", "sprites")

FRAME = 64
SHEET_W, SHEET_H = 832, 1344  # 13 cols x 21 rows: full classic universal sheet

# block -> base_row (top of its 4-direction span). Paste each layer's <block>.png at
# y = base_row*FRAME, x = 0. import_lpc.py reads the east row (base_row+3) from here.
BLOCKS = {
    "thrust": 4,
    "walk": 8,
    "slash": 12,
    "shoot": 16,
    "hurt": 20,
}
HERO_BLOCKS = ["thrust", "walk", "slash", "shoot", "hurt"]
ENEMY_BLOCKS = ["walk", "slash", "hurt"]

# z-order bottom -> top. Paths are relative to the repo's spritesheets/ dir.
CHARACTERS = {
    "hero": dict(kind="hero", blocks=HERO_BLOCKS, layers=[
        "body/bodies/male",
        "head/heads/human/male",
        ("legs/pants/male", None, (55, 95, 200)),               # blue jeans
        "feet/shoes/basic/male",
        ("torso/clothes/shortsleeve/tshirt/male", None, (225, 65, 65)),  # red tee
        "hair/plain/adult",
        ("hat/cloth/leather_cap/adult", None, (245, 205, 50)),  # yellow cap
    ]),
    "zombie": dict(kind="enemy", blocks=ENEMY_BLOCKS, layers=[
        ("body/bodies/zombie", "zombie"),
        "head/heads/zombie/adult",
        ("torso/clothes/shortsleeve/tshirt/male", None, (120, 80, 150)),  # tattered purple
    ]),
    "pirate": dict(kind="enemy", blocks=ENEMY_BLOCKS, layers=[
        "body/bodies/male",
        "head/heads/human/male",
        ("legs/pants/male", None, (40, 40, 55)),
        "feet/boots/basic/male",
        ("torso/clothes/shortsleeve/tshirt/male", None, (210, 55, 55)),  # red stripes vibe
        "hat/pirate/tricorne/basic/adult",
    ]),
    "robot": dict(kind="enemy", blocks=ENEMY_BLOCKS, layers=[
        "body/bodies/male",
        "head/heads/human/male",
        ("legs/armour/plate/male", "steel", (95, 155, 215)),
        ("feet/armour/plate/male", "steel", (95, 155, 215)),
        ("torso/armour/plate/male", "steel", (95, 155, 215)),  # bright blue mech
        ("hat/helmet/barbuta/male", None, (110, 175, 230)),
    ]),
}


def _get(url):
    try:
        with urllib.request.urlopen(url, timeout=30) as r:
            return Image.open(io.BytesIO(r.read())).convert("RGBA")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def colorize(img, rgb):
    """Recolor a layer toward `rgb` (kept transparent), preserving its shading.

    Maps luminance dark->light onto rgb*0.3 -> rgb, so flat LPC base colors become
    vivid without losing the pixel shading. Used to make outfits more colorful.
    """
    alpha = img.getchannel("A")
    gray = img.convert("L")
    dark = tuple(int(c * 0.30) for c in rgb)
    out = ImageOps.colorize(gray, black=dark, white=rgb).convert("RGBA")
    out.putalpha(alpha)
    return out


def fetch(layer, block):
    """Fetch one animation block for a layer.

    Layers come in two on-disk shapes: flat (`<path>/<block>.png`) or color-nested
    (`<path>/<block>/<color>.png`). A layer entry is one of:
      "path"                      flat, no recolor
      ("path", color)             color = a nested color filename (e.g. "zombie")
      ("path", color, (r,g,b))    also recolor toward (r,g,b); color may be None
    Returns the (optionally recolored) image, or None on 404.
    """
    if isinstance(layer, tuple):
        path, color = layer[0], layer[1]
        tint = layer[2] if len(layer) > 2 else None
    else:
        path, color, tint = layer, None, None
    img = None
    if color:
        img = _get(f"{RAW}/{path}/{block}/{color}.png")
    if img is None:
        img = _get(f"{RAW}/{path}/{block}.png")
    if img is not None and tint is not None:
        img = colorize(img, tint)
    return img


def build(name, spec):
    sheet = Image.new("RGBA", (SHEET_W, SHEET_H), (0, 0, 0, 0))
    used, missing = [], []
    for layer in spec["layers"]:
        got_any = False
        for block in spec["blocks"]:
            img = fetch(layer, block)
            if img is None:
                continue
            sheet.alpha_composite(img, (0, BLOCKS[block] * FRAME))
            got_any = True
        (used if got_any else missing).append(layer)
    print(f"[{name}] layers used: {used}")
    if missing:
        print(f"[{name}] layers MISSING (skipped): {missing}", file=sys.stderr)

    os.makedirs(SPRITES_DIR, exist_ok=True)
    out = os.path.join(SPRITES_DIR, f"{name}.png")
    sheet.save(out)
    print(f"[{name}] wrote {os.path.relpath(out, PROJECT_ROOT)}")

    subprocess.run([sys.executable, os.path.join(PROJECT_ROOT, "tools", "import_lpc.py"),
                    "--sheet", out, "--name", name, "--kind", spec["kind"]], check=True)


def main():
    wanted = sys.argv[1:] or list(CHARACTERS)
    for name in wanted:
        if name not in CHARACTERS:
            sys.exit(f"unknown character: {name} (have {list(CHARACTERS)})")
        build(name, CHARACTERS[name])
    print("\nDone. Now run: godot --headless --import")


if __name__ == "__main__":
    main()
