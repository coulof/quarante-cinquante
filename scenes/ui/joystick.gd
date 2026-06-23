extends Control
## On-screen virtual joystick for touch. Drives the `move_*` input actions (full
## strength past a per-axis threshold → clean 8-way), so the hero's movement
## (`Input.get_vector` in get_desired_velocity) works unchanged. Dynamic base: the
## stick centres wherever you first press inside this control. Handles both touch
## (mobile) and mouse (editor testing).

const RADIUS := 90.0
const AXIS_THRESHOLD := 0.35   # fraction of RADIUS before an axis engages

var _active := false
var _origin := Vector2.ZERO
var _knob := Vector2.ZERO


func _gui_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch or event is InputEventMouseButton:
		if event.pressed:
			_active = true
			_origin = event.position
			_knob = event.position
			_apply(Vector2.ZERO)
		else:
			_active = false
			_apply(Vector2.ZERO)
		queue_redraw()
		accept_event()
	elif _active and (event is InputEventScreenDrag or event is InputEventMouseMotion):
		_knob = _origin + (event.position - _origin).limit_length(RADIUS)
		_apply((_knob - _origin) / RADIUS)
		queue_redraw()
		accept_event()


func _apply(vec: Vector2) -> void:
	_axis("move_left", "move_right", vec.x)
	_axis("move_up", "move_down", vec.y)


func _axis(neg: String, pos: String, v: float) -> void:
	if v > AXIS_THRESHOLD:
		Input.action_release(neg)
		Input.action_press(pos, 1.0)
	elif v < -AXIS_THRESHOLD:
		Input.action_release(pos)
		Input.action_press(neg, 1.0)
	else:
		Input.action_release(neg)
		Input.action_release(pos)


func _draw() -> void:
	var base := _origin if _active else Vector2(RADIUS + 24, size.y - RADIUS - 24)
	var knob := _knob if _active else base
	draw_circle(base, RADIUS, Color(1, 1, 1, 0.10))
	draw_circle(base, RADIUS, Color(1, 1, 1, 0.18), false, 3.0)
	draw_circle(knob, RADIUS * 0.45, Color(1, 1, 1, 0.28))
