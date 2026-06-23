extends CanvasLayer
## Shown when a level is cleared. Announces the newly unlocked weapon + skin,
## then replays the level when the player continues.

signal continued

@onready var title_label: Label = $Center/Panel/VBox/Title
@onready var weapon_label: Label = $Center/Panel/VBox/WeaponLine
@onready var skin_label: Label = $Center/Panel/VBox/SkinLine
@onready var continue_button: Button = $Center/Panel/VBox/ContinueButton

var _next_scene: String = ""
var _done := false


func _ready() -> void:
	continue_button.pressed.connect(_on_continue)          # desktop mouse + keyboard
	# Touch: Button.pressed doesn't fire from touch with emulate_mouse_from_touch off.
	continue_button.gui_input.connect(func(e: InputEvent):
		if e is InputEventScreenTouch and e.pressed:
			_on_continue())
	continue_button.grab_focus()


func setup(weapon_name: String, skin_name: String, next_scene: String = "") -> void:
	_next_scene = next_scene
	if next_scene == "":
		# Final level cleared → win / ending screen.
		title_label.text = "YOU WIN! 🎉"
		weapon_label.text = "You cleared every level!"
		weapon_label.visible = true
		skin_label.text = "Thanks for playing 🏆"
		skin_label.visible = true
		continue_button.text = "Play again"
	else:
		if weapon_name.is_empty():
			weapon_label.visible = false
		else:
			weapon_label.text = "New weapon: %s" % weapon_name
		if skin_name.is_empty():
			skin_label.visible = false
		else:
			skin_label.text = "New hero skin: %s" % skin_name
	_spawn_confetti(next_scene == "")   # bigger burst on the final level (win)


## A one-shot rain of colored confetti from the top of the screen.
func _spawn_confetti(big: bool) -> void:
	var img := Image.create(6, 6, false, Image.FORMAT_RGBA8)
	img.fill(Color.WHITE)
	var tex := ImageTexture.create_from_image(img)
	var colors := [
		Color(0.96, 0.62, 0.20), Color(0.25, 0.80, 1.0), Color(0.92, 0.36, 0.43),
		Color(0.40, 0.85, 0.50), Color(0.97, 0.90, 0.30), Color(0.70, 0.50, 0.95),
	]
	for c in colors:
		var p := CPUParticles2D.new()
		p.texture = tex
		p.color = c
		p.position = Vector2(640, -16)            # top-centre (screen space; 1280x720)
		p.one_shot = true
		p.explosiveness = 0.85
		p.amount = 34 if big else 20
		p.lifetime = 2.4
		p.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
		p.emission_rect_extents = Vector2(640, 8)  # full width
		p.direction = Vector2(0, 1)
		p.spread = 30.0
		p.gravity = Vector2(0, 430)
		p.initial_velocity_min = 120.0
		p.initial_velocity_max = 260.0
		p.angular_velocity_min = -480.0
		p.angular_velocity_max = 480.0
		p.scale_amount_min = 2.0
		p.scale_amount_max = 4.0
		add_child(p)
		p.emitting = true
		get_tree().create_timer(p.lifetime + 0.5).timeout.connect(p.queue_free)


func _on_continue() -> void:
	if _done:           # guard against mouse + touch both firing
		return
	_done = true
	Audio.play("ui_confirm")
	continued.emit()
	if _next_scene.is_empty():
		# Win → fresh run from Level 1 (session-only progress resets to the pickaxe).
		GameState.reset()
		get_tree().change_scene_to_file("res://scenes/world/level_01.tscn")
	else:
		get_tree().change_scene_to_file(_next_scene)
