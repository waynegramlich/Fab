# Doc: Doc: Convert Python doc strings to Markdown files.
The Doc program reads Python files and generates Markdown files from embedded doc strings.
These files can be converted into HTML files via a Markdown program like `cmark`.

     Usage:
       python3 Doc.py [--directory=OUTPUT_DIR] [--markdown=CONVERTER] [FILES_NAMES_DIRECTORIES...]

As a convenience, the inputs can be specified as a combination of the following:
* Python File:  A Python file has a suffix of `.py`.
* Python Module Name:  A Python file without the `.py`. suffix.
* Python Package Directory: A directory containing Python files.
  If the directory contains an `__init__.py` file, they `__init__.py` file is scanned for a doc
  string and processed.  The first line of the doc string must be for the format
  `PACKAGE_NAME: ...` and it generates a corresponding `PACKAGE_NAME.md` file name.

If no output directory is explicitly specified via `--directory=...`, the default is to
try to use a local `docs` directory first, followed by `/tmp` second.

If `--markdown=CONVERTER` is specified, the CONVERTER is run as `CONVERTER FILE.md -o FILE.html`
as a convenience.  If `--markdown=...` is not specified and `cmark` is in accessible via your
PATH environment variable.  `--markdown=` is used to disable automatic conversion via `cmark`.

In general, running `python3 Doc` (or `./Doc.py`) will scan the current directory, write out
the markdown files and convert them to HTML files in the local `docs` sub-directory.

This is a relatively dumb program.  All Python doc strings need to be written in Markdown notation.

## Table of Contents (alphabetical order):

