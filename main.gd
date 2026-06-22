extends Node
## Root bootstrap. GameState/CombatSystem are autoloads that initialise before
## this runs; here we just hand off to the first playable scene.

@export var first_scene: String = "res://scenes/world/level_01.tscn"


func _ready() -> void:
	call_deferred("_goto_first_scene")


func _goto_first_scene() -> void:
	get_tree().change_scene_to_file(first_scene)
