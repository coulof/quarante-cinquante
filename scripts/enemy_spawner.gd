extends Node
class_name EnemySpawner
## Zone-based wave controller. Spawns a zone's enemies over time, tracks how many
## are still alive, and advances to next_zone when the zone is cleared.

signal enemy_spawned(enemy: Node)
signal wave_progress(remaining: int, total: int)
signal zone_cleared(zone: Zone)
signal all_zones_cleared

@export var first_zone: Zone
## Rectangle (in the level's world space) where enemies appear.
@export var spawn_area: Rect2 = Rect2(960, 220, 260, 300)

var _enemies_root: Node = null
var _current_zone: Zone = null
var _to_spawn: int = 0
var _spawned: int = 0
var _alive: int = 0
var _spawn_timer: float = 0.0
var _rng := RandomNumberGenerator.new()


func start(enemies_root: Node) -> void:
	_enemies_root = enemies_root
	_rng.randomize()
	_begin_zone(first_zone)


func _begin_zone(zone: Zone) -> void:
	_current_zone = zone
	if zone == null:
		all_zones_cleared.emit()
		set_process(false)
		return
	_to_spawn = zone.enemy_count
	_spawned = 0
	_alive = 0
	_spawn_timer = 0.0
	wave_progress.emit(_remaining(), _current_zone.enemy_count)


func _process(delta: float) -> void:
	if _current_zone == null:
		return
	if _spawned < _to_spawn:
		_spawn_timer -= delta
		if _spawn_timer <= 0.0:
			_spawn_one()
			_spawn_timer = _current_zone.spawn_interval


func _pick_scene() -> PackedScene:
	if not _current_zone.enemy_scenes.is_empty():
		return _current_zone.enemy_scenes[_rng.randi_range(0, _current_zone.enemy_scenes.size() - 1)]
	return _current_zone.enemy_scene


func _spawn_one() -> void:
	var enemy := _pick_scene().instantiate()
	_enemies_root.add_child(enemy)
	enemy.global_position = _random_spawn_point()
	_spawned += 1
	_alive += 1
	enemy.died.connect(_on_enemy_died)
	enemy_spawned.emit(enemy)
	wave_progress.emit(_remaining(), _current_zone.enemy_count)


func _on_enemy_died() -> void:
	_alive -= 1
	wave_progress.emit(_remaining(), _current_zone.enemy_count)
	if _alive <= 0 and _spawned >= _to_spawn:
		var cleared := _current_zone
		zone_cleared.emit(cleared)
		_begin_zone(cleared.next_zone)


func _remaining() -> int:
	return (_to_spawn - _spawned) + _alive


func _random_spawn_point() -> Vector2:
	return Vector2(
		_rng.randf_range(spawn_area.position.x, spawn_area.end.x),
		_rng.randf_range(spawn_area.position.y, spawn_area.end.y)
	)
