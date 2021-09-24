.PHONY: all clean tests

PYTHON := python3
PIP := $(PYTHON) -m pip
COVERAGE := $(PYTHON) -m coverage

PYTHON_FILES := \
    importer.py \
    py2md.py
#     shopfab.py
COVER_FILES := ${PYTHON_FILES:%.py=%.py,cover}

all: tests

tests:
	# Ensure that Python `coverage` package is installed:
	if [ ! "$$($(PIP) list | grep coverage)" ] ; \
	   then $(PIP) install coverage ; \
	fi  # .coveragerc file controls the `# pragma: no cover` and the like
	$(COVERAGE) erase  # Erase previous in coverage runs
	for py_file in ${PYTHON_FILES}; do  # Collect coverage on the specified files \
	    $(COVERAGE) run --append "$${py_file}" --unit-test ; \
	done
	$(COVERAGE) report  # Generate a summary report
	$(COVERAGE) annotate  # Generate annotated coverage files
	grep -n "^!" ${COVER_FILES} || true  # Highlight uncovered lines
	rm -f ${COVER_FILES}  # Remove annotated coverage files
