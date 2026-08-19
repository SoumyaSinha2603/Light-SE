# Limitations

Reproduced and expanded from the manuscript's Limitations section. Read this before
quoting any magnitude from this work.

## The target is heavily floored, and it bounds every number here

Semantic entropy over ten generations can take only the finitely many values
attainable by partitions of ten items, and this data occupies that grid very
unevenly. Measured from `results/target/`:

| Cell | Distinct values | At exactly zero | At ceiling (ln 10) |
|---|---|---|---|
| TQA-Llama | 34 | 25.5% | 5.3% |
| TQA-Mistral | 37 | 45.9% | 1.2% |
| Bio-Llama | 36 | 36.4% | 2.0% |
| Bio-Mistral | 36 | 50.1% | 2.3% |
| SQ-Llama | 36 | 21.9% | 6.7% |
| SQ-Mistral | 35 | 36.2% | 1.7% |
| **Pooled (n=4,902)** | **38** | **36.0%** | **3.2%** |

The dominant feature is the **point mass at exactly zero** — items where all ten
generations merge into a single meaning cluster, so the target carries no variance at
all. Over a third of the grid sits there.

Partial correlations computed against a target with more than a third of its mass at
a single floor value are attenuated. The absolute size of every association reported
— geometric and baseline alike — is a **lower bound**, not a calibrated effect size.
Anyone reading *r* ≈ 0.15 as "a small effect" without this caveat is reading it wrong.

This cuts two ways, and both directions matter:

- It does **not** threaten the equal-footing comparison (C-B). Curvature and token
  entropy face the identical target, so the ordering between them is unaffected by
  the floor mass.
- It does plausibly contribute to the held-out instability (C-C). A heavily floored
  target at *n* = 245 is precisely the regime in which CI-cleanness should be
  expected to flicker across resamplings — and that contribution cannot be separated
  from resampling variance itself.

A finer-grained target — more samples per question, or a continuous similarity-based
construction — is the direct way to reduce the floor mass, and is the most
informative single extension of this work.

### A correction, stated in the open

Revisions of this paper up to and including the one archived as Zenodo v1 described
the target as taking **seven distinct values, roughly a third at the maximum, and 6%
at exactly zero**. Those figures are wrong. They were computed from a legacy `SE`
column in the feature table which predates the hybrid semantic-entropy construction
by four days and correlates with it at only *r* = +0.436, disagreeing about zero-ness
on 205 of 817 items in the anchor cell.

The error was confined to the *description of the target*. Every reported correlation
was computed against the correct hybrid target, and none of them changed — the
recomputation in `verify_numbers.py` reproduces the anchor cell exactly. But the
characterisation was not merely imprecise, it was inverted: the real distribution
piles up at the floor, not the ceiling.

`verify_numbers.py` now measures all of these figures from the target files on every
run, so the paper can no longer describe its own data from memory.

## C-C counts cells, not features

The most common misreading. "The CI-clean count swings from zero to three" refers to
**model×dataset cells** — one feature, curvature, evaluated in six cells. It does
**not** mean three different geometric features survived.

An earlier revision of the abstract said "features" here. That was a unit error and
was corrected; `verify_numbers.py` asserts the distinction explicitly.

## Two readings of the BioASQ fork, neither adjudicated

At full power, BioASQ-Mistral is CI-clean and positive (+0.090 [0.021, 0.160]). At the
held-out endpoint the same cell is null and slightly negative (−0.011 [−0.140, 0.122]).

Under one reading the full-sample positives are real and the held-out nulls merely
underpowered, so curvature is a small but fairly general effect sitting near the
*n* = 245 detection floor. Under the other, the full-sample column is optimistic
because it includes the rows on which features were characterised, and the held-out
column is the trustworthy out-of-sample estimate, which is null off the anchor.

The paper does not adjudicate. Because the held-out endpoint is the pre-registered
primary, it defaults to the conservative reading — curvature's effect is not reliably
recoverable out-of-sample beyond the anchor — while reporting the full-817 column in
full so a reader can weigh the alternative.

This is endpoint instability, **not** a model-family effect. The same instability
afflicts cells in both models, which is the point.

## Scope

Two models, three datasets, one curvature definition (mean turning angle over the
0–16 window), one hybrid semantic-entropy construction, one token-entropy baseline. A
different geometric feature or uncertainty target could behave differently — though
the instability finding (C-C) concerns evaluation design and is largely independent of
which specific feature is measured.

## The baseline is question-position, not generation-derived

Token entropy here is computed from the question's forward pass. A generation-derived
token entropy is the more conventional choice and might be stronger still, which would
only deepen the negative result — but it was not tested.

## The length confound is correlational, not causal

Sequence length is highly collinear with the spectral features, but length is not
separable in this data from an upstream factor such as question difficulty. The claim
is that these features are largely explained by length, not that length is the causal
source.

## The mid-band observation is post-hoc

The mid-network layer band where curvature peaks is a post-hoc, cell-specific
observation. The pre-registered 0–16 window is reported as primary precisely to avoid
selecting a window after seeing its result. A pre-registered mid-band study is the
right way to revisit it. Do not read the layer sweep in `week3_state.json` as a
positive result about mid-network layers.

## Held-out power

The held-out sample size (*n* = 245) sits near the detection floor for effects this
small. This is simultaneously part of the C-C instability finding **and** a genuine
limit on the power to affirm a weak geometric signal. Neither edge should be read
alone.
