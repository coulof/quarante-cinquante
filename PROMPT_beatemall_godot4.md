# Browser Beat-em-all — Godot 4 Project

2D pixel-art beat-em-all playable in the browser (HTML5), for a 7-year-old audience.
This file is the living spec/status; see `CLAUDE.md` for how to work in the repo.

---

## Project vision
Kid-friendly enemies (Zombies, Robots, Pirates, Aliens…). Hero: a boy with a cap.
Combat feel inspired by the TMNT arcade. Hosted on itch.io (free).

## Art direction
- Style: chunky pixel art, 32x48px characters.
- **Current art: procedurally-generated CC0 placeholders** (`tools/generate_sprites.py`)
  — animated idle/run/attack/hurt/dead per character. NOT hand-edited; regenerate
  via the script. Phase 2: swap in a real pack (Kenney/itch.io) or Aseprite art by
  replacing `assets/sprites/*.png` + the SpriteFrames anim names.
- All texture imports: Filter = Nearest (project default_texture_filter = 0).
- Resolution: 1280x720, stretch mode `canvas_items`, aspect `keep`.

## Tech stack
- Engine: Godot 4.6.x. GDScript only, no C#.
- Target: HTML5 export → itch.io free hosting (deploy via `Taskfile.yml`,
  `butler push`). The nothreads build needs no COOP/COEP headers.
- Save: localStorage via JavaScriptBridge on web, `user://` JSON elsewhere.
- **Signals over direct calls everywhere.**

## Core mechanic: weapon vs enemy type
Each enemy type has ONE weapon weakness. Hero carries ALL unlocked weapons at once,
switched with number keys.

| Enemy  | Weakness  | Key | Weapon style                 |
|--------|-----------|-----|------------------------------|
| Zombie | Shovel    | 1   | melee (overhead chop)        |
| Robot  | Laser gun | 2   | **ranged** (fires LaserBolt) |
| Pirate | Sabre     | 3   | melee (slash)                |

- Correct weapon = 100% damage (`Outcome.WEAK`). Wrong = 25% chip (`Outcome.CHIP`).
- Weapons: **pickaxe** (vs zombie, melee), **glow sword** (vs robot, ranged blue bolt),
  **whip** (vs pirate, mid-range melee — larger `melee_reach`).
- Hero plays a **distinct attack animation per weapon** (`attack_pickaxe` /
  `attack_glowsword` / `attack_whip`), driven by `weapon.attack_anim`.
- Enemy telegraphs its weakness above its head for 1.5s before attacking; the HUD
  also shows "USE: <weapon>".
- Weapon hotkeys match `event.physical_keycode` so 1/2/3 work on any keyboard
  layout (the dev uses AZERTY).
- Phase 2 later: correct weapon + perfect timing = 150% + special animation.

## Progression (4 levels, gentle ramp)
- **L1** zombies only — start with the pickaxe. Clear → unlock glow sword.
- **L2** robots only — use the glow sword. Clear → unlock whip.
- **L3** zombies + robots (mixed) — switch pickaxe/glow sword. Clear → skin.
- **L4** zombies + robots + pirates (mixed) — all three weapons. Final.
- Zones: `level_0N_zone.tres`; mixed waves use `enemy_scenes[]`. Levels chain via
  `next_level_scene`; unlock screen advances to it (empty = replay).
- Unlocks persist via GameState autoload → localStorage.

## Actual structure
```
res://
├── main.tscn / main.gd          # bootstrap → loads level_01
├── project.godot                # autoloads, input map, 1280x720 canvas_items
├── export_presets.cfg           # Web preset (build/index.html)
├── Taskfile.yml                 # build / serve / itch:* / deploy
├── tools/generate_sprites.py    # regenerates CC0 sprites + SpriteFrames
├── scenes/
│   ├── world/  level_01.tscn, level_02.tscn (share level_01.gd), hud, zone.gd
│   ├── entities/ character_base (+states/), hero, enemy_base, zombie/robot/pirate,
│   │             projectile.gd, laser_bolt.tscn
│   └── ui/ unlock_screen, character_select (stub)
├── scripts/ game_state.gd, combat_system.gd (autoloads), enemy_spawner.gd, weapon.gd
├── resources/ weapons/*.tres, zones/*.tres, sprite_frames/*.tres
└── assets/ sprites/ (generated PNGs), fonts/
```

## Resource specs (current)
- **weapon.gd**: `id, display_name, damage_multiplier, hotkey: Key, placeholder_color,
  sprite, attack_anim, ranged: bool, projectile_scene: PackedScene`.
- **zone.gd**: `enemy_scene, enemy_scenes: Array[PackedScene] (mixed waves),
  enemy_count, spawn_interval, next_zone, camera_target_x (stubbed)`.
- **combat_system.gd**: `enum Outcome { WEAK, CHIP }`, `resolve_hit(weapon_id, enemy)`,
  `damage_for(outcome, base)`, signal `attack_resolved`.
- **StateMachine**: states IDLE/RUN/ATTACK/HURT/DEAD as separate scripts in
  `scenes/entities/states/`; transitions by emitting `transitioned`; HURT/DEAD forced
  from the character's `hurt`/`died` signals via `force_transition`.

## Status — DONE
Bootstrap + scaffolding, save/load, combat, hero inventory + hotkeys, telegraph,
HUD weapon strip, **4-level progression** (zombie → robot → mixed → all three), unlock
flow, **LPC character art** (`tools/gen_lpc_character.py`), pickaxe/glow sword/whip with
per-weapon attack anims + reach, ranged glow-sword bolt, Web export + itch.io Taskfile.

## Out of scope / TODO
- **Held-weapon overlays**: show the actual pickaxe/sword/whip sprite in the hero's
  hand. Only sword-type overlays cleanly fit the base body's `slash`; see
  `docs/lpc-characters.md`. Aliens roster.
- Audio, main menu / title screen.
- Camera scrolling (`zone.camera_target_x` stubbed).
- Perfect-timing mechanic (Phase 2), gamepad, mobile touch.
- Hero skin actually changing visuals (unlock tracked, art not yet swapped).
