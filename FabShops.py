#!/usr/bin/env python3
"""FabShop: Shop and associated Machines.

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

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

# Issues:
# * Turn off Legacy tools Path => Preferences => [] Enable Legacy Tools
# * Edit move the from line 11 to line 10 in .../Tools/Bit/45degree_chamfer.fctb to fix JSON error.
# * When setting path to library, be sure to include .../Tools/Library  (one level up does not work)

from dataclasses import dataclass, field
from pathlib import Path as PathFile
from typeguard import check_argument_types, check_type
from typing import Dict, List, Optional, Tuple
from FabTools import FabBit, FabLibrary, FabLibraries, FabTooling, FabToolingFactory

# Useful reference:
# * [MachiningDoctor](https://www.machiningdoctor.com/calculators/chip-load-calculator/):
#   Describes the formulas to use for chip load, speed, and feed calculations.

from FabToolBits import FabEndMillBit


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

    # FabAxis.example():
    @staticmethod
    def example() -> "FabAxis":
        """Return an example FabAxis."""
        return FabAxis(
            Name="X Axis", Letter="X", Linear=True, Range=100.0, Speed=10.0,
            Acceleration=0.0, EndSensors=True, Brake=False
        )

    # FabAxis._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run FabAxis unit tests."""
        if tracing:
            print(f"{tracing}=>FabAxis._unit_tests()")

        linear_axis: FabAxis = FabAxis.example()
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

    # FabSpindle.example()
    @staticmethod
    def example() -> "FabSpindle":
        """Return an example FabSpindle"""
        return FabSpindle(
            Type="R8", Speed=5000, Reversible=True, FloodCooling=True, MistCooling=False)

    # FabSpindle._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabSpindle unit tests."""
        if tracing:
            print(f"{tracing}=>FabSpindle._unit_tests()")
        spindle: FabSpindle = FabSpindle.example()
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
    * *SlotPitch (float): The pitch between slot center-lines.
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

    # FabTable.example():
    @staticmethod
    def example() -> "FabTable":
        """Return an example FabTable."""
        return FabTable(
            Name="TestTable", Length=100.0, Width=50.0, Height=30.0,
            Slots=4, SlotPitch=10.0, SlotWidth=5.0, SlotDepth=5.0,
            KeywayWidth=10.0, KeywayHeight=5.0
        )

    # FabTable._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform unit tests on FabTable."""
        if tracing:
            print(f"{tracing}=>FabTable._unit_tests()")
        table: FabTable = FabTable.example()
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

    # FabControler.example():
    @staticmethod
    def example() -> "FabController":
        """Return example FabController."""
        return FabController(Name="MyMill", PostProcessor="linuxcnc")

    # FabController._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabController Unit Tests."""
        if tracing:
            print(f"{tracing}=>FabController._unit_tests()")
        controller: FabController = FabController.example()
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
    * *Library* (FabLibrary): The library of tools available.
    * *Kind* (str): The machine kind (supplied by sub-class as a property).

    Constructor:
    * Fabmachine("Name", "Placement")

    """

    Name: str
    Placement: str
    Library: FabLibrary

    # FabMachine.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabMachine."""
        check_type("FabMachine.Name", self.Name, str)
        check_type("FabMachine.Placement", self.Placement, str)

    # FabMachine.Kind():
    @property
    def Kind(self) -> str:
        """Return the FabMachine kind."""
        raise NotImplementedError(
            f"{type(self)}.Kind() is not implemented.")  # pragma: no unit test

    # FabMachine._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabMachine unit tests."""
        if tracing:
            print(f"{tracing}=>FabMachine._unit_tests()")
        tools_directory: PathFile = PathFile(__file__).parent / "Tools"
        tooling: FabTooling = FabTooling.read(tools_directory)
        libraries: FabLibraries = tooling.Libraries
        library: FabLibrary = libraries.Libraries[0]
        machine: FabMachine = FabMachine("TestMachine", "Test Placement", library)
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
    * *Axes* (Tuple[FabAxis, ...]): The various control axes (usually, X/Y/Z).
    * *Table* (FabTable):
    * *Spindle* (FabSpindle): The spindle description.
    * *Controller* (FabController): The Controller used by the CNC machine.
    * *Library* (FabLibrary): The library containing all of the tools.

    Constructor:
    * FabCNC("Name", "Placement", Axes, Table, Spindle, Controller)

    """

    Axes: Tuple[FabAxis, ...]
    Table: FabTable
    Spindle: FabSpindle
    Controller: FabController
    Library: FabLibrary

    # FabCNC.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabCNC."""
        super().__post_init__()
        check_type("FabCNC.WorkVolume", self.Axes, Tuple[FabAxis, ...])
        check_type("FabCNC.Table", self.Table, FabTable)
        check_type("FabCNC.Spindle", self.Spindle, FabSpindle)
        check_type("FabCNC.Controller", self.Controller, FabController)
        check_type("FabCNC.Library", self.Library, FabLibrary)

    # FabCNC._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabCNC unit tests."""
        if tracing:
            print(f"{tracing}=>FabCNC._unit_tests()")
        x_axis: FabAxis = FabAxis(
            Name="X Axis", Letter="X", Linear=True, Range=100.0, Speed=10.0, Acceleration=0.0,
            EndSensors=True, Brake=False)
        y_axis: FabAxis = FabAxis(
            Name="Y Axis", Letter="Y", Linear=True, Range=100.0, Speed=10.0, Acceleration=0.0,
            EndSensors=True, Brake=False)
        z_axis: FabAxis = FabAxis(
            Name="Z Axis", Letter="Z", Linear=True, Range=100.0, Speed=10.0, Acceleration=0.0,
            EndSensors=True, Brake=False)
        axes: Tuple[FabAxis, ...] = (x_axis, y_axis, z_axis)
        spindle: FabSpindle = FabSpindle(
            Type="R8", Speed=5000, Reversible=True, FloodCooling=True, MistCooling=False)
        table: FabTable = FabTable("TestTable", 100.0, 50.0, 30.0, 4, 10.0, 5.0, 5.0, 10.0, 5.0)
        controller: FabController = FabController("MyMill", "linuxcnc")

        tools_directory: PathFile = PathFile(__file__).parent / "Tools"
        tooling_factory: FabToolingFactory = FabToolingFactory("TestTooling", tools_directory)
        tooling_factory.createExampleTools()
        library: FabLibrary = tooling_factory.getLibrary("TestLibrary", tools_directory)
        cnc: FabCNC = FabCNC(Name="TestCNC", Placement="placement", Axes=axes, Table=table,
                             Spindle=spindle, Controller=controller, Library=library)
        assert cnc.Name == "TestCNC"
        assert cnc.Placement == "placement"
        assert cnc.Axes is axes
        assert cnc.Table is table
        assert cnc.Spindle is spindle
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
    * *Axes* (Tuple[FabAxis, ...]): The mill axes.
    * *Table* (FabTable):
    * *Spindle* (FabSpindle): The spindle description.
    * *Controller* (FabController): The Controller used by the CNC machine.
    * *Library* (FabLibrary): The tool library to use.
    * *Kind* (str): A property that returns the string "CNCMill".

    Constructor:
    * FabCNCMill("Name", "Placement", WorkVolume, Spindle, Table, Spindle, Controller, Library)

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

    # FabCNCMill.getExample():
    @staticmethod
    def getExample() -> "FabCNCMill":
        """Return an example FabCNCMill."""
        x_axis: FabAxis = FabAxis(
            Name="X Axis", Letter="X", Linear=True, Range=100.0, Speed=10.0, Acceleration=0.0,
            EndSensors=True, Brake=False)
        y_axis: FabAxis = FabAxis(
            Name="Y Axis", Letter="Y", Linear=True, Range=100.0, Speed=10.0, Acceleration=0.0,
            EndSensors=True, Brake=False)
        z_axis: FabAxis = FabAxis(
            Name="Z Axis", Letter="Z", Linear=True, Range=100.0, Speed=10.0, Acceleration=0.0,
            EndSensors=True, Brake=False)
        axes: Tuple[FabAxis, ...] = (x_axis, y_axis, z_axis)
        controller: FabController = FabController.example()
        spindle: FabSpindle = FabSpindle.example()
        table: FabTable = FabTable.example()
        tools_directory: PathFile = PathFile(__file__).parent / "Tools"
        tooling_factory: FabToolingFactory = FabToolingFactory("", tools_directory)
        tooling_factory.createExampleTools()
        library: FabLibrary = tooling_factory.getLibrary("Library", tools_directory)
        cnc_mill: FabCNCMill = FabCNCMill(
            Name="TestCNC", Placement="placement", Axes=axes, Table=table,
            Spindle=spindle, Controller=controller, Library=library
        )
        return cnc_mill

    # FabCNCMill._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabCNCMill unit tests."""
        if tracing:
            print(f"{tracing}=>FabCNCMill._unit_tests()")
        cnc_mill: FabCNCMill = FabCNCMill.getExample()
        assert cnc_mill.Name == "TestCNC", cnc_mill.Name
        assert cnc_mill.Placement == "placement", cnc_mill.Placement
        assert isinstance(cnc_mill.Spindle, FabSpindle), cnc_mill.Spindle
        assert isinstance(cnc_mill.Controller, FabController), cnc_mill.Controller
        assert cnc_mill.Kind == "CNCMill", cnc_mill.Kind
        if tracing:
            print(f"{tracing}<=FabCNCMill._unit_tests()")


