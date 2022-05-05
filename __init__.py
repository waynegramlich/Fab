"""Fab: Python Modeling and Fabrication.

## Table of Contents:

* [Introduction](#introduction)
* [Overview](#overview)
* [Commonly Used Fab Classes](#commonly-used-fab-classes)
* [Workflow](#workflow)
* [Type Hints and Data Classes](#type-hints-and-data-classes)
* [Python Modules](#python-modules)
* [Bearing Block Example](#bearing-block-example)
* [Additional Documentation](#additional-documentation)
* [Installation](#installation)

## Introduction

The Fab package is a FreeCAD/CadQuery focused Python library that supports a DFM workflow where:

* FreeCAD/CadQuery are an open source CAD/CAM (Computer Aided Design/Manufacturing) applications,

* Python is rather popular programming language, and

* DFM stands for Design For Manufacture.

The Fab Python package aids the process of transforming an idea into a design and eventually
into finalized physical object.

In Fab, each individual part conceptually starts with some stock material followed by operations
performed on the stock material (e.g. contour outlines, drill holes, remove pockets, etc.)
All of the individual parts are assembled into a final assembly which can be viewed using FreeCAD.

Fab supports the concept of multiple different shops,
where the specific machines and associated tooling within each shop are specified.
The Fab design in conjunction with a the Fab shop specification generates the various files
(`.cnc`, `.stl`, `.dxf`, etc.) needed to manufacture the part for a specific shop.
Thus, one Fab design can be shared among multiple people with different shops and
still get basically the same physical objects.

## Overview <a name="overview"></a>

The abbreviations NIY (Not Implemented Yet) and WIP (Work In Progress) are used
to indicate current development status.

The way Fab works is as follows:

1. (WIP)
   You write one or more Python design modules (e.g. `.py` files) that defines of all of the parts
   you wish to buy/create and how they are assembled together.
   While simple projects can be in one Python module,
   more complex projects will span multiple Python modules (e.g. a Python package.)
   These python modules are written to use generic mills, lathes, laser cutters, 3D printers, etc.
   These designs are meant to parametric in that somebody can change dimensions, materials, etc.

2. (WIP)
   You may have access to multiple shops (e.g your home shop, a maker space, etc.)
   For each shop, somebody writes a Python module that describes the shop machines
   (e.g. 3D printers, laser cutters, mills, lathes, etc.)
   and any associated machine tooling (e.g. mill bits, lathe cutters, etc.)

3. (NIY)
   A Python module is written that does the following:

   1. Imports a collection of design files (step 1) and shops (step 2).

   2. Parametric values are specified (e.g. lengths, angle, materials, etc.)

   3. Specific shop machines are can be bound to specific parts.
      This will cause the correct output for each part to be generated
      (e.g. `.stl`, `.dxf`, `.cnc` files.)

   In order, to keep this Python module small,
   defaults are used to simplify the shop machine to part binding process.

Using this architecture, the result is shareable parametric designs that fabricated
using different shops and still get basically the same result.

## Commonly Used Fab Classes

Each Fab project is implemented as one or more Python files that import Fab package classes.
(As a side note, each user facing Fab class is always prefixed with `Fab`.)

The Fab strategy is to construct nested tree of FabNode's,
where a FabNode is a base class that sub-classed to provide additional structure.
The sub-classes are:

1. FabProject:
   This is the top level FabNode that encapsulates your entire project.

2. FabDocument:
   This corresponds to a FreeCAD document file (i.e. `.FCStd`).
   There is usually only one of these.

3. FabAssembly:
   This a group of smaller FabAssembly's and individual FabSolid's.

4. FabSolid:
   This corresponds to a single Solid object
   that can be represented as CAD industry standard file interchange format call a STEP file.

There is one FabProject at the tree root, typically almost always just one FabDocument,
followed nested as series of zero, one or more FabAssembly's,
with the leaf nodes all being FabSolid's.

An example decomposition is shown immediately below:

* FabProject (root)
  * FabDocument (usually only one of these)
    * FabAssembly 1
      * FabSolid 1
      * FabAssembly 2
        * FabSolid 2
        * FabSolid 3
      * FabSolid 4

In addition, there is a FabGeometry base class that currently provides the following sub-classes
which are assembled using Vector's (i.e. points) and dimensions (i.e. floats):

* FabPolygon:
  This is defined as a sequence of Vector's that that define a loop of line segments in 3D space.
  In practice, these line segments are always projected onto plane in 3D space before being used.
  Each polygon corner has an optional rounding radius for filleting purposes.

* FabCircle: This defines a sphere of a known diameter/radius centered around a Vector (point).
  Again, this sphere is projected onto a plane to generate a circle in 3D space.

These FabGeoemtry objects are used by the FabSolid methods to generate 3D solids.

A FabSolid is produced in a very CNC (Computer Numerical Control) fashion using a sequence of
one or more mounts (called FabMount's) and performing operations on each FabMount.
The FabMount class specifies a work plane in 3D space (this essentially a CadQuery Workplane.)
Once the FabMount is created, sequence of operations are performed using FabMount methods.

The current FabMount methods are:

* extrude: Extrudes from an initial FabGeometry this can generate block of material or a
  more complex shape line C-channel, I-beam, 8020, etc.

* Pocket: Removes a pocket of material.

* Drill: Drill holes for fasteners.

It should be noted that order of the operations may be rearranged to optimize CNC G-code generation.

## Workflow <a name="workflow"></a>

The basic work flow is done in phases:

1. Instantiate Tree:

   The FabNode tree is instantiated once at the beginning and does change afterwards.
   This is performed via classic Python initializer technology where the FabProject
   is instantiated first, which instantiates one (or more) FabDocument's, and so
   forth until the entire tree is present.

   As a side note, the Fab package heavily uses Python both type hints and dataclasses.
   See the section [dataclasses and type hints](data-classes-and-type-hints) for more information.

   The `run` method on the top level FabProject node is used to perform all of the work:
   In short, a Fab program looks like:

       def main() -> None:
           project: FabProject = MyProject()
           project.run()

2. Constraint Propagation.

   Constraint propagation is how parametric designs are supported.
   Constraint propagation is an iterative process where each FabNode is allowed to
   access values defined in other FabNode's to compute new values for itself.
   The `produce` recursively called for each FabNode is the tree
   until constraint values no longer change.
   It is possible to get into a loop where some constraints do not converge to a final stable value.
   When this occurs, Fab system lists the values that did not converge.

3. Solid Construction.

   Using the same `produce` method for defined for each FabNode,
   each produce method is called once is "construct" mode.
   In this mode, the FabMount objects (mentioned above in the previous section) are activated
   and the underlying CadQuery machinery is activated to produce one STEP file per FabSolid.
   A STEP file is a standard file format for the interchange of 3D parts and assemblies
   by Mechanical CAD program..
   In addition, a JSON file is generated that summarizes what was generated.
   
4. Visualization and CNC.

   The FreeCAD program is used for both visualization of the resulting parts and assembly
   and for generating CNC G-code files.
   For technical reasons, CadQuery can not be subsumed into FreeCad,
   so this code has to be run separately.
   In the visualization step, the generated JSON file is read and processed causing all of
   the previously generated STEP files to be read into FreeCad for viewing purposes.

   If CNC G-Code generation is required, the FreeCad CNC Path package is used to generate G-code.
   The generated G-code paths can also be visualized using FreeCAD.
   Indeed, the FreeCAD Path simulator can be used to simulate the machining process.

5. Fabrication.

   The generated `.cnc`, `.dxf`, `.stl` files, can be fed into the appropriate shop machines
   to actually fabricate each part.

## Python Modules <a name="python-modules"></a>

The (current) main Python modules are:

* [FabProjects](docs/FabProjects.md):
  The top level FabNode sub-classes of FabProject, FabDocument, and FabAssembly.

* [FabSolids](docs/FabSolids.md):
  The Solid creation class of FabSolid and FabMount.

* [FabNodes](docs/FabNodes.md):
  The base FabNode class and its associated bounding box FabBox sub-class.

* [FabGeometries](docs/FabGeometries.md):
  The FabPolygon and FabCircle sub-classes of FabGeometry.

* [FabUtilities](doc/FabUtilities.md):
  The FabColor and FabMaterial and utility classes.

Additional Python modules are:

* [FabShops](docs/FabShops.md):
  Classes for defining the available machines within a Shop.

* [FabTools](docs/FabTools.md):
  Classes for defining the available toolingwithin a Shop.

* [FabJoins](docs/FabJoins.md):
  Classes for defining fastener stacks of screws, bolts, washers, nuts, etc.

* [Doc](docs/Doc.md):
  A program for reading Python files and generating HTML documentation.

* [FabBOM](docs/FabBOM.md):
  The beginnings of a Bill of Materials manager.

## Type Hints and Data Classes <a name="type-hints-and-data-classes"></a>

The Fab project is implemented using both Python type hints and Python data classes.
This section briefly discusses Python type hints and
then goes into significantly more detail on using Python data classes and some of their "quirks".
This discussion is in preparation for a simple Fab example in the following section.

In short, Python type hints are based on importing the Python `typing` module and
decorating variables, class attributes and return values with static type information.
In general, type hints improve the legibility of Python functions and class methods.
In addition, there are various type checking and documentation tools that use these type hints.
In particular, the `mypy` program reads the type hints and attempts to flag static typing errors.
There are plenty of Python type hint tutorials available in the web
and you should read a few of them to get the idea how Python type hints work.
You are strongly encouraged to learn use `mypy` on your own code to find and fix static type errors.

Next, all of Fab classes are implemented as the Python data classes.
Python data classes require Python type hints.
There are plenty of type hint web tutorials available,
but most data classes tutorials are pretty basic and miss some important issues.
Please read some of the Python data classes tutorials,
but come back for the discussion about data classes sub-class immediately below.

In short, a Python data class is just a container with named and typed entries.
For example:

```
     from dataclasses import dataclass, field  # `field` is use later on.
     from typing import List

     @dataclass
     class Book(object):
         Title: str
         Author: str
         ISBN: str

     def __post_init__(self) -> None:   # _post_init__ is discussed later on
         pass
```

The Python `@dataclass` decorator creates an `__init__`  for the `Book` class object;
The generated `__init__` method looks basically as follows:

```
     def __init__(self, Title: str, Author: str, ISBN: str) -> None:
         self.Title = Title
         self.Author = Author
         self.ISBN = ISBN
         if hasattr(self, "__post_init__"):
             self.__post_init__()
```

The `~@dataclass` decorator generates other methods (e.g. `__repr__`, `__eq__`, etc.)
These other generated methods are not of any particular interest to the Fab package.

A trivial example of usage Book class is shown immediately below:

```
     books: List[Book]: = [
         Book("Snow Crash", "Neal Stephenson", "0553380958"),
         Book("The Shockwave Rider", "John Brunner", "0345467175"),
     ]
```

Python data classes can be sub-classed.
For example,

```
     @dataclass
     class SeriesBook(Book):
          Series: str
          Number: int

     def __post_init__(self) -> None:
          super().__post_init__()
```

With usage:

```
     books.extend([
         SeriesBook("The Fellowship of the Ring", "J. R. R. Tolkien", "0008376123",
                    "Lord of the Rings", 1),
         SeriesBook("The Fellowship of the Ring", "J. R. R. Tolkien", "0345339711",
                    "Lord of the Rings", 2),
         SeriesBook("The Return of the King", "J. R. R. Tolkien", "1514298139)",
                    "Lord of the Rings", 3),
     ])
```

You will notice that there is this method called `__post_init__()` is being shown.
This method is used to initialize attributes that are not specified by __init__ arguments.
A contrived example, is to add a `Hash` attribute to the `Book` class:

```
     from dataclasses import import dataclass, field  # Note the added `field` type

     @dataclass
     class Book(object):
         Title: str
         Author: str
         ISBN: str
         Hash: int = field(init=False)  # Not an argument in the __init__() method

     def __post_init__(self) -> None:
         self.Hash = hash(self.Title + self.Author + self.ISBN)

     @dataclass
     class SeriesBook(Book):
          Series: str
          Number: int

     def __post_init__(self) -> None:
          super().__post_init__()
```

The `Book.__init__()` method always calls `__post_init__()` to initialize attributes that do not
explicit `__init__()` method arguments (e.g. `Hash`.)

With that introduction to sub-classing Python data classes, here are the "rules" for
sub-classing Fab classes:

1. All FabClass's are Python data classes.

2. All FabClass's have a `__post_init__()` method that ***MUST*** get called.

3. Standard usage of Fab classes requires you to sub-class the
   FabProject, FabDocument, FabAssembly and FabSolid classes as Python data classes.

4. This means that your sub-classes ***MUST*** define a `__post_init__()` method, ***AND*** ...

5. Your `__post_init__()` method ***MUST*** call `super().__post_init()`.
   It can do other stuff as well, but the call to `__post_init__()` is required.

If you do not follow these steps,
the Fab system will break horribly because `__post_init__()` does not get properly called
for one of the Fab classes and the Fab code will get confused.

## Bearing Block Example

TBD:

<!-- 
Some URL's:
Note: [typeguard and dataclasses](https://stackoverflow.com/questions/71309231/typeddict-and-dataclass-check-with-typeguard)
Note: [Awesome Python Typing](https://github.com/typeddjango/awesome-python-typing)
Note: [??](https://www.youtube.com/watch?v=WJmqgJn9TXg)
Note: [Which Python @dataclass is best?](https://www.youtube.com/watch?v=vCLetdhswMg)
-->

## Additional documentation

There are some additional miscellaneous Python modules:
* [Doc](docs/Doc.md):
  A documentation extraction utility that reads the Python documentation strings and
  generates both markdown and HTML documentation files.
* [TarSync.py](TarSync.md)]:
  A program that mirrors FreeCAD `.fcstd` files to `.tar` files that are more effectively stored
  under the `git` revision control system.
* [Coding/Documentation/Testing](coding_documentation.md):
  The coding, documentation, and testing standards uses for code in
* [LICENSE.md](LICENSE.md): The Open Source license for the Model source files.

## Installation

These installation instructions are currently focused towards the Ubuntu 20.04 Linux distribution.

* Install the `build-essential` and `git` packages:

     sudo apt install build-essential git code_spell

* Clone the Fab git repository:

     mkdir -p ~/downloads  # or where you like to download git repositories.
     cd ~/downloads
     git clone ...  # (TBD)

* Run `make install`:

     make install

## Installation

Installation is always a problematic since there are multiple operating systems out there
(e.g. Windows, MacOS, Linux).
In the Linux space, there are multiple distributions (e.g. Ubuntu, Red Hat, Arch, etc.)
On top of that there various versions of all of these platforms.

Since this code is currently only has one developer,
these installation instructions are focused on Ubuntu 20.04LTS.
In late November of 2202, the plan is to update to Ubuntu 22.04LTS.

The installations steps are:

1. [Install miniconda](#install-miniconda)

2. [Install CadQuery](#install-cadquery)

3. [Install Fab](#install-fab)

4. [Install FreeCad](#install-freecad)

### Install miniconda

Cadquery is currently deployed on via [miniconda](https://docs.conda.io/en/latest/miniconda.html).

These are the steps to follow to install miniconda:

1. Look at:
   [Mini-conda linux installer](https://docs.conda.io/en/latest/miniconda.html#linux-installers)

2. Grab Mminicconda with Python 3.8 for Ubuntu 20.04LTS:

   ```
   wget https://repo.anaconda.com/miniconda/Miniconda3-py38_4.10.3-Linux-x86_64.sh -O /tmp/miniconda.sh
   ```

3. Verify [Miniconda hash information](https://docs.conda.io/en/latest/miniconda_hashes.html)

   ```
   # You probably want "Miniconda3 Linux 64-bit"
   shasum -a 256 /tmp/miniconda.sh
   # Example: 4bb91089ecc5cc2538dece680bfe2e8192de1901e5e420f63d4e78eb26b0ac1a
   ```

4. Follow the instructions in
   [How to Install Miniconda In linux](https://ostechnix.com/how-to-install-miniconda-in-linux/):

   ```
   bash /tmp/miniconda.sh
   # It will ask some questions.
   # Type ENTER to continue
   # Type spaces to scroll through license
   # Type "yes" to accept license
   # Accept ENTER to accept default install directory: (/home/YOURLOGIN/miniconda3)
   # Type "yes" for running conda init
   # Type "yes" to initialize Miniconda3
   # All done
   ```

6. Do initial miniconda activate:

   Run:

   ```
   source `~/.bashrc`
   ```

   There is a new `(base) ` prefix in your shell prompt.


6. Deactivate conda auto activate on shell startup:

   ```
   conda config --set auto_activate_base false
   source ~/.bashrc
   ```
   # The `(base) ` prefix should disappear from your shell prompt.

7. Activate and decativate conda:

   To activate/deactivate miniconda, use one of the commands below

   ```
   conda activate
   # `(base) ` should appear
   conda deactivate
   # `(base) ` should disappear
   ```

8. Update miniconda.


   ```
   conda activate
   conda update conda
   # Type `y` to do the update.
   ```

If you eventually decide remove miniconda, do the following:

1. Edit `~/.bashrc` and remove the stuff from `# >>> conda initialize >>>` to
   `# <<< conda initialize <<<<`.

2. Remove the `miniconda3` directory:

   ```
        rm -rf ~/miniconda3 ~/.condarc ~/.conda ~/continuum
   ```

### Install CadQuery

After minconda is installed do the following:

1. Watch the 10 minute CadQuery installation [Video](https://www.youtube.com/watch?v=sjLTePOq8bQ).

2. Install and activate miniforge:

   ```
   # Install miniforge in `~/miniconda` directory:
   wget https://github.com/conda-forge/miniforge/releases/latest/download/Miniforge3-Linux-x86_64.sh -O miniforge.sh
   bash miniforge.sh -b -p $HOME/miniconda
   # Do not do the init step, since it modifies your `~/.bashrc`.

   # Each time you want to activate miniconda, doe the following command:
   source $HOME/miniconda/bin/activate
   # The  miniconda/ directory is now ~407M.
   ```
   

3. Create cadquery-dev and install CadQuery from master:

   ```
   # Create the environment.
   conda create -n cadquery-dev
   # The miniconda/ directory is now ~500M.
   # Type `y` for all questions except for the init.
   conda activate cadquery-dev  # Do not forget to do this step
   conda install -c cadquery -c conda-forge cadquery=master
   # Test things out
   python3
   >> import cadquery
   >> cadquery.Workplane()
   # Deactivate cadquery-dev
   conda deactivate
   # The miniconda/ directory is ~3.2G.

4. Install cq--editor into cadquery-master:

   ```
   # Install cq-editor:
   conda activate cadquery-master
   conda install -c cadquery -c conda-forge cq-editor=master
   cq-editor
   # If a screen pops up, you have succeeded.
   # If not, well miniconda failed you.  It is not strictly required.
   # Exit the cq-editor
   conda deactivate
   # The miniconda/ directory is ~3.6G.
   ```

5. Create cadquery-stable and install CadQuery stable:

   # Create cadquery-stable and install 2.1:
   conda create -n cadquery-stable
   # Type `y` for all questions except for the init.
   conda activate cadquery-stable  # Do not forget to do this step
   conda install -c cadquery -c conda-forge cadquery=2
   # Test things out
   python3
   >> import cadquery
   >> cadquery.Workplane()
   # Deactivate cadquery-stable
   conda deactivate
   # miniconda/ directory is ~4.5G
   ```

### Install FreeCad

1. Using your web browser, visit the
   [FreeCAD Downloads Page](https://www.freecadweb.org/downloads.php)

2. Scroll to Linux tile and click on [64-Bit Appimage].
   The file usually lands in the `~/Downloads` directory named something like
   `FreeCAD_0.19.3-Linux-Conda_glibc2.12-x86_64.AppImage`

3. Move the file to `~/bin` (or wherever you feel).
   This is currently about ~915MB.

4. Install a symbolic link to make the program a little shorter to type:

   ```
   ln -s ~/bin/FreeCAD_0.19.3-Linux-Conda_glibc2.12-x86_64.AppImage ~/bin/freecad
   ```
   
4. Make the symbolic link executable:

   chmod +x ~/bin/freecad

4. Execute the FreeCAD program:

   ```
   freecad &
   ```

   The FreeCAD window should pop u.

### Install Fab

Do the following to install Fab:

1. Clone 

   ```
   git clone https://github.com/waynegramlich/Fab.git
   # The Fab directory is currently ~2MB.
   
   ```

2. Install packages:

   ```
   # To Be Figured out
   ```

### Install FreeCAD

The Fab Shop system uses some CNC tool files from the FreeCAD Path module.
In the directory that parent directory of the Fab directory,
install the entire source tree from FreeCAD.
This is a huge download to get a small number of files,
but these days both "disk space" and download bandwidth is pretty inexpensive.

    ```
    cd .. # Go to the parent directory of the Fab package
    # One of the following:
    git clone https://github.com/FreeCAD/FreeCAD.git  # If you do not have Git SSH keys installed
    git clone git@github.com:FreeCAD/FreeCAD.git  # If you do have Git SSH keys installed
    cd Fab  # Return to Fab Directory
    ls -R ../FreeCAD/src/Mod/Path/Tools  # verify that the Tools directory exists
    ```
"""

