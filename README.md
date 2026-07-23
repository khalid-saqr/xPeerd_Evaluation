# xPeerd Evaluation Studies

[![Studies](https://img.shields.io/badge/studies-2-4C78A8)](#studies-at-a-glance)
[![Python](https://img.shields.io/badge/Python-%E2%89%A53.11-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Zenodo DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21479700.svg)](https://doi.org/10.5281/zenodo.21479700)
[![Open Study 2 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/khalid-saqr/xPeerd_Evaluation/blob/main/TRACE_R_reproducibility/TRACE_R_reproducible.ipynb)
[![TRACE-R quality gates](https://img.shields.io/badge/TRACE--R%20quality%20gates-22%2F22%20passing-2E7D32)](TRACE_R_reproducibility/REPRODUCTION_TEST_REPORT.md)
[![Reference checks](https://img.shields.io/badge/reference%20checks-29%2F29%20passing-2E7D32)](TRACE_R_reproducibility/REPRODUCTION_TEST_REPORT.md)
[![TRACE-R licence](https://img.shields.io/badge/TRACE--R%20licence-MIT-2E7D32)](TRACE_R_reproducibility/LICENSE)

This repository contains two complementary studies of **xPeerd peer-review simulations**:

1. **Study 1** characterizes xPeerd simulation performance on its own.
2. **Study 2 (TRACE-R)** compares paired xPeerd and human peer-review reports using a locked, publicly reproducible framework.

> **Naming note:** `xPeerd` is the canonical product spelling used throughout the analyses. Immutable source filenames and legacy paths may retain the archival lowercase spelling `xpeerd`.

## Studies at a glance

| Study | Research question | Comparator | Primary input | Entry point |
|---|---|---|---|---|
| **Study 1 — Intrinsic xPeerd benchmark** | What structural, disciplinary, decision, workload and grounding characteristics are observable in xPeerd simulations? | None; xPeerd is analyzed on its own | CSV with `Prompt`, `Completion`, and optional `Time` | [`xPeerdEvaluation.py`](xPeerdEvaluation.py) |
| **Study 2 — TRACE-R paired evaluation** | How strongly do observable properties of xPeerd reports correspond to paired human reports, and how stable are those findings under deterministic and probabilistic tests? | Two human reports versus two xPeerd reports per manuscript | Version-pinned Zenodo package | [`TRACE_R_reproducibility/`](TRACE_R_reproducibility/) |

---

# Study 1 — Intrinsic benchmark of xPeerd simulations

Study 1 is the repository's original analysis. Its implementation remains unchanged.

## Purpose

Study 1 evaluates xPeerd peer-review simulations **without treating human reports as a reference set**. It transforms unstructured simulation outputs into structured cases, characterizes the generated reviews, performs disciplinary classification, and produces statistical summaries and publication-oriented figures.

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
                     └─> JSON results and figures
```

## Input

The Study 1 CSV requires:

| Column | Requirement | Meaning |
|---|---|---|
| `Prompt` | Required | Original instruction; used to identify the simulation type |
| `Completion` | Required | Full xPeerd peer-review simulation |
| `Time` | Optional | ISO-compatible timestamp |

Supported review modes include `/HCReview`, `/DAReview`, `/DBReviewSim`, `/PRR`, and `/ConfReview`.

## Analysis

The existing Study 1 pipeline performs:

- deterministic parsing of review type, recommendation, major issues, minor issues and anchoring cues;
- ASJC supergroup classification using lexical evidence and `all-MiniLM-L6-v2` sentence embeddings;
- uncertainty diagnostics for the disciplinary classifier;
- decision, workload and anchoring summaries;
- chi-squared tests for categorical associations;
- Kruskal–Wallis tests for group differences;
- Spearman rank correlations for continuous/ordinal relationships;
- five publication-oriented figures.

## Outputs

Study 1 writes its outputs to `/content/xpeerd_outputs`, including:

- `extracted_cases.json`;
- `evaluation_results.json`;
- five PNG figures covering disciplinary composition, decision distributions, length/anchoring relationships, issue distributions and anchoring compliance.

Study 1 answers an **intrinsic characterization** question. It does not estimate agreement with human peer review and should not be interpreted as evidence that a simulation is scientifically correct.

---

# Study 2 — TRACE-R paired human–xPeerd evaluation

[![Open Study 2 in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/khalid-saqr/xPeerd_Evaluation/blob/main/TRACE_R_reproducibility/TRACE_R_reproducible.ipynb)

Study 2 uses **TRACE-R** to compare observable properties of xPeerd reports with human reports attached to the same manuscripts. The complete implementation, tests, environment definitions, reference hashes and public notebook are in [`TRACE_R_reproducibility/`](TRACE_R_reproducibility/).

> TRACE-R measures textual structure, attested manuscript alignment, concern correspondence, category coverage, recommendation association and statistical agreement. It does **not** claim to establish scientific correctness, true novelty, complete flaw recall, true severity, epistemic harm or replacement of human reviewers.

## Public source dataset and provenance

- **Version DOI:** [`10.5281/zenodo.21479700`](https://doi.org/10.5281/zenodo.21479700)
- **Archive:** `xpeerd_benchmark_study_2026_v1.0.0.zip`
- **SHA-256:** `0ab7cb88d2b2db687b586ad303e017a9db0a8104e10f1b8e18c30b8f6a75129c`
- **MD5:** `95bb05a1d2164d66db24a5176749aa77`
- **Records:** 1,108
- **Seed:** `20260723`

The default public workflow resolves the Zenodo record, downloads the archive, verifies both checksums, validates the packaged schema and stops immediately if any pinned invariant fails.

## Transparent cohort construction

For manuscript record \(i\), let:

- \(n_H(i)\) be the number of non-empty human review reports;
- \(n_X(i)\) be the number of non-empty xPeerd reviewer fields among `Reviewer1` and `Reviewer2`;
- \(m(i)=1\) when manuscript text is non-empty.

The locked complete-case cohort is

$$
\mathcal{I}
=
\left\{
i:
n_H(i)=2
\;\land\;
n_X(i)=2
\;\land\;
m(i)=1
\right\}.
$$

The criteria are applied sequentially and are mutually exclusive:

| Outcome | Criterion | Records |
|---|---|---:|
| Excluded | \(n_H=3\) | 265 |
| Excluded | \(n_H=4\) | 33 |
| Excluded | \(n_H=5\) | 8 |
| Excluded | \(n_H=2,\;m=1,\;n_X=0\) | 421 |
| Excluded | \(n_H=2,\;m=1,\;n_X=1\) | 110 |
| Excluded | \(n_H=2,\;m=0\) | 0 |
| **Included** | \(n_H=2,\;m=1,\;n_X=2\) | **271** |
| **Total** |  | **1,108** |

The included dataset therefore contains

$$
271 \times (2\ \text{Human} + 2\ \text{xPeerd}) = 1{,}084
$$

review reports. Missing xPeerd reviewer reports are never imputed or reconstructed.

## Deterministic concern-unit extraction

Reports are segmented into sentence-like units. A unit must contain at least five words and satisfy a declared concern, action or concern-section rule. Each retained unit receives auditable binary or categorical features for:

- explicit manuscript targeting;
- explicit reasoning;
- requested action;
- scientific category;
- presentation-only versus scientific relevance;
- question form.

The nine-category vocabulary is: statistics, study design, methods/reproducibility, data/results, interpretation/claims, literature/context, ethics/reporting, presentation/clarity and other scientific concerns.

For a report with \(U\) extracted units and \(W\) words, concern density is

$$
D = \frac{1000U}{\max(1,W)}.
$$

Reports with no extracted units remain in the analysis with zero-valued unit-derived features.

## The locked TRACE-R profile

TRACE-R does not create a single epistemic-value score. Each dimension is retained separately. Unit-level values are averaged within a report; manuscript-level source profiles then aggregate the two reports from that source.

| Dimension | Operational definition |
|---|---|
| **T — Targeting** | Fraction of units containing an explicit target cue such as a section, figure, table, method, result, sample or dataset |
| **R — Reasoning** | Fraction of units containing an explicit rationale or consequence cue |
| **A — Attested alignment** | Weighted manuscript-grounding proxy combining TF–IDF similarity and token overlap |
| **C — Coverage** | Number of represented concern categories divided by the nine-category vocabulary |
| **E — Executability** | Fraction of units containing an explicit requested action |
| **R — Relevance** | Fraction of units not classified as presentation/clarity only |

### Attested alignment

Manuscripts are divided into 160-word chunks with a 40-word overlap. Concern units and manuscript chunks are represented by sublinear TF–IDF vectors using unigrams and bigrams.

For concern \(u\), let \(p^*(u)\) be its highest-similarity manuscript chunk. Define

$$
s_{\mathrm{TFIDF}}(u)
=
\cos\!\left(
\mathbf{v}_u,
\mathbf{v}_{p^*(u)}
\right),
$$

and let \(C_u\) and \(P_{p^*(u)}\) be the non-stopword content-token sets of the concern and selected chunk:

$$
o_{\mathrm{token}}(u)
=
\frac{
\left|C_u \cap P_{p^*(u)}\right|
}{
\max(1,\left|C_u\right|)
}.
$$

The locked attested-alignment proxy is

$$
A(u)
=
0.75\,s_{\mathrm{TFIDF}}(u)
+
0.25\,o_{\mathrm{token}}(u).
$$

This establishes observable textual attestation, not whether the criticism is scientifically valid.

### Coverage

For report \(r\), with category breadth \(B_r\),

$$
C_r=\frac{B_r}{9}.
$$

## Unique human–xPeerd concern correspondence

For each manuscript, human and xPeerd concern units are represented using the same sublinear unigram/bigram TF–IDF model. Let

$$
S_{uv}
=
\cos(\mathbf{v}^{H}_{u},\mathbf{v}^{X}_{v})
$$

be the human–xPeerd similarity matrix. A Hungarian linear assignment selects the unique pairing

$$
\pi^*
=
\arg\max_{\pi}
\sum_{(u,v)\in\pi} S_{uv}.
$$

At threshold \(\tau\), accepted pairs are

$$
M_\tau
=
\left\{
(u,v)\in\pi^* : S_{uv}\ge\tau
\right\}.
$$

The locked primary threshold is \(\tau=0.35\); sensitivity is reported for

$$
\tau\in\{0.25,0.30,0.35,0.40,0.45,0.50\}.
$$

Two directional proxies are retained:

$$
\text{Human recovery proxy}
=
\frac{|M_{0.35}|}{\max(1,n_H)},
$$

$$
\text{xPeerd alignment proxy}
=
\frac{|M_{0.35}|}{\max(1,n_X)},
$$

where \(n_H\) and \(n_X\) are the extracted concern-unit counts. These are correspondence measures, not precision or recall against scientific ground truth.

Within-source reviewer redundancy is

$$
R_{\mathrm{dup}}
=
\frac{
\#\{\text{uniquely assigned reviewer-unit pairs with }S\ge0.35\}
}{
\max(1,\min(n_1,n_2))
}.
$$

## Statistical stress tests

Association, agreement and source differences are reported separately.

### Paired source differences

For each manuscript-level metric,

$$
d_i=X_i-H_i,
\qquad
\Delta=\frac{1}{N}\sum_{i=1}^{N}d_i.
$$

TRACE-R reports:

- the mean paired difference \(\Delta\);
- percentile bootstrap 95% intervals from 2,000 paired resamples;
- Wilcoxon signed-rank tests;
- paired rank-biserial effect sizes;
- two-sided sign-flip permutation tests with 1,999 replicates.

The sign-flip Monte Carlo \(p\)-value is

$$
p
=
\frac{
1+\#\left\{
|\overline{d}^{\,*}|
\ge
|\overline{d}|
\right\}
}{
B+1
}.
$$

### Association and agreement

For every paired metric, the package reports Pearson \(r\), Spearman \(\rho\), Kendall \(\tau_b\), distance correlation and a partial rank correlation that residualizes each source's ranked metric against that source's ranked report length.

Lin's concordance correlation coefficient is

$$
\rho_c
=
\frac{
2s_{HX}
}{
s_H^2+s_X^2+(\overline{H}-\overline{X})^2
}.
$$

Error and bias diagnostics are

$$
\operatorname{MAE}
=
\frac{1}{N}\sum_{i=1}^{N}|X_i-H_i|,
$$

$$
\operatorname{RMSE}
=
\sqrt{
\frac{1}{N}\sum_{i=1}^{N}(X_i-H_i)^2
},
$$

$$
\text{bias}=\overline{d},
\qquad
\text{limits of agreement}
=
\overline{d}\pm1.96\,s_d.
$$

Spearman and concordance intervals use 2,000 bootstrap resamples; Spearman permutation tests use 1,999 permutations.

### Category and recommendation correspondence

For each concern category, TRACE-R reports prevalence, Jaccard overlap, phi correlation, exact McNemar tests and a Haldane-corrected paired odds ratio:

$$
\operatorname{OR}_{H}
=
\frac{n_{\text{xPeerd-only}}+0.5}{n_{\text{Human-only}}+0.5}.
$$

Recommendations are mapped to an ordinal scale:

$$
\text{reject}=0,
\qquad
\text{revise/reservations}=1,
\qquad
\text{approve}=2.
$$

The secondary recommendation analysis reports source-level consensus means, Spearman association, Lin concordance, quadratic weighted kappa, exact rounded agreement and ordinal MAE. Reviewer identities are not assumed to correspond across sources.

All declared families of \(p\)-values are corrected with the Benjamini–Hochberg procedure.

## Figures

The five multipanel figures use complementary chart families rather than repeating a single representation:

1. distribution and pairing: split violins, ECDF and source comparison;
2. TRACE-R association/agreement: split polar profile, forest estimates and heatmap;
3. correspondence and bias: hexbin/scatter, Bland–Altman and paired differences;
4. category correspondence: lollipop, grouped/stacked bars and association display;
5. recommendations and robustness: confusion/stacked displays and threshold-sensitivity curves.

Each figure shows the Human/xPeerd legend once, in panel **a**, and exports both PDF and 400-dpi PNG formats.

## Reproduce Study 2

### Google Colab

Open [`TRACE_R_reproducible.ipynb`](TRACE_R_reproducibility/TRACE_R_reproducible.ipynb) in a fresh runtime and run all cells. The notebook downloads the DOI-pinned source directly; Google Drive is not required.

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

Offline execution with an already downloaded archive:

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

The locked package records:

| Evidence | Result |
|---|---:|
| Analytical quality gates | **22/22 passed** |
| Reference-output comparisons | **29/29 passed** |
| Figure exports | **10/10 non-empty PDF/PNG files** |
| Included manuscripts | **271** |
| Excluded records | **837** |
| Comparative reports | **1,084** |
| Extracted concern units | **15,563** |

Deterministic CSV tables are compared using exact hashes under the locked environment. Figure bytes are not required to be identical across platforms because fonts and rendering libraries can differ; figures are instead validated through their source tables, existence, nonzero size, panel/legend assertions and reference-output reproduction.

See:

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

Cite the version-specific dataset DOI:

> xPeerd Benchmark Study 2026, version 1.0.0. Zenodo. <https://doi.org/10.5281/zenodo.21479700>

Software citation metadata is provided in [`TRACE_R_reproducibility/CITATION.cff`](TRACE_R_reproducibility/CITATION.cff).
