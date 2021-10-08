# `py2md`: Python document strings to Markdown.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class BlockComment](#blockcomment)
* 3 [Class LineData](#linedata)
  * 3.1 [LineData.line\_parse](#linedata-line-parse)
* 4 [Class Markdown](#markdown)
  * 4.1 [Markdown.\_\_init\_\_](#markdown---init--)
  * 4.2 [Markdown.generate](#markdown-generate)
  * 4.3 [Markdown.read](#markdown-read)
  * 4.4 [Markdown.sharps\_extract](#markdown-sharps-extract)
  * 4.5 [Markdown.triples\_extract](#markdown-triples-extract)
* 5 [Class Tag](#tag)
* 6 [Functions](#functions)
  * 6.1 [fix](#fix)
  * 6.2 [italicize](#italicize)
  * 6.3 [main](#main)

## 1 <a name="introduction"></a>Introduction


This project attempted to use the [Sphinx](https://www.sphinx-doc.org/) documenation system,
but it really requires all of the code to be pushed through the Python system.
Missing imports are a show stopper and configuring Sphinx to find them all is non-trivial.
The bottom line is that Sphinx is currently unworkable for this project.

`py2md` is much simpler and just reads the document strings from one
Python file at a time and writes the corresponding Markdown file.

Usage: `py2md [.py ...] [dir ...]`

The requirement is that each comment block that has a `# CLASS_NAME():`, `# FUNC_NAME():`,
`# CLASS_NAME.METHOD_NAME():` at the front shows up in documentation.  In addition,
the first comment in the file shows up as the introduction.

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
             


## 2 Class BlockComment <a name="blockcomment"></a>

class BlockComment:

Represents a sequence of lines constituting a single comment.

* Attributes:
  * *tag* (str): The sorting key to use.
  * *index* (int):
  * *indent* (int): The indentation of the first line.
  * *is\_triple* (bool): True if the first line started with a triple quote.
  * *preceding* (Tuple[LineData, ...]):
    The lines preceding the first line up until a blank line.
  * *body* (Tuple[LineData, ...] ): The lines that make up the actual comment.

## 3 Class LineData <a name="linedata"></a>

class LineData:

Provides data about one file coment line.

* Attributes:
  * *stripped* (str): The line stripped of any preceding spaces and triple quotes.
  * *index* (int): The line index of the line (0 for first line).
  * *indent* (int): The number of preceding spaces stripped off the front.
  * *sharp\_start* (bool): True if first non-space character is sharp character.
  * *triple\_start* (str):
     Set to first 3 non-space characters if they are triple quotes;
     otherwise set to "".
  * *triple\_end* (str): Set to last 3 non-space characters are triple quotes;
     otherwise set to "".

### 3.1 LineData.line\_parse <a name="linedata-line-parse"></a>

def *line\_parse*(cls, *line*:  *str*, *index*:  *int*) -> "LineData":

Parse a line into LineData.

* Arguments:
  * *line* (str): The line to parse.
  * *index* (int): The line index associated with *line*:
* Returns:
  * Returns the LineData.

## 4 Class Markdown <a name="markdown"></a>

class Markdown(object):

Class containing Python markdown information.

### 4.1 Markdown.\_\_init\_\_ <a name="markdown---init--"></a>

def \_\_init\_\_(self, *path*:  Path) -> None:

Initialize a Markdown.

* Arguments:
  * *path* (Path): The Path to the python file.

### 4.2 Markdown.generate <a name="markdown-generate"></a>

def *generate*(self) -> None:

Generate Markdown file containing Python documentation.

### 4.3 Markdown.read <a name="markdown-read"></a>

def *read*(self, *path*:  Path) -> Tuple[LineData, ...]:

Read in Python file and convert to LineData's.

* Arguments:
  * *path* (Path): The Python file to read.
* Returns (Tuple[LineData, ...]) a tuple of LineData's for each line in the file.

### 4.4 Markdown.sharps\_extract <a name="markdown-sharps-extract"></a>

def *sharps\_extract*( *self*, *remaining\_line\_datas*:  Tuple[LineData, ...] ) -> Tuple[BlockComment, ...]:  # *pragma*:  *no* *unit* *cover*

Return the CommentBlock's that start with `# ... `.

* Arguments:
  * *remaining\_line\_datas* (Tuple[LineData]):
    The LineData's to scan scan for sharp (`#`) delineated comment blocks.
* Returns:
  * (Tuple[BlockComment, ...]) containing the sharp delineated block comments.

### 4.5 Markdown.triples\_extract <a name="markdown-triples-extract"></a>

def *triples\_extract*( *self*, *line\_datas*:  Tuple[LineData, ...] ) -> Tuple[Tuple[LineData, ...], Tuple[BlockComment, ...]]:

Extract BlockComment's containing Triples.

* Arguments:
  * *line\_datas* (Tuple[LineData, ...]): A tuple of LineData's from the file.
* Returns:
  * Tuple[LineData, ...] containing remaining LineData's that were not used.
  * Tuple[BlockComent, ...] containing extracted BlockComment's.

## 5 Class Tag <a name="tag"></a>

class Tag:

Provides sort able tag for block comments.

* Attributes:
  * *group* (str): The class name (or "~") for no class name.
  * *name* (str): The function/method name.  Use empty for class name.
  * *anchor* (str): The HTML anchor to use anchor Tag.

## 6 Functions <a name="functions"></a>

### 6.1 fix <a name="fix"></a>

def *fix*(text:  *str*) -> *str*:

Fix underscores for markdown.

* Arguments:
  * *text* (str): The text to fix.
* Returns:
  * (str) the string with each underscore preceded by backslash character.

### 6.2 italicize <a name="italicize"></a>

def *italicize*(match\_obj) -> *str*:

Italicize words.

* Arguments:
  * *match\_obj* (?): The regular expression match object.
* Returns:
  * (str) the match object where each word has an asterisk in front and back.

### 6.3 main <a name="main"></a>

def *main*() -> None:

Run the main program.
