# file: ml/generate_build.py
import pandas as pd
import numpy as np
import os

# Use a dynamic path that is independent of where the script is executed
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, "../ml_presets_V5.6.csv")

# Load the dataset using the corrected path
raw_df = pd.read_csv(csv_path)

slots = {
    "weapons": ["RH1", "RH2", "LH1", "LH2"],
    "armor": ["Helms", "Chest Armor", "Gauntlets", "Greaves"],
    "talismans": ["Talisman1", "Talisman2", "Talisman3", "Talisman4"],
    "spells": ["Spell1", "Spell2", "Spell3", "Spell4"],
    "ashes": ["AshOfWar1", "AshOfWar2"],
}


def uniq(values):
    vals = [v for v in values if pd.notna(v)]
    return sorted(set(vals))


# Build catalogs
weapon_catalog = uniq(pd.concat([raw_df[c] for c in slots["weapons"]], ignore_index=True))
armor_catalog = {k: uniq(raw_df[k]) for k in slots["armor"]}
talisman_catalog = uniq(pd.concat([raw_df[c] for c in slots["talismans"]], ignore_index=True))
spell_catalog = uniq(pd.concat([raw_df[c] for c in slots["spells"]], ignore_index=True))
ash_catalog = uniq(pd.concat([raw_df[c] for c in slots["ashes"]], ignore_index=True))


# ---- TAGGING HELPERS ----
def tag_weapon(name: str) -> set[str]:
    n = str(name).lower()
    tags = set()
    if "greatsword" in n or "colossal" in n or "great axe" in n or "greathammer" in n or "golem" in n or "guts" in n or "hammer" in n or "giant-crusher" in n:
        tags.add("strength")
        tags.add("heavy")
        tags.add("colossal")
    if "katana" in n or "uchigatana" in n or "bloodhound fang" in n or "nagakiba" in n or "claw" in n or "twinblade" in n or "dagger" in n or "scythe" in n:
        tags.add("dex")
        tags.add("fast")
    if "seal" in n or "incantation" in n or "faith" in n or "gravel stone seal" in n:
        tags.add("faith")
        tags.add("incantation")
        tags.add("caster")
    if "staff" in n or "sorcery" in n or "magic" in n:
        tags.add("int")
        tags.add("sorcery")
        tags.add("caster")
    if "blood" in n or "rivers of blood" in n or "reduvia" in n or "mohgs" in n or "occult" in n or "arcane" in n or "hookclaws" in n:
        tags.add("bleed")
        tags.add("arcane")
    if "eleonora's poleblade" in n:
        tags.add("bleed")
        tags.add("dex")
    if "magma" in n or "fire" in n:
        tags.add("fire")
    if "ice" in n or "frost" in n or "hoarfrost" in n:
        tags.add("frost")
        tags.add("magic")
    if "black bow" in n or "serpent bow" in n:
        tags.add("ranged")
        tags.add("dex")
    if "jellyfish shield" in n:
        tags.add("buff")
        tags.add("defense")
    return tags


def tag_ash(name: str) -> set[str]:
    n = str(name).lower()
    tags = set()
    if "seppuku" in n or "bloody" in n or "blood" in n:
        tags.add("bleed")
    if "lion's claw" in n or "giant hunt" in n or "cragblade" in n or "wild strikes" in n:
        tags.add("strength")
        tags.add("heavy")
    if "quickstep" in n or "bloodhound" in n or "double slash" in n or "unsheathe" in n:
        tags.add("dex")
        tags.add("fast")
    if "golden vow" in n or "flame, grant me strength" in n:
        tags.add("faith")
        tags.add("buff")
    if "hoarfrost" in n:
        tags.add("frost")
    return tags


