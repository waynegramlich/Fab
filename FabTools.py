#!/usr/bin/env python3
"""FabTools: Tools for Fab..

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

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

# Issues:
# * Turn off Legacy tools Path => Preferences => [] Enable Legacy Tools
# * Edit move the from line 11 to line 10 in .../Tools/Bit/45degree_chamfer.fctb to fix JSON error.
# * When setting path to library, be sure to include .../Tools/Library  (one level up does not work)

import json
from typeguard import check_type, check_argument_types
from typing import Any, Dict, IO, List, Tuple, Union
from dataclasses import dataclass
from pathlib import Path as PathFile
from FabToolTemplates import FabAttributes, FabBit, FabBitTemplate, FabBitTemplates, FabShapes


# FabBallEndBit:
@dataclass(frozen=True)
class FabBallEndBit(FabBit):
    """FabBallEndBit: An end-mill bit template.

    Attributes:
    * *Name* (str): The name of Ball End bit.
    * *BitFile* (PathFile): The `.fctb` file.
    * *Shape* (FabShape): The associated `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated attributes.
    * *CuttingEdgeHeight* (Union[str, float]): The ball end cutting edge height.
    * *Diameter* (Union[str, float]): The ball end cutter diameter.
    * *Length* (Union[str, float]): The total length of the ball end.
    * *ShankDiameter: (Union[str, float]): The ball end shank diameter.

    Constructor:
    * FabBallEndBit("Name", BitFile, Shape, Attributes,
      CuttingEdgeHeight, Diameter, Length, ShankDiameter)
    """

    CuttingEdgeHeight: Union[str, float]
    Diameter: Union[str, float]
    Length: Union[str, float]
    ShankDiameter: Union[str, float]

    # FabBallEndBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabBallEndTool."""
        super().__post_init__()
        check_type("FabBallEndBit.CuttingEdgeHeight", self.CuttingEdgeHeight, Union[float, str])
        check_type("FabBallEndBit.Diameter", self.Diameter, Union[float, str])
        check_type("FabBallEndBit.Length", self.Length, Union[float, str])
        check_type("FabBallEndBit.ShankDiameter", self.ShankDiameter, Union[float, str])

    # FabBallEndBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabBallEndBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabBallEndBit._unit_tests()")
        ball_end_bit: Any = FabBitTemplates.getExample(FabBallEndBit)
        assert isinstance(ball_end_bit, FabBallEndBit)
        assert ball_end_bit.Name == "6mm_Ball_End"
        assert ball_end_bit.BitFile.name == "ballend.fctb"
        assert ball_end_bit.Shape.Name == "BallEnd"
        assert ball_end_bit.CuttingEdgeHeight == "40.0000 mm"
        assert ball_end_bit.Diameter == "5.000 mm"
        assert ball_end_bit.Length == "50.000 mm"
        assert ball_end_bit.ShankDiameter == "3.000 mm"
        assert ball_end_bit.Attributes == FabAttributes.fromJSON({
            "Flutes": 2,
            "Material": "HSS",
        })
        # ball_end_json: Dict[str, Any] = ball_end_bit.toJSON()
        # assert FabBit.fromJSON(ball_end_json) == ball_end_bit
        if tracing:
            print(f"{tracing}<=FabBallEndBit._unit_tests()")


# FabBullNoseBit:
@dataclass(frozen=True)
class FabBullNoseBit(FabBit):
    """FabBullNoseBit: An end-mill bit template.

    Attributes:
    * *Name* (str): The name of Ball End bit.
    * *BitFile* (PathFile): The `.fctb` file.
    * *Shape* (FabShape): The associated `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated attributes.
    * *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
    * *Diameter* (Union[str, float]): The bull nose cutter diameter.
    * *FlatRadius* (Union[str, float]): The flat radius of the bull nose cutter.
    * *Length* (Union[str, float]): The total length of the bull nose cutter.
    * *ShankDiameter: (Union[str, float]): The shank diameter.

    Constructor:
    * FabBullNoseBit("Name", BitFile, Shape, Attributes,
      CuttingEdgeHeight, Diameter, Length, ShankDiameter)
    """

    CuttingEdgeHeight: Union[str, float]
    Diameter: Union[str, float]
    FlatRadius: Union[str, float]
    Length: Union[str, float]
    ShankDiameter: Union[str, float]

    # FabBullNoseBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabBullNoseTool."""
        super().__post_init__()
        check_type("FabBullNoseBit.CuttingEdgeHeight", self.CuttingEdgeHeight, Union[float, str])
        check_type("FabBullNoseBit.Diameter", self.Diameter, Union[float, str])
        check_type("FabBullNoseBit.FlatRadius", self.FlatRadius, Union[float, str])
        check_type("FabBullNoseBit.Length", self.Length, Union[float, str])
        check_type("FabBullNoseBit.ShankDiameter", self.ShankDiameter, Union[float, str])

    # FabBullNoseBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabBullNoseBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabBullNoseBit._unit_tests()")
        bull_nose_bit: Any = FabBitTemplates.getExample(FabBullNoseBit)
        assert bull_nose_bit.Name == "6mm_Bull_Nose"
        assert bull_nose_bit.BitFile.name == "bullnose.fctb"
        assert bull_nose_bit.Shape.Name == "BullNose"
        assert bull_nose_bit.CuttingEdgeHeight == "40.000 mm"
        assert bull_nose_bit.Diameter == "5.000 mm"
        assert bull_nose_bit.Length == "50.000 mm"
        assert bull_nose_bit.ShankDiameter == "3.000 mm"
        assert bull_nose_bit.Attributes == FabAttributes.fromJSON({
            "Flutes": 2,
            "Material": "HSS",
        })
        if tracing:
            print(f"{tracing}<=FabBullNoseBit._unit_tests()")


