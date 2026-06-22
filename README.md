# Browser Beat-em-all (Godot 4)

2D pixel-art beat-em-all for the browser, built in Godot 4.x / GDScript. Phase 1
uses colored-rectangle placeholders (no art yet).

## Run

```bash
godot --path .          # opens the editor
godot --path . main.tscn  # run the game directly
```

Boots `main.tscn` → loads `scenes/world/level_01.tscn` (one wave of 5 zombies).

### Controls

- **Move:** arrow keys / WASD
- **Attack:** Space (or left mouse)
- **Switch weapon:** `1` Shovel · `2` Laser · `3` Sabre (only unlocked ones work)

Each enemy has one weapon weakness (Zombie→Shovel, Robot→Laser, Pirate→Sabre).
Correct weapon = 100% damage, wrong weapon = 25% chip. Enemies telegraph their
type above their head for 1.5s before striking. Clear the wave → unlock screen.

## Web export & Cloudflare Pages

Everything is driven by [go-task](https://taskfile.dev) (`Taskfile.yml`):

```bash
task                 # list tasks
task templates       # one-time: download matching Godot export templates (~1.2 GB)
task build           # export Web build to build/ and copy the _headers file in
task serve           # preview locally via `wrangler pages dev` (applies _headers)

task cf:login        # one-time: authenticate wrangler with Cloudflare
task cf:create       # one-time: create the Pages project
task deploy          # build + deploy to production (main)
task cf:deploy       # build + deploy a preview
```

Set the Pages project name via the `PROJECT_NAME` var at the top of `Taskfile.yml`
(default `quarante-cinquante`). `GODOT_VERSION` must match your editor build so the
right export templates are installed.

`_headers` ships the COOP/COEP headers for cross-origin isolation and is copied
into `build/` on every `task build`. Saves persist to `localStorage` via
`JavaScriptBridge` on web, and to `user://` elsewhere.

## Layout

- `scripts/` — autoloads (`game_state`, `combat_system`), `enemy_spawner`, `weapon` resource
- `scenes/entities/` — `character_base` + StateMachine (`states/`), `hero`, `enemy_base`, enemy types
- `scenes/world/` — `level_01`, `hud`, `zone` resource
- `scenes/ui/` — `unlock_screen`, `character_select` (stub)
- `resources/` — weapon `.tres` files, level zone definitions
