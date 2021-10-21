#!/usr/bin/env python3
"""Apex base classes.

The Apex base classes are:
* ApexBoundBox:
  This is a wrapper class around the FreeCAD BoundBox class for specifying bounding boxes.
  It introduces some consistent attributes for accessing the faces, corners and edges
  of a bounding box.  Alas, for technical reasons, this not a true sub-class of BoundBox.
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
* ApexPose:
  This is a wrapper class around the FreeCAD Matrix class that provides an openGL style
  transformation consisting of a rotation point, rotation axis, and rotation angle,
  followed by a final translation.  It also keeps track of the inverse matrix.

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

import os
import sys

assert sys.version_info.major == 3, "Python 3.x is not running"
assert sys.version_info.minor == 8, "Python 3.8 is not running"
sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])

from FreeCAD import BoundBox, Matrix, Placement, Rotation, Vector  # type: ignore

from dataclasses import dataclass
import math
from typing import Any, Callable, cast, ClassVar, List, Dict, Optional, Sequence, Tuple, Union


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
        * BB (BoundBox): The wrapped BoundBox object.
        * C (Vector): Center point (same as Center).
        * DB (Vector): Bottom direction (i.e. B - C)
        * DE (Vector): East direction (i.e. E - C)
        * DN (Vector): North direction (i.e. N - C)
        * DS (Vector): South direction (i.e. S - C)
        * DT (Vector): Top direction (i.e. T - C)
        * DW (Vector): West direction (i.e. W - C)
        * DX (float): X bounding box length
        * DY (float): Y bounding box length
        * DZ (float): Z bounding box length
    """

    # ApexBoundBox.__init__():
    def __init__(self,
                 corners: Sequence[Union[Vector, "ApexPoint", BoundBox, "ApexBoundBox"]]) -> None:
        """Initialize an ApexBoundBox.

        Arguments:
          * *corners* (Sequence[Union[Vector, ApexPoint, BoundBox, ApexBoundBox]]):
            A sequence of points/corners to enclose by the bounding box.

        Raises:
          * ValueError: For bad or empty corners.

        """
        if not isinstance(corners, (list, tuple)):
            raise ValueError(f"{corners} is neither a List nor a Tuple")

        # Convert *corners* into *vectors*:
        corner: Union[Vector, ApexPoint, BoundBox, ApexBoundBox]
        vectors: List[Vector] = []
        index: int
        for index, corner in enumerate(corners):
            if isinstance(corner, Vector):
                vectors.append(corner)
            elif isinstance(corner, ApexPoint):
                vectors.append(corner.vector)
            elif isinstance(corner, BoundBox):
                vectors.append(Vector(corner.XMin, corner.YMin, corner.ZMin))
                vectors.append(Vector(corner.XMax, corner.YMax, corner.ZMax))
            elif isinstance(corner, ApexBoundBox):
                vectors.append(corner.TNE)
                vectors.append(corner.BSW)
            else:
                raise ValueError(
                    f"{corner} is not of type Vector/ApexPoint/BoundBox/ApexBoundBox")
        if not vectors:
            raise ValueError("Corners sequence is empty")

        # Initialize with from the first vector:
        vector0: Vector = vectors[0]
        x_min: float = vector0.x
        y_min: float = vector0.y
        z_min: float = vector0.z
        x_max: float = x_min
        y_max: float = y_min
        z_max: float = z_min

        # Sweep through *vectors* expanding the bounding box limits:
        vector: Vector
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

        self._bound_box: BoundBox = BoundBox(x_min, y_min, z_min, x_max, y_max, z_max)

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

    @property
    def DB(self) -> float:
        """Direction Bottom."""
        return self.B - self.C

    @property
    def DE(self) -> float:
        """Direction East."""
        return self.E - self.C

    @property
    def DN(self) -> float:
        """Direction North."""
        return self.N - self.C

    @property
    def DS(self) -> float:
        """Direction South."""
        return self.S - self.C

    @property
    def DT(self) -> float:
        """Direction Top."""
        return self.T - self.C

    @property
    def DW(self) -> float:
        """Direction West."""
        return self.W - self.C

    @property
    def DX(self) -> float:
        """Delta X."""
        bb: BoundBox = self._bound_box
        return bb.XMax - bb.XMin

    @property
    def DY(self) -> float:
        """Delta Y."""
        bb: BoundBox = self._bound_box
        return bb.YMax - bb.YMin

    @property
    def DZ(self) -> float:
        """Delta Z."""
        bb: BoundBox = self._bound_box
        return bb.ZMax - bb.ZMin

    # ApexBoundBox.__repr__():
    def __repr__(self) -> str:
        """Return a representation of an ApexBoundBox."""
        return self.__str__()

    # ApexBoundBox.__str__():
    def __str__(self) -> str:
        """Return a representation of an ApexBoundBox."""
        return f"ApexBoundBox({self.BB})"

    @staticmethod
    def _unit_tests() -> None:
        """Perform ApexBoundBox unit tests."""
        # Initial tests:
        bound_box: BoundBox = BoundBox(-1.0, -2.0, -3.0, 1.0, 2.0, 3.0)
        assert bound_box == bound_box
        apex_bound_box: ApexBoundBox = ApexBoundBox([bound_box])
        assert isinstance(apex_bound_box, ApexBoundBox)

        # FreeCAD.BoundBox.__eq__() appears to only compare ids for equality.
        # Thus, it is necessary to test that each value is equal by hand.
        assert apex_bound_box.BB.XMin == bound_box.XMin
        assert apex_bound_box.BB.YMin == bound_box.YMin
        assert apex_bound_box.BB.ZMin == bound_box.ZMin
        assert apex_bound_box.BB.XMax == bound_box.XMax
        assert apex_bound_box.BB.YMax == bound_box.YMax
        assert apex_bound_box.BB.ZMax == bound_box.ZMax

        # Verify __str__() works:
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
        assert isinstance(apex_bound_box.BB, BoundBox), "BB error"
        assert apex_bound_box.C == apex_bound_box.BB.Center, "C != Center"
        assert apex_bound_box.DX == 2.0, "DX"
        assert apex_bound_box.DY == 4.0, "DY"
        assert apex_bound_box.DZ == 6.0, "DZ"
        assert check(apex_bound_box.DB, 0, 0, -3), "DB"
        assert check(apex_bound_box.DE, 1, 0, 0), "DE"
        assert check(apex_bound_box.DN, 0, 2, 0), "DN"
        assert check(apex_bound_box.DS, 0, -2, 0), "DS"
        assert check(apex_bound_box.DT, 0, 0, 3), "DT"
        assert check(apex_bound_box.DW, -1, 0, 0), "DW"

        # Test *from_vector* and *from_bound_boxes* methods:
        vector: Vector = Vector(-1, -2, -3)
        apex_vector: ApexPoint = ApexPoint(1, 2, 3)
        new_apex_bound_box: ApexBoundBox = ApexBoundBox((vector, apex_vector))
        assert f"{new_apex_bound_box.BB}" == f"{apex_bound_box.BB}"
        next_apex_bound_box: ApexBoundBox = ApexBoundBox((bound_box, new_apex_bound_box))
        want = "ApexBoundBox(BoundBox (-1, -2, -3, 1, 2, 3))"
        assert f"{next_apex_bound_box}" == want, f"'{next_apex_bound_box}' != '{want}'"
        assert next_apex_bound_box.__repr__() == want

        # Do some error checking:
        try:
            ApexBoundBox(())
        except ValueError as value_error:
            assert str(value_error) == "Corners sequence is empty", str(value_error)
        try:
            ApexBoundBox(cast(List, 123))  # Force invalid argument type.
        except ValueError as value_error:
            assert str(value_error) == "123 is neither a List nor a Tuple", str(value_error)
        try:
            ApexBoundBox(cast(List, [123]))  # Force invalid corner type
        except ValueError as value_error:
            assert str(value_error) == "123 is not of type Vector/ApexPoint/BoundBox/ApexBoundBox"


