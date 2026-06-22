extends State
## HURT: brief stun + knockback after taking damage, then back to IDLE.

var _timer := 0.0


func enter() -> void:
	_timer = character.hurt_stun_time
	character.velocity = character.knockback_velocity


func physics_update(delta: float) -> void:
	# Decay the knockback so the stun ends with the character at rest.
	character.velocity = character.velocity.move_toward(Vector2.ZERO, character.move_speed * 4.0 * delta)
	character.move_and_slide()
	_timer -= delta
	if _timer <= 0.0:
		transitioned.emit("Idle")
