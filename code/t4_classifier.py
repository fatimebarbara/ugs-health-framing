"""Learned tier T4 (Table 5).

Character n-grams of length 2-5 within word boundaries, TF-IDF weighted;
logistic regression with balanced class weights; five-fold stratified
cross-validation with a fixed seed. Every post is scored by a model trained on
the other four folds (cross_val_predict), and precision, recall and F1 are
computed once on the pooled out-of-fold predictions.

Needs data/texts.csv (tweet_id, text); see README.

    python code/t4_classifier.py
"""
import sys
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.pipeline import make_pipeline

ROOT = Path(__file__).resolve().parents[1]
SEED = 2026


def evaluate(texts, labels):
    model = make_pipeline(
        TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5)),
        LogisticRegression(class_weight="balanced", max_iter=3000),
    )
    folds = StratifiedKFold(n_splits=5, shuffle=True, random_state=SEED)
    pred = cross_val_predict(model, texts, labels, cv=folds)
    p, r, f, _ = precision_recall_fscore_support(labels, pred, average="binary", zero_division=0)
    return p, r, f, pred


def main():
    texts_path = ROOT / "data" / "texts.csv"
    if not texts_path.exists():
        sys.exit("data/texts.csv not found: rehydrate the posts from their tweet_id first (see README).")
    census = pd.read_csv(ROOT / "data" / "census_coded_v3.csv", dtype={"tweet_id": str})
    texts = pd.read_csv(texts_path, dtype={"tweet_id": str})[["tweet_id", "text"]]
    posts = census.merge(texts, on="tweet_id", how="left")
    posts["text"] = posts.text.fillna("").astype(str)

    print(f"{'task':12s}{'n':>6}{'pos':>6}{'P':>6}{'R':>6}{'F1':>6}")
    y = posts.status.eq("valid").astype(int)
    p, r, f, pred = evaluate(posts.text.values, y.values)
    print(f"{'relevance':12s}{len(y):>6}{y.sum():>6}{p:>6.2f}{r:>6.2f}{f:>6.2f}")

    valid = posts[posts.status.eq("valid")]
    for fn in ["health", "climate", "amenity", "equity", "none", "economic"]:
        yy = valid["function_" + fn].astype(int)
        p_, r_, f_, _ = evaluate(valid.text.values, yy.values)
        print(f"{fn:12s}{len(yy):>6}{yy.sum():>6}{p_:>6.2f}{r_:>6.2f}{f_:>6.2f}")

    print("\nRelevance recall by city (cities where the reader accepted at least one post)")
    posts["pred"] = pred
    for city, g in posts[y == 1].groupby("city"):
        print(f"  {city:12s} {g.pred.mean():.2f}  ({int(g.pred.sum())} of {len(g)})")


if __name__ == "__main__":
    main()
