# xPeerd Evaluation Studies

[![Studies](https://img.shields.io/badge/studies-2-4C78A8)](#studies-at-a-glance)
[![Python](https://img.shields.io/badge/Python-%E2%89%A53.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21479700.svg)](https://doi.org/10.5281/zenodo.21479700)
[![Open Study 2 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/khalid-saqr/xPeerd_Evaluation/blob/main/TRACE_R_reproducibility/TRACE_R_reproducible.ipynb)
[![TRACE-R quality gates](https://img.shields.io/badge/TRACE--R%20quality%20gates-22%2F22%20passing-2E7D32)](TRACE_R_reproducibility/REPRODUCTION_TEST_REPORT.md)
[![Reference checks](https://img.shields.io/badge/reference%20checks-29%2F29%20passing-2E7D32)](TRACE_R_reproducibility/REPRODUCTION_TEST_REPORT.md)
[![TRACE-R licence](https://img.shields.io/badge/TRACE--R%20licence-MIT-2E7D32)](TRACE_R_reproducibility/LICENSE)

This repository contains two complementary studies of **xPeerd peer-review simulations**:

1. **Study 1** benchmarks and characterizes xPeerd simulations on their own.
2. **Study 2 (TRACE-R)** compares paired xPeerd and human peer-review reports through a locked public reproducibility package.

> **Naming:** `xPeerd` is the canonical product spelling. Immutable archive filenames and legacy paths may retain the lowercase archival spelling `xpeerd`.

## Studies at a glance

| Study | Research question | Comparator | Input | Entry point |
|---|---|---|---|---|
| **Study 1 — Intrinsic xPeerd benchmark** | What structural, disciplinary, decision, workload and grounding characteristics are observable in xPeerd simulations? | None; xPeerd is analyzed on its own | CSV containing `Prompt`, `Completion`, and optional `Time` | [`xPeerdEvaluation.py`](xPeerdEvaluation.py) |
| **Study 2 — TRACE-R paired evaluation** | How strongly do observable xPeerd review properties correspond to paired human reports, and how stable are the findings across deterministic and probabilistic tests? | Two human reports versus two xPeerd reports per manuscript | Version-pinned Zenodo package | [`TRACE_R_reproducibility/`](TRACE_R_reproducibility/) |

---

# Study 1 — Intrinsic benchmark of xPeerd simulations

Study 1 is the repository's original analysis. Its existing implementation is intentionally left unchanged.

## Purpose

Study 1 analyzes xPeerd peer-review simulations **without using human reports as a reference set**. It converts unstructured simulation outputs into structured cases, characterizes review behavior, classifies disciplinary scope, performs statistical tests, and generates publication-oriented figures.

## Workflow

```text
CSV
 └─> case extraction
      ├─> review-type detection
      ├─> decision normalization
      ├─> major/minor issue extraction
      ├─> page/figure/table anchoring
      └─> report metadata
           └─> ASJC supergroup classification
                └─> descriptive and inferential statistics
                     └─> JSON outputs and figures
```

## Input

| Column | Requirement | Meaning |
|---|---|---|
| `Prompt` | Required | Original instruction and review-mode indicator |
| `Completion` | Required | Full xPeerd peer-review simulation |
| `Time` | Optional | ISO-compatible timestamp |

Supported modes include `/HCReview`, `/DAReview`, `/DBReviewSim`, `/PRR`, and `/ConfReview`.

## Analysis

The existing Study 1 pipeline performs:

- deterministic review-type, recommendation, issue and anchoring extraction;
- ASJC supergroup classification using lexical evidence and `all-MiniLM-L6-v2` sentence embeddings;
- uncertainty diagnostics for disciplinary classification;
- decision, workload and anchoring summaries;
- chi-squared tests for categorical associations;
- Kruskal–Wallis tests for group differences;
- Spearman rank correlations for continuous or ordinal relationships;
- five publication-oriented figures.

## Outputs

Study 1 writes to `/content/xpeerd_outputs`, including:

- `extracted_cases.json`;
- `evaluation_results.json`;
- five PNG figures covering disciplinary composition, decision distributions, length/anchoring relationships, issue distributions and anchoring compliance.

**Interpretation boundary:** Study 1 is an intrinsic characterization of xPeerd outputs. It does not estimate correspondence with human peer review and does not establish scientific correctness.

---

# Study 2 — TRACE-R paired human–xPeerd evaluation

[![Open Study 2 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/khalid-saqr/xPeerd_Evaluation/blob/main/TRACE_R_reproducibility/TRACE_R_reproducible.ipynb)

Study 2 applies **TRACE-R** to paired human and xPeerd reports attached to the same manuscripts. The complete notebook, executable Python package, locked configuration, checksums, tests, reference hashes and environment definitions are under [`TRACE_R_reproducibility/`](TRACE_R_reproducibility/).

> TRACE-R measures observable textual structure, manuscript attestation, concern correspondence, category coverage, recommendation association and statistical agreement. It does **not** establish scientific correctness, true novelty, complete flaw recall, true severity, epistemic harm or replacement of human reviewers.

## Public dataset and provenance

| Item | Locked value |
|---|---|
| Version DOI | [`10.5281/zenodo.21479700`](https://doi.org/10.5281/zenodo.21479700) |
| Archive | `xpeerd_benchmark_study_2026_v1.0.0.zip` |
| SHA-256 | `0ab7cb88d2b2db687b586ad303e017a9db0a8104e10f1b8e18c30b8f6a75129c` |
| MD5 | `95bb05a1d2164d66db24a5176749aa77` |
| Records | 1,108 |
| Random seed | `20260723` |
| Bootstrap replicates | 2,000 |
| Permutation replicates | 1,999 |

The public workflow resolves the Zenodo record, downloads the exact archive, verifies both checksums, validates the schema and stops if any pinned invariant changes.

## Transparent cohort construction

For record $i$, define:

- $n_H(i)$: number of non-empty human review reports;
- $n_X(i)$: number of non-empty xPeerd reviewer fields among `Reviewer1` and `Reviewer2`;
- $m(i)=1$: manuscript text is non-empty.

The locked cohort is

```math
\mathcal{I}=\left\{i:\ n_H(i)=2\ \land\ n_X(i)=2\ \land\ m(i)=1\right\}.
```

Criteria are applied sequentially and are mutually exclusive:

| Outcome | Criterion | Records |
|---|---|---:|
| Excluded | $n_H=3$ | 265 |
| Excluded | $n_H=4$ | 33 |
| Excluded | $n_H=5$ | 8 |
| Excluded | $n_H=2$, $m=1$, $n_X=0$ | 421 |
| Excluded | $n_H=2$, $m=1$, $n_X=1$ | 110 |
| Excluded | $n_H=2$, $m=0$ | 0 |
| **Included** | $n_H=2$, $m=1$, $n_X=2$ | **271** |
| **Total** |  | **1,108** |

The comparative dataset contains

```math
271\times\left(2\ \mathrm{Human}+2\ \mathrm{xPeerd}\right)=1{,}084
```

reports. Missing xPeerd reports are never imputed or reconstructed.

## Deterministic concern units

Reports are segmented into sentence-like units. A retained unit must contain at least five words and satisfy a declared concern, action or concern-section rule. Each unit receives auditable features for targeting, rationale, requested action, category, scientific relevance and question form.

The nine categories are:

1. statistics;
2. study design;
3. methods/reproducibility;
4. data/results;
5. interpretation/claims;
6. literature/context;
7. ethics/reporting;
8. presentation/clarity;
9. other scientific concerns.

For a report with $U$ extracted units and $W$ words, concern density is

```math
D=\frac{1000U}{\max(1,W)}.
```

Reports with no extracted concern units remain explicit in the analysis with zero-valued unit-derived features.

## Locked TRACE-R dimensions

TRACE-R does not collapse the dimensions into a single epistemic-value score. Unit-level measurements are aggregated within reports and then across the two reports from each source.

| Dimension | Operational definition |
|---|---|
| **T — Targeting** | Fraction of units containing an explicit target cue such as a section, figure, table, method, result, sample or dataset |
| **R — Reasoning** | Fraction of units containing an explicit rationale or consequence cue |
| **A — Attested alignment** | Weighted manuscript-grounding proxy combining TF–IDF similarity and token overlap |
| **C — Coverage** | Represented concern categories divided by the nine-category vocabulary |
| **E — Executability** | Fraction of units containing an explicit requested action |
| **R — Relevance** | Fraction of units not classified as presentation/clarity only |

### Attested alignment

Manuscripts are split into 160-word chunks with a 40-word overlap. Concern units and chunks use sublinear TF–IDF vectors with unigrams and bigrams.

For concern unit $u$, let $p^*(u)$ be the manuscript chunk with maximum TF–IDF cosine similarity:

```math
s_{\mathrm{TFIDF}}(u)=\cos\!\left(\mathbf{v}_u,\mathbf{v}_{p^*(u)}\right).
```

For non-stopword content-token sets $C_u$ and $P_{p^*(u)}$,

```math
o_{\mathrm{token}}(u)=\frac{\left|C_u\cap P_{p^*(u)}\right|}{\max\!\left(1,\left|C_u\right|\right)}.
```

The locked proxy is

```math
A(u)=0.75\,s_{\mathrm{TFIDF}}(u)+0.25\,o_{\mathrm{token}}(u).
```

This measures textual attestation to manuscript content, not scientific validity.

### Coverage

If report $r$ contains $B_r$ distinct categories,

```math
C_r=\frac{B_r}{9}.
```

## Unique human–xPeerd concern correspondence

For each manuscript, human and xPeerd concern units use the same sublinear unigram/bigram TF–IDF space. Let

```math
S_{uv}=\cos\!\left(\mathbf{v}^{H}_{u},\mathbf{v}^{X}_{v}\right)
```

be the cross-source similarity matrix. Hungarian linear assignment selects

```math
\pi^*=\underset{\pi}{\operatorname{arg\,max}}\ \sum_{(u,v)\in\pi}S_{uv}.
```

At threshold $\tau$,

```math
M_{\tau}=\left\{(u,v)\in\pi^*:S_{uv}\ge\tau\right\}.
```

The primary threshold is $\tau=0.35$, with sensitivity analysis over

```math
\tau\in\left\{0.25,0.30,0.35,0.40,0.45,0.50\right\}.
```

The directional correspondence proxies are

```math
\mathrm{Human\ recovery\ proxy}=\frac{|M_{0.35}|}{\max(1,U_H)},
```

```math
\mathrm{xPeerd\ alignment\ proxy}=\frac{|M_{0.35}|}{\max(1,U_X)},
```

where $U_H$ and $U_X$ are human and xPeerd concern-unit counts. These are not precision or recall against scientific ground truth.

Within-source redundancy is

```math
R_{\mathrm{dup}}=\frac{\#\left\{\text{assigned reviewer-unit pairs with }S\ge0.35\right\}}{\max\!\left(1,\min(U_1,U_2)\right)}.
```

## Deterministic and probabilistic stress tests

Association, agreement and source differences are reported separately.

### Paired source differences

For paired manuscript-level measurements $H_i$ and $X_i$,

```math
d_i=X_i-H_i,\qquad \Delta=\frac{1}{N}\sum_{i=1}^{N}d_i.
```

The package reports the paired mean difference, percentile bootstrap 95% interval, Wilcoxon signed-rank test, paired rank-biserial effect size and a two-sided sign-flip permutation test.

For $B=1{,}999$ sign flips, the Monte Carlo value is

```math
p=\frac{1+\#\left\{|\bar d^{*}|\ge|\bar d|\right\}}{B+1}.
```

### Association and agreement

For each paired metric, TRACE-R reports:

- Pearson $r$;
- Spearman $\rho$ with bootstrap interval and permutation test;
- Kendall $\tau_b$;
- distance correlation;
- partial rank correlation after residualizing each source's ranked metric against that source's ranked report length;
- Lin's concordance correlation coefficient;
- MAE, RMSE and Bland–Altman diagnostics.

Lin's concordance coefficient is

```math
\rho_c=\frac{2s_{HX}}{s_H^2+s_X^2+(\bar H-\bar X)^2}.
```

Error and bias measures are

```math
\operatorname{MAE}=\frac{1}{N}\sum_{i=1}^{N}|X_i-H_i|,
```

```math
\operatorname{RMSE}=\sqrt{\frac{1}{N}\sum_{i=1}^{N}(X_i-H_i)^2},
```

```math
\mathrm{bias}=\bar d,\qquad \mathrm{limits\ of\ agreement}=\bar d\pm1.96s_d.
```

### Category correspondence

For each category, the package reports prevalence, Jaccard overlap, phi correlation, exact McNemar tests and a Haldane-corrected paired odds ratio:

```math
\operatorname{OR}_{H}=\frac{n_{\mathrm{xPeerd\text{-}only}}+0.5}{n_{\mathrm{Human\text{-}only}}+0.5}.
```

### Recommendation correspondence

Human metadata and auditable xPeerd decision lines are normalized to

```math
\mathrm{reject}=0,\qquad \mathrm{revise/reservations}=1,\qquad \mathrm{approve}=2.
```

The secondary recommendation analysis reports source-level consensus means, Spearman association, Lin concordance, quadratic weighted kappa, exact rounded agreement and ordinal MAE. Reviewer identities are not treated as corresponding across sources.

All declared families of $p$-values use Benjamini–Hochberg correction.

## Multipanel figures

The five figures intentionally diversify chart types:

1. **Distribution and pairing:** split violins, ECDF and source comparison;
2. **TRACE-R association/agreement:** split polar profile, forest estimates and heatmap;
3. **Correspondence and bias:** hexbin/scatter, Bland–Altman and paired differences;
4. **Category correspondence:** lollipop, grouped/stacked bars and association display;
5. **Recommendations and robustness:** confusion/stacked displays and threshold-sensitivity curves.

Each multipanel figure shows the Human/xPeerd legend once, in panel **a**, and exports PDF plus 400-dpi PNG.

## Reproduce Study 2

### Google Colab

Open [`TRACE_R_reproducible.ipynb`](TRACE_R_reproducibility/TRACE_R_reproducible.ipynb) in a fresh runtime and run all cells. The notebook downloads the DOI-pinned archive directly; Google Drive is not required.

### Command line

```bash
git clone https://github.com/khalid-saqr/xPeerd_Evaluation.git
cd xPeerd_Evaluation/TRACE_R_reproducibility

python -m venv .venv
source .venv/bin/activate
pip install -e .

trace-r --output results
python compare_reference.py results
```

Offline execution:

```bash
trace-r \
  --input-zip /path/to/xpeerd_benchmark_study_2026_v1.0.0.zip \
  --output results
```

### Docker

```bash
cd TRACE_R_reproducibility
docker build -t trace-r:1.0.0 .
docker run --rm \
  -v "$PWD/results:/app/results" \
  trace-r:1.0.0 \
  --output /app/results
```

## Reproducibility evidence

| Evidence | Result |
|---|---:|
| Analytical quality gates | **22/22 passed** |
| Reference-output comparisons | **29/29 passed** |
| Figure exports | **10/10 non-empty PDF/PNG files** |
| Included manuscripts | **271** |
| Excluded records | **837** |
| Comparative reports | **1,084** |
| Extracted concern units | **15,563** |

Deterministic CSV tables are checked with exact hashes under the locked environment. Figure bytes may vary across platforms because of fonts and rendering libraries; figures are instead checked through source-table reproduction, file existence, nonzero size, panel/legend assertions and reference-output tests.

Documentation:

- [`TRACE_R_reproducibility/README.md`](TRACE_R_reproducibility/README.md)
- [`TRACE_R_reproducibility/METHODS.md`](TRACE_R_reproducibility/METHODS.md)
- [`TRACE_R_reproducibility/REPRODUCTION_TEST_REPORT.md`](TRACE_R_reproducibility/REPRODUCTION_TEST_REPORT.md)
- [`TRACE_R_reproducibility/PUBLICATION_CHECKLIST.md`](TRACE_R_reproducibility/PUBLICATION_CHECKLIST.md)

## Repository layout

```text
.
├── README.md
├── xPeerdEvaluation.py
└── TRACE_R_reproducibility/
    ├── TRACE_R_reproducible.ipynb
    ├── run_trace_r.py
    ├── compare_reference.py
    ├── config/
    ├── checksums/
    ├── reference/
    ├── src/trace_r/
    ├── tests/
    ├── Dockerfile
    ├── environment.yml
    └── requirements-lock.txt
```

## Citation

Cite the version-specific dataset:

> xPeerd Benchmark Study 2026, version 1.0.0. Zenodo. <https://doi.org/10.5281/zenodo.21479700>

Software citation metadata is provided in [`TRACE_R_reproducibility/CITATION.cff`](TRACE_R_reproducibility/CITATION.cff).
