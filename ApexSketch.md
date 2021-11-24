# ApexSketch: An interface to FreeCAD Sketches.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class ApexArcFeature](#apexarcfeature)
  * 2.1 [ApexArcFeature.\_\_init\_\_](#apexarcfeature---init--)
  * 2.2 [ApexArcFeature.\_\_str\_\_](#apexarcfeature---str--)
  * 2.3 [ApexArcFeature.apex](#apexarcfeature-apex)
  * 2.4 [ApexArcFeature.begin](#apexarcfeature-begin)
  * 2.5 [ApexArcFeature.center](#apexarcfeature-center)
  * 2.6 [ApexArcFeature.end](#apexarcfeature-end)
  * 2.7 [ApexArcFeature.finish](#apexarcfeature-finish)
  * 2.8 [ApexArcFeature.finish\_angle](#apexarcfeature-finish-angle)
  * 2.9 [ApexArcFeature.finish\_key](#apexarcfeature-finish-key)
  * 2.10 [ApexArcFeature.finish\_length](#apexarcfeature-finish-length)
  * 2.11 [ApexArcFeature.input](#apexarcfeature-input)
  * 2.12 [ApexArcFeature.part\_feature](#apexarcfeature-part-feature)
  * 2.13 [ApexArcFeature.radius](#apexarcfeature-radius)
  * 2.14 [ApexArcFeature.repr](#apexarcfeature-repr)
  * 2.15 [ApexArcFeature.start](#apexarcfeature-start)
  * 2.16 [ApexArcFeature.start\_angle](#apexarcfeature-start-angle)
  * 2.17 [ApexArcFeature.start\_key](#apexarcfeature-start-key)
  * 2.18 [ApexArcFeature.start\_length](#apexarcfeature-start-length)
  * 2.19 [ApexArcFeature.sweep\_angle](#apexarcfeature-sweep-angle)
  * 2.20 [ApexArcFeature.type\_name](#apexarcfeature-type-name)
* 3 [Class ApexCircle](#apexcircle)
  * 3.1 [ApexCircle.\_\_post\_init](#apexcircle---post-init)
  * 3.2 [ApexCircle.constraints\_append](#apexcircle-constraints-append)
  * 3.3 [ApexCircle.features\_get](#apexcircle-features-get)
  * 3.4 [ApexCircle.reorient](#apexcircle-reorient)
* 4 [Class ApexCircleFeature](#apexcirclefeature)
  * 4.1 [ApexCircleFeature.\_\_init\_\_](#apexcirclefeature---init--)
  * 4.2 [ApexCircleFeature.center](#apexcirclefeature-center)
  * 4.3 [ApexCircleFeature.part\_element](#apexcirclefeature-part-element)
  * 4.4 [ApexCircleFeature.radius](#apexcirclefeature-radius)
  * 4.5 [ApexCircleFeature.type\_name](#apexcirclefeature-type-name)
* 5 [Class ApexCorner](#apexcorner)
  * 5.1 [ApexCorner.\_\_post\_init\_\_](#apexcorner---post-init--)
  * 5.2 [ApexCorner.\_\_repr\_\_](#apexcorner---repr--)
  * 5.3 [ApexCorner.\_\_str\_\_](#apexcorner---str--)
  * 5.4 [ApexCorner.\_unit\_tests](#apexcorner--unit-tests)
* 6 [Class ApexDrawing](#apexdrawing)
  * 6.1 [ApexDrawing.\_\_post\_init\_\_](#apexdrawing---post-init--)
  * 6.2 [ApexDrawing.create\_datum\_plane](#apexdrawing-create-datum-plane)
  * 6.3 [ApexDrawing.features\_get](#apexdrawing-features-get)
  * 6.4 [ApexDrawing.plane\_process](#apexdrawing-plane-process)
  * 6.5 [ApexDrawing.point\_constraints\_append](#apexdrawing-point-constraints-append)
  * 6.6 [ApexDrawing.reorient](#apexdrawing-reorient)
  * 6.7 [ApexDrawing.sketch](#apexdrawing-sketch)
* 7 [Class ApexFeature](#apexfeature)
  * 7.1 [ApexFeature.\_\_init\_\_](#apexfeature---init--)
  * 7.2 [ApexFeature.\_\_repr\_\_](#apexfeature---repr--)
  * 7.3 [ApexFeature.\_\_str\_\_](#apexfeature---str--)
  * 7.4 [ApexFeature.constraints\_append](#apexfeature-constraints-append)
  * 7.5 [ApexFeature.drawing](#apexfeature-drawing)
  * 7.6 [ApexFeature.finish](#apexfeature-finish)
  * 7.7 [ApexFeature.index](#apexfeature-index)
  * 7.8 [ApexFeature.name](#apexfeature-name)
  * 7.9 [ApexFeature.part\_feature](#apexfeature-part-feature)
  * 7.10 [ApexFeature.previous](#apexfeature-previous)
  * 7.11 [ApexFeature.start](#apexfeature-start)
  * 7.12 [ApexFeature.type\_name](#apexfeature-type-name)
* 8 [Class ApexHole](#apexhole)
  * 8.1 [ApexHole.\_\_post\_init\_\_](#apexhole---post-init--)
  * 8.2 [ApexHole.body\_apply](#apexhole-body-apply)
  * 8.3 [ApexHole.constraints\_append](#apexhole-constraints-append)
  * 8.4 [ApexHole.features\_get](#apexhole-features-get)
  * 8.5 [ApexHole.reorient](#apexhole-reorient)
  * 8.6 [ApexHole.shape\_get](#apexhole-shape-get)
* 9 [Class ApexLineFeature](#apexlinefeature)
  * 9.1 [ApexLineFeature.\_\_init\_\_](#apexlinefeature---init--)
  * 9.2 [ApexLineFeature.\_\_repr\_\_](#apexlinefeature---repr--)
  * 9.3 [ApexLineFeature.\_\_str\_\_](#apexlinefeature---str--)
  * 9.4 [ApexLineFeature.drawing](#apexlinefeature-drawing)
  * 9.5 [ApexLineFeature.finish](#apexlinefeature-finish)
  * 9.6 [ApexLineFeature.finish\_key](#apexlinefeature-finish-key)
  * 9.7 [ApexLineFeature.part\_feature](#apexlinefeature-part-feature)
  * 9.8 [ApexLineFeature.start](#apexlinefeature-start)
  * 9.9 [ApexLineFeature.start\_key](#apexlinefeature-start-key)
  * 9.10 [ApexLineFeature.type\_name](#apexlinefeature-type-name)
* 10 [Class ApexOperation](#apexoperation)
  * 10.1 [ApexOperation.body\_apply](#apexoperation-body-apply)
  * 10.2 [ApexOperation.constraints\_append](#apexoperation-constraints-append)
  * 10.3 [ApexOperation.features\_get](#apexoperation-features-get)
  * 10.4 [ApexOperation.reorient](#apexoperation-reorient)
  * 10.5 [ApexOperation.shape\_get](#apexoperation-shape-get)
  * 10.6 [ApexOperation.show](#apexoperation-show)
* 11 [Class ApexPad](#apexpad)
  * 11.1 [ApexPad.\_\_post\_init\_\_](#apexpad---post-init--)
  * 11.2 [ApexPad.body\_apply](#apexpad-body-apply)
  * 11.3 [ApexPad.constraints\_append](#apexpad-constraints-append)
  * 11.4 [ApexPad.features\_get](#apexpad-features-get)
  * 11.5 [ApexPad.reorient](#apexpad-reorient)
  * 11.6 [ApexPad.shape\_get](#apexpad-shape-get)
  * 11.7 [ApexPad.shape\_get](#apexpad-shape-get)
* 12 [Class ApexPocket](#apexpocket)
  * 12.1 [ApexPocket.\_\_post\_init\_\_](#apexpocket---post-init--)
  * 12.2 [ApexPocket.body\_apply](#apexpocket-body-apply)
  * 12.3 [ApexPocket.constraints\_append](#apexpocket-constraints-append)
* 13 [Class ApexPointFeature](#apexpointfeature)
  * 13.1 [ApexPointFeature.\_\_init\_\_](#apexpointfeature---init--)
  * 13.2 [ApexPointFeature.\_\_str\_\_](#apexpointfeature---str--)
  * 13.3 [ApexPointFeature.part\_feature](#apexpointfeature-part-feature)
  * 13.4 [ApexPointFeature.point](#apexpointfeature-point)
  * 13.5 [ApexPointFeature.type\_name](#apexpointfeature-type-name)
* 14 [Class ApexPolygon](#apexpolygon)
  * 14.1 [ApexPolygon.\_\_post\_init\_\_](#apexpolygon---post-init--)
  * 14.2 [ApexPolygon.\_\_repr\_\_](#apexpolygon---repr--)
  * 14.3 [ApexPolygon.\_\_str\_\_](#apexpolygon---str--)
  * 14.4 [ApexPolygon.constraints\_append](#apexpolygon-constraints-append)
  * 14.5 [ApexPolygon.features\_get](#apexpolygon-features-get)
  * 14.6 [ApexPolygon.reorient](#apexpolygon-reorient)
  * 14.7 [ApexPolygon.show](#apexpolygon-show)
* 15 [Class ApexShape](#apexshape)
  * 15.1 [ApexShape.constraints\_append](#apexshape-constraints-append)
  * 15.2 [ApexShape.features\_get](#apexshape-features-get)
  * 15.3 [ApexShape.reorient](#apexshape-reorient)
  * 15.4 [ApexShape.show](#apexshape-show)

## 1 <a name="introduction"></a>Introduction


This module provides an interface that both creates FreeCAD sketches and applies those sketches
to FreeCAD Part Design workbench Body objects.  Addition information is provided to supporting
the FreeCAD Path workbench.

The are 4 base classes of used in this module:
* ApexDrawing: Create one or more FreeCAD Sketches and applies Part Design and Path operations.
* ApexShape: This is the geometric shapes that go into the ApexDrawing.
* ApexOperation: This is the Part Design and Path operation information.
* ApexFeature: This is an internal class used to construct a fully constrained FreeCAD sketch.

The ApexShape sub-classes are:
* ApexCircle: This represents a circle in the ApexDrawing.
* ApexPolygon: This is basically a sequence of ApexCorner's (see below) that represent a polygon,
  where each corner can optionally have rounded with a fillet.
* ApexCorner: This represents one corner of an ApexPolygon and specifies the fillet radius.
Each ApexShape has an associated ApexOperation (see below).

There is a rich set of FreeCAD PartDesign operations that can be applied to sketches.
The construction operations are pad, revolve, loft, sweep and helix.
The subtraction operations are pocket, hole, groove, loft, sweep and helix.

The current ApexOperation sub-classes are:
* ApexPad: Performs a FreeCAD Part Design pad operation.
* ApexPocket: Performs a FreeCAD Part Design pocket operation
* ApexHole: Performs a FreeCAD Part Design pocket operation

All of this information is collected into an ApexDrawing instance.
The ApexDrawing.body_apply() takes a FreeCAD Part Design Body and applies operations drawing to it.

## 2 Class ApexArcFeature <a name="apexarcfeature"></a>

class ApexArcFeature(ApexFeature):

Represents an an arc in a sketch.

### 2.1 ApexArcFeature.\_\_init\_\_ <a name="apexarcfeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  "ApexDrawing", *begin*:  ApexCorner, *at*:  ApexCorner, *end*:  ApexCorner, *name*:  *str* = "", *tracing*:  *str* = "") -> None:

Initialize an ApexArcFeature.

### 2.2 ApexArcFeature.\_\_str\_\_ <a name="apexarcfeature---str--"></a>

def \_\_str\_\_(self) -> *str*:

Return string reprentation of ApexFeature.

### 2.3 ApexArcFeature.apex <a name="apexarcfeature-apex"></a>

def *at*(self) -> Vector:

Return the ApexArcFeature apex Vector.

### 2.4 ApexArcFeature.begin <a name="apexarcfeature-begin"></a>

def *begin*(self) -> Vector:  # *pragma*:  *no* *unit* *test*

Return the ApexArcFeature arc begin Vector.

### 2.5 ApexArcFeature.center <a name="apexarcfeature-center"></a>

def *center*(self) -> Vector:

Return the ApexArcFeature arc center.

### 2.6 ApexArcFeature.end <a name="apexarcfeature-end"></a>

def *end*(self) -> Vector:  # *pragma*:  *no* *unit* *test*

Return the initial ApexArcFeature end Vector.

### 2.7 ApexArcFeature.finish <a name="apexarcfeature-finish"></a>

def *finish*(self) -> Vector:

Return the ApexArcFeature arc finish Vector.

### 2.8 ApexArcFeature.finish\_angle <a name="apexarcfeature-finish-angle"></a>

def *finish\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ApexArcFeature arc finish angle.

### 2.9 ApexArcFeature.finish\_key <a name="apexarcfeature-finish-key"></a>

def *finish\_key*(self) -> *int*:

Return the ApexArcFeature finish Constraint key.

### 2.10 ApexArcFeature.finish\_length <a name="apexarcfeature-finish-length"></a>

def *finish\_length*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return distance from arc finish Vector to the apex Vector.

### 2.11 ApexArcFeature.input <a name="apexarcfeature-input"></a>

def *input*(self) -> Vector:  # *pragma*:  *no* *unit* *test*

Return the initial ApexArcFeature arc start Vector.

### 2.12 ApexArcFeature.part\_feature <a name="apexarcfeature-part-feature"></a>

def *part\_feature*(self) -> PartFeature:

Return ApexArcFeature Part.Arc.

### 2.13 ApexArcFeature.radius <a name="apexarcfeature-radius"></a>

def *radius*(self) -> *float*:

Return the initial ApexArcFeature radius.

### 2.14 ApexArcFeature.repr <a name="apexarcfeature-repr"></a>

def \_\_repr\_\_(self) -> *str*:  # *pragma*:  *no* *unit* *test*

Return ApexArcFeature string representation.

### 2.15 ApexArcFeature.start <a name="apexarcfeature-start"></a>

def *start*(self) -> Vector:

Return the ApexArcFeature arc start Vector.

### 2.16 ApexArcFeature.start\_angle <a name="apexarcfeature-start-angle"></a>

def *start\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ApexArcFeature arc start angle.

### 2.17 ApexArcFeature.start\_key <a name="apexarcfeature-start-key"></a>

def *start\_key*(self) -> *int*:

Return the ApexArcFeature finish Constraint key.

### 2.18 ApexArcFeature.start\_length <a name="apexarcfeature-start-length"></a>

def *start\_length*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ApexArcFeature distance from start Vector to apex Vector.

### 2.19 ApexArcFeature.sweep\_angle <a name="apexarcfeature-sweep-angle"></a>

def *sweep\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *cover*

Return the ApexArcFeature sweep angle from start angle to end angle.

### 2.20 ApexArcFeature.type\_name <a name="apexarcfeature-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexArcFeature type name.

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

Return the ApexCircleFeature constraints.

### 3.3 ApexCircle.features\_get <a name="apexcircle-features-get"></a>

def *features\_get*(self, *drawing*:  "ApexDrawing", *tracing*:  *str* = "") -> Tuple[ApexFeature, ...]:

Return the ApexCircleFeature.

### 3.4 ApexCircle.reorient <a name="apexcircle-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  Optional[str] = "", *tracing*:  *str* = "") -> "ApexCircle":

Return a new reoriented ApexCircle.

Arguments:
* *placement* (Placement): The FreeCAD Placement reorient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")


## 4 Class ApexCircleFeature <a name="apexcirclefeature"></a>

class ApexCircleFeature(ApexFeature):

Represents a circle in a sketch.

### 4.1 ApexCircleFeature.\_\_init\_\_ <a name="apexcirclefeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  "ApexDrawing", *center*:  Vector, *radius*:  *float*, *name*:  *str* = "") -> None:

Initialize a ApexCircleFeature.

### 4.2 ApexCircleFeature.center <a name="apexcirclefeature-center"></a>

def *center*(self) -> Vector:  # *pragma*:  *no* *unit* *cover*

Return the ApexCircleFeature center.

### 4.3 ApexCircleFeature.part\_element <a name="apexcirclefeature-part-element"></a>

def *part\_feature*(self) -> PartFeature:

Return the ApexCircleFeature PartFeature.

### 4.4 ApexCircleFeature.radius <a name="apexcirclefeature-radius"></a>

def *radius*(self) -> *float*:  # *pragma*:  *no* *unit* *cover*

Return the ApexCircleFeature radius.

### 4.5 ApexCircleFeature.type\_name <a name="apexcirclefeature-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexCircleFeature type name.

## 5 Class ApexCorner <a name="apexcorner"></a>

class ApexCorner(object):

ApexCorner: An ApexPolygon corner with a radius.

Usage: ApexCorner(point, radius, name)

Attributes:
* *Point* (Vector): A point for a polygon.
* *Radius (float): The corner radius in millmeters.  (Default: 0.0)
* *Name* (str): The corner name. (Default: "")
* *Box* (ApexBox): Box that encloses the corner as if it was a sphere of size Radis.


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

def *create\_datum\_plane*(self, *body*:  "PartDesign.Body", *name*:  Optional[str] = None, *tracing*:  *str* = "") -> "Part.ApexFeature":

Return the FreeCAD DatumPlane used for the drawing.

Arguments:
* *body* (PartDesign.Body): The FreeCAD Part design Body to attach the datum plane to.
* *name* (Optional[str]): The datum plane name.
  (Default: "...DatumPlaneN", where N is incremented.)
* Returns:
  * (Part.ApexFeature) that is the datum\_plane.

### 6.3 ApexDrawing.features\_get <a name="apexdrawing-features-get"></a>

def *point\_features\_get*(self, *point*:  Vector, *tracing*:  *str* = "") -> Tuple["ApexFeature", ...]:

Return the ApexPointFeature Feature's.

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

## 7 Class ApexFeature <a name="apexfeature"></a>

class ApexFeature(object):

Base class a sketch feature.

### 7.1 ApexFeature.\_\_init\_\_ <a name="apexfeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  "ApexDrawing", *start*:  Vector, *finish*:  Vector, *name*:  *str* = "") -> None:

Initialize a ApexFeature.

### 7.2 ApexFeature.\_\_repr\_\_ <a name="apexfeature---repr--"></a>

def \_\_repr\_\_(self) -> *str*:

Return string reprentation of ApexFeature.

### 7.3 ApexFeature.\_\_str\_\_ <a name="apexfeature---str--"></a>

def \_\_str\_\_(self) -> *str*:

Return string reprentation of ApexFeature.

### 7.4 ApexFeature.constraints\_append <a name="apexfeature-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  "ApexDrawing", *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Append the ApexShape constraints to drawing.

Arguments:
* *drawing* (ApexDrawing): The drawing to use.
* *constraints* (List[SketcherConstraint]): The constraints list to append to.


### 7.5 ApexFeature.drawing <a name="apexfeature-drawing"></a>

def *drawing*(self) -> "ApexDrawing":  # *pragma*:  *no* *unit* *test*

Return the ApexFeature ApexDrawing.

### 7.6 ApexFeature.finish <a name="apexfeature-finish"></a>

def *finish*(self) -> Vector:  # *pragma*:  *no* *unit* *test*

Return the ApexFeature finish point.

### 7.7 ApexFeature.index <a name="apexfeature-index"></a>

def *index*(self) -> *int*:

Return the ApexFeature index.

### 7.8 ApexFeature.name <a name="apexfeature-name"></a>

def *name*(self) -> *str*:

Return ApexFeature name.

### 7.9 ApexFeature.part\_feature <a name="apexfeature-part-feature"></a>

def *part\_feature*(self) -> PartFeature:

Return the PartFeature associated with ApexFeature.

### 7.10 ApexFeature.previous <a name="apexfeature-previous"></a>

def *previous*(self) -> "ApexFeature":  # *pragma*:  *no* *unit* *test*

Return the previous Part ApexFeature in circular list.

### 7.11 ApexFeature.start <a name="apexfeature-start"></a>

def *start*(self) -> Vector:  # *pragma*:  *no* *unit* *test*

Return the ApexFeature start point.

### 7.12 ApexFeature.type\_name <a name="apexfeature-type-name"></a>

def *type\_name*(self) -> *str*:

Return the ApexFeature type name.

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

def *body\_apply*(self, *body*:  "PartDesign.Body", *group\_name*:  *str*, *sketch*:  "Sketcher.SketchObject", *gui\_document*:  Optional["Gui.ActiveDocument"]) -> None:

Apply hole operation to PartDesign body.

### 8.3 ApexHole.constraints\_append <a name="apexhole-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  "ApexDrawing", *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Append the ApexOperation constraints to drawing.

Arguments:
* *drawing* (ApexDrawing): The drawing to use.
* *constraints* (List[SketcherConstraint]): The constraints list to append to.


### 8.4 ApexHole.features\_get <a name="apexhole-features-get"></a>

def *features\_get*(self, *drawing*:  "ApexDrawing", *tracing*:  *str* = "") -> Tuple[ApexFeature, ...]:

Return the ApexHole drawing features.

### 8.5 ApexHole.reorient <a name="apexhole-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  *str* = None, *tracing*:  *str* = "") -> "ApexHole":

Reorient an ApexHole.

Arguments:
* *placement* (Placement): The FreeCAD Placement to reorient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")


### 8.6 ApexHole.shape\_get <a name="apexhole-shape-get"></a>

def *shape\_get*(self) -> ApexShape:

Return the ApexHole ApexShape.

## 9 Class ApexLineFeature <a name="apexlinefeature"></a>

class ApexLineFeature(ApexFeature):

Represents a line segment in a sketch.

### 9.1 ApexLineFeature.\_\_init\_\_ <a name="apexlinefeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  "ApexDrawing", *start*:  Vector, *finish*:  Vector, *name*:  *str* = "", *tracing*:  *str* = "") -> None:

Initialize a ApexLineFeature.

### 9.2 ApexLineFeature.\_\_repr\_\_ <a name="apexlinefeature---repr--"></a>

def \_\_repr\_\_(self) -> *str*:

Return string representation of ApexLineFeature.

### 9.3 ApexLineFeature.\_\_str\_\_ <a name="apexlinefeature---str--"></a>

def \_\_str\_\_(self) -> *str*:

Return string representation of ApexLineFeature.

### 9.4 ApexLineFeature.drawing <a name="apexlinefeature-drawing"></a>

def *drawing*(self) -> "ApexDrawing":  # *pragma*:  *no* *unit* *cover*

Return the ApexLineFeature ApexDrawing.

### 9.5 ApexLineFeature.finish <a name="apexlinefeature-finish"></a>

def *finish*(self) -> Vector:  # *pragma*:  *no* *unit* *cover*

Return the ApexLineFeature finish Vector.

### 9.6 ApexLineFeature.finish\_key <a name="apexlinefeature-finish-key"></a>

def *finish\_key*(self) -> *int*:

Return the ApexLineFeature finish Constraint key.

### 9.7 ApexLineFeature.part\_feature <a name="apexlinefeature-part-feature"></a>

def *part\_feature*(self) -> PartFeature:

Return the PartFeature associated with a ApexLineFeature.

### 9.8 ApexLineFeature.start <a name="apexlinefeature-start"></a>

def *start*(self) -> ApexCorner:

Return the ApexLineFeature start Vector.

### 9.9 ApexLineFeature.start\_key <a name="apexlinefeature-start-key"></a>

def *start\_key*(self) -> *int*:

Return the ApexLineFeature start Constraint key.

### 9.10 ApexLineFeature.type\_name <a name="apexlinefeature-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexLineFeature type name.

## 10 Class ApexOperation <a name="apexoperation"></a>

class ApexOperation(object):

Represents a FreeCAD Part Design workbench operation.

This is a base class for ApexHole, ApexPad, and ApexPocket.

Attributes:
* *SortKey*: (Tuple[str, ...]): A key generated by sub-class used to sort ApexOpertions.


### 10.1 ApexOperation.body\_apply <a name="apexoperation-body-apply"></a>

def *body\_apply*(self, *body*:  "PartDesign.Body", *group\_name*:  *str*, *sketch*:  "Sketcher.SketchObject", *gui\_document*:  Optional["Gui.ActiveDocument"]) -> None:

Apply operation to a Part Design body.

### 10.2 ApexOperation.constraints\_append <a name="apexoperation-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  "ApexDrawing", *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Append the ApexOperation constraints to drawing.

Arguments:
* *drawing* (ApexDrawing): The drawing to use.
* *constraints* (List[SketcherConstraint]): The constraints list to append to.


### 10.3 ApexOperation.features\_get <a name="apexoperation-features-get"></a>

def *features\_get*(self, *drawing*:  "ApexDrawing", *tracing*:  *str* = "") -> Tuple[ApexFeature, ...]:

Return the features associated with an operation.

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

def *body\_apply*(self, *body*:  "PartDesign.Body", *group\_name*:  *str*, *sketch*:  "Sketcher.SketchObject", *gui\_document*:  Optional["Gui.ActiveDocument"]) -> None:

Apply ApexPad opertation to PartDesign Body.

### 11.3 ApexPad.constraints\_append <a name="apexpad-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  "ApexDrawing", *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Append the ApexOperation constraints to drawing.

Arguments:
* *drawing* (ApexDrawing): The drawing to use.
* *constraints* (List[SketcherConstraint]): The constraints list to append to.


### 11.4 ApexPad.features\_get <a name="apexpad-features-get"></a>

def *features\_get*(self, *drawing*:  "ApexDrawing", *tracing*:  *str* = "") -> Tuple[ApexFeature, ...]:

Return the features associated with an operation.

### 11.5 ApexPad.reorient <a name="apexpad-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  *str* = None, *tracing*:  *str* = "") -> "ApexPad":

Reorient an ApexPad .

Arguments:
* *placement* (Placement): The FreeCAD Placement reorient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")


### 11.6 ApexPad.shape\_get <a name="apexpad-shape-get"></a>

def *shape\_get*(self) -> ApexShape:

Return the associated ApexShape's.

### 11.7 ApexPad.shape\_get <a name="apexpad-shape-get"></a>

def *shape\_get*(self) -> ApexShape:

Return the ApexPad ApexShape.

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

def *body\_apply*(self, *body*:  "PartDesign.Body", *group\_name*:  *str*, *sketch*:  "Sketcher.SketchObject", *gui\_document*:  Optional["Gui.ActiveDocument"]) -> None:

Apply pocket operation to PartDesign Body.

### 12.3 ApexPocket.constraints\_append <a name="apexpocket-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  "ApexDrawing", *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Append the ApexPocket constraints to drawing.

Arguments:
* *drawing* (ApexDrawing): The drawing to use.
* *constraints* (List[SketcherConstraint]): The constraints list to append to.


## 13 Class ApexPointFeature <a name="apexpointfeature"></a>

class ApexPointFeature(ApexFeature):

Represents a point in a sketch.

### 13.1 ApexPointFeature.\_\_init\_\_ <a name="apexpointfeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  "ApexDrawing", *point*:  Vector, *name*:  *str* = "") -> None:

Initialize a ApexPointFeature.

### 13.2 ApexPointFeature.\_\_str\_\_ <a name="apexpointfeature---str--"></a>

def \_\_str\_\_(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return ApexPointFeature string .

### 13.3 ApexPointFeature.part\_feature <a name="apexpointfeature-part-feature"></a>

def *part\_feature*(self) -> PartFeature:

Return the  ApexPointFeature.

### 13.4 ApexPointFeature.point <a name="apexpointfeature-point"></a>

def *point*(self) -> Vector:  # *pragma*:  *no* *unit* *cover*

Return the ApexPointFeature Vector.

### 13.5 ApexPointFeature.type\_name <a name="apexpointfeature-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexPointFeature type name.

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


### 14.4 ApexPolygon.constraints\_append <a name="apexpolygon-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  "ApexDrawing", *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Return the ApexPolygon constraints for a ApexDrawing.

### 14.5 ApexPolygon.features\_get <a name="apexpolygon-features-get"></a>

def *features\_get*(self, *drawing*:  "ApexDrawing", *tracing*:  *str* = "") -> Tuple[ApexFeature, ...]:

Return the ApexPolygon ApexFeatures tuple.

### 14.6 ApexPolygon.reorient <a name="apexpolygon-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  Optional[str] = "", *tracing*:  *str* = "") -> "ApexPolygon":

Reorient an ApexPolygon with a new Placement.

Arguments:
* *placement* (Placement):
  The FreeCAD Placement to reorient with.
* *suffix* (Optional[str]):
  A suffix to append to the name.  If None, an empty name is used. (Default: "")


### 14.7 ApexPolygon.show <a name="apexpolygon-show"></a>

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


### 15.2 ApexShape.features\_get <a name="apexshape-features-get"></a>

def *features\_get*(self, *drawing*:  "ApexDrawing", *tracing*:  *str* = "") -> Tuple[ApexFeature, ...]:

Return the ApexShape ApexFeatures tuple.

Arguments:
* *drawing* (ApexDrawing): The associated drawing to use for feature extraction.

Returns:
* (Tuple[ApexFeature, ...]) of extracted ApexFeature's.


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
