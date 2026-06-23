extends CharacterBase
class_name EnemyBase
## Walks toward the hero, telegraphs its weakness above its head for
## `telegraph_time` seconds, then attacks. Each enemy type sets `weakness`.

signal telegraph_started(weakness: String)
signal telegraph_ended

@export var weakness: String = "pickaxe"
@export var attack_range: float = 52.0
@export var detection_range: float = 800.0
@export var telegraph_time: float = 1.5
@export var attack_cooldown: float = 1.2
## Ranged enemies (e.g. the robot) fire `projectile_scene` at the hero instead of a
## melee hit. Give them a larger `attack_range` so they keep their distance.
@export var ranged: bool = false
@export var projectile_scene: PackedScene

var target: Node2D = null

var _attack_intent := false
var _cooldown := 0.0
var _telegraphing := false
var _telegraph_timer := 0.0

@onready var telegraph_icon: Label = $TelegraphIcon


func _setup() -> void:
	add_to_group("enemies")
	_show_telegraph(false)
	_acquire_target()


func _acquire_target() -> void:
	target = get_tree().get_first_node_in_group("hero")


func _process(delta: float) -> void:
	if is_dead:
		return
	if target == null or not is_instance_valid(target):
		_acquire_target()
		return

	if _cooldown > 0.0:
		_cooldown -= delta

	var dist := global_position.distance_to(target.global_position)
	if dist <= attack_range:
		if _telegraphing:
			_telegraph_timer -= delta
			if _telegraph_timer <= 0.0:
				_end_telegraph()
				_attack_intent = true
				_cooldown = attack_cooldown
		elif _cooldown <= 0.0:
			_begin_telegraph()
	elif _telegraphing:
		# Hero escaped the strike zone: abandon the wind-up.
		_end_telegraph()


func _begin_telegraph() -> void:
	_telegraphing = true
	_telegraph_timer = telegraph_time
	_show_telegraph(true)
	telegraph_started.emit(weakness)
	Audio.play("telegraph")


func _end_telegraph() -> void:
	if not _telegraphing:
		return
	_telegraphing = false
	_show_telegraph(false)
	telegraph_ended.emit()


func _show_telegraph(visible_now: bool) -> void:
	if telegraph_icon:
		telegraph_icon.visible = visible_now
		if visible_now:
			telegraph_icon.text = weakness.to_upper()


# --- State interface ----------------------------------------------------------
func get_desired_velocity() -> Vector2:
	if target == null or _telegraphing or is_dead:
		return Vector2.ZERO
	var dist := global_position.distance_to(target.global_position)
	if dist <= attack_range or dist > detection_range:
		return Vector2.ZERO
	return (target.global_position - global_position).normalized()


func wants_to_attack() -> bool:
	return _attack_intent


func consume_attack() -> void:
	_attack_intent = false


func perform_attack() -> float:
	if target != null and is_instance_valid(target) and not target.is_dead:
		if ranged and projectile_scene != null:
			_fire_projectile()
		elif global_position.distance_to(target.global_position) <= attack_range * 1.2:
			if target.has_method("take_damage"):
				target.take_damage(base_damage, global_position)
				Audio.play("enemy_attack")
	return attack_duration


## Fire a hostile bolt at the hero (ranged enemies). The bolt's scene sets hostile +
## its collision mask, so it only hits the hero and deals flat `base_damage`.
func _fire_projectile() -> void:
	Audio.play("robot_laser")
	var bolt: Projectile = projectile_scene.instantiate()
	get_parent().add_child(bolt)
	var dir := (target.global_position - global_position).normalized()
	face(dir.x)
	bolt.setup(weakness, base_damage, dir, global_position + dir * 18.0 + Vector2(0, -28))
