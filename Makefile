.PHONY: all documentation clean flake8 tests 

PYTHON := python3
PIP := $(PYTHON) -m pip
COVERAGE := $(PYTHON) -m coverage
PY2MD := py2md.py

# Leave CQtoFC.py out for now.  It confuses Doc.py.

MODULES := \
    BOM \
    CNC \
    Doc \
    Embed \
    Geometry \
    Join \
    Node \
    Project \
    Shop \
    Solid \
    TarSync \
    Utilities
#    CQtoFC has Flake8 issues (probably mypy issues as well)

MD_FILES := \
    docs/Fab.md \
    ${MODULES:%=docs/%.md}

FLAKE8_FILES := ${MODULES:%=/tmp/.%.flake8}

all: documentation flake8

# PY_FILES := {${MODULES}:%=%.py}

# DOC_PY_FILES := __init__.py ${PY_FILES}
# OTHER_MD_FILES := \
#     LICENSE.md \
#     README.md \
#     coding_documentation.md \
#     embedded_freecad.md

# COVER_FILES := ${PY_FILES:%.py=%.py,cover} __init__.py,cover
# LINT_FILES := ${PY_FILES:%.py=.%.lint}
# ModFab is generated from __init__.py using a special rule:
# HTML_FILES := ${PY_FILES:%.py=docs/%.md}

# CQtoFc.py currently causes Doc.py to have indigestion.  So leave it off for now.


# MODULES_TXTS := ${MODULES:%=/tmp/%.txt}


CLEAN_FILES := \
    ${FLAKE8_FILES} \
    ${MD_FILES}

#   ${COVER_FILES} \
#   ${LINT_FILES} \
#   ${MODULES_TXTS} \
#   .tests


# Specific rule for "__init__.py" => "docs/ModFab.py":
DOC_GEN := ./Doc.py
docs/ModFab.html: __init__.py
	$(DOC_GEN) __init__
README.html: README.md
	cmark $< > $@

texts: ${MODULES_TXTS}

documentation: ${MD_FILES}


lint: ${LINT_FILES}

tests: .tests

.tests: ${PYTHON_FILES}
	echo "Running coverage"
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

.PHONY: clean flake8


# Pattern Rules:
docs/%.md: %.py
	./Doc.py $<
*.html: %.md
	cmark $@ > $<
.%.lint: %.py
	mypy  $<
	flake8 --max-line-length=100 --ignore=E402,W504 $<
	touch $@
/tmp/%.txt:
	python3 -c "import os ; import sys ; sys.path.extend([os.path.join(os.getcwd(), 'squashfs-root/usr/lib'), '.']) ; import FreeCAD ; import ${@:/tmp/%.txt=%} ; help(${@:/tmp/%.txt=%})" > $@

/tmp/.%.flake8: %.py
	flake8 --max-line-length=100 --ignore=E402,W504 $< && touch $@

# Special Rull for __init__.py => docs/Fab.md
docs/Fab.md: __init__.py
	$(DOC_GEN) __init__


flake8: ${FLAKE8_FILES}


clean:
	rm -f ${CLEAN_FILES}

