#!/usr/bin/env python3
"""FabShop: Shop and associated Machines.

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

"""


from cadquery import Vector  # type: ignore


# <--------------------------------------- 100 characters ---------------------------------------> #

# Issues:
# * Turn off Legacy tools Path => Preferrences => [] Enable Legacy Tools
# * Edit move the from line 11 to line 10 in .../Tools/Bit/45degree_chamfer.fctb to fix JSON error.
# * When setting path to library, be sure to include .../Tools/Library  (one level up does not work)

from typeguard import check_argument_types, check_type
from typing import Dict, Tuple
from dataclasses import dataclass, field


# FabSpindle:
@dataclass(frozen=True)
class FabSpindle(object):
    """FabSpindle: Represents a machine tool spindle.

    Attributes:
    * *Type* (str): Spindle Type (e.g. "R8", "Cat40", etc.)
    * *Speed* (int): Maximum spindle speed in rotations per minute.
    * *Reversable* (bool): True if spindle can be reversed.
    * *FloodCooling* (bool): True if flood cooling is available.
    * *MistCooling* (bool): True if mist coooling is available.

    Constructor:
    * FabSpindle("Type", Speed, Reversable, FloodCooling, MistCooling)

    """

    Type: str
    Speed: int
    Reversable: bool
    FloodCooling: bool
    MistCooling: bool

    # FabSpindle.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing the FabSpindle."""
        check_type("FabSpindle.Type", self.Type, str)
        check_type("FabSpindle.Speed", self.Speed, int)
        check_type("FabSpindle.Reversable", self.Reversable, bool)
        check_type("FabSpindle.FloodCooling", self.FloodCooling, bool)
        check_type("FabSpindle.MistCooling", self.MistCooling, bool)

    # FabSpindle._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Perform FabSpindle unit tests."""

        spindle: FabSpindle = FabSpindle("R8", 5000, True, True, False)
        assert spindle.Type == "R8", spindle.Type
        assert spindle.Speed == 5000, spindle.Speed
        assert spindle.Reversable, spindle.Reversable
        assert spindle.FloodCooling, spindle.FloodCooling
        assert not spindle.MistCooling, spindle.MistCooling


# FabTable:
@dataclass(frozen=True)
class FabTable(object):
    """FabTable: Represents a CNC table.

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

    """

    Name: str
    Length: float
    Width: float
    Height: float
    Slots: int
    SlotPitch: float
    SlotWidth: float
    SlotDepth: float
    KeywayWidth: float
    KeywayHeight: float

    # FabTable.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabTable."""
        check_type("FabTable.Name", self.Name, str)
        check_type("FabTable.Length", self.Length, float)
        check_type("FabTable.Width", self.Width, float)
        check_type("FabTable.Height", self.Height, float)
        check_type("FabTable.Slots", self.Slots, int)
        check_type("FabTable.SlotsPitch", self.SlotPitch, float)
        check_type("FabTable.SlotWidth", self.SlotWidth, float)
        check_type("FabTable.SlotDepth", self.SlotDepth, float)
        check_type("FabTable.KeywayWidth", self.KeywayWidth, float)
        check_type("FabTable.KeywayHeight", self.KeywayHeight, float)

    # FabTable._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Perform unit tests on FabTable."""
        table: FabTable = FabTable("TestTable", 100.0, 50.0, 30.0, 4, 10.0, 5.0, 5.0, 10.0, 5.0)
        assert table.Name == "TestTable", table.Name
        assert table.Length == 100.0, table.Length
        assert table.Width == 50.0, table.Width
        assert table.Height == 30.0, table.Height
        assert table.Slots == 4, table.Slots
        assert table.SlotWidth == 5.0, table.SlotWidth
        assert table.SlotDepth == 5.0, table.SlotDepth
        assert table.KeywayWidth == 10.0, table.KeywayWidth
        assert table.KeywayHeight == 5.0, table.KeywayHeight


