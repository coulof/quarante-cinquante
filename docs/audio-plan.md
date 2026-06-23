# Plan: Game audio — sound list to record + integration

## Context
The game has no audio yet. The dev will **record the sound effects themselves** and
needs a definitive, organized list of what to record. Every sound below is tied to a
real game event/signal so it maps cleanly to where it will trigger. After the dev
records them, a small signal-driven `Audio` autoload plays them — built to no-op for
any clip not yet recorded, so partial sound sets work immediately.

Engine is signal-based already (see the signal inventory in `combat_system.gd`,
`character_base.gd`, `enemy_base.gd`, `hero.gd`, `enemy_spawner.gd`, `unlock_screen.gd`),
so wiring audio means connecting to existing signals — no gameplay rewrites.

---

## THE SOUND LIST (what to record)

### 1. Hero (voice / foley)
| File | Triggers on | Notes |
|------|-------------|-------|
| `hero_hurt` | hero `hurt` signal (took damage) | short "ow!"/grunt; record **2–3 takes** → randomized |
| `hero_die` | hero `died` → lose | defeated cry |

### 2. Enemies (voice / foley) — one hurt + one death each
| File | Triggers on | Notes |
|------|-------------|-------|
| `zombie_hurt` / `zombie_die` | zombie `hurt` / `died` | groan / death moan |
| `robot_hurt` / `robot_die` | robot `hurt` / `died` | metallic clank / power-down (a little explosion) |
| `pirate_hurt` / `pirate_die` | pirate `hurt` / `died` | "argh!" / yell |
| `enemy_attack` | enemy `perform_attack` (melee) | shared lunge/grunt (per-type optional later) |
| `telegraph` | enemy `telegraph_started` | wind-up "tell" cue (alert beep / inhale) |
| `robot_laser` | robot ranged `_fire_projectile` | laser/zap fire |

### 3. Hero weapons (the swing/use sound)
| File | Triggers on | Notes |
|------|-------------|-------|
| `wpn_pickaxe` | pickaxe attack (`_swing`) | heavy whoosh + thud |
| `wpn_glowsword` | glow-sword fire (`_fire_projectile_delayed`) | energy hum + zap |
| `wpn_whip` | whip attack (`_swing`) | whip crack |

### 4. Combat feedback (hit results — `CombatSystem.attack_resolved`)
| File | Triggers on | Notes |
|------|-------------|-------|
| `hit_weak` | `Outcome.WEAK` (correct weapon) | satisfying solid impact |
| `hit_chip` | `Outcome.CHIP` (wrong weapon) | dull/weak clink (teaches "wrong weapon") |
| `enemy_bolt_hit` | hostile bolt hits hero | zap impact (can reuse `hero_hurt`) |

### 5. Flow / UI / win-lose
| File | Triggers on | Notes |
|------|-------------|-------|
| `ui_weapon_switch` | `hero.weapon_switched` | quick blip/click |
| `ui_confirm` | unlock-screen continue (`continued`) | button confirm |
| `wave_clear` | spawner `zone_cleared` | short positive jingle |
| `unlock_fanfare` | level cleared / unlock screen shown | "new weapon!" celebratory sting |
| `win` | final level cleared (`all_zones_cleared`, no next) | victory sting |
| `lose` | hero `died` (level restart) | game-over sting |
| `level_start` | level `_ready` | short "go!" cue *(optional)* |

### 6. Ambience / music *(optional — may not be "recorded"; can be separate)*
| File | Triggers on | Notes |
|------|-------------|-------|
| `music_gameplay` | per-level loop | calm desert track (looping) |
| `ambient_wind` | level loop | soft desert wind *(optional)* |
| `hero_step` | run state | footstep *(optional, often skipped)* |

**Minimum viable set** (biggest impact first): `hit_weak`, `hit_chip`, the 3
`wpn_*`, `hero_hurt`, the 3 `*_die`, `unlock_fanfare`, `win`, `lose`,
`ui_weapon_switch`. Everything else layers on top.

---

## Recording specs
- **Format:** mono **WAV** for SFX (easy to trim); **OGG Vorbis** for music/loops.
  (I convert/import as needed; the web export prefers OGG for size.)
- **Length:** SFX ~0.15–1.0s; trim silence at head/tail.
- **Naming:** exactly the `File` column, lowercase: `assets/audio/sfx/<name>.wav`,
  music in `assets/audio/music/<name>.ogg`. Multiple takes → `hero_hurt_1/2/3`.
- Keep levels consistent / not clipping; I'll normalize on import if needed.

---

## Integration (after recording — the code work)
- **New autoload `Audio`** (`scripts/audio.gd`, registered in `project.godot`):
  - On `_ready`, scans `assets/audio/sfx/` and builds `name -> AudioStream` (so any
    file you drop in "just works"; missing names **no-op**, so partial sets are fine).
  - `play(name)` via a small pool of `AudioStreamPlayer`s (round-robin); auto-picks a
    random `_1/_2/_3` variant if present. `play_music(name, loop=true)` on a dedicated
    player. Simple `master`/`sfx`/`music` buses for volume.
- **Wire to existing signals (centralized, minimal edits):**
  - `CombatSystem.attack_resolved` → `hit_weak` / `hit_chip`.
  - `hero.weapon_switched` → `ui_weapon_switch`; hero `hurt`/`died` → `hero_hurt`/`lose`.
  - In `enemy_base.gd`: `telegraph_started` → `telegraph`; `_fire_projectile` →
    `robot_laser`; melee `perform_attack` → `enemy_attack`; connect each enemy's
    `hurt`/`died` to its `<type>_hurt`/`<type>_die` (add an exported `sfx_id` on enemies,
    e.g. "zombie"/"robot"/"pirate").
  - In `hero.gd`: `_swing`/`_fire_projectile_delayed` → the active `wpn_*`.
  - `enemy_spawner.zone_cleared` → `wave_clear`; level clear/unlock screen →
    `unlock_fanfare`; `_on_hero_died` → `lose`; final-level clear → `win`.
- **Files touched:** new `scripts/audio.gd`; `project.godot` (autoload); light
  `Audio.play(...)` calls in `hero.gd`, `enemy_base.gd`, `level_01.gd`,
  `unlock_screen.gd`; per-enemy `sfx_id` in `zombie/robot/pirate.tscn`.
- Docs: note the audio system + the sound-name contract in `CLAUDE.md`.

## Verification
- Drop a few WAVs in `assets/audio/sfx/`, `godot --headless --import`, then
  `godot --headless --quit-after 300` (and level_02) → clean output, no missing-resource
  errors (missing clips no-op).
- In-editor F5: switch weapons (blip), hit zombie with pickaxe (`hit_weak`) vs wrong
  weapon (`hit_chip`), take a robot bolt (`hero_hurt`), clear L1 (`wave_clear` +
  `unlock_fanfare`), die (`lose`), beat L4 (`win`).
