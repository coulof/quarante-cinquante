#!/usr/bin/env python3
"""Turn an AI/painted image into proper pixel art for a 1280x720 backdrop.

AI "pixel-art" images aren't on a real pixel grid and use hundreds of colors. This
crops to 16:9, downsamples to a small grid (so every pixel is a real, equal cell),
quantizes to a small palette, then nearest-upscales back to 1280x720 — so it reads
as deliberate pixel art that matches the chunky sprites.

    python3 tools/pixelate_bg.py --in assets/background-roof-city.jpg \
        --out assets/bg_roof.png --width 320 --colors 48

--width must divide 1280 (640=x2, 320=x4, 256=x5) for crisp integer scaling.
"""
import argparse
from PIL import Image

GAME_W, GAME_H = 1280, 720


def crop_169(im, keep_bottom=0.62, zoom=1.0):
    """Crop to 16:9, then optionally zoom in (crop a 1/zoom centered sub-region and
    let it be upscaled to fill the screen) so the scene reads bigger vs the sprites.
    keep_bottom biases which part survives (0.5 = centered, higher = keep the rooftop)."""
    w, h = im.size
    target_h = round(w * GAME_H / GAME_W)
    # keep_bottom: 0 = keep top, 1 = keep bottom (rooftop). Higher -> crop more off top.
    if target_h <= h:                       # too tall -> trim vertically
        extra = h - target_h
        top = round(extra * keep_bottom)
        im = im.crop((0, top, w, top + target_h))
    else:                                   # too wide -> trim horizontally (centered)
        target_w = round(h * GAME_W / GAME_H)
        left = (w - target_w) // 2
        im = im.crop((left, 0, left + target_w, h))
    if zoom and zoom > 1.0:                  # zoom in (crop a 1/zoom sub-region)
        w2, h2 = im.size
        cw, ch = round(w2 / zoom), round(h2 / zoom)
        left = (w2 - cw) // 2
        top = round((h2 - ch) * keep_bottom)
        im = im.crop((left, top, left + cw, top + ch))
    return im


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--width", type=int, default=320, help="internal pixel-grid width")
    ap.add_argument("--colors", type=int, default=48, help="palette size")
    ap.add_argument("--keep-bottom", type=float, default=0.62)
    ap.add_argument("--zoom", type=float, default=1.0, help="zoom into the scene (>1 = bigger)")
    args = ap.parse_args()

    im = Image.open(args.src).convert("RGB")
    im = crop_169(im, args.keep_bottom, args.zoom)
    small = im.resize((args.width, round(args.width * GAME_H / GAME_W)), Image.LANCZOS)
    small = small.quantize(colors=args.colors, method=Image.MEDIANCUT, dither=Image.NONE)
    out = small.convert("RGB").resize((GAME_W, GAME_H), Image.NEAREST)
    out.save(args.out)
    print(f"wrote {args.out}  grid={small.size}  colors={args.colors}")


if __name__ == "__main__":
    main()
