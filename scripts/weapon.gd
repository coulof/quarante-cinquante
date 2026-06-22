extends Resource
class_name Weapon
## Data-driven weapon definition. Instances live as .tres files in
## res://resources/weapons/ so designers can add weapons without code.

@export var id: String = ""
@export var display_name: String = ""
@export var damage_multiplier: float = 1.0
## Raw keycode used to select this weapon (KEY_1, KEY_2, ...).
@export var hotkey: Key = KEY_1
## Placeholder tint used while there is no real sprite art (Phase 1).
@export var placeholder_color: Color = Color.WHITE
@export var sprite: Texture2D
