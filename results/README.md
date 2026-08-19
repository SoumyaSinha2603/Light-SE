# Canonical result files

These four files are the paper's receipts. `../verify_numbers.py` checks every
headline quantity in the manuscript against them.

| File | Contents |
|---|---|
| `week3_state.json` | Master state file. Curvature estimates at both endpoints, the length-confound audit, the layer sweep, and the canonical anchor. |
| `baseline_dominance_seedcheck.json` | C-B. Per-cell curvature and token-entropy means on equal footing, seed win-counts, and the five-seed gap range. |
| `c4_seed_robustness.json` | C-C. Held-out CI-clean **cell** counts across seeds 42, 7, 123, 2024, 99. |
| `lid_grid_extension.json` | LID across the full grid. The only valid source for LID numbers. |
| `target/se_hybrid_*.json` | The prediction target itself — per-question hybrid semantic entropy, cluster labels and cluster counts, for all six cells (817 questions each). |
| `tqa_llama_features_817.csv` | Per-question feature table for the anchor cell: canonical `hybrid_SE`, token entropy, sequence length, three curvature variants, and the seed-42 split label. |

## The feature table carries the canonical target, not the legacy one

The source feature table shipped an `SE` column that predates the hybrid
semantic-entropy construction and correlates with it at only *r* = +0.436. That
column is **dropped**; the committed table carries `hybrid_SE`, joined from
`target/se_hybrid_817.json`. Recompute against `hybrid_SE` and nothing else.

## Two things to know before quoting these files

### 1. `week3_state.json` contains a retained audit trail of superseded values

The file documents its own history. It carries a `DOWNSTREAM_STALE_DO_NOT_TRUST`
block listing values that were computed against a semantic-entropy column later found
to be stale, and a `DOWNSTREAM_STALE_RESOLVED_20260626` block recording how each was
corrected. The stale block is **kept on purpose**, as provenance — not because those
values are live.

Quote from these paths, which are current:

- `audit_closeout.curvature_key_estimates.full817_partial_r`
- `audit_closeout.curvature_key_estimates.heldout_n245_partial_r`
- `audit_closeout.length_confound_audit.*.pct_length_variance_per_cell`
- `canonical_anchor.CANONICAL_full817`

Do **not** quote `+0.149` / `+0.208` for the held-out anchor cells, or the retired
`0.458` length-correlation family, or `35–77%` for effective rank. Each was
superseded; the file says so in place.

### 2. Two bootstrap runs of the anchor cell's held-out interval exist

For TQA-Llama held-out, `canonical_anchor.CANONICAL_heldout_n245` gives
*r* = +0.098, CI [−0.043, 0.224], while
`audit_closeout.curvature_key_estimates.heldout_n245_partial_r` gives
*r* = +0.098, CI [−0.041, 0.228].

The point estimate is identical; the interval differs in the third decimal. This is
ordinary bootstrap resampling variation between two runs of the same procedure, not a
disagreement about the result — both include zero, and the verdict (not CI-clean) is
the same either way. The manuscript's Table 2 reports the
`curvature_key_estimates` interval, and `verify_numbers.py` checks against that one.

## The C-B margin has no interval

The win margin (token entropy − curvature) is supported by seed win-counts (`te_wins`)
and by `gap_range`, which is the **minimum and maximum of the per-seed gap over five
seeds**. It is not a bootstrap interval, and no paired bootstrap on the margin exists
anywhere in this project.

The bootstrap confidence intervals that *do* appear here are per-feature, and are used
for the C-C CI-clean count. Do not attach interval language to the margin. See
`../docs/METHODOLOGY.md`.
