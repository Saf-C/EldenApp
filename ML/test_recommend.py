# ML/test_recommend.py

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json
import os

# The recommend_plus module contains the enhanced recommendation function
from ML.recommend_plus import recommend_build
from ML.generate_build import generate_build


# --- Preprocessing function ---
def preprocess(text):
    return str(text).lower().replace("'", "").replace("-", " ")


# 1. Load raw dataset
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, "../ml_presets_V5.6.csv")
raw_df = pd.read_csv(csv_path)

# Columns that define each build
text_cols = [
    "RH1", "RH2", "LH1", "LH2", "Helms", "Chest Armor",
    "Gauntlets", "Greaves",
    "Talisman1", "Talisman2", "Talisman3", "Talisman4",
    "Spell1", "Spell2", "Spell3", "Spell4",
    "AshOfWar1", "AshOfWar2",

]

# Step 1: join items + add tags
raw_df["build_text"] = (
        raw_df[text_cols].fillna("").agg(" ".join, axis=1)
        + " strength dex int faith arcane bleed frost poison fire holy magic lightning"
)

# Step 2: preprocess
raw_df["build_text"] = raw_df["build_text"].map(preprocess)

# 2. Vectorize
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(raw_df["build_text"])

# 4. Example usage
# load tiny tag rules if needed
tags_path = os.path.join(current_dir, "tags.json")
with open(tags_path) as f:
    TAGS = json.load(f)

if __name__ == "__main__":
    # --- Example 1: General Query ---
    # This shows the default, varied recommendations without any hard filters
    general_query = "strength bleed"
    general_recs = recommend_build(general_query, top_n=3, boost={"bleed": 3})

    print("--- Recommended Builds for '{}' (General Search) ---".format(general_query))
    for i, rec in enumerate(general_recs):
        print("\nRecommendation {}: (Similarity: {})".format(i + 1, rec["similarity"]))
        for item, name in rec["items"].items():
            if pd.notna(name):
                print(f"  {item}: {name}")

    # --- Example 2: Specific Query with 'must_have' and 'boost' ---
    # This shows how to get highly-specific, tailored recommendations
    specific_query = "bleed"
    must_have_items = ["Rivers of Blood"]
    boost_tags = {"bleed": 5, "dex": 5}

    specific_recs = recommend_build(
        specific_query,
        top_n=3,
        must_have=must_have_items,
        boost=boost_tags
    )

    print("\n" + "=" * 40)
    print("--- Recommended Builds for '{}' (Specific Search) ---".format(specific_query))
    for i, rec in enumerate(specific_recs):
        print("\nRecommendation {}: (Similarity: {})".format(i + 1, rec["similarity"]))
        for item, name in rec["items"].items():
            if pd.notna(name):
                print(f"  {item}: {name}")

    # --- Example 3: Different Build Type (Int Caster) ---
    print("\n" + "=" * 40)
    print("--- Recommended Builds for 'int caster' (General Search) ---")
    int_query = "int caster"
    int_recs = recommend_build(int_query, top_n=3, boost={"staff": 3})
    for i, rec in enumerate(int_recs):
        print("\nRecommendation {}: (Similarity: {})".format(i + 1, rec["similarity"]))
        for item, name in rec["items"].items():
            if pd.notna(name):
                print(f"  {item}: {name}")

    # --- Generate a new build (Unchanged) ---
    print("\n" + "=" * 40)
    print("Generating a new build from scratch:")
    new_build = generate_build(query=general_query)
    for slot, item in new_build.items():
        print(f"  {slot}: {item}")