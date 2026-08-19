#!/usr/bin/env python3
"""
verify_numbers.py — check every headline number in the LIGHT-SE paper against the
canonical result files in results/.

This is the paper's audit trail. It does NOT re-run the experiments: it asserts that
each quantitative claim in the manuscript is present in, and equal to, the result
files that were fixed at analysis time.

Standard library only. No GPU, no install, no data download:

    python verify_numbers.py

Exit code 0 = every claim traced. Non-zero = at least one claim did not.
"""

import csv
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "results")


def load(name):
    with open(os.path.join(RESULTS, name), encoding="utf-8") as f:
        return json.load(f)


WEEK3 = load("week3_state.json")
BASE = load("baseline_dominance_seedcheck.json")
C4 = load("c4_seed_robustness.json")
LID = load("lid_grid_extension.json")

CURV = WEEK3["audit_closeout"]["curvature_key_estimates"]
LENGTH = WEEK3["audit_closeout"]["length_confound_audit"]

CELLS = ["TQA-Llama", "TQA-Mistral", "Bio-Llama", "Bio-Mistral", "SQ-Llama", "SQ-Mistral"]

results = []


def check(claim, section, paper_value, actual_value, ok=None):
    if ok is None:
        ok = paper_value == actual_value
    results.append((bool(ok), section, claim, paper_value, actual_value))


def approx(a, b, tol=5e-4):
    return abs(a - b) <= tol


# ---------------------------------------------------------------------------
# C-B — a free token-entropy baseline matches or beats every geometric feature
# ---------------------------------------------------------------------------

wins = {c: BASE["per_cell"][c]["te_wins"] for c in CELLS}
check(
    "Token entropy wins 5/5 seeds in five of six cells",
    "C-B",
    5,
    sum(1 for c in CELLS if wins[c] == "5/5"),
)
check(
    "The sixth cell (SQ-Mistral) is 3/5",
    "C-B",
    "3/5",
    wins["SQ-Mistral"],
)

non_degenerate = [c for c in CELLS if c != "SQ-Mistral"]
gaps = [BASE["per_cell"][c]["gap_mean"] for c in non_degenerate]
check(
    "Margin (token entropy - curvature) low end = +0.116",
    "C-B",
    0.116,
    round(min(gaps), 3),
    approx(min(gaps), 0.116),
)
check(
    "Margin high end = +0.191",
    "C-B",
    0.191,
    round(max(gaps), 3),
    approx(max(gaps), 0.191),
)

# The margin's stability is a FIVE-SEED RANGE, not a bootstrap interval.
# See docs/METHODOLOGY.md — this distinction is load-bearing.
excl = [c for c in CELLS if min(BASE["per_cell"][c]["gap_range"]) > 0]
check(
    "Per-seed gap sign stable (5-seed range excludes zero) on 5 of 6 cells",
    "C-B",
    5,
    len(excl),
)
check(
    "SQ-Mistral is the sole cell whose 5-seed range straddles zero",
    "C-B",
    True,
    min(BASE["per_cell"]["SQ-Mistral"]["gap_range"]) < 0
    < max(BASE["per_cell"]["SQ-Mistral"]["gap_range"]),
)

# Table 1 — equal-footing per-cell means
TABLE1 = {
    "TQA-Llama": (0.034, 0.224),
    "TQA-Mistral": (0.011, 0.149),
    "Bio-Llama": (0.077, 0.268),
    "Bio-Mistral": (0.077, 0.195),
    "SQ-Llama": (0.145, 0.261),
    "SQ-Mistral": (0.071, 0.108),
}
for cell, (pc, pt) in TABLE1.items():
    got = BASE["per_cell"][cell]
    check(
        "Table 1 %s: curvature %+.3f / token entropy %+.3f" % (cell, pc, pt),
        "C-B",
        (pc, pt),
        (got["curv_mean"], got["te_mean"]),
        approx(got["curv_mean"], pc) and approx(got["te_mean"], pt),
    )

# ---------------------------------------------------------------------------
# C-A — two prominent spectral features are sequence-length confounds
# ---------------------------------------------------------------------------

eig = LENGTH["eigenscore_full"]["corr_with_seqlen"]
check(
    "Eigenscore correlation with sequence length spans 0.981-0.996",
    "C-A",
    (0.981, 0.996),
    (min(eig), max(eig)),
    approx(min(eig), 0.981) and approx(max(eig), 0.996),
)

