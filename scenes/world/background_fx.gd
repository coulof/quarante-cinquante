extends Node2D
## Decorative, time-based background animation for the fixed-camera arena: a slow
## endless cloud drift across the sky + faint drifting dust. Instantiated by the level
## (level_01.gd) behind the play area. Camera doesn't scroll, so this (not Godot's
## ParallaxBackground) is what makes the backdrop feel alive.

const CLOUDS_TEX := "res://assets/bg_desert_clouds.png"
const CLOUD_SPEED := 11.0   # px/s, leftward

var _clouds: Array[Sprite2D] = []
var _strip_w := 1280.0


func _ready() -> void:
	var tex: Texture2D = load(CLOUDS_TEX) if ResourceLoader.exists(CLOUDS_TEX) else null
	if tex:
		_strip_w = tex.get_width()
		for i in 2:                       # two copies tile end-to-end
			var s := Sprite2D.new()
			s.texture = tex
			s.centered = false
			s.position = Vector2(i * _strip_w, 6)   # up in the sky
			add_child(s)
			_clouds.append(s)
	_spawn_dust()


func _process(delta: float) -> void:
	for s in _clouds:
		s.position.x -= CLOUD_SPEED * delta
		if s.position.x <= -_strip_w:
			s.position.x += 2.0 * _strip_w


func _spawn_dust() -> void:
	var img := Image.create(3, 3, false, Image.FORMAT_RGBA8)
	img.fill(Color.WHITE)
	var p := CPUParticles2D.new()
	p.texture = ImageTexture.create_from_image(img)
	p.amount = 30
	p.lifetime = 12.0
	p.preprocess = 12.0               # pre-fill the screen so it's not empty at start
	p.position = Vector2(640, 360)
	p.emission_shape = CPUParticles2D.EMISSION_SHAPE_RECTANGLE
	p.emission_rect_extents = Vector2(680, 380)   # whole screen
	p.direction = Vector2(-1, -0.15)              # drift left, matching the clouds
	p.spread = 25.0
	p.gravity = Vector2.ZERO
	p.initial_velocity_min = 18.0
	p.initial_velocity_max = 46.0
	p.scale_amount_min = 1.0
	p.scale_amount_max = 2.5
	p.color = Color(1.0, 0.97, 0.9, 0.35)
	add_child(p)
	p.emitting = true
