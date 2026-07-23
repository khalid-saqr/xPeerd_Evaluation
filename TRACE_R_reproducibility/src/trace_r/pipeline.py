from __future__ import annotations

from pathlib import Path

_PARTS_DIR = Path(__file__).with_name("pipeline_parts")
_PARTS = sorted(_PARTS_DIR.glob("part_*.pyfrag"))
if len(_PARTS) != 11:
    raise RuntimeError(f"Expected 11 TRACE-R pipeline fragments, found {len(_PARTS)}")
_SOURCE = "".join(path.read_text(encoding="utf-8") for path in _PARTS)
exec(compile(_SOURCE, str(Path(__file__).with_suffix(".assembled.py")), "exec"), globals(), globals())
del _SOURCE