# Random links.

# [Part2DObject](http://www.iesensor.com/FreeCADDoc/0.16-dev/d9/d57/classPart_1_1Part2DObject.html)
# [App FeaturePython](https://wiki.freecadweb.org/App_FeaturePython)
# [Vidos from "Part Design Scripting" Guy](https://www.youtube.com/c/mwganson/videos)
# [Part Design Scripting](https://forum.freecadweb.org/viewtopic.php?t=62751)
# [Scripted Objects](https://wiki.freecadweb.org/Scripted_objects)
# [FilletArc]
#     (https://github.com/FreeCAD/FreeCAD/blob/master/src/Mod/PartDesign/Scripts/FilletArc.py)
# [Creating and Manipulating Geometry](https://yorikvanhavre.gitbooks.io/
#    a-freecad-manual/content/python_scripting/creating_and_manipulating_geometry.html)
# [Use LineSegment instead of Line](https://forum.freecadweb.org/viewtopic.php?p=330999)
# [Topo Data Scripting](https://wiki.freecadweb.org/index.php?title=Topological_data_scripting)
# [Part Scripting](https://wiki.freecadweb.org/Part_scripting)

# [Draft SelectPlane](https://wiki.freecadweb.org/Draft_SelectPlane)
# [Draft Workbench Scripting](https://wiki.freecadweb.org/Draft_Workbench#Scripting)

