# ShopFab: A shop based design workflow.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class ApexArcFeature](#apexarcfeature)
  * 2.1 [ApexArcFeature.\_\_init\_\_](#apexarcfeature---init--)
  * 2.2 [ApexArcFeature.apex](#apexarcfeature-apex)
  * 2.3 [ApexArcFeature.begin](#apexarcfeature-begin)
  * 2.4 [ApexArcFeature.center](#apexarcfeature-center)
  * 2.5 [ApexArcFeature.end](#apexarcfeature-end)
  * 2.6 [ApexArcFeature.finish](#apexarcfeature-finish)
  * 2.7 [ApexArcFeature.finish\_angle](#apexarcfeature-finish-angle)
  * 2.8 [ApexArcFeature.finish\_key](#apexarcfeature-finish-key)
  * 2.9 [ApexArcFeature.finish\_length](#apexarcfeature-finish-length)
  * 2.10 [ApexArcFeature.input](#apexarcfeature-input)
  * 2.11 [ApexArcFeature.part\_feature](#apexarcfeature-part-feature)
  * 2.12 [ApexArcFeature.radius](#apexarcfeature-radius)
  * 2.13 [ApexArcFeature.repr](#apexarcfeature-repr)
  * 2.14 [ApexArcFeature.start](#apexarcfeature-start)
  * 2.15 [ApexArcFeature.start\_angle](#apexarcfeature-start-angle)
  * 2.16 [ApexArcFeature.start\_key](#apexarcfeature-start-key)
  * 2.17 [ApexArcFeature.start\_length](#apexarcfeature-start-length)
  * 2.18 [ApexArcFeature.sweep\_angle](#apexarcfeature-sweep-angle)
  * 2.19 [ApexArcFeature.type\_name](#apexarcfeature-type-name)
  * 2.20 [ApexCircle.\_\_init](#apexcircle---init)
  * 2.21 [ApexCircle.bounding\_box](#apexcircle-bounding-box)
  * 2.22 [ApexCircle.center](#apexcircle-center)
  * 2.23 [ApexCircle.circle\_feature](#apexcircle-circle-feature)
  * 2.24 [ApexCircle.constraints\_append](#apexcircle-constraints-append)
  * 2.25 [ApexCircle.depth](#apexcircle-depth)
  * 2.26 [ApexCircle.features\_get](#apexcircle-features-get)
  * 2.27 [ApexCircle.flat](#apexcircle-flat)
  * 2.28 [ApexCircle.forward\_transform](#apexcircle-forward-transform)
  * 2.29 [ApexCircle.name](#apexcircle-name)
  * 2.30 [ApexCircle.radius](#apexcircle-radius)
* 3 [Class ApexCircleFeature](#apexcirclefeature)
  * 3.1 [ApexCircleFeature.\_\_init\_\_](#apexcirclefeature---init--)
  * 3.2 [ApexCircleFeature.\_\_repr\_\_](#apexcirclefeature---repr--)
  * 3.3 [ApexCircleFeature.center](#apexcirclefeature-center)
  * 3.4 [ApexCircleFeature.part\_element](#apexcirclefeature-part-element)
  * 3.5 [ApexCircleFeature.radius](#apexcirclefeature-radius)
  * 3.6 [ApexCircleFeature.type\_name](#apexcirclefeature-type-name)
* 4 [Class ApexDrawing](#apexdrawing)
  * 4.1 [ApexDrawing.\_\_init\_\_](#apexdrawing---init--)
  * 4.2 [ApexDrawing.bounding\_box](#apexdrawing-bounding-box)
  * 4.3 [ApexDrawing.circles](#apexdrawing-circles)
  * 4.4 [ApexDrawing.features\_get](#apexdrawing-features-get)
  * 4.5 [ApexDrawing.forward\_transform](#apexdrawing-forward-transform)
  * 4.6 [ApexDrawing.name](#apexdrawing-name)
  * 4.7 [ApexDrawing.origin\_index](#apexdrawing-origin-index)
  * 4.8 [ApexDrawing.point\_constraints\_append](#apexdrawing-point-constraints-append)
  * 4.9 [ApexDrawing.polygons](#apexdrawing-polygons)
  * 4.10 [ApexDrawing.sketch](#apexdrawing-sketch)
* 5 [Class ApexFeature](#apexfeature)
  * 5.1 [ApexFeature.\_\_init\_\_](#apexfeature---init--)
  * 5.2 [ApexFeature.drawing](#apexfeature-drawing)
  * 5.3 [ApexFeature.finish](#apexfeature-finish)
  * 5.4 [ApexFeature.index](#apexfeature-index)
  * 5.5 [ApexFeature.name](#apexfeature-name)
  * 5.6 [ApexFeature.part\_feature](#apexfeature-part-feature)
  * 5.7 [ApexFeature.previous](#apexfeature-previous)
  * 5.8 [ApexFeature.start](#apexfeature-start)
  * 5.9 [ApexFeature.type\_name](#apexfeature-type-name)
* 6 [Class ApexLineFeature](#apexlinefeature)
  * 6.1 [ApexLineFeature.\_\_init\_\_](#apexlinefeature---init--)
  * 6.2 [ApexLineFeature.drawing](#apexlinefeature-drawing)
  * 6.3 [ApexLineFeature.finish](#apexlinefeature-finish)
  * 6.4 [ApexLineFeature.finish\_key](#apexlinefeature-finish-key)
  * 6.5 [ApexLineFeature.part\_feature](#apexlinefeature-part-feature)
  * 6.6 [ApexLineFeature.start](#apexlinefeature-start)
  * 6.7 [ApexLineFeature.start\_key](#apexlinefeature-start-key)
  * 6.8 [ApexLineFeature.type\_name](#apexlinefeature-type-name)
* 7 [Class ApexPointFeature](#apexpointfeature)
  * 7.1 [ApexPointFeature.\_\_init\_\_](#apexpointfeature---init--)
  * 7.2 [ApexPointFeature.\_\_str\_\_](#apexpointfeature---str--)
  * 7.3 [ApexPointFeature.part\_feature](#apexpointfeature-part-feature)
  * 7.4 [ApexPointFeature.point](#apexpointfeature-point)
  * 7.5 [ApexPointFeature.type\_name](#apexpointfeature-type-name)
* 8 [Class ApexPolygon](#apexpolygon)
  * 8.1 [ApexPolygon.\_\_init\_\_](#apexpolygon---init--)
  * 8.2 [ApexPolygon.bounding\_box](#apexpolygon-bounding-box)
  * 8.3 [ApexPolygon.clockwise](#apexpolygon-clockwise)
  * 8.4 [ApexPolygon.constraints\_append](#apexpolygon-constraints-append)
  * 8.5 [ApexPolygon.depth](#apexpolygon-depth)
  * 8.6 [ApexPolygon.features\_get](#apexpolygon-features-get)
  * 8.7 [ApexPolygon.flat](#apexpolygon-flat)
  * 8.8 [ApexPolygon.name](#apexpolygon-name)
  * 8.9 [ApexPolygon.points](#apexpolygon-points)

## 1 <a name="introduction"></a>Introduction


## 2 Class ApexArcFeature <a name="apexarcfeature"></a>

class ApexArcFeature(ApexFeature):

Represents an an arc in a sketch.

### 2.1 ApexArcFeature.\_\_init\_\_ <a name="apexarcfeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  ApexDrawing, *begin*:  ApexPoint, *apex*:  ApexPoint, *end*:  ApexPoint, *name*:  *str* = "", *tracing*:  *str* = "") -> None:

Initialize an ApexArcFeature.

### 2.2 ApexArcFeature.apex <a name="apexarcfeature-apex"></a>

def *apex*(self) -> ApexPoint:

Return the ApexArcFeature apex ApexPoint.

### 2.3 ApexArcFeature.begin <a name="apexarcfeature-begin"></a>

def *begin*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *test*

Return the ApexArcFeature arc begin ApexPoint.

### 2.4 ApexArcFeature.center <a name="apexarcfeature-center"></a>

def *center*(self) -> ApexPoint:

Return the ApexArcFeature arc center.

### 2.5 ApexArcFeature.end <a name="apexarcfeature-end"></a>

def *end*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *test*

Return the initial ApexArcFeature end ApexPoint.

### 2.6 ApexArcFeature.finish <a name="apexarcfeature-finish"></a>

def *finish*(self) -> ApexPoint:

Return the ApexArcFeature arc finish ApexPoint.

### 2.7 ApexArcFeature.finish\_angle <a name="apexarcfeature-finish-angle"></a>

def *finish\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ApexArcFeature arc finish angle.

### 2.8 ApexArcFeature.finish\_key <a name="apexarcfeature-finish-key"></a>

def *finish\_key*(self) -> *int*:

Return the ApexArcFeature finish Constraint key.

### 2.9 ApexArcFeature.finish\_length <a name="apexarcfeature-finish-length"></a>

def *finish\_length*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return distance from arc finish ApexPoint to the apex ApexPoint.

### 2.10 ApexArcFeature.input <a name="apexarcfeature-input"></a>

def *input*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *test*

Return the initial ApexArcFeature arc start ApexPoint.

### 2.11 ApexArcFeature.part\_feature <a name="apexarcfeature-part-feature"></a>

def *part\_feature*(self) -> PartFeature:

Return ApexArcFeature Part.Arc.

### 2.12 ApexArcFeature.radius <a name="apexarcfeature-radius"></a>

def *radius*(self) -> *float*:

Return the initial ApexArcFeature radius.

### 2.13 ApexArcFeature.repr <a name="apexarcfeature-repr"></a>

def \_\_repr\_\_(self) -> *str*:  # *pragma*:  *no* *unit* *test*

Return ApexArcFeature string representation.

### 2.14 ApexArcFeature.start <a name="apexarcfeature-start"></a>

def *start*(self) -> ApexPoint:

Return the ApexArcFeature arc start ApexPoint.

### 2.15 ApexArcFeature.start\_angle <a name="apexarcfeature-start-angle"></a>

def *start\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ApexArcFeature arc start angle.

### 2.16 ApexArcFeature.start\_key <a name="apexarcfeature-start-key"></a>

def *start\_key*(self) -> *int*:

Return the ApexArcFeature finish Constraint key.

### 2.17 ApexArcFeature.start\_length <a name="apexarcfeature-start-length"></a>

def *start\_length*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ApexArcFeature distance from start ApexPoint to apex ApexPoint.

### 2.18 ApexArcFeature.sweep\_angle <a name="apexarcfeature-sweep-angle"></a>

def *sweep\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *cover*

Return the ApexArcFeature sweep angle from start angle to end angle.

### 2.19 ApexArcFeature.type\_name <a name="apexarcfeature-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexArcFeature type name.

### 2.20 ApexCircle.\_\_init <a name="apexcircle---init"></a>

def \_\_init\_\_( *self*, *center*:  ApexPoint, *depth*:  *float* = 0.0, *flat*:  *bool* = False, *name*:  *str* = "" ) -> None:

Initialize a circle.

### 2.21 ApexCircle.bounding\_box <a name="apexcircle-bounding-box"></a>

def *bounding\_box*(self) -> ApexBoundBox:

Return the ApexCircle ApexBoundBox.

### 2.22 ApexCircle.center <a name="apexcircle-center"></a>

def *center*(self) -> ApexPoint:

Return the ApexCircle center ApexPoint.

### 2.23 ApexCircle.circle\_featu <a name="apexcircle-circle-feature"></a>

def *circle\_feature*(self) -> ApexCircleFeature:

Return the ApexCircle ApexCircleFeature.

### 2.24 ApexCircle.constraints\_append <a name="apexcircle-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  ApexDrawing, *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Return the ApexCircleFeature constraints.

### 2.25 ApexCircle.depth <a name="apexcircle-depth"></a>

def *depth*(self) -> *float*:

Return the ApexCircle Depth.

### 2.26 ApexCircle.features\_get <a name="apexcircle-features-get"></a>

def *features\_get*(self, *drawing*:  ApexDrawing) -> Tuple[ApexFeature, ...]:

Return the ApexCircleFeature.

### 2.27 ApexCircle.flat <a name="apexcircle-flat"></a>

def *flat*(self) -> *bool*:

Return whether the ApexCircle bottom is flat.

### 2.28 ApexCircle.forward\_transform <a name="apexcircle-forward-transform"></a>

def *forward\_transform*(self, *matrix*:  ApexPlace) -> "ApexCircle":

Return a forward transformed ApexCircle.

### 2.29 ApexCircle.name <a name="apexcircle-name"></a>

def *name*(self) -> *str*:

Return the name of the ApexCircle.

### 2.30 ApexCircle.radius <a name="apexcircle-radius"></a>

def *radius*(self) -> *float*:

Return the ApexCircle radius.

## 3 Class ApexCircleFeature <a name="apexcirclefeature"></a>

class ApexCircleFeature(ApexFeature):

Represents a circle in a sketch.

### 3.1 ApexCircleFeature.\_\_init\_\_ <a name="apexcirclefeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  ApexDrawing, *center*:  ApexPoint, *radius*:  *float*, *name*:  *str* = "") -> None:

Initialize a ApexCircleFeature.

### 3.2 ApexCircleFeature.\_\_repr\_\_ <a name="apexcirclefeature---repr--"></a>

def \_\_repr\_\_(self) -> *str*:

Return a string representation of ApexCircle.

### 3.3 ApexCircleFeature.center <a name="apexcirclefeature-center"></a>

def *center*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *cover*

Return the ApexCircleFeature center.

### 3.4 ApexCircleFeature.part\_element <a name="apexcirclefeature-part-element"></a>

def *part\_feature*(self) -> PartFeature:

Return the ApexCircleFeature PartFeature.

### 3.5 ApexCircleFeature.radius <a name="apexcirclefeature-radius"></a>

def *radius*(self) -> *float*:  # *pragma*:  *no* *unit* *cover*

Return the ApexCircleFeature radius.

### 3.6 ApexCircleFeature.type\_name <a name="apexcirclefeature-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexCircleFeature type name.

## 4 Class ApexDrawing <a name="apexdrawing"></a>

class ApexDrawing(object):

Represents a 2D drawing.

### 4.1 ApexDrawing.\_\_init\_\_ <a name="apexdrawing---init--"></a>

def \_\_init\_\_( *self*, *circles*:  Tuple["ApexCircle", ...], *polygons*:  Tuple["ApexPolygon", ...], *name*:  *str* = "" ) -> None:

Initialize a drawing.

### 4.2 ApexDrawing.bounding\_box <a name="apexdrawing-bounding-box"></a>

def *bounding\_box*(self) -> ApexBoundBox:

Return the ApexDrawing ApexBoundBox.

### 4.3 ApexDrawing.circles <a name="apexdrawing-circles"></a>

def *circles*(self) -> Tuple["ApexCircle", ...]:  # *pragma*:  *no* *unit* *test*

Return the ApexDrawing Circle's.

### 4.4 ApexDrawing.features\_get <a name="apexdrawing-features-get"></a>

def *point\_features\_get*(self, *point*:  ApexPoint, *tracing*:  *str* = "") -> Tuple["ApexFeature", ...]:

Return the ApexPointFeature Feature's.

### 4.5 ApexDrawing.forward\_transform <a name="apexdrawing-forward-transform"></a>

def *forward\_transform*(self, *matrix*:  ApexPlace) -> "ApexDrawing":

Return an ApexDrawing that is offset via a forward transform.

### 4.6 ApexDrawing.name <a name="apexdrawing-name"></a>

def *name*(self) -> *str*:

Return the ApexDrawing name.

### 4.7 ApexDrawing.origin\_index <a name="apexdrawing-origin-index"></a>

def *origin\_index*(self) -> *int*:

Return the ApexDrawing origin index.

### 4.8 ApexDrawing.point\_constraints\_append <a name="apexdrawing-point-constraints-append"></a>

def *point\_constraints\_append*(self, *point*:  ApexPoint, *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:  # REMOVE

Append ApexPoint constraints to a list.

### 4.9 ApexDrawing.polygons <a name="apexdrawing-polygons"></a>

def *polygons*(self) -> Tuple["ApexPolygon", ...]:  # *pragma*:  *no* *unit* *test*

Return the ApexDrawing ApexPolygon's.

### 4.10 ApexDrawing.sketch <a name="apexdrawing-sketch"></a>

def *sketch*(self, *sketcher*:  "Sketcher.SketchObject", *lower\_left*:  ApexPoint, *tracing*:  *str* = "") -> None:

Sketch a ApexDrawing.

## 5 Class ApexFeature <a name="apexfeature"></a>

class ApexFeature(object):

Base class a schematic features.

### 5.1 ApexFeature.\_\_init\_\_ <a name="apexfeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  ApexDrawing, *start*:  ApexPoint, *finish*:  ApexPoint, *name*:  *str* = "") -> None:

Initialize a ApexFeature.

### 5.2 ApexFeature.drawing <a name="apexfeature-drawing"></a>

def *drawing*(self) -> ApexDrawing:  # *pragma*:  *no* *unit* *test*

Return the ApexFeature ApexDrawing.

### 5.3 ApexFeature.finish <a name="apexfeature-finish"></a>

def *finish*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *test*

Return the ApexFeature finish point.

### 5.4 ApexFeature.index <a name="apexfeature-index"></a>

def *index*(self) -> *int*:

Return the ApexFeature index.

### 5.5 ApexFeature.name <a name="apexfeature-name"></a>

def *name*(self) -> *str*:

Return ApexFeature name.

### 5.6 ApexFeature.part\_feature <a name="apexfeature-part-feature"></a>

def *part\_feature*(self) -> PartFeature:

Return the PartFeature associated with ApexFeature.

### 5.7 ApexFeature.previous <a name="apexfeature-previous"></a>

def *previous*(self) -> "ApexFeature":  # *pragma*:  *no* *unit* *test*

Return the previous Part ApexFeature in circular list.

### 5.8 ApexFeature.start <a name="apexfeature-start"></a>

def *start*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *test*

Return the ApexFeature start point.

### 5.9 ApexFeature.type\_name <a name="apexfeature-type-name"></a>

def *type\_name*(self) -> *str*:

Return the ApexFeature type name.

## 6 Class ApexLineFeature <a name="apexlinefeature"></a>

class ApexLineFeature(ApexFeature):

Represents a line segment in a sketch.

### 6.1 ApexLineFeature.\_\_init\_\_ <a name="apexlinefeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  ApexDrawing, *start*:  ApexPoint, *finish*:  ApexPoint, *name*:  *str* = "", *tracing*:  *str* = "") -> None:

Initialize a ApexLineFeature.

### 6.2 ApexLineFeature.drawing <a name="apexlinefeature-drawing"></a>

def *drawing*(self) -> ApexDrawing:  # *pragma*:  *no* *unit* *cover*

Return the ApexLineFeature ApexDrawing.

### 6.3 ApexLineFeature.finish <a name="apexlinefeature-finish"></a>

def *finish*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *cover*

Return the ApexLineFeature finish ApexPoint.

### 6.4 ApexLineFeature.finish\_key <a name="apexlinefeature-finish-key"></a>

def *finish\_key*(self) -> *int*:

Return the ApexLineFeature finish Constraint key.

### 6.5 ApexLineFeature.part\_feature <a name="apexlinefeature-part-feature"></a>

def *part\_feature*(self) -> PartFeature:

Return the PartFeature associated with a ApexLineFeature.

### 6.6 ApexLineFeature.start <a name="apexlinefeature-start"></a>

def *start*(self) -> ApexPoint:

Return the ApexLineFeature start ApexPoint.

### 6.7 ApexLineFeature.start\_key <a name="apexlinefeature-start-key"></a>

def *start\_key*(self) -> *int*:

Return the ApexLineFeature start Constraint key.

### 6.8 ApexLineFeature.type\_name <a name="apexlinefeature-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexLineFeature type name.

## 7 Class ApexPointFeature <a name="apexpointfeature"></a>

class ApexPointFeature(ApexFeature):

Represents a point in a sketch.

### 7.1 ApexPointFeature.\_\_init\_\_ <a name="apexpointfeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  ApexDrawing, *point*:  ApexPoint, *name*:  *str* = "") -> None:

Initialize a ApexPointFeature.

### 7.2 ApexPointFeature.\_\_str\_\_ <a name="apexpointfeature---str--"></a>

def \_\_str\_\_(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return ApexPointFeature string .

### 7.3 ApexPointFeature.part\_feature <a name="apexpointfeature-part-feature"></a>

def *part\_feature*(self) -> PartFeature:

Return the  ApexPointFeature.

### 7.4 ApexPointFeature.point <a name="apexpointfeature-point"></a>

def *point*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *cover*

Return the ApexPointFeature ApexPoint.

### 7.5 ApexPointFeature.type\_name <a name="apexpointfeature-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexPointFeature type name.

## 8 Class ApexPolygon <a name="apexpolygon"></a>

class ApexPolygon(object):

Represents a polygon with possible rounded corners.

### 8.1 ApexPolygon.\_\_init\_\_ <a name="apexpolygon---init--"></a>

def \_\_init\_\_( *self*, *points*:  Tuple[ApexPoint, ...], *depth*:  *float* = 0.0, *flat*:  *bool* = False, *name*:  *str* = "" ) -> None:

Initialize a ApexPolygon.

### 8.2 ApexPolygon.bounding\_box <a name="apexpolygon-bounding-box"></a>

def *bounding\_box*(self) -> ApexBoundBox:

Return the ApexPolygon ApexBoundBox.

### 8.3 ApexPolygon.clockwise <a name="apexpolygon-clockwise"></a>

def *clockwise*(self) -> *bool*:  # *pragma*:  *no* *unit* *cover*

Return whether the ApexPolygon points are clockwise.

### 8.4 ApexPolygon.constraints\_append <a name="apexpolygon-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  ApexDrawing, *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Return the ApexPolygon constraints for a ApexDrawing.

### 8.5 ApexPolygon.depth <a name="apexpolygon-depth"></a>

def *depth*(self) -> *float*:

Return the ApexPolygon depth.

### 8.6 ApexPolygon.features\_get <a name="apexpolygon-features-get"></a>

def *features\_get*(self, *drawing*:  ApexDrawing, *tracing*:  *str* = "") -> Tuple[ApexFeature, ...]:

Return the ApexPolygon ApexFeatures tuple.

### 8.7 ApexPolygon.flat <a name="apexpolygon-flat"></a>

def *flat*(self) -> *bool*:  # *pragma*:  *no* *unit* *cover*

Return the flat flag.

### 8.8 ApexPolygon.name <a name="apexpolygon-name"></a>

def *name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexPolygon depth.

### 8.9 ApexPolygon.points <a name="apexpolygon-points"></a>

def *points*(self) -> Tuple[ApexPoint, ...]:  # *pragma*:  *no* *unit* *cover*

Return the ApexPolygon points.