# FabChamferBit:
@dataclass(frozen=True)
class FabChamferBit(FabBit):
    """FabChamferBit: An end-mill bit template.

    Attributes:
    * *Name* (str): The name of Ball End bit.
    * *BitFile* (PathFile): The `.fctb` file.
    * *Shape* (FabShape): The associated `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated attributes.
    * *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle.
    * *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
    * *Diameter* (Union[str, float]): The chamfer outer diameter.
    * *Length* (Union[str, float]): The total length of the chamfer cutter.
    * *ShankDiameter: (Union[str, float]): The shank diameter.
    * *TipDiameter* (Union[str, float]): The tip radius of the chamfer cutter.

    Constructor:
    * FabChamferBit("Name", BitFile, Shape, Attributes,
      CuttingEdgeHeight, Diameter, Length, ShankDiameter)
    """

    CuttingEdgeAngle: Union[str, float]
    CuttingEdgeHeight: Union[str, float]
    Diameter: Union[str, float]
    Length: Union[str, float]
    ShankDiameter: Union[str, float]
    TipDiameter: Union[str, float]

    # FabChamferBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabChamferTool."""
        super().__post_init__()
        check_type("FabChamferBit.CuttingEdgeAngle", self.CuttingEdgeAngle, Union[float, str])
        check_type("FabChamferBit.CuttingEdgeHeight", self.CuttingEdgeHeight, Union[float, str])
        check_type("FabChamferBit.Diameter", self.Diameter, Union[float, str])
        check_type("FabChamferBit.Length", self.Length, Union[float, str])
        check_type("FabChamferBit.ShankDiameter", self.ShankDiameter, Union[float, str])
        check_type("FabChamferBit.TipDiameter", self.TipDiameter, Union[float, str])

    # FabChamferBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabChamferBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabChamferBit._unit_tests()")
        chamfer_bit: Any = FabBitTemplates.getExample(FabChamferBit)
        assert chamfer_bit.Name == "45degree_chamfer"
        assert chamfer_bit.BitFile.name == "chamfer.fctb"
        assert chamfer_bit.Shape.Name == "Chamfer"
        assert chamfer_bit.CuttingEdgeAngle == "60.000 °"
        assert chamfer_bit.CuttingEdgeHeight == "6.350 mm"
        assert chamfer_bit.Diameter == "12.000 mm"
        assert chamfer_bit.Length == "30.000 mm"
        assert chamfer_bit.ShankDiameter == "6.350 mm"
        assert chamfer_bit.TipDiameter == "5.000 mm"
        assert chamfer_bit.Attributes == FabAttributes.fromJSON({
            "Flutes": 2,
            "Material": "HSS",
        })
        if tracing:
            print(f"{tracing}<=FabChamferBit._unit_tests()")


# FabDoveTailBit:
@dataclass(frozen=True)
class FabDoveTailBit(FabBit):
    """FabDoveTailBit: An end-mill bit template.

    Attributes:
    * *Name* (str): The name of Ball End bit.
    * *BitFile* (PathFile): The `.fctb` file.
    * *Shape* (FabShape): The associated `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated attributes.
    * *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle.
    * *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
    * *Diameter* (Union[str, float]): The chamfer outer diameter.
    * *Length* (Union[str, float]): The total length of the chamfer cutter.
    * *NeckDiameter* (Union[str, float]): The diameter of the neck between the cutter and shank
    * *NeckHeight* (Union[str, float]): The height of the neck between the cutter and shank
    * *ShankDiameter: (Union[str, float]): The shank diameter.
    * *TipDiameter* (Union[str, float]): The tip radius of the chamfer cutter.

    Constructor:
    * FabDoveTailBit("Name", BitFile, Shape, Attributes, CuttingEdgeAngle, CuttingEdgeHeight,
      Diameter, Length, NeckDiameter, NeckHeight,  ShankDiameter, TipDiameter)
    """

    CuttingEdgeAngle: Union[str, float]
    CuttingEdgeHeight: Union[str, float]
    Diameter: Union[str, float]
    Length: Union[str, float]
    NeckDiameter: Union[str, float]
    NeckHeight: Union[str, float]
    ShankDiameter: Union[str, float]
    TipDiameter: Union[str, float]

    # FabDoveTailBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabChamferTool."""
        super().__post_init__()
        check_type("FabDoveTailBit.CuttingEdgeAngle", self.CuttingEdgeAngle, Union[float, str])
        check_type("FabDoveTailBit.CuttingEdgeHeight", self.CuttingEdgeHeight, Union[float, str])
        check_type("FabDoveTailBit.Diameter", self.Diameter, Union[float, str])
        check_type("FabDoveTailBit.Length", self.Length, Union[float, str])
        check_type("FabDoveTailBit.ShankDiameter", self.ShankDiameter, Union[float, str])
        check_type("FabDoveTailBit.NeckHieght", self.NeckHeight, Union[float, str])
        check_type("FabDoveTailBit.NeckDiameter", self.NeckDiameter, Union[float, str])
        check_type("FabDoveTailBit.TipDiameter", self.TipDiameter, Union[float, str])

    # FabDoveTailBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabDoveTailBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabDoveTailBit._unit_tests()")
        dove_tail_bit: Any = FabBitTemplates.getExample(FabDoveTailBit)
        assert dove_tail_bit.Name == "no_dovetail_yet"
        assert dove_tail_bit.BitFile.name == "dovetail.fctb"
        assert dove_tail_bit.Shape.Name == "DoveTail"
        assert dove_tail_bit.CuttingEdgeAngle == "60.000 °"
        assert dove_tail_bit.CuttingEdgeHeight == "9.000 mm"
        assert dove_tail_bit.Diameter == "19.050 mm"
        assert dove_tail_bit.Length == "54.200 mm"
        assert dove_tail_bit.ShankDiameter == "9.525 mm"
        assert dove_tail_bit.TipDiameter == "5.000 mm"
        assert dove_tail_bit.Attributes == FabAttributes.fromJSON({
            "Flutes": 2,
            "Material": "HSS",
        })
        if tracing:
            print(f"{tracing}<=FabDoveTailBit._unit_tests()")


