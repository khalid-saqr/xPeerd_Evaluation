PYTHON ?= python
INPUT ?=
OUTPUT ?= results

install:
	$(PYTHON) -m pip install -e .

reproduce:
	trace-r $(if $(INPUT),--input-zip $(INPUT),) --output $(OUTPUT)

test:
	pytest -q -m "not slow"

test-all:
	pytest -q
