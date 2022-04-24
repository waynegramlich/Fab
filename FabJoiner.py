#!/usr/bin/env python3
"""FabJoiner: Fab fastener management system.

While the most common fasteners are screws and bolts, there are others like rivets, set screws,
cotter pins, etc.  This package centralizes all of the issues associated with fasteners
so that changing a fastener does not become a nightmare of having to individually find
each fastener and make manual changes to each one.  The change is made in once place and
it propagates to all locations where the fastener is used.

The FabJoiner module deals with the following issues:
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
  line to connect them all.  (Not even remotely started yet.)
* Fastener WorkBench:
  The FreeCAD Fasteners workbench is used wherever possible.  (This may not happen.)

The basic class hierarchy is:

* FabFasten: A profile for a set of related hardware for using a fastener.
* FabOption: A base class for the sub-classes immediately below:
  * FabHead: The fastener head definition along with counter sink/bore information.
  * FabWasher: washer that is attached on the fastener.
  * FabNut: A nut that threads onto the fastener.
* FabJoin: A specific instance of fastener that has a start and end point.

I addition the "public" classes listed immediately above.  There are a number of "private" classes
of the form `Fab_` that are used to implement everything.  The interfaces to the classes are
not stable and can be changed at will by the developers; thus, they should not be depended upon.

A FabFasten basically lists a thread profile (i.e. #4-4, M3x0.5, etc), the driver head,
associated lock washers, regular washers, nuts, etc.  These are specified as a list
of FabOption's (i.e. FabHead, FabWasher, FabNut, etc.)

A FabJoin specifies a FabJoiner, a start point and an end point.  The first end point is
the specifies a point just under the screw/bolt head and any regular/lock washers just below
the head.  The end point is where any additional regular/lock washers and nuts go at the other
end of the fastener.

The Part module has three basic FabOperation's -- FabThread, FabClose, and FabLoose,
which vary the diameter of the Part Hole.  These operations take a FabJoin, verifies that
the fastener is perpendicular to the mount plane, and drills the correct diameter hole to
the correct depth.

Eventually, the system will create a BOM (Bill Of Materials) that lists all of the needed
hardware.

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

from dataclasses import dataclass, field
from typeguard import check_type
from typing import Any, ClassVar, Dict, List, Tuple, Union

from cadquery import Vector  # type: ignore

from FabUtilities import FabMaterial


# Fab_MDrillTap:
@dataclass
class Fab_MDrillTap(object):
    """Fab_MDrillTap: Metric drill/tap information.

    Attributes:
    * *MName* (str): The Metric major diameter name starting with "M" (e.g. M1)
    * *MPitch* (float): The threads per millimeter.
    * *M75* (float): The preferred metric drill for 75% thread.
    * *I75* (str): The preferred imperial drill for 75% thread.
    * *M50* (float): The preferred metric drill for 50% thread.
    * *I50* (str): The preferred imperial drill for 70% thread.
    * *MClose* (float): The preferred metric drill for a close fit.
    * *IClose* (str): The preferred imperial drill for a close fit.
    * *MStandard* (float): The preferred metric drill for a standard fit.
    * *IStandard* (str): The preferred imperial drill for a standard fit.

    Constructor:
    * Fab_MDrillTap(MName, MPitch, M75, M50, MClose, IClose, MStandard, IStandard)

    """

    MName: str
    MPitch: float
    M75: float
    I75: str
    M50: float
    I50: str
    MClose: float
    IClose: str
    MStandard: float
    IStandard: str

    # Fab_MDrillTap.__post_init__():
    def __post_init__(self) -> None:
        """Finish initalizign Fab_MDrillTap."""
        check_type("Fab_MDrillTap.MName", self.MName, str)
        check_type("Fab_MDrillTap.MPitch", self.MPitch, float)
        check_type("Fab_MDrillTap.M75", self.M75, float)
        check_type("Fab_MDrillTap.I75", self.I75, str)
        check_type("Fab_MDrillTap.M50", self.M50, float)
        check_type("Fab_MDrillTap.I50", self.I50, str)
        check_type("Fab_MDrillTap.MClose", self.MClose, float)
        check_type("Fab_MDrillTap.IClose", self.IClose, str)
        check_type("Fab_MDrillTap.MStandard", self.MStandard, float)
        check_type("Fab_MDrillTap.IStandard", self.IStandard, str)


# Fab_DrillChoice:
@dataclass
class Fab_DrillChoice(object):
    """Fab_DrillChoice: Preferred Metric and Imperial drill sizes.

    The final choice of hole sizes typically depends upon the available hardware.  In North
    America, the non metric size drills (fractional, letter, number) are readily available.
    Pretty much everywhere else, the metric drill sizes are more readily available.

    Attributes:
    * *MetricName* (str):
       A metric drill is specified as number in millimeters (e.g. "3", "3.5").
       The empty string is specified if there is no specified metric drill.
    * *MetricDiameter* (float): This is the name converted to a float.
       This is 0.0 if no metric drill is specified.
    * *ImperialName* (str):
      The imperial drill is name is either a fractional drill name (e.g. "1-1/8", "7/16"),
      a letter drill name (e.g "A", "J"),  or a number drill name (e.g. "N8", "N27".)
      The empty string is specified if there is no specified metric drill.
    * *ImperialDiameter (float): This is the drill diameter in millimeters.
       This is 0.0 if no metric drill is specified.

    Constructor:
    * Fab_DrillChoice(MetricName, MetricDiameter, ImperialName, ImperialDiameter)

    """
    MetricName: str
    MetricDiameter: float
    ImperialName: str
    ImperialDiameter: float

    # Fab_DrillChoice.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing Fab_DrillChoice."""
        check_type("FabDrillCheck.MetricName", self.MetricName, str)
        check_type("FabDrillCheck.MetricDiameter", self.MetricDiameter, float)
        check_type("FabDrillCheck.ImperialName", self.ImperialName, str)
        check_type("FabDrillCheck.ImperialDiameter", self.ImperialDiameter, float)


# Fab_DrillTap(object):
@dataclass
class Fab_DrillTap(object):
    """Fab_DrillTap: Drill/Tap diameters and drill selections.

    Attributes:
    * *Name* (str): Name of drill/tap selections.
    * *Thread75* (Fab_DrillChoice):  The drill choice for 75% thread operations.
    * *Thread50* (Fab_DrillChoice):  The drill choice for 50% thread operations.
    * *Close* (Fab_DrillChoice):  The drill choice for a close fit hole.
    * *Standard* (Fab_DrillChoice):  The drill choice for a standard fit hole.

    Constructor:
    * Fab_DrillTap(Name, Thread75, Thread50, Close, Standard)

    """

    Name: str
    Thread75: Fab_DrillChoice
    Thread50: Fab_DrillChoice
    Close: Fab_DrillChoice
    Standard: Fab_DrillChoice

    # Fab_DrillTap.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing Fab_DrillChoice."""
        check_type("FabDrillCheck.Thread75", self.Thread75, Fab_DrillChoice)
        check_type("FabDrillCheck.Thread50", self.Thread50, Fab_DrillChoice)
        check_type("FabDrillCheck.ThreadClose", self.Close, Fab_DrillChoice)
        check_type("FabDrillCheck.ThreadStandard", self.Standard, Fab_DrillChoice)


