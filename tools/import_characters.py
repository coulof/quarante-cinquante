#!/usr/bin/env python3
"""Re-import character sprites from their LPC split exports — one command.

Drop a fresh "split by animation" export into assets/sprites/lpc_src/<dir>/, then:

    python3 tools/import_characters.py            # re-import every present character
    python3 tools/import_characters.py robot      # just one (or several names)
    # or: task sprites          /  task sprites -- robot

For each character it runs tools/import_lpc_split.py with that character's recipe
(which animation is the attack; --from-walk for bodies like Skeleton/muscular that have
no idle/run), then refreshes CREDITS.md from the exports' credit files, strips WSL
`Zone.Identifier` junk, and runs `godot --headless --import`.

Edit RECIPES below only when a character's **weapon** (→ attack file) or **body**
(→ from_walk) changes; a plain reskin keeping the same kit needs no edit here.
"""
import glob
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LPC = "assets/sprites/lpc_src"

# name -> (export subdir under lpc_src, attack PNG relative to it, from_walk)
RECIPES = {
    "hero":           ("hero",           "standard/slash.png",        False),
    "hero_pickaxe":   ("hero_pickaxe",   "custom/slash_128.png",      False),
    "hero_glowsword": ("hero_glowsword", "custom/slash_oversize.png", False),
    "hero_whip":      ("hero_whip",      "custom/tool_whip.png",      False),
    "zombie":         ("zombie",         "standard/thrust.png",       True),
    "robot":          ("robot",          "custom/slash_oversize.png", True),
    "pirate":         ("pirate",         "custom/slash_oversize.png", True),
}


def slice_one(name: str) -> bool:
    sub, attack, from_walk = RECIPES[name]
    if not os.path.isdir(os.path.join(ROOT, LPC, sub)):
        print(f"  – {name}: no export at {LPC}/{sub}, skipping")
        return False
    cmd = [sys.executable, os.path.join(ROOT, "tools", "import_lpc_split.py"),
           "--dir", f"{LPC}/{sub}", "--name", name, "--attack", attack]
    if from_walk:
        cmd.append("--from-walk")
    subprocess.run(cmd, cwd=ROOT, check=True)
    return True


def refresh_credits() -> None:
    blocks = {}
    for f in sorted(glob.glob(os.path.join(ROOT, LPC, "*/credits/credits.txt"))):
        for blk in open(f).read().split("\n\n"):
            blk = blk.strip("\n")
            if blk.strip() and "Licenses:" in blk:
                blocks.setdefault(blk.splitlines()[0].strip(), blk)
    if not blocks:
        return
    out = ["# Credits", "", "## Character art — Liberated Pixel Cup (LPC)", "",
           "All characters are composed in the",
           "[Universal LPC Spritesheet Generator](https://liberatedpixelcup.github.io/Universal-LPC-Spritesheet-Character-Generator)",
           "and sliced by `tools/import_lpc_split.py` (via `tools/import_characters.py`).",
           "LPC art is **CC-BY-SA 3.0 / OGA-BY 3.0 / GPL** — per component below.", "", "```"]
    for k in sorted(blocks):
        out += [blocks[k], ""]
    out += ["```", "", "## Code & engine",
            "- Game code: © Florian Coulombel. Built with [Godot 4](https://godotengine.org) (MIT).",
            "- Earlier procedural sprites (`tools/generate_sprites.py`, `gen_lpc_character.py`): CC0 / superseded.", ""]
    open(os.path.join(ROOT, "CREDITS.md"), "w").write("\n".join(out))
    print(f"CREDITS.md refreshed: {len(blocks)} LPC components")


def main() -> None:
    names = sys.argv[1:] or list(RECIPES)
    for n in names:
        if n not in RECIPES:
            sys.exit(f"unknown character '{n}'. Known: {', '.join(RECIPES)}")
    did = False
    for n in names:
        print(f"== {n} ==")
        did = slice_one(n) or did
    if not did:
        sys.exit("nothing imported (no matching exports under %s/)" % LPC)
    for z in glob.glob(os.path.join(ROOT, LPC, "**", "*Zone.Identifier"), recursive=True):
        os.remove(z)
    refresh_credits()
    print("Importing into Godot…")
    subprocess.run(["godot", "--headless", "--import"], cwd=ROOT, check=False)
    print("Done.")


if __name__ == "__main__":
    main()
