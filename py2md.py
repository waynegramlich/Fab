#!/usr/bin/python3
'''
`py2md`: Python document strings to Markdown.

An attempt was made to use [Sphinx](https://www.sphinx-doc.org/),
but it really requires all of the code to be pushed the Python system.
Missing imports are a show stopper and configuring Sphinx to find all the
missing imports is non-trivial.
`py2md` is much simpler and just reads the document strings from one
Python file at a time and writes the corresponding Markdown file.

Usage: `py2md [.py ...] [dir ...]`

The basic Python file format is shown immediately below (`##` is for informational comments):

     #!/usr/bin/env python3  ## Optional for executable files.
     """Module line description.   ## One SENTENCE that ends in a period.  Blank line is next.

     More module description here.  Module constants are listed here.
     """

     # CLASS_NAME(PARENT_CLASS):   ## Class definition is preceded by a 1-line comment.
     class CLASS_NAME(PARENT_CLASS):  ## Use `object` for base classes.
         """Class line description.

         Additional class description goes here.
         """

         # CLASS_NAME.METHOD_NAME():  ## One line comment with both CLASS_NAME and METHOD_NAME.
         def CLASS_NAME(self, ...) -> ...:   ## Use Python Type Hints.
             """Method one line description.

             Optional more verbose method description goes here.

             * Arguments:  ## Use `* Arguments: None` if there are no arguments.
               * *arg1* (TYPE1): *arg1 description...
               ...
               * *argN* (TYPEn): *argN description...
             * Returns:   ## Use `* Returns nothing.` if there are no returns.
               * (TYPE1) first return type description.
               ...
               * (TYPEn) Last return type description.
             * Raises:   ## (Eliminate if no exceptions are raised.)
               * exception1: ...
               ...
               * exceptionN: ...
             """

Both `@property` and `@dataclass` decorators are encouraged and have special extra parsing to
extract property names and the like.
'''

# <--------------------------------------- 100 characters ---------------------------------------> #

from dataclasses import dataclass

from pathlib import Path
from typing import IO, List, Tuple
import re
import sys


@dataclass(frozen=True)
# LineData:
class LineData:
    """Provides data about one file line.

    * Attributes:
      * *stripped* (str): The line stripped of any preceeding spaces and triple quotes.
      * *index* (int): The line index of the line (0 for first line).
      * *indent* (int): The number of preceding spaces stripped off the front.
      * *sharp_start* (bool): True if first non-space character is sharp character.
      * *triple_start* (str):
         Set to first 3 non-space characters if they are triple quotes;
         otherwise set to "".
      * *triple_end* (str): Set to last 3 non-space characters are triple quotes;
         otherwise set to "".
    """

    stripped: str
    index: int
    indent: int
    sharp_start: bool
    triple_start: str
    triple_end: str

    @classmethod
    # LineData.line_parse():
    def line_parse(cls, line: str, index: int) -> "LineData":
        """Parse a line into LineData.

        * Arguments:
          * *line* (str): The line to parse.
          * *index* (int): The line index associated with *line*:
        * Returns:
          * Returns the LineData.
        """
        # Remove indentation and trailing white space:
        stripped: str = line.lstrip()
        indent: int = len(line) - len(stripped)
        stripped = stripped.rstrip()

        # Search for `# ...` and `""" ... """`.
        sharp_start: bool = stripped.startswith("#")
        triple_start: str = ""
        if stripped.startswith("'''") or stripped.startswith('"""'):
            triple_start = stripped[:3]
        triple_end: str = ""
        if stripped.endswith("'''") or stripped.endswith('"""'):
            triple_end = stripped[-3:]

        if stripped[:3] == triple_start:
            stripped = stripped[3:]
        if stripped[-3:] == triple_end:
            stripped = stripped[:-3]

        # print(f"{indent}\t{line}")
        return LineData(stripped, index, indent, sharp_start, triple_start, triple_end)