eff = LENGTH["effrank_mean"]["pct_length_variance_per_cell"]
eff_full = [v["full_pct"] for v in eff.values()]
check(
    "Effective rank: length + length^2 explain 58-93% of variance",
    "C-A",
    (58, 93),
    (round(min(eff_full), 1), round(max(eff_full), 1)),
    58 <= min(eff_full) < 59 and 92 <= max(eff_full) <= 93,
)
check(
    "Effective rank anchor cell (TQA-Llama) is 83%",
    "C-A",
    83.0,
    eff["TQA-Llama"]["full_pct"],
    approx(eff["TQA-Llama"]["full_pct"], 83.0, 0.05),
)

# Figure 1 caption: curvature's length-independent remainder
pct = LENGTH["curvature_curv_std_w016"]["pct_length_variance_per_cell"]
rem = [100 - v for v in pct.values()]
check(
    "Fig 1: curvature length-independent remainder 59-77%",
    "C-A",
    (59, 77),
    (round(min(rem), 1), round(max(rem), 1)),
    58 <= min(rem) <= 59 and 77 <= max(rem) <= 78,
)

# ---------------------------------------------------------------------------
# C-C — which features survive is set by evaluation design
# ---------------------------------------------------------------------------

check("Full-sample (n=817) CI-clean cell count is fixed at 4", "C-C", 4, C4["full817_clean"])
check("Full-sample count is fixed across seeds", "C-C", True, C4["full817_fixed"])

per_seed = C4["heldout_clean_per_seed"]
check(
    "Held-out clean count per seed [42, 7, 123, 2024, 99] = 1, 0, 3, 2, 0",
    "C-C",
    [1, 0, 3, 2, 0],
    [per_seed[s] for s in ["42", "7", "123", "2024", "99"]],
)
check("Held-out clean count ranges 0-3", "C-C", [0, 3], C4["heldout_range"])
check("Held-out mean clean count 1.2", "C-C", 1.2, C4["heldout_mean"])
check(
    "No cell is CI-clean on all five splits",
    "C-C",
    True,
    "no cell clean on all 5 splits" in C4["verdict"].lower(),
)

# The count is over model x dataset CELLS, not over features. One feature
# (curvature) in six cells. See docs/LIMITATIONS.md.
check(
    "Counts are over cells, not features",
    "C-C",
    True,
    "cell" in C4["verdict"].lower(),
)

# ---------------------------------------------------------------------------
# C-D — the one length-independent feature is small, redundant, split-unstable
# ---------------------------------------------------------------------------

TABLE2_FULL = {
    "TQA-Llama": 0.086,
    "SQ-Llama": 0.100,
    "Bio-Llama": 0.087,
    "Bio-Mistral": 0.090,
    "TQA-Mistral": 0.055,
    "SQ-Mistral": 0.039,
}
for cell, r in TABLE2_FULL.items():
    got = CURV["full817_partial_r"][cell]
    check("Table 2 full-817 %s r = %+.3f" % (cell, r), "C-D", r, got, approx(got, r))

TABLE2_HELD = {
    "TQA-Llama": (0.098, [-0.041, 0.228], False),
    "SQ-Llama": (0.172, [0.050, 0.297], True),
    "Bio-Llama": (0.053, [-0.076, 0.180], False),
    "Bio-Mistral": (-0.011, [-0.140, 0.122], False),
    "TQA-Mistral": (0.044, [-0.085, 0.174], False),
    "SQ-Mistral": (0.030, [-0.086, 0.145], False),
}
for cell, (r, ci, clean) in TABLE2_HELD.items():
    got = CURV["heldout_n245_partial_r"][cell]
    check(
        "Table 2 held-out %s r = %+.3f, CI %s, clean=%s" % (cell, r, ci, clean),
        "C-D",
        (r, ci, clean),
        (got["r"], got["CI"], got["clean"]),
        approx(got["r"], r)
        and approx(got["CI"][0], ci[0])
        and approx(got["CI"][1], ci[1])
        and got["clean"] == clean,
    )

check(
    "SQ-Llama is the sole CI-clean cell on the pre-registered split",
    "C-D",
    1,
    sum(1 for c in CELLS if CURV["heldout_n245_partial_r"][c]["clean"]),
)

