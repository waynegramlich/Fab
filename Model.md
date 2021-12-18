# Model: An interface to FreeCAD Sketches.

Table of Contents:
* 1 [Introduction](#introduction):
* 2 [Class Box](#box)
  * 2.1 [Box.compute](#box-compute)
* 3 [Class ModelCircle](#modelcircle)
  * 3.1 [ModelCircle.\_\_post\_init\_\_](#modelcircle---post-init--)
  * 3.2 [ModelCircle.get\_geometries](#modelcircle-get-geometries)
  * 3.3 [ModelCircle.produce](#modelcircle-produce)
  * 3.4 [ModelFile.\_\_enter\_\_](#modelfile---enter--)
  * 3.5 [ModelFile.\_\_exit\_\_](#modelfile---exit--)
  * 3.6 [ModelFile.\_\_post\_init\_\_](#modelfile---post-init--)
  * 3.7 [ModelFile.\_unit\_tests](#modelfile--unit-tests)
  * 3.8 [ModelFile.produce](#modelfile-produce)
* 4 [Class ModelGeometry](#modelgeometry)
  * 4.1 [ModelGeometry.produce](#modelgeometry-produce)
* 5 [Class ModelHole](#modelhole)
  * 5.1 [ModelHole.\_\_post\_init\_\_](#modelhole---post-init--)
  * 5.2 [ModelHole.get\_name](#modelhole-get-name)
  * 5.3 [ModelHole.produce](#modelhole-produce)
* 6 [Class ModelMount](#modelmount)
  * 6.1 [ModelMount.\_\_post\_init\_\_](#modelmount---post-init--)
  * 6.2 [ModelMount.produce](#modelmount-produce)
* 7 [Class ModelOperation](#modeloperation)
  * 7.1 [ModelOperation.\_viewer\_upate](#modeloperation--viewer-upate)
  * 7.2 [ModelOperation.get\_name](#modeloperation-get-name)
  * 7.3 [ModelOperation.produce](#modeloperation-produce)
  * 7.4 [ModelOperation.produce\_shape\_binder](#modeloperation-produce-shape-binder)
* 8 [Class ModelPad](#modelpad)
  * 8.1 [ModelPad.\_\_post\_init\_\_](#modelpad---post-init--)
  * 8.2 [ModelPad.get\_name](#modelpad-get-name)
  * 8.3 [ModelPad.produce](#modelpad-produce)
* 9 [Class ModelPart](#modelpart)
  * 9.1 [ModelPart.\_\_post\_init\_\_](#modelpart---post-init--)
  * 9.2 [ModelPart.produce](#modelpart-produce)
* 10 [Class ModelPocket](#modelpocket)
  * 10.1 [ModelPocket.get\_name](#modelpocket-get-name)
  * 10.2 [ModelPocket.produce](#modelpocket-produce)
* 11 [Class ModelPolygon](#modelpolygon)
  * 11.1 [ModelPolygon.\_\_post\_init\_\_](#modelpolygon---post-init--)
  * 11.2 [ModelPolygon.\_colinear\_check](#modelpolygon--colinear-check)
  * 11.3 [ModelPolygon.\_compute\_arcs](#modelpolygon--compute-arcs)
  * 11.4 [ModelPolygon.\_compute\_lines](#modelpolygon--compute-lines)
  * 11.5 [ModelPolygon.\_double\_link](#modelpolygon--double-link)
  * 11.6 [ModelPolygon.\_plane\_2d\_project](#modelpolygon--plane-2d-project)
  * 11.7 [ModelPolygon.\_radii\_check](#modelpolygon--radii-check)
  * 11.8 [ModelPolygon.\_unit\_tests](#modelpolygon--unit-tests)
  * 11.9 [ModelPolygon.get\_geometries](#modelpolygon-get-geometries)
  * 11.10 [ModelPolygon.produce](#modelpolygon-produce)
* 12 [Class \_ModelArc](#-modelarc)
  * 12.1 [\_ModelArc.\_make\_arc\_3points](#-modelarc--make-arc-3points)
  * 12.2 [\_ModelArc.produce](#-modelarc-produce)
  * 12.3 [\_ModelCircle.produce](#-modelcircle-produce)
* 13 [Class \_ModelFillet](#-modelfillet)
  * 13.1 [\_ModelFillet.\_\_post\_init\_\_](#-modelfillet---post-init--)
  * 13.2 [\_ModelFillet.compute\_arc](#-modelfillet-compute-arc)
  * 13.3 [\_ModelFillet.plane\_2d\_project](#-modelfillet-plane-2d-project)
* 14 [Class \_ModelGeometry](#-modelgeometry)
* 15 [Class \_ModelLine](#-modelline)
  * 15.1 [\_ModelLine.produce](#-modelline-produce)
  * 15.2 [ModelPocket\_\_post\_init\_\_](#modelpocket--post-init--)

## 1 <a name="introduction"></a>Introduction


## 2 Class Box <a name="box"></a>

class Box(object):

Model a box.

Builds a box given a length, width, height, material, thickness and center point"

Attributes:
* *Name* (str): Box name.
* *Length* (float): length in X direction in millimeters.
* *Width* (float): width in Y direction in millimeters.
* *Height* (float): height in Z direction in millimeters.
* *Thickness* (float): Material thickness in millimeters.
* *Material* (str): Material to use.
* *Center* Vector: Center of Box.


### 2.1 Box.compute <a name="box-compute"></a>

def *compute*(self) -> None:

Compute a box.

## 3 Class ModelCircle <a name="modelcircle"></a>

class ModelCircle(ModelGeometry):

ModelCircle: A circle with a center and a radius.

This is actually a sphere of at a specified location and diameter.  It gets cut into
circle later on.

Attributes:
* *Center* (Vector): The circle center.
* *Diameter* (float): The diameter in radians.


### 3.1 ModelCircle.\_\_post\_init\_\_ <a name="modelcircle---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Make private copy of Center.

### 3.2 ModelCircle.get\_geometries <a name="modelcircle-get-geometries"></a>

def *get\_geometries*(self) -> Tuple[\_ModelGeometry, ...]:

Return the ModelPolygon lines and arcs.

### 3.3 ModelCircle.produce <a name="modelcircle-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*) -> Tuple[Part.Part2DObject, ...]:

Produce the FreeCAD objects needed for ModelPolygon.

### 3.4 ModelFile.\_\_enter\_\_ <a name="modelfile---enter--"></a>

def \_\_enter\_\_(self) -> "ModelFile":

Open the ModelFile.

### 3.5 ModelFile.\_\_exit\_\_ <a name="modelfile---exit--"></a>

def \_\_exit\_\_(self, *exec\_type*, *exec\_value*, *exec\_table*) -> None:

Close the ModelFile.

### 3.6 ModelFile.\_\_post\_init\_\_ <a name="modelfile---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Initialize the AppDocument.

### 3.7 ModelFile.\_unit\_tests <a name="modelfile--unit-tests"></a>

def \_unit\_tests() -> None:

Run ModelFile unit tests.

### 3.8 ModelFile.produce <a name="modelfile-produce"></a>

def *produce*(self) -> None:

Produce all of the ModelPart's.

## 4 Class ModelGeometry <a name="modelgeometry"></a>

class ModelGeometry(object):

ModelGeometry: The base class for ModelPolygon and ModelCircle.

### 4.1 ModelGeometry.produce <a name="modelgeometry-produce"></a>

def *produce*(self, *model\_context*:  ModelFile, *prefix*:  *str*) -> Tuple[Part.Part2DObject, ...]:

Produce the necessary FreeCAD objects for the ModelGeometry.

## 5 Class ModelHole <a name="modelhole"></a>

class ModelHole(ModelOperation):

ModelHole: A FreeCAD PartDesign Pocket operation.

Attributes:
    *Name* (str): The operation name.
    *Circle* (ModelCircle): The Circle to drill.
    *Depth* (float): The depth


### 5.1 ModelHole.\_\_post\_init\_\_ <a name="modelhole---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify ModelPad values.

### 5.2 ModelHole.get\_name <a name="modelhole-get-name"></a>

def *get\_name*(self) -> *str*:

Return ModelHole name.

### 5.3 ModelHole.produce <a name="modelhole-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*) -> None:

Produce the Hole.

## 6 Class ModelMount <a name="modelmount"></a>

class ModelMount(object):

ModelMount: An operations plane that can be oriented for subsequent machine operations.

This class basically corresponds to a FreeCad Datum Plane.  It is basically the surface
to which the 2D ModelGeometry's are mapped onto prior to performing each operation.
This class is immutable (i.e. frozen.)

Attributes:
* *Name*: (str): The name of the ModelPlane.
* *Contact* (Vector): A point on the plane.
* *Normal* (Vector): A normal to the plane
* *North* (Vector):
  A vector in the plane that specifies the north direction when mounted  in a machining vice.
* *Operations* (Tuple[ModelOperation, ...]): The operations to perform.


### 6.1 ModelMount.\_\_post\_init\_\_ <a name="modelmount---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify that ModelMount arguments are valid.

### 6.2 ModelMount.produce <a name="modelmount-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*) -> None:

Create the FreeCAD DatumPlane used for the drawing support.

Arguments:
* *body* (PartDesign.Body): The FreeCAD Part design Body to attach the datum plane to.
* *name* (Optional[str]): The datum plane name.
  (Default: "...DatumPlaneN", where N is incremented.)
* Returns:
  * (Part.Geometry) that is the datum\_plane.


## 7 Class ModelOperation <a name="modeloperation"></a>

class ModelOperation(object):

ModelOperation: An base class for operations -- ModelPad, ModelPocket, ModelHole, etc.

All model operations are immutable (i.e. frozen.)

### 7.1 ModelOperation.\_viewer\_upate <a name="modeloperation--viewer-upate"></a>

def \_viewer\_update(self, *body*:  Part.BodyBase, *part\_feature*:  Part.Feature) -> None:

Update the view Body view provider.

### 7.2 ModelOperation.get\_name <a name="modeloperation-get-name"></a>

def *get\_name*(self) -> *str*:

Return ModelOperation name.

### 7.3 ModelOperation.produce <a name="modeloperation-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*) -> None:

Return the operation sort key.

### 7.4 ModelOperation.produce\_shape\_binder <a name="modeloperation-produce-shape-binder"></a>

def *produce\_shape\_binder*(self, *model\_file*:  ModelFile, *part\_geometries*:  Tuple[Part.Part2DObject, ...], *prefix*:  *str*) -> Part.Feature:

Produce the shape binder needed for the pad, pocket, hole, ... operations.

## 8 Class ModelPad <a name="modelpad"></a>

class ModelPad(ModelOperation):

ModelPad: A FreeCAD PartDesign Pad operation.

Attributes:
    *Name* (str): The operation name.
    *Geometry* (ModelGeometry): The ModlePolygon or ModelCircle to pad with.
    *Depth* (float): The depth to pad to in millimeters.


### 8.1 ModelPad.\_\_post\_init\_\_ <a name="modelpad---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify ModelPad values.

### 8.2 ModelPad.get\_name <a name="modelpad-get-name"></a>

def *get\_name*(self) -> *str*:

Return ModelPad name.

### 8.3 ModelPad.produce <a name="modelpad-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*) -> None:

Produce the Pad.

## 9 Class ModelPart <a name="modelpart"></a>

class ModelPart(object):

Model: Represents a single part constructed using FreeCAD Part Design paradigm.

Attributes:
* *Name* (str): The model name.
* *Material* (str): The material to use.
* *Color* (str): The color to use.
* *Mounts* (Tuple[ModelMount, ...]): The various model mounts to use to construct the part.


### 9.1 ModelPart.\_\_post\_init\_\_ <a name="modelpart---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify ModelPart arguments.

### 9.2 ModelPart.produce <a name="modelpart-produce"></a>

def *produce*(self, *model\_file*:  ModelFile) -> None:

Produce the ModelPart.

## 10 Class ModelPocket <a name="modelpocket"></a>

class ModelPocket(ModelOperation):

ModelPocket: A FreeCAD PartDesign Pocket operation.

Attributes:
    *Name* (str): The operation name.
    *Geometry* (ModelGeometry): The Polygon or Circle to pocket.
    *Depth* (float): The depth


### 10.1 ModelPocket.get\_name <a name="modelpocket-get-name"></a>

def *get\_name*(self) -> *str*:

Return ModelPocket name.

### 10.2 ModelPocket.produce <a name="modelpocket-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*) -> None:

Produce the Pad.

## 11 Class ModelPolygon <a name="modelpolygon"></a>

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
* *Name* (str): The name of the polygon.  (Default: "")
* *Corners* (Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...]):
  See description below for more on corners.

Raises:
* ValueError for improper corner specifications.


### 11.1 ModelPolygon.\_\_post\_init\_\_ <a name="modelpolygon---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify that the corners passed in are correct.

### 11.2 ModelPolygon.\_colinear\_check <a name="modelpolygon--colinear-check"></a>

def \_colinear\_check(self) -> *str*:

Check for colinearity errors.

### 11.3 ModelPolygon.\_compute\_arcs <a name="modelpolygon--compute-arcs"></a>

def \_compute\_arcs(self) -> None:

Create any Arc's needed for non-zero radius \_ModelFillet's.

### 11.4 ModelPolygon.\_compute\_lines <a name="modelpolygon--compute-lines"></a>

def \_compute\_lines(self) -> None:

Create Create any Line's need for \_ModelFillet's.

### 11.5 ModelPolygon.\_double\_link <a name="modelpolygon--double-link"></a>

def \_double\_link(self) -> None:

Double link the \_ModelFillet's together.

### 11.6 ModelPolygon.\_plane\_2d\_project <a name="modelpolygon--plane-2d-project"></a>

def \_plane\_2d\_project(self, *contact*:  Vector, *normal*:  Vector) -> None:

Update the \_ModelFillet's to be projected onto a Plane.

Arguments:
* *contact* (Vector): A point on the plane.
* *normal* (Vector): A plane normal.


### 11.7 ModelPolygon.\_radii\_check <a name="modelpolygon--radii-check"></a>

def \_radii\_check(self) -> *str*:

Check for radius overlap errors.

### 11.8 ModelPolygon.\_unit\_tests <a name="modelpolygon--unit-tests"></a>

def \_unit\_tests() -> None:

Do some unit tests.

### 11.9 ModelPolygon.get\_geometries <a name="modelpolygon-get-geometries"></a>

def *get\_geometries*(self, *contact*:  Vector, Normal:  Vector) -> Tuple[\_ModelGeometry, ...]:

Return the ModelPolygon lines and arcs.

### 11.10 ModelPolygon.produce <a name="modelpolygon-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*) -> Tuple[Part.Part2DObject, ...]:

Produce the FreeCAD objects needed for ModelPolygon.

## 12 Class \_ModelArc <a name="-modelarc"></a>

class \_ModelArc(\_ModelGeometry):

\_ModelArc: An internal representation an arc geometry.

Attributes:
* *Apex* (Vector): The fillet apex point.
* *Radius* (float): The arc radius in millimeters.
* *Center* (Vector): The arc center point.
* *Start* (Vector): The Arc start point.
* *Middle* (Vector): The Arc midpoint.
* *Finish* (Vector): The Arc finish point.

# Old:
* *StartAngle* (float): The start arc angle in radians.
* *FinishAngle* (float): The finish arc angle in radiuns.
* *DeltaAngle* (float):
  The value to add to *StartAngle* to get *FinishAngle* (module 2 radians):


### 12.1 \_ModelArc.\_make\_arc\_3points <a name="-modelarc--make-arc-3points"></a>

def *make\_arc\_3points*(points:  Tuple[Vector, ...], *placement*=None, *face*=False, *support*=None, *map\_mode*="Deactivated", *primitive*=False) -> Any:

Make arc using a copy of Draft.make\_arc\_3points without print statements.

### 12.2 \_ModelArc.produce <a name="-modelarc-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*, *index*:  *int*) -> Part.Part2DObject:

Return line segment after moving it into Geometry group.

### 12.3 \_ModelCircle.produce <a name="-modelcircle-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*, *index*:  *int*) -> Part.Part2DObject:

Return line segment after moving it into Geometry group.

## 13 Class \_ModelFillet <a name="-modelfillet"></a>

class \_ModelFillet(object):

\_ModelFillet: An object that represents one fillet of a ModelPolygon.

Attributes:
* *Apex* (Vector): The apex corner point for the fillet.
* *Radius* (float): The fillet radius in millimeters.
* *Before* (\_ModelFillet): The previous \_ModelFillet in the ModelPolygon.
* *After* (\_ModelFillet): The next \_ModelFillet in the ModelPolygon.
* *Arc* (Optional[\_ModelArc]): The fillet Arc if Radius is non-zero.
* *Line* (Optional[\_ModelLine]): The line that connects to the previous \_ModelFillet


### 13.1 \_ModelFillet.\_\_post\_init\_\_ <a name="-modelfillet---post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Initialize \_ModelFillet.

### 13.2 \_ModelFillet.compute\_arc <a name="-modelfillet-compute-arc"></a>

def *compute\_arc*(self, *tracing*:  *str* = "") -> \_ModelArc:

Return the arc associated with a \_ModelFillet with non-zero radius.

### 13.3 \_ModelFillet.plane\_2d\_proje <a name="-modelfillet-plane-2d-project"></a>

def *plane\_2d\_project*(self, *contact*:  Vector, *normal*:  Vector) -> None:

Project the Apex onto a plane.

Arguments:
* *contact* (Vector): A point on the projection plane.
* *normal* (Vector): A normal to the projection plane.


## 14 Class \_ModelGeometry <a name="-modelgeometry"></a>

class \_ModelGeometry(object):

\_ModelGeometry: An Internal base class for \_ModelArc, \_ModelCircle, and \_ModelLine.

All \_ModelGeometry classes are immutable (i.e. frozen.)

## 15 Class \_ModelLine <a name="-modelline"></a>

class \_ModelLine(\_ModelGeometry):

\_ModelLine: An internal representation of a line segment geometry.

Attributes:
* *Start (Vector): The line segment start point.
* *Finish (Vector): The line segment finish point.


### 15.1 \_ModelLine.produce <a name="-modelline-produce"></a>

def *produce*(self, *model\_file*:  ModelFile, *prefix*:  *str*, *index*:  *int*) -> Part.Part2DObject:

Return line segment after moving it into Geometry group.

### 15.2 ModelPocket\_\_post\_init\_\_ <a name="modelpocket--post-init--"></a>

def \_\_post\_init\_\_(self) -> None:

Verify ModelPad values.
