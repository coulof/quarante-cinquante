extends Resource
class_name Weapon
## Data-driven weapon definition. Instances live as .tres files in
## res://resources/weapons/ so designers can add weapons without code.

@export var id: String = ""
@export var display_name: String = ""
@export var damage_multiplier: float = 1.0
## Raw keycode used to select this weapon (KEY_1, KEY_2, ...). Matched against
## the event's physical_keycode so it works regardless of keyboard layout.
@export var hotkey: Key = KEY_1
## Placeholder tint used while there is no real sprite art (Phase 1).
@export var placeholder_color: Color = Color.WHITE
@export var sprite: Texture2D
## Hero AnimatedSprite2D animation to play when attacking with this weapon.
@export var attack_anim: String = "attack"
## Ranged weapons fire `projectile_scene` instead of doing a melee sweep.
@export var ranged: bool = false
@export var projectile_scene: PackedScene
