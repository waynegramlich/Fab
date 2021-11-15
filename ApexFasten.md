# ApexFasten: A Package for managing fasteners in the Apex system.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class ApexFasten](#apexfasten)
* 3 [Class ApexHead](#apexhead)
* 4 [Class ApexJoin](#apexjoin)
* 5 [Class ApexNut](#apexnut)
* 6 [Class ApexOption](#apexoption)
* 7 [Class ApexWasher](#apexwasher)
* 8 [Class ApexWasher](#apexwasher)

## 1 <a name="introduction"></a>Introduction


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


## 2 Class ApexFasten <a name="apexfasten"></a>

class ApexFasten:

ApexFastner: The class of Fastener to use.

Attributes:
* Name (str): ApexFasten Name.
* Profile (str): ApexFasten Profile.  Must be one of the ApexFasten constants --
  `ISO\_COARSE`, `ISO\_FINE`,  `UTS\_COARSE`, `UTS\_FINE`, and `UTS\_EXTRA\_FINE.
* Size (str): Standard fastener size.  Must be one of the ApexFasten constants --
  `UTS\_N1`, `UTS\_N2`, `UTS\_N3`, `UTS\_N4`, `UTS\_N5`, `UTS\_N6`, `UTS\_N8`, `UTS\_N10`, `UTS\_N12`,
  `UTS\_F1\_4`, `UTS\_F5\_16`, `UTS\_F3\_8`, `UTS\_F7\_16`, `UTS\_F1\_2`, `UTS\_F9\_16`, `UTS\_F5\_8`,
  `UTS\_F3\_4`, `UTS\_F3\_4`, `M1\_6`, `M2`, `M2\_5`, `M3`, `M3\_5`, `M4`, `M5`, `M6`, `M8`, `M10`,
  `M12`, `M14`, `M16`, `M18,  `M20`, `M22`, `M24`, `M27`, `M30`, `M36`, `M42`, `M48`, `M56`,
  `M68.


## 3 Class ApexHead <a name="apexhead"></a>

class ApexHead(ApexOption):

Represents the Head of the ApexFastener.

Attributes:
* *Name* (str): The name for this head.
* *Detail* (str): Short ApexHead description.
* *Material* (ApexMaterial): The ApexHead fastener material.
* *Shape* (str): The ApexHead shape.
* *Drive* (str): The ApexH drive .


## 4 Class ApexJoin <a name="apexjoin"></a>

class ApexJoin(object):

ApexJoin: Specifies a single fastener instance.

Attributes:
* Fasten (ApexFasten): ApexFasten object to use for basic dimensions.
* Start (Vector): Start point for ApexJoin.
* End (Vector): End point for ApexJoin.
* Options (Tuple[ApexOption]): The various options associated with the ApexJoin.


## 5 Class ApexNut <a name="apexnut"></a>

class ApexNut(ApexOption):

ApexNut: A class the represents a fastener nut.

Attributes:
* Name (str): Nut name.
* Detail (str): More nut detail.
* Sides (int): The number of nut sides (either 4 or 6.)
* Width (float): The Nut width between 2 opposite faces.
* Thickness (float): The nut thickness in millimeters.
* Material (ApexMaterial): The nut material


## 6 Class ApexOption <a name="apexoption"></a>

class ApexOption(object):

ApexOption: Base class for ApexFasten options (e.g. washers, nuts, etc...).

Attributes:
* *Name* (str): The option name.
* *Detail* (str): More detailed information about the option.


## 7 Class ApexWasher <a name="apexwasher"></a>

class ApexWasher(ApexOption):

ApexWahser: Represents a washer.

Constants:
* PLAIN: Plain washer.
* INTERNAL\_LOCK: Internal tooth lock washer.
* EXTERNAL\_LOCK: External tooth lock washer.
* SPLIT\_LOCK: Split ring lock washer.

Attributes:
* *Name* (str): The washer name.
* *Detail* (str): More detail about the ApexWasher.
* *Inner* (float): The Inner diameter in millimeters.
* *Outer* (float): The Outer diameter in millimeters.
* *Thickness* (float): The thickness in millimeters.
* *Material* (ApexMaterial): The Material the washer is made out of.
* *Kind* (str): The washer kind -- one of following ApexWasher constants --
  `PLAIN`, `INTERNAL\_LOCK`, `EXTERNAL\_LOCK`, or `SPLIT\_LOCK`.


### 8.0 ApexWash <a name="apexwasher"></a>

def \_\_post\_init\_\_(self):

Post process ApexWasher looking for errors.
