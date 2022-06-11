# FabTools: FabTools: Tools for Fab.
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
  * FabTooling: This corresponds to the `Tools/` directory.

## Table of Contents (alphabetical order):

* 1 Class: [FabBits](#fabtools--fabbits):
  * 1.1 [write()](#fabtools----write): Write FabBits out to disk.
  * 1.2 [nameLookup()](#fabtools----namelookup): Look up a FabBit by name.
  * 1.3 [stemLookup()](#fabtools----stemlookup): Look up a FabBit by file stem.
* 2 Class: [FabLibraries](#fabtools--fablibraries):
  * 2.1 [nameLookup()](#fabtools----namelookup): Lookup a library by name.
  * 2.2 [write()](#fabtools----write): Write FabLibraries out to disk.
* 3 Class: [FabLibrary](#fabtools--fablibrary):
  * 3.1 [lookupName()](#fabtools----lookupname): Lookup a FabBit by name.
  * 3.2 [lookupNumber()](#fabtools----lookupnumber): Lookup a FabBit by name.
  * 3.3 [write()](#fabtools----write): Write FabLibrary out to disk.
* 4 Class: [FabTooling](#fabtools--fabtooling):
  * 4.1 [write()](#fabtools----write): Write FabTooling into a directory.
* 5 Class: [FabToolingFactory](#fabtools--fabtoolingfactory):
  * 5.1 [drill()](#fabtools----drill): Add a drill to FabToolingFactory:
  * 5.2 [double_angle()](#fabtools----double-angle): Add a drill to FabToolingFactory:
  * 5.3 [dove_tail()](#fabtools----dove-tail): Add a drill to FabToolingFactory:
  * 5.4 [end_mill()](#fabtools----end-mill): Add a drill to FabToolingFactory:
  * 5.5 [v_groove()](#fabtools----v-groove): Add a V grove bit to FabToolingFactory:
  * 5.6 [getLibrary()](#fabtools----getlibrary): Return a FabLibrary containti the current tools.
  * 5.7 [getBits()](#fabtools----getbits): Return FabBits from a FabToolingFactory.
  * 5.8 [write()](#fabtools----write): Using FabToolingFactory write out files for a FabTooling.
  * 5.9 [create_example_tools()](#fabtools----create-example-tools): Create some example tools.

## <a name="fabtools--fabbits"></a>1 Class FabBits:

A collection FabBit's that corresponds to a `Tools/Bit/` sub-directory..
Attributes:
* *Bits* (Tuple[FabBit, ...]): The associated FabBit's in name sorted order.
* *Names* (Tuple[str, ...]): The sorted FabBit names.
* *Stems* (Tuple[str, ...]): Stem names in the same order as the Bits.

Constructor:
* FabBits(Bits, Names, Stems)

### <a name="fabtools----write"></a>1.1 `FabBits.`write():

FabBits.write(self, tools_directory: pathlib.Path, tracing: str = '') -> None:

Write FabBits out to disk.

### <a name="fabtools----namelookup"></a>1.2 `FabBits.`nameLookup():

FabBits.nameLookup(self, name: str) -> FabToolTemplates.FabBit:

Look up a FabBit by name.
Arguments:
* *name* (str): The name of the FabBit.

Returns:
* (FabBit): The mataching FabBit.

Raises:
* (KeyError): If FabBit is  not present.

### <a name="fabtools----stemlookup"></a>1.3 `FabBits.`stemLookup():

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
* *Libraries* (Tuple[FabLibrary, ...): The actual libraries sorted by library name.
* *LibraryNames*: Tuple[str, ...]: The sorted library names.

Constructor:
* FabLibraries("Name", Libraries, LibraryNames)

### <a name="fabtools----namelookup"></a>2.1 `FabLibraries.`nameLookup():

FabLibraries.nameLookup(self, name: str) -> FabTools.FabLibrary:

Lookup a library by name.

### <a name="fabtools----write"></a>2.2 `FabLibraries.`write():

FabLibraries.write(self, tools_directory: pathlib.Path, tracing: str = '') -> None:

Write FabLibraries out to disk.


## <a name="fabtools--fablibrary"></a>3 Class FabLibrary:

Tool libraries directory (e.g. `.../Tools/Library/*.fctl`).
Attributes:
* *Name* (str): The stem of LibraryFile (i.e. `xyz.fctl` => "xyz".)
* *NumberedBits*: Tuple[Tuple[int, FabBit], ...]: A list of numbered to FabBit's.

Constructor:
* FabLibrary("Name", NumberedBits)

### <a name="fabtools----lookupname"></a>3.1 `FabLibrary.`lookupName():

FabLibrary.lookupName(self, name: str) -> FabToolTemplates.FabBit:

Lookup a FabBit by name.

### <a name="fabtools----lookupnumber"></a>3.2 `FabLibrary.`lookupNumber():

FabLibrary.lookupNumber(self, number: int) -> FabToolTemplates.FabBit:

Lookup a FabBit by name.

### <a name="fabtools----write"></a>3.3 `FabLibrary.`write():

FabLibrary.write(self, tools_directory: pathlib.Path, tracing: str = '') -> None:

Write FabLibrary out to disk.


## <a name="fabtools--fabtooling"></a>4 Class FabTooling:

A class that contains FabBit's, FabShape's, and FabLibrary's.
Attributes:
* *Shapes* (FabShapes): The FabShape's.
* *Bits* (FabBits): The FabBit's
* *Libraries* (FabLibraries): The FabLibrary's

Constructor:
* FabTooling(Shapes, Bits, Libraries)

In practice, The FabToolingFactory class is an easier way to create a FabTooling object.

### <a name="fabtools----write"></a>4.1 `FabTooling.`write():

FabTooling.write(self, tools_directory: pathlib.Path, tracing: str = '') -> None:

Write FabTooling into a directory.
Arguments:
* *tools_directory* (PatFile): The `.../Tooling` directory to read from.

Returns:
* (FabTooling) The resulting FabTooling object.


## <a name="fabtools--fabtoolingfactory"></a>5 Class FabToolingFactory:

A class to build a FabTooling.
Attributes:
* *Name* (str): The name of the tooling factory (empty string is allowed.)
* *InitialToolsPath* (PathFile):
  The parent directory of an initial `Tools` directory.
  This directory is used to fetch the available shapes from `.../Tools/Shape`.

### <a name="fabtools----drill"></a>5.1 `FabToolingFactory.`drill():

FabToolingFactory.drill(self, tool_number: int, name: str, stem_name: str, material: str, flutes: int, diameter: Union[str, float], length: Union[str, float], tip_angle: Union[str, float], is_center_cut: bool, maximum_depth: Union[str, float]) -> None:

Add a drill to FabToolingFactory:
Arguments:
* *tool_number* (int): The tool number to use.
* *name* (str): The drill name:
* *stem_name* (str): The file stem name to use for the `.fctb` file.
* *material* (str): The material the tool is made out of.
* *flutes* (int): The number of flutes.
* *diameter* (Union[str, float]): The drill diameter as string (mm/inch) or a float (mm).
* *length* (Union[str, float]): The overall length of the drill.
* *tip_angle* (Union[str, float): The drill point tip angle in degrees.
* *is_center_cut* (bool): True for center cut drills and False otherwise.
* *maximum_depth* (Union[str, float]): The maximum drilling depth.

### <a name="fabtools----double-angle"></a>5.2 `FabToolingFactory.`double_angle():

FabToolingFactory.double_angle(self, tool_number: int, name: str, stem_name: str, material: str, flutes: int, diameter: Union[str, float], cutting_edge_height: Union[str, float], cutting_edge_angle: Union[str, float], length: Union[str, float], shank_diameter: Union[str, float], neck_diameter: Union[str, float], neck_height: Union[str, float]) -> None:

Add a drill to FabToolingFactory:
Arguments:
* *tool_number* (int): The tool number to use.
* *name* (str): The drill name:
* *stem_name* (str): The file stem name to use for the `.fctb` file.
* *material* (str): The material the tool is made out of.
* *flutes* (int): The number of flutes.
* *diameter* (Union[str, float]):
   The diameter of the double angle cutter as string (mm/inch) or a float (mm).
* *cutting_edge_height* (Union[str, float]):
  The height of the double angle cutter from the tool bottom to the neck bottom.
* *cutting_edge_angle* (Union[str, float]):
  The cutting angle of the double angle cutter.
* *length* (Union[str, float]):
  The overall length of the entire double angle cutter including shank.
* *shank_diameter* (Union[str, float]): The diameter of the shank (i.e. non cutting edge.)
* *neck_diameter* (Union[str, float]):
  The diameter of double angle cutter neck.
* *neck_height* (Union[str, float]):
  The height of the neck from the top of the double angle cutter to the bottom of the shank.

### <a name="fabtools----dove-tail"></a>5.3 `FabToolingFactory.`dove_tail():

FabToolingFactory.dove_tail(self, tool_number: int, name: str, stem_name: str, material: str, flutes: int, diameter: Union[str, float], cutting_edge_height: Union[str, float], cutting_edge_angle: Union[str, float], length: Union[str, float], shank_diameter: Union[str, float], neck_diameter: Union[str, float], neck_height: Union[str, float]) -> None:

Add a drill to FabToolingFactory:
Arguments:
* *tool_number* (int): The tool number to use.
* *name* (str): The drill name:
* *stem_name* (str): The file stem name to use for the `.fctb` file.
* *material* (str): The material the tool is made out of.
* *flutes* (int): The number of flutes.
* *diameter* (Union[str, float]):
   The diameter of the bottom of the dove tail cutter as string (mm/inch) or a float (mm).
* *cutting_edge_height* (Union[str, float]):
  The height of the dove tail cutter from the bottom to the neck bottom.
* *cutting_edge_angle* (Union[str, float]):
  The height of the dove tail cutter from the bottom to the neck bottom.
* *length* (Union[str, float]):
  The overall length of the entire dove tail cutter including shank.
* *shank_diameter* (Union[str, float]): The diameter of the shank (i.e. non cutting edge.)
* *neck_diameter* (Union[str, float]):
  The diameter of dove tail cutter neck.
* *neck_height* (Union[str, float]):
  The height of the neck from the top of the dove tail cutter to the bottom of the shank.

### <a name="fabtools----end-mill"></a>5.4 `FabToolingFactory.`end_mill():

FabToolingFactory.end_mill(self, tool_number: int, name: str, stem_name: str, material: str, flutes: int, diameter: Union[str, float], cutting_edge_height: Union[str, float], length: Union[str, float], shank_diameter: Union[str, float]) -> None:

Add a drill to FabToolingFactory:
Arguments:
* *tool_number* (int): The tool number to use.
* *name* (str): The drill name:
* *stem_name* (str): The file stem name to use for the `.fctb` file.
* *material* (str): The material the tool is made out of.
* *flutes* (int): The number of flutes.
* *diameter* (Union[str, float]):
   The diameter end mill cutter as string (mm/inch) or a float (mm).
* *length* (Union[str, float]): The overall length of the entire end-mill including shank.
* *cutting_edge_height (Union[str, float]): The length of the cutting edge.
* *shank_diameter* (Union[str, float]): The diameter of the shank (i.e. non cutting edge.)

### <a name="fabtools----v-groove"></a>5.5 `FabToolingFactory.`v_groove():

FabToolingFactory.v_groove(self, tool_number: int, name: str, stem_name: str, material: str, flutes: int, diameter: Union[str, float], cutting_edge_angle: Union[str, float], cutting_edge_height: Union[str, float], length: Union[str, float], shank_diameter: Union[str, float], tip_diameter: Union[str, float]) -> None:

Add a V grove bit to FabToolingFactory:
Arguments:
* *tool_number* (int): The tool number to use.
* *name* (str): The drill name:
* *stem_name* (str): The file stem name to use for the `.fctb` file.
* *material* (str): The material the tool is made out of.
* *flutes* (int): The number of flutes.
* *diameter* (Union[str, float]):
   The outer diameter v grove bit as string (mm/inch) or a float (mm).
* *length* (Union[str, float]): The overall length of the entire end-mill including shank.
* *cutting_edge_angle (Union[str, float]): The cutting edge angle in degrees.
* *cutting_edge_height (Union[str, float]):
  The length of the cutting edge above the V portion of the bit.
* *shank_diameter* (Union[str, float]): The diameter of the shank (i.e. non cutting edge.)
* *tip_diameter* (Union[str, float]): The bottom tip diameter (set to 0 for a point.)

### <a name="fabtools----getlibrary"></a>5.6 `FabToolingFactory.`getLibrary():

FabToolingFactory.getLibrary(self, library_stem: str, tools_directory: pathlib.Path, tracing: str = '') -> FabTools.FabLibrary:

Return a FabLibrary containti the current tools.

### <a name="fabtools----getbits"></a>5.7 `FabToolingFactory.`getBits():

FabToolingFactory.getBits(self) -> FabTools.FabBits:

Return FabBits from a FabToolingFactory.

### <a name="fabtools----write"></a>5.8 `FabToolingFactory.`write():

FabToolingFactory.write(self, library_stem: str, tools_directory: pathlib.Path, tracing: str) -> None:

Using FabToolingFactory write out files for a FabTooling.
Arguments:
* *library_stem* (str): The stem of the `.fctl` library file in `.../Tools/Library/`.
* *tools_directory* (PathFile): The Tools directory to write everything out to.

### <a name="fabtools----create-example-tools"></a>5.9 `FabToolingFactory.`create_example_tools():

FabToolingFactory.create_example_tools(self, tracing: str = '') -> None:

Create some example tools.



