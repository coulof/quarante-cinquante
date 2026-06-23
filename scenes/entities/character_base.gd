extends CharacterBody2D
class_name CharacterBase
## Shared base for hero and enemies: health, knockback, and a StateMachine.
## Subclasses provide intent (get_desired_velocity / wants_to_attack) and the
## attack itself (perform_attack). Everything talks through signals.

signal health_changed(current: float, maximum: float)
signal hurt
signal died

@export var max_health: float = 100.0
@export var move_speed: float = 160.0
@export var attack_duration: float = 0.35
@export var hurt_stun_time: float = 0.25
@export var knockback_strength: float = 220.0
## Base damage this character deals before the combat multiplier is applied.
@export var base_damage: float = 25.0
## Sound prefix for this character, e.g. "hero"/"zombie" → plays `<sfx_id>_hurt` /
## `<sfx_id>_die`. Empty = silent.
@export var sfx_id: String = ""

var health: float = 0.0
var is_dead: bool = false
var facing: int = 1
var knockback_velocity: Vector2 = Vector2.ZERO

@onready var state_machine: StateMachine = $StateMachine
@onready var visual: AnimatedSprite2D = $Visual


func _ready() -> void:
	health = max_health
	_setup()
	# Connect before setup() so the initial state's animation actually plays.
	state_machine.state_entered.connect(_on_state_entered)
	hurt.connect(_on_hurt)
	died.connect(_on_died)
	state_machine.setup(self)
	health_changed.emit(health, max_health)


## Subclass hook, runs before the state machine starts.
func _setup() -> void:
	pass


# --- Interface consumed by State scripts (override in subclasses) -------------
func get_desired_velocity() -> Vector2:
	return Vector2.ZERO


func wants_to_attack() -> bool:
	return false


func consume_attack() -> void:
	pass


## Returns how long the ATTACK state should last (seconds).
func perform_attack() -> float:
	return attack_duration


func on_death() -> void:
	collision_layer = 0
	collision_mask = 0
	var tween := create_tween()
	tween.tween_property(visual, "modulate:a", 0.0, 0.5)
	tween.tween_callback(queue_free)


# --- Combat -------------------------------------------------------------------
func take_damage(amount: float, from_position: Vector2 = global_position) -> void:
	if is_dead:
		return
	health = maxf(0.0, health - amount)
	health_changed.emit(health, max_health)

	var dir := (global_position - from_position)
	knockback_velocity = (dir.normalized() if dir.length() > 0.01 else Vector2.LEFT) * knockback_strength

	if health <= 0.0:
		is_dead = true
		died.emit()
	else:
		hurt.emit()


func face(dir_x: float) -> void:
	if absf(dir_x) < 0.01:
		return
	facing = 1 if dir_x > 0.0 else -1
	if visual:
		visual.flip_h = facing < 0


# --- Signal reactions ---------------------------------------------------------
func _on_hurt() -> void:
	if not is_dead:
		state_machine.force_transition("Hurt")
		if sfx_id != "":
			Audio.play(sfx_id + "_hurt")


func _on_died() -> void:
	state_machine.force_transition("Dead")
	if sfx_id != "":
		Audio.play(sfx_id + "_die")


## Which attack animation to play; hero overrides this to vary it per weapon.
func get_attack_anim() -> String:
	return "attack"


func _on_state_entered(state_name: String) -> void:
	var state := state_name.to_lower()
	var anim := get_attack_anim() if state == "attack" else state
	if visual and visual.sprite_frames:
		if visual.sprite_frames.has_animation(anim):
			visual.play(anim)
		elif visual.sprite_frames.has_animation("attack") and state == "attack":
			visual.play("attack")  # fallback if a weapon anim is missing
	if state == "hurt":
		_flash(Color(1, 0.45, 0.45))


func _flash(tint: Color) -> void:
	if not visual:
		return
	visual.modulate = tint
	var tween := create_tween()
	tween.tween_property(visual, "modulate", Color.WHITE, 0.25)
