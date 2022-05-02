# FabTools: FabTools: Tools for Fab..
This is a package provides classes used to define the tooling that is available in a shop.
They basically define some classes that interface with the FreeCAD Path Tools infrastructure.
The "new" FreeCAD Path Tools infrastructure organizes everything into a top level `Tools/`
directory and associated sub-directories as follows:

* `Tools/`: The top level directory that contains a `Shape/`, `Bit/`, and `Library/` sub-directory.
  * `Tools/Shape/`: This sub-directory contains tool template files in FreeCAD `.fcstd` format:
    * `ballend.fcstd`:  The ball end tool template.
    * ...
    * `v-bit.fcstd`: The V-bit groove tool template.

  * `Tools/Bit/`: This sub-directory contains FreeCAD Path Tool bit JSON files (`.fctb`):
    The JSON in each tool bit file (`.fctb`) references one shape `.fcstd` file from `Tools/Shape/`.
    * `6mm_Ball_End.fctb`: A 6mm Ball end end tool bit that uses `ballend.fcstd`.
    * ...
    * `60degree_VBit.fctb`: A 60-degree VBit tool bit that uses `v-bit.fcstd`.

  * `Tools/Library/`: This sub-directory contains FreeCAD Path library JSON files (`.fctl`)
    These files define a tool number to tool bit binding.  In general, each Shop machine
    will tend to have a dedicated library associated with it.  However, some machine tools can
    share the same library.  Each `.fctl` JSON library references Tool Bit files from `Tools/Bin/`.

    * `Default.fctl`: The default tools that comes with FreeCAD.
    * `Machine1.fctl`: The tools library for Machine1.
    * ...
    * `MachineN.fctl`: The tools library for MachineN.

The top-down class hierarchy for the FabTools package is:
* FabToolsDirectory: This corresponds to a `Tools/` directory:
  * FabShapes: This corresponds to a `Tools/Shape/` directory:
    * FabShape: This corresponds to a `.fcstd` tool shape template in the `Tools/Shape/` directory.
  * FabBits: This corresponds to a `Tools/Bit/` sub-Directory:
    * FabBit: This corresponds to a `.fctb` file in the `Tools/Bit/` directory.  For each different
      Shape, there is a dedicated class that represents that shape:
      * FabBallBalleEndBit: This corresponds to `Tools/Shape/ballend.fcstd`.
      * FabBallBullNoseBit: This corresponds to `Tools/Shape/bullnose.fcstd`.
      * FabChamferBit: This corresponds to `Tools/Shape/chamfer.fcstd`.
      * FabDrillBit: This corresponds to `Tools/Shape/drill.fcstd`.
      * FabEndMillBit: This corresponds to `Tools/Shape/endmill.fcstd`.
      * FabProbeBit: This corresponds to `Tools/Shape/probe.fcstd`.
      * FabSlittingSawBit: This corresponds to `Tools/Shape/slittingsaw.fcstd`.
      * FabThreadMillBit: This corresponds to `Tools/Shape/thread-mill.fcstd`.
      * FabVBit: This corresponds to `Tools/Shape/v-bit.fcstd`.
  * FabLibraries: This corresponds to a `Tool/Library` directory:
    * FabLibrary: This corresponds to an individual `.fctl` file in the `Tools/Library` directory.

## Table of Contents (alphabetical order):

