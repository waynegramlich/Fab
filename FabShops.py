#!/usr/bin/env python3
"""FabShop: Shop and associated Machines.

This is a package provides classes used to define what machines are available in a shop.

* FabShop: A collection of FabMachine's.
* FabMachine: A base class for all machines.
  * FabCNC: A CNC mill or router:
    * FabRouter: A CNC router.
    * FabMill: A CNC Mill.
  * FabCutter: A CNC Laser, Water Jet, or Plasma Cutter.  (TBD)
  * FabLathe: A CNC lathe.  (TBD)
  * Fab3DPrinter: A 3D printer.  (TBD)

"""


from cadquery import Vector  # type: ignore


# <--------------------------------------- 100 characters ---------------------------------------> #

# Issues:
# * Turn off Legacy tools Path => Preferences => [] Enable Legacy Tools
# * Edit move the from line 11 to line 10 in .../Tools/Bit/45degree_chamfer.fctb to fix JSON error.
# * When setting path to library, be sure to include .../Tools/Library  (one level up does not work)

from typeguard import check_argument_types, check_type
from typing import List, Tuple
from dataclasses import dataclass


# FabAxis:
@dataclass(frozen=True)
class FabAxis(object):
    """FabAxis: Represents one axis of FabMachine.

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

    """

    Name: str
    Letter: str
    Linear: bool
    Range: float
    Speed: float
    Acceleration: float
    EndSensors: bool
    Brake: bool

    # FabAxis.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing the FabAxis."""
        check_type("FabAxis.Name", self.Name, str)
        check_type("FabAxis.Letter", self.Letter, str)
        check_type("FabAxis.Linear", self.Linear, bool)
        check_type("FabAxis.Range", self.Range, float)
        check_type("FabAxis.Speed", self.Speed, float)
        check_type("FabAxis.Acceleration", self.Acceleration, float)
        check_type("FabAxis.EndSensors", self.EndSensors, bool)
        check_type("FabAxis.Brake", self.Brake, bool)

    # FabAxis._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run FabAxis unit tests."""
        if tracing:
            print(f"{tracing}=>FabAxis._unit_tests()")

        linear_axis: FabAxis = FabAxis("X Axis", "X", True, 100.0, 10.0, 0.0, True, False)
        assert linear_axis.Name == "X Axis", linear_axis
        assert linear_axis.Letter == "X", linear_axis
        assert linear_axis.Linear, linear_axis
        assert linear_axis.Range == 100.00, linear_axis
        assert linear_axis.Speed == 10.00, linear_axis
        assert linear_axis.Acceleration == 0.00, linear_axis
        assert linear_axis.EndSensors, linear_axis
        assert not linear_axis.Brake, linear_axis

        if tracing:
            print(f"{tracing}<=FabAxis._unit_tests()")