* 1 Class: [ModelClass](#doc--modelclass):
  * 1.1 [set_annotations()](#doc----set-annotations): Set the Markdown anchor.
  * 1.2 [summary_lines()](#doc----summary-lines): Return ModelModule summary lines.
  * 1.3 [documentation_lines()](#doc----documentation-lines): Return the ModelModule documentaion lines.
* 2 Class: [ModelDoc](#doc--modeldoc):
  * 2.1 [set_lines()](#doc----set-lines): Set the Lines field of a ModelDoc.
  * 2.2 [set_annotations()](#doc----set-annotations): Set the ModelDoc Anchor and Number attributes.
* 3 Class: [ModelFunction](#doc--modelfunction):
  * 3.1 [set_annotations()](#doc----set-annotations): Set the markdown annotations.
  * 3.2 [summary_lines()](#doc----summary-lines): Return ModelModule table of contents summary lines.
  * 3.3 [documentation_lines()](#doc----documentation-lines): Return the ModelModule documentaion lines.
* 4 Class: [ModelModule](#doc--modelmodule):
  * 4.1 [set_annotations()](#doc----set-annotations): Set the Markdown anchor.
  * 4.2 [summary_lines()](#doc----summary-lines): Return ModelModule summary lines.
  * 4.3 [documentation_lines()](#doc----documentation-lines): Return the ModelModule documentaion lines.
  * 4.4 [generate()](#doc----generate): Generate the markdown and HTML files.

## <a name="doc--modelclass"></a>1 Class ModelClass:

Represents a class method.
Attributes:
*  Inherited Attributes: *Name*, *Lines*, *Anchor*, *Number* from ModelDoc.
* *Class* (Any): The underlying Python class object that is imported.
* *Functions* (Tuple[ModelFunction, ...]): The various functions associated with the Class.

### <a name="doc----set-annotations"></a>1.1 `ModelClass.`set_annotations():

ModelClass.set_annotations(self, anchor_prefix: str, number_prefix: str) -> None:

Set the Markdown anchor.

### <a name="doc----summary-lines"></a>1.2 `ModelClass.`summary_lines():

ModelClass.summary_lines(self, indent: str) -> typing.Tuple[str, ...]:

Return ModelModule summary lines.

### <a name="doc----documentation-lines"></a>1.3 `ModelClass.`documentation_lines():

ModelClass.documentation_lines(self, prefix: str) -> typing.Tuple[str, ...]:

Return the ModelModule documentaion lines.


## <a name="doc--modeldoc"></a>2 Class ModelDoc:

Base class ModelFunction, ModelClass, and ModelModule classes.
Attributes:
* *Name* (str):
   The Document element name (i.e. function/class/module name.)
* *Lines* (Tuple[str, ...]):
   The documentation string converted into lines with extraneous indentation removed.
   This attribute is  set by the *set_lines*() method.
* *Anchor* (str):
   The generated Markdown anchor for the documentation element.
   It is of the form "MODULE--CLASS--FUNCTION", where the module/class/function names
   have underscores converted to hypen.
* *Number* (str):
   The Table of contents number as a string.  '#" for classes and "#.#" for functions.

### <a name="doc----set-lines"></a>2.1 `ModelDoc.`set_lines():

ModelDoc.set_lines(self, doc_string: typing.Union[str, NoneType]) -> None:

Set the Lines field of a ModelDoc.
Arguments:
* *doc_string* (str): A raw doc string.

This method takes a raw doc string where the first line has no embedded indentation
space and subsequent non-empty lines have common indentation padding and converts
them into sequence of lines that have the common inendation removed.

### <a name="doc----set-annotations"></a>2.2 `ModelDoc.`set_annotations():

ModelDoc.set_annotations(self, anchor_prefix: str, number_prefix: str) -> None:

Set the ModelDoc Anchor and Number attributes.
Arguments:
* *anchor_prefix* (str):
  The string to prepend to the document element name before setting the Anchor attribute.
* *number_prefix* (str):
  The string to prepend to the document element name before setting the Number attribute.

This method must be implemented by sub-classes.


## <a name="doc--modelfunction"></a>3 Class ModelFunction:

Represents a function method.
Attributes:
*  Inherited Attributes: *Name*, *Lines*, *Anchor*, *Number* from ModelDoc.
*  *Function* (Callable): The actual function object.

### <a name="doc----set-annotations"></a>3.1 `ModelFunction.`set_annotations():

ModelFunction.set_annotations(self, anchor_prefix: str, number_prefix: str) -> None:

Set the markdown annotations.
(see [ModeDoc.set_annoations](#Doc-ModelDoc-set_annotations)

### <a name="doc----summary-lines"></a>3.2 `ModelFunction.`summary_lines():

ModelFunction.summary_lines(self, class_name: str, indent: str) -> typing.Tuple[str, ...]:

Return ModelModule table of contents summary lines.
Arguments:
* *class_name*: The class name the function is a member of.
* *indent* (int) The prefix spaces to make the markdown work.

### <a name="doc----documentation-lines"></a>3.3 `ModelFunction.`documentation_lines():

ModelFunction.documentation_lines(self, class_name: str, prefix: str) -> typing.Tuple[str, ...]:

Return the ModelModule documentaion lines.
Arguments:
* *prefix* (str): The prefix to use to make the markdown work.


## <a name="doc--modelmodule"></a>4 Class ModelModule:

ModelMethod: Represents a class method.

### <a name="doc----set-annotations"></a>4.1 `ModelModule.`set_annotations():

ModelModule.set_annotations(self, anchor_prefix: str, number_prefix: str) -> None:

Set the Markdown anchor.

### <a name="doc----summary-lines"></a>4.2 `ModelModule.`summary_lines():

ModelModule.summary_lines(self) -> typing.Tuple[str, ...]:

Return ModelModule summary lines.

### <a name="doc----documentation-lines"></a>4.3 `ModelModule.`documentation_lines():

ModelModule.documentation_lines(self, prefix: str) -> typing.Tuple[str, ...]:

Return the ModelModule documentaion lines.

### <a name="doc----generate"></a>4.4 `ModelModule.`generate():

ModelModule.generate(self, document_directory: pathlib.Path, markdown_program: str) -> None:

Generate the markdown and HTML files.



