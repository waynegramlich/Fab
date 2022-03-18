# CNC: ApexPath: Apex interface to FreeCAD Path workbench.

## Table of Contents (alphabetical order):

* 1 Class: [FabBallEndBit](#cnc--fabballendbit):
* 2 Class: [FabBitTemplate](#cnc--fabbittemplate):
  * 2.1 [to_json()](#cnc----to-json): Return FabBitTemptlate as a JSON string.
  * 2.2 [write_json()](#cnc----write-json): Write FabBitTemptlate out to a JSON file.
* 3 Class: [FabBullNoseBit](#cnc--fabbullnosebit):
* 4 Class: [FabChamferBit](#cnc--fabchamferbit):
* 5 Class: [FabDrillBit](#cnc--fabdrillbit):
* 6 Class: [FabEndMillBit](#cnc--fabendmillbit):
* 7 Class: [FabProbeBit](#cnc--fabprobebit):
* 8 Class: [FabSlittingSawBit](#cnc--fabslittingsawbit):
* 9 Class: [FabThreadCutter](#cnc--fabthreadcutter):
* 10 Class: [FabVBit](#cnc--fabvbit):

## <a name="cnc--fabballendbit"></a>1 Class FabBallEndBit:

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


## <a name="cnc--fabbittemplate"></a>2 Class FabBitTemplate:

FabCNCShape: Base class for CNC tool bit templates.
Required Base Attributes:
* *Name* (str): The name of the tool template.
* *FileName* (pathlib.Path): The tool template file name (must have a suffix of`.fcstd` file)

Keyword Only Base Attributes:
* *Material: (Tuple[str, ...] = ()):
  The tool material as a tulple from generic to specific
  (e.g. `Material=("steel", "HSS", "Cobalt")`.)
* *ToolHolderHeight: (Union[None, str, float] = None):
  The distance from tool tip to the base of the tool holder.

### <a name="cnc----to-json"></a>2.1 `FabBitTemplate.`to_json():

FabBitTemplate.to_json(self, with_attributes: bool = True) -> str:

Return FabBitTemptlate as a JSON string.
Arguments:
* *with_attributes* (bool = True):
  If True include additional "non-FreeCAD" attributes; otherwise leave blank.

### <a name="cnc----write-json"></a>2.2 `FabBitTemplate.`write_json():

FabBitTemplate.write_json(self, file_path: pathlib.Path) -> None:

Write FabBitTemptlate out to a JSON file.


## <a name="cnc--fabbullnosebit"></a>3 Class FabBullNoseBit:

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


## <a name="cnc--fabchamferbit"></a>4 Class FabChamferBit:

FabDrillBit: An drill bit template.
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


## <a name="cnc--fabdrillbit"></a>5 Class FabDrillBit:

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


## <a name="cnc--fabendmillbit"></a>6 Class FabEndMillBit:

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


## <a name="cnc--fabprobebit"></a>7 Class FabProbeBit:

A touch off probe.
Required Base Attributes: *Name*, *FileName*.
Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

Required FreeCAD Parameter Attributes:
* *Diameter* (Union[str, float]): The end mill cutter diameter.
* *Length* (Union[str, float]): The total length of the end mill.
* *ShaftDiameter: (Union[str, float]): The shaft diameter.


## <a name="cnc--fabslittingsawbit"></a>8 Class FabSlittingSawBit:

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


## <a name="cnc--fabthreadcutter"></a>9 Class FabThreadCutter:

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


## <a name="cnc--fabvbit"></a>10 Class FabVBit:

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



