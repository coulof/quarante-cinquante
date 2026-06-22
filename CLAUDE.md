# CLAUDE.md

Guidance for working in this repo. See `PROMPT_beatemall_godot4.md` for the game spec/status.

## What this is
Browser (HTML5) beat-em-all in **Godot 4.6 / GDScript only** (no C#), aimed at a
7-year-old. Hero carries every unlocked weapon and switches with number keys; each
enemy has one weapon weakness (correct = full damage, wrong = 25% chip). Deployed to
Cloudflare Pages.

## Commands (via go-task — `Taskfile.yml`)
```bash
task                 # list tasks
godot --path .       # open the editor; F5 to play (main.tscn → level_01)
godot --headless --import                 # import resources (after adding assets)
godot --headless --quit-after 300         # boot headless; clean output = no errors

task templates       # one-time: download matching Godot export templates (~1.2 GB)
task build           # Web export to build/ + copies _headers in
task serve           # local preview via `wrangler pages dev` (applies _headers)
task deploy          # build + wrangler pages deploy build --branch=main
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
- **Combat flow**: hero ATTACK → `perform_attack()`; melee does a `intersect_shape`
  query, ranged spawns `laser_bolt.tscn` (a `Projectile` Area2D). Both call
  `CombatSystem.resolve_hit(weapon_id, enemy)` then `enemy.take_damage(...)`.
- **Spawner** (`enemy_spawner.gd`): reads a `Zone` resource, spawns over time, tracks
  deaths, advances `next_zone`; `zone.enemy_scenes[]` (non-empty) = mixed waves.
- **Levels**: `level_01.gd` is generic and shared by `level_01`/`level_02` (exported
  unlock fields + `next_level_scene`). It wires hero ↔ HUD ↔ spawner by signals.

## Conventions / gotchas
- **Signals over direct calls** — the whole entity/HUD/level wiring is signal-based.
- **Keyboard input uses `event.physical_keycode`**, not `keycode` — the dev is on
  AZERTY, where `keycode` is layout-dependent. Movement uses physical-key input actions.
- **Collision layers**: walls=1, hero=2, enemy=4. Hero melee query masks 4; enemy
  attacks mask 2; laser bolt masks 4.
- **Sprites are generated CC0**: edit `tools/generate_sprites.py` and rerun
  `python3 tools/generate_sprites.py`, then `godot --headless --import`. Don't hand-edit
  the PNGs or `resources/sprite_frames/*.tres`. Per-weapon hero attack anims are named
  `attack` / `attack_laser` / `attack_sabre` (from `weapon.attack_anim`).
- **`.tscn`/`.tres` are hand-written** here; keep `load_steps` correct and reference
  ext resources by path. Typed arrays serialize as e.g. `Array[Weapon]([...])`.
- **Web export needs templates** matching the editor version exactly (`task templates`).
- `build/` and `.godot/` are gitignored. Commit `*.uid` and `*.import` files.

## Git
Commit only when asked. End commit messages with the
`Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>` trailer.