def tag_talisman(name: str) -> set[str]:
    n = str(name).lower()
    tags = set()
    if "lord of blood" in n or "rotten winged sword" in n or "millicent" in n or "shard of alexander" in n:
        tags.add("aggressive")
        tags.add("damage")
    if "warrior jar shard" in n:
        tags.add("skill_boost")
    if "claw talisman" in n:
        tags.add("jump attack")
    if "ritual sword" in n:
        tags.add("caster")
        tags.add("damage")
    if "dragoncrest greatshield" in n or "bull-goat" in n:
        tags.add("defense")
        tags.add("tanky")
    if "green turtle" in n:
        tags.add("stamina")
    if "godfrey icon" in n:
        tags.add("charged attack")
        tags.add("damage")
    if "twinblade" in n:
        tags.add("combo")
    if "starscourge" in n:
        tags.add("str_boost")
    if "great-jar's arsenal" in n:
        tags.add("equip_load")
        tags.add("heavy")
    if "graven-school" in n or "graven-mass" in n:
        tags.add("int")
        tags.add("sorcery")
        tags.add("caster")
    return tags


def tag_spell(name: str) -> set[str]:
    n = str(name).lower()
    tags = set()
    if "golden vow" in n or "flame, grant me strength" in n or "black flame" in n:
        tags.add("faith")
        tags.add("buff")
    if "terra magica" in n or "comet azur" in n or "sorcery" in n:
        tags.add("int")
        tags.add("sorcery")
        tags.add("magic")
    if "bloodflame blade" in n or "swarm of flies" in n:
        tags.add("bleed")
    return tags


def tag_armor(name: str) -> set[str]:
    n = str(name).lower()
    tags = set()
    if "bull-goat" in n or "radahn" in n or "crucible" in n or "lionel" in n or "veteran's" in n:
        tags.add("strength")
        tags.add("heavy")
        tags.add("tanky")
    if "white mask" in n or "ronin" in n:
        tags.add("bleed")
        tags.add("light")
    if "black knife" in n or "raptor" in n:
        tags.add("dex")
        tags.add("light")
    if "queen's" in n or "snow witch" in n or "carian" in n or "sorcerer" in n:
        tags.add("int")
        tags.add("sorcery")
    return tags


# Precompute tag maps
weapon_tags = {w: tag_weapon(w) for w in weapon_catalog}
ash_tags = {a: tag_ash(a) for a in ash_catalog}
talisman_tags = {t: tag_talisman(t) for t in talisman_catalog}
spell_tags = {s: tag_spell(s) for s in spell_catalog}
armor_tags = {item: tag_armor(item) for cat in armor_catalog.values() for item in cat}

rng = np.random.default_rng(7)


def pick_best(catalog, tags_map, query_tags: set[str], k: int = 1, used_items: set = None):
    used_items = used_items if used_items is not None else set()
    scored = []

    if not catalog:
        return []

    # First, filter out any used items
    filtered_catalog = [item for item in catalog if item not in used_items]

    for item in filtered_catalog:
        item_tags = tags_map.get(item, set())
        score = len(query_tags & item_tags)

        # Add a bonus for highly-relevant items
        if "bleed" in query_tags and "lord of blood's exultation" in str(item).lower():
            score += 10
        if "strength" in query_tags and "shard of alexander" in str(item).lower():
            score += 10

        if item_tags.isdisjoint(query_tags) and query_tags:
            score = 0
        else:
            score += rng.random() * 0.01
        scored.append((score, item))
    scored.sort(reverse=True)
    return [x[1] for x in scored[:k]]


