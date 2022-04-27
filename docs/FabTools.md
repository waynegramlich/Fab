# FabTools: FabTools: Tools for Fab..
This is a package provides classes used to define the tooling that is available in a shop.
They basically some classes that interface with the FreeCAD tool bit and tool table JSON files.

The classes are:
* FabTool: The base class for tool bits.
  * FabBallEndTool: The class for defining a ball end mill.
  * FabBullNoseTool: The class for defining a bull nose end mill.
  * FabChamferTool: The class for defining a chamfer end mill.
  * FabDrillTool: The class for defining a drill bit.
  * FabEndMillTool: The class for defining a standard end mill.
  * FabProbeTool: The class for defining a probe tool.
  * FabSlittingSawTool: The class for defining a slitting saw.
  * FabThreadMill: The class for defining a thread cutter.
  * FabVTool: The class for defining a V bit mill.
* FabToolTable: A class for defining a tool table for one a given FabMachine.

## Table of Contents (alphabetical order):

* 1 Class: [FabBallEndTool](#fabtools--fabballendtool):
* 2 Class: [FabBullNoseTool](#fabtools--fabbullnosetool):
* 3 Class: [FabChamferTool](#fabtools--fabchamfertool):
* 4 Class: [FabDrillTool](#fabtools--fabdrilltool):
* 5 Class: [FabEndMillTool](#fabtools--fabendmilltool):
* 6 Class: [FabProbeTool](#fabtools--fabprobetool):
* 7 Class: [FabSlittingSawTool](#fabtools--fabslittingsawtool):
* 8 Class: [FabThreadMill](#fabtools--fabthreadmill):
* 9 Class: [FabTool](#fabtools--fabtool):
  * 9.1 [to_json()](#fabtools----to-json): Return FabToolTemptlate as a JSON string.
  * 9.2 [write_json()](#fabtools----write-json): Write FabToolTemptlate out to a JSON file.
* 10 Class: [FabTools](#fabtools--fabtools):
  * 10.1 [add_tool()](#fabtools----add-tool): Add a FabTool to FabTools.
  * 10.2 [add_tools()](#fabtools----add-tools): Add a some FabTool's to a FabTools.
  * 10.3 [to_library_json()](#fabtools----to-library-json): Convert FabToolTable to JSON.
  * 10.4 [combined_to_json()](#fabtools----combined-to-json): Return the JSON of a combined tool table JASON file.
* 11 Class: [FabVBitTool](#fabtools--fabvbittool):

## <a name="fabtools--fabballendtool"></a>1 Class FabBallEndTool:

An end-mill bit template.
Required Base Attributes: *Name*, *FileName*.
Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

Required FreeCAD Parameter Attributes:
* *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
* *Diameter* (Union[str, float]): The end mill cutter diameter.
* *Length* (Union[str, float]): The total length of the end mill.
* *ShankDiameter: (Union[str, float]): The shank diameter.

Extra Keyword Only Attributes:
* *Flutes*: (int): The number of flutes.


## <a name="fabtools--fabbullnosetool"></a>2 Class FabBullNoseTool:

FabBullNose: A bull nose template.
Required Base Attributes: *Name*, *FileName*.
Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

Required FreeCAD Parameter Attributes:
* *CuttingEdgeHeight* (Union[str, float]): The total length of the cutting edge.
* *Diameter* (Union[str, float]): The primary diameter
* *FlatRadius* (Union[str, float]):
  The radius at the flat portion at the bottom where cutters are rounded.
* *Length* (Union[str, float]): The total length of the bull nose cutter.
* *ShankDiameter: (Union[str, float]): The shank diameter.

Extra Keyword Only Attributes:
* *Flutes*: (int = 0): The number of flutes.


## <a name="fabtools--fabchamfertool"></a>3 Class FabChamferTool:

FabDrillTool: An drill bit template.
Required Base Attributes: *Name*, *FileName*.
Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

Required FreeCAD Parameter Attributes:
* *CuttingEdgeHeight* (Union[str, float]): The cutting edge edge height.
* *Diameter* (Union[str, float]): The widest diameter.
* *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle in degrees.
* *Length* (Union[str, float]): The total length of the chamfer bit.
* *ShankDiameter*: (Union[str, float]): The shank diameter.
* *TipDiameter*: (Union[str, float]): The diameter at the "tip".

Extra Keyword Only Attributes:
* *Flutes*: (int = 0): The number of flutes.


## <a name="fabtools--fabdrilltool"></a>4 Class FabDrillTool:

An drill bit template.
Required Base Attributes: *Name*, *FileName*.
Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

Required FreeCAD Parameter Attributes:
* *Diameter* (Union[str, float]): The end mill cutter diameter.
* *Length* (Union[str, float]): The total length of the end mill.
* *TipAngle: (Union[str, float]): The shank diameter.

Extra Keyword Only Attributes:
* *Flutes*: (int = 0): The number of flutes.
* *FlutesLength* (Union[str, float] = 0.0): The drill flutes length (i.e. maximum drill depth).
* *SplitPoint* (bool = False): True if self-centering split points are present.


## <a name="fabtools--fabendmilltool"></a>5 Class FabEndMillTool:

An end-mill bit template.
Required Base Attributes: *Name*, *FileName*.
Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

Required FreeCAD Parameter Attributes:
* *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
* *Diameter* (Union[str, float]): The end mill cutter diameter.
* *Length* (Union[str, float]): The total length of the end mill.
* *ShankDiameter: (Union[str, float]): The shank diameter.

Extra Keyword Only Attributes:
* *Flutes*: (int): The number of flutes.


## <a name="fabtools--fabprobetool"></a>6 Class FabProbeTool:

A touch off probe.
Required Base Attributes: *Name*, *FileName*.
Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

Required FreeCAD Parameter Attributes:
* *Diameter* (Union[str, float]): The end mill cutter diameter.
* *Length* (Union[str, float]): The total length of the end mill.
* *ShaftDiameter: (Union[str, float]): The shaft diameter.


## <a name="fabtools--fabslittingsawtool"></a>7 Class FabSlittingSawTool:

An slitting saw bit.
Required Base Attributes: *Name*, *FileName*.
Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

Required FreeCAD Parameter Attributes:
* *BladeThickness* (Union[str, float]): The blade thickness.
* *CapHeight* (Union[str, float]): The screw cap height.
* *CapDiameter* (Union[str, float]): The screw cap diameter.
* *Diameter* (Union[str, float]): The blade diameter.
* *Length* (Union[str, float]): The over tool length.
* *ShankDiameter* (Union[str, float]): The diameter of the shank above the blade.

Extra Keyword Only Attributes:
* *Teeth*: (int = 0): The of teeth on the saw blade.


## <a name="fabtools--fabthreadmill"></a>8 Class FabThreadMill:

An thread cutter bit.
Required Base Attributes: *Name*, *FileName*.
Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

Required FreeCAD Parameter Attributes:
* *Crest* (Union[str, float]): The height of the cutting disk.
* *Diameter* (Union[str, float]): The diameter of the cutting disk.
* *Length* (Union[str, float]): The over tool length.
* *NeckDiameter* (Union[str, float]): The diameter of the neck poartion above the cutting disk.
* *NeckLength* (Union[str, float]): The length of the neck portion above the cutting disk.
* *ShankDiameter* (Union[str, float]): The diameter of the shank above the Disk.

Extra Keyword Only Attributes:
* *Flutes*: (int = 0): The number of flutes.


## <a name="fabtools--fabtool"></a>9 Class FabTool:

FabCNCShape: Base class for CNC tool bit templates.
Required Base Attributes:
* *Name* (str): The name of the tool template.
* *FileName* (pathlib.Path): The tool template file name (must have a suffix of`.fcstd` file)

Keyword Only Base Attributes:
* *Material: (str = ""):
  The tool material is one of "Carbide", "CastAlloy", "Ceramics", "Diamond",
  "HighCarbonToolSteel", "HighSpeedSteel", or "Sialon".  This can optionally be followed
  by further description (e.g. ":Cobalt", ":Cobalt:M42", ":Cobalt:M42:ALTIN")
* *OffsetLength: (Unnion[None, str, float] = None):
  The distance from the tool tip to the Z zero point on the mill.
  This is used to populate a CNC controller offset field for each tool.
* *ToolHolderHeight: (Union[None, str, float] = None):
  The distance from tool tip to the base of the tool holder.
  The tool holder must be kept above the clearance height.

### <a name="fabtools----to-json"></a>9.1 `FabTool.`to_json():

FabTool.to_json(self, with_attributes: bool = True, table_name: str = '') -> str:

Return FabToolTemptlate as a JSON string.
Arguments:
* *with_attributes* (bool = True):
  If True include additional "non-FreeCAD" attributes; otherwise leave blank.
* *table_name* (str = ""):
  A stand alone JSON file is produced when empty, otherwise an indented JSON
  dictiornary named *table_name* is produced.

### <a name="fabtools----write-json"></a>9.2 `FabTool.`write_json():

FabTool.write_json(self, file_path: pathlib.Path) -> None:

Write FabToolTemptlate out to a JSON file.


## <a name="fabtools--fabtools"></a>10 Class FabTools:

A collection of related FabTool's.
Attributes:
* *Name* (str): The Tooltable name.
* *Description* (str): A brief description of the tool table/library.

In FreeCAD there is currently two very related concepts.  There is a tool table
and a tool library.  A tool table is the JSON file that FreeCAD Path GUI can import
and export.  This file has all of the information for each tool embedded inside.
The new tool library is JSON file that just has a number and a reference to a "bit" JSON file.
This class can deal with both.

### <a name="fabtools----add-tool"></a>10.1 `FabTools.`add_tool():

FabTools.add_tool(self, tool_number: int, tool: FabTools.FabTool) -> None:

Add a FabTool to FabTools.

### <a name="fabtools----add-tools"></a>10.2 `FabTools.`add_tools():

FabTools.add_tools(self, tools: Dict[int, FabTools.FabTool]) -> None:

Add a some FabTool's to a FabTools.

### <a name="fabtools----to-library-json"></a>10.3 `FabTools.`to_library_json():

FabTools.to_library_json(self, with_hash: bool) -> None:

Convert FabToolTable to JSON.

### <a name="fabtools----combined-to-json"></a>10.4 `FabTools.`combined_to_json():

FabTools.combined_to_json(self, table_name: str) -> str:

Return the JSON of a combined tool table JASON file.


## <a name="fabtools--fabvbittool"></a>11 Class FabVBitTool:

An V bit template.
Required Base Attributes: *Name*, *FileName*.
Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

Required FreeCAD Parameter Attributes:
* *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle in degrees.
* *Diameter* (Union[str, float]): The widest diameter.
* *CuttingEdgeHeight* (Union[str, float]): The cutting edge edge height.
* *TipDiameter*: (Union[str, float]): The diameter at the "tip".
* *Length* (Union[str, float]): The total length of the chamfer bit.
* *ShankDiameter*: (Union[str, float]): The shank diameter.

Extra Keyword Only Attributes:
* *Flutes*: (int = 0): The number of flutes.