# FabCNCRouter:
@dataclass(frozen=True)
class FabCNCRouter(FabCNC):
    """FabCNCRouter: Represents a CNC Router.

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

    """

    # FabCNCRouter.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabCNCRouter."""
        super().__post_init__()

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
        x_axis: FabAxis = FabAxis(
            Name="X Axis", Letter="X", Linear=True, Range=100.0, Speed=10.0, Acceleration=0.0,
            EndSensors=True, Brake=False)
        y_axis: FabAxis = FabAxis(
            Name="Y Axis", Letter="Y", Linear=True, Range=100.0, Speed=10.0, Acceleration=0.0,
            EndSensors=True, Brake=False)
        z_axis: FabAxis = FabAxis(
            Name="Z Axis", Letter="Z", Linear=True, Range=100.0, Speed=10.0, Acceleration=0.0,
            EndSensors=True, Brake=False)
        axes: Tuple[FabAxis, ...] = (x_axis, y_axis, z_axis)
        spindle: FabSpindle = FabSpindle(
            Type="R8", Speed=5000, Reversible=True, FloodCooling=True, MistCooling=False)
        controller: FabController = FabController(Name="MyMill", PostProcessor="linuxcnc")
        table: FabTable = FabTable(
            Name="TestTable", Length=100.0, Width=50.0, Height=30.0, Slots=5, SlotPitch=20.0,
            SlotWidth=5.0, SlotDepth=60.0, KeywayWidth=15.0, KeywayHeight=10.0)
        tools_directory: PathFile = PathFile(__file__).parent / "Tools"
        tooling_factory: FabToolingFactory = FabToolingFactory("TestTooling", tools_directory)
        tooling_factory.createExampleTools()
        library: FabLibrary = tooling_factory.getLibrary("TestLibrary", tools_directory)
        cnc: FabCNCRouter = FabCNCRouter(
            Name="TestCNC", Placement="placement", Axes=axes, Spindle=spindle, Table=table,
            Controller=controller, Library=library
        )
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

    """

    CountryCode: str = ""
    StateProvince: str = ""
    County: str = ""
    City: str = ""
    StreetAddress1: str = ""
    StreetAddress2: str = ""
    Unit: str = ""
    ZipCode: str = ""
    Latitude: str = ""
    Longitude: str = ""
    PhoneNumber: str = ""
    URL: str = ""

    # FabLocation.__post_init__():
    def __post_init__(self) -> None:
        """Finish initlializing FabLocation."""
        check_type("FabLocation.CountryCode", self.CountryCode, str)
        check_type("FabLocation.StateProvince", self.StateProvince, str)
        check_type("FabLocation.County", self.County, str)
        check_type("FabLocation.City", self.City, str)
        check_type("FabLocation.StreetAddress1", self.StreetAddress1, str)
        check_type("FabLocation.StreetAddress2", self.StreetAddress2, str)
        check_type("FabLocation.Unit", self.Unit, str)
        check_type("FabLocation.ZipCode", self.ZipCode, str)
        check_type("FabLocation.Latitude", self.Latitude, str)
        check_type("FabLocation.Longitude", self.Longitude, str)
        check_type("FabLocation.PhoneNumber", self.PhoneNumber, str)
        check_type("FabLocation.URL", self.URL, str)

    # FabLocation.getExample():
    @staticmethod
    def getExample() -> "FabLocation":
        """Return an example FabLocation."""
        location: FabLocation = FabLocation(
            CountryCode="US",
            StateProvince="CA",
            County="Santa Clara",
            City="Sunnyvale",
            StreetAddress1="Sunnyvale Police Public Safety Services",
            StreetAddress2="700 All American Way",
            Unit="",
            ZipCode="94086",
            Latitude="37.37066",
            Longitude="-122.04002",
            PhoneNumber="1-408-730-7100",
            URL="https://www.townofsunnyvale.org/81/Police"
        )
        return location

    # FabLocation._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run FabLocation unit tests."""
        if tracing:
            print(f"{tracing}=>FabLocation._unit__tests()")
        location: FabLocation = FabLocation.getExample()
        assert location.CountryCode == "US"
        assert location.StateProvince == "CA"
        assert location.County == "Santa Clara"
        assert location.City == "Sunnyvale"
        assert location.StreetAddress1 == "Sunnyvale Police Public Safety Services"
        assert location.StreetAddress2 == "700 All American Way"
        assert location.Unit == ""
        assert location.ZipCode == "94086"
        assert location.Latitude == "37.37066"
        assert location.Longitude == "-122.04002"
        assert location.PhoneNumber == "1-408-730-7100"
        assert location.URL == "https://www.townofsunnyvale.org/81/Police"
        if tracing:
            print(f"{tracing}<=FabLocation._unit__tests()")


