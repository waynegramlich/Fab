# ApexSketch: An interface to FreeCAD Sketches.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class ApexCircle](#apexcircle)
  * 2.1 [ApexCircle.\_\_post\_init](#apexcircle---post-init)
  * 2.2 [ApexCircle.get\_constraints](#apexcircle-get-constraints)
  * 2.3 [ApexCircle.get\_geometries](#apexcircle-get-geometries)
  * 2.4 [ApexCircle.reorient](#apexcircle-reorient)
* 3 [Class ApexCorner](#apexcorner)
  * 3.1 [ApexCorner.\_\_post\_init\_\_](#apexcorner---post-init--)
  * 3.2 [ApexCorner.\_unit\_tests](#apexcorner--unit-tests)
* 4 [Class ApexDrawing](#apexdrawing)
  * 4.1 [ApexDrawing.\_\_post\_init\_\_](#apexdrawing---post-init--)
  * 4.2 [ApexDrawing.create\_datum\_plane](#apexdrawing-create-datum-plane)
  * 4.3 [ApexDrawing.get\_geometries](#apexdrawing-get-geometries)
  * 4.4 [ApexDrawing.get\_origin\_constraints](#apexdrawing-get-origin-constraints)
  * 4.5 [ApexDrawing.plane\_process](#apexdrawing-plane-process)
  * 4.6 [ApexDrawing.reorient](#apexdrawing-reorient)
  * 4.7 [ApexDrawing.sketch](#apexdrawing-sketch)
* 5 [Class ApexHole](#apexhole)
  * 5.1 [ApexHole.\_\_post\_init\_\_](#apexhole---post-init--)
  * 5.2 [ApexHole.body\_apply](#apexhole-body-apply)
  * 5.3 [ApexHole.get\_shape](#apexhole-get-shape)
  * 5.4 [ApexHole.reorient](#apexhole-reorient)
* 6 [Class ApexOperation](#apexoperation)
  * 6.1 [ApexOperation.body\_apply](#apexoperation-body-apply)
  * 6.2 [ApexOperation.get\_constraints](#apexoperation-get-constraints)
  * 6.3 [ApexOperation.get\_geometries](#apexoperation-get-geometries)
  * 6.4 [ApexOperation.get\_shape](#apexoperation-get-shape)
  * 6.5 [ApexOperation.reorient](#apexoperation-reorient)
  * 6.6 [ApexOperation.show](#apexoperation-show)
* 7 [Class ApexPad](#apexpad)
  * 7.1 [ApexPad.\_\_post\_init\_\_](#apexpad---post-init--)
  * 7.2 [ApexPad.body\_apply](#apexpad-body-apply)
  * 7.3 [ApexPad.get\_shape](#apexpad-get-shape)
  * 7.4 [ApexPad.reorient](#apexpad-reorient)
* 8 [Class ApexPocket](#apexpocket)
  * 8.1 [ApexPocket.\_\_post\_init\_\_](#apexpocket---post-init--)
  * 8.2 [ApexPocket.body\_apply](#apexpocket-body-apply)
  * 8.3 [ApexPocket.get\_shape](#apexpocket-get-shape)
  * 8.4 [ApexPocket.reorient](#apexpocket-reorient)
* 9 [Class ApexPolygon](#apexpolygon)
  * 9.1 [ApexPolygon.\_\_post\_init\_\_](#apexpolygon---post-init--)
  * 9.2 [ApexPolygon.\_arcs\_create](#apexpolygon--arcs-create)
  * 9.3 [ApexPolygon.\_get\_constraints](#apexpolygon--get-constraints)
  * 9.4 [ApexPolygon.\_get\_geometries](#apexpolygon--get-geometries)
  * 9.5 [ApexPolygon.\_get\_wire](#apexpolygon--get-wire)
  * 9.6 [ApexPolygon.\_lines\_create](#apexpolygon--lines-create)
  * 9.7 [ApexPolygon.\_radii\_overlap\_check](#apexpolygon--radii-overlap-check)
  * 9.8 [ApexPolygon.\_unit\_tests](#apexpolygon--unit-tests)
  * 9.9 [ApexPolygon.get\_box](#apexpolygon-get-box)
  * 9.10 [ApexPolygon.get\_constraints](#apexpolygon-get-constraints)
  * 9.11 [ApexPolygon.get\_geometries](#apexpolygon-get-geometries)
  * 9.12 [ApexPolygon.reorient](#apexpolygon-reorient)
  * 9.13 [ApexPolygon.show](#apexpolygon-show)
* 10 [Class ApexShape](#apexshape)
  * 10.1 [ApexShape.\_get\_constraints](#apexshape--get-constraints)
  * 10.2 [ApexShape.\_get\_wire](#apexshape--get-wire)
  * 10.3 [ApexShape.get\_box](#apexshape-get-box)
  * 10.4 [ApexShape.get\_constraints](#apexshape-get-constraints)
  * 10.5 [ApexShape.get\_geometries](#apexshape-get-geometries)
  * 10.6 [ApexShape.reorient](#apexshape-reorient)
  * 10.7 [ApexShape.show](#apexshape-show)
* 11 [Class ArcGeometry](#arcgeometry)
  * 11.1 [ArcGeometry.Finish](#arcgeometry-finish)
  * 11.2 [ArcGeometry.FinishKey](#arcgeometry-finishkey)
  * 11.3 [ArcGeometry.Radius](#arcgeometry-radius)
  * 11.4 [ArcGeometry.Start](#arcgeometry-start)
  * 11.5 [ArcGeometry.StartKey](#arcgeometry-startkey)
  * 11.6 [ArcGeometry.TypeName](#arcgeometry-typename)
  * 11.7 [ArcGeometry.\_\_init\_\_](#arcgeometry---init--)
  * 11.8 [ArcGeometry.\_\_str\_\_](#arcgeometry---str--)
  * 11.9 [ArcGeometry.apex](#arcgeometry-apex)
  * 11.10 [ArcGeometry.begin](#arcgeometry-begin)
  * 11.11 [ArcGeometry.center](#arcgeometry-center)
  * 11.12 [ArcGeometry.end](#arcgeometry-end)
  * 11.13 [ArcGeometry.finish\_angle](#arcgeometry-finish-angle)
  * 11.14 [ArcGeometry.finish\_length](#arcgeometry-finish-length)
  * 11.15 [ArcGeometry.get\_begin\_pair](#arcgeometry-get-begin-pair)
  * 11.16 [ArcGeometry.get\_begin\_point](#arcgeometry-get-begin-point)
  * 11.17 [ArcGeometry.get\_center\_pair](#arcgeometry-get-center-pair)
  * 11.18 [ArcGeometry.get\_end\_pair](#arcgeometry-get-end-pair)
  * 11.19 [ArcGeometry.get\_end\_point](#arcgeometry-get-end-point)
  * 11.20 [ArcGeometry.input](#arcgeometry-input)
  * 11.21 [ArcGeometry.name](#arcgeometry-name)
  * 11.22 [ArcGeometry.part\_geometry](#arcgeometry-part-geometry)
  * 11.23 [ArcGeometry.start\_angle](#arcgeometry-start-angle)
  * 11.24 [ArcGeometry.start\_length](#arcgeometry-start-length)
  * 11.25 [ArcGeometry.sweep\_angle](#arcgeometry-sweep-angle)
* 12 [Class CircleGeometry](#circlegeometry)
  * 12.1 [CircleGeometry.get\_part\_geometry](#circlegeometry-get-part-geometry)
  * 12.2 [CircleGeometry.type\_name](#circlegeometry-type-name)
* 13 [Class Corner](#corner)
  * 13.1 [Corner.\_\_post\_init\_\_](#corner---post-init--)
  * 13.2 [Corner.\_get\_end\_point](#corner--get-end-point)
  * 13.3 [Corner.\_get\_start\_point](#corner--get-start-point)
  * 13.4 [Corner.foo](#corner-foo)
  * 13.5 [Corner.get\_begin\_point](#corner-get-begin-point)
  * 13.6 [Corner.get\_constraints](#corner-get-constraints)
  * 13.7 [Corner.get\_end\_point](#corner-get-end-point)
  * 13.8 [Corner.get\_first\_geometry](#corner-get-first-geometry)
  * 13.9 [Corner.get\_geometries](#corner-get-geometries)
  * 13.10 [Corner.get\_last\_geometry](#corner-get-last-geometry)
* 14 [Class Geometry](#geometry)
  * 14.1 [Geometry.Finish](#geometry-finish)
  * 14.2 [Geometry.FinishKey](#geometry-finishkey)
  * 14.3 [Geometry.Index](#geometry-index)
  * 14.4 [Geometry.Name](#geometry-name)
  * 14.5 [Geometry.Start](#geometry-start)
  * 14.6 [Geometry.StartKey](#geometry-startkey)
  * 14.7 [Geometry.TypeName](#geometry-typename)
  * 14.8 [Geometry.get\_begin\_pair](#geometry-get-begin-pair)
  * 14.9 [Geometry.get\_begin\_point](#geometry-get-begin-point)
  * 14.10 [Geometry.get\_center\_pair](#geometry-get-center-pair)
  * 14.11 [Geometry.get\_constraints](#geometry-get-constraints)
  * 14.12 [Geometry.get\_end\_pair](#geometry-get-end-pair)
  * 14.13 [Geometry.get\_end\_point](#geometry-get-end-point)
  * 14.14 [Geometry.get\_part\_geometry](#geometry-get-part-geometry)
* 15 [Class LineGeometry](#linegeometry)
  * 15.1 [LineGeometry.Finish](#linegeometry-finish)
  * 15.2 [LineGeometry.FinishKey](#linegeometry-finishkey)
  * 15.3 [LineGeometry.Name](#linegeometry-name)
  * 15.4 [LineGeometry.Start](#linegeometry-start)
  * 15.5 [LineGeometry.StartKey](#linegeometry-startkey)
  * 15.6 [LineGeometry.TypeName](#linegeometry-typename)
  * 15.7 [LineGeometry.\_\_repr\_\_](#linegeometry---repr--)
  * 15.8 [LineGeometry.\_\_str\_\_](#linegeometry---str--)
  * 15.9 [LineGeometry.get\_begin\_pair](#linegeometry-get-begin-pair)
  * 15.10 [LineGeometry.get\_begin\_point](#linegeometry-get-begin-point)
  * 15.11 [LineGeometry.get\_center\_pair](#linegeometry-get-center-pair)
  * 15.12 [LineGeometry.get\_end\_pair](#linegeometry-get-end-pair)
  * 15.13 [LineGeometry.get\_end\_point](#linegeometry-get-end-point)
  * 15.14 [LineGeometry.get\_part\_geometry](#linegeometry-get-part-geometry)
* 16 [Class PointGeometry](#pointgeometry)
  * 16.1 [PointGeometry.get\_center\_pair](#pointgeometry-get-center-pair)
  * 16.2 [PointGeometry.part\_geometry](#pointgeometry-part-geometry)
  * 16.3 [PointGeometry.type\_name](#pointgeometry-type-name)
* 17 [Class \_InternalCircle](#-internalcircle)
* 18 [Class \_InternalPolygon](#-internalpolygon)

## 1 <a name="introduction"></a>Introduction


This module provides an interface that both creates FreeCAD sketches and applies those sketches
to FreeCAD Part Design workbench Body objects.  Additional sketch information is also provided to
supporting the FreeCAD Path workbench.

The are 3 base classes of used in this module:
* ApexDrawing: Create one or more FreeCAD Sketches and apply Part Design and Path operations.
* ApexOperation: This base class encapsulates the Part Design and Path operation information.
* ApexShape: This class class provides geometric shapes that go into the ApexDrawing.
* Geometry: The internal base class represents 2D geometric constructs (point, line, arc, circle).
ApexShape is the user facing class for point/line/arc/circle and it gets converted into lower
level Geometry objects that are 1-to-1 with FreeCAD data structures.

There is a rich set of FreeCAD PartDesign operations that can be applied to sketches.
The construction operations are pad, revolve, loft, sweep and helix and
the subtraction operations are pocket, hole, groove, loft, sweep and helix.
Currently, only a small subset of these operations are supported with ApexOperation sub-classes:
* ApexPad: Performs a FreeCAD Part Design pad operation.
* ApexPocket: Performs a FreeCAD Part Design pocket operation
* ApexHole: Performs a FreeCAD Part Design pocket operation
Each of these operations takes either an ApexCircle or an ApexPolygon as an argument.
Over time, the supported operations will be expanded.

The ApexShape sub-classes are:
* ApexCircle: This represents a circle in the ApexDrawing.
* ApexPolygon: This is basically a sequence of ApexCorner's (see below) that represent a polygon,
  where each corner can optionally have rounded with a fillet.
* ApexCorner: This represents one corner of an ApexPolygon and specifies the fillet radius.

The internal Geometry sub-classes are:
* PointGeometry: This represents a single point geometry.
* LineGeometry: This represents a line segment geometry.
* ArcGeometry: This represents an arc on a circle geometry.
* CircleGeometry This represents a circle geometry.
These classes are for internal use only.

All of this information is collected into an ApexDrawing instance.
The ApexDrawing.body_apply() takes a FreeCAD Part Design Body and applies operations drawing to it.

## 2 Class ApexCircle <a name="apexcircle"></a>

class ApexCircle(ApexShape):

ApexCircle: Represents a circle.

Usage: ApexCircle(center, diameter, name)

Attributes:
* *Center* (Vector): The center of the circle.
* *Diameter* (float): Circle diameter in millimeters
* *Name* (str):  Name of circle.  (Default: "")
* *Box* (ApexBox): ApexBox that encloses ApexCircle as if it is a sphere.
* *\_internal\_circle* (\_InternalCircle): Internal private/mutatable data.


### 2.1 ApexCircle.\_\_post\_init <a name="apexcircle---post-init"></a>

def \_\_post\_init\_\_(self) -> None:

Initialize a circle.

### 2.2 ApexCircle.get\_constraints <a name="apexcircle-get-constraints"></a>

def *get\_constraints*(self, *origin\_point*:  PointGeometry, *tracing*:  *str* = "") -> Tuple[Sketcher.Constraint, ...]:

Return the CircleGeometry constraints.

Arguments:
* *origin\_point* (PointGeometry): The origin to use.


### 2.3 ApexCircle.get\_geometries <a name="apexcircle-get-geometries"></a>

def *get\_geometries*(self, *tracing*:  *str* = "") -> Tuple[Geometry, ...]:

Return the CircleGeometry.

### 2.4 ApexCircle.reorient <a name="apexcircle-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  Optional[str] = "", *tracing*:  *str* = "") -> "ApexCircle":

Return a new reoriented ApexCircle.

Arguments:
* *placement* (Placement): The FreeCAD Placement reorient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")


## 3 Class ApexCorner <a name="apexcorner"></a>

class ApexCorner(object):

ApexCorner: An ApexPolygon corner with a radius.

Usage: ApexCorner(point, radius, name)

Attributes:
* *Point* (Vector): A point for a polygon.
* *Radius (float): The corner radius in millimeters.  (Default: 0.0)
* *Name* (str): The corner name. (Default: "")


### 3.1 ApexCorner.\_\_post\_init\_\_ <a name="apexcorner---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify contents of ApexCorner.

### 3.2 ApexCorner.\_unit\_tests <a name="apexcorner--unit-tests"></a>

def \_unit\_tests() -> None:

Run unit tests for ApexCorner.

## 4 Class ApexDrawing <a name="apexdrawing"></a>

class ApexDrawing(object):

ApexDrawing: Used to create fully constrained 2D drawings.

Usage: ApexDrawing(contact, normal, operations, name)

Attributes:
* *Contact*: (Vector): On point on the surface of the polygon.
* *Normal*: (Vector): A normal to the polygon plane.
* *Operations* (Tuple[ApexOperation, ...]): Operations to perform on drawing.
* *Name* (str): The ApexDrawing name. (Default: "")
* *Box* (ApexBox): A computed ApexBox that encloses all of the operations.


### 4.1 ApexDrawing.\_\_post\_init\_\_ <a name="apexdrawing---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Initialize a drawing.

### 4.2 ApexDrawing.create\_datum\_plane <a name="apexdrawing-create-datum-plane"></a>

def *create\_datum\_plane*(self, *body*:  "PartDesign.Body", *name*:  Optional[str] = None, *tracing*:  *str* = "") -> "Part.Geometry":

Return the FreeCAD DatumPlane used for the drawing.

Arguments:
* *body* (PartDesign.Body): The FreeCAD Part design Body to attach the datum plane to.
* *name* (Optional[str]): The datum plane name.
  (Default: "...DatumPlaneN", where N is incremented.)
* Returns:
  * (Part.Geometry) that is the datum\_plane.

### 4.3 ApexDrawing.get\_geometries <a name="apexdrawing-get-geometries"></a>

def *point\_get\_geometries*(self, *point*:  Vector, *tracing*:  *str* = "") -> Tuple["Geometry", ...]:

Return the PointGeometry Geometry's.

### 4.4 ApexDrawing.get\_origin\_constraints <a name="apexdrawing-get-origin-constraints"></a>

def *get\_origin\_constraints*(self, *origin\_point*:  PointGeometry, *tracing*:  *str* = "") -> Tuple[Sketcher.Constraint, ...]:

Return constraints associated for the origin point.

Arguments:
* *origin\_point* (PointGeometry): The origin point to constrain.

### 4.5 ApexDrawing.plane\_process <a name="apexdrawing-plane-process"></a>

def *plane\_process*(self, *body*:  "PartDesign.Body", *document\_name*:  *str*, *tracing*:  *str* = "") -> None:

Plane\_Process.

### 4.6 ApexDrawing.reorient <a name="apexdrawing-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  Optional[str] = "", *tracing*:  *str* = "") -> "ApexDrawing":

Return a reoriented ApexDrawing.

Arguments:
* *placement* (Placement): The Placement to apply ApexCircle's and ApexPolygon's.
* *suffix* (Optional[str]): The suffix to append at all names.  If None, all
  names are set to "" instead appending the suffix.  (Default: "")


### 4.7 ApexDrawing.sketch <a name="apexdrawing-sketch"></a>

def *sketch*(self, *sketcher*:  Part.Part2DObject, *document\_name*:  *str*, *tracing*:  *str* = "") -> None:

Insert an ApexDrawing into a FreeCAD SketchObject.

Arguments:
* sketcher (Sketcher.SketchObject): The sketcher object to use.

## 5 Class ApexHole <a name="apexhole"></a>

class ApexHole(ApexOperation):

ApexHole represents a FreeCAD Part Design workbench Hole operation.

Usage: ApexHole(circle, depth, name)

Attributes:
* *Circle: (ApexCircle): The ApexCircle for the hole.
* *Depth* (float): The hole depth in millimeters.
* *Name* (str): The name of the operation.  (Default: "")
* *SortKey* (Tuple[str, ...]): A generated sorting key used to sort ApexOperation's.


### 5.1 ApexHole.\_\_post\_init\_\_ <a name="apexhole---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify argument types.

### 5.2 ApexHole.body\_apply <a name="apexhole-body-apply"></a>

def *body\_apply*(self, *body*:  "PartDesign.Body", *group\_name*:  *str*, *part2d*:  Part.Part2DObject, *gui\_document*:  Optional["Gui.ActiveDocument"], *tracing*:  *str* = "") -> None:

Apply hole operation to PartDesign body.

### 5.3 ApexHole.get\_shape <a name="apexhole-get-shape"></a>

def *get\_shape*(self) -> ApexShape:

Return the ApexHole ApexShape.

### 5.4 ApexHole.reorient <a name="apexhole-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  *str* = None, *tracing*:  *str* = "") -> "ApexHole":

Reorient an ApexHole.

Arguments:
* *placement* (Placement): The FreeCAD Placement to reorient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")


## 6 Class ApexOperation <a name="apexoperation"></a>

class ApexOperation(object):

Represents a FreeCAD Part Design workbench operation.

This is a base class for ApexHole, ApexPad, and ApexPocket.

Attributes:
* *SortKey*: (Tuple[str, ...]): A key generated by sub-class used to sort ApexOpertions.


### 6.1 ApexOperation.body\_apply <a name="apexoperation-body-apply"></a>

def *body\_apply*(self, *body*:  "PartDesign.Body", *group\_name*:  *str*, *part2d*:  Part.Part2DObject, *gui\_document*:  Optional["Gui.ActiveDocument"], *tracing*:  *str* = "") -> None:

Apply operation to a Part Design body.

### 6.2 ApexOperation.get\_constraints <a name="apexoperation-get-constraints"></a>

def *get\_constraints*(self, *origin\_point*:  PointGeometry, *tracing*:  *str* = "") -> Tuple[Sketcher.Constraint, ...]:

Return ApexOperation constraints.

Arguments:
* *origin\_point* (PointGeometry): The PointGeometry to use for the origin.


### 6.3 ApexOperation.get\_geometries <a name="apexoperation-get-geometries"></a>

def *get\_geometries*(self, *tracing*:  *str* = "") -> Tuple[Geometry, ...]:

Return the geometries associated with an operation.

### 6.4 ApexOperation.get\_shape <a name="apexoperation-get-shape"></a>

def *get\_shape*(self) -> ApexShape:

Return the associated ApexOperation ApexShape.

### 6.5 ApexOperation.reorient <a name="apexoperation-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  *str* = None, *tracing*:  *str* = "") -> "ApexOperation":

Reorient an operation.

Arguments:
* *placement* (Placement): The FreeCAD Placement reorient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")


### 6.6 ApexOperation.show <a name="apexoperation-show"></a>

def *show*(self) -> *str*:

Return a string that shows operation.

## 7 Class ApexPad <a name="apexpad"></a>

class ApexPad(ApexOperation):

ApexPad represents a FreeCAD Part Design workbench Pad operation.

Attributes:
* *Shape* (ApexShape): The ApexCircle/ApexPolygon to use for padding.
* *Depth* (float): The depth of the pad operation.
* *Name* (str): The name of the operation.  (Default: "")
* *SortKey* (Tuple[str, ...]): A generated sorting key used to sort ApexOperation's.

Usage: ApexPad(circle\_or\_pologon, depth, name)


### 7.1 ApexPad.\_\_post\_init\_\_ <a name="apexpad---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify argument types.

### 7.2 ApexPad.body\_apply <a name="apexpad-body-apply"></a>

def *body\_apply*(self, *body*:  "PartDesign.Body", *group\_name*:  *str*, *part2d*:  Part.Part2DObject, *gui\_document*:  Optional["Gui.ActiveDocument"], *tracing*:  *str* = "") -> None:

Apply ApexPad opertation to PartDesign Body.

### 7.3 ApexPad.get\_shape <a name="apexpad-get-shape"></a>

def *get\_shape*(self) -> ApexShape:

Return the associated ApexShape's.

### 7.4 ApexPad.reorient <a name="apexpad-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  *str* = None, *tracing*:  *str* = "") -> "ApexPad":

Reorient an ApexPad .

Arguments:
* *placement* (Placement): The FreeCAD Placement reorient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")


## 8 Class ApexPocket <a name="apexpocket"></a>

class ApexPocket(ApexOperation):

ApexPocket represents a FreeCAD Part Design workbench Pad operation.

Usage: ApexPad(circle\_or\_polygon, depth, name)

Attributes:
* *Shape* (ApexShape): The ApexCircle/ApexPolygon to use for the pocket operation.
* *Depth* (float): The depth of the pocke operation.
* *Name* (str): The name of the operation.  (Default: "")
* *SortKey* (Tuple[str, ...]): A generated sorting key used to sort ApexOperations.


### 8.1 ApexPocket.\_\_post\_init\_\_ <a name="apexpocket---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify argument types.

### 8.2 ApexPocket.body\_apply <a name="apexpocket-body-apply"></a>

def *body\_apply*(self, *body*:  "PartDesign.Body", *group\_name*:  *str*, *part2d*:  Part.Part2DObject, *gui\_document*:  Optional["Gui.ActiveDocument"], *tracing*:  *str* = "") -> None:

Apply pocket operation to PartDesign Body.

### 8.3 ApexPocket.get\_shape <a name="apexpocket-get-shape"></a>

def *get\_shape*(self) -> ApexShape:

Return the ApexPad ApexShape.

### 8.4 ApexPocket.reorient <a name="apexpocket-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  *str* = None, *tracing*:  *str* = "") -> "ApexPocket":

Reorient an ApexPocket .

Arguments:
* *placement* (Placement): The FreeCAD Placement reorient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")


## 9 Class ApexPolygon <a name="apexpolygon"></a>

class ApexPolygon(ApexShape):

ApexPolyon: A closed polygon of Vectors.

Usage: ApexPolygon(corners, name)

Attributes:
* *Corners* (Tuple[ApexCorner, ...]): The ApexCorner's of the ApexPoloygon.
* *Name* (str): The ApexPolygon name.  (Default: "")
* *Box* (ApexBox): An ApexBox that encloses all of the Corners.
* *Clockwise* (bool): Computed to be True when the Corners are in clockwise order.
* *InternalRadius* (float): The computed minimum radius for internal corners in millimeters.
* *\_internal\_polygon* (\_InternalPolygon): Internal (mutable) ApexPolygon data structures.


### 9.1 ApexPolygon.\_\_post\_init\_\_ <a name="apexpolygon---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Initialize a ApexPolygon.

### 9.2 ApexPolygon.\_arcs\_create <a name="apexpolygon--arcs-create"></a>

def \_arcs\_create(self, *tracing*:  *str* = "") -> None:

Create all of the needed ArcGeometry's.

### 9.3 ApexPolygon.\_get\_constraints <a name="apexpolygon--get-constraints"></a>

def \_get\_constraints(self, *origin\_point*:  PointGeometry, *tracing*:  *str* = "") -> Tuple[Sketcher.Constraint, ...]:

Return the constraints for an ApexPolygon.

Arguments:
* *origin\_point* (PointGeometry): The origin to use.


### 9.4 ApexPolygon.\_get\_geometries <a name="apexpolygon--get-geometries"></a>

def \_get\_geometries(self, *tracing*:  *str* = "") -> Tuple[Geometry, ...]:

Return the ApexPolygon Geometry's.

### 9.5 ApexPolygon.\_get\_wire <a name="apexpolygon--get-wire"></a>

def \_get\_wire(self, *tracing*:  *str* = "") -> Part.Wire:

Return the wire formed by ApexPolygon.

### 9.6 ApexPolygon.\_lines\_create <a name="apexpolygon--lines-create"></a>

def \_lines\_create(self, *tracing*:  *str* = "") -> None:

Create all of the needed LineGemomety's.

### 9.7 ApexPolygon.\_radii\_overlap\_check <a name="apexpolygon--radii-overlap-check"></a>

def \_radii\_overlap\_check(self) -> None:

Verify that the corner radii do not overlap.

### 9.8 ApexPolygon.\_unit\_tests <a name="apexpolygon--unit-tests"></a>

def \_unit\_tests() -> None:

Run ApexPolygon unit tests.

### 9.9 ApexPolygon.get\_box <a name="apexpolygon-get-box"></a>

def *get\_box*(self) -> ApexBox:

Return the ApexBox for an ApexPolygon.

### 9.10 ApexPolygon.get\_constraints <a name="apexpolygon-get-constraints"></a>

def *get\_constraints*(self, *origin\_point*:  PointGeometry, *tracing*:  *str* = "") -> Tuple[Sketcher.Constraint, ...]:

Return the constraints for an ApexPolygon.

Arguments:
* *origin\_point* (PointGeometry): The origin to use.


### 9.11 ApexPolygon.get\_geometries <a name="apexpolygon-get-geometries"></a>

def *get\_geometries*(self, *tracing*:  *str* = "") -> Tuple[Geometry, ...]:

Return the ApexPolygon ApexGeometries tuple.

### 9.12 ApexPolygon.reorient <a name="apexpolygon-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  Optional[str] = "", *tracing*:  *str* = "") -> "ApexPolygon":

Reorient an ApexPolygon with a new Placement.

Arguments:
* *placement* (Placement):
  The FreeCAD Placement to reorient with.
* *suffix* (Optional[str]):
  A suffix to append to the name.  If None, an empty name is used. (Default: "")


### 9.13 ApexPolygon.show <a name="apexpolygon-show"></a>

def *show*(self) -> *str*:

Return compact string showing ApexPolygon contents.

## 10 Class ApexShape <a name="apexshape"></a>

class ApexShape(object):

ApexShape: Is a base class for geometric shapes (e.g. ApexPolygon, etc).

ApexShape is a base class for the various geometric shapes.  See sub-classes for attributes.

### 10.1 ApexShape.\_get\_constraints <a name="apexshape--get-constraints"></a>

def \_get\_constraints(self, *origin\_point*:  PointGeometry, *tracing*:  *str* = "") -> Tuple[Sketcher.Constraint, ...]:

Return The contstraints for an ApexShape.

Arguments:
* *origin\_point* (PointGeometry): The PointGeometry to used for the origin.


### 10.2 ApexShape.\_get\_wire <a name="apexshape--get-wire"></a>

def \_get\_wire(self, *tracing*:  *str* = "") -> Part.Wire:

Return wire.

### 10.3 ApexShape.get\_box <a name="apexshape-get-box"></a>

def *get\_box*(self) -> ApexBox:

Return ApexBox that enclose the ApexShape.

### 10.4 ApexShape.get\_constraints <a name="apexshape-get-constraints"></a>

def *get\_constraints*(self, *origin\_point*:  PointGeometry, *tracing*:  *str* = "") -> Tuple[Sketcher.Constraint, ...]:

Return The contstraints for an ApexShape.

Arguments:
* *origin\_point* (PointGeometry): The PointGeometry to used for the origin.


### 10.5 ApexShape.get\_geometries <a name="apexshape-get-geometries"></a>

def *get\_geometries*(self, *tracing*:  *str* = "") -> Tuple[Geometry, ...]:

Return the ApexShape ApexGeometries tuple.

Returns:
* (Tuple[Geometry, ...]) of extracted Geometry's.


### 10.6 ApexShape.reorient <a name="apexshape-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  Optional[str] = "", *tracing*:  *str* = "") -> "ApexShape":

Return a new reoriented ApexCircle.

Arguments:
* *placement* (Placement): The FreeCAD Placement to reorient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")

# Returns:
* (ApexShape) that has been reoriented with a new name.

### 10.7 ApexShape.show <a name="apexshape-show"></a>

def *show*(self) -> *str*:

Return compact string for ApexShape.

## 11 Class ArcGeometry <a name="arcgeometry"></a>

class ArcGeometry(Geometry):

Represents an an arc in a sketch.

### 11.1 ArcGeometry.Finish <a name="arcgeometry-finish"></a>

def Finish(self) -> Vector:

Return the ArcGeometry arc finish Vector.

### 11.2 ArcGeometry.FinishKey <a name="arcgeometry-finishkey"></a>

def FinishKey(self) -> *int*:

Return the ArcGeometry finish Constraint key.

### 11.3 ArcGeometry.Radius <a name="arcgeometry-radius"></a>

def Radius(self) -> *float*:

Return the initial ArcGeometry radius.

### 11.4 ArcGeometry.Start <a name="arcgeometry-start"></a>

def Start(self) -> Vector:

Return the ArcGeometry arc start Vector.

### 11.5 ArcGeometry.StartKey <a name="arcgeometry-startkey"></a>

def StartKey(self) -> *int*:

Return the ArcGeometry finish Constraint key.

### 11.6 ArcGeometry.TypeName <a name="arcgeometry-typename"></a>

def TypeName(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ArcGeometry type name.

### 11.7 ArcGeometry.\_\_init\_\_ <a name="arcgeometry---init--"></a>

def \_\_init\_\_(self, *begin*:  ApexCorner, *at*:  ApexCorner, *end*:  ApexCorner, *name*:  *str* = "", *tracing*:  *str* = "") -> None:

Initialize an ArcGeometry.

### 11.8 ArcGeometry.\_\_str\_\_ <a name="arcgeometry---str--"></a>

def \_\_str\_\_(self) -> *str*:

Return string representation of Geometry.

### 11.9 ArcGeometry.apex <a name="arcgeometry-apex"></a>

def *at*(self) -> Vector:

Return the ArcGeometry apex Vector.

### 11.10 ArcGeometry.begin <a name="arcgeometry-begin"></a>

def *begin*(self) -> Vector:  # *pragma*:  *no* *unit* *test*

Return the ArcGeometry arc begin Vector.

### 11.11 ArcGeometry.center <a name="arcgeometry-center"></a>

def *center*(self) -> Vector:

Return the ArcGeometry arc center.

### 11.12 ArcGeometry.end <a name="arcgeometry-end"></a>

def *end*(self) -> Vector:  # *pragma*:  *no* *unit* *test*

Return the initial ArcGeometry end Vector.

### 11.13 ArcGeometry.finish\_angle <a name="arcgeometry-finish-angle"></a>

def *finish\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ArcGeometry arc finish angle.

### 11.14 ArcGeometry.finish\_length <a name="arcgeometry-finish-length"></a>

def *finish\_length*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return distance from arc finish Vector to the apex Vector.

### 11.15 ArcGeometry.get\_begin\_pair <a name="arcgeometry-get-begin-pair"></a>

def *get\_begin\_pair*(self) -> Tuple[int, *int*]:

Return the ArcGeometry begin pair.

### 11.16 ArcGeometry.get\_begin\_point <a name="arcgeometry-get-begin-point"></a>

def *get\_begin\_point*(self) -> Vector:

Return the ArcGeometry begin point.

### 11.17 ArcGeometry.get\_center\_pair <a name="arcgeometry-get-center-pair"></a>

def *get\_center\_pair*(self) -> Tuple[int, *int*]:

Return the ArcGeometry center pair.

### 11.18 ArcGeometry.get\_end\_pair <a name="arcgeometry-get-end-pair"></a>

def *get\_end\_pair*(self) -> Vector:

Return the ArcGGeometry end point.

### 11.19 ArcGeometry.get\_end\_point <a name="arcgeometry-get-end-point"></a>

def *get\_end\_point*(self) -> Vector:

Return the ArcGGeometry end point.

### 11.20 ArcGeometry.input <a name="arcgeometry-input"></a>

def *input*(self) -> Vector:  # *pragma*:  *no* *unit* *test*

Return the initial ArcGeometry arc start Vector.

### 11.21 ArcGeometry.name <a name="arcgeometry-name"></a>

def Name(self) -> *str*:

Return name.

### 11.22 ArcGeometry.part\_geometry <a name="arcgeometry-part-geometry"></a>

def *get\_part\_geometry*(self) -> PartGeometryUnion:

Return ArcGeometry Part.Arc.

### 11.23 ArcGeometry.start\_angle <a name="arcgeometry-start-angle"></a>

def *start\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ArcGeometry arc start angle.

### 11.24 ArcGeometry.start\_length <a name="arcgeometry-start-length"></a>

def *start\_length*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ArcGeometry distance from start Vector to apex Vector.

### 11.25 ArcGeometry.sweep\_angle <a name="arcgeometry-sweep-angle"></a>

def *sweep\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *cover*

Return the ArcGeometry sweep angle from start angle to end angle.

## 12 Class CircleGeometry <a name="circlegeometry"></a>

class CircleGeometry(Geometry):

Represents a circle in a sketch.

### 12.1 CircleGeometry.get\_part\_geometry <a name="circlegeometry-get-part-geometry"></a>

def *get\_part\_geometry*(self) -> PartGeometryUnion:

Return the PartGeometry.

### 12.2 CircleGeometry.type\_name <a name="circlegeometry-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the CircleGeometry type name.

## 13 Class Corner <a name="corner"></a>

class Corner(object):

Corner: An internal mutable class that corresponds to an ApexCorner.

### 13.1 Corner.\_\_post\_init\_\_ <a name="corner---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Initialize contents of Corner.

### 13.2 Corner.\_get\_end\_point <a name="corner--get-end-point"></a>

def \_get\_end\_point(self) -> Vector:

Return Corner end point.

### 13.3 Corner.\_get\_start\_point <a name="corner--get-start-point"></a>

def \_get\_start\_point(self) -> Vector:

Return Corner end point.

### 13.4 Corner.foo <a name="corner-foo"></a>

def *foo*(before:  Vector, *apex*:  Vector, *after*:  Vector, *radius*:  *float*, *tracing*:  *str* = "") -> Tuple[Vector, Vector, Vector]:

Generate the arc for a corner.

### 13.5 Corner.get\_begin\_point <a name="corner-get-begin-point"></a>

def *get\_begin\_point*(self) -> Vector:

Return the Corner beginning point.

### 13.6 Corner.get\_constraints <a name="corner-get-constraints"></a>

def *get\_constraints*(self, *origin\_point*:  PointGeometry, *tracing*:  *str* = "") -> Tuple[Sketcher.Constraint, ...]:

Return the Corner sketch constraints.

### 13.7 Corner.get\_end\_point <a name="corner-get-end-point"></a>

def *get\_end\_point*(self) -> Vector:

Return the Corner ending point.

### 13.8 Corner.get\_first\_geometry <a name="corner-get-first-geometry"></a>

def *get\_first\_geometry*(self) -> Geometry:

Return the last Geometry in Corner.

### 13.9 Corner.get\_geometries <a name="corner-get-geometries"></a>

def *get\_geometries*(self) -> Tuple[Geometry, ...]:

Return the Corner Geometry's.

### 13.10 Corner.get\_last\_geometry <a name="corner-get-last-geometry"></a>

def *get\_last\_geometry*(self) -> Geometry:

Return the last Geometry in Corner.

## 14 Class Geometry <a name="geometry"></a>

class Geometry(object):

Geometry: Internal Base class for 2D geometry objects.

This is basically a wrapper around the arguments need to create Sketch elements.
It is mutable and always contains a bunch of helper functions.

### 14.1 Geometry.Finish <a name="geometry-finish"></a>

def Finish(self) -> Vector:  # *pragma*:  *no* *unit* *test*

Return the Geometry finish point.

### 14.2 Geometry.FinishKey <a name="geometry-finishkey"></a>

def FinishKey(self) -> *int*:  # *pragma*:  *no* *unit* *test*

Return the Geometry Constraint key for the finish point.

### 14.3 Geometry.Ind <a name="geometry-index"></a>

def Index(self) -> *int*:

Return the Geometry index.

### 14.4 Geometry.Name <a name="geometry-name"></a>

def Name(self) -> *str*:

Return Geometry Name.

### 14.5 Geometry.Start <a name="geometry-start"></a>

def Start(self) -> Vector:  # *pragma*:  *no* *unit* *test*

Return the Geometry start point.

### 14.6 Geometry.StartKey <a name="geometry-startkey"></a>

def StartKey(self) -> *int*:

Return the Geometry Constraint key for the start point.

### 14.7 Geometry.TypeNa <a name="geometry-typename"></a>

def TypeName(self) -> *str*:

Return the Geometry type name.

### 14.8 Geometry.get\_begin\_pair <a name="geometry-get-begin-pair"></a>

def *get\_begin\_pair*(self) -> Tuple[int, *int*]:

Return the Geometry index/start key pair.

### 14.9 Geometry.get\_begin\_point <a name="geometry-get-begin-point"></a>

def *get\_begin\_point*(self) -> Vector:

Return start location of Geometry.

### 14.10 Geometry.get\_center\_pair <a name="geometry-get-center-pair"></a>

def *get\_center\_pair*(self) -> Tuple[int, *int*]:

Return the Geometry index/center key pair.

### 14.11 Geometry.get\_constraints <a name="geometry-get-constraints"></a>

def *get\_constraints*(self, *origin\_point*:  "PointGeometry", *tracing*:  *str* = "") -> Tuple[Sketcher.Constraint, ...]:

Return the constraints associated with the Geometry.

Arguments:
* *origin\_point* (PointGeometry): The PointGeometry to use for the origin

Returns the assoicated contraints as a tuple.

### 14.12 Geometry.get\_end\_pair <a name="geometry-get-end-pair"></a>

def *get\_end\_pair*(self) -> Tuple[int, *int*]:

Return the Geometry index/start key pair.

### 14.13 Geometry.get\_end\_point <a name="geometry-get-end-point"></a>

def *get\_end\_point*(self) -> Vector:

Return starting location of Geometry.

### 14.14 Geometry.get\_part\_geometry <a name="geometry-get-part-geometry"></a>

def *get\_part\_geometry*(self) -> PartGeometryUnion:

Return the PartGeometry associated with Geometry.

## 15 Class LineGeometry <a name="linegeometry"></a>

class LineGeometry(Geometry):

Represents a line segment in a sketch.

### 15.1 LineGeometry.Finish <a name="linegeometry-finish"></a>

def Finish(self) -> Vector:  # *pragma*:  *no* *unit* *cover*

Return the LineGeometry finish Vector.

### 15.2 LineGeometry.FinishKey <a name="linegeometry-finishkey"></a>

def FinishKey(self) -> *int*:

Return the LineGeometry finish Constraint key.

### 15.3 LineGeometry.Name <a name="linegeometry-name"></a>

def Name(self) -> *str*:

Return name.

### 15.4 LineGeometry.Start <a name="linegeometry-start"></a>

def Start(self) -> ApexCorner:

Return the LineGeometry start Vector.

### 15.5 LineGeometry.StartKey <a name="linegeometry-startkey"></a>

def StartKey(self) -> *int*:

Return the LineGeometry start Constraint key.

### 15.6 LineGeometry.TypeName <a name="linegeometry-typename"></a>

def TypeName(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the LineGeometry type name.

### 15.7 LineGeometry.\_\_repr\_\_ <a name="linegeometry---repr--"></a>

def \_\_repr\_\_(self) -> *str*:

Return string representation of LineGeometry.

### 15.8 LineGeometry.\_\_str\_\_ <a name="linegeometry---str--"></a>

def \_\_str\_\_(self) -> *str*:

Return string representation of LineGeometry.

### 15.9 LineGeometry.get\_begin\_pair <a name="linegeometry-get-begin-pair"></a>

def *get\_begin\_pair*(self) -> Tuple[int, *int*]:

Return the LineGeometry start location.

### 15.10 LineGeometry.get\_begin\_point <a name="linegeometry-get-begin-point"></a>

def *get\_begin\_point*(self) -> Vector:

Return the LineGeometry start location.

### 15.11 LineGeometry.get\_center\_pair <a name="linegeometry-get-center-pair"></a>

def *get\_center\_pair*(self) -> Tuple[int, *int*]:

Return index/key for line start.

### 15.12 LineGeometry.get\_end\_pair <a name="linegeometry-get-end-pair"></a>

def *get\_end\_pair*(self) -> Tuple[int, *int*]:

Return index/key for line start.

### 15.13 LineGeometry.get\_end\_point <a name="linegeometry-get-end-point"></a>

def *get\_end\_point*(self) -> Vector:

Return the LineGeometry start location.

### 15.14 LineGeometry.get\_part\_geometry <a name="linegeometry-get-part-geometry"></a>

def *get\_part\_geometry*(self) -> PartGeometryUnion:

Return the PartGeometry associated with a LineGeometry.

## 16 Class PointGeometry <a name="pointgeometry"></a>

class PointGeometry(Geometry):

Represents a point in a sketch.

### 16.1 PointGeometry.get\_center\_pair <a name="pointgeometry-get-center-pair"></a>

def *get\_center\_pair*(self) -> Tuple[int, *int*]:

Return the PointGeometry center pair.

### 16.2 PointGeometry.part\_geometry <a name="pointgeometry-part-geometry"></a>

def *get\_part\_geometry*(self) -> PartGeometryUnion:

Return the  PointGeometry.

### 16.3 PointGeometry.type\_name <a name="pointgeometry-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the PointGeometry type name.

## 17 Class \_InternalCircle <a name="-internalcircle"></a>

class \_InternalCircle(object):

InternalCircle: Internal (private/mutable) data structures for an ApexCircle.

## 18 Class \_InternalPolygon <a name="-internalpolygon"></a>

class \_InternalPolygon(object):

InternalPolygon: A place to store mutable data structures needed for ApexPolygon.
