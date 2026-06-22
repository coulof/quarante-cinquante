extends State
## RUN: moving on the arena floor. Leaves for ATTACK on intent, IDLE when stopped.


func physics_update(_delta: float) -> void:
	if character.is_dead:
		return
	if character.wants_to_attack():
		transitioned.emit("Attack")
		return

	var dir: Vector2 = character.get_desired_velocity()
	if dir.length() < 0.1:
		transitioned.emit("Idle")
		return

	character.velocity = dir * character.move_speed
	character.face(dir.x)
	character.move_and_slide()
