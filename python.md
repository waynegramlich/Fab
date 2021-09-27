# FreeCAD Python

## Running a FreeCAD Python Script File from the Command Line

https://wiki.freecadweb.org/Start_up_and_Configuration

A really good place to start the journey of FreeCAD Python scripting is at the
[Power Users Hub](https://wiki.freecadweb.org/Power_users_hub).  The next web page to visit is
[FreeCAD Scripting Basics](https://wiki.freecadweb.org/FreeCAD_Scripting_Basics).
Pay careful attention about the difference between the application (i.e. App) which deals
with the geometry and the Graphical User Interface (i.e. Gui) which deals with visualization
issued.  This distinction is really important.

Early on, the [Embedding FreeCAD](https://wiki.freecadweb.org/Embedding_FreeCAD)
suggested that FreeCAD could relatively easily imported into stand-alone Python program.
While a little effort is required to get all of the FreeCAD Python libraries, those files can
be easily extracted from a FreeCAD [AppImage](https://wiki.freecadweb.org/AppImage).
Unfortunately, while FreeCAD Embedded Python can easily manipulate the geometry,
it does not have access to the FreeCAD Gui.  Thus, the Embedded FreeCAD strategy is really
only workable for geometry only manipulation.  This is really unfortunate, since
embedded FreeCAD approach easily supports debuggers, unit tests, code coverage, etc.
It is probably possible to do all of this without the embedded FreeCAD,
but it is also probably more involved.

The alternative strategy is to use FreeCAD macros which which Python modules (e.g. `.py` files)
that are directly run while the FreeCAD Window is visible the computer screen.  Using this strategy,
it is possible to access both the App and Gui objects inside of a FreeCAD document.
The details are to put you code into a Python module (e.g. `my_code.py`) and create symbolic
link to the file with a suffix of `.FCMacro` (e.g. `ln -s my_code.py my_code.FCmacro.)
Your favorite editor (e.g. `emacs`, `vim`, `vscode`, etc.) can be used to edit a Python
program and get whatever visualization, browsing, it support.

In the code, you need to create an *app_document* (geometry only) and extract
its associated *gui_document*:

     import FreeCAD as App
     import FreeCADGui as Gui

     app_document = App.newDocument("MyCode")
     gui_document = Gui.ActiveDocument
     
When done:

     app_document.saveAs("MyCode.fcstd")  # Optional
     App.closeDocument("MyCode")
     Gui.getMainWindow().close()

To run the Python script:

     freecad my_code.FCmacro

The FreeCad GUI will pop up on the screen, run the program, and exit.
The generated `MyCode.fcstd` file can be viewed using:

     freecad my_code.fcstd

That summarizes everything.

##

Next, visit the [Power Users Hub](https://wiki.freecadweb.org/Power_users_hub).  There are
plenty of links useful Python scripting information there.  Two useful links from that page
that cover some of most of the information immediately above are at the two are listed
immediately below:

* [Embedding FreeCAD](https://wiki.freecadweb.org/Embedding_FreeCAD):
  This explains some (but not all) of stuff above.

* [AppImage](https://wiki.freecadweb.org/AppImage):
  This explains how to download and use the FreeCAD AppImage.  Down in the
  [AppImage Developer Section](https://wiki.freecadweb.org/AppImage#Developer_Section)
  it explains how to unpack an AppImage (as mentioned above.)

After that, here are some additional extra links:

* [FreeCAD Scripting Basics](https://wiki.freecadweb.org/FreeCAD_Scripting_Basics):
  Explains a lot of issues about Python scripting.  In particular it introduces the App
  (accessed via the FreeCAD module) and Gui (accessed via the FreeCADGui module objects.
  The former contains physical dimensions and the latter contains everything else related
  to 

* [Document Structure](https://wiki.freecadweb.org/Document_structure):
  Explains the document structure.

* [Topolgical Data Scripting](https://wiki.freecadweb.org/Topological_data_scripting):
  Examples of using Python to create Part's.

* [Constructing Parts Using Python](https://wiki.freecadweb.org/Part_scripting):

* [Sketcher Python Scripting](https://wiki.freecadweb.org/Sketcher_scripting):

https://wiki.freecadweb.org/Sketcher_ConstrainCoincident#Scripting

https://wiki.freecadweb.org/Sketcher_scripting

https://wiki.freecadweb.org/Category:Command_Reference

* [Fasteners](https://wiki.freecadweb.org/Fasteners_BOM):
  There is an external workbench called Fasteners.


* Two part video on python scripting:
  * [FreeCAD Python 1 of 2: create & access collections ...](https://www.youtube.com/watch?v=2PO_fvE2NQM)
  * [FreeCAD Python 2 of 2: create & access collections ...](https://www.youtube.com/watch?v=iADzJkIU_tU)

[FreeCAD forum about Python](https://forum.freecadweb.org/viewtopic.php?f=22&t=48870)

[Code snippets](https://wiki.freecadweb.org/index.php?title=Code_snippets)

[Methods for FreeCAD Class](https://wiki.freecadweb.org/FreeCAD_API)







* How to run a python program from the command line:

     ./freecad19 -c foo.py   # Runs foo.py under FreeCad python interpreter.

* Howe to catch exceptions and print a traceback:

     import traceback
     def main():
         try:
             import FreeCAD
             import Part
             foo()
	 except Exception as exception:
             print("\n".join(traceback.format_exc().splitlines() + []))

     def foo():
	 bar()  # Undefined

# Create a document.
import FreeCAD
FreeCAD.newDocument()

# Add a line to a document.
import Part
doc=App.activeDocument()
# add a line element to the document and set its points
l=Part.LineSegment()
l.StartPoint=(0.0,0.0,0.0)
l.EndPoint=(1.0,1.0,1.0)
doc.addObject("Part::Feature","Line").Shape=l.toShape()
doc.recompute()
doc.saveAs("/tmp/Unnamed.fcstd")

# https://freecad.github.io/SourceDoc/dd/dc2/namespaceApp.html
# https://freecad.github.io/SourceDoc/d7/d75/classApp_1_1GeoFeature.html
# https://freecad.github.io/SourceDoc/modules.html


## Python Doc Strings:

* [Docstrings](https://stackoverflow.com/questions/36237477/python-docstrings-to-github-readme-md)
* [Sphninx Installation](https://www.sphinx-doc.org/en/master/usage/installation.html)
* Commands:
  * Install sphinx-dox: `sudo apt install sphinx-doc`  
  * Install sphinx-markdown-builder: `pip install sphinx sphinx-markdown-builder`
  * Install sphinx-autodoc-typehints: `pip install sphinx-autodoc-typehints`

  * Create `sphinx_docs/` using:

         sphinx-apidoc -o sphinx-docs . sphinx-apidoc --full -A 'SomeName'

  * Append the following to the `sphinx_docs/conf.py` file:

         import os
         import sys
         sys.path.insert(0, os.path.abspath("../"))

         def skip(app, what, name, obj,would_skip, options):
             if name in ("__init__",):
                 return False
             return would_skip

         def setup(app):
             app.connect("autodoc-skip-member", skip)

         extensions.append("sphinx_autodoc_typehints")

   * Showtime: `(cd sphinx_docs ; make markdown)`
   * Copy files: `mv _build/markdown/* ../; rm -r Sphinx-docs;


pip install coverage
python3 -m coverage erase
python3 -m coverage run -a DIR_FILE?
python3 -m coverage report   # 
python3 -m coverage annotate --include=FILE_DIR1,...,FILE_DIRn
