"""Model: Python Focused Device Design and Fabrication.

# Table of Contents:

* [Introduction](#introduction)
* [Overview](#overview)
* [Python Modules](#python-modules)
* [Installation](#installation)

## Introduction <a name="introduction"></a>

The Model package is a FreeCAD focused Python library that supports a DFM workflow where:
* FreeCAD is an open source CAD/CAM (Computer Aided Design/Manufacturing) application,
* Python is rather popular programming language, and
* DFM stands for Design For Manufacture.
The Model library aids the process of transforming an idea int a design and eventually
into finalized physical object.

In Model, each individual part starts with some stock material followed by operations
performed on the stock material (e.g. contour outlines, drill holes, remove pockets, etc.)
All of the individual parts are assembled into a final assembly which can be viewed
using FreeCAD.

Model supports the concept of multiple different shops, where the specific shop machines
and tooling are specified.
The ApexShop part design in conjunction with the ApexShop shop specification generates
the various files (G-code, STL, DXF) needed to manufacture the part for the specific shop.
Thus, one ApexShop design can be easily shared among multiple people with different shops
and still get basically the same physical objects.

## Overview <a name="overview"></a>

The overall strategy is that an overall project is nested tree of ModelNode's.
The ModelNode is the primitive base class and roughly (but not exactly) corresponds
to the FreeCAD object tree.
There are various sub-classes of ModeNode -- ModelGeometry, ModelOperation, ModelPart,
ModelAssembly, ModelFile, and ModelRoot, where ModelRoot is the root of the ModeNode tree.

The ModelNode tree is constructed in a bottom up fashion:
1. Various lengths and angles are defined.
2. 3D points, called Vectors's, are defined using the various lengths and angles.
3. Subsets of the Vectors's are projected onto a 2D plane to form lines, arcs, and circles
   which are then converted to form a 2D drawing which based the FreeCAD Draft workbench.
   The 2D geometry is the ModelGeometry sub-class of ModelNode.
4. These drawings are converted into solid geometry using the some additional ModelNode's
   (called ModelOperation's) that basically schedule the FreeCAD PartDesign workbench to
   perform using a variety of 3D operations (e.g. extrude, pocket, drill, etc.)
   The result is a the ModelPart sub-class of ModelNode.
5. The various parts are configured into assemblies with a ModelAssembly sub-class of ModelNode.
6. The final ModelRoot sub-class of ModeNode is created.

Once the ModelRoot is present there are 4 phases perfomed:
1. The ModelRoot is iterated in configuration mode whereby constraints are propagated through
   out the ModeTree.  Sometimes there is a constraint loop, which is detected and reported
   as a failure that needs to get fixed.
2. The ModelRoot is iterated over to construct the 3D model which can be viewed using FreeCAD.
3. When the design looks good, all of the manufacturing files are generated
   (e.g. .nc, .stl, .dxf files.)
4. The manufacturing files are used to fabricate the individual parts which are
   then assembled into the final assembly.

## Python Modules <a name="python-modules"></a>

The bottom up module list is:
* [Utilitys](Utilitys.html):
  Utility module of miscellaneous classes -- Bounding Box, Colors, Materials, etc.
* [Tree](Tree.html):
  This defines the basic ModeNode classes.
* [Geometry](Geometry.html):
  The defines the 2D geometry ModelNode classes for using the FreeCAD Draft workbench.
* [Part](ApexNode.html):
  A library that supports generating parts using the FreeCAD PartDesign workbench.
* [Shop](Shop.html):
  A library that defines machines and tooling available in a given shop.
* [CNC](CNC.html):
  A library that interfaces with the FreeCAD Path workbench for producing CNC files.
* [Doc](Doc.html):
  A documentation extraction utility that reads the Python documentation strings and
  generates both markdown and HTML documentation files.

Some miscellaneous files are:
* [py2md](py2md.md):
  A Python documentation string to markdown file generator.
* [Embedded FreeCAD](embedded_freecad.md):
  This explains how the Apex modules can be run within or externally from FreeCAD.
* [fcstd_tar_sync.py](fcstd_tar_sync.md)]:
  A program that mirrors FreeCAD `.fcstd` files to `.tar` files that are more easily stored
  under the `git` revision control system.
* [Coding/Documentation/Testing](coding_documentation.md):
  The coding, documentation, and testing standards uses for code in
* [LICENSE.md](LICENSE.md): The Open Source license for the Model source files.

## Installation <a name="installation"></a>

These installation instructions are currently focused towards the Ubuntu 20.04 Linux distribution.

* Install `build-essential` and `git` packages
     sudo apt install build-essential git
* Clone repository Apex git repository:
     mkdir -p ~/downloads  # or where you like to download git repositories.
     cd ~/downloads
     git clone ....
* Run `make install`:
     make install

"""

