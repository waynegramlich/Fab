# ShopFab

ShopFab is Python library for device design and fabrication.

## Introduction

ShopFab is FreeCAD focused Python library that supports a DFM workflow where:
* FreeCAD is an open source CAD/CAM (Computer Aided Design/Manufacturing) application,
* Python is currently a rather popular programming language, and
* DFM stands for Design For Manufacture.
ShopFab library aids the process of converting from an idea into a physical object.

In ShopFab, each individual part starts with some stock material followed by operations
performed on the stock material (e.g. contour outlines, drill holes, remove pockets, etc.)
All of the individual parts are assembled into a final assembly which can be viewed
using FreeCAD.

With ShopFab, the machines/tooling for each different shop are specified.
The ShopFab part design in conjunction with the ShopFab shop specification will generate
the various files (G-code, STL, DXF) needed to manufacture the part for the specific shop.
Thus, one ShopFab design can be easily shared among multiple people with differing shops
and still result in essentially the same physical object.

