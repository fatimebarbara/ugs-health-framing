"""Lexicon tiers T1 and T2 against the human coding (Table 3, Appendix A).

Reproduces:
  - Table 3: precision, recall and F1 of T1, T2 and T2 without beneficiary terms
  - T2 recall by city (Table 7, cities with at least 8 health-framed posts)
  - the code counts among health-framed posts (Section 4.3)
  - the per-term match counts of Tables A2 and A3 (written to term_counts.csv)

The post texts are not deposited (see README). Put them in data/texts.csv with
two columns, tweet_id and text, then run:

    python code/t1_t2_matching.py

Matching rule (Appendix A of the paper, A.2): a term matches when one of its listed variants
occurs in the post, ignoring case, not preceded or followed by a letter, digit
or underscore. No suffix is allowed. For each post the variants searched are
those of the city's language(s) plus English. T1 and T2 are scored on the valid
posts, every one of which a reader accepted as referring to a green space.
"""
import re
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

CITY_LANGUAGES = {
    "Athens": ["greek"], "Barcelona": ["catalan", "spanish"], "Berlin": ["german"],
    "Bratislava": ["slovak"], "Brussels": ["french", "dutch"], "Bucharest": ["romanian"],
    "Budapest": ["hungarian"], "Copenhagen": ["danish"], "Dublin": ["english"],
    "Helsinki": ["finnish"], "Lisbon": ["portuguese"], "Ljubljana": ["slovenian"],
    "Madrid": ["spanish"], "Paris": ["french"], "Prague": ["czech"], "Riga": ["latvian"],
    "Rome": ["italian"], "Sofia": ["bulgarian"], "Stockholm": ["swedish"],
    "Vienna": ["german"], "Vilnius": ["lithuanian"], "Warsaw": ["polish"],
    "Zagreb": ["croatian"],
}

_cache = {}


def pattern(variant):
    if variant not in _cache:
        _cache[variant] = re.compile(r"(?<!\w)" + re.escape(variant.lower()) + r"(?!\w)")
    return _cache[variant]


def match_matrix(posts, lexicon):
    """Boolean DataFrame: one row per post, one column per lexicon term."""
    rows = []
    for _, post in posts.iterrows():
        text = str(post.text).lower()
        languages = set(CITY_LANGUAGES[post.city] + ["english"])
        hits = []
        for i in lexicon.index:
            hit = False
            for lang in languages:
                cell = lexicon.at[i, lang]
                if isinstance(cell, str):
                    for v in cell.split(";"):
                        v = v.strip()
                        if v and pattern(v).search(text):
                            hit = True
                            break
                if hit:
                    break
            hits.append(hit)
        rows.append(hits)
    return pd.DataFrame(rows, index=posts.index, columns=lexicon.index)


def score(flag, truth):
    tp = int((flag & truth).sum()); fp = int((flag & ~truth).sum()); fn = int((~flag & truth).sum())
    p = tp / (tp + fp) if tp + fp else float("nan")
    r = tp / (tp + fn) if tp + fn else float("nan")
    f = 2 * p * r / (p + r) if p + r else float("nan")
    return int(flag.sum()), tp, fp, fn, p, r, f


def main():
    texts_path = ROOT / "data" / "texts.csv"
    if not texts_path.exists():
        sys.exit("data/texts.csv not found: rehydrate the posts from their tweet_id first (see README).")
    census = pd.read_csv(ROOT / "data" / "census_coded_v3.csv", dtype={"tweet_id": str})
    texts = pd.read_csv(texts_path, dtype={"tweet_id": str})[["tweet_id", "text"]]
    posts = census.merge(texts, on="tweet_id", how="left")
    missing = posts.text.isna().sum()
    if missing:
        print(f"warning: {missing} posts have no text and count as unmatched")
    lexicon = pd.read_csv(ROOT / "lexicon" / "lexicon_v2.1.csv")

    M = match_matrix(posts, lexicon)
    valid = posts.status.eq("valid")
    health = valid & posts.function_health.eq(1)
    layer_b = [i for i in lexicon.index if lexicon.layer[i].startswith("B")]
    code = lexicon.code
    outcome = [i for i in layer_b if code[i] == "outcome"]
    no_ben = [i for i in layer_b if code[i] != "beneficiary"]

    v = posts[valid]
    truth = v.function_health.eq(1)
    print("Table 3 (n = %d valid posts, %d health-framed)" % (len(v), truth.sum()))
    print(f"{'tier':28s}{'flagged':>8}{'TP':>5}{'FP':>5}{'FN':>5}{'P':>6}{'R':>6}{'F1':>6}")
    for name, cols in [("T1 strict lexical", outcome), ("T2 pathway", layer_b),
                       ("T2 without beneficiary", no_ben)]:
        n, tp, fp, fn, p, r, f = score(M.loc[valid, cols].any(axis=1), truth)
        print(f"{name:28s}{n:>8}{tp:>5}{fp:>5}{fn:>5}{p:>6.2f}{r:>6.2f}{f:>6.2f}")

    t2 = M[layer_b].any(axis=1)
    print("\nT2 recall by city (cities with >= 8 health-framed posts)")
    for city, g in posts[health].groupby("city"):
        if len(g) >= 8:
            print(f"  {city:12s} {t2[g.index].mean():.2f}  ({int(t2[g.index].sum())} of {len(g)})")

    print("\nCodes among the health-framed posts (a post can carry several)")
    for c in ["build", "outcome", "beneficiary", "harm", "restore"]:
        cols = [i for i in layer_b if code[i] == c]
        print(f"  {c:12s} {int(M.loc[health, cols].any(axis=1).sum())}")
    print(f"  no Layer B term: {int((~t2[health]).sum())}")

    counts = pd.DataFrame({
        "layer": lexicon.layer.str[0], "term_en": lexicon.term_en, "code": code,
        "posts_retrieved": M.sum().values, "posts_valid": M[valid].sum().values,
        "posts_health_framed": M[health].sum().values,
    })
    out = ROOT / "code" / "term_counts.csv"
    counts.to_csv(out, index=False)
    print(f"\nPer-term counts written to {out.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
