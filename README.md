# ApexShop: Python Focused Device Design and Fabrication

[Introduction](#introduction)

[Overview](#overview)

[Python Modules](#python-modules)

[Installation](#installation)


## Introduction <a name="introduction"></a>

ApexShop is FreeCAD focused Python library that supports a DFM workflow where:
* FreeCAD is an open source CAD/CAM (Computer Aided Design/Manufacturing) application,
* Python is rather popular programming language, and
* DFM stands for Design For Manufacture.
The ApexShop library aids the process of transforming an idea into a physical object.

In ApexShop, each individual part starts with some stock material followed by operations
performed on the stock material (e.g. contour outlines, drill holes, remove pockets, etc.)
All of the individual parts are assembled into a final assembly which can be viewed
using FreeCAD.

ApexShop supports the concept of multiple different shops, where the specific shop machines
and tooling are specified.
The ApexShop part design in conjunction with the ApexShop shop specification generates
the various files (G-code, STL, DXF) needed to manufacture the part for the specific shop.
Thus, one ApexShop design can be easily shared among multiple people with different shops
and still get basically the same physical objects.

The Apex prefix is used because it short and sounds "cool".

## Overview <a name="overview"></a>

The overall strategy is that an overall project is nested tree of ApexPart's.
The ApexPart tree leaf nodes are physical parts that can be purchased/manufactured and
the interior nodes are sub-assemblies.
Each part/assembly is a sub-class of ApexPart.

The process of creating an ApexPart is as follows:
1. Various lengths and angles are defined.
2. 3D points, called ApexPoints's, are defined using the various lengths and angles.
3. Subsets of the ApexPoints's are projected onto a 2D plane to form lines, arcs,
   and circles which are then converted to form a 2D sketch, called an ApexSketch,
   which is 1-to-1 with a FreeCAD Sketch.
4. The ApexSketchs are converted into solid geometry using the FreeCAD Part Library doing
   various CNC style operations such as Contouring, Drilling, Pocketing, etc.

The final steps are to:
1. The ApexPart tree is iterated over to propagate constraints between individual ApexPart's.
2. The resultant design can be read into FreeCAD to view.
3. When the design looks good, all of the manufacturing files are generated
   (e.g. .nc, .stl, .dxf files.)
4. The manufacturing files are used to fabricate the individual parts which are
   then assembled into the final assembly.

## Python Modules <a name="python-modules"></a>

The bottom up module list is:
* [ApexBase](ApexBase.md):
  A libarary of base classes for lengths, angles, bounding boxes, transform matrices etc.
* [ApexSketch](ApexSketch.md):
  A library that converts ApexPoint's into fully constrained FreeCAD sketches.
* [ApexPart](ApexPart.md):
  A library that supports generating parts using the FreeCAD PartDesign workbench.
* [ApexShop](ApexShop.md):
  A library that defines machines and tooling available in a given shop.
* [ApexPath](ApexPath.md):
  A library that interfaces with the FreeCAD Path subsystem to generate CNC G-code files.

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
* [LICENSE.md](LICENSE.md): The Open Source license for the Apex source files.

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