# Fab_IDrillTap:
@dataclass
class Fab_IDrillTap(object):
    """Fab_IDrillTap: Imperial Screw/Bolt Drill Selection.

    The standard imperial screw/bolt major shaft diameters are measured in inches.
    The three primary characteristics are:
    * Major shaft diameter:
      The major shaft diameters that are less than 0.25in are given "number" names "000", "00", "0",
      "1", "2", through "12".  There is no "7", "9", or "11".  After 0.25in, sizes are specified
      as fraction inches -- "1/4", "5/16", "3/8", ..., "1-3/4".
    * Threads Pitch:
      The thread pitch is measured in threads per inch and is always an integer.
    * Pitch Series:
      The three imperial pitch series that specify the threads per inch for a screw/bolt.
      The three series are course (NC), fine (NF), extremely fine (NEF).  There are also
      some pitch values that are non standard (NS), but still available.
      While screw/bolts are available in all three series, most are restricted to only one or
      two of the thread series.

    Imperial drill sizes are number drills (1-80), letter drills (A-Z), and fractional drills
    (3/64 - 1-3/4.)  The drill diameters of these series all overlap.  Many Imperial drill sets
    come with selections of all three drill series.

    Attributes:
    * *Size* (str):
      This is the "number" or "fractional" shaft size (e.g. "000", "0", "1/4", "1-1/4".)
    * *MajorDiameter* (float):
       This is the major shaft diameter in inches.
    * *ThreadsPerInch* (int):
      This is the threads pitch in thread per inch.  It is always an integer.
    * *Series* (str):
       This the pitch series -- "NF", "NS", "NC" or "NS".
       There are a few "standard" pitches are non-standard that are marked as "-".
    * *MinorDiameter* (float): This is the inner thread diameter in inches.
    * *Thread75Name* (str): The drill name to use for 75% threading in soft materials.
    * *Thread75Inch* (float): The *Thread75Name* drill diameter in inches.
    * *Thread50Name* (str): The drill name to use for 50% threading in hard materials.
    * *Thread50Inch* (float): The *Thread50Name* drill diameter in inches.
    * *CloseName* (str): The drill name to use for a close hole clearance.
    * *CloseInch (float): The *CloseName* drill diameter in inches.
    * *StandardName (str): The drill name to use for looser hole.
    * *StandardInch (float): The *StandardName* drill diameter in inches.

    Constructor:
    * Fab_IDrillTap(Size, MajorDiameter, ThreadsPerInch, Series, MinorDiameter, Thread75Name,
      Thread75Inch, Thread50Name, Thread50Inch, CloseName, CloseInch, StandardName, StandardInch)

    """

    Size: str
    MajorDiameter: float
    ThreadsPerInch: int
    Series: str
    MinorDiameter: float
    Thread75Name: str
    Thread75Inch: float
    Thread50Name: str
    Thread50Inch: float
    CloseName: str
    CloseInch: float
    StandardName: str
    StandardInch: float

    # Fab_IDrillTap.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing Fab_IDrillTap."""
        check_type("Fab_IDrillTap.Size", self.Size, str)
        check_type("Fab_IDrillTap.MajorDiameter", self.MajorDiameter, float)
        check_type("Fab_IDrillTap.ThreadsPerInch", self.ThreadsPerInch, int)
        check_type("Fab_IDrillTap.Series", self.Series, str)
        check_type("Fab_IDrillTap.MinorDiameter", self.MinorDiameter, float)
        check_type("Fab_IDrillTap.Thread75Name", self.Thread75Name, str)
        check_type("Fab_IDrillTap.Thread75Inch", self.Thread75Inch, float)
        check_type("Fab_IDrillTap.Thread50Name", self.Thread50Name, str)
        check_type("Fab_IDrillTap.Thread50Inch", self.Thread50Inch, float)
        check_type("Fab_IDrillTap.CloseName", self.CloseName, str)
        check_type("Fab_IDrillTap.CloseInch", self.CloseInch, float)
        check_type("Fab_IDrillTap.StandardName", self.StandardName, str)
        check_type("Fab_IDrillTap.StandardInch", self.StandardInch, float)


# Fab_Fastener:
@dataclass
class Fab_Fastener(object):
    """Fab_Fastener: Imperial/Metric fastener information.

    Attributes:
    * *Name* (str): The Fastener name.
    * *Thread50Diameter* (float): The 50% thread drill diameter.
    * *Thread50Drill* (str): The 50% thread drill name.
    * *Thread75Diameter* (float): The 75% thread drill diameter.
    * *Thread75Drill* (str): The 75% thread drill name.
    * *CloseDiameter* (float): The close fit hole diameter.
    * *CloseDrill* (str): The close fit drill name.
    * *StandardDiameter* (float): The standard fit hole diameter.
    * *StandardDrill* (str): The standard fit drill name.

    Constructor:
    * FabFastener(Name, Thread50Diameter, Thread50Drill, Thread75Diameter, Thread75Drill,
      CloseDiameter, CloseDrill, StandardDiameter, StandardDrill)

    """

    Name: str
    Thread50Diameter: float
    Thread50Drill: str
    Thread75Diameter: float
    Thread750Drill: str
    CloseDiameter: float
    CloseDrill: str
    StandardDiameter: float
    StandardDrill: str

    # Fab_Fastener.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing a Fab_Fastener."""
        check_type("Fab_Fastener.Name", self.Name, str)
        check_type("Fab_Fastener.Thread50Diameter", self.Thread50Diameter, float)
        check_type("Fab_Fastener.Thread50Drill", self.Thread50Drill, str)
        check_type("Fab_Fastener.Thread75Diameter", self.Thread75Diameter, float)
        check_type("Fab_Fastener.Thread750Drill", self.Thread750Drill, str)
        check_type("Fab_Fastener.CloseDiameter", self.CloseDiameter, float)
        check_type("Fab_Fastener.CloseDrill", self.CloseDrill, str)
        check_type("Fab_Fastener.StandardDiameter", self.StandardDiameter, float)
        check_type("Fab_Fastener.StandardDrill", self.StandardDrill, str)


