.PHONY: all clean test

PYTHON := python3
PIP := $(PYTHON) -m pip
COVERAGE := $(PYTHON) -m coverage

test:
	# Ensure that Python `coverage` package is installed:
	if [ ! "$$($(PIP) list | grep coverage)" ] ; \
	   then $(PIP) install coverage ; \
	   fi  # .coveragerc file controls the `# pragma: no cover` and the like
	$(COVERAGE) erase # Erase previous coverage information:
	$(COVERAGE) run --append py2md.py  # --rcfile=coverage.rc
	$(COVERAGE) report
	$(COVERAGE) annotate --include=py2md.py
	grep -n "^!" *,cover || true
	rm -f *,cover






