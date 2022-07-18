#!/usr/bin/env python3
"""Solid: A module for constructing 3D solids.

This module defines the following user facing classes:
* FabSolid: A 3D solid part that corresponds to a STEP file.
* FabMount: A CNC-like work plane on which other operations are performed.

There are internal classes that represent operations such as extrude, pocket, drill, etc.
This internal classes are managed by FabMount methods.

"""

import sys
import math

from enum import IntEnum, auto
from dataclasses import dataclass, field
from pathlib import Path as PathFile
from typeguard import check_argument_types, check_type
from typing import Any, cast, Dict, Generator, IO, List, Optional, Sequence, Tuple, Union

import cadquery as cq  # type: ignore
from cadquery import Vector  # type: ignore

# import Part  # type: ignore

from FabGeometries import (
    FabCircle, FabGeometry, Fab_GeometryContext, FabGeometryInfo, FabPlane, Fab_Query
)
from FabJoins import FabFasten, FabJoin
from FabNodes import FabBox, FabNode, Fab_Prefix, Fab_ProduceState
# from FabShops import FabCNC, FabMachine, FabShop
# from FabTools import FabLibrary
from FabToolBits import FabDrillBit, FabEndMillBit, FabVBit
from FabToolTemplates import FabBit
from FabUtilities import FabColor, FabMaterial, FabToolController
from FabShops import Fab_ShopBit, FabShops

# The *_suppress_stdout* function is based on code from:
#   [I/O Redirect](https://stackoverflow.com/questions/4675728/redirect-stdout-to-a-file-in-python)
# This code is used to suppress extraneous output from lower levels of cadquery.Assembly.save().

# <--------------------------------------- 100 characters ---------------------------------------> #

import os
from contextlib import contextmanager


# _suppress_stdout():
@contextmanager
def _suppress_stdout() -> Generator:
    """Suppress standard output inside of a context."""
    stdout: IO[str] = sys.stdout
    stdout.flush()
    with open("/dev/null", "wb") as dev_null:
        dev_null_fd: int = dev_null.fileno()
        # IPython (used in cq-editor) does not support *fileno*() method...
        # So we just hard code it to be 1.
        original_stdout_fd: int = 1
        assert isinstance(original_stdout_fd, int), original_stdout_fd
        # Copy original stdout FD to someplace else and restore it later.
        copied_stdout: Any
        with os.fdopen(os.dup(original_stdout_fd), "wb") as copied_stdout:
            copied_stdout_fd: int = copied_stdout.fileno()
            os.dup2(dev_null_fd, original_stdout_fd)
            try:
                yield sys.stdout  # Allow the code be run with redirected stdout
            finally:
                # Restore stdout:
                sys.stdout.flush()
                os.dup2(copied_stdout_fd, original_stdout_fd)
                # os.close(copied_std_fd)
                # Logical the statement immediately above should be called to close the file
                # descriptor.  In fact, it is automagically closed.  It is unclear why this happens.


# FabStock:
@dataclass
class FabStock(object):
    """FabStock: Represents the stock material to machine a part from.

    Attributes:
    * *Name* (str): The FabStock Name.
    * *StockIncrements* (Vector):
      The increments that the stock cuboid comes in  X, Y, and Z.
      The StockThicknesses attribute will override Z if possible.
    * *StockThicknesses* (Tuple[float ...]):
      The standard increments of stock thickness to use.
    * *StockMinimumCut* (float):
      The minimum amount that contour operation must remove in X and Y.
    """

    Name: str
    StockIncrements: Vector
    StockThicknesses: Tuple[float, ...]
    StockMinimumCut: float

    # FabStock.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing."""
        copy: Vector = Vector()
        self.StockIncrements += copy
        self.StockThicknesses = tuple(sorted(self.StockThicknesses))

    # FabStock.enclose():
    def enclose(self, box: FabBox) -> Tuple[Vector, Vector]:
        """Wrap some stock material around a FabBox."""
        # An internal function:
        def adjust(value: float, increment: float) -> float:
            """Adjust a value up to the nearest multiple of an increment."""
            count: int = math.floor(value / increment)
            while count * increment < value:
                count += 1  # pragma: no unit cover
            return count * increment

        # Unpack:
        stock_increments: Vector = self.StockIncrements
        stock_thicknesses: Tuple[float, ...] = self.StockThicknesses
        stock_minimum_cut: float = self.StockMinimumCut
        x_increment: float = stock_increments.x
        y_increment: float = stock_increments.y
        z_increment: float = stock_increments.z

        stock_dx: float = adjust(box.DX + 2.0 * stock_minimum_cut, x_increment)
        stock_dy: float = adjust(box.DY + 2.0 * stock_minimum_cut, y_increment)
        stock_dz: float = -1.0
        box_dz: float = box.DZ
        thickness: float
        for thickness in stock_thicknesses:
            if thickness >= box_dz:
                stock_dz = thickness
                break
        if stock_dz < 0.0:
            stock_dz = adjust(box_dz, z_increment)  # pragma: no unit cover

        offset: Vector = Vector(stock_dx / 2.0, stock_dy / 2.0, stock_dz / 2.0)
        center: Vector = box.C
        stock_bsw: Vector = center - offset
        stock_tne: Vector = center + offset
        return (stock_bsw, stock_tne)

    # FabStock._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run FabStock unit tests."""
        if tracing:
            print(f"{tracing}=>FabStock._unit_tests()")

        inch: float = 25.4
        quarter_inch = inch / 4.0
        eight_inch = inch / 8.0
        stock: FabStock = FabStock(
            "Name",
            Vector(quarter_inch, quarter_inch, quarter_inch),
            (
                inch / 16.0,
                eight_inch,
                quarter_inch,
                3 * eight_inch,
                inch / 3.0,
                3 * quarter_inch, inch
            ),
            inch / 8.0
        )
        box: FabBox = FabBox()
        box.enclose([Vector(0, 0, 0), Vector(inch, inch, quarter_inch)])
        if tracing:
            print(f"{tracing}{box.BSW=} {box.TNE=}")
        results: Tuple[Vector, Vector] = stock.enclose(box)
        if tracing:
            print(f"{tracing}{results=}")

        if tracing:
            print(f"{tracing}<=FabStock._unit_tests()")


# Fab_OperationOrder:
class Fab_OperationOrder(IntEnum):
    """ OperationOrder: A enumeration that specifies the desired order of operations."""

    NONE = auto()
    MOUNT = auto()
    DOWEL_PIN = auto()
    END_MILL_EXTERIOR = auto()
    MILL_DRILL_EXTERIOR = auto()
    MILL_DRILL_COUNTERSINK = auto()
    MILL_DRILL_CHAMFER = auto()
    MILL_DRILL = auto()
    END_MILL_DRILL = auto()
    END_MILL_POCKET = auto()
    MILL_DRILL_POCKET_CHAMFER = auto()
    MILL_DOVE_TAIL_CHAMFER = auto()
    DOUBLE_ANGLE_V_GROOVE = auto()
    DOUBLE_ANGLE_CHAMFER = auto()
    DRILL = auto()
    TAP = auto()
    VERTICAL_LATHE = auto()
    SLIDE = auto()
    LAST = auto()

    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform unit tests on Fab_OperationOrder."""
        if tracing:
            print(f"{tracing}=>Fab_OperationOrder._unit_tests()")

        none = Fab_OperationOrder.NONE
        mount = Fab_OperationOrder.MOUNT
        pin = Fab_OperationOrder.DOWEL_PIN
        end_mill = Fab_OperationOrder.END_MILL_EXTERIOR
        mill_drill_exterior = Fab_OperationOrder.MILL_DRILL_EXTERIOR
        mill_drill_chamfer = Fab_OperationOrder.MILL_DRILL_CHAMFER
        mill_drill_countersink = Fab_OperationOrder.MILL_DRILL_COUNTERSINK
        mill_drill = Fab_OperationOrder.MILL_DRILL
        end_mill_drill = Fab_OperationOrder.END_MILL_DRILL
        end_mill_pocket = Fab_OperationOrder.END_MILL_POCKET
        mill_drill_pocket_chamfer = Fab_OperationOrder.MILL_DRILL_POCKET_CHAMFER
        mill_dove_tail_chamfer = Fab_OperationOrder.MILL_DOVE_TAIL_CHAMFER
        double_angle_v_groove = Fab_OperationOrder.DOUBLE_ANGLE_V_GROOVE
        double_angle_chamfer = Fab_OperationOrder.DOUBLE_ANGLE_CHAMFER
        drill = Fab_OperationOrder.DRILL
        tap = Fab_OperationOrder.TAP
        vertical_lathe = Fab_OperationOrder.VERTICAL_LATHE
        slide = Fab_OperationOrder.SLIDE
        last = Fab_OperationOrder.LAST
        assert none < mount < pin < end_mill < mill_drill_exterior < mill_drill_chamfer
        assert mill_drill_countersink < mill_drill_chamfer < mill_drill < end_mill_drill
        assert mill_drill < end_mill_pocket < mill_drill_pocket_chamfer < mill_dove_tail_chamfer
        assert mill_dove_tail_chamfer < double_angle_v_groove < double_angle_chamfer
        assert double_angle_chamfer < drill < tap < vertical_lathe < slide < last

        if tracing:
            print(f"{tracing}<=Fab_OperationOrder._unit_tests()")


# Fab_OperationKind:
class Fab_OperationKind(IntEnum):
    """Fab_OperationKind: Value for the kind of operation. """
    CONTOUR = auto()
    DOWEL_PIN = auto()
    DRILL = auto()
    ROUND_POCKET = auto()
    SIMPLE_EXTERIOR = auto()
    SIMPLE_POCKET = auto()
    VERTICAL_LATHE = auto()
    SLIDE = auto()

    # OperationKind._unit_tests()
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform unit tests on Fab_OperationKind."""
        if tracing:
            print(f"{tracing}=>OperationKind._unit_tests()")

        contour = Fab_OperationKind.CONTOUR
        dowel_pin = Fab_OperationKind.DOWEL_PIN
        drill = Fab_OperationKind.DRILL
        round_pocket = Fab_OperationKind.ROUND_POCKET
        simple_exterior = Fab_OperationKind.SIMPLE_EXTERIOR
        simple_pocket = Fab_OperationKind.SIMPLE_POCKET
        vertical_lathe = Fab_OperationKind.VERTICAL_LATHE
        slide = Fab_OperationKind.SLIDE
        assert contour < dowel_pin < drill < round_pocket < simple_exterior < simple_pocket
        assert simple_pocket < vertical_lathe < slide

        if tracing:
            print(f"{tracing}<=OperationKind._unit_tests()")


# Fab_OperationKey:
@dataclass(frozen=True, order=True)
class Fab_OperationKey:
    """Fab_OperationKey: Provides a sorting key for Fab_Operations.

    Attributes:
    * *MountFence* (int): The user managed fence index for grouping operations within a mount.
    * *OperationOrder* (Fab_OperationOrder): The preferred operation order within a group.
    * *BitPriority*: (float): A negative number obtained via the getBitPriority method.
    * *ShopIndex* (int): The shop index of the bit to be used.
    * *MachineIndex* (int): The machine index of the bit to be used.
    * *ToolNumber* (int): The Tool number for the tool.

    Constructor:
    * Fab_OperationKey(MountFence, OperationOrder, BitPriority, ShopIndex, MachineIndex, ToolNumber)

    """

    MountFence: int
    OperationOrder: Fab_OperationOrder
    BitPriority: float
    ShopIndex: int
    MachineIndex: int
    ToolNumber: int

    # Fab_OperationKey.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing a FabOperationKey."""
        pass

    # Fab_OperationKey._unitTests():
    @staticmethod
    def _unitTests(tracing: str = ""):
        """Perform unit tests."""
        if tracing:
            print(f"{tracing}=>Fab_OperationKey._unitTests()")
        key1: Fab_OperationKey = Fab_OperationKey(
            0, Fab_OperationOrder.MILL_DRILL_EXTERIOR, -1.0, 0, 0, 1)
        key2: Fab_OperationKey = Fab_OperationKey(
            0, Fab_OperationOrder.MILL_DRILL_COUNTERSINK, -1.0, 0, 0, 2)
        assert key1 < key2
        if tracing:
            print(f"{tracing}<=Fab_OperationKey._unitTests()")


