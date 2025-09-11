# ml/recommend_plus.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

def preprocess(text: str) -> str:
    return str(text).lower().replace("'", "").replace("-", " ")

# Use a dynamic path that is independent of where the script is executed
current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, "../ml_presets_V5.6.csv")

# Load the dataset using the corrected path
raw_df = pd.read_csv(csv_path)

text_cols = [
    "RH1", "RH2", "LH1", "LH2",
    "Helms", "Chest Armor","Gauntlets", "Greaves",
    "Talisman1", "Talisman2","Talisman3", "Talisman4",
    "Spell1", "Spell2", "Spell3", "Spell4",
    "AshOfWar1", "AshOfWar2"
]

# Build text + lightweight global tags (keep for now)
raw_df["build_text"] = (
    raw_df[text_cols].fillna("").agg(" ".join, axis=1)
    + " strength dex int faith arcane bleed frost poison fire holy magic lightning"
)
raw_df["build_text"] = raw_df["build_text"].map(preprocess)

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(raw_df["build_text"])

# quick helper: does a row contain any of the needles (case-insensitive)
def row_has_any(row, needles):
    low = {str(x).lower() for x in row.values if pd.notna(x)}
    return any(any(n in cell for n in needles) for cell in low)

def recommend_build(query: str,
                    top_n: int = 5,
                    must_have: list[str] | None = None,
                    boost: dict[str, int] | None = None):
    """
    must_have: list of substrings that must appear in any equip slot (e.g., ["claymore", "finger seal"])
    boost: {"claymore": 3, "bleed": 2} repeats keywords to weight them
    """
    q = preprocess(query)

    # keyword boosting by repetition (simple but effective with TF-IDF)
    if boost:
        for k, times in boost.items():
            q += " " + (" ".join([preprocess(k)] * max(1, times)))

    # optional hard filter for must_have
    if must_have:
        needles = [preprocess(x) for x in must_have]
        mask = raw_df[text_cols].apply(lambda r: row_has_any(r, needles), axis=1)
        df = raw_df[mask].copy()
        if df.empty:
            return []
        X_local = vectorizer.transform(df["build_text"])
    else:
        df = raw_df
        X_local = X

    user_vec = vectorizer.transform([q])
    sims = cosine_similarity(user_vec, X_local).flatten()
    top_idx = np.argsort(sims)[-top_n:][::-1]

    results = []
    # Filter for unique primary weapons
    seen_weapons = set()
    for i in top_idx:
        row = df.iloc[i]
        weapon = row["RH1"]
        if weapon not in seen_weapons:
            results.append({
                "build_id": int(row["build_id"]),
                "similarity": float(round(sims[i], 3)),
                "items": row[text_cols].to_dict()
            })
            seen_weapons.add(weapon)
    return results

if __name__ == "__main__":
    recs = recommend_build(
        "strength bleed",
        top_n=3,
        must_have=["claymore"],
        boost={"claymore": 4, "bleed": 2, "strength": 2}
    )
    for r in recs:
        print(r["build_id"], r["similarity"], r["items"]["RH1"])