# FabDrillBit:
@dataclass(frozen=True)
class FabDrillBit(FabBit):
    """FabDrillBit: An end-mill bit template.

    Attributes:
    * *Name* (str): The name of Ball End bit.
    * *BitFile* (PathFile): The `.fctb` file.
    * *Shape* (FabShape): The associated `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated attributes.
    * *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle.
    * *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
    * *Diameter* (Union[str, float]): The drill outer diameter.
    * *Length* (Union[str, float]): The total length of the drill cutter.
    * *TipAngle: (Union[str, float]): The drill tip point angle.

    Constructor:
    * FabDrillBit("Name", BitFile, Shape, Attributes, Diameter, Length, TipAngle)
    """

    Diameter: Union[str, float]
    Length: Union[str, float]
    TipAngle: Union[str, float]

    # FabDrillBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabDrillTool."""
        super().__post_init__()
        check_type("FabDrillBit.Diameter", self.Diameter, Union[float, str])
        check_type("FabDrillBit.Length", self.Length, Union[float, str])
        check_type("FabDrillBit.TipAngle", self.TipAngle, Union[float, str])

    # FabDrillBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabDrillBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabDrillBit._unit_tests()")
        drill_bit: Any = FabBitTemplates.getExample(FabDrillBit)
        assert drill_bit.Name == "5mm_Drill"
        assert drill_bit.BitFile.name == "drill.fctb"
        assert drill_bit.Shape.Name == "Drill"
        assert drill_bit.Diameter == "3.000 mm"
        assert drill_bit.Length == "50.000 mm"
        assert drill_bit.TipAngle == "119.000 °"
        assert drill_bit.Attributes == FabAttributes.fromJSON({
            "Flutes": 2,
            "Material": "HSS",
        })
        if tracing:
            print(f"{tracing}<=FabChamferBit._unit_tests()")


# FabEndMillBit:
@dataclass(frozen=True)
class FabEndMillBit(FabBit):
    """FabEndMillBit: An end-mill bit template.

    Attributes:
    * *Name* (str): The name of Ball End bit.
    * *BitFile* (PathFile): The `.fctb` file.
    * *Shape* (FabShape): The associated `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated attributes.
    * *CuttingEdgeHeight* (Union[str, float]): The end mill cutting edge height.
    * *Diameter* (Union[str, float]): The end mill cutter diameter.
    * *Length* (Union[str, float]): The total length of the end mill.
    * *ShankDiameter: (Union[str, float]): The end millshank diameter.

    Constructor:
    * FabEndMillBit("Name", BitFile, Shape, Attributes,
      CuttingEdgeHeight, Diameter, Length, ShankDiameter)
    """

    CuttingEdgeHeight: Union[str, float]
    Diameter: Union[str, float]
    Length: Union[str, float]
    ShankDiameter: Union[str, float]

    # FabEndMillBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabEndMillTool."""
        super().__post_init__()
        check_type("FabEndMillBit.CuttingEdgeHeight", self.CuttingEdgeHeight, Union[float, str])
        check_type("FabEndMillBit.Diameter", self.Diameter, Union[float, str])
        check_type("FabEndMillBit.Length", self.Length, Union[float, str])
        check_type("FabEndMillBit.ShankDiameter", self.ShankDiameter, Union[float, str])

    # FabEndMillBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabEndMillBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabEndMillBit._unit_tests()")
        end_mill_bit: Any = FabBitTemplates.getExample(FabEndMillBit)
        assert isinstance(end_mill_bit, FabEndMillBit)
        assert end_mill_bit.Name == "5mm_Endmill"
        assert end_mill_bit.BitFile.name == "endmill.fctb"
        assert end_mill_bit.Shape.Name == "EndMill"
        assert end_mill_bit.CuttingEdgeHeight == "30.000 mm"
        assert end_mill_bit.Diameter == "5.000 mm"
        assert end_mill_bit.Length == "50.000 mm"
        assert end_mill_bit.ShankDiameter == "3.000 mm"
        assert end_mill_bit.Attributes == FabAttributes.fromJSON({
            "Flutes": 2,
            "Material": "HSS",
        }), end_mill_bit.Attributes
        if tracing:
            print(f"{tracing}<=FabEndMillBit._unit_tests()")


# FabProbeBit:
@dataclass(frozen=True)
class FabProbeBit(FabBit):
    """FabProbeBit: An end-mill bit template.

    Attributes:
    * *Name* (str): The name of Ball End bit.
    * *BitFile* (PathFile): The `.fctb` file.
    * *Shape* (FabShape): The associated `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated attributes.
    * *Diameter* (Union[str, float]): The probe ball diameter.
    * *Length* (Union[str, float]): The total length of the probe.
    * *ShaftDiameter: (Union[str, float]): The probe shaft diameter.

    Constructor:
    * FabProbeBit("Name", BitFile, Shape, Attributes, Diameter, Length, TipAngle)
    """

    Diameter: Union[str, float]
    Length: Union[str, float]
    ShaftDiameter: Union[str, float]

    # FabProbeBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabProbeTool."""
        super().__post_init__()
        check_type("FabProbeBit.Diameter", self.Diameter, Union[float, str])
        check_type("FabProbeBit.Length", self.Length, Union[float, str])
        check_type("FabProbeBit.ShaftDiameter", self.ShaftDiameter, Union[float, str])

    # FabProbeBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabProbeBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabProbeBit._unit_tests()")
        probe_bit: Any = FabBitTemplates.getExample(FabProbeBit)
        assert probe_bit.Name == "probe"
        assert probe_bit.BitFile.name == "probe.fctb"
        assert probe_bit.Shape.Name == "Probe"
        assert probe_bit.Diameter == "6.000 mm"
        assert probe_bit.Length == "50.000 mm"
        assert probe_bit.ShaftDiameter == "4.000 mm"
        assert probe_bit.Attributes == FabAttributes.fromJSON({
            "Spindle Power": False,
        })
        if tracing:
            print(f"{tracing}<=FabChamferBit._unit_tests()")


