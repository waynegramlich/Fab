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
* 3 Class: [FabPolygon](#geometry--fabpolygon):
  * 3.1 [get_hash()](#geometry----get-hash): Return the FabPolygon Hash.
  * 3.2 [project_to_plane()](#geometry----project-to-plane): Return nre FabPolygon projected onto a plane.
  * 3.3 [get_geometries()](#geometry----get-geometries): Return the FabPolygon lines and arcs.
  * 3.4 [produce()](#geometry----produce): Produce the FreeCAD objects needed for FabPolygon.
* 4 Class: [Fab_Arc](#geometry--fab-arc):
  * 4.1 [produce()](#geometry----produce): Return line segment after moving it into Geometry group.
* 5 Class: [Fab_Circle](#geometry--fab-circle):
  * 5.1 [produce()](#geometry----produce): Return line segment after moving it into Geometry group.
* 6 Class: [Fab_Fillet](#geometry--fab-fillet):
  * 6.1 [compute_arc()](#geometry----compute-arc): Return the arc associated with a Fab_Fillet with non-zero radius.
  * 6.2 [plane_2d_project()](#geometry----plane-2d-project): Project the Apex onto a plane.
  * 6.3 [get_geometries()](#geometry----get-geometries): NO DOC STRING!
* 7 Class: [Fab_Geometry](#geometry--fab-geometry):
  * 7.1 [produce()](#geometry----produce): NO DOC STRING!
  * 7.2 [get_start()](#geometry----get-start): Return start point of geometry.
* 8 Class: [Fab_GeometryContext](#geometry--fab-geometrycontext):
  * 8.1 [copy()](#geometry----copy): Return a Fab_GeometryContext copy.
  * 8.2 [copy_with_plane_adjust()](#geometry----copy-with-plane-adjust): Return a Fab_GeometryContext copy with the plane adjusted up/down.
  * 8.3 [set_geometry_group()](#geometry----set-geometry-group): Set the GeometryContext geometry group.
* 9 Class: [Fab_Line](#geometry--fab-line):
  * 9.1 [get_start()](#geometry----get-start): Return the start point of the Fab_Line.
  * 9.2 [produce()](#geometry----produce): Return line segment after moving it into Geometry group.
* 10 Class: [Fab_Plane](#geometry--fab-plane):
  * 10.1 [point_project()](#geometry----point-project): Project a point onto a plane.
  * 10.2 [adjust()](#geometry----adjust): Return a new Fab_Plane that has been adjusted up/down the normal by a delta.
  * 10.3 [rotate_to_z_axis()](#geometry----rotate-to-z-axis): Rotate a point around the origin until the normal aligns with the +Z axis.
* 11 Class: [Fab_Query](#geometry--fab-query):
  * 11.1 [circle()](#geometry----circle): Draw a circle to a point.
  * 11.2 [close()](#geometry----close): Close a sequence of arcs and lines.
  * 11.3 [copy_workplane()](#geometry----copy-workplane): Create a new CadQuery workplane and push it onto the stack.
  * 11.4 [cut_blind()](#geometry----cut-blind): Use the current 2D object to cut a pocket to a known depth.
  * 11.5 [extrude()](#geometry----extrude): Extrude current 2D object to a known depth.
  * 11.6 [hole()](#geometry----hole): Drill a hole.
  * 11.7 [line_to()](#geometry----line-to): Draw a line to a point.
  * 11.8 [move_to()](#geometry----move-to): Draw a line to a point.
  * 11.9 [show()](#geometry----show): Print a detailed dump of a Fab_Query.
  * 11.10 [subtract()](#geometry----subtract): Subtract one solid form a Fab_Query.
  * 11.11 [three_point_arc()](#geometry----three-point-arc): Draw a three point arc.

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

FabCircle.project_to_plane(self, plane: Geometry.Fab_Plane, tracing: str = '') -> 'FabCircle':

Return a new FabCircle projected onto a plane.
Arguments:
* *plane* (Fab_Plane): Plane to project to.

Returns:
* (FabCircle): The newly projected FabCicle.

### <a name="geometry----produce"></a>1.3 `FabCircle.`produce():

FabCircle.produce(self, geometry_context: Geometry.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Tuple[Any, ...]:

Produce the FreeCAD objects needed for FabPolygon.

### <a name="geometry----get-geometries"></a>1.4 `FabCircle.`get_geometries():

FabCircle.get_geometries(self) -> Tuple[Geometry.Fab_Geometry, ...]:

Return the FabPolygon lines and arcs.


## <a name="geometry--fabgeometry"></a>2 Class FabGeometry:

The base class for FabPolygon and FabCircle.

### <a name="geometry----get-hash"></a>2.1 `FabGeometry.`get_hash():

FabGeometry.get_hash(self) -> Tuple[Any, ...]:

Return FabGeometry hash.

### <a name="geometry----produce"></a>2.2 `FabGeometry.`produce():

FabGeometry.produce(self, geometry_context: Geometry.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Tuple[Any, ...]:

Produce the necessary FreeCAD objects for the FabGeometry.

### <a name="geometry----project-to-plane"></a>2.3 `FabGeometry.`project_to_plane():

FabGeometry.project_to_plane(self, plane: Geometry.Fab_Plane) -> 'FabGeometry':

Return a new FabGeometry projected onto a plane.


## <a name="geometry--fabpolygon"></a>3 Class FabPolygon:

An immutable polygon with rounded corners.
A FabPolygon is represented as a sequence of corners (i.e. a Vector) where each corner can
optionally be filleted with a radius.  In order to make it easier to use, a corner can be
specified as simple Vector or as a tuple that specifies a Vector and a radius.  The radius
is in millimeters and can be provided as either Python int or float.  When an explicit
fillet radius is not specified, higher levels in the software stack will typically substitute
in a deburr radius for external corners and an internal tool radius for internal corners.
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

### <a name="geometry----get-hash"></a>3.1 `FabPolygon.`get_hash():

FabPolygon.get_hash(self) -> Tuple[Any, ...]:

Return the FabPolygon Hash.

### <a name="geometry----project-to-plane"></a>3.2 `FabPolygon.`project_to_plane():

FabPolygon.project_to_plane(self, plane: Geometry.Fab_Plane, tracing: str = '') -> 'FabPolygon':

Return nre FabPolygon projected onto a plane.
Arguments:
* *plane* (Fab_Plane): The plane to project onto.

Returns:
* (FabPolyGon): The newly projected FabPolygon.

### <a name="geometry----get-geometries"></a>3.3 `FabPolygon.`get_geometries():

FabPolygon.get_geometries(self, contact: cadquery.occ_impl.geom.Vector, Normal: cadquery.occ_impl.geom.Vector) -> Tuple[Geometry.Fab_Geometry, ...]:

Return the FabPolygon lines and arcs.

### <a name="geometry----produce"></a>3.4 `FabPolygon.`produce():

FabPolygon.produce(self, geometry_context: Geometry.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Tuple[Any, ...]:

Produce the FreeCAD objects needed for FabPolygon.


## <a name="geometry--fab-arc"></a>4 Class Fab_Arc:

An internal representation an arc geometry.
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

### <a name="geometry----produce"></a>4.1 `Fab_Arc.`produce():

Fab_Arc.produce(self, geometry_context: Geometry.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Any:

Return line segment after moving it into Geometry group.


## <a name="geometry--fab-circle"></a>5 Class Fab_Circle:

An internal representation of a circle geometry.
Attributes:
* *Center (Vector): The circle center.
* *Diameter (float): The circle diameter in millimeters.

### <a name="geometry----produce"></a>5.1 `Fab_Circle.`produce():

Fab_Circle.produce(self, geometry_context: Geometry.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Any:

Return line segment after moving it into Geometry group.


## <a name="geometry--fab-fillet"></a>6 Class Fab_Fillet:

An object that represents one fillet of a FabPolygon.
Attributes:
* *Apex* (Vector): The apex corner point for the fillet.
* *Radius* (float): The fillet radius in millimeters.
* *Before* (Fab_Fillet): The previous Fab_Fillet in the FabPolygon.
* *After* (Fab_Fillet): The next Fab_Fillet in the FabPolygon.
* *Arc* (Optional[Fab_Arc]): The fillet Arc if Radius is non-zero.
* *Line* (Optional[Fab_Line]): The line that connects to the previous Fab_Fillet

### <a name="geometry----compute-arc"></a>6.1 `Fab_Fillet.`compute_arc():

Fab_Fillet.compute_arc(self, tracing: str = '') -> Geometry.Fab_Arc:

Return the arc associated with a Fab_Fillet with non-zero radius.

### <a name="geometry----plane-2d-project"></a>6.2 `Fab_Fillet.`plane_2d_project():

Fab_Fillet.plane_2d_project(self, plane: Geometry.Fab_Plane) -> None:

Project the Apex onto a plane.
Arguments:
* *plane* (Fab_Plane): The plane to project the Fab_Fillet onto.

Modifies Fab_Fillet.

### <a name="geometry----get-geometries"></a>6.3 `Fab_Fillet.`get_geometries():

Fab_Fillet.get_geometries(self) -> Tuple[Geometry.Fab_Geometry, ...]:

NO DOC STRING!


## <a name="geometry--fab-geometry"></a>7 Class Fab_Geometry:

An Internal base class for Fab_Arc, Fab_Circle, and Fab_Line.
All Fab_Geometry classes are immutable (i.e. frozen.)

### <a name="geometry----produce"></a>7.1 `Fab_Geometry.`produce():

Fab_Geometry.produce(self, geometry_context: Geometry.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Any:

NO DOC STRING!

### <a name="geometry----get-start"></a>7.2 `Fab_Geometry.`get_start():

Fab_Geometry.get_start(self) -> cadquery.occ_impl.geom.Vector:

Return start point of geometry.


## <a name="geometry--fab-geometrycontext"></a>8 Class Fab_GeometryContext:

GeometryProduce: Context needed to produce FreeCAD geometry objects.
Attributes:
* *Plane* (Fab_Plane): Plane to use.
* *Query* (Fab_Query): The CadQuery Workplane wrapper to use.
* *_GeometryGroup*: (App.DocumentObjectGroup):
  The FreeCAD group to store FreeCAD Geometry objects into.
  This field needs to be set prior to use with set_geometry_group() method.

### <a name="geometry----copy"></a>8.1 `Fab_GeometryContext.`copy():

Fab_GeometryContext.copy(self, tracing: str = '') -> 'Fab_GeometryContext':

Return a Fab_GeometryContext copy.

### <a name="geometry----copy-with-plane-adjust"></a>8.2 `Fab_GeometryContext.`copy_with_plane_adjust():

Fab_GeometryContext.copy_with_plane_adjust(self, delta: float, tracing: str = '') -> 'Fab_GeometryContext':

Return a Fab_GeometryContext copy with the plane adjusted up/down.

### <a name="geometry----set-geometry-group"></a>8.3 `Fab_GeometryContext.`set_geometry_group():

Fab_GeometryContext.set_geometry_group(self, geometry_group: Any) -> None:

Set the GeometryContext geometry group.


## <a name="geometry--fab-line"></a>9 Class Fab_Line:

An internal representation of a line segment geometry.
Attributes:
* *Start (Vector): The line segment start point.
* *Finish (Vector): The line segment finish point.

### <a name="geometry----get-start"></a>9.1 `Fab_Line.`get_start():

Fab_Line.get_start(self) -> cadquery.occ_impl.geom.Vector:

Return the start point of the Fab_Line.

### <a name="geometry----produce"></a>9.2 `Fab_Line.`produce():

Fab_Line.produce(self, geometry_context: Geometry.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Any:

Return line segment after moving it into Geometry group.


## <a name="geometry--fab-plane"></a>10 Class Fab_Plane:

A Plane class.
* *Contact* (Vector):  The contact point of the plane.
* *Normal* (Vector): The normal to the plane.

### <a name="geometry----point-project"></a>10.1 `Fab_Plane.`point_project():

Fab_Plane.point_project(self, point: cadquery.occ_impl.geom.Vector) -> cadquery.occ_impl.geom.Vector:

Project a point onto a plane.

### <a name="geometry----adjust"></a>10.2 `Fab_Plane.`adjust():

Fab_Plane.adjust(self, delta: float) -> 'Fab_Plane':

Return a new Fab_Plane that has been adjusted up/down the normal by a delta.

### <a name="geometry----rotate-to-z-axis"></a>10.3 `Fab_Plane.`rotate_to_z_axis():

Fab_Plane.rotate_to_z_axis(self, point: cadquery.occ_impl.geom.Vector, reversed: bool = False, tracing: str = '') -> cadquery.occ_impl.geom.Vector:

Rotate a point around the origin until the normal aligns with the +Z axis.
Arguments:
* *point* (Vector): The point to rotate.
* *reversed* (bool = False): If True, do the inverse rotation.

Returns:
* (Vector): The rotated vector position.


## <a name="geometry--fab-query"></a>11 Class Fab_Query:

A CadQuery Workplane wrapper.
This class creates CadQuery Workplane provides a consistent head of the Workplane chain..
CadQuery Operations are added as needed.

Attributes:
* *Plane* (Fab_Plane): The plain to use for CadQuery initialization.
* *WorkPlane: (cadquery.Workplane): The resulting CadQuery Workplane object.

### <a name="geometry----circle"></a>11.1 `Fab_Query.`circle():

Fab_Query.circle(self, center: cadquery.occ_impl.geom.Vector, radius: float, for_construction=False, tracing: str = '') -> None:

Draw a circle to a point.

### <a name="geometry----close"></a>11.2 `Fab_Query.`close():

Fab_Query.close(self, tracing: str = '') -> None:

Close a sequence of arcs and lines.

### <a name="geometry----copy-workplane"></a>11.3 `Fab_Query.`copy_workplane():

Fab_Query.copy_workplane(self, plane: Geometry.Fab_Plane, tracing: str = '') -> None:

Create a new CadQuery workplane and push it onto the stack.

### <a name="geometry----cut-blind"></a>11.4 `Fab_Query.`cut_blind():

Fab_Query.cut_blind(self, depth: float, tracing: str = '') -> None:

Use the current 2D object to cut a pocket to a known depth.

### <a name="geometry----extrude"></a>11.5 `Fab_Query.`extrude():

Fab_Query.extrude(self, depth: float, tracing: str = '') -> None:

Extrude current 2D object to a known depth.

### <a name="geometry----hole"></a>11.6 `Fab_Query.`hole():

Fab_Query.hole(self, diameter: float, depth: float, tracing: str = '') -> None:

Drill a hole.

### <a name="geometry----line-to"></a>11.7 `Fab_Query.`line_to():

Fab_Query.line_to(self, end: cadquery.occ_impl.geom.Vector, for_construction=False, tracing: str = '') -> None:

Draw a line to a point.

### <a name="geometry----move-to"></a>11.8 `Fab_Query.`move_to():

Fab_Query.move_to(self, point: cadquery.occ_impl.geom.Vector, tracing: str = '') -> None:

Draw a line to a point.

### <a name="geometry----show"></a>11.9 `Fab_Query.`show():

Fab_Query.show(self, label: str, tracing: str = '') -> None:

Print a detailed dump of a Fab_Query.

### <a name="geometry----subtract"></a>11.10 `Fab_Query.`subtract():

Fab_Query.subtract(self, remove_solid: 'Fab_Query', tracing: str = '') -> None:

Subtract one solid form a Fab_Query.

### <a name="geometry----three-point-arc"></a>11.11 `Fab_Query.`three_point_arc():

Fab_Query.three_point_arc(self, middle: cadquery.occ_impl.geom.Vector, end: cadquery.occ_impl.geom.Vector, for_construction: bool = False, tracing: str = '') -> None:

Draw a three point arc.



