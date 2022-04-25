# FabJoins: FabJoins: Fab fastener management system.
While the most common fasteners are screws and bolts, there are others like rivets, set screws,
cotter pins, etc.  This package centralizes all of the issues associated with fasteners
so that changing a fastener does not become a nightmare of having to individually find
each fastener and make manual changes to each one.  The change is made in once place and
it propagates to all locations where the fastener is used.

The FabJoins module deals with the following issues:
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

The basic bottom up class hierarchy is:

* FabOption: A base class for the sub-classes immediately below:
  * FabHead: The fastener head definition along with counter sink/bore information.
  * FabWasher: washer that is attached on the fastener.
  * FabNut: A nut that threads onto the fastener.
* FabFasten: A profile for a set of related hardware for using a fastener.
* FabJoin: A specific instance of a FabBasten that has a start and end point.

I addition the "public" classes listed immediately above.  There are a number of "private" classes
of the form `Fab_` that are used to implement everything.  The interfaces to the classes are
not stable and can be changed at will by the developers; thus, they should not be depended upon.

A FabFasten basically lists a thread profile (i.e. #4-4, M3x0.5, etc), the driver head,
associated lock washers, regular washers, nuts, etc.  These are specified as a list
of FabOption's (i.e. FabHead, FabWasher, FabNut, etc.)

A FabJoin specifies a FabJoins with both a start point and an end point.  The first end point is
the specifies a point just under the screw/bolt head and any regular/lock washers just below
the head.  The end point is where any additional regular/lock washers and nuts go at the other
end of the fastener.

The Part module has three basic FabOperation's -- FabThread, FabClose, and FabLoose,
which vary the diameter of the Part Hole.  These operations take a FabJoin, verifies that
the fastener is perpendicular to the mount plane, and drills the correct diameter hole to
the correct depth.

Eventually, the system will create a BOM (Bill Of Materials) that lists all of the needed
hardware.

## Table of Contents (alphabetical order):

* 1 Class: [FabFasten](#fabjoins--fabfasten):
  * 1.1 [get_hash()](#fabjoins----get-hash): Return FabFasten hash.
  * 1.2 [get_diameter()](#fabjoins----get-diameter): Return actual diameter based on request hole kind.
* 2 Class: [FabHead](#fabjoins--fabhead):
* 3 Class: [FabJoin](#fabjoins--fabjoin):
  * 3.1 [get_hash()](#fabjoins----get-hash): Return FabJoin hash.
  * 3.2 [normal_aligned()](#fabjoins----normal-aligned): Return whether the normal is aligned with the FabJoin.
* 4 Class: [FabNut](#fabjoins--fabnut):
* 5 Class: [FabOption](#fabjoins--faboption):
  * 5.1 [get_hash()](#fabjoins----get-hash): Return FabOption hash.
* 6 Class: [FabWasher](#fabjoins--fabwasher):
* 7 Class: [Fab_DrillChoice](#fabjoins--fab-drillchoice):
* 8 Class: [Fab_DrillTap](#fabjoins--fab-drilltap):
* 9 Class: [Fab_FastenTables](#fabjoins--fab-fastentables):
* 10 Class: [Fab_Fastener](#fabjoins--fab-fastener):
* 11 Class: [Fab_IDrillTap](#fabjoins--fab-idrilltap):
* 12 Class: [Fab_MDrillTap](#fabjoins--fab-mdrilltap):

## <a name="fabjoins--fabfasten"></a>1 Class FabFasten:

The class of Fastener to use.
Attributes:
* Name (str): FabFasten Name.
* ThreadName (str): A thread selection (e.g. "M3x.5", "#4-40", "1/4-20")
* Options (Tuple[FabOption, ...]): Various Head/Tail options for fastener stack

Constructor:
* FabFasten(Name, ThreadName, Options)

### <a name="fabjoins----get-hash"></a>1.1 `FabFasten.`get_hash():

FabFasten.get_hash(self) -> Tuple[Any, ...]:

Return FabFasten hash.

### <a name="fabjoins----get-diameter"></a>1.2 `FabFasten.`get_diameter():

FabFasten.get_diameter(self, kind: str) -> float:

Return actual diameter based on request hole kind.


## <a name="fabjoins--fabhead"></a>2 Class FabHead:

Represents the Head of the FabFastener.
Attributes:
* *Name* (str): The name for this head.
* *Detail* (str): Short FabHead description.
* *Material* (FabMaterial): The FabHead fastener material.
* *Shape* (str): The FabHead shape.
* *Drive* (str): The FabHead drive.

Constructor:
* FabHead(Name, Detail, Material, Shape, Drive)


## <a name="fabjoins--fabjoin"></a>3 Class FabJoin:

Specifies a single fastener instance.
Attributes:
* Name (str): A name used for error reporting.
* Fasten (FabFasten): FabFasten object to use for basic dimensions.
* Start (Vector): Start point for FabJoin.
* End (Vector): End point for FabJoin.

Constructor:
* FabJoin(Name, Fasten, Start, End)

### <a name="fabjoins----get-hash"></a>3.1 `FabJoin.`get_hash():

FabJoin.get_hash(self) -> Tuple[Any, ...]:

Return FabJoin hash.

### <a name="fabjoins----normal-aligned"></a>3.2 `FabJoin.`normal_aligned():

FabJoin.normal_aligned(self, test_normal: cadquery.occ_impl.geom.Vector) -> bool:

Return whether the normal is aligned with the FabJoin.


## <a name="fabjoins--fabnut"></a>4 Class FabNut:

A class the represents a fastener nut.
Attributes:
* Name (str): Nut name.
* Detail (str): More nut detail.
* Sides (int): The number of nut sides (either 4 or 6.)
* Width (float): The Nut width between 2 opposite faces.
* Thickness (float): The nut thickness in millimeters.
* Material (FabMaterial): The nut material

Constructor:
* FabNut(Name, Detail, Sides, Width, Thickness, Material)


## <a name="fabjoins--faboption"></a>5 Class FabOption:

Base class for FabFasten options (e.g. washers, nuts, etc...).
Attributes:
* *Name* (str): The option name.
* *Detail* (str): More detailed information about the option.

Constructor:
* This is meant to be sub-classed, so this class should never be constructed manually.

### <a name="fabjoins----get-hash"></a>5.1 `FabOption.`get_hash():

FabOption.get_hash(self) -> Tuple[Any, ...]:

Return FabOption hash.


## <a name="fabjoins--fabwasher"></a>6 Class FabWasher:

Represents a washer.
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


## <a name="fabjoins--fab-drillchoice"></a>7 Class Fab_DrillChoice:

Preferred Metric and Imperial drill sizes.
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


## <a name="fabjoins--fab-drilltap"></a>8 Class Fab_DrillTap:

Drill/Tap diameters and drill selections.
Attributes:
* *Name* (str): Name of drill/tap selections.
* *Thread75* (Fab_DrillChoice):  The drill choice for 75% thread operations.
* *Thread50* (Fab_DrillChoice):  The drill choice for 50% thread operations.
* *Close* (Fab_DrillChoice):  The drill choice for a close fit hole.
* *Standard* (Fab_DrillChoice):  The drill choice for a standard fit hole.

Constructor:
* Fab_DrillTap(Name, Thread75, Thread50, Close, Standard)


## <a name="fabjoins--fab-fastentables"></a>9 Class Fab_FastenTables:

Tables of metric/imperial screws and bolts.
This is a class only object, so no constructor is ever used.


## <a name="fabjoins--fab-fastener"></a>10 Class Fab_Fastener:

Imperial/Metric fastener information.
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


## <a name="fabjoins--fab-idrilltap"></a>11 Class Fab_IDrillTap:

Imperial Screw/Bolt Drill Selection.
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


## <a name="fabjoins--fab-mdrilltap"></a>12 Class Fab_MDrillTap:

Metric drill/tap information.
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



