extends Control
## Heads-up display: HP bar, the weapon strip (all unlocked weapons + their keys,
## active one highlighted), enemy-type telegraph, and wave counter. Driven by
## signals wired up in the level script.

## Emitted when a weapon chip is tapped (touch / mouse) — the level routes it to the hero.
signal weapon_selected(weapon_id: String)

@onready var health_bar: ProgressBar = $HealthBar
@onready var weapon_strip: HBoxContainer = $WeaponStrip
@onready var enemy_type_label: Label = $EnemyTypeLabel
@onready var wave_label: Label = $WaveLabel
@onready var joystick: Control = $Joystick
@onready var attack_button: Button = $AttackButton
@onready var rotate_hint: ColorRect = $RotateHint

const ACTIVE_MODULATE := Color(1, 1, 1, 1)
const INACTIVE_MODULATE := Color(1, 1, 1, 0.55)

## Force the on-screen touch controls on even without a touchscreen (editor testing).
@export var force_touch_ui := false

var _chips: Dictionary = {}  # weapon_id -> PanelContainer


func _ready() -> void:
	enemy_type_label.visible = false
	var touch := force_touch_ui or DisplayServer.is_touchscreen_available()
	joystick.visible = touch
	attack_button.visible = touch
	# Drive the "attack" action directly from touch/mouse on the button. (Button's
	# button_down/up signals don't fire from touch when emulate_mouse_from_touch is off,
	# so we handle ScreenTouch ourselves — same pattern as the joystick + weapon chips.)
	attack_button.gui_input.connect(func(e: InputEvent):
		if e is InputEventScreenTouch or e is InputEventMouseButton:
			if e.pressed:
				Input.action_press("attack")
			else:
				Input.action_release("attack"))


func _process(_delta: float) -> void:
	# Web can't force orientation: nudge the player to landscape on a portrait phone.
	if rotate_hint:
		var vp := get_viewport_rect().size
		rotate_hint.visible = DisplayServer.is_touchscreen_available() and vp.y > vp.x


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
		var chip: PanelContainer = _chips[id]
		var is_active: bool = id == active.id
		var accent: Color = chip.get_meta("accent")
		chip.modulate = ACTIVE_MODULATE if is_active else INACTIVE_MODULATE
		chip.add_theme_stylebox_override("panel", _chip_style(accent, is_active))


func set_wave(remaining: int, total: int) -> void:
	wave_label.text = "Enemies: %d / %d" % [remaining, total]


func show_enemy_type(weakness: String) -> void:
	enemy_type_label.text = "USE: %s" % weakness.to_upper()
	enemy_type_label.visible = true


func hide_enemy_type() -> void:
	enemy_type_label.visible = false


## A rounded card: dark background, weapon-colored border (thick + glow when active).
func _chip_style(accent: Color, active: bool) -> StyleBoxFlat:
	var sb := StyleBoxFlat.new()
	sb.bg_color = Color(0.11, 0.12, 0.17, 0.95 if active else 0.7)
	sb.set_corner_radius_all(8)
	sb.set_border_width_all(3 if active else 1)
	sb.border_color = accent if active else Color(0.45, 0.47, 0.55, 0.8)
	sb.content_margin_left = 8
	sb.content_margin_right = 8
	sb.content_margin_top = 6
	sb.content_margin_bottom = 6
	if active:
		sb.shadow_color = Color(accent.r, accent.g, accent.b, 0.55)
		sb.shadow_size = 7
	return sb


func _make_chip(weapon: Weapon) -> PanelContainer:
	var accent: Color = weapon.placeholder_color
	var panel := PanelContainer.new()
	panel.custom_minimum_size = Vector2(96, 0)
	panel.set_meta("accent", accent)
	panel.add_theme_stylebox_override("panel", _chip_style(accent, false))

	# Tap (touch or click) selects this weapon; inner controls ignore input so the tap
	# reaches the panel.
	panel.gui_input.connect(func(e: InputEvent):
		if (e is InputEventMouseButton and e.pressed) or (e is InputEventScreenTouch and e.pressed):
			weapon_selected.emit(weapon.id))

	var vbox := VBoxContainer.new()
	vbox.mouse_filter = Control.MOUSE_FILTER_IGNORE
	vbox.add_theme_constant_override("separation", 3)
	panel.add_child(vbox)

	# Key badge, tinted with the weapon's accent.
	var key := Label.new()
	key.text = char(int(weapon.hotkey))
	key.mouse_filter = Control.MOUSE_FILTER_IGNORE
	key.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	key.add_theme_font_size_override("font_size", 20)
	key.add_theme_color_override("font_color", accent)
	vbox.add_child(key)

	var swatch := ColorRect.new()
	swatch.color = accent
	swatch.mouse_filter = Control.MOUSE_FILTER_IGNORE
	swatch.custom_minimum_size = Vector2(0, 16)
	swatch.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	vbox.add_child(swatch)

	var name_label := Label.new()
	name_label.text = weapon.display_name
	name_label.mouse_filter = Control.MOUSE_FILTER_IGNORE
	name_label.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	name_label.add_theme_font_size_override("font_size", 12)
	vbox.add_child(name_label)

	return panel
