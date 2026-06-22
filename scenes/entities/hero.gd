extends CharacterBase
class_name Hero
## Player character. Carries every unlocked weapon at once; number keys switch
## the active one. Attacking resolves each hit through the CombatSystem so the
## right weapon does full damage and the wrong one only chips.

signal weapon_switched(weapon: Weapon)

## All weapons that exist in the game, assigned in the scene (shovel/laser/sabre).
## Only those present in GameState.unlocked_weapons become selectable.
@export var all_weapons: Array[Weapon] = []
@export var attack_reach: float = 40.0
@export var attack_height: float = 44.0

var available_weapons: Array[Weapon] = []
var current_weapon: Weapon = null

var _attack_queued := false

const ENEMY_MASK := 4  # enemies live on collision layer 3 (bit value 4)


func _setup() -> void:
	add_to_group("hero")
	_refresh_weapons()
	GameState.weapon_unlocked.connect(func(_id: String): _refresh_weapons())


func _refresh_weapons() -> void:
	available_weapons.clear()
	for w in all_weapons:
		if w != null and GameState.has_weapon(w.id):
			available_weapons.append(w)
	if current_weapon == null or not GameState.has_weapon(current_weapon.id):
		if not available_weapons.is_empty():
			_select(available_weapons[0])


func _select(weapon: Weapon) -> void:
	current_weapon = weapon
	weapon_switched.emit(weapon)


func _unhandled_input(event: InputEvent) -> void:
	if is_dead:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		for w in available_weapons:
			if event.keycode == w.hotkey:
				_select(w)
				return
	if event.is_action_pressed("attack"):
		_attack_queued = true


# --- State interface ----------------------------------------------------------
func get_desired_velocity() -> Vector2:
	return Input.get_vector("move_left", "move_right", "move_up", "move_down")


func wants_to_attack() -> bool:
	return _attack_queued


func consume_attack() -> void:
	_attack_queued = false


func perform_attack() -> float:
	if current_weapon != null:
		_swing()
	return attack_duration


func _swing() -> void:
	var space := get_world_2d().direct_space_state
	var query := PhysicsShapeQueryParameters2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(attack_reach, attack_height)
	query.shape = shape
	# Centre the swing box in front of the hero, on the facing side.
	query.transform = Transform2D(0.0, global_position + Vector2(facing * attack_reach * 0.6, -attack_height * 0.5))
	query.collision_mask = ENEMY_MASK
	query.collide_with_bodies = true

	for hit in space.intersect_shape(query, 16):
		var enemy = hit.get("collider")
		if enemy is CharacterBase and "weakness" in enemy and not enemy.is_dead:
			var outcome := CombatSystem.resolve_hit(current_weapon.id, enemy)
			var dmg := CombatSystem.damage_for(outcome, base_damage * current_weapon.damage_multiplier)
			enemy.take_damage(dmg, global_position)
