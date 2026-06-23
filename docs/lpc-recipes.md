# Character recipes (LPC) — for re-editing later

Quick reference for regenerating/modifying the hero and enemies on the
[Universal LPC generator](https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator).
Full pipeline (import + wiring) is in [`lpc-characters.md`](./lpc-characters.md).

## Hero — exact character

Open this URL to reload the hero in the generator, pre-filled:

```
https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator/#sex=male&body=Body_Color_light&head=Human_Male_light&expression=Neutral_light&hair=Spiked_gold&hat=Cavalier_green&clothes=Shortsleeve_green&vest=Vest_open_maroon&legs=Cuffed_Pants_white&shoes=Basic_Boots_leather&weapon=Whip_whip
```

Decoded selections:

| Slot | Value |
|------|-------|
| Sex / Body | male / `Body_Color_light` |
| Head / Expression | `Human_Male_light` / `Neutral_light` |
| Hair | `Spiked_gold` |
| Hat | `Cavalier_green` |
| Clothes | `Shortsleeve_green` |
| Vest | `Vest_open_maroon` |
| Legs | `Cuffed_Pants_white` |
| Shoes | `Basic_Boots_leather` |
| Weapon | **changes per export** (see below) |

### Exporting the 4 weapon variants
Keep everything above the same; change only the **Weapon**, then export. Drop the
PNGs in `assets/sprites/lpc_src/` (overwrite the existing ones):

| File | Weapon to equip |
|------|-----------------|
| `hero.png` | none (`#…&weapon=none`) — the bare-handed fallback sheet |
| `hero_pickaxe.png` | a pickaxe / axe |
| `hero_glowsword.png` | Sword → **Glowsword** (blue) |
| `hero_whip.png` | **Whip** |

> Tip: a **split-by-animation** export is easier to import than the giant
> universal sheet (each animation is its own correctly-sized grid — important for the
> oversize whip/glowsword). See `lpc-characters.md` for which import mode to use.

## Enemies — layer recipes

Enemies are currently composited by `tools/gen_lpc_character.py` (the `CHARACTERS`
dict). To tweak them, edit that recipe and rerun, or rebuild them on the website like
the hero. Current recipes (layer paths = generator category paths):

- **Zombie** — Body `zombie`, Head `zombie`, T-shirt recolored purple.
- **Pirate** — Body male, Human head, pants (dark), Boots basic, T-shirt red,
  Hat → Pirate → **Tricorne**.
- **Robot** — Body male, Human head, **Armour → Plate** (legs/torso/feet, steel)
  recolored bright blue, Helmet → **Barbute** (blue).

Regenerate via:
```bash
python3 tools/gen_lpc_character.py            # all
python3 tools/gen_lpc_character.py zombie     # one
godot --headless --import
```

## License
LPC art is CC-BY-SA 3.0 / GPL — keep each export's per-layer credits in `CREDITS.md`.
