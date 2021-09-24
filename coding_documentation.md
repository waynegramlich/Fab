# ShopFab Coding and Documenation Standards;

ShopFab is open source software released under the MIT license.
It is much easier for people to contribute to an open source project if the code
is well documented and written in a consistent fashion.

## Coding Style

* Python:
  Python3.8+ is used.
* Indentation:
  Spaces and increments by 4 spaces each indentation level.
* Strings:
  Most strings are in double quotes (i.e "...").
* Line Length:
  The maximum line length is 100 characters (not the more restrictive 80 characters.)
  Line wrapping past 100 characters is not done.
* Type Hints:
  Python type hints are extensively used everywhere
  (function prototypes, variable declarations, etc.)
* Variable Names:
  Whenever possible, full words are used, separated with underscores.
  The code is edited with a spelling checker turned on.
* Type Names:
  Camel Case  is the Python standard.
* Immutable Data Structures:
  Whenever possible Tuples are preferred over Lists.
  Dataclasses with (Frozen=True) are used.

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
  * Unit tests:
    Unit tests are included with the module.
  * Code Coverage:
    All unit tests are run with code coverage enables and unexecuted lines are flagged.

## License:

* License:
  The MIT License is used for all code.

