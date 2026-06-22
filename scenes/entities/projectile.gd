extends Area2D
class_name Projectile
## A travelling shot (e.g. laser bolt). Resolves combat through the CombatSystem
## on the first enemy it touches, so a ranged weapon still respects weaknesses.

@export var speed: float = 720.0
@export var lifetime: float = 1.1

var weapon_id: String = "laser"
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
	if body is CharacterBase and "weakness" in body and not body.is_dead:
		var outcome := CombatSystem.resolve_hit(weapon_id, body)
		body.take_damage(CombatSystem.damage_for(outcome, damage), global_position)
		queue_free()
