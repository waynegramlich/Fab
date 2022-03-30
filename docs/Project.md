# Project: Project: A module for creating Fab projects.

## Table of Contents (alphabetical order):

* 1 Class: [FabAssembly](#project--fabassembly):
  * 1.1 [is_assembly()](#project----is-assembly):  Return True if FabNode is a FabGroup.
  * 1.2 [to_json()](#project----to-json): Return FabProject JSON structure.
  * 1.3 [post_produce1()](#project----post-produce1): Preform FabAssembly phase1 post production.
  * 1.4 [post_produce2()](#project----post-produce2): Perform FabAssembly phase 2 post production.
* 2 Class: [FabDocument](#project--fabdocument):
  * 2.1 [to_json()](#project----to-json): Return FabProject JSON structure.
  * 2.2 [post_produce1()](#project----post-produce1): Perform FabDocument phase 1 post production.
  * 2.3 [post_produce2()](#project----post-produce2): Close the FabDocument.
  * 2.4 [is_document()](#project----is-document):  Return True if FabNode is a FabGroup.
  * 2.5 [produce()](#project----produce): Produce FabDocument.
* 3 Class: [FabGroup](#project--fabgroup):
  * 3.1 [post_produce1()](#project----post-produce1): Perform FabGroup phase 1 post production.
  * 3.2 [produce()](#project----produce): Create the FreeCAD group object.
  * 3.3 [is_group()](#project----is-group):  Return True if FabNode is a FabGroup.
* 4 Class: [FabProject](#project--fabproject):
  * 4.1 [get_errors()](#project----get-errors): Return the FabProject errors list.
  * 4.2 [is_project()](#project----is-project):  Return True if FabNode is a FabGroup.
  * 4.3 [to_json()](#project----to-json): Return FabProject JSON structure.
  * 4.4 [run()](#project----run): NO DOC STRING!

## <a name="project--fabassembly"></a>1 Class FabAssembly:

A group FabSolid's and sub-FabAssembly's.

### <a name="project----is-assembly"></a>1.1 `FabAssembly.`is_assembly():

FabAssembly.is_assembly(self) -> bool:

 Return True if FabNode is a FabGroup.

### <a name="project----to-json"></a>1.2 `FabAssembly.`to_json():

FabAssembly.to_json(self) -> Dict[str, Any]:

Return FabProject JSON structure.

### <a name="project----post-produce1"></a>1.3 `FabAssembly.`post_produce1():

FabAssembly.post_produce1(self, produce_state: Node._NodeProduceState, tracing: str = '') -> None:

Preform FabAssembly phase1 post production.

### <a name="project----post-produce2"></a>1.4 `FabAssembly.`post_produce2():

FabAssembly.post_produce2(self, produce_state: Node._NodeProduceState) -> None:

Perform FabAssembly phase 2 post production.


## <a name="project--fabdocument"></a>2 Class FabDocument:

Represents a FreeCAD document Document.
Inherited Attributes:
* *Name* (str): Node name
* *Children* (Tuple[Union[FabAssembly, FablGroup, FabSolid], ...]):
  The children nodes which are constrained to "group-like" or a FabSolid.
* *ChlidrenNames* (Tuple[str, ...]): The Children names.

Attributes:
* *FilePath* (Path):
  The Python pathlib.Path file name which must have a suffix of `.fcstd` or `.FCStd`.

### <a name="project----to-json"></a>2.1 `FabDocument.`to_json():

FabDocument.to_json(self) -> Dict[str, Any]:

Return FabProject JSON structure.

### <a name="project----post-produce1"></a>2.2 `FabDocument.`post_produce1():

FabDocument.post_produce1(self, produce_state: Node._NodeProduceState, tracing: str = '') -> None:

Perform FabDocument phase 1 post production.

### <a name="project----post-produce2"></a>2.3 `FabDocument.`post_produce2():

FabDocument.post_produce2(self, produce_state: Node._NodeProduceState) -> None:

Close the FabDocument.

### <a name="project----is-document"></a>2.4 `FabDocument.`is_document():

FabDocument.is_document(self) -> bool:

 Return True if FabNode is a FabGroup.

### <a name="project----produce"></a>2.5 `FabDocument.`produce():

FabDocument.produce(self) -> None:

Produce FabDocument.


## <a name="project--fabgroup"></a>3 Class FabGroup:

A named group of FabNode's.
Inherited Attributes:
* *Name* (str)
* *Parent* (FabNode)
* *Children* (Tuple[FabNode, ...)

### <a name="project----post-produce1"></a>3.1 `FabGroup.`post_produce1():

FabGroup.post_produce1(self, produce_state: Node._NodeProduceState, tracing: str = '') -> None:

Perform FabGroup phase 1 post production.

### <a name="project----produce"></a>3.2 `FabGroup.`produce():

FabGroup.produce(self) -> None:

Create the FreeCAD group object.

### <a name="project----is-group"></a>3.3 `FabGroup.`is_group():

FabGroup.is_group(self) -> bool:

 Return True if FabNode is a FabGroup.


## <a name="project--fabproject"></a>4 Class FabProject:

The Root mode a FabNode tree.

### <a name="project----get-errors"></a>4.1 `FabProject.`get_errors():

FabProject.get_errors(self) -> List[str]:

Return the FabProject errors list.

### <a name="project----is-project"></a>4.2 `FabProject.`is_project():

FabProject.is_project(self) -> bool:

 Return True if FabNode is a FabGroup.

### <a name="project----to-json"></a>4.3 `FabProject.`to_json():

FabProject.to_json(self) -> Dict[str, Any]:

Return FabProject JSON structure.

### <a name="project----run"></a>4.4 `FabProject.`run():

FabProject.run(self, step_directory: Union[pathlib.Path, NoneType] = None) -> None:

NO DOC STRING!



