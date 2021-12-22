# Solid: Solid: A module for constructing 3D solids.

## Table of Contents (alphabetical order):

* 1 Class: [Box](#solid--box):
  * 1.1 [compute()](#solid----compute): Compute a box.
  * 1.2 [produce()](#solid----produce): Produce a box.
* 2 Class: [ModelCircle](#solid--modelcircle):
  * 2.1 [produce()](#solid----produce): Produce the FreeCAD objects needed for ModelPolygon.
  * 2.2 [get_geometries()](#solid----get-geometries): Return the ModelPolygon lines and arcs.
* 3 Class: [ModelFile](#solid--modelfile):
  * 3.1 [produce()](#solid----produce): Produce all of the ModelSolid's.
* 4 Class: [ModelGeometry](#solid--modelgeometry):
  * 4.1 [produce()](#solid----produce): Produce the necessary FreeCAD objects for the ModelGeometry.
* 5 Class: [ModelHole](#solid--modelhole):
  * 5.1 [get_name()](#solid----get-name): Return ModelHole name.
  * 5.2 [produce()](#solid----produce): Produce the Hole.
* 6 Class: [ModelMount](#solid--modelmount):
  * 6.1 [produce()](#solid----produce): Create the FreeCAD DatumPlane used for the drawing support.
* 7 Class: [ModelOperation](#solid--modeloperation):
  * 7.1 [get_name()](#solid----get-name): Return ModelOperation name.
  * 7.2 [produce()](#solid----produce): Return the operation sort key.
  * 7.3 [produce_shape_binder()](#solid----produce-shape-binder): Produce the shape binder needed for the pad, pocket, hole, ... operations.
* 8 Class: [ModelPad](#solid--modelpad):
  * 8.1 [get_name()](#solid----get-name): Return ModelPad name.
  * 8.2 [produce()](#solid----produce): Produce the Pad.
* 9 Class: [ModelPocket](#solid--modelpocket):
  * 9.1 [get_name()](#solid----get-name): Return ModelPocket name.
  * 9.2 [produce()](#solid----produce): Produce the Pad.
* 10 Class: [ModelPolygon](#solid--modelpolygon):
  * 10.1 [get_geometries()](#solid----get-geometries): Return the ModelPolygon lines and arcs.
  * 10.2 [produce()](#solid----produce): Produce the FreeCAD objects needed for ModelPolygon.
* 11 Class: [ModelSolid](#solid--modelsolid):
  * 11.1 [produce()](#solid----produce): Produce the ModelSolid.

## <a name="solid--box"></a>1 Class Box:

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

### <a name="solid----compute"></a>1.1 `Box.`compute():

Box.compute(self) -> None:

Compute a box.

### <a name="solid----produce"></a>1.2 `Box.`produce():

Box.produce(self) -> typing.Tuple[Solid.ModelSolid, ...]:

Produce a box.


## <a name="solid--modelcircle"></a>2 Class ModelCircle:

A circle with a center and a radius.
This is actually a sphere of at a specified location and diameter.  It gets cut into
circle later on.

Attributes:
* *Center* (Vector): The circle center.
* *Diameter* (float): The diameter in radians.

### <a name="solid----produce"></a>2.1 `ModelCircle.`produce():

ModelCircle.produce(self, model_file: Solid.ModelFile, prefix: str) -> typing.Tuple[Part.Part2DObject, ...]:

Produce the FreeCAD objects needed for ModelPolygon.

### <a name="solid----get-geometries"></a>2.2 `ModelCircle.`get_geometries():

ModelCircle.get_geometries(self) -> typing.Tuple[Solid._ModelGeometry, ...]:

Return the ModelPolygon lines and arcs.


## <a name="solid--modelfile"></a>3 Class ModelFile:

Represents a FreeCAD document file.

### <a name="solid----produce"></a>3.1 `ModelFile.`produce():

ModelFile.produce(self) -> None:

Produce all of the ModelSolid's.


## <a name="solid--modelgeometry"></a>4 Class ModelGeometry:

The base class for ModelPolygon and ModelCircle.

### <a name="solid----produce"></a>4.1 `ModelGeometry.`produce():

ModelGeometry.produce(self, model_context: Solid.ModelFile, prefix: str) -> typing.Tuple[Part.Part2DObject, ...]:

Produce the necessary FreeCAD objects for the ModelGeometry.


## <a name="solid--modelhole"></a>5 Class ModelHole:

A FreeCAD PartDesign Pocket operation.
Attributes:
* *Name* (str): The operation name.
* *Circle* (ModelCircle): The Circle to drill.
* *Depth* (float): The depth

### <a name="solid----get-name"></a>5.1 `ModelHole.`get_name():

ModelHole.get_name(self) -> str:

Return ModelHole name.

### <a name="solid----produce"></a>5.2 `ModelHole.`produce():

ModelHole.produce(self, model_file: Solid.ModelFile, prefix: str) -> None:

Produce the Hole.


## <a name="solid--modelmount"></a>6 Class ModelMount:

An operations plane that can be oriented for subsequent machine operations.
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

### <a name="solid----produce"></a>6.1 `ModelMount.`produce():

ModelMount.produce(self, model_file: Solid.ModelFile, prefix: str) -> None:

Create the FreeCAD DatumPlane used for the drawing support.
Arguments:
* *body* (PartDesign.Body): The FreeCAD Part design Body to attach the datum plane to.
* *name* (Optional[str]): The datum plane name.
  (Default: "...DatumPlaneN", where N is incremented.)
* Returns:
  * (Part.Geometry) that is the datum_plane.


## <a name="solid--modeloperation"></a>7 Class ModelOperation:

An base class for operations -- ModelPad, ModelPocket, ModelHole, etc.
All model operations are immutable (i.e. frozen.)

### <a name="solid----get-name"></a>7.1 `ModelOperation.`get_name():

ModelOperation.get_name(self) -> str:

Return ModelOperation name.

### <a name="solid----produce"></a>7.2 `ModelOperation.`produce():

ModelOperation.produce(self, model_file: Solid.ModelFile, prefix: str) -> None:

Return the operation sort key.

### <a name="solid----produce-shape-binder"></a>7.3 `ModelOperation.`produce_shape_binder():

ModelOperation.produce_shape_binder(self, model_file: Solid.ModelFile, part_geometries: typing.Tuple[Part.Part2DObject, ...], prefix: str) -> Part.Feature:

Produce the shape binder needed for the pad, pocket, hole, ... operations.


## <a name="solid--modelpad"></a>8 Class ModelPad:

A FreeCAD PartDesign Pad operation.
Attributes:
* *Name* (str): The operation name.
* *Geometry* (ModelGeometry): The ModlePolygon or ModelCircle to pad with.
* *Depth* (float): The depth to pad to in millimeters.

### <a name="solid----get-name"></a>8.1 `ModelPad.`get_name():

ModelPad.get_name(self) -> str:

Return ModelPad name.

### <a name="solid----produce"></a>8.2 `ModelPad.`produce():

ModelPad.produce(self, model_file: Solid.ModelFile, prefix: str) -> None:

Produce the Pad.


## <a name="solid--modelpocket"></a>9 Class ModelPocket:

A FreeCAD PartDesign Pocket operation.
Attributes:
* *Name* (str): The operation name.
* *Geometry* (ModelGeometry): The Polygon or Circle to pocket.
* *Depth* (float): The pocket depth in millimeters.

### <a name="solid----get-name"></a>9.1 `ModelPocket.`get_name():

ModelPocket.get_name(self) -> str:

Return ModelPocket name.

### <a name="solid----produce"></a>9.2 `ModelPocket.`produce():

ModelPocket.produce(self, model_file: Solid.ModelFile, prefix: str) -> None:

Produce the Pad.


## <a name="solid--modelpolygon"></a>10 Class ModelPolygon:

An immutable polygon with rounded corners.
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

### <a name="solid----get-geometries"></a>10.1 `ModelPolygon.`get_geometries():

ModelPolygon.get_geometries(self, contact: Base.Vector, Normal: Base.Vector) -> typing.Tuple[Solid._ModelGeometry, ...]:

Return the ModelPolygon lines and arcs.

### <a name="solid----produce"></a>10.2 `ModelPolygon.`produce():

ModelPolygon.produce(self, model_file: Solid.ModelFile, prefix: str) -> typing.Tuple[Part.Part2DObject, ...]:

Produce the FreeCAD objects needed for ModelPolygon.


## <a name="solid--modelsolid"></a>11 Class ModelSolid:

Model: Represents a single part constructed using FreeCAD Part Design paradigm.
Attributes:
* *Name* (str): The model name.
* *Material* (str): The material to use.
* *Color* (str): The color to use.
* *Mounts* (Tuple[ModelMount, ...]): The various model mounts to use to construct the part.

### <a name="solid----produce"></a>11.1 `ModelSolid.`produce():

ModelSolid.produce(self, model_file: Solid.ModelFile) -> None:

Produce the ModelSolid.



