extends Control
## Heads-up display: HP bar, the weapon strip (all unlocked weapons + their keys,
## active one highlighted), enemy-type telegraph, and wave counter. Driven by
## signals wired up in the level script.

@onready var health_bar: ProgressBar = $HealthBar
@onready var weapon_strip: HBoxContainer = $WeaponStrip
@onready var enemy_type_label: Label = $EnemyTypeLabel
@onready var wave_label: Label = $WaveLabel

const ACTIVE_MODULATE := Color(1, 1, 1, 1)
const INACTIVE_MODULATE := Color(1, 1, 1, 0.4)

var _chips: Dictionary = {}  # weapon_id -> PanelContainer


func _ready() -> void:
	enemy_type_label.visible = false


func set_health(current: float, maximum: float) -> void:
	health_bar.max_value = maximum
	health_bar.value = current


## Build the weapon strip from the hero's currently available weapons.
func set_weapons(weapons: Array, active: Weapon) -> void:
	for child in weapon_strip.get_children():
		child.queue_free()
	_chips.clear()
	for w in weapons:
		var chip := _make_chip(w)
		weapon_strip.add_child(chip)
		_chips[w.id] = chip
	set_weapon(active)


## Highlight the active weapon's chip (called on every weapon switch).
func set_weapon(active: Weapon) -> void:
	if active == null:
		return
	for id in _chips:
		var chip: Control = _chips[id]
		chip.modulate = ACTIVE_MODULATE if id == active.id else INACTIVE_MODULATE


func set_wave(remaining: int, total: int) -> void:
	wave_label.text = "Enemies: %d / %d" % [remaining, total]


func show_enemy_type(weakness: String) -> void:
	enemy_type_label.text = "USE: %s" % weakness.to_upper()
	enemy_type_label.visible = true


func hide_enemy_type() -> void:
	enemy_type_label.visible = false


func _make_chip(weapon: Weapon) -> Control:
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(92, 0)

	var vbox := VBoxContainer.new()
	vbox.add_theme_constant_override("separation", 2)
	panel.add_child(vbox)

	var key := Label.new()
	key.text = "[%s]" % char(int(weapon.hotkey))
	key.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	key.add_theme_font_size_override("font_size", 18)
	vbox.add_child(key)

	var swatch := ColorRect.new()
	swatch.color = weapon.placeholder_color
	swatch.custom_minimum_size = Vector2(0, 18)
	swatch.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vbox.add_child(swatch)

	var name_label := Label.new()
	name_label.text = weapon.display_name
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_label.add_theme_font_size_override("font_size", 12)
	vbox.add_child(name_label)

	return panel