# Fab_FastenTables:
class Fab_FastenTables(object):
    """Fab_FastenTables: Tables of metric/imperial screws and bolts.

    This is a class only object, so no constructor is ever used.
    """

    # [Metric Tap & Clearance Drill Sizes]
    #   (https://littlemachineshop.com/images/gallery/PDF/TapDrillSizes.pdf)
    METRIC_DRILL_TAPS: ClassVar[Tuple[Fab_MDrillTap, ...]] = (
        Fab_MDrillTap("M1.5", 0.35, 1.15, "N56", 1.25, "N55", 1.60, "1/16", 1.65, "N52"),
        Fab_MDrillTap("M1.6", 0.35, 1.25, "N55", 1.35, "N54", 1.70, "N51", 1.75, "N50"),
        Fab_MDrillTap("M1.8", 0.35, 1.45, "N53", 1.55, "1/16", 1.90, "N49", 2.00, "5/64"),
        Fab_MDrillTap("M2", 0.45, 1.55, "1/16", 1.70, "N51", 2.10, "N45", 2.20, "N44"),
        Fab_MDrillTap("M2", 0.40, 1.60, "N52", 1.75, "N50", 2.10, "N45", 2.20, "N44"),
        Fab_MDrillTap("M2.2", 0.45, 1.75, "N50", 1.90, "N48", 2.30, "3/32", 2.40, "N41"),
        Fab_MDrillTap("M2.5", 0.45, 2.05, "N46", 2.20, "N44", 2.65, "N37", 2.75, "7/64"),
        Fab_MDrillTap("M3", 0.60, 2.40, "N41", 2.60, "N37", 3.15, "1/8", 3.30, "N30"),
        Fab_MDrillTap("M3", 0.50, 2.50, "N39", 2.70, "N36", 3.15, "1/8", 3.30, "N30"),
        Fab_MDrillTap("M3.5", 0.60, 2.90, "N32", 3.10, "N31", 3.70, "N27", 3.85, "N24"),
        Fab_MDrillTap("M4", 0.75, 3.25, "N30", 3.50, "N28", 4.20, "N19", 4.40, "N17"),
        Fab_MDrillTap("M4", 0.70, 3.30, "N30", 3.50, "N28", 4.20, "N19", 4.40, "N17"),
        Fab_MDrillTap("M4.5", 0.75, 3.75, "N25", 4.00, "N22", 4.75, "N13", 5.00, "N9"),
        Fab_MDrillTap("M5", 1.00, 4.00, "N21", 4.40, "11/64", 5.25, "N5", 5.50, "7/32"),
        Fab_MDrillTap("M5", 0.90, 4.10, "N20", 4.40, "N17", 5.25, "N5", 5.50, "7/32"),
        Fab_MDrillTap("M5", 0.80, 4.20, "N19", 4.50, "N16", 5.25, "N5", 5.50, "7/32"),
        Fab_MDrillTap("M5.5", 0.90, 4.60, "N14", 4.90, "N10", 5.80, "N1", 6.10, "B"),
        Fab_MDrillTap("M6", 1.00, 5.00, "N8", 5.40, "N4", 6.30, "E", 6.60, "G"),
        Fab_MDrillTap("M6", 0.75, 5.25, "N4", 5.50, "7/32", 6.30, "E", 6.60, "G"),
        Fab_MDrillTap("M7", 1.00, 6.00, "B", 6.40, "E", 7.40, "L", 7.70, "N"),
        Fab_MDrillTap("M7", 0.75, 6.25, "D", 6.50, "F", 7.40, "L", 7.70, "N"),
        Fab_MDrillTap("M8", 1.25, 6.80, "H", 7.20, "J", 8.40, "Q", 8.80, "S"),
        Fab_MDrillTap("M8", 1.00, 7.00, "J", 7.40, "L", 8.40, "Q", 8.80, "S"),
        Fab_MDrillTap("M9", 1.25, 7.80, "N", 8.20, "P", 9.50, "3/8", 9.90, "25/64"),
        Fab_MDrillTap("M9", 1.00, 8.00, "O", 8.40, "21/64", 9.50, "3/8", 9.90, "25/64"),
        Fab_MDrillTap("M10", 1.50, 8.50, "R", 9.00, "T", 10.50, "Z", 11.00, "7/16"),
        Fab_MDrillTap("M10", 1.25, 8.80, "11/32", 9.20, "23/64", 10.50, "Z", 11.00, "7/16"),
        Fab_MDrillTap("M10", 1.00, 9.00, "T", 9.40, "U", 10.50, "Z", 11.00, "7/16"),
        Fab_MDrillTap("M11", 1.50, 9.50, "3/8", 10.00, "X", 11.60, "29/64", 12.10, "15/32"),
        Fab_MDrillTap("M12", 1.75, 10.30, "13/32", 10.90, "27/64", 12.60, "1/2", 13.20, "33/64"),
        Fab_MDrillTap("M12", 1.50, 10.50, "Z", 11.00, "7/16", 12.60, "1/2", 13.20, "33/64"),
        Fab_MDrillTap("M12", 1.25, 10.80, "27/64", 11.20, "7/16", 12.60, "1/2", 13.20, "33/64"),
        Fab_MDrillTap("M14", 2.00, 12.10, "15/32", 12.70, "1/2", 14.75, "37/64", 15.50, "39/64"),
        Fab_MDrillTap("M14", 1.50, 12.50, "1/2", 13.00, "33/64", 14.75, "37/64", 15.50, "39/64"),
        Fab_MDrillTap("M14", 1.25, 12.80, "1/2", 13.20, "33/64", 14.75, "37/64", 15.50, "39/64"),
        Fab_MDrillTap("M15", 1.50, 13.50, "17/32", 14.00, "35/64", 15.75, "5/8", 16.50, "21/32"),
        Fab_MDrillTap("M16", 2.00, 14.00, "35/64", 14.75, "37/64", 16.75, "21/32", 17.50, "11/16"),
        Fab_MDrillTap("M16", 1.50, 14.50, "37/64", 15.00, "19/32", 16.75, "21/32", 17.50, "11/16"),
        Fab_MDrillTap("M17", 1.50, 15.50, "39/64", 16.00, "5/8", 18.00, "45/64", 18.50, "47/64"),
        Fab_MDrillTap("M18", 2.50, 15.50, "39/64", 16.50, "41/64", 19.00, "3/4", 20.00, "25/32"),
        Fab_MDrillTap("M18", 2.00, 16.00, "5/8", 16.75, "21/32", 19.00, "3/4", 20.00, "25/32"),
        Fab_MDrillTap("M18", 1.50, 16.50, "21/32", 17.00, "43/64", 19.00, "3/4", 20.00, "25/32"),
        Fab_MDrillTap("M19", 2.50, 16.50, "21/32", 17.50, "11/16", 20.00, "25/32", 21.00, "53/64"),
        Fab_MDrillTap("M20", 2.50, 17.50, "11/16", 18.50, "23/32", 21.00, "53/64", 22.00, "55/64"),
        Fab_MDrillTap("M20", 2.00, 18.00, "45/64", 18.50, "47/64", 21.00, "53/64", 22.00, "55/64"),
        Fab_MDrillTap("M20", 1.50, 18.50, "47/64", 19.00, "3/4", 21.00, "53/64", 22.00, "55/64"),
    )

    # [Imperial Tap Chart](https://www.armstrongmetalcrafts.com/Reference/ImperialTapChart.aspx)
    IMPERIAL_DRILL_TAPS: ClassVar[Tuple[Fab_IDrillTap, ...]] = (
        Fab_IDrillTap("#000", 0.0340, 120, "NS", .0232,
                      "N71", 0.026, "N71", 0.0260, "N65", 0.0350, "N62", 0.0380),
        Fab_IDrillTap("#00", 0.0470, 90, "NS", .0334,
                      "N65", 0.0350, "N61", 0.0390, "3/64", 0.0469, "N55", 0.0520),
        Fab_IDrillTap("#0", 0.060, 80, "NF", .0465,
                      "3/64", 0.0469, "N55", 0.0520, "N52", 0.0635, "N50", 0.070),
        Fab_IDrillTap("#1", 0.073, 56, "NS", .0498,
                      "N54", 0.055, "-", -1.0, "48", 0.076, "N46", 0.081),
        Fab_IDrillTap("#1", 0.073, 64, "NC", 0.0538,
                      "N53", 0.0595, "1/16", 0.0625, "N48", 0.076, "N46", 0.081),
        Fab_IDrillTap("#1", 0.073, 72, "NF", 0.056,
                      "N53", 0.0595, "N52", 0.0635, "N48", 0.076, "N46", 0.081),
        Fab_IDrillTap("#2", 0.086, 56, "NC", 0.0641,
                      "N50", 0.07, "N49", 0.073, "N43", 0.089, "N41", 0.096),
        Fab_IDrillTap("#2", 0.086, 64, "NF", 0.0668,
                      "N50", 0.07, "N48", 0.076, "N43", 0.089, "N41", 0.096),
        Fab_IDrillTap("#3", 0.099, 48, "NC", 0.0734,
                      "N47", 0.0785, "N44", 0.086, "N37", 0.104, "N35", 0.110),
        Fab_IDrillTap("#3", 0.099, 56, "NF", 0.0771,
                      "N45", 0.082, "N43", 0.089, "N37", 0.104, "N35", 0.110),
        Fab_IDrillTap("#4", 0.112, 40, "NC", 0.0813,
                      "N43", 0.089, "N41", 0.096, "N32", 0.116, "N30", 0.1285),
        Fab_IDrillTap("#4", 0.112, 48, "NF", 0.0864,
                      "N42", 0.0935, "N40", 0.098, "N32", 0.116, "N30", 0.1285),
        Fab_IDrillTap("#5", 0.125, 40, "NC", 0.0943,
                      "N38", 0.1015, "9/64", 0.1094, "N30", 0.1285, "N29", 0.136),
        Fab_IDrillTap("#5", 0.125, 44, "NF", 0.0971,
                      "N37", 0.104, "N35", 0.110, "N30", 0.1285, "N29", 0.136),
        Fab_IDrillTap("#6", 0.138, 32, "NC", 0.0997,
                      "N36", 0.1065, "N32", 0.116, "N27", 0.144, "N25", 0.1495),
        Fab_IDrillTap("#6", 0.138, 40, "NF", 0.1073,
                      "N33", 0.113, "N31", 0.120, "N27", 0.144, "N25", 0.1495),
        Fab_IDrillTap("#8", 0.164, 32, "NC", 0.1257,
                      "N29", 0.136, "N27", 0.144, "N18", 0.1695, "N16", 0.177),
        Fab_IDrillTap("#8", 0.164, 36, "NF", 0.1299,
                      "N29", 0.136, "N26", 0.147, "N18", 0.1695, "N16", 0.177),
        Fab_IDrillTap("#10", 0.190, 24, "NC", 0.1389,
                      "N25", 0.1495, "N20", 0.161, "N9", 0.196, "N7", 0.201),
        Fab_IDrillTap("#10", 0.190, 32, "NF", 0.1517,
                      "N21", 0.159, "N18", 0.1695, "N9", 0.196, "N7", 0.201),
        Fab_IDrillTap("#12", 0.216, 24, "NC", 0.1649,
                      "N16", 0.177, "N12", 0.189, "N2", 0.221, "N1", 0.228),
        Fab_IDrillTap("#12", 0.216, 28, "NF", 0.1722,
                      "N14", 0.182, "N10", 0.1935, "N2", 0.221, "N1", 0.228),
        Fab_IDrillTap("#12", 0.216, 32, "NEF", 0.1777,
                      "N13", 0.185, "N9", 0.196, "N2", 0.221, "N1", 0.228),
        Fab_IDrillTap("1/4", 0.250, 20, "NC", 0.1887,
                      "N7", 0.201, "7/32", 0.2188, "F", 0.257, "H", 0.266),
        Fab_IDrillTap("1/4", 0.250, 28, "NF", 0.2062,
                      "N3", 0.213, "N1", 0.228, "F", 0.257, "H", 0.266),
        Fab_IDrillTap("1/4", 0.250, 32, "NEF", 0.2117,
                      "7/32", 0.2188, "N1", 0.228, "F", 0.257, "H", 0.266),
        Fab_IDrillTap("5/16", 0.3125, 18, "NC", 0.2443,
                      "F", 0.257, "J", 0.277, "P", 0.323, "Q", 0.332),
        Fab_IDrillTap("5/16", 0.3125, 24, "NF", 0.2614,
                      "I", 0.272, "9/32", 0.2812, "P", 0.323, "Q", 0.332),
        Fab_IDrillTap("5/16", 0.3125, 32, "NEF", 0.2742,
                      "9/32", 0.2812, "L", 0.290, "P", 0.323, "Q", 0.332),
        Fab_IDrillTap("3/8", 0.375, 16, "NC", 0.2983,
                      "5/16", 0.3125, "Q", 0.332, "W", 0.386, "X", 0.397),
        Fab_IDrillTap("3/8", 0.375, 24, "NF", 0.3239,
                      "Q", 0.332, "S", 0.348, "W", 0.386, "X", 0.397),
        Fab_IDrillTap("3/8", 0.375, 32, "NEF", 0.3367,
                      "11/32", 0.3438, "T", 0.358, "W", 0.386, "X", 0.397),
        Fab_IDrillTap("7/16", 0.4375, 14, "NC", 0.3499,
                      "U", 0.368, "25/64", 0.3906, "29/64", 0.4531, "15/32", 0.4687),
        Fab_IDrillTap("7/16", 0.4375, 20, "NF", 0.3762,
                      "25/64", 0.3906, "13/32", 0.4062, "29/64", 0.4531, "15/32", 0.4687),
        Fab_IDrillTap("7/16", 0.4375, 28, "NEF", 0.3937,
                      "Y", 0.404, "Z", 0.413, "29/64", 0.4531, "15/32", 0.4687),
        Fab_IDrillTap("1/2", 0.500, 13, "NC", 0.4056,
                      "27/64", 0.4219, "29/64", 0.4531, "33/64", 0.5156, "17/32", 0.5312),
        Fab_IDrillTap("1/2", 0.500, 20, "NF", 0.4387,
                      "29/64", 0.4531, "15/32", 0.4688, "33/64", 0.5156, "17/32", 0.5312),
        Fab_IDrillTap("1/2", 0.500, 28, "NEF", 0.4562,
                      "15/32", 0.4688, "15/32", 0.4688, "33/64", 0.5156, "17/32", 0.5312),
        Fab_IDrillTap("9/16", 0.5625, 12, "NC", 0.4603,
                      "31/64", 0.4844, "33/64", 0.5156, "37/64", 0.5781, "19/32", 0.5938),
        Fab_IDrillTap("9/16", 0.5625, 18, "NF", 0.4943,
                      "33/64", 0.5156, "17/32", 0.5312, "37/64", 0.5781, "19/32", 0.5938),
        Fab_IDrillTap("9/16", 0.5625, 24, "NEF", 0.5114,
                      "33/64", 0.5156, "17/32", 0.5312, "37/64", 0.5781, "19/32", 0.5938),
        Fab_IDrillTap("5/8", 0.625, 11, "NC", 0.5135,
                      "17/32", 0.5312, "41168", 0.5625, "41/64", 0.6406, "21/32", 0.6562),
        Fab_IDrillTap("5/8", 0.625, 18, "NF", 0.5568,
                      "37/64", 0.5781, "19/32", 0.5938, "41/64", 0.6406, "21/32", 0.6562),
        Fab_IDrillTap("5/8", 0.625, 24, "NEF", 0.5739,
                      "37/64", 0.5781, "19/32", 0.5938, "41/64", 0.6406, "21/32", 0.6562),
        Fab_IDrillTap("11/16", 0.6875, 24, "NS", 0.6364,
                      "41/64", 0.6406, "21/32", 0.6562, "45/64", 0.7031, "23/32", 0.7188),
        Fab_IDrillTap("3/4", 0.750, 10, "NC", 0.6273,
                      "21/32", 0.6562, "41229", 0.6875, "49/64", 0.7656, "25/32", 0.7812),
        Fab_IDrillTap("3/4", 0.750, 16, "NF", 0.6733,
                      "11/166", 0.6875, "45/64", 0.7031, "49/64", 0.7656, "25/32", 0.7812),
        Fab_IDrillTap("3/4", 0.750, 20, "NEF", 0.6887,
                      "45/64", 0.7031, "23/32", 0.7188, "49/64", 0.7656, "25/32", 0.7812),
        Fab_IDrillTap("13/16", 0.8125, 20, "NS", 0.7512,
                      "49/64", 0.7656, "25/32", 0.7812, "53/64", 0.8281, "27/32", 0.8438),
        Fab_IDrillTap("7/8", 0.875, 9, "NC", 0.7387,
                      "49/64", 0.7656, "51/64", 0.7969, "57/64", 0.8906, "29/32", 0.9062),
        Fab_IDrillTap("7/8", 0.875, 14, "NF", 0.7874,
                      "13/16", 0.8125, "53/64", 0.8281, "57/64", 0.8906, "29/32", 0.9062),
        Fab_IDrillTap("7/8", 0.875, 20, "NEF", 0.8137,
                      "53/64", 0.8281, "27/32", 0.8438, "57/64", 0.8906, "29/32", 0.9062),
        Fab_IDrillTap("15/16", 0.9375, 20, "NS", 0.8762,
                      "57/64", 0.8906, "29/32", 0.9062, "61/64", 0.9531, "31/32", 0.9688),
        Fab_IDrillTap("1", 1.000, 8, "NC", 0.8466,
                      "7/8", 0.875, "59/64", 0.9219, "1-1/64", 1.0156, "1-31/32", 1.0313),
        Fab_IDrillTap("1", 1.000, 12, "NF", 0.8978,
                      "15/16", 0.9375, "61/64", 0.9531, "1-1/64", 1.0156, "1-31/32", 1.0313),
        Fab_IDrillTap("1", 1.000, 20, "NEF", 0.9387,
                      "61/64", 0.953, "31/32", 0.9688, "1-1/64", 1.0156, "1-31/32", 1.0313),
        Fab_IDrillTap("1-1/16", 1.0625, 18, "NEF", 0.9943,
                      "1", 1.0, "1-1/64", 1.0156, "1-5/64", 1.0781, "1-3/32", 1.0938),
        Fab_IDrillTap("1-1/8", 1.125, 7, "NC", 0.9497,
                      "63/64", 0.9844, "1-1/32", 1.0313, "1-9/64", 1.1406, "1-5/32", 1.1562),
        Fab_IDrillTap("1-1/8", 1.125, 12, "NF", 1.0228,
                      "1-3/64", 1.0469, "1-5/64", 1.0781, "1-9/64", 1.1406, "1-5/32", 1.1562),
        Fab_IDrillTap("1-1/8", 1.125, 18, "NEF", 1.0568,
                      "1-1/16", 1.0625, "1-5/64", 1.0781, "1-9/64", 1.1406, "1-5/32", 1.1562),
        Fab_IDrillTap("1-3/16", 1.1875, 18, "NEF", 1.1193,
                      "49/64", 1.125, "1-9/64", 1.1406, "1-13/64", 1.2031, "1-7/32", 1.2188),
        Fab_IDrillTap("1-1/4", 1.250, 7, "NC", 1.0747,
                      "1-7/64", 1.1094, "1-5/32", 1.1562, "1-17/64", 1.2656, "1-9/32", 1.2812),
        Fab_IDrillTap("1-1/4", 1.250, 12, "NF", 1.1478,
                      "1-11/64", 1.1719, "1-13/64", 1.2031, "1-17/64", 1.2656, "1-9/32", 1.2812),
        Fab_IDrillTap("1-1/4", 1.250, 18, "NEF", 1.1818,
                      "1-3/16", 1.1875, "1-13/64", 1.2031, "1-17/64", 1.2656, "1-9/32", 1.2812),
        Fab_IDrillTap("1-5/16", 1.3125, 18, "NEF", 1.2443,
                      "1-1/4", 1.25, "1-17/64", 1.2656, "1-21/64", 1.3281, "1-11/32", 1.3438),
        Fab_IDrillTap("1-3/8", 1.375, 6, "NC", 1.1705,
                      "1-7/32", 1.2187, "1-17/64", 1.2656, "1-25/64", 1.3906, "1-13/32", 1.4062),
        Fab_IDrillTap("1-3/8", 1.375, 12, "NF", 1.2728,
                      "1-19/64", 1.2969, "1-21/64", 1.3281, "1-25/64", 1.3906, "1-13/32", 1.4062),
        Fab_IDrillTap("1-3/8", 1.375, 18, "NEF", 1.3068,
                      "1-5/16", 1.3125, "1-21/64", 1.3281, "1-25/64", 1.3906, "1-13/32", 1.4062),
        Fab_IDrillTap("1-7/16", 1.4375, 18, "NEF", 1.3693,
                      "1-3/8", 1.375, "1-25/64", 1.3906, "1-29/64", 1.4531, "1-15/32", 1.4688),
        Fab_IDrillTap("1-1/2", 1.500, 6, "NC", 1.2955,
                      "1-11/32", 1.3437, "1-25/64", 1.3906, "1-33/64", 1.5156, "1-17/32", 1.5312),
        Fab_IDrillTap("1-1/2", 1.500, 12, "NF", 1.3978,
                      "1-27/64", 1.4219, "1-7/16", 1.4375, "1-33/64", 1.5156, "1-17/32", 1.5312),
        Fab_IDrillTap("1-1/2", 1.500, 18, "NEF", 1.4318,
                      "1-7/16", 1.4375, "1-29/64", 1.4531, "1-33/64", 1.5156, "1-17/32", 1.5312),
        Fab_IDrillTap("1-9/16", 1.5625, 18, "NEF", 1.4943,
                      "1-1/2", 1.5, "1-33/64", 1.5156, "1-37/64", 1.5781, "1-19/32", 1.5938),
        Fab_IDrillTap("1-5/8", 1.625, 18, "NEF", 1.5568,
                      "1-9/16", 1.5625, "1-37/64", 1.5781, "1-41/64", 1.6406, "1-21/32", 1.6562),
        Fab_IDrillTap("1-11/16", 1.6875, 18, "NEF", 1.6193,
                      "1-5/8", 1.625, "1-41/64", 1.6406, "1-45/64", 1.7031, "1-23/32", 1.7188),
        Fab_IDrillTap("1-3/4", 1.750, 5, "NC", 1.5046,
                      "1-9/16", 1.5625, "1-5/8", 1.625, "1-49/64", 1.7659, "1-25/32", 1.7812),
    )

    LETTER_DRILL_DIAMETERS: ClassVar[Dict[str, float]] = {
        "A": 0.234,  # inches
        "B": 0.238,
        "C": 0.242,
        "D": 0.246,
        "E": 0.250,
        "F": 0.257,
        "G": 0.261,
        "H": 0.266,
        "I": 0.272,
        "J": 0.277,
        "K": 0.281,
        "L": 0.29,
        "M": 0.295,
        "N": 0.302,
        "O": 0.316,
        "P": 0.323,
        "Q": 0.332,
        "R": 0.339,
        "S": 0.348,
        "T": 0.358,
        "U": 0.368,
        "V": 0.377,
        "W": 0.386,
        "X": 0.397,
        "Y": 0.404,
        "Z": 0.413,
    }

    NUMBER_DRILL_DIAMETERS: ClassVar[Dict[str, float]] = {
        "N80": 0.0135,  # inches
        "N79": 0.0145,
        "N78": 0.016,
        "N77": 0.018,
        "N76": 0.020,
        "N75": 0.021,
        "N74": 0.0225,
        "N73": 0.024,
        "N72": 0.025,
        "N71": 0.026,
        "N70": 0.028,
        "N69": 0.029,
        "N68": 0.031,
        "N67": 0.032,
        "N66": 0.033,
        "N65": 0.035,
        "N64": 0.036,
        "N63": 0.037,
        "N62": 0.038,
        "N61": 0.039,
        "N60": 0.040,
        "N59": 0.041,
        "N58": 0.042,
        "N57": 0.043,
        "N56": 0.046,
        "N55": 0.052,
        "N54": 0.055,
        "N53": 0.0595,
        "N52": 0.0635,
        "N51": 0.067,
        "N50": 0.070,
        "N49": 0.073,
        "N48": 0.076,
        "N47": 0.0785,
        "N46": 0.081,
        "N45": 0.082,
        "N44": 0.086,
        "N43": 0.089,
        "N42": 0.0935,
        "N41": 0.096,
        "N40": 0.098,
        "N39": 0.0995,
        "N38": 0.1015,
        "N37": 0.104,
        "N36": 0.1065,
        "N35": 0.11,
        "N34": 0.111,
        "N33": 0.113,
        "N32": 0.116,
        "N31": 0.120,
        "N30": 0.1285,
        "N29": 0.136,
        "N28": 0.14,
        "N27": 0.144,
        "N26": 0.147,
        "N25": 0.150,
        "N24": 0.152,
        "N23": 0.154,
        "N22": 0.157,
        "N21": 0.159,
        "N20": 0.161,
        "N19": 0.166,
        "N18": 0.170,
        "N17": 0.173,
        "N16": 0.177,
        "N15": 0.18,
        "N14": 0.182,
        "N13": 0.185,
        "N12": 0.189,
        "N11": 0.191,
        "N10": 0.193,
        "N9": 0.196,
        "N8": 0.199,
        "N7": 0.201,
        "N6": 0.204,
        "N5": 0.205,
        "N4": 0.209,
        "N3": 0.213,
        "N2": 0.221,
        "N1": 0.228,
    }

    FastenerTable: ClassVar[Dict[str, Fab_DrillTap]] = {}

    # is_fractional_drill():
    @classmethod
    def is_fractional_drill(cls, name: str) -> bool:
        """Return whether a drill name is an imperial fractional drill.

        The format of a fractional drill is on of the following "1-N/D", "N/D", or "1",
        where "1" is a 1 inch diameter drill.  D must be one of 2, 4, 8, 16, 32, or 64.
        N must be positive and less than D (i.e. 1 <= N < D.)
        """
        # Split *name* into *whole* and *fraction*:
        if name == "1":
            return True
        if name == "":
            return False
        if name.startswith("1-"):
            name = name[2:]
        parts: List[str] = name.split("/")
        if len(parts) != 2:
            return False
        if not (parts[0].isnumeric() and parts[1].isnumeric()):
            return False
        numerator: int = int(parts[0])
        denominator: int = int(parts[1])
        if denominator in (2, 4, 8, 16, 32, 64) and 1 <= numerator < denominator:
            return True
        return False

    # fractional_value():
    @classmethod
    def fractional_value(cls, name: str) -> float:
        """Return fractional drill diameter in millimeters."""
        assert cls.is_fractional_drill(name)
        inches: float = 0.0
        if name == "1":
            inches = 1.0
        elif name.startswith("1-"):
            inches = 1
            name = name[2:]
            numerator, denominator = name.split("/")
            inches += float(numerator) / float(denominator)
        return inches

    # is_letter_drill():
    @classmethod
    def is_letter_drill(cls, name: str) -> bool:
        """Return whether a drill name is an imperial letter drill between A and Z."""
        return len(name) == 1 and name.isupper()

    # is_number_drill():
    @classmethod
    def is_number_drill(cls, name: str) -> bool:
        """Return whether a drill name is a number drill of the form "Ni" where 1<=i<=107."""
        if not name.startswith("N"):
            return False
        if not name[1:].isnumeric:
            return False
        number: int = int(name[1:])
        return 1 <= int(number) <= 107  # Number drills less than 80 are not readily available.

    # is_imperial_drill():
    @classmethod
    def is_imperial_drill(cls, name: str) -> bool:
        return (
            cls.is_fractional_drill(name) or cls.is_letter_drill(name) or cls.is_number_drill(name))

    @classmethod
    def to_mm(cls, imperial_name: str) -> float:
        inches: float
        if cls.is_fractional_drill(imperial_name):
            inches = cls.fractional_value(imperial_name)
        elif cls.is_letter_drill(imperial_name):
            inches = cls.LETTER_DRILL_DIAMETERS[imperial_name]
        elif cls.is_number_drill(imperial_name):
            inches = cls.NUMBER_DRILL_DIAMETERS[imperial_name]
        else:
            raise ValueError(f"'{imperial_name}' is not an imperial drill name")
        return inches * 25.4

    @classmethod
    def table_initialize(cls) -> None:
        drill_tap: Fab_DrillTap
        name: str
        mtap: Fab_MDrillTap
        for mtap in cls.METRIC_DRILL_TAPS:
            name = f"{mtap.MName}x{mtap.MPitch}".replace("x0", "x")  # "M??x0.PP" => "M??x.PP"
            drill_tap = Fab_DrillTap(
                name,
                Fab_DrillChoice(str(mtap.M75), mtap.M75, mtap.I75, cls.to_mm(mtap.I75)),
                Fab_DrillChoice(str(mtap.M50), mtap.M50, mtap.I50, cls.to_mm(mtap.I50)),
                Fab_DrillChoice(str(mtap.MClose), mtap.MClose, mtap.IClose, cls.to_mm(mtap.IClose)),
                Fab_DrillChoice(str(mtap.MStandard), mtap.MStandard,
                                mtap.IStandard, cls.to_mm(mtap.IStandard))
            )
            cls.FastenerTable[name] = drill_tap

        itap: Fab_IDrillTap
        for itap in cls.IMPERIAL_DRILL_TAPS:
            name = f"{itap.Size}-{itap.ThreadsPerInch}"
            drill_tap = Fab_DrillTap(
                name,
                Fab_DrillChoice("", 0.0, itap.Thread75Name, itap.Thread75Inch * 25.4),
                Fab_DrillChoice("", 0.0, itap.Thread50Name, itap.Thread50Inch * 25.4),
                Fab_DrillChoice("", 0.0, itap.CloseName, itap.CloseInch * 25.4),
                Fab_DrillChoice("", 0.0, itap.StandardName, itap.StandardInch * 25.4)
            )
            cls.FastenerTable[name] = drill_tap

    @classmethod
    def lookup(cls, name: str) -> Fab_DrillTap:
        """Return the Fab_DrillTap for a requested threaded fastener."""
        if not cls.FastenerTable:
            cls.table_initialize()
        if name not in cls.FastenerTable:
            raise RuntimeError(f"Threaded fastener '{name}' is not found. "
                               f"{tuple(cls.FastenerTable.keys())}")
        return cls.FastenerTable[name]


