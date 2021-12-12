# Model: An interface to FreeCAD Sketches.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class ModelCircle](#modelcircle)
  * 2.1 [ModelCircle.\_\_post\_init\_\_](#modelcircle---post-init--)
  * 2.2 [ModelCircle.get\_geometries](#modelcircle-get-geometries)
  * 2.3 [ModelCircle.produce](#modelcircle-produce)
  * 2.4 [ModelFile.\_\_enter\_\_](#modelfile---enter--)
  * 2.5 [ModelFile.\_\_exit\_\_](#modelfile---exit--)
  * 2.6 [ModelFile.\_\_post\_init\_\_](#modelfile---post-init--)
  * 2.7 [ModelFile.produce](#modelfile-produce)
* 3 [Class ModelGeometry](#modelgeometry)
  * 3.1 [ModelGeometry.produce](#modelgeometry-produce)
* 4 [Class ModelHole](#modelhole)
  * 4.1 [ModelHole.\_\_post\_init\_\_](#modelhole---post-init--)
  * 4.2 [ModelHole.get\_name](#modelhole-get-name)
  * 4.3 [ModelHole.produce](#modelhole-produce)
* 5 [Class ModelMount](#modelmount)
  * 5.1 [ModelMount.\_\_post\_init\_\_](#modelmount---post-init--)
  * 5.2 [ModelMount.produce](#modelmount-produce)
* 6 [Class ModelOperation](#modeloperation)
  * 6.1 [ModelOperation.get\_name](#modeloperation-get-name)
* 7 [Class ModelPad](#modelpad)
  * 7.1 [ModelPad.\_\_post\_init\_\_](#modelpad---post-init--)
  * 7.2 [ModelPad.get\_name](#modelpad-get-name)
  * 7.3 [ModelPad.produce](#modelpad-produce)
* 8 [Class ModelPart](#modelpart)
  * 8.1 [ModelPart.\_\_post\_init\_\_](#modelpart---post-init--)
  * 8.2 [ModelPart.produce](#modelpart-produce)
* 9 [Class ModelPocket](#modelpocket)
  * 9.1 [ModelPocket.get\_name](#modelpocket-get-name)
  * 9.2 [ModelPocket.produce](#modelpocket-produce)
* 10 [Class ModelPolygon](#modelpolygon)
  * 10.1 [ModelPolygon.\_\_post\_init\_\_](#modelpolygon---post-init--)
  * 10.2 [ModelPolygon.compute\_arcs](#modelpolygon-compute-arcs)
  * 10.3 [ModelPolygon.compute\_lines](#modelpolygon-compute-lines)
  * 10.4 [ModelPolygon.get\_geometries](#modelpolygon-get-geometries)
  * 10.5 [ModelPolygon.produce](#modelpolygon-produce)
  * 10.6 [ModelPolygon.unit\_test](#modelpolygon-unit-test)
* 11 [Class \_ModelArc](#-modelarc)
  * 11.1 [\_ModelArc.produce](#-modelarc-produce)
  * 11.2 [\_ModelCircle.produce](#-modelcircle-produce)
* 12 [Class \_ModelFillet](#-modelfillet)
  * 12.1 [\_ModelFillet.\_\_post\_init\_\_](#-modelfillet---post-init--)
  * 12.2 [\_ModelFillet.compute\_arc](#-modelfillet-compute-arc)
  * 12.3 [\_ModelFillet.double\_link](#-modelfillet-double-link)
* 13 [Class \_ModelGeometry](#-modelgeometry)
* 14 [Class \_ModelLine](#-modelline)
  * 14.1 [\_ModelLine.produce](#-modelline-produce)
  * 14.2 [ModelPocket\_\_post\_init\_\_](#modelpocket--post-init--)

## 1 <a name="introduction"></a>Introduction


## 2 Class ModelCircle <a name="modelcircle"></a>

class ModelCircle(ModelGeometry):

ModelCircle: A circle with a center and a radius.

Attributes:
* *Center* (Vector): The circle center.
* *Diameter* (float): The diameter in radians.


### 2.1 ModelCircle.\_\_post\_init\_\_ <a name="modelcircle---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Make private copy of Center.

### 2.2 ModelCircle.get\_geometries <a name="modelcircle-get-geometries"></a>

def *get\_geometries*(self) -> Tuple[\_ModelGeometry, ...]:

Return the ModelPolygon lines and arcs.

### 2.3 ModelCircle.produce <a name="modelcircle-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*) -> Tuple[Part.Part2DObject, ...]:

Produce the FreeCAD objects needed for ModelPolygon.

### 2.4 ModelFile.\_\_enter\_\_ <a name="modelfile---enter--"></a>

def \_\_enter\_\_(self) -> "ModelFile":

Open the ModelFile.

### 2.5 ModelFile.\_\_exit\_\_ <a name="modelfile---exit--"></a>

def \_\_exit\_\_(self, *exec\_type*, *exec\_value*, *exec\_table*) -> None:

Close the ModelFile.

### 2.6 ModelFile.\_\_post\_init\_\_ <a name="modelfile---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Initialize the AppDocument.

### 2.7 ModelFile.produce <a name="modelfile-produce"></a>

def *produce*(self) -> None:

Produce all of the ModelPart's.

## 3 Class ModelGeometry <a name="modelgeometry"></a>

class ModelGeometry(object):

ModelGeometry: The base class for ModelPolygon and ModelCircle.

### 3.1 ModelGeometry.produce <a name="modelgeometry-produce"></a>

def *produce*(self, *model\_context*:  ModelFile, *prefix*:  *str*) -> Tuple[Part.Part2DObject, ...]:

Produce the necessary FreeCAD objects for the ModelGeometry.

## 4 Class ModelHole <a name="modelhole"></a>

class ModelHole(ModelOperation):

ModelHole: A FreeCAD PartDesign Pocket operation.

Attributes:
    *Circle* (ModelCircle): The Circle to drill.
    *Depth* (float): The depth
    *Name* (str): The operation name.


### 4.1 ModelHole.\_\_post\_init\_\_ <a name="modelhole---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify ModelPad values.

### 4.2 ModelHole.get\_name <a name="modelhole-get-name"></a>

def *get\_name*(self) -> *str*:

Return ModelHole name.

### 4.3 ModelHole.produce <a name="modelhole-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*) -> None:

Produce the Pad.

## 5 Class ModelMount <a name="modelmount"></a>

class ModelMount(object):

ModelMount: An operations plane that can be oriented for subsequent machine operations.

This class basically corresponds to a FreeCad Datum Plane.  It is basically the surface
to which the 2D ModelGeometry's are mapped onto prior to performing each operation.
This class is immutable (i.e. frozen.)

Attributes:
* *Contact* (Vector): A point on the plane.
* *Normal* (Vector): A normal to the plane
* *North* (Vector):
  A vector in the plane that specifies the north direction when mounted  in a machining vice.
* *Operations* (Tuple[ModelOperation, ...]): The operations to perform.
* *Name*: (str): The name of the ModelPlane.


### 5.1 ModelMount.\_\_post\_init\_\_ <a name="modelmount---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify that ModelMount arguments are valid.

### 5.2 ModelMount.produce <a name="modelmount-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*) -> None:

Process the ModelMount.

## 6 Class ModelOperation <a name="modeloperation"></a>

class ModelOperation(object):

ModelOperation: An base class for operations -- ModelPad, ModelPocket, ModelHole, etc.

All model operations are immutable (i.e. frozen.)

### 6.1 ModelOperation.get\_name <a name="modeloperation-get-name"></a>

def *get\_name*(self) -> *str*:

Return ModelOperation name.

## 7 Class ModelPad <a name="modelpad"></a>

class ModelPad(ModelOperation):

ModelPad: A FreeCAD PartDesign Pad operation.

Attributes:
    *Geometry* (ModelGeometry): The ModlePolygon or ModelCircle to pad with.
    *Depth* (float): The depth to pad to in millimeters.
    *Name* (str): The operation name.


### 7.1 ModelPad.\_\_post\_init\_\_ <a name="modelpad---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify ModelPad values.

### 7.2 ModelPad.get\_name <a name="modelpad-get-name"></a>

def *get\_name*(self) -> *str*:

Return ModelPad name.

### 7.3 ModelPad.produce <a name="modelpad-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*) -> None:

Produce the Pad.

## 8 Class ModelPart <a name="modelpart"></a>

class ModelPart(object):

Model: Represents a single part constructed using FreeCAD Part Design paradigm.

Attributes:
* *Material*: The material to use.
* *Color*: The color to use.
* *Mounts* (Tuple[ModelMount, ...]): The various model mounts to use to construct the part.
* *Name*: The model name.


### 8.1 ModelPart.\_\_post\_init\_\_ <a name="modelpart---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify ModelPart arguments.

### 8.2 ModelPart.produce <a name="modelpart-produce"></a>

def *produce*(self, *model\_file*:  ModelFile) -> None:

Produce the ModelPart.

## 9 Class ModelPocket <a name="modelpocket"></a>

class ModelPocket(ModelOperation):

ModelPocket: A FreeCAD PartDesign Pocket operation.

Attributes:
    *Geometry* (ModelGeometry): The Polygon or Circle to pocket.
    *Depth* (float): The depth
    *Name* (str): The operation name.


### 9.1 ModelPocket.get\_name <a name="modelpocket-get-name"></a>

def *get\_name*(self) -> *str*:

Return ModelPocket name.

### 9.2 ModelPocket.produce <a name="modelpocket-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*) -> None:

Produce the Pad.

## 10 Class ModelPolygon <a name="modelpolygon"></a>

class ModelPolygon(ModelGeometry):

ModelPolygon: An immutable polygon with rounded corners.

A ModelPolygon is represented as a sequence of corners (i.e. a Vector) where each corner can
optionally be filleted with a radius.  In order to make it easier to use, a corner can be
specified as simple Vector or as a tuple that specifes a Vector and a radius.  The radius
is in millimeters and can be provided as either Python int or float.  When an explicit
fillet radius is not specified, higher levels in the software stack will typically substitute
in a deburr radius for external corners and an interal tool radius for internal corners.
ModelPolygon's are frozen and can not be modified after creation.

Example:
     polygon: Model.ModelPolyon = Model.ModelPolygon((
         Vector(-10, -10, 0),  # Lower left (no radius)
         Vector(10, -10, 0),  # Lower right (no radius)
         (Vector(10, 10, 0), 5),  # Upper right (5mm radius)
         (Vector(-0, 10, 0), 5.5),  # Upper right (5.5mm radius)
     ), "Name")

Attributes:
* *Corners* (Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...]):
  See description below for more on corners.
* *Name* (str): The name of the polygon.  (Default: "")

Raises:
* ValueError for improper corner specifications.


### 10.1 ModelPolygon.\_\_post\_init\_\_ <a name="modelpolygon---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify that the corners passed in are correct.

### 10.2 ModelPolygon.compute\_arcs <a name="modelpolygon-compute-arcs"></a>

def *compute\_arcs*(self) -> None:

Create any Arc's needed for non-zero radius \_ModelFillet's.

### 10.3 ModelPolygon.compute\_lines <a name="modelpolygon-compute-lines"></a>

def *compute\_lines*(self) -> None:

Create Create any Line's need for \_ModelFillet's.

### 10.4 ModelPolygon.get\_geometries <a name="modelpolygon-get-geometries"></a>

def *get\_geometries*(self) -> Tuple[\_ModelGeometry, ...]:

Return the ModelPolygon lines and arcs.

### 10.5 ModelPolygon.produce <a name="modelpolygon-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*) -> Tuple[Part.Part2DObject, ...]:

Produce the FreeCAD objects needed for ModelPolygon.

### 10.6 ModelPolygon.unit\_test <a name="modelpolygon-unit-test"></a>

def *unit\_test*() -> None:

Do some unit tests.

## 11 Class \_ModelArc <a name="-modelarc"></a>

class \_ModelArc(\_ModelGeometry):

\_ModelArc: An internal representation an arc geometry.

Attributes:
* *Apex* (Vector): The fillet apex point.
* *Radius* (float): The arc radius in millimeters.
* *Center* (Vector): The arc center point.
* *Start* (Vector): The Arc start point.
* *Middle* (Vector): The Arc midpoint.
* *Finish* (Vector): The Arc finish point.
* *StartAngle* (float): The start arc angle in radians.
* *FinishAngle* (float): The finish arc angle in radiuns.
* *DeltaAngle* (float):
  The value to add to *StartAngle* to get *FinishAngle* (module 2 radians):


### 11.1 \_ModelArc.produce <a name="-modelarc-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*, *index*:  *int*) -> Part.Part2DObject:

Return line segment after moving it into Geometry group.

### 11.2 \_ModelCircle.produce <a name="-modelcircle-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*, *index*:  *int*) -> Part.Part2DObject:

Return line segment after moving it into Geometry group.

## 12 Class \_ModelFillet <a name="-modelfillet"></a>

class \_ModelFillet(object):

\_ModelFillet: An object that represents one fillet of a ModelPolygon.

Attributes:
* *Apex* (Vector): The apex corner point for the fillet.
* *Radius* (float): The fillet radius in millimeters.
* *Before* (\_ModelFillet): The previous \_ModelFillet in the ModelPolygon.
* *After* (\_ModelFillet): The next \_ModelFillet in the ModelPolygon.
* *Arc* (Optional[\_ModelArc]): The fillet Arc if Radius is non-zero.
* *Line* (Optional[\_ModelLine]): The line that connects to the previous \_ModelFillet


### 12.1 \_ModelFillet.\_\_post\_init\_\_ <a name="-modelfillet---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Initialize \_ModelFillet.

### 12.2 \_ModelFillet.compute\_arc <a name="-modelfillet-compute-arc"></a>

def *compute\_arc*(self, *tracing*:  *str* = "") -> \_ModelArc:

Return the arc associated with a \_ModelFillet with non-zero radius.

### 12.3 \_ModelFillet.double\_link <a name="-modelfillet-double-link"></a>

def *double\_link*(self) -> None:

Double link the \_ModelFillet's together.

## 13 Class \_ModelGeometry <a name="-modelgeometry"></a>

class \_ModelGeometry(object):

\_ModelGeometry: An Internal base class for \_ModelArc, \_ModelCircle, and \_ModelLine.

All \_ModelGeometry classes are immutable (i.e. frozen.)

## 14 Class \_ModelLine <a name="-modelline"></a>

class \_ModelLine(\_ModelGeometry):

\_ModelLine: An internal representation of a line segment geometry.

Attributes:
* *Start (Vector): The line segment start point.
* *Finish (Vector): The line segment finish point.


### 14.1 \_ModelLine.produce <a name="-modelline-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*, *index*:  *int*) -> Part.Part2DObject:

Return line segment after moving it into Geometry group.

### 14.2 ModelPocket\_\_post\_init\_\_ <a name="modelpocket--post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify ModelPad values.
