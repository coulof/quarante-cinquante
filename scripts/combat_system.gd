extends Node
## Autoload singleton. Pure rules engine for "weapon vs enemy weakness".
## Knows nothing about scenes; callers apply the resulting damage themselves.

enum Outcome { WEAK, CHIP }

## Damage multipliers per outcome. Phase 2 will add a PERFECT outcome (1.5).
const DAMAGE_MULT := {
	Outcome.WEAK: 1.0,   # correct weapon: full damage + hit animation
	Outcome.CHIP: 0.25,  # wrong weapon: chip damage only
}

signal attack_resolved(outcome: Outcome, target: Node)


## Resolve a single hit. `enemy` must expose a `weakness: String` property.
func resolve_hit(weapon_id: String, enemy: Node) -> Outcome:
	var outcome := Outcome.CHIP
	if "weakness" in enemy and weapon_id == enemy.weakness:
		outcome = Outcome.WEAK
	attack_resolved.emit(outcome, enemy)
	return outcome


## Convenience: how much damage `base_damage` becomes for a given outcome.
func damage_for(outcome: Outcome, base_damage: float) -> float:
	return base_damage * DAMAGE_MULT.get(outcome, 0.0)
