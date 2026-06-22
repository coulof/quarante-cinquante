extends Node
class_name StateMachine
## Generic finite state machine. Each child Node that extends State is registered
## by its (lower-cased) node name. The owning entity calls setup(self) once.

signal state_entered(state_name: String)

@export var initial_state_name: String = "Idle"

var current_state: State = null
var _states: Dictionary = {}
var _ready_done := false


func setup(character: Node) -> void:
	for child in get_children():
		if child is State:
			_states[child.name.to_lower()] = child
			child.character = character
			child.transitioned.connect(_on_state_transitioned)

	var start: State = _states.get(initial_state_name.to_lower())
	if start:
		current_state = start
		current_state.enter()
		state_entered.emit(start.name)
	_ready_done = true


func _process(delta: float) -> void:
	if _ready_done and current_state:
		current_state.update(delta)


func _physics_process(delta: float) -> void:
	if _ready_done and current_state:
		current_state.physics_update(delta)


func _unhandled_input(event: InputEvent) -> void:
	if _ready_done and current_state:
		current_state.handle_input(event)


func is_in(state_name: String) -> bool:
	return current_state != null and current_state.name.to_lower() == state_name.to_lower()


## Used by the owning entity to react to its own gameplay signals (hurt/death),
## which can interrupt any current state.
func force_transition(state_name: String) -> void:
	_on_state_transitioned(state_name)


func _on_state_transitioned(next_state_name: String) -> void:
	var next: State = _states.get(next_state_name.to_lower())
	if next == null:
		push_warning("StateMachine: unknown state '%s'" % next_state_name)
		return
	if current_state:
		current_state.exit()
	current_state = next
	current_state.enter()
	state_entered.emit(current_state.name)
