# Solid: Solid: A module for constructing 3D solids.
This module defines the following user facing classes:
* FabSolid: A 3D solid part that corresponds to a STEP file.
* FabMount: A CNC-like work plane on which other operations are performed.

There are internal classes that represent operations such as extrude, pocket, drill, etc.
This internal classes are managed by FabMount methods.

## Table of Contents (alphabetical order):

* 1 Class: [FabMount](#solid--fabmount):
  * 1.1 [get_hash()](#solid----get-hash): Return a has the current contents of a FabMount.
  * 1.2 [record_operation()](#solid----record-operation): Record an operation to a FabMount.
  * 1.3 [set_geometry_group()](#solid----set-geometry-group): Set the FabMount GeometryGroup need for the FabGeometryContex.
  * 1.4 [post_produce1()](#solid----post-produce1): Perform FabMount phase 1 post procduction.
  * 1.5 [to_json()](#solid----to-json): Return FabMount JSON structure.
  * 1.6 [extrude()](#solid----extrude): Perform a extrude operation.
  * 1.7 [pocket()](#solid----pocket): Perform a pocket operation.
  * 1.8 [drill_joins()](#solid----drill-joins): Drill some FabJoin's into a FabMount.
* 2 Class: [FabSolid](#solid--fabsolid):
  * 2.1 [to_json()](#solid----to-json): Return FabProject JSON structure.
  * 2.2 [set_body()](#solid----set-body): Set the BodyBase of a FabSolid.
  * 2.3 [is_solid()](#solid----is-solid):  Return True if FabNode is a FabAssembly.
  * 2.4 [pre_produce()](#solid----pre-produce): Perform FabSolid pre production.
  * 2.5 [get_hash()](#solid----get-hash): Return FabSolid hash.
  * 2.6 [mount()](#solid----mount): Return a new FabMount.
  * 2.7 [drill_joins()](#solid----drill-joins): Apply drill FabJoin holes for a FabSolid.
  * 2.8 [post_produce1()](#solid----post-produce1): Perform FabSolid Phase1 post production.
* 3 Class: [FabStock](#solid--fabstock):
  * 3.1 [enclose()](#solid----enclose): Wrap some stock material around a FabBox.

## <a name="solid--fabmount"></a>1 Class FabMount:

An operations plane that can be oriented for subsequent machine operations.
This class basically corresponds to a FreeCad Datum Plane.  It is basically the surface
to which the 2D FabGeometry's are mapped onto prior to performing each operation.

Attributes:
* *Name*: (str): The name of the FabPlane.
* *Solid*: (FabSolid): The FabSolid to work on.
* *Contact* (Vector): A point on the mount plane.
* *Normal* (Vector): A normal to the mount plane
* *Orient* (Vector):
  A vector that is projected onto the mount plane to specify orientation
  when mounted for CNC operations.
* *Depth* (float): The maximum depth limit for all operations.
* *WorkPlane* (FabQuery): The CadQuery workplane wrapper class object.

### <a name="solid----get-hash"></a>1.1 `FabMount.`get_hash():

FabMount.get_hash(self) -> Tuple[Any, ...]:

Return a has the current contents of a FabMount.

### <a name="solid----record-operation"></a>1.2 `FabMount.`record_operation():

FabMount.record_operation(self, operation: Solid._Operation) -> None:

Record an operation to a FabMount.

### <a name="solid----set-geometry-group"></a>1.3 `FabMount.`set_geometry_group():

FabMount.set_geometry_group(self, geometry_group: Any) -> None:

Set the FabMount GeometryGroup need for the FabGeometryContex.

### <a name="solid----post-produce1"></a>1.4 `FabMount.`post_produce1():

FabMount.post_produce1(self, produce_state: Node.Fab_ProduceState, tracing: str = '') -> None:

Perform FabMount phase 1 post procduction.

### <a name="solid----to-json"></a>1.5 `FabMount.`to_json():

FabMount.to_json(self) -> Dict[str, Any]:

Return FabMount JSON structure.

### <a name="solid----extrude"></a>1.6 `FabMount.`extrude():

FabMount.extrude(self, name: str, shapes: Union[Geometry.FabGeometry, Tuple[Geometry.FabGeometry, ...]], depth: float, contour: bool = True, tracing: str = '') -> None:

Perform a extrude operation.

### <a name="solid----pocket"></a>1.7 `FabMount.`pocket():

FabMount.pocket(self, name: str, shapes: Union[Geometry.FabGeometry, Tuple[Geometry.FabGeometry, ...]], depth: float, tracing: str = '') -> None:

Perform a pocket operation.

### <a name="solid----drill-joins"></a>1.8 `FabMount.`drill_joins():

FabMount.drill_joins(self, joins_name: str, joins: Union[FabJoiner.FabJoin, Sequence[FabJoiner.FabJoin]], tracing: str = '') -> None:

Drill some FabJoin's into a FabMount.


## <a name="solid--fabsolid"></a>2 Class FabSolid:

Fab: Represents a single 3D solid that is represented as a STEP file.
Inherited Attributes:
* *Name* (str): The model name.
* *Parent* (FabNode): The Parent FabNode.

Attributes:
* *Material* (str): The material to use.
* *Color* (str): The color to use.

### <a name="solid----to-json"></a>2.1 `FabSolid.`to_json():

FabSolid.to_json(self) -> Dict[str, Any]:

Return FabProject JSON structure.

### <a name="solid----set-body"></a>2.2 `FabSolid.`set_body():

FabSolid.set_body(self, body: Any) -> None:

Set the BodyBase of a FabSolid.

### <a name="solid----is-solid"></a>2.3 `FabSolid.`is_solid():

FabSolid.is_solid(self) -> bool:

 Return True if FabNode is a FabAssembly.

### <a name="solid----pre-produce"></a>2.4 `FabSolid.`pre_produce():

FabSolid.pre_produce(self, produce_state: Node.Fab_ProduceState) -> None:

Perform FabSolid pre production.

### <a name="solid----get-hash"></a>2.5 `FabSolid.`get_hash():

FabSolid.get_hash(self) -> Tuple[Any, ...]:

Return FabSolid hash.

### <a name="solid----mount"></a>2.6 `FabSolid.`mount():

FabSolid.mount(self, name: str, contact: cadquery.occ_impl.geom.Vector, normal: cadquery.occ_impl.geom.Vector, orient: cadquery.occ_impl.geom.Vector, depth: float, tracing: str = '') -> Solid.FabMount:

Return a new FabMount.

### <a name="solid----drill-joins"></a>2.7 `FabSolid.`drill_joins():

FabSolid.drill_joins(self, name: str, joins: Sequence[FabJoiner.FabJoin], mounts: Union[Sequence[Solid.FabMount], NoneType] = None) -> None:

Apply drill FabJoin holes for a FabSolid.
Iterate pairwise through a sequence of FabJoin's and FabMount's and for each pair
attempt to drill a bunch the FabJoin holes for the associated FabSolid.  The drill
operation only occurs if the FabJoin is in alignment with the FabMount normal (in
either direction) *and* if the FabJoin intersects with the underlying FabSolid;
otherwise nothing is for that particular FabMount and FabJoin pair.

Arguments:
* *name* (str): The collective name for all of the drills.
* *joins* (Optional[Sequence[FabJoin]]):
  The tuple/list of FabJoin's to apply.
* *mounts* (Optional[Sequence[FabMount]]):
  The mounts to to apply the *joins* to.  If *mounts* is *None*, all of the
  mounts for the current FabSolid are used.  (Default: None)

For now, please call this method after all FabMount's are created.

### <a name="solid----post-produce1"></a>2.8 `FabSolid.`post_produce1():

FabSolid.post_produce1(self, produce_state: Node.Fab_ProduceState, tracing: str = '') -> None:

Perform FabSolid Phase1 post production.


## <a name="solid--fabstock"></a>3 Class FabStock:

Represents the stock matereial for machine a part from.
Attributes:
* *Name* (str): The FabStock Name.
* *StockIncrements* (Vector):
  The increments that the stock cuboid comes in  X, Y, and Z.
  The StockThicknesses attribute will override Z if possible.
* *StockThicknesses* (Tuple[float ...]):
  The standard increments of stock thickness to use.
* *StockMinimumCut* (float):
  The minimum amount that contour operation must remove in X and Y.

### <a name="solid----enclose"></a>3.1 `FabStock.`enclose():

FabStock.enclose(self, box: Node.FabBox) -> Tuple[cadquery.occ_impl.geom.Vector, cadquery.occ_impl.geom.Vector]:

Wrap some stock material around a FabBox.