# [Combine Draft and Sketch to simplify Modeling.](https://www.youtube.com/watch?v=lfzGEk727eo)

# Note this code uses nested dataclasses that are frozen.  Computed attributes are tricky.
# See (Set frozen data class files in __post_init__)[https://stackoverflow.com/questions/53756788]

# [Part2DObject](http://www.iesensor.com/FreeCADDoc/0.16-dev/d9/d57/classPart_1_1Part2DObject.html)
# [App FeaturePython](https://wiki.freecadweb.org/App_FeaturePython)
# [Vidos from "Part Design Scripting" Guy](https://www.youtube.com/c/mwganson/videos)
# [Part Design Scripting](https://forum.freecadweb.org/viewtopic.php?t=62751)
# [Scripted Objects](https://wiki.freecadweb.org/Scripted_objects)
# [FilletArc]
#     (https://github.com/FreeCAD/FreeCAD/blob/master/src/Mod/PartDesign/Scripts/FilletArc.py)
# [Creating and Manipulating Geometry](https://yorikvanhavre.gitbooks.io/
#    a-freecad-manual/content/python_scripting/creating_and_manipulating_geometry.html)
# [Use LineSegment instead of Line](https://forum.freecadweb.org/viewtopic.php?p=330999)
# [Topo Data Scripting](https://wiki.freecadweb.org/index.php?title=Topological_data_scripting)
# [Part Scripting](https://wiki.freecadweb.org/Part_scripting)

# [Draft SelectPlane](https://wiki.freecadweb.org/Draft_SelectPlane)
# [Draft Workbench Scripting](https://wiki.freecadweb.org/Draft_Workbench#Scripting)
