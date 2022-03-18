# Join: Join: A package for managing fasteners in the Fab system.
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
  line to connect them all.  (Not done implemented.)
* Fastener WorkBench:
  The FreeCAD Fasteners workbench is used wherever possible.

The basic class hierarchy is:

* FabJoiner: A profile for a set of related hardware for using a fastener.
* FabJoinerOption: A base class for the sub-classes immediately below:
  * FabHead: The fastener head definition along with counter sink/bore information.
  * FabWasher: washer that is attached on the fastener.
  * FabNut: A nut that threads onto the fastener.
* FabJoin: A specific instance of fastener that has a start and end point.

A FabJoiner basically lists a thread profile (i.e. #4-4, M3x0.5, etc), the driver head,
associated lock washers, regular washers, nuts, etc.  These are specified as a list
of FabJoinerOption's (i.e. FabHead, FabWasher, FabNut, etc.)

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

## Table of Contents (alphabetical order):

* 1 Class: [FabDrillChoice](#join--fabdrillchoice):
* 2 Class: [FabDrillTap](#join--fabdrilltap):
* 3 Class: [FabFasten](#join--fabfasten):
  * 3.1 [get_hash()](#join----get-hash): Return FabFasten hash.
  * 3.2 [get_diameter()](#join----get-diameter): Return actual diameter based on request hole kind.
* 4 Class: [FabFastenTables](#join--fabfastentables):
* 5 Class: [FabHead](#join--fabhead):
* 6 Class: [FabJoin](#join--fabjoin):
  * 6.1 [get_hash()](#join----get-hash): Return FabJoin hash.
  * 6.2 [normal_aligned()](#join----normal-aligned): Return whether the normal is aligned with the FabJoin.
* 7 Class: [FabNut](#join--fabnut):
* 8 Class: [FabOption](#join--faboption):
  * 8.1 [get_hash()](#join----get-hash): Return FabOption hash.
* 9 Class: [FabWasher](#join--fabwasher):

## <a name="join--fabdrillchoice"></a>1 Class FabDrillChoice:

Preferred Metric and Imperial drill sizes.
The final choice of hole sizes typically depends upon the available hardware.
In North America, these the pre-metric size drills (fractional, letter, number) are
readily available.  Pretty much everywhere else, these are the metric drill sizes
are more readily available.

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


## <a name="join--fabdrilltap"></a>2 Class FabDrillTap:

Drill/Tap diameters and drill selections.


## <a name="join--fabfasten"></a>3 Class FabFasten:

FabFastner: The class of Fastener to use.
Attributes:
* Name (str): FabFasten Name.
* ThreadName (str): A thread selection (e.g. "M3x.5", "#4-40", "1/4-20")
* Options (Tuple[FabOption, ...]): Various Head/Tail options for fastener stack

### <a name="join----get-hash"></a>3.1 `FabFasten.`get_hash():

FabFasten.get_hash(self) -> Tuple[Any, ...]:

Return FabFasten hash.

### <a name="join----get-diameter"></a>3.2 `FabFasten.`get_diameter():

FabFasten.get_diameter(self, kind: str) -> float:

Return actual diameter based on request hole kind.


## <a name="join--fabfastentables"></a>4 Class FabFastenTables:

Tables of metric/imperial screws and bolts.


## <a name="join--fabhead"></a>5 Class FabHead:

Represents the Head of the FabFastener.
Attributes:
* *Name* (str): The name for this head.
* *Detail* (str): Short FabHead description.
* *Material* (FabMaterial): The FabHead fastener material.
* *Shape* (str): The FabHead shape.
* *Drive* (str): The FabH drive .


## <a name="join--fabjoin"></a>6 Class FabJoin:

Specifies a single fastener instance.
Attributes:
* Name (str): A name used for error reporting.
* Fasten (FabFasten): FabFasten object to use for basic dimensions.
* Start (Vector): Start point for FabJoin.
* End (Vector): End point for FabJoin.

### <a name="join----get-hash"></a>6.1 `FabJoin.`get_hash():

FabJoin.get_hash(self) -> Tuple[Any, ...]:

Return FabJoin hash.

### <a name="join----normal-aligned"></a>6.2 `FabJoin.`normal_aligned():

FabJoin.normal_aligned(self, test_normal: Base.Vector) -> bool:

Return whether the normal is aligned with the FabJoin.


## <a name="join--fabnut"></a>7 Class FabNut:

A class the represents a fastener nut.
Attributes:
* Name (str): Nut name.
* Detail (str): More nut detail.
* Sides (int): The number of nut sides (either 4 or 6.)
* Width (float): The Nut width between 2 opposite faces.
* Thickness (float): The nut thickness in millimeters.
* Material (FabMaterial): The nut material


## <a name="join--faboption"></a>8 Class FabOption:

Base class for FabFasten options (e.g. washers, nuts, etc...).
Attributes:
* *Name* (str): The option name.
* *Detail* (str): More detailed information about the option.

### <a name="join----get-hash"></a>8.1 `FabOption.`get_hash():

FabOption.get_hash(self) -> Tuple[Any, ...]:

Return FabOption hash.


## <a name="join--fabwasher"></a>9 Class FabWasher:

FabWahser: Represents a washer.
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



