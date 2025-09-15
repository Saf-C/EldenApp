# file: ml/generate_build.py
import pandas as pd
import numpy as np
import os
import re

# Use a dynamic path that is independent of where the script is executed
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, "../ml_presets_V5.6.csv")

try:
    raw_df = pd.read_csv(csv_path)
except FileNotFoundError:
    raise FileNotFoundError(f"CSV file not found at: {csv_path}")

slots = {
    "weapons": ["RH1", "RH2", "LH1", "LH2"],
    "armor": ["Helms", "Chest Armor", "Gauntlets", "Greaves"],
    "talismans": ["Talisman1", "Talisman2", "Talisman3", "Talisman4"],
    "spells": ["Spell1", "Spell2", "Spell3", "Spell4"],
    "ashes": ["AshOfWar1", "AshOfWar2"],
}


def uniq(values):
    vals = [str(v) for v in values if pd.notna(v)]
    return sorted(set(vals))


weapon_catalog = uniq(pd.concat([raw_df[c] for c in slots["weapons"]], ignore_index=True))
armor_catalog = {k: uniq(raw_df[k]) for k in slots["armor"]}
talisman_catalog = uniq(pd.concat([raw_df[c] for c in slots["talismans"]], ignore_index=True))
spell_catalog = uniq(pd.concat([raw_df[c] for c in slots["spells"]], ignore_index=True))
ash_catalog = uniq(pd.concat([raw_df[c] for c in slots["ashes"]], ignore_index=True))


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


weapon_tags = {w: tag_weapon(w) for w in weapon_catalog}
ash_tags = {a: tag_ash(a) for a in ash_catalog}
talisman_tags = {t: tag_talisman(t) for t in talisman_catalog}
spell_tags = {s: tag_spell(s) for s in spell_catalog}
armor_tags = {item: tag_armor(item) for cat in armor_catalog.values() for item in cat}

rng = np.random.default_rng(7)


def pick_best(catalog, tags_map, query_tags: set[str], k: int = 1, used_items: set = None):
    used_items = used_items if used_items is not None else set()
    scored = []
    if not catalog: return []
    filtered_catalog = [str(item) for item in catalog if pd.notna(item) and str(item) not in used_items]
    for item in filtered_catalog:
        item_tags = tags_map.get(item, set())
        score = len(query_tags & item_tags)
        if "bleed" in query_tags and "lord of blood's exultation" in item.lower():
            score += 5
        if "strength" in query_tags and "shard of alexander" in item.lower():
            score += 5
        if "int" in query_tags and "graven-mass talisman" in item.lower():
            score += 5
        score += rng.random() * 0.01
        scored.append((score, item))
    scored.sort(reverse=True)
    return [x[1] for x in scored[:k]]


def generate_build(base_items=None, query: str = ""):
    q = query.lower()
    query_tags = {t for t in ["strength", "dex", "int", "faith", "bleed"] if t in q}
    used = set()

    build = {slot: None for cat in slots.values() for slot in cat}
    if base_items: build.update(base_items)

    # --- Weapon locking
    weapon_mention = next((w for w in weapon_catalog if w and w.lower() in q), None)
    if weapon_mention:
        build["RH1"] = weapon_mention
        used.add(weapon_mention)
        query_tags |= tag_weapon(weapon_mention)

    # Weapons
    if not build["RH1"]:
        picks = pick_best(weapon_catalog, weapon_tags, query_tags, k=2, used_items=used)
        if picks:
            build["RH1"] = picks[0]; used.add(picks[0])
            if len(picks) > 1 and "dual" in q: build["LH1"] = picks[1]

    # Ashes (only if not caster)
    if not any(t in query_tags for t in ["int", "faith", "caster"]):
        for i, a in enumerate(pick_best(ash_catalog, ash_tags, query_tags, k=2), start=1):
            build[f"AshOfWar{i}"] = a

    # Spells
    for i, s in enumerate(pick_best(spell_catalog, spell_tags, query_tags, k=4, used_items=used), start=1):
        build[f"Spell{i}"] = s

    # Talismans
    for i, t in enumerate(pick_best(talisman_catalog, talisman_tags, query_tags, k=4, used_items=used), start=1):
        build[f"Talisman{i}"] = t

    # Armor sets
    set_found = False
    for _, row in raw_df[slots["armor"]].iterrows():
        set_tags = tag_armor(str(row["Helms"])) | tag_armor(str(row["Chest Armor"]))
        if query_tags & set_tags:
            build.update({c: row[c] for c in slots["armor"]})
            set_found = True
            break
    if not set_found:
        for armor_slot in slots["armor"]:
            picks = pick_best(armor_catalog[armor_slot], armor_tags, query_tags, k=1, used_items=used)
            if picks: build[armor_slot] = picks[0]

    # Auto add staff/seal if spells but no tool
    if any(build[s] for s in slots["spells"]):
        if not any(build.get(w) and isinstance(build[w], str) and ("seal" in build[w].lower() or "staff" in build[w].lower()) for w in slots["weapons"]):

            seal = pick_best([w for w in weapon_catalog if "seal" in str(w).lower() or "staff" in str(w).lower()],
                             weapon_tags, query_tags, k=1)
            if seal: build["LH2"] = seal[0]


    return {slot: (item if pd.notna(item) else None) for slot, item in build.items()}



if __name__ == "__main__":
    print("--- Example: Generating a new 'strength bleed' build from scratch ---")
    new_build_1 = generate_build(query="strength bleed")
    for slot, item in new_build_1.items():
        print(f"  {slot}: {item}")
    print("\n--- Example: Generating a new 'int' build from scratch ---")
    new_build_2 = generate_build(query="int")
    for slot, item in new_build_2.items():
        print(f"  {slot}: {item}")