anchor = WEEK3["canonical_anchor"]
check(
    "Anchor cell full-817: +0.086 [0.018, 0.156], CI-clean",
    "C-D",
    (0.086, [0.018, 0.156]),
    (anchor["CANONICAL_full817"]["r"], anchor["CANONICAL_full817"]["CI"]),
)

# ---------------------------------------------------------------------------
# LID — reported for completeness only, one appendix line
# ---------------------------------------------------------------------------

sqm = LID["SQ-Mistral"]
check(
    "LID SQ-Mistral full-817 = -0.122 [-0.183, -0.056]",
    "LID",
    (-0.122, [-0.183, -0.056]),
    (round(sqm["pr_full"][0], 3), [round(sqm["pr_full"][1], 3), round(sqm["pr_full"][2], 3)]),
)
check(
    "LID SQ-Mistral held-out = -0.191 [-0.288, -0.081]",
    "LID",
    (-0.191, [-0.288, -0.081]),
    (round(sqm["pr_held"][0], 3), [round(sqm["pr_held"][1], 3), round(sqm["pr_held"][2], 3)]),
)
lid_zero_crossing = sum(
    1 for c in CELLS if LID[c]["pr_full"][1] < 0 < LID[c]["pr_full"][2]
)
check(
    "LID includes zero at full-817 in five of six cells",
    "LID",
    5,
    lid_zero_crossing,
)

# ---------------------------------------------------------------------------
# TARGET — the distribution of hybrid semantic entropy itself
#
# These checks exist because an earlier revision of this paper characterised the
# target from the WRONG COLUMN: a legacy `SE` field in the feature table that
# predates the hybrid construction by four days and correlates with it at only
# r = +0.436. That revision claimed seven distinct values, a third at the maximum
# and 6% at zero. The real target is measured below. Every figure the manuscript
# states about its own target is now computed from the target files, not asserted.
# ---------------------------------------------------------------------------

TARGET_FILES = [
    ("TQA-Llama", "se_hybrid_817.json"),
    ("TQA-Mistral", "se_hybrid_mistral_817.json"),
    ("Bio-Llama", "se_hybrid_bioasq_llama_817.json"),
    ("Bio-Mistral", "se_hybrid_bioasq_mistral_817.json"),
    ("SQ-Llama", "se_hybrid_squadv2_llama_817.json"),
    ("SQ-Mistral", "se_hybrid_squadv2_mistral_817.json"),
]


def target_values(fname):
    with open(os.path.join(RESULTS, "target", fname), encoding="utf-8") as f:
        q = json.load(f)["questions"]
    # clamp -0.0 to 0.0, matching the canonical convention
    return [max(v["se"], 0.0) for v in q.values()]


per_cell = {name: target_values(fn) for name, fn in TARGET_FILES}
pooled = [v for vals in per_cell.values() for v in vals]
CEIL = math.log(10)


def distinct(vals):
    return len({round(v, 6) for v in vals})


def frac(vals, pred):
    return 100.0 * sum(1 for v in vals if pred(v)) / len(vals)


dc = [distinct(v) for v in per_cell.values()]
check(
    "Per-cell distinct target values span 34-37",
    "TARGET",
    (34, 37),
    (min(dc), max(dc)),
)
check("Pooled distinct target values = 38", "TARGET", 38, distinct(pooled))

zero_pcts = {k: frac(v, lambda x: x == 0.0) for k, v in per_cell.items()}
check(
    "Floor mass (SE exactly zero) lowest = 21.9% on SQ-Llama",
    "TARGET",
    21.9,
    round(zero_pcts["SQ-Llama"], 1),
    approx(zero_pcts["SQ-Llama"], 21.9, 0.05)
    and min(zero_pcts, key=zero_pcts.get) == "SQ-Llama",
)
check(
    "Floor mass highest = 50.1% on Bio-Mistral",
    "TARGET",
    50.1,
    round(zero_pcts["Bio-Mistral"], 1),
    approx(zero_pcts["Bio-Mistral"], 50.1, 0.05)
    and max(zero_pcts, key=zero_pcts.get) == "Bio-Mistral",
)
pooled_zero = frac(pooled, lambda x: x == 0.0)
check(
    "Pooled floor mass = 36.0%, i.e. more than a third",
    "TARGET",
    36.0,
    round(pooled_zero, 1),
    approx(pooled_zero, 36.0, 0.05) and pooled_zero > 33.3,
)

