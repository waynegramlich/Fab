# FabProjects: FabProjects: Module for creating Fabrication projects.
Classes:
* FabProject: The top-level project.
* FabDocument: This is one-to-one with a FreeCAD (`.fcstd`) document file.
* FabAssembly: This is a collection of FabAssembly's and FabSolid's.

## Table of Contents (alphabetical order):

* 1 Class: [FabAssembly](#fabprojects--fabassembly):
  * 1.1 [is_assembly()](#fabprojects----is-assembly):  Return True if FabNode is a Fab_Group.
  * 1.2 [to_json()](#fabprojects----to-json): Return FabProject JSON structure.
  * 1.3 [post_produce2()](#fabprojects----post-produce2): Perform FabAssembly phase1 post production.
  * 1.4 [post_produce3()](#fabprojects----post-produce3): Perform FabAssembly phase 2 post production.
* 2 Class: [FabDocument](#fabprojects--fabdocument):
  * 2.1 [to_json()](#fabprojects----to-json): Return FabProject JSON structure.
  * 2.2 [post_produce2()](#fabprojects----post-produce2): Perform FabDocument phase 1 post production.
  * 2.3 [post_produce3()](#fabprojects----post-produce3): Close the FabDocument.
  * 2.4 [is_document()](#fabprojects----is-document):  Return True if FabNode is a Fab_Group.
  * 2.5 [produce()](#fabprojects----produce): Produce FabDocument.
* 3 Class: [FabProject](#fabprojects--fabproject):
  * 3.1 [setShops()](#fabprojects----setshops): Set the shops to use for a FabProject.
  * 3.2 [get_errors()](#fabprojects----get-errors): Return the FabProject errors list.
  * 3.3 [is_project()](#fabprojects----is-project):  Return True if FabNode is a Fab_Group.
  * 3.4 [to_json()](#fabprojects----to-json): Return FabProject JSON structure.
  * 3.5 [run()](#fabprojects----run): NO DOC STRING!
* 4 Class: [Fab_Group](#fabprojects--fab-group):
  * 4.1 [post_produce2()](#fabprojects----post-produce2): Perform Fab_Group phase 1 post production.
  * 4.2 [produce()](#fabprojects----produce): Create the FreeCAD group object.
  * 4.3 [is_group()](#fabprojects----is-group):  Return True if FabNode is a Fab_Group.

## <a name="fabprojects--fabassembly"></a>1 Class FabAssembly:

A group FabSolid's and sub-FabAssembly's.

### <a name="fabprojects----is-assembly"></a>1.1 `FabAssembly.`is_assembly():

FabAssembly.is_assembly(self) -> bool:

 Return True if FabNode is a Fab_Group.

### <a name="fabprojects----to-json"></a>1.2 `FabAssembly.`to_json():

FabAssembly.to_json(self) -> Dict[str, Any]:

Return FabProject JSON structure.

### <a name="fabprojects----post-produce2"></a>1.3 `FabAssembly.`post_produce2():

FabAssembly.post_produce2(self, produce_state: FabNodes.Fab_ProduceState, tracing: str = '') -> None:

Perform FabAssembly phase1 post production.

### <a name="fabprojects----post-produce3"></a>1.4 `FabAssembly.`post_produce3():

FabAssembly.post_produce3(self, produce_state: FabNodes.Fab_ProduceState) -> None:

Perform FabAssembly phase 2 post production.


## <a name="fabprojects--fabdocument"></a>2 Class FabDocument:

Represents a FreeCAD document Document.
Inherited Attributes:
* *Name* (str): Node name
* *Children* (Tuple[Union[FabAssembly, FablGroup, FabSolid], ...]):
  The children nodes which are constrained to "group-like" or a FabSolid.
* *ChlidrenNames* (Tuple[str, ...]): The Children names.

Attributes:
* *FilePath* (Path):
  The Python pathlib.Path file name which must have a suffix of `.fcstd` or `.FCStd`.

### <a name="fabprojects----to-json"></a>2.1 `FabDocument.`to_json():

FabDocument.to_json(self) -> Dict[str, Any]:

Return FabProject JSON structure.

### <a name="fabprojects----post-produce2"></a>2.2 `FabDocument.`post_produce2():

FabDocument.post_produce2(self, produce_state: FabNodes.Fab_ProduceState, tracing: str = '') -> None:

Perform FabDocument phase 1 post production.

### <a name="fabprojects----post-produce3"></a>2.3 `FabDocument.`post_produce3():

FabDocument.post_produce3(self, produce_state: FabNodes.Fab_ProduceState) -> None:

Close the FabDocument.

### <a name="fabprojects----is-document"></a>2.4 `FabDocument.`is_document():

FabDocument.is_document(self) -> bool:

 Return True if FabNode is a Fab_Group.

### <a name="fabprojects----produce"></a>2.5 `FabDocument.`produce():

FabDocument.produce(self) -> None:

Produce FabDocument.


## <a name="fabprojects--fabproject"></a>3 Class FabProject:

The Root mode a FabNode tree.
Attributes:
* *Label* (str): The project name.
* *Shops* (FabShops):
  The FabShop's available for fabrication.  Set using FabShop.setShops() method.

Constructor:
* FabProject.new("Name")

### <a name="fabprojects----setshops"></a>3.1 `FabProject.`setShops():

FabProject.setShops(self, shops: FabShops.FabShops) -> None:

Set the shops to use for a FabProject.

### <a name="fabprojects----get-errors"></a>3.2 `FabProject.`get_errors():

FabProject.get_errors(self) -> List[str]:

Return the FabProject errors list.

### <a name="fabprojects----is-project"></a>3.3 `FabProject.`is_project():

FabProject.is_project(self) -> bool:

 Return True if FabNode is a Fab_Group.

### <a name="fabprojects----to-json"></a>3.4 `FabProject.`to_json():

FabProject.to_json(self) -> Dict[str, Any]:

Return FabProject JSON structure.

### <a name="fabprojects----run"></a>3.5 `FabProject.`run():

FabProject.run(self, step_directory: Union[pathlib.Path, NoneType] = None) -> None:

NO DOC STRING!


## <a name="fabprojects--fab-group"></a>4 Class Fab_Group:

A named group of FabNode's.
Inherited Attributes:
* *Name* (str)
* *Parent* (FabNode)
* *Children* (Tuple[FabNode, ...)

### <a name="fabprojects----post-produce2"></a>4.1 `Fab_Group.`post_produce2():

Fab_Group.post_produce2(self, produce_state: FabNodes.Fab_ProduceState, tracing: str = '') -> None:

Perform Fab_Group phase 1 post production.

### <a name="fabprojects----produce"></a>4.2 `Fab_Group.`produce():

Fab_Group.produce(self) -> None:

Create the FreeCAD group object.

### <a name="fabprojects----is-group"></a>4.3 `Fab_Group.`is_group():

Fab_Group.is_group(self) -> bool:

 Return True if FabNode is a Fab_Group.



