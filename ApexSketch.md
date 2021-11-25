# ApexSketch: An interface to FreeCAD Sketches.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class ApexArcGeometry](#apexarcgeometry)
  * 2.1 [ApexArcGeometry.\_\_init\_\_](#apexarcgeometry---init--)
  * 2.2 [ApexArcGeometry.\_\_str\_\_](#apexarcgeometry---str--)
  * 2.3 [ApexArcGeometry.apex](#apexarcgeometry-apex)
  * 2.4 [ApexArcGeometry.begin](#apexarcgeometry-begin)
  * 2.5 [ApexArcGeometry.center](#apexarcgeometry-center)
  * 2.6 [ApexArcGeometry.end](#apexarcgeometry-end)
  * 2.7 [ApexArcGeometry.finish](#apexarcgeometry-finish)
  * 2.8 [ApexArcGeometry.finish\_angle](#apexarcgeometry-finish-angle)
  * 2.9 [ApexArcGeometry.finish\_key](#apexarcgeometry-finish-key)
  * 2.10 [ApexArcGeometry.finish\_length](#apexarcgeometry-finish-length)
  * 2.11 [ApexArcGeometry.input](#apexarcgeometry-input)
  * 2.12 [ApexArcGeometry.part\_geometry](#apexarcgeometry-part-geometry)
  * 2.13 [ApexArcGeometry.radius](#apexarcgeometry-radius)
  * 2.14 [ApexArcGeometry.repr](#apexarcgeometry-repr)
  * 2.15 [ApexArcGeometry.start](#apexarcgeometry-start)
  * 2.16 [ApexArcGeometry.start\_angle](#apexarcgeometry-start-angle)
  * 2.17 [ApexArcGeometry.start\_key](#apexarcgeometry-start-key)
  * 2.18 [ApexArcGeometry.start\_length](#apexarcgeometry-start-length)
  * 2.19 [ApexArcGeometry.sweep\_angle](#apexarcgeometry-sweep-angle)
  * 2.20 [ApexArcGeometry.type\_name](#apexarcgeometry-type-name)
* 3 [Class ApexCircle](#apexcircle)
  * 3.1 [ApexCircle.\_\_post\_init](#apexcircle---post-init)
  * 3.2 [ApexCircle.constraints\_append](#apexcircle-constraints-append)
  * 3.3 [ApexCircle.geometries\_get](#apexcircle-geometries-get)
  * 3.4 [ApexCircle.reorient](#apexcircle-reorient)
* 4 [Class ApexCircleGeometry](#apexcirclegeometry)
  * 4.1 [ApexCircleGeometry.\_\_init\_\_](#apexcirclegeometry---init--)
  * 4.2 [ApexCircleGeometry.\_\_repr\_\_](#apexcirclegeometry---repr--)
  * 4.3 [ApexCircleGeometry.\_\_str\_\_](#apexcirclegeometry---str--)
  * 4.4 [ApexCircleGeometry.center](#apexcirclegeometry-center)
  * 4.5 [ApexCircleGeometry.part\_element](#apexcirclegeometry-part-element)
  * 4.6 [ApexCircleGeometry.radius](#apexcirclegeometry-radius)
  * 4.7 [ApexCircleGeometry.type\_name](#apexcirclegeometry-type-name)
* 5 [Class ApexCorner](#apexcorner)
  * 5.1 [ApexCorner.\_\_post\_init\_\_](#apexcorner---post-init--)
  * 5.2 [ApexCorner.\_\_repr\_\_](#apexcorner---repr--)
  * 5.3 [ApexCorner.\_\_str\_\_](#apexcorner---str--)
  * 5.4 [ApexCorner.\_unit\_tests](#apexcorner--unit-tests)
* 6 [Class ApexDrawing](#apexdrawing)
  * 6.1 [ApexDrawing.\_\_post\_init\_\_](#apexdrawing---post-init--)
  * 6.2 [ApexDrawing.create\_datum\_plane](#apexdrawing-create-datum-plane)
  * 6.3 [ApexDrawing.geometries\_get](#apexdrawing-geometries-get)
  * 6.4 [ApexDrawing.plane\_process](#apexdrawing-plane-process)
  * 6.5 [ApexDrawing.point\_constraints\_append](#apexdrawing-point-constraints-append)
  * 6.6 [ApexDrawing.reorient](#apexdrawing-reorient)
  * 6.7 [ApexDrawing.sketch](#apexdrawing-sketch)
* 7 [Class ApexGeometry](#apexgeometry)
  * 7.1 [ApexGeometry.\_\_init\_\_](#apexgeometry---init--)
  * 7.2 [ApexGeometry.constraints\_append](#apexgeometry-constraints-append)
  * 7.3 [ApexGeometry.drawing](#apexgeometry-drawing)
  * 7.4 [ApexGeometry.finish](#apexgeometry-finish)
  * 7.5 [ApexGeometry.index](#apexgeometry-index)
  * 7.6 [ApexGeometry.name](#apexgeometry-name)
  * 7.7 [ApexGeometry.part\_geometry](#apexgeometry-part-geometry)
  * 7.8 [ApexGeometry.previous](#apexgeometry-previous)
  * 7.9 [ApexGeometry.start](#apexgeometry-start)
  * 7.10 [ApexGeometry.type\_name](#apexgeometry-type-name)
* 8 [Class ApexHole](#apexhole)
  * 8.1 [ApexHole.\_\_post\_init\_\_](#apexhole---post-init--)
  * 8.2 [ApexHole.body\_apply](#apexhole-body-apply)
  * 8.3 [ApexHole.reorient](#apexhole-reorient)
  * 8.4 [ApexHole.shape\_get](#apexhole-shape-get)
* 9 [Class ApexLineGeometry](#apexlinegeometry)
  * 9.1 [ApexLineGeometry.\_\_init\_\_](#apexlinegeometry---init--)
  * 9.2 [ApexLineGeometry.\_\_repr\_\_](#apexlinegeometry---repr--)
  * 9.3 [ApexLineGeometry.\_\_str\_\_](#apexlinegeometry---str--)
  * 9.4 [ApexLineGeometry.drawing](#apexlinegeometry-drawing)
  * 9.5 [ApexLineGeometry.finish](#apexlinegeometry-finish)
  * 9.6 [ApexLineGeometry.finish\_key](#apexlinegeometry-finish-key)
  * 9.7 [ApexLineGeometry.part\_geometry](#apexlinegeometry-part-geometry)
  * 9.8 [ApexLineGeometry.start](#apexlinegeometry-start)
  * 9.9 [ApexLineGeometry.start\_key](#apexlinegeometry-start-key)
  * 9.10 [ApexLineGeometry.type\_name](#apexlinegeometry-type-name)
* 10 [Class ApexOperation](#apexoperation)
  * 10.1 [ApexOperation.body\_apply](#apexoperation-body-apply)
  * 10.2 [ApexOperation.constraints\_append](#apexoperation-constraints-append)
  * 10.3 [ApexOperation.geometries\_get](#apexoperation-geometries-get)
  * 10.4 [ApexOperation.reorient](#apexoperation-reorient)
  * 10.5 [ApexOperation.shape\_get](#apexoperation-shape-get)
  * 10.6 [ApexOperation.show](#apexoperation-show)
* 11 [Class ApexPad](#apexpad)
  * 11.1 [ApexPad.\_\_post\_init\_\_](#apexpad---post-init--)
  * 11.2 [ApexPad.body\_apply](#apexpad-body-apply)
  * 11.3 [ApexPad.reorient](#apexpad-reorient)
  * 11.4 [ApexPad.shape\_get](#apexpad-shape-get)
* 12 [Class ApexPocket](#apexpocket)
  * 12.1 [ApexPocket.\_\_post\_init\_\_](#apexpocket---post-init--)
  * 12.2 [ApexPocket.body\_apply](#apexpocket-body-apply)
  * 12.3 [ApexPocket.reorient](#apexpocket-reorient)
  * 12.4 [ApexPocket.shape\_get](#apexpocket-shape-get)
* 13 [Class ApexPointGeometry](#apexpointgeometry)
  * 13.1 [ApexPointGeometry.\_\_init\_\_](#apexpointgeometry---init--)
  * 13.2 [ApexPointGeometry.\_\_str\_\_](#apexpointgeometry---str--)
  * 13.3 [ApexPointGeometry.part\_geometry](#apexpointgeometry-part-geometry)
  * 13.4 [ApexPointGeometry.point](#apexpointgeometry-point)
  * 13.5 [ApexPointGeometry.type\_name](#apexpointgeometry-type-name)
* 14 [Class ApexPolygon](#apexpolygon)
  * 14.1 [ApexPolygon.\_\_post\_init\_\_](#apexpolygon---post-init--)
  * 14.2 [ApexPolygon.\_\_repr\_\_](#apexpolygon---repr--)
  * 14.3 [ApexPolygon.\_\_str\_\_](#apexpolygon---str--)
  * 14.4 [ApexPolygon.\_unit\_tests](#apexpolygon--unit-tests)
  * 14.5 [ApexPolygon.constraints\_append](#apexpolygon-constraints-append)
  * 14.6 [ApexPolygon.geometries\_get](#apexpolygon-geometries-get)
  * 14.7 [ApexPolygon.reorient](#apexpolygon-reorient)
  * 14.8 [ApexPolygon.show](#apexpolygon-show)
* 15 [Class ApexShape](#apexshape)
  * 15.1 [ApexShape.constraints\_append](#apexshape-constraints-append)
  * 15.2 [ApexShape.geometries\_get](#apexshape-geometries-get)
  * 15.3 [ApexShape.reorient](#apexshape-reorient)
  * 15.4 [ApexShape.show](#apexshape-show)
* 16 [Class \_ApexCornerExtra](#-apexcornerextra)

## 1 <a name="introduction"></a>Introduction


This module provides an interface that both creates FreeCAD sketches and applies those sketches
to FreeCAD Part Design workbench Body objects.  Addition information is provided to supporting
the FreeCAD Path workbench.

The are 4 base classes of used in this module:
* ApexDrawing: Create one or more FreeCAD Sketches and applies Part Design and Path operations.
* ApexOperation: This is the Part Design and Path operation information.
* ApexShape: This is the geometric shapes that go into the ApexDrawing.
* ApexGeometry: The class of objects represents 2D geometric constructs (point, line, arc, circle).

There is a rich set of FreeCAD PartDesign operations that can be applied to sketches.
The construction operations are pad, revolve, loft, sweep and helix.
The subtraction operations are pocket, hole, groove, loft, sweep and helix.
The current ApexOperation sub-classes are:
* ApexPad: Performs a FreeCAD Part Design pad operation.
* ApexPocket: Performs a FreeCAD Part Design pocket operation
* ApexHole: Performs a FreeCAD Part Design pocket operation
Each of these these operations takes either an ApexCircle or an ApexPolygon as an argument.

The ApexShape sub-classes are:
* ApexCircle: This represents a circle in the ApexDrawing.
* ApexPolygon: This is basically a sequence of ApexCorner's (see below) that represent a polygon,
  where each corner can optionally have rounded with a fillet.
* ApexCorner: This represents one corner of an ApexPolygon and specifies the fillet radius.
Each ApexShape has an associated ApexOperation (see below).

The internal ApexGeometry sub-classes are:
* ApexPoint: This represents a single point geometry.
* ApexLine: This represents a line segment geometry.
* ApexArc: This represents an arc on a circle geometry.
* ApexCircle This represents a circle geometry.

All of this information is collected into an ApexDrawing instance.
The ApexDrawing.body_apply() takes a FreeCAD Part Design Body and applies operations drawing to it.

## 2 Class ApexArcGeometry <a name="apexarcgeometry"></a>

class ApexArcGeometry(ApexGeometry):

Represents an an arc in a sketch.

### 2.1 ApexArcGeometry.\_\_init\_\_ <a name="apexarcgeometry---init--"></a>

def \_\_init\_\_(self, *drawing*:  "ApexDrawing", *begin*:  ApexCorner, *at*:  ApexCorner, *end*:  ApexCorner, *name*:  *str* = "", *tracing*:  *str* = "") -> None:

Initialize an ApexArcGeometry.

### 2.2 ApexArcGeometry.\_\_str\_\_ <a name="apexarcgeometry---str--"></a>

def \_\_str\_\_(self) -> *str*:

Return string representation of ApexGeometry.

### 2.3 ApexArcGeometry.apex <a name="apexarcgeometry-apex"></a>

def *at*(self) -> Vector:

Return the ApexArcGeometry apex Vector.

### 2.4 ApexArcGeometry.begin <a name="apexarcgeometry-begin"></a>

def *begin*(self) -> Vector:  # *pragma*:  *no* *unit* *test*

Return the ApexArcGeometry arc begin Vector.

### 2.5 ApexArcGeometry.center <a name="apexarcgeometry-center"></a>

def *center*(self) -> Vector:

Return the ApexArcGeometry arc center.

### 2.6 ApexArcGeometry.end <a name="apexarcgeometry-end"></a>

def *end*(self) -> Vector:  # *pragma*:  *no* *unit* *test*

Return the initial ApexArcGeometry end Vector.

### 2.7 ApexArcGeometry.finish <a name="apexarcgeometry-finish"></a>

def *finish*(self) -> Vector:

Return the ApexArcGeometry arc finish Vector.

### 2.8 ApexArcGeometry.finish\_angle <a name="apexarcgeometry-finish-angle"></a>

def *finish\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ApexArcGeometry arc finish angle.

### 2.9 ApexArcGeometry.finish\_key <a name="apexarcgeometry-finish-key"></a>

def *finish\_key*(self) -> *int*:

Return the ApexArcGeometry finish Constraint key.

### 2.10 ApexArcGeometry.finish\_length <a name="apexarcgeometry-finish-length"></a>

def *finish\_length*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return distance from arc finish Vector to the apex Vector.

### 2.11 ApexArcGeometry.input <a name="apexarcgeometry-input"></a>

def *input*(self) -> Vector:  # *pragma*:  *no* *unit* *test*

Return the initial ApexArcGeometry arc start Vector.

### 2.12 ApexArcGeometry.part\_geometry <a name="apexarcgeometry-part-geometry"></a>

def *part\_geometry*(self) -> PartGeometry:

Return ApexArcGeometry Part.Arc.

### 2.13 ApexArcGeometry.radius <a name="apexarcgeometry-radius"></a>

def *radius*(self) -> *float*:

Return the initial ApexArcGeometry radius.

### 2.14 ApexArcGeometry.repr <a name="apexarcgeometry-repr"></a>

def \_\_repr\_\_(self) -> *str*:  # *pragma*:  *no* *unit* *test*

Return ApexArcGeometry string representation.

### 2.15 ApexArcGeometry.start <a name="apexarcgeometry-start"></a>

def *start*(self) -> Vector:

Return the ApexArcGeometry arc start Vector.

### 2.16 ApexArcGeometry.start\_angle <a name="apexarcgeometry-start-angle"></a>

def *start\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ApexArcGeometry arc start angle.

### 2.17 ApexArcGeometry.start\_key <a name="apexarcgeometry-start-key"></a>

def *start\_key*(self) -> *int*:

Return the ApexArcGeometry finish Constraint key.

### 2.18 ApexArcGeometry.start\_length <a name="apexarcgeometry-start-length"></a>

def *start\_length*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ApexArcGeometry distance from start Vector to apex Vector.

### 2.19 ApexArcGeometry.sweep\_angle <a name="apexarcgeometry-sweep-angle"></a>

def *sweep\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *cover*

Return the ApexArcGeometry sweep angle from start angle to end angle.

### 2.20 ApexArcGeometry.type\_name <a name="apexarcgeometry-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexArcGeometry type name.

## 3 Class ApexCircle <a name="apexcircle"></a>

class ApexCircle(ApexShape):

ApexCircle: Represents a circle.

Usage: ApexCircle(center, diameter, name)

Attributes:
* *Center* (Vector): The center of the circle.
* *Diameter* (float): Circle diameter in millimeters
* *Name* (str):  Name of circle.  (Default: "")
* *Box* (ApexBox): ApexBox that encloses ApexCircle as if it is a sphere.
* *Constraints* (Tuple[Sketcher.Constraint, ...):  Computed constraints.


### 3.1 ApexCircle.\_\_post\_init <a name="apexcircle---post-init"></a>

def \_\_post\_init\_\_(self) -> None:

Initialize a circle.

### 3.2 ApexCircle.constraints\_append <a name="apexcircle-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  "ApexDrawing", *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Return the ApexCircleGeometry constraints.

### 3.3 ApexCircle.geometries\_get <a name="apexcircle-geometries-get"></a>

def *geometries\_get*(self, *drawing*:  "ApexDrawing", *tracing*:  *str* = "") -> Tuple[ApexGeometry, ...]:

Return the ApexCircleGeometry.

### 3.4 ApexCircle.reorient <a name="apexcircle-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  Optional[str] = "", *tracing*:  *str* = "") -> "ApexCircle":

Return a new reoriented ApexCircle.

Arguments:
* *placement* (Placement): The FreeCAD Placement reorient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")


## 4 Class ApexCircleGeometry <a name="apexcirclegeometry"></a>

class ApexCircleGeometry(ApexGeometry):

Represents a circle in a sketch.

### 4.1 ApexCircleGeometry.\_\_init\_\_ <a name="apexcirclegeometry---init--"></a>

def \_\_init\_\_(self, *drawing*:  "ApexDrawing", *center*:  Vector, *radius*:  *float*, *name*:  *str* = "") -> None:

Initialize a ApexCircleGeometry.

### 4.2 ApexCircleGeometry.\_\_repr\_\_ <a name="apexcirclegeometry---repr--"></a>

def \_\_repr\_\_(self) -> *str*:

Return string representation of ApexGeometry.

### 4.3 ApexCircleGeometry.\_\_str\_\_ <a name="apexcirclegeometry---str--"></a>

def \_\_str\_\_(self) -> *str*:

Return string representation of ApexGeometry.

### 4.4 ApexCircleGeometry.center <a name="apexcirclegeometry-center"></a>

def *center*(self) -> Vector:  # *pragma*:  *no* *unit* *cover*

Return the ApexCircleGeometry center.

### 4.5 ApexCircleGeometry.part\_element <a name="apexcirclegeometry-part-element"></a>

def *part\_geometry*(self) -> PartGeometry:

Return the ApexCircleGeometry PartGeometry.

### 4.6 ApexCircleGeometry.radius <a name="apexcirclegeometry-radius"></a>

def *radius*(self) -> *float*:  # *pragma*:  *no* *unit* *cover*

Return the ApexCircleGeometry radius.

### 4.7 ApexCircleGeometry.type\_name <a name="apexcirclegeometry-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexCircleGeometry type name.

## 5 Class ApexCorner <a name="apexcorner"></a>

class ApexCorner(object):

ApexCorner: An ApexPolygon corner with a radius.

Usage: ApexCorner(point, radius, name)

Attributes:
* *Point* (Vector): A point for a polygon.
* *Radius (float): The corner radius in millimeters.  (Default: 0.0)
* *Name* (str): The corner name. (Default: "")
* *Box* (ApexBox): A computed ApexBox that encloses corner as if it was a sphere of size Radius.


### 5.1 ApexCorner.\_\_post\_init\_\_ <a name="apexcorner---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify contents of ApexCorner.

### 5.2 ApexCorner.\_\_repr\_\_ <a name="apexcorner---repr--"></a>

def \_\_repr\_\_(self) -> *str*:

Return string representation of ApexCorner.

### 5.3 ApexCorner.\_\_str\_\_ <a name="apexcorner---str--"></a>

def \_\_str\_\_(self) -> *str*:

Return string representation of ApexCorner.

### 5.4 ApexCorner.\_unit\_tests <a name="apexcorner--unit-tests"></a>

def \_unit\_tests() -> None:

Run unit tests for ApexCorner.

## 6 Class ApexDrawing <a name="apexdrawing"></a>

class ApexDrawing(object):

ApexDrawing: Used to create fully constrained 2D drawings.

Usage: ApexDrawing(contact, normal, operations, name)

Attributes:
* *Contact*: (Vector): On point on the surface of the polygon.
* *Normal*: (Vector): A normal to the polygon plane.
* *Operations* (Tuple[ApexOperation, ...]): Operations to perform on drawing.
* *Name* (str): The ApexDrawing name. (Default: "")
* *Box* (ApexBox): A computed ApexBox that encloses all of the operations.


### 6.1 ApexDrawing.\_\_post\_init\_\_ <a name="apexdrawing---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Initialize a drawing.

### 6.2 ApexDrawing.create\_datum\_plane <a name="apexdrawing-create-datum-plane"></a>

def *create\_datum\_plane*(self, *body*:  "PartDesign.Body", *name*:  Optional[str] = None, *tracing*:  *str* = "") -> "Part.ApexGeometry":

Return the FreeCAD DatumPlane used for the drawing.

Arguments:
* *body* (PartDesign.Body): The FreeCAD Part design Body to attach the datum plane to.
* *name* (Optional[str]): The datum plane name.
  (Default: "...DatumPlaneN", where N is incremented.)
* Returns:
  * (Part.ApexGeometry) that is the datum\_plane.

### 6.3 ApexDrawing.geometries\_get <a name="apexdrawing-geometries-get"></a>

def *point\_geometries\_get*(self, *point*:  Vector, *tracing*:  *str* = "") -> Tuple["ApexGeometry", ...]:

Return the ApexPointGeometry Geometry's.

### 6.4 ApexDrawing.plane\_process <a name="apexdrawing-plane-process"></a>

def *plane\_process*(self, *body*:  "PartDesign.Body", *document\_name*:  *str*, *tracing*:  *str* = "") -> None:

Plane\_Process.

### 6.5 ApexDrawing.point\_constraints\_append <a name="apexdrawing-point-constraints-append"></a>

def *point\_constraints\_append*(self, *point*:  Vector, *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:  # REMOVE

Append Vector constraints to a list.

### 6.6 ApexDrawing.reorient <a name="apexdrawing-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  Optional[str] = "", *tracing*:  *str* = "") -> "ApexDrawing":

Return a reoriented ApexDrawing.

Arguments:
* *placement* (Placement): The Placement to apply ApexCircle's and ApexPolygon's.
* *suffix* (Optional[str]): The suffix to append at all names.  If None, all
  names are set to "" instead appending the suffix.  (Default: "")


### 6.7 ApexDrawing.sketch <a name="apexdrawing-sketch"></a>

def *sketch*(self, *sketcher*:  "Sketcher.SketchObject", *tracing*:  *str* = "") -> None:

Insert an ApexDrawing into a FreeCAD SketchObject.

Arguments:
* sketcher (Sketcher.SketchObject): The sketcher object to use.

## 7 Class ApexGeometry <a name="apexgeometry"></a>

class ApexGeometry(object):

ApexGeometry: Internal Base class for 2D geometry objects.

This is basically a wrapper around the arguments need to create Sketch elements.
It is mutable and always contains a bunch of helper functions.

### 7.1 ApexGeometry.\_\_init\_\_ <a name="apexgeometry---init--"></a>

def \_\_init\_\_(self, *drawing*:  "ApexDrawing", *start*:  Vector, *finish*:  Vector, *name*:  *str* = "") -> None:

Initialize a ApexGeometry.

### 7.2 ApexGeometry.constraints\_append <a name="apexgeometry-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  "ApexDrawing", *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Append the ApexShape constraints to drawing.

Arguments:
* *drawing* (ApexDrawing): The drawing to use.
* *constraints* (List[SketcherConstraint]): The constraints list to append to.


### 7.3 ApexGeometry.drawing <a name="apexgeometry-drawing"></a>

def *drawing*(self) -> "ApexDrawing":  # *pragma*:  *no* *unit* *test*

Return the ApexGeometry ApexDrawing.

### 7.4 ApexGeometry.finish <a name="apexgeometry-finish"></a>

def *finish*(self) -> Vector:  # *pragma*:  *no* *unit* *test*

Return the ApexGeometry finish point.

### 7.5 ApexGeometry.index <a name="apexgeometry-index"></a>

def *index*(self) -> *int*:

Return the ApexGeometry index.

### 7.6 ApexGeometry.name <a name="apexgeometry-name"></a>

def *name*(self) -> *str*:

Return ApexGeometry name.

### 7.7 ApexGeometry.part\_geometry <a name="apexgeometry-part-geometry"></a>

def *part\_geometry*(self) -> PartGeometry:

Return the PartGeometry associated with ApexGeometry.

### 7.8 ApexGeometry.previous <a name="apexgeometry-previous"></a>

def *previous*(self) -> "ApexGeometry":  # *pragma*:  *no* *unit* *test*

Return the previous Part ApexGeometry in circular list.

### 7.9 ApexGeometry.start <a name="apexgeometry-start"></a>

def *start*(self) -> Vector:  # *pragma*:  *no* *unit* *test*

Return the ApexGeometry start point.

### 7.10 ApexGeometry.type\_name <a name="apexgeometry-type-name"></a>

def *type\_name*(self) -> *str*:

Return the ApexGeometry type name.

## 8 Class ApexHole <a name="apexhole"></a>

class ApexHole(ApexOperation):

ApexHole represents a FreeCAD Part Design workbench Hole operation.

Usage: ApexHole(circle, depth, name)

Attributes:
* *Circle: (ApexCircle): The ApexCircle for the hole.
* *Depth* (float): The hole depth in millimeters.
* *Name* (str): The name of the operation.  (Default: "")
* *SortKey* (Tuple[str, ...]): A generated sorting key used to sort ApexOperation's.


### 8.1 ApexHole.\_\_post\_init\_\_ <a name="apexhole---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify argument types.

### 8.2 ApexHole.body\_apply <a name="apexhole-body-apply"></a>

def *body\_apply*(self, *body*:  "PartDesign.Body", *group\_name*:  *str*, *sketch*:  "Sketcher.SketchObject", *gui\_document*:  Optional["Gui.ActiveDocument"], *tracing*:  *str* = "") -> None:

Apply hole operation to PartDesign body.

### 8.3 ApexHole.reorient <a name="apexhole-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  *str* = None, *tracing*:  *str* = "") -> "ApexHole":

Reorient an ApexHole.

Arguments:
* *placement* (Placement): The FreeCAD Placement to reorient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")


### 8.4 ApexHole.shape\_get <a name="apexhole-shape-get"></a>

def *shape\_get*(self) -> ApexShape:

Return the ApexHole ApexShape.

## 9 Class ApexLineGeometry <a name="apexlinegeometry"></a>

class ApexLineGeometry(ApexGeometry):

Represents a line segment in a sketch.

### 9.1 ApexLineGeometry.\_\_init\_\_ <a name="apexlinegeometry---init--"></a>

def \_\_init\_\_(self, *drawing*:  "ApexDrawing", *start*:  Vector, *finish*:  Vector, *name*:  *str* = "", *tracing*:  *str* = "") -> None:

Initialize a ApexLineGeometry.

### 9.2 ApexLineGeometry.\_\_repr\_\_ <a name="apexlinegeometry---repr--"></a>

def \_\_repr\_\_(self) -> *str*:

Return string representation of ApexLineGeometry.

### 9.3 ApexLineGeometry.\_\_str\_\_ <a name="apexlinegeometry---str--"></a>

def \_\_str\_\_(self) -> *str*:

Return string representation of ApexLineGeometry.

### 9.4 ApexLineGeometry.drawing <a name="apexlinegeometry-drawing"></a>

def *drawing*(self) -> "ApexDrawing":  # *pragma*:  *no* *unit* *cover*

Return the ApexLineGeometry ApexDrawing.

### 9.5 ApexLineGeometry.finish <a name="apexlinegeometry-finish"></a>

def *finish*(self) -> Vector:  # *pragma*:  *no* *unit* *cover*

Return the ApexLineGeometry finish Vector.

### 9.6 ApexLineGeometry.finish\_key <a name="apexlinegeometry-finish-key"></a>

def *finish\_key*(self) -> *int*:

Return the ApexLineGeometry finish Constraint key.

### 9.7 ApexLineGeometry.part\_geometry <a name="apexlinegeometry-part-geometry"></a>

def *part\_geometry*(self) -> PartGeometry:

Return the PartGeometry associated with a ApexLineGeometry.

### 9.8 ApexLineGeometry.start <a name="apexlinegeometry-start"></a>

def *start*(self) -> ApexCorner:

Return the ApexLineGeometry start Vector.

### 9.9 ApexLineGeometry.start\_key <a name="apexlinegeometry-start-key"></a>

def *start\_key*(self) -> *int*:

Return the ApexLineGeometry start Constraint key.

### 9.10 ApexLineGeometry.type\_name <a name="apexlinegeometry-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexLineGeometry type name.

## 10 Class ApexOperation <a name="apexoperation"></a>

class ApexOperation(object):

Represents a FreeCAD Part Design workbench operation.

This is a base class for ApexHole, ApexPad, and ApexPocket.

Attributes:
* *SortKey*: (Tuple[str, ...]): A key generated by sub-class used to sort ApexOpertions.


### 10.1 ApexOperation.body\_apply <a name="apexoperation-body-apply"></a>

def *body\_apply*(self, *body*:  "PartDesign.Body", *group\_name*:  *str*, *sketch*:  "Sketcher.SketchObject", *gui\_document*:  Optional["Gui.ActiveDocument"], *tracing*:  *str* = "") -> None:

Apply operation to a Part Design body.

### 10.2 ApexOperation.constraints\_append <a name="apexoperation-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  "ApexDrawing", *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Append the ApexOperation constraints to drawing.

Arguments:
* *drawing* (ApexDrawing): The drawing to use.
* *constraints* (List[SketcherConstraint]): The constraints list to append to.


### 10.3 ApexOperation.geometries\_get <a name="apexoperation-geometries-get"></a>

def *geometries\_get*(self, *drawing*:  "ApexDrawing", *tracing*:  *str* = "") -> Tuple[ApexGeometry, ...]:

Return the geometries associated with an operation.

### 10.4 ApexOperation.reorient <a name="apexoperation-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  *str* = None, *tracing*:  *str* = "") -> "ApexOperation":

Reorient an operation.

Arguments:
* *placement* (Placement): The FreeCAD Placement reorient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")


### 10.5 ApexOperation.shape\_get <a name="apexoperation-shape-get"></a>

def *shape\_get*(self) -> ApexShape:

Return the associated ApexOperation ApexShape.

### 10.6 ApexOperation.show <a name="apexoperation-show"></a>

def *show*(self) -> *str*:

Return a string that shows operation.

## 11 Class ApexPad <a name="apexpad"></a>

class ApexPad(ApexOperation):

ApexPad represents a FreeCAD Part Design workbench Pad operation.

Attributes:
* *Shape* (ApexShape): The ApexCircle/ApexPolygon to use for padding.
* *Depth* (float): The depth of the pad operation.
* *Name* (str): The name of the operation.  (Default: "")
* *SortKey* (Tuple[str, ...]): A generated sorting key used to sort ApexOperation's.

Usage: ApexPad(circle\_or\_pologon, depth, name)


### 11.1 ApexPad.\_\_post\_init\_\_ <a name="apexpad---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify argument types.

### 11.2 ApexPad.body\_apply <a name="apexpad-body-apply"></a>

def *body\_apply*(self, *body*:  "PartDesign.Body", *group\_name*:  *str*, *sketch*:  "Sketcher.SketchObject", *gui\_document*:  Optional["Gui.ActiveDocument"], *tracing*:  *str* = "") -> None:

Apply ApexPad opertation to PartDesign Body.

### 11.3 ApexPad.reorient <a name="apexpad-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  *str* = None, *tracing*:  *str* = "") -> "ApexPad":

Reorient an ApexPad .

Arguments:
* *placement* (Placement): The FreeCAD Placement reorient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")


### 11.4 ApexPad.shape\_get <a name="apexpad-shape-get"></a>

def *shape\_get*(self) -> ApexShape:

Return the associated ApexShape's.

## 12 Class ApexPocket <a name="apexpocket"></a>

class ApexPocket(ApexOperation):

ApexPocket represents a FreeCAD Part Design workbench Pad operation.

Usage: ApexPad(circle\_or\_polygon, depth, name)

Attributes:
* *Shape* (ApexShape): The ApexCircle/ApexPolygon to use for the pocket operation.
* *Depth* (float): The depth of the pocke operation.
* *Name* (str): The name of the operation.  (Default: "")
* *SortKey* (Tuple[str, ...]): A generated sorting key used to sort ApexOperations.


### 12.1 ApexPocket.\_\_post\_init\_\_ <a name="apexpocket---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify argument types.

### 12.2 ApexPocket.body\_apply <a name="apexpocket-body-apply"></a>

def *body\_apply*(self, *body*:  "PartDesign.Body", *group\_name*:  *str*, *sketch*:  "Sketcher.SketchObject", *gui\_document*:  Optional["Gui.ActiveDocument"], *tracing*:  *str* = "") -> None:

Apply pocket operation to PartDesign Body.

### 12.3 ApexPocket.reorient <a name="apexpocket-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  *str* = None, *tracing*:  *str* = "") -> "ApexPocket":

Reorient an ApexPocket .

Arguments:
* *placement* (Placement): The FreeCAD Placement reorient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")


### 12.4 ApexPocket.shape\_get <a name="apexpocket-shape-get"></a>

def *shape\_get*(self) -> ApexShape:

Return the ApexPad ApexShape.

## 13 Class ApexPointGeometry <a name="apexpointgeometry"></a>

class ApexPointGeometry(ApexGeometry):

Represents a point in a sketch.

### 13.1 ApexPointGeometry.\_\_init\_\_ <a name="apexpointgeometry---init--"></a>

def \_\_init\_\_(self, *drawing*:  "ApexDrawing", *point*:  Vector, *name*:  *str* = "") -> None:

Initialize a ApexPointGeometry.

### 13.2 ApexPointGeometry.\_\_str\_\_ <a name="apexpointgeometry---str--"></a>

def \_\_str\_\_(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return ApexPointGeometry string .

### 13.3 ApexPointGeometry.part\_geometry <a name="apexpointgeometry-part-geometry"></a>

def *part\_geometry*(self) -> PartGeometry:

Return the  ApexPointGeometry.

### 13.4 ApexPointGeometry.point <a name="apexpointgeometry-point"></a>

def *point*(self) -> Vector:  # *pragma*:  *no* *unit* *cover*

Return the ApexPointGeometry Vector.

### 13.5 ApexPointGeometry.type\_name <a name="apexpointgeometry-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexPointGeometry type name.

## 14 Class ApexPolygon <a name="apexpolygon"></a>

class ApexPolygon(ApexShape):

ApexPolyon: A closed polygon of Vectors.

Usage: ApexPolygon(corners, name)

Attributes:
* *Corners* (Tuple[ApexCorner, ...]): The ApexCorner's of the ApexPoloygon.
* *Name* (str): The ApexPolygon name.  (Default: "")
* *Box* (ApexBox): An ApexBox that encloses all of the corners.
* *Clockwise* (bool): Computed to True the corners are in clockwise order.
* *InternalRadius* (float): The computed minimum radius for internal corners in millimeters.


### 14.1 ApexPolygon.\_\_post\_init\_\_ <a name="apexpolygon---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Initialize a ApexPolygon.

### 14.2 ApexPolygon.\_\_repr\_\_ <a name="apexpolygon---repr--"></a>

def \_\_repr\_\_(self) -> *str*:

Return string representation of ApexPolygon.

### 14.3 ApexPolygon.\_\_str\_\_ <a name="apexpolygon---str--"></a>

def \_\_str\_\_(self, *short*:  *bool* = False) -> *str*:

Return string representation of ApexPolygon.

Arguments:
* *short* (bool): If true, a shorter versions returned.


### 14.4 ApexPolygon.\_unit\_tests <a name="apexpolygon--unit-tests"></a>

def \_unit\_tests() -> None:

Run ApexPolygon unit tests.

### 14.5 ApexPolygon.constraints\_append <a name="apexpolygon-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  "ApexDrawing", *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Return the ApexPolygon constraints for a ApexDrawing.

### 14.6 ApexPolygon.geometries\_get <a name="apexpolygon-geometries-get"></a>

def *geometries\_get*(self, *drawing*:  "ApexDrawing", *tracing*:  *str* = "") -> Tuple[ApexGeometry, ...]:

Return the ApexPolygon ApexGeometries tuple.

### 14.7 ApexPolygon.reorient <a name="apexpolygon-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  Optional[str] = "", *tracing*:  *str* = "") -> "ApexPolygon":

Reorient an ApexPolygon with a new Placement.

Arguments:
* *placement* (Placement):
  The FreeCAD Placement to reorient with.
* *suffix* (Optional[str]):
  A suffix to append to the name.  If None, an empty name is used. (Default: "")


### 14.8 ApexPolygon.show <a name="apexpolygon-show"></a>

def *show*(self) -> *str*:

Return compact string showing ApexPolygon contents.

## 15 Class ApexShape <a name="apexshape"></a>

class ApexShape(object):

ApexShape: Is a base class for geometric shapes (e.g. ApexPolygon, etc).

ApexShape is a base class for the various geometric shapes.  See sub-classes for attributes.

### 15.1 ApexShape.constraints\_append <a name="apexshape-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  "ApexDrawing", *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Append the ApexShape constraints to drawing.

Arguments:
* *drawing* (ApexDrawing): The drawing to use.
* *constraints* (List[SketcherConstraint]): The constraints list to append to.


### 15.2 ApexShape.geometries\_get <a name="apexshape-geometries-get"></a>

def *geometries\_get*(self, *drawing*:  "ApexDrawing", *tracing*:  *str* = "") -> Tuple[ApexGeometry, ...]:

Return the ApexShape ApexGeometries tuple.

Arguments:
* *drawing* (ApexDrawing): The associated drawing to use for geometry extraction.

Returns:
* (Tuple[ApexGeometry, ...]) of extracted ApexGeometry's.


### 15.3 ApexShape.reorient <a name="apexshape-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  Optional[str] = "", *tracing*:  *str* = "") -> "ApexShape":

Return a new reoriented ApexCircle.

Arguments:
* *placement* (Placement): The FreeCAD Placement to reorient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")

# Returns:
* (ApexShape) that has been reoriented with a new name.

### 15.4 ApexShape.show <a name="apexshape-show"></a>

def *show*(self) -> *str*:

Return compact string for ApexShape.

## 16 Class \_ApexCornerExtra <a name="-apexcornerextra"></a>

class \_ApexCornerExtra(object):

\_ApexCornerExtra: An internal mutable class that corresponds to an ApexCorner.
