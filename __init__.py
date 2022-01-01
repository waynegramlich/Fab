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
  Utilities module of miscellaneous classes -- Bounding Box, Colors, Materials, etc.
* [Tree](Tree.html):
  This defines the basic FabNode classes.
* [Geometry](Geometry.html):
  The defines the 2D geometry FabNode classes for using the FreeCAD Draft workbench.
* [Solid](Solid.html):
  A library that supports generating parts using the FreeCAD PartDesign workbench.
* [Shop](Shop.html):
  A library that defines machines and tooling available in a given shop.
* [CNC](CNC.html):
  A library that interfaces with the FreeCAD Path workbench for producing CNC files.

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