# ApexCheck:
@dataclass(frozen=True)
class ApexCheck(object):
    """ApexCheck: Check arguments for type mismatch errors.

    Attributes:
    * *name* (str):
       The argument name (used for error messages.)
    * *type* (Tuple[Any]):
      A tuple of acceptable types.

    An ApexCheck contains is used to type check a single function argument.
    The static method `Apexcheck.check()` takes a list of argument values and the
    corresponding tuple ApexCheck's and verifies that they are correct.

    Example:

         MY_FUNCTION_CHECKS = (
             ApexCheck("arg1", int),
             ApexCheck("arg2", bool),
             ApexCheck("arg3", object),  # Any <=> object
             ApexCheck("arg4," list),   # List <=> list
         )
         def my_function(arg1: int, arg2: bool, arg3: Any, arg4: List[str]) -> None:
             '''Doc string here.'''
            value_error: str = ApexCheck.check((arg1, arg2, arg3, arg4), MY_FUNCTION_CHECKS)
            if value_error:
                raise ValueError(value_error)
            # Rest of code goes here.

    """

    name: str  # Argument name
    types: Tuple[Any, ...]  # Types to match

    @staticmethod
    def _type_name(t: Any) -> str:
        """Return the best guess for the type name."""
        name: str = f"{t}"
        if hasattr(t, "__name__"):
            name = t.__name__
        elif hasattr(t, "__class__"):
            name = t.__class__.__name__
        return name

    def _message(self, argument_name: str, value: Any) -> str:
        """Return error message."""
        type_names: Sequence[str] = [ApexCheck._type_name(t) for t in self.types]
        return (f"Argument '{argument_name}' is {ApexCheck._type_name(type(value))} "
                f"which is not one of {type_names}")

    # ApexCheck.check():
    @classmethod
    def check(cls, values: Sequence[Any], apex_checks: Sequence["ApexCheck"]) -> str:
        """Return type mismatch error message."""
        assert len(values) == len(apex_checks), (
            f"{len(values)} values do not match {len(apex_checks)} checks")
        error: str = ""
        index: int
        apex_check: "ApexCheck"
        for index, apex_check in enumerate(apex_checks):
            value: Any = values[index]
            if not isinstance(value, apex_check.types):
                error = apex_check._message(apex_check.name, value)
                break
        return error

    @staticmethod
    def init_show(name: str, arguments: Sequence[Any], apex_checks: Sequence["ApexCheck"]) -> str:
        """Return string representation based in initializer arguments.

        Arguments:
        * *name* (str): Full fuction/method name.
        * *arguments* (Sequence[Any]): All argument values.
        * *apex_checks*: (Sequence[ApexCheck]): Associated ApexCheck's.

        Returns:
        * (str) containing function/method name with associated initialize arguments:

        Raises:
        * ValueError: For length mismatches and bad parameter types:

        """
        # Assemble *results* which is the list of positional and keyword arguments:
        if len(arguments) != len(apex_checks):
            raise ValueError(
                f"Arguments size ({len(arguments)}) != checks size ({len(apex_checks)})")
        if not isinstance(name, str):
            raise ValueError(f"{name} is not a string")

        # Assemble *results* from *arguments* and *apex_checks*:
        keywords_needed: bool = False
        index: int
        argument_value: Any
        results: List[str] = []
        for index, argument_value in enumerate(arguments):
            apex_check: ApexCheck = apex_checks[index]
            if not isinstance(apex_check, ApexCheck):
                raise ValueError(f"{apex_check} is not an ApexCheck")
            argument_name: str = apex_check.name
            argument_types: Tuple[Any, ...] = apex_check.types
            none_allowed: bool = type(None) in argument_types
            is_none: bool = isinstance(argument_value, type(None))

            # Append appropriate values to *results*:
            if isinstance(argument_value, str):
                argument_value = f"'{argument_value}'"
            if is_none and none_allowed:
                # None occurred and is allowed.  From now on prefix *result* with a keyword:
                keywords_needed = True
            elif keywords_needed:
                results.append(f"{argument_name}={argument_value}")
            else:
                results.append(f"{argument_value}")
        return f"{name}({', '.join(results)})"

    @classmethod
    def _unit_tests(cls):
        """Run ApexCheck unit tests."""
        # Test *ApexCheck._type_name():
        assert ApexCheck._type_name(None) == "NoneType"
        assert ApexCheck._type_name(int) == "int"
        assert ApexCheck._type_name(float) == "float"
        assert ApexCheck._type_name(str) == "str"
        assert ApexCheck._type_name({}) == "dict"
        assert ApexCheck._type_name([]) == "list"
        assert ApexCheck._type_name(()) == "tuple"
        assert ApexCheck._type_name(ApexCheck) == "ApexCheck"

        # Construct some ApexCheck's to use in tests below:
        int_check: ApexCheck = ApexCheck("int", (int,))
        float_check: ApexCheck = ApexCheck("float", (float,))
        number_check: ApexCheck = ApexCheck("number", (int, float))
        str_check: ApexCheck = ApexCheck("str", (str,))
        optional_int: ApexCheck = ApexCheck("optional_int", (type(None), int))
        optional_float: ApexCheck = ApexCheck("optional_float", (type(None), float))
        optional_number: ApexCheck = ApexCheck(
            "optional_int_float", (type(None), int, float))
        optional_str: ApexCheck = ApexCheck("optional_str", (type(None), str))

        # All of the *good_pairs* should not generate an error:
        good_pairs: Sequence[Tuple[Any, ApexCheck]] = (
            # Simple matches:
            (1, int_check),
            (1.0, float_check),
            (1, number_check),
            (1.0, number_check),
            ("", str_check),

            # Optional matches:
            (None, optional_int),
            (1, optional_int),
            (None, optional_float),
            (1.0, optional_float),
            (None, optional_number),
            (1, optional_number),
            (1.0, optional_number),
            (None, optional_str),
            ("", optional_str),
        )
        pair: Tuple[Any, ApexCheck]
        values: Sequence[Any] = tuple([pair[0] for pair in good_pairs])
        apex_checks: Sequence[ApexCheck] = tuple([pair[1] for pair in good_pairs])
        error: str = ApexCheck.check(values, apex_checks)
        assert not error, f"Unexpected error='{error}'"

        # Each of the *bad_pairs* should generate an error:
        bad_pairs: Sequence[Tuple[Any, ApexCheck]] = (
            (None, int_check),
            (1.0, int_check),
            (None, float_check),
            (1, float_check),
            (None, number_check),
        )
        value: Any
        apex_check: ApexCheck
        for value, apex_check in bad_pairs:
            assert ApexCheck.check((value,), (apex_check,)), f"{value=} {apex_check=} did not fail"

        # Test ApexCheck.init_show():
        apex_checks: Tuple[ApexCheck, ...] = (
            int_check,
            str_check,
            optional_int,
            optional_str,
            optional_float
        )
        result: str = ApexCheck.init_show("Foo", (1, "a", 1, "b", 1.0), apex_checks)
        assert result == "Foo(1, 'a', 1, 'b', 1.0)", result
        result: str = ApexCheck.init_show("Foo", (1, "a", 1, "b", None), apex_checks)
        assert result == "Foo(1, 'a', 1, 'b')", result
        result: str = ApexCheck.init_show("Foo", (1, "a", 1, None, None), apex_checks)
        assert result == "Foo(1, 'a', 1)", result
        result: str = ApexCheck.init_show("Foo", (1, "a", None, None, None), apex_checks)
        assert result == "Foo(1, 'a')", result
        result: str = ApexCheck.init_show("Foo", (1, "a", None, None, 1.0), apex_checks)
        assert result == "Foo(1, 'a', optional_float=1.0)", result
        result: str = ApexCheck.init_show("Foo", (1, "a", None, "b", 1.0), apex_checks)
        assert result == "Foo(1, 'a', optional_str='b', optional_float=1.0)", result
        result: str = ApexCheck.init_show("Foo", (1, "a", None, None, 1.0), apex_checks)
        assert result == "Foo(1, 'a', optional_float=1.0)", result
        try:
            ApexCheck.init_show("Foo", (), apex_checks)  # Arguments/ApexCheck's misamtch.
        except ValueError as value_error:
            assert str(value_error) == "Arguments size (0) != checks size (5)", str(value_error)
        try:
            ApexCheck.init_show("Foo", (0,), (cast(ApexCheck, 0),))
        except ValueError as value_error:
            assert str(value_error) == "0 is not an ApexCheck", str(value_error)
        try:
            ApexCheck.init_show(cast(str, 0), (0,), (int_check,))
        except ValueError as value_error:
            assert str(value_error) == "0 is not a string", str(value_error)


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
            raise ValueError(f"value ({value}) is neither a float nor an int")
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
            raise ValueError(f"units ('{units}') is not one of {tuple(conversions.keys())}")
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

    @staticmethod
    def _unit_tests() -> None:
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
            assert str(value_error) == "name (7) is not a str", str(value_error)

        try:
            ApexLength(None)
        except ValueError as value_error:
            assert str(value_error) == "value (None) is neither a float nor an int", (
                str(value_error))

        try:
            ApexLength(units="angstrom")
        except ValueError as value_error:
            units = "'km', 'm', 'cm', 'mm', 'µm', 'um', 'nm', 'ft', 'in', 'thou'"
            assert str(value_error) == f"units ('angstrom') is not one of ({units})", (
                str(value_error))


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

    @staticmethod
    def _unit_tests() -> None:
        """Run ApexMaterial unit tests."""
        try:
            ApexMaterial((), "")
        except ValueError as error:
            assert str(error) == "Material name is an empty tuple.", str(error)


