extends Node
class_name State
## Base class for every state in an entity's StateMachine.
## States never call each other directly; they request a change by emitting
## `transitioned`, which the StateMachine listens for (signals over calls).

signal transitioned(next_state_name: String)

## The CharacterBody2D this state machine drives. Injected by StateMachine.setup().
var character: Node = null


func enter() -> void:
	pass


func exit() -> void:
	pass


func update(_delta: float) -> void:
	pass


func physics_update(_delta: float) -> void:
	pass


func handle_input(_event: InputEvent) -> void:
	pass
