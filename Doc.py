#!/usr/bin/env python3
"""Doc: Convert Python doc strings to Markdown files.

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

"""

# <--------------------------------------- 100 characters ---------------------------------------> #


from dataclasses import dataclass, field
import inspect
import importlib
from pathlib import Path
import sys
from typing import Any, Callable, cast, IO, List, Set, Tuple, Optional
import subprocess

# ModelDoc:
@dataclass
class ModelDoc(object):
    """ModelDoc: Base class ModelFunction, ModelClass, and ModelModule classes.

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

    """

    Name: str = field(init=False, default="")
    Lines: Tuple[str, ...] = field(init=False, repr=False, default=())
    Anchor: str = field(init=False, repr=False, default="")
    Number: str = field(init=False, repr=False, default="??")

    # ModelDoc.set_lines():
    def set_lines(self, doc_string: Optional[str]) -> None:
        """Set the Lines field of a ModelDoc.

        Arguments:
        * *doc_string* (str): A raw doc string.

        This method takes a raw doc string where the first line has no embedded indentation
        space and subsequent non-empty lines have common indentation padding and converts
        them into sequence of lines that have the common inendation removed.

        """
        self.Lines = ("NO DOC STRING!",)
        if isinstance(doc_string, str):
            line: str
            lines: List[str] = [line.rstrip() for line in doc_string.split("\n")]

            # Compute the *common_indent* in spaces ignoring empty lines:
            big: int = 123456789
            common_indent: int = big
            for line in lines[1:]:   # Skip the first line which is special.
                indent: int = len(line) - len(line.lstrip())
                if line:  # Skip empty lines:
                    common_indent = min(common_indent, indent)
            if common_indent == big:
                common_indent = 0

            # Convert "NAME: Summary line." => "Summary_line.":
            first_line: str = lines[0]
            pattern: str = f"{self.Name}: "
            if first_line.startswith(pattern):
                lines[0] = first_line[len(pattern):]

            # Strip the common indentation off of each *line*:
            index: int
            for index, line in enumerate(lines):
                if index > 0 and len(line) >= common_indent:
                    lines[index] = line[common_indent:]

            # Strip off blank lines from the end:
            while lines and lines[-1] == "":
                lines.pop()

            # Strip off blank lines between summary line an body:
            while len(lines) >= 2 and lines[1] == "":
                del(lines[1])

            self.Lines = tuple(lines)

    # ModelDoc.set_annotations():
    def set_annotations(self, anchor_prefix: str, number_prefix: str) -> None:
        """Set the ModelDoc Anchor and Number attributes.

        Arguments:
        * *anchor_prefix* (str):
          The string to prepend to the document element name before setting the Anchor attribute.
        * *number_prefix* (str):
          The string to prepend to the document element name before setting the Number attribute.

        This method must be implemented by sub-classes.

        """
        raise NotImplementedError(f"{self}.set_annotations() is not implemented.")


# ModelFunction:
@dataclass
class ModelFunction(ModelDoc):
    """ModelFunction: Represents a function method.

    Attributes:
    *  Inherited Attributes: *Name*, *Lines*, *Anchor*, *Number* from ModelDoc.
    *  *Function* (Callable): The actual function object.

    """

    Function: Callable

    # ModelFunction.__post_init__():
    def __post_init__(self) -> None:
        """Post process a ModelFunction."""
        function: Callable = self.Function
        if hasattr(function, "__name__"):
            self.Name = getattr(function, "__name__")
        if hasattr(function, "__doc__"):
            self.set_lines(getattr(function, "__doc__"))

    # ModelFunction.set_annotations():
    def set_annotations(self, anchor_prefix: str, number_prefix: str) -> None:
        """Set the markdown annotations.

        (see [ModeDoc.set_annoations](#Doc-ModelDoc-set_annotations)

        """
        self.Anchor = anchor_prefix + self.Name.lower().replace("_", "-")
        self.Number = number_prefix

    # ModelFunction.summary_lines():
    def summary_lines(self, class_name: str, indent: str) -> Tuple[str, ...]:
        """Return ModelModule table of contents summary lines.

        Arguments:
        * *class_name*: The class name the function is a member of.
        * *indent* (int) The prefix spaces to make the markdown work.

        """
        return (f"{indent}* {self.Number} [{self.Name}()]"
                f"(#{self.Anchor}): {self.Lines[0]}",)

    # ModelFunction.documentation_lines():
    def documentation_lines(self, class_name: str, prefix: str) -> Tuple[str, ...]:
        """Return the ModelModule documentaion lines.

        Arguments:
        * *prefix* (str): The prefix to use to make the markdown work.

        """
        lines: Tuple[str, ...] = self.Lines
        signature: inspect.Signature = inspect.Signature.from_callable(self.Function)
        doc_lines: Tuple[str, ...] = (
            (f"{prefix} <a name=\"{self.Anchor}\"></a>{self.Number} "
             f"`{class_name}.`{self.Name}():"),
            "",
            f"{class_name}.{self.Name}{signature}:",
            ""
        ) + lines + ("",)
        return doc_lines


