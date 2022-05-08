# FabToolTemplates: FabToolTemplates: Templates for defining tool bits.
This package provides some classes that are used to build tables of tools needed for a shop
definition.  These are lower level classes that really are not expected to be used by end-users.
The classes are:
* FabShape:
  This represents a single Tool Bit shape template that is represented as a standard FreeCAD
  `.fcstd` document.  These files live in the `.../Tools/Shape/` directory.
* FabShapes:
  This represents all of the FabShape's in a `.../Tools/Shape/` directory.
* FabAttributes:
  This a just a sorted list of attribute value pairs. These values get stored into `.fctb` files
  in the `.../Tools/Bit/` directory.  In general, these values do not specify the physical shape
  parameters needed by the FabShape `.fcstd` files.  Instead, they specify things like the tool
  bit material, number flutes, etc.
* FabBitTemplate:
  This a class that specifies a all of the fields needed to for a FabBit.  The `.fctb` files
  live in the `.../Tools/Bit/` directory and a template is used to read/write the `.fctb` files.
* FabBitTemplates:
  This class simply lists one FaBBitTemplate for each different FabShape.
* FabTemplatesFactory:
  This is a trivial class that instatiates one of each FabTemplate object that can be reused since
  they never change.

## Table of Contents (alphabetical order):

