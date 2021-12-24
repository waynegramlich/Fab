#!/usr/bin/env python3
"""Join: A package for managing fasteners in the ModFab system.

While the most common fasteners are screws and bolts, there are others like rivets, set screws,
cotter pins, etc.  This package centralizes all of the issues associated with fasteners
so that changing a fastener does not become a nightmare of having to individually find
each fastener and make manual changes to each one.  The change is made in once place and
it propagates to all associated fasteners.

The Join module deals with the following issues:
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

The basic class hierarchy is:

* ModFabJoiner: A profile for a set of related hardware for using a fastener.
* ModFabJoinerOption: A base class for the sub-classes immediately below:
  * ModFabHead: The fastener head definition along with counter sink/bore information.
  * ModFabWasher: washer that is attached on the fastener.
  * ModFabNut: A nut that threads onto the fastener.
* ModFabJoin: A specific instance of fastener that has a start and end point.

A ModFabJoiner basically lists a thread profile (i.e. #4-4, M3x0.5, etc), the driver head,
associated lock washers, regular washers, nuts, etc.  These are specified as a list
of ModFabJoinerOption's (i.e. ModFabHead, ModFabWasher, ModFabNut, etc.)

A ModFabJoin specifies a ModFabJoiner, a start point and an end point.  The first end point is
the specifies a point just under the screw/bolt head and any regular/lock washers just below
the head.  The end point is where any additional regular/lock washers and nuts go at the other
end of the fastener.

The Part module has three basic ModFabOperation's -- ModFabThread, ModFabClose, and ModFabLoose,
which vary the diameter of the Part Hole.  These operations take a ModFabJoin, verifies that
the fastener is perpendicular to the mount plane, and drills the correct diameter hole to
the correct depth.

Eventually, the system will create a BOM (Bill Of Materials) that lists all of the needed
hardware.

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

import os
import sys

assert sys.version_info.major == 3, "Python 3.x is not running"
assert sys.version_info.minor == 8, "Python 3.8 is not running"
sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])

from dataclasses import dataclass
from typing import cast, Tuple

from Utilities import ModFabCheck, ModFabMaterial
from FreeCAD import Vector  # type: ignore

#  https://github.com/shaise/FreeCAD_FastenersWB


# ModFabOption:
@dataclass(frozen=True)
class ModFabOption(object):
    """ModFabOption: Base class for ModFabFasten options (e.g. washers, nuts, etc...).

    Attributes:
    * *Name* (str): The option name.
    * *Detail* (str): More detailed information about the option.

    """

    Name: str  # ModFabOption name
    Detail: str  # ModFabOption description.

    POST_INIT_CHECKS = (
        ModFabCheck("Name", ("+", str)),
        ModFabCheck("Detail", ("+", str)),
    )

    def __post_init__(self) -> None:
        """Ensure values are reasonable."""
        arguments = (self.Name, self.Detail)
        value_error: str = ModFabCheck.check(arguments, ModFabOption.POST_INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)

    def __repr__(self) -> str:
        """Return String representation of ModFabOption."""
        return self.__str__()

    def __str__(self) -> str:
        """Return String representation of ModFabOption."""
        return f"ModFabOption('{self.Name}', '{self.Detail}')"

    @staticmethod
    def _unit_tests() -> None:
        """Run ModFabOption unit tests."""
        name: str = "name"
        detail: str = "detail"
        option: ModFabOption = ModFabOption(name, detail)
        assert option.Name == name
        assert option.Detail == detail
        assert f"{option}" == "ModFabOption('name', 'detail')", f"{option}"

        # Error tests:
        # Non string for Name.
        try:
            ModFabOption(cast(str, 1), detail)
        except ValueError as value_error:
            assert str(value_error) == "[0]: Argument 'Name' has no length", str(value_error)

        # Empty string for Name:
        try:
            ModFabOption("", detail)
        except ValueError as value_error:
            assert str(value_error) == "[0]: Argument 'Name' has no length", str(value_error)

        # Non string for Detail.
        try:
            ModFabOption(name, cast(str, 2))
        except ValueError as value_error:
            assert str(value_error) == "[1]: Argument 'Detail' has no length", str(value_error)

        # Empty string for Detail:
        try:
            ModFabOption(name, "")
        except ValueError as value_error:
            assert str(value_error) == "[1]: Argument 'Detail' has no length", str(value_error)


# ModFabHead:
@dataclass(frozen=True)
class ModFabHead(ModFabOption):
    """Represents the Head of the ModFabFastener.

    Attributes:
    * *Name* (str): The name for this head.
    * *Detail* (str): Short ModFabHead description.
    * *Material* (ModFabMaterial): The ModFabHead fastener material.
    * *Shape* (str): The ModFabHead shape.
    * *Drive* (str): The ModFabH drive .

    """

    Material: ModFabMaterial  # ModFabHead material
    Shape: str  # ModFabHead shape
    Drive: str  # ModFabHead drive

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
        ModFabCheck("Name", ("+", str,)),
        ModFabCheck("Detail", ("+", str,)),
        ModFabCheck("Material", (ModFabMaterial,)),
        ModFabCheck("Shape", (str,)),
        ModFabCheck("Drive", (str,)),
    )

    def __post_init__(self) -> None:
        """Verify ModFabHead."""
        arguments = (self.Name, self.Detail, self.Material, self.Shape, self.Drive)
        value_error: str = ModFabCheck.check(arguments, ModFabHead.INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)
        if self.Shape not in ModFabHead.HEADS:
            raise ValueError(f"Shape (='{self.Shape}') is not in {ModFabHead.HEADS}")
        if self.Drive not in ModFabHead.DRIVES:
            raise ValueError(f"Head (='{self.Drive}') is not in {ModFabHead.DRIVES}")

    def __repr__(self) -> str:
        """Return ModFabHead as a string."""
        return self.__str__()

    def __str__(self) -> str:
        """Return ModFabHead as a string."""
        return (f"ModFabHead('{self.Name}', '{self.Detail}', "
                f"{self.Material}, '{self.Shape}', {self.Drive})")

    @staticmethod
    def _unit_tests() -> None:
        """Run ModFabHead unit tests."""
        name: str = "PH"
        detail: str = "Brass Philips Pan Head"
        material: ModFabMaterial = ModFabMaterial(("Brass",), "orange")
        shape: str = ModFabHead.PAN_HEAD
        drive: str = ModFabHead.PHILIPS_DRIVE
        apex_head: ModFabHead = ModFabHead(name, detail, material, shape, drive)

        # Verify __repr__() and attributes work:
        assert f"{apex_head}" == (
            "ModFabHead('PH', 'Brass Philips Pan Head', ModFabMaterial(('Brass',), 'orange'), "
            "'Pan', Philips)"), f"{apex_head}"
        assert apex_head.__repr__() == (
            "ModFabHead('PH', 'Brass Philips Pan Head', ModFabMaterial(('Brass',), 'orange'), "
            "'Pan', Philips)"), f"{apex_head}"
        assert apex_head.Name == name, apex_head.Name
        assert apex_head.Material is material, apex_head.Material
        assert apex_head.Shape == shape, apex_head.Shape
        assert apex_head.Drive == drive, apex_head.Drive

        # Empty Name Test:
        try:
            ModFabHead("", detail, material, shape, drive)
            assert False
        except ValueError as value_error:
            assert str(value_error) == "[0]: Argument 'Name' has no length", str(value_error)

        # Bad Detail:
        try:
            ModFabHead(name, "", cast(ModFabMaterial, 0), shape, drive)
        except ValueError as value_error:
            assert str(value_error) == "[1]: Argument 'Detail' has no length", str(value_error)

        # Bad Material:
        try:
            ModFabHead(name, detail, cast(ModFabMaterial, 0), shape, drive)
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'Material' is int which is not one of ['ModFabMaterial']"
            ), str(value_error)

        # Bad Shape:
        try:
            ModFabHead(name, detail, material, "", drive)
            assert False
        except ValueError as value_error:
            assert str(value_error) == ("Shape (='') is not in ('Cheese', 'Fillister', "
                                        "'Flat', 'Hex', 'Oval', 'Pan', 'Round')"), str(value_error)

        # Bad Drive:
        try:
            ModFabHead(name, detail, material, shape, "")
        except ValueError as value_error:
            got: str = str(value_error)
            assert got == (
                "Head (='') is not in ('Carriage', 'Hex', 'Philips', 'Slot', 'Torx')"), got


# ModFabNut:
@dataclass(frozen=True)
class ModFabNut(ModFabOption):
    """ModFabNut: A class the represents a fastener nut.

    Attributes:
    * Name (str): Nut name.
    * Detail (str): More nut detail.
    * Sides (int): The number of nut sides (either 4 or 6.)
    * Width (float): The Nut width between 2 opposite faces.
    * Thickness (float): The nut thickness in millimeters.
    * Material (ModFabMaterial): The nut material

    """

    Sides: int  # The Nut sides (either, 4 or 6).
    Width: float  # The Nut width between 2 faces in millimeters.
    Thickness: float  # The Nut thickness in millimeters.
    Material: ModFabMaterial  # The Nut material.

    INIT_CHECKS = (
        ModFabCheck("Name", (str,)),
        ModFabCheck("Detail", (str,)),
        ModFabCheck("Sides", (int,)),
        ModFabCheck("Width", (float,)),
        ModFabCheck("Thickness", (float,)),
        ModFabCheck("Material", (ModFabMaterial,)),
    )

    def __post_init__(self) -> None:
        """Verify everything is reasonable."""
        arguments = (self.Name, self.Detail, self.Sides, self.Width, self.Thickness, self.Material)
        value_error: str = ModFabCheck.check(arguments, ModFabNut.INIT_CHECKS)
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
        """Return ModFabNut string representation."""
        return self.__str__()

    def __str__(self) -> str:
        """Return ModFabNut string representation."""
        return (f"ModFabNut('{self.Name}', '{self.Detail}', {self.Sides}, {self.Width}, "
                f"{self.Thickness}, {self.Material})")

    @staticmethod
    def _unit_tests() -> None:
        """Run ModFabNut unit tests."""
        # Create the ModFabNut:
        name: str = "M3Nut"
        detail: str = "Brass M3 Hex Nut"
        sides: int = 6
        width: float = 6.2
        thickness: float = 2.0
        material: ModFabMaterial = ModFabMaterial(("brass",), "orange")
        nut: ModFabNut = ModFabNut(name, detail, sides, width, thickness, material)

        # Verify that __repr__() and __str__() work.
        want: str = ("ModFabNut('M3Nut', 'Brass M3 Hex Nut', 6, 6.2, 2.0, "
                     "ModFabMaterial(('brass',), 'orange'))")
        assert f"{nut}" == want, f"{nut}"
        assert nut.__repr__() == want
        assert str(nut) == want

        # Verify attributes:
        assert nut.Name == name, nut.Name
        assert nut.Detail == detail, nut.Detail
        assert nut.Sides == sides, nut.Sides
        assert nut.Width == width, nut.Width
        assert nut.Thickness == thickness, nut.Thickness
        assert nut.Material == material, nut.Material

        # Verify __repr__() and __str__():
        nut_text: str = (
            f"ModFabNut('{name}', '{detail}', {sides}, {width}, {thickness}, {material})")
        assert f"{nut}" == nut_text, (f"{nut}", nut_text)

        # Do argument checking:
        try:
            # Empty name:
            ModFabNut("", detail, sides, width, thickness, material)
        except ValueError as value_error:
            assert str(value_error) == "Name is empty", str(value_error)

        try:
            # Empty detail:
            ModFabNut(name, "", sides, width, thickness, material)
        except ValueError as value_error:
            assert str(value_error) == "Detail is empty", str(value_error)

        try:  # Bad sides:
            ModFabNut(name, detail, 5, width, thickness, material)
        except ValueError as value_error:
            assert str(value_error) == "Sides (=5) is neither 4 nor 6", str(value_error)

        try:  # Bad width:
            ModFabNut(name, detail, sides, 0.0, thickness, material)
        except ValueError as value_error:
            assert str(value_error) == "Width (=0.0) is not positive", str(value_error)

        try:  # Bad thickness:
            ModFabNut(name, detail, sides, width, 0.0, material)
        except ValueError as value_error:
            assert str(value_error) == "Thickness (=0.0) is not positive", str(value_error)

        try:  # Bad Material:
            ModFabNut(name, detail, sides, width, thickness, cast(ModFabMaterial, 0))
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'Material' is int which is not one of ['ModFabMaterial']"
            ), str(value_error)


# ModFabWasher:
@dataclass(frozen=True)
class ModFabWasher(ModFabOption):
    """ModFabWahser: Represents a washer.

    Constants:
    * PLAIN: Plain washer.
    * INTERNAL_LOCK: Internal tooth lock washer.
    * EXTERNAL_LOCK: External tooth lock washer.
    * SPLIT_LOCK: Split ring lock washer.

    Attributes:
    * *Name* (str): The washer name.
    * *Detail* (str): More detail about the ModFabWasher.
    * *Inner* (float): The Inner diameter in millimeters.
    * *Outer* (float): The Outer diameter in millimeters.
    * *Thickness* (float): The thickness in millimeters.
    * *Material* (ModFabMaterial): The Material the washer is made out of.
    * *Kind* (str): The washer kind -- one of following ModFabWasher constants --
      `PLAIN`, `INTERNAL_LOCK`, `EXTERNAL_LOCK`, or `SPLIT_LOCK`.

    """

    Inner: float  # Inner diameter
    Outer: float  # Outer diameter
    Thickness: float  # Thickness
    Material: ModFabMaterial  # Material
    Kind: str  # Kind

    # Predefined constants for Kind.
    PLAIN = "PLAIN"
    INTERNAL_LOCK = "INTERNAL_LOCK"
    EXTERNAL_LOCK = "EXTERNAL_LOCK"
    SPLIT_LOCK = "SPLIT_LOCK"

    INIT_CHECKS = (
        ModFabCheck("Name", ("+", str)),
        ModFabCheck("Detail", ("+", str)),
        ModFabCheck("Inner", (float,)),
        ModFabCheck("Outer", (float,)),
        ModFabCheck("Thickness", (float,)),
        ModFabCheck("Material", (ModFabMaterial,)),
        ModFabCheck("Kind", ("+", str,)),
    )

    # ModFabWasher:
    def __post_init__(self):
        """Post process ModFabWasher looking for errors."""
        # Check the arguments and do any requested *tracing*:
        arguments = (self.Name, self.Detail, self.Inner, self.Outer, self.Thickness,
                     self.Material, self.Kind)
        value_error: str = ModFabCheck.check(arguments, ModFabWasher.INIT_CHECKS)
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
            ModFabWasher.PLAIN,
            ModFabWasher.INTERNAL_LOCK,
            ModFabWasher.EXTERNAL_LOCK,
            ModFabWasher.SPLIT_LOCK,
        )
        if self.Kind not in kinds:
            raise ValueError(f"Kind (='{self.Kind}') is not one of {kinds}")

    def __repr__(self) -> str:
        """Return string representation of ModFabWasher."""
        return self.__str__()

    def __str__(self) -> str:
        """Return string representation of ModFabWasher."""
        return (f"ModFabWasher('{self.Name}', '{self.Detail}', {self.Inner}, {self.Outer}, "
                f"{self.Thickness}, {self.Material}, '{self.Kind}')")

    @staticmethod
    def _unit_tests() -> None:
        """Perform ModFabWasher unit tests."""
        # Create the *washer*:
        name: str = "W6x.5"
        detail: str = "M3 Washer (ID=3.2 OD=6, Thick=.5)"
        inner: float = 3.2
        outer: float = 6.0
        thickness: float = 0.5
        material: ModFabMaterial = ModFabMaterial(("brass",), "orange")
        kind: str = ModFabWasher.PLAIN
        washer: ModFabWasher = ModFabWasher(name, detail, inner, outer, thickness, material, kind)

        # Ensure that the __str__() method works:
        washer_text: str = (f"ModFabWasher('{name}', '{detail}', "
                            f"{inner}, {outer}, {thickness}, {material}, '{kind}')")
        assert f"{washer}" == washer_text, (f"{washer}", washer_text)
        assert str(washer) == washer_text
        assert washer.__repr__() == washer_text

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
            ModFabWasher("", detail, inner, outer, thickness, material, kind)
        except ValueError as value_error:
            assert str(value_error) == "[0]: Argument 'Name' has no length", str(value_error)

        try:
            # Empty detail errora:
            ModFabWasher(name, "", inner, outer, thickness, material, kind)
        except ValueError as value_error:
            assert str(value_error) == "[1]: Argument 'Detail' has no length", str(value_error)

        try:
            # Bad Inner:
            washer = ModFabWasher(name, detail, 0.0, outer, thickness, material, kind)
        except ValueError as value_error:
            assert str(value_error) == "Inner (=0.0) is not positive", str(value_error)

        try:
            # Bad Outer:
            ModFabWasher(name, detail, inner, 0.0, thickness, material, kind)
        except ValueError as value_error:
            assert str(value_error) == "Outer (=0.0) is not positive", str(value_error)

        try:
            # Inner >= Outer:
            ModFabWasher(name, detail, 10.0, 5.0, 0.0, material, kind)
        except ValueError as value_error:
            assert str(value_error) == "Inner (=10.0) >= Outer (=5.0)", str(value_error)

        try:
            # Bad Thickness:
            ModFabWasher(name, detail, inner, outer, 0.0, material, kind)
        except ValueError as value_error:
            assert str(value_error) == "Thickness (=0.0) is not positive", str(value_error)

        try:
            # Bad Material:
            ModFabWasher(name, detail, inner, outer, thickness, cast(ModFabMaterial, 0), kind)
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'Material' is int which is not one of ['ModFabMaterial']"
            ), str(value_error)

        try:
            # Bad kind:
            ModFabWasher(name, detail, inner, outer, thickness, material, "BOGUS")
        except ValueError as value_error:
            assert str(value_error) == (
                "Kind (='BOGUS') is not one of "
                "('PLAIN', 'INTERNAL_LOCK', 'EXTERNAL_LOCK', 'SPLIT_LOCK')"
            ), str(value_error)


# ModFabFasten:
@dataclass(frozen=True)
class ModFabFasten:
    """ModFabFastner: The class of Fastener to use.

    Attributes:
    * Name (str): ModFabFasten Name.
    * Profile (str): ModFabFasten Profile.  Must be one of the ModFabFasten constants --
      `ISO_COARSE`, `ISO_FINE`,  `UTS_COARSE`, `UTS_FINE`, and `UTS_EXTRA_FINE.
    * Size (str): Standard fastener size.  Must be one of the ModFabFasten constants --
      `UTS_N1`, `UTS_N2`, `UTS_N3`, `UTS_N4`, `UTS_N5`, `UTS_N6`, `UTS_N8`, `UTS_N10`, `UTS_N12`,
      `UTS_F1_4`, `UTS_F5_16`, `UTS_F3_8`, `UTS_F7_16`, `UTS_F1_2`, `UTS_F9_16`, `UTS_F5_8`,
      `UTS_F3_4`, `UTS_F3_4`, `M1_6`, `M2`, `M2_5`, `M3`, `M3_5`, `M4`, `M5`, `M6`, `M8`, `M10`,
      `M12`, `M14`, `M16`, `M18,  `M20`, `M22`, `M24`, `M27`, `M30`, `M36`, `M42`, `M48`, `M56`,
      `M68.

    """

    Name: str  # ModFabFasten Name
    Profile: str  # ModFabFasten Profile
    Size: str  # ModFabFasten Size
    Options: Tuple[ModFabOption, ...]  # ModFabFasten Options

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
        ModFabCheck("Name", (str,)),
        ModFabCheck("Profile", (str,)),
        ModFabCheck("Size", (str,)),
        ModFabCheck("Options", ("T", ModFabOption)),
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
        """Return a string representation of an ModFabFasten."""
        return self.__str__()

    def __str__(self) -> str:
        """Return a string representation of an ModFabFasten."""
        return f"ModFabFasten('{self.Name}', '{self.Profile}', '{self.Size}')"

    POST_INIT_CHECKS = (
        ModFabCheck("Name", ("+", str)),
        ModFabCheck("Profile", ("+", str)),
        ModFabCheck("Size", ("+", str)),
        ModFabCheck("Options", ("T", ModFabOption)),
    )

    def __post_init__(self):
        """Verify that ModFabFasten is properly initialized.

        Arguments:
        * Profile (str): Profile to use.  Select from the following predefined ModFabFasten
          constants -- `PROFILE_CUSTOM`, `PROFILE_ISO_COARSE`, `PROFILE_ISO_FINE`,
          `PROFILE_UTS_COARSE`, `PROFILE_UTS_FINE`, `PROFILE_UTS_EXTRA_FINE`.  `PROFILE_CUSTOM`
          requires additional sizes to be specified -- `close_diameter`, `loose_diameter`,
          `thread_diameter`.
        * Size (str): Size to use. Select from the following predefined ModFabFasten constants --
          `CUSTOM_SIZE`, `UTS_N1`, `UTS_N2`, `UTS_N3`, `UTS_N4`, `UTS_N5`, `UTS_N6`, `UTS_N8`,
          `UTS_N10`, `UTS_N12`, `UTS_F1_4`, `UTS_F5_16`, `UTS_F3_8`, `UTS_F7_16`, `UTS_F1_2`,
          `UTS_F9_16`, `UTS_F5_8`, `UTS_F3_4`, `UTS_F3_4`, `M1_6`, `M2`, `M2_5`, `M3`, `M3_5`,
          `M4`, `M5`, `M6`, `M8`, `M10`, `M12`, `M14`, `M16`, `M18`, `M20`, `M22`, `M24`, `M27`,
          `M30`, `M36`, `M42`, `M48`, `M56`, `M68`.
        """
        arguments = (self.Name, self.Profile, self.Size, self.Options)
        value_error: str = ModFabCheck.check(arguments, ModFabFasten.INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)
        if self.Profile not in ModFabFasten.PROFILES:
            raise ValueError(f"'{self.Profile}' is not one of {ModFabFasten.PROFILES}")
        if self.Size not in ModFabFasten.SIZES:
            raise ValueError(f"'{self.Size}' is not a valid size")

        # Ensure that Options is a tuple and only contains ModFabOptions:
        if not isinstance(self.Options, tuple):
            raise ValueError("Options is not a tuple")
        option: ModFabOption
        for option in self.Options:
            if not isinstance(option, ModFabOption):
                raise ValueError(f"{option} is not an ModFabOption")

    @staticmethod
    def _unit_tests() -> None:
        """Run ModFabFasten unit tests."""
        name: str = "#4-40"
        profile: str = ModFabFasten.UTS_FINE
        size: str = ModFabFasten.UTS_N4
        fasten: ModFabFasten = ModFabFasten(name, profile, size, ())

        # Verify __repr__() works:
        assert f"{fasten}" == "ModFabFasten('#4-40', 'UTS Fine', 'UTS #4')", f"{fasten}"

        # Empty profile:
        try:
            ModFabFasten(name, "bad", size, ())
        except ValueError as value_error:
            got: str = str(value_error)
            want: str = ("'bad' is not one of ('ISO Metric Coarse', 'ISO Metric FINE', "
                         "'UTS Coarse', 'UTS Fine', 'UTS Extra Fine')")
            assert want == got, (want, got)


# ModFabJoin:
@dataclass(frozen=True)
class ModFabJoin(object):
    """ModFabJoin: Specifies a single fastener instance.

    Attributes:
    * Fasten (ModFabFasten): ModFabFasten object to use for basic dimensions.
    * Start (Vector): Start point for ModFabJoin.
    * End (Vector): End point for ModFabJoin.
    * Options (Tuple[ModFabOption]): The various options associated with the ModFabJoin.

    """

    Fasten: ModFabFasten  # Parent ModFabFasten
    Start: Vector  # Start point (near screw/bolt head)
    End: Vector  # End point (ene screw/bolt tip)
    Stack: str  # Stack of items that make up the entire ModFabJoin stack.

    POST_INIT_CHECKS = (
        ModFabCheck("Fasten", (ModFabFasten,)),
        ModFabCheck("Start", (Vector,)),
        ModFabCheck("End", (Vector,)),
        ModFabCheck("Stack", (str,)),
    )

    def __post_init__(self) -> None:
        """Initialize a single ModFabJoin."""
        arguments = (self.Fasten, self.Start, self.End, self.Stack)
        value_error: str = ModFabCheck.check(arguments, ModFabJoin.POST_INIT_CHECKS)
        if value_error:
            raise ValueError

    @staticmethod
    def _unit_tests() -> None:
        """Run ModFabJoint unit tests."""
        brass: ModFabMaterial = ModFabMaterial(("brass",), "orange")
        apex_head: ModFabHead = ModFabHead("PH", "Brass Philips Pan Head",
                                           brass, ModFabHead.PAN_HEAD, ModFabHead.PHILIPS_DRIVE)
        options: Tuple[ModFabOption, ...] = (apex_head,)
        apex_fasten: ModFabFasten = ModFabFasten(
            "#4-40", ModFabFasten.UTS_FINE, ModFabFasten.UTS_N4, options)
        start: Vector = Vector(0, 0, 0)
        stop: Vector = Vector(1, 1, 1)
        apex_join: ModFabJoin = ModFabJoin(apex_fasten, start, stop, "")
        _ = apex_join


def _unit_tests() -> None:
    """Run unit tests."""
    ModFabOption._unit_tests()
    ModFabHead._unit_tests()
    ModFabFasten._unit_tests()
    ModFabNut._unit_tests()
    ModFabWasher._unit_tests()
    ModFabJoin._unit_tests()


if __name__ == "__main__":
    _unit_tests()