# ModelClass:
@dataclass
class ModelClass(ModelDoc):
    """ModelClass: Represents a class method.

    Attributes:
    *  Inherited Attributes: *Name*, *Lines*, *Anchor*, *Number* from ModelDoc.
    * *Class* (Any): The underlying Python class object that is imported.
    * *Functions* (Tuple[ModelFunction, ...]): The various functions associated with the Class.

    """

    Class: Any = field(repr=False)
    Functions: Tuple[ModelFunction, ...] = field(init=False, default=())

    # ModelClass.__post_init__():
    def __post_init__(self) -> None:
        """Post process ModelClass."""
        # Set Name and Lines attributes:
        if hasattr(self.Class, "__name__"):
            self.Name = cast(str, getattr(self.Class, "__name__"))
        if hasattr(self.Class, "__doc__"):
            self.set_lines(cast(str, getattr(self.Class, "__doc__")))

        # Set the Funcions attribute:
        model_functions: List[ModelFunction] = []
        attribute_name: str
        attribute: Any
        for attribute_name, attribute in self.Class.__dict__.items():
            if not attribute_name.startswith("_") and callable(attribute):
                model_functions.append(ModelFunction(attribute))
        self.Functions = tuple(model_functions)

    # ModelClass.set_annotations():
    def set_annotations(self, anchor_prefix: str, number_prefix: str) -> None:
        """Set the Markdown anchor."""
        anchor: str = anchor_prefix + self.Name.lower().replace("_", "-")
        self.Anchor = anchor
        self.Number = number_prefix

        next_anchor_prefix: str = anchor_prefix + "--"
        model_function: ModelFunction
        for index, model_function in enumerate(self.Functions):
            model_function.set_annotations(next_anchor_prefix, f"{number_prefix}.{index + 1}")

    # ModelClass.summary_lines():
    def summary_lines(self, indent: str) -> Tuple[str, ...]:
        """Return ModelModule summary lines."""
        lines: List[str] = [
            f"{indent}* {self.Number} Class: [{self.Name}](#{self.Anchor}):"]
        next_indent: str = indent + "  "
        model_function: ModelFunction
        for model_function in self.Functions:
            lines.extend(model_function.summary_lines(self.Name, next_indent))
        return tuple(lines)

    # ModelClass.documentation_lines():
    def documentation_lines(self, prefix: str) -> Tuple[str, ...]:
        """Return the ModelModule documentaion lines."""
        lines: Tuple[str, ...] = self.Lines
        doc_lines: List[str] = [
            f"{prefix} <a name=\"{self.Anchor}\"></a>{self.Number} Class {self.Name}:",
            "",
        ]
        doc_lines.extend(lines)
        doc_lines.append("")
        next_prefix: str = prefix + "#"
        function: ModelFunction
        for function in self.Functions:
            doc_lines.extend(function.documentation_lines(self.Name, next_prefix))
        doc_lines.append("")
        return tuple(doc_lines)


