# Editing character art (LPC)

Character sprites are **Liberated Pixel Cup (LPC)** art. You have two ways to change
them. The website is the easy/manual one; the script is for batch/repeatable builds.

> **Animation names are a contract.** Whatever you do, the game needs these frames:
> hero `idle` `run` `attack_pickaxe` `attack_whip` `attack_glowsword` `hurt` `dead`;
> enemies `idle` `run` `attack` `hurt` `dead`. They're derived from these LPC animations:
>
> | game anim | LPC animation | used by |
> |-----------|---------------|---------|
> | `run` (+ `idle`) | **walk** | movement |
> | `attack_pickaxe` | **slash** | pickaxe vs zombie (also enemy `attack`) |
> | `attack_whip` | **thrust** | whip vs pirate (mid-range melee) |
> | `attack_glowsword` | **shoot** | glowsword vs robot (ranged blue bolt) |
> | `hurt` / `dead` | **hurt/death** row | taking damage / dying |
>
> So when you style a character, make sure **walk, slash, thrust, shoot and the
> hurt/death** animations are enabled and look right. The game shows the
> **right-facing** rows and mirrors them for left, so face your character's detail to
> work both ways.

## Weapons visible in the hero's hand

The hero is **one `AnimatedSprite2D`** but switches weapons live, so a single sheet
can't show three different held weapons on the same walk/idle frames. Instead each
weapon carries its **own** in-hand sheet and the hero swaps `SpriteFrames` on weapon
select (`hero.gd::_select`). A weapon with no sheet falls back to the shared
bare-handed hero sheet (`hero_frames.tres`) + its `attack_anim`.

To give a weapon a visible in-hand sprite, use the generator's **"split by animation"**
export — it's far easier than the giant universal sheet, because each animation comes
as its own correctly-sized grid (including the oversize whip/glowsword attacks):

1. In the generator, build the **same hero character**, equip the weapon (e.g.
   *Weapon ▸ Sword ▸ Glowsword*, *Weapon ▸ Whip*), and use **"split by animation"**
   download. You get a folder with `standard/*.png` (64px anims) and `custom/*.png`
   (the oversize attack: `slash_128.png`, `slash_oversize.png`, `tool_whip.png`).
   Drop it under `assets/sprites/lpc_src/<variant>/`.
2. Import with the split importer, pointing `--attack` at the weapon's attack file:
   ```bash
   python3 tools/import_lpc_split.py --dir assets/sprites/lpc_src/hero_pickaxe \
       --name hero_pickaxe   --attack custom/slash_128.png
   python3 tools/import_lpc_split.py --dir assets/sprites/lpc_src/hero_glowsword \
       --name hero_glowsword --attack custom/slash_oversize.png
   python3 tools/import_lpc_split.py --dir assets/sprites/lpc_src/hero_whip \
       --name hero_whip      --attack custom/tool_whip.png
   godot --headless --import
   ```
   It slices the **east-facing** row of idle/run/attack/hurt into
   `resources/sprite_frames/hero_<weapon>_frames.tres` (copying the PNGs it needs into
   `assets/sprites/<name>/`). The oversize attack frames "just work" — the body stays
   centered and the weapon extends forward.
3. Point the weapon at its sheet — set `frames` in `resources/weapons/<weapon>.tres`,
   e.g. `frames = ExtResource("…/hero_pickaxe_frames.tres")`. Selecting that weapon now
   shows it in-hand for movement and attack.

> The base hero (`tools/import_lpc_split.py --dir …/hero --name hero --attack
> standard/slash.png`) is the bare-handed fallback used before a weapon is selected.
> `tools/import_lpc.py` (universal-sheet slicer) still exists but the split importer is
> preferred. `assets/sprites/lpc_src/` is marked `.godotignore` so the raw export dump
> isn't imported.

## A. Tweak it on the website (manual, recommended)

1. Open the generator:
   <https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator>
2. Build your character — pick the **body** (e.g. male/female/teen/zombie), then hair,
   hat (e.g. a cap under *Hat ▸ Cloth ▸ Leather cap*), clothes, shoes, etc.
3. Make sure the **walk / slash / thrust / shoot / hurt** animations are included
   (they're the standard set and sit at the top of the sheet). Extra animations are
   fine — they append below and the importer ignores them, so offsets stay correct.
4. Click **Download** to save the spritesheet PNG. Also note the **credits list** the
   generator shows (author/license per layer) — you must keep it (share-alike).
5. Slice it into the game:
   ```bash
   python3 tools/import_lpc.py --sheet ~/Downloads/your.png --name hero  --kind hero
   #   enemies:                                              --name zombie --kind enemy
   godot --headless --import
   ```
   `--name` must be one of `hero` / `zombie` / `robot` / `pirate` (it overwrites
   `assets/sprites/<name>.png` + `resources/sprite_frames/<name>_frames.tres`).
6. Paste the credits for that character into `CREDITS.md`.
7. Play it: `godot --path .` then F5.

That's it — no scene edits needed. LPC frames are 64×64 and the shared
`character_base.tscn` already scales the `Visual` node to `0.75` so they sit at the
right size. If a hat/feet looks a few pixels off, it's usually because the hat was
authored for "adult" proportions on a shorter body — pick an adult/male/teen body, or
nudge the `Visual` `position` in `scenes/entities/hero.tscn` (hero) or the relevant
enemy scene.

## B. Rebuild from layer recipes (scripted)

`tools/gen_lpc_character.py` downloads LPC layers straight from the asset repo and
stacks them, then calls `import_lpc.py`. Edit the `CHARACTERS` dict to change a recipe
(layer paths are relative to the repo's `spritesheets/`; order is bottom→top):

```python
"hero": dict(kind="hero", blocks=HERO_BLOCKS, layers=[
    "body/bodies/male",                       # flat: <path>/<anim>.png
    "legs/pants/male",
    "torso/clothes/shortsleeve/tshirt/male",
    "hair/plain/adult",
    "hat/cloth/leather_cap/adult",
    ("body/bodies/zombie", "zombie"),         # color-nested: <path>/<anim>/<color>.png
]),
```

- A layer is either a path string (`<path>/<anim>.png`) or a `(path, color)` tuple for
  assets stored as `<path>/<anim>/<color>.png` (e.g. zombie body, metal armour).
- Missing layers are skipped with a warning, so a wrong path won't break the build —
  the character just renders without that piece.
- Browse available parts via the GitHub API, e.g.
  `https://api.github.com/repos/LiberatedPixelCup/Universal-LPC-Spritesheet-Character-Generator/contents/spritesheets/hat`

Then:
```bash
python3 tools/gen_lpc_character.py            # all characters
python3 tools/gen_lpc_character.py hero       # just one
godot --headless --import
```

## Licensing
LPC art is **CC-BY-SA 3.0 / GPL 3.0** (not CC0). Every character you ship must credit
its layers in `CREDITS.md`.
```