# FabOption:
@dataclass(frozen=True)
class FabOption(object):
    """FabOption: Base class for FabFasten options (e.g. washers, nuts, etc...).

    Attributes:
    * *Name* (str): The option name.
    * *Detail* (str): More detailed information about the option.

    Constructor:
    * This is meant to be sub-classed, so this class should never be constructed manually.
    """

    Name: str  # FabOption name
    Detail: str  # FabOption description.

    # FabOption.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing a FabOption."""
        check_type("FabOption.Name", self.Name, str)
        check_type("FabOption.Detail", self.Detail, str)

    # FabOption.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return FabOption hash."""
        raise RuntimeError(f"get_hash() is not implemented for {type(self)}")

    # FabOption._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Run FabOption unit tests."""
        name: str = "name"
        detail: str = "detail"
        option: FabOption = FabOption(name, detail)
        assert option.Name == name
        assert option.Detail == detail


# FabHead:
@dataclass(frozen=True)
class FabHead(FabOption):
    """Represents the Head of the FabFastener.

    Attributes:
    * *Name* (str): The name for this head.
    * *Detail* (str): Short FabHead description.
    * *Material* (FabMaterial): The FabHead fastener material.
    * *Shape* (str): The FabHead shape.
    * *Drive* (str): The FabHead drive.

    Constructor:
    * FabHead(Name, Detail, Material, Shape, Drive)

    """

    Material: FabMaterial
    Shape: str
    Drive: str

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

    # FabHead.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabHead."""
        super().__post_init__()
        check_type("FabHead.Material", self.Material, FabMaterial)
        check_type("FabHead.Shape", self.Shape, str)
        check_type("FabHead.Drive", self.Drive, str)
        assert self.Shape in FabHead.HEADS, "f{self.Shape} is not one of {FabHead.HEADS}"
        assert self.Drive in FabHead.DRIVES, "f{self.Drive} is not one of {FabHead.DRIVES}"

    # FabHead._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Run FabHead unit tests."""
        name: str = "PH"
        detail: str = "Brass Philips Pan Head"
        material: FabMaterial = FabMaterial(("Brass",), "orange")
        shape: str = FabHead.PAN_HEAD
        drive: str = FabHead.PHILIPS_DRIVE
        apex_head: FabHead = FabHead(name, detail, material, shape, drive)

        assert apex_head.Name == name, apex_head.Name
        assert apex_head.Material is material, apex_head.Material
        assert apex_head.Shape == shape, apex_head.Shape
        assert apex_head.Drive == drive, apex_head.Drive


