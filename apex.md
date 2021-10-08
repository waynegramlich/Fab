# Apex base classes.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class ApexBoundBox](#apexboundbox)
  * 2.1 [ApexBoundBox.\_\_init\_\_](#apexboundbox---init--)
  * 2.2 [ApexBoundBox.\_\_repr\_\_](#apexboundbox---repr--)
  * 2.3 [ApexBoundBox.\_\_str\_\_](#apexboundbox---str--)
  * 2.4 [ApexBoundBox.from\_vectors](#apexboundbox-from-vectors)
* 3 [Class ApexLength](#apexlength)
  * 3.1 [ApexLength.\_\_new\_\_](#apexlength---new--)
  * 3.2 [ApexLength.\_\_repr\_\_](#apexlength---repr--)
  * 3.3 [ApexLength.\_\_str\_\_](#apexlength---str--)
  * 3.4 [ApexLength.unit\_test](#apexlength-unit-test)
  * 3.5 [ApexLength.unit\_test](#apexlength-unit-test)
* 4 [Class ApexMatrix](#apexmatrix)
  * 4.1 [ApexMatrix.\_\_init\_\_](#apexmatrix---init--)
* 5 [Class ApexPoint](#apexpoint)
  * 5.1 [ApexPoint.\_\_add\_\_](#apexpoint---add--)
  * 5.2 [ApexPoint.\_\_init\_\_](#apexpoint---init--)
  * 5.3 [ApexPoint.\_\_neg\_\_](#apexpoint---neg--)
  * 5.4 [ApexPoint.\_\_repr\_\_](#apexpoint---repr--)
  * 5.5 [ApexPoint.\_\_rmul\_\_](#apexpoint---rmul--)
  * 5.6 [ApexPoint.\_\_str\_\_](#apexpoint---str--)
  * 5.7 [ApexPoint.\_\_sub\_\_](#apexpoint---sub--)
  * 5.8 [ApexPoint.\_\_truediv\_\_](#apexpoint---truediv--)
  * 5.9 [ApexPoint.atan2](#apexpoint-atan2)
  * 5.10 [ApexPoint.forward](#apexpoint-forward)
  * 5.11 [ApexPoint.magnitude](#apexpoint-magnitude)

## 1 <a name="introduction"></a>Introduction


The Apex Base classes are:
* ApexLength:
  This is sub-class of *float* and provides a way of specifying a length in different units
  (e.g. mm, cm, inch, ft, etc.) and an optional name.
* ApexBoundBox:
  This is a wrapper class around the FreeCAD BoundBox class for specifying bounding boxes.
  It introduces some consistent attributes for accessing the faces, corners and edges
  of a bounding box.  Alas, for technical reasons, this not a true sub-class of BoundBox.
* ApexPoint:
  This is a wrapper class around the FreeCAD Vector class that adds an optional diameter
  and name for each 3D Vector point.  For the same technical reasons, this is not a true
  sub-class of Vector.
* ApexMatrix:
  This is a wrapper class around the FreeCAD Matrix class that provides an openGL style
  transformation consisting of a rotation point, rotation axis, and rotation angle,
  followed by a final translation.  It also computes the inverse matrix.


## 2 Class ApexBoundBox <a name="apexboundbox"></a>

class ApexBoundBox:

An ApexBoundBox is FreeCAD BoundBox with some additional attributes.

An ApexBoundBox is a simple wrapper around a FreeCAD BoundBox object that provides
additional attributes that represent various points on the surface of the bounding box.
The nomenclature is that East/West represents the X axis, North/South represents the Y axis,
and the Top/Bottom represents the Z axis.  Thus, TNE represents the Top North East corner
of the bounding box.  NE represents the center of the North East edge of the bounding box.
T represents the center of the top face of the bounding box.  By the way, the C attribute
is the same as the BoundBox Center attribute.

The preferred way to do this would be to sub-class BoundBox, but the FreeCAD implementation
is written in C++ and for technical reasons does not support sub-classing.

* Attributes (alphabetical order in each group):
  * The 6 face attributes:
    * B (Vector): Center of bottom face.
    * E (Vector): Center of east face.
    * N (Vector): Center of north face.
    * S (Vector): Center of south face.
    * T (Vector): Center of top face.
    * W (Vector): Center of west face.
  * The 8 corner attributes:
    * BNE (Vector): Bottom North East corner.
    * BNW (Vector): Bottom North West corner.
    * BSE (Vector): Bottom South East corner.
    * BSW (Vector): Bottom South West corner.
    * TNE (Vector): Top North East corner.
    * TNW (Vector): Top North West corner.
    * TSE (Vector): Top South East corner.
    * TSW (Vector): Bottom South West corner.
  * The 12 edge attributes:
    * BE (Vector): Center of Bottom East edge.
    * BN (Vector): Center of Bottom North edge.
    * BS (Vector): Center of Bottom South edge.
    * BW (Vector): Center of Bottom West edge.
    * NE (Vector): Center of North East edge
    * NW (Vector): Center of North West edge
    * SE (Vector): Center of South East edge
    * SW (Vector): Center of South West edge
    * TE (Vector): Center of Top East edge.
    * TN (Vector): Center of Top North edge.
    * TS (Vector): Center of Top South edge.
    * TW (Vector): Center of Top West edge.
  * The other ttributes:
    * C (Vector): Center point (same as Center).
    * BB (BoundBox): The wrapped BoundBox object.

### 2.1 ApexBoundBox.\_\_init\_\_ <a name="apexboundbox---init--"></a>

def \_\_init\_\_(self, *bound\_box*:  BoundBox) -> None:

Initialize an ApexBoundBox.

Read about \_\_new\_\_() vs. \_\_init\_\_() at the URL below:
* [new](https://stackoverflow.com/questions/4859129/python-and-python-c-api-new-versus-init)

* Arguments:
  *bound\_box* (BoundBox): The bounding box to wrap.

### 2.2 ApexBoundBox.\_\_repr\_\_ <a name="apexboundbox---repr--"></a>

def \_\_repr\_\_(self) -> *str*:

Return a representation of an ApexBoundBox.

### 2.3 ApexBoundBox.\_\_str\_\_ <a name="apexboundbox---str--"></a>

def \_\_str\_\_(self) -> *str*:

Return a representation of an ApexBoundBox.

### 2.4 ApexBoundBox.from\_vectors <a name="apexboundbox-from-vectors"></a>

def *from\_vectors*(vectors:  Tuple[Union[Vector, "ApexPoint"], ...]) -> "ApexBoundBox":

Compute BoundingBox from some Point's.

## 3 Class ApexLength <a name="apexlength"></a>

class ApexLength(float):

ApexLength is a float with with optional name and units.

* Attributes:
  * *length* (float): The length measured in millimeters.
  * *units* (str): The units (e.g. "km", "m", "cm", "mm", "µm", "nm", "ft", "thou", etc.)
  * *name* (str): The optional name.

### 3.1 ApexLength.\_\_new\_\_ <a name="apexlength---new--"></a>

def \_\_new\_\_(cls, *args, **kwargs) -> "ApexLength":

Create an ApexLength.

(Note: When sub-classing *float*, \_\_new\_\_() is used instead of \_\_init\_\_().)
The actual function signature is:
      \_\_new\_\_(cls, value: Union[float, int] = 0.0, units: str = "mm", name: str = ""):

* Arguments:
  * *value* (Union[float, int]): The distance value.  (Optional: Default = 0.0).
  * *units* (str): The units to use.  (Optional: Default = "mm").
  * *name*: (str): An name to associate with the length.  (Optional: Default = "").
* Returns:
  (ApexLength) containing the desired values.

### 3.2 ApexLength.\_\_repr\_\_ <a name="apexlength---repr--"></a>

def \_\_repr\_\_(self) -> *str*:

Return the string representation.

### 3.3 ApexLength.\_\_str\_\_ <a name="apexlength---str--"></a>

def \_\_str\_\_(self) -> *str*:

Return the string representation.

### 3.4 ApexLength.unit\_test <a name="apexlength-unit-test"></a>

def *unit\_tests*() -> None:

Perform Unit tests for ApexLength.

### 3.5 ApexLength.unit\_test <a name="apexlength-unit-test"></a>

def *unit\_tests*() -> None:  Perform Unit *tests* *for* ApexLength. *def* *check*(apex\_length:  ApexLength, *length*:  *float*, *value*:  *float*, *units*:  *str*, *name*:  *str*, *repr*:  *str*) -> None:

Ensure that an ApexLength has the right values.

## 4 Class ApexMatrix <a name="apexmatrix"></a>

class ApexMatrix:

ApexMatrix is a wrapper around the FreeCAD Matrix class.

This is a wrapper class around the FreeCAD Matrix class that provides an openGL style
transformation consisting of a rotation point, rotation axis, and rotation angle,
followed by a final translation.  It also computes the inverse matrix.

* Attributes:
  * *forward* (Matrix): A FreeCAD Matrix that maps a Vector to a new location.
  * *reverse* (Matrix): The inverse FreeCAD matrix that for new not location back.

### 4.1 ApexMatrix.\_\_init\_\_ <a name="apexmatrix---init--"></a>

def \_\_init\_\_(self, *center*:  Optional[Union[ApexPoint, Vector]] = None, *axis*:  Optional[Union[ApexPoint, Vector]] = None, # Z *axis* *angle*:  Optional[float] = None, *translate*:  Optional[Union[ApexPoint, Vector]] = None, *name*:  Optional[str] = None, *tracing*:  *str* = "") -> None:

Create ApexMatrix rotation with point/axis/angle and a translate.

## 5 Class ApexPoint <a name="apexpoint"></a>

class ApexPoint:

An ApexPoint is basically just a Vector with an optional diameter and/or name.

* Attributes:
  * *vector* (Vector): The underlying FreeCAD Vector.
  * *x* (float): The x coordinate of the vector.
  * *y* (float): The y coordinate of the vector.
  * *z* (float): The z coordinate of the vector.
  * *diameter* (Union[float, ApexLength]): The apex diameter.
  * *radius* (float): The apex radius.
  * *name* (str): The apex name.

### 5.1 ApexPoint.\_\_add\_\_ <a name="apexpoint---add--"></a>

def \_\_add\_\_(self, *vector*:  "ApexPoint") -> "ApexPoint":

Return the sum of two ApexPoint's.

### 5.2 ApexPoint.\_\_init\_\_ <a name="apexpoint---init--"></a>

def \_\_init\_\_(self, *x*:  Union[int, *float*, ApexLength] = 0.0, *y*:  Union[int, *float*, ApexLength] = 0.0, *z*:  Union[int, *float*, ApexLength] = 0.0, *diameter*:  Union[int, *float*, ApexLength] = 0.0, *name*:  *str* = "") -> None:

Initialize an ApexPoint.

* Arguments:
  * *x* (Union[int, float, ApexLength]): The x coordinate of the vector. (Default: 0.0)
  * *y* (Union[int, float, ApexLength]): The y coordinate of the vector. (Default: 0.0)
  * *z* (Union[int, float, ApexLength]): The z coordinate of the vector. (Default: 0.0)
  * *diameter* (Union[int, float, ApexLength]): The apex diameter. (Default: 0.0)
  * *name* (str): A name primarily used for debugging. (Default: "")

### 5.3 ApexPoint.\_\_neg\_\_ <a name="apexpoint---neg--"></a>

def \_\_neg\_\_(self) -> "ApexPoint":

Return the negative of an ApexPoint.

### 5.4 ApexPoint.\_\_repr\_\_ <a name="apexpoint---repr--"></a>

def \_\_repr\_\_(self) -> *str*:

Return representation of ApexPoint.

### 5.5 ApexPoint.\_\_rmul\_\_ <a name="apexpoint---rmul--"></a>

def \_\_mul\_\_(self, *scale*:  *float*) -> "ApexPoint":

Return a Point that has been scaled.

### 5.6 ApexPoint.\_\_str\_\_ <a name="apexpoint---str--"></a>

def \_\_str\_\_(self) -> *str*:

Return string representation of ApexPoint.

### 5.7 ApexPoint.\_\_sub\_\_ <a name="apexpoint---sub--"></a>

def \_\_sub\_\_(self, *vector*:  "ApexPoint") -> "ApexPoint":

Return the difference of two Point's.

### 5.8 ApexPoint.\_\_truediv\_\_ <a name="apexpoint---truediv--"></a>

def \_\_truediv\_\_(self, *divisor*:  *float*) -> "ApexPoint":

Return a Point that has been scaleddown.

### 5.9 ApexPoint.atan2 <a name="apexpoint-atan2"></a>

def *atan2*(self) -> *float*:

Return the atan2 of the x and y values.

### 5.10 ApexPoint.forward <a name="apexpoint-forward"></a>

def *forward*(self, *matrix*:  "ApexMatrix") -> "ApexPoint":

Perform a forward matrix transform using an ApexMatrix.

### 5.11 ApexPoint.magnitude <a name="apexpoint-magnitude"></a>

def *magnitude*(self) -> *float*:

Return the magnitude of the point vector.
