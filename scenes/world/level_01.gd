extends Node2D
## Level 1 arena: fixed camera, one zone of zombies. Wires the hero, spawner and
## HUD together and shows the unlock screen on clear.

## Content unlocked by clearing this level (the level-2 weapon + a new skin).
@export var unlock_weapon_id: String = "glowsword"
@export var unlock_weapon_name: String = "Glow Sword"
@export var unlock_skin_id: String = "hero_robotslayer"
@export var unlock_skin_name: String = "Robot Slayer"
@export var next_level_index: int = 2
## Scene to load after the unlock screen. Empty = replay this level.
@export_file("*.tscn") var next_level_scene: String = ""

const UNLOCK_SCREEN := preload("res://scenes/ui/unlock_screen.tscn")

@onready var hero: Hero = $Hero
@onready var spawner: EnemySpawner = $EnemySpawner
@onready var enemies_root: Node2D = $Enemies
@onready var hud: Control = $HUDLayer/HUD

var _cleared := false


func _ready() -> void:
	GameState.reach_level(1)

	# Hero -> HUD
	hero.health_changed.connect(hud.set_health)
	hero.weapon_switched.connect(hud.set_weapon)
	hero.died.connect(_on_hero_died)
	hud.weapon_selected.connect(hero.select_weapon_id)
	hud.set_health(hero.health, hero.max_health)
	hud.set_weapons(hero.available_weapons, hero.current_weapon)

	# Spawner -> HUD / level
	spawner.wave_progress.connect(hud.set_wave)
	spawner.enemy_spawned.connect(_on_enemy_spawned)
	spawner.all_zones_cleared.connect(_on_level_cleared)
	spawner.zone_cleared.connect(func(_z): Audio.play("wave_clear"))

	Audio.play_music("music_gameplay")
	Audio.play("level_start")
	spawner.start(enemies_root)


func _on_enemy_spawned(enemy: Node) -> void:
	if enemy.has_signal("telegraph_started"):
		enemy.telegraph_started.connect(hud.show_enemy_type)
		enemy.telegraph_ended.connect(hud.hide_enemy_type)


func _on_level_cleared() -> void:
	if _cleared:
		return
	_cleared = true
	Audio.play("win" if next_level_scene == "" else "unlock_fanfare")

	GameState.unlock_weapon(unlock_weapon_id)
	GameState.unlock_skin(unlock_skin_id)
	GameState.reach_level(next_level_index)

	var screen := UNLOCK_SCREEN.instantiate()
	add_child(screen)
	screen.setup(unlock_weapon_name, unlock_skin_name, next_level_scene)


func _on_hero_died() -> void:
	Audio.play("lose")
	# Bootstrap behaviour: brief pause, then restart the arena.
	await get_tree().create_timer(1.5).timeout
	get_tree().reload_current_scene()


func _unhandled_input(event: InputEvent) -> void:
	# Debug only (editor / debug builds, NOT the itch release): F1 wipes saved progress
	# and restarts at level 1 with just the pickaxe — handy when testing the unlock flow.
	if not OS.is_debug_build():
		return
	if event is InputEventKey and event.pressed and not event.echo and event.keycode == KEY_F1:
		GameState.reset()
		get_tree().change_scene_to_file("res://scenes/world/level_01.tscn")
