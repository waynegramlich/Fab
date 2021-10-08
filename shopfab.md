# ShopFab: A shop based design workflow.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class ArcFeature](#arcfeature)
  * 2.1 [ArcFeature.\_\_init\_\_](#arcfeature---init--)
  * 2.2 [ArcFeature.apex](#arcfeature-apex)
  * 2.3 [ArcFeature.begin](#arcfeature-begin)
  * 2.4 [ArcFeature.center](#arcfeature-center)
  * 2.5 [ArcFeature.end](#arcfeature-end)
  * 2.6 [ArcFeature.finish](#arcfeature-finish)
  * 2.7 [ArcFeature.finish\_angle](#arcfeature-finish-angle)
  * 2.8 [ArcFeature.finish\_key](#arcfeature-finish-key)
  * 2.9 [ArcFeature.finish\_length](#arcfeature-finish-length)
  * 2.10 [ArcFeature.input](#arcfeature-input)
  * 2.11 [ArcFeature.part\_feature](#arcfeature-part-feature)
  * 2.12 [ArcFeature.radius](#arcfeature-radius)
  * 2.13 [ArcFeature.repr](#arcfeature-repr)
  * 2.14 [ArcFeature.start](#arcfeature-start)
  * 2.15 [ArcFeature.start\_angle](#arcfeature-start-angle)
  * 2.16 [ArcFeature.start\_key](#arcfeature-start-key)
  * 2.17 [ArcFeature.start\_length](#arcfeature-start-length)
  * 2.18 [ArcFeature.sweep\_angle](#arcfeature-sweep-angle)
  * 2.19 [ArcFeature.type\_name](#arcfeature-type-name)
  * 2.20 [Circle.\_\_init](#circle---init)
  * 2.21 [Circle.bounding\_box](#circle-bounding-box)
  * 2.22 [Circle.center](#circle-center)
  * 2.23 [Circle.circle\_feature](#circle-circle-feature)
  * 2.24 [Circle.constraints\_append](#circle-constraints-append)
  * 2.25 [Circle.depth](#circle-depth)
  * 2.26 [Circle.features\_get](#circle-features-get)
  * 2.27 [Circle.flat](#circle-flat)
  * 2.28 [Circle.forward\_transform](#circle-forward-transform)
  * 2.29 [Circle.name](#circle-name)
  * 2.30 [Circle.radius](#circle-radius)
* 3 [Class CircleFeature](#circlefeature)
  * 3.1 [CircleFeature.\_\_init\_\_](#circlefeature---init--)
  * 3.2 [CircleFeature.\_\_repr\_\_](#circlefeature---repr--)
  * 3.3 [CircleFeature.center](#circlefeature-center)
  * 3.4 [CircleFeature.part\_element](#circlefeature-part-element)
  * 3.5 [CircleFeature.radius](#circlefeature-radius)
  * 3.6 [CircleFeature.type\_name](#circlefeature-type-name)
* 4 [Class Drawing](#drawing)
  * 4.1 [Drawing.\_\_init\_\_](#drawing---init--)
  * 4.2 [Drawing.bounding\_box](#drawing-bounding-box)
  * 4.3 [Drawing.circles](#drawing-circles)
  * 4.4 [Drawing.features\_get](#drawing-features-get)
  * 4.5 [Drawing.forward\_transform](#drawing-forward-transform)
  * 4.6 [Drawing.name](#drawing-name)
  * 4.7 [Drawing.origin\_index](#drawing-origin-index)
  * 4.8 [Drawing.point\_constraints\_append](#drawing-point-constraints-append)
  * 4.9 [Drawing.polygons](#drawing-polygons)
  * 4.10 [Drawing.sketch](#drawing-sketch)
* 5 [Class Feature](#feature)
  * 5.1 [Feature.\_\_init\_\_](#feature---init--)
  * 5.2 [Feature.drawing](#feature-drawing)
  * 5.3 [Feature.finish](#feature-finish)
  * 5.4 [Feature.index](#feature-index)
  * 5.5 [Feature.name](#feature-name)
  * 5.6 [Feature.part\_feature](#feature-part-feature)
  * 5.7 [Feature.previous](#feature-previous)
  * 5.8 [Feature.start](#feature-start)
  * 5.9 [Feature.type\_name](#feature-type-name)
* 6 [Class LineFeature](#linefeature)
  * 6.1 [LineFeature.\_\_init\_\_](#linefeature---init--)
  * 6.2 [LineFeature.drawing](#linefeature-drawing)
  * 6.3 [LineFeature.finish](#linefeature-finish)
  * 6.4 [LineFeature.finish\_key](#linefeature-finish-key)
  * 6.5 [LineFeature.part\_feature](#linefeature-part-feature)
  * 6.6 [LineFeature.start](#linefeature-start)
  * 6.7 [LineFeature.start\_key](#linefeature-start-key)
  * 6.8 [LineFeature.type\_name](#linefeature-type-name)
* 7 [Class PointFeature](#pointfeature)
  * 7.1 [PointFeature.\_\_init\_\_](#pointfeature---init--)
  * 7.2 [PointFeature.\_\_str\_\_](#pointfeature---str--)
  * 7.3 [PointFeature.part\_feature](#pointfeature-part-feature)
  * 7.4 [PointFeature.point](#pointfeature-point)
  * 7.5 [PointFeature.type\_name](#pointfeature-type-name)
* 8 [Class Polygon](#polygon)
  * 8.1 [Polygon.\_\_init\_\_](#polygon---init--)
  * 8.2 [Polygon.bounding\_box](#polygon-bounding-box)
  * 8.3 [Polygon.clockwise](#polygon-clockwise)
  * 8.4 [Polygon.constraints\_append](#polygon-constraints-append)
  * 8.5 [Polygon.depth](#polygon-depth)
  * 8.6 [Polygon.features\_get](#polygon-features-get)
  * 8.7 [Polygon.flat](#polygon-flat)
  * 8.8 [Polygon.name](#polygon-name)
  * 8.9 [Polygon.points](#polygon-points)

## 1 <a name="introduction"></a>Introduction


## 2 Class ArcFeature <a name="arcfeature"></a>

class ArcFeature(Feature):

Represents an an arc in a sketch.

### 2.1 ArcFeature.\_\_init\_\_ <a name="arcfeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  Drawing, *begin*:  ApexPoint, *apex*:  ApexPoint, *end*:  ApexPoint, *name*:  *str* = "", *tracing*:  *str* = "") -> None:

Initialize an ArcFeature.

### 2.2 ArcFeature.apex <a name="arcfeature-apex"></a>

def *apex*(self) -> ApexPoint:

Return the ArcFeature apex ApexPoint.

### 2.3 ArcFeature.begin <a name="arcfeature-begin"></a>

def *begin*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *test*

Return the ArcFeature arc begin ApexPoint.

### 2.4 ArcFeature.center <a name="arcfeature-center"></a>

def *center*(self) -> ApexPoint:

Return the ArcFeature arc center.

### 2.5 ArcFeature.end <a name="arcfeature-end"></a>

def *end*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *test*

Return the initial ArcFeature end ApexPoint.

### 2.6 ArcFeature.finish <a name="arcfeature-finish"></a>

def *finish*(self) -> ApexPoint:

Return the ArcFeature arc finish ApexPoint.

### 2.7 ArcFeature.finish\_angle <a name="arcfeature-finish-angle"></a>

def *finish\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ArcFeature arc finish angle.

### 2.8 ArcFeature.finish\_key <a name="arcfeature-finish-key"></a>

def *finish\_key*(self) -> *int*:

Return the ArcFeature finish Constraint key.

### 2.9 ArcFeature.finish\_length <a name="arcfeature-finish-length"></a>

def *finish\_length*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return distance from arc finish ApexPoint to the apex ApexPoint.

### 2.10 ArcFeature.input <a name="arcfeature-input"></a>

def *input*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *test*

Return the initial ArcFeature arc start ApexPoint.

### 2.11 ArcFeature.part\_feature <a name="arcfeature-part-feature"></a>

def *part\_feature*(self) -> PartFeature:

Return ArcFeature Part.Arc.

### 2.12 ArcFeature.radius <a name="arcfeature-radius"></a>

def *radius*(self) -> *float*:

Return the initial ArcFeature radius.

### 2.13 ArcFeature.repr <a name="arcfeature-repr"></a>

def \_\_repr\_\_(self) -> *str*:  # *pragma*:  *no* *unit* *test*

Return ArcFeature string representation.

### 2.14 ArcFeature.start <a name="arcfeature-start"></a>

def *start*(self) -> ApexPoint:

Return the ArcFeature arc start ApexPoint.

### 2.15 ArcFeature.start\_angle <a name="arcfeature-start-angle"></a>

def *start\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ArcFeature arc start angle.

### 2.16 ArcFeature.start\_key <a name="arcfeature-start-key"></a>

def *start\_key*(self) -> *int*:

Return the ArcFeature finish Constraint key.

### 2.17 ArcFeature.start\_length <a name="arcfeature-start-length"></a>

def *start\_length*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ArcFeature distance from start ApexPoint to apex ApexPoint.

### 2.18 ArcFeature.sweep\_angle <a name="arcfeature-sweep-angle"></a>

def *sweep\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *cover*

Return the ArcFeature sweep angle from start angle to end angle.

### 2.19 ArcFeature.type\_name <a name="arcfeature-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ArcFeature type name.

### 2.20 Circle.\_\_init <a name="circle---init"></a>

def \_\_init\_\_( *self*, *center*:  ApexPoint, *depth*:  *float* = 0.0, *flat*:  *bool* = False, *name*:  *str* = "" ) -> None:

Initialize a circle.

### 2.21 Circle.bounding\_box <a name="circle-bounding-box"></a>

def *bounding\_box*(self) -> BoundingBox:

Return the Circle BoundingBox.

### 2.22 Circle.center <a name="circle-center"></a>

def *center*(self) -> ApexPoint:

Return the Circle center ApexPoint.

### 2.23 Circle.circle\_featu <a name="circle-circle-feature"></a>

def *circle\_feature*(self) -> CircleFeature:

Return the Circle CircleFeature.

### 2.24 Circle.constraints\_append <a name="circle-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  Drawing, *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Return the CircleFeature constraints.

### 2.25 Circle.depth <a name="circle-depth"></a>

def *depth*(self) -> *float*:

Return the Circle Depth.

### 2.26 Circle.features\_get <a name="circle-features-get"></a>

def *features\_get*(self, *drawing*:  Drawing) -> Tuple[Feature, ...]:

Return the CircleFeature.

### 2.27 Circle.flat <a name="circle-flat"></a>

def *flat*(self) -> *bool*:

Return whether the Circle bottom is flat.

### 2.28 Circle.forward\_transform <a name="circle-forward-transform"></a>

def *forward\_transform*(self, *matrix*:  ApexMatrix) -> "Circle":

Return a forward transformed Circle.

### 2.29 Circle.name <a name="circle-name"></a>

def *name*(self) -> *str*:

Return the name of the Circle.

### 2.30 Circle.radius <a name="circle-radius"></a>

def *radius*(self) -> *float*:

Return the Circle radius.

## 3 Class CircleFeature <a name="circlefeature"></a>

class CircleFeature(Feature):

Represents a circle in a sketch.

### 3.1 CircleFeature.\_\_init\_\_ <a name="circlefeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  Drawing, *center*:  ApexPoint, *radius*:  *float*, *name*:  *str* = "") -> None:

Initialize a CircleFeature.

### 3.2 CircleFeature.\_\_repr\_\_ <a name="circlefeature---repr--"></a>

def \_\_repr\_\_(self) -> *str*:

Return a string representation of Circle.

### 3.3 CircleFeature.center <a name="circlefeature-center"></a>

def *center*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *cover*

Return the CircleFeature center.

### 3.4 CircleFeature.part\_element <a name="circlefeature-part-element"></a>

def *part\_feature*(self) -> PartFeature:

Return the CircleFeature PartFeature.

### 3.5 CircleFeature.radius <a name="circlefeature-radius"></a>

def *radius*(self) -> *float*:  # *pragma*:  *no* *unit* *cover*

Return the CircleFeature radius.

### 3.6 CircleFeature.type\_name <a name="circlefeature-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the CircleFeature type name.

## 4 Class Drawing <a name="drawing"></a>

class Drawing(object):

Represents a 2D drawing.

### 4.1 Drawing.\_\_init\_\_ <a name="drawing---init--"></a>

def \_\_init\_\_( *self*, *circles*:  Tuple["Circle", ...], *polygons*:  Tuple["Polygon", ...], *name*:  *str* = "" ) -> None:

Initialize a drawing.

### 4.2 Drawing.bounding\_box <a name="drawing-bounding-box"></a>

def *bounding\_box*(self) -> BoundingBox:

Return the Drawing BoundingBox.

### 4.3 Drawing.circles <a name="drawing-circles"></a>

def *circles*(self) -> Tuple["Circle", ...]:  # *pragma*:  *no* *unit* *test*

Return the Drawing Circle's.

### 4.4 Drawing.features\_get <a name="drawing-features-get"></a>

def *point\_features\_get*(self, *point*:  ApexPoint, *tracing*:  *str* = "") -> Tuple["Feature", ...]:

Return the PointFeature Feature's.

### 4.5 Drawing.forward\_transform <a name="drawing-forward-transform"></a>

def *forward\_transform*(self, *matrix*:  ApexMatrix) -> "Drawing":

Return an Drawing that is offset via a forward transform.

### 4.6 Drawing.name <a name="drawing-name"></a>

def *name*(self) -> *str*:

Return the Drawing name.

### 4.7 Drawing.origin\_index <a name="drawing-origin-index"></a>

def *origin\_index*(self) -> *int*:

Return the Drawing origin index.

### 4.8 Drawing.point\_constraints\_append <a name="drawing-point-constraints-append"></a>

def *point\_constraints\_append*(self, *point*:  ApexPoint, *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:  # REMOVE

Append ApexPoint constraints to a list.

### 4.9 Drawing.polygons <a name="drawing-polygons"></a>

def *polygons*(self) -> Tuple["Polygon", ...]:  # *pragma*:  *no* *unit* *test*

Return the Drawing Polygon's.

### 4.10 Drawing.sketch <a name="drawing-sketch"></a>

def *sketch*(self, *sketcher*:  "Sketcher.SketchObject", *lower\_left*:  ApexPoint, *tracing*:  *str* = "") -> None:

Sketch a Drawing.

## 5 Class Feature <a name="feature"></a>

class Feature(object):

Base class a schematic features.

### 5.1 Feature.\_\_init\_\_ <a name="feature---init--"></a>

def \_\_init\_\_(self, *drawing*:  Drawing, *start*:  ApexPoint, *finish*:  ApexPoint, *name*:  *str* = "") -> None:

Initialize a Feature.

### 5.2 Feature.drawing <a name="feature-drawing"></a>

def *drawing*(self) -> Drawing:  # *pragma*:  *no* *unit* *test*

Return the Feature Drawing.

### 5.3 Feature.finish <a name="feature-finish"></a>

def *finish*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *test*

Return the Feature finish point.

### 5.4 Feature.index <a name="feature-index"></a>

def *index*(self) -> *int*:

Return the Feature index.

### 5.5 Feature.name <a name="feature-name"></a>

def *name*(self) -> *str*:

Return Feature name.

### 5.6 Feature.part\_feature <a name="feature-part-feature"></a>

def *part\_feature*(self) -> PartFeature:

Return the PartFeature associated with Feature.

### 5.7 Feature.previous <a name="feature-previous"></a>

def *previous*(self) -> "Feature":  # *pragma*:  *no* *unit* *test*

Return the previous Part Feature in circular list.

### 5.8 Feature.start <a name="feature-start"></a>

def *start*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *test*

Return the Feature start point.

### 5.9 Feature.type\_name <a name="feature-type-name"></a>

def *type\_name*(self) -> *str*:

Return the Feature type name.

## 6 Class LineFeature <a name="linefeature"></a>

class LineFeature(Feature):

Represents a line segment in a sketch.

### 6.1 LineFeature.\_\_init\_\_ <a name="linefeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  Drawing, *start*:  ApexPoint, *finish*:  ApexPoint, *name*:  *str* = "", *tracing*:  *str* = "") -> None:

Initialize a LineFeature.

### 6.2 LineFeature.drawing <a name="linefeature-drawing"></a>

def *drawing*(self) -> Drawing:  # *pragma*:  *no* *unit* *cover*

Return the LineFeature Drawing.

### 6.3 LineFeature.finish <a name="linefeature-finish"></a>

def *finish*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *cover*

Return the LineFeature finish ApexPoint.

### 6.4 LineFeature.finish\_key <a name="linefeature-finish-key"></a>

def *finish\_key*(self) -> *int*:

Return the LineFeature finish Constraint key.

### 6.5 LineFeature.part\_feature <a name="linefeature-part-feature"></a>

def *part\_feature*(self) -> PartFeature:

Return the PartFeature associated with a LineFeature.

### 6.6 LineFeature.start <a name="linefeature-start"></a>

def *start*(self) -> ApexPoint:

Return the LineFeature start ApexPoint.

### 6.7 LineFeature.start\_key <a name="linefeature-start-key"></a>

def *start\_key*(self) -> *int*:

Return the LineFeature start Constraint key.

### 6.8 LineFeature.type\_name <a name="linefeature-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the LineFeature type name.

## 7 Class PointFeature <a name="pointfeature"></a>

class PointFeature(Feature):

Represents a point in a sketch.

### 7.1 PointFeature.\_\_init\_\_ <a name="pointfeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  Drawing, *point*:  ApexPoint, *name*:  *str* = "") -> None:

Initialize a PointFeature.

### 7.2 PointFeature.\_\_str\_\_ <a name="pointfeature---str--"></a>

def \_\_str\_\_(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return PointFeature string .

### 7.3 PointFeature.part\_feature <a name="pointfeature-part-feature"></a>

def *part\_feature*(self) -> PartFeature:

Return the  PointFeature.

### 7.4 PointFeature.point <a name="pointfeature-point"></a>

def *point*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *cover*

Return the PointFeature ApexPoint.

### 7.5 PointFeature.type\_name <a name="pointfeature-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the PointFeature type name.

## 8 Class Polygon <a name="polygon"></a>

class Polygon(object):

Represents a polygon with possible rounded corners.

### 8.1 Polygon.\_\_init\_\_ <a name="polygon---init--"></a>

def \_\_init\_\_( *self*, *points*:  Tuple[ApexPoint, ...], *depth*:  *float* = 0.0, *flat*:  *bool* = False, *name*:  *str* = "" ) -> None:

Initialize a Polygon.

### 8.2 Polygon.bounding\_box <a name="polygon-bounding-box"></a>

def *bounding\_box*(self) -> BoundingBox:

Return the Polygon BoundingBox.

### 8.3 Polygon.clockwise <a name="polygon-clockwise"></a>

def *clockwise*(self) -> *bool*:  # *pragma*:  *no* *unit* *cover*

Return whether the Polygon points are clockwise.

### 8.4 Polygon.constraints\_append <a name="polygon-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  Drawing, *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Return the Polygon constraints for a Drawing.

### 8.5 Polygon.depth <a name="polygon-depth"></a>

def *depth*(self) -> *float*:

Return the Polygon depth.

### 8.6 Polygon.features\_get <a name="polygon-features-get"></a>

def *features\_get*(self, *drawing*:  Drawing, *tracing*:  *str* = "") -> Tuple[Feature, ...]:

Return the Polygon Features tuple.

### 8.7 Polygon.flat <a name="polygon-flat"></a>

def *flat*(self) -> *bool*:  # *pragma*:  *no* *unit* *cover*

Return the flat flag.

### 8.8 Polygon.name <a name="polygon-name"></a>

def *name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the Polygon depth.

### 8.9 Polygon.points <a name="polygon-points"></a>

def *points*(self) -> Tuple[ApexPoint, ...]:  # *pragma*:  *no* *unit* *cover*

Return the Polygon points.
