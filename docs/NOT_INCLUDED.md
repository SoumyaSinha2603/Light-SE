# What this repository does not contain, and why

This repository is deliberately **receipts-first**. It is complete for checking the
paper's statistics and incomplete for re-running the experiments from scratch. Being
explicit about the boundary is cheaper than letting a reader discover it.

## Not included, and coming

### Feature-extraction and generation code

Generation, hidden-state extraction, semantic-entropy clustering, and the grid runner
currently live in Colab notebooks. They are not committed yet because publishing them
responsibly requires three things that are not done:

1. Stripping Colab `executionInfo` metadata, which embeds the author's display name
   and numeric user ID in every executed cell of every notebook.
2. Removing hardcoded `/content/drive/MyDrive/...` and local Windows paths.
3. Replacing at least one retired code path (below).

Publishing the notebooks with those defects would be worse than publishing nothing,
so they wait.

### Feature tables for the five non-anchor cells

`results/tqa_llama_features_817.csv` covers the anchor cell (TruthfulQA + Llama-3) and
is enough to recompute that cell's headline numbers, which `verify_numbers.py` does.
The equivalent per-question tables for the other five model×dataset cells are not yet
extracted. The canonical *target* for all six cells is committed in `results/target/`;
what is missing is the feature side.

Note that the committed table carries the canonical `hybrid_SE` target and **not** the
legacy `SE` column present in the source file. That column predates the hybrid
construction by four days, correlates with it at only *r* = +0.436, and disagrees
about zero-ness on 205 of 817 items. Shipping it would invite a reader to recompute
every correlation against the wrong target — which is exactly the error that produced
one of this project's reversals, and, later, a wrong paragraph in the paper itself.
It is dropped at source rather than left for the consumer to notice.

### The interactive HTML figures

Four standalone HTML visualisations exist in the project's working folder and are
**not** published. They were built before the 2026-06-26 corrections and each embeds a
framing the project has since retired: a "model-bound, not task-bound" reading of
curvature (retired as a standalone claim — the effect is endpoint instability, not a
model-family effect), the seed-42-specific "four cells collapse to one" figure (the
general result is a clean count of 0-3 with median 1 across five seeds), and a "survivor
quadrant" framing that was also retired. Publishing them would place three superseded
claims beside a corrected paper. The three PNG figures in `figures/` are the current
ones and are the figures the manuscript uses.

### Raw hidden states

Per-question `.npz` hidden-state dumps run to gigabytes and a pooled array of ~97 MB.
These are regenerable from the specification in the paper rather than archivable in
git. The grid is reconstructible independently: both models are public checkpoints
loaded under the 4-bit NF4 configuration stated in the README, the split is 572/245
at seed 42, the resampling seeds are 42/7/123/2024/99, the curvature window is layers
0–16, and the target is the hybrid construction described in the Methods section.

## Deliberately withheld

### `build_corr_df.py`

An early analysis script that will *not* be committed in its current form, and the
reason is worth stating rather than hiding.

It has two disqualifying properties. First, it is pilot-era: it operates on the
n=248 TruthfulQA pilot, not the 817-question six-cell grid the paper reports, so it
does not produce any number in the manuscript. Second, and more seriously, it loads
the raw LID array and indexes it positionally:

```python
lid_arr = np.load('lid_layer16_k30_PRIMARY.npy')
lid_df  = pd.DataFrame({'question_id': lid_qids, 'lid_k30': lid_arr[lid_qids]})
```

That `.npy` artifact was subsequently found to be **mis-ordered** relative to the
canonical frame construction. The project's own routing rules retired it: LID numbers
come from `results/lid_grid_extension.json` and from nothing else. Committing the
script — or refactoring it forward into a `src/stats.py`, which an earlier migration
plan proposed — would carry a known-bad code path into the public record and invite
someone to reproduce a number the authors already know to be wrong.

It will be replaced by code written against the canonical frame, not resurrected.

## Third-party material not redistributed

Reference PDFs of prior work are cited in the bibliography, not copied here. Model
weights are public checkpoints, downloaded from their original sources.

## Internal project material excluded

Working notes, venue correspondence, submission strategy, and intermediate
methodology logs are not part of the scientific record and are not published. Several
of those logs contain conclusions that were later reversed during the project and
numbers computed against a semantic-entropy column that was subsequently found to be
stale; publishing them would invite a reader to quote an invalidated number back at
the paper. The canonical files in `results/` are the surviving record, and
`results/README.md` documents which of their fields are themselves superseded.
