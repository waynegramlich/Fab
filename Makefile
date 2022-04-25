# Gnu make directives:

# Top level non-file targets:
.PHONY: all clean documentation flake8 html mypy tests tools

# Simple declarations:
PYTHON := python3
PIP := $(PYTHON) -m pip
COVERAGE := $(PYTHON) -m coverage
DOC_GEN := ./Doc.py  # Read Python doc strings, produces btoth Mardown (.md) and HTML (.html) files.
TOOLS_ROOT := FreeCADRoot/Mod/Path/Tools
# List all of the modules to be dealt with:
SAFE_MODULES := \
    BOM \
    Doc \
    FabJoiner \
    FabNodes \
    FabUtilities \
    Geometry \
    Project \
    Shop \
    Solid \
    TarSync \
    Test
NON_SAFE_MODULES := \
    CNC
MODULES := \
    ${SAFE_MODULES} \
    ${NON_SAFE_MODULES}

#    CQtoFC has Flake8 issues (probably mypy issues as well)

# Various files lists derived from MODULES:
PY_FILES := ${MODULES:%=%.py}
MD_FILES := \
    docs/Fab.md \
    ${SAFE_MODULES:%=docs/%.md}
HTML_FILES := \
    docs/Fab.html \
    ${SAFE_MODULES:%=docs/%.html}
TEST_FILES := ${SAFE_MODULES:%=%.py}
FLAKE8_FILES := \
    ${MODULES:%=/tmp/.%.flake8} \
    /tmp/.CQtoFC.flake8
MYPY_FILES := \
    ${MODULES:%=%.py} \
    CQtoFC.py
TOOLS_DIRS := \
    $(TOOLS_DIR)/Bit \
    $(TOOLS_DIR)/Library \
    $(TOOLS_DIR)/Shape
COVER_FILES := ${MODULES:%=%.py,cover}
CLEAN_FILES := \
    ${FLAKE8_FILES} \
    ${MD_FILES} \
    ${HTML_FILES} \
    ${COVER_FILES} \
    .mypy \
    .tests \
    .tools

# Top level ".PHONY" targets:
all: mypy flake8 documentation tests

documentation: ${MD_FILES}

lint: ${LINT_FILES}

flake8: ${FLAKE8_FILES}

clean:
	rm -f ${CLEAN_FILES} .tests

mypy: .mypy  # Use .mypyp to remember when tests were run

.mypy: ${MYPY_FILES}
	mypy ${MYPY_FILES}
	touch $@

tools: .tools

.tools:
	mkdir -p Tools
	( cd $(TOOLS_ROOT) ; tar cf - . ) | (cd Tools ; tar xf -)  # Copy without deleting extras
	rm -f Tools/README.md Tools/toolbit-attributes.py
	touch $@

tests: .tests  # Use .tests to remember that tests were run.

# Use `cover.sh` to suppress output to stdout.  Output to stderr comes through.
.tests: ${TEST_FILES}
	echo "Running coverage"
	if [ ! "$$($(PIP) list | grep '^coverage')" ] ; then \
	   $(PIP) install coverage ; \
	fi
	$(COVERAGE) erase  # Erase previous coverage runs.
	for py_file in ${TEST_FILES} ; do \
	    echo Testing $$py_file ; \
	    if ! ./cover.sh $$py_file ; then \
	        echo "$$py_file >>>>>>>>>>>>>>>> failed" ; \
	    fi ; \
	done
	$(COVERAGE) annotate  # Generate annotated coverage files.
	( grep -n "^!" ${COVER_FILES} | \
	    grep -v "pragma: no unit test" > /tmp/uncovered_lines ) || true
	$(COVERAGE) report  # Generate the summary report.
	$(COVERAGE) erase  # Do not leave around stale coverge information
	rm -f ${COVER_FILES}  # Remove coverage files.
	touch $@

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

# Special Rule for __init__.py => docs/Fab.md
docs/Fab.md: __init__.py
	$(DOC_GEN) __init__