# FabNut:
@dataclass(frozen=True)
class FabNut(FabOption):
    """FabNut: A class the represents a fastener nut.

    Attributes:
    * Name (str): Nut name.
    * Detail (str): More nut detail.
    * Sides (int): The number of nut sides (either 4 or 6.)
    * Width (float): The Nut width between 2 opposite faces.
    * Thickness (float): The nut thickness in millimeters.
    * Material (FabMaterial): The nut material

    Constructor:
    * FabNut(Name, Detail, Sides, Width, Thickness, Material)

    """

    Sides: int  # The Nut sides (either, 4 or 6).
    Width: float  # The Nut width between 2 faces in millimeters.
    Thickness: float  # The Nut thickness in millimeters.
    Material: FabMaterial  # The Nut material.

    # FabNut.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabNut."""
        super().__post_init__()
        check_type("FabNut.Sides", self.Sides, int)
        check_type("FabNut.Width", self.Width, float)
        check_type("FabNut.Thickness", self.Thickness, float)
        check_type("FabNut.Material", self.Material, FabMaterial)
        assert self.Sides in (4, 6), f"Sides ({self.Sides}) is not one of (4, 6)"
        assert self.Width > 0.0, f"Width ({self.Width}) is not positive"
        assert self.Thickness > 0.0, f"Thickness ({self}) is not positive"

    # FabNut._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Run FabNut unit tests."""
        # Create the FabNut:
        name: str = "M3Nut"
        detail: str = "Brass M3 Hex Nut"
        sides: int = 6
        width: float = 6.2
        thickness: float = 2.0
        material: FabMaterial = FabMaterial(("brass",), "orange")
        nut: FabNut = FabNut(name, detail, sides, width, thickness, material)

        # Verify attributes:
        assert nut.Name == name, nut.Name
        assert nut.Detail == detail, nut.Detail
        assert nut.Sides == sides, nut.Sides
        assert nut.Width == width, nut.Width
        assert nut.Thickness == thickness, nut.Thickness
        assert nut.Material == material, nut.Material