# BlockComment:
@dataclass(frozen=True, order=True)
class BlockComment:
    """Represents a sequence of lines constituting a single comment.

    * Attributes:
      * *index* (int):
      * *indent* (int): The indentation of the first line.
      * *is_triple* (bool): True if the first line started with a triple quote.
      * *preceding* (Tuple[LineData, ...]):
        The lines preceeding the first line up until a blank line.
      * *body* (Tuple[LineData, ...] ): The lines that make up the actual comment.
    """

    index: int
    indent: int
    is_triple: bool
    preceding: Tuple[LineData, ...]
    body: Tuple[LineData, ...]


# Markdown:
class Markdown(object):
    """Class containing Python markdown information."""

    # Markdown.__init__():
    def __init__(self, path: Path) -> None:
        """Initialize a Markdown.

        * Arguments:
          * *path* (Path): The Path to the python file.
        """
        line_datas: Tuple[LineData, ...] = self.read(path)
        triples: Tuple[BlockComment, ...]
        line_datas, triples = self.triples_extract(line_datas)
        # sharps: Tuple[BlockComment, ...] = self.sharps_extract(line_datas)

        self._path: Path = path
        self._sharps: Tuple[BlockComment, ...] = ()  # sharps
        self._triples: Tuple[BlockComment, ...] = triples

    # Markdown.read():
    def read(self, path: Path) -> Tuple[LineData, ...]:
        """Read in Python file and convert to LineData's.

        * Arguments:
          * *path* (Path): The Python file to read.
        * Returns (Tuple[LineData, ...]) a tuple of LineData's for each line in the file.
        """
        line_datas: List[LineData] = []
        in_file: IO[str]
        with open(path, "r") as in_file:
            lines: Tuple[str, ...] = tuple(in_file.read().split("\n"))
            index: int
            line: str
            for index, line in enumerate(lines):
                line_data: LineData = LineData.line_parse(line, index)
                line_datas.append(line_data)
        return tuple(line_datas)

    # Markdown.triples_extract():
    def triples_extract(
            self,
            line_datas: Tuple[LineData, ...]
    ) -> Tuple[Tuple[LineData, ...], Tuple[BlockComment, ...]]:
        """Extract BlockComment's containing Triples.

        * Arguments:
          * *line_datas* (Tuple[LineData, ...]): A tuple of LineData's from the file.
        * Returns:
          * Tuple[LineData, ...] containing remaining LineData's that were not used.
          * Tuple[BlockComent, ...] containing extracted BlockComment's.
        """
        # print(f"=>triples_extract(|{len(line_datas)=}|)")
        triples: List[BlockComment] = []
        remaining_line_datas: List[LineData] = []
        triple_line_datas: List[LineData] = []
        line_data: LineData
        index: int
        in_triple: str = ""
        for index, line_data in enumerate(line_datas):
            tracing: bool = False
            if tracing:
                print(f"line_datas[{index}]: s='{line_data.triple_start}' "
                      f"e='{line_data.triple_end}' i='{in_triple}' "
                      f"x={line_data.indent} |{len(triple_line_datas)}| "
                      f"{line_data.indent * ' '}{line_data.stripped}")

            # Manage *in_triple* flag and append *line_data* to only one buffer:
            triple_start: str = line_data.triple_start
            triple_end: str = line_data.triple_end
            stripped = line_data.stripped

            if triple_start and triple_end:
                if stripped == "":
                    # Single `"""` or `'''` on a line:
                    if in_triple:
                        if in_triple == triple_start:
                            in_triple = ""
                        else:
                            # It is either `"""` in a `''' ... '''` or vice versa.
                            triple_line_datas.append(line_data)
                    else:
                        in_triple = triple_start
                else:
                    # Single line with `""" ... """` or `''' ... '''`:
                    triple_line_datas.append(line_data)
            elif not in_triple and triple_start:
                in_triple = triple_start
                triple_line_datas.append(line_data)
            elif in_triple and triple_end and triple_end == in_triple:  # pragma: no unit cover
                triple_line_datas.append(line_data)
                in_triple = ""
            elif in_triple:
                triple_line_datas.append(line_data)
            else:
                remaining_line_datas.append(line_data)

            # Flush out *triple_line_datas*:
            if triple_line_datas and not in_triple:
                # Now reverse search for *preceding* lines until a blank line is found:
                first_line_data: LineData = triple_line_datas[0]
                preceding_line_datas: List[LineData] = []
                find_index = first_line_data.index - 1
                while find_index >= 0:
                    line_data = line_datas[find_index]
                    if line_data.indent == 0 and line_data.stripped == "":
                        break
                    preceding_line_datas.append(line_data)
                    find_index -= 1

                block_comment: BlockComment = BlockComment(
                    first_line_data.index,
                    first_line_data.indent,
                    True,
                    tuple(reversed(preceding_line_datas)),
                    tuple(triple_line_datas))
                triples.append(block_comment)
                # print(f"[{index}]:|{len(block_comment.body)=}| ")
                triple_line_datas = []
        # print(f"<=triples_extract()=>|{len(triples)}|")
        return tuple(remaining_line_datas), tuple(triples)

    # Markdown.sharps_extract():
    def sharps_extract(
            self,
            remaining_line_datas: Tuple[LineData, ...]
    ) -> Tuple[BlockComment, ...]:  # pragma: no unit cover
        """Return the CommentBlock's that start with `# ... `.

        * Arguments:
          * *remaining_line_datas* (Tuple[LineData]):
            The LineData's to scan scan for sharp (`#`) delineated comment blocks.
        * Returns:
          * (Tuple[BlockComment, ...]) containing the sharp delineated block comments.
        """
        sharp_indent: int = -1
        sharps: List[BlockComment] = []
        line_datas: List[LineData] = []
        line_data: LineData
        for line_data in remaining_line_datas:
            sharp_start: bool = line_data.sharp_start
            indent: int = line_data.indent
            if sharp_start and sharp_indent < 0:
                line_datas.append(line_data)
                sharp_indent = indent
            elif sharp_start and sharp_indent == line_data.indent:
                line_datas.append(line_data)
            elif sharp_indent > 0 and line_data.stripped == "":
                line_datas.append(line_data)
            elif line_datas:
                first_line_data: LineData = line_datas[0]
                block_comment = BlockComment(
                    first_line_data.index,
                    first_line_data.indent,
                    False,
                    (),  # No preceding LineData's.
                    tuple(line_datas))
                sharps.append(block_comment)
                line_datas = []
                sharp_indent = -1
        return tuple(sharps)

    # Markdown.generate():
    def generate(self) -> None:
        """Generate Markdown file containing Python documentation."""
        # print("=>Markdown.generate()")
        # Output the file header (i.e. # FILE_NAME):
        path: Path = self._path
        markdown_lines: List[str] = []

        # Print out the comments:
        padding: str
        triples: Tuple[BlockComment, ...] = self._triples
        # print(f"|{len(triples)=}|")

        block_comment: BlockComment
        line_data: LineData
        index: int

        # Find the first non-empty line in *module.body*:
        module: BlockComment = triples[0]
        for index, line_data in enumerate(module.body):
            if line_data.stripped != "":
                break

        # Output the Markdown header followed by the module document string:
        markdown_lines.append(f"# {line_data.stripped}")
        markdown_lines.extend([f"{line_data.indent * ' '}{line_data.stripped}"
                               for line_data in module.body[index + 1:]])

        class_counter: int = 0
        method_counter: int = 0
        class_or_module: BlockComment
        for index, class_or_module in enumerate(triples[1:]):
            # print(f"triples[{index}]: |{len(markdown_lines)=}|")
            indent: int = class_or_module.indent

            # Prescan *preceding_lines* looking for `class` or `def':
            is_class: bool = False
            is_def: bool = False
            stripped: str
            for line_data in class_or_module.preceding:
                stripped = line_data.stripped
                is_class |= stripped.startswith("class ")
                is_def |= stripped.startswith("def ")

            # Scrape the useful information from *preceding_lines*:
            pieces: List[str] = []
            for line_data in class_or_module.preceding:
                stripped = line_data.stripped
                if stripped.startswith("# ") and stripped.endswith(":"):
                    if is_class:
                        # `# CLASS_NAME(...):` expected:
                        # [2:-1] => Remove `# ` at front and `:`
                        class_counter += 1
                        method_counter = 0
                        markdown_lines.extend([
                            f"## {class_counter}.0 Class {fix(stripped[2:-1])}",
                            ""])
                    if is_def:
                        # `CLASS_NAME.METHOD_NAME():` expected:
                        # [2:-3] => Remove `# ` at front and `():` at end.
                        method_counter += 1
                        markdown_lines.extend([
                            f"### {class_counter}.{method_counter} {fix(stripped[2:-3])}",
                            ""])
                elif not stripped.startswith("@"):
                    pieces.append(f" {stripped} ")
            if pieces:
                # print(f"{pieces=}")
                joined: str = " ".join(pieces)
                # joined = joined.replace("def ", "")
                # joined = joined.replace("class ", "")
                joined = joined.replace("  ", " ")
                joined = joined.replace("  ", " ")
                joined = joined.replace("  ", " ")
                joined = joined.replace(" ,", ",")
                joined = joined.replace(" ,", ",")
                joined = joined.replace("  ->", "-> ")
                joined = joined.replace("  ->", "-> ")
                joined = joined.replace("->  ", "-> ")
                joined = joined.replace("->  ", "-> ")
                joined = joined.replace(":", ": ")
                joined = joined.strip()
                joined = " " + re.sub(r" [a-z][a-z0-9_]*", italicize, joined)
                joined = joined.replace("_", "\\_")
                if joined.startswith(" "):
                    joined = joined[1:]
                markdown_lines.append(joined)
                markdown_lines.append("")

            indent = class_or_module.indent
            for line_data in class_or_module.body:
                padding = max(0, line_data.indent - indent) * " "
                stripped = line_data.stripped
                markdown_lines.append(f"{padding}{fix(stripped)}")
            markdown_lines.append("")

        # Output *markdown_lines*:
        markdown_path: Path = Path(f"{path.stem}.md")
        # print(f"{markdown_path=}")
        markdown_file: IO[str]
        with open(markdown_path, "w") as markdown_file:
            markdown_file.write("\n".join(markdown_lines + [""]))
        # print("<=Markdown.generate()")


