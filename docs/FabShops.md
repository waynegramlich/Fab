# FabShops: FabShop: Shop and associated Machines.
This is a package provides classes used to define what machines are available in a shop.

* FabShop: A collection of FabMachine's.
* FabMachine: A base class for all machines.
  * FabCNC: A CNC mill or router:
    * FabRouter: A CNC router.
    * FabMill: A CNC Mill.
  * FabCutter: A CNC Laser or Water Jet:
    * FabLaser: A CNC laser.
    * FabWaterJet: A CNC water jet.
  * FabLathe: A CNC lathe.
  * Fab3DPrinter: A 3D printer.

## Table of Contents (alphabetical order):

* 1 Class: [FabBallEndTool](#fabshops--fabballendtool):
* 2 Class: [FabBullNoseTool](#fabshops--fabbullnosetool):
* 3 Class: [FabCNC](#fabshops--fabcnc):
* 4 Class: [FabCNCMill](#fabshops--fabcncmill):
* 5 Class: [FabCNCRouter](#fabshops--fabcncrouter):
* 6 Class: [FabChamferTool](#fabshops--fabchamfertool):
* 7 Class: [FabController](#fabshops--fabcontroller):
* 8 Class: [FabDrillTool](#fabshops--fabdrilltool):
* 9 Class: [FabEndMillTool](#fabshops--fabendmilltool):
* 10 Class: [FabLocation](#fabshops--fablocation):
* 11 Class: [FabMachine](#fabshops--fabmachine):
* 12 Class: [FabProbeTool](#fabshops--fabprobetool):
* 13 Class: [FabShop](#fabshops--fabshop):
  * 13.1 [lookup()](#fabshops----lookup): Return the named FabMachine.
* 14 Class: [FabSlittingSawTool](#fabshops--fabslittingsawtool):
* 15 Class: [FabSpindle](#fabshops--fabspindle):
* 16 Class: [FabTable](#fabshops--fabtable):
* 17 Class: [FabThreadMill](#fabshops--fabthreadmill):
* 18 Class: [FabTool](#fabshops--fabtool):
  * 18.1 [to_json()](#fabshops----to-json): Return FabToolTemptlate as a JSON string.
  * 18.2 [write_json()](#fabshops----write-json): Write FabToolTemptlate out to a JSON file.
* 19 Class: [FabTools](#fabshops--fabtools):
  * 19.1 [add_tool()](#fabshops----add-tool): Add a FabTool to FabTools.
  * 19.2 [add_tools()](#fabshops----add-tools): Add a some FabTool's to a FabTools.
  * 19.3 [to_library_json()](#fabshops----to-library-json): Convert FabToolTable to JSON.
  * 19.4 [combined_to_json()](#fabshops----combined-to-json): Return the JSON of a combined tool table JASON file.
* 20 Class: [FabVBitTool](#fabshops--fabvbittool):

## <a name="fabshops--fabballendtool"></a>1 Class FabBallEndTool:

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


## <a name="fabshops--fabbullnosetool"></a>2 Class FabBullNoseTool:

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


## <a name="fabshops--fabcnc"></a>3 Class FabCNC:

Represents a CNC mill or router.
Attributes:
* *Name* (str): The CNC mill name.
* *Placement* (str): The placement in the shop.
* *WorkVolume* (Vector): The work volume DX/DY/DZ.
* *Table* (FabTable):
* *Spindle* (FabSpindle): The spindle description.
* *Controller* (FabController): The Controller used by the CNC machine.

Contstructor:
* FabCNC("Name", "Position", WorkVolume, Spindle, Table, Controller)


## <a name="fabshops--fabcncmill"></a>4 Class FabCNCMill:

Represents a CNC mill.
Attributes:
* *Name* (str): The CNC mill name.
* *Placement* (str): The placement in the shop.
* *WorkVolume* (Vector): The work volume DX/DY/DZ.
* *Table* (FabTable):
* *Spindle* (FabSpindle): The spindle description.
* *Controller* (FabController): The Controller used by the CNC machine.
* *Kind* (str): Return the string "CNCMill".

Contstructor:
* FabCNCMill("Name", "Position", WorkVolume, Spindle, Table, Spindle, Controller)


## <a name="fabshops--fabcncrouter"></a>5 Class FabCNCRouter:

Represents a CNC Router.
Attributes:
* *Name* (str): The CNC mill name.
* *Position* (str): The position in the shop.
* *WorkVolume* (Vector): The work volume DX/DY/DZ.
* *Table* (FabTable):
* *Spindle* (FabSpindle): The spindle description.
* *Controller* (FabController): The Controller used by the CNC machine.
* *Kind* (str): Return the string "CNCRouter".

Contstructor:
* FabCNCRouter("Name", "Position", WorkVolume, Spindle, Table, Spindle, Controller)


## <a name="fabshops--fabchamfertool"></a>6 Class FabChamferTool:

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


## <a name="fabshops--fabcontroller"></a>7 Class FabController:

Specifies a CNC controller.
Attributes:
* *Name* (str): The controller name.
* *PostProcessor* (str): The post processor to use.

Constructor:
* FabController("Name", PostProcessor)


## <a name="fabshops--fabdrilltool"></a>8 Class FabDrillTool:

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


## <a name="fabshops--fabendmilltool"></a>9 Class FabEndMillTool:

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


## <a name="fabshops--fablocation"></a>10 Class FabLocation:

Location information for a shop.
The shop can be located with as much or as little specificity and the shop owner chooses.
Sometimes the Shop is on a mobile platform (like a boat) and no location makes much sense.

Attributes:
* *CountryCode* (str):
  The two letter country code of the country the shop is located in.  (Default: "")
* *StateProvince* (str):
  The state or province the shop is located in. (Default: "")
* *County* (str):
  The county/canton/whatever that the shop is located in.  (Default: "")
* *City* (str):
  The city the shop is located in.  (Default: "")
* *StreetAddress* (str):
  The street address of the shop. (Default: "")
* *Unit* (str):
  The unit within the building that contains the shop. (Default: "")
* *ZipCode* (str):
  The postal Zip Code that contains the shop. (Default: "")
* *Latitude* (str):
  The shop latitude. (Default: "")
* *Longitude* (str):
  The shop longitude. (Default: "")
* *PhoneNumber* (str):
  The shop phone number. (Default: "")
* *URL* (str):
  The shop Web URL. (Default: "")

Constructor (use Keywords):
* FabLocation(CountryCode="...", StateProvince="...", County="...", City="...",
  StreetAddress="...", Unit="...", ZipCode="...", Latitude="...", Longitude="...",
  PhoneNumber="...", URL="...)


## <a name="fabshops--fabmachine"></a>11 Class FabMachine:

Base class for a FabShop machine.
Attributes:
* *Name* (str): The name of the  machines.
* *Placement* (str): The machine placement in the shop.
* *Kind* (str): The machine kind (supplied by sub-class).

Constructor:
* Fabmachine("Name", "Placement")


## <a name="fabshops--fabprobetool"></a>12 Class FabProbeTool:

A touch off probe.
Required Base Attributes: *Name*, *FileName*.
Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

Required FreeCAD Parameter Attributes:
* *Diameter* (Union[str, float]): The end mill cutter diameter.
* *Length* (Union[str, float]): The total length of the end mill.
* *ShaftDiameter: (Union[str, float]): The shaft diameter.


## <a name="fabshops--fabshop"></a>13 Class FabShop:

Describes Machines/Tool in a Shop.
Attributes:
* *Name* (str): The Shop Name.
* *Location* (FabLocation): The shop location.
* *Machines* (Tuple[FabMachine, ...]):
  The machines within the shop.  The machines must have unique names within the shop.

Constructor  :
* FabShop(Name="Name", Location=FabLocation(...), Machines=(...,))

### <a name="fabshops----lookup"></a>13.1 `FabShop.`lookup():

FabShop.lookup(self, machine_name: str) -> FabShops.FabMachine:

Return the named FabMachine.


## <a name="fabshops--fabslittingsawtool"></a>14 Class FabSlittingSawTool:

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


## <a name="fabshops--fabspindle"></a>15 Class FabSpindle:

Represents a machine tool spindle.
Attributes:
* *Type* (str): Spindle Type (e.g. "R8", "Cat40", etc.)
* *Speed* (int): Maximum spindle speed in rotations per minute.
* *Reversable* (bool): True if spindle can be reversed.
* *FloodCooling* (bool): True if flood cooling is available.
* *MistCooling* (bool): True if mist coooling is available.

Constructor:
* FabSpindle("Type", Speed, Reversable, FloodCooling, MistCooling)


## <a name="fabshops--fabtable"></a>16 Class FabTable:

Represents a CNC table.
Attributes:
* *Name* (str): The table name.
* *Length* (float): The overall table length in millimeters.
* *Width* (float): The overall table width in millimieters.
* *Height* (float): The overall table Height in millimeters.
* *Slots* (int): The number of T slots.
* *SlotWidth* (float): The top slot width in millimeters.
* *SlotDepth* (float): The overall slot depth from top to keyway bottom in millimeters.
* *KeywayWidth* (float): The keyway width in millimeters.
* *KeywayHeight* (float): The keyway height in millimeters.

Constructor:
*  FabTable("Name", Length, Width, Height, Slots,
   SlotWidth, SlotDepth, KeywayWidth, KeywayHeight)


## <a name="fabshops--fabthreadmill"></a>17 Class FabThreadMill:

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


## <a name="fabshops--fabtool"></a>18 Class FabTool:

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

### <a name="fabshops----to-json"></a>18.1 `FabTool.`to_json():

FabTool.to_json(self, with_attributes: bool = True, table_name: str = '') -> str:

Return FabToolTemptlate as a JSON string.
Arguments:
* *with_attributes* (bool = True):
  If True include additional "non-FreeCAD" attributes; otherwise leave blank.
* *table_name* (str = ""):
  A stand alone JSON file is produced when empty, otherwise an indented JSON
  dictiornary named *table_name* is produced.

### <a name="fabshops----write-json"></a>18.2 `FabTool.`write_json():

FabTool.write_json(self, file_path: pathlib.Path) -> None:

Write FabToolTemptlate out to a JSON file.


## <a name="fabshops--fabtools"></a>19 Class FabTools:

A collection of related FabTool's.
Attributes:
* *Name* (str): The Tooltable name.
* *Description* (str): A brief description of the tool table/library.

In FreeCAD there is currently two very related concepts.  There is a tool table
and a tool library.  A tool table is the JSON file that FreeCAD Path GUI can import
and export.  This file has all of the information for each tool embedded inside.
The new tool library is JSON file that just has a number and a reference to a "bit" JSON file.
This class can deal with both.

### <a name="fabshops----add-tool"></a>19.1 `FabTools.`add_tool():

FabTools.add_tool(self, tool_number: int, tool: FabShops.FabTool) -> None:

Add a FabTool to FabTools.

### <a name="fabshops----add-tools"></a>19.2 `FabTools.`add_tools():

FabTools.add_tools(self, tools: Dict[int, FabShops.FabTool]) -> None:

Add a some FabTool's to a FabTools.

### <a name="fabshops----to-library-json"></a>19.3 `FabTools.`to_library_json():

FabTools.to_library_json(self, with_hash: bool) -> None:

Convert FabToolTable to JSON.

### <a name="fabshops----combined-to-json"></a>19.4 `FabTools.`combined_to_json():

FabTools.combined_to_json(self, table_name: str) -> str:

Return the JSON of a combined tool table JASON file.


## <a name="fabshops--fabvbittool"></a>20 Class FabVBitTool:

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



