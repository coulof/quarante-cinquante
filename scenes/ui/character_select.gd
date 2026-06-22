extends Control
## Stub screen for picking the active hero skin (unlocked via progression).
## Out of scope this session beyond listing unlocked skins; wired for later use.

@onready var skin_list: VBoxContainer = $Center/Panel/VBox/SkinList
@onready var start_button: Button = $Center/Panel/VBox/StartButton


func _ready() -> void:
	_populate()
	start_button.pressed.connect(_on_start)


func _populate() -> void:
	for child in skin_list.get_children():
		child.queue_free()
	for skin_id in GameState.unlocked_skins:
		var button := Button.new()
		button.text = skin_id
		button.toggle_mode = true
		button.button_pressed = (skin_id == GameState.active_skin)
		button.pressed.connect(GameState.set_active_skin.bind(skin_id))
		skin_list.add_child(button)


func _on_start() -> void:
	get_tree().change_scene_to_file("res://scenes/world/level_01.tscn")
