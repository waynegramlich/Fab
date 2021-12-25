.PHONY: all clean lint tests documentation

PYTHON := python3
PIP := $(PYTHON) -m pip
COVERAGE := $(PYTHON) -m coverage
PY2MD := py2md.py

#     ApexPath.py \
#     fcstd_tar_sync.py \
#     py2md.py
PY_FILES := \
    CNC.py \
    Doc.py \
    Embed.py \
    Geometry.py \
    Join.py \
    Solid.py \
    TarSync.py \
    Tree.py \
    Utilities.py
DOC_PY_FILES := __init__.py ${PY_FILES}
OTHER_MD_FILES := \
    LICENSE.md \
    README.md \
    coding_documentation.md \
    embedded_freecad.md

COVER_FILES := ${PY_FILES:%.py=%.py,cover} __init__.py,cover
LINT_FILES := ${PY_FILES:%.py=.%.lint}
# ModFab is generated from __init__.py using a special rule:
HTML_FILES := README.html docs/ModFab.html ${PY_FILES:%.py=docs/%.html}

MODULES := \
    CNC \
    Embed \
    FreeCAD \
    FreeCADGui \
    Join \
    Model \
    Part \
    Path \
    Solid \
    TarSync \
    Utilities
MODULES_TXTS := ${MODULES:%=/tmp/%.txt}

all: documentation lint tests

# Specific rule for "__init__.py" => "docs/ModFab.py":
DOC_GEN := ./Doc.py
docs/ModFab.html: __init__.py
	$(DOC_GEN) __init__
README.html: README.md
	cmark $< > $@

texts: ${MODULES_TXTS}

documentation: ${HTML_FILES}

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


# Pattern Rules:
docs/%.html: %.py
	./Doc.py $<
.%.lint: %.py
	mypy  $<
	flake8 --max-line-length=100 --ignore=E402,W504 $<
	touch $@
/tmp/%.txt:
	python3 -c "import os ; import sys ; sys.path.extend([os.path.join(os.getcwd(), 'squashfs-root/usr/lib'), '.']) ; import FreeCAD ; import ${@:/tmp/%.txt=%} ; help(${@:/tmp/%.txt=%})" > $@



clean:
	rm -f ${COVER_FILES} ${LINT_FILES} ${HTML_FILES} ${MODULES_TXTS} .tests
