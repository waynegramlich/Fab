b# ShopFab

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

