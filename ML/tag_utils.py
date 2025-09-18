# file: ml/tag_utils.py
import json
import os
import re

current_dir = os.path.dirname(os.path.abspath(__file__))
tags_path = os.path.join(current_dir, "tags.json")

try:
    with open(tags_path, "r", encoding="utf-8") as f:
        TAGS = json.load(f)
except FileNotFoundError:
    raise FileNotFoundError(f"tags.json not found at: {tags_path}")


def expand_query(query: str) -> str:
    """
    Expand a query with tags.json synonyms, while preserving multi-word matches
    like 'rivers of blood' or 'dual katana'.
    """
    q = query.lower()
    expanded = set([q])

    # Multi-word expansions first
    for tag, words in TAGS.items():
        for word in words:
            if word.lower() in q:
                expanded.add(tag.lower())
                expanded.update(w.lower() for w in words)

    # Token-based fallback
    tokens = re.findall(r"\w+", q)
    for token in tokens:
        for tag, words in TAGS.items():
            words_lower = [w.lower() for w in words]
            if token == tag or token in words_lower:
                expanded.add(tag.lower())
                expanded.update(words_lower)

    return " ".join(expanded)


def tags_for_item(item_name: str) -> set[str]:
    """
    Return all tags from tags.json that apply to this item name.
    """
    n = str(item_name).lower()
    item_tags = set()
    for tag, words in TAGS.items():
        words_lower = [w.lower() for w in words]
        if tag in n or any(word in n for word in words_lower):
            item_tags.add(tag)
    return item_tags
