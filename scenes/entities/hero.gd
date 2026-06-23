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
## The shared bare-handed hero sheet, used when a weapon has no in-hand `frames`.
var _default_frames: SpriteFrames = null

const ENEMY_MASK := 4  # enemies live on collision layer 3 (bit value 4)


func _setup() -> void:
	add_to_group("hero")
	_default_frames = visual.sprite_frames
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
	# Swap to the weapon's in-hand sheet (or the shared bare-handed one), keeping
	# whatever animation is currently playing (idle/run) running on the new frames.
	var wanted: SpriteFrames = weapon.frames if weapon.frames != null else _default_frames
	if wanted != null and visual.sprite_frames != wanted:
		var anim := visual.animation
		visual.sprite_frames = wanted
		if wanted.has_animation(anim):
			visual.play(anim)
	weapon_switched.emit(weapon)


func _unhandled_input(event: InputEvent) -> void:
	if is_dead:
		return
	if event is InputEventKey and event.pressed and not event.echo:
		for w in available_weapons:
			# Match physical position so 1/2/3 work on any keyboard layout (AZERTY etc.).
			if event.physical_keycode == w.hotkey:
				_select(w)
				Audio.play("ui_weapon_switch")
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
		Audio.play("wpn_" + current_weapon.id)
		if current_weapon.ranged:
			# Fire near the end of the swing so the bolt leaves as the blade finishes.
			_fire_projectile_delayed(attack_duration * 0.65)
		else:
			_swing()
	return attack_duration


## Spawn the projectile after `delay`s (coroutine — perform_attack returns immediately).
func _fire_projectile_delayed(delay: float) -> void:
	var weapon := current_weapon
	await get_tree().create_timer(delay).timeout
	# Still alive and still wielding the same ranged weapon?
	if is_dead or current_weapon != weapon or not weapon.ranged:
		return
	_fire_projectile()


## Hero plays a weapon-specific attack animation. In-hand weapon sheets use a single
## "attack"; the shared sheet uses the per-weapon `attack_anim` (attack_pickaxe, ...).
func get_attack_anim() -> String:
	if current_weapon != null and current_weapon.frames != null:
		return "attack"
	if current_weapon != null and not current_weapon.attack_anim.is_empty():
		return current_weapon.attack_anim
	return "attack"


func _fire_projectile() -> void:
	if current_weapon.projectile_scene == null:
		return
	var bolt: Projectile = current_weapon.projectile_scene.instantiate()
	get_parent().add_child(bolt)
	var muzzle := global_position + Vector2(facing * 24.0, -attack_height * 0.5)
	bolt.setup(current_weapon.id, base_damage * current_weapon.damage_multiplier,
		Vector2(facing, 0.0), muzzle)


func _swing() -> void:
	# Whip and other mid-range weapons override the default reach.
	var reach := attack_reach
	if current_weapon != null and current_weapon.melee_reach > 0.0:
		reach = current_weapon.melee_reach
	var space := get_world_2d().direct_space_state
	var query := PhysicsShapeQueryParameters2D.new()
	var shape := RectangleShape2D.new()
	shape.size = Vector2(reach, attack_height)
	query.shape = shape
	# Centre the swing box in front of the hero, on the facing side.
	query.transform = Transform2D(0.0, global_position + Vector2(facing * reach * 0.6, -attack_height * 0.5))
	query.collision_mask = ENEMY_MASK
	query.collide_with_bodies = true

	for hit in space.intersect_shape(query, 16):
		var enemy = hit.get("collider")
		if enemy is CharacterBase and "weakness" in enemy and not enemy.is_dead:
			var outcome := CombatSystem.resolve_hit(current_weapon.id, enemy)
			var dmg := CombatSystem.damage_for(outcome, base_damage * current_weapon.damage_multiplier)
			enemy.take_damage(dmg, global_position)
