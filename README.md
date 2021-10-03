# ShopFab

ShopFab is Python library for device design and fabrication.

## Introduction

ShopFab is FreeCAD focused Python library that supports a DFM workflow where:
* FreeCAD is an open source CAD/CAM (Computer Aided Design/Manufacturing) application,
* Python is rather popular programming language, and
* DFM stands for Design For Manufacture.
The ShopFab library aids the process of transforming an idea into a physical object.

In ShopFab, each individual part starts with some stock material followed by operations
performed on the stock material (e.g. contour outlines, drill holes, remove pockets, etc.)
All of the individual parts are assembled into a final assembly which can be viewed
using FreeCAD.

ShopFab supports the concept of multiple different shops, where the specific shop machines
and tooling are specified.
The ShopFab part design in conjunction with the ShopFab shop specification generates
the various files (G-code, STL, DXF) needed to manufacture the part for the specific shop.
Thus, one ShopFab design can be easily shared among multiple people with different shops
and still get basically the same physical objects.

## Overview

The overall strategy is that overall project is nested tree of ApexPart's.
The ApexPart tree leaf nodes are individual physical parts and
the interior nodes are sub-assemblies.
The way that each physical part is developed to create a Python class
that sub-classes ApexPart and provides a small number of required methods.

The process of an ApexPart is as follows:
1. Various lengths and angles are defined.
2. 3D points, called ApexVector's, are defined using the various lengths and angles.
3. Subsets of the ApexVector's are projected onto a 2D plane to form lines, arcs,
   and circles which are then converted to form a 2D sketch, called an ApexSketch,
   which is 1-to-1 with a FreeCAD Sketch.
4. The ApexSketchs are converted into solid geometry using the FreeCAD Part Library doing
   various CNC style operations such as Contouring, Drilling, Pocketing, etc.

The final steps are to:
1. Iteratively propagate constraints between all of the ApexPart's.
2. The resultant design can be read into FreeCAD to view the design.
3. When the design looks good, all of the manufacturing files are generated
   (e.g. .nc, .stl, .dxf files.)
4. The manufacturing files are used to fabricate the individual parts which are
   then assembled into the final assembly.