# ApexPoint:
class ApexPoint:
    """An ApexPoint is basically just a Vector with an optional diameter and/or name.

    * Attributes:
      * *vector* (Vector): The underlying FreeCAD Vector.
      * *x* (Union[float, Apex): The x coordinate of the vector.
      * *y* (float): The y coordinate of the vector.
      * *z* (float): The z coordinate of the vector.
      * *diameter* (Union[float, ApexLength]): The apex diameter.
      * *radius* (float): The apex radius.
      * *name* (str): The apex name.
    """

    INIT_CHECKS = (
        ApexCheck("x", (int, float, ApexLength)),
        ApexCheck("y", (int, float, ApexLength)),
        ApexCheck("z", (int, float, ApexLength)),
        ApexCheck("diameter", (int, float, ApexLength)),
        ApexCheck("name", (str,)),
    )

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
        value_error: str = ApexCheck.check((x, y, z, diameter, name), ApexPoint.INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)

        self.x: Union[float, ApexLength] = float(x) if isinstance(x, int) else x
        self.y: Union[float, ApexLength] = float(y) if isinstance(y, int) else y
        self.z: Union[float, ApexLength] = float(z) if isinstance(z, int) else z
        self.diameter: Union[float, ApexLength] = (
            float(diameter) if isinstance(diameter, int) else diameter)
        self.radius: float = float(diameter) / 2.0
        self.name: str = name

    @property
    def vector(self) -> Vector:
        """Return associated Vector."""
        return Vector(self.x, self.y, self.z)

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
    def forward(self, matrix: "ApexPose") -> "ApexPoint":
        """Perform a forward matrix transform using an ApexPose."""
        vector: Vector = matrix.forward * self.vector
        return ApexPoint(vector.x, vector.y, vector.z, self.diameter, self.name)

    # ApexPoint.magnitude():
    def magnitude(self) -> float:
        """Return the magnitude of the point vector."""
        x: float = float(self.x)
        y: float = float(self.y)
        z: float = float(self.z)
        return math.sqrt(x * x + y * y + z * z)

    # ApexPoint.Reorient():
    REORIENT_CHECKS = (
        ApexCheck("placement", (Placement,)),
        ApexCheck("suffix", (type(None), str)),
    )

    def reorient(self, placement: Placement, suffix: Optional[str] = "") -> "ApexPoint":
        """Return the a new ApexPoint that has been reoriented.

        Arguments:
        * *placement* (Placement):
          A FreeCAD Placement of the form Placement(translate, rotate, center) where:
          * *translate* (Vector):
           Specifies a translation that occurs **AFTER** the rotation (Default: Vector().)
          * *rotation* (Rotation):
            Specifies a rotation about the center point. (Default: Rotation().)
          * *center* (Vector):
            Specifies the rotation center point. (Default: Vector().)
        * *suffix* (Optional[str]):
          A suffix to append to the name of each original *ApexPoint* name.  If `None`
          is specified the name is set to the empty string.  (Default: "")
        """
        value_error: str = ApexCheck.check((placement, suffix), ApexPoint.REORIENT_CHECKS)
        if value_error:
            raise ValueError(value_error)
        name: str = "" if suffix is None else f"{self.name}{suffix}"
        reoriented: Vector = placement * self.vector
        return ApexPoint(reoriented.x, reoriented.y, reoriented.z, self.diameter, name)

    @staticmethod
    def _unit_tests() -> None:
        """Perform ApexPoint unit tests."""
        vector: Vector = Vector(1, 2, 3)
        apex_point: ApexPoint = ApexPoint(1, 2, 3, diameter=5, name="test1")
        assert isinstance(vector, Vector)
        assert isinstance(apex_point, ApexPoint)
        assert apex_point.vector == vector
        want: str = "ApexPoint(1.0, 2.0, 3.0, 5.0, 'test1')"
        assert f"{apex_point}" == want, f"{apex_point} != {want}"
        assert apex_point.__repr__() == want
        assert (-apex_point).vector == Vector(-1, -2, -3)
        assert (apex_point / 2).vector == Vector(0.5, 1.0, 1.5)

        try:
            ApexPoint(cast(int, "x"), cast(float, "y"), cast(ApexLength, "z"),
                      cast(float, "diameter"), cast(str, None))
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'x' is str which is not one of ['int', 'float', 'ApexLength']")

        def whole(vector: Vector) -> Vector:
            """Return Vector that is close to integers (testing only)."""
            def fix(value: float) -> float:
                """Round floats to closest whole number."""
                negative: bool = value < 0.0
                if negative:
                    value = -value
                whole: float
                fractional: float
                whole, fractional = divmod(value, 1.0)
                epsilon: float = 1.0e-10
                if abs(fractional) < epsilon:
                    fractional = 0.0
                if abs(fractional - 1.0) < epsilon:
                    fractional = 0.0  # pragma: no unit cover
                    whole += 1.0  # pragma: no unit cover
                value = whole + fractional
                if negative:
                    value = -value
                return value
            fixed_vector: Vector = Vector(fix(vector.x), fix(vector.y), fix(vector.z))
            # print(f"whole({vector}) => {fixed_vector}")
            return fixed_vector

        def reorients(vectors: Sequence[Vector], placement: Placement) -> Sequence[Vector]:
            """Reorient ApexPoints by a Placement."""
            vector: Vector
            apex_points: List[ApexPoint] = ([
                ApexPoint(vector.x, vector.y, vector.z) for vector in vectors])
            # print(f"{apex_points=}")
            apex_point: ApexPoint
            reoriented_apex_points: Sequence[ApexPoint] = tuple(
                [apex_point.reorient(placement) for apex_point in apex_points])
            # print(f"{reoriented_apex_points=}")
            reoriented_vectors: Sequence[Vector] = tuple(
                [whole(apex_point.vector) for apex_point in reoriented_apex_points])
            # print(f"{reoriented_vectors=}")
            return reoriented_vectors

        t0: Vector = Vector(0, 0, 0)  # No translation
        t10: Vector = Vector(10, 10, 10)  # Translate by +10 in X/Y/Z
        c0: Vector = t0  # Center point at origin
        c10: Vector = t10  # Center point at (10, 10, 10)

        x_axis: Vector = Vector(1, 0, 0)
        y_axis: Vector = Vector(0, 1, 0)
        z_axis: Vector = Vector(0, 0, 1)
        xyz: Sequence[Vector] = (x_axis, y_axis, z_axis)

        x2z: Rotation = Rotation(x_axis, z_axis)  # X-axis to Z-axis
        # y2z: Rotation = Rotation(y, z)  # Y-axis to Z-axis
        # z2x: Rotation = Rotation(x, z)  # Z-axis to X-axis
        # z2y: Rotation = Rotation(y, z)  # Z-axis to Y-axis
        z2z: Rotation = Rotation(z_axis, z_axis)  # Z-axis to Z-axis

        # Rotate origin from X-axis to Z-axis;
        t0_x2z_c0: Placement = Placement(t0, x2z, c0)
        t0_x2z_c0_xyz: Sequence[ApexPoint] = reorients(xyz, t0_x2z_c0)
        assert t0_x2z_c0_xyz == (Vector(0, 0, 1), Vector(0, 1, 0), Vector(-1, 0, 0))

        # Translate origin to *t10*:
        t10_z2z_c0: Placement = Placement(t10, z2z, c0)
        t10_xyz: Vector[ApexPoint] = reorients(xyz, t10_z2z_c0)
        assert t10_xyz == (Vector(11, 10, 10), Vector(10, 11, 10), Vector(10, 10, 11)), t10_xyz

        # Rotate around the center at *t10*:
        t0_x2z_c10: Placement = Placement(t0, x2z, c10)
        t0_x2z_c10_xyz: Placement = reorients(t10_xyz, t0_x2z_c10)
        assert t0_x2z_c10_xyz == (Vector(10, 10, 11), Vector(10, 11, 10), Vector(9, 10, 10))

        # Try to trigger a value error:
        try:
            apex_point.reorient(None)
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'placement' is NoneType which is not one of ['Placement']")


