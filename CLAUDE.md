# CLAUDE.md

Guidance for working in this repo. See `docs/ROADMAP.md` for the vision/roadmap.

## What this is
Browser (HTML5) beat-em-all in **Godot 4.6 / GDScript only** (no C#), aimed at a
7-year-old. Hero carries every unlocked weapon and switches with number keys; each
enemy has one weapon weakness (correct = full damage, wrong = 25% chip). Deployed to
itch.io (free) via butler.

## Commands (via go-task — `Taskfile.yml`)
```bash
task                 # list tasks
godot --path .       # open the editor; F5 to play (main.tscn → level_01)
godot --headless --import                 # import resources (after adding assets)
godot --headless --quit-after 300         # boot headless; clean output = no errors

task templates       # one-time: download matching Godot export templates (~1.2 GB)
task build           # Web export to build/
task serve           # local preview via python http.server on :8060
task itch:login      # one-time: authenticate butler with itch.io
task deploy          # build + butler push build → itch.io (= task itch:push)
task itch:zip        # zip build/ for manual upload via the itch.io web UI
```

### Testing
No test framework wired in. Validate logic with headless SceneTree scripts:
`godot --headless -s /tmp/foo.gd` where `foo.gd extends SceneTree`. Note: autoloads'
**global identifiers may not resolve** in external `-s` scripts — add the autoload as
a node manually, and avoid statically referencing `class_name` types that depend on
autoloads (instantiate at runtime instead). gdUnit4 is documented in
`.agents/skills/godot/` if you want a real framework.

## Architecture
- **Autoloads** (`scripts/`, registered in `project.godot`): `GameState` (unlocks +
  save/load), `CombatSystem` (`resolve_hit` / `damage_for`, `enum Outcome {WEAK, CHIP}`).
- **Entities**: `character_base.tscn` (CharacterBody2D + `Visual` AnimatedSprite2D +
  StateMachine). `hero.tscn` and `enemy_base.tscn` are **inherited scenes** overriding
  the script/props; `zombie/robot/pirate` inherit `enemy_base`; concrete scenes set
  `Visual.sprite_frames`.
- **StateMachine** (`scenes/entities/states/`): IDLE/RUN/ATTACK/HURT/DEAD, one script
  each. States request changes by **emitting `transitioned`** (never call each other).
  HURT/DEAD are forced from the character's `hurt`/`died` signals via `force_transition`.
- **Combat flow**: hero ATTACK → `perform_attack()`; melee does an `intersect_shape`
  query (whip overrides reach via `weapon.melee_reach`), ranged spawns `laser_bolt.tscn`
  (a `Projectile` Area2D) **after a delay** (`attack_duration * 0.65`) so the glow-sword
  bolt leaves as the slash finishes. Both call `CombatSystem.resolve_hit(weapon_id,
  enemy)` then `enemy.take_damage(...)`.
- **Weapon art swap**: each `Weapon` has a `frames: SpriteFrames` (the hero holding it,
  idle/run/attack/hurt/dead). `hero.gd::_select` swaps `Visual.sprite_frames` on weapon
  switch; `get_attack_anim()` returns `"attack"` for those sheets. Null `frames` falls
  back to the shared bare-handed `hero_frames.tres` + per-weapon `attack_anim`.
- **Spawner** (`enemy_spawner.gd`): reads a `Zone` resource, spawns over time, tracks
  deaths, advances `next_zone`; `zone.enemy_scenes[]` (non-empty) = mixed waves.
- **Levels**: `level_01.gd` is generic and shared by `level_01`–`level_04` (exported
  unlock fields + `next_level_scene`). It wires hero ↔ HUD ↔ spawner by signals. Each
  level has a `Background` TextureRect (`assets/bg_desert*.png`); the **arena is the
  lower-half plain** — the top wall (y=360) and enemy `spawn_area` are constrained to
  the sand so nothing spawns in the sky.
- **Backgrounds**: procedural pixel-art deserts from `tools/gen_desert_bg.py` (Moebius/
  Sable; themes + `--seed`). Level 1 = `bg_desert.png` (theme `dusk`, seed 0 = byte-stable
  default). Regenerate via `task bg -- …` / `task backgrounds`. Don't hand-edit the PNGs.

## Conventions / gotchas
- **Signals over direct calls** — the whole entity/HUD/level wiring is signal-based.
- **Keyboard input uses `event.physical_keycode`**, not `keycode` — the dev is on
  AZERTY, where `keycode` is layout-dependent. Movement uses physical-key input actions.
- **Touch controls** (mobile web): `scenes/ui/joystick.gd` feeds the `move_*` actions;
  the HUD (`hud.gd`/`hud.tscn`) has an ATK button (drives the `attack` action) + tappable
  weapon chips (`weapon_selected` → `hero.select_weapon_id`). Shown only when
  `DisplayServer.is_touchscreen_available()` (or HUD `force_touch_ui` for editor testing).
  `emulate_mouse_from_touch=false` so touches don't fire the mouse-bound attack. Hero
  polls `attack` in `_process` so keyboard/mouse/touch all funnel through one path.
- **Collision layers**: walls=1, hero=2, enemy=4. Hero melee query masks 4; enemy
  attacks mask 2; laser bolt masks 4.
- **Sprite anim names are the contract**: per-weapon **in-hand** hero sheets use a single
  `attack` (+ `idle`/`run`/`hurt`/`dead`); the bare-handed fallback sheet uses
  `attack_pickaxe`/`attack_glowsword`/`attack_whip` (from `weapon.attack_anim`); enemies
  use a generic `attack`. Any art source must produce these names. Art sources:
  - **LPC split export (current, CC-BY-SA)**: the path for **all** characters now (hero +
    zombie/robot/pirate). Generator → "split by animation" →
    `assets/sprites/lpc_src/<variant>/` → `tools/import_lpc_split.py --dir … --name …
    --attack <standard/…|custom/<oversize>.png>`. Slices the east row into a frames
    `.tres` (copies the PNGs into `assets/sprites/<name>/`). Add **`--from-walk`** for
    bodies with no idle/run anims (Skeleton, muscular) — otherwise those frames show only
    the head. See `docs/lpc-characters.md` + `docs/lpc-recipes.md`. `lpc_src/` has a
    `.gdignore` and is gitignored (regenerate from the recipe; the game uses the copies).
  - **Legacy LPC tools**: `tools/import_lpc.py` (universal-sheet slicer) and
    `tools/gen_lpc_character.py` (layer-stacking compositor) — superseded by the split
    importer. LPC frames are 64×64 (oversize attacks 128/192px); `character_base.tscn`'s
    `Visual` is scaled `0.75`. Credit every layer in `CREDITS.md` (share-alike).
  - **Procedural CC0 (legacy)**: `tools/generate_sprites.py` (32×48). It **overwrites**
    `assets/sprites/*.png` + `resources/sprite_frames/*.tres`, so don't rerun it for a
    character you've replaced with LPC art.
- **Audio**: `Audio` autoload (`scripts/audio.gd`) plays SFX/music; `Audio.play("<name>")`
  no-ops if the clip is absent. Names are the contract (`Audio.SOUNDS`); drop
  `<name>.ogg` (+ `_1/_2…` variants → randomized) in `assets/audio/sfx/`, music in
  `assets/audio/music/`. Per-character hurt/die via `CharacterBase.sfx_id`. Godot can't
  import m4a/aac — convert to OGG (`ffmpeg … -c:a libvorbis`). See `assets/audio/README.md`.
- **`.tscn`/`.tres` are hand-written** here; keep `load_steps` correct and reference
  ext resources by path. Typed arrays serialize as e.g. `Array[Weapon]([...])`.
- **Web export needs templates** matching the editor version exactly (`task templates`).
- `build/` and `.godot/` are gitignored. Commit `*.uid` and `*.import` files.
- **Progress is session-only** (`GameState.PERSIST = false`): each launch starts at
  Level 1 with just the pickaxe; weapons unlock as you advance within a run (held in the
  `GameState` autoload across level scenes), nothing is written to disk. This is the
  permanent fix for the recurring "all weapons already unlocked on a fresh start" — there
  is no save to reload. F1 (debug builds, `OS.is_debug_build()`) resets mid-run. Flip
  `PERSIST` to restore cross-session save/load.

## Git
Commit only when asked. End commit messages with the
`Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer.
