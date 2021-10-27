# Apex base classes.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class ApexBox](#apexbox)
  * 2.1 [ApexBox.\_\_init\_\_](#apexbox---init--)
  * 2.2 [ApexBox.reorient](#apexbox-reorient)
* 3 [Class ApexCheck](#apexcheck)
  * 3.1 [ApexCheck.check](#apexcheck-check)
* 4 [Class ApexLength](#apexlength)
  * 4.1 [ApexLength.\_\_new\_\_](#apexlength---new--)
  * 4.2 [ApexLength.\_\_repr\_\_](#apexlength---repr--)
  * 4.3 [ApexLength.\_\_str\_\_](#apexlength---str--)
* 5 [Class ApexMaterial](#apexmaterial)
  * 5.1 [ApexMaterial.\_\_init\_\_](#apexmaterial---init--)
* 6 [Class ApexPoint](#apexpoint)
  * 6.1 [ApexPoint.\_\_init\_\_](#apexpoint---init--)
  * 6.2 [ApexPoint.atan2](#apexpoint-atan2)
  * 6.3 [ApexPoint.magnitude](#apexpoint-magnitude)

## 1 <a name="introduction"></a>Introduction


The Apex base classes are:
* ApexBox:
  This is a wrapper class around the FreeCAD BoundBox class for specifying bounding boxes.
  It introduces some consistent attributes for accessing the faces, corners and edges
  of a bounding box.  Alas, for technical reasons, this not a true sub-class of BoundBox.
  Also, it called a box rather than a bounding box.
* ApexCheck:
  This is some common code to check argument types for public functions.
* ApexLength:
  This is sub-class of *float* and provides a way of specifying a length in different units
  (e.g. mm, cm, inch, ft, etc.) and an optional name.
* ApexMaterial:
  This is a class that describes material properties.
* ApexPoint:
  This is a wrapper class around the FreeCAD Vector class that adds an optional diameter
  and name for each 3D Vector point.  For the same technical reasons, this is not a true
  sub-class of Vector.


## 2 Class ApexBox <a name="apexbox"></a>

class ApexBox:

An ApexBox is FreeCAD BoundBox with some additional attributes.

An ApexBox is a simple wrapper around a FreeCAD BoundBox object that provides
additional attributes that represent various points on the surface of the box.
The nomenclature is that East/West represents the +X/-X axes, North/South represents the
+Y/-Y axes, nd the Top/Bottom represents the +Z/-Z axes.  Thus, TNE represents the Top
North East corner of the box.  NE represents the center of the North East edge of the
box.  T represents the center of the top face of the box.  By the way, the C attribute
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
    * BB (BoundBox): The wrapped BoundBox object.
    * C (Vector): Center point (same as Center).
    * DB (Vector): Bottom direction (i.e. B - C)
    * DE (Vector): East direction (i.e. E - C)
    * DN (Vector): North direction (i.e. N - C)
    * DS (Vector): South direction (i.e. S - C)
    * DT (Vector): Top direction (i.e. T - C)
    * DW (Vector): West direction (i.e. W - C)
    * DX (float): X box length
    * DXY (Vector): X box length
    * DXZ (Vector): X/Y box lengths
    * DXYZ (Vector): X/Y/Z box lengths
    * DY (float): Y box length
    * DYZ (Vector): Y/Z box length
    * DZ (float): Z box length
    * Name (str): The ApexBox name.

### 2.1 ApexBox.\_\_init\_\_ <a name="apexbox---init--"></a>

def \_\_init\_\_(self, *corners*:  Sequence[Union[Vector, "ApexPoint", BoundBox, "ApexBox"]], *name*:  *str* = "") -> None:

Initialize an ApexBox.

Arguments:
  * *corners* (Sequence[Union[Vector, ApexPoint, BoundBox, ApexBox]]):
    A sequence of points/corners to enclose by the box.

Raises:
  * ValueError: For bad or empty corners.


### 2.2 ApexBox.reorient <a name="apexbox-reorient"></a>

def *reorient*(self, *placement*:  Placement, *suffix*:  Optional[str] = "") -> "ApexBox":

Reorient ApexBox given a Placement.

Note after the *placement* is applied, the resulting box is still rectilinear with the
X/Y/Z axes.  In particular, box volume is *not* conserved.

Arguments:
* *placement* (Placement): The placement of the box corners.
* *suffix* (Optional[str]): The suffix to append at all names.  If None, all
  names are set to "" instead appending the suffix.  (Default: "")

## 3 Class ApexCheck <a name="apexcheck"></a>

class ApexCheck(object):

ApexCheck: Check arguments for type mismatch errors.

Attributes:
* *name* (str):
   The argument name (used for error messages.)
* *type* (Tuple[Any]):
  A tuple of acceptable types.

An ApexCheck contains is used to type check a single function argument.
The static method `Apexcheck.check()` takes a list of argument values and the
corresponding tuple ApexCheck's and verifies that they are correct.

Example:

     MY\_FUNCTION\_CHECKS = (
         ApexCheck("arg1", int),
         ApexCheck("arg2", bool),
         ApexCheck("arg3", object),  # Any <=> object
         ApexCheck("arg4," list),   # List <=> list
     )
     def my\_function(arg1: int, arg2: bool, arg3: Any, arg4: List[str]) -> None:
         Doc string here.
        value\_error: str = ApexCheck.check((arg1, arg2, arg3, arg4), MY\_FUNCTION\_CHECKS)
        if value\_error:
            raise ValueError(value\_error)
        # Rest of code goes here.


### 3.1 ApexCheck.check <a name="apexcheck-check"></a>

def *check*(cls, *values*:  Sequence[Any], *apex\_checks*:  Sequence["ApexCheck"]) -> *str*:

Return type mismatch error message.

## 4 Class ApexLength <a name="apexlength"></a>

class ApexLength(float):

ApexLength is a float with with optional name and units.

* Attributes:
  * *length* (float): The length measured in millimeters.
  * *units* (str): The units (e.g. "km", "m", "cm", "mm", "µm", "nm", "ft", "thou", etc.)
  * *name* (str): The optional name.

### 4.1 ApexLength.\_\_new\_\_ <a name="apexlength---new--"></a>

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

### 4.2 ApexLength.\_\_repr\_\_ <a name="apexlength---repr--"></a>

def \_\_repr\_\_(self) -> *str*:

Return the string representation.

### 4.3 ApexLength.\_\_str\_\_ <a name="apexlength---str--"></a>

def \_\_str\_\_(self) -> *str*:

Return the string representation.

## 5 Class ApexMaterial <a name="apexmaterial"></a>

class ApexMaterial(object):

ApexMaterial: Represents a stock material.

Other properties to be added later (e.g. transparency, shine, machining properties, etc.)

Attributes:
* *name* (Tuple[str, ...]): A list of material names from generict to specific.
* *color* (str): The color name to use.


### 5.1 ApexMaterial.\_\_init\_\_ <a name="apexmaterial---init--"></a>

def \_\_init\_\_(self, *name*:  Tuple[str, ...], *color*:  *str*) -> None:

Initialize and ApexMaterial.

* Arguments:
  * *name* (Tuple[str, ...): Non-empty to tuple of material names from broad to narrow.
  * *color* (str):
     An [SVG color name](https://www.december.com/html/spec/colorsvgsvg.html).

* Raises:
  * ValueError for either an empty name or a bad svg color.

## 6 Class ApexPoint <a name="apexpoint"></a>

class ApexPoint:

An ApexPoint is basically just a Vector with an optional diameter and/or name.

* Attributes:
  * *vector* (Vector): The underlying FreeCAD Vector.
  * *x* (Union[float, Apex): The x coordinate of the vector.
  * *y* (float): The y coordinate of the vector.
  * *z* (float): The z coordinate of the vector.
  * *diameter* (Union[float, ApexLength]): The apex diameter.
  * *radius* (float): The apex radius.
  * *name* (str): The apex name.
  * *box* (ApexBox): The ApexBox that encloses an ApexPoint assuming a *diameter* sphere.

### 6.1 ApexPoint.\_\_init\_\_ <a name="apexpoint---init--"></a>

def \_\_init\_\_( *self*, *x*:  Union[int, *float*, ApexLength] = 0.0, *y*:  Union[int, *float*, ApexLength] = 0.0, *z*:  Union[int, *float*, ApexLength] = 0.0, *diameter*:  Union[int, *float*, ApexLength] = 0.0, *name*:  *str* = "", *vector*:  Optional[Vector] = None, *fix*:  *bool* = False ) -> None:

Initialize an ApexPoint.

Arguments:
  * *x* (Union[int, float, ApexLength]): The x coordinate of the vector. (Default: 0.0)
  * *y* (Union[int, float, ApexLength]): The y coordinate of the vector. (Default: 0.0)
  * *z* (Union[int, float, ApexLength]): The z coordinate of the vector. (Default: 0.0)
  * *diameter* (Union[int, float, ApexLength]): The apex diameter. (Default: 0.0)
  * *name* (str): A name primarily used for debugging. (Default: "")
  * *vector* (Vector): A vector to initialize *x*, *y*, and *z* with.
    (Default: Vector(0.0, 0.0, 0.0)
  * *fix* (bool): If True, fix float values that are close to hole numbers to be whole.

### 6.2 ApexPoint.atan2 <a name="apexpoint-atan2"></a>

def *atan2*(self) -> *float*:

Return the atan2 of the x and y values.

### 6.3 ApexPoint.magnitude <a name="apexpoint-magnitude"></a>

def *magnitude*(self) -> *float*:

Return the magnitude of the point vector.
