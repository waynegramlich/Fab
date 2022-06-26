# FabShops: FabShop: Shop and associated Machines.
This is a package provides classes used to define what machines are available in a shop.

* FabShops: A collection of FabShops's.
* FabShop: A collection of FabMachine's.
* FabMachine: A base class for all machines.
  * FabCNC: A CNC mill or router:
    * FabRouter: A CNC router.
    * FabMill: A CNC Mill.
  * FabCutter: A CNC Laser, Water Jet, or Plasma Cutter.  (TBD)
  * FabLathe: A CNC lathe.  (TBD)
  * Fab3DPrinter: A 3D printer.  (TBD)

## Table of Contents (alphabetical order):

* 1 Class: [FabAxis](#fabshops--fabaxis):
* 2 Class: [FabCNC](#fabshops--fabcnc):
* 3 Class: [FabCNCMill](#fabshops--fabcncmill):
* 4 Class: [FabCNCRouter](#fabshops--fabcncrouter):
* 5 Class: [FabController](#fabshops--fabcontroller):
* 6 Class: [FabLocation](#fabshops--fablocation):
* 7 Class: [FabMachine](#fabshops--fabmachine):
* 8 Class: [FabShop](#fabshops--fabshop):
  * 8.1 [lookup()](#fabshops----lookup): Return the named FabMachine.
* 9 Class: [FabShops](#fabshops--fabshops):
* 10 Class: [FabSpindle](#fabshops--fabspindle):
* 11 Class: [FabTable](#fabshops--fabtable):
* 12 Class: [Fab_ShopBit](#fabshops--fab-shopbit):

## <a name="fabshops--fabaxis"></a>1 Class FabAxis:

Represents one axis of FabMachine.
Attributes:
* Name (*str*): The long name for the axis.
* Letter (*str*): The letter name for the axis (usually 'X', 'Y', 'Z', or 'A')
* Linear (*bool*): True for a linear axis and False for a rotational axis.
* Range (*float*):
  The range that axis can span in millimeters (Linear=True) or in degrees (Linear=False).
  If there are no restrictions for the rotational axis, set to 0.0.
* Speed (*float*):
  The maximum speed for the axis in mm/sec (Linear=True) or degrees/sec (Linear=False).
* Acceleration (*float*):
  The maximum acceleration for axis in mm/sec^2 (Linear=True) or degrees/sec^2 (Linear=False).
  Set to 0.0 if maximum acceleration is not known.
* EndSensors (*bool): True if the axis has limit sensors for both ends of the the travel.
* Brake (*bool*):
  True if there is a brake to lock the axis and False otherwise.
  Typically this is only available for rotational axes.

Constructor:
* FabAxis("Name", "Letter", Linear, Range, Speed, EndSensors, Brake)


## <a name="fabshops--fabcnc"></a>2 Class FabCNC:

Represents a CNC mill or router.
Attributes:
* *Name* (str): The CNC mill name.
* *Placement* (str): The placement in the shop.
* *Axes* (Tuple[FabAxis, ...]): The various control axes (usually, X/Y/Z).
* *Table* (FabTable):
* *Spindle* (FabSpindle): The spindle description.
* *Controller* (FabController): The Controller used by the CNC machine.
* *Library* (FabLibrary): The library containing all of the tools.

Constructor:
* FabCNC("Name", "Placement", Axes, Table, Spindle, Controller)


## <a name="fabshops--fabcncmill"></a>3 Class FabCNCMill:

Represents a CNC mill.
Attributes:
* *Name* (str): The CNC mill name.
* *Placement* (str): The placement in the shop.
* *Axes* (Tuple[FabAxis, ...]): The mill axes.
* *Table* (FabTable):
* *Spindle* (FabSpindle): The spindle description.
* *Controller* (FabController): The Controller used by the CNC machine.
* *Library* (FabLibrary): The tool library to use.
* *Kind* (str): A property that returns the string "CNCMill".

Constructor:
* FabCNCMill("Name", "Placement", WorkVolume, Spindle, Table, Spindle, Controller, Library)


## <a name="fabshops--fabcncrouter"></a>4 Class FabCNCRouter:

Represents a CNC Router.
Attributes:
* *Name* (str): The CNC mill name.
* *Position* (str): The position in the shop.
* *Axes* (Tuple[FabAxis, ...]): The axis descriptions.
* *Table* (FabTable): The table description.
* *Spindle* (FabSpindle): The spindle description.
* *Controller* (FabController): The Controller used by the CNC machine.
* *Kind* (str): Return the string "CNCRouter".

Constructor:
* FabCNCRouter("Name", "Position", Axes, Table, Spindle, Controller)


## <a name="fabshops--fabcontroller"></a>5 Class FabController:

Specifies a CNC controller.
Attributes:
* *Name* (str): The controller name.
* *PostProcessor* (str): The post processor to use.

Constructor:
* FabController("Name", PostProcessor)


## <a name="fabshops--fablocation"></a>6 Class FabLocation:

Location information for a shop.
The shop can be located with as much or as little specificity that the shop owner chooses.
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
* *StreetAddress1* (str):
  The first line of the shop street address. (Default: "")
* *StreetAddress2* (str):
  The second line of the shop street address. (Default: "")
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


## <a name="fabshops--fabmachine"></a>7 Class FabMachine:

Base class for a FabShop machine.
Attributes:
* *Name* (str): The name of the  machines.
* *Placement* (str): The machine placement in the shop.
* *Library* (FabLibrary): The library of tools available.
* *Kind* (str): The machine kind (supplied by sub-class as a property).

Constructor:
* Fabmachine("Name", "Placement")


## <a name="fabshops--fabshop"></a>8 Class FabShop:

Describes Machines/Tool in a Shop.
Attributes:
* *Name* (str): The Shop Name.
* *Location* (FabLocation): The shop location.
* *Machines* (Tuple[FabMachine, ...]):
  The machines within the shop.  The machines must have unique names within the shop.

Constructor  :
* FabShop(Name="Name", Location=FabLocation(...), Machines=(...,))

### <a name="fabshops----lookup"></a>8.1 `FabShop.`lookup():

FabShop.lookup(self, machine_name: str) -> FabShops.FabMachine:

Return the named FabMachine.


## <a name="fabshops--fabshops"></a>9 Class FabShops:

A collection of FabShop's.
This class collects all available FabShop's together.
It precomputes the Fab_ShopBit's that are available for each operation type.

Attributes:
* *Shops* (Tuple[FabShop, ...]: All available FabShop's.
* *Machines* (Tuple[Tuple[FabShop, FabMachine, ...]: A tuple of all (FabShop, FabMachine) pairs.
* *AllShopBits: (Tuple[Fab_ShopBit, ...]): A tuple of a Fab_ShopBit's.
* *ContourShopBits: (Tuple[Fab_ShopBit, ...]):
  A tuple of Fab_ShopBit's suitable for exterior contour contouring.
* *CounterSinkShopBits: (Tuple[TFab_ShopBit, ...):
  A tuple of Fab_ShopBit's suitable for countersinking.
* *DrillShipBits (Tuple[Fab_ShopBit, ...]):
  A tuple of Fab_ShopBit's suitable for exterior drilling.
* *PocketShopBits: (Tuple[Fab_ShopBit, ...]): A tuple of Fab_ShopBit's suitable for pocketing.

Constructor:
* FabShops(Shops)


## <a name="fabshops--fabspindle"></a>10 Class FabSpindle:

Represents a machine tool spindle.
Attributes:
* *Type* (str): Spindle Type (e.g. "R8", "Cat40", etc.)
* *Speed* (int): Maximum spindle speed in rotations per minute.
* *Reversible* (bool): True if spindle can be reversed.
* *FloodCooling* (bool): True if flood cooling is available.
* *MistCooling* (bool): True if mist coooling is available.

Constructor:
* FabSpindle("Type", Speed, Reversible, FloodCooling, MistCooling)


## <a name="fabshops--fabtable"></a>11 Class FabTable:

Represents a CNC table.
Attributes:
* *Name* (str): The table name.
* *Length* (float): The overall table length in millimeters.
* *Width* (float): The overall table width in millimieters.
* *Height* (float): The overall table Height in millimeters.
* *Slots* (int): The number of T slots.
* *SlotPitch (float): The pitch between slot center-lines.
* *SlotWidth* (float): The top slot width in millimeters.
* *SlotDepth* (float): The overall slot depth from top to keyway bottom in millimeters.
* *KeywayWidth* (float): The keyway width in millimeters.
* *KeywayHeight* (float): The keyway height in millimeters.

Constructor:
*  FabTable("Name", Length, Width, Height, Slots,
   SlotWidth, SlotDepth, KeywayWidth, KeywayHeight)


## <a name="fabshops--fab-shopbit"></a>12 Class Fab_ShopBit:


Fab_ShopBit: Represents a tool bit for a FabMachine in a FabShop.

Fab_ShopBit is a sub-class of FabBit and it is used to describe a FabBit that can be used
given operation -- pocket, drill, chamfer, face mill, etc.  Fab_ShopBit's are assembled
into operation specific lists that are subsequently searched to find ones that match.

When a FabSolid is produced using a CNC machine (i.e. a FabCNCMill) process, it starts with
some stock material which is machined down with one or more mount operations.  Conceptually,
a FabSolid can be mounted onto any CNC machine that is capable of performing all requested
operations.  Since moving a part between machines is annoying (particularly if the machines
are in different shops), the Fab system attempts find a single CNC machine that can perform
all of the mounts for a given solid.  However, sometimes that is not possible.  A contrived
example is one CNC machine having the only 25mm drill bit and another having the only 8mm
drill bit.  Once the Fab system has identified a minimal set of CNC machines that can be
used to fabricate the FabSolid, it will generate G-code files for those machines.
For example, if a FabSolid has 5 mounts (arbitrarily named A, B, C, and D), where machine 1
can perform mounts [A, B, D] and machine 2 can perform mounts [A, C, D], the Fab system will
produce G-code files 1A, 2A, 1B, 2C, 1D, and 2D.  The user will probably use 1A, 1B, 2C and 2D.
Whenever possible, the Fab system will attempt to minimize moving a FabSolid between different
FabShop's, since FabShop's may be located a distance from one another.

Attributes:
* *BitPriorty* (float):
  This specifies the preferred priority for selecting a bit.
  This is typically a negative number since more negative number sorts first.
* *Shop* (FabShop): The shop that tool bit.
* *ShopIndex* (int): The index of the FabShop in FabShops.
  This is used to distinguish
* *Machine* (FabMachine): The machine that can use the tool bit.
* *MachineIndex* (int): The machine precedence order (lower values sort first.)
* *Bit*: (FabBit): The machine tool bit.
* *ToolNumber*: (int): The tool bit number to use in generated G-Code.

Constructor:
* Fab_ShopBit(BitPriority, Shop, ShopIndex, Machine, MachineIndex, Bit, Number)



