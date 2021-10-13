#!/usr/bin/env python3
"""Apex base classes.

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
* ApexPlace:
  This is a wrapper class around the FreeCAD Matrix class that provides an openGL style
  transformation consisting of a rotation point, rotation axis, and rotation angle,
  followed by a final translation.  It also computes the inverse matrix.

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

import os
import sys

assert sys.version_info.major == 3, "Python 3.x is not running"
assert sys.version_info.minor == 8, "Python 3.8 is not running"
sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])

from FreeCAD import BoundBox, Matrix, Vector  # type: ignore

import math
from typing import Any, Callable, ClassVar, List, Dict, Optional, Tuple, Union


# ApexLength:
class ApexLength(float):
    """ApexLength is a float with with optional name and units.

    * Attributes:
      * *length* (float): The length measured in millimeters.
      * *units* (str): The units (e.g. "km", "m", "cm", "mm", "µm", "nm", "ft", "thou", etc.)
      * *name* (str): The optional name.
    """

    _conversions: ClassVar[Dict[str, float]] = {
        "km": 1000000.0,
        "m": 1000.0,
        "cm": 10.0,
        "mm": 1.0,
        "µm": 1. / 1000.0,  # Unicode in strings is fully suported by Python 3.
        "um": 1. / 1000.0,
        "nm": 1. / 1000000.0,
        "ft": 2.54 * 12.0,
        "in": 2.54,
        # "mil" means "thou" in US/Canada and "mm" everywhere else.  So it is not allowed.
        "thou": 2.54 / 1000.0,
    }
    _value: float
    _scale: float
    _units: str
    _name: str

    # ApexLength.__new__():
    def __new__(cls, *args, **kwargs) -> "ApexLength":
        """Create an ApexLength.

        (Note: When sub-classing *float*, __new__() is used instead of __init__().)
        The actual function signature is:
              __new__(cls, value: Union[float, int] = 0.0, units: str = "mm", name: str = ""):

        * Arguments:
          * *value* (Union[float, int]): The distance value.  (Optional: Default = 0.0).
          * *units* (str): The units to use.  (Optional: Default = "mm").
          * *name*: (str): An name to associate with the length.  (Optional: Default = "").
        * Returns:
          (ApexLength) containing the desired values.
        """
        tracing: str = kwargs["tracing"] if "tracing" in kwargs else ""
        if tracing:
            print(f"{tracing}=>ApexLength.__new__({args}, {kwargs})")
        # Tediously extract arguments from *args* and *kwargs* (Probably there is a better way...):
        args_size: int = len(args)
        value: Any = args[0] if args_size >= 1 else (
            kwargs["value"] if "value" in kwargs else 0.0)
        if not isinstance(value, (float, int)):
            raise ValueError(f"value ({value}) is neither a neither a float nor int")
        value = float(value)

        units: Any = args[1] if args_size >= 2 else (
            kwargs["units"] if "units" in kwargs else "mm")
        units = units if units else "mm"
        if tracing:
            print(f"{tracing}{units=}")
        if not isinstance(units, str):
            raise ValueError(f"units ({units}) is not a str")
        conversions: Dict[str, float] = ApexLength._conversions
        if units not in conversions:
            raise ValueError(f"units ('{units}' units not one of {tuple(conversions.keys())}")
        scale = conversions[units]

        name: Any = args[2] if args_size >= 3 else (
            kwargs["name"] if "name" in kwargs else "")
        if not isinstance(name, str):
            raise ValueError(f"name ({name}) is not a str")

        # Install everything into *apex_length* and return.
        apex_length: ApexLength = super(ApexLength, cls).__new__(cls, value * scale)  # type: ignore
        apex_length._units = units
        apex_length._name = name
        apex_length._scale = scale
        assert isinstance(apex_length, float)
        assert isinstance(apex_length, ApexLength)
        if tracing:
            print(f"{tracing}<=ApexLength.__new__({args}, {kwargs})=>{apex_length}")
        return apex_length

    # ApexLength.__repr__():
    def __repr__(self) -> str:
        """Return the string representation."""
        value: float = float(self) / self._scale
        units: str = self._units
        name: str = self._name
        # print(f"=>repr({value}, '{units}', 'name')")

        name = f", '{name}'" if name else ""
        units = "" if not name and units == "mm" else f", '{units}'"
        result: str = f"ApexLength({value}{units}{name})"
        return result

    # ApexLength.__str__():
    def __str__(self) -> str:
        """Return the string representation."""
        return self.__repr__()

    @property
    def length(self) -> float:
        """Return length in millimeters as a float."""
        return float(self)

    @property
    def units(self) -> str:
        """Return the units."""
        return self._units

    @property
    def name(self) -> str:
        """Return the name."""
        return self._name

    @property
    def value(self) -> float:
        """Return the value in user specfied units."""
        return float(self) / self._scale

    # ApexLength.unit_test():
    @staticmethod
    def unit_tests() -> None:
        """Perform Unit tests for ApexLength."""
        def check(apex_length: ApexLength, length: float, value: float, units: str, name: str,
                  repr: str) -> None:
            """Ensure that an ApexLength has the right values."""
            assert apex_length.length == length, f"{apex_length.length} != {length}"
            assert apex_length.value == value, f"{apex_length.value} != {value}"
            assert apex_length.units == units, f"{apex_length.units} != {units}"
            assert apex_length.__repr__() == repr, f"'{apex_length.__repr__()}' != '{repr}'"

        f0a: ApexLength = ApexLength()  # No arguments
        assert isinstance(f0a, ApexLength)
        check(f0a, 0.0, 0.0, "mm", "", "ApexLength(0.0)")
        f0b: ApexLength = ApexLength(0)  # Integer argument of zero.
        check(f0b, 0.0, 0.0, "mm", "", "ApexLength(0.0)")

        f1a: ApexLength = ApexLength(1.0)  # Float argument
        check(f1a, 1.0, 1.0, "mm", "", "ApexLength(1.0)")
        f1b: ApexLength = ApexLength(1)  # Integer argument
        check(f1b, 1.0, 1.0, "mm", "", "ApexLength(1.0)")

        f10a: ApexLength = ApexLength(1.0, "cm")
        check(f10a, 10.0, 1.0, "cm", "", "ApexLength(1.0, 'cm')")
        f10b: ApexLength = ApexLength(10)
        check(f10b, 10.0, 10.0, "mm", "", "ApexLength(10.0)")
        assert float(f10a) == float(f10b)

        f254a: ApexLength = ApexLength(1, "in")
        check(f254a, 2.54, 1.0, "in", "", "ApexLength(1.0, 'in')")
        f254b: ApexLength = ApexLength(2.54)
        check(f254b, 2.54, 2.54, "mm", "", "ApexLength(2.54)")
        assert float(f254a) == float(f254b)

        f0c: ApexLength = ApexLength(name="f0c")
        check(f0c, 0.0, 0.0, "mm", "", "ApexLength(0.0, 'mm', 'f0c')")
        f0d: ApexLength = ApexLength(0, "", "f0d")
        check(f0d, 0.0, 0.0, "mm", "", "ApexLength(0.0, 'mm', 'f0d')")
        f1c: ApexLength = ApexLength(1, name="f1c")
        check(f1c, 1.0, 1.0, "mm", "", "ApexLength(1.0, 'mm', 'f1c')")
        assert f1c.name == "f1c"

        # Miscellaneous tests:
        assert str(f0a) == "ApexLength(0.0)", "test __str__()"
        # Do some error testing:
        try:
            ApexLength(units=7)
        except ValueError as value_error:
            assert str(value_error) == "units (7) is not a str"
        try:
            ApexLength(name=7)
        except ValueError as value_error:
            assert str(value_error) == "name (7) is not a str"


# ApexBoundBox:
class ApexBoundBox:
    """An ApexBoundBox is FreeCAD BoundBox with some additional attributes.

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
    """

    # ApexBoundBox.__init__():
    def __init__(self, bound_box: BoundBox) -> None:
        """Initialize an ApexBoundBox.

        Read about __new__() vs. __init__() at the URL below:
        * [new](https://stackoverflow.com/questions/4859129/python-and-python-c-api-new-versus-init)

        * Arguments:
          *bound_box* (BoundBox): The bounding box to wrap.
        """
        self._bound_box: BoundBox = bound_box

    # ApexBoundBox.from_vectors():
    @staticmethod
    def from_vectors(vectors: Tuple[Union[Vector, "ApexPoint"], ...]) -> "ApexBoundBox":
        """Compute BoundingBox from some Point's."""
        if not vectors:
            raise ValueError("No vectors")
        vector0: Vector = vectors[0]
        x_min: float = vector0.x
        y_min: float = vector0.y
        z_min: float = vector0.z
        x_max: float = x_min
        y_max: float = y_min
        z_max: float = z_min

        vector: Union[Vector, ApexPoint]
        for vector in vectors[1:]:
            x: float = vector.x
            y: float = vector.y
            z: float = vector.z
            x_min = min(x_min, x)
            y_min = min(y_min, y)
            z_min = min(z_min, z)
            x_max = max(x_max, x)
            y_max = max(y_max, y)
            z_max = max(z_max, z)

        bound_box: BoundBox = BoundBox(x_min, y_min, z_min, x_max, y_max, z_max)
        return ApexBoundBox(bound_box)

    @staticmethod
    def from_bound_boxes(
            bound_boxes: Tuple[Union[BoundBox, "ApexBoundBox"], ...]) -> "ApexBoundBox":
        """Create ApexBoundingBox from BoundingBox/ApexBoundBox tuple."""
        if not bound_boxes:
            raise ValueError("No bounding boxes")  # pragma: no unit test

        bound_box: Union[BoundBox, "ApexBoundBox"] = bound_boxes[0]
        bound_box = bound_box if isinstance(bound_box, BoundBox) else bound_box.BB
        assert isinstance(bound_box, BoundBox)
        x_min: float = bound_box.XMin
        y_min: float = bound_box.YMin
        z_min: float = bound_box.ZMin
        x_max: float = x_min
        y_max: float = y_min
        z_max: float = z_min

        for bound_box in bound_boxes[1:]:
            bound_box = bound_box if isinstance(bound_box, BoundBox) else bound_box.BB
            x_min = min(x_min, bound_box.XMin)
            y_min = min(y_min, bound_box.YMin)
            z_min = min(z_min, bound_box.ZMin)
            x_max = max(x_max, bound_box.XMax)
            y_max = max(y_max, bound_box.YMax)
            z_max = max(z_max, bound_box.ZMax)

        bound_box = BoundBox(x_min, y_min, z_min, x_max, y_max, z_max)
        return ApexBoundBox(bound_box)

    # Standard BoundBox attributes:

    @property
    def B(self) -> Vector:
        """Bottom face center."""
        bb: BoundBox = self._bound_box
        return Vector((bb.XMin + bb.XMax) / 2.0, (bb.YMin + bb.YMax) / 2.0, bb.ZMin)

    @property
    def E(self) -> Vector:
        """East face center."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMax, (bb.YMin + bb.YMax) / 2.0, (bb.ZMin + bb.ZMax) / 2.0)

    @property
    def N(self) -> Vector:
        """North face center."""
        bb: BoundBox = self._bound_box
        return Vector((bb.XMin + bb.XMax) / 2.0, bb.YMax, (bb.ZMin + bb.ZMax) / 2.0)

    @property
    def S(self) -> Vector:
        """South face center."""
        bb: BoundBox = self._bound_box
        return Vector((bb.XMin + bb.XMax) / 2.0, bb.YMin, (bb.ZMin + bb.ZMax) / 2.0)

    @property
    def T(self) -> Vector:
        """Top face center."""
        bb: BoundBox = self._bound_box
        return Vector((bb.XMin + bb.XMax) / 2.0, (bb.YMin + bb.YMax) / 2.0, bb.ZMax)

    @property
    def W(self) -> Vector:
        """Center of bottom face."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMin, (bb.YMin + bb.YMax) / 2.0, (bb.ZMin + bb.ZMax) / 2.0)

    # 8 Corner, BNE, BNW, BSE, BSW, TNE, TNW, TSE, TSW:

    @property
    def BNE(self) -> Vector:
        """Bottom North East corner."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMax, bb.YMax, bb.ZMin)

    @property
    def BNW(self) -> Vector:
        """Bottom North West corner."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMin, bb.YMax, bb.ZMin)

    @property
    def BSE(self) -> Vector:
        """Bottom South East corner."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMax, bb.YMin, bb.ZMin)

    @property
    def BSW(self) -> Vector:
        """Bottom South West corner."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMin, bb.YMin, bb.ZMin)

    @property
    def TNE(self) -> Vector:
        """Top North East corner."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMax, bb.YMax, bb.ZMax)

    @property
    def TNW(self) -> Vector:
        """Top North West corner."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMin, bb.YMax, bb.ZMax)

    @property
    def TSE(self) -> Vector:
        """Top South East corner."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMax, bb.YMin, bb.ZMax)

    @property
    def TSW(self) -> Vector:
        """Top South West corner."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMin, bb.YMin, bb.ZMax)

    # 12 Edges BE, BW, BN, BS, NE, NW, SE, SW, TE, TW, TN, TS:

    @property
    def BE(self) -> Vector:
        """Bottom East edge center."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMax, (bb.YMin + bb.YMax) / 2.0, bb.ZMin)

    @property
    def BW(self) -> Vector:
        """Bottom West edge center."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMin, (bb.YMin + bb.YMax) / 2.0, bb.ZMin)

    @property
    def BN(self) -> Vector:
        """Bottom North edge center."""
        bb: BoundBox = self._bound_box
        return Vector((bb.XMin + bb.XMax) / 2.0, bb.YMax, bb.ZMin)

    @property
    def BS(self) -> Vector:
        """Bottom South edge center."""
        bb: BoundBox = self._bound_box
        return Vector((bb.XMin + bb.XMax) / 2.0, bb.YMin, bb.ZMin)

    @property
    def NE(self) -> Vector:
        """North East edge center."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMax, bb.YMax, (bb.ZMin + bb.ZMax) / 2.0)

    @property
    def NW(self) -> Vector:
        """North West edge center."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMin, bb.YMax, (bb.ZMin + bb.ZMax) / 2.0)

    @property
    def SE(self) -> Vector:
        """North East edge center."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMax, bb.YMin, (bb.ZMin + bb.ZMax) / 2.0)

    @property
    def SW(self) -> Vector:
        """South East edge center."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMin, bb.YMin, (bb.ZMin + bb.ZMax) / 2.0)

    @property
    def TE(self) -> Vector:
        """Bottom East edge center."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMax, (bb.YMin + bb.YMax) / 2.0, bb.ZMax)

    @property
    def TW(self) -> Vector:
        """Bottom West edge center."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMin, (bb.YMin + bb.YMax) / 2.0, bb.ZMax)

    @property
    def TN(self) -> Vector:
        """Bottom North edge center."""
        bb: BoundBox = self._bound_box
        return Vector((bb.XMin + bb.XMax) / 2.0, bb.YMax, bb.ZMax)

    @property
    def TS(self) -> Vector:
        """Bottom South edge center."""
        bb: BoundBox = self._bound_box
        return Vector((bb.XMin + bb.XMax) / 2.0, bb.YMin, bb.ZMax)

    # Miscellaneous attributes:

    @property
    def BB(self) -> BoundBox:
        """Access the wrapped a BoundBox."""
        return self._bound_box

    @property
    def C(self) -> Vector:
        """Center point."""
        return self._bound_box.Center

    # ApexBoundBox.__repr__():
    def __repr__(self) -> str:
        """Return a representation of an ApexBoundBox."""
        return self.__str__()

    # ApexBoundBox.__str__():
    def __str__(self) -> str:
        """Return a representation of an ApexBoundBox."""
        return f"ApexBoundBox({self.BB})"

    @staticmethod
    def unit_tests() -> None:
        """Perform ApexBoundBox unit tests."""
        # Verity directories match:
        bound_box: BoundBox = BoundBox(-1, -2, -3, 1, 2, 3)
        apex_bound_box: ApexBoundBox = ApexBoundBox(bound_box)
        assert isinstance(apex_bound_box, ApexBoundBox)

        # Verity __str__() and __repr():
        want: str = f"ApexBoundBox({bound_box})"
        assert f"{apex_bound_box}" == want, f"'{apex_bound_box}' != '{want}'"

        def check(vector: Vector, x: float, y: float, z: float) -> bool:
            assert vector.x == x, f"{vector.x} != {x}"
            assert vector.y == y, f"{vector.y} != {y}"
            assert vector.z == z, f"{vector.z} != {z}"
            return vector.x == x and vector.y == y and vector.z == z

        # Do 6 faces:
        assert check(apex_bound_box.E, 1, 0, 0), "E"
        assert check(apex_bound_box.W, -1, 0, 0), "W"
        assert check(apex_bound_box.N, 0, 2, 0), "N"
        assert check(apex_bound_box.S, 0, -2, 0), "S"
        assert check(apex_bound_box.T, 0, 0, 3), "T"
        assert check(apex_bound_box.B, 0, 0, -3), "B"

        # Do the 12 edges:
        assert check(apex_bound_box.BE, 1, 0, -3), "BE"
        assert check(apex_bound_box.BN, 0, 2, -3), "BN"
        assert check(apex_bound_box.BS, 0, -2, -3), "BS"
        assert check(apex_bound_box.BW, -1, 0, -3), "BW"
        assert check(apex_bound_box.NE, 1, 2, 0), "NE"
        assert check(apex_bound_box.NW, -1, 2, 0), "NW"
        assert check(apex_bound_box.SE, 1, -2, 0), "SE"
        assert check(apex_bound_box.SW, -1, -2, 0), "SW"
        assert check(apex_bound_box.TE, 1, 0, 3), "TE"
        assert check(apex_bound_box.TN, 0, 2, 3), "TN"
        assert check(apex_bound_box.TS, 0, -2, 3), "TS"
        assert check(apex_bound_box.TW, -1, 0, 3), "TW"

        # Do the 8 corners:
        assert check(apex_bound_box.BNE, 1, 2, -3), "BNE"
        assert check(apex_bound_box.BNW, -1, 2, -3), "BNW"
        assert check(apex_bound_box.BSE, 1, -2, -3), "BSE"
        assert check(apex_bound_box.BSW, -1, -2, -3), "BSW"
        assert check(apex_bound_box.TNE, 1, 2, 3), "TNE"
        assert check(apex_bound_box.TNW, -1, 2, 3), "TNW"
        assert check(apex_bound_box.TSE, 1, -2, 3), "TSE"
        assert check(apex_bound_box.TSW, -1, -2, 3), "TSW"

        # Do the miscellaneous attributes:
        assert check(apex_bound_box.C, 0, 0, 0), "C"
        assert check(apex_bound_box.BB.Center, 0, 0, 0), "Center"
        assert apex_bound_box.BB is bound_box, "BB error"
        assert apex_bound_box.C == apex_bound_box.BB.Center, "C != Center"

        # Test *from_vector* and *from_bound_boxes* methods:
        vector: Vector = Vector(-1, -2, -3)
        apex_vector: ApexPoint = ApexPoint(1, 2, 3)
        new_apex_bound_box: ApexBoundBox = ApexBoundBox.from_vectors((vector, apex_vector))
        assert f"{new_apex_bound_box.BB}" == f"{apex_bound_box.BB}"
        next_apex_bound_box: ApexBoundBox = ApexBoundBox.from_bound_boxes(
            (bound_box, new_apex_bound_box))
        want = "ApexBoundBox(BoundBox (-1, -2, -3, 1, 2, 3))"
        assert f"{next_apex_bound_box}" == want, f"'{next_apex_bound_box}' != '{want}'"
        assert next_apex_bound_box.__repr__() == want
        try:
            ApexBoundBox.from_vectors(())
        except ValueError as value_error:
            assert str(value_error) == "No vectors"
        try:
            ApexBoundBox.from_bound_boxes(())
        except ValueError as value_error:
            assert str(value_error) == "No bounding boxes"


# ApexPoint:
class ApexPoint:
    """An ApexPoint is basically just a Vector with an optional diameter and/or name.

    * Attributes:
      * *vector* (Vector): The underlying FreeCAD Vector.
      * *x* (float): The x coordinate of the vector.
      * *y* (float): The y coordinate of the vector.
      * *z* (float): The z coordinate of the vector.
      * *diameter* (Union[float, ApexLength]): The apex diameter.
      * *radius* (float): The apex radius.
      * *name* (str): The apex name.
    """

    # ApexPoint.__init__():
    def __init__(self,
                 x: Union[int, float, ApexLength] = 0.0,
                 y: Union[int, float, ApexLength] = 0.0,
                 z: Union[int, float, ApexLength] = 0.0,
                 diameter: Union[int, float, ApexLength] = 0.0,
                 name: str = "") -> None:
        """Initialize an ApexPoint.

        * Arguments:
          * *x* (Union[int, float, ApexLength]): The x coordinate of the vector. (Default: 0.0)
          * *y* (Union[int, float, ApexLength]): The y coordinate of the vector. (Default: 0.0)
          * *z* (Union[int, float, ApexLength]): The z coordinate of the vector. (Default: 0.0)
          * *diameter* (Union[int, float, ApexLength]): The apex diameter. (Default: 0.0)
          * *name* (str): A name primarily used for debugging. (Default: "")
        """
        self.vector: Vector = Vector(x, y, z)
        self.x: Union[float, ApexLength] = float(x) if isinstance(x, int) else x
        self.y: Union[float, ApexLength] = float(y) if isinstance(y, int) else y
        self.z: Union[float, ApexLength] = float(z) if isinstance(z, int) else z
        self.diameter: Union[float, ApexLength] = (
            float(diameter) if isinstance(diameter, int) else diameter)
        self.radius: float = float(diameter) / 2.0
        self.name: str = name

    # ApexPoint.__add__():
    def __add__(self, vector: "ApexPoint") -> "ApexPoint":
        """Return the sum of two ApexPoint's."""
        return ApexPoint(self.x + vector.x, self.y + vector.y, self.z + vector.z)

    # ApexPoint.__neg__():
    def __neg__(self) -> "ApexPoint":
        """Return the negative of an ApexPoint."""
        return ApexPoint(-self.x, -self.y, -self.z, self.radius, self.name)

    # ApexPoint.__rmul__():
    def __mul__(self, scale: float) -> "ApexPoint":
        """Return a Point that has been scaled."""
        return ApexPoint(self.x * scale, self.y * scale, self.z * scale)

    # ApexPoint.__repr__():
    def __repr__(self) -> str:
        """Return representation of ApexPoint."""
        return self.__str__()

    # ApexPoint.__str__():
    def __str__(self) -> str:
        """Return string representation of ApexPoint."""
        diameter: str = f", {self.diameter}" if self.diameter else ""
        name: str = f", '{self.name}'" if self.name else ""
        result: str = f"ApexPoint({self.x}, {self.y}, {self.z}{diameter}{name})"
        return result

    # ApexPoint.__truediv__():
    def __truediv__(self, divisor: float) -> "ApexPoint":
        """Return a Point that has been scaleddown."""
        return ApexPoint(self.x / divisor, self.y / divisor, self.z / divisor)

    # ApexPoint.__sub__():
    def __sub__(self, vector: "ApexPoint") -> "ApexPoint":
        """Return the difference of two Point's."""
        return ApexPoint(self.x - vector.x, self.y - vector.y, self.z - vector.z)

    # ApexPoint.atan2():
    def atan2(self) -> float:
        """Return the atan2 of the x and y values."""
        return math.atan2(self.x, self.y)

    # ApexPoint.forward():
    def forward(self, matrix: "ApexPlace") -> "ApexPoint":
        """Perform a forward matrix transform using an ApexPlace."""
        vector: Vector = matrix.forward * self.vector
        return ApexPoint(vector.x, vector.y, vector.z, self.diameter, self.name)

    # ApexPoint.magnitude():
    def magnitude(self) -> float:
        """Return the magnitude of the point vector."""
        x: float = float(self.x)
        y: float = float(self.y)
        z: float = float(self.z)
        return math.sqrt(x * x + y * y + z * z)

    @staticmethod
    def unit_tests() -> None:
        """Perform ApexPoint unit tests."""
        vector: Vector = Vector(1, 2, 3)
        apex_vector: ApexPoint = ApexPoint(1, 2, 3, diameter=5, name="test1")
        assert isinstance(vector, Vector)
        assert isinstance(apex_vector, ApexPoint)
        assert apex_vector.vector == vector
        want: str = "ApexPoint(1.0, 2.0, 3.0, 5.0, 'test1')"
        assert f"{apex_vector}" == want, f"{apex_vector} != {want}"
        assert apex_vector.__repr__() == want


# ApexPlace:
class ApexPlace:
    """ApexPlace is a wrapper around the FreeCAD Matrix class.

    This is a wrapper class around the FreeCAD Matrix class that provides an openGL style
    transformation consisting of a rotation point, rotation axis, and rotation angle,
    followed by a final translation.  It also computes the inverse matrix.

    * Attributes:
      * *forward* (Matrix): A FreeCAD Matrix that maps a Vector to a new location.
      * *reverse* (Matrix): The inverse FreeCAD matrix that for new not location back.
    """

    # The matrix format is an affine 4x4 matrix in the following format:
    #
    #    [ r00 r01 r02 dx ]
    #    [ r10 r11 r12 dy ]
    #    [ r20 r21 r22 dz ]
    #    [ 0   0   0   1  ]
    #
    # An affine point format is a 1x4 matrix of the following format:
    #
    #    [ x y z 1 ]
    #
    # The 4x4 matrix (on left) is multiplied with a vertex (1x4) on the right to yield
    # the translated point.

    # ApexPlace.__init__():
    def __init__(self,
                 center: Optional[Union[ApexPoint, Vector]] = None,
                 axis: Optional[Union[ApexPoint, Vector]] = None,  # Z axis
                 angle: Optional[float] = None,
                 translate: Optional[Union[ApexPoint, Vector]] = None,
                 name: Optional[str] = None,
                 tracing: str = "") -> None:
        """Create ApexPlace rotation with point/axis/angle and a translate."""
        if tracing:
            print(f"{tracing}=>ApexPlace.__new___("
                  f"{center}, {axis}, {angle}, {translate}, '{name}')")
        # Arguments are only used for __str__():
        arguments: Tuple[Union[None, ApexPoint, Vector], ...] = (
            center, axis, angle, translate, name)
        center = Vector() if center is None else (
            center if isinstance(center, Vector) else center.vector)
        axis = Vector(0, 0, 1) if axis is None else (  # Z axis is default
            axis if isinstance(axis, Vector) else axis.vector)
        angle = 0.0 if angle is None else angle
        translate = Vector() if translate is None else (
            translate if isinstance(translate, Vector) else translate.vector)
        name = "" if name is None else name
        # Remind mypy that there are no None's in *arguments* anymore.
        assert isinstance(center, Vector)
        assert isinstance(axis, Vector)
        assert isinstance(angle, float)
        assert isinstance(translate, Vector)
        assert isinstance(name, str)

        # Compute FreeCAD Matrix's:
        center_forward: Matrix = Matrix()
        center_forward.move(center)
        center_reverse: Matrix = Matrix()
        center_reverse.move(-center)
        rotate_forward: Matrix
        rotate_reverse: Matrix
        try:
            rotate_forward = ApexPlace._rotate(axis, angle)
            rotate_reverse = ApexPlace._rotate(axis, -angle)
        except ValueError as value_error:
            if tracing:
                print(f"{tracing}<=Raising {value_error}")
            raise ValueError(value_error)
        translate_forward: Matrix = Matrix()
        translate_forward.move(translate)
        translate_reverse: Matrix = Matrix()
        translate_reverse.move(-translate)
        forward: Matrix = center_forward * rotate_forward * center_reverse * translate_forward
        reverse: Matrix = translate_reverse * center_forward * rotate_reverse * center_reverse

        self._arguments: Tuple[Union[None, ApexPoint, Vector], ...] = arguments
        self._forward: Matrix = forward
        self._reverse: Matrix = reverse
        if tracing:
            print(f"{tracing}<=ApexPlace.__new___("
                  f"{center}, {axis}, {angle}, {translate}, '{name}')")

    @staticmethod
    def zf(value: float) -> float:
        """Round values near zero to zero."""
        return 0.0 if abs(value) < 1.0e-10 else value

    @staticmethod
    def _rotate(axis: Union[ApexPoint, Vector], angle: float) -> Matrix:
        """Return a FreeCAD Matrix for rotation around an axis.

        * Arguments:
        * *axis* (Union[ApexPoint, Vector]): The axis to rotate around.
          * *angle* (float): The number of radians to rotate by.
        * Returns:
          * Returns the FreeCAD rotation Matrix.
        """
        # Normalize *angle* to be between -180.0 and 180.0 and convert to radians:
        pi: float = math.pi
        pi2: float = 2.0 * pi
        angle = angle % pi2
        angle = angle if angle <= pi else angle - pi2
        assert -pi <= angle <= pi, f"{angle=}"

        zf: Callable[[float], float] = ApexPlace.zf
        # Compute the X/Y/Z components of a normal vector of *length* 1.
        axis = axis.vector if isinstance(axis, ApexPoint) else axis
        assert isinstance(axis, Vector)
        nx: float = zf(axis.x)
        ny: float = zf(axis.y)
        nz: float = zf(axis.z)
        length: float = math.sqrt(nx * nx + ny * ny + nz * nz)
        if length <= 0.0:
            raise ValueError("Axis has a length of 0.0")
        nx = zf(nx / length)
        ny = zf(ny / length)
        nz = zf(nz / length)

        # The matrix for rotating by *angle* around the normal *axis* is:
        #
        #     [ xx(1-c)+c   xy(1-c)+zs  xz(1-c)-ys   0  ]
        #     [ yx(1-c)-zs  yy(1-c)+c   yz(1-c)+xs   0  ]
        #     [ zx(1-c)+ys  zy(1-c)-xs  zz(1-c)+c    0  ]
        #     [ 0           0           0            1  ]

        # Compute some sub expressions:
        # Why is -*angle* used?
        c = math.cos(angle)
        s = math.sin(angle)
        omc = 1.0 - c  # *omc* stands for One Minus *c*.
        x_omc = nx * omc
        y_omc = ny * omc
        z_omc = nz * omc
        xs = nx * s
        ys = ny * s
        zs = nz * s

        # Create the *matrix* and return it:
        # matrix: Matrix = Matrix(
        #     zf(nx * x_omc + c), zf(nx * y_omc - zs), zf(nx * z_omc + ys), 0.0,
        #     zf(ny * x_omc + zs), zf(ny * y_omc + c), zf(ny * z_omc - xs), 0.0,
        #     zf(nz * x_omc - ys), zf(nz * y_omc + xs), zf(nz * z_omc + c), 0.0,
        #     0.0, 0.0, 0.0, 1.0)

        # X & Z only:
        # matrix: Matrix = Matrix(
        #     zf(nx * x_omc + c), zf(ny * x_omc + zs), zf(nz * x_omc - ys), 0.0,
        #     zf(nx * y_omc - zs), zf(ny * y_omc + c), zf(nz * y_omc + xs), 0.0,
        #     zf(nx * z_omc + ys), zf(ny * z_omc - xs), zf(nz * z_omc + c), 0.0,
        #     0.0, 0.0, 0.0, 1.0)

        matrix: Matrix = Matrix(
            zf(nx * x_omc + c), zf(nx * y_omc - zs), zf(nx * z_omc + ys), 0.0,
            zf(ny * x_omc + zs), zf(ny * y_omc + c), zf(ny * z_omc - xs), 0.0,
            zf(nz * x_omc - ys), zf(nz * y_omc + xs), zf(nz * z_omc + c), 0.0,
            0.0, 0.0, 0.0, 1.0)
        return matrix

    @staticmethod
    def matrix_clean(matrix: Matrix) -> Matrix:
        """Return a matrix where values close to zero are set to zero."""
        assert isinstance(matrix, Matrix)
        elements: Tuple[float, ...] = matrix.A
        element: float
        cleaned_elements: List[float] = []
        for element in elements:
            cleaned_elements.append(ApexPlace.zf(element))
        return Matrix(*cleaned_elements)

    def __repr__(self) -> str:
        """Return string representation of an ApexPlace."""
        return self.__str__()

    def __str__(self) -> str:
        """Return string representation of an ApexPlace."""
        # Assemble *results* which is the list of positonal and keyword arguments:
        keywords: Tuple[str, ...] = ("center=", "axis=", "angle=", "translate=", "name=")
        keywords_needed: bool = False
        results: List[str] = []
        index: int
        argument: Union[None, ApexPoint, Vector]
        for index, argument in enumerate(self._arguments):
            # print(f"'{keyword}', {value}, {default}")
            result: str = f"'{argument}'" if isinstance(argument, str) else f"{argument}"
            if argument:
                results.append(keywords[index] + result if keywords_needed else result)
            else:
                keywords_needed = True
        return f"ApexPlace({', '.join(results)})"

    @property
    def forward(self) -> Matrix:
        """Return the FreeCAD Matrix."""
        return self._forward

    @property
    def reverse(self) -> Matrix:
        """Return the FreeCAD Matrix."""
        return self._reverse

    @staticmethod
    def unit_tests() -> None:
        """Run unit tests."""
        identity: ApexPlace = ApexPlace()

        # Create some ApexPlace's and verity that __str__() yields the same output:
        assert isinstance(identity, ApexPlace), f"{identity}"
        want: str = "ApexPlace()"
        assert f"{identity}" == want, f"{identity=})"
        assert f"{identity}" == identity.__repr__(), f"{identity=}"

        # Test the __str__() method:
        x_translate: ApexPlace = ApexPlace(translate=Vector(1, 0, 0), name="x_translate")
        want = "ApexPlace(translate=Vector (1.0, 0.0, 0.0), name='x_translate')"
        assert f"{x_translate}" == want, f"{x_translate=}"

        y_translate: ApexPlace = ApexPlace(translate=Vector(0, 2, 0), name="y_translate")
        want = "ApexPlace(translate=Vector (0.0, 2.0, 0.0), name='y_translate')"
        assert f"{y_translate}" == want, f"{y_translate=}"

        z_translate: ApexPlace = ApexPlace(translate=Vector(0, 0, 3), name="z_translate")
        want = "ApexPlace(translate=Vector (0.0, 0.0, 3.0), name='z_translate')"
        assert f"{z_translate}" == want, f"{z_translate=}"

        x90: ApexPlace = ApexPlace(axis=Vector(1, 0, 0), angle=90.0, name="x90")
        want = "ApexPlace(axis=Vector (1.0, 0.0, 0.0), angle=90.0, name='x90')"
        assert f"{x90}" == want, f"{x90=}"

        want = "ApexPlace(axis=Vector (0.0, 1.0, 0.0), angle=90.0, name='y90')"
        y90: ApexPlace = ApexPlace(axis=Vector(0, 1, 0), angle=90.0, name="y90")
        assert f"{y90}" == want, f"{y90=}"

        want = "ApexPlace(axis=Vector (0.0, 1.0, 0.0), angle=90.0, name='z90a')"
        z90a: ApexPlace = ApexPlace(axis=Vector(0, 1, 0), angle=90.0, name="z90a")
        assert f"{z90a}" == want, f"{z90a=}"

        z90b: ApexPlace = ApexPlace(angle=90.0, name="z90b")
        want = "ApexPlace(angle=90.0, name='z90b')"
        assert f"{z90b}" == want, f"{z90b=}"

        cx90: ApexPlace = ApexPlace(Vector(1, 1, 1), Vector(1, 0, 0), 90.0, name="cx90")
        want = "ApexPlace(Vector (1.0, 1.0, 1.0), Vector (1.0, 0.0, 0.0), 90.0, name='cx90')"
        assert f"{cx90}" == want, f"{cx90=}"

        # Test translate only:
        v123: ApexPoint = ApexPoint(1.0, 2.0, 3.0, name="v123")
        assert v123.vector == Vector(1, 2, 3)
        m_t123: Matrix = Matrix()
        m_t123.move(v123.vector)
        ap_t123: ApexPlace = ApexPlace(translate=v123)
        assert ap_t123.forward.A == m_t123.A
        assert (ap_t123.forward * ap_t123.reverse).A == identity.forward.A

        degrees90: float = math.pi / 2.0
        matrix_clean: Callable[[Matrix], Matrix] = ApexPlace.matrix_clean
        v100: Vector = Vector(1, 0, 0)  # X axis
        v010: Vector = Vector(0, 1, 0)  # Y axis
        v001: Vector = Vector(0, 0, 1)  # Z axis

        # Rotate around the X axis:
        m_x90: Matrix = Matrix()
        m_x90.rotateX(degrees90)
        m_x90 = matrix_clean(m_x90)
        ap_x90: ApexPlace = ApexPlace(axis=ApexPoint(1, 0, 0), angle=degrees90)
        assert m_x90.A == ap_x90.forward.A, f"{m_x90.A} != {ap_x90.forward.A}"
        m_v: Vector = m_x90 * v010
        ap_v: Vector = ap_x90.forward * v010
        assert m_v == ap_v == v001

        # Rotate around the Y axis:
        m_y90: Matrix = Matrix()
        m_y90.rotateY(degrees90)
        m_y90 = matrix_clean(m_y90)
        ap_y90: ApexPlace = ApexPlace(axis=ApexPoint(0, 1, 0), angle=degrees90)
        assert m_y90.A == ap_y90.forward.A, f"{m_y90.A} != {ap_y90.forward.A}"
        m_v = m_y90 * v001
        ap_v = ap_y90.forward * v001
        assert ap_v == m_v == v100

        # Rotate around the Z axis:
        m_z90: Matrix = Matrix()
        m_z90.rotateZ(degrees90)
        m_z90 = matrix_clean(m_z90)
        ap_z90: ApexPlace = ApexPlace(angle=degrees90)
        assert m_z90.A == ap_z90.forward.A, f"{m_z90.A} != {ap_z90.forward.A}"
        m_v = m_z90 * v100
        ap_v = ap_z90.forward * v100
        assert m_v == ap_v == v010

        # Do some error tests:
        try:
            ApexPlace(axis=Vector(0, 0, 0), angle=degrees90)
            assert False, "Should have failed"  # pragma: no unit cover
        except ValueError as error:
            assert str(error) == "Axis has a length of 0.0"


# ApexMaterial:
class ApexMaterial(object):
    """ApexMaterial: Represents a stock material.

    Other properties to be added later (e.g. transparency, shine, machining properties, etc.)

    Attributes:
    * *name* (Tuple[str, ...]): A list of material names from generict to specific.
    * *color* (str): The color name to use.

    """

    # ApexMaterial.__init__():
    def __init__(self, name: Tuple[str, ...], color: str) -> None:
        """Initialize and ApexMaterial.

        * Arguments:
          * *name* (Tuple[str, ...): Non-empty to tuple of material names from broad to narrow.
          * *color* (str):
             An [SVG color name](https://www.december.com/html/spec/colorsvgsvg.html).

        * Raises:
          * ValueError for either an empty name or a bad svg color.
        """
        if not name:
            raise ValueError(f"Material name is an empty tuple.")
        # Check for SVG color here.
        self.name: Tuple[str, ...] = name
        self.color: str = color


# unit_tests():
def unit_tests() -> None:
    """Run the unit tests."""
    ApexBoundBox.unit_tests()
    ApexPlace.unit_tests()
    ApexLength.unit_tests()
    ApexPoint.unit_tests()


if __name__ == "__main__":
    unit_tests()