# ApexPose:
class ApexPose(object):
    """ApexPose is a wrapper around the FreeCAD Matrix class.

    This is a wrapper class around the FreeCAD Matrix class that provides a number of
    stadard rotations and translations.  It also computes the inverse matrix.

    Attributes:
    * *forward* (Matrix): A FreeCAD Matrix that maps a Vector to a new pose.
    * *reverse* (Matrix): The inverse FreeCAD matrix that maps the pose back to its initial value.

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

    INIT_CHECKS = (
        ApexCheck("center", (type(None), ApexPoint, Vector)),
        ApexCheck("axis", (type(None), ApexPoint, Vector)),
        ApexCheck("angle", (type(None), float, int)),
        ApexCheck("z_align", (type(None), ApexPoint, Vector)),
        ApexCheck("y_align", (type(None), ApexPoint, Vector)),
        ApexCheck("translate", (type(None), ApexPoint, Vector)),
        ApexCheck("name", (type(None), str)),
    )

    # ApexPose.__init__():
    def __init__(
            self,
            center: Optional[Union[ApexPoint, Vector]] = None,  # Default: origin
            axis: Optional[Union[ApexPoint, Vector]] = None,  # Default: +Z axis
            angle: Optional[float] = None,  # Default: 0 degrees
            z_align: Optional[Union[ApexPoint, Vector]] = None,  # Default: +Z axis
            y_align: Optional[Union[ApexPoint, Vector]] = None,  # Default: +Y axis
            translate: Optional[Union[ApexPoint, Vector]] = None,  # Default: origin
            name: Optional[str] = None,  # Default: ""
            tracing: str = ""  # Default: Disabled
    ) -> None:
        """Create ApexPose rotation with point/axis/angle and a translate.

        Arguments:
        * *center* (Optional[Union[ApexPoint, Vector]]):
          The point around which all rotations occur (default: origin)).
        * *axis* (Optional[Union[ApexPoint, Vector]]):
          A direction axis rotate around (default: Z axis)).
        * *angle (Optional[float]):
          The angle to rotate around the *axis* measured in radians (default: 0 radians).
        * *z_align* (Optional[Union[ApexPoint, Vector]]):
          An direction axis to reorient to point in the +Z direction (default: +Z axis).
        * *y_align* (Optional[Union[ApexPoint, Vector]]):
          After applying the *z_align* rotation to *y_align*, project the resulting point down
          onto the X/Y plane and rotate the point around the Z axis until is alignes with the +Y
          axis.
        * *translate* (Optional[Union[ApexPoint, Vector]]):
          The final translation to perform.
        The direction axes do *not* need to be normalized to a length of 1.0.

        There are two rotation styles:
        * Axis-Angle:
          An *axis* that points outward from *center* is specified and a rotation
          of *angle* radians in a counter clockwise direction occurs (i.e. right hand rule.)
        * Mounting:
          Frequently parts need to be mounted in a vice.  For this the part need to be rotated
          so that the surface to be machines is normal to the *Z axis.  And another surface
          is aligned to be normal to the +Y axis.  For "boxy" parts, the *ApexBoundBox* is
          used to get these directions.  Specifically, *z_align* rotates the part such that
          *z_align* is in the +Z axis direction and *y_align* rotates the part such that the
          part is aligned in the +Y axis.

        The operation order is:
        1. Translate *center* to origin.
        2. Perform *axis*/*angle* rotation.
        3. Perform *z_align* rotation.
        4. Perform *y_align* rotation.
        5. Translate from origin back to *center*.
        6. Perform final *translation*.
        """
        # Process *arguments*:
        arguments: Sequence[Any] = (center, axis, angle, z_align, y_align, translate, name)
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>ApexPose.__init__{arguments}")
        value_error: str = ApexCheck.check(arguments, ApexPose.INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)

        if not name:
            name = ""
        assert isinstance(name, str), f"{name} is not a str"

        # Compute *center_forward* and *center_reverse* Matrix's:
        if not center:
            center = Vector()
        if isinstance(center, ApexPoint):
            center = center.vector
        assert isinstance(center, Vector)
        center_forward: Matrix = Matrix()
        center_reverse: Matrix = Matrix()
        if center:
            assert isinstance(center, Vector), f"{center=} is not a Vector"
            center_forward.move(center)
            center_reverse.move(-center)

        # Compute the *rotate_forward* and *rotate_reverse* Matrix's from *axis* and *angle*:
        pi: float = math.pi
        origin: Vector = Vector()
        epsilon: float = 1.0e-10
        if isinstance(axis, ApexPoint):
            axis = axis.vector
        if axis is None:
            axis = Vector(0.0, 0.0, 1.0)  # Default is +Z axis
        assert isinstance(axis, Vector)
        if abs(axis.distanceToPoint(origin)) < epsilon:
            raise ValueError(f"Rotation axis ({axis}) has no direction")
        if not angle:
            angle = 0.0
        if not -2.0 * pi <= angle <= 2.0 * pi:
            angle = angle % (2.0 * pi)
        rotate_forward: Matrix = ApexPose._rotate(axis, angle)
        rotate_reverse: Matrix = ApexPose._rotate(axis, -angle)

        # Compute the *z_align_forward* and *z_align_reverse* Matrix's:
        spot: Vector = Vector(1, 1, 2)
        z_align_spot: Vector = spot
        z_align_forward: Matrix = Matrix()
        z_align_reverse: Matrix = Matrix()
        if z_align:
            if isinstance(z_align, ApexPoint):
                z_align = z_align.vector
            if z_align.distanceToPoint(origin) < epsilon:
                raise ValueError(f"{z_align=} has no direction")
            z_axis: Vector = Vector(0.0, 0.0, 1.0)
            z_tracing: str = f"{next_tracing}z_align:" if tracing else ""
            z_align_forward, z_align_reverse = ApexPose._rotate_from_to(
                z_align, z_axis, tracing=z_tracing)
            z_align_spot = z_align_forward * spot
            if tracing:
                print(f"{z_tracing}z_spot:{spot}=>{z_align_spot}")

        # Compute *y_align_forward* and *y_align_reverse* Matrix's:
        y_align_spot: Vector = z_align_spot
        y_align_forward: Matrix = Matrix()
        y_align_reverse: Matrix = Matrix()
        if y_align:
            if isinstance(y_align, ApexPoint):
                y_align = y_align.vector
            if y_align.distanceToPoint(origin) < epsilon:
                raise ValueError(f"{y_align=} has no direction")

            # Rotate *y_align* to *new_y_align*, project on to X/Y plane, and normalize:
            y_tracing: str = f"{next_tracing}y_align:" if tracing else ""
            new_y_align: Vector = z_align_forward * y_align
            if tracing:
                print(f"{y_tracing}new_y_align:{y_align=}=>{new_y_align}")
            final_y_align: Vector = Vector(new_y_align.x, new_y_align.y, 0.0).normalize()
            y_axis: Vector = Vector(0.0, 1.0, 0.0)
            y_align_forward, y_align_reverse = ApexPose._rotate_from_to(
                final_y_align, y_axis, tracing=y_tracing)
            y_align_spot = y_align_forward * z_align_spot
            if tracing:
                print(f"{y_tracing}y_spot:{z_align_spot}=>{y_align_spot}")

            check: bool = True
            if check:
                z_spot: Vector = z_align_forward * spot
                y_spot: Vector = y_align_forward * z_align_forward * spot
                if tracing:
                    print(f"{tracing}z_spot={z_spot} vs. z_align_spot={z_align_spot}")
                    print(f"{tracing}y_spot={y_spot} vs. y_align_spot={y_align_spot}")

        # Compute the *translate_forward* and *translate_reverse* Matrix's:
        if not translate:
            translate = Vector()
        if isinstance(translate, ApexPoint):
            translate = translate.vector
        assert isinstance(translate, Vector)
        translate_forward: Matrix = Matrix()
        translate_forward.move(translate)
        translate_reverse: Matrix = Matrix()
        translate_reverse.move(-translate)

        # Compute the final forward/reverse matrices:
        self._arguments: Sequence[Any] = arguments
        # For some reason the code works if *y_align_forward* occurs before *z_align_forward*.
        # It is counter intuitive, but it work.  Weird.
        self._forward: Matrix = (center_forward * rotate_forward * y_align_forward *
                                 z_align_forward * center_reverse * translate_forward)
        self._reverse: Matrix = (translate_reverse * center_forward * z_align_reverse *
                                 y_align_reverse * rotate_reverse * center_reverse)

        if tracing:
            print(f"{tracing}<=ApexPose.__init__{arguments}")

    @staticmethod
    def _rotate_from_to(start: Vector, finish: Vector, tracing: str = "") -> Tuple[Matrix, Matrix]:
        """Return to/from rotation Matrix's between to vectors.

        Arguments:
        * *start* (Vector): The vector orientation to start at.
        * *finish* (Vector): The vector orientation to finish at.

        Returns:
        * (Matrix) The Matrix to rotate from start to finish.
        * (Matrix) The Matrix to rotate from finish to start.

        """
        if tracing:
            print(f"{tracing}=>ApexPose._rotate_from_to({start}, {finish})")
        start = start.normalize()
        finish = finish.normalize()
        abs_angle: float = abs(start.getAngle(finish))
        epsilon: float = 1.0e-10
        pi: float = math.pi
        matrix1: Matrix
        matrix2: Matrix
        axis: Optional[Vector] = None
        # Cross products do not work if the two vectors are colinear.
        if abs_angle < epsilon:
            # *from* and *to* are colinear in the same direction.  Use *identity* matrix:
            if tracing:
                print(f"{tracing}:No Rotate")
            matrix1 = Matrix()
            matrix2 = matrix1
        elif abs(pi - abs_angle) < epsilon:
            # The goal is to compute an *axis* that orthogonal to *from*.  A cross product
            # with the X, Y, or Z axis will work just fine.
            x_cross: Vector = start.cross(Vector(1.0, 0.0, 0.0))
            y_cross: Vector = start.cross(Vector(0.0, 1.0, 0.0))
            z_cross: Vector = start.cross(Vector(0.0, 1.0, 0.0))
            origin: Vector = Vector(0.0, 0.0, 0.0)
            x_distance: float = x_cross.distanceToPoint(origin)
            y_distance: float = y_cross.distanceToPoint(origin)
            z_distance: float = z_cross.distanceToPoint(origin)
            max_distance: float = max(x_distance, y_distance, z_distance)
            if x_distance >= max_distance:
                axis = x_cross
            if y_distance >= max_distance:
                axis = y_cross
            if z_distance >= max_distance:
                axis = z_cross
            assert axis, "Internal error, no orthogonal axis found."
            axis = axis.normalize()

            # Finally, rotate by 180 degrees around axis:
            matrix1 = ApexPose._rotate(axis, pi)
            matrix2 = matrix1  # The same matrix will flip it back.
            if tracing:
                print(f"{tracing}Rotate 180 around:{axis}")
        else:
            # Use a cross product to find a rotation *axis*:
            axis = start.cross(finish).normalize()
            matrix1 = ApexPose._rotate(axis, abs_angle)
            matrix2 = ApexPose._rotate(axis, -abs_angle)
            angle: float = abs_angle
            if abs((matrix1 * start).distanceToPoint(finish)) > epsilon:  # pragma: no unit cover
                # Swap the matrices:
                matrix1, matrix2 = matrix2, matrix1
                assert abs((matrix1 * start).distanceToPoint(finish)) < epsilon
                angle = -abs_angle
            if tracing:
                print(f"{tracing}Rotate {math.degrees(angle)}deg around {axis}")

        # Optinally test results:
        check: bool = True
        if check:
            assert (matrix1 * start).distanceToPoint(finish) < epsilon
            assert (matrix2 * finish).distanceToPoint(start) < epsilon

        if tracing:
            print(f"{tracing}<=ApexPose._rotate_from_to({start}, {finish})=>{matrix1}, {matrix2}")
        return matrix1, matrix2

    @staticmethod
    def _zf(value: float) -> float:
        """Round values near zero to zero."""
        return 0.0 if abs(value) < 1.0e-10 else value

    @staticmethod
    def _rotate(axis: Union[ApexPoint, Vector], angle: float, tracing: str = "") -> Matrix:
        """Return a FreeCAD Matrix for rotation around an axis.

        * Arguments:
        * *axis* (Union[ApexPoint, Vector]): The axis to rotate around.
          * *angle* (float): The number of radians to rotate by.
        * Returns:
          * Returns the FreeCAD rotation Matrix.
        """
        # Ensure -*pi* <= *angle* <= *pi:
        pi: float = math.pi
        pi2: float = 2.0 * pi
        angle = angle % pi2
        angle = angle if angle <= pi else angle - pi2
        assert -pi <= angle <= pi, f"{angle=}"

        if tracing:
            print(f"{tracing}=>ApexPose._rotate({axis}, {math.degrees(angle)}deg)")

        # Normalize *angle* to be between -180.0 and 180.0 and convert to radians:

        _zf: Callable[[float], float] = ApexPose._zf
        # Compute the X/Y/Z components of a normal vector of *length* 1.
        axis = axis.vector if isinstance(axis, ApexPoint) else axis
        assert isinstance(axis, Vector)
        nx: float = _zf(axis.x)
        ny: float = _zf(axis.y)
        nz: float = _zf(axis.z)
        length: float = math.sqrt(nx * nx + ny * ny + nz * nz)
        assert length > 0.0, "Internal error: {length=}"
        nx = _zf(nx / length)
        ny = _zf(ny / length)
        nz = _zf(nz / length)

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
            _zf(nx * x_omc + c), _zf(nx * y_omc - zs), _zf(nx * z_omc + ys), 0.0,
            _zf(ny * x_omc + zs), _zf(ny * y_omc + c), _zf(ny * z_omc - xs), 0.0,
            _zf(nz * x_omc - ys), _zf(nz * y_omc + xs), _zf(nz * z_omc + c), 0.0,
            0.0, 0.0, 0.0, 1.0)
        if tracing:
            print(f"{tracing}<=ApexPose._rotate({axis}, {math.degrees(angle)}deg)=>{matrix}")
        return matrix

    @staticmethod
    def _matrix_clean(matrix: Matrix) -> Matrix:
        """Return a matrix where values close to zero are set to zero."""
        assert isinstance(matrix, Matrix)
        elements: Tuple[float, ...] = matrix.A
        element: float
        cleaned_elements: List[float] = []
        for element in elements:
            cleaned_elements.append(ApexPose._zf(element))
        return Matrix(*cleaned_elements)

    def __repr__(self) -> str:
        """Return string representation of an ApexPose."""
        return self.__str__()

    def __str__(self) -> str:
        """Return string representation of an ApexPose."""
        return ApexCheck.init_show("ApexPose", self._arguments, ApexPose.INIT_CHECKS)

    @property
    def forward(self) -> Matrix:
        """Return the FreeCAD Matrix."""
        return self._forward

    @property
    def reverse(self) -> Matrix:
        """Return the FreeCAD Matrix."""
        return self._reverse

    @staticmethod
    def _xy_align_unit_tests() -> None:
        """Run unit tests that use x_align and y_align in ApexPose.__init.

        Test *z_align* and *y_align*.  There are basically 24 possibilities because there
        are 6 faces (T, B, N, S, E, W) each of which can be rotated around the Z axis 4
        different ways (0, 90, 180, 270 degrees.)  The orientations were figured out by
        taking small cardboard box, labeling the six faces (T, B, N, S, E, W) and orienting
        T facing up (+Z) with N facing north (+Y).  The box is assumed to be 4 x 4 x 4 with a
        center of (0, 0, 0).  Thus, the opposite corners are (-2, -2, -2) and (2, 2, 2).
        A *spot*  is placed on the Top surface at (1, 1, 2).  For each of the 24 reorient
        possibilities the spot lands in a different and unique position.
        """
        class _Reorient(object):
            """_Reorient: A helper class for _xy_align_unit_tests."""

            def __init__(self, z_align: Vector, y_align: Vector,
                         x: int, y: int, z: int, tag: str) -> None:
                """Initialize _Reorient."""
                self.z_align: Vector = z_align  # Direction to reorient to the top (+Z)
                self.y_align: Vector = y_align  # Direction to reorient to the north (+Y)
                self.x: int = x  # X Location of rotated spot
                self.y: int = y  # Y Location of rotated spot
                self.z: int = z  # Z Location of rotated spot
                self.tag: str = tag  # String "ab", where "a" is *top* and "b" is *north*

        # Define the 24 test cases in *reorients*:
        spot: Vector = Vector(1, 1, 2)
        e: Vector = Vector(1, 0, 0)
        w: Vector = Vector(-1, 0, 0)
        n: Vector = Vector(0, 1, 0)
        s: Vector = Vector(0, -1, 0)
        t: Vector = Vector(0, 0, 1)
        b: Vector = Vector(0, 0, -1)
        reorients: Sequence[_Reorient] = (
            # Top is T:
            _Reorient(t, n, 1, 1, 2, "TN"),  # TN => No rotation at all => matches *spot*
            _Reorient(t, s, -1, -1, 2, "TS"),
            _Reorient(t, e, -1, 1, 2, "TE"),
            _Reorient(t, w, 1, -1, 2, "TW"),

            # Top is B:
            _Reorient(b, n, -1, 1, -2, "BN"),
            _Reorient(b, s, 1, -1, -2, "BS"),
            _Reorient(b, e, 1, 1, -2, "BE"),
            _Reorient(b, w, -1, -1, -2, "BW"),

            # Top is N:
            _Reorient(n, t, -1, 2, 1, "NT"),
            _Reorient(n, b, 1, -2, 1, "NB"),
            _Reorient(n, e, 2, 1, 1, "NE"),
            _Reorient(n, w, -2, -1, 1, "NW"),

            # Top is S:
            _Reorient(s, t, 1, 2, -1, "ST"),
            _Reorient(s, b, -1, -2, -1, "SB"),
            _Reorient(s, e, -2, 1, -1, "SE"),
            _Reorient(s, w, 2, -1, -1, "SW"),

            # Top is E:
            _Reorient(e, t, 1, 2, 1, "ET"),
            _Reorient(e, b, -1, -2, 1, "EB"),
            _Reorient(e, n, -2, 1, 1, "EN"),
            _Reorient(e, s, 2, -1, 1, "ES"),

            # Top is W:
            _Reorient(w, t, -1, 2, -1, "WT"),
            _Reorient(w, b, 1, -2, -1, "WB"),
            _Reorient(w, n, 2, 1, -1, "WN"),
            _Reorient(w, s, -2, -1, -1, "WS"),
        )

        # Verify that the *absolute_key* associated with each *key* has exactly two 1's, and one 2.
        # In addition, use *duplicates* to ensure that no *key* is duplicated:
        reorient: _Reorient
        duplicates: Dict[Tuple[int, int, int], str] = {}
        tag: str
        for reorient in reorients:
            tag = reorient.tag
            key: Tuple[int, int, int] = (reorient.x, reorient.y, reorient.z)
            absolute_key: Tuple[int, int, int] = (abs(key[0]), abs(key[1]), abs(key[2]))
            assert sorted(absolute_key) != (1, 1, 2), (f"{key=} is bad")
            assert key not in duplicates, f"'{duplicates[key]}' conflicts with '{tag}'"
            duplicates[key] = tag

        # Sweep through all 24 cases in *reorients* and verify that both forward and
        # reverse are correct:
        epsilon: float = 1.0e-10
        for reorient in reorients:
            tag = reorient.tag
            z_align: Vector = reorient.z_align
            y_align: Vector = reorient.y_align
            apex_pose: ApexPose = ApexPose(z_align=z_align, y_align=y_align)
            spot_want: Vector = Vector(reorient.x, reorient.y, reorient.z)
            spot_got: Vector = apex_pose.forward * spot
            assert spot_want.distanceToPoint(spot_got) < epsilon, (
                f"{tag}: {spot_want} != {spot_got}")
            spot_back: Vector = apex_pose.reverse * spot_want
            assert spot.distanceToPoint(spot_back) < epsilon, (
                f"{tag}: {spot} != {spot_back}")

    @staticmethod
    def _other_unit_tests() -> None:
        """Run some other unit tests."""
        # Create some ApexPose's and verity that __str__() yields the same output:
        identity_pose: ApexPose = ApexPose()
        errors: int = 0
        assert isinstance(identity_pose, ApexPose), f"{identity_pose} is not ApexPose"
        want: str = "ApexPose()"
        assert f"{identity_pose}" == want, f"{identity_pose=})"
        assert f"{identity_pose}" == identity_pose.__repr__(), f"{identity_pose=}"

        # Test the __str__() method:
        x_translate: ApexPose = ApexPose(translate=Vector(1, 0, 0), name="x_translate")
        want = "ApexPose(translate=Vector (1.0, 0.0, 0.0), name='x_translate')"
        assert f"{x_translate}" == want, f"{x_translate=}"

        y_translate: ApexPose = ApexPose(translate=Vector(0, 2, 0), name="y_translate")
        want = "ApexPose(translate=Vector (0.0, 2.0, 0.0), name='y_translate')"
        assert f"{y_translate}" == want, f"{y_translate=}"

        z_translate: ApexPose = ApexPose(translate=Vector(0, 0, 3), name="z_translate")
        want = "ApexPose(translate=Vector (0.0, 0.0, 3.0), name='z_translate')"
        assert f"{z_translate}" == want, f"{z_translate=}"

        x90: ApexPose = ApexPose(axis=Vector(1, 0, 0), angle=90.0, name="x90")
        want = "ApexPose(axis=Vector (1.0, 0.0, 0.0), angle=90.0, name='x90')"
        assert f"{x90}" == want, f"{x90=}"

        want = "ApexPose(axis=Vector (0.0, 1.0, 0.0), angle=90.0, name='y90')"
        y90: ApexPose = ApexPose(axis=Vector(0, 1, 0), angle=90.0, name="y90")
        assert f"{y90}" == want, f"{y90=}"

        want = "ApexPose(axis=Vector (0.0, 1.0, 0.0), angle=90.0, name='z90a')"
        z90a: ApexPose = ApexPose(axis=Vector(0, 1, 0), angle=90.0, name="z90a")
        assert f"{z90a}" == want, f"{z90a=}"

        z90b: ApexPose = ApexPose(angle=90.0, name="z90b")
        want = "ApexPose(angle=90.0, name='z90b')"
        assert f"{z90b}" == want, f"{z90b=}"

        cx90: ApexPose = ApexPose(Vector(1, 1, 1), Vector(1, 0, 0), 90.0, name="cx90")
        want = "ApexPose(Vector (1.0, 1.0, 1.0), Vector (1.0, 0.0, 0.0), 90.0, name='cx90')"
        assert f"{cx90}" == want, f"{cx90=}"

        # Test translate only:
        v123: ApexPoint = ApexPoint(1.0, 2.0, 3.0, name="v123")
        assert v123.vector == Vector(1, 2, 3)
        m_t123: Matrix = Matrix()
        m_t123.move(v123.vector)
        ap_t123: ApexPose = ApexPose(center=ApexPoint(0, 0, 0), translate=v123)
        assert ap_t123.forward.A == m_t123.A
        assert (ap_t123.forward * ap_t123.reverse).A == identity_pose.forward.A

        degrees90: float = math.pi / 2.0
        _matrix_clean: Callable[[Matrix], Matrix] = ApexPose._matrix_clean
        v100: Vector = Vector(1, 0, 0)  # X axis
        v010: Vector = Vector(0, 1, 0)  # Y axis
        v001: Vector = Vector(0, 0, 1)  # Z axis

        # Rotate around the X axis:
        m_x90: Matrix = _matrix_clean(Matrix())
        m_x90.rotateX(degrees90)
        m_x90 = _matrix_clean(m_x90)

        m_x90 = _matrix_clean(m_x90)
        ap_x90: ApexPose = ApexPose(axis=ApexPoint(1, 0, 0), angle=degrees90)
        assert m_x90.A == ap_x90.forward.A, f"{m_x90.A} != {ap_x90.forward.A}"
        m_v: Vector = m_x90 * v010
        ap_v: Vector = ap_x90.forward * v010
        assert m_v == ap_v == v001

        # Rotate around the Y axis:
        m_y90: Matrix = Matrix()
        m_y90.rotateY(degrees90)
        m_y90 = _matrix_clean(m_y90)
        ap_y90: ApexPose = ApexPose(axis=ApexPoint(0, 1, 0), angle=degrees90)
        assert m_y90.A == ap_y90.forward.A, f"{m_y90.A} != {ap_y90.forward.A}"
        m_v = m_y90 * v001
        ap_v = ap_y90.forward * v001
        assert ap_v == m_v == v100

        # Rotate around the Z axis:
        m_z90: Matrix = Matrix()
        m_z90.rotateZ(degrees90)
        m_z90 = _matrix_clean(m_z90)
        ap_z90: ApexPose = ApexPose(angle=degrees90)
        assert m_z90.A == ap_z90.forward.A, f"{m_z90.A} != {ap_z90.forward.A}"
        m_v = m_z90 * v100
        ap_v = ap_z90.forward * v100
        assert m_v == ap_v == v010

        # Do some error tests:
        try:
            ApexPose(axis=Vector(0, 0, 0), angle=degrees90, center=ApexPoint(0, 0, 0))
        except ValueError as error:
            assert str(error) == "Rotation axis (Vector (0.0, 0.0, 0.0)) has no direction", (
                f"{str(error)=}")
        try:
            ApexPose(axis={})
        except ValueError as error:
            desired_error: str = (
                "Argument 'axis' is dict which is not one of ['NoneType', 'ApexPoint', 'Vector']")
            assert str(error) == desired_error, f"{str(error)=}"
        assert not errors, f"{errors} errors encountered"

        ApexPose(z_align=ApexPoint(0, 1, 0), y_align=ApexPoint(1, 0, 0),
                 center=ApexPoint(0, 0, 1), name="y_align")

        try:
            ApexPose(z_align=Vector())
        except ValueError as error:
            assert str(error) == "z_align=Vector (0.0, 0.0, 0.0) has no direction", str(error)
        try:
            ApexPose(y_align=Vector())
        except ValueError as error:
            assert str(error) == "y_align=Vector (0.0, 0.0, 0.0) has no direction", str(error)
        try:
            ApexPose(center=23)
        except ValueError as error:
            assert str(error) == (
                "Argument 'center' is int which is not one of ['NoneType', 'ApexPoint', 'Vector']")
        try:
            ApexPose(axis=34)
        except ValueError as error:
            assert str(error) == (
                "Argument 'axis' is int which is not one of ['NoneType', 'ApexPoint', 'Vector']")
        try:
            ApexPose(z_align=45)
        except ValueError as error:
            assert str(error) == (
                "Argument 'z_align' is int which is not one of ['NoneType', 'ApexPoint', 'Vector']")
        try:
            ApexPose(y_align=56)
        except ValueError as error:
            assert str(error) == (
                "Argument 'y_align' is int which is not one of ['NoneType', 'ApexPoint', 'Vector']")
        try:
            ApexPose(axis=Vector())
        except ValueError as error:
            assert str(error) == "Rotation axis (Vector (0.0, 0.0, 0.0)) has no direction"

    @staticmethod
    def _unit_tests() -> None:
        """Run unit tests."""
        ApexPose._other_unit_tests()
        ApexPose._xy_align_unit_tests()


def _unit_tests() -> None:
    """Run the unit tests."""
    ApexCheck._unit_tests()
    ApexBoundBox._unit_tests()
    ApexPose._unit_tests()
    ApexLength._unit_tests()
    ApexPoint._unit_tests()
    ApexMaterial._unit_tests()


if __name__ == "__main__":
    _unit_tests()
