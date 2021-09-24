.PHONY: all clean tests documentation

PYTHON := python3
PIP := $(PYTHON) -m pip
COVERAGE := $(PYTHON) -m coverage
PY2MD := py2md.py

PYTHON_FILES := \
    importer.py \
    py2md.py
#     shopfab.py
COVER_FILES := ${PYTHON_FILES:%.py=%.py,cover}
MD_FILES := ${PYTHON_FILES:%.py=%.md}

all: documentation tests

documentation: ${MD_FILES}  # Use *.py => *.md pattern rules

tests: .tests

.tests: ${PYTHON_FILES}
	if [ ! "$$($(PIP) list | grep coverage)" ] ; # Ensure `coverage` package is installed: \
	   then $(PIP) install coverage ; # Do the install \
	fi  # .coveragerc file controls the `# pragma: no cover` and other options.
	$(COVERAGE) erase  # Erase previous coverage runs.
	for py_file in ${PYTHON_FILES}; do  # Collect coverage on the specified files. \
	    $(COVERAGE) run --append "$${py_file}" --unit-test ; # --unit-test forces unit tests \
	done
	$(COVERAGE) annotate  # Generate annotated coverage files.
	grep -n "^!" ${COVER_FILES} || true  # Highlight any uncovered lines.
	rm -f ${COVER_FILES}  # Remove annotated coverage files.
	$(COVERAGE) report  # Generate the summary report.
	$(COVERAGE) erase  # Do not leave around stale coverge information
	touch $@


# Pattern Rules:
%.md: %.py
	$(PY2MD) $<

clean:
	rm -f ${COVER_FILES} ${MD_FILES} .tests
