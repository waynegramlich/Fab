"""Fab: Python Modeling and Fabrication.

## Table of Contents:

* [Introduction](#introduction)
* [Overview](#overview)
* [Commonly Used Fab Classes](#commonly-used-fab-classes)
* [Workflow](#workflow)
* [Python Modules](#python-modules)
* [Addtional Documentation](#additional-documentation)
* [Installation](#installation)


## Introduction <a name="introduction"></a>

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
   Simple projects can be in one Python module,
   but more complex projects will span multiple Python modules (e.g. a Python package.)
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

## Commonly Used Fab Classes <a name="commonly-used-fab-classes"></a>

Each Fab project is implemented as one or more Python files that import Fab package classes.
(As a side note, each user facing Fab class is always prefixed with `Fab`.)

The Fab strategy is to construct nested tree of FabNode's,
where a FabNode is a base class that sub-classed to provide additional structure.
The sub-classes are:

1. FabProject: This is the top level FabNode that encapsulates your entire project.

2. FabDocument: This corresponds to a FreeCAD document file (i.e. `.FCStd`).

3. FabAssembly: This a group of smaller FabAssembly's and FabSolid's.

4. FabSolid: This corresponds to a single Solid object
   that can be represented as CAD industry standard file interchange format call a STEP file.

There is one FabProject at the tree root, typically almost always just one FabDocument,
followed nested as series of zero, one or more FabAssembly's,
with the leaf nodes all being FabSolid's.

An example decomposition is shown immediately below:

* FabProject (root)
  * FabDocument (usually only one of these)
    * FabAssembly 1 (usually there is just one top level FabAssembly just under the Fab Document)
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
   Constraint propagation is an iterative process where each FabNode is allow to
   access values defined in other FabNode's to compute new values for itself.
   The `produce` method of each for each FabNode is recursively called until the
   constraint values no longer change.
   It is possible to get into a loop where some constraints do not converge to a final stable value.
   When this occurs, Fab system lists the values that did not converge.

3. Solid Construction.

   Using the same `produce` method for defined for each FabNode,
   each produce method is called once is "construct" mode.
   In this mode, the FabMount objects (see above) are activated
   and the underlying CadQuery machinery is activated to produce one STEP file per solid.
   A STEP file is a standard file format for the interchange of 3D parts and assemblies.
   In addition, a JSON file is generated that summarizes what was generated.
   
4. Visualization.

   The FreeCAD program is used for both visualization of the resulting parts and assembly
   and for generating CNC G-code files.
   For technical reasons, CadQuery can not be subsumed into FreeCad, so this code has
   to be run separately.
   In the visualization step, the previously generated JSON file is read which, in turn,
   causes all of the generated STEP files to be read into FreeCad for viewing purposes.

   If CNC is specified, the FreeCad CNC Path package is accessed to generate G-code files.
   The G-code paths can also be visualized using FreeCAD.
   Indeed, the FreeCAD Path simulator can be used to simulate the machining process.

5. Fabrication.

   The generated `.cnc`, `.dxf`, `.stl` files, can be fed into the appropriate shop machines
   to actually fabricate each part.

## Python Modules <a name="python-modules"></a>

The (current) main Python modules are:

* [Project](docs/Project.html):
  The top level FabNode sub-classes of FabProject, FabDocument, and FabAssembly.

* [Solid](docs/Solid.html):
  The Solid creation class of FabSolid and FabMount.

* [Geometry](docs/Geometry.html):
  The FabPolygon, FabCircle sub-classes of FabGeometry.

* [Node](docs/Node.html):
  The base FabNode class and associated FabBox class for describing bounding boxes.

* [Utilities](doc/Utilities.html):
  This contains some utility classes like FabColor and FabMaterial.

Additional Python modules are:

* [Shop](docs/Shop.html):
  Classes for defining Shop machines and tooling.

* [CNC](docs/CNC.html):
  Classes for accessing the FreeCad Path CNC G-code generation library.

* [Join](docs/Join.html):
  Classes for defining fastener stacks of screws, bolts, washers, nuts, etc.

* [Doc](docs/Doc.html):
  A program for reading Python files and generating HTML documentation.

* [BOM](docs/BOM.html):
  The beginnings of a Bill of Materials manager.

## Type Hints and Data Classes <a name="type-hints-and-data-classes"></a>

(This section is really painful to read and needs to be fixed.)

If you are completely unfamiliar with Python Type hints, please see the following references:
* [mypy](http://mypy-lang.org/)
* [`typing` -- Support for type hints](https://docs.python.org/3/library/typing.html)

While the underlying FreeCAD Python support currently does not support Python type hints,
the Fab Python package is heavily annotated with Python Type Hints.
What this means is that if you write your Python code that uses the Fab package using type hints,
you can frequently uncover errors via before execution using static analysis with the
`mypy` program.

In addition, all Fab Package classes are done using Python data classes (see immediately below).
Python data classes which ***require*** type hints.
Since the way the Fab package requires that you that you sub-class from Fab package classes,
its necessary to learn more about both topics.

The reference documentation of [Data Classes](https://docs.python.org/3/library/dataclasses.html)
is actually quite dense and difficult to understand.
The readily available free tutorials are good,
but tend to be introductory without getting into important details.
This section attempts to delve into the data class issues that are important for the Fab package.

A basic usage of data classes is:

     # Import the `dataclass` "decorator" from the `dataclasses` package.
     from dataclasses import dataclass, field

     # Define the dataclass:
     @dataclass  # Decorator that specifies class is a data class
     class ClassName(SubClass):  # The `class` definition with associated SubClass
         '''Python class documentation string goes here.'''

         FieldName1: Type1   # There ***MUST*** be at least one field defined.
         FieldName2: Type2
         # ...
         FieldNameN: TypeN     

         def __post_init__(self) -> None:
             '''Python method documentation string goes here.'''
             super().__post_init__()  # Required for sub-class.  Not needed for a base dataclass.

             # Additional initialization code goes here.

The key thing is that it is a Python class definition with a preceding `@dataclass` decorator.
There are one or more field names followed by a colon and a type hint.
What the class decorator does is generate both an `__init__()` method and a `__repr__()`.

The field names are defined in one of three ways:

        Required: Type
        Optional: Type = InitialValue
        Private: Type = field(init=False, ...)

All required and optional fields show up in the generated `__init__()` method.
None of the private fields show up in the `__init__()` method.

Understanding the `__init__()` method construction is *very* important.
The order that fields show up in the `__init__()` method depends on sub-classing.
Look at the following contrived example:

     @dataclass
     class BaseClass(object):
        BR1: BRT1  # Base Required 1
        BR2: BRT2  # Base Required 2
        BO1: BOT1 = BV1  # Base Optional 1
        BO2: BOT2 = BV2  # Base Optional 2
        BP1: BPT1 = field(init=False)  # Base Private 1
        BP2: BPT2 = field(init=False)  # Base Private 2

     @dataclass
     class SubClass(object):
        SR1: SRT1  # Base required type
        SR2: SRT2  # Base required type
        SO1: SOT1 = SV1 # Base optional type
        SO2: SOT2 = SV2  # Base optional type
        SP1: SPT1 = field(init=False)
        SP2: SPT2 = field(init=False)

The generated `__init__()` method for BassClass is:

     def __init__(BR1: BRT1, BR2: BRT2, BO1: BOT1 = BV1, BO2: BPT2 = BV2) -> None:
        ...

The generated `__init__()` method for SubClass is:

     def __init__(BR1: BRT1, BR2: BRT2, BO1: BOT1 = BV1, BO2: BOT2 = BV2,
                  SR1: SRT1, SR2: SRT2, SO1: SOT1 = SV1, SO2: SOT2 = BV2) -> None:
         # ...

Notice that all of the required arguments are sorted first, followed by the optional arguments.
None of the private fields show up in the `__init__()` method.

This is really important.  All dataclass's should implement the `__post_init__()` method.
This method is called by at the end of the generated `__init__()` method.  There are a
few situations where it can be skipped, but they are not worth figuring out.  In addition,
each sub_class needs to call the `__post_init__()` method of its super class.

     @dataclass
     class BassClass(object):
         '''Documentation string.'''

         Field1: Type1
         ...
         FieldN: TypeN

         def __post_init__(self) -> None:
             '''Documentation String.'''
             # Either `pass` or some other initialization code goes here.

     @dataclass
     class SubClass(BaseClass):
         '''Documentation string.'''

         SField1: SType1
         ...
         SFieldN: STypeN

         def __post_init__(self) -> None:
             '''Documentation string.'''
             super().__post_init__()
             # More initialization code goes here.

Next, the `__repr__()`  method needs discussion.  In general, every field will show up
in the `__repr__()` method unless it is explicitly disabled.  The way to disable the
field in `__repr__()` is as follows:

    RequiredField: RequiredType = field(init=False)
    OptionalField: OptionalType = field(init=False, default=OptionalValue)
    PrivateField: PrivateType = field(init=False, repr=False)

By common convention, classes, methods, and fields that start with an underscore (`'_'`)
are considered to be private and only the "owner" should access these fields.
While other languages enforce private fields, Python does not.
The preceding underscore convention is widely adhered to through out large bodies of Python code.

Sometime it is desirable to provide read only access to field.
The preferred way to solve this problem is to use a python property.
(See [Methods and @property)](https://pythonguide.readthedocs.io/en/latest/python/property.html)
for more detail.

In short a private field can provide a public read-only access as follows:

     @dataclass
     class MyClass(object):
         '''MyClass documentation string.'''

         _Field: FieldType   # Internal field declaration

        # Accessor function for 
        @property
        def Field(self) -> FieldType:
            '''Field documentation string.'''
            return self._Field

It should be noted that many of the most common FreeCAD base types
(e.g. Vector, Rotation, Placement, etc.) are *mutable*, where mutable means that
the contents can be changed.
Usually, people like to treat these classes as if they are immutable.
It is extremely copy to have accessor functions that return a copy of a private field.
For the FreeCAD Vector class, the easiest way to make a copy is as follows:

     @property
     def Normal(self) -> Vector:
         '''Return the Normal to the object.'''
         copy: Vector = Vector()  # Returns Vector(0, 0, 0)
         return self._Normal + copy  # Returns a copy of self._Normal.

Likewise when mutable object is passed into dataclass, it is frequently desirable to
make a private copy.  This can be done in `__post_init__()`:

         @dataclass
         class LineSegment(object):
             '''LineSegment document string goes here.'''

             _Point1: Vector
             _Point2: Vector
             _copy: Vector = field(init=False, repr=False)
    
             def __post_init__(self) -> self:
                 '''Document string goes here.'''
                 self._copy: Vector = Vector()
                 self._Point1 += copy  # Force copy into _Point1
                 self._Point2 += copy  # Force copy into _Point2

             @property
             def Point1(self) -> Vector:
                 '''Document string goes here.'''
                 return self._Point1 + self._copy  # Return copy of _Point1
             
             @property
             def Point2(self) -> Vector:
                 '''Document string goes here.'''
                 return self._Point2 + self._copy  # Return copy of _Point2
            

Usage of the class above would be like:

     point1: Vector = Vector(1, 2, 3)
     point2: Vector = Vector(4, 5, 6)
     line_segment: LineSegment = LineSegment(point1, point2)
     # Copies of *point1* and *point2* are stored in *line_segment*.

     assert line_segment.point1 == Vector(1, 2, 3)

     point1.x = -1  # Modify point1
     assert point1 == Vector(-1, 2, 3)

     segment_point1: Vector = line_segment.Point1
     assert segment.point1 == Vector(1, 2, 3)  # The copies were used.

     segment_point1.y = -2
     assert segment_point == Vector(1, -2, 3)

     assert line_segment.Point1 == Vector(1, 2, 3)  # The accessor always returns a copy.

It would be nice if the FreeCAD Vector class were not mutable, but since it is not,
extra care is the prudent way to avoid accidental mutations of internal values.

## Additional documentation <a name="additional-documentation"></a>

There are some additional miscellaneous Python modules:
* [Doc](docs/Doc.html):
  A documentation extraction utility that reads the Python documentation strings and
  generates both markdown and HTML documentation files.
* [Embedded FreeCAD](embedded_freecad.html):
  This explains how the Fab modules can be run within or externally from FreeCAD.
* [fcstd_tar_sync.py](fcstd_tar_sync.html)]:
  A program that mirrors FreeCAD `.fcstd` files to `.tar` files that are more easily stored
  under the `git` revision control system.
* [Coding/Documentation/Testing](coding_documentation.html):
  The coding, documentation, and testing standards uses for code in
* [LICENSE.md](LICENSE.md): The Open Source license for the Model source files.

## Installation <a name="installation"></a>

These installation instructions are currently focused towards the Ubuntu 20.04 Linux distribution.

* Install the `build-essential` and `git` packages:

     sudo apt install build-essential git

* Clone the Fab git repository:

     mkdir -p ~/downloads  # or where you like to download git repositories.
     cd ~/downloads
     git clone ...  # (TBD)

* Run `make install`:

     make install

"""