# FabWasher:
@dataclass(frozen=True)
class FabWasher(FabOption):
    """FabWasher: Represents a washer.

    Constants:
    * PLAIN: Plain washer.
    * INTERNAL_LOCK: Internal tooth lock washer.
    * EXTERNAL_LOCK: External tooth lock washer.
    * SPLIT_LOCK: Split ring lock washer.

    Attributes:
    * *Name* (str): The washer name.
    * *Detail* (str): More detail about the FabWasher.
    * *Inner* (float): The Inner diameter in millimeters.
    * *Outer* (float): The Outer diameter in millimeters.
    * *Thickness* (float): The thickness in millimeters.
    * *Material* (FabMaterial): The Material the washer is made out of.
    * *Kind* (str): The washer kind -- one of following FabWasher constants --
      `PLAIN`, `INTERNAL_LOCK`, `EXTERNAL_LOCK`, or `SPLIT_LOCK`.

    Constructor:
    * FabNut(Name, Detail, Inner, Outer, Thickness, Material, Kind)

    """

    Inner: float  # Inner diameter
    Outer: float  # Outer diameter
    Thickness: float  # Thickness
    Material: FabMaterial  # Material
    Kind: str  # Kind

    # Predefined constants for Kind.
    PLAIN = "PLAIN"
    INTERNAL_LOCK = "INTERNAL_LOCK"
    EXTERNAL_LOCK = "EXTERNAL_LOCK"
    SPLIT_LOCK = "SPLIT_LOCK"
    KINDS = (PLAIN, INTERNAL_LOCK, EXTERNAL_LOCK, SPLIT_LOCK)

    # FabWasher.__post_init__():
    def __post_init__(self):
        """Finish initialializing FabWasher."""
        super().__post_init__()
        check_type("FlatWasher.Inner", self.Inner, float)
        check_type("FlatWasher.Outer", self.Outer, float)
        check_type("FlatWasher.Thickness", self.Thickness, float)
        check_type("FlatWasher.Material", self.Material, FabMaterial)
        check_type("FlatWasher.Kind", self.Kind, str)

        assert self.Inner > 0.0, f"Inner({self.Inner}) is not positive"
        assert self.Outer > 0.0, f"Outer({self.Outer}) is not positive"
        assert self.Inner < self.Outer, f"Inner({self.Inner}) not less that Outer({self.Outer})"
        assert self.Kind in FabWasher.KINDS, f"Kind({self.Kind}) is not one of {FabWasher.KINDS}"

    # FabWasher._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Perform FabWasher unit tests."""
        # Create the *washer*:
        name: str = "W6x.5"
        detail: str = "M3 Washer (ID=3.2 OD=6, Thick=.5)"
        inner: float = 3.2
        outer: float = 6.0
        thickness: float = 0.5
        material: FabMaterial = FabMaterial(("brass",), "orange")
        kind: str = FabWasher.PLAIN
        washer: FabWasher = FabWasher(name, detail, inner, outer, thickness, material, kind)

        # Access all of the attributes:
        assert washer.Name == name, washer.Name
        assert washer.Detail == detail, washer.Detail
        assert washer.Inner == inner, washer.Inner
        assert washer.Outer == outer, washer.Outer
        assert washer.Thickness == thickness, washer.Thickness
        assert washer.Material is material, washer.Material
        assert washer.Kind == kind, washer.Kind


