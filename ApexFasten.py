#!/usr/bin/env python3
"""ApexFasten: A Package for managing fasteners in the Apex system.

While the most common fasteners are screws and bolts, there are others like rivets, set screws,
cotter pins, etc.  This package centralizes all of the issues associated with fasteners
so that changing a fastener does not become a nightmare of having to individually find
each fastener and make manual changes to each one.  The change is made in once place and
it propagates to all associated fasteners.

The ApexFasten class deals with the following issues:
* Hole Drilling/Milling:
  Getting a hole of the of the correct size and depth at the correct location on a part.
* Threading:
  Ensuring that the hole is properly threaded using the appropriate threading tool.
* Countersink/Counterbore:
  Ensuring that appropriate counter sinks and counter bores occur at the correct depth
* Deburring:
  Deburring hole edges.
* Fastener stacks:
  Specifying the washers, lock washers, nuts, cotter pins, etc. to screws/bolts.
* Substitutions:
  Graceful substitutions between imperial (North America) vs. metric hardware (everyone else.)
* Lengths:
  Selecting appropriate screw/bolt lengths to deal with parametric changes to shapes.
* Bill of Materials:
  Collecting all of the fasteners into a bill of materials.
* Assembly View:
  When assembly views are supported, all of the fasteners are exploded out with a dashed
  line to connect them all.
* Fastener WorkBench:
  The FreeCAD Fasteners workbench is used wherever possible.

The ApexJoin class specifics a single fastener instance.  It specifies two end points
(i.e. Vector's) and a class of sub-parts (screw head, screw drive, washer, lock washer, etc.)
The screw/bolt length to use is determined and associated operations occur.  For a given part,
the holes are correctly placed and sized for each part.  The end user basically says "this part
interacts with this following ApexJoin's" and the Apex system takes care of the rest.  Moving
either of the two end-points of an ApexJoin automatically updates all associated parts that
use the ApexJoin.

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

import os
import sys

assert sys.version_info.major == 3, "Python 3.x is not running"
assert sys.version_info.minor == 8, "Python 3.8 is not running"
sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])

from dataclasses import dataclass
from typing import cast, Tuple

from Apex import ApexCheck, ApexMaterial
from FreeCAD import Vector  # type: ignore

#  https://github.com/shaise/FreeCAD_FastenersWB


# ApexOption:
@dataclass(frozen=True)
class ApexOption(object):
    """ApexOption: Base class for ApexFasten options (e.g. washers, nuts, etc...).

    Attributes:
    * *Name* (str): The option name.
    * *Detail* (str): More detailed information about the option.

    """

    Name: str  # ApexOption name
    Detail: str  # ApexOption description.

    def __post_init__(self) -> None:
        """Ensure values are reasonable."""
        if not isinstance(self.Name, str):
            raise ValueError("Name is not a string.")
        if not self.Name:
            raise ValueError(f"Name is empty")
        if not isinstance(self.Detail, str):
            raise ValueError(f"Detail is not a string.")
        if not self.Detail:
            raise ValueError(f"Detail is empty")

    def __repr__(self) -> str:
        """Return String representation of ApexOption."""
        return self.__str__()

    def __str__(self) -> str:
        """Return String representation of ApexOption."""
        return f"ApexOption('{self.Name}', '{self.Detail}')"

    @staticmethod
    def _unit_tests() -> None:
        """Run ApexOption unit tests."""
        name: str = "name"
        detail: str = "detail"
        option: ApexOption = ApexOption(name, detail)
        assert option.Name == name
        assert option.Detail == detail
        assert f"{option}" == "ApexOption('name', 'detail')", f"{option}"


# ApexHead:
@dataclass(frozen=True)
class ApexHead(ApexOption):
    """Represents the Head of the ApexFastener.

    Attributes:
    * *Name* (str): The name for this head.
    * *Detail* (str): Short ApexHead description.
    * *Material* (ApexMaterial): The ApexHead fastener material.
    * *Shape* (str): The ApexHead shape.
    * *Drive* (str): The ApexH drive .

    """

    Material: ApexMaterial  # ApexHead material
    Shape: str  # ApexHead shape
    Drive: str  # ApexHead drive

    # Screw Heads:
    CHEESE_HEAD = "Cheese"
    FILLISTER_HEAD = "Fillister"
    FLAT_HEAD = "Flat"
    HEX_HEAD = "Hex"  # For a Bolt
    OVAL_HEAD = "Oval"
    PAN_HEAD = "Pan"
    ROUND_HEAD = "Round"

    # Screw Drives:
    CARRIAGE = "Carriage"  # Carriage Bolts do not get driven
    HEX_DRIVE = "Hex"
    PHILIPS_DRIVE = "Philips"
    SLOT_DRIVE = "Slot"
    TORX_DRIVE = "Torx"

    HEADS = (CHEESE_HEAD, FILLISTER_HEAD, FLAT_HEAD, HEX_HEAD, OVAL_HEAD, PAN_HEAD, ROUND_HEAD)
    DRIVES = (CARRIAGE, HEX_DRIVE, PHILIPS_DRIVE, SLOT_DRIVE, TORX_DRIVE)

    INIT_CHECKS = (
        ApexCheck("Name", (str,)),
        ApexCheck("Detail", (str,)),
        ApexCheck("Material", (ApexMaterial,)),
        ApexCheck("Shape", (str,)),
        ApexCheck("Drive", (str,)),
    )

    def __post_init__(self) -> None:
        """Verify ApexHead."""
        arguments = (self.Name, self.Detail, self.Material, self.Shape, self.Drive)
        value_error: str = ApexCheck.check(arguments, ApexHead.INIT_CHECKS)
        if not self.Name:
            raise ValueError("Name is empty")
        if not self.Detail:
            raise ValueError("Detail is empty")
        if value_error:
            raise ValueError(value_error)
        if not isinstance(self.Material, ApexMaterial):
            raise ValueError("Material is not an ApexMaterial")
        if self.Shape not in ApexHead.HEADS:
            raise ValueError(f"Shape (='{self.Shape}') is not in {ApexHead.HEADS}")
        if self.Drive not in ApexHead.DRIVES:
            raise ValueError(f"Head (='{self.Drive}') is not in {ApexHead.DRIVES}")

    def __repr__(self) -> str:
        """Return ApexHead as a string."""
        return self.__str__()

    def __str__(self) -> str:
        """Return ApexHead as a string."""
        return (f"ApexHead('{self.Name}', '{self.Detail}', "
                f"{self.Material}, '{self.Shape}', {self.Drive})")

    @staticmethod
    def _unit_tests() -> None:
        """Run ApexHead unit tests."""
        name: str = "PH"
        detail: str = "Brass Philips Pan Head"
        material: ApexMaterial = ApexMaterial(("Brass",), "orange")
        shape: str = ApexHead.PAN_HEAD
        drive: str = ApexHead.PHILIPS_DRIVE
        apex_head: ApexHead = ApexHead(name, detail, material, shape, drive)

        # Verify __repr__() and attributes work:
        assert f"{apex_head}" == (
            "ApexHead('PH', 'Brass Philips Pan Head', ApexMaterial(('Brass',), 'orange'), "
            "'Pan', Philips)"), f"{apex_head}"
        assert apex_head.Name == name, apex_head.Name
        assert apex_head.Material is material, apex_head.Material
        assert apex_head.Shape == shape, apex_head.Shape
        assert apex_head.Drive == drive, apex_head.Drive

        # Empty Name Test:
        try:
            ApexHead("", detail, material, shape, drive)
        except ValueError as value_error:
            assert str(value_error) == "Name is empty", str(value_error)

        # Bad Detail:
        try:
            ApexHead(name, "", cast(ApexMaterial, 0), shape, drive)
        except ValueError as value_error:
            assert str(value_error) == "Detail is empty", str(value_error)

        # Bad Material:
        try:
            ApexHead(name, detail, cast(ApexMaterial, 0), shape, drive)
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'Material' is int which is not one of ['ApexMaterial']"), str(value_error)

        # Bad Shape:
        try:
            ApexHead(name, detail, material, "", drive)
        except ValueError as value_error:
            assert str(value_error) == ("Shape (='') is not in ('Cheese', 'Fillister', "
                                        "'Flat', 'Hex', 'Oval', 'Pan', 'Round')"), str(value_error)

        # Bad Drive:
        try:
            ApexHead(name, detail, material, "", drive)
        except ValueError as value_error:
            assert str(value_error) == ("Shape (='') is not in ('Cheese', 'Fillister', 'Flat', "
                                        "'Hex', 'Oval', 'Pan', 'Round')"), str(value_error)


# ApexNut:
@dataclass(frozen=True)
class ApexNut(ApexOption):
    """ApexNut: A class the represents a fastener nut.

    Attributes:
    * Name (str): Nut name.
    * Detail (str): More nut detail.
    * Sides (int): The number of nut sides (either 4 or 6.)
    * Width (float): The Nut width between 2 opposite faces.
    * Thickness (float): The nut thickness in millimeters.
    * Material (ApexMaterial): The nut material

    """

    Sides: int  # The Nut sides (either, 4 or 6).
    Width: float  # The Nut width between 2 faces in millimeters.
    Thickness: float  # The Nut thickness in millimeters.
    Material: ApexMaterial  # The Nut material.

    INIT_CHECKS = (
        ApexCheck("Name", (str,)),
        ApexCheck("Detail", (str,)),
        ApexCheck("Sides", (int,)),
        ApexCheck("Width", (float,)),
        ApexCheck("Thickness", (float,)),
        ApexCheck("Material", (ApexMaterial,)),
    )

    def __post_init__(self) -> None:
        """Verify everything is reasonable."""
        arguments = (self.Name, self.Detail, self.Sides, self.Width, self.Thickness, self.Material)
        value_error: str = ApexCheck.check(arguments, ApexNut.INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)
        if not self.Name:
            raise ValueError(f"Name is empty")
        if not self.Detail:
            raise ValueError(f"Detail is empty")
        if self.Sides not in (4, 6):
            raise ValueError(f"Sides (={self.Sides}) is neither 4 nor 6")
        if self.Width <= 0.0:
            raise ValueError(f"Width (={self.Width}) is not positive")
        if self.Thickness <= 0.0:
            raise ValueError(f"Thickness (={self.Thickness}) is not positive")

    def __repr__(self) -> str:
        """Return ApexNut string representation."""
        return self.__str__()

    def __str__(self) -> str:
        """Return ApexNut string representation."""
        return (f"ApexNut('{self.Name}', '{self.Detail}', {self.Sides}, {self.Width}, "
                f"{self.Thickness}, {self.Material})")

    @staticmethod
    def _unit_tests() -> None:
        """Run ApexNut unit tests."""
        # Create the ApexNut:
        name: str = "M3Nut"
        detail: str = "Brass M3 Hex Nut"
        sides: int = 6
        width: float = 6.2
        thickness: float = 2.0
        material: ApexMaterial = ApexMaterial(("brass",), "orange")
        nut: ApexNut = ApexNut(name, detail, sides, width, thickness, material)

        # Verify attributes:
        assert nut.Name == name, nut.Name
        assert nut.Detail == detail, nut.Detail
        assert nut.Sides == sides, nut.Sides
        assert nut.Width == width, nut.Width
        assert nut.Thickness == thickness, nut.Thickness
        assert nut.Material == material, nut.Material

        # Verify __repr__() and __str__():
        nut_text: str = f"ApexNut('{name}', '{detail}', {sides}, {width}, {thickness}, {material})"
        assert f"{nut}" == nut_text, (f"{nut}", nut_text)

        # Do argument checking:
        try:
            # Empty name:
            ApexNut("", detail, sides, width, thickness, material)
        except ValueError as value_error:
            assert str(value_error) == "Name is empty", str(value_error)

        try:
            # Empty detail:
            ApexNut(name, "", sides, width, thickness, material)
        except ValueError as value_error:
            assert str(value_error) == "Detail is empty", str(value_error)

        try:  # Bad sides:
            ApexNut(name, detail, 5, width, thickness, material)
        except ValueError as value_error:
            assert str(value_error) == "Sides (=5) is neither 4 nor 6", str(value_error)

        try:  # Bad width:
            ApexNut(name, detail, sides, 0.0, thickness, material)
        except ValueError as value_error:
            assert str(value_error) == "Width (=0.0) is not positive", str(value_error)

        try:  # Bad thickness:
            ApexNut(name, detail, sides, width, 0.0, material)
        except ValueError as value_error:
            assert str(value_error) == "Thickness (=0.0) is not positive", str(value_error)

        try:  # Bad Material:
            ApexNut(name, detail, sides, width, thickness, cast(ApexMaterial, 0))
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'Material' is int which is not one of ['ApexMaterial']"), str(value_error)


# ApexWasher:
@dataclass(frozen=True)
class ApexWasher(ApexOption):
    """ApexWahser: Represents a washer.

    Constants:
    * PLAIN: Plain washer.
    * INTERNAL_LOCK: Internal tooth lock washer.
    * EXTERNAL_LOCK: External tooth lock washer.
    * SPLIT_LOCK: Split ring lock washer.

    Attributes:
    * *Name* (str): The washer name.
    * *Detail* (str): More detail about the ApexWasher.
    * *Inner* (float): The Inner diameter in millimeters.
    * *Outer* (float): The Outer diameter in millimeters.
    * *Thickness* (float): The thickness in millimeters.
    * *Material* (ApexMaterial): The Material the washer is made out of.
    * *Kind* (str): The washer kind -- one of following ApexWasher constants --
      `PLAIN`, `INTERNAL_LOCK`, `EXTERNAL_LOCK`, or `SPLIT_LOCK`.

    """

    Inner: float  # Inner diameter
    Outer: float  # Outer diameter
    Thickness: float  # Thickness
    Material: ApexMaterial  # Material
    Kind: str  # Kind

    # Predefined constants for Kind.
    PLAIN = "PLAIN"
    INTERNAL_LOCK = "INTERNAL_LOCK"
    EXTERNAL_LOCK = "EXTERNAL_LOCK"
    SPLIT_LOCK = "SPLIT_LOCK"

    INIT_CHECKS = (
        ApexCheck("Name", (str,)),
        ApexCheck("Detail", (str,)),
        ApexCheck("Inner", (float,)),
        ApexCheck("Outer", (float,)),
        ApexCheck("Thickness", (float,)),
        ApexCheck("Material", (ApexMaterial,)),
        ApexCheck("Kind", (str,)),
    )

    # ApexWasher:
    def __post_init__(self):
        """Post process ApexWasher looking for errors."""
        # Check the arguments and do any requested *tracing*:
        arguments = (self.Name, self.Detail, self.Inner, self.Outer, self.Thickness,
                     self.Material, self.Kind)
        value_error: str = ApexCheck.check(arguments, ApexWasher.INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)
        if self.Inner <= 0.0:
            raise ValueError(f"Inner (={self.Inner}) is not positive")
        if self.Outer <= 0.0:
            raise ValueError(f"Outer (={self.Outer}) is not positive")
        if self.Inner >= self.Outer:
            raise ValueError(f"Inner (={self.Inner}) >= Outer (={self.Outer})")
        if self.Thickness <= 0.0:
            raise ValueError(f"Thickness (={self.Thickness}) is not positive")
        kinds: Tuple[str, ...] = (
            ApexWasher.PLAIN,
            ApexWasher.INTERNAL_LOCK,
            ApexWasher.EXTERNAL_LOCK,
            ApexWasher.SPLIT_LOCK,
        )
        if self.Kind not in kinds:
            raise ValueError(f"Kind (='{self.Kind}') is not one of {kinds}")

    def __repr__(self) -> str:
        """Return string representation of ApexWasher."""
        return self.__str__()

    def __str__(self) -> str:
        """Return string representation of ApexWasher."""
        return (f"ApexWasher('{self.Name}', '{self.Detail}', {self.Inner}, {self.Outer}, "
                f"{self.Thickness}, {self.Material}, '{self.Kind}')")

    @staticmethod
    def _unit_tests() -> None:
        """Perform ApexWasher unit tests."""
        # Create the *washer*:
        name: str = "W6x.5"
        detail: str = "M3 Washer (ID=3.2 OD=6, Thick=.5)"
        inner: float = 3.2
        outer: float = 6.0
        thickness: float = 0.5
        material: ApexMaterial = ApexMaterial(("brass",), "orange")
        kind: str = ApexWasher.PLAIN
        washer: ApexWasher = ApexWasher(name, detail, inner, outer, thickness, material, kind)

        # Ensure that the __str__() method works:
        washer_text: str = (f"ApexWasher('{name}', '{detail}', "
                            f"{inner}, {outer}, {thickness}, {material}, '{kind}')")
        assert f"{washer}" == washer_text, (f"{washer}", washer_text)

        # Access all of the attributes:
        assert washer.Name == name, washer.Name
        assert washer.Detail == detail, washer.Detail
        assert washer.Inner == inner, washer.Inner
        assert washer.Outer == outer, washer.Outer
        assert washer.Thickness == thickness, washer.Thickness
        assert washer.Material is material, washer.Material
        assert washer.Kind == kind, washer.Kind

        # Do argument checks:
        try:
            # Empty name error:
            ApexWasher("", detail, inner, outer, thickness, material, kind)
        except ValueError as value_error:
            assert str(value_error) == "Name is empty", str(value_error)

        try:
            # Empty detail errora:
            ApexWasher(name, "", inner, outer, thickness, material, kind)
        except ValueError as value_error:
            assert str(value_error) == "Detail is empty", str(value_error)

        try:
            # Bad Inner:
            washer = ApexWasher(name, detail, 0.0, outer, thickness, material, kind)
        except ValueError as value_error:
            assert str(value_error) == "Inner (=0.0) is not positive", str(value_error)

        try:
            # Bad Outer:
            ApexWasher(name, detail, inner, 0.0, thickness, material, kind)
        except ValueError as value_error:
            assert str(value_error) == "Outer (=0.0) is not positive", str(value_error)

        try:
            # Inner >= Outer:
            ApexWasher(name, detail, 10.0, 5.0, 0.0, material, kind)
        except ValueError as value_error:
            assert str(value_error) == "Inner (=10.0) >= Outer (=5.0)", str(value_error)

        try:
            # Bad Thickness:
            ApexWasher(name, detail, inner, outer, 0.0, material, kind)
        except ValueError as value_error:
            assert str(value_error) == "Thickness (=0.0) is not positive", str(value_error)

        try:
            # Bad Material:
            ApexWasher(name, detail, inner, outer, thickness, cast(ApexMaterial, 0), kind)
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'Material' is int which is not one of ['ApexMaterial']"), str(value_error)

        try:
            # Bad kind:
            ApexWasher(name, detail, inner, outer, thickness, material, "BOGUS")
        except ValueError as value_error:
            assert str(value_error) == (
                "Kind (='BOGUS') is not one of "
                "('PLAIN', 'INTERNAL_LOCK', 'EXTERNAL_LOCK', 'SPLIT_LOCK')"
            ), str(value_error)


# ApexFasten:
@dataclass(frozen=True)
class ApexFasten:
    """ApexFastner: The class of Fastener to use.

    Attributes:
    * Name (str): ApexFasten Name.
    * Profile (str): ApexFasten Profile.  Must be one of the ApexFasten constants --
      `ISO_COARSE`, `ISO_FINE`,  `UTS_COARSE`, `UTS_FINE`, and `UTS_EXTRA_FINE.
    * Size (str): Standard fastener size.  Must be one of the ApexFasten constants --
      `UTS_N1`, `UTS_N2`, `UTS_N3`, `UTS_N4`, `UTS_N5`, `UTS_N6`, `UTS_N8`, `UTS_N10`, `UTS_N12`,
      `UTS_F1_4`, `UTS_F5_16`, `UTS_F3_8`, `UTS_F7_16`, `UTS_F1_2`, `UTS_F9_16`, `UTS_F5_8`,
      `UTS_F3_4`, `UTS_F3_4`, `M1_6`, `M2`, `M2_5`, `M3`, `M3_5`, `M4`, `M5`, `M6`, `M8`, `M10`,
      `M12`, `M14`, `M16`, `M18,  `M20`, `M22`, `M24`, `M27`, `M30`, `M36`, `M42`, `M48`, `M56`,
      `M68.

    """

    Name: str  # ApexFasten Name
    Profile: str  # ApexFasten Profile
    Size: str  # ApexFasten Size
    Options: Tuple[ApexOption, ...]  # ApexFasten Options

    # Profile:
    ISO_COARSE = "ISO Metric Coarse"
    ISO_FINE = "ISO Metric FINE"
    UTS_COARSE = "UTS Coarse"
    UTS_FINE = "UTS Fine"
    UTS_EXTRA_FINE = "UTS Extra Fine"

    # Various standard sizes:
    UTS_N1 = "UTS #1"
    UTS_N2 = "UTS #2"
    UTS_N3 = "UTS #3"
    UTS_N4 = "UTS #4"
    UTS_N5 = "UTS #5"
    UTS_N6 = "UTS #6"
    UTS_N8 = "UTS #8"
    UTS_N10 = "UTS #10"
    UTS_N12 = "UTS #12"
    UTS_F1_4 = "UTS 1/4"
    UTS_F5_16 = "UTS 5/16"
    UTS_F3_8 = "UTS 3/8"
    UTS_F7_16 = "UTS 7/16"
    UTS_F1_2 = "UTS 1/2"
    UTS_F9_16 = "UTS 9/16"
    UTS_F5_8 = "UTS 5/8"
    UTS_F3_4 = "UTS 3/4"
    UTS_F3_4 = "UTS 1"
    M1_6 = "M1.60"
    M2 = "M2"
    M2_5 = "M2.50"
    M3 = "M3"
    M3_5 = "M3.50"
    M4 = "M4"
    M5 = "M5"
    M6 = "M6"
    M8 = "M8"
    M10 = "M10"
    M12 = "M12"
    M14 = "M14"
    M16 = "M16"
    M18 = "M18"
    M20 = "M20"
    M22 = "M22"
    M24 = "M24"
    M27 = "M27"
    M30 = "M30"
    M36 = "M36"
    M42 = "M42"
    M48 = "M48"
    M56 = "M56"
    M68 = "M68"

    # Direction:
    DIRECTION_LEFT = "Direction Left"
    DIRECTION_RIGHT = "Direction Right"

    # Fit:
    FIT_STANDARD = "Standard"  # Loose
    FIT_CLOSE = "Close"

    # SAE has a different system 2-8
    # Class (4=lower 7=higher) strength (G=external H=internal) thread?:
    CLASS_4G = "4G"
    CLASS_4H = "4H"
    CLASS_5G = "5G"
    CLASS_5H = "5H"
    CLASS_6G = "6G"
    CLASS_6H = "6H"
    CLASS_7G = "7G"
    CLASS_7H = "7H"

    # Depth:
    DEPTH_THROUGH = "Through"
    DEPTH_DIMENSION = "Dimensioned"

    # Hole Cut:
    CUT_NONE = "None"
    CUT_COUNTERBORE = "Counterbore"
    CUT_CHESEHEAD = "Cheesehead"
    CUT_COUNTERSINK = "Countersink"
    CUT_SOCKET_SCREW = "Socket Screw"
    CUT_CAP_SCREW = "CAP Screw"

    # Diameter:
    # Depth:
    # Countersink angle:

    # Drill Point:
    POINT_FLAT = "Flat"
    POINT_ANGLED = "Angled"

    # Misc:
    #  Tapered (angle)
    #  Reversed bool

    INIT_CHECKS = (
        ApexCheck("Name", (str,)),
        ApexCheck("Profile", (str,)),
        ApexCheck("Size", (str,)),
        ApexCheck("Options", (tuple,)),
    )
    PROFILES = (
        ISO_COARSE,
        ISO_FINE,
        UTS_COARSE,
        UTS_FINE,
        UTS_EXTRA_FINE,
    )
    SIZES = (
        UTS_N1, UTS_N2, UTS_N3, UTS_N4, UTS_N5, UTS_N6, UTS_N8, UTS_N10, UTS_N12,
        UTS_F1_4, UTS_F5_16, UTS_F3_8, UTS_F7_16, UTS_F1_2, UTS_F9_16, UTS_F5_8, UTS_F3_4, UTS_F3_4,
        M1_6, M2, M2_5, M3, M3_5, M4, M5, M6, M8, M10, M12, M14, M16, M18,
        M20, M22, M24, M27, M30, M36, M42, M48, M56, M68,
    )

    def __repr__(self) -> str:
        """Return a string representation of an ApexFasten."""
        return self.__str__()

    def __str__(self) -> str:
        """Return a string representation of an ApexFasten."""
        return f"ApexFasten('{self.Name}', '{self.Profile}', '{self.Size}'))"

    def __post_init__(self):
        """Verify that ApexFasten is properly initialized.

        Arguments:
        * Profile (str): Profile to use.  Select from the following predefined ApexFasten
          constants -- `PROFILE_CUSTOM`, `PROFILE_ISO_COARSE`, `PROFILE_ISO_FINE`,
          `PROFILE_UTS_COARSE`, `PROFILE_UTS_FINE`, `PROFILE_UTS_EXTRA_FINE`.  `PROFILE_CUSTOM`
          requires additional sizes to be specified -- `close_diameter`, `loose_diameter`,
          `thread_diameter`.
        * Size (str): Size to use. Select from the following predefined ApexFasten constants --
          `CUSTOM_SIZE`, `UTS_N1`, `UTS_N2`, `UTS_N3`, `UTS_N4`, `UTS_N5`, `UTS_N6`, `UTS_N8`,
          `UTS_N10`, `UTS_N12`, `UTS_F1_4`, `UTS_F5_16`, `UTS_F3_8`, `UTS_F7_16`, `UTS_F1_2`,
          `UTS_F9_16`, `UTS_F5_8`, `UTS_F3_4`, `UTS_F3_4`, `M1_6`, `M2`, `M2_5`, `M3`, `M3_5`,
          `M4`, `M5`, `M6`, `M8`, `M10`, `M12`, `M14`, `M16`, `M18`, `M20`, `M22`, `M24`, `M27`,
          `M30`, `M36`, `M42`, `M48`, `M56`, `M68`.
        """
        arguments = (self.Name, self.Profile, self.Size, self.Options)
        value_error: str = ApexCheck.check(arguments, ApexFasten.INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)
        if not self.Name:
            raise ValueError("Name is empty")
        if self.Profile not in ApexFasten.PROFILES:
            raise ValueError(f"'{self.Profile}' is not one of {ApexFasten.Profiles}")
        if self.Profile not in ApexFasten.SIZES:
            raise ValueError(f"'{self.Profile}' is not a valid size")

        # Ensure that Options is a tuple and only contains ApexOptions:
        if not isinstance(self.Options, tuple):
            raise ValueError("Options is not a tuple")
        option: ApexOption
        for option in self.Options:
            if not isinstance(option, ApexOption):
                raise ValueError(f"{option} is not an ApexOption")

    @staticmethod
    def _unit_tests() -> None:
        """Run ApexFasten unit tests."""
        name: str = "#4-40"
        profile: str = ApexFasten.UTS_FINE
        size: str = ApexFasten.UTS_N4
        fasten: ApexFasten = ApexFasten(name, profile, size, ())
        _ = fasten

        # Verify __repr__() works:
        pass


# ApexJoin:
class ApexJoin(object):
    """ApexJoin: Specifies a single fastener instance."""

    # ApexJoin.__init__():
    def __init__(self, fasten: ApexFasten, start: Vector, end: Vector, options: str = "") -> None:
        """Initialize a single ApexJoin."""
        pass

    @staticmethod
    def _unit_tests() -> None:
        """Run ApexJoint unit tests."""
        brass: ApexMaterial = ApexMaterial(("brass",), "orange")
        apex_head: ApexHead = ApexHead("PH", "Brass Philips Pan Head",
                                       brass, ApexHead.PAN_HEAD, ApexHead.PHILIPS_DRIVE)
        options: Tuple[ApexOption, ...] = (apex_head,)
        apex_fasten: ApexFasten = ApexFasten(
            "#4-40", ApexFasten.UTS_FINE, ApexFasten.UTS_N4, options)
        start: Vector = Vector(0, 0, 0)
        stop: Vector = Vector(1, 1, 1)
        apex_join: ApexJoin = ApexJoin(apex_fasten, start, stop, "")
        _ = apex_join


def _unit_tests() -> None:
    """Run unit tests."""
    ApexOption._unit_tests()
    ApexHead._unit_tests()
    # ApexFasten._unit_tests()
    ApexNut._unit_tests()
    ApexWasher._unit_tests()


if __name__ == "__main__":
    _unit_tests()
