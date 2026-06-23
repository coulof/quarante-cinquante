# Audio — drop your recordings here

Put **SFX** in `assets/audio/sfx/` and **music/loops** in `assets/audio/music/`, as
**OGG**. Name files exactly as below (lowercase). For variety, add numbered takes —
`hero_hurt_1.ogg`, `hero_hurt_2.ogg`, … — and the engine picks one at random. Missing
files are fine: the `Audio` autoload no-ops anything not yet recorded.

**Godot can't import `.m4a`/`.aac`** — convert recordings to OGG with ffmpeg:
```bash
ffmpeg -i clip.m4a -ac 1 -c:a libvorbis -q:a 5 clip.ogg     # SFX (mono)
ffmpeg -i music.mp3      -c:a libvorbis -q:a 5 music.ogg     # music (keep stereo)
```
Then `godot --headless --import`. The system is already wired (see `scripts/audio.gd`
+ `docs/audio-plan.md`); a recorded clip plays as soon as its `<name>.ogg` is present.

Full context + where each triggers: `docs/audio-plan.md`.

## sfx/ checklist
Hero:        hero_hurt   hero_die
Zombie:      zombie_hurt   zombie_die
Robot:       robot_hurt   robot_die   robot_laser
Pirate:      pirate_hurt   pirate_die
Enemies:     enemy_attack   telegraph
Weapons:     wpn_pickaxe   wpn_glowsword   wpn_whip
Hits:        hit_weak   hit_chip   enemy_bolt_hit
UI / flow:   ui_weapon_switch   ui_confirm   wave_clear   unlock_fanfare   win   lose
Optional:    level_start   hero_step

## music/ (optional)
music_gameplay (looping)   ambient_wind (optional)

### Minimum set for the biggest impact
hit_weak, hit_chip, wpn_pickaxe, wpn_glowsword, wpn_whip, hero_hurt,
zombie_die, robot_die, pirate_die, ui_weapon_switch, unlock_fanfare, win, lose