* 1 Class: [FabAttributes](#fabtools--fabattributes):
  * 1.1 [toJSON()](#fabtools----tojson): Return FabAttributes as JSON dictionary.
* 2 Class: [FabBallEndBit](#fabtools--fabballendbit):
* 3 Class: [FabBit](#fabtools--fabbit):
* 4 Class: [FabBitTemplate](#fabtools--fabbittemplate):
  * 4.1 [kwargsFromJSON()](#fabtools----kwargsfromjson): Return the keyword arguments needed to initialize a FabBit.
  * 4.2 [toJSON()](#fabtools----tojson): Convert a FabBit to a JSON dictionary using a FabBitTemplate.
* 5 Class: [FabBitTemplates](#fabtools--fabbittemplates):
* 6 Class: [FabBits](#fabtools--fabbits):
  * 6.1 [lookup()](#fabtools----lookup): Look up a FabBit by name.
* 7 Class: [FabBullNoseBit](#fabtools--fabbullnosebit):
* 8 Class: [FabChamferBit](#fabtools--fabchamferbit):
* 9 Class: [FabDoveTailBit](#fabtools--fabdovetailbit):
* 10 Class: [FabDrillBit](#fabtools--fabdrillbit):
* 11 Class: [FabLibraries](#fabtools--fablibraries):
  * 11.1 [nameLookup()](#fabtools----namelookup): Lookup a library by name.
* 12 Class: [FabLibrary](#fabtools--fablibrary):
  * 12.1 [lookupName()](#fabtools----lookupname): Lookup a FabBit by name.
  * 12.2 [lookupNumber()](#fabtools----lookupnumber): Lookup a FabBit by name.
* 13 Class: [FabShape](#fabtools--fabshape):
* 14 Class: [FabShapes](#fabtools--fabshapes):
  * 14.1 [lookup()](#fabtools----lookup): Lookup a FabShape by name.

## <a name="fabtools--fabattributes"></a>1 Class FabAttributes:

Additional information about a FabBit.
Attributes:
* *Values* (Tuple[Tuple[str, Any], ...): Sorted list of named attribute values.
* *Names* (Tuple[str, ...]): Sorted list of attribute names:

### <a name="fabtools----tojson"></a>1.1 `FabAttributes.`toJSON():

FabAttributes.toJSON(self) -> Dict[str, Any]:

Return FabAttributes as JSON dictionary.


## <a name="fabtools--fabballendbit"></a>2 Class FabBallEndBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
* *Diameter* (Union[str, float]): The end mill cutter diameter.
* *Length* (Union[str, float]): The total length of the end mill.
* *ShankDiameter: (Union[str, float]): The shank diameter.

Constructor:
* FabBallEndBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)


## <a name="fabtools--fabbit"></a>3 Class FabBit:

Base class common to all FabBit sub-classes;
Attributes:
* *Name* (str): The name of the tool template.
* *BitFile* (PathFile): The file path to the corresponding `.fctb` file.
* *Shape*: (FabShape): The associated FabShape.
* *Attributes*: (FabAttributes): The optional bit attributes.

Constructor:
* FabBit("Name", BitFile, Shape, Attributes)


## <a name="fabtools--fabbittemplate"></a>4 Class FabBitTemplate:

A Template for creating a FabBit.
Attributes:
* Name* (str): The FabBit name.
* Shape* (FabShape):
* Parameters (Tuple[Tuple[str, Tuple[type, ...]], ...]):
  The allowed parameter names and associated types of the form:
  ("ParameterName", (type1, ..., typeN), "example") for no type checking ("ParameterName",)
* Attributes (Tuple[Tuple[str, Tuple[type, ...]], ...]):
  The allowed parameter names and associated types of the form:
  ("ParameterName", (type1, ..., typeN), "example") for no type checking ("ParameterName",)

### <a name="fabtools----kwargsfromjson"></a>4.1 `FabBitTemplate.`kwargsFromJSON():

FabBitTemplate.kwargsFromJSON(self, json_dict: Dict[str, Any], bit_file: pathlib.Path, shapes: FabTools.FabShapes, tracing: str = '') -> Dict[str, Any]:

Return the keyword arguments needed to initialize a FabBit.

### <a name="fabtools----tojson"></a>4.2 `FabBitTemplate.`toJSON():

FabBitTemplate.toJSON(self, bit: 'FabBit', with_attributes: bool) -> Dict[str, Any]:

Convert a FabBit to a JSON dictionary using a FabBitTemplate.


## <a name="fabtools--fabbittemplates"></a>5 Class FabBitTemplates:

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
* *VBit* (FabBitTemplate): A template for creating FabVBitBits's.
Constructor:
* FabBitTemplates(BallEnd, BullNose, Chamfer, DoveTail, Drill,
  EndMill, Probe, SlittingSaw, ThreadMill, VBit)

Use FabBitTemplates.factory() instead of the constructor.


## <a name="fabtools--fabbits"></a>6 Class FabBits:

A collection FabBit's that corresponds to a `Tools/Bit/` sub-directory..
Attributes:
* *BitsDirectory*: (PathFile): The path to the `Tools/Bit/` sub-directory.
* *Bits* (Tuple[FabBit, ...]): The associated FabBit's in name sorted order.
* *Names* (Tuple[str, ...]): The sorted FabBit names.

Contructor:
* FabBits("Name", BitsPath, Bits, Names)

### <a name="fabtools----lookup"></a>6.1 `FabBits.`lookup():

FabBits.lookup(self, name: str) -> FabTools.FabBit:

Look up a FabBit by name.
Arguments:
* *name* (str): The name of the FabBit.

Returns:
* (FabBit): The mataching FabBit.

Raises:
* (KeyError): If FabBit is  not present.


## <a name="fabtools--fabbullnosebit"></a>7 Class FabBullNoseBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
* *Diameter* (Union[str, float]): The bull nose cutter diameter.
* *FlatRadius* (Union[str, float]): The flat radius of the bull nose cutter.
* *Length* (Union[str, float]): The total length of the bull nose cutter.
* *ShankDiameter: (Union[str, float]): The shank diameter.

Constructor:
* FabBullNoseBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)


## <a name="fabtools--fabchamferbit"></a>8 Class FabChamferBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle.
* *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
* *Diameter* (Union[str, float]): The chamfer outer diameter.
* *Length* (Union[str, float]): The total length of the chamfer cutter.
* *ShankDiameter: (Union[str, float]): The shank diameter.
* *TipDiameter* (Union[str, float]): The tip radius of the chamfer cutter.

Constructor:
* FabChamferBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)


## <a name="fabtools--fabdovetailbit"></a>9 Class FabDoveTailBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle.
* *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
* *Diameter* (Union[str, float]): The chamfer outer diameter.
* *Length* (Union[str, float]): The total length of the chamfer cutter.
* *NeckDiameter* (Union[str, float]): The diameter of the neck between the cutter and shank
* *NeckHeight* (Union[str, float]): The height of the neck between the cutter and shank
* *ShankDiameter: (Union[str, float]): The shank diameter.
* *TipDiameter* (Union[str, float]): The tip radius of the chamfer cutter.

Constructor:
* FabDoveTailBit("Name", BitFile, Shape, Attributes, CuttingEdgeAngle, CuttingEdgeHeight,
  Diameter, Length, NeckDiameter, NeckHeight,  ShankDiameter, TipDiameter)


## <a name="fabtools--fabdrillbit"></a>10 Class FabDrillBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle.
* *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
* *Diameter* (Union[str, float]): The drill outer diameter.
* *Length* (Union[str, float]): The total length of the drill cutter.
* *TipAngle: (Union[str, float]): The drill tip point angle.

Constructor:
* FabDrillBit("Name", BitFile, Shape, Attributes, Diameter, Length, TipAngle)


## <a name="fabtools--fablibraries"></a>11 Class FabLibraries:

Represents a directory of FabLibrary's.
Attributes:
* *Name* (str): The directory name (i.e. the stem the LibraryPath.)
* *LibrariesPath (PathFile): The directory that contains the FabLibraries.
* *Libraries* (Tuple[FabLibrary, ...): The actual libraries sorted by library name.
* *LibraryNames*: Tuple[str, ...]: The sorted library names.

Constructor:
* FabLibraries("Name", LibrariesPath, Libraries)

### <a name="fabtools----namelookup"></a>11.1 `FabLibraries.`nameLookup():

FabLibraries.nameLookup(self, name: str) -> FabTools.FabLibrary:

Lookup a library by name.


## <a name="fabtools--fablibrary"></a>12 Class FabLibrary:

Tool libraries directory (e.g. `.../Tools/Library/*.fctl`).
Attributes:
* *Name* (str): The stem of LibraryFile (i.e. `xyz.fctl` => "xyz".)
* *LibraryFile* (PathFile): The file for the `.fctl` file.
* *NumberedBitss*: Tuple[Tuple[int, FabBit], ...]: A list of numbered to FabBit's.

Constructor:
* FabLibrary("Name", LibraryFile, Tools)

### <a name="fabtools----lookupname"></a>12.1 `FabLibrary.`lookupName():

FabLibrary.lookupName(self, name: str) -> FabTools.FabBit:

Lookup a FabBit by name.

### <a name="fabtools----lookupnumber"></a>12.2 `FabLibrary.`lookupNumber():

FabLibrary.lookupNumber(self, number: int) -> FabTools.FabBit:

Lookup a FabBit by name.


## <a name="fabtools--fabshape"></a>13 Class FabShape:

Corresponds to FreeCAD Path library Shape 'template'.
Attributes:
* *Name* (str): The shape name.
* *ShapePath* (PathFile): The path to the associated `fcstd` file.


## <a name="fabtools--fabshapes"></a>14 Class FabShapes:

A directory of FabShape's.
Attributes:
* *Directory* (PathFile): The directory containing the FabShapes (.fcstd) files.
* *Shapes* (Tuple[FabShape, ...]: The corresponding FabShape's.
* *Names* (Tuple[str, ...]: The sorted names of the FabShape's.

Constructor:
* FabShapes(Directory, Shapes)

### <a name="fabtools----lookup"></a>14.1 `FabShapes.`lookup():

FabShapes.lookup(self, name) -> FabTools.FabShape:

Lookup a FabShape by name.



