# Project: Project: A module for creating Fab projects.

## Table of Contents (alphabetical order):

* 1 Class: [Box](#project--box):
  * 1.1 [produce()](#project----produce): Produce the Box.
  * 1.2 [get_all_screws()](#project----get-all-screws): Return all Box screws.
* 2 Class: [BoxSide](#project--boxside):
  * 2.1 [produce()](#project----produce): Produce BoxSide.
* 3 Class: [FabAssembly](#project--fabassembly):
  * 3.1 [is_assembly()](#project----is-assembly):  Return True if FabNode is a FabGroup.
  * 3.2 [to_json()](#project----to-json): Return FabProject JSON structure.
  * 3.3 [post_produce1()](#project----post-produce1): Preform FabAssembly phase1 post production.
  * 3.4 [post_produce2()](#project----post-produce2): Perform FabAssembly phase 2 post production.
* 4 Class: [FabDocument](#project--fabdocument):
  * 4.1 [to_json()](#project----to-json): Return FabProject JSON structure.
  * 4.2 [post_produce1()](#project----post-produce1): Perform FabDocument phase 1 post production.
  * 4.3 [post_produce2()](#project----post-produce2): Close the FabDocument.
  * 4.4 [is_document()](#project----is-document):  Return True if FabNode is a FabGroup.
  * 4.5 [produce()](#project----produce): Produce FabDocument.
* 5 Class: [FabGroup](#project--fabgroup):
  * 5.1 [post_produce1()](#project----post-produce1): Perform FabGroup phase 1 post production.
  * 5.2 [produce()](#project----produce): Create the FreeCAD group object.
  * 5.3 [is_group()](#project----is-group):  Return True if FabNode is a FabGroup.
* 6 Class: [FabProject](#project--fabproject):
  * 6.1 [get_errors()](#project----get-errors): Return the FabProject errors list.
  * 6.2 [is_project()](#project----is-project):  Return True if FabNode is a FabGroup.
  * 6.3 [to_json()](#project----to-json): Return FabProject JSON structure.
  * 6.4 [run()](#project----run): NO DOC STRING!
* 7 Class: [TestAssembly](#project--testassembly):
* 8 Class: [TestDocument](#project--testdocument):
* 9 Class: [TestProject](#project--testproject):
  * 9.1 [probe()](#project----probe): Print out some probe values.
* 10 Class: [TestSolid](#project--testsolid):
  * 10.1 [produce()](#project----produce): NO DOC STRING!

## <a name="project--box"></a>1 Class Box:

Fabricate  a box.
Builds a box given a length, width, height, material, thickness and center point"

Inherited Constructor Attributes:
* *Name* (str): Box name.
* *Parent* (*FabNode*): The parent container.

Additional Constructor Attributes:
* *Length* (float): length in X direction in millimeters.x
* *Width* (float): width in Y direction in millimeters.
* *Height* (float): height in Z direction in millimeters.
* *Thickness* (float): Material thickness in millimeters.
* *Material* (str): Material to use.
* *Center* (Vector): Center of Box.

Produced Attributes:
* *Top* (FabSolid): The box top solid.
* *Bottom* (FabSolid): The box bottom solid.
* *North* (FabSolid): The box north solid.
* *South* (FabSolid): The box south solid.
* *East* (FabSolid): The box east solid.
* *West* (FabSolid): The box west solid.
* *Fasten* (FabFasten): The screw template to use.

### <a name="project----produce"></a>1.1 `Box.`produce():

Box.produce(self) -> None:

Produce the Box.

### <a name="project----get-all-screws"></a>1.2 `Box.`get_all_screws():

Box.get_all_screws(self) -> typing.Tuple[Join.FabJoin, ...]:

Return all Box screws.


## <a name="project--boxside"></a>2 Class BoxSide:

A Box side.
Inherited Constructor Attributes:
* *Name* (str): Box name.
* *Parent* (*FabNode*): The parent container.
* *Material* (str): The Material to use.
* *Color* (str): The color to use.

Additional Constructor Attributes:
* *Contact* (Vector): The center "top" of the side.
* *Normal* (Vector): The normal of the side (away from box center).
* *Orient* (Vector): The orientation vector.
* *HalfLength* (Vector): A vector of half the length in the length direction
* *HalfWidth* (Vector): A vector of half the width in the width direction.
* *Depth* float: Depth of side (opposite direction of *normal*.

### <a name="project----produce"></a>2.1 `BoxSide.`produce():

BoxSide.produce(self) -> None:

Produce BoxSide.


## <a name="project--fabassembly"></a>3 Class FabAssembly:

A group FabSolid's and sub-FabAssembly's.

### <a name="project----is-assembly"></a>3.1 `FabAssembly.`is_assembly():

FabAssembly.is_assembly(self) -> bool:

 Return True if FabNode is a FabGroup.

### <a name="project----to-json"></a>3.2 `FabAssembly.`to_json():

FabAssembly.to_json(self) -> typing.Dict[str, typing.Any]:

Return FabProject JSON structure.

### <a name="project----post-produce1"></a>3.3 `FabAssembly.`post_produce1():

FabAssembly.post_produce1(self, objects_table: typing.Dict[str, typing.Any], fab_steps: Node.FabSteps) -> None:

Preform FabAssembly phase1 post production.

### <a name="project----post-produce2"></a>3.4 `FabAssembly.`post_produce2():

FabAssembly.post_produce2(self, objects_table: typing.Dict[str, typing.Any]) -> None:

Perform FabAssembly phase 2 post production.


## <a name="project--fabdocument"></a>4 Class FabDocument:

Represents a FreeCAD document Document.
Inherited Attributes:
* *Name* (str): Node name
* *Children* (Tuple[Union[FabAssembly, FablGroup, FabSolid], ...]):
  The children nodes which are constrained to "group-like" or a FabSolid.
* *ChlidrenNames* (Tuple[str, ...]): The Children names.

Attributes:
* *FilePath* (Path):
  The Python pathlib.Path file name which must have a suffix of `.fcstd` or `.FCStd`.

### <a name="project----to-json"></a>4.1 `FabDocument.`to_json():

FabDocument.to_json(self) -> typing.Dict[str, typing.Any]:

Return FabProject JSON structure.

### <a name="project----post-produce1"></a>4.2 `FabDocument.`post_produce1():

FabDocument.post_produce1(self, objects_table: typing.Dict[str, typing.Any], fab_steps: Node.FabSteps) -> None:

Perform FabDocument phase 1 post production.

### <a name="project----post-produce2"></a>4.3 `FabDocument.`post_produce2():

FabDocument.post_produce2(self, objects_table: typing.Dict[str, typing.Any]) -> None:

Close the FabDocument.

### <a name="project----is-document"></a>4.4 `FabDocument.`is_document():

FabDocument.is_document(self) -> bool:

 Return True if FabNode is a FabGroup.

### <a name="project----produce"></a>4.5 `FabDocument.`produce():

FabDocument.produce(self) -> None:

Produce FabDocument.


## <a name="project--fabgroup"></a>5 Class FabGroup:

A named group of FabNode's.
Inherited Attributes:
* *Name* (str)
* *Parent* (FabNode)
* *Children* (Tuple[FabNode, ...)

### <a name="project----post-produce1"></a>5.1 `FabGroup.`post_produce1():

FabGroup.post_produce1(self, objects_table: typing.Dict[str, typing.Any], fab_steps: Node.FabSteps) -> None:

Perform FabGroup phase 1 post production.

### <a name="project----produce"></a>5.2 `FabGroup.`produce():

FabGroup.produce(self) -> None:

Create the FreeCAD group object.

### <a name="project----is-group"></a>5.3 `FabGroup.`is_group():

FabGroup.is_group(self) -> bool:

 Return True if FabNode is a FabGroup.


## <a name="project--fabproject"></a>6 Class FabProject:

The Root mode a FabNode tree.

### <a name="project----get-errors"></a>6.1 `FabProject.`get_errors():

FabProject.get_errors(self) -> typing.List[str]:

Return the FabProject errors list.

### <a name="project----is-project"></a>6.2 `FabProject.`is_project():

FabProject.is_project(self) -> bool:

 Return True if FabNode is a FabGroup.

### <a name="project----to-json"></a>6.3 `FabProject.`to_json():

FabProject.to_json(self) -> typing.Dict[str, typing.Any]:

Return FabProject JSON structure.

### <a name="project----run"></a>6.4 `FabProject.`run():

FabProject.run(self, objects_table: typing.Union[typing.Dict[str, typing.Any], NoneType] = None, step_directory: typing.Union[pathlib.Path, NoneType] = None) -> None:

NO DOC STRING!


## <a name="project--testassembly"></a>7 Class TestAssembly:

A Class to test an assembly.


## <a name="project--testdocument"></a>8 Class TestDocument:

A Test file.


## <a name="project--testproject"></a>9 Class TestProject:

A Test Project.

### <a name="project----probe"></a>9.1 `TestProject.`probe():

TestProject.probe(self, label: str) -> None:

Print out some probe values.


## <a name="project--testsolid"></a>10 Class TestSolid:

A test solid to exercise FabSolid code.

### <a name="project----produce"></a>10.1 `TestSolid.`produce():

TestSolid.produce(self) -> None:

NO DOC STRING!