# FabShop:
@dataclass(frozen=True)
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

    # FabShop.getExample():
    @staticmethod
    def getExample() -> "FabShop":
        """Return an example FabShop."""
        cnc_mill: FabCNCMill = FabCNCMill.getExample()
        location: FabLocation = FabLocation.getExample()
        machines: Tuple[FabMachine, ...] = (cnc_mill,)
        shop: FabShop = FabShop(Name="MyShop", Location=location, Machines=machines)
        return shop

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

        shop: FabShop = FabShop.getExample()
        location: FabLocation = FabLocation.getExample()
        cnc_mill: FabCNCMill = FabCNCMill.getExample()
        assert shop.Name == "MyShop", shop.Name
        assert shop.Location == location, shop.Location
        assert shop.Machines == (cnc_mill,), shop.Machines

        # Test lookup():
        try:
            shop.lookup("BadMachine")
            assert False
        except KeyError as key_error:
            want: str = "\"Machine BadMachine is not one of ['TestCNC']\""
            got: str = str(key_error)
            assert want == got, f"\n{want} !=\n{got}"
        assert shop.lookup("TestCNC") == cnc_mill
        if tracing:
            print(f"{tracing}<=FabShop._unit_tests()")


# Fab_ShopBit:
@dataclass(frozen=True, order=True)
class Fab_ShopBit(object):
    """
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
    * *Number*: (int): The tool bit number to use in generated G-Code.

    Constructor:
    * Fab_ShopBit(BitPriority, Shop, ShopIndex, Machine, MachineIndex, Bit, Number)

    """

    BitPriority: float
    Shop: FabShop = field(compare=False, repr=False)
    ShopIndex: int
    Machine: FabMachine = field(compare=False, repr=False)
    MachineIndex: int
    Bit: FabBit = field(compare=False, repr=False)
    Number: int

    # Fab_ShopBit.__post_init__():
    def __post_init__(self) -> None:
        """ Finish initializing a Fab_Shopbit."""
        check_type("Fab_ShopBit.BitPriority", self.BitPriority, float)
        check_type("Fab_ShopBit.Shop", self.Shop, FabShop)
        check_type("Fab_ShopBit.ShopIndex", self.ShopIndex, int)
        check_type("Fab_ShopBit.Machine", self.Machine, FabMachine)
        check_type("Fab_ShopBit.MachineIndex", self.MachineIndex, int)
        check_type("Fab_ShopBit.Bit", self.Bit, FabBit)
        check_type("Fab_ShopBit.Number", self.Number, int)

    # Fab_ShopBit.getExample():
    @staticmethod
    def getExample() -> "Fab_ShopBit":
        """Return an example Fab_ShopBit."""
        shop: FabShop = FabShop.getExample()
        end_mill_bit: FabEndMillBit = FabEndMillBit.getExample()
        cnc_machine: FabCNCMill = FabCNCMill.getExample()
        shop_bit: Fab_ShopBit = Fab_ShopBit(
            BitPriority=-123.456, Shop=shop, ShopIndex=0,
            Machine=cnc_machine, MachineIndex=0, Bit=end_mill_bit, Number=1)
        return shop_bit

    # Fab_ShopBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run Fab_ShopBit unit tests."""
        if tracing:
            print(f"{tracing}=>Fab_ShopBit._unit_tests()")

        shop_bit: Fab_ShopBit = Fab_ShopBit.getExample()
        assert shop_bit.BitPriority == -123.456
        assert shop_bit.Shop == FabShop.getExample()
        assert shop_bit.ShopIndex == 0
        assert shop_bit.Machine == FabCNCMill.getExample()
        assert shop_bit.MachineIndex == 0
        assert shop_bit.Bit == FabEndMillBit.getExample()
        assert shop_bit.Number == 1

        if tracing:
            print(f"{tracing}<=Fab_ShopBit._unit_tests()")


