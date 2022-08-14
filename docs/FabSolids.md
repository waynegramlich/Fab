# FabSolids: Solid: A module for constructing 3D solids.
This module defines the following user facing classes:
* FabSolid: A 3D solid part that corresponds to a STEP file.
* FabMount: A CNC-like work plane on which other operations are performed.

There are internal classes that represent operations such as extrude, pocket, drill, etc.
This internal classes are managed by FabMount methods.

## Table of Contents (alphabetical order):

* 1 Class: [FabMount](#fabsolids--fabmount):
  * 1.1 [lookup_prefix()](#fabsolids----lookup-prefix): Return the Fab_Prefix for an operation.
  * 1.2 [fence()](#fabsolids----fence): Put a fence between operations to keep sub-groups together.
  * 1.3 [getHash()](#fabsolids----gethash): Return a has the current contents of a FabMount.
  * 1.4 [record_operation()](#fabsolids----record-operation): Record an operation to a FabMount.
  * 1.5 [setGeometryGroup()](#fabsolids----setgeometrygroup): Set the FabMount GeometryGroup need for the FabGeometryContex.
  * 1.6 [post_produce1()](#fabsolids----post-produce1): Expand both Mounts and Operations within each Mount.
  * 1.7 [post_produce2()](#fabsolids----post-produce2): Perform FabMount phase 1 post production.
  * 1.8 [to_json()](#fabsolids----to-json): Return FabMount JSON structure.
  * 1.9 [extrude()](#fabsolids----extrude): Perform a extrude operation.
  * 1.10 [pocket()](#fabsolids----pocket): Perform a pocket operation.
  * 1.11 [drill_joins()](#fabsolids----drill-joins): Drill some FabJoin's into a FabMount.
* 2 Class: [FabSolid](#fabsolids--fabsolid):
  * 2.1 [lookup_prefix()](#fabsolids----lookup-prefix): Return the Fab_Prefix for a mount/operation name pair.
  * 2.2 [to_json()](#fabsolids----to-json): Return FabProject JSON structure.
  * 2.3 [set_body()](#fabsolids----set-body): Set the BodyBase of a FabSolid.
  * 2.4 [is_solid()](#fabsolids----is-solid):  Return True if FabNode is a FabAssembly.
  * 2.5 [pre_produce()](#fabsolids----pre-produce): Perform FabSolid pre production.
  * 2.6 [post_produce1()](#fabsolids----post-produce1): Perform FabSolid pre production.
  * 2.7 [getHash()](#fabsolids----gethash): Return FabSolid hash.
  * 2.8 [mount()](#fabsolids----mount): Add a new FabMount to a FabSolid.
  * 2.9 [drill_joins()](#fabsolids----drill-joins): Apply drill FabJoin holes for a FabSolid.
  * 2.10 [post_produce2()](#fabsolids----post-produce2): Perform FabSolid Phase2 post production.
* 3 Class: [FabStock](#fabsolids--fabstock):
  * 3.1 [enclose()](#fabsolids----enclose): Wrap some stock material around a FabBox.
* 4 Class: [Fab_Extrude](#fabsolids--fab-extrude):
  * 4.1 [get_kind()](#fabsolids----get-kind): Return Fab_Extrude kind.
  * 4.2 [getOperationOrder()](#fabsolids----getoperationorder): Return the Fab_OperationOrder for a Fab_Operation.
  * 4.3 [getHash()](#fabsolids----gethash): Return hash for Fab_Extrude operation.
  * 4.4 [post_produce1()](#fabsolids----post-produce1): Expand simple operations as approprated.
  * 4.5 [post_produce2()](#fabsolids----post-produce2): Produce the Extrude.
  * 4.6 [to_json()](#fabsolids----to-json): Return JSON dictionary for Fab_Extrude.
* 5 Class: [Fab_Hole](#fabsolids--fab-hole):
  * 5.1 [get_kind()](#fabsolids----get-kind): Return Fab_Hole kind.
  * 5.2 [getHash()](#fabsolids----gethash): Return Fab_Hole hash.
  * 5.3 [getOperationOrder()](#fabsolids----getoperationorder): Return the Fab_OperationOrder for a Fab_Operation.
  * 5.4 [post_produce1()](#fabsolids----post-produce1): Expand simple operations as approprated.
  * 5.5 [post_produce2()](#fabsolids----post-produce2): Perform Fab_Hole phase 1 post production.
  * 5.6 [to_json()](#fabsolids----to-json): Return the FabHole JSON.
* 6 Class: [Fab_HoleKey](#fabsolids--fab-holekey):
  * 6.1 [getHash()](#fabsolids----gethash): Return a hash tuple for a Fab_HoleKey.
* 7 Class: [Fab_Operation](#fabsolids--fab-operation):
  * 7.1 [setBit()](#fabsolids----setbit): Set the Fab_Operation bit and associated index.
  * 7.2 [set_tool_controller()](#fabsolids----set-tool-controller): Set the Fab_Operation tool controller and associated index.
  * 7.3 [get_kind()](#fabsolids----get-kind): Return Fab_Operation kind.
  * 7.4 [get_name()](#fabsolids----get-name): Return Fab_Operation name.
  * 7.5 [selectShopBit()](#fabsolids----selectshopbit): Select a Fab_Shop bit for a Fab_Operation.
  * 7.6 [getOperationOrder()](#fabsolids----getoperationorder): Return the Fab_OperationOrder for a Fab_Operation.
  * 7.7 [getInitialOperationKey()](#fabsolids----getinitialoperationkey): Return initial Fab_OperationKey for a Fab_Operation.
  * 7.8 [getInitialOperationKeyTrampoline()](#fabsolids----getinitialoperationkeytrampoline): Get the initial operation key for a Fab_Operation.
  * 7.9 [getHash()](#fabsolids----gethash): Return Fab_Operation hash.
  * 7.10 [get_geometries_hash()](#fabsolids----get-geometries-hash): Return hash of FabGeometry's.
  * 7.11 [setShopBits()](#fabsolids----setshopbits): Set the Fab_Operation ShopBits attribute.
  * 7.12 [produce()](#fabsolids----produce): Return the operation sort key.
  * 7.13 [post_produce1()](#fabsolids----post-produce1): Expand simple operations as approprate.
  * 7.14 [post_produce2()](#fabsolids----post-produce2): NO DOC STRING!
  * 7.15 [to_json()](#fabsolids----to-json): Return a base JSON dictionary for an Fab_Operation.
* 8 Class: [Fab_OperationKey](#fabsolids--fab-operationkey):
* 9 Class: [Fab_OperationKind](#fabsolids--fab-operationkind):
* 10 Class: [Fab_OperationOrder](#fabsolids--fab-operationorder):
* 11 Class: [Fab_Pocket](#fabsolids--fab-pocket):
  * 11.1 [post_produce1()](#fabsolids----post-produce1): Expand simple operations as approprated.
  * 11.2 [getOperationOrder()](#fabsolids----getoperationorder): Return the Fab_OperationOrder for a Fab_Operation.
  * 11.3 [getHash()](#fabsolids----gethash): Return Fab_Pocket hash.
  * 11.4 [get_kind()](#fabsolids----get-kind): Return Fab_Pocket kind.
  * 11.5 [post_produce2()](#fabsolids----post-produce2): Produce the Pocket.
  * 11.6 [to_json()](#fabsolids----to-json): Return JSON dictionary for Fab_Extrude.

## <a name="fabsolids--fabmount"></a>1 Class FabMount:

An operations plane that can be oriented for subsequent machine operations.
This class basically corresponds to a FreeCad Datum Plane.  It is basically the surface
to which the 2D FabGeometry's are mapped onto prior to performing each operation.
While this is a public class, it is expected that people will use the FabSolid.mount()
to actually create a FabMount.

Constructor Attributes:
* *Name*: (str): The name of the FabPlane.
* *Solid*: (FabSolid): The FabSolid to work on.
* *Contact* (Vector): A point on the mount plane.
* *Normal* (Vector): A normal to the mount plane
* *Depth* (float): The maximum depth limit for all operations.
* *OrientStart* (Vector): The starting point of the orientation vector used for CNC operations.
* *OrientEnd* (Vector): The ending point of the orientation vector used for CNC operations.
* *WorkPlane* (Fab_Query): The CadQuery workplane wrapper class object.

Constructor:
* FabMount("Name", Solid, Contact, Normal, Depth, OrientStart, OrientEnd, WorkPlane)

Additional Property Attributes:
* OrientAngle (float):
  The amount the part is rotated to align the orient vector with the CNC +X axis.
  This angle is applied after the mount plane has been rotated to be parallel with CNC XY plane.
* OrientTranslate (float):
  The amount the part is translated to get the origin to match CNC origin.
  This translation is applied after the mount plane has been rotated to be parallel with
  CNC XY plane.

The orient vector is used to ensure that a part is properly oriented on a CNC machine
prior to machining.  Is specifies two points called *OrientStart* and *OrientEnd*.
These two points are first projected onto the mount plane and then the mount plane is
rotated to align with the CNC XY plane.  The part is rotated on the CNC machine until
the projected orientation vector points in same the CNC machine +X axis.

### <a name="fabsolids----lookup-prefix"></a>1.1 `FabMount.`lookup_prefix():

FabMount.lookup_prefix(self, operation_name: str) -> FabNodes.Fab_Prefix:

Return the Fab_Prefix for an operation.

### <a name="fabsolids----fence"></a>1.2 `FabMount.`fence():

FabMount.fence(self) -> None:

Put a fence between operations to keep sub-groups together.

### <a name="fabsolids----gethash"></a>1.3 `FabMount.`getHash():

FabMount.getHash(self) -> Tuple[Any, ...]:

Return a has the current contents of a FabMount.

### <a name="fabsolids----record-operation"></a>1.4 `FabMount.`record_operation():

FabMount.record_operation(self, operation: FabSolids.Fab_Operation) -> None:

Record an operation to a FabMount.

### <a name="fabsolids----setgeometrygroup"></a>1.5 `FabMount.`setGeometryGroup():

FabMount.setGeometryGroup(self, geometry_group: Any) -> None:

Set the FabMount GeometryGroup need for the FabGeometryContex.

### <a name="fabsolids----post-produce1"></a>1.6 `FabMount.`post_produce1():

FabMount.post_produce1(self, produce_state: FabNodes.Fab_ProduceState, expanded_mounts: List[ForwardRef('FabMount')], tracing: str = '') -> None:

Expand both Mounts and Operations within each Mount.

### <a name="fabsolids----post-produce2"></a>1.7 `FabMount.`post_produce2():

FabMount.post_produce2(self, produce_state: FabNodes.Fab_ProduceState, tracing: str = '') -> None:

Perform FabMount phase 1 post production.

### <a name="fabsolids----to-json"></a>1.8 `FabMount.`to_json():

FabMount.to_json(self) -> Dict[str, Any]:

Return FabMount JSON structure.

### <a name="fabsolids----extrude"></a>1.9 `FabMount.`extrude():

FabMount.extrude(self, name: str, shapes: Union[FabGeometries.FabGeometry, Tuple[FabGeometries.FabGeometry, ...]], depth: float, contour: bool = True, debug: bool = False, tracing: str = '') -> None:

Perform a extrude operation.
Arguments:
* *name* (str): The user name of the operation that shows up various generated files.
* *shapes* (Union[FabGeometry, Tuple[FabGeometry]]):
  Either FabGeometry the specifies the exterior, or multiple FabGeometry's where
  the first specifies the exterior and the are interior "holes".
* *depth* (float): The depth (i.e. length) of the extrusion.  (Default: True)
* *contour* (bool):
  If True, an exterior contour operation is scheduled; otherwise, no contour operation
  occurs. (Default: True)
* *debug* (bool): If True, the extrude solid is made visible; otherwise it is not shown.

### <a name="fabsolids----pocket"></a>1.10 `FabMount.`pocket():

FabMount.pocket(self, name: str, shapes: Union[FabGeometries.FabGeometry, Tuple[FabGeometries.FabGeometry, ...]], depth: float, debug: bool = False, tracing: str = '') -> None:

Perform a pocket operation.
Arguments:
* *name* (str): The name of the pocket.
* *shapes* (Union[FabGeometry, Tuple[FabGeometry, ...]]):
  Either a single FabGeometry or a tuple of FabGeometry's.  The first FabGeometry specifies
  the pocket boundary.
* *depth* (float): The pocket depth in millimeters from the mount plane.
* *debug* (bool): If True, the pocket solid is made visible; otherwise it is not shown.

### <a name="fabsolids----drill-joins"></a>1.11 `FabMount.`drill_joins():

FabMount.drill_joins(self, joins_name: str, joins: Union[FabJoins.FabJoin, Sequence[FabJoins.FabJoin]], debug: bool = False, tracing: str = '') -> None:

Drill some FabJoin's into a FabMount.
Arguments:
* *joins_name* (str):
  A user name for the all of the joins.  This name is used in file names, labels, etc..
* *joins* (Union[FabJoin, Sequence[FabJoin]]):
* *debug* (bool):  If True, the joins solid is made visible; otherwise it is not.


## <a name="fabsolids--fabsolid"></a>2 Class FabSolid:

Fab: Represents a single 3D solid that is represented as a STEP file.
Inherited Attributes:
* *Name* (str): The model name.
* *Parent* (FabNode): The Parent FabNode.

Attributes:
* *Material* (str): The material to use.
* *Color* (str): The color to use.

Constructor:
* FabSolid("Name", Parent, Material, Color)

### <a name="fabsolids----lookup-prefix"></a>2.1 `FabSolid.`lookup_prefix():

FabSolid.lookup_prefix(self, mount_name: str, operation_name: str) -> FabNodes.Fab_Prefix:

Return the Fab_Prefix for a mount/operation name pair.

### <a name="fabsolids----to-json"></a>2.2 `FabSolid.`to_json():

FabSolid.to_json(self) -> Dict[str, Any]:

Return FabProject JSON structure.

### <a name="fabsolids----set-body"></a>2.3 `FabSolid.`set_body():

FabSolid.set_body(self, body: Any) -> None:

Set the BodyBase of a FabSolid.

### <a name="fabsolids----is-solid"></a>2.4 `FabSolid.`is_solid():

FabSolid.is_solid(self) -> bool:

 Return True if FabNode is a FabAssembly.

### <a name="fabsolids----pre-produce"></a>2.5 `FabSolid.`pre_produce():

FabSolid.pre_produce(self, produce_state: FabNodes.Fab_ProduceState) -> None:

Perform FabSolid pre production.

### <a name="fabsolids----post-produce1"></a>2.6 `FabSolid.`post_produce1():

FabSolid.post_produce1(self, produce_state: FabNodes.Fab_ProduceState, tracing: str = '') -> None:

Perform FabSolid pre production.

### <a name="fabsolids----gethash"></a>2.7 `FabSolid.`getHash():

FabSolid.getHash(self) -> Tuple[Any, ...]:

Return FabSolid hash.

### <a name="fabsolids----mount"></a>2.8 `FabSolid.`mount():

FabSolid.mount(self, name: str, plane: FabGeometries.FabPlane, depth: float, orient_start: cadquery.occ_impl.geom.Vector, orient_end: cadquery.occ_impl.geom.Vector, tracing: str = '') -> FabSolids.FabMount:

Add a new FabMount to a FabSolid.
Arguments:
* *name* (str): The name of the mount.
* *plane* (FabPlane): The FabMount plane.
* *depth* (float): The amount of space needed under the mount to perform CNC operations.
* *orient_start* (Vector):
  The starting point of the CNC orientation vector.  (See discuss CNC orient vector below.)
* *orient_end* (Vector):
  The ending point of the CNC orientation vector.  (See discuss CNC orient vector below.)

Returns:
* (FabMount): The Resulting FabMount object.

The following steps are performed using *orient_start* and *orient_end*:
1. A CNC orient vector is computed as *orient_end* - *orient_start*.
2. The CNC orient vector is projected onto the mount plane.
3. The mount plane is rotated about the origin to be parallel to the XY plane.
4. The solid is rotated so that the orient vector points in the same direction as the
   CNC +X axis.
Thus, the CNC orientation specifies the solid orientation when it is mounted to the CNC
table prior to machining.

### <a name="fabsolids----drill-joins"></a>2.9 `FabSolid.`drill_joins():

FabSolid.drill_joins(self, name: str, joins: Sequence[FabJoins.FabJoin], mounts: Union[Sequence[FabSolids.FabMount], NoneType] = None) -> None:

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

### <a name="fabsolids----post-produce2"></a>2.10 `FabSolid.`post_produce2():

FabSolid.post_produce2(self, produce_state: FabNodes.Fab_ProduceState, tracing: str = '') -> None:

Perform FabSolid Phase2 post production.


## <a name="fabsolids--fabstock"></a>3 Class FabStock:

Represents the stock material to machine a part from.
Attributes:
* *Name* (str): The FabStock Name.
* *StockIncrements* (Vector):
  The increments that the stock cuboid comes in  X, Y, and Z.
  The StockThicknesses attribute will override Z if possible.
* *StockThicknesses* (Tuple[float ...]):
  The standard increments of stock thickness to use.
* *StockMinimumCut* (float):
  The minimum amount that contour operation must remove in X and Y.

### <a name="fabsolids----enclose"></a>3.1 `FabStock.`enclose():

FabStock.enclose(self, box: FabNodes.FabBox) -> Tuple[cadquery.occ_impl.geom.Vector, cadquery.occ_impl.geom.Vector]:

Wrap some stock material around a FabBox.


## <a name="fabsolids--fab-extrude"></a>4 Class Fab_Extrude:

Represents and extrude operation.
Attributes:
* *Mount* (FabMount): The FabMount to use for performing operations.
* *Name* (str): The FabExtrude operation name.
* *Geometry* (Union[FabGeometry, Tuple[FabGeometry, ...]):
  The FabGeometry (i.e. FabPolygon or FabCircle) or a tuple of FabGeometry's to extrude with.
  When the tuple is used, the largest FabGeometry (which is traditionally the first one)
  is the outside of the extrusion, and the rest are "pockets".  This is useful for tubes.
* *Depth* (float): The depth to extrude to in millimeters.
* *Contour* (bool):
  If True and profile CNC contour path is performed; otherwise, no profile is performed.
See Fab_Operation for extra computed Attributes.

Constructor:
* Fab_Extrude("Name", Mount, Geometry, Depth, Contour)

### <a name="fabsolids----get-kind"></a>4.1 `Fab_Extrude.`get_kind():

Fab_Extrude.get_kind(self) -> str:

Return Fab_Extrude kind.

### <a name="fabsolids----getoperationorder"></a>4.2 `Fab_Extrude.`getOperationOrder():

Fab_Extrude.getOperationOrder(self, bit: FabToolTemplates.FabBit) -> FabSolids.Fab_OperationOrder:

Return the Fab_OperationOrder for a Fab_Operation.

### <a name="fabsolids----gethash"></a>4.3 `Fab_Extrude.`getHash():

Fab_Extrude.getHash(self) -> Tuple[Any, ...]:

Return hash for Fab_Extrude operation.

### <a name="fabsolids----post-produce1"></a>4.4 `Fab_Extrude.`post_produce1():

Fab_Extrude.post_produce1(self, produce_state: FabNodes.Fab_ProduceState, expanded_operations: 'List[Fab_Operation]', tracing: str = '') -> None:

Expand simple operations as approprated.

### <a name="fabsolids----post-produce2"></a>4.5 `Fab_Extrude.`post_produce2():

Fab_Extrude.post_produce2(self, produce_state: FabNodes.Fab_ProduceState, tracing: str = '') -> None:

Produce the Extrude.

### <a name="fabsolids----to-json"></a>4.6 `Fab_Extrude.`to_json():

Fab_Extrude.to_json(self) -> Dict[str, Any]:

Return JSON dictionary for Fab_Extrude.


## <a name="fabsolids--fab-hole"></a>5 Class Fab_Hole:

FabDrill helper class that represents one or more holes related holes.
Attributes:
* *Name* (str): The name of the Fab_Hole.
* *Mount* (FabMount): The FabMount to use for performing operations.
* Key (FabHoleKey): The hole key used for grouping holes.
* Join (FabJoin): The associated FabJoin the produced the hole.
* Centers (Tuple[Vector, ...]): The associated start centers.
* Name (str): The hole name.
* Depth (str): The hole depth.

Computed Attributes:
* HolesCount (int): The number of complatible holes.
* StartDepth (float): The starting depth in millimeters from the mount plane.

Constructor:
* Fab_Hole("Name", Mount, Key, Centers, Join, Depth)

### <a name="fabsolids----get-kind"></a>5.1 `Fab_Hole.`get_kind():

Fab_Hole.get_kind(self) -> str:

Return Fab_Hole kind.

### <a name="fabsolids----gethash"></a>5.2 `Fab_Hole.`getHash():

Fab_Hole.getHash(self) -> Tuple[Any, ...]:

Return Fab_Hole hash.

### <a name="fabsolids----getoperationorder"></a>5.3 `Fab_Hole.`getOperationOrder():

Fab_Hole.getOperationOrder(self, bit: FabToolTemplates.FabBit) -> FabSolids.Fab_OperationOrder:

Return the Fab_OperationOrder for a Fab_Operation.

### <a name="fabsolids----post-produce1"></a>5.4 `Fab_Hole.`post_produce1():

Fab_Hole.post_produce1(self, produce_state: FabNodes.Fab_ProduceState, expanded_operations: 'List[Fab_Operation]', tracing: str = '') -> None:

Expand simple operations as approprated.

### <a name="fabsolids----post-produce2"></a>5.5 `Fab_Hole.`post_produce2():

Fab_Hole.post_produce2(self, produce_state: FabNodes.Fab_ProduceState, tracing: str = '') -> None:

Perform Fab_Hole phase 1 post production.

### <a name="fabsolids----to-json"></a>5.6 `Fab_Hole.`to_json():

Fab_Hole.to_json(self) -> Dict[str, Any]:

Return the FabHole JSON.


## <a name="fabsolids--fab-holekey"></a>6 Class Fab_HoleKey:

Represents a group of holes that can be grouped together.
Attributes:
* *ThreadName* (str): The name of the thread class for the hole.
* *Kind* (str): The kind of thread hole (one of "thread", "close", or "standard".)
* *Depth* (float): The hole depth.
* *IsTop* (bool): True when hole is the top of the fastener for countersink and counterboring.
See Fab_Operation for even more extra computed Attributes.

Constructor:
* Fab_HoleKey("Name", Mount, "ThreadName", "Kind", Depth, IsTop)

### <a name="fabsolids----gethash"></a>6.1 `Fab_HoleKey.`getHash():

Fab_HoleKey.getHash(self) -> Tuple[Any, ...]:

Return a hash tuple for a Fab_HoleKey.


## <a name="fabsolids--fab-operation"></a>7 Class Fab_Operation:

An base class for FabMount operations.
Attributes:
* *Name* (str): The name of the Fab_Operation.
* *Mount* (FabMount): The FabMount to use for performing operations.
* *Fence* (int): Used to order sub groups of operations.
* *Bit* (Optional[FabBit):
  The bit to use for this CNC operation.  (default: None)
* *BitIndex* (int):
  The bit index associated with the bit.  (Default: -1)
* *ToolController* (Optional[FabToolController]):
  The tool controller (i.e. speeds, feeds, etc.) to use. (Default: None)
* *ToolControllerIndex* (int):
  The tool controller index associated with the tool controller.  (Default: -1)
* *JsonEnabled* (bool):
  Enables the generation of JSON if True, otherwise suppresses it.  (Default: True)
* *Active* (bool):
  If True, the resulting operation is performed.  About the only time this is set to False
  is for an extrude of stock material like a C channel, I beam, etc.  (Default: True)
* *Prefix* (Fab_Prefix):
  The prefix information to use for file name generation.
* *ShopBits*: Tuple[Fab_ShopBit, ...]:
  The available Fab_ShopBit's to select from for CNC operations.
* *InitialOperationKey* (Optional[Fab_OperationKey]):
  The initial Fab_OperationKey used to do the initially sort the operations.
* *SelectedShopBit* (Optional[Fab_ShopBit]):
  The final selected Fab_ShopBit for the operation.
* *Debug* (bool):
  If True, the resulting operation is made visible; otherwise, it is left not made visible.

Constructor:
* Fab_Operation("Name", Mount)

### <a name="fabsolids----setbit"></a>7.1 `Fab_Operation.`setBit():

Fab_Operation.setBit(self, bit: FabToolTemplates.FabBit, bits_table: Dict[FabToolTemplates.FabBit, int]) -> None:

Set the Fab_Operation bit and associated index.

### <a name="fabsolids----set-tool-controller"></a>7.2 `Fab_Operation.`set_tool_controller():

Fab_Operation.set_tool_controller(self, tool_controller: FabUtilities.FabToolController, tool_controllers_table: Dict[FabUtilities.FabToolController, int]) -> None:

Set the Fab_Operation tool controller and associated index.

### <a name="fabsolids----get-kind"></a>7.3 `Fab_Operation.`get_kind():

Fab_Operation.get_kind(self) -> str:

Return Fab_Operation kind.

### <a name="fabsolids----get-name"></a>7.4 `Fab_Operation.`get_name():

Fab_Operation.get_name(self) -> str:

Return Fab_Operation name.

### <a name="fabsolids----selectshopbit"></a>7.5 `Fab_Operation.`selectShopBit():

Fab_Operation.selectShopBit(self, shop_bit: FabShops.Fab_ShopBit) -> None:

Select a Fab_Shop bit for a Fab_Operation.

### <a name="fabsolids----getoperationorder"></a>7.6 `Fab_Operation.`getOperationOrder():

Fab_Operation.getOperationOrder(self, bit: FabToolTemplates.FabBit) -> FabSolids.Fab_OperationOrder:

Return the Fab_OperationOrder for a Fab_Operation.

### <a name="fabsolids----getinitialoperationkey"></a>7.7 `Fab_Operation.`getInitialOperationKey():

Fab_Operation.getInitialOperationKey(self) -> FabSolids.Fab_OperationKey:

Return initial Fab_OperationKey for a Fab_Operation.

### <a name="fabsolids----getinitialoperationkeytrampoline"></a>7.8 `Fab_Operation.`getInitialOperationKeyTrampoline():

Fab_Operation.getInitialOperationKeyTrampoline(self) -> FabSolids.Fab_OperationKey:

Get the initial operation key for a Fab_Operation.

### <a name="fabsolids----gethash"></a>7.9 `Fab_Operation.`getHash():

Fab_Operation.getHash(self) -> Tuple[Any, ...]:

Return Fab_Operation hash.

### <a name="fabsolids----get-geometries-hash"></a>7.10 `Fab_Operation.`get_geometries_hash():

Fab_Operation.get_geometries_hash(self, geometries: Union[FabGeometries.FabGeometry, Tuple[FabGeometries.FabGeometry, ...]]) -> Tuple[Any, ...]:

Return hash of FabGeometry's.

### <a name="fabsolids----setshopbits"></a>7.11 `Fab_Operation.`setShopBits():

Fab_Operation.setShopBits(self, shop_bits: List[FabShops.Fab_ShopBit]) -> None:

Set the Fab_Operation ShopBits attribute.

### <a name="fabsolids----produce"></a>7.12 `Fab_Operation.`produce():

Fab_Operation.produce(self, tracing: str = '') -> Tuple[str, ...]:

Return the operation sort key.

### <a name="fabsolids----post-produce1"></a>7.13 `Fab_Operation.`post_produce1():

Fab_Operation.post_produce1(self, produce_state: FabNodes.Fab_ProduceState, expanded_operations: 'List[Fab_Operation]', tracing: str = '') -> None:

Expand simple operations as approprate.

### <a name="fabsolids----post-produce2"></a>7.14 `Fab_Operation.`post_produce2():

Fab_Operation.post_produce2(self, produce_state: FabNodes.Fab_ProduceState, tracing: str = '') -> None:

NO DOC STRING!

### <a name="fabsolids----to-json"></a>7.15 `Fab_Operation.`to_json():

Fab_Operation.to_json(self) -> Dict[str, Any]:

Return a base JSON dictionary for an Fab_Operation.


## <a name="fabsolids--fab-operationkey"></a>8 Class Fab_OperationKey:

Provides a sorting key for Fab_Operations.
Attributes:
* *MountFence* (int): The user managed fence index for grouping operations within a mount.
* *OperationOrder* (Fab_OperationOrder): The preferred operation order within a group.
* *BitPriority*: (float): A negative number obtained via the getBitPriority method.
* *ShopIndex* (int): The shop index of the bit to be used.
* *MachineIndex* (int): The machine index of the bit to be used.
* *ToolNumber* (int): The Tool number for the tool.

Constructor:
* Fab_OperationKey(MountFence, OperationOrder, BitPriority, ShopIndex, MachineIndex, ToolNumber)


## <a name="fabsolids--fab-operationkind"></a>9 Class Fab_OperationKind:

Value for the kind of operation.


## <a name="fabsolids--fab-operationorder"></a>10 Class Fab_OperationOrder:

 OperationOrder: A enumeration that specifies the desired order of operations.


## <a name="fabsolids--fab-pocket"></a>11 Class Fab_Pocket:

Represents a pocketing operation.
Attributes:
* Name (str): The operation name.
* Mount (FabMount): The FabMount to use for pocketing.
* Geometries (Tuple[FabGeometry, ...]):
  The FabGeomety's that specify the pocket.  The first one must be the outer most pocket
  contour.  The remaining FabGeometries must be pocket "islands".  All islands must be
  contained by the outer most pocket contour and islands must not overlap.
* Depth (float): The pocket depth in millimeters.

Extra Computed Attributes:
* *Geometries* (Tuple[FabGeometry, ...]):
   The Polygon or Circle to pocket.  If a tuple is given, first FabGeometry in the tuple
   specifies the pocket exterior, and the remaining FabGeometry's specify islands of
   material within the pocket that must not be removed.
* *Depth* (float): The pocket depth in millimeters.
* *Bottom_Path* (str): The the path to the generated Pocket bottom STEP file.
See Fab_Operation for even more extra computed Attributes.

Constructor:
* Fab_Pocket(Mount, "Name", Geometries, Depth)

### <a name="fabsolids----post-produce1"></a>11.1 `Fab_Pocket.`post_produce1():

Fab_Pocket.post_produce1(self, produce_state: FabNodes.Fab_ProduceState, expanded_operations: 'List[Fab_Operation]', tracing: str = '') -> None:

Expand simple operations as approprated.

### <a name="fabsolids----getoperationorder"></a>11.2 `Fab_Pocket.`getOperationOrder():

Fab_Pocket.getOperationOrder(self, bit: FabToolTemplates.FabBit) -> FabSolids.Fab_OperationOrder:

Return the Fab_OperationOrder for a Fab_Operation.

### <a name="fabsolids----gethash"></a>11.3 `Fab_Pocket.`getHash():

Fab_Pocket.getHash(self) -> Tuple[Any, ...]:

Return Fab_Pocket hash.

### <a name="fabsolids----get-kind"></a>11.4 `Fab_Pocket.`get_kind():

Fab_Pocket.get_kind(self) -> str:

Return Fab_Pocket kind.

### <a name="fabsolids----post-produce2"></a>11.5 `Fab_Pocket.`post_produce2():

Fab_Pocket.post_produce2(self, produce_state: FabNodes.Fab_ProduceState, tracing: str = '') -> None:

Produce the Pocket.

### <a name="fabsolids----to-json"></a>11.6 `Fab_Pocket.`to_json():

Fab_Pocket.to_json(self) -> Dict[str, Any]:

Return JSON dictionary for Fab_Extrude.