# FabFasten:
@dataclass(frozen=True)
class FabFasten(object):
    """FabFasten: The class of Fastener to use.

    Attributes:
    * Name (str): FabFasten Name.
    * ThreadName (str): A thread selection (e.g. "M3x.5", "#4-40", "1/4-20")
    * Options (Tuple[FabOption, ...]): Various Head/Tail options for fastener stack

    Constructor:
    * FabFasten(Name, ThreadName, Options)

    """

    Name: str  # FabFasten Name
    ThreadName: str
    Options: Tuple[FabOption, ...] = field(repr=False)  # FabFasten Options

    # Profile: str  # FabFasten Profile
    # Size: str  # FabFasten Size
    # * Profile (str): FabFasten Profile.  Must be one of the FabFasten constants --
    #   `ISO_COARSE`, `ISO_FINE`,  `UTS_COARSE`, `UTS_FINE`, and `UTS_EXTRA_FINE.
    # * Size (str): Standard fastener size.  Must be one of the FabFasten constants --
    #   `UTS_N1`, `UTS_N2`, `UTS_N3`, `UTS_N4`, `UTS_N5`, `UTS_N6`, `UTS_N8`, `UTS_N10`, `UTS_N12`,
    #   `UTS_F1_4`, `UTS_F5_16`, `UTS_F3_8`, `UTS_F7_16`, `UTS_F1_2`, `UTS_F9_16`, `UTS_F5_8`,
    #   `UTS_F3_4`, `UTS_F3_4`, `M1_6`, `M2`, `M2_5`, `M3`, `M3_5`, `M4`, `M5`, `M6`, `M8`, `M10`,
    #   `M12`, `M14`, `M16`, `M18,  `M20`, `M22`, `M24`, `M27`, `M30`, `M36`, `M42`, `M48`, `M56`,
    #   `M68.

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
    M1 = "M1"
    M1_1 = "M1.10"
    M1_2 = "M1.20"
    M1_4 = "M1.40"
    M1_6 = "M1.60"
    M1_8 = "M1.80"
    M2 = "M2"
    M2_5 = "M2.50"
    M3 = "M3"
    M3_5 = "M3.50"
    M4 = "M4"
    M4_5 = "M4.50"
    M5 = "M5"
    M6 = "M6"
    M7 = "M7"
    M8 = "M8"
    M9 = "M9"
    M10 = "M10"
    M11 = "M11"
    M12 = "M12"
    M14 = "M14"
    M16 = "M16"
    M18 = "M18"
    M20 = "M20"
    M22 = "M22"
    M24 = "M24"
    M27 = "M27"
    M30 = "M30"
    M33 = "M33"
    M36 = "M36"
    M36 = "M39"
    M42 = "M42"
    M42 = "M45"
    M48 = "M48"
    M48 = "M62"
    M56 = "M56"
    M60 = "M60"
    M64 = "M68"
    M68 = "M68"

    # [Metric Thread - Drill & Tap Chart](http://shender4.com/metric_thread_chart.htm)
    metric_coarse = (
        ("M1x.25", 0.75),
        ("M1.1x.25", 0.85),
        ("M1.2x.25", 0.95),
        ("M1.4x.3", 1.10),
        ("M1.6x.35", 1.25),
        ("M1.8x.35", 1.45),
        ("M2x0.4", 1.60),
        ("M2.2x.45", 1.75),
        ("M2.5x.45", 2.05),
        ("M3x.5", 2.50),
        ("M3.5x.60", 2.90),
        ("M4x0.70", 3.30),
        ("M4.5x.75", 3.70),
        ("M5x0.8", 4.20),
        ("M7x1", 6.00),
        ("M8x1.25", 6.80),
        ("M9x1.25", 7.80),
        ("M10x1.5", 8.50),
        ("M11x1.5", 9.50),
        ("M12x1.75", 10.20),
        ("M14x2", 12.00),
        ("M16x2", 14.00),
        ("M18x2.5", 15.50),
        ("M20x2.5", 17.50),
        ("M22x2.5", 19.50),
        ("M24x3", 21.00),
        ("M27x3", 24.00),
        ("M30x3.5", 26.50),
        ("M33x3.5", 29.50),
        ("M36x40", 32.00),
        ("M39x4", 35.00),
        ("M42x4.5", 37.50),
        ("M45x4.5", 40.50),
        ("M6x1", 5.00),
        ("M48x5", 43.00),
        ("M52x5", 47.00),
        ("M56x5.5", 50.50),
        ("M60x5.5", 54.50),
        ("M64x6", 58.00),
        ("M68x6", 62.00),
    )

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

    # FabFasten.__post_init__():
    def __post_init__(self):
        """Finish initializing FabFasten.

        Arguments:
        * Profile (str): Profile to use.  Select from the following predefined FabFasten
          constants -- `PROFILE_CUSTOM`, `PROFILE_ISO_COARSE`, `PROFILE_ISO_FINE`,
          `PROFILE_UTS_COARSE`, `PROFILE_UTS_FINE`, `PROFILE_UTS_EXTRA_FINE`.  `PROFILE_CUSTOM`
          requires additional sizes to be specified -- `close_diameter`, `loose_diameter`,
          `thread_diameter`.
        * Size (str): Size to use. Select from the following predefined FabFasten constants --
          `CUSTOM_SIZE`, `UTS_N1`, `UTS_N2`, `UTS_N3`, `UTS_N4`, `UTS_N5`, `UTS_N6`, `UTS_N8`,
          `UTS_N10`, `UTS_N12`, `UTS_F1_4`, `UTS_F5_16`, `UTS_F3_8`, `UTS_F7_16`, `UTS_F1_2`,
          `UTS_F9_16`, `UTS_F5_8`, `UTS_F3_4`, `UTS_F3_4`, `M1_6`, `M2`, `M2_5`, `M3`, `M3_5`,
          `M4`, `M5`, `M6`, `M8`, `M10`, `M12`, `M14`, `M16`, `M18`, `M20`, `M22`, `M24`, `M27`,
          `M30`, `M36`, `M42`, `M48`, `M56`, `M68`.
        """
        check_type("FabFasten.Name", self.Name, str)
        check_type("FabFasten.ThreadName", self.ThreadName, str)
        check_type("FabFasten.Options", self.Options, Tuple[FabOption, ...])

    # FabFasten.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return FabFasten hash."""
        hashes: List[Union[int, str, Tuple[Any, ...]]] = [
            "FabFasten",
            self.Name,
            self.ThreadName,
        ]
        option: FabOption
        for option in self.Options:
            hashes.append(option.get_hash())
        return tuple(hashes)

    # FabFasten.get_diameter():
    def get_diameter(self, kind: str) -> float:
        """Return actual diameter based on request hole kind."""
        drill_tap: Fab_DrillTap = Fab_FastenTables.lookup(self.ThreadName)
        drill_choice: Fab_DrillChoice
        if kind == "thread":
            drill_choice = drill_tap.Thread75
        elif kind == "close":
            drill_choice = drill_tap.Close
        elif kind == "standard":
            drill_choice = drill_tap.Standard
        else:
            raise RuntimeError(f"'{kind}' is not one of 'thread', 'close', or 'standard'")
        if drill_choice.MetricName:
            return drill_choice.MetricDiameter
        if drill_choice.ImperialName:
            return drill_choice.ImperialDiameter
        raise RuntimeError("Empty drill choice")

    # FabFasten._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Run FabFasten unit tests."""
        name: str = "#4-40"
        fasten: FabFasten = FabFasten(name, "#4-40", ())

        assert fasten.Name == name
        assert fasten.ThreadName == name
        assert fasten.Options == ()


