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
	if weapon_name.is_empty():
		weapon_label.visible = false
	else:
		weapon_label.text = "New weapon: %s" % weapon_name
	if skin_name.is_empty():
		skin_label.visible = false
	else:
		skin_label.text = "New hero skin: %s" % skin_name


func _on_continue() -> void:
	if _done:           # guard against mouse + touch both firing
		return
	_done = true
	Audio.play("ui_confirm")
	continued.emit()
	if _next_scene.is_empty():
		get_tree().reload_current_scene()
	else:
		get_tree().change_scene_to_file(_next_scene)
