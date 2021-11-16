# ApexFasten: A Package for managing fasteners in the Apex system.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class ApexCounter](#apexcounter)
* 3 [Class ApexNut](#apexnut)
* 4 [Class ApexScrew](#apexscrew)
  * 4.1 [ApexScrew.\_\_post\_init\_\_](#apexscrew---post-init--)
  * 4.2 [ApexScrew.\_unit\_tests](#apexscrew--unit-tests)
* 5 [Class ApexStack](#apexstack)
  * 5.1 [ApexStack.\_\_post\_init\_\_](#apexstack---post-init--)
  * 5.2 [ApexStack.\_\_repr\_\_](#apexstack---repr--)
  * 5.3 [ApexStack.\_\_str\_\_](#apexstack---str--)
  * 5.4 [ApexStack.\_unit\_tests](#apexstack--unit-tests)
* 6 [Class ApexStackBody](#apexstackbody)
  * 6.1 [ApexStackBody.\_\_post\_init\_\_](#apexstackbody---post-init--)
  * 6.2 [ApexStackBody.\_\_repr\_\_](#apexstackbody---repr--)
  * 6.3 [ApexStackBody.\_\_str\_\_](#apexstackbody---str--)
  * 6.4 [ApexStackBody.\_unit\_tests](#apexstackbody--unit-tests)
* 7 [Class ApexStackOption](#apexstackoption)
* 8 [Class ApexWasher](#apexwasher)
* 9 [Class ApexWasher](#apexwasher)

## 1 <a name="introduction"></a>Introduction


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


## 2 Class ApexCounter <a name="apexcounter"></a>

class ApexCounter(ApexStackOption):

ApexCounter: A class the represents a fastener counter.

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


## 3 Class ApexNut <a name="apexnut"></a>

class ApexNut(ApexStackOption):

ApexNut: A class the represents a fastener nut.

Attributes:
* Name (str): Nut name.
* Detail (str): More nut detail.
* Material (ApexMaterial): The nut material
* Sides (int): The number of nut sides (either 4 or 6.)
* Width (float): The Nut width between 2 opposite faces.
* Thickness (float): The nut thickness in millimeters.


## 4 Class ApexScrew <a name="apexscrew"></a>

class ApexScrew(object):

ApexScrew: Specifies a single fastener instance.

Attributes:
* Stack (ApexStack): ApexStack object to use for basic dimensions.
* Start (Vector): Start point for ApexJoin.
* End (Vector): End point for ApexJoin.


### 4.1 ApexScrew.\_\_post\_init\_\_ <a name="apexscrew---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Initialize a single ApexJoin.

### 4.2 ApexScrew.\_unit\_tests <a name="apexscrew--unit-tests"></a>

def \_unit\_tests() -> None:

Run ApexJoint unit tests.

## 5 Class ApexStack <a name="apexstack"></a>

class ApexStack:

ApexStack: A class consisting of an ApexStackBody and associated ApexStackOptions.

Attributes:
* Name (str): The name of the ApexStack.
* Detail (str): A more detailed description of the ApexStack.
* StackBody (ApexStackBody): The basic screw/bolt to use.
* HeadOptions: (Tuple[ApexStackOption, ...]): Additional washers, etc mounted at the head.
* TailOptions: (Tuple[ApexStackOption, ...]): Additional washers, etc mounted at the tail.


### 5.1 ApexStack.\_\_post\_init\_\_ <a name="apexstack---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify the ApexStack values.

### 5.2 ApexStack.\_\_repr\_\_ <a name="apexstack---repr--"></a>

def \_\_repr\_\_(self) -> *str*:

Return ApexStack as a string.

### 5.3 ApexStack.\_\_str\_\_ <a name="apexstack---str--"></a>

def \_\_str\_\_(self) -> *str*:

Return ApexStack as a string.

### 5.4 ApexStack.\_unit\_tests <a name="apexstack--unit-tests"></a>

def \_unit\_tests(cls) -> None:

Run unit tests for ApexStack.

## 6 Class ApexStackBody <a name="apexstackbody"></a>

class ApexStackBody:

ApexFastner: The class of Fastener to use.

Attributes:
* Name (str): ApexStack Name.
* Detail (str): A more detailed description of the ApexStack.
* Pitch (str): ApexStack Profile.  Must be one of the ApexStack constants --
  `ISO\_COARSE`, `ISO\_FINE`,  `UTS\_COARSE`, `UTS\_FINE`, and `UTS\_EXTRA\_FINE.
* Size (str): Standard fastener size.  Must be one of the ApexStack constants --
  `UTS\_N1`, `UTS\_N2`, `UTS\_N3`, `UTS\_N4`, `UTS\_N5`, `UTS\_N6`, `UTS\_N8`, `UTS\_N10`, `UTS\_N12`,
  `UTS\_F1\_4`, `UTS\_F5\_16`, `UTS\_F3\_8`, `UTS\_F7\_16`, `UTS\_F1\_2`, `UTS\_F9\_16`, `UTS\_F5\_8`,
  `UTS\_F3\_4`, `UTS\_F3\_4`, `M1\_6`, `M2`, `M2\_5`, `M3`, `M3\_5`, `M4`, `M5`, `M6`, `M8`, `M10`,
  `M12`, `M14`, `M16`, `M18,  `M20`, `M22`, `M24`, `M27`, `M30`, `M36`, `M42`, `M48`, `M56`,
  `M68.
* Material (ApexMaterial): The material that the primary fastener is made out of.
* Head (str): The screw head shape (e.g. FLAT, OVAL, ...)
* Drive (str): The screw drive (e.g. PHILIPS, SLOT, ...)


### 6.1 ApexStackBody.\_\_post\_init\_\_ <a name="apexstackbody---post-init--"></a>

def \_\_post\_init\_\_(self):

Verify that ApexStack is properly initialized.

### 6.2 ApexStackBody.\_\_repr\_\_ <a name="apexstackbody---repr--"></a>

def \_\_repr\_\_(self) -> *str*:

Return string representation of ApexStack.

### 6.3 ApexStackBody.\_\_str\_\_ <a name="apexstackbody---str--"></a>

def \_\_str\_\_(self) -> *str*:

Return string representation of ApexStack.

### 6.4 ApexStackBody.\_unit\_tests <a name="apexstackbody--unit-tests"></a>

def \_unit\_tests() -> None:

Run ApexStackBody unit tests.

## 7 Class ApexStackOption <a name="apexstackoption"></a>

class ApexStackOption(object):

ApexStackOption: Base class for ApexFasten options (e.g. washers, nuts, etc...).

Attributes:
* *Name* (str): The option name.
* *Detail* (str): More detailed information about the option.


## 8 Class ApexWasher <a name="apexwasher"></a>

class ApexWasher(ApexStackOption):

ApexWahser: Represents a washer.

Constants:
* PLAIN: Plain washer.
* INTERNAL\_LOCK: Internal tooth lock washer.
* EXTERNAL\_LOCK: External tooth lock washer.
* SPLIT\_LOCK: Split ring lock washer.

Attributes:
* *Name* (str): The washer name.
* *Detail* (str): More detail about the ApexWasher.
* *Material* (ApexMaterial): The Material the washer is made out of.
* *Inner* (float): The Inner diameter in millimeters.
* *Outer* (float): The Outer diameter in millimeters.
* *Thickness* (float): The thickness in millimeters.
* *Kind* (str): The washer kind -- one of following ApexWasher constants --
  `PLAIN`, `INTERNAL\_LOCK`, `EXTERNAL\_LOCK`, or `SPLIT\_LOCK`.


### 9.0 ApexWash <a name="apexwasher"></a>

def \_\_post\_init\_\_(self):

Post process ApexWasher looking for errors.
