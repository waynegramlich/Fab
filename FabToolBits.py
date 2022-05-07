#!/usr/bin/env python3
"""FabToolBits: Toop Bit classes.

This module provides one class for each different kind of supported tool bit.
Instatiations of these tool bits live in the `.../Tools/Bit/` directory with a suffix of `.fctb`.
Each of the classes below is a sub-class of the FabBit class defined in the FabToolTemplates module.

The classes are:
  * FabBallEndBit: This corresponds to `Tools/Shape/ballend.fcstd`.
  * FabBullNoseBit: This corresponds to `Tools/Shape/bullnose.fcstd`.
  * FabChamferBit: This corresponds to `Tools/Shape/chamfer.fcstd`.
  * FabDoveTailBit: This corresponds to `Tools/Shape/dovetail.fcstd`.
  * FabDrillBit: This corresponds to `Tools/Shape/drill.fcstd`.
  * FabEndMillBit: This corresponds to `Tools/Shape/endmill.fcstd`.
  * FabProbeBit: This corresponds to `Tools/Shape/probe.fcstd`.
  * FabSlittingSawBit: This corresponds to `Tools/Shape/slittingsaw.fcstd`.
  * FabThreadMillBit: This corresponds to `Tools/Shape/thread-mill.fcstd`.
  * FabVBit: This corresponds to `Tools/Shape/v-bit.fcstd`.

The FabBit sub-class defines the following 4 attributes which is present in every FabBit sub-class:
  * *Name* (str): The name of Ball End bit.
  * *BitFile* (PathFile): The `.fctb` file.
  * *Shape* (FabShape): The associated `.fcstd` shape.
  * *Attributes* (FabAttributes): Any associated attributes.
Both FabShape and FabAttributes are also defined in the FabTemplates module as well.

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

from typeguard import check_type
from typing import Any, Union
from dataclasses import dataclass
from FabToolTemplates import FabAttributes, FabBit, FabBitTemplates


# FabBallEndBit:
@dataclass(frozen=True)
class FabBallEndBit(FabBit):
    """FabBallEndBit: An ball end bit template.

    Attributes:
    * *Name* (str): The name of Ball End bit.
    * *BitFile* (PathFile): The ball end `.fctb` file.
    * *Shape* (FabShape): The associated ball end `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated ball end attributes.
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
    """FabBullNoseBit: An bull nose bit template.

    Attributes:
    * *Name* (str): The name of Bull Nose bit.
    * *BitFile* (PathFile): The bull nose `.fctb` file.
    * *Shape* (FabShape): The associated bull nose `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated bull nose attributes.
    * *CuttingEdgeHeight* (Union[str, float]): The bull nose cutting edge height.
    * *Diameter* (Union[str, float]): The bull nose cutter diameter.
    * *FlatRadius* (Union[str, float]): The flat radius of the bull nose cutter.
    * *Length* (Union[str, float]): The total length of the bull nose cutter.
    * *ShankDiameter: (Union[str, float]): The bull nose shank diameter.

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
    """FabChamferBit: An chamfer bit template.

    Attributes:
    * *Name* (str): The name of Chamfer bit.
    * *BitFile* (PathFile): The `.fctb` file.
    * *Shape* (FabShape): The associated `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated attributes.
    * *CuttingEdgeAngle* (Union[str, float]): The chamfer bit cutting edge angle.
    * *CuttingEdgeHeight* (Union[str, float]): The chamfer bit cutting edge height.
    * *Diameter* (Union[str, float]): The chamfer bit outer diameter.
    * *Length* (Union[str, float]): The total length of the chamfer bit.
    * *ShankDiameter: (Union[str, float]): The chamfer bit shank diameter.
    * *TipDiameter* (Union[str, float]): The tip radius of the chamfer bit.

    Constructor:
    * FabChamferBit("Name", BitFile, Shape, Attributes,
      CuttingEdgeAngle, CuttingEdgeHeight, Diameter, Length, ShankDiameter, TipDiameter)
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
    """FabDoveTailBit: An dove tail bit template.

    Attributes:
    * *Name* (str): The name of dove tail bit.
    * *BitFile* (PathFile): The dove tail `.fctb` file.
    * *Shape* (FabShape): The associated dove tail `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated dove tail attributes.
    * *CuttingEdgeAngle* (Union[str, float]): The dove tail cutting edge angle.
    * *CuttingEdgeHeight* (Union[str, float]): The dove tale cutting edge height.
    * *Diameter* (Union[str, float]): The dove tail outer diameter.
    * *Length* (Union[str, float]): The dove tail total length.
    * *NeckDiameter* (Union[str, float]): The diameter of the neck between the dove tail and shank.
    * *NeckHeight* (Union[str, float]):
       The height of the neck between the dove tail cutter and shank.
    * *ShankDiameter: (Union[str, float]): The dove tail shank diameter.
    * *TipDiameter* (Union[str, float]): The tip radius of the dove tail.

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
    """FabDrillBit: An drill bit template.

    Attributes:
    * *Name* (str): The name of drill bit.
    * *BitFile* (PathFile): The drill bit `.fctb` file.
    * *Shape* (FabShape): The associated drill bit `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated drill bit attributes.
    * *Diameter* (Union[str, float]): The drill bit outer diameter.
    * *Length* (Union[str, float]): The total length of the drill bit.
    * *TipAngle: (Union[str, float]): The drill bit tip point angle.

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
    * *Name* (str): The name of end mill bit.
    * *BitFile* (PathFile): The end mill `.fctb` file.
    * *Shape* (FabShape): The associated end mill `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated end mill attributes.
    * *CuttingEdgeHeight* (Union[str, float]): The end mill cutting edge height.
    * *Diameter* (Union[str, float]): The end mill cutter diameter.
    * *Length* (Union[str, float]): The total length of the end mill.
    * *ShankDiameter: (Union[str, float]): The end mill shank diameter.

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
    """FabProbeBit: A probe bit template.

    Attributes:
    * *Name* (str): The name of probe bit.
    * *BitFile* (PathFile): The probe `.fctb` file.
    * *Shape* (FabShape): The associated probe `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated probe attributes.
    * *Diameter* (Union[str, float]): The probe ball diameter.
    * *Length* (Union[str, float]): The total length of the probe.
    * *ShaftDiameter: (Union[str, float]): The probe shaft diameter.

    Constructor:
    * FabProbeBit("Name", BitFile, Shape, Attributes, Diameter, Length, ShaftDiameter)
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
    """FabSlittingSawBit: An slitting saw bit.

    Attributes:
    * *Name* (str): The name of slitting saw bit.
    * *BitFile* (PathFile): The slitting saw `.fctb` file.
    * *Shape* (FabShape): The associated slitting saw `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated slitting saw attributes.
    * *BladeThickness* (Union[str, float]): The slitting saw blade thickness.
    * *CapDiameter* (Union[str, float]): The slitting saw end cab diameter.
    * *CapHeight* (Union[str, float]): The slitting end end cab height.
    * *Diameter* (Union[str, float]): The slitting saw blade diameter.
    * *Length* (Union[str, float]): The length of the slitting saw.
    * *ShankDiameter: (Union[str, float]): The slitting saw shank diameter.

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
    * *BitFile* (PathFile): The thread mill `.fctb` file.
    * *Shape* (FabShape): The associated thread mill `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated thread mill attributes.
    * *CuttingAngle* (Union[str, float]): The thread mill point angle.
    * *Crest* (Union[str, float]): The thread mill crest thickness.
    * *Diameter* (Union[str, float]): The thread mill outer diameter.
    * *Length* (Union[str, float]): The total length of the thread mill cutter.
    * *NeckDiameter* (Union[str, float]): The diameter of the neck between the cutter and shank
    * *NeckLength* (Union[str, float]): The height of the neck between the cutter and shank
    * *ShankDiameter: (Union[str, float]): The thread mill shank diameter.

    Constructor:
    * FabThreadMillBit("Name", BitFile, Shape, Attributes,
      CuttingAngle, Crest, Diameter, Length, NeckDiameter, NeckLength, ShankDiameter)
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
    """FabVBit: An V bit template.

    Attributes:
    * *Name* (str): The name of V bit.
    * *BitFile* (PathFile): The V bit `.fctb` file.
    * *Shape* (FabShape): The associated V bit `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated V bit  attributes.
    * *CuttingEdgeAngle* (Union[str, float]): The V bit cutting edge angle.
    * *CuttingEdgeHeight* (Union[str, float]): The V bit cutting edge height.
    * *Diameter* (Union[str, float]): The V bit outer diameter.
    * *Length* (Union[str, float]): The total length of the V bit.
    * *ShankDiameter: (Union[str, float]): The V bit shank diameter.
    * *TipDiameter* (Union[str, float]): The tip radius of the V bit

    Constructor:
    * FabVBit("Name", BitFile, Shape, Attributes,
      CuttingEdgeAngle, CuttingEdgeHeight, Diameter, Length, ShankDiameter, TipDiameter)
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
    if tracing:
        print(f"{tracing}<=main()")


if __name__ == "__main__":
    main(tracing=" ")
