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
* 3 [Class ApexCircle](#apexcircle)
  * 3.1 [ApexCircle.\_\_init](#apexcircle---init)
  * 3.2 [ApexCircle.box](#apexcircle-box)
  * 3.3 [ApexCircle.constraints\_append](#apexcircle-constraints-append)
  * 3.4 [ApexCircle.features\_get](#apexcircle-features-get)
  * 3.5 [ApexCircle.reorient](#apexcircle-reorient)
* 4 [Class ApexCircleFeature](#apexcirclefeature)
  * 4.1 [ApexCircleFeature.\_\_init\_\_](#apexcirclefeature---init--)
  * 4.2 [ApexCircleFeature.center](#apexcirclefeature-center)
  * 4.3 [ApexCircleFeature.part\_element](#apexcirclefeature-part-element)
  * 4.4 [ApexCircleFeature.radius](#apexcirclefeature-radius)
  * 4.5 [ApexCircleFeature.type\_name](#apexcirclefeature-type-name)
* 5 [Class ApexDrawing](#apexdrawing)
  * 5.1 [ApexDrawing.\_\_init\_\_](#apexdrawing---init--)
  * 5.2 [ApexDrawing.create\_datum\_plane](#apexdrawing-create-datum-plane)
  * 5.3 [ApexDrawing.features\_get](#apexdrawing-features-get)
  * 5.4 [ApexDrawing.plane\_process](#apexdrawing-plane-process)
  * 5.5 [ApexDrawing.point\_constraints\_append](#apexdrawing-point-constraints-append)
  * 5.6 [ApexDrawing.reorient](#apexdrawing-reorient)
  * 5.7 [ApexDrawing.sketch](#apexdrawing-sketch)
  * 5.8 [ApexElement.\_\_init\_\_](#apexelement---init--)
  * 5.9 [ApexElement.constraints\_append](#apexelement-constraints-append)
  * 5.10 [ApexElement.features\_get](#apexelement-features-get)
  * 5.11 [ApexElement.reorient](#apexelement-reorient)
* 6 [Class ApexFeature](#apexfeature)
  * 6.1 [ApexFeature.\_\_init\_\_](#apexfeature---init--)
  * 6.2 [ApexFeature.drawing](#apexfeature-drawing)
  * 6.3 [ApexFeature.finish](#apexfeature-finish)
  * 6.4 [ApexFeature.index](#apexfeature-index)
  * 6.5 [ApexFeature.name](#apexfeature-name)
  * 6.6 [ApexFeature.part\_feature](#apexfeature-part-feature)
  * 6.7 [ApexFeature.previous](#apexfeature-previous)
  * 6.8 [ApexFeature.start](#apexfeature-start)
  * 6.9 [ApexFeature.type\_name](#apexfeature-type-name)
* 7 [Class ApexLineFeature](#apexlinefeature)
  * 7.1 [ApexLineFeature.\_\_init\_\_](#apexlinefeature---init--)
  * 7.2 [ApexLineFeature.drawing](#apexlinefeature-drawing)
  * 7.3 [ApexLineFeature.finish](#apexlinefeature-finish)
  * 7.4 [ApexLineFeature.finish\_key](#apexlinefeature-finish-key)
  * 7.5 [ApexLineFeature.part\_feature](#apexlinefeature-part-feature)
  * 7.6 [ApexLineFeature.start](#apexlinefeature-start)
  * 7.7 [ApexLineFeature.start\_key](#apexlinefeature-start-key)
  * 7.8 [ApexLineFeature.type\_name](#apexlinefeature-type-name)
* 8 [Class ApexPointFeature](#apexpointfeature)
  * 8.1 [ApexPointFeature.\_\_init\_\_](#apexpointfeature---init--)
  * 8.2 [ApexPointFeature.\_\_str\_\_](#apexpointfeature---str--)
  * 8.3 [ApexPointFeature.part\_feature](#apexpointfeature-part-feature)
  * 8.4 [ApexPointFeature.point](#apexpointfeature-point)
  * 8.5 [ApexPointFeature.type\_name](#apexpointfeature-type-name)
* 9 [Class ApexPolygon](#apexpolygon)
  * 9.1 [ApexPolygon.\_\_init\_\_](#apexpolygon---init--)
  * 9.2 [ApexPolygon.clockwise](#apexpolygon-clockwise)
  * 9.3 [ApexPolygon.constraints\_append](#apexpolygon-constraints-append)
  * 9.4 [ApexPolygon.depth](#apexpolygon-depth)
  * 9.5 [ApexPolygon.features\_get](#apexpolygon-features-get)
  * 9.6 [ApexPolygon.name](#apexpolygon-name)
  * 9.7 [ApexPolygon.points](#apexpolygon-points)
  * 9.8 [ApexPolygon.reorient](#apexpolygon-reorient)
  * 9.9 [ApexElement](#apexelement)
  * 9.10 [ApexElementKey](#apexelementkey)

## 1 <a name="introduction"></a>Introduction


## 2 Class ApexArcFeature <a name="apexarcfeature"></a>

class ApexArcFeature(ApexFeature):

Represents an an arc in a sketch.

### 2.1 ApexArcFeature.\_\_init\_\_ <a name="apexarcfeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  "ApexDrawing", *begin*:  ApexPoint, *apex*:  ApexPoint, *end*:  ApexPoint, *name*:  *str* = "", *tracing*:  *str* = "") -> None:

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

## 3 Class ApexCircle <a name="apexcircle"></a>

class ApexCircle(ApexElement):

ApexCircle: Represents a circle with an optional hole.

Attributes:
* *box* (ApexBoundBox): The ApexCircle ApexBoundBox.
* *center* (ApexPoint): The center of the circle.
* *circle\_feature* (ApexCircleFeature): The ApexCircleFeature for the circle.
* *depth* (float): The hole depth in millimeters.
* *flat* (bool): True if the hole bottom is flat.
* *is\_exterior* (bool): True if the ApexCircle is the exterior of an ApexDrawing.
* *name* (str): The ApexCircle name.
* *radius* (str): The ApexCircle radius in millimeters.


### 3.1 ApexCircle.\_\_init <a name="apexcircle---init"></a>

def \_\_init\_\_( *self*, *center*:  ApexPoint, *depth*:  *float* = 0.0, *flat*:  *bool* = False, *is\_exterior*:  *bool* = False, *name*:  *str* = "" ) -> None:

Initialize a circle.

### 3.2 ApexCircle.box <a name="apexcircle-box"></a>

def *box*(self) -> ApexBox:

Return the ApexCircle ApexBox.

### 3.3 ApexCircle.constraints\_append <a name="apexcircle-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  "ApexDrawing", *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Return the ApexCircleFeature constraints.

### 3.4 ApexCircle.features\_get <a name="apexcircle-features-get"></a>

def *features\_get*(self, *drawing*:  "ApexDrawing", *tracing*:  *str* = "") -> Tuple[ApexFeature, ...]:

Return the ApexCircleFeature.

### 3.5 ApexCircle.reorient <a name="apexcircle-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  Optional[str] = "", *tracing*:  *str* = "") -> "ApexCircle":

Return a new reoriented ApexCircle.

Arguments:
* *placement* (Placement): The FreeCAD Placement reoirient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")


## 4 Class ApexCircleFeature <a name="apexcirclefeature"></a>

class ApexCircleFeature(ApexFeature):

Represents a circle in a sketch.

### 4.1 ApexCircleFeature.\_\_init\_\_ <a name="apexcirclefeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  "ApexDrawing", *center*:  ApexPoint, *radius*:  *float*, *name*:  *str* = "") -> None:

Initialize a ApexCircleFeature.

### 4.2 ApexCircleFeature.center <a name="apexcirclefeature-center"></a>

def *center*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *cover*

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

## 5 Class ApexDrawing <a name="apexdrawing"></a>

class ApexDrawing(object):

ApexDrawing: Used to create fully constrained 2D drawings.

Attributes:
* *contact*: (Union[Vector, ApexPoint]): On point on the surface of the polygon.
* *normal*: (Union[Vector, ApexPoint]): A normal to the polygon plane.
* *elements* (Tuple[ApexElement, ...]): All ApexElements (including *exterior*, if present.)
* *exterior* (Optional[ApexElement]): The exterior ApexElement, if present (Default: None).
* *name* (str): The ApexDrawing name. (Default: "")


### 5.1 ApexDrawing.\_\_init\_\_ <a name="apexdrawing---init--"></a>

def \_\_init\_\_( *self*, *contact*:  Union["ApexPoint", "Vector"], *normal*:  Union["ApexPoint", "Vector"], *elements*:  Tuple[ApexElement, ...], *exterior*:  Optional[ApexElement] = None, *name*:  *str* = "", *tracing*:  *str* = "" ) -> None:

Initialize a drawing.

Arguments:
* *contact* (Union[ApexPoint, Vector]):
  A point on the surface of the drawing in 3D space.  (Default: Vector(0, 0, 0))
* *normal* (Union[ApexPoint, Vector]):
  An ApexPoint/Vector that is normal to the plane that goes through *contact*.
  (Default: Vector(0, 0, 1))
* *exterior*: (Optional[ApexElement]):
  The exterior contour of the part.  None if exterior is not needed. (Default: None)
* *name*: (str): The drawing name.  (Default: "")

Raises:
* ValueError if no exterior, circles, or polygons are specified.


### 5.2 ApexDrawing.create\_datum\_plane <a name="apexdrawing-create-datum-plane"></a>

def *create\_datum\_plane*(self, *body*:  "PartDesign.Body", *name*:  *str* = "DatumPlane", *tracing*:  *str* = "") -> "Part.ApexFeature":

Return the FreeCAD DatumPlane used for the drawing.

Arguments:
* *body* (PartDesign.Body): The FreeCAD Part design Body to attach the datum plane to.
* *name* (str): The datum plane name (Default: "DatumPlane")

* Returns:
  * (Part.ApexFeature) that is the datum\_plane.

### 5.3 ApexDrawing.features\_get <a name="apexdrawing-features-get"></a>

def *point\_features\_get*(self, *point*:  ApexPoint, *tracing*:  *str* = "") -> Tuple["ApexFeature", ...]:

Return the ApexPointFeature Feature's.

### 5.4 ApexDrawing.plane\_process <a name="apexdrawing-plane-process"></a>

def *plane\_process*(self, *body*:  "PartDesign.Body", *tracing*:  *str* = "") -> None:

Plane\_Process.

### 5.5 ApexDrawing.point\_constraints\_append <a name="apexdrawing-point-constraints-append"></a>

def *point\_constraints\_append*(self, *point*:  ApexPoint, *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:  # REMOVE

Append ApexPoint constraints to a list.

### 5.6 ApexDrawing.reorient <a name="apexdrawing-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  Optional[str] = "", *tracing*:  *str* = "") -> "ApexDrawing":

Return a reoriented ApexDrawing.

Arguments:
* *placement* (Placement): The Placement to apply to internal ApexCircles and ApexPolygons.
* *suffix* (Optional[str]): The suffix to append at all names.  If None, all
  names are set to "" instead appending the suffix.  (Default: "")


### 5.7 ApexDrawing.sketch <a name="apexdrawing-sketch"></a>

def *sketch*(self, *sketcher*:  "Sketcher.SketchObject", *tracing*:  *str* = "") -> None:

Insert an ApexDrawing into a FreeCAD SketchObject.

Arguments:
* sketcher (Sketcher.SketchObject): The sketcher object to use.

### 5.8 ApexElement.\_\_init\_\_ <a name="apexelement---init--"></a>

def \_\_init\_\_(self, *is\_exterior*:  *bool* = False, *depth*:  Union[float, ApexLength] = 0.0, *diameter*:  Union[float, ApexLength] = 0.0, *name*:  *str* = "") -> None:

Initialize the ApexElement.

Arguments:
* *is\_exterior* (bool): True if the Element is the exterior of an ApexDrawing.
* *depth* (Union[float, ApexLength]): The ApexElement depth.
* *diameter* (Union[float, ApexLength]): The ApexElement diameter (0.0 for ApexPolygon.)
* *depth* (Union[float, ApexLength]): The ApexElement depth.
* *name* (str): The ApexElement name (Default: "").


### 5.9 ApexElement.constraints\_append <a name="apexelement-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  "ApexDrawing", *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Append the ApexElement constraints to drawing.

Arguments:
* *drawing* (ApexDrawing): The drawing to use.
* *constraints* (List[SketcherConstraint]): The contstraints list to append to.


### 5.10 ApexElement.features\_get <a name="apexelement-features-get"></a>

def *features\_get*(self, *drawing*:  "ApexDrawing", *tracing*:  *str* = "") -> Tuple[ApexFeature, ...]:

Return the ApexElement ApexFeatures tuple.

Arguments:
* *drawing* (ApexDrawing): The associated drawing to use for feature extraction.

Returns:
* (Tuple[ApexFeature, ...]) of extracted ApexFeature's.


### 5.11 ApexElement.reorient <a name="apexelement-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  Optional[str] = "", *tracing*:  *str* = "") -> "ApexElement":

Return a new reoriented ApexCircle.

Arguments:
* *placement* (Placement): The FreeCAD Placement reoirient with.
* *suffix* (str): The suffix to append to the current name string.  None, specifies
  that an empty name is to be used.  (Default: "")

# Returns:
* (ApexElement) that has been reoriented with a new name.

## 6 Class ApexFeature <a name="apexfeature"></a>

class ApexFeature(object):

Base class a schematic features.

### 6.1 ApexFeature.\_\_init\_\_ <a name="apexfeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  "ApexDrawing", *start*:  ApexPoint, *finish*:  ApexPoint, *name*:  *str* = "") -> None:

Initialize a ApexFeature.

### 6.2 ApexFeature.drawing <a name="apexfeature-drawing"></a>

def *drawing*(self) -> "ApexDrawing":  # *pragma*:  *no* *unit* *test*

Return the ApexFeature ApexDrawing.

### 6.3 ApexFeature.finish <a name="apexfeature-finish"></a>

def *finish*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *test*

Return the ApexFeature finish point.

### 6.4 ApexFeature.index <a name="apexfeature-index"></a>

def *index*(self) -> *int*:

Return the ApexFeature index.

### 6.5 ApexFeature.name <a name="apexfeature-name"></a>

def *name*(self) -> *str*:

Return ApexFeature name.

### 6.6 ApexFeature.part\_feature <a name="apexfeature-part-feature"></a>

def *part\_feature*(self) -> PartFeature:

Return the PartFeature associated with ApexFeature.

### 6.7 ApexFeature.previous <a name="apexfeature-previous"></a>

def *previous*(self) -> "ApexFeature":  # *pragma*:  *no* *unit* *test*

Return the previous Part ApexFeature in circular list.

### 6.8 ApexFeature.start <a name="apexfeature-start"></a>

def *start*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *test*

Return the ApexFeature start point.

### 6.9 ApexFeature.type\_name <a name="apexfeature-type-name"></a>

def *type\_name*(self) -> *str*:

Return the ApexFeature type name.

## 7 Class ApexLineFeature <a name="apexlinefeature"></a>

class ApexLineFeature(ApexFeature):

Represents a line segment in a sketch.

### 7.1 ApexLineFeature.\_\_init\_\_ <a name="apexlinefeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  "ApexDrawing", *start*:  ApexPoint, *finish*:  ApexPoint, *name*:  *str* = "", *tracing*:  *str* = "") -> None:

Initialize a ApexLineFeature.

### 7.2 ApexLineFeature.drawing <a name="apexlinefeature-drawing"></a>

def *drawing*(self) -> "ApexDrawing":  # *pragma*:  *no* *unit* *cover*

Return the ApexLineFeature ApexDrawing.

### 7.3 ApexLineFeature.finish <a name="apexlinefeature-finish"></a>

def *finish*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *cover*

Return the ApexLineFeature finish ApexPoint.

### 7.4 ApexLineFeature.finish\_key <a name="apexlinefeature-finish-key"></a>

def *finish\_key*(self) -> *int*:

Return the ApexLineFeature finish Constraint key.

### 7.5 ApexLineFeature.part\_feature <a name="apexlinefeature-part-feature"></a>

def *part\_feature*(self) -> PartFeature:

Return the PartFeature associated with a ApexLineFeature.

### 7.6 ApexLineFeature.start <a name="apexlinefeature-start"></a>

def *start*(self) -> ApexPoint:

Return the ApexLineFeature start ApexPoint.

### 7.7 ApexLineFeature.start\_key <a name="apexlinefeature-start-key"></a>

def *start\_key*(self) -> *int*:

Return the ApexLineFeature start Constraint key.

### 7.8 ApexLineFeature.type\_name <a name="apexlinefeature-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexLineFeature type name.

## 8 Class ApexPointFeature <a name="apexpointfeature"></a>

class ApexPointFeature(ApexFeature):

Represents a point in a sketch.

### 8.1 ApexPointFeature.\_\_init\_\_ <a name="apexpointfeature---init--"></a>

def \_\_init\_\_(self, *drawing*:  "ApexDrawing", *point*:  ApexPoint, *name*:  *str* = "") -> None:

Initialize a ApexPointFeature.

### 8.2 ApexPointFeature.\_\_str\_\_ <a name="apexpointfeature---str--"></a>

def \_\_str\_\_(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return ApexPointFeature string .

### 8.3 ApexPointFeature.part\_feature <a name="apexpointfeature-part-feature"></a>

def *part\_feature*(self) -> PartFeature:

Return the  ApexPointFeature.

### 8.4 ApexPointFeature.point <a name="apexpointfeature-point"></a>

def *point*(self) -> ApexPoint:  # *pragma*:  *no* *unit* *cover*

Return the ApexPointFeature ApexPoint.

### 8.5 ApexPointFeature.type\_name <a name="apexpointfeature-type-name"></a>

def *type\_name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexPointFeature type name.

## 9 Class ApexPolygon <a name="apexpolygon"></a>

class ApexPolygon(ApexElement):

ApexPolyon: A closed polygon of ApexPoints.

Attributes:
* *box* (ApexBox): The bounding box of the ApexPoint's.
* *clockwise* (bool): True if the ApexPoints are clockwise and False otherwise.
* *depth* (Union[float, ApexLength]): The ApexPolygon depth.
* *diameter* (Union[Float, ApexLength]): Always 0.0 for an ApexPolygon.
* *name* (str): The ApexPolygon name.
* *points* (Tuple[ApexPoint, ...]): The ApexPoint's of the ApexPoloygon.


### 9.1 ApexPolygon.\_\_init\_\_ <a name="apexpolygon---init--"></a>

def \_\_init\_\_( *self*, *points*:  Tuple[ApexPoint, ...], *depth*:  Union[ApexLength, *float*] = 0.0, *is\_exterior*:  *bool* = False, *name*:  *str* = "" ) -> None:

Initialize a ApexPolygon.

### 9.2 ApexPolygon.clockwise <a name="apexpolygon-clockwise"></a>

def *clockwise*(self) -> *bool*:  # *pragma*:  *no* *unit* *cover*

Return whether the ApexPolygon points are clockwise.

### 9.3 ApexPolygon.constraints\_append <a name="apexpolygon-constraints-append"></a>

def *constraints\_append*(self, *drawing*:  "ApexDrawing", *constraints*:  List[Sketcher.Constraint], *tracing*:  *str* = "") -> None:

Return the ApexPolygon constraints for a ApexDrawing.

### 9.4 ApexPolygon.depth <a name="apexpolygon-depth"></a>

def *depth*(self) -> *float*:

Return the ApexPolygon depth.

### 9.5 ApexPolygon.features\_get <a name="apexpolygon-features-get"></a>

def *features\_get*(self, *drawing*:  "ApexDrawing", *tracing*:  *str* = "") -> Tuple[ApexFeature, ...]:

Return the ApexPolygon ApexFeatures tuple.

### 9.6 ApexPolygon.name <a name="apexpolygon-name"></a>

def *name*(self) -> *str*:  # *pragma*:  *no* *unit* *cover*

Return the ApexPolygon depth.

### 9.7 ApexPolygon.points <a name="apexpolygon-points"></a>

def *points*(self) -> Tuple[ApexPoint, ...]:  # *pragma*:  *no* *unit* *cover*

Return the ApexPolygon points.

### 9.8 ApexPolygon.reorient <a name="apexpolygon-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  Optional[str] = "", *tracing*:  *str* = "") -> "ApexPolygon":

Reorient an ApexPolygon with a new Placement.

Arguments:
* *placement* (Placement):
  The FreeCAD Placement to use for reorientation.
* *suffix* (Optional[str]):
  A suffix to append to the name.  If None, an empty name is used. (Default: "")


## 9 Class ApexElement() <a name="apexelement"></a>

class ApexElement(object):

ApexElement: Base class for ApexCircle and ApexPolygon.

Attributes:
* *box* (ApexBox): The Apex box for the ApexElement.
* *depth* (Union[float, ApexLength]): The element depth.
* *diameter* (Union[float, ApexLength]): The element diameter.
* *is\_exterior* (bool): True if ApexElement is the exterior.
* *key* (ApexElementKey): The grouping key FreeCAD Part Design operations.
* *name* (Optional[str]): The ApexElement name:


## 9 Class ApexElementKey() <a name="apexelementkey"></a>

class ApexElementKey(object):

ApexElementKey: Sorting key for ApexElement's.

Attributues:
* *is\_exterior* (bool): True if ApexElement is the exterior.
* *depth* (float): The ApexElement depth.
* *diameter* (float): The ApexCircle diameter (or 0.0 for an ApexPolygon).

An ApexElementKey is used to group ApexElements and choose between Pad, Pocket, and
Hole operations.