# FabController:
@dataclass(frozen=True)
class FabController(object):
    """FabController: Specifies a CNC controller.

    Attributes:
    * *Name* (str): The controller name.
    * *PostProcessor* (str): The post processor to use.

    Constructor:
    * FabController("Name", PostProcessor)

    """

    Name: str
    PostProcessor: str

    # FabController.__post_process__():
    def __post_process__(self) -> None:
        """Finish initializing FabController."""
        check_type("FabController.Name", self.Name, str)
        check_type("FabController.PostProcessor", self.PostProcessor, str)

    # FabController._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Perform FabController Unit Tests."""
        controller: FabController = FabController("MyMill", "linuxcnc")
        assert controller.Name == "MyMill", controller.Name
        assert controller.PostProcessor == "linuxcnc", controller.PostProcessor


# FabMachine:
@dataclass(frozen=True)
class FabMachine(object):
    """FabMachine: Base class for a FabShop machine.

    Attributes:
    * *Name* (str): The name of the  machines.
    * *Placement* (str): The machine placement in the shop.
    * *Kind* (str): The machine kind (supplied by sub-class).

    Constructor:
    * Fabmachine("Name", "Placement")

    """

    Name: str
    Placement: str

    # FabMachine.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabMachine."""
        check_type("FabMachine.Name", self.Name, str)
        check_type("FabMachine.Placement", self.Placement, str)

    # FabMachine.Kind():
    @property
    def Kind(self) -> str:
        """Return the FabMachine kind."""
        raise NotImplementedError(f"{type(self)}.Kind() is not implemented.")

    # FabMachine._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Perform FabMachine unit tests."""
        machine: FabMachine = FabMachine("TestMachine", "Test Placement")
        assert machine.Name == "TestMachine", machine.Name
        assert machine.Placement == "Test Placement", machine.Placement


# FabCNC:
@dataclass(frozen=True)
class FabCNC(FabMachine):
    """FabCNC: Represents a CNC mill or router.

    Attributes:
    * *Name* (str): The CNC mill name.
    * *Placement* (str): The placement in the shop.
    * *WorkVolume* (Vector): The work volume DX/DY/DZ.
    * *Table* (FabTable):
    * *Spindle* (FabSpindle): The spindle description.
    * *Controller* (FabController): The Controller used by the CNC machine.

    Contstructor:
    * FabCNC("Name", "Position", WorkVolume, Spindle, Table, Controller)

    """

    _WorkVolume: Vector
    _Spindle: FabSpindle
    _Table: FabTable
    _Controller: FabController

    # FabCNC.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabCNCMill."""
        super().__post_init__()
        check_type("FabCNC.WorkVolume", self._WorkVolume, Vector)
        check_type("FabCNC.Spindle", self._Spindle, FabSpindle)
        check_type("FabCNC.Table", self._Table, FabTable)
        check_type("FabCNC.Controller", self._Controller, FabController)


# FabCNCMill:
@dataclass(frozen=True)
class FabCNCMill(FabCNC):
    """FabCNCMill: Represents a CNC mill.

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

    """

    # FabCNCMill.__post_init__():
    def __post_init__(self) -> None:
        """Finish Initializing FabCNCMill."""
        super().__post_init__()

    # FabCNCMill.Kind():
    @property
    def Kind(self) -> str:
        """Return the FabCNCMill kind."""
        return "CNC_Mill"


# FabCNCRouter:
@dataclass(frozen=True)
class FabCNCRouter(FabCNC):
    """FabCNCRouter: Represents a CNC Router.

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

    """

    # FabCNCRouter.Kind():
    @property
    def Kind(self) -> str:
        """Return the FabCNCRouter kind."""
        return "CNCRouter"


