"""Intra-coder reliability (Table 4). Runs on the deposited files; no post texts needed.

    python code/reliability_alpha.py

Krippendorff's alpha, nominal, two codings, no missing values (Krippendorff 2004;
Hayes and Krippendorff 2007), computed per function on the posts of the re-code
sample that were valid in the final census and kept their first-pass codes
(column in_table4 = 1; n = 59).
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
FUNCTIONS = ["health", "climate", "amenity", "equity", "economic", "none"]


def kalpha_nominal(a, b):
    a = np.asarray(a); b = np.asarray(b)
    n = 2 * len(a)
    observed = np.mean(a != b)
    counts = np.array([(a == v).sum() + (b == v).sum() for v in np.unique(np.r_[a, b])])
    expected = 1 - (counts * (counts - 1)).sum() / (n * (n - 1))
    return float("nan") if expected == 0 else 1 - observed / expected


def main():
    s = pd.read_csv(ROOT / "data" / "recode_sample_128.csv")
    print(f"re-code sample: {len(s)} posts; rejected on the blind second coding: {s.recode_reject.sum()}")
    print(f"final status: {(s.final_status == 'valid').sum()} valid, {(s.final_status == 'rejected').sum()} rejected; "
          f"re-coded in the re-screen: {int(((s.final_status == 'valid') & (s.recoded_in_rescreen == 1)).sum())}")
    t = s[s.in_table4 == 1]
    print(f"\nTable 4 (n = {len(t)}; second-coding rejects among them count as no function: {t.recode_reject.sum()})")
    print(f"{'function':10s}{'alpha':>7}{'agree':>8}{'pass 1':>8}{'pass 2':>8}")
    for f in FUNCTIONS:
        a = t["pass1_" + f].astype(int).values
        b = t["recode_" + f].astype(int).values
        print(f"{f:10s}{kalpha_nominal(a, b):>7.2f}{100 * np.mean(a == b):>7.0f}%{a.sum():>8}{b.sum():>8}")


if __name__ == "__main__":
    main()
