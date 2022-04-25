# Node: 
Node: Fab tree management.

The Node package provides a tree of FabNode's that roughly corresponds to a FreeCAD tree
as shown in the FreeCAD model view.

There are two classes defined:
* FabBox:
  This is a generic bounding box class similar to the FreeCAD BoundBox class
  is used to enclose the FabNode contents and its children FabNode's.
  This class has way more more properties and is immutable (unlike the FreeCAD BoundBox class.)
* FabNode:
  This is a sub-class of FabBox that has a name, a parent FabNode and other data structures
  required to maintain the tree.

Other Fab packages (e.g. Project and Solid) further sub-class FabNode to provide finer
grained distinctions between FabNode's.

The FabNode class enforces the following constraints:
* Each FabNode name must be compatible with a Python variable name
  (i.e. upper/lower letters, digits, and underscores with a non-digit first letter.)
* All of the children FabNode's must have distinct names.
* A FabNode may occur only once in the Tree (i.e. DAG = Direct Acyclic Graph.)

Two notable attributes of the FabNode are:
* *Up* (FabNode):
   The FabNode's parent.
   Up is frequently used in code to access other FabNode's higher in the FabNode tree.
* *Project* (FabNode):
   The FabNode tree root and is always of type FabProject which is defined in Project package.
   Due to the Python lanaguage disallowal of circular `import` statements, this is returned
   as type FabNode rather than type FabProject.
See the FabNode documentation for further attributes.

(Briefly talk about produce() method here.)

## Table of Contents (alphabetical order):

