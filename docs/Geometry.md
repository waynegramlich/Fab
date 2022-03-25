# Geometry: Geometry: A module for constructing 2D geometry.

## Table of Contents (alphabetical order):

* 1 Class: [FabCircle](#geometry--fabcircle):
  * 1.1 [get_hash()](#geometry----get-hash): Feturn FabCircle hash.
  * 1.2 [project_to_plane()](#geometry----project-to-plane): Return a new FabCircle projected onto a plane.
  * 1.3 [produce()](#geometry----produce): Produce the FreeCAD objects needed for FabPolygon.
  * 1.4 [get_geometries()](#geometry----get-geometries): Return the FabPolygon lines and arcs.
* 2 Class: [FabGeometry](#geometry--fabgeometry):
  * 2.1 [get_hash()](#geometry----get-hash): Return FabGeometry hash.
  * 2.2 [produce()](#geometry----produce): Produce the necessary FreeCAD objects for the FabGeometry.
  * 2.3 [project_to_plane()](#geometry----project-to-plane): Return a new FabGeometry projected onto a plane.
* 3 Class: [FabGeometryContext](#geometry--fabgeometrycontext):
  * 3.1 [copy()](#geometry----copy): Return a FabGeometryContext copy.
  * 3.2 [set_geometry_group()](#geometry----set-geometry-group): Set the GeometryContext geometry group.
* 4 Class: [FabPlane](#geometry--fabplane):
  * 4.1 [point_project()](#geometry----point-project): Project a point onto a plane.
  * 4.2 [rotate_to_z_axis()](#geometry----rotate-to-z-axis): Rotate a point around the origin until the normal aligns with the +Z axis.
* 5 Class: [FabPolygon](#geometry--fabpolygon):
  * 5.1 [get_hash()](#geometry----get-hash): Return the FabPolygon Hash.
  * 5.2 [project_to_plane()](#geometry----project-to-plane): Return nre FabPolygon prejected onto a plane.
  * 5.3 [get_geometries()](#geometry----get-geometries): Return the FabPolygon lines and arcs.
  * 5.4 [produce()](#geometry----produce): Produce the FreeCAD objects needed for FabPolygon.
* 6 Class: [FabQuery](#geometry--fabquery):
  * 6.1 [circle()](#geometry----circle): Draw a circle to a point.
  * 6.2 [close()](#geometry----close): Close a sequence of arcs and lines.
  * 6.3 [copy_workplane()](#geometry----copy-workplane): Create a new CadQuery workplane and push it onto the stack.
  * 6.4 [cut_blind()](#geometry----cut-blind): Use the current 2D object to cut a pocket to a known depth.
  * 6.5 [extrude()](#geometry----extrude): Extrude current 2D object to a known depth.
  * 6.6 [hole()](#geometry----hole): Drill a hole.
  * 6.7 [line_to()](#geometry----line-to): Draw a line to a point.
  * 6.8 [move_to()](#geometry----move-to): Draw a line to a point.
  * 6.9 [show()](#geometry----show): Print a detailed dump of a FabQuery.
  * 6.10 [subtract()](#geometry----subtract): Subtract one solid form a FabQuery.
  * 6.11 [three_point_arc()](#geometry----three-point-arc): Draw a three point arc.

## <a name="geometry--fabcircle"></a>1 Class FabCircle:

A circle with a center and a radius.
This is actually a sphere of at a specified location and diameter.  It gets cut into
circle later on.

Attributes:
* *Center* (Vector): The circle center.
* *Normal* (Vector): The normal to circle plane.
* *Diameter* (float): The diameter in millimeters.

### <a name="geometry----get-hash"></a>1.1 `FabCircle.`get_hash():

FabCircle.get_hash(self) -> Tuple[Any, ...]:

Feturn FabCircle hash.

### <a name="geometry----project-to-plane"></a>1.2 `FabCircle.`project_to_plane():

FabCircle.project_to_plane(self, plane: Geometry.FabPlane, tracing: str = '') -> 'FabCircle':

Return a new FabCircle projected onto a plane.
Arguments:
* *plane* (FabPlane): Plane to proejct to.

Returns:
* (FabCircle): The newly projected FabCicle.

### <a name="geometry----produce"></a>1.3 `FabCircle.`produce():

FabCircle.produce(self, geometry_context: Geometry.FabGeometryContext, prefix: str, index: int, tracing: str = '') -> Tuple[Any, ...]:

Produce the FreeCAD objects needed for FabPolygon.

### <a name="geometry----get-geometries"></a>1.4 `FabCircle.`get_geometries():

FabCircle.get_geometries(self) -> Tuple[Geometry._Geometry, ...]:

Return the FabPolygon lines and arcs.


## <a name="geometry--fabgeometry"></a>2 Class FabGeometry:

The base class for FabPolygon and FabCircle.

### <a name="geometry----get-hash"></a>2.1 `FabGeometry.`get_hash():

FabGeometry.get_hash(self) -> Tuple[Any, ...]:

Return FabGeometry hash.

### <a name="geometry----produce"></a>2.2 `FabGeometry.`produce():

FabGeometry.produce(self, geometry_context: Geometry.FabGeometryContext, prefix: str, index: int, tracing: str = '') -> Tuple[Any, ...]:

Produce the necessary FreeCAD objects for the FabGeometry.

### <a name="geometry----project-to-plane"></a>2.3 `FabGeometry.`project_to_plane():

FabGeometry.project_to_plane(self, plane: Geometry.FabPlane) -> 'FabGeometry':

Return a new FabGeometry projected onto a plane.


## <a name="geometry--fabgeometrycontext"></a>3 Class FabGeometryContext:

GeometryProduce: Context needed to produce FreeCAD geometry objects.
Attributes:
* *_Plane* (Plane): Plane to use.
* *_WorkPlane* (FabQuery): The CadQuery Workplane wrapper to use.
* *_GeometryGroup*: (App.DocumentObjectGroup):
  The FreeCAD group to store FreeCAD Geometry objects into.
  This field needs to be set prior to use with set_geometry_group() method.

### <a name="geometry----copy"></a>3.1 `FabGeometryContext.`copy():

FabGeometryContext.copy(self, tracing: str = '') -> 'FabGeometryContext':

Return a FabGeometryContext copy.

### <a name="geometry----set-geometry-group"></a>3.2 `FabGeometryContext.`set_geometry_group():

FabGeometryContext.set_geometry_group(self, geometry_group: Any) -> None:

Set the GeometryContext geometry group.


## <a name="geometry--fabplane"></a>4 Class FabPlane:

A Plane class.
* *Contact* (Vector):  The contact point of the plane.
* *Normal* (Vector): The normal to the plane.

### <a name="geometry----point-project"></a>4.1 `FabPlane.`point_project():

FabPlane.point_project(self, point: cadquery.occ_impl.geom.Vector) -> cadquery.occ_impl.geom.Vector:

Project a point onto a plane.

### <a name="geometry----rotate-to-z-axis"></a>4.2 `FabPlane.`rotate_to_z_axis():

FabPlane.rotate_to_z_axis(self, point: cadquery.occ_impl.geom.Vector, reversed: bool = False, tracing: str = '') -> cadquery.occ_impl.geom.Vector:

Rotate a point around the origin until the normal aligns with the +Z axis.
Arguments:
* *point* (Vector): The point to rotate.
* *reversed* (bool = False): If True, do the inverse rotation.

Returns:
* (Vector): The rotated vector position.


## <a name="geometry--fabpolygon"></a>5 Class FabPolygon:

An immutable polygon with rounded corners.
A FabPolygon is represented as a sequence of corners (i.e. a Vector) where each corner can
optionally be filleted with a radius.  In order to make it easier to use, a corner can be
specified as simple Vector or as a tuple that specifes a Vector and a radius.  The radius
is in millimeters and can be provided as either Python int or float.  When an explicit
fillet radius is not specified, higher levels in the software stack will typically substitute
in a deburr radius for external corners and an interal tool radius for internal corners.
FabPolygon's are frozen and can not be modified after creation.

Example:
     polygon: Fab.FabPolyon = Fab.FabPolygon((
         Vector(-10, -10, 0),  # Lower left (no radius)
         Vector(10, -10, 0),  # Lower right (no radius)
         (Vector(10, 10, 0), 5),  # Upper right (5mm radius)
         (Vector(-0, 10, 0), 5.5),  # Upper right (5.5mm radius)
     ), "Name")

Attributes:
* *Corners* (Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...]):
  See description below for more on corners.

### <a name="geometry----get-hash"></a>5.1 `FabPolygon.`get_hash():

FabPolygon.get_hash(self) -> Tuple[Any, ...]:

Return the FabPolygon Hash.

### <a name="geometry----project-to-plane"></a>5.2 `FabPolygon.`project_to_plane():

FabPolygon.project_to_plane(self, plane: Geometry.FabPlane, tracing: str = '') -> 'FabPolygon':

Return nre FabPolygon prejected onto a plane.
Arguments:
* *plane* (FabPlane): The plane to project onto.

Returns:
* (FabPolyGon): The newly projected FabPolygon.

### <a name="geometry----get-geometries"></a>5.3 `FabPolygon.`get_geometries():

FabPolygon.get_geometries(self, contact: cadquery.occ_impl.geom.Vector, Normal: cadquery.occ_impl.geom.Vector) -> Tuple[Geometry._Geometry, ...]:

Return the FabPolygon lines and arcs.

### <a name="geometry----produce"></a>5.4 `FabPolygon.`produce():

FabPolygon.produce(self, geometry_context: Geometry.FabGeometryContext, prefix: str, index: int, tracing: str = '') -> Tuple[Any, ...]:

Produce the FreeCAD objects needed for FabPolygon.


## <a name="geometry--fabquery"></a>6 Class FabQuery:

A CadQuery Workplane wrapper.
This class creates CadQuery Workplane provides a consistent head of the Workplane chain..
CadQuery Operations are added as needed.

Attributes:
* *Plane* (FabPlane): The plain to use for CadQuery initialization.
* *WorkPlane: (cadquery.Workplane): The resulting CadQuery Workplane object.

### <a name="geometry----circle"></a>6.1 `FabQuery.`circle():

FabQuery.circle(self, center: cadquery.occ_impl.geom.Vector, radius: float, for_construction=False, tracing: str = '') -> None:

Draw a circle to a point.

### <a name="geometry----close"></a>6.2 `FabQuery.`close():

FabQuery.close(self, tracing: str = '') -> None:

Close a sequence of arcs and lines.

### <a name="geometry----copy-workplane"></a>6.3 `FabQuery.`copy_workplane():

FabQuery.copy_workplane(self, plane: Geometry.FabPlane, tracing: str = '') -> None:

Create a new CadQuery workplane and push it onto the stack.

### <a name="geometry----cut-blind"></a>6.4 `FabQuery.`cut_blind():

FabQuery.cut_blind(self, depth: float, tracing: str = '') -> None:

Use the current 2D object to cut a pocket to a known depth.

### <a name="geometry----extrude"></a>6.5 `FabQuery.`extrude():

FabQuery.extrude(self, depth: float, tracing: str = '') -> None:

Extrude current 2D object to a known depth.

### <a name="geometry----hole"></a>6.6 `FabQuery.`hole():

FabQuery.hole(self, diameter: float, depth: float, tracing: str = '') -> None:

Drill a hole.

### <a name="geometry----line-to"></a>6.7 `FabQuery.`line_to():

FabQuery.line_to(self, end: cadquery.occ_impl.geom.Vector, for_construction=False, tracing: str = '') -> None:

Draw a line to a point.

### <a name="geometry----move-to"></a>6.8 `FabQuery.`move_to():

FabQuery.move_to(self, point: cadquery.occ_impl.geom.Vector, tracing: str = '') -> None:

Draw a line to a point.

### <a name="geometry----show"></a>6.9 `FabQuery.`show():

FabQuery.show(self, label: str, tracing: str = '') -> None:

Print a detailed dump of a FabQuery.

### <a name="geometry----subtract"></a>6.10 `FabQuery.`subtract():

FabQuery.subtract(self, remove_solid: 'FabQuery', tracing: str = '') -> None:

Subtract one solid form a FabQuery.

### <a name="geometry----three-point-arc"></a>6.11 `FabQuery.`three_point_arc():

FabQuery.three_point_arc(self, middle: cadquery.occ_impl.geom.Vector, end: cadquery.occ_impl.geom.Vector, for_construction: bool = False, tracing: str = '') -> None:

Draw a three point arc.



