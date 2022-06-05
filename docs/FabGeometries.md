# FabGeometries: Geometry: A module for constructing 2D geometry.

## Table of Contents (alphabetical order):

* 1 Class: [FabCircle](#fabgeometries--fabcircle):
  * 1.1 [get_hash()](#fabgeometries----get-hash): Feturn FabCircle hash.
  * 1.2 [get_geometry_info()](#fabgeometries----get-geometry-info): Return information about FabGeometry.
  * 1.3 [project_to_plane()](#fabgeometries----project-to-plane): Return a new FabCircle projected onto a plane.
  * 1.4 [produce()](#fabgeometries----produce): Produce the FreeCAD objects needed for FabPolygon.
  * 1.5 [get_geometries()](#fabgeometries----get-geometries): Return the FabPolygon lines and arcs.
* 2 Class: [FabGeometry](#fabgeometries--fabgeometry):
  * 2.1 [get_hash()](#fabgeometries----get-hash): Return FabGeometry hash.
  * 2.2 [produce()](#fabgeometries----produce): Produce the necessary FreeCAD objects for the FabGeometry.
  * 2.3 [project_to_plane()](#fabgeometries----project-to-plane): Return a new FabGeometry projected onto a plane.
  * 2.4 [get_geometry_info()](#fabgeometries----get-geometry-info): Return information about FabGeometry.
* 3 Class: [FabPolygon](#fabgeometries--fabpolygon):
  * 3.1 [get_geometry_info()](#fabgeometries----get-geometry-info): Return the values needed for a FabGeometry_Info from a FabPolygon.
  * 3.2 [get_hash()](#fabgeometries----get-hash): Return the FabPolygon Hash.
  * 3.3 [project_to_plane()](#fabgeometries----project-to-plane): Return nre FabPolygon projected onto a plane.
  * 3.4 [get_geometries()](#fabgeometries----get-geometries): Return the FabPolygon lines and arcs.
  * 3.5 [produce()](#fabgeometries----produce): Produce the FreeCAD objects needed for FabPolygon.
* 4 Class: [Fab_Arc](#fabgeometries--fab-arc):
  * 4.1 [produce()](#fabgeometries----produce): Return line segment after moving it into Geometry group.
* 5 Class: [Fab_Circle](#fabgeometries--fab-circle):
  * 5.1 [produce()](#fabgeometries----produce): Return line segment after moving it into Geometry group.
* 6 Class: [Fab_Fillet](#fabgeometries--fab-fillet):
  * 6.1 [compute_arc()](#fabgeometries----compute-arc): Return the arc associated with a Fab_Fillet with non-zero radius.
  * 6.2 [plane_2d_project()](#fabgeometries----plane-2d-project): Project the Apex onto a plane.
  * 6.3 [compute_fillet_area_perimeter()](#fabgeometries----compute-fillet-area-perimeter): Return the excluded fillet area and the perimeter for a Fab_Fillet.
  * 6.4 [get_geometries()](#fabgeometries----get-geometries): NO DOC STRING!
* 7 Class: [Fab_Geometry](#fabgeometries--fab-geometry):
  * 7.1 [produce()](#fabgeometries----produce): NO DOC STRING!
  * 7.2 [get_start()](#fabgeometries----get-start): Return start point of geometry.
* 8 Class: [Fab_GeometryContext](#fabgeometries--fab-geometrycontext):
  * 8.1 [copy()](#fabgeometries----copy): Return a Fab_GeometryContext copy.
  * 8.2 [copy_with_plane_adjust()](#fabgeometries----copy-with-plane-adjust): Return a Fab_GeometryContext copy with the plane adjusted up/down.
  * 8.3 [set_geometry_group()](#fabgeometries----set-geometry-group): Set the GeometryContext geometry group.
* 9 Class: [Fab_GeometryInfo](#fabgeometries--fab-geometryinfo):
* 10 Class: [Fab_Line](#fabgeometries--fab-line):
  * 10.1 [get_start()](#fabgeometries----get-start): Return the start point of the Fab_Line.
  * 10.2 [produce()](#fabgeometries----produce): Return line segment after moving it into Geometry group.
* 11 Class: [Fab_Plane](#fabgeometries--fab-plane):
  * 11.1 [point_project()](#fabgeometries----point-project): Project a point onto a plane.
  * 11.2 [adjust()](#fabgeometries----adjust): Return a new Fab_Plane that has been adjusted up/down the normal by a delta.
  * 11.3 [rotate_to_z_axis()](#fabgeometries----rotate-to-z-axis): Rotate a point around the origin until the normal aligns with the +Z axis.
* 12 Class: [Fab_Query](#fabgeometries--fab-query):
  * 12.1 [circle()](#fabgeometries----circle): Draw a circle to a point.
  * 12.2 [close()](#fabgeometries----close): Close a sequence of arcs and lines.
  * 12.3 [copy_workplane()](#fabgeometries----copy-workplane): Create a new CadQuery workplane and push it onto the stack.
  * 12.4 [extrude()](#fabgeometries----extrude): Extrude current 2D object to a known depth.
  * 12.5 [hole()](#fabgeometries----hole): Drill a hole.
  * 12.6 [line_to()](#fabgeometries----line-to): Draw a line to a point.
  * 12.7 [move_to()](#fabgeometries----move-to): Draw a line to a point.
  * 12.8 [show()](#fabgeometries----show): Print a detailed dump of a Fab_Query.
  * 12.9 [subtract()](#fabgeometries----subtract): Subtract one solid form a Fab_Query.
  * 12.10 [three_point_arc()](#fabgeometries----three-point-arc): Draw a three point arc.

## <a name="fabgeometries--fabcircle"></a>1 Class FabCircle:

A circle with a center and a radius.
This is actually a sphere of at a specified location and diameter.  It gets cut into
circle later on.

Attributes:
* *Center* (Vector): The circle center.
* *Normal* (Vector): The normal to circle plane.
* *Diameter* (float): The diameter in millimeters.

### <a name="fabgeometries----get-hash"></a>1.1 `FabCircle.`get_hash():

FabCircle.get_hash(self) -> Tuple[Any, ...]:

Feturn FabCircle hash.

### <a name="fabgeometries----get-geometry-info"></a>1.2 `FabCircle.`get_geometry_info():

FabCircle.get_geometry_info(self, plane: FabGeometries.Fab_Plane, tracing: str = '') -> Tuple[float, float, float, float]:

Return information about FabGeometry.
Arguments:
* *plane* (Fab_Plane): The plane to project FabGeometry onto.

Returns:
* (float): The circle area in square millimeters.
* (float): The perimeter length in millimeters.
* (float): -1 since there are no internal radius corners for a circle.
* (float): The circle radius in millimeters.

### <a name="fabgeometries----project-to-plane"></a>1.3 `FabCircle.`project_to_plane():

FabCircle.project_to_plane(self, plane: FabGeometries.Fab_Plane, tracing: str = '') -> 'FabCircle':

Return a new FabCircle projected onto a plane.
Arguments:
* *plane* (Fab_Plane): Plane to project to.

Returns:
* (FabCircle): The newly projected FabCicle.

### <a name="fabgeometries----produce"></a>1.4 `FabCircle.`produce():

FabCircle.produce(self, geometry_context: FabGeometries.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Tuple[Any, ...]:

Produce the FreeCAD objects needed for FabPolygon.

### <a name="fabgeometries----get-geometries"></a>1.5 `FabCircle.`get_geometries():

FabCircle.get_geometries(self) -> Tuple[FabGeometries.Fab_Geometry, ...]:

Return the FabPolygon lines and arcs.


## <a name="fabgeometries--fabgeometry"></a>2 Class FabGeometry:

The base class for FabPolygon and FabCircle.

### <a name="fabgeometries----get-hash"></a>2.1 `FabGeometry.`get_hash():

FabGeometry.get_hash(self) -> Tuple[Any, ...]:

Return FabGeometry hash.

### <a name="fabgeometries----produce"></a>2.2 `FabGeometry.`produce():

FabGeometry.produce(self, geometry_context: FabGeometries.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Tuple[Any, ...]:

Produce the necessary FreeCAD objects for the FabGeometry.

### <a name="fabgeometries----project-to-plane"></a>2.3 `FabGeometry.`project_to_plane():

FabGeometry.project_to_plane(self, plane: FabGeometries.Fab_Plane) -> 'FabGeometry':

Return a new FabGeometry projected onto a plane.

### <a name="fabgeometries----get-geometry-info"></a>2.4 `FabGeometry.`get_geometry_info():

FabGeometry.get_geometry_info(self, plane: FabGeometries.Fab_Plane, tracing: str = '') -> Tuple[float, float, float, float]:

Return information about FabGeometry.
Arguments:
* *plane* (Fab_Plane): The plane to project the FabGeometry onto.

Returns:
* (float): The geometry area in square millimeters.
* (float): The perimeter length in millimeters.
* (float):
  The minimum internal radius in millimeters. -1.0 means there is no internal radius.
* (float): The minimum external radius in millimeters. 0 means that all corners are "sharp".


## <a name="fabgeometries--fabpolygon"></a>3 Class FabPolygon:

An immutable polygon with rounded corners.
    A FabPolygon is represented as a sequence of corners (i.e. a Vector) where each corner can
    optionally be filleted with a radius.  In order to make it easier to use, a corner can be
    specified as simple Vector or as a tuple that specifies a Vector and a radius.  The radius
    is in millimeters and can be provided as either a Python int or float.  When an explicit
    fillet radius is not specified, higher levels in the software stack will typically substitute
x    in a deburr radius for external corners and an internal tool radius for internal corners.
    FabPolygon's are frozen and can not be modified after creation.  Since Vector's are mutable,
    a copy of each vector stored inside the FabPolygon.

    Attributes:
    * *Corners* (Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...]):
      See description below for more on corners.

    Constructor:
    * FabPolygon(Corners):

    Example:
    ```
         polygon: FabPolyon = FabPolygon((
             Vector(-10, -10, 0),  # Lower left (no radius)
             Vector(10, -10, 0),  # Lower right (no radius)
             (Vector(10, 10, 0), 5),  # Upper right (5mm radius)
             (Vector(-0, 10, 0), 5.5),  # Upper right (5.5mm radius)
         ), "Name")
    ```

### <a name="fabgeometries----get-geometry-info"></a>3.1 `FabPolygon.`get_geometry_info():

FabPolygon.get_geometry_info(self, plane: FabGeometries.Fab_Plane, tracing: str = '') -> Tuple[float, float, float, float]:

Return the values needed for a FabGeometry_Info from a FabPolygon.
Method Arguments:
* *plane* (Fab_Plane): The FabPolygon projection to use for Area computation.

Returns:
* (float): The area of the projected FabPolygon.
* (float): The polygon perimeter in millimeters with rounded corners.
* (float):
  The minimum internal radius corners for the polygon.
  -1.0 means no internal corners.
* (float): The minimum external radius corners for the polygon.

### <a name="fabgeometries----get-hash"></a>3.2 `FabPolygon.`get_hash():

FabPolygon.get_hash(self) -> Tuple[Any, ...]:

Return the FabPolygon Hash.

### <a name="fabgeometries----project-to-plane"></a>3.3 `FabPolygon.`project_to_plane():

FabPolygon.project_to_plane(self, plane: FabGeometries.Fab_Plane, tracing: str = '') -> 'FabPolygon':

Return nre FabPolygon projected onto a plane.
Arguments:
* *plane* (Fab_Plane): The plane to project onto.

Returns:
* (FabPolyGon): The newly projected FabPolygon.

### <a name="fabgeometries----get-geometries"></a>3.4 `FabPolygon.`get_geometries():

FabPolygon.get_geometries(self, contact: cadquery.occ_impl.geom.Vector, Normal: cadquery.occ_impl.geom.Vector) -> Tuple[FabGeometries.Fab_Geometry, ...]:

Return the FabPolygon lines and arcs.

### <a name="fabgeometries----produce"></a>3.5 `FabPolygon.`produce():

FabPolygon.produce(self, geometry_context: FabGeometries.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Tuple[Any, ...]:

Produce the FreeCAD objects needed for FabPolygon.


## <a name="fabgeometries--fab-arc"></a>4 Class Fab_Arc:

An internal representation an arc geometry.
Attributes:
* *Apex* (Vector): The fillet apex point.
* *Radius* (float): The arc radius in millimeters.
* *Center* (Vector): The arc center point.
* *Start* (Vector): The Arc start point.
* *Middle* (Vector): The Arc midpoint.
* *Finish* (Vector): The Arc finish point.

Constructor:
* Fab_Arc(Apex, Radius, Center, Start, Middle, Finish)

### <a name="fabgeometries----produce"></a>4.1 `Fab_Arc.`produce():

Fab_Arc.produce(self, geometry_context: FabGeometries.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Any:

Return line segment after moving it into Geometry group.


## <a name="fabgeometries--fab-circle"></a>5 Class Fab_Circle:

An internal representation of a circle geometry.
Attributes:
* *Center (Vector): The circle center.
* *Diameter (float): The circle diameter in millimeters.

### <a name="fabgeometries----produce"></a>5.1 `Fab_Circle.`produce():

Fab_Circle.produce(self, geometry_context: FabGeometries.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Any:

Return line segment after moving it into Geometry group.


## <a name="fabgeometries--fab-fillet"></a>6 Class Fab_Fillet:

An object that represents one fillet of a FabPolygon.
Attributes:
* *Apex* (Vector): The apex corner point for the fillet.
* *Radius* (float): The fillet radius in millimeters.
* *Before* (Fab_Fillet): The previous Fab_Fillet in the FabPolygon.
* *After* (Fab_Fillet): The next Fab_Fillet in the FabPolygon.
* *Arc* (Optional[Fab_Arc]): The fillet Arc if Radius is non-zero.
* *Line* (Optional[Fab_Line]): The line that connects to the previous Fab_Fillet

### <a name="fabgeometries----compute-arc"></a>6.1 `Fab_Fillet.`compute_arc():

Fab_Fillet.compute_arc(self, tracing: str = '') -> FabGeometries.Fab_Arc:

Return the arc associated with a Fab_Fillet with non-zero radius.

### <a name="fabgeometries----plane-2d-project"></a>6.2 `Fab_Fillet.`plane_2d_project():

Fab_Fillet.plane_2d_project(self, plane: FabGeometries.Fab_Plane) -> None:

Project the Apex onto a plane.
Arguments:
* *plane* (Fab_Plane): The plane to project the Fab_Fillet onto.

Modifies Fab_Fillet.

### <a name="fabgeometries----compute-fillet-area-perimeter"></a>6.3 `Fab_Fillet.`compute_fillet_area_perimeter():

Fab_Fillet.compute_fillet_area_perimeter(self, tracing: str = '') -> Tuple[float, float]:

Return the excluded fillet area and the perimeter for a Fab_Fillet.
To be more concise, the fillet_area is the area outside of the fillet arc, but inside
the straight lines "corner" of the fillet.

Returns:
* (float): The excluded area of a fillet (i.e. the area not under the arc segment.)
* (float): The length the of the arc segment.

### <a name="fabgeometries----get-geometries"></a>6.4 `Fab_Fillet.`get_geometries():

Fab_Fillet.get_geometries(self) -> Tuple[FabGeometries.Fab_Geometry, ...]:

NO DOC STRING!


## <a name="fabgeometries--fab-geometry"></a>7 Class Fab_Geometry:

An Internal base class for Fab_Arc, Fab_Circle, and Fab_Line.
All Fab_Geometry classes are immutable (i.e. frozen.)

### <a name="fabgeometries----produce"></a>7.1 `Fab_Geometry.`produce():

Fab_Geometry.produce(self, geometry_context: FabGeometries.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Any:

NO DOC STRING!

### <a name="fabgeometries----get-start"></a>7.2 `Fab_Geometry.`get_start():

Fab_Geometry.get_start(self) -> cadquery.occ_impl.geom.Vector:

Return start point of geometry.


## <a name="fabgeometries--fab-geometrycontext"></a>8 Class Fab_GeometryContext:

GeometryProduce: Context needed to produce FreeCAD geometry objects.
Attributes:
* *Plane* (Fab_Plane): Plane to use.
* *Query* (Fab_Query): The CadQuery Workplane wrapper to use.
* *_GeometryGroup*: (App.DocumentObjectGroup):
  The FreeCAD group to store FreeCAD Geometry objects into.
  This field needs to be set prior to use with set_geometry_group() method.

### <a name="fabgeometries----copy"></a>8.1 `Fab_GeometryContext.`copy():

Fab_GeometryContext.copy(self, tracing: str = '') -> 'Fab_GeometryContext':

Return a Fab_GeometryContext copy.

### <a name="fabgeometries----copy-with-plane-adjust"></a>8.2 `Fab_GeometryContext.`copy_with_plane_adjust():

Fab_GeometryContext.copy_with_plane_adjust(self, delta: float, tracing: str = '') -> 'Fab_GeometryContext':

Return a Fab_GeometryContext copy with the plane adjusted up/down.

### <a name="fabgeometries----set-geometry-group"></a>8.3 `Fab_GeometryContext.`set_geometry_group():

Fab_GeometryContext.set_geometry_group(self, geometry_group: Any) -> None:

Set the GeometryContext geometry group.


## <a name="fabgeometries--fab-geometryinfo"></a>9 Class Fab_GeometryInfo:

Information about a FabGeomtry object.
Attributes:
* Geometry (FabGeometry): The FabGeometry object used.
* Plane (Fab_Plane): The geometry plane to project onto.
* Area (float): The geometry area in square millimeters.
* Perimeter (float): The perimeter length in millimetes.
* MinimumInternalRadius:
  The minimum internal radius in millimeters. -1.0 means there is no internal radius.
* MinimumExternalRadius:
  The minimum external radius in millimeters.

Constructor:
* Fab_GeometryInfo(Geometry)


## <a name="fabgeometries--fab-line"></a>10 Class Fab_Line:

An internal representation of a line segment geometry.
Attributes:
* *Start (Vector): The line segment start point.
* *Finish (Vector): The line segment finish point.

Constructor:
* Fab_Line(Start, Finish)

### <a name="fabgeometries----get-start"></a>10.1 `Fab_Line.`get_start():

Fab_Line.get_start(self) -> cadquery.occ_impl.geom.Vector:

Return the start point of the Fab_Line.

### <a name="fabgeometries----produce"></a>10.2 `Fab_Line.`produce():

Fab_Line.produce(self, geometry_context: FabGeometries.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Any:

Return line segment after moving it into Geometry group.


## <a name="fabgeometries--fab-plane"></a>11 Class Fab_Plane:

A Plane class.
* *Contact* (Vector):  The contact point of the plane.
* *Normal* (Vector): The normal to the plane.

### <a name="fabgeometries----point-project"></a>11.1 `Fab_Plane.`point_project():

Fab_Plane.point_project(self, point: cadquery.occ_impl.geom.Vector) -> cadquery.occ_impl.geom.Vector:

Project a point onto a plane.

### <a name="fabgeometries----adjust"></a>11.2 `Fab_Plane.`adjust():

Fab_Plane.adjust(self, delta: float) -> 'Fab_Plane':

Return a new Fab_Plane that has been adjusted up/down the normal by a delta.

### <a name="fabgeometries----rotate-to-z-axis"></a>11.3 `Fab_Plane.`rotate_to_z_axis():

Fab_Plane.rotate_to_z_axis(self, point: cadquery.occ_impl.geom.Vector, reversed: bool = False, tracing: str = '') -> cadquery.occ_impl.geom.Vector:

Rotate a point around the origin until the normal aligns with the +Z axis.
Arguments:
* *point* (Vector): The point to rotate.
* *reversed* (bool = False): If True, do the inverse rotation.

Returns:
* (Vector): The rotated vector position.


## <a name="fabgeometries--fab-query"></a>12 Class Fab_Query:

A CadQuery Workplane wrapper.
This class creates CadQuery Workplane provides a consistent head of the Workplane chain..
CadQuery Operations are added as needed.

Attributes:
* *Plane* (Fab_Plane): The plane to use for CadQuery initialization.
* *WorkPlane: (cadquery.Workplane): The resulting CadQuery Workplane object.

### <a name="fabgeometries----circle"></a>12.1 `Fab_Query.`circle():

Fab_Query.circle(self, center: cadquery.occ_impl.geom.Vector, radius: float, for_construction=False, tracing: str = '') -> None:

Draw a circle to a point.

### <a name="fabgeometries----close"></a>12.2 `Fab_Query.`close():

Fab_Query.close(self, tracing: str = '') -> None:

Close a sequence of arcs and lines.

### <a name="fabgeometries----copy-workplane"></a>12.3 `Fab_Query.`copy_workplane():

Fab_Query.copy_workplane(self, plane: FabGeometries.Fab_Plane, tracing: str = '') -> None:

Create a new CadQuery workplane and push it onto the stack.

### <a name="fabgeometries----extrude"></a>12.4 `Fab_Query.`extrude():

Fab_Query.extrude(self, depth: float, tracing: str = '') -> None:

Extrude current 2D object to a known depth.

### <a name="fabgeometries----hole"></a>12.5 `Fab_Query.`hole():

Fab_Query.hole(self, diameter: float, depth: float, tracing: str = '') -> None:

Drill a hole.

### <a name="fabgeometries----line-to"></a>12.6 `Fab_Query.`line_to():

Fab_Query.line_to(self, end: cadquery.occ_impl.geom.Vector, for_construction=False, tracing: str = '') -> None:

Draw a line to a point.

### <a name="fabgeometries----move-to"></a>12.7 `Fab_Query.`move_to():

Fab_Query.move_to(self, point: cadquery.occ_impl.geom.Vector, tracing: str = '') -> None:

Draw a line to a point.

### <a name="fabgeometries----show"></a>12.8 `Fab_Query.`show():

Fab_Query.show(self, label: str, tracing: str = '') -> None:

Print a detailed dump of a Fab_Query.

### <a name="fabgeometries----subtract"></a>12.9 `Fab_Query.`subtract():

Fab_Query.subtract(self, remove_solid: 'Fab_Query', tracing: str = '') -> None:

Subtract one solid form a Fab_Query.

### <a name="fabgeometries----three-point-arc"></a>12.10 `Fab_Query.`three_point_arc():

Fab_Query.three_point_arc(self, middle: cadquery.occ_impl.geom.Vector, end: cadquery.occ_impl.geom.Vector, for_construction: bool = False, tracing: str = '') -> None:

Draw a three point arc.



