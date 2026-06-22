extends State
## DEAD: terminal state. Hands off to character.on_death() and never transitions out.


func enter() -> void:
	character.velocity = Vector2.ZERO
	character.on_death()
