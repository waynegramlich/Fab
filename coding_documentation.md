# Apex Coding and Documentation Standards;

Apex is open source software released under the MIT license.
It is much easier for people to contribute to an open source project if the code
is well documented and written in a consistent fashion.

## Coding Style

* Python:
  Currently Python 3.8+ is used.
* Indentation:
  Spaces and increments by 4 spaces each indentation level.
* Line Length:
  The maximum line length is 100 characters (not the more restrictive 80 characters.)
  Line wrapping past 100 characters is not done.
* Strings:
  Most strings are in double quotes (i.e "...").
* Long strings:
  Long string are broken into chunks and concatenated "very long str" => ("very " "long " "str")
* Formatted strings:
  f"...{exp1}...{exp2}...{expN}..." is the preferred.
* Type Hints:
  Python type hints are extensively used everywhere
  (function prototypes, variable declarations, etc.)
* Immutable Data Structures:
  Whenever possible Tuples are preferred over Lists.
  Python Dataclasses with (Frozen=True) are frequently used.
* Alphabetical ordering:
  Classes, method, and attributes are sorted alphabetically (where '_' is treated as a space.)
* Private vs Public:
  Private classes/methods/attributes start with an underscore ('_').
  Public classes/method/attributes start with a letter.
* Variable Names:
  Whenever possible, full words are used, separated with underscores.
  The code is typically edited with a spelling checker turned on.
* Type Names:
  Camel Case is the Python standard.

## Documentation Standards:

* Document strings:
  Document strings adhere to most the Python standards.
  One quirk is that they are written in markdown to support extraction to a Markdown file.
* Comments:
  Comments in the code are strongly encouraged.  A paragraph style is used where
  a sentence precedes each block of code.  It should be possible to read the comments
  to get the overall flow of the code.  Again Markdown syntax is used in comments.
* Overview:
  Whenever possible overview comments are provided to explain design, algorithm and
  data structure decisions.
* Markdown Documentation:
  They `py2md.py` document strings and generates a `.md` Markdown file.
  Not great, but better than nothing.
  These markdown files are checked in so that GitHub.Com will convert them to HTML files.

## Testing:

* Linting:
  * mypy:
    The mypy static type checker is used.
  * flake8:
    The Flake8 style enforcer is used.  (Options: --maximum-line-length=100 -Q00)
  * pydocstyle:
    Used to get enforce additional documentation style.

* Testing:
  * Argument Checking:
    Public methods test argument validity and raise a `ValueError` exception for bad arguments.
    The `ApexCheck` class is used for this.
  * Unit tests:
    Unit tests are included with the module.
  * Code Coverage:
    All unit tests are run with code coverage enables and unexecuted lines are flagged.
    The goal is to have "100%" code coverage.
    `#pragma: no unit coverage` is used to indicate code lines not caught by the unit tests.
  * Tracing:
    Tracing is a standard debugging technology and follows pattern immediately below:

         def my_method(self, ..., tracing: str = "") -> ResultType:
	     """Doc string."""
	     next_tracing: str = tracing + " " if tracing else ""
	     if tracing:
	         print(f"{tracing}=>MyClass.my_method(...)")
             # ...
             call_some_other_function_with_tracing(..., tracing=next_tracing)

	     result: ResultType = ...
	     if tracing:
	         print(f"{tracing}<=MyClass.my_method(...)=>{result}"
	     return result

## License:

*
License:
  The MIT License is used for all code.
  This should be compatible with the LGPL2+ license preferred by the FreeCAD community.


