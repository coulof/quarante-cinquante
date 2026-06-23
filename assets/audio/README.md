# Audio — drop your recordings here

Put **SFX** in `assets/audio/sfx/` as mono **WAV** (or OGG), and **music/loops** in
`assets/audio/music/` as **OGG**. Name files exactly as below (lowercase). For variety,
add numbered takes — `hero_hurt_1.wav`, `hero_hurt_2.wav`, … — and the engine picks one
at random. Missing files are fine: the `Audio` system no-ops anything not yet recorded.

Full context + where each triggers: `~/.claude/plans/rippling-doodling-pearl.md`.

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