# fix():
def fix(text: str) -> str:
    """Fix underscores for markdown.

    * Arguments:
      * *text* (str): The text to fix.
    * Returns:
      * (str) the string with each underscore preceeded by backslash character.
    """
    return text.replace("_", "\\_")


# italicize():
def italicize(match_obj) -> str:
    """Italicize words.

    * Arguments:
      * *match_obj* (?): The regular expression match object.
    * Returns:
      * (str) the match object where each word has an asterisk in front and back.
    """
    text: str = match_obj.group()
    return f" *{text[1:]}*"


# main():
def main() -> None:
    """Run the main program."""
    arguments: Tuple[str, ...] = tuple(sys.argv[1:])  # Strip off program name
    if "--unit-test" in arguments:
        arguments = ("py2md.py", )
    if not arguments:
        print("Usage: py2md.py  PYFILE...")  # pragma: no unit cover
    else:
        # Expand directories in *arguments*:
        paths: List[Path] = []
        for argument in arguments:
            path: Path = Path(argument)
            if path.is_dir():
                paths.extend(path.glob("*.py"))  # pragma: no unit cover
            elif path.suffix == ".py":
                paths.append(path)
            else:  # pragma: no unit cover
                print(f"{path.name} does not have a suffix of `.py`")

        markdowns: Tuple[Markdown, ...] = tuple([Markdown(path) for path in paths])
        markdown: Markdown
        index: int
        for index, markdown in enumerate(markdowns):
            markdown.generate()


if __name__ == "__main__":
    main()
