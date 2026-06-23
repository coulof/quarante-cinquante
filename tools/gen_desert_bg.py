#!/usr/bin/env python3
"""Procedural pixel-art desert backdrops (Moebius / 'Sable' spirit), parameterised.

Flat colour fields, a low sun/moon, layered mesas/dunes and a wide sandy plain that
doubles as the brawler arena (lower ~half, where characters stand). Drawn on a small
grid with a limited palette, then nearest-upscaled to 1280x720 -> clean pixel art.

    # level 1 (the approved look = defaults; byte-stable):
    python3 tools/gen_desert_bg.py --out assets/bg_desert.png
    # variants for later levels:
    python3 tools/gen_desert_bg.py --out assets/bg_desert_02.png --theme noon  --seed 2
    python3 tools/gen_desert_bg.py --out assets/bg_desert_03.png --theme dawn  --seed 5
    python3 tools/gen_desert_bg.py --out assets/bg_desert_04.png --theme night --seed 9

`--seed 0` (default) draws the fixed, hand-placed layout; `--seed >0` randomises the
mesas/dunes/rocks for variety. Pick a palette with `--theme`.
"""
import argparse
import math
import random
from PIL import Image, ImageDraw

W, H, SCALE = 320, 180, 4

# --- limited palettes (top->horizon sky, sun/moon rings, mesas, dunes, sand...) ---
THEMES = {
    "dusk": dict(  # the approved level-1 look
        sky=[(150, 152, 188), (170, 158, 186), (190, 162, 176), (210, 168, 162),
             (228, 180, 150), (242, 200, 156), (250, 222, 176)],
        sun=[(250, 224, 176), (250, 232, 190), (251, 240, 206), (253, 248, 226)],
        mesa_far=(190, 152, 158), mesa_mid=(200, 134, 116),
        dunes=[(228, 192, 144), (218, 178, 130), (206, 164, 118), (194, 150, 108)],
        sand=(232, 200, 152), shadow=(150, 120, 120, 55),
        rock=(172, 130, 118), rock_lit=(208, 170, 142)),
    "dawn": dict(
        sky=[(180, 170, 200), (204, 176, 196), (224, 182, 182), (238, 190, 168),
             (246, 204, 168), (250, 218, 182), (252, 232, 200)],
        sun=[(252, 228, 200), (253, 236, 212), (254, 244, 226), (255, 250, 238)],
        mesa_far=(202, 162, 172), mesa_mid=(212, 150, 140),
        dunes=[(238, 206, 162), (230, 194, 150), (220, 182, 140), (210, 170, 130)],
        sand=(242, 212, 168), shadow=(160, 130, 140, 50),
        rock=(186, 148, 140), rock_lit=(220, 184, 160)),
    "noon": dict(
        sky=[(120, 164, 200), (150, 182, 210), (180, 196, 214), (206, 206, 206),
             (226, 212, 196), (240, 222, 190), (248, 232, 196)],
        sun=[(248, 240, 210), (251, 246, 224), (253, 250, 236), (255, 253, 246)],
        mesa_far=(196, 166, 150), mesa_mid=(200, 150, 124),
        dunes=[(236, 212, 166), (226, 200, 154), (214, 186, 140), (202, 172, 126)],
        sand=(238, 214, 168), shadow=(130, 120, 120, 45),
        rock=(176, 140, 122), rock_lit=(212, 180, 150)),
    "night": dict(
        sky=[(28, 30, 60), (40, 40, 78), (56, 52, 92), (76, 64, 104),
             (98, 78, 112), (124, 96, 118), (150, 116, 124)],
        sun=[(180, 196, 220), (204, 216, 234), (226, 234, 246), (244, 248, 252)],
        mesa_far=(70, 64, 96), mesa_mid=(92, 72, 96),
        dunes=[(120, 104, 116), (106, 92, 106), (92, 80, 96), (80, 70, 86)],
        sand=(132, 112, 120), shadow=(20, 20, 40, 80),
        rock=(86, 74, 90), rock_lit=(120, 104, 116)),
}


def wavy_top(d, horizon, y_base, amp, period, color, phase=0.0):
    """Fill below a gentle sine ridge down to the horizon line (a dune band)."""
    pts = [(0, horizon)]
    for x in range(0, W + 1, 2):
        pts.append((x, y_base + int(amp * math.sin((x / period) + phase))))
    pts += [(W, horizon)]
    d.polygon(pts, fill=color)