* 1 Class: [FabBox](#node--fabbox):
  * 1.1 [enclose()](#node----enclose): Initialize a FabBox.
  * 1.2 [reorient()](#node----reorient): Reorient FabBox given a Placement.
  * 1.3 [intersect()](#node----intersect): Compute Line Segment intersection with a FabBox.a
* 2 Class: [FabNode](#node--fabnode):
  * 2.1 [get_errors()](#node----get-errors): Return FabNode errors list.
  * 2.2 [error()](#node----error): Record and error message with FabNode root.
  * 2.3 [is_project()](#node----is-project): Return True if FabNode is a FabProject.
  * 2.4 [is_document()](#node----is-document): Return True if FabNode is a FabProject.
  * 2.5 [is_group()](#node----is-group): Return True if FabNode is a FabGroup.
  * 2.6 [is_assembly()](#node----is-assembly): Return True if FabNode is a FabAssembly.
  * 2.7 [is_solid()](#node----is-solid): Return True if FabNode is a FabAssembly.
  * 2.8 [to_json()](#node----to-json): Return a dictionary for JSON output.
  * 2.9 [pre_produce()](#node----pre-produce): Perform FabNode pre produce operations.
  * 2.10 [produce()](#node----produce): Empty FabNode produce method to be over-ridden.
  * 2.11 [post_produce1()](#node----post-produce1): Do FabNode phase 1 post production.
  * 2.12 [post_produce2()](#node----post-produce2): Do FabNode phase 2 post production.
  * 2.13 [get_parent_document()](#node----get-parent-document): NO DOC STRING!
  * 2.14 [set_tracing()](#node----set-tracing): Set the FabNode indentation tracing level.
  * 2.15 [probe()](#node----probe): Perform a probe operation.
* 3 Class: [FabSteps](#node--fabsteps):
  * 3.1 [scan()](#node----scan): Scan the associated directory for matching .step files.
  * 3.2 [activate()](#node----activate): Reserve a .step file name to be read/written.
  * 3.3 [flush_inactives()](#node----flush-inactives): Delete inactive .step files.

## <a name="node--fabbox"></a>1 Class FabBox:

X/Y/Z Axis Aligned Cuboid.
An FabBox is represents a cuboid (i.e. a rectangular parallelpiped, or right prism) where
the edges are aligned with the X, Y, and Z axes.  This is basically equivalent to the FreeCAD
BoundBox object, but with way more attributes to access various points on the cuboid surface.

The basic attribute nomenclature is based on the compass points North (+Y), South (-Y),
East (+X) and West (-X).  Two additional "compass" points called Top (+Z) and Bottom (-Z)
are introduced as well.

Thus:
* TNE represents the Top North East corner of the box.
* NE represents the center of the North East box edge.
* T represents the center of the top face of the box.

Attributes:
* Minimums/Maximums:
  * XMax (float): The maximum X (East).
  * XMin (float): The minimum X (West).
  * YMax (float): The maximum Y (North).
  * YMin (float): The minimum Y (South).
  * ZMax (float): The maximum Z (Top).
  * ZMin (float): The minimum Z (Bottom).
* The 6 face attributes:
  * B (Vector): Center of bottom face.
  * E (Vector): Center of east face.
  * N (Vector): Center of north face.
  * S (Vector): Center of south face.
  * T (Vector): Center of top face.
  * W (Vector): Center of west face.
* The 8 corner attributes:
  * BNE (Vector): Bottom North East corner.
  * BNW (Vector): Bottom North West corner.
  * BSE (Vector): Bottom South East corner.
  * BSW (Vector): Bottom South West corner.
  * TNE (Vector): Top North East corner.
  * TNW (Vector): Top North West corner.
  * TSE (Vector): Top South East corner.
  * TSW (Vector): Bottom South West corner.
* The 12 edge attributes:
  * BE (Vector): Center of Bottom East edge.
  * BN (Vector): Center of Bottom North edge.
  * BS (Vector): Center of Bottom South edge.
  * BW (Vector): Center of Bottom West edge.
  * NE (Vector): Center of North East edge
  * NW (Vector): Center of North West edge
  * SE (Vector): Center of South East edge
  * SW (Vector): Center of South West edge
  * TE (Vector): Center of Top East edge.
  * TN (Vector): Center of Top North edge.
  * TS (Vector): Center of Top South edge.
  * TW (Vector): Center of Top West edge.
* The other attributes:
  * C (Vector): Center point.
  * DB (Vector): Bottom direction (i.e. B - C)
  * DE (Vector): East direction (i.e. E - C)
  * DN (Vector): North direction (i.e. N - C)
  * DS (Vector): South direction (i.e. S - C)
  * DT (Vector): Top direction (i.e. T - C)
  * DW (Vector): West direction (i.e. W - C)
  * DX (float): X box length (i.e. (E - W).Length)
  * DY (float): Y box length (i.e. (N - S).Length)
  * DZ (float): Z box length (i.e. (T - B).Length)

### <a name="node----enclose"></a>1.1 `FabBox.`enclose():

FabBox.enclose(self, bounds: Sequence[Union[cadquery.occ_impl.geom.Vector, ForwardRef('FabBox')]]) -> None:

Initialize a FabBox.
Arguments:
  * *bounds* (Sequence[Union[Vector, FabBox]]):
    A sequence of points or boxes to enclose.

Raises:
  * ValueError: For bad or empty corners.

### <a name="node----reorient"></a>1.2 `FabBox.`reorient():

FabBox.reorient(self, placement: Any) -> 'FabBox':

Reorient FabBox given a Placement.
Note after the *placement* is applied, the resulting box is still rectilinear with the
X/Y/Z axes.  In particular, box volume is *not* conserved.

Arguments:
* *placement* (Placement): The placement of the box corners.

### <a name="node----intersect"></a>1.3 `FabBox.`intersect():

FabBox.intersect(self, segment_start: cadquery.occ_impl.geom.Vector, segment_end: cadquery.occ_impl.geom.Vector, tracing: str = '') -> Tuple[bool, float, float]:

Compute Line Segment intersection with a FabBox.a
Arguments:
* *segment_start* (Vector): Start point of the line segment.
* *segment_end* (Vector): End point of the line segment.

Returns:
* (bool): True is some portion of the line segment is inside of the FabBox.
* (Vector): When True, the possibly truncated line segment point near *segment_start*.
* (Vector): When True, the possibly truncated line segment point near *segment_end*.


## <a name="node--fabnode"></a>2 Class FabNode:

Represents one node in the FabNode tree.
Inherited Attributes:
* All of the FabBox attributes.

Attributes:
* *Label* (str): The FabNode name.
* *Up* (FabNode): The FabNode parent.
* *FullPath* (str):  The FabNode full path from the root.  (Filled in)
* *Tracing* (str):
  A non-empty indentation string when tracing is enabled.
  This field is recursively set when *set_tracing*() is explicitly set.

### <a name="node----get-errors"></a>2.1 `FabNode.`get_errors():

FabNode.get_errors(self) -> List[str]:

Return FabNode errors list.
This method is only implemented by the FabProject class.

### <a name="node----error"></a>2.2 `FabNode.`error():

FabNode.error(self, error_message: str) -> None:

Record and error message with FabNode root.

### <a name="node----is-project"></a>2.3 `FabNode.`is_project():

FabNode.is_project(self) -> bool:

Return True if FabNode is a FabProject.

### <a name="node----is-document"></a>2.4 `FabNode.`is_document():

FabNode.is_document(self) -> bool:

Return True if FabNode is a FabProject.

### <a name="node----is-group"></a>2.5 `FabNode.`is_group():

FabNode.is_group(self) -> bool:

Return True if FabNode is a FabGroup.

### <a name="node----is-assembly"></a>2.6 `FabNode.`is_assembly():

FabNode.is_assembly(self) -> bool:

Return True if FabNode is a FabAssembly.

### <a name="node----is-solid"></a>2.7 `FabNode.`is_solid():

FabNode.is_solid(self) -> bool:

Return True if FabNode is a FabAssembly.

### <a name="node----to-json"></a>2.8 `FabNode.`to_json():

FabNode.to_json(self) -> Dict[str, Any]:

Return a dictionary for JSON output.

### <a name="node----pre-produce"></a>2.9 `FabNode.`pre_produce():

FabNode.pre_produce(self, produce_state: Node._NodeProduceState) -> None:

Perform FabNode pre produce operations.

### <a name="node----produce"></a>2.10 `FabNode.`produce():

FabNode.produce(self) -> None:

Empty FabNode produce method to be over-ridden.

### <a name="node----post-produce1"></a>2.11 `FabNode.`post_produce1():

FabNode.post_produce1(self, produce_state: Node._NodeProduceState, tracing: str = '') -> None:

Do FabNode phase 1 post production.

### <a name="node----post-produce2"></a>2.12 `FabNode.`post_produce2():

FabNode.post_produce2(self, produce_state: Node._NodeProduceState) -> None:

Do FabNode phase 2 post production.

### <a name="node----get-parent-document"></a>2.13 `FabNode.`get_parent_document():

FabNode.get_parent_document(self, tracing: str = '') -> 'FabNode':

NO DOC STRING!

### <a name="node----set-tracing"></a>2.14 `FabNode.`set_tracing():

FabNode.set_tracing(self, tracing: str):

Set the FabNode indentation tracing level.
This typically done, by adding this call immediately after calling super().__post_init__().

     @dataclass
     class MySubClass(Node):   # Or some class descended from Node*.
        '''MySubClass doc string.'''

        super().__post_init__()
        self.set_tracing(" ")  # Set the tracing here.
        # All children nodes will that are added, will have tracing set as well.

### <a name="node----probe"></a>2.15 `FabNode.`probe():

FabNode.probe(self, label: str) -> None:

Perform a probe operation.
This method can be overriden and called to perform debug probes.


## <a name="node--fabsteps"></a>3 Class FabSteps:

Manage directory of .step files.
This class will scan a directory for STEP files of the format `Name__XXXXXXXXXXXXXXXX.stp`,
where  `Name` is the human readable name of the file and `XXXXXXXXXXXXXXXX` is the 64-bit
has value associated with the .step file contents.

There are three operations:
* FabSteps(): This is the initalizer.
* activate(): This method is used to activate a .stp file for reading and/or writing.
* flush_stales(): This method is used to remove previous .stp files that are now longer used.

### <a name="node----scan"></a>3.1 `FabSteps.`scan():

FabSteps.scan(self, tracing: str = '') -> None:

Scan the associated directory for matching .step files.

### <a name="node----activate"></a>3.2 `FabSteps.`activate():

FabSteps.activate(self, name: str, hash_tuple: Tuple[Any, ...], tracing: str = '') -> pathlib.Path:

Reserve a .step file name to be read/written.
This method reserves a .step file name to be read/written.

Arguments:
* name (str): The human readable name of the step file.
* hash_tuple (Tuple[Any]):
  A tuple tree, where the leaf values are bool, int, float, or str values.

Returns:
* (Path): The full path to the .step file to be read/written.

### <a name="node----flush-inactives"></a>3.3 `FabSteps.`flush_inactives():

FabSteps.flush_inactives(self, tracing: str = '') -> None:

Delete inactive .step files.



