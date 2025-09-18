# file: ml/recommend_plus.py
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import os

from .tag_utils import expand_query, tags_for_item


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


def enrich_text(row: pd.Series) -> str:
    """
    Enrich each row's text using tags.json.
    """
    words = []
    for col in text_cols:
        val = str(row[col]).lower() if pd.notna(row[col]) else ""
        words.append(val)
        words.extend(tags_for_item(val))
    return " ".join(words)


# Build enriched training text
raw_df["build_text"] = raw_df.apply(enrich_text, axis=1)
raw_df["build_text"] = raw_df["build_text"].map(preprocess)

# Pre-compute the vectorizer
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(raw_df["build_text"])


def row_has_any(row, needles):
    low = {str(x).lower() for x in row.values if pd.notna(x)}
    return any(any(n in cell for n in needles) for cell in low)


def recommend_build(query: str, top_n: int = 5, must_have=None, boost=None):
    # Expand + preprocess query
    q = preprocess(expand_query(query))

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
                        clean_items[col] = None
                else:
                    clean_items[col] = None

            item_tags = set()
            for val in row[text_cols]:
                if pd.notna(val):
                    item_tags |= tags_for_item(val)

            # Intersection bonus
            if "bleed" in q and "katana" in q and ("katana" in item_tags and "bleed" in item_tags):
                sims[idx] += 0.1

            results.append({
                "build_id": int(row["build_id"]),
                "similarity": float(round(sims[idx], 3)),
                "items": clean_items
            })
            seen.add(key)
    return results


if __name__ == "__main__":
    recs = recommend_build("magic katana", top_n=3)
    for r in recs:
        print(r["build_id"], r["similarity"], r["items"]["RH1"])