# FabSlittingSawBit:
@dataclass(frozen=True)
class FabSlittingSawBit(FabBit):
    """FabSlittingSawBit: An end-mill bit template.

    Attributes:
    * *Name* (str): The name of Ball End bit.
    * *BitFile* (PathFile): The `.fctb` file.
    * *Shape* (FabShape): The associated `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated attributes.
    * *BladeThickness* (Union[str, float]): The cutting saw blade thickness.
    * *CapDiameter* (Union[str, float]): The cutting saw end cab diameter.
    * *CapHeight* (Union[str, float]): The cutting end end cab height.
    * *Diameter* (Union[str, float]): The cutting saw blade diameter.
    * *ShankDiameter: (Union[str, float]): The cutting saw shank diameter.

    Constructor:
    * FabSlittingSawBit("Name", BitFile, Shape, Attributes,
      BladeThickness, CapDiameter, CapHeight, Diameter, Length, ShankDiameter)
    """

    BladeThickness: Union[str, float]
    CapDiameter: Union[str, float]
    CapHeight: Union[str, float]
    Diameter: Union[str, float]
    Length: Union[str, float]
    ShankDiameter: Union[str, float]

    # FabSlittingSawBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabChamferTool."""
        super().__post_init__()
        check_type("FabSlittingSawBit.BladeThickness", self.BladeThickness, Union[float, str])
        check_type("FabSlittingSawBit.CapDiameter", self.CapDiameter, Union[float, str])
        check_type("FabSlittingSawBit.CapHeight", self.CapHeight, Union[float, str])
        check_type("FabSlittingSawBit.Diameter", self.Diameter, Union[float, str])
        check_type("FabSlittingSawBit.Length", self.Length, Union[float, str])
        check_type("FabSlittingSawBit.ShankDiameter", self.ShankDiameter, Union[float, str])

    # FabSlittingSawBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabSlittingSawBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabSlittingSawBit._unit_tests()")
        slitting_saw_bit: Any = FabBitTemplates.getExample(FabSlittingSawBit)
        assert slitting_saw_bit.Name == "slittingsaw"
        assert slitting_saw_bit.BitFile.name == "slittingsaw.fctb"
        assert slitting_saw_bit.Shape.Name == "SlittingSaw"
        assert slitting_saw_bit.BladeThickness == "3.000 mm"
        assert slitting_saw_bit.CapDiameter == "8.000 mm"
        assert slitting_saw_bit.CapHeight == "3.000 mm"
        assert slitting_saw_bit.Diameter == "76.200 mm"
        assert slitting_saw_bit.Length == "50.000 mm"
        assert slitting_saw_bit.ShankDiameter == "19.050 mm"
        assert slitting_saw_bit.Attributes == FabAttributes.fromJSON({
            "Flutes": 30,
            "Material": "HSS",
        })
        if tracing:
            print(f"{tracing}<=FabSlittingSawBit._unit_tests()")


# FabThreadMillBit:
@dataclass(frozen=True)
class FabThreadMillBit(FabBit):
    """FabThreadMillBit: An thread mill bit template.

    Attributes:
    * *Name* (str): The name of thread mill bit.
    * *BitFile* (PathFile): The `.fctb` file.
    * *Shape* (FabShape): The associated `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated attributes.
    * *CuttingAngle* (Union[str, float]): The cutter point angle.
    * *Crest* (Union[str, float]): The thread cutter crest thickness.
    * *Diameter* (Union[str, float]): The chamfer outer diameter.
    * *Length* (Union[str, float]): The total length of the chamfer cutter.
    * *NeckDiameter* (Union[str, float]): The diameter of the neck between the cutter and shank
    * *NeckLength* (Union[str, float]): The height of the neck between the cutter and shank
    * *ShankDiameter: (Union[str, float]): The shank diameter.

    Constructor:
    * FabThreadMillBit("Name", BitFile, Shape, Attributes, Cuttingngle, Diameter, Length,
      NeckDiameter, NeckLength,  ShankDiameter)
    """

    CuttingAngle: Union[str, float]
    Crest: Union[str, float]
    Diameter: Union[str, float]
    Length: Union[str, float]
    NeckDiameter: Union[str, float]
    NeckLength: Union[str, float]
    ShankDiameter: Union[str, float]

    # FabThreadMillBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabChamferTool."""
        super().__post_init__()
        check_type("FabThreadMillBit.CuttingAngle", self.CuttingAngle, Union[float, str])
        check_type("FabThreadMillBit.Crest", self.Crest, Union[float, str])
        check_type("FabThreadMillBit.Diameter", self.Diameter, Union[float, str])
        check_type("FabThreadMillBit.Length", self.Length, Union[float, str])
        check_type("FabThreadMillBit.NeckDiameter", self.NeckDiameter, Union[float, str])
        check_type("FabThreadMillBit.NeckLength", self.NeckLength, Union[float, str])
        check_type("FabThreadMillBit.ShankDiameter", self.ShankDiameter, Union[float, str])

    # FabThreadMillBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabThreadMillBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabThreadMillBit._unit_tests()")
        thread_mill_bit: Any = FabBitTemplates.getExample(FabThreadMillBit)
        assert thread_mill_bit.Name == "5mm-thread-cutter"
        assert thread_mill_bit.BitFile.name == "threadmill.fctb"
        assert thread_mill_bit.Shape.Name == "ThreadMill"
        assert thread_mill_bit.CuttingAngle == "60.000 °"
        assert thread_mill_bit.Diameter == "5.000 mm"
        assert thread_mill_bit.Length == "50.000 mm"
        assert thread_mill_bit.ShankDiameter == "5.000 mm"
        assert thread_mill_bit.Attributes == FabAttributes.fromJSON({
            "Flutes": 10,
            "Material": "HSS",
        })
        if tracing:
            print(f"{tracing}<=FabThreadMillBit._unit_tests()")


