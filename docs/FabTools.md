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

* 1 Class: [FabBits](#fabtools--fabbits):
  * 1.1 [nameLookup()](#fabtools----namelookup): Look up a FabBit by name.
  * 1.2 [stemLookup()](#fabtools----stemlookup): Look up a FabBit by file stem.
* 2 Class: [FabLibraries](#fabtools--fablibraries):
  * 2.1 [nameLookup()](#fabtools----namelookup): Lookup a library by name.
* 3 Class: [FabLibrary](#fabtools--fablibrary):
  * 3.1 [lookupName()](#fabtools----lookupname): Lookup a FabBit by name.
  * 3.2 [lookupNumber()](#fabtools----lookupnumber): Lookup a FabBit by name.

## <a name="fabtools--fabbits"></a>1 Class FabBits:

A collection FabBit's that corresponds to a `Tools/Bit/` sub-directory..
Attributes:
* *BitsDirectory*: (PathFile): The path to the `Tools/Bit/` sub-directory.
* *Bits* (Tuple[FabBit, ...]): The associated FabBit's in name sorted order.
* *Names* (Tuple[str, ...]): The sorted FabBit names.
* *Stems* (Tuple[str, ...]): Stem names in the same order as the Bits.

Constructor:
* FabBits("Name", BitsPath, Bits, Names)

### <a name="fabtools----namelookup"></a>1.1 `FabBits.`nameLookup():

FabBits.nameLookup(self, name: str) -> FabToolTemplates.FabBit:

Look up a FabBit by name.
Arguments:
* *name* (str): The name of the FabBit.

Returns:
* (FabBit): The mataching FabBit.

Raises:
* (KeyError): If FabBit is  not present.

### <a name="fabtools----stemlookup"></a>1.2 `FabBits.`stemLookup():

FabBits.stemLookup(self, stem: str) -> FabToolTemplates.FabBit:

Look up a FabBit by file stem.
Arguments:
* *stem* (str): The stem of the FabBit (i.e. "5mm_Endmill.fctb" => "5mm_Endmill".)

Returns:
* (FabBit): The mataching FabBit.

Raises:
* (KeyError): If FabBit is  not present.


## <a name="fabtools--fablibraries"></a>2 Class FabLibraries:

Represents a directory of FabLibrary's.
Attributes:
* *Name* (str): The directory name (i.e. the stem the LibraryPath.)
* *LibrariesPath (PathFile): The directory that contains the FabLibraries.
* *Libraries* (Tuple[FabLibrary, ...): The actual libraries sorted by library name.
* *LibraryNames*: Tuple[str, ...]: The sorted library names.

Constructor:
* FabLibraries("Name", LibrariesPath, Libraries)

### <a name="fabtools----namelookup"></a>2.1 `FabLibraries.`nameLookup():

FabLibraries.nameLookup(self, name: str) -> FabTools.FabLibrary:

Lookup a library by name.


## <a name="fabtools--fablibrary"></a>3 Class FabLibrary:

Tool libraries directory (e.g. `.../Tools/Library/*.fctl`).
Attributes:
* *Name* (str): The stem of LibraryFile (i.e. `xyz.fctl` => "xyz".)
* *LibraryFile* (PathFile): The file for the `.fctl` file.
* *NumberedBitss*: Tuple[Tuple[int, FabBit], ...]: A list of numbered to FabBit's.

Constructor:
* FabLibrary("Name", LibraryFile, Tools)

### <a name="fabtools----lookupname"></a>3.1 `FabLibrary.`lookupName():

FabLibrary.lookupName(self, name: str) -> FabToolTemplates.FabBit:

Lookup a FabBit by name.

### <a name="fabtools----lookupnumber"></a>3.2 `FabLibrary.`lookupNumber():

FabLibrary.lookupNumber(self, number: int) -> FabToolTemplates.FabBit:

Lookup a FabBit by name.



