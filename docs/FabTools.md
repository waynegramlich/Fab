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
* FabToolsDirectory: This corresponds to a `Tools/` directory:  (TBD).
  * FabShapes: This corresponds to a `Tools/Shape/` directory:
    * FabShape: This corresponds to a `.fcstd` tool shape template in the `Tools/Shape/` directory.
  * FabAttributes: This corresponds to bit attributes that do not specify bit shape dimensions.
  * FabBitTemplates: This contains all of the known FabBitTemplate's.
    * FabBitTemplate: This corresponds to a template is used to construct FabBit.
  * FabBits: This corresponds to a `Tools/Bit/` sub-Directory:
    * FabBit: This corresponds to a `.fctb` file in the `Tools/Bit/` directory.  For each different
      Shape, there is a dedicated class that represents that shape:
      * FabBallEndBit: This corresponds to `Tools/Shape/ballend.fcstd`.
      * FabBullNoseBit: This corresponds to `Tools/Shape/bullnose.fcstd`.
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

* 1 Class: [FabBallEndBit](#fabtools--fabballendbit):
* 2 Class: [FabBits](#fabtools--fabbits):
  * 2.1 [lookup()](#fabtools----lookup): Look up a FabBit by name.
* 3 Class: [FabBullNoseBit](#fabtools--fabbullnosebit):
* 4 Class: [FabChamferBit](#fabtools--fabchamferbit):
* 5 Class: [FabDoveTailBit](#fabtools--fabdovetailbit):
* 6 Class: [FabDrillBit](#fabtools--fabdrillbit):
* 7 Class: [FabEndMillBit](#fabtools--fabendmillbit):
* 8 Class: [FabLibraries](#fabtools--fablibraries):
  * 8.1 [nameLookup()](#fabtools----namelookup): Lookup a library by name.
* 9 Class: [FabLibrary](#fabtools--fablibrary):
  * 9.1 [lookupName()](#fabtools----lookupname): Lookup a FabBit by name.
  * 9.2 [lookupNumber()](#fabtools----lookupnumber): Lookup a FabBit by name.
* 10 Class: [FabProbeBit](#fabtools--fabprobebit):
* 11 Class: [FabSlittingSawBit](#fabtools--fabslittingsawbit):
* 12 Class: [FabThreadMillBit](#fabtools--fabthreadmillbit):
* 13 Class: [FabVBit](#fabtools--fabvbit):

## <a name="fabtools--fabballendbit"></a>1 Class FabBallEndBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeHeight* (Union[str, float]): The ball end cutting edge height.
* *Diameter* (Union[str, float]): The ball end cutter diameter.
* *Length* (Union[str, float]): The total length of the ball end.
* *ShankDiameter: (Union[str, float]): The ball end shank diameter.

Constructor:
* FabBallEndBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)


## <a name="fabtools--fabbits"></a>2 Class FabBits:

A collection FabBit's that corresponds to a `Tools/Bit/` sub-directory..
Attributes:
* *BitsDirectory*: (PathFile): The path to the `Tools/Bit/` sub-directory.
* *Bits* (Tuple[FabBit, ...]): The associated FabBit's in name sorted order.
* *Names* (Tuple[str, ...]): The sorted FabBit names.

Constructor:
* FabBits("Name", BitsPath, Bits, Names)

### <a name="fabtools----lookup"></a>2.1 `FabBits.`lookup():

FabBits.lookup(self, name: str) -> FabToolTemplates.FabBit:

Look up a FabBit by name.
Arguments:
* *name* (str): The name of the FabBit.

Returns:
* (FabBit): The mataching FabBit.

Raises:
* (KeyError): If FabBit is  not present.


## <a name="fabtools--fabbullnosebit"></a>3 Class FabBullNoseBit:

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


## <a name="fabtools--fabchamferbit"></a>4 Class FabChamferBit:

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


## <a name="fabtools--fabdovetailbit"></a>5 Class FabDoveTailBit:

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


## <a name="fabtools--fabdrillbit"></a>6 Class FabDrillBit:

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


## <a name="fabtools--fabendmillbit"></a>7 Class FabEndMillBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeHeight* (Union[str, float]): The end mill cutting edge height.
* *Diameter* (Union[str, float]): The end mill cutter diameter.
* *Length* (Union[str, float]): The total length of the end mill.
* *ShankDiameter: (Union[str, float]): The end millshank diameter.

Constructor:
* FabEndMillBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)


## <a name="fabtools--fablibraries"></a>8 Class FabLibraries:

Represents a directory of FabLibrary's.
Attributes:
* *Name* (str): The directory name (i.e. the stem the LibraryPath.)
* *LibrariesPath (PathFile): The directory that contains the FabLibraries.
* *Libraries* (Tuple[FabLibrary, ...): The actual libraries sorted by library name.
* *LibraryNames*: Tuple[str, ...]: The sorted library names.

Constructor:
* FabLibraries("Name", LibrariesPath, Libraries)

### <a name="fabtools----namelookup"></a>8.1 `FabLibraries.`nameLookup():

FabLibraries.nameLookup(self, name: str) -> FabTools.FabLibrary:

Lookup a library by name.


## <a name="fabtools--fablibrary"></a>9 Class FabLibrary:

Tool libraries directory (e.g. `.../Tools/Library/*.fctl`).
Attributes:
* *Name* (str): The stem of LibraryFile (i.e. `xyz.fctl` => "xyz".)
* *LibraryFile* (PathFile): The file for the `.fctl` file.
* *NumberedBitss*: Tuple[Tuple[int, FabBit], ...]: A list of numbered to FabBit's.

Constructor:
* FabLibrary("Name", LibraryFile, Tools)

### <a name="fabtools----lookupname"></a>9.1 `FabLibrary.`lookupName():

FabLibrary.lookupName(self, name: str) -> FabToolTemplates.FabBit:

Lookup a FabBit by name.

### <a name="fabtools----lookupnumber"></a>9.2 `FabLibrary.`lookupNumber():

FabLibrary.lookupNumber(self, number: int) -> FabToolTemplates.FabBit:

Lookup a FabBit by name.


## <a name="fabtools--fabprobebit"></a>10 Class FabProbeBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *Diameter* (Union[str, float]): The probe ball diameter.
* *Length* (Union[str, float]): The total length of the probe.
* *ShaftDiameter: (Union[str, float]): The probe shaft diameter.

Constructor:
* FabProbeBit("Name", BitFile, Shape, Attributes, Diameter, Length, TipAngle)


## <a name="fabtools--fabslittingsawbit"></a>11 Class FabSlittingSawBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *BladeThickness* (Union[str, float]): The cutting saw blade thickness.
* *CapDiameter* (Union[str, float]): The cutting saw end cab diameter.
* *CapHeight* (Union[str, float]): The cutting end end cab height.
* *Diameter* (Union[str, float]): The cutting saw blade diameter.
* *ShankDiameter: (Union[str, float]): The cutting saw shank diameter.

Constructor:
* FabSlittingSawBit("Name", BitFile, Shape, Attributes,
  BladeThickness, CapDiameter, CapHeight, Diameter, Length, ShankDiameter)


## <a name="fabtools--fabthreadmillbit"></a>12 Class FabThreadMillBit:

An thread mill bit template.
Attributes:
* *Name* (str): The name of thread mill bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingAngle* (Union[str, float]): The cutter point angle.
* *Crest* (Union[str, float]): The thread cutter crest thickness.
* *Diameter* (Union[str, float]): The chamfer outer diameter.
* *Length* (Union[str, float]): The total length of the chamfer cutter.
* *NeckDiameter* (Union[str, float]): The diameter of the neck between the cutter and shank
* *NeckLength* (Union[str, float]): The height of the neck between the cutter and shank
* *ShankDiameter: (Union[str, float]): The shank diameter.

Constructor:
* FabThreadMillBit("Name", BitFile, Shape, Attributes, Cuttingngle, Diameter, Length,
  NeckDiameter, NeckLength,  ShankDiameter)


## <a name="fabtools--fabvbit"></a>13 Class FabVBit:

An V groove bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle.
* *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
* *Diameter* (Union[str, float]): The v outer diameter.
* *Length* (Union[str, float]): The total length of the v cutter.
* *ShankDiameter: (Union[str, float]): The shank diameter.
* *TipDiameter* (Union[str, float]): The tip radius of the v cutter.

Constructor:
* FabVBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)



