extends State
## ATTACK: locked in place for the swing duration, then back to IDLE.
## The actual hit resolution happens in character.perform_attack().

var _timer := 0.0


func enter() -> void:
	character.consume_attack()
	_timer = character.perform_attack()
	character.velocity = Vector2.ZERO


func physics_update(delta: float) -> void:
	if character.is_dead:
		return
	character.move_and_slide()
	_timer -= delta
	if _timer <= 0.0:
		transitioned.emit("Idle")
