# ShopFab: A shop based design workflow.
class Point(object):

Represents a drawing point.

### 0.1 Point.\_\_init\_\_

def \_\_init\_\_(self, *x*:  *float* = 0.0, *y*:  *float* = 0.0, *z*:  *float* = 0.0, *name*:  *str* = "", *radius*:  *float* = 0.0) -> None:

Initialize a Point.

### 0.2 Point.\_\_sub\_\_

def \_\_add\_\_(self, *point*:  "Point") -> "Point":

Return the difference of two Point's.

### 0.3 Point.\_\_truediv\_\_

def \_\_truediv\_\_(self, *divisor*:  *float*) -> "Point":

Return a Point that has been scaleddown.

### 0.4 Point.\_\_rmul\_\_

def \_\_mul\_\_(self, *scale*:  *float*) -> "Point":

Return a Point that has been scaled.

### 0.5 Point.\_\_neg\_\_

def \_\_neg\_\_(self) -> "Point":

Return the negative of a Point.

### 0.6 Point.\_\_repr\_\_

def \_\_repr\_\_(self) -> *str*:  # *pragma*:  *no* *unit* *test*

Return a string representation of a Point.

### 0.7 Point.\_\_str\_\_

def \_\_str\_\_(self) -> *str*:  # *pragma*:  *no* *unit* *test*

Return a string representation of a Point.

### 0.8 Point.\_\_sub\_\_

def \_\_sub\_\_(self, *point*:  "Point") -> "Point":

Return the difference of two Point's.

### 0.9 Point.atan2

def *atan2*(self) -> *float*:

Return the Point arc tangent of y/x.

### 0.10 Point.constraints\_append