# FabSpindle:
@dataclass(frozen=True)
class FabSpindle(object):
    """FabSpindle: Represents a machine tool spindle.

    Attributes:
    * *Type* (str): Spindle Type (e.g. "R8", "Cat40", etc.)
    * *Speed* (int): Maximum spindle speed in rotations per minute.
    * *Reversible* (bool): True if spindle can be reversed.
    * *FloodCooling* (bool): True if flood cooling is available.
    * *MistCooling* (bool): True if mist coooling is available.

    Constructor:
    * FabSpindle("Type", Speed, Reversible, FloodCooling, MistCooling)

    """

    Type: str
    Speed: int
    Reversible: bool
    FloodCooling: bool
    MistCooling: bool

    # FabSpindle.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing the FabSpindle."""
        check_type("FabSpindle.Type", self.Type, str)
        check_type("FabSpindle.Speed", self.Speed, int)
        check_type("FabSpindle.Reversible", self.Reversible, bool)
        check_type("FabSpindle.FloodCooling", self.FloodCooling, bool)
        check_type("FabSpindle.MistCooling", self.MistCooling, bool)

    # FabSpindle._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabSpindle unit tests."""
        if tracing:
            print(f"{tracing}=>FabSpindle._unit_tests()")
        spindle: FabSpindle = FabSpindle("R8", 5000, True, True, False)
        assert spindle.Type == "R8", spindle.Type
        assert spindle.Speed == 5000, spindle.Speed
        assert spindle.Reversible, spindle.Reversible
        assert spindle.FloodCooling, spindle.FloodCooling
        assert not spindle.MistCooling, spindle.MistCooling
        if tracing:
            print(f"{tracing}<=FabSpindle._unit_tests()")


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
    def _unit_tests(tracing: str = "") -> None:
        """Perform unit tests on FabTable."""
        if tracing:
            print(f"{tracing}=>FabTable._unit_tests()")
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
        if tracing:
            print(f"{tracing}=>FabTable._unit_tests()")


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

    # FabController.__post_init__():
    def __post_init__(self, tracing: str = "") -> None:
        """Finish initializing FabController."""
        if tracing:
            print(f"{tracing}=>FabController._unit_tests()")
        check_type("FabController.Name", self.Name, str)
        check_type("FabController.PostProcessor", self.PostProcessor, str)
        if tracing:
            print(f"{tracing}<=FabController._unit_tests()")

    # FabController._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabController Unit Tests."""
        if tracing:
            print(f"{tracing}=>FabController._unit_tests()")
        controller: FabController = FabController("MyMill", "linuxcnc")
        assert controller.Name == "MyMill", controller.Name
        assert controller.PostProcessor == "linuxcnc", controller.PostProcessor
        if tracing:
            print(f"{tracing}<=FabController._unit_tests()")


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
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabMachine unit tests."""
        if tracing:
            print(f"{tracing}=>FabMachine._unit_tests()")
        machine: FabMachine = FabMachine("TestMachine", "Test Placement")
        assert machine.Name == "TestMachine", machine.Name
        assert machine.Placement == "Test Placement", machine.Placement
        if tracing:
            print(f"{tracing}<=FabMachine._unit_tests()")


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

    Constructor:
    * FabCNC("Name", "Position", WorkVolume, Spindle, Table, Controller)

    """

    WorkVolume: Vector
    Spindle: FabSpindle
    Table: FabTable
    Controller: FabController

    # FabCNC.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabCNCMill."""
        super().__post_init__()
        check_type("FabCNC.WorkVolume", self.WorkVolume, Vector)
        check_type("FabCNC.Spindle", self.Spindle, FabSpindle)
        check_type("FabCNC.Table", self.Table, FabTable)
        check_type("FabCNC.Controller", self.Controller, FabController)

    # FabCNC._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabCNC unit tests."""
        if tracing:
            print(f"{tracing}=>FabCNC._unit_tests()")
        work_volume: Vector = Vector(100.0, 50.0, 30.0)
        spindle: FabSpindle = FabSpindle("R8", 5000, True, True, False)
        table: FabTable = FabTable("TestTable", 100.0, 50.0, 30.0, 4, 10.0, 5.0, 5.0, 10.0, 5.0)
        controller: FabController = FabController("MyMill", "linuxcnc")
        cnc: FabCNC = FabCNC("TestCNC", "placement", work_volume, spindle, table, controller)
        assert cnc.Name == "TestCNC"
        assert cnc.Placement == "placement"
        assert cnc.Spindle is spindle
        assert cnc.Table is table
        assert cnc.Controller is controller
        if tracing:
            print(f"{tracing}<=FabCNC._unit_tests()")


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

    Constructor:
    * FabCNCMill("Name", "Placement", WorkVolume, Spindle, Table, Spindle, Controller)

    """

    # FabCNCMill.__post_init__():
    def __post_init__(self) -> None:
        """Finish Initializing FabCNCMill."""
        super().__post_init__()

    # FabCNCMill.Kind():
    @property
    def Kind(self) -> str:
        """Return the FabCNCMill kind."""
        return "CNCMill"

    # FabCNCMill._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabCNCMill unit tests."""
        if tracing:
            print(f"{tracing}=>FabCNCMill._unit_tests()")
        work_volume: Vector = Vector(100.0, 50.0, 30.0)
        spindle: FabSpindle = FabSpindle("R8", 5000, True, True, False)
        controller: FabController = FabController("MyMill", "linuxcnc")
        table: FabTable = FabTable("TestTable", 100.0, 50.0, 30.0, 4, 10.0, 5.0, 5.0, 10.0, 5.0)
        cnc: FabCNCMill = FabCNCMill(
            "TestCNC", "placement", work_volume, spindle, table, controller)
        assert cnc.Name == "TestCNC", cnc.Name
        assert cnc.Placement == "placement", cnc.Placement
        assert cnc.Spindle is spindle, cnc.Spindle
        assert cnc.Controller is controller, cnc.Controller
        assert cnc.Kind == "CNCMill", cnc.Kind
        if tracing:
            print(f"{tracing}<=FabCNCMill._unit_tests()")


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

    Constructor:
    * FabCNCRouter("Name", "Position", WorkVolume, Spindle, Table, Spindle, Controller)

    """

    # FabCNCRouter.Kind():
    @property
    def Kind(self) -> str:
        """Return the FabCNCRouter kind."""
        return "CNCRouter"

    # FabCNCRouter._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabCNCRouter unit tests."""
        if tracing:
            print(f"{tracing}=>FabCNCRouter._unit_tests()")
        work_volume: Vector = Vector(100.0, 50.0, 30.0)
        spindle: FabSpindle = FabSpindle("R8", 5000, True, True, False)
        controller: FabController = FabController("MyMill", "linuxcnc")
        table: FabTable = FabTable("TestTable", 100.0, 50.0, 30.0, 0, 0.0, 0.0, 0.0, 0.0, 0.0)
        cnc: FabCNCRouter = FabCNCRouter(
            "TestCNC", "placement", work_volume, spindle, table, controller)
        assert cnc.Name == "TestCNC", cnc.Name
        assert cnc.Placement == "placement", cnc.Placement
        assert cnc.Spindle is spindle, cnc.Spindle
        assert cnc.Controller is controller, cnc.Controller
        assert cnc.Kind == "CNCRouter", cnc.Kind
        if tracing:
            print(f"{tracing}<=FabCNCRouter._unit_tests()")