# FabJoin:
@dataclass
class FabJoin(object):
    """FabJoin: Specifies a single fastener instance.

    Attributes:
    * Name (str): A name used for error reporting.
    * Fasten (FabFasten): FabFasten object to use for basic dimensions.
    * Start (Vector): Start point for FabJoin.
    * End (Vector): End point for FabJoin.

    Constructor:
    * FabJoin(Name, Fasten, Start, End)

    """

    _Name: str
    _Fasten: FabFasten  # Parent FabFasten
    _Start: Vector  # Start point (near screw/bolt head)
    _End: Vector  # End point (ene screw/bolt tip)

    # FabJoin.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return FabJoin hash."""
        start: Vector = self._Start
        end: Vector = self._End
        hashes: Tuple[Union[int, str, Tuple[Any, ...]], ...] = (
            "FabJoin",
            self._Name,
            self._Fasten.get_hash(),
            f"{start.x:.6f}",
            f"{start.y:.6f}",
            f"{start.z:.6f}",
            f"{end.x:.6f}",
            f"{end.y:.6f}",
            f"{end.z:.6f}",
        )
        return hashes

    # FabJoin.__post_init__():
    def __post_init__(self) -> None:
        """Initialize a single FabJoin."""
        # Make private copies of everything.
        copy: Vector = Vector()
        self._Start += copy
        self._End += copy

    # FabJoin.Name():
    @property
    def Name(self) -> str:
        """Return FabJoin Name."""
        return self._Name

    # FabJoin.Fasten():
    @property
    def Fasten(self) -> FabFasten:
        """Return FabJoin FabFasten."""
        return self._Fasten

    # FabJoin.Start():
    @property
    def Start(self) -> str:
        """Return FabJoin start point."""
        return self._Start

    # FabJoin.End():
    @property
    def End(self) -> str:
        """Return FabJoin end point."""
        return self._End

    # FabJoin.normal_aligned():
    def normal_aligned(self, test_normal: Vector) -> bool:
        """Return whether the normal is aligned with the FabJoin."""
        EPSILON = 1.0e-8
        join_direction: Vector = self._Start - self.End
        join_normal: Vector = join_direction / join_direction.Length
        test_normal = test_normal / test_normal.Length
        same_direction: bool = (join_normal - test_normal).Length < EPSILON
        opposite_direction: bool = (join_normal + test_normal).Length < EPSILON
        return same_direction or opposite_direction

    @staticmethod
    def _unit_tests() -> None:
        """Run FabJoint unit tests."""
        brass: FabMaterial = FabMaterial(("brass",), "orange")
        apex_head: FabHead = FabHead("PH", "Brass Philips Pan Head",
                                           brass, FabHead.PAN_HEAD, FabHead.PHILIPS_DRIVE)
        options: Tuple[FabOption, ...] = (apex_head,)
        apex_fasten: FabFasten = FabFasten("Test", "#4-40", options)
        start: Vector = Vector(0, 0, 0)
        stop: Vector = Vector(1, 1, 1)
        apex_join: FabJoin = FabJoin("Test", apex_fasten, start, stop)
        _ = apex_join


def _unit_tests() -> None:
    """Run unit tests."""
    FabOption._unit_tests()
    FabHead._unit_tests()
    FabFasten._unit_tests()
    FabNut._unit_tests()
    FabWasher._unit_tests()
    FabJoin._unit_tests()


if __name__ == "__main__":
    _unit_tests()
