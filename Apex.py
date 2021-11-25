#!/usr/bin/env python3
"""Apex base classes.

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

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

import os
import sys

assert sys.version_info.major == 3, "Python 3.x is not running"
assert sys.version_info.minor == 8, "Python 3.8 is not running"
sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])

from FreeCAD import BoundBox, Placement, Vector  # type: ignore

# import colorsys  # Color conversion routines.
from dataclasses import dataclass
from typing import Any, cast, List, Dict, Optional, Sequence, Tuple, Union


# ApexBox:
class ApexBox:
    """An ApexBox is FreeCAD BoundBox with some additional attributes.

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
    """

    # ApexBox.__init__():
    def __init__(self,
                 corners: Sequence[Union[Vector, BoundBox, "ApexBox"]],
                 name: str = "") -> None:
        """Initialize an ApexBox.

        Arguments:
          * *corners* (Sequence[Union[Vector, BoundBox, ApexBox]]):
            A sequence of points/corners to enclose by the box.

        Raises:
          * ValueError: For bad or empty corners.

        """
        if not isinstance(corners, (list, tuple)):
            raise ValueError(f"{corners} is neither a List nor a Tuple")

        # Convert *corners* into *vectors*:
        corner: Union[Vector, BoundBox, ApexBox]
        vectors: List[Vector] = []
        index: int
        for index, corner in enumerate(corners):
            if isinstance(corner, Vector):
                vectors.append(corner)
            elif isinstance(corner, BoundBox):
                vectors.append(Vector(corner.XMin, corner.YMin, corner.ZMin))
                vectors.append(Vector(corner.XMax, corner.YMax, corner.ZMax))
            elif isinstance(corner, ApexBox):
                vectors.append(corner.TNE)
                vectors.append(corner.BSW)
            else:
                raise ValueError(
                    f"{corner} is not of type Vector/BoundBox/ApexBox")
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

        # Sweep through *vectors* expanding the box limits:
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

        self._name: str = name
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
    def DXY(self) -> Vector:
        """Delta X/Y."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMax - bb.XMin, bb.YMax - bb.YMin, 0.0)

    @property
    def DXYZ(self) -> Vector:
        """Delta X/Y/Z."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMax - bb.XMin, bb.YMax - bb.YMin, bb.ZMax - bb.ZMin)

    @property
    def DXZ(self) -> float:
        """Delta X/Z."""
        bb: BoundBox = self._bound_box
        return Vector(bb.XMax - bb.XMin, 0.0, bb.ZMax - bb.ZMin)

    @property
    def DY(self) -> float:
        """Delta Y."""
        bb: BoundBox = self._bound_box
        return bb.YMax - bb.YMin

    @property
    def DYZ(self) -> Vector:
        """Delta Y/Z."""
        bb: BoundBox = self._bound_box
        return Vector(0.0, bb.YMax - bb.YMin, bb.ZMax - bb.ZMin)

    @property
    def DZ(self) -> float:
        """Delta Z."""
        bb: BoundBox = self._bound_box
        return bb.ZMax - bb.ZMin

    @property
    def Name(self) -> str:
        """Name."""
        return self._name

    def __repr__(self) -> str:
        """Return a representation of an ApexBox."""
        return self.__str__()

    def __str__(self) -> str:
        """Return a representation of an ApexBox."""
        return f"ApexBox({self.BB})"

    # ApexBox.reorient():
    def reorient(self, placement: Placement, suffix: Optional[str] = "") -> "ApexBox":
        """Reorient ApexBox given a Placement.

        Note after the *placement* is applied, the resulting box is still rectilinear with the
        X/Y/Z axes.  In particular, box volume is *not* conserved.

        Arguments:
        * *placement* (Placement): The placement of the box corners.
        * *suffix* (Optional[str]): The suffix to append at all names.  If None, all
          names are set to "" instead appending the suffix.  (Default: "")
        """
        reorient_suffix: str = "" if suffix is None else f"{self._name}{suffix}"
        reoriented_bsw: Vector = placement * self.BSW
        reoriented_tne: Vector = placement * self.TNE
        return ApexBox((reoriented_bsw, reoriented_tne), reorient_suffix)

    @staticmethod
    def _unit_tests() -> None:
        """Perform ApexBox unit tests."""
        # Initial tests:
        bound_box: BoundBox = BoundBox(-1.0, -2.0, -3.0, 1.0, 2.0, 3.0)
        assert bound_box == bound_box
        apex_box: ApexBox = ApexBox([bound_box], name="Test")
        assert isinstance(apex_box, ApexBox)
        assert apex_box.Name == "Test"

        # FreeCAD.BoundBox.__eq__() appears to only compare ids for equality.
        # Thus, it is necessary to test that each value is equal by hand.
        assert apex_box.BB.XMin == bound_box.XMin
        assert apex_box.BB.YMin == bound_box.YMin
        assert apex_box.BB.ZMin == bound_box.ZMin
        assert apex_box.BB.XMax == bound_box.XMax
        assert apex_box.BB.YMax == bound_box.YMax
        assert apex_box.BB.ZMax == bound_box.ZMax

        # Verify __str__() works:
        want: str = f"ApexBox({bound_box})"
        assert f"{apex_box}" == want, f"'{apex_box}' != '{want}'"

        def check(vector: Vector, x: float, y: float, z: float) -> bool:
            assert vector.x == x, f"{vector.x} != {x}"
            assert vector.y == y, f"{vector.y} != {y}"
            assert vector.z == z, f"{vector.z} != {z}"
            return vector.x == x and vector.y == y and vector.z == z

        # Do 6 faces:
        assert check(apex_box.E, 1, 0, 0), "E"
        assert check(apex_box.W, -1, 0, 0), "W"
        assert check(apex_box.N, 0, 2, 0), "N"
        assert check(apex_box.S, 0, -2, 0), "S"
        assert check(apex_box.T, 0, 0, 3), "T"
        assert check(apex_box.B, 0, 0, -3), "B"

        # Do the 12 edges:
        assert check(apex_box.BE, 1, 0, -3), "BE"
        assert check(apex_box.BN, 0, 2, -3), "BN"
        assert check(apex_box.BS, 0, -2, -3), "BS"
        assert check(apex_box.BW, -1, 0, -3), "BW"
        assert check(apex_box.NE, 1, 2, 0), "NE"
        assert check(apex_box.NW, -1, 2, 0), "NW"
        assert check(apex_box.SE, 1, -2, 0), "SE"
        assert check(apex_box.SW, -1, -2, 0), "SW"
        assert check(apex_box.TE, 1, 0, 3), "TE"
        assert check(apex_box.TN, 0, 2, 3), "TN"
        assert check(apex_box.TS, 0, -2, 3), "TS"
        assert check(apex_box.TW, -1, 0, 3), "TW"

        # Do the 8 corners:
        assert check(apex_box.BNE, 1, 2, -3), "BNE"
        assert check(apex_box.BNW, -1, 2, -3), "BNW"
        assert check(apex_box.BSE, 1, -2, -3), "BSE"
        assert check(apex_box.BSW, -1, -2, -3), "BSW"
        assert check(apex_box.TNE, 1, 2, 3), "TNE"
        assert check(apex_box.TNW, -1, 2, 3), "TNW"
        assert check(apex_box.TSE, 1, -2, 3), "TSE"
        assert check(apex_box.TSW, -1, -2, 3), "TSW"

        # Do the miscellaneous attributes:
        assert check(apex_box.C, 0, 0, 0), "C"
        assert check(apex_box.BB.Center, 0, 0, 0), "Center"
        assert isinstance(apex_box.BB, BoundBox), "BB error"
        assert apex_box.C == apex_box.BB.Center, "C != Center"
        assert apex_box.DX == 2.0, "DX"
        assert apex_box.DXY == Vector(2.0, 4.0, 0.0), "DXY"
        assert apex_box.DXYZ == Vector(2.0, 4.0, 6.0), "DXYZ"
        assert apex_box.DXZ == Vector(2.0, 0.0, 6.0), "DXZ"
        assert apex_box.DY == 4.0, "DY"
        assert apex_box.DYZ == Vector(0.0, 4.0, 6.0), "DYZ"
        assert apex_box.DZ == 6.0, "DZ"
        assert check(apex_box.DB, 0, 0, -3), "DB"
        assert check(apex_box.DE, 1, 0, 0), "DE"
        assert check(apex_box.DN, 0, 2, 0), "DN"
        assert check(apex_box.DS, 0, -2, 0), "DS"
        assert check(apex_box.DT, 0, 0, 3), "DT"
        assert check(apex_box.DW, -1, 0, 0), "DW"

        # Test ApexBox() contructors:
        vector1: Vector = Vector(-1, -2, -3)
        vector2: Vector = Vector(1, 2, 3)
        new_apex_box: ApexBox = ApexBox((vector1, vector2))
        assert f"{new_apex_box.BB}" == f"{apex_box.BB}"
        next_apex_box: ApexBox = ApexBox((bound_box, new_apex_box))
        want = "ApexBox(BoundBox (-1, -2, -3, 1, 2, 3))"
        assert f"{next_apex_box}" == want, f"'{next_apex_box}' != '{want}'"
        assert next_apex_box.__repr__() == want

        # Do some error checking:
        try:
            ApexBox(())
        except ValueError as value_error:
            assert str(value_error) == "Corners sequence is empty", str(value_error)
        try:
            ApexBox(cast(List, 123))  # Force invalid argument type.
        except ValueError as value_error:
            assert str(value_error) == "123 is neither a List nor a Tuple", str(value_error)
        try:
            ApexBox(cast(List, [123]))  # Force invalid corner type
        except ValueError as value_error:
            assert str(value_error) == "123 is not of type Vector/BoundBox/ApexBox"


# ApexCheck:
@dataclass(frozen=True)
class ApexCheck(object):
    """ApexCheck: Check arguments for type mismatch errors.

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

         EXAMPLE1_CHECKS = (
             ApexCheck("arg1", (int,)),
             ApexCheck("arg2", (bool,)),
             ApexCheck("arg3", (type(None), MyType),  # Optional[myType]
             ApexCheck("arg4," list),   # List[Any]
         )
         def my_function(arg1: int, arg2: bool, arg3: Any, arg4: List[str]) -> None:
             '''Doc string here.'''
            value_error: str = ApexCheck.check((arg1, arg2, arg3, arg4), MY_FUNCTION_CHECKS)
            if value_error:
                raise ValueError(value_error)
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

        EXAMPLE2_CHECKS = (
            ApexCheck("arg1", ("+", str)),  # Arg1 must be a non-empty string
            ApexCheck("arg2", ("?", str)),  # Arg2 can be a string or None
            ApexCheck("arg3", ("+?", str)),  # Arg3 can be a non-empty string or None
            ApexCheck("arg4", ("L", str)),  # Arg4 can be a list of strings
            ApexCheck("arg5", ("T", str)),  # Arg4 can be a tuple of strings
            ApexCheck("arg6", ("S", str)),  # Arg6 can be a list or tuple of strings
            ApexCheck("arg7", ("L", (float, int)),  # Arg7 can be a list of mixed float and int

    """

    name: str  # Argument name
    options: Tuple[Any, ...]  # Types or patterns to match

    @staticmethod
    def _type_name(t: Any) -> str:
        """Return the best guess for the type name."""
        name: str = f"{t}"
        if hasattr(t, "__name__"):
            name = t.__name__
        elif hasattr(t, "__class__"):
            name = t.__class__.__name__
        return name

    # ApexCheck.check():
    @classmethod
    def check(cls, values: Sequence[Any],
              apex_checks: Sequence["ApexCheck"], tracing: str = "") -> str:
        """Return type mismatch error message."""
        if tracing:
            print(f"{tracing}=>ApexCheck({values}, {apex_checks}")
        assert len(values) == len(apex_checks), (
            f"{len(values)} values do not match {len(apex_checks)} checks")
        error: str = ""
        index: int
        value: Any
        for index, value in enumerate(values):
            # Catagorize *value*:
            is_list: bool = isinstance(value, list)
            is_tuple: bool = isinstance(value, tuple)
            is_sequence: bool = is_list or is_tuple
            length: int = -1
            try:
                length = len(value)
            except TypeError:
                pass
            if tracing:
                print(f"{tracing}{is_list=} {is_tuple=} {is_sequence=} {length=}")

            # Get associated *apex_check* and unpack it:
            apex_check: "ApexCheck" = apex_checks[index]
            # if not isinstance(apex_check, cls):
            #     raise ValueError(f"[{index}]:{apex_check} is not ApexCheck:  {apex_checks}")
            name: str = apex_check.name
            options: Tuple[Any, ...] = apex_check.options
            # if not options:
            #    raise ValueError(f"[{index}]:{apex_check} has empty options")
            flags: str = ""
            if isinstance(options[0], str):
                flags = options[0]
                options = options[1:]
            if tracing:
                print(f"{tracing}{flags=} {options=}")

            # Process each *flag* in *flags*:
            flag: str
            for flag in sorted(flags, reverse=True):  # Do letter flags first:
                if flag == 'S':
                    if not is_sequence:
                        error = f"[{index}]: Argument '{name}' is neither a list nor tuple"
                elif flag == 'L':
                    if not is_list:
                        error = f"[{index}]: Argument '{name}' is not a list"
                elif flag == 'T':
                    if tracing:
                        print(f"{tracing}{flag=} {is_tuple=}")
                    if not is_tuple:
                        error = f"[{index}]: Argument '{name}' is not a tuple"
                elif flag == '+':
                    if tracing:
                        print(f"{tracing}{flag=}")
                    if length < 1:
                        error = f"[{index}]: Argument '{name}' has no length"
                    elif length == 0:
                        error = f"[{index}]: Argument '{name}' is empty"
                elif flag == '?':
                    options += (type(None),)  # Allow for None type.
                else:
                    raise ValueError(f"Flag '{flag=}' is not allowed {flags=}.")
                if flag:
                    break

            if not error:
                type_names: Sequence[str]
                if is_sequence:
                    # For a sequence, verify the sequence element types:
                    element: Any
                    for index, element in enumerate(value):
                        for option in options:
                            if isinstance(element, option):
                                break
                        else:
                            type_names = [ApexCheck._type_name(option)
                                          for option in options]
                            error = (f"[{index}]: {element} ({cls._type_name(element)}) "
                                     f"is not of type {type_names}")
                            break
                else:
                    # For a non-sequence, verify the types:
                    for option in options:
                        if isinstance(value, option):
                            break  # Type matched
                    else:
                        type_names = [ApexCheck._type_name(option)
                                      for option in options]
                        error = (f"Argument '{name}' is {cls._type_name(value)} "
                                 f"which is not one of {type_names}")
                        break
        if tracing:
            print(f"{tracing}<=ApexCheck({values}, {apex_checks}=>'{error}'")
        return error

    # ApexCheck.init_show():
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
            argument_options: Tuple[Any, ...] = apex_check.options
            none_allowed: bool = type(None) in argument_options
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

        # Do some flags based checks:
        float_list_check: ApexCheck = ApexCheck("float_list_check", ("L", float))
        float_sequence_check: ApexCheck = ApexCheck("float_sequence_check", ("S", float))
        float_tuple_check: ApexCheck = ApexCheck("float_tuple_check", ("T", float))
        int_list_check: ApexCheck = ApexCheck("int_list_check", ("L", int))
        int_sequence_check: ApexCheck = ApexCheck("int_sequence_check", ("S", int))
        int_tuple_check: ApexCheck = ApexCheck("int_tuple_check", ("T", int))
        number_list_check: ApexCheck = ApexCheck("float_list_check", ("L", float, int))
        number_sequence_check: ApexCheck = ApexCheck("float_sequence_check", ("S", float, int))
        number_tuple_check: ApexCheck = ApexCheck("float_tuple_check", ("T", float, int))

        empty_list: List[Union[int, float]] = []
        empty_tuple: Tuple[Union[int, float], ...] = ()
        int_list: List[int] = [1, 2, 3]
        int_tuple: Tuple[int, ...] = (1, 2, 3)
        float_list: List[float] = [1.0, 2.0, 3.0]
        float_tuple: Tuple[float, ...] = (.0, 2.0, 3.0)
        number_list: List[Union[int, float], ...] = [1, 2.0, 3]
        number_tuple: Tuple[Union[int, float], ...] = (1, 2.0, 3)

        good_pairs: Sequence[Tuple[Any, ApexCheck]] = (
            # Empty Checks:
            (empty_list, int_list_check),
            (empty_list, float_list_check),
            (empty_list, number_list_check),
            (empty_list, int_sequence_check),
            (empty_list, float_sequence_check),
            (empty_list, number_sequence_check),

            (empty_tuple, int_tuple_check),
            (empty_tuple, float_tuple_check),
            (empty_tuple, number_tuple_check),
            (empty_tuple, int_sequence_check),
            (empty_tuple, float_sequence_check),
            (empty_tuple, number_sequence_check),

            # Non_empty check:
            (int_list, int_list_check),
            (int_list, number_list_check),
            (int_list, int_sequence_check),
            (int_list, number_sequence_check),

            (float_list, float_list_check),
            (float_list, number_list_check),
            (float_list, float_sequence_check),
            (float_list, number_sequence_check),

            (number_list, number_list_check),
            (number_list, number_sequence_check),

            (int_tuple, int_tuple_check),
            (int_tuple, number_tuple_check),
            (int_tuple, int_sequence_check),
            (int_tuple, number_sequence_check),

            (float_tuple, float_tuple_check),
            (float_tuple, number_tuple_check),
            (float_tuple, float_sequence_check),
            (float_tuple, number_sequence_check),

            # (number_tuple, number_tuple_check),
            (number_tuple, number_sequence_check),
        )

        bad_pairs: Sequence[Tuple[Any, ApexCheck]] = (
            (int_tuple, int_list_check),
            (float_tuple, int_list_check),
            (number_tuple, int_list_check),
            (float_list, int_list_check),
            (number_list, int_list_check),
            (int_list, float_list_check),
            (number_list, float_list_check),
        )

        index: int
        value: Any
        apex_check: ApexCheck
        good_pair: Tuple

        good_pair: Tuple[Any, ApexCheck]
        for index, good_pair in enumerate(good_pairs):
            value, apex_check = good_pair
            assert isinstance(apex_check, cls), apex_check
            error = ApexCheck.check((value,), (apex_check,))
            assert not error, f"[{index}]: {value=} {apex_check=} {error=}"

        value: Any
        apex_check: ApexCheck
        for value, apex_check in bad_pairs:
            assert isinstance(apex_check, cls)
            error = ApexCheck.check((value,), (apex_check,))
            assert error, "No error generated"

        # Test non sequence checks:
        non_empty_string_check: ApexCheck = ApexCheck("Name", ("+", str))
        value_error: str = ApexCheck.check(("non-empty",), (non_empty_string_check,))
        assert value_error == "", f"{value_error=}"
        value_error = ApexCheck.check(("",), (non_empty_string_check,))
        assert value_error == "[0]: Argument 'Name' has no length", value_error

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


# ApexColor:
class ApexColor(object):
    """ApexColor: Convert from SVG color names to FreeCAD HSL."""

    RGB_COLORS = {
        "alice_blue": 0xf0f8ff,
        "antique_white": 0xfaebd7,
        "aqua": 0x00ffff,
        "aquamarine": 0x7fffd4,
        "azure": 0xf0ffff,
        "beige": 0xf5f5dc,
        "bisque": 0xffe4c4,
        "black": 0x000000,
        "blanched_almond": 0xffebcd,
        "blue": 0x0000ff,
        "blue_violet": 0x8a2be2,
        "brown": 0xa52a2a,
        "burlywood": 0xdeb887,
        "cadet_blue": 0x5f9ea0,
        "chartreuse": 0x7fff00,
        "chocolate": 0xd2691e,
        "coral": 0xf08080,
        "corn_flower_blue": 0x6495ed,
        "corn_silk": 0xfff8dc,
        "crimson": 0xdc143c,
        "cyan": 0x00ffff,
        "dark_blue": 0x00008b,
        "dark_cyan": 0x008b8b,
        "dark_goldenrod": 0xb8860b,
        "dark_gray": 0xa9a9a9,
        "dark_green": 0x006400,
        "dark_grey": 0xa9a9a9,
        "dark_khaki": 0xbdb76b,
        "dark_magenta": 0x8b008b,
        "dark_olive_green": 0x556b2f,
        "dark_orange": 0xff8c00,
        "dark_orchid": 0x9932cc,
        "dark_red": 0x8b0000,
        "dark_salmon": 0xe9967a,
        "dark_sea_green": 0x8fbc8f,
        "dark_slate_blue": 0x483d8b,
        "dark_slate_gray": 0x2f4f4f,
        "dark_slate_grey": 0x2f4f4f,
        "dark_turquoise": 0x40e0d0,
        "dark_violet": 0x9f00d3,
        "deep_pink": 0xff1493,
        "deep_sky_blue": 0x00bfff,
        "dim_gray": 0x696969,
        "dim_grey": 0x696969,
        "dodger_blue": 0x1e90ff,
        "fire_brick": 0xb22222,
        "floral_white": 0xfffaf0,
        "forest_green": 0x228b22,
        "fuchsia": 0xff00ff,
        "gainsboro": 0xdcdcdc,
        "ghost_white": 0xf8f8ff,
        "gold": 0xffd700,
        "goldenrod": 0xdaa520,
        "gray": 0x808080,
        "green": 0x008000,
        "green_yellow": 0xadff2f,
        "grey": 0x808080,
        "honey_dew": 0xf0fff0,
        "hot_pink": 0xff1493,
        "indian_red": 0xcd5c5c,
        "indigo": 0x4b0082,
        "ivory": 0xfffff0,
        "khaki": 0xf0e68c,
        "lavender": 0xe6e6fa,
        "lavender_blush": 0xfff0f5,
        "lawn_green": 0x7cfc00,
        "lemon_chiffon": 0xfffacd,
        "light_blue": 0xadd8e6,
        "light_coral": 0xf08080,
        "light_cyan": 0xe0ffff,
        "light_goldenrod_yellow": 0xfafad2,
        "light_gray": 0xd3d3d3,
        "light_green": 0x90ee90,
        "light_grey": 0xd3d3d3,
        "light_pink": 0xffb6c1,
        "light_salmon": 0xffa07a,
        "light_sea_green": 0x20b2aa,
        "light_sky_blue": 0x87cefa,
        "light_slate_gray": 0x778899,
        "light_slate_grey": 0x778899,
        "light_steel_blue": 0xb0c4de,
        "light_yellow": 0xffffe0,
        "lime": 0x00ff00,
        "lime_green": 0x2e8b57,
        "linen": 0xfaf0e6,
        "magenta": 0xff00ff,
        "maroon": 0x800000,
        "medium_aquamarine": 0x66cdaa,
        "medium_blue": 0x0000cd,
        "medium_orchid": 0xba55d3,
        "medium_purple": 0x9370db,
        "medium_sea_green": 0x3cb371,
        "medium_slate_blue": 0x66cdaa,
        "medium_spring_green": 0x00fa9a,
        "medium_turquoise": 0x48d1cc,
        "medium_violet_red": 0xc71585,
        "mid_night_blue": 0x191970,
        "mint_cream": 0xf5fffa,
        "misty_rose": 0xffe4e1,
        "moccasin": 0xffe4b5,
        "navajo_white": 0xffdead,
        "navy": 0x000080,
        "old_lace": 0xfdf5e6,
        "olive": 0x808000,
        "olive_drab": 0x6b8e23,
        "orange": 0xffa500,
        "orange_red": 0xff4500,
        "orchid": 0xda70d6,
        "pale_goldenrod": 0xeee8aa,
        "pale_green": 0x98fb98,
        "pale_turquoise": 0xafeeee,
        "pale_violet_red": 0xdb7093,
        "papaya_whip": 0xffefd5,
        "peach_puff": 0xffdab9,
        "peru": 0xcd8f3f,
        "pink": 0xffc0cb,
        "plum": 0xdda0dd,
        "powder_blue": 0xb0e0e6,
        "purple": 0x800080,
        "red": 0xff0000,
        "rosy_brown": 0xbc8f8f,
        "royal_blue": 0x4169e1,
        "saddle_brown": 0x8b2be2,
        "salmon": 0xfa8072,
        "sandy_brown": 0xf4a460,
        "sea_green": 0x2e8b57,
        "sea_shell": 0xfff5ee,
        "sienna": 0xa0522d,
        "silver": 0xc0c0c0,
        "sky_blue": 0x87ceeb,
        "slate_blue": 0x6a5acd,
        "slate_gray": 0x708090,
        "slate_grey": 0x708090,
        "snow": 0xfffafa,
        "spring_green": 0x00ff7f,
        "steel_blue": 0x4682b4,
        "tan": 0xd2b48c,
        "teal": 0x008080,
        "thistle": 0xd8bfd8,
        "tomato": 0xff6347,
        "turquoise": 0x40e0d0,
        "violet": 0xee82ee,
        "wheat": 0xf5deb3,
        "white": 0xffffff,
        "white_smoke": 0xf5f5f5,
        "yellow": 0xffff00,
        "yellow_green": 0x9acd32,
    }

    @staticmethod
    def svg_to_rgb(svg_color_name: str) -> Tuple[float, float, float]:
        """Convert Scalable Vector Graphics color to Hue/Saturation/Value tuple.

        Arguments:
        * *svg_color_name* (str): The SVG color name to use.

        Returns:
        * (Tuple[float, float, float]) as HSV (Hue/Satruation/Value) tuple used by FreeCAD.

        """
        rgb_colors: Dict[str, int] = ApexColor.RGB_COLORS
        if svg_color_name not in rgb_colors:
            raise ValueError(f"'{svg_color_name}' is not a supported SVG color name.")
        rgb_color: int = rgb_colors[svg_color_name]
        red: int = (rgb_color >> 16) & 0xff
        green: int = (rgb_color >> 8) & 0xff
        blue: int = rgb_color & 0xff
        return (float(red) / 255.0, float(green) / 255.0, float(blue) / 255.0)

    @staticmethod
    def _unit_tests() -> None:
        """Run ApexColor unit tests."""
        _ = ApexColor.svg_to_rgb("red")

        try:
            ApexColor.svg_to_rgb("fred")
        except ValueError as value_error:
            assert str(value_error) == "'fred' is not a supported SVG color name.", str(value_error)


# Miscellaneous functions:

# float_fix():
def float_fix(length: float) -> float:
    """Return a length that is rounded to a whole number when appropriate."""
    is_negative: bool = length < 0.0
    if is_negative:
        length = -length

    whole: float
    fractional: float
    whole, fractional = divmod(length, 1.0)

    epsilon: float = 1.0e-8
    if abs(fractional) < epsilon:
        fractional = 0.0
    if abs(fractional - 1.0) < epsilon:
        fractional = 0.0  # pragma: no unit cover
        whole += 1.0  # pragma: no unit cover
    fixed_length: float = whole + fractional
    if is_negative:
        fixed_length = -fixed_length
    if abs(fixed_length) == 0.0:
        fixed_length = 0.0
    return fixed_length


# vector_fix():
def vector_fix(vector: Vector) -> Vector:
    """Return Vector with values rounded to appropriate hole numbers."""
    return Vector(float_fix(vector.x), float_fix(vector.y), float_fix(vector.y))


# ApexMaterial:
@dataclass
class ApexMaterial(object):
    """ApexMaterial: Represents a stock material.

    Other properties to be added later (e.g. transparency, shine, machining properties, etc.)

    Attributes:
    * *Name* (Tuple[str, ...]): A list of material names from generict to specific.
    * *Color* (str): The color name to use.

    """

    Name: Tuple[str, ...]  # Hierarchical name from least specific to most specific.
    Color: str  # SVG color name to use.

    INIT_CHECKS = (
        ApexCheck("Name", ("T+", str)),
        ApexCheck("Color", (str,)),
    )

    # ApexMaterial.__init__():
    def __post_init__(self) -> None:
        """Post process."""
        arguments = (self.Name, self.Color)
        value_error: str = ApexCheck.check(arguments, ApexMaterial.INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)
        assert isinstance(self.Name, tuple)
        if len(self.Name) == 0:
            raise ValueError(f"Material is an empty tuple.")
        name: str
        for name in self.Name:
            if not name:
                raise ValueError("Name contains an empty string")
        if not self.Color:
            raise ValueError(f"Color name is empty")

    def __repr__(self) -> str:
        """Return string representation of ApexMaterial."""
        return self.__str__()

    def __str__(self) -> str:
        """Return string representation of ApexMaterial."""
        return f"ApexMaterial({self.Name}, '{self.Color}')"

    @staticmethod
    def _unit_tests() -> None:
        """Run ApexMaterial unit tests."""
        name: Tuple[str, ...] = ("brass",)
        color: str = "orange"
        material: ApexMaterial = ApexMaterial(name, color)
        assert material.__repr__() == "ApexMaterial(('brass',), 'orange')"
        assert f"{material}" == "ApexMaterial(('brass',), 'orange')", f"{material}"
        material_text: str = f"ApexMaterial({name}, '{color}')"
        assert f"{material}" == material_text, f"{material}"

        # Name is not a Tuple:
        try:
            ApexMaterial(cast(tuple, 0), color)
        except ValueError as value_error:
            want: str = "[0]: Argument 'Name' is not a tuple"
            got: str = str(value_error)
            assert want == got, (want, got)

        # Name is empty tuple:
        try:
            ApexMaterial((), color)
        except ValueError as value_error:
            assert str(value_error) == "Material is an empty tuple.", str(value_error)

        # Name with an empty string:
        try:
            ApexMaterial(("",), color)
        except ValueError as value_error:
            assert str(value_error) == "Name contains an empty string", str(value_error)

        # Name is does not have a string:
        try:
            ApexMaterial((cast(str, 1),), color)
        except ValueError as value_error:
            want = "[0]: 1 (int) is not of type ['str']"
            got = str(value_error)
            assert got == want, (got, want)

        # Color is empty.
        try:
            ApexMaterial(("Brass",), "")
        except ValueError as value_error:
            assert str(value_error) == "Color name is empty", str(value_error)


def _misc_unit_tests() -> None:
    """Test helper functions."""
    # Test float_fix():
    assert float_fix(0.0) == 0.0, "Zero fail"
    assert float_fix(1.0) == 1.0, "1.0 fail"
    assert float_fix(-1.0) == -1.0, "-1.0 fail"
    assert float_fix(0.5) == 0.5, "0.5 fail"
    assert float_fix(-0.5) == -0.5, "-0.5 fail"
    epsilon: float = 1.0e-11
    assert float_fix(epsilon) == 0.0, "epsilon fail"
    assert float_fix(-epsilon) == 0.0, "-epsilon fail"
    assert float_fix(1 - epsilon) == 1.0, "1-epsilon fail"
    assert float_fix(1 + epsilon) == 1.0, "1+epsilon fail"
    assert float_fix(-1 - epsilon) == -1.0, "-1-epsilon fail"
    assert float_fix(-1 + epsilon) == -1.0, "-1+epsilon fail"

    # Test vector_fix():
    return vector_fix(Vector(epsilon, 1.0 - epsilon, -1.0 + epsilon)) == Vector(0.0, 0.0, 0.0)


def _unit_tests() -> None:
    """Run the unit tests."""
    _misc_unit_tests()
    ApexCheck._unit_tests()
    ApexColor._unit_tests()
    ApexBox._unit_tests()
    ApexMaterial._unit_tests()


if __name__ == "__main__":
    _unit_tests()
