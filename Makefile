.PHONY: all clean lint tests documentation

PYTHON := python3
PIP := $(PYTHON) -m pip
COVERAGE := $(PYTHON) -m coverage
PY2MD := py2md.py

PYTHON_FILES := \
    apex.py \
    fcstd_tar_sync.py \
    py2md.py

#    shopfab.py
COVER_FILES := ${PYTHON_FILES:%.py=%.py,cover}
MD_FILES := ${PYTHON_FILES:%.py=%.md}
LINT_FILES := ${PYTHON_FILES:%.py=.%.lint}
HTML_FILES := ${PYTHON_FILES:%.py=/tmp/%.html}

all: documentation lint tests

documentation: ${MD_FILES} ${HTML_FILES}  # Use *.py => *.md pattern rules

lint: ${LINT_FILES}

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
	grep -n "^!" ${COVER_FILES} | grep -v "pragma: no unit test" || true  # Flag coverage.
	rm -f ${COVER_FILES}  # Remove annotated coverage files.
	$(COVERAGE) report  # Generate the summary report.
	$(COVERAGE) erase  # Do not leave around stale coverge information
	touch $@


# Pattern Rules:
%.md: %.py
	$(PY2MD) $<
.%.lint: %.py
	mypy  $<
	flake8 --max-line-length=100 --ignore=E402 $<
	pydocstyle $<
	touch $@
/tmp/%.html: %.md
	cmark $< -o $@

clean:
	rm -f ${COVER_FILES} ${MD_FILES} ${LINT_FILES} ${HTML_FILES} .tests
