extends State
## IDLE: standing still. Leaves for ATTACK on attack intent, RUN on movement.


func physics_update(_delta: float) -> void:
	if character.is_dead:
		return
	character.velocity = Vector2.ZERO
	character.move_and_slide()

	if character.wants_to_attack():
		transitioned.emit("Attack")
	elif character.get_desired_velocity().length() > 0.1:
		transitioned.emit("Run")
