# Browser Beat-em-all (Godot 4)

2D pixel-art beat-em-all for the browser, built in Godot 4.x / GDScript, aimed at a
7-year-old. Characters use [LPC](https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator)
art (CC-BY-SA — see `CREDITS.md`); each weapon shows in the hero's hand.

## Run

```bash
godot --path .          # opens the editor
godot --path . main.tscn  # run the game directly
```

Boots `main.tscn` → `scenes/world/level_01.tscn`, the first of four levels.

### Controls

- **Move:** arrow keys / WASD
- **Attack:** Space (or left mouse)
- **Switch weapon:** `1` Pickaxe · `2` Glow Sword · `3` Whip (only unlocked ones work)

Each enemy has one weapon weakness: **Zombie → Pickaxe** (melee), **Robot → Glow Sword**
(ranged blue bolt), **Pirate → Whip** (mid-range). Correct weapon = 100% damage, wrong
weapon = 25% chip. Enemies telegraph their weakness above their head for 1.5s before
striking. Clear a wave → unlock screen → next level.

### Progression
- **L1** zombies → unlock Glow Sword · **L2** robots → unlock Whip ·
  **L3** zombies+robots · **L4** zombies+robots+pirates. Start with just the pickaxe.

## Web export & itch.io

Everything is driven by [go-task](https://taskfile.dev) (`Taskfile.yml`):

```bash
task                 # list tasks
task templates       # one-time: download matching Godot export templates (~1.2 GB)
task build           # export Web build to build/
task serve           # preview locally (python http.server on :8060)

task itch:login      # one-time: authenticate butler with itch.io
task deploy          # build + push to itch.io (= task itch:push)
task itch:zip        # zip build/ for manual upload via the itch.io web UI
```

Set the itch.io target (`<user>/<game>`) via the `ITCH_TARGET` var at the top of
`Taskfile.yml` (default `bauagonzo/quarante-cinquante`); create the game page on
itch.io first. `GODOT_VERSION` must match your editor build so the right export
templates are installed.

The HTML5 (nothreads) build runs without cross-origin isolation, so no special
headers are needed — itch.io serves it as a playable web game (tick "This file
will be played in the browser"). Saves persist to `localStorage` via
`JavaScriptBridge` on web, and to `user://` elsewhere.

## Layout

- `scripts/` — autoloads (`game_state`, `combat_system`), `enemy_spawner`, `weapon` resource
- `scenes/entities/` — `character_base` + StateMachine (`states/`), `hero`, `enemy_base`, enemy types
- `scenes/world/` — `level_01`–`level_04` (share `level_01.gd`), `hud`, `zone` resource
- `scenes/ui/` — `unlock_screen`, `character_select` (stub)
- `resources/` — weapon `.tres` (with in-hand `frames`), level zone definitions
- `assets/` — `bg_desert*.png` per-level backdrops, character spritesheets
- `tools/` — `import_lpc_split.py` (split-export → SpriteFrames), `gen_lpc_character.py`,
  `gen_desert_bg.py` (procedural Moebius/Sable desert backdrops)
- `docs/` — `ROADMAP.md` (vision/status), `lpc-characters.md`, `lpc-recipes.md` (re-edit characters)

### Backgrounds
Levels use procedural pixel-art desert backdrops. Retune or add them with:
```bash
task bg -- --out assets/bg_desert_05.png --theme night --seed 3   # one-off
task backgrounds                                                   # regenerate the level set
```
Themes: `dusk` (level 1, the byte-stable default), `dawn`, `noon`, `night`. `--seed >0`
randomises the mesas/dunes/rocks; many other knobs (`--sun-x/-y/-r`, `--horizon`, …).
The lower half is the flat arena (walls + enemy spawns are constrained to the sand).
