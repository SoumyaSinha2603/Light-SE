# Methodology

Condensed from the manuscript's Methods section. `paper/LIGHT-SE_v5.pdf` is the
authoritative statement; this file exists so the repository is self-contained.

## Grid

Six model×dataset cells: `meta-llama/Meta-Llama-3-8B-Instruct` and
`mistralai/Mistral-7B-Instruct-v0.2`, each on TruthfulQA, BioASQ, and SQuAD v2.

Both models load with an identical `BitsAndBytesConfig` — `load_in_4bit=True`,
`bnb_4bit_quant_type=nf4`, `bnb_4bit_use_double_quant=True`,
`bnb_4bit_compute_dtype=float16`. Stated explicitly because identical quantisation
means any cross-model difference reflects the model rather than its compression.

Each dataset contains 817 questions, split 572/245 (train/test) at seed 42, applied
uniformly to all six cells. Ten independent generations per question via the chat
template with the question as the sole user turn: `do_sample=True`, temperature 1.0,
top-*p* 0.9, `max_new_tokens=50`, input truncation at 512 tokens, produced by ten
separate decoding calls rather than batched return sequences.

## Prediction target: hybrid semantic entropy

Semantic entropy over the ten generations. Two generations join the same meaning
cluster when they satisfy both halves of a hybrid equivalence relation: embedding
cosine similarity (`all-mpnet-base-v2`) ≥ 0.90 **and** `roberta-large-mnli` returning
a non-contradiction label in both directions. Clusters form by connected components;
semantic entropy is the entropy of the resulting cluster distribution.

Two signals are hybridised because strict bidirectional NLI entailment alone fails to
recognise obvious paraphrases at any usable threshold. The target is treated as fixed
ground truth, not proposed as a contribution.

## The baseline geometry must beat: token entropy

Mean per-token predictive entropy — the entropy of the next-token distribution
averaged over the question's forward pass. One scalar per question, no hidden states,
no sampling.

**On non-circularity.** It is computed from the model's logits in the same forward
pass used to extract the geometric features, and is wholly separate from the
answer-sampling pipeline that defines the target. The target is a hybrid of two
equivalence relations with no token-entropy term. The comparison is therefore not
circular, and any cell where token entropy matches or beats a geometric feature is a
fair result rather than a shared-input artifact.

## Geometric features

Hidden states are extracted from the bare question only (truncation at 512 tokens),
so every geometric feature — and the baseline — is a property of the question's
forward trajectory rather than of the sampled answers. States are saved at nine
layers: {0, 4, 8, 12, 16, 20, 24, 28, 31}.

- **Curvature** — mean turning angle along the per-layer trajectory of mean-pooled
  hidden states over the pre-registered 0–16 sub-window (layers 0, 4, 8, 12, 16),
  with per-layer standardisation **fit on training rows only**, so no test
  information enters the feature.
- **Eigenscore** — computed on the full per-token, per-layer stack, mean-centred, as
  the Shannon entropy of normalised **squared** singular values:
  with *pᵢ* = *sᵢ*² / Σ*sⱼ*², eigenscore = −Σ *pᵢ* log *pᵢ*.
- **Effective rank** — computed on the mean-pooled per-layer trajectory (the 9 × 4096
  matrix of layer means, mean-centred) as the **exponential** of the entropy of the
  **raw** normalised singular values: with *ŝₙ* = *Sₙ* / Σ*Sₘ*,
  effective rank = exp(−Σ *ŝₙ* log *ŝₙ*).
- **LID** — local intrinsic dimensionality by local TwoNN over the layer-16
  last-token neighbourhood, neighbour tree built on training rows only.

Eigenscore and effective rank differ deliberately: squared versus raw singular values,
entropy versus exponentiated entropy, full token stack versus mean-pooled trajectory.
Both forms follow their original definitions.

## Controls and estimation

All feature–target associations are partial correlations with bootstrap 95%
confidence intervals. A feature is **CI-clean** in a cell when its interval excludes
zero.

Sequence length **and its square** are controlled throughout. The nonlinear term is
load-bearing: linear-only length control leaks signal that the quadratic term removes,
and effective rank's apparent survival under linear-only control disappears once the
quadratic term is added.

Two analyses use the controls differently, and conflating them is the most common way
to misread the results:

| Question | Controls |
|---|---|
| Does a geometric feature carry signal *beyond* the free baseline? | sequence length, length², **and token entropy** |
| Which of curvature and token entropy better predicts semantic entropy? | sequence length and length² only — the identical control set for both, with neither controlled for the other |

One cannot control a feature for token entropy and then compare it against token
entropy. This is why SQuAD-Llama's held-out estimate differs slightly between regimes
(+0.172 vs +0.178): the difference is the additional token-entropy term, nothing else.

## Evaluation protocol and pre-registration

The pre-registered primary endpoint is the held-out test set (*n* = 245, 30% split,
seed 42). The full-sample evaluation (*n* = 817) is reported **only** as a power
supplement and is explicitly not an out-of-sample claim, since it includes the rows on
which features were characterised.

To test whether held-out conclusions are reproducible rather than split-specific, the
held-out evaluation is repeated across five random splits (seeds 42, 7, 123, 2024, 99)
and the variation in the CI-clean set is reported.

The curvature window 0–16 is fixed by pre-registration. A post-hoc layer sweep is
reported separately and labelled as such, so that no window is selected after seeing
its result.

## One distinction that is load-bearing

**The C-B win margin has no confidence interval of any kind.** Its support is (a)
per-seed win counts and (b) the five-seed range of the gap. The bootstrap intervals
elsewhere in this project are per-feature and belong to the C-C CI-clean count.

With five seeds, "the five-seed range excludes zero" and "the per-seed sign is stable"
are the same statement. Neither is a bootstrap result. An earlier manuscript revision
described the margin's stability as a bootstrap interval; that was a mislabel of the
five-seed range and was corrected. No number changed.

If a reader wants a paired within-sample interval on the margin, that is a genuine
gap in this analysis and would require new computation, not a lookup.
