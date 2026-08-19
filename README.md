# Light-SE

**When Does Geometry Beat a Token-Entropy Baseline for Predicting Semantic Entropy?
A Robustness Audit of Training-Free Hallucination Signals**

> This is an audit, not a detector proposal. The paper reports no detection metric —
> no AUROC, no precision, no recall. The quantity every feature is scored against is
> meaning-clustered **semantic entropy**.

[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.21097426-blue)](https://doi.org/10.5281/zenodo.21097426)
[![Code licence: MIT](https://img.shields.io/badge/code-MIT-green)](LICENSE)
[![Data licence: CC BY 4.0](https://img.shields.io/badge/results-CC%20BY%204.0-green)](LICENSE-DATA)

## TL;DR

A trivial token-entropy baseline — one free scalar, no hidden states — matches or
beats every training-free geometric uncertainty feature tested (trajectory curvature,
eigenscore, effective rank; LID is reported for completeness only) across a 2×3
model×dataset grid. Two of the most prominent geometric features are largely
sequence-length confounds. And the held-out verdict itself is unstable across random
splits.

## Verify the paper's numbers in one command

```bash
python verify_numbers.py
```

Standard library only. No install, no GPU, no data download. The script checks all 52
headline quantities in the manuscript, printing a pass/fail line for each and exiting
non-zero on any disagreement. It does three things:

1. **Traces** every reported estimate, interval and count to the canonical result
   files in `results/`.
2. **Measures** the prediction target's own distribution from `results/target/`,
   rather than taking the paper's word for it.
3. **Recomputes** the anchor cell's headline partial correlation from the feature
   table and the target — arriving at +0.086 (full-817) and +0.098 (held-out),
   matching Table 2 — so at least one number in the paper is verified from data and
   not merely looked up.

This is the point of this repository. Every number in the paper is a claim about a
file that is committed here, and that claim is machine-checkable by anyone in about
one second.

## Headline findings

| # | Finding | Strength |
|---|---|---|
| C-B | Token entropy beats geometry: 5/5 seeds on 5 of 6 cells; margin +0.116 to +0.191 | Primary |
| C-C | Held-out CI-clean **cell** count swings 0–3 across seeds (mean 1.2) while full-817 is fixed at 4 | Primary |
| C-A | Eigenscore ~98–99% length variance; effective rank 58–93% under length + length² | Supporting |
| C-D | Curvature: genuine but small (partial *r* ≈ 0.1–0.18), redundant with the baseline, split-unstable | Honest negative |

Presented in the paper's escalation order.

**Read C-C carefully.** The count is over model×dataset **cells** — one feature
(curvature) evaluated in six cells — not over features. It does not mean three
different geometric features survived. See [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Setup studied

- **Models** — `meta-llama/Meta-Llama-3-8B-Instruct` and `mistralai/Mistral-7B-Instruct-v0.2`,
  both under an identical 4-bit NF4 config (double quantisation, `compute_dtype=float16`),
  so any cross-model difference reflects the model and not its compression.
- **Datasets** — TruthfulQA, BioASQ, SQuAD v2. 817 questions each, split 572/245 at seed 42.
- **Target** — hybrid semantic entropy over ten sampled generations: embedding cosine
  (`all-mpnet-base-v2`) ≥ 0.90 **and** `roberta-large-mnli` non-contradiction in both
  directions, clustered by connected components.
- **Resampling seeds** — 42, 7, 123, 2024, 99.
- **Curvature window** — layers 0–16, fixed by pre-registration.

## What is here

```
results/                        canonical result files — the receipts behind every number
  target/                       hybrid semantic entropy per question, all six cells
  tqa_llama_features_817.csv    per-question feature table for the anchor cell
figures/                        the three manuscript figures
paper/                          manuscript source, bibliography, and compiled PDF
docs/                           methodology, limitations, what is missing
verify_numbers.py
```

`results/target/` holds the prediction target itself — per-question semantic entropy,
cluster labels and cluster counts for all 4,902 model×dataset items. Together with
`tqa_llama_features_817.csv` this is enough to recompute the anchor cell's results
from scratch, which `verify_numbers.py` does.

## What is NOT here (yet)

This repository is **receipts-first**. It makes the paper's statistics checkable; it
is not yet an end-to-end pipeline. See [docs/NOT_INCLUDED.md](docs/NOT_INCLUDED.md)
for the full account, including one file deliberately withheld because it contains a
retired code path. In short, still to come:

- Feature-extraction and generation code, refactored out of Colab notebooks
- Feature tables for the five non-anchor cells
- Raw hidden states — gigabytes of `.npz`, regenerable rather than archivable

## Known limitation, stated up front

The target is heavily floored. Semantic entropy over ten generations can only take
values attainable by partitions of ten items; each cell realises 34–37 of them, and
the ceiling (ln 10 ≈ 2.303) is reached on just 1.2–6.7% of items. The dominant
feature of the distribution is a **large point mass at exactly zero** — every one of
the ten generations merging into a single meaning cluster — covering 21.9% of items
on SQuAD-Llama, 50.1% on BioASQ-Mistral, and **36.0% pooled across the grid**.

Every partial correlation reported — geometric and baseline alike — is therefore an
attenuated lower bound rather than a calibrated effect size. This bounds absolute
magnitudes. It does not affect the ordering between features, which face an identical
target.

These figures are measured by `verify_numbers.py` from `results/target/` on every
run, not asserted. That is deliberate: an earlier revision of this paper described
the target from a legacy column that predates the hybrid construction and correlates
with it at only *r* = +0.436, and reported seven distinct values with a third at the
maximum. Those numbers were wrong. See [docs/LIMITATIONS.md](docs/LIMITATIONS.md).

## Citation

See [CITATION.cff](CITATION.cff). Cite the concept DOI
[10.5281/zenodo.21097426](https://doi.org/10.5281/zenodo.21097426), which always
resolves to the latest version.

## Licence

Code MIT ([LICENSE](LICENSE)) · results and figures CC BY 4.0
([LICENSE-DATA](LICENSE-DATA)).
