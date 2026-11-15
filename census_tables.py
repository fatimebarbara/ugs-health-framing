"""Census counts (Tables 1, 2, 6, 7 of the paper; Tables B1, B2). Runs on the deposited files.

    python code/census_tables.py
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
F = ["amenity", "climate", "health", "equity", "none", "economic"]


def main():
    d = pd.read_csv(ROOT / "data" / "census_coded_v3.csv")
    valid = d[d.status == "valid"]
    first = d[d.pass1_status == "valid"]
    print(f"retrieved {len(d)} | valid after first pass {len(first)} | valid final {len(valid)} | "
          f"health-framed {int(valid.function_health.sum())}")

    print("\nRejections by class and pass (Tables 2 and B1)")
    r = d[d.status == "rejected"]
    t = pd.crosstab(r.reject_class, r.reject_pass, margins=True, margins_name="total")
    print(t.sort_values("total", ascending=False).to_string())

    print("\nFunctions, final and first pass (Table 6)")
    for f in F:
        n = int(valid["function_" + f].sum())
        n1 = int(first["pass1_" + f].sum())
        print(f"  {f:9s} {n:4d}  {100 * n / len(valid):5.1f}%   first pass {100 * n1 / len(first):5.1f}%")
    codes = valid[["function_" + f for f in F]].sum().sum()
    print(f"  codes per valid post: {codes / len(valid):.2f}")
    h = valid[valid.function_health == 1]
    others = ["function_" + f for f in ["climate", "amenity", "equity", "economic"]]
    print(f"  health with climate {int(h.function_climate.sum())}, amenity {int(h.function_amenity.sum())}, "
          f"equity {int(h.function_equity.sum())}; health only {int((h[others].sum(axis=1) == 0).sum())}")

    print("\nBy city (Table 7)")
    g = d.groupby("city").agg(retrieved=("row", "size"),
                              valid_pass1=("pass1_status", lambda s: (s == "valid").sum()),
                              valid_final=("status", lambda s: (s == "valid").sum()))
    g["rejected_pct"] = (100 * (1 - g.valid_final / g.retrieved)).round(0)
    g["health_n"] = valid.groupby("city").function_health.sum().reindex(g.index).fillna(0).astype(int)
    g["health_pct"] = (100 * g.health_n / g.valid_final).round(1)
    print(g.sort_values("valid_final", ascending=False).to_string())


if __name__ == "__main__":
    main()