def generate_build(base_items=None, query: str = ""):
    q = query.lower()
    query_tags = set(t for t in ["strength", "dex", "int", "faith", "bleed"] if t in q)
    used_items = set()

    build = base_items.copy() if base_items else {
        "RH1": None, "RH2": None, "LH1": None, "LH2": None,
        "Helms": None, "Chest Armor": None, "Gauntlets": None, "Greaves": None,
        "Talisman1": None, "Talisman2": None, "Talisman3": None, "Talisman4": None,
        "Spell1": None, "Spell2": None, "Spell3": None, "Spell4": None,
        "AshOfWar1": None, "AshOfWar2": None,
    }

    # Find and handle a specific weapon mention
    weapon_mention = next((w for w in weapon_catalog if w.lower() in q), None)
    if weapon_mention:
        build["RH1"] = weapon_mention
        used_items.add(weapon_mention)
        # Adjust tags based on the weapon found
        query_tags |= tag_weapon(weapon_mention)

    # --- Weapons ---
    if not build["RH1"]:
        chosen_wpn = pick_best(weapon_catalog, weapon_tags, query_tags, k=2, used_items=used_items)
        if chosen_wpn:
            build["RH1"] = chosen_wpn[0]
            used_items.add(chosen_wpn[0])
            if len(chosen_wpn) > 1 and "dual" in q:
                build["LH1"] = chosen_wpn[1]
                used_items.add(chosen_wpn[1])

    # --- Ashes ---
    # Only pick Ashes of War if the weapon isn't a staff or seal
    is_caster = any(t in query_tags for t in ["int", "faith", "caster"])
    if not is_caster:
        chosen_ashes = pick_best(ash_catalog, ash_tags, query_tags, k=2)
        for i, a in enumerate(chosen_ashes, start=1):
            build[f"AshOfWar{i}"] = a
            used_items.add(a)

    # --- Spells ---
    chosen_spells = pick_best(spell_catalog, spell_tags, query_tags, k=4, used_items=used_items)
    for i, s in enumerate(chosen_spells, start=1):
        build[f"Spell{i}"] = s
        used_items.add(s)

    # --- Talismans ---
    chosen_tals = pick_best(talisman_catalog, talisman_tags, query_tags, k=4, used_items=used_items)
    for i, t in enumerate(chosen_tals, start=1):
        build[f"Talisman{i}"] = t
        used_items.add(t)

    # --- Armor ---
    armor_sets = []
    for i, (helm, chest, gauntlets, greaves) in raw_df[[c for c in slots["armor"]]].iterrows():
        set_tags = tag_armor(str(helm)) | tag_armor(str(chest)) | tag_armor(str(gauntlets)) | tag_armor(str(greaves))
        if query_tags.issubset(set_tags):
            armor_sets.append([helm, chest, gauntlets, greaves])

    if armor_sets:
        chosen_set = armor_sets[0]
        build["Helms"] = chosen_set[0]
        build["Chest Armor"] = chosen_set[1]
        build["Gauntlets"] = chosen_set[2]
        build["Greaves"] = chosen_set[3]
    else:
        # Fallback to general best armor if no matching set found
        for slot in slots["armor"]:
            chosen = pick_best(armor_catalog.get(slot, []), armor_tags, query_tags, k=1, used_items=used_items)
            if chosen:
                build[slot] = chosen[0]

    # --- Off-hand Seal Rule ---
    # Check if spells were chosen, but no staff/seal is equipped
    has_spells = any(build.get(s) for s in slots["spells"])
    has_casting_tool = any("seal" in str(build.get(w)).lower() or "staff" in str(build.get(w)).lower() for w in
                           ["RH1", "LH1", "RH2", "LH2"])

    if has_spells and not has_casting_tool:
        chosen_seal = pick_best([s for s in weapon_catalog if "seal" in str(s).lower() or "staff" in str(s).lower()],
                                weapon_tags, query_tags, k=1)
        if chosen_seal:
            if not build["LH2"]:
                build["LH2"] = chosen_seal[0]
            elif not build["RH2"]:
                build["RH2"] = chosen_seal[0]

    return build


if __name__ == "__main__":
    print("--- Example: Generating a new 'strength bleed' build from scratch ---")
    new_build_1 = generate_build(query="strength bleed")
    for slot, item in new_build_1.items():
        print(f"  {slot}: {item}")

    print("\n--- Example: Generating a new 'int' build from scratch ---")
    new_build_2 = generate_build(query="int")
    for slot, item in new_build_2.items():
        print(f"  {slot}: {item}")