def *constraints\_append*(self, *drawing*:  "Drawing", *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Append Point constraints to a list.

### 0.11 PointFeature.features\_get

def *features\_get*(self, *drawing*:  "Drawing", *tracing*:  *str* = "") -> Tuple["Feature", ...]:

Return the PointFeature Feature's.

### 0.12 Point.origin

def *origin*(cls) -> "Point":  # *pragma*:  *no* *unit* *test*

Return an origin point.

### 0.13 Point

def *x*(self) -> *float*:

Return the x coordinate.

### 0.14 Point

def *y*(self) -> *float*:

Return the y coordinate.

### 0.15 Point

def *z*(self) -> *float*:

Return the z coordinate.

### 0.16 Point.radi

def *radius*(self) -> *float*:

Return the radius.

### 0.17 Point.na

def *name*(self) -> *str*:

Return the name.

### 0.18 Point.app\_vect

def *app\_vector*(self) -> App.Vector:

Return Vector from the Point.

### 0.19 Point.magnitude

def *magnitude*(self) -> *float*:

Return the magnitude of the point vector.

### 0.20 Point.normalize

def *normalize*(self) -> "Point":

Return the normal of the point vector.

### 0.21 Point.forward

def *forward*(self, *transform*:  "Transform") -> "Point":

Perform a forward transform of a point.

### 0.22 Point.reverse

def *reverse*(self, *transform*:  "Transform") -> "Point":  # *pragma*:  *no* *unit* *test*

Perform a reverse transform of a point.

## 1.0 Class BoundingBox

class BoundingBox:

Bounding box for a set of Point's.

### 1.1 BoundingBox.\_\_init\_\_

def \_\_init\_\_(self, *lower*:  Point, *upper*:  Point, *name*:  *str* = "") -> None:

Initiliaze a bounding box.

### 1.2 BoundingBox.center

def *center*(self) -> Point:  # *pragma*:  *no* *unit* *test*

Return center BoundingBox Point.

### 1.3 BoundingBox.lower

def *lower*(self) -> Point:

Return lower left BoundingBox Point.

### 1.4 BoundingBox.name

def *name*(self) -> *str*:  # *pragma*:  *no* *unit* *test*

Return BoundingBox name.

### 1.5 BoundingBox.lower

def *upper*(self) -> Point:

Return upper right BoundingBox Point.

def *from\_points*(points:  Tuple[Point, ...]) -> "BoundingBox":

Compute BoundingBox from some Point's.

def *from\_bounding\_boxes*(bounding\_boxes:  Tuple["BoundingBox", ...]) -> "BoundingBox":

Compute enclosing BoundingBox from some BoundingBox's.

class Transform:

A transform matrix using a 4x4 affine matrix.

The matrix format is an affine 4x4 matrix in the following format:

    [ r00 r01 r02 0 ]
    [ r10 r11 r12 0 ]
    [ r20 r21 r22 0 ]
    [ dx  dy  dz  1 ]

An affine point format is a 1x4 matrix of the following format:

   [ x y z 1 ]

We multiply with the point on the left (1x4) and the matrix on the right (4x4).
This yields a 1x4 point matrix of the same form.

Only two transforms are supported:
* Transform.translate(Point)
* Transform.rotate(Point, Angle)

A Transform object is immutable:
It should have its inverse matrix computed.

### 1.6 Transform.\_\_init\_\_

def \_\_init\_\_(self, *center*:  Optional[Point] = None, *axis*:  Optional[Point] = None, *angle*:  *float* = 0.0, *translate*:  Optional[Point] = None, *name*:  *str* = "") -> None:

Return the identity transform.

def *forward*(self, *point*:  Point) -> Point:

Apply a transform to a point.

def *reverse*(self, *point*:  Point) -> Point:  # *pragma*:  *no* *unit* *test*

Apply a transform to a point.

def *zero\_fix*(value:  *float*) -> *float*:

Convert small values to zero and also covnvert -0.0 to 0.0.

def *zero\_clean*(matrix:  *np*.ndarray) -> *np*.ndarray:  # *pragma*:  *no* *unit* *test*

Round small numbers to zero.

### 1.7 Transform.rotate

def *rotate*(axis:  Point, *angle*:  *float*) -> *np*.ndarray:

Return a rotation matrix.

The matrix for rotating by *angle* around the normal *axis* is:
    #
    # [ xx(1-c)+c   yx(1-c)-zs  zx(1-c)+ys   0  ]
    # [ xy(1-c)+zs  yy(1-c)+c   zy(1-c)-xs   0  ]
    # [ xz(1-c)-ys  yz(1-c)+xs  zz(1-c)+c    0  ]
    # [ 0           0           0            1  ]
    #
    # Where c = cos(*angle*), s = sin(*angle*), and *angle* is measured in radians.

def *translate*(translate:  Point) -> *np*.ndarray:

Return a 4x4 affine matrix to translate over by a point.

## 2.0 Class Drawing

class Drawing(object):

Represents a 2D drawing.

### 2.1 Drawing.\_\_init\_\_

def \_\_init\_\_( *self*, *circles*:  Tuple["Circle", ...], *polygons*:  Tuple["Polygon", ...], *name*:  *str* = "" ) -> None:

Initialize a drawing.

### 2.2 Drawing.bounding\_box

def *bounding\_box*(self) -> BoundingBox:

Return the Drawing BoundingBox.

### 2.3 Drawing.circles

def *circles*(self) -> Tuple["Circle", ...]:  # *pragma*:  *no* *unit* *test*

Return the Drawing Circle's.

### 2.4 Drawing.forward\_transform

def *forward\_transform*(self, *transform*:  Transform) -> "Drawing":

Return an Drawing that is offset via a forward transform.

### 2.5 Drawing.name

def *name*(self) -> *str*:

Return the Drawing name.

### 2.6 Drawing.origin\_index

def *origin\_index*(self) -> *int*:

Return the Drawing origin index.

### 2.7 Drawing.polygons

def *polygons*(self) -> Tuple["Polygon", ...]:  # *pragma*:  *no* *unit* *test*

Return the Drawing Polygon's.

### 2.8 Drawing.sketch

def *sketch*(self, *sketcher*:  "Sketcher.SketchObject", *lower\_left*:  Point, *tracing*:  *str* = "") -> None:

Sketch a Drawing.

## 3.0 Class Feature

class Feature(object):

Base class a schematic features.

### 3.1 Feature.\_\_init\_\_

def \_\_init\_\_(self, *drawing*:  Drawing, *start*:  Point, *finish*:  Point, *name*:  *str* = "") -> None:

Initialize a Feature.

### 3.2 Feature.drawing

def *drawing*(self) -> Drawing:  # *pragma*:  *no* *unit* *test*

Return the Feature Drawing.

### 3.3 Feature.finish

def *finish*(self) -> Point:  # *pragma*:  *no* *unit* *test*

Return the Feature finish point.

### 3.4 Feature.index

def *index*(self) -> *int*:

Return the Feature index.

### 3.5 Feature.index.setter

def *index*(self, *index*:  *int*) -> None:

Set the Feature index.

def *finish\_key*(self) -> *int*:  # *pragma*:  *no* *unit* *test*

Return the Feature Constraint key for the finish point.

### 3.6 Feature.name

def *name*(self) -> *str*:

Return Feature name.

# Feature.next() *def* *next*(self) -> "Feature":  # *pragma*:  *no* *unit* *test*

Return the next Feature in circular list.

### 3.7 Feature.index.setter

def *next*(self, *next*:  "Feature") -> None:

Set the next Feature in circular list.

### 3.8 Feature.part\_feature

def *part\_feature*(self) -> PartFeature:

Return the PartFeature associated with Feature.

### 3.9 Feature.previous

def *previous*(self) -> "Feature":  # *pragma*:  *no* *unit* *test*

Return the previous Part Feature in circular list.

### 3.10 Feature.previous.setter

def *previous*(self, *next*:  "Feature") -> None:

Set the previous Part Feature in circular list.

### 3.11 Feature.start

def *start*(self) -> Point:  # *pragma*:  *no* *unit* *test*

Return the Feature start point.

def *start\_key*(self) -> *int*:

Return the Feature Constraint key for the start point.

### 3.12 Feature.type\_name

def *type\_name*(self) -> *str*:

Return the Feature type name.

## 4.0 Class ArcFeature

class ArcFeature(Feature):

Represents an an arc in a sketch.

### 4.1 ArcFeature.\_\_init\_\_

def \_\_init\_\_(self, *drawing*:  Drawing, *begin*:  Point, *apex*:  Point, *end*:  Point, *name*:  *str* = "", *tracing*:  *str* = "") -> None:

Initialize an ArcFeature.

### 4.2 ArcFeature.repr

def \_\_repr\_\_(self) -> *str*:  # *pragma*:  *no* *unit* *test*

Return ArcFeature string representation.

### 4.3 ArcFeature.apex

def *apex*(self) -> Point:

Return the ArcFeature apex Point.

### 4.4 ArcFeature.begin

def *begin*(self) -> Point:  # *pragma*:  *no* *unit* *test*

Return the ArcFeature arc begin Point.

### 4.5 ArcFeature.center

def *center*(self) -> Point:

Return the ArcFeature arc center.

### 4.6 ArcFeature.end

def *end*(self) -> Point:  # *pragma*:  *no* *unit* *test*

Return the initial ArcFeature end Point.

### 4.7 ArcFeature.finish

def *finish*(self) -> Point:

Return the ArcFeature arc finish Point.

### 4.8 ArcFeature.finish\_key

def *finish\_key*(self) -> *int*:

Return the ArcFeature finish Constraint key.

### 4.9 ArcFeature.finish\_angle

def *finish\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ArcFeature arc finish angle.

### 4.10 ArcFeature.finish\_length

def *finish\_length*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return distance from arc finish Point to the apex Point.

### 4.11 ArcFeature.input

def *input*(self) -> Point:  # *pragma*:  *no* *unit* *test*

Return the initial ArcFeature arc start Point.

### 4.12 ArcFeatrue.part\_feature

def *part\_feature*(self) -> PartFeature:

Return ArcFeature Part.Arc.

### 4.13 ArcFeature.radius

def *radius*(self) -> *float*:

Return the initial ArcFeature radius.

### 4.14 ArcFeature.start

def *start*(self) -> Point:

Return the ArcFeature arc start Point.

### 4.15 ArcFeature.start\_angle

def *start\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ArcFeature arc start angle.

### 4.16 ArcFeature.start\_key

def *start\_key*(self) -> *int*:

Return the ArcFeature finish Constraint key.

### 4.17 ArcFeature.start\_length

def *start\_length*(self) -> *float*:  # *pragma*:  *no* *unit* *test*

Return the ArcFeature distance from start Point to apex Point.

### 4.18 ArcFeature.sweep\_angle

def *sweep\_angle*(self) -> *float*:  # *pragma*:  *no* *unit* *cover*

Return the ArcFeature sweep angle from start angle to end angle.

### 4.19 ArcFeature.type\_name

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ArcFeature type name.

## 5.0 Class CircleFeature

class CircleFeature(Feature):

Represents a circle in a sketch.

### 5.1 CircleFeature.\_\_init\_\_

def \_\_init\_\_(self, *drawing*:  Drawing, *center*:  Point, *radius*:  *float*, *name*:  *str* = "") -> None:

Initialize a CircleFeature.

### 5.2 CircleFeature.center

def *center*(self) -> Point:  # *pragma*:  *no* *unit* *cover*

Return the CircleFeature center.

### 5.3 CircleFeature.part\_element

def *part\_feature*(self) -> PartFeature:

Return the CircleFeature PartFeature.

### 5.4 CircleFeature.radius

def *radius*(self) -> *float*:  # *pragma*:  *no* *unit* *cover*

Return the CircleFeature radius.

### 5.5 CircleFeature.type\_name

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the CircleFeature type name.

## 6.0 Class LineFeature

class LineFeature(Feature):

Represents a line segment in a sketch.

### 6.1 LineFeature.\_\_init\_\_

def \_\_init\_\_( *self*, *drawing*:  Drawing, *start*:  Point, *finish*:  Point, *name*:  *str* = "", *tracing*:  *str* = "" ) -> None:

Initialize a LineFeature.

### 6.2 LineFeature.drawing

def *drawing*(self) -> Drawing:  # *pragma*:  *no* *unit* *cover*

Return the LineFeature Drawing.

### 6.3 LineFeature.part\_feature

def *part\_feature*(self) -> PartFeature:

Return the PartFeature associated with a LineFeature.

### 6.4 LineFeature.finish

def *finish*(self) -> Point:  # *pragma*:  *no* *unit* *cover*

Return the LineFeature finish Point.

### 6.5 LineFeature.finish\_key

def *finish\_key*(self) -> *int*:

Return the LineFeature finish Constraint key.

### 6.6 LineFeature.start

def *start*(self) -> Point:

Return the LineFeature start Point.

### 6.7 LineFeature.start\_key

def *start\_key*(self) -> *int*:

Return the LineFeature start Constraint key.

### 6.8 LineFeature.type\_name

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the LineFeature type name.

## 7.0 Class PointFeature

class PointFeature(Feature):

Represents a point in a sketch.

### 7.1 PointFeature.\_\_init\_\_

def \_\_init\_\_(self, *drawing*:  Drawing, *point*:  Point, *name*:  *str* = "") -> None:

Initialize a PointFeature.

### 7.2 PointFeature.\_\_str\_\_

def \_\_str\_\_(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return PointFeature string .

### 7.3 PointFeature.part\_feature

def *part\_feature*(self) -> PartFeature:

Return the  PointFeature.

### 7.4 PointFeature.point

def *point*(self) -> Point:  # *pragma*:  *no* *unit* *cover*

Return the PointFeature Point.

### 7.5 PointFeature.type\_name

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the PointFeature type name.

## 8.0 Class Polygon

class Polygon(object):

Represents a polygon with possible rounded corners.

### 8.1 Polygon.\_\_init\_\_

def \_\_init\_\_( *self*, *points*:  Tuple[Point, ...], *depth*:  *float* = 0.0, *flat*:  *bool* = False, *name*:  *str* = "" ) -> None:

Initialize a Polygon.

### 8.2 Polygon.bounding\_box

def *bounding\_box*(self) -> BoundingBox:

Return the Polygon BoundingBox.

### 8.3 Polygon.clockwise

def *clockwise*(self) -> *bool*:  # *pragma*:  *no* *unit* *cover*

Return whether the Polygon points are clockwise.

### 8.4 Polygon.constraints\_append

def *constraints\_append*(self, *drawing*:  Drawing, *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Return the Polygon constraints for a Drawing.

### 8.5 Polygon.depth

def *depth*(self) -> *float*:

Return the Polygon depth.

### 8.6 Polygon.flat

def *flat*(self) -> *bool*:  # *pragma*:  *no* *unit* *cover*

Return the flat flag.

### 8.7 Polygon.features\_get

def *features\_get*(self, *drawing*:  Drawing, *tracing*:  *str* = "") -> Tuple[Feature, ...]:

Return the Polygon Features tuple.

### 8.8 Polygon.name

def *name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the Polygon depth.

### 8.9 Polygon.points

def *points*(self) -> Tuple[Point, ...]:  # *pragma*:  *no* *unit* *cover*

Return the Polygon points.

def *forward\_transform*(self, *transform*:  Transform) -> "Polygon":

Return a forward transformed Polygon.

class Circle(object):

Represents a circle.

### 8.10 Circle.\_\_init

def \_\_init\_\_( *self*, *center*:  Point, *depth*:  *float* = 0.0, *flat*:  *bool* = False, *name*:  *str* = "" ) -> None:

Initialize a circle.

### 8.11 CircleFeature.\_\_repr\_\_

def \_\_repr\_\_(self) -> *str*:

Return a string representation of Circle.

### 8.12 Circle.bounding\_box

def *bounding\_box*(self) -> BoundingBox:

Return the Circle BoundingBox.

### 8.13 Circle.center

def *center*(self) -> Point:

Return the Circle center Point.

### 8.14 Circle.circle\_featu

def *circle\_feature*(self) -> CircleFeature:

Return the Circle CircleFeature.

### 8.15 Circle.constraints\_append

def *constraints\_append*(self, *drawing*:  Drawing, *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Return the CircleFeature constraints.

### 8.16 Circle.depth

def *depth*(self) -> *float*:

Return the Circle Depth.

### 8.17 Circle.flat

def *flat*(self) -> *bool*:

Return whether the Circle bottom is flat.

### 8.18 Circle.features\_get

def *features\_get*(self, *drawing*:  Drawing) -> Tuple[Feature, ...]:

Return the CircleFeature.

### 8.19 Circle.forward\_transform

def *forward\_transform*(self, *transform*:  Transform) -> "Circle":

Return a forward transformed Circle.

### 8.20 Circle.name

def *name*(self) -> *str*:

Return the name of the Circle.

### 8.21 Circle.radius

def *radius*(self) -> *float*:

Return the Circle radius.

def *visibility\_set*(element:  Any, *new\_value*:  *bool* = True) -> None:

Set the visibility of an element.

def *main*() -> *int*:

Run the program.

def *class\_names\_show*(module\_object:  Any) -> None:  # *pragma*:  *no* *unit* *cover*

Show the the class name of an object.

def *attributes\_show*(some\_object:  Any) -> None:  # *pragma*:  *no* *unit* *cover*

Show the attributes of an object.

