extends Area2D
class_name Projectile
## A travelling shot. Hero bolts (hostile=false) resolve through the CombatSystem on
## the first enemy hit (weapon vs weakness). Enemy bolts (hostile=true) deal flat
## damage to the hero. Collision_mask on the scene decides which it can touch
## (hero bolt masks 4=enemies, enemy bolt masks 2=hero).

@export var speed: float = 720.0
@export var lifetime: float = 1.1
@export var hostile: bool = false

var weapon_id: String = "glowsword"
var damage: float = 30.0
var direction: Vector2 = Vector2.RIGHT


func setup(p_weapon_id: String, p_damage: float, p_direction: Vector2, p_position: Vector2) -> void:
	weapon_id = p_weapon_id
	damage = p_damage
	direction = p_direction.normalized()
	global_position = p_position
	if direction.x < 0:
		scale.x = -1.0


func _ready() -> void:
	body_entered.connect(_on_body_entered)
	get_tree().create_timer(lifetime).timeout.connect(queue_free)


func _physics_process(delta: float) -> void:
	global_position += direction * speed * delta


func _on_body_entered(body: Node) -> void:
	if not (body is CharacterBase) or body.is_dead:
		return
	if hostile:
		# Enemy shot: flat damage to whatever it hit (its mask only sees the hero).
		body.take_damage(damage, global_position)
	elif "weakness" in body:
		# Hero shot: weapon vs enemy weakness.
		var outcome := CombatSystem.resolve_hit(weapon_id, body)
		body.take_damage(CombatSystem.damage_for(outcome, damage), global_position)
	else:
		return
	queue_free()