* 1 Class: [FabAttributes](#fabtooltemplates--fabattributes):
  * 1.1 [toJSON()](#fabtooltemplates----tojson): Return FabAttributes as JSON dictionary.
* 2 Class: [FabBit](#fabtooltemplates--fabbit):
  * 2.1 [toJSON()](#fabtooltemplates----tojson): Return the JSON associated with a FabBit.
  * 2.2 [write()](#fabtooltemplates----write): Write FabBit out to disk.
* 3 Class: [FabBitTemplate](#fabtooltemplates--fabbittemplate):
  * 3.1 [kwargsFromJSON()](#fabtooltemplates----kwargsfromjson): Return the keyword arguments needed to initialize a FabBit.
  * 3.2 [toJSON()](#fabtooltemplates----tojson): Convert a FabBit to a JSON dictionary using a FabBitTemplate.
* 4 Class: [FabBitTemplates](#fabtooltemplates--fabbittemplates):
* 5 Class: [FabBitTemplatesFactory](#fabtooltemplates--fabbittemplatesfactory):
* 6 Class: [FabShape](#fabtooltemplates--fabshape):
  * 6.1 [verify()](#fabtooltemplates----verify): Verify that FabShape contents matches the actual file contents.
  * 6.2 [write()](#fabtooltemplates----write): Write FabShape out to disk.
* 7 Class: [FabShapes](#fabtooltemplates--fabshapes):
  * 7.1 [lookup()](#fabtooltemplates----lookup): Lookup a FabShape by name.
  * 7.2 [write()](#fabtooltemplates----write): Write FabShapes out to disk.

## <a name="fabtooltemplates--fabattributes"></a>1 Class FabAttributes:

Additional information about a FabBit.
Attributes:
* *Values* (Tuple[Tuple[str, Any], ...): Sorted list of named attribute values.
* *Names* (Tuple[str, ...]): Sorted list of attribute names:

### <a name="fabtooltemplates----tojson"></a>1.1 `FabAttributes.`toJSON():

FabAttributes.toJSON(self) -> Dict[str, Any]:

Return FabAttributes as JSON dictionary.


## <a name="fabtooltemplates--fabbit"></a>2 Class FabBit:

Base class common to all FabBit sub-classes;
Attributes:
* *Name* (str): The name of the tool template (e.g. "5mm Endmill".)
* *BitStem* (str): The stem of the corresponding `.fctb` file (e.g. "5mm_Endmill".)
* *ShapeStem*: (str): The stem of the corresponding shape `.fcstd` file (e.g. "endmill".)
* *Attributes*: (FabAttributes): The optional bit attributes.

Constructor:
* FabBit("Name", BitStem, ShapeStem, Attributes)

### <a name="fabtooltemplates----tojson"></a>2.1 `FabBit.`toJSON():

FabBit.toJSON(self) -> Dict[str, Any]:

Return the JSON associated with a FabBit.

### <a name="fabtooltemplates----write"></a>2.2 `FabBit.`write():

FabBit.write(self, tools_directory: pathlib.Path, tracing: str = '') -> None:

Write FabBit out to disk.


## <a name="fabtooltemplates--fabbittemplate"></a>3 Class FabBitTemplate:

A Template for creating a FabBit.
Attributes:
* *Name* (str): The template name which matches the FabXXXBit class type.
* *BitName* (str): The name of the example bit.
* *BitStem* (str): The stem of the example `.fctb` file.  (see getExample).
* *ShapeStem* (str): The stem of associated example `.fcstd` shape file.
* *Parameters* (Tuple[Tuple[str, Tuple[type, ...]], ...]):
  The allowed parameter names and associated types of the form:
  ("ParameterName", (type1, ..., typeN), "example") for no type checking ("ParameterName",)
* *Attributes* (Tuple[Tuple[str, Tuple[type, ...]], ...]):
  The allowed parameter names and associated types of the form:
  ("ParameterName", (type1, ..., typeN), "example") for no type checking ("ParameterName",)

Constructor:
* FabBitTemplate("Name", "BitStem", "ShapeStem", Parameters, Attributes)

### <a name="fabtooltemplates----kwargsfromjson"></a>3.1 `FabBitTemplate.`kwargsFromJSON():

FabBitTemplate.kwargsFromJSON(self, json_dict: Dict[str, Any], bit_file: pathlib.Path, tracing: str = '') -> Dict[str, Any]:

Return the keyword arguments needed to initialize a FabBit.
Arguments:
* *json_dict* (Dict[str, Any]): The JSON dictionary of information.
* *bit_file* (PathFile): The PathFile to the FabBit JSON.

Returns:
* (Dict[str, Any]) this is aF bunch of keyword arguments that can be passed in as
  a arguments to FabBit constructor.

### <a name="fabtooltemplates----tojson"></a>3.2 `FabBitTemplate.`toJSON():

FabBitTemplate.toJSON(self, bit: 'FabBit', with_attributes: bool) -> Dict[str, Any]:

Convert a FabBit to a JSON dictionary using a FabBitTemplate.
Arguments:
* *bit* (FabBit): The FabBit to convert into JASON.
* *with_attributes* (bool): If True, all attributes are present, otherwise they are not.

Returns:
* (Dict[str, Any]): The associated JSON dictionary.


## <a name="fabtooltemplates--fabbittemplates"></a>4 Class FabBitTemplates:

A container of FabBitTemplate's to/from JSON.
Attributes:
* *BallEnd* (FabBitTemplate): A template for creating FabBallEndBit's.
* *BullNose* (FabBitTemplate): A template for creating FabBullNoseBit's.
* *Chamfer* (FabBitTemplate): A template for creating FabChamferBit's.
* *DoveTail* (FabBitTemplate): A template for creating FabDoveTailBit's.
* *Drill* (FabBitTemplate): A template for creating FabDrillBit's.
* *EndMill* (FabBitTemplate): A template for creating FabEndMillBit's.
* *Probe* (FabBitTemplate): A template for creating FabProbeBit's.
* *SlittingSaw* (FabBitTemplate): A template for creating FabSlittingSawBit's.
* *ThreadMill* (FabBitTemplate): A template for create FabThreadMillBit's.
* *V* (FabBitTemplate): A template for creating FabVBit's.
Constructor:
* FabBitTemplates(BallEnd, BullNose, Chamfer, DoveTail, Drill,
  EndMill, Probe, SlittingSaw, ThreadMill, VBit)

Use FabBitTemplates.factory() instead of the constructor.


## <a name="fabtooltemplates--fabbittemplatesfactory"></a>5 Class FabBitTemplatesFactory:

FabBitTempaltesFactory: A class for getting a shared FabBitsTemplate object.


## <a name="fabtooltemplates--fabshape"></a>6 Class FabShape:

Corresponds to FreeCAD Path library Shape 'template'.
Attributes:
* *Name* (str):
  The shape name which happens to be the stem `.fcstd` file (e.g. "v-bit.fcstd" => "v-bit".)
* *Contents* (bytes):
  The contents of the `.fcstd` file.

### <a name="fabtooltemplates----verify"></a>6.1 `FabShape.`verify():

FabShape.verify(self, tools_directory: pathlib.Path) -> bool:

Verify that FabShape contents matches the actual file contents.

### <a name="fabtooltemplates----write"></a>6.2 `FabShape.`write():

FabShape.write(self, tools_directory: pathlib.Path, tracing: str = '') -> None:

Write FabShape out to disk.


## <a name="fabtooltemplates--fabshapes"></a>7 Class FabShapes:

A directory of FabShape's.
Attributes:
* *Shapes* (Tuple[FabShape, ...]: The corresponding FabShape's.
* *Names* (Tuple[str, ...]: The sorted names of the FabShape's.

Constructor:
* FabShapes(Directory, Shapes, Names)

### <a name="fabtooltemplates----lookup"></a>7.1 `FabShapes.`lookup():

FabShapes.lookup(self, name) -> FabToolTemplates.FabShape:

Lookup a FabShape by name.

### <a name="fabtooltemplates----write"></a>7.2 `FabShapes.`write():

FabShapes.write(self, tools_directory: pathlib.Path, tracing: str = '') -> None:

Write FabShapes out to disk.