# Fab_Operation:
@dataclass(order=True)
class Fab_Operation(object):
    """Fab_Operation: An base class for FabMount operations.

    Attributes:
    * *Name* (str): The name of the Fab_Operation.
    * *Mount* (FabMount): The FabMount to use for performing operations.
    * *Fence* (int): Used to order sub groups of operations.
    * *Bit* (Optional[FabBit):
      The bit to use for this CNC operation.  (default: None)
    * *BitIndex* (int):
      The bit index associated with the bit.  (Default: -1)
    * *ToolController* (Optional[FabToolController]):
      The tool controller (i.e. speeds, feeds, etc.) to use. (Default: None)
    * *ToolControllerIndex* (int):
      The tool controller index associated with the tool controller.  (Default: -1)
    * *JsonEnabled* (bool):
      Enables the generation of JSON if True, otherwise suppresses it.  (Default: True)
    * *Active* (bool):
      If True, the resulting operation is performed.  About the only time this is set to False
      is for an extrude of stock material like a C channel, I beam, etc.  (Default: True)
    * *Prefix* (Fab_Prefix):
      The prefix information to use for file name generation.
    * *ShopBits*: Tuple[Fab_ShopBit, ...]:
      The available Fab_ShopBit's to select from for CNC operations.
    * *InitialOperationKey* (Optional[Fab_OperationKey]):
      The initial Fab_OperationKey used to do the initially sort the operations.
    * *SelectedShopBit* (Optional[Fab_ShopBit]):
      The final selected Fab_ShopBit for the operation.

    Constructor:
    * Fab_Operation("Name", Mount)

    """

    Name: str
    Mount: "FabMount" = field(repr=False, compare=False)
    Fence: int = field(init=False, repr=False, compare=False)
    Bit: Optional[FabBit] = field(init=False, repr=False)
    BitIndex: int = field(init=False, repr=False)
    ToolController: Optional[FabToolController] = field(init=False, repr=False)
    ToolControllerIndex: int = field(init=False, repr=False)
    JsonEnabled: bool = field(init=False, repr=False)
    Active: bool = field(init=False, repr=False)
    Prefix: Fab_Prefix = field(init=False, repr=False)
    ShopBits: Tuple[Fab_ShopBit, ...] = field(init=False, repr=False)
    InitialOperationKey: Optional[Fab_OperationKey] = field(init=False, repr=False, compare=False)
    SelectedShopBit: Optional[Fab_ShopBit] = field(init=False, repr=False, compare=False)

    # Fab_Operation.__post_init__():
    def __post_init__(self) -> None:
        """Initialize Fab_Operation."""
        check_type("Fab_Oparation.Name", self.Name, str)
        check_type("Fab_Oparation.Mount", self.Mount, "FabMount")
        self.Fence = self.Mount.Fence
        self.Bit = None
        self.BitIndex = -1  # Unassigned.
        self.ToolController = None
        self.ToolControllerIndex = -1  # Unassigned.
        self.JsonEnabled = True
        self.Active = True
        self.Prefix = self.Mount.lookup_prefix(self.Name)
        self.ShopBits = ()
        self.InitialOperationKey = None
        self.SelectedShopBit = None

    # Fab_Operation.get_tool_controller():
    # def get_tool_controller(self) -> FabToolController:
    #     """Return the Fab_Operation tool controller"""
    #     if not self.ToolController:
    #         raise RuntimeError(
    #             "Fab_Operation().get_tool_controller(): "
    #             "ToolController not set yet.")  # pragma: no unit cover
    #     return self.ToolController

    # Fab_Operation.setBit():
    def setBit(self, bit: FabBit, bits_table: Dict[FabBit, int]) -> None:
        """Set the Fab_Operation bit and associated index. """
        assert check_argument_types()
        bit_index: int
        if bit in bits_table:
            bit_index = bits_table[bit]
        else:
            bit_index = len(bits_table)
            bits_table[bit] = bit_index
            self.Bit = bit
        self.BitIndex = bit_index

    # Fab_Operation.set_tool_controller():
    def set_tool_controller(self, tool_controller: FabToolController,
                            tool_controllers_table: Dict[FabToolController, int]) -> None:
        """Set the Fab_Operation tool controller and associated index."""
        tool_controller_index: int
        if tool_controller in tool_controllers_table:
            tool_controller_index = tool_controllers_table[tool_controller]
            self.ToolController = None
        else:
            tool_controller_index = len(tool_controllers_table)
            tool_controllers_table[tool_controller] = tool_controller_index
            self.ToolController = tool_controller
        self.ToolControllerIndex = tool_controller_index

    # Fab_Operation.get_kind():
    def get_kind(self) -> str:
        """Return Fab_Operation kind."""
        raise RuntimeError(
            f"Fab_Operation().get_kind() not implemented for {type(self)}")  # pragma: no unit cover

    # Fab_Operation.get_name():
    def get_name(self) -> str:
        """Return Fab_Operation name."""
        return self.Name

    # Fab_Operation.selectShopBit():
    def selectShopBit(self, shop_bit: Fab_ShopBit) -> None:
        """Select a Fab_Shop bit for a Fab_Operation."""
        assert self.SelectedShopBit is None, "Fab_Operation.setShopBit(): already set"
        self.SelectedShopBit = shop_bit

    # Fab_Operation.getOperationOrder():
    def getOperationOrder(self, bit: FabBit) -> Fab_OperationOrder:
        """Return the Fab_OperationOrder for a Fab_Operation."""
        assert False, (
            f"Fab_Operation.getOperationOrder(): {type(self)}.getOperationOrder() not implemented")

    # Fab_Operation.getInitialOperationKey():
    def getInitialOperationKey(self) -> Fab_OperationKey:
        """Return initial Fab_OperationKey for a Fab_Operation."""
        initial_operation_key: Optional[Fab_OperationKey] = self.InitialOperationKey
        if initial_operation_key is None:
            best_shop_bit: Fab_ShopBit
            best_bit_priority: float = 0.0  # 0.0 will be replaces since priorities are negative.
            shop_bit: Fab_ShopBit
            index: int
            for index, shop_bit in enumerate(self.ShopBits):
                if index == 0 or shop_bit.BitPriority < best_bit_priority:
                    best_shop_bit = shop_bit
                    best_bit_priority = shop_bit.BitPriority
            if best_bit_priority >= 0.0:
                raise RuntimeError(
                    "FabExtrude.getInitialOperationKey(): "
                    f"{self.Mount._Solid.Label}.{self.Mount.Name}.{self.Name}: "
                    f"no bit found: {self.ShopBits=}")  # pragma: no unit cover
            fence: int = self.Mount.Fence
            bit: FabBit = shop_bit.Bit
            operation_order: Fab_OperationOrder = self.getOperationOrder(bit)

            initial_operation_key = Fab_OperationKey(
                fence, operation_order, best_shop_bit.BitPriority, best_shop_bit.ShopIndex,
                best_shop_bit.MachineIndex, best_shop_bit.ToolNumber)
            self.InitialOperationKey = initial_operation_key
        return initial_operation_key

    # Fab_Operation.getInitialOperationKeyTrampoline():
    def getInitialOperationKeyTrampoline(self) -> Fab_OperationKey:
        """Get the initial operation key for a Fab_Operation."""
        # In general, the Fab_Fab_OperationKey's are used to sort operations.
        # Unfortunately, when the sort method is called with
        # `key=Fab_Operation.getInitialOperationKey` it strongly binds to the place holder
        # Fab_Operation.getInitialOperationKey method() rather than call the desired
        # sub-class method.  To work around this, this method forwards the method call to the
        # desired sub-class method.  Yes, it bounces the call to the correct sub-class method.
        return self.getInitialOperationKey()

    # Fab_Operation.getHash():
    def getHash(self) -> Tuple[Any, ...]:
        """Return Fab_Operation hash."""
        raise RuntimeError(
            f"Fab_Operation().getHash() not implemented "
            f"for {type(self)}")  # pragma: no unit cover

    # Fab_Operation.get_geometries_hash():
    def get_geometries_hash(
            self, geometries: Union[FabGeometry, Tuple[FabGeometry, ...]]) -> Tuple[Any, ...]:
        """Return hash of FabGeometry's."""
        hashes: List[Union[int, str, Tuple[Any, ...]]] = []
        if isinstance(geometries, FabGeometry):
            geometries = (geometries,)  # pragma: no unit cover
        geometry: FabGeometry  # pragma: no unit cover
        for geometry in geometries:
            hashes.append(geometry.getHash())
        return tuple(hashes)

    # Fab_Operation.setShopBits():
    def setShopBits(self, shop_bits: List[Fab_ShopBit]) -> None:
        """Set the Fab_Operation ShopBits attribute."""
        self.ShopBits = tuple(shop_bits)

    # Fab_Operation.produce():
    def produce(self, tracing: str = "") -> Tuple[str, ...]:
        """Return the operation sort key."""
        raise NotImplementedError(
            f"{type(self)}.produce() is not implemented")  # pragma: no unit cover

    # Fab_Operation.post_produce1():
    def post_produce1(
            self, produce_state: Fab_ProduceState,
            expanded_operations: "List[Fab_Operation]", tracing: str = "") -> None:
        """Expand simple operations as approprate."""
        expanded_operations.append(self)  # pragma: no unit cover
        if tracing:
            print(f"{tracing}<=>{type(self)}.post_produce1()")

    # Fab_Operation.post_produce2():
    def post_produce2(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        raise NotImplementedError(
            f"{type(self)}.post_produce2() is not implemented")  # pragma: no unit cover

    # Fab_Operation.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return a base JSON dictionary for an Fab_Operation."""
        json_dict: Dict[str, Any] = {
            "Kind": self.get_kind(),
            "Label": self.get_name(),
            "_Active": self.Active,
        }
        if self.BitIndex >= 0:
            json_dict["BitIndex"] = self.BitIndex
        if self.Bit:
            bit_json: Dict[str, Any] = self.Bit.toJSON()
            json_dict["Bit"] = bit_json
        if self.ToolControllerIndex >= 0:
            json_dict["ToolControllerIndex"] = self.ToolControllerIndex
        if self.ToolController:
            tool_controller_json: Dict[str, Any] = self.ToolController.to_json()
            json_dict["ToolController"] = tool_controller_json
        return json_dict


# Fab_Extrude:
@dataclass(order=True)
class Fab_Extrude(Fab_Operation):
    """Fab_Extrude: Represents and extrude operation.

    Attributes:
    * *Mount* (FabMount): The FabMount to use for performing operations.
    * *Name* (str): The FabExtrude operation name.
    * *Geometry* (Union[FabGeometry, Tuple[FabGeometry, ...]):
      The FabGeometry (i.e. FabPolygon or FabCircle) or a tuple of FabGeometry's to extrude with.
      When the tuple is used, the largest FabGeometry (which is traditionally the first one)
      is the outside of the extrusion, and the rest are "pockets".  This is useful for tubes.
    * *Depth* (float): The depth to extrude to in millimeters.
    * *Contour* (bool):
      If True and profile CNC contour path is performed; otherwise, no profile is performed.
    See Fab_Operation for extra computed Attributes.

    Constructor:
    * Fab_Extrude("Name", Mount, Geometry, Depth, Contour)

    """

    _Geometry: Union[FabGeometry, Tuple[FabGeometry, ...]] = field(compare=False)
    _Depth: float
    _Contour: bool
    # TODO: Make _Geometries be comparable.
    _Geometries: Tuple[FabGeometry, ...] = field(init=False, repr=False, compare=False)
    _StepFile: str = field(init=False, repr=False, compare=False)
    _StartDepth: float = field(init=False, repr=False, compare=False)
    _StepDown: float = field(init=False, repr=False, compare=False)
    _FinalDepth: float = field(init=False, repr=False, compare=False)

    # Fab_Extrude.__post_init__():
    def __post_init__(self) -> None:
        """Verify Fab_Extrude values."""
        super().__post_init__()
        check_type("Fab_Extrude.Geometry", self._Geometry,
                   Union[FabGeometry, Tuple[FabGeometry, ...]])
        check_type("Fab_Extrude.Depth", self._Depth, float)
        check_type("Fab_Extrude.Contour", self._Contour, bool)

        # Type check self._Geometry and convert into self._Geometries:
        geometries: List[FabGeometry] = []
        self_geometry: Union[FabGeometry, Tuple[FabGeometry, ...]] = self._Geometry
        if isinstance(self_geometry, FabGeometry):
            geometries = [self_geometry]
        elif isinstance(self_geometry, tuple):  # pragma: no unit cover
            geometry: FabGeometry
            for geometry in self_geometry:
                if not isinstance(geometry, FabGeometry):
                    raise RuntimeError(
                        f"Fab_Extrude.__post_init__({self.Name}):"
                        f"{type(geometry)} is not a FabGeometry")
                geometries.append(geometry)
        else:  # pragma: no unit cover
            raise RuntimeError(
                f"Fab_Extrude.__post_init__({self.Name}):{type(self.Geometry)} "
                f"is neither a FabGeometry nor a Tuple[FabGeometry, ...]")  # pragma: no unit cover
        self._Geometries = tuple(geometries)

        if self.Depth <= 0.0:
            raise RuntimeError(f"Fab_Extrude.__post_init__({self.Name}):"
                               f"Depth ({self.Depth}) is not positive.")  # pragma: no unit cover
        self._StepFile = "Fab_Extrude.__post_init__()"
        self._StartDepth = 0.0
        self._StepDown = 3.0
        self._FinalDepth = -self.Depth
        self.Active = self._Contour

    # Fab_Extrude.Geometry():
    @property
    def Geometry(self) -> Union[FabGeometry, Tuple[FabGeometry, ...]]:
        """Return the Fab_Extrude FabGeometry."""
        return self._Geometry  # pragma: no unit cover

    # Fab_Extrude.Depth():
    @property
    def Depth(self) -> float:
        """Return the Depth."""
        return self._Depth

    # Fab_Extrude.get_kind():
    def get_kind(self) -> str:
        """Return Fab_Extrude kind."""
        return "Extrude"

    # Fab_Extrude.getOperationOrder():
    def getOperationOrder(self, bit: FabBit) -> Fab_OperationOrder:
        """Return the Fab_OperationOrder for a Fab_Operation."""
        operation_order: Fab_OperationOrder = Fab_OperationOrder.NONE
        if isinstance(bit, FabEndMillBit):
            operation_order = Fab_OperationOrder.END_MILL_EXTERIOR
        elif isinstance(bit, FabVBit):  # pragma: no unit cover
            # A mill drill is represented as a FabVBit.
            operation_order = Fab_OperationOrder.MILL_DRILL_EXTERIOR
        else:
            raise RuntimeError(
                f"FabExtrude, Fab_Extrude.getOperationOrder {type(bit)} "
                "which is neither FabEndMillBit nor FabMillDrillBit")  # pragma: no unit cover
        return operation_order

    # Fab_Extrude.getHash():
    def getHash(self) -> Tuple[Any, ...]:
        """Return hash for Fab_Extrude operation."""
        return (
            "Fab_Extrude",
            self.Name,
            f"{self._Depth:.6f}",
            self.get_geometries_hash(self._Geometries),
        )

    # Fab_Extrude.post_produce1():
    def post_produce1(
            self, produce_state: Fab_ProduceState,
            expanded_operations: "List[Fab_Operation]", tracing: str = "") -> None:
        """Expand simple operations as approprated."""
        tracing = "      "
        # next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_Extrude.post_produce1('{self.Name}')")

        depth: float = self.Depth
        geometries: Tuple[FabGeometry, ...] = self._Geometries
        plane: FabPlane = self.Mount.Plane

        # Split into *exterior* and *pockets* and process them differently.
        exterior: FabGeometry = geometries[0]
        pockets: Tuple[FabGeometry, ...] = geometries[1:]

        # Deal with *exterior_info* first:
        exterior_info: FabGeometryInfo = exterior.GeometryInfo
        if tracing:
            print(f"{tracing}{plane=} {exterior_info=}")
        area: float = exterior_info.Area
        perimeter: float = exterior_info.Perimeter
        internal_radius: float = exterior_info.MinimumInternalRadius
        external_radius: float = exterior_info.MinimumExternalRadius
        if tracing:
            print(f"{tracing}{area=} {perimeter=} {internal_radius=} {external_radius=}")
        internal_radius = max(0.0, exterior_info.MinimumInternalRadius)  # no internals: -1.0=>0.0
        maximum_diameter = 2.0 * internal_radius if internal_radius > 0.0 else 987654321.0
        if tracing:
            print(f"{tracing}")
            print(f"{tracing}{self.Name=} {maximum_diameter=} {depth=}")

        # Search *drill_shop_bits* and fill in *matching_shop_bits*:
        shops: FabShops = produce_state.Shops
        contour_shop_bits: Tuple[Fab_ShopBit, ...] = shops.ContourShopBits
        assert len(contour_shop_bits) > 0
        shop_bit: Fab_ShopBit
        allowed_bit_types: Tuple[type, ...] = (FabEndMillBit, FabVBit)  # MillDrill=>FabVBit
        matching_shop_bits: List[Fab_ShopBit] = []
        index: int
        for index, shop_bit in enumerate(contour_shop_bits):
            contour_bit: FabBit = shop_bit.Bit
            if tracing:
                print(f"{tracing}EndMill[{index}]: {contour_bit.Name}")
            assert isinstance(contour_bit, allowed_bit_types), (
                f"FabExtrude.produce1(): {type(contour_bit)} is not one of {allowed_bit_types}")
            contour_bit_length: Union[float, int] = contour_bit.getNumber("Length")
            contour_bit_diameter: Union[float, int] = contour_bit.getNumber("Diameter")
            length_ok: bool = depth <= contour_bit_length
            diameter_ok: bool = contour_bit_diameter <= maximum_diameter
            if tracing:
                print(f"{tracing}{depth=} {contour_bit_length}")
                print(f"{tracing}{maximum_diameter=} {contour_bit_diameter=}")
                print(f"{tracing}{length_ok=} {diameter_ok=}")
            if length_ok and diameter_ok:
                if tracing:
                    print(f"{tracing}Match!")
                matching_shop_bits.append(shop_bit)
        assert len(matching_shop_bits) > 0
        # For now, fail horribly if there are no *matching_shop_bits*:
        # assert len(matching_shop_bits) > 0
        self.setShopBits(matching_shop_bits)
        expanded_operations.append(self)

        # Deal with *pockets*:
        pocket: FabGeometry
        for pocket in pockets:
            self.post_produce1(produce_state, expanded_operations)  # pragma: no unit cover

        if tracing:
            print(f"{tracing}<=Fab_Extrude.post_produce1('{self.Name}')")

    # Fab_Extrude.post_produce2():
    def post_produce2(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        """Produce the Extrude."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_Extrude.produce2('{self.Name}')")

        # Step 1: Produce the extrude Step file for the extrude:
        # Step 1a: Create the needed CadQuery *extrude_context*:
        mount: FabMount = self.Mount
        geometry_context: Fab_GeometryContext = mount._GeometryContext
        # Leave the extruded solid on the top of the *geometry_context* for further operations.
        extrude_context: Fab_GeometryContext = geometry_context
        extrude_query: Fab_Query = extrude_context.Query
        if tracing:
            extrude_query.show("Extrude Query Context Before", tracing)

        # Step 1b: Transfer *geometries* to *extrude_context* and perform the extrusion:
        geometry_prefix: str = f"{mount.Name}_{self.Name}"
        geometries: Tuple[FabGeometry, ...] = self._Geometries
        for index, geometry in enumerate(geometries):
            if tracing:
                print(f"{tracing}Geometry[{index}]:{geometry=}")
            _ = geometry.xyPlaneReorient(0.0, Vector(), tracing=next_tracing)
            geometry.produce(extrude_context, geometry_prefix, index, tracing=next_tracing)
        # geometry_context.WorkPlane.close(tracing=next_tracing)
        extrude_context.Query.extrude(self.Depth, tracing=next_tracing)

        # Step 1c: Save extrusion to a STEP file:
        prefix: Fab_Prefix = self.Prefix
        prefix_text: str = prefix.to_string()
        extrude_name: str = f"{prefix_text}__{self.Name}__extrude"
        extrude_path = produce_state.Steps.activate(extrude_name,
                                                    self.get_geometries_hash(geometries))
        self._StepFile = str(extrude_path)
        if not extrude_path.exists():
            # Save it out here.
            extrude_assembly = cq.Assembly(
                extrude_context.Query.WorkPlane, name=extrude_name,
                color=cq.Color(0.5, 0.5, 0.5, 0.5))
            _ = extrude_assembly

            # Use Fab_Steps to manage duplicates.
            with _suppress_stdout():
                extrude_assembly.save(str(extrude_path), "STEP")
        assert extrude_path.exists()

        # Do Contour computations:
        plane: FabPlane = extrude_context.Plane
        normal: Vector = plane.Normal
        origin: Vector = plane.Origin
        distance: float = origin.Length
        positive_origin: Vector = distance * normal
        negative_origin: Vector = -distance * normal
        # TODO: the computation below looks wrong.
        start_depth: float = (
            distance
            if (origin - positive_origin).Length < (origin - negative_origin).Length
            else -distance
        )
        self._StartDepth = start_depth
        self._StepDown = 3.0
        self._FinalDepth = start_depth - self.Depth

        selected_shop_bit: Optional[Fab_ShopBit] = self.SelectedShopBit
        assert isinstance(selected_shop_bit, Fab_ShopBit), selected_shop_bit
        selected_bit: FabBit = selected_shop_bit.Bit
        assert isinstance(selected_bit, (FabEndMillBit, FabVBit)), selected_bit
        material: FabMaterial = self.Mount.Solid.Material
        assert isinstance(material, FabMaterial), material

        tool_controller: FabToolController
        maxiumum_tool_depth: float
        tool_controller, maximum_tool_depth = FabToolController.computeToolController(
            material, selected_shop_bit, self._Depth)
        _ = maximum_tool_depth
        self.setBit(selected_bit, produce_state.BitsTable)
        self.set_tool_controller(tool_controller, produce_state.ToolControllersTable)

        if tracing:
            print(f"{tracing}<=Fab_Extrude.post_produce2('{self.Name}')")

    # Fab_Extrude.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return JSON dictionary for Fab_Extrude."""
        coolant_modes: Tuple[str, ...] = ("None", "Flood", "Mist")
        direction_modes: Tuple[str, ...] = ("CCW", "CW")
        side_modes: Tuple[str, ...] = ("Inside", "Outside")
        json_dict: Dict[str, Any] = super().to_json()
        json_dict["StepFile"] = self._StepFile
        json_dict["_Active"] = self.Active
        json_dict["_ClearanceHeight"] = self._StartDepth + 10.0  # TODO: Fix
        json_dict["_CoolantMode"] = coolant_modes[1]  # TODO: Fix
        json_dict["_Direction"] = direction_modes[0]
        json_dict["_FinalDepth"] = self._FinalDepth
        json_dict["_SafeHeight"] = self._StartDepth + 5.0  # TODO: Fix
        json_dict["_Side"] = side_modes[1]
        json_dict["_StartDepth"] = self._StartDepth
        json_dict["_StepDown"] = self._StepDown
        return json_dict


# Fab_Pocket:
@dataclass(order=True)
class Fab_Pocket(Fab_Operation):
    """Fab_Pocket: Represents a pocketing operation.

    Attributes:
    * Name (str): The operation name.
    * Mount (FabMount): The FabMount to use for pocketing.
    * Geometries (Tuple[FabGeometry, ...]):
      The FabGeomety's that specify the pocket.  The first one must be the outer most pocket
      contour.  The remaining FabGeometries must be pocket "islands".  All islands must be
      contained by the outer most pocket contour and islands must not overlap.
    * Depth (float): The pocket depth in millimeters.

    Extra Computed Attributes:
    * *Geometries* (Tuple[FabGeometry, ...]):
       The Polygon or Circle to pocket.  If a tuple is given, first FabGeometry in the tuple
       specifies the pocket exterior, and the remaining FabGeometry's specify islands of
       material within the pocket that must not be removed.
    * *Depth* (float): The pocket depth in millimeters.
    * *Bottom_Path* (str): The the path to the generated Pocket bottom STEP file.
    See Fab_Operation for even more extra computed Attributes.

    Constructor:
    * Fab_Pocket(Mount, "Name", Geometries, Depth)

    """

    _Geometries: Tuple[FabGeometry, ...] = field(compare=False)
    _Depth: float
    # TODO: Make _Geometries be comparable.
    _BottomPath: Optional[PathFile] = field(init=False)
    _FinalDepth: float = field(init=False, repr=False)
    _TopDepth: float = field(init=False, repr=False)
    _StartDepth: float = field(init=False, repr=False)
    _StepDepth: float = field(init=False, repr=False)

    # Fab_Pocket.__post_init__():
    def __post_init__(self) -> None:
        """Verify Fab_Pocket values."""
        super().__post_init__()

        # Type check self._Geometry and convert into self._Geometries:
        geometries: List[FabGeometry] = []
        self_geometry: Union[FabGeometry, Tuple[FabGeometry, ...]] = self._Geometries
        if isinstance(self_geometry, FabGeometry):
            geometries = [self_geometry]  # pragma: no unit cover
        elif isinstance(self_geometry, tuple):  # pragma: no unit cover
            geometry: FabGeometry
            for geometry in self_geometry:
                if not isinstance(geometry, FabGeometry):  # pragma: no unit cover
                    raise RuntimeError(
                        f"Fab_Extrude.__post_init__({self.Name}):"
                        f"{type(geometry)} is not a FabGeometry")  # pragma: no unit cover
                geometries.append(geometry)
        else:  # pragma: no unit cover
            raise RuntimeError(  # pragma: no unit cover
                f"Fab_Extrude.__post_init__({self.Name}):{type(self.Geometries)} "
                f"is neither a FabGeometry nor a Tuple[FabGeometry, ...]")  # pragma: no unit cover
        self._Geometries = tuple(geometries)

        if self._Depth <= 0.0:
            raise RuntimeError(
                f"Fab_Extrude.__post_init__({self.Name}):"
                f"Depth ({self.Depth}) is not positive.")  # pragma: no unit cover
        self._BottomPath = None

        # Unpack some values from *mount*:
        mount: FabMount = self.Mount
        geometry_context: Fab_GeometryContext = mount._GeometryContext
        plane: FabPlane = geometry_context.Plane
        top_depth: float = plane.Distance
        final_depth: float = top_depth - self._Depth
        delta_depth: float = top_depth - final_depth
        # tool_edge_height: float = 30.00  # TODO: Fix
        # if delta_depth > tool_edge_height:
        #     raise RuntimeError("FIXME")  # pragma: no unit cover

        tool_diameter: float = 5.00  # TODO: Fix
        step_depth: float = tool_diameter / 2.0
        steps: int = int(math.ceil(delta_depth / step_depth))
        step_down = delta_depth / float(steps)
        self._TopDepth = top_depth
        self._StartDepth = max(top_depth - step_depth, final_depth)
        self._StepDown = step_down
        self._FinalDepth = final_depth

    # Fab_Pocket.post_produce1():
    def post_produce1(
            self, produce_state: Fab_ProduceState,
            expanded_operations: "List[Fab_Operation]", tracing: str = "") -> None:
        """Expand simple operations as approprated."""
        # next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_Pocket.post_produce1()")

        depth: float = self.Depth
        geometries: Tuple[FabGeometry, ...] = self._Geometries
        exterior: FabGeometry = geometries[0]
        exterior_info: FabGeometryInfo = exterior.GeometryInfo
        if tracing:
            area: float = exterior_info.Area
            perimeter: float = exterior_info.Perimeter
            internal_radius: float = exterior_info.MinimumInternalRadius
            external_radius: float = exterior_info.MinimumInternalRadius
            print(f"{tracing}{area=} {perimeter=} {internal_radius=} {external_radius=}")

        # This is counter intuitive.  For a pocket, the external perimeter of geometry is
        # traversed.  The external corners of the polygon are actually internal corners
        # for pocketing purposes.
        external_radius = exterior_info.MinimumExternalRadius
        assert external_radius > 0.0, external_radius
        maximum_diameter = 2.0 * external_radius
        if tracing:
            print(f"{tracing}")
            print(f"{tracing}{self.Name=} {maximum_diameter=} {depth=}")

        # Search *drill_shop_bits* and fill in *matching_shop_bits*:
        shops: FabShops = produce_state.Shops
        pocket_shop_bits: Tuple[Fab_ShopBit, ...] = shops.PocketShopBits
        pocket_shop_bit: Fab_ShopBit
        matching_shop_bits: List[Fab_ShopBit] = []
        index: int
        for index, pocket_shop_bit in enumerate(pocket_shop_bits):
            end_mill_bit: FabBit = pocket_shop_bit.Bit
            if tracing:
                print(f"{tracing}EndMill[{index}]: {end_mill_bit.Name}")
            assert isinstance(end_mill_bit, FabEndMillBit)
            end_mill_bit_length: Union[float, int] = end_mill_bit.getNumber("Length")
            end_mill_bit_diameter: Union[float, int] = end_mill_bit.getNumber("Diameter")
            length_ok: bool = depth <= end_mill_bit_length
            diameter_ok: bool = end_mill_bit_diameter <= maximum_diameter
            if tracing:
                print(f"{tracing}{depth=} {end_mill_bit_length}")
                print(f"{tracing}{maximum_diameter=} {end_mill_bit_diameter=}")
                print(f"{tracing}{length_ok=} {diameter_ok=}")
            if length_ok and diameter_ok:
                if tracing:
                    print(f"{tracing}Match!")
                matching_shop_bits.append(pocket_shop_bit)

        # For now, fail horribly if there are no *matching_shop_bits*:
        # assert len(matching_shop_bits) > 0
        self.setShopBits(matching_shop_bits)
        expanded_operations.append(self)

        if tracing:
            print(f"{tracing}<=Fab_Pocket.post_produce1()")

    # Fab_Pocket.getOperationOrder():
    def getOperationOrder(self, bit: FabBit) -> Fab_OperationOrder:
        """Return the Fab_OperationOrder for a Fab_Operation."""
        operation_order: Fab_OperationOrder = Fab_OperationOrder.NONE
        if isinstance(bit, FabEndMillBit):
            operation_order = Fab_OperationOrder.END_MILL_POCKET
        else:
            raise RuntimeError(
                f"FabExtrude, Fab_Pockt.getOperationOrder {type(bit)} "
                "is not a FabEndMillBit")  # pragma: no unit cover
        return operation_order

    # Fab_Pocket.Geometries():
    @property
    def Geometries(self) -> Tuple[FabGeometry, ...]:
        """Return the original Geometry."""
        return self._Geometries  # pragma: no unit cover

    # Fab_Pocket.Depth():
    @property
    def Depth(self) -> float:
        """Return the original Depth."""
        return self._Depth  # pragma: no unit cover

    # Fab_Pocket.getHash():
    def getHash(self) -> Tuple[Any, ...]:
        """Return Fab_Pocket hash."""
        hashes: List[Any] = [
            "Fab_Pocket",
            self.Name,
            f"{self._Depth:.6f}",
        ]
        geometry: FabGeometry
        for geometry in self._Geometries:
            hashes.append(geometry.getHash())
        return tuple(hashes)

    # Fab_Pocket.get_kind():
    def get_kind(self) -> str:
        """Return Fab_Pocket kind."""
        return "Pocket"

    # Fab_Pocket.post_produce2():
    def post_produce2(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        """Produce the Pocket."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_Pocket.post_produce2('{self.Name}')")

        # Step 1: Produce the pocket Step file for the pocket:
        # Step 1a: Create the needed CadQuery *pocket_context* and *bottom_context*:
        mount: FabMount = self.Mount
        geometry_context: Fab_GeometryContext = mount._GeometryContext
        top_context: Fab_GeometryContext = geometry_context.copy(tracing=next_tracing)
        top_pocket_query: Fab_Query = top_context.Query
        bottom_context: Fab_GeometryContext = geometry_context.copyWithPlaneAdjust(
            -self._Depth, tracing=next_tracing)
        if tracing:
            top_pocket_query.show("Top Pocket Context Before", tracing)

        # Step 1b: Transfer *geometries* to *pocket_context* and *bottom_context*:
        prefix: Fab_Prefix = self.Prefix
        prefix_text: str = prefix.to_string()
        geometry: FabGeometry
        geometries: Tuple[FabGeometry, ...] = self._Geometries
        index: int
        for index, geometry in enumerate(geometries):
            geometry.produce(top_context, prefix_text, index, tracing=next_tracing)
            geometry.produce(bottom_context, prefix_text, index, tracing=next_tracing)
            if tracing:
                top_pocket_query.show(f"Top Pocket Context after Geometry {index}", tracing)

        # Step 1c: Extrude *bottom_path* and save it to a STEP file:
        top_pocket_query.extrude(self._Depth, tracing=next_tracing)
        bottom_name: str = f"{prefix_text}__{self.Name}__pocket_bottom"
        bottom_path = produce_state.Steps.activate(bottom_name,
                                                   self.get_geometries_hash(geometries))
        if not bottom_path.exists():
            # Save it out here.
            self._BottomPath = bottom_path
            bottom_context.Query.extrude(0.000001, tracing=next_tracing)  # Make it very thin.
            bottom_assembly = cq.Assembly(
                bottom_context.Query.WorkPlane, name=bottom_name,
                color=cq.Color(0.5, 0.5, 0.5, 0.5))
            _ = bottom_assembly

            # Use Fab_Steps to manage duplicates.
            with _suppress_stdout():
                bottom_assembly.save(str(bottom_path), "STEP")
        assert bottom_path.exists()
        self._BottomPath = bottom_path

        # Step 2: Now deal with finding acceptable tool bits from *machines* in *shops*:
        # pocket_geometry: FabGeometry = self._Geometries[0]
        # pocket_info: FabGeometryInfo = pocket_geometry.GetGeometryInfo()
        # _ = pocket_info

        selected_shop_bit: Optional[Fab_ShopBit] = self.SelectedShopBit
        assert isinstance(selected_shop_bit, Fab_ShopBit), selected_shop_bit
        selected_bit: FabBit = selected_shop_bit.Bit
        assert isinstance(selected_bit, (FabEndMillBit, FabVBit)), selected_bit
        material: FabMaterial = self.Mount.Solid.Material
        assert isinstance(material, FabMaterial), material

        tool_controller: FabToolController
        maximum_depth: float
        tool_controller, maximum_depth = FabToolController.computeToolController(
            material, selected_shop_bit, self._Depth)
        self.setBit(selected_bit, produce_state.BitsTable)
        self.set_tool_controller(tool_controller, produce_state.ToolControllersTable)

        if tracing:
            top_pocket_query.show("Pocket Context after Extrude:", tracing)

        # TODO: Use the CadQuery *cut* operation instead of *subtract*:
        query: Any = geometry_context.Query
        assert isinstance(query, Fab_Query), query
        if tracing:
            query.show("Pocket Main Before Subtract", tracing)
        query.subtract(top_pocket_query, tracing=next_tracing)
        if tracing:
            query.show("Pocket After Subtract", tracing)
            print(f"{tracing}<=Fab_Pocket.post_produce2('{self.Name}')")

    # Fab_Pocket.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return JSON dictionary for Fab_Extrude."""
        bottom_path: Optional[PathFile] = self._BottomPath
        cut_modes: Tuple[str, ...] = ("Climb", "Conventional")
        coolant_modes: Tuple[str, ...] = ("None", "Flood", "Mist")
        offset_patterns: Tuple[str, ...] = (
            "Grid", "Line", "Offset", "Spiral", "Triangle", "ZigZag", "ZigZagOffset")
        start_ats: Tuple[str, ...] = ("Center", "Edge")

        start_depth: float = self._StartDepth
        step_down: float = self._StepDown
        final_depth: float = self._FinalDepth

        json_dict: Dict[str, Any] = super().to_json()
        json_dict["StepFile"] = str(bottom_path)  # Step file
        json_dict["_ClearanceHeight"] = start_depth + 10.0  # TODO: Fix
        json_dict["_CoolantMode"] = coolant_modes[1]  # TODO: Fix
        json_dict["_CutMode"] = cut_modes[0]  # TODO: Fix
        json_dict["_FinalDepth"] = final_depth  # TODO: Fix  (Lowest Z depth in pocket)
        json_dict["_FinishDepth"] = 0.0  # TODO: Fix (Maximum material removed on final pass)
        json_dict["_KeepToolDown"] = False
        json_dict["_MinTravel"] = False
        json_dict["_OffsetPattern"] = offset_patterns[5]
        json_dict["_SafeHeight"] = start_depth + 5.0  # TODO: Fix
        json_dict["_StartAt"] = start_ats[0]
        json_dict["_StartDepth"] = 0.0  # TODO: Starting depth of first cut (pocket_top - delta)
        json_dict["_StepDown"] = step_down  # TODO: Incremental Step Down of Tool
        json_dict["_StepOver"] = 90  # Percent of cutter diameter to step over on each pass
        json_dict["_ZigZagAngle"] = 45.0  # Angle in degrees

        return json_dict


# Fab_HoleKey:
@dataclass(frozen=True)
class Fab_HoleKey(object):
    """Fab_HoleKey: Represents a group of holes that can be grouped together.

    Attributes:
    * *ThreadName* (str): The name of the thread class for the hole.
    * *Kind* (str): The kind of thread hole (one of "thread", "close", or "standard".)
    * *Depth* (float): The hole depth.
    * *IsTop* (bool): True when hole is the top of the fastener for countersink and counterboring.
    See Fab_Operation for even more extra computed Attributes.

    Constructor:
    * Fab_HoleKey("Name", Mount, "ThreadName", "Kind", Depth, IsTop)

    """
    ThreadName: str
    Kind: str
    Depth: float
    IsTop: bool

    # Fab_HoleKey.__post_init__():
    def __post_init__(self) -> None:
        """Perform checks on Fab_HoleKey."""
        thread_name: str = self.ThreadName
        assert thread_name.startswith("M") or thread_name.startswith("#") or (
            thread_name.find("/") > 0), thread_name
        assert self.Kind in ("thread", "close", "standard"), self.Kind
        assert self.Depth > 0.0, self.Depth
        assert isinstance(self.IsTop, bool), self.IsTop

    # Fab_HoleKey.getHash():
    def getHash(self) -> Tuple[Any, ...]:
        """Return a hash tuple for a Fab_HoleKey."""
        return (
            self.ThreadName,
            self.Kind,
            f"{self.Depth:.6f}",
            self.IsTop,
        )

    # Fab_HoleKey._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = ""):
        """Run unit tests for Fab_HoleKey."""
        if tracing:
            print(f"{tracing}=>Fab_HoleKey._unit_tests()")

        hole_key: Fab_HoleKey = Fab_HoleKey("#4-40", "close", 10.0, True)
        assert hole_key.ThreadName == "#4-40"
        assert hole_key.Kind == "close"
        assert hole_key.Depth == 10.0
        assert hole_key.IsTop
        hole_key_hash: Tuple[Any, ...] = hole_key.getHash()
        assert hole_key_hash == ("#4-40", "close", "10.000000", True), hole_key_hash

        if tracing:
            print(f"{tracing}<=Fab_HoleKey._unit_tests()")


# Fab_Hole:
@dataclass
class Fab_Hole(Fab_Operation):
    """Fab_Hole: FabDrill helper class that represents one or more holes related holes.

    Attributes:
    * *Name* (str): The name of the Fab_Hole.
    * *Mount* (FabMount): The FabMount to use for performing operations.
    * Key (FabHoleKey): The hole key used for grouping holes.
    * Join (FabJoin): The associated FabJoin the produced the hole.
    * Centers (Tuple[Vector, ...]): The associated start centers.
    * Name (str): The hole name.
    * Depth (str): The hole depth.

    Computed Attributes:
    * HolesCount (int): The number of complatible holes.
    * StartDepth (float): The starting depth in millimeters from the mount plane.

    Constructor:
    * Fab_Hole("Name", Mount, Key, Centers, Join, Depth)
    """

    Key: Fab_HoleKey
    Centers: Tuple[Vector, ...]  # The Center (start point) of the drills
    Join: FabJoin = field(repr=False)  # The associated FabJoin
    Depth: float  # Hole depth
    HolesCount: int = field(init=False, repr=False)  # Number of holes in this operation
    StartDepth: float = field(init=False, repr=False)
    StepFile: str = field(init=False, repr=False)

    # Fab_Hole.__post_init__():
    def __post_init__(self) -> None:
        """Perform final initialization of Fab_Hole"""

        super().__post_init__()
        check_type("Fab_Hole.Key", self.Key, Fab_HoleKey)
        check_type("Fab_Hole.Centers", self.Centers, Tuple[Vector, ...])
        check_type("Fab_Hole.Join", self.Join, FabJoin)
        check_type("Fab_Hole.Depth", self.Depth, float)
        self.HolesCount = 0
        self.StartDepth = 0.0
        self.StepFile = ""

    # Fab_Hole.get_kind():
    def get_kind(self) -> str:
        """Return Fab_Hole kind."""
        return "Drilling"

    # Fab_Hole.getHash():
    def getHash(self) -> Tuple[Any, ...]:
        """Return Fab_Hole hash."""
        hashes: List[Any] = [
            "Fab_Hole",
            self.Key.getHash(),
            self.Join.getHash(),
        ]
        center: Vector
        for center in self.Centers:
            hashes.append(f"{center.x:.6f}")
            hashes.append(f"{center.y:.6f}")
            hashes.append(f"{center.z:.6f}")
        return tuple(hashes)

    # Fab_Hole.getOperationOrder():
    def getOperationOrder(self, bit: FabBit) -> Fab_OperationOrder:
        """Return the Fab_OperationOrder for a Fab_Operation."""
        operation_order: Fab_OperationOrder = Fab_OperationOrder.NONE
        if isinstance(bit, FabDrillBit):
            operation_order = Fab_OperationOrder.DRILL
        else:
            raise RuntimeError(
                f"FabExtrude, Fab_Pocket.getOperationOrder {type(bit)} "
                "is not a FabDrillBit")  # pragma: no unit cover
        return operation_order

    # Fab_Hole.post_produce1():
    def post_produce1(
            self, produce_state: Fab_ProduceState,
            expanded_operations: "List[Fab_Operation]", tracing: str = "") -> None:
        """Expand simple operations as approprated."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_Hole.post_produce1()")

        # Extract the desired drill *depth* and *diameter*:
        kind: str = self.Key.Kind
        depth: float = self.Key.Depth
        # TODO: Extend *depth* to deal with through holes.
        diameter: float = self.Join.Fasten.get_diameter(kind)

        # Search *drill_shop_bits* and fill in *matching_shop_bits*:
        shops: FabShops = produce_state.Shops
        matching_shop_bits: List[Fab_ShopBit] = []
        drill_shop_bits: Tuple[Fab_ShopBit, ...] = shops.DrillShopBits
        drill_shop_bit: Fab_ShopBit
        for drill_shop_bit in drill_shop_bits:
            drill_bit: FabBit = drill_shop_bit.Bit
            assert isinstance(drill_bit, FabDrillBit)
            drill_bit_length: Union[float, int] = drill_bit.getNumber("Length")
            drill_bit_diameter: Union[float, int] = drill_bit.getNumber("Diameter")
            if depth <= drill_bit_length and abs(diameter - drill_bit_diameter) < 0.0001:  # mm
                matching_shop_bits.append(drill_shop_bit)

        # If there is least one drill bit, use it; otherwise, convert everything FabPocket's:
        if matching_shop_bits:
            self.setShopBits(matching_shop_bits)
            expanded_operations.append(self)
        else:
            # Create a FabPocket for each hole *center*:
            mount_plane: FabPlane = self.Mount.Plane
            mount: FabMount = self.Mount
            center: Vector
            index: int
            for index, center in enumerate(self.Centers):
                circle_geometry: FabCircle = FabCircle(mount_plane, center, diameter)
                pocket_name: str = f"{self.Name}_{index}"
                pocket: Fab_Pocket = Fab_Pocket(
                    pocket_name, mount, (circle_geometry,), depth)
                pocket.post_produce1(produce_state, expanded_operations, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=Fab_Hole.post_produce1()")

    # Fab_Hole.post_produce2():
    def post_produce2(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        """Perform Fab_Hole phase 1 post production."""

        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_Hole({self.Name}).post_produce2()")

        # Unpack the *mount* and associated *geometry_context*:
        mount: FabMount = self.Mount
        geometry_context: Fab_GeometryContext = mount._GeometryContext
        plane: FabPlane = geometry_context.Plane
        query: Fab_Query = geometry_context.Query

        key: Fab_HoleKey = self.Key
        kind: str = key.Kind
        join: FabJoin = self.Join
        depth: float = key.Depth
        fasten: FabFasten = join.Fasten
        diameter: Vector = fasten.get_diameter(kind)
        self.Depth = depth

        # Drill the holes in the in the rotated solid:
        # Collect the min/max x/y of the each *rotated_center* and drill the holes :
        max_x: float = 0.0
        max_y: float = 0.0
        min_x: float = 0.0
        min_y: float = 0.0
        rotated_centers: List[Vector] = []
        index: int
        center: Vector
        for index, center in enumerate(self.Centers):
            circle: FabCircle = FabCircle(plane, center, diameter)
            projected_circle: FabCircle = circle.projectToPlane(plane, tracing=next_tracing)
            projected_center: Vector = projected_circle.Center
            rotated_center: Vector = plane.rotateToZAxis(projected_center, tracing=next_tracing)
            rotated_centers.append(rotated_center)
            x: float = projected_center.x
            y: float = projected_center.y
            max_x = x if index == 0 else max(max_x, x)
            min_x = x if index == 0 else min(min_x, x)
            max_y = y if index == 0 else max(max_y, y)
            min_y = y if index == 0 else min(min_y, y)

            # Perform the *query* drill operation.
            query.move_to(rotated_center, tracing=next_tracing)
            query.hole(diameter, depth, tracing=next_tracing)

        # Create a new solid that encloses all of the holes:
        z_axis: Vector = Vector(0.0, 0.0, 1.0)
        if (plane.UnitNormal - z_axis).Length > 1.0e-8:
            self.JsonEnabled = False
        else:
            # Start with a new *holes_plane* and *holes_query*:
            self.StartDepth = plane.Distance
            holes_contact: Vector = Vector(0.0, 0.0, self.StartDepth)
            holes_plane: FabPlane = FabPlane(holes_contact, z_axis)
            holes_query: Fab_Query = Fab_Query(holes_plane)
            self.StartDepth = plane.Distance

            # Compute the closing solid corners.  The enclose face area must be greater the
            # drill face area so that the JSON reader code can distinguish between faces.
            # Thus, we make extend it by *diameter* in +/- X/Y.
            extra: float = diameter
            z: float = 0.0  # *z* is ignored.
            enclose_ne: Vector = Vector(max_x + extra, max_y + extra, z)
            enclose_nw: Vector = Vector(min_x - extra, max_y + extra, z)
            enclose_sw: Vector = Vector(min_x - extra, min_y - extra, z)
            enclose_se: Vector = Vector(max_x + extra, min_y - extra, z)

            # Create the enclosing extrusion:
            holes_query.copy_workplane(holes_plane, tracing=next_tracing)
            holes_query.move_to(enclose_ne)
            holes_query.line_to(enclose_nw)
            holes_query.line_to(enclose_sw)
            holes_query.line_to(enclose_se)
            holes_query.line_to(enclose_ne)
            holes_query.close()
            # The + 1.0mm ensures that there is always a bottom face at the hole bottom.
            # Thus there are no through holes in the final drilled extrusion.
            holes_query.extrude(depth + 1.0)  # TODO: 1.0 may be too high.  Use depth/100.0?

            # Drill the holes:
            for center in self.Centers:
                holes_query.move_to(center)  # TODO: Assume +Z axis for now.
                holes_query.hole(diameter, depth)
            self.HolesCount = len(self.Centers)

            prefix: Fab_Prefix = self.Prefix
            prefix_text: str = prefix.to_string()
            step_base_name: str = f"{prefix_text}__{self.Name}_holes"
            assembly: cq.Assembly = cq.Assembly(
                holes_query.WorkPlane, name=step_base_name, color=cq.Color(0.5, 0.5, 0.5, 1.0))

            holes_path: PathFile = produce_state.Steps.activate(step_base_name, self.getHash())
            self.StepFile: str = str(holes_path)

            if not holes_path.exists():
                with _suppress_stdout():
                    assembly.save(self.StepFile, "STEP")

            selected_shop_bit: Optional[Fab_ShopBit] = self.SelectedShopBit
            assert isinstance(selected_shop_bit, Fab_ShopBit), selected_shop_bit
            selected_bit: FabBit = selected_shop_bit.Bit
            assert isinstance(selected_bit, FabDrillBit), selected_bit
            material: FabMaterial = self.Mount.Solid.Material
            assert isinstance(material, FabMaterial), material

            tool_controller: FabToolController
            maxiumum_tool_depth: float
            tool_controller, maximum_tool_depth = FabToolController.computeToolController(
                material, selected_shop_bit, self.Depth)
            _ = maximum_tool_depth
            self.setBit(selected_bit, produce_state.BitsTable)
            self.set_tool_controller(tool_controller, produce_state.ToolControllersTable)

        if tracing:
            print(f"{tracing}<=Fab_Hole({self.Name}).post_produce2()")

    # Fab_Hole.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return the FabHole JSON."""
        start_depth: float = self.StartDepth
        extra_offset_modes: Tuple[str, ...] = ("2x Drill Tip", "Drill Tip", "None")
        json_dict: Dict[str, Any] = super().to_json()
        json_dict["HolesCount"] = self.HolesCount
        json_dict["StepFile"] = self.StepFile
        json_dict["ToolControllerIndex"] = 1  # TODO Fix
        json_dict["_Active"] = True
        json_dict["_ClearanceHeight"] = self.StartDepth + 1.0  # TODO: Fix
        json_dict["_CoolantMode"] = "Flood"  # TODO: Fix
        json_dict["_ExtraOffset"] = extra_offset_modes[2]
        json_dict["_FinalDepth"] = self.StartDepth - self.Depth
        json_dict["_PeckDepth"] = 2.0  # TODO: Fix
        json_dict["_PeckEnabled"] = False
        json_dict["_SafeHeight"] = start_depth + 5.0  # TODO: Fix
        json_dict["_StartDepth"] = start_depth

        return json_dict


# FabMount:
@dataclass
class FabMount(object):
    """FabMount: An operations plane that can be oriented for subsequent machine operations.

    This class basically corresponds to a FreeCad Datum Plane.  It is basically the surface
    to which the 2D FabGeometry's are mapped onto prior to performing each operation.

    Attributes:
    * *Name*: (str): The name of the FabPlane.
    * *Solid*: (FabSolid): The FabSolid to work on.
    * *Contact* (Vector): A point on the mount plane.
    * *Normal* (Vector): A normal to the mount plane
    * *Orient* (Vector):
      A vector that is projected onto the mount plane to specify orientation
      when mounted for CNC operations.
    * *Depth* (float): The maximum depth limit for all operations.
    * *WorkPlane* (Fab_Query): The CadQuery workplane wrapper class object.

    """

    _Name: str
    _Solid: "FabSolid"
    _Contact: Vector
    _Normal: Vector
    _Orient: Vector
    _Depth: float
    _Query: Fab_Query
    _Operations: List[Fab_Operation] = field(init=False, repr=False)
    _Fence: int = field(init=False, repr=False)  # Used to group operations
    _Copy: Vector = field(init=False, repr=False)  # Used for making private copies of Vector's
    _Tracing: str = field(init=False, repr=False)
    _GeometryContext: Fab_GeometryContext = field(init=False, repr=False)
    _AppDatumPlane: Any = field(init=False, repr=False)  # TODO: Remove
    _GuiDatumPlane: Any = field(init=False, repr=False)  # TODO: Remove
    _Plane: FabPlane = field(init=False, repr=False)
    Prefix: Optional[Fab_Prefix] = field(init=False, repr=False)

    # FabMount.__post_init__():
    def __post_init__(self) -> None:
        """Verify that FabMount arguments are valid."""
        solid: "FabSolid" = self._Solid
        tracing: str = solid.Tracing
        # next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).__post_init__()")

        # Do type checking here.
        check_type("FabMount.Name", self._Name, str)
        check_type("FabMount.Solid", self._Solid, FabSolid)
        check_type("FabMount.Contact", self._Contact, Vector)
        check_type("FabMount.Normal", self._Normal, Vector)
        check_type("FabMount.Orient", self._Orient, Vector)
        check_type("FabMount.Depth", self._Depth, float)
        check_type("FabMount.Query", self._Query, Fab_Query)

        copy: Vector = Vector()  # Make private copy of Vector's.
        self._Copy = copy
        self._Contact = self._Contact + copy
        self._Normal = self._Normal + copy
        self._Operations = []
        # Vector metheds like to modify Vector contents; force copies beforehand:
        self._Fence = 0
        self._Plane: FabPlane = FabPlane(self._Contact, self._Normal)  # , tracing=next_tracing)
        self._Orient = self._Plane.projectPoint(self._Orient)
        self._GeometryContext = Fab_GeometryContext(self._Plane, self._Query)
        self._AppDatumPlane = None
        self._GuiDatumPlane = None
        self.Prefix = None

        if tracing:
            print(f"{tracing}{self._Contact=} {self._Normal=}")
            print(f"{tracing}{self._Depth=} {self._GeometryContext=}")
            print(f"{tracing}<=FabMount({self.Name}).__post_init__()")

    # FabMount.Fenct():
    @property
    def Fence(self) -> int:
        """Return the FabMount fence operations sub-group number."""
        return self._Fence

    # FabMount.Name():
    @property
    def Name(self) -> str:
        """Return the FabMount name."""
        return self._Name

    # FabMount.Solid:
    @property
    def Solid(self) -> "FabSolid":
        """Return the FabSolid."""
        return self._Solid  # pragma: no unit cover

    # FabMount.Body:
    @property
    def Body(self) -> Any:
        """Return PartBodyBase fr FabMount."""
        return self._Solid.Body  # pragma: no unit cover

    # FabMount.Contact:
    @property
    def Contact(self) -> Vector:
        """Return the FabMount contact point."""
        return self._Contact + self._Copy  # pragma: no unit cover

    # FabMount.Normal:
    @property
    def Normal(self) -> Vector:
        """Return the FabMount normal."""
        return self._Normal + self._Copy  # pragma: no unit cover

    # FabMount.Orient:
    @property
    def Orient(self) -> Vector:
        """Return the FabMount Orientation."""
        return self._Orient + self._Copy  # pragma: no unit cover

    # FabMount.Plane:
    @property
    def Plane(self) -> FabPlane:
        """Return the FabPlane."""
        return self._Plane

    # FabMount.Depth:
    @property
    def Depth(self) -> float:
        """Return the depth."""
        return self._Depth  # pragma: no cover

    # FabMount.lookup_prefix():
    def lookup_prefix(self, operation_name: str) -> Fab_Prefix:
        """Return the Fab_Prefix for an operation."""
        solid: FabSolid = self._Solid
        prefix: Fab_Prefix = solid.lookup_prefix(self.Name, operation_name)
        return prefix

    # FabMount.fence():
    def fence(self) -> None:
        """Put a fence between operations to keep sub-groups together."""
        self._Fence += 1  # pragma: no unit cover

    # FabMount.getHash():
    def getHash(self) -> Tuple[Any, ...]:
        """Return a has the current contents of a FabMount."""
        hashes: List[Any] = [
            "FabMount",
            self._Name,
            f"{self._Contact.x:.6f}",
            f"{self._Contact.y:.6f}",
            f"{self._Contact.z:.6f}",
            f"{self._Normal.x:.6f}",
            f"{self._Normal.y:.6f}",
            f"{self._Normal.z:.6f}",
            f"{self._Depth:.6f}",
        ]
        operation: Fab_Operation
        for operation in self._Operations:
            hashes.append(operation.getHash())
        return tuple(hashes)

    # FabMount.record_operation():
    def record_operation(self, operation: Fab_Operation) -> None:
        """Record an operation to a FabMount."""
        if not isinstance(operation, Fab_Operation):
            raise RuntimeError(
                f"FabMount.add_operation({self._Name}).{type(operation)} "
                "is not an Fab_Operation")  # pragma: no unit cover
        self._Operations.append(operation)

    # FabMount.setGeometryGroup():
    def setGeometryGroup(self, geometry_group: Any) -> None:
        """Set the FabMount GeometryGroup need for the FabGeometryContex."""
        self._GeometryContext.setGeometryGroup(geometry_group)  # pragma: no unit covert

    # FabMount.post_produce1():
    def post_produce1(
            self, produce_state: Fab_ProduceState,
            expanded_mounts: List["FabMount"], tracing: str = "") -> None:
        """Expand both Mounts and Operations within each Mount."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabMount.post_produce1('{self.Name}'):")

        # Scan *operations* and perform conversions/expansions as needed into *expanded_operations*:
        operations: List[Fab_Operation] = self._Operations
        before_operations_size: int = len(operations)
        expanded_operations: List[Fab_Operation] = []
        operation: Fab_Operation
        for operation in self._Operations:
            operation.post_produce1(produce_state, expanded_operations, tracing=next_tracing)

        # Perform the initial sort of *expanded_operations*.  This maintains fence sub-groups
        # and maintains operation order (e.g. center drill before drill, etc.)
        expanded_operations.sort(key=Fab_Operation.getInitialOperationKeyTrampoline)

        # The goal here is to minimize the number of times that a part needs to be moved between
        # shops and machines.  Each time the part has to visit another machine is annoying.
        same_machine_operations: List[Fab_Operation] = []

        # Now the *expanded_operations* need to select a specific Fab_ShopBit.  The preference
        # is to always select one from the current shop and machine.  Failing that, a machine
        # in the same shop is preferred.  Failing that, any machine from any shop that can do
        # the operation is selected.  *expanded_mounts* is filled with one or more copies of
        # the current Fab_Mount (i.e. *self*), where each individual Fab_Mount has Fab_ShopBit's
        # are on the same machine.

        # Helper function to create a copy of *self* that contains *operations*:
        def flush_operations(
                operations: List[Fab_Operation], expanded_mounts: List[FabMount]) -> None:
            """Flush a list of Fab_Operation's into a new FabMount."""
            if len(operations) > 0:
                copied_operations: List[Fab_Operation] = operations[:]
                del operations[:]
                new_name: str = self._Name
                if len(expanded_mounts) == 0:
                    new_name = f"{self._Name}{len(expanded_mounts)+1:03d}"
                new_mount: FabMount = FabMount(
                    new_name, self._Solid, self._Contact, self._Normal, self._Orient,
                    self._Depth, self._Query)
                new_mount._Operations = copied_operations
                expanded_mounts.append(new_mount)

        # Sweep across *expanded_operations*:
        current_shop_index: int = produce_state.CurrentShopIndex
        current_machine_index: int = produce_state.CurrentMachineIndex
        for operation in expanded_operations:
            same_machine_shop_bit: Optional[Fab_ShopBit] = None
            same_shop_bit: Optional[Fab_ShopBit] = None
            other_shop_bit: Optional[Fab_ShopBit] = None

            # Sweep across *shop_bits* to select the closest to the current machine.
            shop_bits: Tuple[Fab_ShopBit, ...] = operation.ShopBits
            for shop_bit in shop_bits:
                if shop_bit.ShopIndex == current_shop_index:
                    if shop_bit.MachineIndex == current_machine_index:
                        if same_machine_shop_bit is None:
                            same_machine_shop_bit = shop_bit
                            break  # This is the one to use, no need to look any further.
                    else:  # pragma: no unit cover
                        if same_shop_bit is None:
                            same_shop_bit = shop_bit
                elif other_shop_bit is None:  # pragma: no unit cover
                    other_shop_bit = shop_bit

            # Now decide if a machine switch happened:
            if same_machine_shop_bit is not None:
                operation.selectShopBit(same_machine_shop_bit)
                same_machine_operations.append(operation)
            else:  # pragma: no unit cover
                if same_shop_bit is not None:  # pragma: no unit cover
                    operation.selectShopBit(same_shop_bit)
                    current_machine_index = same_shop_bit.ShopIndex
                elif other_shop_bit is not None:  # pragma: no unit cover
                    operation.selectShopBit(other_shop_bit)
                    current_shop_index = other_shop_bit.ShopIndex
                    current_machine_index = other_shop_bit.MachineIndex
                else:  # pragma: no unit cover
                    raise RuntimeError("FabMount.post_produce1(): No matching shop bit found.")
                # Create operation here:
                flush_operations(same_machine_operations, expanded_mounts)
                same_machine_operations = [operation]

        # Wrap up *expanded_operations*:
        flush_operations(same_machine_operations, expanded_mounts)
        produce_state.CurrentShopIndex = current_shop_index
        produce_state.CurrentMachineIndex = current_machine_index

        if tracing:
            print(f"{tracing}=>FabMount.post_produce1('{self.Name}'): "
                  f"|{before_operations_size}| => |{len(expanded_operations)}|")

    # FabMount.post_produce2():
    def post_produce2(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        """Perform FabMount phase 1 post production."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabMount.post_produce2('{self.Name}')")

        # If there are no *operations* there is nothing to do:
        operations: List[Fab_Operation] = self._Operations
        if operations:
            # Create the FabPlane used for the drawing support.
            plane: FabPlane = self.Plane
            assert isinstance(plane, FabPlane), plane
            contact: Vector = plane.Contact
            normal: Vector = plane.Normal

            if tracing:
                print(f"{tracing}Name={self._Name}")
                print(f"{tracing}Solid={self._Solid.Label}")
                print(f"{tracing}Contact={contact}")
                print(f"{tracing}Normal={normal}")
                print(f"{tracing}Orient={self._Orient}")
                print(f"{tracing}Depth={self._Depth}")
                print(f"{tracing}Contact={contact}")
                print(f"{tracing}{plane=}")

            query: Optional[Fab_Query] = self._Solid._Query
            assert isinstance(query, Fab_Query), query
            query.copy_workplane(plane, tracing=next_tracing)

            # Process each *operation* in *operations*:
            operation_index: int = 0
            operation: Fab_Operation
            for operation in operations:
                if tracing:
                    print(f"{tracing}Operation[{operation.Name}]:")
                produce_state.OperationIndex = operation_index
                operation.post_produce2(produce_state, tracing=next_tracing)
                operation_index += 1

        # Install the FabMount (i.e. *self*) and *datum_plane* into *model_file* prior
        # to recursively performing the *operations*:
        if tracing:
            print(f"{tracing}<=FabMount.produce('{self.Name}')")

    # FabMount.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return FabMount JSON structure."""
        json_operations: List[Any] = []
        operations: List[Fab_Operation] = self._Operations
        operation: Fab_Operation
        for operation in operations:
            if isinstance(operation, (Fab_Extrude, Fab_Pocket, Fab_Hole)):
                if operation.JsonEnabled:
                    json_operations.append(operation.to_json())

        contact: Vector = self._Contact
        normal: Vector = self._Normal
        orient: Vector = self._Orient
        json_dict: Dict[str, Any] = {
            "Kind": "Mount",
            "Label": self.Name,
            "_Contact": [contact.x, contact.y, contact.z],
            "_Normal": [normal.x, normal.y, normal.z],
            "_Orient": [orient.x, orient.y, orient.z],
            "children": json_operations,
        }
        return json_dict

    # FabMount.extrude():
    def extrude(self, name: str, shapes: Union[FabGeometry, Tuple[FabGeometry, ...]],
                depth: float, contour: bool = True, debug: bool = False, tracing: str = "") -> None:
        """Perform a extrude operation.

        Arguments:
        * *name* (str): The user name of the operation that shows up various generated files.
        * *shapes* (Union[FabGeometry, Tuple[FabGeometry]]):
          Either FabGeometry the specifies the exterior, or multiple FabGeometry's where
          the first specifies the exterior and the are interior "holes".
        * *depth* (float): The depth (i.e. length) of the extrusion.  (Default: True)
        * *contour* (bool):
          If True, an exterior contour operation is scheduled; otherwise, no contour operation
          occurs. (Default: True)
        * *debug* (bool): If True, the extrude solid is made visble; otherwise it is not shown.
        """
        tracing = self._Solid.Tracing
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).extrude('{name}', *, {depth}, {contour})")

        # Figure out the contact
        top_contact: Vector = self._Contact
        normal: Vector = self._Normal / self._Normal.Length
        bottom_contact: Vector = top_contact - depth * normal
        top_plane: FabPlane = FabPlane(top_contact, normal)
        bottom_plane: FabPlane = FabPlane(bottom_contact, normal)
        if tracing:
            print(f"{tracing}{top_contact=} {normal=} {bottom_contact=}")

        # Compute a bounding box that encloses all of the associated *geometries*:
        boxes: List[FabBox] = []
        geometries: Tuple[FabGeometry, ...]
        if isinstance(shapes, FabGeometry):
            geometries = (shapes,)
        else:  # pragma: no unit cover
            geometries = shapes
        geometry: FabGeometry
        for geometry in geometries:
            # if tracing:
            #     print(f"{tracing}{geometry=}")
            boxes.append(geometry.projectToPlane(top_plane).Box)
            boxes.append(geometry.projectToPlane(bottom_plane).Box)
        self._Solid.enclose(boxes)

        # Create and record the *extrude*:
        extrude: Fab_Extrude = Fab_Extrude(name, self, shapes, depth, contour)
        self.record_operation(extrude)

        if tracing:
            print(f"{tracing}<=FabMount({self.Name}).extrude('{name}', *, {depth}, {contour})")

    # FabMount.pocket():
    def pocket(self, name: str, shapes: Union[FabGeometry, Tuple[FabGeometry, ...]],
               depth: float, debug: bool = False, tracing: str = "") -> None:
        """Perform a pocket operation.

        Arguments:
        * *name* (str): The name of the pocket.
        * *shapes* (Union[FabGeometry, Tuple[FabGeometry, ...]]):
          Either a single FabGeometry or a tuple of FabGeometry's.  The first FabGeometry specifies
          the pocket boundary.
        * *depth* (float): The pocket depth in millimeters from the mount plane.
        * *debug* (bool): If True, the pocket solid is made visible; otherwise it is not shown.
        """
        # TODO: Add the ability to do pockets in pockets.
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).pocket('{name}', *)")

        assert check_argument_types()
        if isinstance(shapes, FabGeometry):
            shapes = (shapes,)
        pocket: Fab_Pocket = Fab_Pocket(name, self, shapes, depth)
        self.record_operation(pocket)

        if tracing:
            print(f"{tracing}<=FabMount({self.Name}).pocket('{name}', *)")

    # FabMount.drill_joins():
    def drill_joins(self, joins_name: str, joins: Union[FabJoin, Sequence[FabJoin]],
                    debug: bool = False, tracing: str = "") -> None:
        """Drill some FabJoin's into a FabMount.

        Arguments:
        * *joins_name* (str):
          A user name for the all of the joins.  This name is used in file names, labels, etc..
        * *joins* (Union[FabJoin, Sequence[FabJoin]]):
        * *debug* (bool):  If True, the joins solid is made visible; otherwise it is not.
        """

        EPSILON: float = 1.0e-8

        # close():
        def close(vector1: Vector, vector2: Vector) -> bool:
            """Return whether 2 normals are very close to one another."""
            return (vector1 - vector2).Length < EPSILON

        # Quickly convert a single FabJoin into a tuple:
        if isinstance(joins, FabJoin):
            joins = (joins,)  # pragma: no unit cover
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).drill_joins(|{len(joins)}|")

        # mount_contact: Vector = self._Contact
        mount_normal: Vector = self._Normal / self._Normal.Length
        # mount_plane: FabPlane = FabPlane(mount_contact, mount_normal)
        mount_depth: float = self._Depth
        solid: "FabSolid" = self._Solid

        # Collects compatible holes in *hole_groups*:
        HoleInfo = Tuple[FabJoin, int, Vector, str]  # (join, joint_index, trimmed_start, name)
        hole_info: HoleInfo
        hole_groups: Dict[Fab_HoleKey, List[HoleInfo]] = {}
        hole_name: str
        hole_key: Fab_HoleKey
        join_index: int  # Used for forcing individual drill operations (see below):
        for join_index, join in enumerate(joins):
            assert isinstance(join, FabJoin), f"{type(join)} is not a FabJoin"
            fasten: FabFasten = join.Fasten

            if join.normal_aligned(mount_normal):
                join_start: Vector = join.Start
                join_end: Vector = join.End
                # if tracing:
                #     print(f"{tracing}>>>>>>>>{join.Name} "
                #            f"aligns {solid.Name}: {join_start}=>{join_end}")
                intersect: bool
                trimmed_start: Vector
                trimmed_end: Vector
                intersect, trimmed_start, trimmed_end = solid.intersect(join_start, join_end)
                if intersect:
                    trimmed_length: float = (trimmed_start - trimmed_end).Length
                    trimmed_depth: float = min(trimmed_length, mount_depth)
                    if tracing:
                        print(f"{tracing}>>>>>>>>>>>>>>>>{join.Name} intesects {solid.Label}")
                        # print(f"{tracing}{solid.Name} Box: {solid.TNE} : {solid.BSW}")
                        # print(f"{tracing}Join:    {join_start} => {join_end}")
                        # nprint(f"{tracing}Trimmed: {trimmed_start} => {trimmed_end}")
                        # print(f"{tracing}Mount - Depth: {mount_start} {trimmed_depth}")
                    is_top: bool = close(join_start, trimmed_start)
                    # TODO: figure out *kind*:
                    kind: str = "close"  # or "thread", or "loose"
                    if tracing:
                        print(f"{tracing}{mount_depth=} {trimmed_depth=}")
                    assert trimmed_depth > 0.0, trimmed_depth
                    # unique: int = -1 if mount_z_aligned else join_index
                    hole_name = f"{joins_name}_{join_index}"
                    hole_key = Fab_HoleKey(fasten.ThreadName, kind, trimmed_depth, is_top)

                    # Compatible *trimmed_start*'s are collected in *hole_groups*:
                    if hole_key not in hole_groups:
                        hole_groups[hole_key] = []
                    hole_info = (join, join_index, trimmed_start, hole_name)
                    hole_groups[hole_key].append(hole_info)

        # Create *grouped_holes* where each *group_hole* has the same *key*.
        grouped_holes: List[Fab_Hole] = []
        grouped_hole: Fab_Hole
        hole_infos: List[HoleInfo]
        for hole_key, hole_infos in hole_groups.items():
            trimmed_starts: List[Vector] = []
            for join, join_index, trimmed_start, hole_name in hole_infos:
                trimmed_starts.append(trimmed_start)
            centers: Tuple[Vector, ...] = tuple(trimmed_starts)
            grouped_hole = Fab_Hole(hole_name, self, hole_key, centers, join, hole_key.Depth)
            grouped_holes.append(grouped_hole)

        hole_index: int
        for hole_index, hole in enumerate(grouped_holes):
            if tracing:
                print(f"{tracing}Hole[{hole_index}]: record_operation({hole})")
            self.record_operation(hole)

        if tracing:
            print(f"{tracing}<=FabMount({self.Name}).drill_joins(|{len(joins)}|")


# FabSolid:
@dataclass
class FabSolid(FabNode):
    """Fab: Represents a single 3D solid that is represented as a STEP file.

    Inherited Attributes:
    * *Name* (str): The model name.
    * *Parent* (FabNode): The Parent FabNode.

    Attributes:
    * *Material* (str): The material to use.
    * *Color* (str): The color to use.

    Constructor:
    * FabSolid("Name", Parent, Material, Color)

    """

    Material: FabMaterial
    Color: str
    _Mounts: List[FabMount] = field(init=False, repr=False)
    _GeometryGroup: Optional[Any] = field(init=False, repr=False)
    _Body: Optional[Any] = field(init=False, repr=False)  # TODO: remove?
    _Query: Fab_Query = field(init=False, repr=False)
    _Assembly: Any = field(init=False, repr=False)
    _StepFile: Optional[PathFile] = field(init=False, repr=False)
    _Color: Optional[Tuple[float, ...]] = field(init=False, repr=False)
    Prefix: Fab_Prefix = field(init=False, repr=False)
    MountOperationPrefixes: Dict[str, Dict[str, Fab_Prefix]] = field(init=False, repr=False)

    # FabSolid.__post_init__():
    def __post_init__(self) -> None:
        """Verify FabSolid arguments."""
        super().__post_init__()
        tracing: str = self.Tracing
        next_tracing: str = tracing + " " if tracing else ""
        _ = next_tracing  # Until it is used elsewhere.
        if tracing:
            print(f"{tracing}=>FabSolid({self.Label}).__post_init__()")
        check_type("FabSolid.Material", self.Material, FabMaterial)
        check_type("FabSolid.Color", self.Color, str)
        # Initial WorkPlane does not matter, it gets set by FabMount.
        origin: Vector = Vector(0.0, 0.0, 0.0)
        z_axis: Vector = Vector(0.0, 0.0, 1.0)
        initial_plane: FabPlane = FabPlane(origin, z_axis)  # , tracing=next_tracing)
        self._Mounts = []
        self._GeometryGroup = None
        self._Body = None
        self._Query = Fab_Query(initial_plane)
        self._Assembly = None
        self._StepFile = None
        self._Color = None
        # See FabSolid.lookup_prefix() for an explanation of MountOperationPrefixes.
        self.MountOperationPrefixes = {}

        # Extract all *all_documents* from *project*:
        project: FabNode = self.Project
        assert project.is_project()

        # Find the *solid_document* that contains this FabSolid (i.e. *self*).
        solid_document: FabNode = self
        while not solid_document.is_document():
            assert not solid_document.is_project(), "Did not find document"
            solid_document = solid_document.Up
        assert solid_document.is_document(), solid_document

        # Determine the *document_index* for *solid_document
        document_index: int
        document: FabNode
        for document_index, document in enumerate(project.Children):
            if document is solid_document:
                break
        else:  # pragma: no unit cover
            raise RuntimeError("Could not find document")

        # Extract *all_solids* from *document*:
        def find_solids(node: FabNode, all_solids: List[FabSolid]) -> None:
            if isinstance(node, FabSolid):
                all_solids.append(node)
            else:
                child: FabNode
                for child in node.Children:
                    find_solids(child, all_solids)
        all_solids: List[FabSolid] = []
        find_solids(document, all_solids)

        # Extract the *solid_index* from *all_solids*:
        solid_index: int
        for solid_index, solid in enumerate(all_solids):
            if tracing:
                print(f"{tracing}[{solid_index}]: {solid.Label}")
            if solid is self:
                break
        else:  # pragma: no unit cover
            raise RuntimeError("Could not find solid")

        # Set the FabPrefix for *self*:
        self.Prefix = Fab_Prefix(document_index + 1, solid_index + 1, 0, 0)

        if tracing:
            print(f"{tracing}<=FabSolid({self.Label}).__post_init__()")

    # FabSolid.lookup_prefix():
    def lookup_prefix(self, mount_name: str, operation_name: str) -> Fab_Prefix:
        """Return the Fab_Prefix for a mount/operation name pair."""

        # Th FabProject, FabDocument, FabAssembly, and FabSolid sub-classes of FabNode are
        # all instantiated once at startup as a FabNode tree.  Thus, assigning a unique
        # Fab_Prefix to each of these object can easily be done in the appropriate constructor.
        #
        # The iterative nataure of constraint propagation causes the *produce* method of
        # each FabNode to be called multiple times.  This causes the recreation of multiple
        # FabMount's and Fab_Operation sub-classes (e.g. Fab_Extrude, Fab_Pocket, Fab_Hole, etc.)
        # These Fab_Operation sub-classes keep being recreated until constraint propagation ends.
        #
        # For debugging and consistency reasons, it is nice to have a "sticky" Fab_Prefix
        # that does not change as a result of constraint propagation changes.  The "sticky"
        # Fab_Prefix's for FabMounts and Fab_Operations are stored in the FabSolid MountOperations
        # attribute.  This attribute is an Dict of Dict's, where the first level is keyed off a
        # mount name and the second level is keyed of an operation name.  Once a Fab_Prefix
        # is assigned to mount/operation name pair, it no longer changes.

        mount_operations: Dict[str, Dict[str, Fab_Prefix]] = self.MountOperationPrefixes

        # The second level dictionary has a key of "" that contains the Mount Fab_Prefix.
        # All remaining entries in the second level dictionary contain Fab_Prefix's that
        # correspond to an explicit operation name.
        operations: Dict[str, Fab_Prefix]
        mount_prefix: Fab_Prefix
        if mount_name in mount_operations:
            operations = mount_operations[mount_name]
        else:
            solid_prefix: Fab_Prefix = self.Prefix
            mount_prefix = Fab_Prefix(
                solid_prefix.DocumentIndex, solid_prefix.SolidIndex, len(mount_operations) + 1, 0)
            operations = {"": mount_prefix}
            mount_operations[mount_name] = operations

        operation_prefix: Fab_Prefix
        if operation_name in operations:
            operation_prefix = operations[operation_name]
        else:
            mount_prefix = operations[""]
            assert mount_prefix.DocumentIndex > 0
            assert mount_prefix.SolidIndex > 0
            assert mount_prefix.MountIndex > 0
            assert len(operations) > 0
            operation_prefix = Fab_Prefix(mount_prefix.DocumentIndex, mount_prefix.SolidIndex,
                                          mount_prefix.MountIndex, len(operations))
            operations[operation_name] = operation_prefix
        return operation_prefix

    # FabSolid.Body():
    @property
    def Body(self) -> Any:  # pragma: no unit cover
        """Return BodyBase for FabSolid."""
        if not self._Body:
            raise RuntimeError(
                f"FabSolid.Body({self.Label}).Body(): body not set yet")
        return self._Body

    # FabSolid.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return FabProject JSON structure."""
        json_dict: Dict[str, Any] = super().to_json()
        json_dict["Kind"] = "Solid"
        if self._StepFile:
            json_dict["StepFile"] = str(self._StepFile)
        if self._Color:
            json_dict["_Color"] = self._Color  # pragma: no unit cover
        json_mounts: List[Any] = []
        name: str
        mount: FabMount
        for mount in self._Mounts:
            # Skip mount if it has no operations.
            if len(mount._Operations) > 0:
                json_mounts.append(mount.to_json())
        json_dict["children"] = json_mounts
        return json_dict

    # FabSolid.set_body():
    def set_body(self, body: Any) -> None:
        """Set the BodyBase of a FabSolid."""
        self._Body = body  # pragma: no unit cover

    # FabSolid.is_solid():
    def is_solid(self) -> bool:
        """ Return True if FabNode is a FabAssembly."""
        return True  # All other FabNode's return False.  # pragma: no unit cover

    # FabSolid.pre_produce():
    def pre_produce(self, produce_state: Fab_ProduceState) -> None:
        """Perform FabSolid pre production."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabSolid({self.Label}).pre_produce()")
        self._Mounts = []
        if tracing:
            print(f"{tracing}{len(self._Mounts)=}")
            print(f"{tracing}<=FabSolid({self.Label}).pre_produce()")

    # FabSolid.post_produce1():
    def post_produce1(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        """Perform FabSolid pre production."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabSolid.post_produce1({self.Label})")

        # Reset the preferred shop and machine.
        produce_state.CurrentShopIndex = 0
        produce_state.CurrentMachineIndex = 0

        # Expand the operations for each *mount*:
        mount: FabMount
        expanded_mounts: List[FabMount] = []
        for mount in self._Mounts:
            mount.post_produce1(produce_state, expanded_mounts, tracing=next_tracing)
        self._Mounts = expanded_mounts

        if tracing:
            print(f"{tracing}<=FabSolid.post_produce1({self.Label})")

    # FabSolid.getHash():
    def getHash(self) -> Tuple[Any, ...]:
        """Return FabSolid hash."""
        hashes: List[Any] = [
            "FabSolid",
            self.Material,
            self.Color,
        ]
        mount: FabMount
        for mount in self._Mounts:
            hashes.append(mount.getHash())
        return tuple(hashes)

    # FabSolid.mount():
    def mount(self, name: str, plane: FabPlane, orient: Vector,
              depth: float, tracing: str = "") -> FabMount:
        """Add a new FabMount to ae FabSolid.

        Arguments:
        * *name* (str): The name of the mount.
        * *plane* (FabPlane): The FabMount plane.
        * *orient* (Vector): The orientation of the FabMount for CNC operations.

        Returns:
        * (FabMount): The Resulting FabMount object.

        """
        if tracing:
            print(f"{tracing}=>FabSolid({self.Label}).mount('{name}', ...)")

        mounts: List[FabMount] = self._Mounts
        self.LastMountPrefix = None
        fab_mount: FabMount = FabMount(
            name, self, plane.Contact, plane.Normal, orient, depth, self._Query)
        mounts.append(fab_mount)

        if tracing:
            print(f"{tracing}=>FabSolid({self.Label}).mount('{name}', ...)=>{fab_mount}")
        return fab_mount

    # FabSolid.drill_joins():
    def drill_joins(self, name: str, joins: Sequence[FabJoin],
                    mounts: Optional[Sequence[FabMount]] = None) -> None:
        """Apply drill FabJoin holes for a FabSolid.

        Iterate pairwise through a sequence of FabJoin's and FabMount's and for each pair
        attempt to drill a bunch the FabJoin holes for the associated FabSolid.  The drill
        operation only occurs if the FabJoin is in alignment with the FabMount normal (in
        either direction) *and* if the FabJoin intersects with the underlying FabSolid;
        otherwise nothing is for that particular FabMount and FabJoin pair.

        Arguments:
        * *name* (str): The collective name for all of the drills.
        * *joins* (Optional[Sequence[FabJoin]]):
          The tuple/list of FabJoin's to apply.
        * *mounts* (Optional[Sequence[FabMount]]):
          The mounts to to apply the *joins* to.  If *mounts* is *None*, all of the
          mounts for the current FabSolid are used.  (Default: None)

        For now, please call this method after all FabMount's are created.
        """
        tracing: str = self.Tracing
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabSolid({self.Label}).drill_joins('{name}', *)")

        if mounts is None:
            mounts = tuple(self._Mounts)
        mount: FabMount
        for mount in mounts:
            mount.drill_joins(name, joins, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=FabSolid({self.Label}).drill_joins('{name}', *)")

    # FabSolid.post_produce2():
    def post_produce2(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        """Perform FabSolid Phase2 post production."""
        tracing = self.Tracing  # Ignore *tracing* argument.
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabSolid.post_produce2('{self.Label}')")

        # Deterimine whether it is possible to *use_cached_step*:
        step_path: PathFile = cast(PathFile, None)  # Force runtime error if used.
        # This was a shocker.  It turns out that __hash__() methods are not necessarily
        # consistent between Python runs.  In other words  __hash__() is non-deterministic.
        # Instead use one of the hashlib hash functions instead:
        #     hash_tuple => repr string => hashlib.sha256 => trim to 16 bytes
        hash_tuple: Tuple[Any, ...] = self.getHash()
        prefix: Fab_Prefix = self.Prefix
        assert isinstance(prefix, Fab_Prefix)
        solid_name: str = f"{prefix.to_string()}__{self.Label}"
        step_path = produce_state.Steps.activate(solid_name, hash_tuple)
        use_cached_step: bool = False
        if step_path.exists():
            use_cached_step = True  # pragma: no unit cover
        self._StepFile = step_path

        # Perform all of the mount operations if unable to *use_cached_step*:
        if not use_cached_step:
            mounts: List[FabMount] = self._Mounts
            if tracing:
                print(f"{tracing}Iterate over |{len(mounts)}| mounts")
            mount_name: str
            mount: FabMount
            for mount in mounts:
                if tracing:
                    print(f"{tracing}[{mount._Name}]: process")
                mount.post_produce2(produce_state, tracing=next_tracing)

        # CadQuery workplanes do not have a color, but Assemblies do.
        rgb_color: Tuple[float, float, float] = FabColor.svg_to_rgb(self.Color)
        # TODO: move this code into Fab_Query:

        assembly: cq.Assembly
        if use_cached_step:  # pragma: no unit cover
            # Read in step file here:
            work_plane: cq.Workplane = cq.importers.importStep(str(step_path))
            assembly = cq.Assembly(work_plane, name=self.Label, color=cq.Color(*rgb_color))
            self._Color = rgb_color
            if tracing:
                print(f"{tracing}Read file '{str(step_path)}' !")
        else:
            assembly = cq.Assembly(
                self._Query.WorkPlane, name=self.Label, color=cq.Color(*rgb_color))
            # This is really ugly.  The cq.Assembly.save() method spews out uninteresting
            # "debug" information.  See the code comments of _suppress_stdout() for more
            # information.
            with _suppress_stdout():
                assembly.save(str(step_path), "STEP")
            if tracing:
                print(f"{tracing}Wrote out {str(step_path)}")
        self._Assembly = assembly
        produce_state.ObjectsTable[self.Label] = assembly

        if tracing:
            print(f"{tracing}<=FabSolid.post_produce2('{self.Label}')")

    # FabSolid._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run FabSolid unit tests."""
        if tracing:
            print(f"{tracing}<=>FabSolid._unit_tests()")


# TODO: Remove
def visibility_set(element: Any, new_value: bool = True, tracing: str = "") -> None:
    """Set the visibility of an element."""
    if tracing:
        print(f"{tracing}<=>visibility_set({element}, {new_value})")
    assert False


# TODO: Add unit tests.
def main(tracing: str = "") -> None:
    """Run unit tests for FabSolids module."""
    next_tracing: str = tracing + " " if tracing else ""
    if tracing:
        print(f"{tracing}=>FabSolids.main()")

    Fab_HoleKey._unit_tests(tracing=next_tracing)
    Fab_OperationOrder._unit_tests(tracing=next_tracing)
    Fab_OperationKind._unit_tests(tracing=next_tracing)
    Fab_OperationKey._unitTests(tracing=next_tracing)
    FabStock._unit_tests(tracing=next_tracing)
    FabSolid._unit_tests(tracing=next_tracing)

    if tracing:
        print(f"{tracing}<=FabSolids.main()")


if __name__ == "__main__":
    main(tracing=" ")
