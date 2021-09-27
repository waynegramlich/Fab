# `py2md`: Python document strings to Markdown.

An attempt was made to use [Sphinx](https://www.sphinx-doc.org/),
but it really requires all of the code to be pushed the Python system.
Missing imports are a show stopper and configuring Sphinx to find all the
missing imports is non-trivial.
`py2md` is much simpler and just reads the document strings from one
Python file at a time and writes the corresponding Markdown file.

Usage: `py2md [.py ...] [dir ...]`

The basic Python file format is shown immediately below (`##` is for informational comments):

     #!/usr/bin/env python3  ## Optional for executable files.
     Module line description.   ## One SENTENCE that ends in a period.  Blank line is next.

     More module description here.  Module constants are listed here.
     

     # CLASS_NAME(PARENT_CLASS):   ## Class definition is preceded by a 1-line comment.
     class CLASS_NAME(PARENT_CLASS):  ## Use `object` for base classes.
         Class line description.

         Additional class description goes here.
         

         # CLASS_NAME.METHOD_NAME():  ## One line comment with both CLASS_NAME and METHOD_NAME.
         def CLASS_NAME(self, ...) -> ...:   ## Use Python Type Hints.
             Method one line description.

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
             

Both `@property` and `@dataclass` decorators are encouraged and have special extra parsing to
extract property names and the like.
## 1.0 Class LineData

class LineData:

Provides data about one file line.

* Attributes:
  * *stripped* (str): The line stripped of any preceeding spaces and triple quotes.
  * *index* (int): The line index of the line (0 for first line).
  * *indent* (int): The number of preceding spaces stripped off the front.
  * *sharp\_start* (bool): True if first non-space character is sharp character.
  * *triple\_start* (str):
     Set to first 3 non-space characters if they are triple quotes;
     otherwise set to "".
  * *triple\_end* (str): Set to last 3 non-space characters are triple quotes;
     otherwise set to "".

### 1.1 LineData.line\_parse

def *line\_parse*(cls, *line*:  *str*, *index*:  *int*) -> "LineData":

Parse a line into LineData.

* Arguments:
  * *line* (str): The line to parse.
  * *index* (int): The line index associated with *line*:
* Returns:
  * Returns the LineData.

## 2.0 Class BlockComment

class BlockComment:

Represents a sequence of lines constituting a single comment.

* Attributes:
  * *index* (int):
  * *indent* (int): The indentation of the first line.
  * *is\_triple* (bool): True if the first line started with a triple quote.
  * *preceding* (Tuple[LineData, ...]):
    The lines preceeding the first line up until a blank line.
  * *body* (Tuple[LineData, ...] ): The lines that make up the actual comment.

## 3.0 Class Markdown

class Markdown(object):

Class containing Python markdown information.

### 3.1 Markdown.\_\_init\_\_

def \_\_init\_\_(self, *path*:  Path) -> None:

Initialize a Markdown.

* Arguments:
  * *path* (Path): The Path to the python file.

### 3.2 Markdown.read

def *read*(self, *path*:  Path) -> Tuple[LineData, ...]:

Read in Python file and convert to LineData's.

* Arguments:
  * *path* (Path): The Python file to read.
* Returns (Tuple[LineData, ...]) a tuple of LineData's for each line in the file.

### 3.3 Markdown.triples\_extract

def *triples\_extract*( *self*, *line\_datas*:  Tuple[LineData, ...] ) -> Tuple[Tuple[LineData, ...], Tuple[BlockComment, ...]]:

Extract BlockComment's containing Triples.

* Arguments:
  * *line\_datas* (Tuple[LineData, ...]): A tuple of LineData's from the file.
* Returns:
  * Tuple[LineData, ...] containing remaining LineData's that were not used.
  * Tuple[BlockComent, ...] containing extracted BlockComment's.

### 3.4 Markdown.sharps\_extract

def *sharps\_extract*( *self*, *remaining\_line\_datas*:  Tuple[LineData, ...] ) -> Tuple[BlockComment, ...]:  # *pragma*:  *no* *unit* *cover*

Return the CommentBlock's that start with `# ... `.

* Arguments:
  * *remaining\_line\_datas* (Tuple[LineData]):
    The LineData's to scan scan for sharp (`#`) delineated comment blocks.
* Returns:
  * (Tuple[BlockComment, ...]) containing the sharp delineated block comments.

### 3.5 Markdown.generate

def *generate*(self) -> None:

Generate Markdown file containing Python documentation.

### 3.6 fix

def *fix*(text:  *str*) -> *str*:

Fix underscores for markdown.

* Arguments:
  * *text* (str): The text to fix.
* Returns:
  * (str) the string with each underscore preceeded by backslash character.

### 3.7 italicize

def *italicize*(match\_obj) -> *str*:

Italicize words.

* Arguments:
  * *match\_obj* (?): The regular expression match object.
* Returns:
  * (str) the match object where each word has an asterisk in front and back.

### 3.8 main

def *main*() -> None:

Run the main program.

