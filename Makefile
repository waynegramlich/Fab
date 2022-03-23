# Gnu make directives:
.PHONY: all documentation html flake8 clean # tests 

# Simple declarations:
PYTHON := python3
PIP := $(PYTHON) -m pip
COVERAGE := $(PYTHON) -m coverage
DOC_GEN := ./Doc.py  # Read Python doc strings, produces btoth Mardown (.md) and HTML (.html) files.

# List all of the modules to be dealt with:
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

# Generate .md files list and flake8 "touch" file lists:
PY_FILES := ${MODULES:%=%.py}
MD_FILES := \
    docs/Fab.md \
    ${MODULES:%=docs/%.md}
HTML_FILES := \
    docs/Fab.html \
    ${MODULES:%=docs/%.html}
FLAKE8_FILES := ${MODULES:%=/tmp/.%.flake8}
COVER_FILES := ${MODULES:%=%.py,cover}

# Generate a list of all files to delete on make clean target.
CLEAN_FILES := \
    ${FLAKE8_FILES} \
    ${MD_FILES} \
    ${HTML_FILES} \
    ${COVER_FILES}

#   ${COVER_FILES} \
#   ${LINT_FILES} \
#   ${MODULES_TXTS} \
#   .tests

# Top level target 
all: flake8 documentation

documentation: ${MD_FILES}

lint: ${LINT_FILES}

tests: .tests

.tests: ${PYTHON_FILES}
	echo "Running coverage"
	if [ ! "$$($(PIP) list | grep '^coverage')" ] ; then \
	   $(PIP) install coverage ; \
	fi
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

flake8: ${FLAKE8_FILES}

clean:
	rm -f ${CLEAN_FILES}

# Specific rule for "__init__.py" => "docs/ModFab.py":
docs/ModFab.html: __init__.py
	$(DOC_GEN) __init__
README.html: README.md
	cmark $< > $@

# Pattern Rules:
# flake8 pattern rule:
/tmp/.%.flake8: %.py
	flake8 --max-line-length=100 --ignore=E402,W504 $< && touch $@
# Markdown pattern rule:
docs/%.md: %.py
	./Doc.py $<
# HTML pattern rule:
docs/%.html: %.md
	cmark $@ > $<

#.%.lint: %.py
#	mypy  $<
#	flake8 --max-line-length=100 --ignore=E402,W504 $<
#	touch $@

# Special Rull for __init__.py => docs/Fab.md
docs/Fab.md: __init__.py
	$(DOC_GEN) __init__

# /tmp/%.txt:
# 	python3 -c "import os ; import sys ; sys.path.extend([os.path.join(os.getcwd(), 'squashfs-root/usr/lib'), '.']) ; import FreeCAD ; import ${@:/tmp/%.txt=%} ; help(${@:/tmp/%.txt=%})" > $@



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