# FabVBit:
@dataclass(frozen=True)
class FabVBit(FabBit):
    """FabVBit: An V groove bit template.

    Attributes:
    * *Name* (str): The name of Ball End bit.
    * *BitFile* (PathFile): The `.fctb` file.
    * *Shape* (FabShape): The associated `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated attributes.
    * *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle.
    * *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
    * *Diameter* (Union[str, float]): The v outer diameter.
    * *Length* (Union[str, float]): The total length of the v cutter.
    * *ShankDiameter: (Union[str, float]): The shank diameter.
    * *TipDiameter* (Union[str, float]): The tip radius of the v cutter.

    Constructor:
    * FabVBit("Name", BitFile, Shape, Attributes,
      CuttingEdgeHeight, Diameter, Length, ShankDiameter)
    """

    CuttingEdgeAngle: Union[str, float]
    CuttingEdgeHeight: Union[str, float]
    Diameter: Union[str, float]
    Length: Union[str, float]
    ShankDiameter: Union[str, float]
    TipDiameter: Union[str, float]

    # FabVBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabVTool."""
        super().__post_init__()
        check_type("FabVBit.CuttingEdgeAngle", self.CuttingEdgeAngle, Union[float, str])
        check_type("FabVBit.CuttingEdgeHeight", self.CuttingEdgeHeight, Union[float, str])
        check_type("FabVBit.Diameter", self.Diameter, Union[float, str])
        check_type("FabVBit.Length", self.Length, Union[float, str])
        check_type("FabVBit.ShankDiameter", self.ShankDiameter, Union[float, str])
        check_type("FabVBit.TipDiameter", self.TipDiameter, Union[float, str])

    # FabVBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabVBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabVBit._unit_tests()")
        v_bit: Any = FabBitTemplates.getExample(FabVBit)
        assert v_bit.Name == "60degree_VBit"
        assert v_bit.BitFile.name == "v.fctb"
        assert v_bit.Shape.Name == "V"
        assert v_bit.CuttingEdgeAngle == "90.000 °"
        assert v_bit.CuttingEdgeHeight == "1.000 mm"
        assert v_bit.Diameter == "10.000 mm"
        assert v_bit.Length == "20.000 mm"
        assert v_bit.ShankDiameter == "5.000 mm"
        assert v_bit.TipDiameter == "1.000 mm"
        assert v_bit.Attributes == FabAttributes.fromJSON({
            "Flutes": 4,
            "Material": "HSS",
        }), v_bit.Attributes
        if tracing:
            print(f"{tracing}<=FabVBit._unit_tests()")


