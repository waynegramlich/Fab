.PHONY: all clean lint tests documentation

PYTHON := python3
PIP := $(PYTHON) -m pip
COVERAGE := $(PYTHON) -m coverage
PY2MD := py2md.py

PY_FILES := \
    ApexBase.py \
    ApexNode.py \
    ApexPath.py \
    ApexSketch.py \
    fcstd_tar_sync.py \
    py2md.py
OTHER_MD_FILES := \
    LICENSE.md \
    README.md \
    coding_documentation.md \
    embedded_freecad.md

COVER_FILES := ${PY_FILES:%.py=%.py,cover}
LINT_FILES := ${PY_FILES:%.py=.%.lint}
PY_MD_FILES := ${PY_FILES:%.py=%.md}
ALL_MD_FILES := ${PY_MD_FILES} ${OTHER_MD_FILES}
HTML_FILES := ${ALL_MD_FILES:%.md=%.html}

all: documentation lint tests

documentation: ${ALL_MD_FILES} ${HTML_FILES}  # Use *.py => *.md pattern rules

lint: ${LINT_FILES}

tests: .tests

.tests: ${PYTHON_FILES}
	if [ ! "$$($(PIP) list | grep coverage)" ] ; # Ensure `coverage` package is installed: \
	   then $(PIP) install coverage ; # Do the install \
	fi  # .coveragerc file controls the `# pragma: no cover` and other options.
	$(COVERAGE) erase  # Erase previous coverage runs.
	for py_file in ${PY_FILES}; do  # Collect coverage on the specified files. \
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
	flake8 --max-line-length=100 --ignore=E402,W504 $<
	pydocstyle $<
	touch $@
%.html: %.md
	cmark $< -o $@

clean:
	rm -f ${COVER_FILES} ${LINT_FILES} ${HTML_FILES} .tests
