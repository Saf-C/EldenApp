# file: ml/recommend_plus.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os


def preprocess(text: str) -> str:
    return str(text).lower().replace("'", "").replace("-", " ")




current_dir = os.path.dirname(os.path.abspath(__file__))
csv_path = os.path.join(current_dir, "../ml_presets_V5.6.csv")

try:
    raw_df = pd.read_csv(csv_path)
except FileNotFoundError:
    raise FileNotFoundError(f"CSV file not found at: {csv_path}")



text_cols = [
    "RH1", "RH2", "LH1", "LH2",
    "Helms", "Chest Armor", "Gauntlets", "Greaves",
    "Talisman1", "Talisman2", "Talisman3", "Talisman4",
    "Spell1", "Spell2", "Spell3", "Spell4",
    "AshOfWar1", "AshOfWar2"
]

raw_df["build_text"] = (
        raw_df[text_cols].fillna("").agg(" ".join, axis=1)
        + " strength dex int faith arcane bleed frost poison fire holy magic lightning scarlet rot"
)
raw_df["build_text"] = raw_df["build_text"].map(preprocess)

# Normalize blanks in Ashes (and other text cols)
raw_df[text_cols] = raw_df[text_cols].replace(r'^\s*$', np.nan, regex=True)


# Pre-compute the vectorizer and vectorized data
# This is done only once when the module is first imported
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(raw_df["build_text"])

def row_has_any(row, needles):
    low = {str(x).lower() for x in row.values if pd.notna(x)}
    return any(any(n in cell for n in needles) for cell in low)

def recommend_build(query: str, top_n: int = 5, must_have=None, boost=None):
    q = preprocess(query)
    if boost:
        for k, times in boost.items():
            q += " " + (" ".join([preprocess(k)] * max(1, times)))

    if must_have:
        needles = [preprocess(x) for x in must_have]
        mask = raw_df[text_cols].apply(lambda row: row_has_any(row, needles), axis=1)
        df = raw_df[mask].copy()
        if df.empty:
            return []
        x_local = vectorizer.transform(df["build_text"])
    else:
        df, x_local = raw_df, X

    user_vec = vectorizer.transform([q])
    sims = cosine_similarity(user_vec, x_local).flatten()

    results, seen = [], set()
    for idx in np.argsort(sims)[-top_n:][::-1]:
        row = df.iloc[idx]
        key = row["RH1"] or row["RH2"]  # dedupe by main weapon
        if key not in seen:
            seen_items = set()
            clean_items = {}
            for col in text_cols:
                val = row[col]
                if pd.notna(val) and str(val).strip() != "":
                    if val not in seen_items:
                        clean_items[col] = val
                        seen_items.add(val)
                    else:
                        clean_items[col] = None  # true duplicate
                else:
                    clean_items[col] = None

            results.append({
                "build_id": int(row["build_id"]),
                "similarity": float(round(sims[idx], 3)),
                "items": clean_items
            })
            seen.add(key)
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