# TRACE-R reproducibility package v1.0.0

This package reproduces the locked TRACE-R comparison of **xPeerd** and human peer-review reports from the version-specific Zenodo dataset DOI **10.5281/zenodo.21479700**.

## Reproducibility contract

The default execution downloads `xpeerd_benchmark_study_2026_v1.0.0.zip` from the published Zenodo record, verifies MD5 and SHA-256, applies mutually exclusive exclusions, regenerates all tables and five multipanel figures, and runs 22 quality gates.

Pinned source SHA-256: `0ab7cb88d2b2db687b586ad303e017a9db0a8104e10f1b8e18c30b8f6a75129c`.

Expected cohort: 1,108 records; 802 with exactly two human reports; 271 strict two-human versus two-xPeerd complete cases; 837 transparently excluded.

## Colab

Open `TRACE_R_reproducible.ipynb` in a fresh Colab runtime and run all cells. No Google Drive is required. The notebook creates `/content/TRACE-R-reproduction/outputs` and a downloadable `TRACE_R_outputs.zip`.

## Command line

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
trace-r --output results
python compare_reference.py results
```

Offline execution with a previously downloaded source package:

```bash
trace-r --input-zip /path/to/xpeerd_benchmark_study_2026_v1.0.0.zip --output results
```

## Docker

```bash
docker build -t trace-r:1.0.0 .
docker run --rm -v "$PWD/results:/app/results" trace-r:1.0.0 --output /app/results
```

## Evidence and limitations

Exact hashes are used for deterministic CSV tables under the locked environment. Figure PDFs/PNGs are validated for existence, nonzero size, panel/legend assertions, and underlying table reproduction; raster or PDF bytes may vary with fonts and rendering libraries. TRACE-R reports observable textual correspondence and proxies, not scientific correctness, true novelty, complete flaw recall, severity calibration, or epistemic harm.
