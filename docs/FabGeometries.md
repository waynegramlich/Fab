# FabGeometries: Geometry: A module for constructing 2D geometry.

## Table of Contents (alphabetical order):

* 1 Class: [FabCircle](#fabgeometries--fabcircle):
  * 1.1 [getHash()](#fabgeometries----gethash): Return FabCircle hash.
  * 1.2 [projectToPlane()](#fabgeometries----projecttoplane): Return a new FabCircle projected onto a plane.
  * 1.3 [produce()](#fabgeometries----produce): Produce the FreeCAD objects needed for FabPolygon.
  * 1.4 [get_geometries()](#fabgeometries----get-geometries): Return the FabPolygon lines and arcs.
* 2 Class: [FabGeometry](#fabgeometries--fabgeometry):
  * 2.1 [getHash()](#fabgeometries----gethash): Return FabGeometry hash.
  * 2.2 [produce()](#fabgeometries----produce): Produce the necessary FreeCAD objects for the FabGeometry.
  * 2.3 [projectToPlane()](#fabgeometries----projecttoplane): Return a new FabGeometry projected onto a plane.
* 3 Class: [FabGeometryInfo](#fabgeometries--fabgeometryinfo):
* 4 Class: [FabPlane](#fabgeometries--fabplane):
  * 4.1 [getHash()](#fabgeometries----gethash): Return a FabPlane hash value.
  * 4.2 [projectPoint()](#fabgeometries----projectpoint): Project a point onto a plane.
  * 4.3 [adjust()](#fabgeometries----adjust): Return a new FabPlane that has been adjusted up/down the normal by a delta.
  * 4.4 [rotate_to_z_axis()](#fabgeometries----rotate-to-z-axis): Rotate a point around the origin until the normal aligns with the +Z axis.
  * 4.5 [projectPointToXY()](#fabgeometries----projectpointtoxy): Project a rotated point onto the X/Y plane.
* 5 Class: [FabPolygon](#fabgeometries--fabpolygon):
  * 5.1 [getHash()](#fabgeometries----gethash): Return the FabPolygon Hash.
  * 5.2 [projectToPlane()](#fabgeometries----projecttoplane): Return nre FabPolygon projected onto a plane.
  * 5.3 [get_geometries()](#fabgeometries----get-geometries): Return the FabPolygon lines and arcs.
  * 5.4 [produce()](#fabgeometries----produce): Produce the FreeCAD objects needed for FabPolygon.
* 6 Class: [Fab_Arc](#fabgeometries--fab-arc):
  * 6.1 [produce()](#fabgeometries----produce): Return line segment after moving it into Geometry group.
* 7 Class: [Fab_Circle](#fabgeometries--fab-circle):
  * 7.1 [produce()](#fabgeometries----produce): Return line segment after moving it into Geometry group.
* 8 Class: [Fab_Fillet](#fabgeometries--fab-fillet):
  * 8.1 [compute_arc()](#fabgeometries----compute-arc): Return the arc associated with a Fab_Fillet with non-zero radius.
  * 8.2 [plane_2d_project()](#fabgeometries----plane-2d-project): Project the Apex onto a plane.
  * 8.3 [compute_fillet_area_perimeter()](#fabgeometries----compute-fillet-area-perimeter): Return the excluded fillet area and the perimeter for a Fab_Fillet.
  * 8.4 [get_geometries()](#fabgeometries----get-geometries): NO DOC STRING!
* 9 Class: [Fab_Geometry](#fabgeometries--fab-geometry):
  * 9.1 [produce()](#fabgeometries----produce): NO DOC STRING!
  * 9.2 [get_start()](#fabgeometries----get-start): Return start point of geometry.
* 10 Class: [Fab_GeometryContext](#fabgeometries--fab-geometrycontext):
  * 10.1 [copy()](#fabgeometries----copy): Return a Fab_GeometryContext copy.
  * 10.2 [copy_with_plane_adjust()](#fabgeometries----copy-with-plane-adjust): Return a Fab_GeometryContext copy with the plane adjusted up/down.
  * 10.3 [set_geometry_group()](#fabgeometries----set-geometry-group): Set the GeometryContext geometry group.
* 11 Class: [Fab_GeometryInfo](#fabgeometries--fab-geometryinfo):
  * 11.1 [toTuple()](#fabgeometries----totuple): Return the area, perimeter, internal/external radius for a FabGeometry.
* 12 Class: [Fab_Line](#fabgeometries--fab-line):
  * 12.1 [get_start()](#fabgeometries----get-start): Return the start point of the Fab_Line.
  * 12.2 [produce()](#fabgeometries----produce): Return line segment after moving it into Geometry group.
* 13 Class: [Fab_Query](#fabgeometries--fab-query):
  * 13.1 [circle()](#fabgeometries----circle): Draw a circle to a point.
  * 13.2 [close()](#fabgeometries----close): Close a sequence of arcs and lines.
  * 13.3 [copy_workplane()](#fabgeometries----copy-workplane): Create a new CadQuery workplane and push it onto the stack.
  * 13.4 [extrude()](#fabgeometries----extrude): Extrude current 2D object to a known depth.
  * 13.5 [hole()](#fabgeometries----hole): Drill a hole.
  * 13.6 [line_to()](#fabgeometries----line-to): Draw a line to a point.
  * 13.7 [move_to()](#fabgeometries----move-to): Draw a line to a point.
  * 13.8 [show()](#fabgeometries----show): Print a detailed dump of a Fab_Query.
  * 13.9 [subtract()](#fabgeometries----subtract): Subtract one solid form a Fab_Query.
  * 13.10 [three_point_arc()](#fabgeometries----three-point-arc): Draw a three point arc.

## <a name="fabgeometries--fabcircle"></a>1 Class FabCircle:

Represents a circle on a plane.
Attributes:
* *Plane* (FabPlane): The plane the circle center is projected onto.
* *Center* (Vector): The circle center after it has been projected.
* *Diameter* (float): The circle diameter in millimeters.
* *Box* (FabBox): The box that encloses FabCircle
* *GeometryInfo* (FabGeometryInfo):
   The geometry information about the FabCircle (e.g. Area, Perimeter, etc.)

Constructor:
* FabCircle(Plane, Center, Diameter)

### <a name="fabgeometries----gethash"></a>1.1 `FabCircle.`getHash():

FabCircle.getHash(self) -> Tuple[Any, ...]:

Return FabCircle hash.

### <a name="fabgeometries----projecttoplane"></a>1.2 `FabCircle.`projectToPlane():

FabCircle.projectToPlane(self, plane: FabGeometries.FabPlane, tracing: str = '') -> 'FabCircle':

Return a new FabCircle projected onto a plane.
Arguments:
* *plane* (FabPlane): Plane to project to.

Returns:
* (FabCircle): The newly projected FabCicle.

### <a name="fabgeometries----produce"></a>1.3 `FabCircle.`produce():

FabCircle.produce(self, geometry_context: FabGeometries.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Tuple[Any, ...]:

Produce the FreeCAD objects needed for FabPolygon.

### <a name="fabgeometries----get-geometries"></a>1.4 `FabCircle.`get_geometries():

FabCircle.get_geometries(self) -> Tuple[FabGeometries.Fab_Geometry, ...]:

Return the FabPolygon lines and arcs.


## <a name="fabgeometries--fabgeometry"></a>2 Class FabGeometry:

The base class for FabPolygon and FabCircle.
Attributes:
* *Plane* (FabPlane): The plane to project the geometry onto.
* *Box* (FabBox): A 3D box that encloses the gemetery.
* *GeometryInfo* (FabGeometryInfo): The geometry information (e.g. area, peremeteter, etc.)

### <a name="fabgeometries----gethash"></a>2.1 `FabGeometry.`getHash():

FabGeometry.getHash(self) -> Tuple[Any, ...]:

Return FabGeometry hash.

### <a name="fabgeometries----produce"></a>2.2 `FabGeometry.`produce():

FabGeometry.produce(self, geometry_context: FabGeometries.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Tuple[Any, ...]:

Produce the necessary FreeCAD objects for the FabGeometry.

### <a name="fabgeometries----projecttoplane"></a>2.3 `FabGeometry.`projectToPlane():

FabGeometry.projectToPlane(self, plane: FabGeometries.FabPlane) -> 'FabGeometry':

Return a new FabGeometry projected onto a plane.


## <a name="fabgeometries--fabgeometryinfo"></a>3 Class FabGeometryInfo:

Geometric information about area, perimeter, etc.
Attributes:
* Area (float): The geometry area in square millimeters.
* Perimeter (float): The perimeter length in millimeters.
* MinimumInternalRadius:
  The minimum internal corner radius in millimeters. -1.0 means there are not internal corners
* MinimumExternalRadius:
  The minimum external corner radius in millimeters, or for circles, this is the circle radius.

Constructor:
* FabGeometryInfo(Area, Perimeter, MinimumInternalRadius, MinimumExternalRadius)


## <a name="fabgeometries--fabplane"></a>4 Class FabPlane:

An immutable Plane class.
* *Contact* (Vector):  Some contact point that anywhere in the plane.
* *Normal* (Vector): The normal to the plane.

### <a name="fabgeometries----gethash"></a>4.1 `FabPlane.`getHash():

FabPlane.getHash(self) -> Tuple[Any, ...]:

Return a FabPlane hash value.

### <a name="fabgeometries----projectpoint"></a>4.2 `FabPlane.`projectPoint():

FabPlane.projectPoint(self, point: cadquery.occ_impl.geom.Vector) -> cadquery.occ_impl.geom.Vector:

Project a point onto a plane.

### <a name="fabgeometries----adjust"></a>4.3 `FabPlane.`adjust():

FabPlane.adjust(self, delta: float) -> 'FabPlane':

Return a new FabPlane that has been adjusted up/down the normal by a delta.

### <a name="fabgeometries----rotate-to-z-axis"></a>4.4 `FabPlane.`rotate_to_z_axis():

FabPlane.rotate_to_z_axis(self, point: cadquery.occ_impl.geom.Vector, reversed: bool = False, tracing: str = '') -> cadquery.occ_impl.geom.Vector:

Rotate a point around the origin until the normal aligns with the +Z axis.
Arguments:
* *point* (Vector): The point to rotate.
* *reversed* (bool = False): If True, do the inverse rotation.

Returns:
* (Vector): The rotated vector position.

### <a name="fabgeometries----projectpointtoxy"></a>4.5 `FabPlane.`projectPointToXY():

FabPlane.projectPointToXY(self, unrotated_point: cadquery.occ_impl.geom.Vector) -> cadquery.occ_impl.geom.Vector:

Project a rotated point onto the X/Y plane.
Take a point do the following:
1. Project the point onto the plane (i.e. *self*)
2. Rotate the plane around the origin until it is parallel to the XY plane.
3. Project the point down to the XY plane.

Arguments:
* *unrotated_point* (Vector): The point before rotation.

Returns:
* (Vector): The point projected point.


## <a name="fabgeometries--fabpolygon"></a>5 Class FabPolygon:

An immutable polygon with rounded corners.
A FabPolygon is represented as a sequence of corners (i.e. a Vector) where each corner can
optionally be filleted with a radius.  In order to make it easier to use, a corner can be
specified either as simple Vector or as a tuple that specifies both a Vector and a radius.
The radius is in millimeters and can be provided as either a Python int or float.  When an
explicit fillet radius is not specified, higher levels in the software stack *may* substitute
in a deburr radius for external corners and an internal tool radius for internal corners.
FabPolygon's are frozen and can not be modified after creation.  Since Vector's are mutable,
a private copy of each vector stored inside the FabPolygon.

Attributes:
* *Plane* (FabPlane: The plane that all of the corners are projected onto.
* *Corners* (Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...]):
  See description immediately above for more on corners.
* *GeometryInfo* (FabGeometryInfo): The geometry information (e.g. area, perimeter, etc.)

Constructor:
* FabPolygon(Plane, Corners):

Example:
```
     xy_plane: FabPlane = FabPlane(Vector(0, 0, 0), Vector(0, 0, 1))
     polygon: FabPolygon = FabPolygon(xy_plane, (
         Vector(-10, -10, 0),  # Lower left (no radius)
         Vector(10, -10, 0),  # Lower right (no radius)
         (Vector(10, 10, 0), 5),  # Upper right (5mm radius)
         (Vector(-0, 10, 0), 5.5),  # Upper right (5.5mm radius)
     ), "Name")
```

### <a name="fabgeometries----gethash"></a>5.1 `FabPolygon.`getHash():

FabPolygon.getHash(self) -> Tuple[Any, ...]:

Return the FabPolygon Hash.

### <a name="fabgeometries----projecttoplane"></a>5.2 `FabPolygon.`projectToPlane():

FabPolygon.projectToPlane(self, plane: FabGeometries.FabPlane, tracing: str = '') -> 'FabPolygon':

Return nre FabPolygon projected onto a plane.
Arguments:
* *plane* (FabPlane): The plane to project onto.

Returns:
* (FabPolyGon): The newly projected FabPolygon.

### <a name="fabgeometries----get-geometries"></a>5.3 `FabPolygon.`get_geometries():

FabPolygon.get_geometries(self) -> Tuple[FabGeometries.Fab_Geometry, ...]:

Return the FabPolygon lines and arcs.

### <a name="fabgeometries----produce"></a>5.4 `FabPolygon.`produce():

FabPolygon.produce(self, geometry_context: FabGeometries.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Tuple[Any, ...]:

Produce the FreeCAD objects needed for FabPolygon.


## <a name="fabgeometries--fab-arc"></a>6 Class Fab_Arc:

An internal representation an arc geometry.
Attributes:
* *Apex* (Vector): The fillet apex point (i.e. corner.)
* *Radius* (float): The arc radius in millimeters.
* *Center* (Vector): The arc center point.
* *Start* (Vector): The Arc start point.
* *Middle* (Vector): The Arc midpoint.
* *Finish* (Vector): The Arc finish point.

* *ApexXY* (Vector): Apex projected onto the XY Plane.
* *CenterXY* (Vector): The Center projected onto the XY Plane.
* *StartXY* (Vector): The Start projected onto the XY Plane.
* *MiddleXY* (Vector): The Middle projected onto the XY Plane
* *FinishXY* (Vector): The Finish projected onto the XY Plane
Constructor:
* Fab_Arc(Apex, Radius, Center, Start, Middle, Finish)

### <a name="fabgeometries----produce"></a>6.1 `Fab_Arc.`produce():

Fab_Arc.produce(self, geometry_context: FabGeometries.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Any:

Return line segment after moving it into Geometry group.


## <a name="fabgeometries--fab-circle"></a>7 Class Fab_Circle:

An internal representation of a circle geometry.
Attributes:
* *Center (Vector): The circle center.
* *Diameter (float): The circle diameter in millimeters.
* *CenterXY* (Vector): Center projected onto XY plane.

### <a name="fabgeometries----produce"></a>7.1 `Fab_Circle.`produce():

Fab_Circle.produce(self, geometry_context: FabGeometries.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Any:

Return line segment after moving it into Geometry group.


## <a name="fabgeometries--fab-fillet"></a>8 Class Fab_Fillet:

An object that represents one fillet of a FabPolygon.
Attributes:
* *Plane* (FabPlane): The plane onto which the fillet is projected.
* *Apex* (Vector): The apex corner point for the fillet.
* *Radius* (float): The fillet radius in millimeters.
* *Before* (Fab_Fillet): The previous Fab_Fillet in the FabPolygon.
* *After* (Fab_Fillet): The next Fab_Fillet in the FabPolygon.
* *Arc* (Optional[Fab_Arc]): The fillet Arc if Radius is non-zero.
* *Line* (Optional[Fab_Line]): The line that connects to the previous Fab_Fillet
* *ApexXY* (Vector): The Apex projected onto the XY plane.

### <a name="fabgeometries----compute-arc"></a>8.1 `Fab_Fillet.`compute_arc():

Fab_Fillet.compute_arc(self, tracing: str = '') -> FabGeometries.Fab_Arc:

Return the arc associated with a Fab_Fillet with non-zero radius.

### <a name="fabgeometries----plane-2d-project"></a>8.2 `Fab_Fillet.`plane_2d_project():

Fab_Fillet.plane_2d_project(self, plane: FabGeometries.FabPlane) -> None:

Project the Apex onto a plane.
Arguments:
* *plane* (FabPlane): The plane to project the Fab_Fillet onto.

Modifies Fab_Fillet.

### <a name="fabgeometries----compute-fillet-area-perimeter"></a>8.3 `Fab_Fillet.`compute_fillet_area_perimeter():

Fab_Fillet.compute_fillet_area_perimeter(self, tracing: str = '') -> Tuple[float, float]:

Return the excluded fillet area and the perimeter for a Fab_Fillet.
To be more concise, the fillet_area is the area outside of the fillet arc, but inside
the straight lines "corner" of the fillet.

Returns:
* (float): The excluded area of a fillet (i.e. the area not under the arc segment.)
* (float): The length the of the arc segment.

### <a name="fabgeometries----get-geometries"></a>8.4 `Fab_Fillet.`get_geometries():

Fab_Fillet.get_geometries(self) -> Tuple[FabGeometries.Fab_Geometry, ...]:

NO DOC STRING!


## <a name="fabgeometries--fab-geometry"></a>9 Class Fab_Geometry:

An Internal base class for Fab_Arc, Fab_Circle, and Fab_Line.
Attributes:
* Plane* (FabPlane): The plane onto which the geo

### <a name="fabgeometries----produce"></a>9.1 `Fab_Geometry.`produce():

Fab_Geometry.produce(self, geometry_context: FabGeometries.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Any:

NO DOC STRING!

### <a name="fabgeometries----get-start"></a>9.2 `Fab_Geometry.`get_start():

Fab_Geometry.get_start(self) -> cadquery.occ_impl.geom.Vector:

Return start point of geometry.


## <a name="fabgeometries--fab-geometrycontext"></a>10 Class Fab_GeometryContext:

GeometryProduce: Context needed to produce FreeCAD geometry objects.
Attributes:
* *Plane* (FabPlane): Plane to use.
* *Query* (Fab_Query): The CadQuery Workplane wrapper to use.
* *_GeometryGroup*: (App.DocumentObjectGroup):
  The FreeCAD group to store FreeCAD Geometry objects into.
  This field needs to be set prior to use with set_geometry_group() method.

### <a name="fabgeometries----copy"></a>10.1 `Fab_GeometryContext.`copy():

Fab_GeometryContext.copy(self, tracing: str = '') -> 'Fab_GeometryContext':

Return a Fab_GeometryContext copy.

### <a name="fabgeometries----copy-with-plane-adjust"></a>10.2 `Fab_GeometryContext.`copy_with_plane_adjust():

Fab_GeometryContext.copy_with_plane_adjust(self, delta: float, tracing: str = '') -> 'Fab_GeometryContext':

Return a Fab_GeometryContext copy with the plane adjusted up/down.

### <a name="fabgeometries----set-geometry-group"></a>10.3 `Fab_GeometryContext.`set_geometry_group():

Fab_GeometryContext.set_geometry_group(self, geometry_group: Any) -> None:

Set the GeometryContext geometry group.


## <a name="fabgeometries--fab-geometryinfo"></a>11 Class Fab_GeometryInfo:

Information about a FabGeometry object.
Attributes:
* Geometry (FabGeometry): The FabGeometry object used.

Constructor:
* Fab_GeometryInfo(Geometry)

### <a name="fabgeometries----totuple"></a>11.1 `Fab_GeometryInfo.`toTuple():

Fab_GeometryInfo.toTuple(self) -> Tuple[float, float, float, float]:

Return the area, perimeter, internal/external radius for a FabGeometry.
Returns:
* (float): The area in square millimeters.
* (float): The perimeter in millimeters.
* (float):
  The minimum internal radius in millimeters or -1.0 if there are now internal corners.
* (float): The minimum external radius in millimeters.


## <a name="fabgeometries--fab-line"></a>12 Class Fab_Line:

An internal representation of a line segment geometry.
Attributes:
* *Plane* (FabPlane): The plane to project the line onto.
* *Start* (Vector): The line segment start point.
* *Finish* (Vector): The line segment finish point.
* *StartXY* (Vector): Start projected onto XY plane.
* *FinishXY* (Vector): Finish projected onto XY plane.

Constructor:
* Fab_Line(Start, Finish)

### <a name="fabgeometries----get-start"></a>12.1 `Fab_Line.`get_start():

Fab_Line.get_start(self) -> cadquery.occ_impl.geom.Vector:

Return the start point of the Fab_Line.

### <a name="fabgeometries----produce"></a>12.2 `Fab_Line.`produce():

Fab_Line.produce(self, geometry_context: FabGeometries.Fab_GeometryContext, prefix: str, index: int, tracing: str = '') -> Any:

Return line segment after moving it into Geometry group.


## <a name="fabgeometries--fab-query"></a>13 Class Fab_Query:

A CadQuery Workplane wrapper.
This class creates CadQuery Workplane provides a consistent head of the Workplane chain..
CadQuery Operations are added as needed.

Attributes:
* *Plane* (FabPlane): The plane to use for CadQuery initialization.
* *WorkPlane: (cadquery.Workplane): The resulting CadQuery Workplane object.

### <a name="fabgeometries----circle"></a>13.1 `Fab_Query.`circle():

Fab_Query.circle(self, center: cadquery.occ_impl.geom.Vector, radius: float, for_construction=False, tracing: str = '') -> None:

Draw a circle to a point.

### <a name="fabgeometries----close"></a>13.2 `Fab_Query.`close():

Fab_Query.close(self, tracing: str = '') -> None:

Close a sequence of arcs and lines.

### <a name="fabgeometries----copy-workplane"></a>13.3 `Fab_Query.`copy_workplane():

Fab_Query.copy_workplane(self, plane: FabGeometries.FabPlane, tracing: str = '') -> None:

Create a new CadQuery workplane and push it onto the stack.

### <a name="fabgeometries----extrude"></a>13.4 `Fab_Query.`extrude():

Fab_Query.extrude(self, depth: float, tracing: str = '') -> None:

Extrude current 2D object to a known depth.

### <a name="fabgeometries----hole"></a>13.5 `Fab_Query.`hole():

Fab_Query.hole(self, diameter: float, depth: float, tracing: str = '') -> None:

Drill a hole.

### <a name="fabgeometries----line-to"></a>13.6 `Fab_Query.`line_to():

Fab_Query.line_to(self, end: cadquery.occ_impl.geom.Vector, for_construction=False, tracing: str = '') -> None:

Draw a line to a point.

### <a name="fabgeometries----move-to"></a>13.7 `Fab_Query.`move_to():

Fab_Query.move_to(self, point: cadquery.occ_impl.geom.Vector, tracing: str = '') -> None:

Draw a line to a point.

### <a name="fabgeometries----show"></a>13.8 `Fab_Query.`show():

Fab_Query.show(self, label: str, tracing: str = '') -> None:

Print a detailed dump of a Fab_Query.

### <a name="fabgeometries----subtract"></a>13.9 `Fab_Query.`subtract():

Fab_Query.subtract(self, remove_solid: 'Fab_Query', tracing: str = '') -> None:

Subtract one solid form a Fab_Query.

### <a name="fabgeometries----three-point-arc"></a>13.10 `Fab_Query.`three_point_arc():

Fab_Query.three_point_arc(self, middle: cadquery.occ_impl.geom.Vector, end: cadquery.occ_impl.geom.Vector, for_construction: bool = False, tracing: str = '') -> None:

Draw a three point arc.



