"""Fab: Python Model/Fabrication w/FreeCAD.

## Table of Contents:

* [Introduction](#introduction)
* [Overview](#overview)
* [Python Modules](#python-modules)
* [Addtional Documentation](#additional-documentation)
* [Installation](#installation)

## Introduction <a name="introduction"></a>

The Fab package is a FreeCAD focused Python library that supports a DFM workflow where:
* FreeCAD is an open source CAD/CAM (Computer Aided Design/Manufacturing) application,
* Python is rather popular programming language, and
* DFM stands for Design For Manufacture.
The Fab Python package aids the process of transforming an idea int a design and eventually
into finalized physical object.

In Fab, each individual part conceptually starts with some stock material followed by operations
performed on the stock material (e.g. contour outlines, drill holes, remove pockets, etc.)
All of the individual parts are assembled into a final assembly which can be viewed
using FreeCAD.

Fab supports the concept of multiple different shops, where the specific shop machines
and tooling are specified.
The Fab design in conjunction with a the Fab shop specification generates the various files
(`.cnc`, `.stl`, `.dxf`, etc.) needed to manufacture the part for a specific shop.
Thus, one Fab design can be shared among multiple people with different shops and
still get basically the same physical objects.

## Overview <a name="overview"></a>

The Fab strategy is to construct nested tree of FabNode's, where a FabNode is the primitive
base class and roughly (but not exactly) corresponds to an object in the FreeCAD object tree.
There are various sub-classes of FabNode -- FabGeometry, FabOperation, FabSolid,
FabAssembly, FabFile, and FabRoot, where FabRoot is the root of the FabNode tree.

The FabNode tree is constructed in a bottom up fashion:
1. Various lengths and angles are defined.
2. 3D points, called Vectors's, are defined using the various lengths and angles.
3. Subsets of the Vectors's are projected onto a 2D plane to form lines, arcs, and circles
   which are then converted to form a 2D drawing which based the FreeCAD Draft workbench.
   The 2D geometry is the FabGeometry.
4. These drawings are converted into solid geometry using the some additional FabNode's
   (called FabOperation's) that basically schedule the FreeCAD PartDesign workbench to
   perform using a variety of 3D operations (e.g. extrude, pocket, drill, etc.) resulting
   in a FabSolid.
5. The various parts are configured into assemblies (FabAssembly) and FreeCAD `.FCstd` files
   (ModeFabFile) are stored in the root of the tree (FabRoot).

Once the FabRoot is present there are 4 phases performed:
1. The FabRoot is iterated in configuration mode whereby constraints are propagated through
   out the Fab tree.  Sometimes there is a constraint loop, which is detected and reported
   as a failure that needs to get fixed.
2. The FabRoot is iterated over to construct the 3D model which can be viewed using FreeCAD.
3. When the design looks good, all of the manufacturing files are generated
   (e.g. .nc, .stl, .dxf files.)
4. The manufacturing files are used to fabricate the individual parts which are
   then assembled into the final assembly.

## Python Modules <a name="python-modules"></a>

The basic Python bottom up Python module list is:
* [Utilities](Utilities.html):
  Utilities module of miscellaneous classes -- Colors, Materials, etc.
* [Node](Node.html):
  This defines the FabBox bounding box and FabNode tree node classes.
* [Geometry](Geometry.html):
  The defines the 2D geometry FabNode classes for using the FreeCAD Draft workbench.
* [Solid](Solid.html):
  A library that supports generating parts using the FreeCAD PartDesign workbench.
* [Shop](Shop.html):
  A library that defines machines and tooling available in a given shop.
* [CNC](CNC.html):
  A library that interfaces with the FreeCAD Path workbench for producing CNC files.

## Type Hints and Data Classes

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

