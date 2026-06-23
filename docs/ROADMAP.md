# Beat-em-all — vision & roadmap

2D pixel-art beat-em-all in the browser (HTML5), for a 7-year-old. This file is the
**vision + status + roadmap** only — architecture lives in `CLAUDE.md`, the overview in
`README.md`, and the art pipelines in `docs/lpc-characters.md` / `docs/lpc-recipes.md`.

## Vision
Kid-friendly enemies (Zombies, Robots, Pirates, Aliens…), a boy hero, TMNT-arcade combat
feel, on a Moebius/Sable-flavoured desert. Gentle difficulty, legible mechanics. Free on
itch.io.

## Core mechanic — weapon vs enemy weakness
Hero carries all unlocked weapons at once, switched with `1`/`2`/`3`. Each enemy has ONE
weakness: correct weapon = 100% damage, wrong = 25% chip. The enemy telegraphs its
weakness for 1.5s and the HUD shows "USE: <weapon>".

| Enemy  | Weakness   | Key | Style                          |
|--------|------------|-----|--------------------------------|
| Zombie | Pickaxe    | 1   | melee (overhead chop)          |
| Robot  | Glow Sword | 2   | **ranged** — fires a blue bolt |
| Pirate | Whip       | 3   | mid-range melee (long reach)   |

## Progression (4 levels, gentle ramp)
L1 zombies (start: pickaxe) → unlock Glow Sword · L2 robots → unlock Whip ·
L3 zombies+robots · L4 zombies+robots+pirates. Unlocks persist (GameState → localStorage).

## Status — DONE
Scaffolding, save/load, combat + weapon weaknesses, hero inventory + hotkeys, telegraph,
restyled HUD weapon menu, 4-level progression + unlock flow, **LPC character art with
per-weapon in-hand sheets** (pickaxe/glow sword/whip, swapped on weapon select), ranged
glow-sword bolt (delayed to the swing's end), **procedural desert backgrounds**
(`tools/gen_desert_bg.py`, per-level themes; arena = the plain), Web export + itch.io.

## Roadmap / TODO
- Audio (SFX + music), title/main menu, win screen.
- Hero **skins** actually change visuals (unlock is tracked; art not yet swapped).
- More enemy types (Aliens) and weapons; per-level background tuning (`task backgrounds`).
- **Enemy abilities:** robot ranged bolt is done; next — **pirates throw bombs** (lobbed,
  fused, blast/AoE damage so the hero must reposition) and pirate **dodge**.
- **Cover / rocks:** rocks become solid obstacles — block hero *and* enemy movement (no
  walking across) *and* stop projectiles, so the player can hide behind them.
- Camera scrolling (`zone.camera_target_x` is stubbed) for longer arenas.
- Phase-2 combat: correct weapon + perfect timing = bonus damage + special anim.
- Gamepad / mobile touch input.
- Procedural background generation from Godot