# FabLibrary:
@dataclass(frozen=True)
class FabLibrary(object):
    """FabLibrary: Tool libraries directory (e.g. `.../Tools/Library/*.fctl`).

    Attributes:
    * *Name* (str): The stem of LibraryFile (i.e. `xyz.fctl` => "xyz".)
    * *LibraryFile* (PathFile): The file for the `.fctl` file.
    * *NumberedBitss*: Tuple[Tuple[int, FabBit], ...]: A list of numbered to FabBit's.

    Constructor:
    * FabLibrary("Name", LibraryFile, Tools)
    """

    Name: str
    LibraryFile: PathFile
    NumberedBits: Tuple[Tuple[int, FabBit], ...]

    # FabLibrary:__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabLibrary."""
        check_type("FabLibrary.Name", self.Name, str)
        check_type("FabLibrary.LibraryFile", self.LibraryFile, PathFile)
        check_type("FabLibrary.NumberedBits", self.NumberedBits, Tuple[Tuple[int, FabBit], ...])

    # FabLibrary.read():
    @staticmethod
    def read(library_file: PathFile, bits: "FabBits", tracing: str = "") -> "FabLibrary":
        """Read in FabLibrary from a JSON file."""
        if tracing:
            print(f"{tracing}=>FabLibrary.read({library_file}, *)")
        assert check_argument_types()

        # Open *library_file*, read it in and parse it into *json_dict*:
        json_file: IO[str]
        json_text: str
        with open(library_file) as json_file:
            json_text = json_file.read()
        try:
            json_dict: Dict[str, Any] = json.loads(json_text)
        except json.decoder.JSONDecodeError as decode_error:  # pragma: no unit cover
            assert False, f"Unable to parse {library_file} as JSON: Error:{str(decode_error)}"

        # The format of *json_dict* should be:
        # {
        #   "version": 1,
        #   "tools": [
        #     {
        #       "nr": 1,
        #       "path": "xyz.fctb"
        #     },
        #     ...
        #   ]
        # }

        # Extract *version* and *tools*:
        check_type("FabLibrary.json_dict", json_dict, Dict[str, Any])
        assert len(json_dict) == 2, "FabLibrary.readJson(): {len(json_dict)=}"
        version: Any = json_dict["version"] if "version" in json_dict else None
        assert isinstance(version, int) and version == 1, f"FabLibrary.readJson(): {version=}"
        tools: Any = json_dict["tools"] if "tools" in json_dict else None
        assert isinstance(tools, list), "FabLibrary.readJson(): {tools=}"

        # Sweep through *tools* in JSON and build sorted *numbered_bit_names* list:
        numbered_bit_names: List[Tuple[int, str]] = []
        bit_number: int
        bit_name: str
        check_type("FabLibrary.readJson(): tools", tools, List[Dict[str, Union[int, str]]])
        bit_dict: Any
        for bit_dict in tools:
            check_type("FabLibrary.readJson(): tool", bit_dict, Dict[str, Union[int, str]])
            bit_number = bit_dict["nr"] if "nr" in bit_dict else -1
            check_type("FabLibrary.readJson(): bit_number", bit_number, int)
            bit_name = bit_dict["path"] if "path" in bit_dict else ""
            check_type("FabLibrary.readJson(): path", bit_name, str)
            assert bit_number >= 0 and bit_name, f"{bit_number=} {bit_name=}"
            numbered_bit_names.append((bit_number, bit_name))
        numbered_bit_names.sort()

        # Lookup up the associated FabBit's:
        numbered_bits: List[Tuple[int, FabBit]] = []
        for bit_number, bit_name in numbered_bit_names:
            assert bit_name.endswith(".fctb")
            bit_stem: str = bit_name[:-5]
            if tracing:
                print(f"{tracing}Tool[{bit_number}]: '{bit_stem}'")
            try:
                bit: FabBit = bits.lookup(bit_stem)
            except KeyError as key_error:
                assert False, f"FabLibrary.readJson(): {str(key_error)}"
            numbered_bits.append((bit_number, bit))

        library: FabLibrary = FabLibrary(library_file.stem, library_file, tuple(numbered_bits))
        if tracing:
            print(f"{tracing}<=FabLibrary.read({library_file}, *)=>*")
        return library

    # FabLibrary.lookupName():
    def lookupName(self, name: str) -> FabBit:
        """Lookup a FabBit by name."""
        numbered_bits: Tuple[Tuple[int, FabBit], ...] = self.NumberedBits
        bit_number: int
        bit: FabBit
        for bit_number, bit in numbered_bits:
            if bit.Name == name:
                return bit
        raise KeyError(f"FabLibrary.lookupName('{name}'): Tool not found.")

    # FabLibrary.lookupNumber():
    def lookupNumber(self, number: int) -> FabBit:
        """Lookup a FabBit by name."""
        bit_number: int
        bit: FabBit
        for bit_number, bit in self.NumberedBits:
            if bit_number == number:
                return bit
        raise KeyError(f"FabLibrary.lookupNumber('{number}'): Tool not found.")

    # FabLibrary._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """FabLibrary Unit tests."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabLibrary._unit_tests()")
        tools_directory: PathFile = PathFile(__file__).parent / "Tools"
        bits_directory: PathFile = tools_directory / "Bit"
        shapes_directory: PathFile = tools_directory / "Shape"
        libraries_directory: PathFile = tools_directory / "Library"

        shapes: FabShapes = FabShapes.read(shapes_directory)
        bits: FabBits = FabBits.read(bits_directory, shapes)
        library_file: PathFile = libraries_directory / "Default.fctl"
        library: FabLibrary = FabLibrary.read(library_file, bits, tracing=next_tracing)

        number: int
        bit: FabBit
        for number, bit in library.NumberedBits:
            assert bit is library.lookupName(bit.Name)
            assert bit is library.lookupNumber(number)

        # Test lookup methods:
        desired_error: str
        try:
            library.lookupName("Bogus")
            assert False
        except KeyError as key_error:
            desired_error = '"FabLibrary.lookupName(\'Bogus\'): Tool not found."'
            assert str(key_error) == desired_error, (str(key_error), desired_error)
        try:
            library.lookupNumber(-1)
            assert False
        except KeyError as key_error:
            desired_error = '"FabLibrary.lookupNumber(\'-1\'): Tool not found."'
            assert str(key_error) == desired_error, (str(key_error), desired_error)

        if tracing:
            print(f"{tracing}<=FabLibrary._unit_tests()")


