# Apex base classes.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class ApexBox](#apexbox)
  * 2.1 [ApexBox.\_\_init\_\_](#apexbox---init--)
  * 2.2 [ApexBox.reorient](#apexbox-reorient)
* 3 [Class ApexCheck](#apexcheck)
  * 3.1 [ApexCheck.check](#apexcheck-check)
  * 3.2 [ApexCheck.init\_show](#apexcheck-init-show)
* 4 [Class ApexColor](#apexcolor)
* 5 [Class ApexMaterial](#apexmaterial)
  * 5.1 [ApexMaterial.\_\_init\_\_](#apexmaterial---init--)
  * 5.2 [float\_fix](#float-fix)
  * 5.3 [vector\_fix](#vector-fix)

## 1 <a name="introduction"></a>Introduction


The Apex base classes are:
* ApexBox:
  This is a wrapper class around the FreeCAD BoundBox class for specifying bounding boxes.
  It introduces some consistent attributes for accessing the faces, corners and edges
  of a bounding box.  Alas, for technical reasons, this not a true sub-class of BoundBox.
  Also, it called a box rather than a bounding box.
* ApexCheck:
  This is some common code to check argument types for public functions.
* ApexMaterial:
  This is a class that describes material properties.
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

def \_\_init\_\_(self, *corners*:  Sequence[Union[Vector, BoundBox, "ApexBox"]], *name*:  *str* = "") -> None:

Initialize an ApexBox.

Arguments:
  * *corners* (Sequence[Union[Vector, BoundBox, ApexBox]]):
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
* *types* (Tuple[Any]):
  A tuple of acceptable types or constrained types.  A type is something line `bool`, `int`,
  `float`, `MyClass`, etc.   A constrained type is a tuple of the form (str, Any, Any, ...)
  and are discussed further below.

An ApexCheck contains is used to type check a single function argument.
The static method `ApexCheck.check()` takes a list of argument values and the
corresponding tuple ApexCheck's and verifies that they are correct.

Example 1:

     EXAMPLE1\_CHECKS = (
         ApexCheck("arg1", (int,)),
         ApexCheck("arg2", (bool,)),
         ApexCheck("arg3", (type(None), MyType),  # Optional[myType]
         ApexCheck("arg4," list),   # List[Any]
     )
     def my\_function(arg1: int, arg2: bool, arg3: Any, arg4: List[str]) -> None:
         Doc string here.
        value\_error: str = ApexCheck.check((arg1, arg2, arg3, arg4), MY\_FUNCTION\_CHECKS)
        if value\_error:
            raise ValueError(value\_error)
        # Rest of code goes here.

A constrained type looks like `("xxx:yyy:zzz", XArg, YArg, ZArg)`, where the `xxx` are flag
characters are associated with `XArg`, `yyy` are for `YArg`, etc.  The flag characters are:
* `L`: A List of Arg
* `T`: A Tuple of Arg
* `S`: A List or Tuple of Arg
* `+`: Len of Arg must be greater than 0
* `?`: None is acceptible.
Additional flags are added as needed.

Example 2:

    EXAMPLE2\_CHECKS = (
        ApexCheck("arg1", ("+", str)),  # Arg1 must be a non-empty string
        ApexCheck("arg2", ("?", str)),  # Arg2 can be a string or None
        ApexCheck("arg3", ("+?", str)),  # Arg3 can be a non-empty string or None
        ApexCheck("arg4", ("L", str)),  # Arg4 can be a list of strings
        ApexCheck("arg5", ("T", str)),  # Arg4 can be a tuple of strings
        ApexCheck("arg6", ("S", str)),  # Arg6 can be a list or tuple of strings
        ApexCheck("arg7", ("L", (float, int)),  # Arg7 can be a list of mixed float and int


### 3.1 ApexCheck.check <a name="apexcheck-check"></a>

def *check*(cls, *values*:  Sequence[Any], *apex\_checks*:  Sequence["ApexCheck"], *tracing*:  *str* = "") -> *str*:

Return type mismatch error message.

### 3.2 ApexCheck.init\_show <a name="apexcheck-init-show"></a>

def *init\_show*(name:  *str*, *arguments*:  Sequence[Any], *apex\_checks*:  Sequence["ApexCheck"]) -> *str*:

Return string representation based in initializer arguments.

Arguments:
* *name* (str): Full fuction/method name.
* *arguments* (Sequence[Any]): All argument values.
* *apex\_checks*: (Sequence[ApexCheck]): Associated ApexCheck's.

Returns:
* (str) containing function/method name with associated initialize arguments:

Raises:
* ValueError: For length mismatches and bad parameter types:


## 4 Class ApexColor <a name="apexcolor"></a>

class ApexColor(object):

ApexColor: Convert from SVG color names to FreeCAD HSL.

## 5 Class ApexMaterial <a name="apexmaterial"></a>

class ApexMaterial(object):

ApexMaterial: Represents a stock material.

Other properties to be added later (e.g. transparency, shine, machining properties, etc.)

Attributes:
* *Name* (Tuple[str, ...]): A list of material names from generict to specific.
* *Color* (str): The color name to use.


### 5.1 ApexMaterial.\_\_init\_\_ <a name="apexmaterial---init--"></a>

def \_\_post\_init\_\_(self) -> None:

Post process.

### 5.2 float\_fix <a name="float-fix"></a>

def *float\_fix*(length:  *float*) -> *float*:

Return a length that is rounded to a whole number when appropriate.

### 5.3 vector\_fix <a name="vector-fix"></a>

def *vector\_fix*(vector:  Vector) -> Vector:

Return Vector with values rounded to appropriate hole numbers.