# FabShops:
@dataclass
class FabShops(object):
    """FabShops: A collection of FabShop's.

    This class collects all available FabShop's together.
    It precomputes the FabShopBit's that are available for each operation type.

    Attributes:
    * *Shops* (Tuple[FabShop, ...]: All available FabShop's.
    * *Machines* (Tuple[Tuple[FabShop, FabMachine, ...]: A tuple of all (FabShop, FabMachine) pairs.
    * *AllShopBits: (Tuple[FabShopBit, ...]): A tuple of a FabShopBit's.
    * *DrillShipBits (Tuple[FabShopBit, ...]):
      A tuple of FabShopBit's suitable for exterior drilling.
    * *PerimeterShopBits: (Tuple[FabShopBit, ...]):
      A tuple of FabShopBit's suitable for exterior perimeter contouring.
    * *PocketShopBits: (Tuple[FabShopBit, ...]): A tuple of FabShopBit's suitable for pocketing.

    Constructor:
    * FabShops(Shops)

    """
    Shops: Tuple[FabShop, ...]
    ShopMachines: Tuple[Tuple[FabShop, FabMachine], ...] = field(init=False, repr=False)
    AllShopBits: Tuple[Fab_ShopBit, ...] = field(init=False, repr=False)
    DrillShopBits: Tuple[Fab_ShopBit, ...] = field(init=False, repr=False)
    PerimeterShopBits: Tuple[Fab_ShopBit, ...] = field(init=False, repr=False)
    PocketShopBits: Tuple[Fab_ShopBit, ...] = field(init=False, repr=False)

    # FabShops.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabShops."""
        all_shop_bits: List[Fab_ShopBit] = []
        drill_shop_bits: List[Fab_ShopBit] = []
        lower_chamfer_shop_bits: List[Fab_ShopBit] = []
        perimeter_shop_bits: List[Fab_ShopBit] = []
        pocket_shop_bits: List[Fab_ShopBit] = []
        upper_chamfer_shop_bits: List[Fab_ShopBit] = []

        operations_table: Dict[str, List[Fab_ShopBit]] = {
            "drill": drill_shop_bits,
            "lower_chamfer": lower_chamfer_shop_bits,
            "perimeter": perimeter_shop_bits,
            "pocket": pocket_shop_bits,
            "upper_chamfer": upper_chamfer_shop_bits,
        }

        shop_index: int
        shop: FabShop
        for shop_index, shop in enumerate(self.Shops):
            machine_index: int
            machine: FabMachine
            for machine_index, machine in enumerate(shop.Machines):
                library: FabLibrary = machine.Library
                number: int
                bit: FabBit
                for number, bit in library.NumberedBits:
                    operation_kinds: Tuple[str, ...] = bit.getOperationKinds()
                    operation_kind: str
                    for operation_kind in operation_kinds:
                        assert operation_kind in operations_table, operation_kind
                        bit_priority: Optional[float] = bit.getBitPriority(operation_kind)
                        if bit_priority is not None:
                            shop_bit: Fab_ShopBit = Fab_ShopBit(bit_priority, shop, shop_index,
                                                                machine, machine_index, bit, number)
                            operations_table[operation_kind].append(shop_bit)

        self.AllShopBits = tuple(all_shop_bits)
        self.DrillShopBits = tuple(drill_shop_bits)
        self.PerimeterShopBits = tuple(perimeter_shop_bits)
        self.PocketShopBits = tuple(pocket_shop_bits)

    # FabShops.getExample():
    @staticmethod
    def getExample() -> "FabShops":
        """Return an example FabShops."""
        shop: FabShop = FabShop.getExample()
        shops: FabShops = FabShops((shop,))
        return shops

    # FabShops._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run FabShops unit tests."""
        if tracing:
            print(f"{tracing}=>FabShops._unit_tests()")

        shops: FabShops = FabShops.getExample()
        if tracing:
            print(f"{tracing}{len(shops.AllShopBits)=}")
            print(f"{tracing}{len(shops.DrillShopBits)=}")
            print(f"{tracing}{len(shops.PerimeterShopBits)=}")
            print(f"{tracing}{len(shops.PocketShopBits)=}")

        if tracing:
            print(f"{tracing}<=FabShops._unit_tests()")


# Main program:
def main(tracing: str = "") -> None:
    """Run the unit test suites."""
    next_tracing: str = tracing + " " if tracing else ""
    if tracing:
        print("=>FabShops.main()")
    FabAxis._unit_tests(tracing=next_tracing)
    FabCNC._unit_tests(tracing=next_tracing)
    FabCNCMill._unit_tests(tracing=next_tracing)
    FabCNCRouter._unit_tests(tracing=next_tracing)
    FabController._unit_tests(tracing=next_tracing)
    FabLocation._unit_tests(tracing=next_tracing)
    FabMachine._unit_tests(tracing=next_tracing)
    FabSpindle._unit_tests(tracing=next_tracing)
    FabShop._unit_tests(tracing=next_tracing)
    FabShops._unit_tests(tracing=next_tracing)
    FabTable._unit_tests(tracing=next_tracing)
    Fab_ShopBit._unit_tests(tracing=next_tracing)
    if tracing:
        print("=>FabShops.main()")


if __name__ == "__main__":
    main(tracing=" ")
