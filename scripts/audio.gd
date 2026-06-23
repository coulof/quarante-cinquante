extends Node
## Autoload. Central SFX/music player. Loads any clip in `assets/audio/sfx/` named in
## SOUNDS (plus `_1.._4` variants → randomized), and plays them on a small voice pool.
## `play(name)` no-ops if the clip isn't present, so partial sound sets work fine.
## Wires itself to the autoload-level CombatSystem; per-instance hooks live in the
## entities (see character_base.gd, hero.gd, enemy_base.gd, level_01.gd, unlock_screen.gd).

const SFX_DIR := "res://assets/audio/sfx/"
const MUSIC_DIR := "res://assets/audio/music/"
const POOL := 8
const MUSIC_DB := -14.0   # music sits under the SFX

## Sound names the game asks for (= the recording checklist). Add new names here.
const SOUNDS := [
	"hero_hurt", "hero_die",
	"zombie_hurt", "zombie_die", "robot_hurt", "robot_die", "pirate_hurt", "pirate_die",
	"enemy_attack", "telegraph", "robot_laser",
	"wpn_pickaxe", "wpn_glowsword", "wpn_whip",
	"hit_weak", "hit_chip", "enemy_bolt_hit",
	"ui_weapon_switch", "ui_confirm", "wave_clear", "unlock_fanfare", "win", "lose",
	"level_start",
]

var _sfx: Dictionary = {}          # name -> Array[AudioStream] (variants)
var _players: Array[AudioStreamPlayer] = []
var _next := 0
var _music: AudioStreamPlayer


func _ready() -> void:
	for i in POOL:
		var p := AudioStreamPlayer.new()
		add_child(p)
		_players.append(p)
	_music = AudioStreamPlayer.new()
	_music.volume_db = MUSIC_DB
	add_child(_music)
	_load_sounds()
	# CombatSystem is an autoload too; hit feedback lives here.
	CombatSystem.attack_resolved.connect(_on_attack_resolved)


func _load_sounds() -> void:
	# Robust in editor + export: load by explicit path (no res:// dir scanning).
	for snd in SOUNDS:
		var variants: Array[AudioStream] = []
		for suffix in ["", "_1", "_2", "_3", "_4"]:
			var path: String = SFX_DIR + snd + suffix + ".ogg"
			if ResourceLoader.exists(path):
				variants.append(load(path))
		if not variants.is_empty():
			_sfx[snd] = variants


func play(snd: String) -> void:
	if not _sfx.has(snd):
		return
	var variants: Array = _sfx[snd]
	var p := _players[_next]
	_next = (_next + 1) % _players.size()
	p.stream = variants[randi() % variants.size()]
	p.play()


func play_music(track: String, loop := true) -> void:
	var path: String = MUSIC_DIR + track + ".ogg"
	if not ResourceLoader.exists(path):
		return
	var s: AudioStream = load(path)
	if s is AudioStreamOggVorbis:
		s.loop = loop
	if _music.stream == s and _music.playing:
		return
	_music.stream = s
	_music.play()


func _on_attack_resolved(outcome: int, _target: Node) -> void:
	play("hit_weak" if outcome == CombatSystem.Outcome.WEAK else "hit_chip")