# ModelModule:
@dataclass
class ModelModule(ModelDoc):
    """ModelMethod: Represents a class method."""

    Module: Any = field(repr=False)
    Classes: Tuple[ModelClass, ...] = field(init=False, default=())

    # ModelModule.__post_init__():
    def __post_init__(self) -> None:
        """Recursively extract information from an object."""
        module: Any = self.Module

        # Get initial *module_name*:
        module_name: str = ""
        if hasattr(module, "__name__"):
            module_name = getattr(module, "__name__")
        is_package: bool = module_name == "__init__"

        tracing: str = "" if is_package else ""  # Change first string to enable package tracing.
        if tracing:
            print(f"{tracing}Processing {module_name} {is_package=}")
        if hasattr(module, "__doc__"):
            doc_string = getattr(module, "__doc__")
            if tracing:
                print(f"{tracing}{doc_string=}")
            self.set_lines(doc_string)
            if is_package:
                first_line: str = self.Lines[0]
                colon_index: int = first_line.find(":")
                if colon_index >= 0:
                    module_name = first_line[:colon_index]
                    first_line = first_line[colon_index + 2:]  # Skip over "...: "
                    self.Lines = (first_line,) + self.Lines[1:]

        # The Python import statment can import class to the module namespace.
        # We are only interested in classes that are defined in *module*:
        model_classes: List[ModelClass] = []
        class_type: type = type(ModelDoc)  # Any class name to get the associated class type.
        assert isinstance(class_type, type)
        attribute_name: str
        # print(f"{module=} {type(module)=}")
        for attribute_name in dir(module):
            if not attribute_name.startswith("_"):
                attribute: Any = getattr(module, attribute_name)
                if hasattr(attribute, "__module__"):
                    defining_module: Any = getattr(attribute, "__module__")
                    # print(f"{attribute_name=} {attribute=} {defining_module}")
                    if isinstance(attribute, class_type) and str(defining_module) == module_name:
                        model_classes.append(ModelClass(attribute))
                        # print(f">>>>>>>>>>Defined class: {attribute_name}")
        self.Name = module_name
        self.Classes = tuple(model_classes)

    # ModelModule.set_annotations():
    def set_annotations(self, anchor_prefix: str, number_prefix: str) -> None:
        """Set the Markdown anchor."""
        anchor: str = anchor_prefix + self.Name.lower().replace("_", "-")
        self.Anchor = anchor

        next_anchor_prefix: str = anchor + "--"
        model_class: ModelClass
        index: int
        for index, model_class in enumerate(self.Classes):
            model_class.set_annotations(next_anchor_prefix, f"{index + 1}")

    # ModelModule.summary_lines():
    def summary_lines(self) -> Tuple[str, ...]:
        """Return ModelModule summary lines."""
        # Create the Title
        lines: List[str] = []
        if self.Name == "__init__":
            lines.extend(self.Lines)  # Package is the top level doc string only.
        else:
            lines.append(f"# {self.Name}: {self.Lines[0]}")
            lines.extend(self.Lines[1:])
            lines.append("")
            if self.Classes:
                lines.append("## Table of Contents (alphabetical order):")
                lines.append("")

            # Fill in the rest of the table of contents:
            model_class: ModelClass
            next_indent: str = ""
            for model_class in self.Classes:
                lines.extend(model_class.summary_lines(next_indent))
            lines.append("")
        return tuple(lines)

    # ModelModule.documentation_lines():
    def documentation_lines(self, prefix: str) -> Tuple[str, ...]:
        """Return the ModelModule documentaion lines."""
        # lines: Tuple[str, ...]  = self.Lines
        # doc_lines: List[str] = [f"{prefix} <a name=\"{self.Anchor}\"></a>{lines[0]}", ""]
        # doc_lines.extend(lines[1:])

        doc_lines: List[str] = []
        next_prefix: str = prefix + "#"
        model_class: ModelClass
        for model_class in self.Classes:
            doc_lines.extend(model_class.documentation_lines(next_prefix))
        doc_lines.append("")
        return tuple(doc_lines)

    # ModelModule.generate():
    def generate(self, document_directory: Path, markdown_program: str) -> None:
        """Generate the markdown and HTML files."""
        # Compute *markdown_lines*:
        module_summary_lines: Tuple[str, ...] = self.summary_lines()
        module_documentation_lines: Tuple[str, ...] = self.documentation_lines("#")
        markdown_lines: Tuple[str, ...] = (
            module_summary_lines + module_documentation_lines + ("",))

        # Write *markdown_lines* out to *markdown_path* file:
        markdown_path: Path = document_directory / f"{self.Name}.md"
        try:
            markdown_file: IO[str]
            with open(markdown_path, "w") as markdown_file:
                markdown_file.write("\n".join(markdown_lines))
        except IOError:
            raise RuntimeError(f"Unable to write to {markdown_path}")

        # Run *markdown_program*:
        if markdown_program:
            html_path: Path = markdown_path.with_suffix(".html")
            arguments: Tuple[str, ...] = (
                markdown_program, str(markdown_path))
            # print(f"{arguments=}")
            html_file: IO[bytes]
            with open(html_path, "wb") as html_file:
                result: subprocess.CompletedProcess
                result = subprocess.run(arguments, capture_output=True)
                output: bytes = result.stdout
                assert isinstance(output, bytes)
                html_file.write(output)