# FabLibraries:
@dataclass(frozen=True)
class FabLibraries(object):
    """FabLibraries: Represents a directory of FabLibrary's.

    Attributes:
    * *Name* (str): The directory name (i.e. the stem the LibraryPath.)
    * *LibrariesPath (PathFile): The directory that contains the FabLibraries.
    * *Libraries* (Tuple[FabLibrary, ...): The actual libraries sorted by library name.
    * *LibraryNames*: Tuple[str, ...]: The sorted library names.

    Constructor:
    * FabLibraries("Name", LibrariesPath, Libraries)

    """

    Name: str
    LibrariesPath: PathFile
    Libraries: Tuple[FabLibrary, ...]
    LibraryNames: Tuple[str, ...]

    # FabLibraries.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabLibriaries."""
        check_type("FabLibraries.Name", self.Name, str)
        check_type("FabLibraries.LibrariesPath", self.LibrariesPath, PathFile)
        check_type("FabLibraries.Libraries", self.Libraries, Tuple[FabLibrary, ...])
        check_type("FabLibraries.LibraryNames", self.LibraryNames, Tuple[str, ...])

    # FabLibraries.read():
    @staticmethod
    def read(libraries_path: PathFile, bits: "FabBits", tracing: str = "") -> "FabLibraries":
        """Read in a FabLibraries from a directory."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabLibraries.read('{str(libraries_path)}('), *)")
        assert check_argument_types(), "FabLibraries.read()"
        assert libraries_path.is_dir(), f"FabLibraries.read(): {libraries_path=}"
        libraries_dict: Dict[str, FabLibrary] = {}
        library_path: PathFile
        for library_path in libraries_path.glob("*.fctl"):
            assert library_path.exists(), "FabLibrary.read(): f{library_path} does not exist"
            library: FabLibrary = FabLibrary.read(library_path, bits, tracing=next_tracing)
            libraries_dict[library.Name] = library
        sorted_library_names: Tuple[str, ...] = tuple(sorted(libraries_dict.keys()))
        library_name: str
        sorted_libraries: Tuple[FabLibrary, ...] = tuple(
            [libraries_dict[library_name] for library_name in libraries_dict.keys()])
        libraries: FabLibraries = FabLibraries(
            libraries_path.stem, libraries_path, sorted_libraries, sorted_library_names)
        if tracing:
            print(f"{tracing}<=FabLibraries.read('{str(libraries_path)}('), *)=>*")
        return libraries

    # FabLibaries.nameLookup():
    def nameLookup(self, name: str) -> FabLibrary:
        """Lookup a library by name."""
        library: FabLibrary
        for library in self.Libraries:
            if library.Name == name:
                return library
        raise KeyError(f"FabLibraries.nameLookup(): {name} is not one of {self.LibraryNames}")

    # FabLibraries._unit_tests:
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform the FabLibraries unit tests."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabLibrarires._unit_tests()")
        tools_directory: PathFile = PathFile(__file__).parent / "Tools"
        shapes_directory: PathFile = tools_directory / "Shape"
        bits_directory: PathFile = tools_directory / "Bit"
        libraries_directory: PathFile = tools_directory / "Library"

        shapes: FabShapes = FabShapes.read(shapes_directory, tracing=next_tracing)
        bits: FabBits = FabBits.read(bits_directory, shapes, tracing=next_tracing)
        libraries: FabLibraries = FabLibraries.read(
            libraries_directory, bits, tracing=next_tracing)
        _ = libraries
        if tracing:
            print(f"{tracing}<=FabLibrarires._unit_tests()")


# FabBits
@dataclass(frozen=True)
class FabBits(object):
    """FabBits: A collection FabBit's that corresponds to a `Tools/Bit/` sub-directory..

    Attributes:
    * *BitsDirectory*: (PathFile): The path to the `Tools/Bit/` sub-directory.
    * *Bits* (Tuple[FabBit, ...]): The associated FabBit's in name sorted order.
    * *Names* (Tuple[str, ...]): The sorted FabBit names.

    Constructor:
    * FabBits("Name", BitsPath, Bits, Names)
    """

    BitsPath: PathFile
    Bits: Tuple[FabBit, ...]
    Names: Tuple[str, ...]

    # FabBits.__post_init__():
    def __post_init__(self) -> None:
        """Initialize a FabBits."""
        check_type("FabBits.BitsPath", self.BitsPath, PathFile)
        check_type("FabBits.Bits", self.Bits, Tuple[FabBit, ...])
        check_type("FabBits.Names", self.Names, Tuple[str, ...])

    # FabBits.read():
    @staticmethod
    def read(bits_directory: PathFile, shapes: FabShapes, tracing: str = "") -> "FabBits":
        """Read in a `Tools/Bit/` sub-directory.

        Arguments:
        * *bits_directory* (PathFile):
          The directory containing the `.fctb` Bit definitions.
        * *shapes* (BitShapes):
          The BitShapes object that corresponds to the `Tools/Shape` sub-directory.

        Returns:
        * (FabBits): The resulting FabBits that corresponds to the `Tools/Bit` sub-directory.

        """
        if tracing:
            print(f"{tracing}=>FabBits.read({str(bits_directory)}, *)")
        bit_templates: FabBitTemplates = FabBitTemplates.factory()
        bits_table: Dict[str, FabBit] = {}
        assert check_argument_types()
        assert bits_directory.is_dir(), f"FabBits.read(): {str(bits_directory)} is not a directory"

        bit_paths_table: Dict[str, PathFile] = {}
        bit_file_path: PathFile
        for bit_file_path in bits_directory.glob("*.fctb"):
            bit_paths_table[str(bit_file_path)] = bit_file_path
        sorted_bit_path_file_names: Tuple[str, ...] = tuple(sorted(bit_paths_table.keys()))
        if tracing:
            print(f"{tracing}{sorted_bit_path_file_names=}")

        bit_path_file_name: str
        index: int
        for index, bit_path_file_name in enumerate(sorted_bit_path_file_names):
            bit_path_file: PathFile = bit_paths_table[bit_path_file_name]
            # Read in the *bit_json* dictionary from *bit_file_path*:
            bit_name: str = bit_path_file.stem
            if tracing:
                print(f"{tracing}BitFile[{index}]: Processing {str(bit_path_file)} {bit_name}")
            bit_file: IO[str]
            bit_json_text: str
            with open(bit_path_file) as bit_file:
                bit_json_text = bit_file.read()
            try:
                bit_json: Any = json.loads(bit_json_text)
            except json.decoder.JSONDecodeError as json_error:  # pragma: no unit cover
                assert f"FabBits.read(): JSON read error {str(bit_path_file)}: {str(json_error)}"
            check_type("FabBits.read(): bit_json", bit_json, Dict[str, Any])
            assert "version" in bit_json, "FabBits.read(): No version found"
            parameters: Dict[str, Any] = bit_json["parameter"] if "parameter" in bit_json else {}
            attributes: Dict[str, Any] = bit_json["attribute"] if "attribute" in bit_json else {}
            _ = attributes

            # Do extract some value from *bit_json*, do sanity checking and get *shape_type*:
            version: Any = bit_json["version"]
            assert isinstance(version, int) and version == 2, "FabBits.read(): version is not 2"
            assert "shape" in bit_json, "FabBits.read(): No shape found"
            shape: Any = bit_json["shape"]
            assert isinstance(shape, str) and shape.endswith(".fcstd"), (
                f"FabBits.read(): {shape=} does not end in '.fcstd'")
            shape_name: str = shape[:-6]
            assert shape_name in shapes.Names, f"Shape {shape_name} not of {shapes.Names}"
            template: FabBitTemplate
            constructor: Any
            if shape_name == "ballend":
                template = bit_templates.BallEnd
                constructor = FabBallEndBit
            elif shape_name == "bullnose":
                template = bit_templates.BullNose
                constructor = FabBullNoseBit
            elif shape_name == "chamfer":
                template = bit_templates.Chamfer
                constructor = FabChamferBit
            elif shape_name == "dovetail":
                template = bit_templates.DoveTail
                constructor = FabSlittingSawBit
            elif shape_name == "drill":
                template = bit_templates.Drill
                constructor = FabDrillBit
            elif shape_name == "endmill":
                template = bit_templates.EndMill
                constructor = FabEndMillBit
            elif shape_name == "probe":
                template = bit_templates.Probe
                constructor = FabProbeBit
            elif shape_name == "slittingsaw":
                template = bit_templates.SlittingSaw
                constructor = FabSlittingSawBit
            elif shape_name == "thread-mill":
                template = bit_templates.ThreadMill
                constructor = FabThreadMillBit
                # The `Tools/Bit/5mm-thread-cutter.fctb` file doe not have a CuttingAngle parameter.
                # So we make one up here:
                if "CuttingAngle" not in parameters:
                    parameters["CuttingAngle"] = "60.000 °"
            elif shape_name == "v-bit":
                template = bit_templates.V
                constructor = FabVBit
            else:
                assert False, f"Unrecogniezed {shape_name=}"
            kwargs: Dict[str, Any] = template.kwargsFromJSON(bit_json, bit_path_file, shapes)
            if tracing:
                print(f"{tracing}{shape_name=} {constructor=}")
                # print(f"{tracing}{kwargs=}")
            bit: FabBit = constructor(**kwargs)
            bits_table[bit_name] = bit
            if tracing:
                print(f"{tracing}BitTable['{bit_name}']: {type(bit)=}")

        # Return the final FabBits object:
        sorted_names: Tuple[str, ...] = tuple(sorted(bits_table.keys()))
        sorted_bits: List[FabBit] = [bits_table[bit_name] for bit_name in sorted_names]
        for index, bit in enumerate(sorted_bits):
            assert sorted_names[index] == bit.Name, (
                f"[{index}] {sorted_names[index]=} != {bit.Name=}")
        # if tracing:
        #     print(f"{tracing}{sorted_names=}")
        #     print(f"{tracing}{sorted_bits=}")
        bits: FabBits = FabBits(bits_directory, tuple(sorted_bits), sorted_names)
        if tracing:
            print(f"{tracing}<=FabBits.read({str(bits_directory)}, *)=>|{len(sorted_names)}|")
        return bits

    # FabBits.lookup():
    def lookup(self, name: str) -> FabBit:
        """Look up a FabBit by name.

        Arguments:
        * *name* (str): The name of the FabBit.

        Returns:
        * (FabBit): The mataching FabBit.

        Raises:
        * (KeyError): If FabBit is  not present.

        """
        bit: FabBit
        for bit in self.Bits:
            if bit.Name == name:
                return bit
        raise KeyError(f"FabBits.lookup(): '{name}' is not one of {self.Names}.")

    # FabBits._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run FabBits unit tests."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabBits._unit_tests()")
        this_directory: PathFile = PathFile(__file__).parent
        tools_directory: PathFile = this_directory / "Tools"
        shapes_directory: PathFile = tools_directory / "Shape"
        bits_directory: PathFile = tools_directory / "Bit"
        shapes: FabShapes = FabShapes.read(shapes_directory)
        bits: FabBits = FabBits.read(bits_directory, shapes, tracing=next_tracing)
        index: int
        bit: FabBit
        for index, bit in enumerate(bits.Bits):
            if tracing:
                print(f"{tracing}Bit[{index}]: {bit.Name=}")
                lookup_bit: FabBit = bits.lookup(bit.Name)
                assert lookup_bit is bit, (bit.Name, bits.Names, lookup_bit, bit)

        # TODO: use *tools_directory*, *bit_directory*, and *shape_directory*.

        # library_file_path: PathFile = library_directory / "Default.fctl"
        # json_file: IO[str]
        # json_text: str
        # with open(library_file_path, "r") as json_file:
        #     json_text = json_file.read()

        # example_tools: Dict[str, FabBit] = FabBit._example_tools()

        # tools: FabBits = FabBits(Name="MyToolTable", Description="")

        # name: str
        # for name, tool in example_tools.items():
        #     tool_number += 1
        #     tools.add_tool(tool_number, tool)

        # my_tool_table_path: PathFile = PathFile(".") / "MyToolTable.json"
        # with open(my_tool_table_path, "w") as json_file:
        #     json_text = tools.combined_to_json("MyToolTable")
        #     json_file.write(json_text)

        if tracing:
            print(f"{tracing}<=FabBits._unit_tests()")


# Main program:
def main(tracing: str) -> None:
    """Main program that executes unit tests."""
    next_tracing: str = tracing + " " if tracing else ""
    if tracing:
        print(f"{tracing}=>main()")

    FabBallEndBit._unit_tests(tracing=next_tracing)
    FabBullNoseBit._unit_tests(tracing=next_tracing)
    FabChamferBit._unit_tests(tracing=next_tracing)
    FabDoveTailBit._unit_tests(tracing=next_tracing)
    FabDrillBit._unit_tests(tracing=next_tracing)
    FabEndMillBit._unit_tests(tracing=next_tracing)
    FabProbeBit._unit_tests(tracing=next_tracing)
    FabSlittingSawBit._unit_tests(tracing=next_tracing)
    FabThreadMillBit._unit_tests(tracing=next_tracing)
    FabVBit._unit_tests(tracing=next_tracing)
    FabBits._unit_tests(tracing=next_tracing)
    FabLibrary._unit_tests(tracing=next_tracing)
    FabLibraries._unit_tests(tracing=next_tracing)
    FabBits._unit_tests(tracing=next_tracing)
    if tracing:
        print(f"{tracing}<=main()")


if __name__ == "__main__":
    main(tracing=" ")
