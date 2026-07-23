from __future__ import annotations

import gzip
import hashlib
import json
import os
import zipfile
from pathlib import Path

import nbformat
import pytest

from trace_r.acquisition import MD5, SHA256, verify
from trace_r.pipeline import run_analysis

ROOT = Path(__file__).parents[1]
EXPECTED_PIPELINE_SHA256 = "d597573656bde055bd527c127dc9eb130bc62ff36ad37fdf54647a618c57f20d"


def _nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def test_pinned_source_constants():
    assert len(SHA256) == 64
    assert len(MD5) == 32


def test_pipeline_fragment_integrity():
    parts = sorted((ROOT / "src/trace_r/pipeline_parts").glob("part_*.pyfrag"))
    assert len(parts) == 11
    assembled = "".join(path.read_text(encoding="utf-8") for path in parts)
    assert hashlib.sha256(assembled.encode("utf-8")).hexdigest() == EXPECTED_PIPELINE_SHA256


def test_notebook_contract():
    nb = nbformat.read(ROOT / "TRACE_R_reproducible.ipynb", as_version=4)
    processing = [c for c in nb.cells if c.cell_type == "code" and c.source.lstrip().startswith("# CELL")]
    figures = [c for c in nb.cells if c.cell_type == "code" and c.source.lstrip().startswith("# FIGURE CELL")]
    assert len(processing) == 10
    assert len(figures) == 5
    assert all(c.outputs == [] and c.execution_count is None for c in nb.cells if c.cell_type == "code")


def test_local_source_and_cohort_contract_when_supplied():
    value = os.environ.get("TRACE_R_TEST_ZIP")
    if not value:
        pytest.skip("TRACE_R_TEST_ZIP not supplied")
    source = Path(value)
    observed = verify(source)
    assert observed["sha256"] == SHA256 and observed["md5"] == MD5
    with zipfile.ZipFile(source) as zf:
        members = [name for name in zf.namelist() if name.endswith(".jsonl.gz")]
        assert len(members) == 1
        with zf.open(members[0]) as raw, gzip.GzipFile(fileobj=raw) as gz:
            records = [json.loads(line) for line in gz if line.strip()]
    assert len(records) == 1108
    exactly_two = 0
    strict = 0
    for record in records:
        humans = record.get("human_reviews") or []
        xpeerd = record.get("xpeer_simulation") or {}
        nh = sum(_nonempty(h.get("review_text")) for h in humans if isinstance(h, dict))
        nx = sum(_nonempty(xpeerd.get(key)) for key in ("Reviewer1", "Reviewer2"))
        manuscript_ok = _nonempty((record.get("manuscript") or {}).get("manuscript_text"))
        exactly_two += nh == 2
        strict += nh == 2 and nx == 2 and manuscript_ok
    assert exactly_two == 802
    assert strict == 271


@pytest.mark.slow
def test_full_reproduction_when_supplied(tmp_path):
    value = os.environ.get("TRACE_R_TEST_ZIP")
    if not value:
        pytest.skip("TRACE_R_TEST_ZIP not supplied")
    report = run_analysis(Path(value), tmp_path / "results")
    assert report["status"] == "PASS"
    assert report["included_manuscripts"] == 271
    assert report["quality_checks_passed"] == report["quality_checks_total"] == 22
    assert report["figure_files_passed"] == 10