def butte(d, x0, x1, top, hor, color, sky_top, arch=False):
    """A flat-topped mesa from x0..x1; optional arch opening (Moebius staple)."""
    bevel = max(2, (x1 - x0) // 8)
    d.polygon([(x0, hor), (x0, top + 6), (x0 + bevel, top), (x1 - bevel, top),
               (x1, top + 6), (x1, hor)], fill=color)
    if arch:
        cx = (x0 + x1) // 2
        d.rectangle([cx - 7, top + 14, cx + 7, hor], fill=sky_top)
        d.ellipse([cx - 9, top + 8, cx + 9, top + 22], fill=sky_top)


def draw(theme, args):
    rng = random.Random(args.seed)
    hor = args.horizon
    img = Image.new("RGB", (W, H))
    d = ImageDraw.Draw(img)

    sky = theme["sky"]
    for i, c in enumerate(sky):
        d.rectangle([0, round(i * hor / len(sky)), W, round((i + 1) * hor / len(sky))], fill=c)

    if not args.no_sun:
        step = max(4, args.sun_r // len(theme["sun"]))
        for i, c in enumerate(theme["sun"]):
            rr = args.sun_r - i * step
            d.ellipse([args.sun_x - rr, args.sun_y - rr, args.sun_x + rr, args.sun_y + rr], fill=c)

    mf, mm = theme["mesa_far"], theme["mesa_mid"]
    if args.seed == 0:                       # fixed, approved layout
        d.polygon([(6, hor), (6, 70), (18, 64), (46, 64), (54, 70), (54, hor)], fill=mf)
        d.polygon([(286, hor), (286, 54), (298, 48), (320, 48), (320, hor)], fill=mf)
        if not args.no_arch:
            d.polygon([(228, hor), (228, 62), (240, 56), (262, 56), (272, 62), (272, hor)], fill=mm)
            d.rectangle([243, 76, 257, hor], fill=sky[-1])
            d.ellipse([241, 70, 259, 84], fill=sky[-1])
        arches = []
    else:                                    # randomised buttes
        arches = []
        for _ in range(args.mesas):
            w = rng.randint(34, 64)
            x0 = rng.randint(0, W - w)
            top = rng.randint(48, 74)
            is_arch = (not args.no_arch) and rng.random() < 0.4
            butte(d, x0, x0 + w, top, hor, mm if is_arch else mf, sky[-1], arch=is_arch)
            if is_arch:
                arches.append((x0 + x0 + w) // 2)

    d.rectangle([0, hor, W, H], fill=theme["sand"])
    dunes = theme["dunes"]
    for i in range(args.dunes):
        wavy_top(d, hor, hor + 8 + i * 16, 3 + i, 70 + i * 12, dunes[i % len(dunes)], phase=i * 1.3)

    # soft shadow pooling off an arch onto the plain
    shadow_x = 250 if args.seed == 0 and not args.no_arch else (arches[0] if arches else None)
    if shadow_x is not None:
        sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(sh).polygon([(shadow_x - 18, hor), (shadow_x + 22, hor),
                                    (shadow_x + 50, H), (shadow_x + 12, H)], fill=theme["shadow"])
        img = Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB")
        d = ImageDraw.Draw(img)

    rocks = [(26, 150, 16), (292, 158, 18)] if args.seed == 0 else \
        [(rng.randint(16, W - 16), rng.randint(H - 36, H - 16), rng.randint(12, 20))
         for _ in range(args.rocks)]
    for rx, ry, rw in rocks:
        d.ellipse([rx - rw, ry, rx + rw, ry + rw], fill=theme["rock"])
        d.ellipse([rx - rw, ry - 3, rx + rw - 6, ry + rw - 8], fill=theme["rock_lit"])

    return img.resize((W * SCALE, H * SCALE), Image.NEAREST)


def _cloud(d, cx, cy, w, base, hi):
    """One soft, flat-bottomed pixel cloud from overlapping circles + a top highlight."""
    r = int(w * 0.22)
    pts = [(cx - w // 2, int(r * 0.7)), (cx - w // 4, r), (cx, int(r * 1.15)),
           (cx + w // 4, r), (cx + w // 2, int(r * 0.7))]
    for x, rr in pts:
        d.ellipse([x - rr, cy - rr, x + rr, cy + rr], fill=base)
    d.rectangle([cx - w // 2, cy, cx + w // 2, cy + int(r * 0.6)], fill=base)   # flat bottom
    for x, rr in pts[1:4]:
        hr = int(rr * 0.6)
        d.ellipse([x - hr, cy - int(r * 0.8), x + hr, cy - int(r * 0.8) + 2 * hr], fill=hi)


def make_clouds() -> Image.Image:
    """A horizontally-tileable, transparent strip of pale clouds (edges kept clear so
    two scrolling copies loop seamlessly). Theme-neutral — reads on every sky."""
    img = Image.new("RGBA", (320, 60), (0, 0, 0, 0))   # small grid -> x4 = 1280x240
    d = ImageDraw.Draw(img)
    base = (242, 238, 228, 95)
    hi = (255, 253, 247, 130)
    for cx, cy, w in [(46, 18, 40), (110, 30, 52), (170, 15, 34), (232, 26, 46), (286, 20, 38)]:
        _cloud(d, cx, cy, w, base, hi)
    return img.resize((320 * SCALE, 60 * SCALE), Image.NEAREST)


def main():
    ap = argparse.ArgumentParser(description="Generate a pixel-art desert backdrop.")
    ap.add_argument("--out", default="assets/bg_desert.png")
    ap.add_argument("--theme", choices=list(THEMES), default="dusk")
    ap.add_argument("--seed", type=int, default=0, help="0 = fixed layout; >0 randomises")
    ap.add_argument("--horizon", type=int, default=92, help="ground line (px on the 180-tall grid)")
    ap.add_argument("--sun-x", type=int, default=150)
    ap.add_argument("--sun-y", type=int, default=64)
    ap.add_argument("--sun-r", type=int, default=34)
    ap.add_argument("--no-sun", action="store_true")
    ap.add_argument("--no-arch", action="store_true")
    ap.add_argument("--mesas", type=int, default=3, help="butte count when --seed >0")
    ap.add_argument("--dunes", type=int, default=4, help="foreground dune bands")
    ap.add_argument("--rocks", type=int, default=2, help="foreground rocks when --seed >0")
    ap.add_argument("--clouds", metavar="PATH", help="instead of a backdrop, write a "
                    "tileable cloud strip to PATH (for the drifting-cloud layer)")
    args = ap.parse_args()
    if args.clouds:
        make_clouds().save(args.clouds)
        print(f"wrote {args.clouds}  (cloud strip)")
        return
    draw(THEMES[args.theme], args).save(args.out)
    print(f"wrote {args.out}  (1280x720, theme={args.theme}, seed={args.seed})")


if __name__ == "__main__":
    main()
