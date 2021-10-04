# Apex base classes.

The Apex Base classes are:
* ApexLength:
  This is sub-class of *float* and provides a way of specifying a length in different units
  (e.g. mm, cm, inch, ft, etc.) and an optional name.
* ApexBoundBox:
  This is a wrapper class around the FreeCAD BoundBox class for specifying bounding boxes.
  It introduces some consistent attributes for accessing the faces, corners and edges
  of a bounding box.  Alas, for technical reasons, this not a true sub-class of BoundBox.
* ApexVector:
  This is a wrapper class around the FreeCAD Vector class that adds an optional diameter
  and name for each 3D Vector point.  For the same technical reasons, this is not a true
  sub-class of Vector.
* ApexMatrix:
  This is a wrapper class around the FreeCAD Matrix class that provides an openGL style
  transformation consisting of a rotation point, rotation axis, and rotation angle,
  followed by a final translation.  It also computes the inverse matrix.

## 1.0 Class ApexLength(float)

class ApexLength(float):

ApexLength is a float with with optional name and units.

* Attributes:
  * *length* (float): The length measured in millimeters.
  * *units* (str): The units (e.g. "km", "m", "cm", "mm", "µm", "nm", "ft", "thou", etc.)
  * *name* (str): The optional name.

### 1.1 ApexLength.\_\_new\_\_

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

### 1.2 ApexLength.\_\_repr\_\_

def \_\_repr\_\_(self) -> *str*:

Return the string representation.

### 1.3 ApexLength.\_\_str\_\_

def \_\_str\_\_(self) -> *str*:

Return the string representation.

def *length*(self) -> *float*:

Return length in millimeters as a float.

def *units*(self) -> *str*:

Return the units.

def *name*(self) -> *str*:

Return the name.

def *value*(self) -> *float*:

Return the value in user specfied units.

### 1.4 ApexLength.unit\_test

def *unit\_tests*() -> None:

Perform Unit tests for ApexLength.

### 1.5 ApexLength.unit\_test

def *unit\_tests*() -> None:  Perform Unit *tests* *for* ApexLength. *def* *check*(apex\_length:  ApexLength, *length*:  *float*, *value*:  *float*, *units*:  *str*, *name*:  *str*, *repr*:  *str*) -> None:

Ensure that an ApexLength has the right values.

## 2.0 Class ApexBoundBox

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

### 2.1 ApexBoundBox.\_\_init\_\_

def \_\_init\_\_(self, *bound\_box*:  BoundBox) -> None:

Initialize an ApexBoundBox.