def process_arguments(arguments: Tuple[str, ...]) -> Tuple[Tuple[str, ...], Path, str]:
    """Return module names list and output directory parsed from arguments."""
    # Process flags and collect *non_flag_arguments:
    documents_directory: Path = Path("docs")
    if not documents_directory.is_dir():
        documents_directory = Path("/tmp")
    markdown_program: str = "cmark"

    directory_flag_prefix = "--directory="
    markdown_flag_prefix = "--markdown="

    non_flag_arguments: List[str] = []
    argument: str
    for argument in arguments:
        if argument.startswith(directory_flag_prefix):
            document_directory = Path(argument[len(directory_flag_prefix):])
            if not document_directory.is_dir():
                raise RuntimeError(f"{document_directory} is not a directory")
        elif argument.startswith(markdown_flag_prefix):
            markdown_program = argument[len(markdown_flag_prefix):]
        elif argument == "--unit-test":
            pass
        else:
            non_flag_arguments.append(argument)
    if not non_flag_arguments:
        non_flag_arguments.append(".")  # Scan current directory.

    module_names: Set[str] = set()
    for argument in non_flag_arguments:
        if argument.endswith(".py"):
            module_names.add(argument[:-3])
        elif Path(argument).is_dir():
            paths = tuple(Path(argument).glob("*.py"))
            path: Path
            for path in paths:
                module_names.add(Path(path).stem)
        else:
            module_names.add(argument)

    # module_names.add("__init__")
    # __init__.py get imported as a side-effect of reading the other packages.
    # Thus, if "__init__" is *model_names*, it must be the first module opened.
    first_module: Tuple[str, ...] = ()
    if "__init__" in module_names:
        module_names.remove("__init__")
        first_module = ("__init__",)
    sorted_module_names: Tuple[str, ...] = first_module + tuple(sorted(module_names))
    return tuple(sorted_module_names), documents_directory, markdown_program


def main() -> int:
    """Generate markdown files from Python document strings."""
    # Process the command line arguments:
    module_names: Tuple[str, ...] = ("Not Updated",)
    document_directory: Path
    markdown_program: str

    try:
        module_names, document_directory, markdown_program = (
            process_arguments(tuple(sys.argv[1:])))
    except RuntimeError as runtime_error:
        print(runtime_error)
        return 1

    # For each *mode_name*, import it, generate documentation, and write it out:
    modules: List[ModelModule] = []
    module_name: str
    for module_name in module_names:
        # Import each Module Name and process it:
        model_module: ModelModule
        try:
            module: Any = importlib.import_module(module_name)
            model_module = ModelModule(module)
        except ModuleNotFoundError as module_not_found_error:
            print(f"Unable to open module '{module_name}': {str(module_not_found_error)}")
            return 1
        except TypeError as type_error:
            print(f"Error with import of module '{module_name}: {str(type_error)}")
        model_module.set_annotations("", "")
        modules.append(model_module)

        # Generate Markdown and HTML files:
        try:
            model_module.generate(document_directory, markdown_program)
        except RuntimeError as runtime_error:
            print(runtime_error)
            return 1

    return 0


if __name__ == "__main__":
    main()