# FabLocation:
@dataclass(frozen=True)
class FabLocation(object):
    """FabLocation: Location information for a shop.

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

    """

    CountryCode: str = ""
    StateProvince: str = ""
    County: str = ""
    City: str = ""
    StreetAddress: str = ""
    Unit: str = ""
    ZipCode: str = ""
    Latitude: str = ""
    Longitude: str = ""
    PhoneNumber: str = ""
    URL: str = ""


# FabShop:
@dataclass
class FabShop(object):
    """FabShop: Describes Machines/Tool in a Shop.

    Attributes:
    * *Name* (str): The Shop Name.
    * *Location* (FabLocation): The shop location.
    * *Machines* (Tuple[FabMachine, ...]):
      The machines within the shop.  The machines must have unique names within the shop.

    Constructor  :
    * FabShop(Name="Name", Location=FabLocation(...), Machines=(...,))

    """

    _Name: str
    _Location: FabLocation
    _Machines: Tuple[FabMachine, ...]
    _MachinesTable: Dict[str, FabMachine] = field(init=False, repr=False)

    # FabShop:__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabShop."""
        check_type("FabShop.Name", self._Name, str)
        check_type("FabShop.Location", self._Location, FabLocation)
        check_type("FabShop.Machines", self._Machines, Tuple[FabMachine, ...])
        machines_table: Dict[str, FabMachine] = {}
        machine: FabMachine
        for machine in self._Machines:
            machine_name: str = machine.Name
            if machine_name in machines_table:
                raise ValueError("Machine {machine_name} occurs more than once.")
            machines_table[machine_name] = machine
        self._MachinesTable = machines_table

    # FabShop.Name():
    @property
    def Name(self) -> str:
        """Return FabShop name."""
        return self._Name

    # FabShop.Location():
    @property
    def Location(self) -> FabLocation:
        """Return FabShop location."""
        return self._Location

    # FabShop.Machines():
    @property
    def Machines(self) -> Tuple[FabMachine, ...]:
        """Return FabShop machines."""
        return self._Machines

    # FabShop.lookup():
    def lookup(self, machine_name: str) -> FabMachine:
        """Return the named FabMachine."""
        assert check_argument_types()
        if machine_name not in self._MachinesTable:
            raise KeyError(
                f"Machine {machine_name} is not one of {sorted(self._MachinesTable.keys())}")
        return self._MachinesTable[machine_name]

    # FabShop._unit_tests()
    @staticmethod
    def _unit_tests() -> None:
        """Perform FabShop unit tests."""
        name: str = "MyShop"
        location: FabLocation = FabLocation(
            CountryCode="US", StateProvince="California", City="Sunnyvale", ZipCode="94086")
        placement: str = "somewhere in shop"
        table: FabTable = FabTable("TestTable", 100.0, 50.0, 30.0, 4, 10.0, 5.0, 5.0, 10.0, 5.0)
        work_volume: Vector = Vector(100.0, 50.0, 40.0)
        spindle: FabSpindle = FabSpindle("R8", 5000, True, True, False)
        controller: FabController = FabController("MyMill", "linuxcnc")
        cnc_mill: FabCNCMill = FabCNCMill(
            "MyCNCMill", placement, work_volume, spindle, table, controller)
        machines: Tuple[FabMachine, ...] = (cnc_mill,)
        shop: FabShop = FabShop("MyShop", location, machines)
        assert shop.Name == name, shop.Name
        assert shop.Location == location, shop.Location
        assert shop.Machines == machines

        # Test lookup():
        try:
            shop.lookup("BadMachine")
            assert False
        except KeyError as key_error:
            want: str = "\"Machine BadMachine is not one of ['MyCNCMill']\""
            got: str = str(key_error)
            assert want == got, f"\n{want} !=\n{got}"
        assert shop.lookup("MyCNCMill") is cnc_mill


# Main program:
def main() -> None:
    FabSpindle._unit_tests()
    FabTable._unit_tests()
    FabController._unit_tests()
    FabMachine._unit_tests()
    FabCNC._unit_tests()
    FabShop._unit_tests()


if __name__ == "__main__":
    main()