Read about \_\_new\_\_() vs. \_\_init\_\_() at the URL below:
* [new](https://stackoverflow.com/questions/4859129/python-and-python-c-api-new-versus-init)

* Arguments:
  *bound\_box* (BoundBox): The bounding box to wrap.

def B(self) -> Vector:

Bottom face center.

def E(self) -> Vector:

East face center.

def N(self) -> Vector:

North face center.

def S(self) -> Vector:

South face center.

def T(self) -> Vector:

Top face center.

def W(self) -> Vector:

Center of bottom face.

def BNE(self) -> Vector:

Bottom North East corner.

def BNW(self) -> Vector:

Bottom North West corner.

def BSE(self) -> Vector:

Bottom South East corner.

def BSW(self) -> Vector:

Bottom South West corner.

def TNE(self) -> Vector:

Top North East corner.

def TNW(self) -> Vector:

Top North West corner.

def TSE(self) -> Vector:

Top South East corner.

def TSW(self) -> Vector:

Top South West corner.

def BE(self) -> Vector:

Bottom East edge center.

def BW(self) -> Vector:

Bottom West edge center.

def BN(self) -> Vector:

Bottom North edge center.

def BS(self) -> Vector:

Bottom South edge center.

def NE(self) -> Vector:

North East edge center.

def NW(self) -> Vector:

North West edge center.

def SE(self) -> Vector:

North East edge center.

def SW(self) -> Vector:

South East edge center.

def TE(self) -> Vector:

Bottom East edge center.

def TW(self) -> Vector:

Bottom West edge center.

def TN(self) -> Vector:

Bottom North edge center.

def TS(self) -> Vector:

Bottom South edge center.

def BB(self) -> BoundBox:

Access the wrapped a BoundBox.

def C(self) -> Vector:

Center point.

def *unit\_tests*() -> None:

Perform ApexBoundBox unit tests.

## 3.0 Class ApexVector

class ApexVector:

An ApexVector is basically just a Vector with an optional diameter and/or name.

* Attributes:
  * *vector* (Vector): The underlying FreeCAD Vector.
  * *x* (float): The x coordinate of the vector.
  * *y* (float): The y coordinate of the vector.
  * *z* (float): The z coordinate of the vector.
  * *diameter* (Union[float, ApexLength]): The apex diameter.
  * *radius* (float): The apex radius.
  * *name* (str): The apex name.

### 3.1 ApexVector.\_\_init\_\_

def \_\_init\_\_(self, *x*:  Union[int, *float*, ApexLength] = 0.0, *y*:  Union[int, *float*, ApexLength] = 0.0, *z*:  Union[int, *float*, ApexLength] = 0.0, *diameter*:  Union[int, *float*, ApexLength] = 0.0, *name*:  *str* = "") -> None:

Initialize an ApexVector.

* Arguments:
  * *x* (Union[int, float, ApexLength]): The x coordinate of the vector. (Default: 0.0)
  * *y* (Union[int, float, ApexLength]): The y coordinate of the vector. (Default: 0.0)
  * *z* (Union[int, float, ApexLength]): The z coordinate of the vector. (Default: 0.0)
  * *diameter* (Union[int, float, ApexLength]): The apex diameter. (Default: 0.0)
  * *name* (str): A name primarily used for debugging. (Default: "")

### 3.2 ApexVector.\_\_repr\_\_

def \_\_repr\_\_(self) -> *str*:

Return representation of ApexVector.

### 3.3 ApexVector.\_\_str\_\_

def \_\_str\_\_(self) -> *str*:

Return string representation of ApexVector.

def *unit\_tests*() -> None:

Perform ApexVector unit tests.

## 4.0 Class ApexMatrix

class ApexMatrix:

ApexMatrix is a wrapper around the FreeCAD Matrix class.

This is a wrapper class around the FreeCAD Matrix class that provides an openGL style
transformation consisting of a rotation point, rotation axis, and rotation angle,
followed by a final translation.  It also computes the inverse matrix.

* Attributes:
  * *forward* (Matrix): A FreeCAD Matrix that maps a Vector to a new location.
  * *reverse* (Matrix): The inverse FreeCAD matrix that for new not location back.

### 4.1 ApexMatrix.\_\_init\_\_

def \_\_init\_\_(self, *center*:  Optional[Union[ApexVector, Vector]] = None, *axis*:  Optional[Union[ApexVector, Vector]] = None, # Z *axis* *angle*:  Optional[float] = None, *translate*:  Optional[Union[ApexVector, Vector]] = None, *name*:  Optional[str] = None) -> None:

Create ApexMatrix rotation with point/axis/angle and a translate.

def *zf*(value:  *float*) -> *float*:

Round values near zero to zero.

def \_rotate(axis:  Union[ApexVector, Vector], *angle*:  *float*) -> Matrix:

Return a FreeCAD Matrix for rotation around an axis.

* Arguments:
* *axis* (Union[ApexVector, Vector]): The axis to rotate around.
  * *angle* (float): The number of radians to rotate by.
* Returns:
  * Returns the FreeCAD rotation Matrix.

def *matrix\_clean*(matrix:  Matrix) -> Matrix:

Return a matrix where values close to zero are set to zero.

def \_\_repr\_\_(self) -> *str*:

Return string representation of an ApexMatrix.

def \_\_str\_\_(self) -> *str*:

Return string representation of an ApexMatrix.

def *forward*(self) -> Matrix:

Return the FreeCAD Matrix.

def *reverse*(self) -> Matrix:

Return the FreeCAD Matrix.

def *unit\_tests*() -> None:

Run unit tests.

def *main*() -> None:

Run the unit tests.

