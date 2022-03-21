# Test: Test: Test classes for Fab.

## Table of Contents (alphabetical order):

* 1 Class: [Box](#test--box):
  * 1.1 [produce()](#test----produce): Produce the Box.
  * 1.2 [get_all_screws()](#test----get-all-screws): Return all Box screws.
* 2 Class: [BoxSide](#test--boxside):
  * 2.1 [produce()](#test----produce): Produce BoxSide.
* 3 Class: [TestAssembly](#test--testassembly):
* 4 Class: [TestDocument](#test--testdocument):
* 5 Class: [TestProject](#test--testproject):
  * 5.1 [probe()](#test----probe): Print out some probe values.
* 6 Class: [TestSolid](#test--testsolid):
  * 6.1 [produce()](#test----produce): NO DOC STRING!

## <a name="test--box"></a>1 Class Box:

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

### <a name="test----produce"></a>1.1 `Box.`produce():

Box.produce(self) -> None:

Produce the Box.

### <a name="test----get-all-screws"></a>1.2 `Box.`get_all_screws():

Box.get_all_screws(self) -> Tuple[Join.FabJoin, ...]:

Return all Box screws.


## <a name="test--boxside"></a>2 Class BoxSide:

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

### <a name="test----produce"></a>2.1 `BoxSide.`produce():

BoxSide.produce(self) -> None:

Produce BoxSide.


## <a name="test--testassembly"></a>3 Class TestAssembly:

A Class to test an assembly.


## <a name="test--testdocument"></a>4 Class TestDocument:

A Test file.


## <a name="test--testproject"></a>5 Class TestProject:

A Test Project.

### <a name="test----probe"></a>5.1 `TestProject.`probe():

TestProject.probe(self, label: str) -> None:

Print out some probe values.


## <a name="test--testsolid"></a>6 Class TestSolid:

A test solid to exercise FabSolid code.

### <a name="test----produce"></a>6.1 `TestSolid.`produce():

TestSolid.produce(self) -> None:

NO DOC STRING!