# FabLocation:
@dataclass(frozen=True)
class FabLocation(object):
    """FabLocation: Location information for a shop.

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

    Name: str
    Location: FabLocation
    Machines: Tuple[FabMachine, ...]

    # FabShop:__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabShop."""
        check_type("FabShop.Name", self.Name, str)
        check_type("FabShop.Location", self.Location, FabLocation)
        check_type("FabShop.Machines", self.Machines, Tuple[FabMachine, ...])

    # FabShop.lookup():
    def lookup(self, machine_name: str) -> FabMachine:
        """Return the named FabMachine."""
        assert check_argument_types()
        machine: FabMachine
        for machine in self.Machines:
            if machine.Name == machine_name:
                return machine
        machine_names: List[str] = [machine.Name for machine in self.Machines]
        raise KeyError(
            f"Machine {machine_name} is not one of {sorted(machine_names)}")

    # FabShop._unit_tests()
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabShop unit tests."""
        if tracing:
            print(f"{tracing}=>FabShop._unit_tests()")
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
        if tracing:
            print(f"{tracing}<=FabShop._unit_tests()")


# Main program:
def main(tracing: str = "") -> None:
    """Run the unit test suites."""
    next_tracing: str = tracing + " " if tracing else ""
    if tracing:
        print("=>FabShops.main()")
    FabAxis._unit_tests(tracing=next_tracing)
    FabSpindle._unit_tests(tracing=next_tracing)
    FabTable._unit_tests(tracing=next_tracing)
    FabController._unit_tests(tracing=next_tracing)
    FabMachine._unit_tests(tracing=next_tracing)
    FabCNC._unit_tests(tracing=next_tracing)
    FabCNCMill._unit_tests(tracing=next_tracing)
    FabCNCRouter._unit_tests(tracing=next_tracing)
    FabShop._unit_tests(tracing=next_tracing)
    if tracing:
        print("=>FabShops.main()")


if __name__ == "__main__":
    main(tracing=" ")
