#!/usr/bin/env python3
"""ApexFasten: A Package for managing fasteners in the Apex system.

While the most common fasteners are screws and bolts, there are others like rivets, set screws,
cotter pins, etc.  This package centralizes all of the issues associated with fasteners
so that changing a fastener does not become a nightmare of having to individually find
each fastener scattered throughout a design and make individual manual changes to each one.
The change is made in once place and it propagates to all associated fasteners.

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

The main classes are:

* ApexStack:
  A screw/bolt "factory" that contains the screw/bolt and associated washer, nuts, etc.
  The overall length is not specified.
* ApexStackBody:
  The specifications for the screw/bolt body.
  A list of available lengths is provided.
* ApexStackOption:
  This is the base class for the following sub-classes:
  * ApexWasher:
    A way to specify flat and lock washers.
  * ApexNut:
    A way to specify nuts.
  * ApexCounter:
    A countersink/counterbore specification.
* ApexScrew:
  This is an instance of an ApexStack that has an actual position and length.

Each ApexScrew can be applied to the contents of an ApexNode to properly place and
size holes in Parts.  The system properly determines where to place the hole on the
appropriate FreeCAD sketch.  If an ApexScrew is moved to a different position in 3D space,
the associated holes are automatically moved to the correct new locations.

There is a base call ApexClass called ApexOption that is used to represent

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
from ApexSketch import ApexElement
from FreeCAD import Vector  # type: ignore

#  https://github.com/shaise/FreeCAD_FastenersWB


# ApexStackOption:
@dataclass(frozen=True)
class ApexStackOption(object):
    """ApexStackOption: Base class for ApexFasten options (e.g. washers, nuts, etc...).

    Attributes:
    * *Name* (str): The option name.
    * *Detail* (str): More detailed information about the option.

    """

    Name: str  # ApexStackOption name
    Detail: str  # ApexStackOption description.

    POST_INIT_CHECKS = (
        ApexCheck("Name", ("+", str)),
        ApexCheck("Detail", ("+", str)),
    )

    def __post_init__(self) -> None:
        """Ensure values are reasonable."""
        arguments = (self.Name, self.Detail)
        value_error: str = ApexCheck.check(arguments, ApexStackOption.POST_INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)

    def __repr__(self) -> str:
        """Return String representation of ApexStackOption."""
        return self.__str__()

    def __str__(self) -> str:
        """Return String representation of ApexStackOption."""
        return f"ApexStackOption('{self.Name}', '{self.Detail}')"

    @staticmethod
    def _unit_tests() -> None:
        """Run ApexStackOption unit tests."""
        name: str = "name"
        detail: str = "detail"
        option: ApexStackOption = ApexStackOption(name, detail)

        # Verify attributes:
        assert option.Name == name
        assert option.Detail == detail

        # Verify __repr__() and __str__():
        want: str = "ApexStackOption('name', 'detail')"
        assert f"{option}" == want, f"{option}"
        assert str(option) == want, str(option)
        assert option.__repr__() == want, option.__repr__()

        # Error tests:
        # Non string for Name.
        try:
            ApexStackOption(cast(str, 1), detail)
        except ValueError as value_error:
            assert str(value_error) == "[0]: Argument 'Name' has no length", str(value_error)

        # Empty string for Name:
        try:
            ApexStackOption("", detail)
        except ValueError as value_error:
            assert str(value_error) == "[0]: Argument 'Name' has no length", str(value_error)

        # Non string for Detail.
        try:
            ApexStackOption(name, cast(str, 2))
        except ValueError as value_error:
            assert str(value_error) == "[1]: Argument 'Detail' has no length", str(value_error)

        # Empty string for Detail:
        try:
            ApexStackOption(name, "")
        except ValueError as value_error:
            assert str(value_error) == "[1]: Argument 'Detail' has no length", str(value_error)

# ApexCounter:
@dataclass(frozen=True)
class ApexCounter(ApexStackOption):
    """ApexCounter: A class the represents a fastener counter.

    Attributes:
    * Name (str): Counter name.
    * Detail (str): More counter detail.
    * Depth (float): Controls depth of countersink/counterbore.  (Default: 0.0)
      * Negative: Specifes exact depth in millimeters.
      * Zero: Use reasonable value (i.e. 110%).
      * Postive: Specifies depth as a percentage options height.
    * Diameter: Controls the diameter of countersink/counterbore. (Default:0.0)
      * Negtive: specifes diameter in millimeters.
      * Zero: Use reasonable value (i.e. 110%).
      * Positive: Specifes diameter as a percentatage of options diameter.

    """

    Depth: float = 0.0
    Diameter: float = 0.0

    INIT_CHECKS = (
        ApexCheck("Name", ("+", str,)),
        ApexCheck("Detail", ("+", str,)),
        ApexCheck("Depth", (float, int)),
        ApexCheck("Diameter", (float, int)),
    )

    def __post_init__(self) -> None:
        """Verify everything is reasonable."""
        arguments = (self.Name, self.Detail, self.Depth, self.Diameter)
        value_error: str = ApexCheck.check(arguments, ApexCounter.INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)

    def __repr__(self) -> str:
        """Return ApexCounter string representation."""
        return self.__str__()

    def __str__(self) -> str:
        """Return ApexCounter string representation."""
        return (f"ApexCounter('{self.Name}', '{self.Detail}', {self.Depth}, {self.Diameter})")

    @staticmethod
    def _unit_tests() -> None:
        """Run ApexCounter unit tests."""
        # Create the ApexCounter:
        name: str = "Counterbore"
        detail: str = "Cheesehead Counterbore"
        depth: float = 120.0
        diameter: float = 120.0
        counter: ApexCounter = ApexCounter(name, detail, depth, diameter)

        # Verify attributes:
        assert counter.Name == name, counter.Name
        assert counter.Detail == detail, counter.Detail
        assert counter.Depth == depth, counter.Depth
        assert counter.Diameter == diameter, counter.Diameter

        # Verify that __repr__() and __str__() work.
        want: str = ("ApexCounter('Counterbore', 'Cheesehead Counterbore', 120.0, 120.0)")
        assert f"{counter}" == want, f"{counter}"
        assert counter.__repr__() == want
        assert str(counter) == want

        # Do argument checking:
        try:
            # Empty Name:
            ApexCounter("", detail, depth, diameter)
            assert False
        except ValueError as value_error:
            assert str(value_error) == "[0]: Argument 'Name' has no length", str(value_error)

        # Empty Detail:
        try:
            ApexCounter(name, "", depth, diameter)
            assert False
        except ValueError as value_error:
            assert str(value_error) == "[1]: Argument 'Detail' has no length", str(value_error)

        # Bad Depth:
        try:
            ApexCounter(name, detail, cast(float, "BAD_DIAMETER"), diameter)
            assert False
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'Depth' is str which is not one of ['float', 'int']"), str(value_error)

        # Bad Diameter:
        try:
            ApexCounter(name, detail, depth, cast(float, "BAD_DIAMETER"))
            assert False
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'Diameter' is str which is not one of ['float', 'int']"), str(value_error)


# ApexNut:
@dataclass(frozen=True)
class ApexNut(ApexStackOption):
    """ApexNut: A class the represents a fastener nut.

    Attributes:
    * Name (str): Nut name.
    * Detail (str): More nut detail.
    * Material (ApexMaterial): The nut material
    * Sides (int): The number of nut sides (either 4 or 6.)
    * Width (float): The Nut width between 2 opposite faces.
    * Thickness (float): The nut thickness in millimeters.

    """

    Material: ApexMaterial  # The Nut material.
    Sides: int  # The Nut sides (either, 4 or 6).
    Width: float  # The Nut width between 2 faces in millimeters.
    Thickness: float  # The Nut thickness in millimeters.

    INIT_CHECKS = (
        ApexCheck("Name", ("+", str,)),
        ApexCheck("Detail", ("+", str,)),
        ApexCheck("Material", (ApexMaterial,)),
        ApexCheck("Sides", (int,)),
        ApexCheck("Width", (float,)),
        ApexCheck("Thickness", (float,)),
    )

    def __post_init__(self) -> None:
        """Verify everything is reasonable."""
        arguments = (self.Name, self.Detail, self.Material, self.Sides, self.Width, self.Thickness)
        value_error: str = ApexCheck.check(arguments, ApexNut.INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)
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
        nut: ApexNut = ApexNut(name, detail, material, sides, width, thickness)

        # Verify that __repr__() and __str__() work.
        want: str = ("ApexNut('M3Nut', 'Brass M3 Hex Nut', 6, 6.2, 2.0, "
                     "ApexMaterial(('brass',), 'orange'))")
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
        nut_text: str = f"ApexNut('{name}', '{detail}', {sides}, {width}, {thickness}, {material})"
        assert f"{nut}" == nut_text, (f"{nut}", nut_text)

        # Do argument checking:
        try:
            # Empty Name:
            ApexNut("", detail, material, sides, width, thickness)
        except ValueError as value_error:
            assert str(value_error) == "[0]: Argument 'Name' has no length", str(value_error)

        try:
            # Empty Detail:
            ApexNut(name, "", material, sides, width, thickness)
        except ValueError as value_error:
            assert str(value_error) == "[1]: Argument 'Detail' has no length", str(value_error)

        try:  # Bad Material:
            ApexNut(name, detail, cast(ApexMaterial, 0), sides, width, thickness)
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'Material' is int which is not one of ['ApexMaterial']"), str(value_error)

        try:  # Bad Sides:
            ApexNut(name, detail, material, 5, width, thickness)
        except ValueError as value_error:
            assert str(value_error) == "Sides (=5) is neither 4 nor 6", str(value_error)

        try:  # Bad Width:
            ApexNut(name, detail, material, sides, 0.0, thickness)
        except ValueError as value_error:
            assert str(value_error) == "Width (=0.0) is not positive", str(value_error)

        try:  # Bad Thickness:
            ApexNut(name, detail, material, sides, width, 0.0)
        except ValueError as value_error:
            assert str(value_error) == "Thickness (=0.0) is not positive", str(value_error)


# ApexWasher:
@dataclass(frozen=True)
class ApexWasher(ApexStackOption):
    """ApexWahser: Represents a washer.

    Constants:
    * PLAIN: Plain washer.
    * INTERNAL_LOCK: Internal tooth lock washer.
    * EXTERNAL_LOCK: External tooth lock washer.
    * SPLIT_LOCK: Split ring lock washer.

    Attributes:
    * *Name* (str): The washer name.
    * *Detail* (str): More detail about the ApexWasher.
    * *Material* (ApexMaterial): The Material the washer is made out of.
    * *Inner* (float): The Inner diameter in millimeters.
    * *Outer* (float): The Outer diameter in millimeters.
    * *Thickness* (float): The thickness in millimeters.
    * *Kind* (str): The washer kind -- one of following ApexWasher constants --
      `PLAIN`, `INTERNAL_LOCK`, `EXTERNAL_LOCK`, or `SPLIT_LOCK`.

    """

    Material: ApexMaterial  # Material
    Inner: float
    Outer: float
    Thickness: float  # Thickness
    Kind: str  # Kind

    # Predefined constants for Kind.
    PLAIN = "PLAIN"
    INTERNAL_LOCK = "INTERNAL_LOCK"
    EXTERNAL_LOCK = "EXTERNAL_LOCK"
    SPLIT_LOCK = "SPLIT_LOCK"

    INIT_CHECKS = (
        ApexCheck("Name", ("+", str)),
        ApexCheck("Detail", ("+", str)),
        ApexCheck("Material", (ApexMaterial,)),
        ApexCheck("Inner", (float,)),
        ApexCheck("Outer", (float,)),
        ApexCheck("Thickness", (float,)),
        ApexCheck("Kind", ("+", str,)),
    )

    # ApexWasher:
    def __post_init__(self):
        """Post process ApexWasher looking for errors."""
        # Check the arguments and do any requested *tracing*:
        arguments = (self.Name, self.Detail, self.Material,
                     self.Inner, self.Outer, self.Thickness, self.Kind)
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
        washer: ApexWasher = ApexWasher(name, detail, material, inner, outer, thickness, kind)

        # Ensure that the __str__() method works:
        washer_text: str = (f"ApexWasher('{name}', '{detail}', "
                            f"{inner}, {outer}, {thickness}, {material}, '{kind}')")
        assert f"{washer}" == washer_text, (f"{washer}", washer_text)
        assert str(washer) == washer_text
        assert washer.__repr__() == washer_text

        # Access all of the attributes:
        assert washer.Name == name, washer.Name
        assert washer.Detail == detail, washer.Detail
        assert washer.Material is material, washer.Material
        assert washer.Inner == inner, washer.Inner
        assert washer.Outer == outer, washer.Outer
        assert washer.Thickness == thickness, washer.Thickness
        assert washer.Kind == kind, washer.Kind

        # Do argument checks:
        try:
            # Empty Name error:
            ApexWasher("", detail, material, inner, outer, thickness, kind)
        except ValueError as value_error:
            assert str(value_error) == "[0]: Argument 'Name' has no length", str(value_error)

        try:
            # Empty Detail error:
            ApexWasher(name, "", material, inner, outer, thickness, kind)
        except ValueError as value_error:
            assert str(value_error) == "[1]: Argument 'Detail' has no length", str(value_error)

        try:
            # Bad Material
            washer = ApexWasher(name, detail, cast(ApexMaterial, 0), 0.0, outer, thickness, kind)
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'Material' is int which is not one of ['ApexMaterial']"), str(value_error)

        try:
            # Bad Inner:
            ApexWasher(name, detail, material, 0.0, outer, thickness, kind)
        except ValueError as value_error:
            assert str(value_error) == "Inner (=0.0) is not positive", str(value_error)

        try:
            # Inner >= Outer:
            ApexWasher(name, detail, material, 10.0, 5.0, 0.0, kind)
        except ValueError as value_error:
            assert str(value_error) == "Inner (=10.0) >= Outer (=5.0)", str(value_error)

        try:
            # Bad Outer:
            ApexWasher(name, detail, material, inner, 0.0, thickness, kind)
        except ValueError as value_error:
            assert str(value_error) == "Outer (=0.0) is not positive", str(value_error)

        try:
            # Bad Thickness:
            ApexWasher(name, detail, material, inner, outer, 0.0, kind)
        except ValueError as value_error:
            assert str(value_error) == "Thickness (=0.0) is not positive", str(value_error)

        try:
            # Bad kind:
            ApexWasher(name, detail, material, inner, outer, thickness, "BOGUS")
        except ValueError as value_error:
            assert str(value_error) == (
                "Kind (='BOGUS') is not one of "
                "('PLAIN', 'INTERNAL_LOCK', 'EXTERNAL_LOCK', 'SPLIT_LOCK')"
            ), str(value_error)


# ApexStackBody:
@dataclass(frozen=True)
class ApexStackBody:
    """ApexFastner: The class of Fastener to use.

    Attributes:
    * Name (str): ApexStack Name.
    * Detail (str): A more detailed description of the ApexStack.
    * Pitch (str): ApexStack Profile.  Must be one of the ApexStack constants --
      `ISO_COARSE`, `ISO_FINE`,  `UTS_COARSE`, `UTS_FINE`, and `UTS_EXTRA_FINE.
    * Size (str): Standard fastener size.  Must be one of the ApexStack constants --
      `UTS_N1`, `UTS_N2`, `UTS_N3`, `UTS_N4`, `UTS_N5`, `UTS_N6`, `UTS_N8`, `UTS_N10`, `UTS_N12`,
      `UTS_F1_4`, `UTS_F5_16`, `UTS_F3_8`, `UTS_F7_16`, `UTS_F1_2`, `UTS_F9_16`, `UTS_F5_8`,
      `UTS_F3_4`, `UTS_F3_4`, `M1_6`, `M2`, `M2_5`, `M3`, `M3_5`, `M4`, `M5`, `M6`, `M8`, `M10`,
      `M12`, `M14`, `M16`, `M18,  `M20`, `M22`, `M24`, `M27`, `M30`, `M36`, `M42`, `M48`, `M56`,
      `M68.
    * Material (ApexMaterial): The material that the primary fastener is made out of.
    * Head (str): The screw head shape (e.g. FLAT, OVAL, ...)
    * Drive (str): The screw drive (e.g. PHILIPS, SLOT, ...)

    """

    Name: str  # Short name to use.
    Detail: str  # Longer more detailed description
    Pitch: str  # The metric/imperial Pitch profile to use (e.g. ISO_FINE, UTS_FINE, ..)
    Size: str  # The metric screw diameter (e.g. UTS_N4, M3, ...)
    Material: ApexMaterial  # The screw material (e.g. brass, stainless-steel, ...)
    Head: str  # The screw head shape (e.g. FLAT, OVAL, ...)
    Drive: str  # Apex drive (e.g. PHILIPS, SLOT, ...)

    # Valid values for Pitch:
    ISO_COARSE = "ISO Metric Coarse"
    ISO_FINE = "ISO Metric FINE"
    UTS_COARSE = "UTS Coarse"
    UTS_FINE = "UTS Fine"
    UTS_EXTRA_FINE = "UTS Extra Fine"

    # Valid Values for Size:
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

    # Screw Heads:
    CARRIAGE = "Carriage Bolt"
    CHEESE = "Cheese"
    FILLISTER = "Fillister"
    FLAT = "Flat"
    HEX_BOLT = "Hex Bolt"  # For a Bolt
    OVAL = "Oval"
    PAN = "Pan"
    ROUND = "Round"

    # Screw Drives:
    NO_DRIVE = "No Drive"  # Carriage Bolts do not get driven
    HEX = "Hex"
    PHILLIPS = "Phillips"
    SLOT = "Slot"
    TORX = "Torx"

    HEADS = (CARRIAGE, CHEESE, FILLISTER, FLAT, HEX_BOLT, OVAL, PAN, ROUND)
    DRIVES = (NO_DRIVE, HEX, PHILLIPS, SLOT, TORX)

    # Old stuff
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

    PITCHES = (
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

    POST_INIT_CHECKS = (
        ApexCheck("Name", ("+", str,)),
        ApexCheck("Detail", ("+", str,)),
        ApexCheck("Pitch", (str,)),
        ApexCheck("Size", (str,)),
        ApexCheck("Material", (ApexMaterial,)),
        ApexCheck("Head", ("+", str)),
        ApexCheck("Drive", ("+", str)),
    )

    # ApexStackBody.__post_init__():
    def __post_init__(self):
        """Verify that ApexStack is properly initialized."""
        arguments = (self.Name, self.Detail,
                     self.Pitch, self.Size, self.Material, self.Head, self.Drive)
        value_error: str = ApexCheck.check(arguments, ApexStackBody.POST_INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)
        if self.Pitch not in ApexStackBody.PITCHES:
            raise ValueError(f"'{self.Pitch}' is not one of {ApexStackBody.PITCHES}")
        if self.Size not in ApexStackBody.SIZES:
            raise ValueError(f"'{self.Size}' is not one of {ApexStackBody.SIZES}")
        if self.Head not in ApexStackBody.HEADS:
            raise ValueError(f"'{self.Head}' is not one of {ApexStackBody.HEADS}")
        if self.Drive not in ApexStackBody.DRIVES:
            raise ValueError(f"'{self.Drive}' is not one of {ApexStackBody.DRIVES}")

    # ApexStackBody.__repr__():
    def __repr__(self) -> str:
        """Return string representation of ApexStack."""
        return self.__str__()

    # ApexStackBody.__str__():
    def __str__(self) -> str:
        """Return string representation of ApexStack."""
        return (
            f"ApexStack('{self.Name}', '{self.Detail}', '{self.Pitch}', '{self.Size}', "
            f"{self.Material}, '{self.Head}', '{self.Drive}')"
        )

    # ApexStackBody._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Run ApexStackBody unit tests."""
        # Create *screw_body*:
        name: str = "#4-40 FH"
        detail: str = "Brass #4-40 FH Slotted"
        pitch: str = ApexStackBody.UTS_FINE
        size: str = ApexStackBody.UTS_N4
        material: ApexMaterial = ApexMaterial(("brass",), "orange")
        head: str = ApexStackBody.FLAT
        drive: str = ApexStackBody.PHILLIPS
        screw_body: ApexStackBody = ApexStackBody(
            name, detail, pitch, size, material, head, drive)

        # Verify attributes:
        assert screw_body.Name == name, screw_body.Name
        assert screw_body.Detail == detail, screw_body.Detail
        assert screw_body.Pitch == pitch, screw_body.Pitch
        assert screw_body.Size == size, screw_body.Size
        assert screw_body.Material is material, screw_body.Material
        assert screw_body.Head == head, screw_body.Head
        assert screw_body.Drive == drive, screw_body.Drive

        # Verify __str__ and __repr__() works:
        want: str = ("ApexStack('#4-40 FH', 'Brass #4-40 FH Slotted', 'UTS Fine', 'UTS #4', "
                     "ApexMaterial(('brass',), 'orange'), 'Flat', 'Phillips')")
        got: str = f"{screw_body}"
        assert want == got, (want, got)
        got = screw_body.__repr__()
        assert want == got, (want, got)
        got = screw_body.__str__()
        assert want == got, (want, got)

        # Empty Name:
        try:
            ApexStackBody("", detail, pitch, size, material, head, drive)
        except ValueError as value_error:
            assert str(value_error) == "[0]: Argument 'Name' has no length", str(value_error)

        # Empty Detail:
        try:
            ApexStackBody(name, "", pitch, size, material, head, drive)
        except ValueError as value_error:
            assert str(value_error) == "[1]: Argument 'Detail' has no length", str(value_error)

        # Bad Pitch:
        try:
            ApexStackBody(name, detail, "BAD_PITCH", size, material, head, drive)
        except ValueError as value_error:
            assert str(value_error) == (
                "'BAD_PITCH' is not one of ('ISO Metric Coarse', 'ISO Metric FINE', "
                "'UTS Coarse', 'UTS Fine', 'UTS Extra Fine')"), str(value_error)

        # Bad Size:
        try:
            ApexStackBody(name, detail, pitch, "BAD_SIZE", material, head, drive)
        except ValueError as value_error:
            assert str(value_error) == (
                "'BAD_SIZE' is not one of ('UTS #1', 'UTS #2', 'UTS #3', 'UTS #4', 'UTS #5', "
                "'UTS #6', 'UTS #8', 'UTS #10', 'UTS #12', 'UTS 1/4', 'UTS 5/16', 'UTS 3/8', "
                "'UTS 7/16', 'UTS 1/2', 'UTS 9/16', 'UTS 5/8', 'UTS 1', 'UTS 1', 'M1.60', "
                "'M2', 'M2.50', 'M3', 'M3.50', 'M4', 'M5', 'M6', 'M8', 'M10', 'M12', 'M14', "
                "'M16', 'M18', 'M20', 'M22', 'M24', 'M27', 'M30', 'M36', 'M42', 'M48', 'M56', "
                "'M68')"), str(value_error)

        # Bad Material:
        try:
            ApexStackBody(name, detail, pitch, size, cast(ApexMaterial, 0), head, drive)
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'Material' is int which is not one of ['ApexMaterial']"), str(value_error)

        # Bad Head:
        try:
            ApexStackBody(name, detail, pitch, size, material, "BAD_HEAD", drive)
        except ValueError as value_error:
            assert str(value_error) == (
                "'BAD_HEAD' is not one of ('Carriage Bolt', 'Cheese', 'Fillister', "
                "'Flat', 'Hex Bolt', 'Oval', 'Pan', 'Round')"), str(value_error)

        # Bad Drive:
        try:
            ApexStackBody(name, detail, pitch, size, material, head, "BAD_DRIVE")
            assert False
        except ValueError as value_error:
            assert str(value_error) == ("'BAD_DRIVE' is not one of ('No Drive', 'Hex', "
                                        "'Phillips', 'Slot', 'Torx')"), str(value_error)


# ApexStack:
@dataclass(frozen=True)
class ApexStack:
    """ApexStack: A class consisting of an ApexStackBody and associated ApexStackOptions.

    Attributes:
    * Name (str): The name of the ApexStack.
    * Detail (str): A more detailed description of the ApexStack.
    * StackBody (ApexStackBody): The basic screw/bolt to use.
    * HeadOptions: (Tuple[ApexStackOption, ...]): Additional washers, etc mounted at the head.
    * TailOptions: (Tuple[ApexStackOption, ...]): Additional washers, etc mounted at the tail.

    """

    Name: str
    Detail: str
    StackBody: ApexStackBody
    HeadOptions: Tuple[ApexStackOption, ...]
    TailOptions: Tuple[ApexStackOption, ...]

    POST_INIT_CHECKS = (
        ApexCheck("Name", ("+", str)),
        ApexCheck("Detail", ("+", str)),
        ApexCheck("StackBody", (ApexStackBody,)),
        ApexCheck("HeadOptions", ("T", ApexStackOption)),
        ApexCheck("TailOptions", ("T", ApexStackOption)),
    )

    # ApexStack.__post_init__():
    def __post_init__(self) -> None:
        """Verify the ApexStack values."""
        arguments = (self.Name, self.Detail, self.StackBody, self.HeadOptions, self.TailOptions)
        value_error: str = ApexCheck.check(arguments, ApexStack.POST_INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)

    # ApexStack.__repr__():
    def __repr__(self) -> str:
        """Return ApexStack as a string."""
        return self.__str__()

    # ApexStack.__str__():
    def __str__(self) -> str:
        """Return ApexStack as a string."""
        return (f"ApexStack('{self.Name}', '{self.Detail}', '{self.StackBody}' "
                f"{self.HeadOptions}, {self.TailOptions})")

    # ApexStack._unit_tests():
    @classmethod
    def _unit_tests(cls) -> None:
        """Run unit tests for ApexStack."""
        # Create a *stack_body*, *washer*, and *nut*:
        brass: ApexMaterial = ApexMaterial(("brass",), "orange")
        stack_body: ApexStackBody = ApexStackBody(
            "#4-40FH", "#4-40 Flat Head Philips Brass",
            ApexStackBody.UTS_FINE, ApexStackBody.UTS_N4, brass,
            ApexStackBody.FLAT, ApexStackBody.PHILLIPS)
        washer: ApexWasher = ApexWasher(
            "Washer", "Flat Washer", brass, 3.0, 6.0, 1.5, ApexWasher.PLAIN)
        nut: ApexNut = ApexNut("Nut", "Hex Nut", brass, 6, 6.0, 2.0)

        # Build *stack*:
        name: str = "name"
        detail: str = "detail"
        head_options: Tuple[ApexStackOption, ...] = (washer,)
        tail_options: Tuple[ApexStackOption, ...] = (nut,)
        stack: ApexStack = ApexStack(name, detail, stack_body, head_options, tail_options)

        # Verify attributes:
        assert stack.Name == name, stack.Name
        assert stack.Detail == detail, stack.Detail
        assert stack.StackBody is stack_body, stack.StackBody
        assert stack.HeadOptions is head_options, stack.HeadOptions
        assert stack.TailOptions is tail_options, stack.TailOptions

        # Verify __str__() and __repr__():
        want: str = (
            "ApexStack('name', 'detail', "
            "'ApexStack('#4-40FH', '#4-40 Flat Head Philips Brass', 'UTS Fine', 'UTS #4', "
            "ApexMaterial(('brass',), 'orange'), 'Flat', 'Phillips')' "
            "(ApexWasher('Washer', 'Flat Washer', 3.0, 6.0, 1.5, "
            "ApexMaterial(('brass',), 'orange'), 'PLAIN'),), "
            "(ApexNut('Nut', 'Hex Nut', 6, 6.0, 2.0, ApexMaterial(('brass',), 'orange')),))")
        assert f"{stack}" == want, f"{stack}"
        assert str(stack) == want, str(stack)
        assert stack.__repr__() == want, stack.__repr__()

        # Bad Name:
        try:
            ApexStack("", detail, stack_body, head_options, tail_options)
        except ValueError as value_error:
            assert str(value_error) == "[0]: Argument 'Name' has no length", str(value_error)

        # Bad Detail:
        try:
            ApexStack(name, "", stack_body, head_options, tail_options)
        except ValueError as value_error:
            assert str(value_error) == "[1]: Argument 'Detail' has no length", str(value_error)

        # Bad StackBody:
        try:
            ApexStack(name, detail, cast(ApexStackBody, 0), head_options, tail_options)
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'StackBody' is int which is not one of ['ApexStackBody']"
            ), str(value_error)

        # Bad HeadOptions:
        try:
            ApexStack(name, detail, stack_body, (cast(ApexStackOption, "BAD_HEAD"), ), tail_options)
        except ValueError as value_error:
            assert str(value_error) == (
                "[0]: BAD_HEAD (str) is not of type ['ApexStackOption']"), str(value_error)

        # Bad TailOptions:
        try:
            ApexStack(name, detail, stack_body, head_options, (cast(ApexStackOption, "BAD_TAIL"), ))
        except ValueError as value_error:
            assert str(value_error) == (
                "[0]: BAD_TAIL (str) is not of type ['ApexStackOption']"), str(value_error)


# ApexScrew:
@dataclass(frozen=True)
class ApexScrew(object):
    """ApexScrew: Specifies a single fastener instance.

    Attributes:
    * Stack (ApexStack): ApexStack object to use for basic dimensions.
    * Start (Vector): Start point for ApexJoin.
    * End (Vector): End point for ApexJoin.

    """

    Stack: ApexStack  # Stack of items that make up the entire ApexScrew.
    Start: Vector  # Start point (near screw/bolt head)
    End: Vector  # End point (ene screw/bolt tip)

    POST_INIT_CHECKS = (
        ApexCheck("Stack", (ApexStack,)),
        ApexCheck("Start", (Vector,)),
        ApexCheck("End", (Vector,)),
    )

    # ApexScrew.__post_init__():
    def __post_init__(self) -> None:
        """Initialize ApexScrew."""
        arguments = (self.Stack, self.Start, self.End)
        value_error: str = ApexCheck.check(arguments, ApexScrew.POST_INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)

    def element(self) -> ApexElement:
        """Return the ApexElmenent for ApexScrew."""
        assert False

    # ApexScrew._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Run ApexJoint unit tests."""
        # Create the *screw*:
        brass: ApexMaterial = ApexMaterial(("brass",), "orange")
        stack_body: ApexStackBody = ApexStackBody(
            "#4-40 PH", "Brass #4-40 Pan Head Phillips",
            ApexStackBody.UTS_FINE, ApexStackBody.UTS_N4,
            brass, ApexStackBody.PAN, ApexStackBody.PHILLIPS)
        stack: ApexStack = ApexStack("#4-40", "Brass #4-40", stack_body, (), ())
        start: Vector = Vector(0.0, 0.0, 1.0)
        end: Vector = Vector(0.0, 0.0, 0.0)
        screw: ApexScrew = ApexScrew(stack, start, end)

        # Verify attributes:
        assert screw.Stack is stack, screw.Stack
        assert screw.Start is start, screw.Start
        assert screw.End is end, screw.End

        # Bad Stack:
        try:
            ApexScrew(cast(ApexStack, 0), start, end)
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'Stack' is int which is not one of ['ApexStack']"), str(value_error)

        # Bad Start:
        try:
            ApexScrew(stack, cast(Vector, 0), end)
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'Start' is int which is not one of ['Vector']"), str(value_error)

        # Bad End:
        try:
            ApexScrew(stack, start, cast(Vector, 0))
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'End' is int which is not one of ['Vector']"), str(value_error)


def _unit_tests() -> None:
    """Run unit tests."""
    ApexStackOption._unit_tests()
    ApexCounter._unit_tests()
    ApexNut._unit_tests()
    ApexWasher._unit_tests()
    ApexStackBody._unit_tests()
    ApexStack._unit_tests()
    ApexScrew._unit_tests()


if __name__ == "__main__":
    _unit_tests()
