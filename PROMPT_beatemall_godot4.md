# Browser Beat-em-all — Godot 4 Project Bootstrap
> Prompt for Claude Code — recommended model: **claude-sonnet-4-6**

---

## Project vision
2D pixel art beat-em-all playable in browser (HTML5), designed for a 7-year-old audience.
Kid-friendly enemies (Zombies, Robots, Pirates, Aliens…). Hero: a boy with a cap (Link-ish).
Combat feel inspired by TMNT arcade. Hosted on Cloudflare Pages.

## Art direction
- Style: chunky pixel art, 32x48px characters
- Phase 1: use a free asset pack (Kenney.nl or Tiny RPG on itch.io) — no custom art yet
- Phase 2 (later): custom sprites via Aseprite
- All imports: Filter = Nearest, no anti-aliasing, compress/mode = 0
- Resolution: 1280x720, pixel-perfect scaling
  (Project > Display > Window > Stretch mode = canvas, aspect = keep)

## Tech stack
- Engine: Godot 4.x
- Language: GDScript only, no C#
- Target: HTML5 export → Cloudflare Pages
  (requires COOP/COEP headers via `_headers` file at repo root)
- Save: localStorage via JavaScriptBridge (user:// doesn't persist in browser)
- Signals over direct calls everywhere

## Core game mechanic: weapon vs enemy type
Each enemy type has ONE weapon weakness.
Starter roster:

| Enemy  | Weakness  | Key |
|--------|-----------|-----|
| Zombie | Shovel    | 1   |
| Robot  | Laser gun | 2   |
| Pirate | Sabre     | 3   |

- Hero carries ALL unlocked weapons simultaneously, switched with number keys 1/2/3…
- Wrong weapon on enemy = 25% damage (chip). Correct weapon = 100% + hit animation.
- Enemy telegraphs its type via icon above head for 1.5s before attacking.
- Phase 2 later: correct weapon + perfect timing = 150% + special animation.

## Progression system
- Start: hero + shovel only. One enemy type (Zombie).
- Level 2 unlock: new weapon (Laser) + new enemy type (Robot).
- Level 3 unlock: new weapon (Sabre) + new enemy type (Pirate).
- Unlock = new skin for hero (visually distinct special attack animation, same stats).
- Unlocks persist via JavaScriptBridge → localStorage.

## Scene tree to scaffold

```
res://
├── main.tscn                    # Root: bootstraps GameState, loads first scene
├── export_presets.cfg           # HTML5 preset pre-configured
├── _headers                     # Cloudflare Pages COOP/COEP headers
├── scenes/
│   ├── world/
│   │   ├── level_01.tscn        # Arena (fixed camera), Zombie waves only
│   │   ├── zone.gd              # Resource: enemy list, clear trigger, next zone ref
│   │   └── hud.tscn             # HP bar, active weapon indicator, enemy type icon
│   ├── entities/
│   │   ├── character_base.tscn  # CharacterBody2D base, StateMachine, AnimatedSprite2D
│   │   ├── hero.tscn            # Extends character_base, weapon inventory, input
│   │   ├── enemy_base.tscn      # Extends character_base, weakness: String, patrol AI
│   │   ├── zombie.tscn          # weakness = "shovel"
│   │   ├── robot.tscn           # weakness = "laser"
│   │   └── pirate.tscn          # weakness = "sabre"
│   └── ui/
│       ├── character_select.tscn
│       └── unlock_screen.tscn
├── scripts/
│   ├── game_state.gd            # Autoload: unlocks, active skin, save/load via JS bridge
│   ├── combat_system.gd         # resolve_hit(attacker_weapon, defender_weakness) → outcome
│   ├── enemy_spawner.gd         # Zone-based wave controller
│   └── weapon.gd                # Resource: id, display_name, damage_mult, key, sprite
└── assets/
    ├── sprites/                 # Asset pack sprites dropped here
    └── fonts/                   # Pixel font (Kenney Pixel or similar)
```

## Key scripts spec

### game_state.gd (Autoload)
```gdscript
# Persisted fields (localStorage via JavaScriptBridge)
var unlocked_weapons: Array[String] = ["shovel"]
var unlocked_skins: Array[String]   = ["hero_default"]
var active_skin: String             = "hero_default"
var highest_level: int              = 1

func save() -> void  # JSON → JavaScriptBridge.eval("localStorage.setItem(...)")
func load() -> void  # JavaScriptBridge.eval("localStorage.getItem(...)") → parse
```

### combat_system.gd
```gdscript
enum Outcome { WEAK, CHIP }

signal attack_resolved(outcome: Outcome, target: Node)

func resolve_hit(weapon_id: String, enemy: Node) -> Outcome:
    if weapon_id == enemy.weakness:
        return Outcome.WEAK   # 100% damage + hit anim
    return Outcome.CHIP       # 25% damage
```

### zone.gd (Resource)
```gdscript
@export var enemy_scene: PackedScene
@export var enemy_count: int
@export var spawn_interval: float
@export var next_zone: Resource     # null = level complete
# Camera scroll target pre-defined here for future scroll support
@export var camera_target_x: float = 0.0
```

### weapon.gd (Resource)
```gdscript
@export var id: String              # "shovel", "laser", "sabre"
@export var display_name: String
@export var damage_multiplier: float
@export var hotkey: Key             # KEY_1, KEY_2, KEY_3
@export var sprite: Texture2D
```

## StateMachine pattern for entities
States: IDLE, RUN, ATTACK, HURT, DEAD
Transitions via signals, not direct method calls.
Each state is an inner class or separate script in a `states/` subfolder.

## _headers file (Cloudflare Pages)
```
/*
  Cross-Origin-Opener-Policy: same-origin
  Cross-Origin-Embedder-Policy: require-corp
```

## Immediate deliverables for this session
1. Full directory + file structure (empty scenes + stubbed scripts)
2. `game_state.gd` with working localStorage save/load via JavaScriptBridge
3. `combat_system.gd` with resolve_hit + signal
4. `weapon.gd` + 3 weapon Resources pre-filled (shovel, laser, sabre)
5. `character_base.tscn` + StateMachine (colored rect placeholder, no art)
6. `hero.tscn` — weapon inventory, hotkey switching (1/2/3), attack triggers combat_system
7. `zombie.tscn` — weakness="shovel", telegraph icon, basic patrol
8. `level_01.tscn` — fixed camera arena, Zone resource with 5 zombies, HUD wired
9. `export_presets.cfg` + `_headers` configured and ready
10. Game boots, one wave of zombies defeatable, unlock screen shows on clear

## Out of scope for this session
- Custom art (use colored rects + placeholder icons)
- Audio
- Main menu / title screen
- Levels 2 and 3 (architecture ready, content later)
- Camera scrolling (zone.camera_target_x stubbed, not activated)
- Perfect timing mechanic (Phase 2)
- Gamepad support
- Mobile touch controls
