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

from dataclasses import dataclass
import math
from typeguard import check_type
from typing import Any, Optional, Tuple, Union

from FabToolTemplates import FabAttributes, FabBit, FabBitTemplates


# FabBallEndBit:
@dataclass(frozen=True)
class FabBallEndBit(FabBit):
    """FabBallEndBit: An ball end bit template.

    Attributes:
    * *Name* (str): The name of Ball End bit.
    * *BitStem* (str): The stem of the ball end `.fctb` file name.
    * *ShapeStem* (str): The stem of the associated ball end `.fcstd` shape (e.g. "ballend".)
    * *Attributes* (FabAttributes): Any associated ball end attributes.
    * *CuttingEdgeHeight* (Union[str, float]): The ball end cutting edge height.
    * *Diameter* (Union[str, float]): The ball end cutter diameter.
    * *Length* (Union[str, float]): The total length of the ball end.
    * *ShankDiameter: (Union[str, float]): The ball end shank diameter.

    Constructor:
    * FabBallEndBit("Name", "BitStem", "ShapeStem", Attributes,
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

    # FabBallEndBit.getOperationKinds():
    def getOperationKinds(self) -> Tuple[str, ...]:
        """Return the kind of operations by a FabBallEndBit.

        Returns:
        * (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)
        """
        return ()  # pragma: no unit cover

    # FabBallEndBit.getExample():
    @staticmethod
    def getExample() -> "FabBallEndBit":
        """Return an example FabBallEndBit."""
        ball_end_bit: Any = FabBitTemplates.getExample(FabBallEndBit)
        assert isinstance(ball_end_bit, FabBallEndBit)
        return ball_end_bit

    # FabBallEndBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabBallEndBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabBallEndBit._unit_tests()")
        ball_end_bit: FabBallEndBit = FabBallEndBit.getExample()
        assert ball_end_bit.Name == "6mm Ball End", ball_end_bit.Name
        assert ball_end_bit.BitStem == "6mm_Ball_End"
        assert ball_end_bit.ShapeStem == "ballend"
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
    * *BitStem* (str): The stem of the bull nose `.fctb` file.
    * *ShapeStem* (str): The stem of associated bull nose `.fcstd` shape (e.g. "bullnose".)
    * *Attributes* (FabAttributes): Any associated bull nose attributes.
    * *CuttingEdgeHeight* (Union[str, float]): The bull nose cutting edge height.
    * *Diameter* (Union[str, float]): The bull nose cutter diameter.
    * *FlatRadius* (Union[str, float]): The flat radius of the bull nose cutter.
    * *Length* (Union[str, float]): The total length of the bull nose cutter.
    * *ShankDiameter: (Union[str, float]): The bull nose shank diameter.

    Constructor:
    * FabBullNoseBit("Name", "BitStem", "ShapeStem", Attributes,
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

    # FabBullNoseBit.getOperationKinds():
    def getOperationKinds(self) -> Tuple[str, ...]:
        """Return the kind of operations by a FabBullNoseBit.

        Returns:
        * (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)
        """
        return ()  # pragma: no cover

    # FabBullNoseBit.getExample():
    @staticmethod
    def getExample() -> "FabBullNoseBit":
        """Return an example FabBullNoseBit."""
        bull_nose_bit: Any = FabBitTemplates.getExample(FabBullNoseBit)
        assert isinstance(bull_nose_bit, FabBullNoseBit)
        return bull_nose_bit

    # FabBullNoseBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabBullNoseBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabBullNoseBit._unit_tests()")
        bull_nose_bit: FabBullNoseBit = FabBullNoseBit.getExample()
        assert bull_nose_bit.Name == "6 mm Bull Nose"
        assert bull_nose_bit.BitStem == "6mm_Bullnose"
        assert bull_nose_bit.ShapeStem == "bullnose"
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
    * *BitStem* (str): The stem of chamfer`.fctb` file name.
    * *ShapeStem* (str): The stem of associated chamfer `.fcstd` shape (e.g. "chamfer".)
    * *Attributes* (FabAttributes): Any associated chamfer bit attributes.
    * *CuttingEdgeAngle* (Union[str, float]): The chamfer bit cutting edge angle.
    * *CuttingEdgeHeight* (Union[str, float]): The chamfer bit cutting edge height.
    * *Diameter* (Union[str, float]): The chamfer bit outer diameter.
    * *Length* (Union[str, float]): The total length of the chamfer bit.
    * *ShankDiameter: (Union[str, float]): The chamfer bit shank diameter.
    * *TipDiameter* (Union[str, float]): The tip radius of the chamfer bit.

    Constructor:
    * FabChamferBit("Name", "BitStem", "ShapeStem", Attributes,
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

    # FabChamferBit.getOperationKinds():
    def getOperationKinds(self) -> Tuple[str, ...]:
        """Return the kind of operations by a FabChamferBit.

        Returns:
        * (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)
        """
        return ("upper_chamfer",)  # pragma: no unit cover

    # FabChamferBit.getExample():
    @staticmethod
    def getExample() -> "FabChamferBit":
        """Return an example FabChamferBit."""
        chamfer_bit: Any = FabBitTemplates.getExample(FabChamferBit)
        assert isinstance(chamfer_bit, FabChamferBit)
        return chamfer_bit

    # FabChamferBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabChamferBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabChamferBit._unit_tests()")
        chamfer_bit: FabChamferBit = FabChamferBit.getExample()
        assert chamfer_bit.Name == "45 Deg. Chamfer"
        assert chamfer_bit.BitStem == "45degree_chamfer"
        assert chamfer_bit.ShapeStem == "chamfer"
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
    * *BitStem* (str): The stem of dove tail `.fctb` file.
    * *ShapeStem* (str): The stem associated dove tail `.fcstd` shape (e.g. "dovetail".)
    * *Attributes* (FabAttributes): Any associated dove tail attributes.
    * *CuttingEdgeAngle* (Union[str, float]): The dove tail cutting edge angle.
    * *CuttingEdgeHeight* (Union[str, float]): The dove tale cutting edge height.
    * *Diameter* (Union[str, float]): The dove tail outer diameter.
    * *Length* (Union[str, float]): The dove tail total length.
    * *NeckDiameter* (Union[str, float]): The diameter of the neck between the dove tail and shank.
    * *NeckHeight* (Union[str, float]):
       The height of the neck between the dove tail cutter and shank.
    * *ShankDiameter: (Union[str, float]): The dove tail shank diameter.
    * *TipDiameter* (Union[str, float]):
      In theory, tip diameter of the dove tail.  In practice, *Diameter* is what is actually used.

    Constructor:
    * FabDoveTailBit("Name", "BitStem", "ShapeStem", Attributes, CuttingEdgeAngle,
      CuttingEdgeHeight, Diameter, Length, NeckDiameter, NeckHeight,  ShankDiameter, TipDiameter)
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
        check_type("FabDoveTailBit.NeckHieght", self.NeckHeight, Union[float, str])
        check_type("FabDoveTailBit.NeckDiameter", self.NeckDiameter, Union[float, str])
        check_type("FabDoveTailBit.ShankDiameter", self.ShankDiameter, Union[float, str])
        check_type("FabDoveTailBit.TipDiameter", self.TipDiameter, Union[float, str])

    # FabDoveTailBit.getExample():
    @staticmethod
    def getExample() -> "FabDoveTailBit":
        """Return an example FabChamferBit."""
        dove_tail_bit: Any = FabBitTemplates.getExample(FabDoveTailBit)
        assert isinstance(dove_tail_bit, FabDoveTailBit)
        return dove_tail_bit

    # FabDDoveTailBit.getOperationKinds():
    def getOperationKinds(self) -> Tuple[str, ...]:
        """Return the kind of operations by a FabDoveTailBit.

        Returns:
        * (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)
        """
        return ("lower_chamfer",)

    # FabDoveTailBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabDoveTailBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabDoveTailBit._unit_tests()")
        dove_tail_bit: FabDoveTailBit = FabDoveTailBit.getExample()
        assert dove_tail_bit.Name == "no_dovetail_name_yet"
        assert dove_tail_bit.BitStem == "no_dovetail_stem_yet"
        assert dove_tail_bit.ShapeStem == "dovetail"
        assert dove_tail_bit.CuttingEdgeAngle == "60.000 °"
        assert dove_tail_bit.CuttingEdgeHeight == "9.000 mm"
        assert dove_tail_bit.Diameter == "19.050 mm"
        assert dove_tail_bit.Length == "54.200 mm"
        assert dove_tail_bit.NeckDiameter == "8.000 mm"
        assert dove_tail_bit.NeckHeight == "5.000 mm"
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
    * *BitStem* (str): The stem of drill bit `.fctb` file.
    * *ShapeStem* (str): The stem of associated drill bit `.fcstd` shape (e.g. "drill".)
    * *Attributes* (FabAttributes): Any associated drill bit attributes.
    * *Diameter* (Union[str, float]): The drill bit outer diameter.
    * *Length* (Union[str, float]): The total length of the drill bit.
    * *TipAngle: (Union[str, float]): The drill bit tip point angle.

    Constructor:
    * FabDrillBit("Name", "BitStem", "ShapeStem", Attributes, Diameter, Length, TipAngle)

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

    # FabDrillBit.gFetExample():
    @staticmethod
    def getExample() -> "FabDrillBit":
        """Return an example FabDrillBit."""
        drill_bit: Any = FabBitTemplates.getExample(FabDrillBit)
        assert isinstance(drill_bit, FabDrillBit)
        return drill_bit

    # FabDrillBit.getOperationKinds():
    def getOperationKinds(self) -> Tuple[str, ...]:
        """Return the kind of operations by a FabDrillBit.

        Returns:
        * (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)
        """
        return ("drill",)

    # FabDrillBit.getBitPriority():
    def getBitPriority(
            self, operation_kind: str, depth: float, tracing: str = "") -> Optional[float]:
        """Return operation priority for a FabEndMillBit.

        Arguments:
        * *operation_kind* (str): The kind of operation (e.g. "pocket", "drill", etc.).
        * *depth* (str): Depth of drill operation.

        Returns:
        * (Optional[float]): The priority as a negative number, where more negative numbers
          have a higher priority.  None is returned if there is bit does not support either
          the operation kind or depth.
        """
        operation_kinds: Tuple[str, ...] = self.getOperationKinds()
        assert operation_kind in operation_kinds, (
            f"FabEndMillBit.getBitPriority(): {operation_kind} is not one of {operation_kinds}")
        priority: Optional[float] = None
        diameter: Union[float, int] = self.getNumber("Diameter")
        flutes: Union[float, int] = self.getNumber("Flutes")
        cutting_edge_length: Union[float, int] = self.getNumber("Length")
        priority = -diameter * flutes * cutting_edge_length
        if tracing:
            print(f"{tracing}FabDrillBit.getBitPriority('{operation_kind}')=>{priority}")
        return priority

    # FabDrillBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabDrillBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabDrillBit._unit_tests()")
        drill_bit: Any = FabDrillBit.getExample()
        assert drill_bit.Name == "5mm Drill"
        assert drill_bit.BitStem == "5mm_Drill"
        assert drill_bit.ShapeStem == "drill"
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
    * *BitStem* (str): The stem of the end mill `.fctb` file.
    * *ShapeStem* (str): The stem of the associated end mill `.fcstd` shape (e.g. "endmill".)
    * *Attributes* (FabAttributes): Any associated end mill attributes.
    * *CuttingEdgeHeight* (Union[str, float]): The end mill cutting edge height.
    * *Diameter* (Union[str, float]): The end mill cutter diameter.
    * *Length* (Union[str, float]): The total length of the end mill.
    * *ShankDiameter: (Union[str, float]): The end mill shank diameter.

    Constructor:
    * FabEndMillBit("Name", "BitStem", "ShapeStem", Attributes,
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

    # FabEndMillBit.getOperationKinds():
    def getOperationKinds(self) -> Tuple[str, ...]:
        """Return the kind of operations by a FabEndMillBit.

        Returns:
        * (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)
        """
        return ("contour", "pocket")

    # FabEndMillBit.getExample():
    @staticmethod
    def getExample() -> "FabEndMillBit":
        """Return an example FabEndMillBit."""
        end_mill_bit: Any = FabBitTemplates.getExample(FabEndMillBit)
        assert isinstance(end_mill_bit, FabEndMillBit)
        return end_mill_bit

    # FabEndMillBit.getBitPriority():
    def getBitPriority(
            self, operation_kind: str, depth: float, tracing: str = "") -> Optional[float]:
        """Return operation priority for a FabEndMillBit.

        Arguments:
        * *operation_kind* (str): The kind of operation (e.g. "pocket", "drill", etc.).
        * *depth* (str):
          Depth of end-mill operation or 0.0 for a "generic" priority independent of depth.

        Returns:
        * (Optional[float]): The priority as a negative number, where more negative numbers
          have a higher priority.  None is returned if there is bit does not support either
          the *operation_kind* or *depth*.
        """
        operation_kinds: Tuple[str, ...] = self.getOperationKinds()
        assert operation_kind in operation_kinds, (
            f"FabEndMillBit.getBitPriority(): {operation_kind} is not one of {operation_kinds}")

        # Compute an initial *single_pass_priority* independent of *depth*:
        diameter: Union[float, int] = self.getNumber("Diameter")
        flutes: Union[float, int] = self.getNumber("Flutes")
        cutting_edge_length: Union[float, int] = self.getNumber("CuttingEdgeHeight")
        single_pass_priority = diameter * flutes * cutting_edge_length

        # When *depth* is specified, adjust *priority*:
        priority: Optional[float] = None
        if depth <= 0.0:
            priority = -single_pass_priority
        elif depth <= cutting_edge_length:
            # 1/3 *diameter* is an ad hoc step depth:
            steps: int = math.ceil(depth / (diameter / 3.0))
            priority = -(float(steps) * single_pass_priority)
            assert priority < 0.0, priority
        if tracing:
            print(f"{tracing}<=>FabEndMillBit.getBitPriority('{operation_kind}')=>{priority}")
        return priority

    # FabEndMillBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabEndMillBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabEndMillBit._unit_tests()")

        end_mill_bit: FabEndMillBit = FabEndMillBit.getExample()
        assert end_mill_bit.Name == "5mm Endmill"
        assert end_mill_bit.BitStem == "5mm_Endmill"
        assert end_mill_bit.ShapeStem == "endmill"
        assert end_mill_bit.CuttingEdgeHeight == "30.000 mm"
        assert end_mill_bit.Diameter == "5.000 mm"
        assert end_mill_bit.Length == "50.000 mm"
        assert end_mill_bit.ShankDiameter == "3.000 mm"
        assert end_mill_bit.Attributes == FabAttributes.fromJSON({
            "Flutes": 2,
            "Material": "HSS",
        }), end_mill_bit.Attributes

        generic_priority: Optional[float] = end_mill_bit.getBitPriority("pocket", 0.0)
        actual_priority: Optional[float] = end_mill_bit.getBitPriority("pocket", 10.0)
        too_deep_priority: Optional[float] = end_mill_bit.getBitPriority("pocket", 100.0)
        assert isinstance(generic_priority, float)
        assert generic_priority == -300.0
        assert isinstance(actual_priority, float)
        assert actual_priority == -1800.0
        assert too_deep_priority is None

        if tracing:
            print(f"{tracing}<=FabEndMillBit._unit_tests()")


# FabProbeBit:
@dataclass(frozen=True)
class FabProbeBit(FabBit):
    """FabProbeBit: A probe bit template.

    Attributes:
    * *Name* (str): The name of probe bit.
    * *BitStem* (str): The stem of the probe `.fctb` file.
    * *ShapeStem* (str): The stem of the associated probe `.fcstd` shape.
    * *Attributes* (FabAttributes): Any associated probe attributes.
    * *Diameter* (Union[str, float]): The probe ball diameter.
    * *Length* (Union[str, float]): The total length of the probe.
    * *ShaftDiameter: (Union[str, float]): The probe shaft diameter.

    Constructor:
    * FabProbeBit("Name", "BitStem", "ShapeStem", Attributes, Diameter, Length, ShaftDiameter)
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

    # FabProbeBit.getOperationKinds():
    def getOperationKinds(self) -> Tuple[str, ...]:
        """Return the kind of operations by a FabProbeBit.

        Returns:
        * (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)
        """
        return ()  # pragma: no unit cover

    # FabProbeBit.getExample():
    @staticmethod
    def getExample() -> "FabProbeBit":
        """Return an example FabProbeBit."""
        probe_bit: Any = FabBitTemplates.getExample(FabProbeBit)
        assert isinstance(probe_bit, FabProbeBit)
        return probe_bit

    # FabProbeBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabProbeBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabProbeBit._unit_tests()")
        probe_bit: FabProbeBit = FabProbeBit.getExample()
        assert probe_bit.Name == "Probe"
        assert probe_bit.BitStem == "probe"
        assert probe_bit.ShapeStem == "probe"
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
    * *BitStem* (str): The stem of slitting saw `.fctb` file.
    * *ShapeStem* (str):
      The stem of the associated slitting saw `.fcstd` shape (e.g. "slittingsaw".)
    * *Attributes* (FabAttributes): Any associated slitting saw attributes.
    * *BladeThickness* (Union[str, float]): The slitting saw blade thickness.
    * *CapDiameter* (Union[str, float]): The slitting saw end cab diameter.
    * *CapHeight* (Union[str, float]): The slitting end end cab height.
    * *Diameter* (Union[str, float]): The slitting saw blade diameter.
    * *Length* (Union[str, float]): The length of the slitting saw.
    * *ShankDiameter: (Union[str, float]): The slitting saw shank diameter.

    Constructor:
    * FabSlittingSawBit("Name", "BitStem", "ShapeStem", Attributes,
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

    # FabSlittingSawBit.getOperationKinds():
    def getOperationKinds(self) -> Tuple[str, ...]:
        """Return the kind of operations by a FabSlittingSawBit.

        Returns:
        * (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)
        """
        return ()  # pragma: no unit cover

    # FabSlittingSawBit.getExample():
    @staticmethod
    def getExample() -> "FabSlittingSawBit":
        """Return an example FabSlittingSawBit."""
        slitting_saw_bit: Any = FabBitTemplates.getExample(FabSlittingSawBit)
        assert isinstance(slitting_saw_bit, FabSlittingSawBit)
        return slitting_saw_bit

    # FabSlittingSawBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabSlittingSawBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabSlittingSawBit._unit_tests()")
        slitting_saw_bit: FabSlittingSawBit = FabSlittingSawBit.getExample()
        assert slitting_saw_bit.Name == "Slitting Saw"
        assert slitting_saw_bit.BitStem == "slittingsaw"
        assert slitting_saw_bit.ShapeStem == "slittingsaw"
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
    * *BitStem* (str): The stem of thread mill `.fctb` file.
    * *ShapeStem* (str): The stem of the associated thread mill `.fcstd` shape (e.g. .
    * *Attributes* (FabAttributes): Any associated thread mill attributes.
    * *CuttingAngle* (Union[str, float]): The thread mill point angle.
    * *Crest* (Union[str, float]): The thread mill crest thickness.
    * *Diameter* (Union[str, float]): The thread mill outer diameter.
    * *Length* (Union[str, float]): The total length of the thread mill cutter.
    * *NeckDiameter* (Union[str, float]): The diameter of the neck between the cutter and shank
    * *NeckLength* (Union[str, float]): The height of the neck between the cutter and shank
    * *ShankDiameter: (Union[str, float]): The thread mill shank diameter.

    Constructor:
    * FabThreadMillBit("Name", "BitStem", "ShapeStem", Attributes,
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

    # FabThreadMillBit.getOperationKinds():
    def getOperationKinds(self) -> Tuple[str, ...]:
        """Return the kind of operations by a FabVBit.

        Returns:
        * (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)
        """
        return ("lower_chamfer", "upper_chamfer")

    # FabThreadMillBit.getBitPriority():
    def getBitPriority(
            self, operation_kind: str, depth: float, tracing: str = "") -> Optional[float]:
        """Return operation priority for a FabEndThreadMillBit.

        Arguments:
        * *operation_kind* (str): The kind of operation (e.g. "pocket", "drill", etc.).
        * *depth* (str): Depth of drill operation.

        Returns:
        * (Optional[float]): The priority as a negative number, where more negative numbers
          have a higher priority.  None is returned if there is bit does not support either
          the operation kind or depth.
        """
        operation_kinds: Tuple[str, ...] = self.getOperationKinds()
        assert operation_kind in operation_kinds, (
            f"FabThreadMillBit.getBitPriority(): {operation_kind} is not one of {operation_kinds}")
        priority: Optional[float] = None
        diameter: Union[float, int] = self.getNumber("Diameter")
        flutes: Union[float, int] = self.getNumber("Flutes")
        cutting_edge_length: Union[float, int] = self.getNumber("Length")
        priority = -diameter * flutes * cutting_edge_length
        if tracing:
            print(f"{tracing}FabThreadMillBit.getBitPriority('{operation_kind}')=>{priority}")
        return priority

    # FabThreadMillBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabThreadMillBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabThreadMillBit._unit_tests()")
        thread_mill_bit: Any = FabBitTemplates.getExample(FabThreadMillBit)
        assert thread_mill_bit.Name == "5mm-thread-cutter"
        assert thread_mill_bit.BitStem == "5mm-thread-cutter"
        assert thread_mill_bit.ShapeStem == "thread-mill"
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
    * *BitStem* (str): The stem of V bit `.fctb` file.
    * *ShapeStem* (str): The stem of the associated V bit `.fcstd` shape (e.g. "v-bit".)
    * *Attributes* (FabAttributes): Any associated V bit  attributes.
    * *CuttingEdgeAngle* (Union[str, float]): The V bit cutting edge angle.
    * *CuttingEdgeHeight* (Union[str, float]): The V bit cutting edge height.
    * *Diameter* (Union[str, float]): The V bit outer diameter.
    * *Length* (Union[str, float]): The total length of the V bit.
    * *ShankDiameter: (Union[str, float]): The V bit shank diameter.
    * *TipDiameter* (Union[str, float]): The tip diameter of the V bit

    Computed Attributes:
    * *AngleCuttingEdgeHeight* (float): The angled cutting edge height.
    * *VerticalCuttingEdgeHeight* (float): The angled cutting edge height.

    Constructor:
    * FabVBit("Name", "BitStem", "ShapeStem", Attributes,
      CuttingEdgeAngle, CuttingEdgeHeight, Diameter, Length, ShankDiameter, TipDiameter)

    Crude ASCII bit diagram:
    ```
               |                       |
               |<--------- D --------->|
               |                       |
               |    +*************+ <--+-------------
               |    *             *    |          ^
               |    *             *    |          |
               |    *             *    |          |
               |    *             *    |          |
                    *             *               |
         ----- +****+             +****+ -------  |
           ^   *                       *    ^     |
           |   *                       *    |     |
           |   *                       *   VCEH   |
           |   *                       *    |     |
           |   *                       *    v     |
           |   +             A.........B -------  L
          CEH   *            .        *     ^     |
           |     *           .       *      |     |
           |      *                 *       |     |
           |       *<--<CEA--+---->*        |     |
           |        *        .    *        ACEH   |
           |         *       .   *          |     |
           |          *      .  *           |     |
           |           *     . *            |     |
           v            *     *             v     v
         --------------- +***C ----------------------

                         |   |
                  TD --->|   |<---
                         |   |

        D = Diameter Diameter
        CEH = Cutting Edge Height
        VCEH = Vertical Cutting Edge Height
        ACEH = Angle Cutting Edge Height (computed from CEA, D
        TD = Tip Diameter
        <CEA = Cutting Edge Angle (i.e. the point angle)
        L = Length (i.e. OAL = Overall Length)
        A/B/C = Points on right triangle where |AC|=ACEH and |AB|=(D-TD)/2
    ```
    """

    CuttingEdgeAngle: Union[str, float]
    CuttingEdgeHeight: Union[str, float]
    Diameter: Union[str, float]
    Length: Union[str, float]
    ShankDiameter: Union[str, float]
    TipDiameter: Union[str, float]

    # FabVBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the Fantail."""
        super().__post_init__()
        check_type("FabVBit.CuttingEdgeAngle", self.CuttingEdgeAngle, Union[float, str])
        check_type("FabVBit.CuttingEdgeHeight", self.CuttingEdgeHeight, Union[float, str])
        check_type("FabVBit.Diameter", self.Diameter, Union[float, str])
        check_type("FabVBit.Length", self.Length, Union[float, str])
        check_type("FabVBit.ShankDiameter", self.ShankDiameter, Union[float, str])
        check_type("FabVBit.TipDiameter", self.TipDiameter, Union[float, str])

    # FabVBit.AngleCuttingEdgeHeight():
    @property
    def AngleCuttingEdgeHeight(self) -> float:
        """Return the height of the FabVBit cutting edge."""
        # Compute *AngleCuttingHeight*.
        # The triangle vertcies the triangle the interest are labeled A, B, C in the diagram above.
        # Notation: <ABC = the angle from A to C with B as the vertex.
        #
        # (1) |AC|/sin(<ABC) = |AB|/sin(<ACB)           # Law of sines
        # (1) |AC| = |AB| * sin(<ABC)) / sin(<ACB)      # Rearrange (1)
        # (2) <ABC = 90° - <ACB                         # Right triangle
        # (3) |AC| = sin(<ABC) * |AB|/sin(<ACB)         # From (1)
        # (4) |AC| = sin(90° - <ACB) * |AB|/sin(<ACB)   # Substitute (2) into (3)
        radius: float = self.getNumber("Diameter") / 2.0
        tip_radius: float = self.getNumber("TipDiameter") / 2.0  # |AB|
        slant_angle: float = self.getNumber("CuttingEdgeAngle") / 2.0  # < ACB
        degrees90: float = math.pi / 2.0  # 180°
        xxx: float = radius - tip_radius
        return xxx * math.sin(degrees90 - slant_angle) / math.sin(slant_angle)  # Using (4)

    # FabVBit.getOperationKinds():
    def getOperationKinds(self) -> Tuple[str, ...]:
        """Return the kind of operations by a FabVBit.

        Returns:
        * (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)
        """
        return ("contour", "countersink", "upper_chamfer")

    # FabDrillBit.getBitPriority():
    def getBitPriority(
            self, operation_kind: str, depth: float, tracing: str = "") -> Optional[float]:
        """Return operation priority for a FabEndMillBit.

        Arguments:
        * *operation_kind* (str): The kind of operation (e.g. "pocket", "drill", etc.).
        * *depth* (str): Depth of drill operation.

        Returns:
        * (Optional[float]): The priority as a negative number, where more negative numbers
          have a higher priority.  None is returned if there is bit does not support either
          the operation kind or depth.
        """
        operation_kinds: Tuple[str, ...] = self.getOperationKinds()
        assert operation_kind in operation_kinds, (
            "FabEndMillBit.getDrillBitPriority(): "
            f"{operation_kind} is not one of {operation_kinds}")
        priority: Optional[float] = None
        diameter: Union[float, int] = self.getNumber("Diameter")
        flutes: Union[float, int] = self.getNumber("Flutes")
        cutting_edge_length: Union[float, int] = self.getNumber("Length")
        priority = -diameter * flutes * cutting_edge_length
        if tracing:
            print(f"{tracing}FabDrillBit.getPriority('{operation_kind}')=>{priority}")
        return priority

    # FabVBit.getExample():
    @staticmethod
    def getExample() -> "FabVBit":
        """Return an example FabVBit."""
        v_bit: Any = FabBitTemplates.getExample(FabVBit)
        assert isinstance(v_bit, FabVBit)
        return v_bit

    # FabVBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabVBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabVBit._unit_tests()")
        v_bit: FabVBit = FabVBit.getExample()
        assert v_bit.Name == "60 Deg. V-Bit"
        assert v_bit.BitStem == "60degree_Vbit", v_bit.BitStem
        assert v_bit.ShapeStem == "v-bit"
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
        want: float = 2.7781633070260057
        assert abs(v_bit.AngleCuttingEdgeHeight - want) < 1.0e-8, v_bit.AngleCuttingEdgeHeight
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
