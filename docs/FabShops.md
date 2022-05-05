# FabShops: FabShop: Shop and associated Machines.
This is a package provides classes used to define what machines are available in a shop.

* FabShop: A collection of FabMachine's.
* FabMachine: A base class for all machines.
  * FabCNC: A CNC mill or router:
    * FabRouter: A CNC router.
    * FabMill: A CNC Mill.
  * FabCutter: A CNC Laser, Water Jet, or Plasma Cutter.  (TBD)
  * FabLathe: A CNC lathe.  (TBD)
  * Fab3DPrinter: A 3D printer.  (TBD)

## Table of Contents (alphabetical order):

* 1 Class: [FabCNC](#fabshops--fabcnc):
* 2 Class: [FabCNCMill](#fabshops--fabcncmill):
* 3 Class: [FabCNCRouter](#fabshops--fabcncrouter):
* 4 Class: [FabController](#fabshops--fabcontroller):
* 5 Class: [FabLocation](#fabshops--fablocation):
* 6 Class: [FabMachine](#fabshops--fabmachine):
* 7 Class: [FabShop](#fabshops--fabshop):
  * 7.1 [lookup()](#fabshops----lookup): Return the named FabMachine.
* 8 Class: [FabSpindle](#fabshops--fabspindle):
* 9 Class: [FabTable](#fabshops--fabtable):

## <a name="fabshops--fabcnc"></a>1 Class FabCNC:

Represents a CNC mill or router.
Attributes:
* *Name* (str): The CNC mill name.
* *Placement* (str): The placement in the shop.
* *WorkVolume* (Vector): The work volume DX/DY/DZ.
* *Table* (FabTable):
* *Spindle* (FabSpindle): The spindle description.
* *Controller* (FabController): The Controller used by the CNC machine.

Constructor:
* FabCNC("Name", "Position", WorkVolume, Spindle, Table, Controller)


## <a name="fabshops--fabcncmill"></a>2 Class FabCNCMill:

Represents a CNC mill.
Attributes:
* *Name* (str): The CNC mill name.
* *Placement* (str): The placement in the shop.
* *WorkVolume* (Vector): The work volume DX/DY/DZ.
* *Table* (FabTable):
* *Spindle* (FabSpindle): The spindle description.
* *Controller* (FabController): The Controller used by the CNC machine.
* *Kind* (str): Return the string "CNCMill".

Constructor:
* FabCNCMill("Name", "Placement", WorkVolume, Spindle, Table, Spindle, Controller)


## <a name="fabshops--fabcncrouter"></a>3 Class FabCNCRouter:

Represents a CNC Router.
Attributes:
* *Name* (str): The CNC mill name.
* *Position* (str): The position in the shop.
* *WorkVolume* (Vector): The work volume DX/DY/DZ.
* *Table* (FabTable):
* *Spindle* (FabSpindle): The spindle description.
* *Controller* (FabController): The Controller used by the CNC machine.
* *Kind* (str): Return the string "CNCRouter".

Constructor:
* FabCNCRouter("Name", "Position", WorkVolume, Spindle, Table, Spindle, Controller)


## <a name="fabshops--fabcontroller"></a>4 Class FabController:

Specifies a CNC controller.
Attributes:
* *Name* (str): The controller name.
* *PostProcessor* (str): The post processor to use.

Constructor:
* FabController("Name", PostProcessor)


## <a name="fabshops--fablocation"></a>5 Class FabLocation:

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


## <a name="fabshops--fabmachine"></a>6 Class FabMachine:

Base class for a FabShop machine.
Attributes:
* *Name* (str): The name of the  machines.
* *Placement* (str): The machine placement in the shop.
* *Kind* (str): The machine kind (supplied by sub-class).

Constructor:
* Fabmachine("Name", "Placement")


## <a name="fabshops--fabshop"></a>7 Class FabShop:

Describes Machines/Tool in a Shop.
Attributes:
* *Name* (str): The Shop Name.
* *Location* (FabLocation): The shop location.
* *Machines* (Tuple[FabMachine, ...]):
  The machines within the shop.  The machines must have unique names within the shop.

Constructor  :
* FabShop(Name="Name", Location=FabLocation(...), Machines=(...,))

### <a name="fabshops----lookup"></a>7.1 `FabShop.`lookup():

FabShop.lookup(self, machine_name: str) -> FabShops.FabMachine:

Return the named FabMachine.


## <a name="fabshops--fabspindle"></a>8 Class FabSpindle:

Represents a machine tool spindle.
Attributes:
* *Type* (str): Spindle Type (e.g. "R8", "Cat40", etc.)
* *Speed* (int): Maximum spindle speed in rotations per minute.
* *Reversible* (bool): True if spindle can be reversed.
* *FloodCooling* (bool): True if flood cooling is available.
* *MistCooling* (bool): True if mist coooling is available.

Constructor:
* FabSpindle("Type", Speed, Reversible, FloodCooling, MistCooling)


## <a name="fabshops--fabtable"></a>9 Class FabTable:

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



