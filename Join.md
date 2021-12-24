# Join: A package for managing fasteners in the Model system.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class ModelFasten](#modelfasten)
* 3 [Class ModelHead](#modelhead)
* 4 [Class ModelJoin](#modeljoin)
* 5 [Class ModelNut](#modelnut)
* 6 [Class ModelOption](#modeloption)
* 7 [Class ModelWasher](#modelwasher)
* 8 [Class ModelWasher](#modelwasher)

## 1 <a name="introduction"></a>Introduction


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

* ModelJoiner: A profile for a set of related hardware for using a fastener.
* ModelJoinerOption: A base class for the sub-classes immediately below:
  * ModelHead: The fastener head definition along with counter sink/bore information.
  * ModelWasher: washer that is attached on the fastener.
  * ModelNut: A nut that threads onto the fastener.
* ModelJoin: A specific instance of fastener that has a start and end point.

A ModelJoiner basically lists a thread profile (i.e. #4-4, M3x0.5, etc), the driver head,
associated lock washers, regular washers, nuts, etc.  These are specified as a list
of ModelJoinerOption's (i.e. ModelHead, ModelWasher, ModelNut, etc.)

A ModelJoin specifies a ModelJoiner, a start point and an end point.  The first end point is
the specifies a point just under the screw/bolt head and any regular/lock washers just below
the head.  The end point is where any additional regular/lock washers and nuts go at the other
end of the fastener.

The Part module has three basic ModelOperation's -- ModelThread, ModelClose, and ModelLoose,
which vary the diameter of the Part Hole.  These operations take a ModelJoin, verifies that
the fastener is perpendicular to the mount plane, and drills the correct diameter hole to
the correct depth.

Eventually, the system will create a BOM (Bill Of Materials) that lists all of the needed
hardware.


## 2 Class ModelFasten <a name="modelfasten"></a>

class ModelFasten:

ModelFastner: The class of Fastener to use.

Attributes:
* Name (str): ModelFasten Name.
* Profile (str): ModelFasten Profile.  Must be one of the ModelFasten constants --
  `ISO\_COARSE`, `ISO\_FINE`,  `UTS\_COARSE`, `UTS\_FINE`, and `UTS\_EXTRA\_FINE.
* Size (str): Standard fastener size.  Must be one of the ModelFasten constants --
  `UTS\_N1`, `UTS\_N2`, `UTS\_N3`, `UTS\_N4`, `UTS\_N5`, `UTS\_N6`, `UTS\_N8`, `UTS\_N10`, `UTS\_N12`,
  `UTS\_F1\_4`, `UTS\_F5\_16`, `UTS\_F3\_8`, `UTS\_F7\_16`, `UTS\_F1\_2`, `UTS\_F9\_16`, `UTS\_F5\_8`,
  `UTS\_F3\_4`, `UTS\_F3\_4`, `M1\_6`, `M2`, `M2\_5`, `M3`, `M3\_5`, `M4`, `M5`, `M6`, `M8`, `M10`,
  `M12`, `M14`, `M16`, `M18,  `M20`, `M22`, `M24`, `M27`, `M30`, `M36`, `M42`, `M48`, `M56`,
  `M68.


## 3 Class ModelHead <a name="modelhead"></a>

class ModelHead(ModelOption):

Represents the Head of the ModelFastener.

Attributes:
* *Name* (str): The name for this head.
* *Detail* (str): Short ModelHead description.
* *Material* (ApexMaterial): The ModelHead fastener material.
* *Shape* (str): The ModelHead shape.
* *Drive* (str): The ModelH drive .


## 4 Class ModelJoin <a name="modeljoin"></a>

class ModelJoin(object):

ModelJoin: Specifies a single fastener instance.

Attributes:
* Fasten (ModelFasten): ModelFasten object to use for basic dimensions.
* Start (Vector): Start point for ModelJoin.
* End (Vector): End point for ModelJoin.
* Options (Tuple[ModelOption]): The various options associated with the ModelJoin.


## 5 Class ModelNut <a name="modelnut"></a>

class ModelNut(ModelOption):

ModelNut: A class the represents a fastener nut.

Attributes:
* Name (str): Nut name.
* Detail (str): More nut detail.
* Sides (int): The number of nut sides (either 4 or 6.)
* Width (float): The Nut width between 2 opposite faces.
* Thickness (float): The nut thickness in millimeters.
* Material (ApexMaterial): The nut material


## 6 Class ModelOption <a name="modeloption"></a>

class ModelOption(object):

ModelOption: Base class for ModelFasten options (e.g. washers, nuts, etc...).

Attributes:
* *Name* (str): The option name.
* *Detail* (str): More detailed information about the option.


## 7 Class ModelWasher <a name="modelwasher"></a>

class ModelWasher(ModelOption):

ModelWahser: Represents a washer.

Constants:
* PLAIN: Plain washer.
* INTERNAL\_LOCK: Internal tooth lock washer.
* EXTERNAL\_LOCK: External tooth lock washer.
* SPLIT\_LOCK: Split ring lock washer.

Attributes:
* *Name* (str): The washer name.
* *Detail* (str): More detail about the ModelWasher.
* *Inner* (float): The Inner diameter in millimeters.
* *Outer* (float): The Outer diameter in millimeters.
* *Thickness* (float): The thickness in millimeters.
* *Material* (ApexMaterial): The Material the washer is made out of.
* *Kind* (str): The washer kind -- one of following ModelWasher constants --
  `PLAIN`, `INTERNAL\_LOCK`, `EXTERNAL\_LOCK`, or `SPLIT\_LOCK`.


### 8.0 ModelWash <a name="modelwasher"></a>

def \_\_post\_init\_\_(self):

Post process ModelWasher looking for errors.