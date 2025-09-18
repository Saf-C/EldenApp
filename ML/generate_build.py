# file: ml/generate_build.py
import pandas as pd
import numpy as np
import os

from .tag_utils import expand_query, tags_for_item

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

rng = np.random.default_rng(7)


def pick_best(catalog, query_tags: set[str], k: int = 1, used_items: set = None):
    used_items = used_items if used_items is not None else set()
    scored = []
    if not catalog:
        return []
    filtered_catalog = [str(item) for item in catalog if pd.notna(item) and str(item) not in used_items]
    for item in filtered_catalog:
        item_tags = tags_for_item(item)
        score = len(query_tags & item_tags)
        # Strong boosts for certain synergies
        if "bleed" in query_tags and "lord of blood's exultation" in item.lower():
            score += 5
        if "strength" in query_tags and "shard of alexander" in item.lower():
            score += 5
        if "int" in query_tags and "graven-mass talisman" in item.lower():
            score += 5
        # Intersection bonus
        if len(query_tags & item_tags) >= 2:
            score += 3

        score += rng.random() * 0.01
        scored.append((score, item))
    scored.sort(reverse=True)
    return [x[1] for x in scored[:k]]


def generate_build(base_items=None, query: str = ""):
    q = expand_query(query)
    query_tags = set(q.split())
    used = set()

    build = {slot: None for cat in slots.values() for slot in cat}
    if base_items:
        build.update(base_items)

    # --- Weapon locking
    weapon_mentions = [w for w in weapon_catalog if w and w.lower() in q]

    if "dual" in q and len(weapon_mentions) >= 2:
        # Lock both dual weapons
        build["RH1"], build["LH1"] = weapon_mentions[:2]
        used.update(weapon_mentions[:2])
        for wm in weapon_mentions:
            query_tags |= tags_for_item(wm)
    elif weapon_mentions:
        build["RH1"] = weapon_mentions[0]
        used.add(weapon_mentions[0])
        query_tags |= tags_for_item(weapon_mentions[0])

    # Weapons
    if not build["RH1"]:
        picks = pick_best(weapon_catalog, query_tags, k=2, used_items=used)
        if picks:
            build["RH1"] = picks[0]
            used.add(picks[0])
            if len(picks) > 1 and "dual" in q:
                build["LH1"] = picks[1]

    # Ashes (only if not caster)
    if not any(t in query_tags for t in ["int", "faith", "caster"]):
        for i, a in enumerate(pick_best(ash_catalog, query_tags, k=2), start=1):
            build[f"AshOfWar{i}"] = a

    # Spells
    for i, s in enumerate(pick_best(spell_catalog, query_tags, k=4, used_items=used), start=1):
        build[f"Spell{i}"] = s

    # Talismans
    for i, t in enumerate(pick_best(talisman_catalog, query_tags, k=4, used_items=used), start=1):
        build[f"Talisman{i}"] = t

    # Armor sets
    set_found = False
    for _, row in raw_df[slots["armor"]].iterrows():
        set_tags = tags_for_item(str(row["Helms"])) | tags_for_item(str(row["Chest Armor"]))
        if query_tags & set_tags:
            build.update({c: row[c] for c in slots["armor"]})
            set_found = True
            break
    if not set_found:
        for armor_slot in slots["armor"]:
            picks = pick_best(armor_catalog[armor_slot], query_tags, k=1, used_items=used)
            if picks:
                build[armor_slot] = picks[0]

    # Auto add staff/seal if spells but no tool
    if any(build[s] for s in slots["spells"]):
        if not any(build.get(w) and isinstance(build[w], str) and ("seal" in build[w].lower() or "staff" in build[w].lower()) for w in slots["weapons"]):
            seal = pick_best([w for w in weapon_catalog if "seal" in str(w).lower() or "staff" in str(w).lower()],
                             query_tags, k=1)
            if seal:
                build["LH2"] = seal[0]

    return {slot: (item if pd.notna(item) else None) for slot, item in build.items()}


if __name__ == "__main__":
    print("--- Example: Generating a new 'strength bleed' build from scratch ---")
    new_build_1 = generate_build(query="strength bleed")
    for slot, item in new_build_1.items():
        print(f"  {slot}: {item}")

    print("\n--- Example: Generating a new 'magic katana' build from scratch ---")
    new_build_2 = generate_build(query="magic katana")
    for slot, item in new_build_2.items():
        print(f"  {slot}: {item}")