ceil_pcts = [frac(v, lambda x: abs(x - CEIL) < 1e-6) for v in per_cell.values()]
check(
    "Ceiling (ln 10) reached on only 1.2-6.7% of items per cell",
    "TARGET",
    (1.2, 6.7),
    (round(min(ceil_pcts), 1), round(max(ceil_pcts), 1)),
    approx(min(ceil_pcts), 1.2, 0.05) and approx(max(ceil_pcts), 6.7, 0.05),
)
check(
    "Target maximum is ln(10) ~ 2.303",
    "TARGET",
    round(CEIL, 3),
    round(max(pooled), 3),
)

# ---------------------------------------------------------------------------
# RECOMPUTE — the anchor cell's headline number, from data rather than from JSON
# ---------------------------------------------------------------------------


def _solve(A):
    k = len(A)
    for c in range(k):
        p = max(range(c, k), key=lambda r: abs(A[r][c]))
        A[c], A[p] = A[p], A[c]
        for r in range(k):
            if r != c and A[c][c] != 0:
                f = A[r][c] / A[c][c]
                for j in range(c, k + 1):
                    A[r][j] -= f * A[c][j]
    return [A[i][k] / A[i][i] for i in range(k)]


def residual(y, X):
    n, k = len(y), len(X[0])
    A = [
        [sum(X[i][a] * X[i][b] for i in range(n)) for b in range(k)]
        + [sum(X[i][a] * y[i] for i in range(n))]
        for a in range(k)
    ]
    b = _solve(A)
    return [y[i] - sum(X[i][j] * b[j] for j in range(k)) for i in range(n)]


def pearson(a, b):
    n = len(a)
    ma, mb = sum(a) / n, sum(b) / n
    num = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    den = math.sqrt(sum((x - ma) ** 2 for x in a)) * math.sqrt(
        sum((x - mb) ** 2 for x in b)
    )
    return num / den


with open(os.path.join(RESULTS, "tqa_llama_features_817.csv"), newline="") as f:
    FEAT = list(csv.DictReader(f))

check("Feature table has 817 rows", "RECOMPUTE", 817, len(FEAT))
check(
    "Split is 572 train / 245 test",
    "RECOMPUTE",
    (572, 245),
    (
        sum(1 for r in FEAT if r["split"] == "train"),
        sum(1 for r in FEAT if r["split"] == "test"),
    ),
)
check(
    "Feature table carries no legacy 'SE' column",
    "RECOMPUTE",
    True,
    "SE" not in FEAT[0] and "hybrid_SE" in FEAT[0],
)

for label, subset, paper_r in (("full-817", None, 0.086), ("held-out n=245", "test", 0.098)):
    sub = [r for r in FEAT if subset is None or r["split"] == subset]
    se = [float(r["hybrid_SE"]) for r in sub]
    cv = [float(r["curv_std_w016"]) for r in sub]
    te = [float(r["token_entropy"]) for r in sub]
    sl = [float(r["seq_len"]) for r in sub]
    X = [[1.0, sl[i], sl[i] ** 2, te[i]] for i in range(len(sub))]
    got = pearson(residual(se, X), residual(cv, X))
    check(
        "Anchor cell %s partial r recomputed from data = %+.3f" % (label, paper_r),
        "RECOMPUTE",
        paper_r,
        round(got, 4),
        approx(got, paper_r, 5e-4),
    )

# ---------------------------------------------------------------------------

def main():
    width = max(len(c) for _, _, c, _, _ in results)
    section = None
    failed = 0
    for ok, sec, claim, paper, actual in results:
        if sec != section:
            print("\n%s" % sec)
            print("-" * (width + 10))
            section = sec
        mark = "ok  " if ok else "FAIL"
        print("  [%s] %s" % (mark, claim.ljust(width)))
        if not ok:
            failed += 1
            print("         paper says : %r" % (paper,))
            print("         files say  : %r" % (actual,))

    total = len(results)
    print("\n%s" % ("=" * (width + 10)))
    print("%d/%d claims traced to results/." % (total - failed, total))
    if failed:
        print("%d FAILED — the manuscript and the result files disagree." % failed)
        return 1
    print("No discrepancy between the manuscript and the canonical result files.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
