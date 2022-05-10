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

from collections import OrderedDict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, cast, Dict, Generator, IO, List, Optional, Sequence, Tuple, Union

import cadquery as cq  # type: ignore
from cadquery import Vector  # type: ignore

# import Part  # type: ignore

from FabGeometries import FabCircle, FabGeometry, Fab_GeometryContext, Fab_Plane, Fab_Query
from FabJoins import FabFasten, FabJoin
from FabNodes import FabBox, FabNode, Fab_ProduceState
from FabUtilities import FabColor, FabToolController

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
    """FabStock: Represents the stock matereial for machine a part from.

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
    def __post__init__(self) -> None:
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
                count += 1
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
            stock_dz = adjust(box_dz, z_increment)

        offset: Vector = Vector(stock_dx / 2.0, stock_dy / 2.0, stock_dz / 2.0)
        center: Vector = box.C
        stock_bsw: Vector = center - offset
        stock_tne: Vector = center + offset
        return (stock_bsw, stock_tne)

    # FabStock._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """FabStock unit tests."""
        inch: float = 2.54
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
        print(f"{box.BSW=} {box.TNE=}")
        results: Tuple[Vector, Vector] = stock.enclose(box)
        print(f"{results=}")
        _ = results


# Fab_Operation:
@dataclass(order=True)
class Fab_Operation(object):
    """Fab_Operation: An base class for FabMount operations -- Fab_Extrude, Fab_Pocket, FabHole, etc.

    Attributes:
    * *Mount* (FabMount):
      The FabMount to use for performing operations.
    * *ToolController* (Optional[FabToolController]):
      The tool controller (i.e. speeds, feeds, etc.) to use. (Default: None)
    * *ToolControllerIndex* (int):
      The tool controller index associated with the tool controller.  (Default: -1)
    * *JsonEnabled* (bool):
      Enables the generation of JSON if True, otherwise suppresses it.  (Default: True)
    * *Active* (bool):
      If True, the resulting operation is performed.  About the only time this is set to False
      is for an extrude of stock material like a C channel, I beam, etc.  (Default: True)

    """

    _Mount: "FabMount" = field(repr=False, compare=False)
    _ToolController: Optional[FabToolController] = field(init=False, repr=False)
    _ToolControllerIndex: int = field(init=False)
    _JsonEnabled: bool = field(init=False)
    _Active: bool = field(init=False)

    # Fab_Operation.__post_init__():
    def __post_init__(self) -> None:
        """Initialize Fab_Operation."""
        # TODO: Enable check:
        # if not self._Mount.is_mount():
        #   raise RuntimeError("Fab_Operation.__post_init__(): {type(self._Mount)} is not FabMount")
        self._ToolController = None
        self._ToolControllerIndex = -1  # Unassigned.
        self._JsonEnabled = True
        self._Active = True

    # Fab_Operation.get_tool_controller():
    def get_tool_controller(self) -> FabToolController:
        """Return the Fab_Operation tool controller"""
        if not self._ToolController:
            raise RuntimeError("Fab_Operation().get_tool_controller(): ToolController not set yet.")
        return self._ToolController

    # Fab_Operation.set_tool_controller():
    def set_tool_controller(self, tool_controller: FabToolController,
                            tool_controllers_table: Dict[FabToolController, int]) -> None:
        """Set the Fab_Operation tool controller and associated index."""
        tool_controller_index: int
        if tool_controller in tool_controllers_table:
            tool_controller_index = tool_controllers_table[tool_controller]
            self._ToolController = None
        else:
            tool_controller_index = len(tool_controllers_table)
            tool_controllers_table[tool_controller] = tool_controller_index
            self._ToolController = tool_controller
        self._ToolControllerIndex = tool_controller_index

    # Fab_Operation.get_kind():
    def get_kind(self) -> str:
        """Return Fab_Operation kind."""
        raise RuntimeError(f"Fab_Operation().get_kind() not implemented for {type(self)}")

    # Fab_Operation.get_name():
    def get_name(self) -> str:
        """Return Fab_Operation name."""
        raise RuntimeError(f"Fab_Operation().get_name() not implemented for {type(self)}")

    # Fab_Operation.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return Fab_Operation hash."""
        raise RuntimeError(f"Fab_Operation().get_hash() not implemented for {type(self)}")

    # Fab_Operation.Mount():
    @property
    def Mount(self) -> "FabMount":
        """Return Fab_Operation FabMount."""
        return self._Mount

    # Fab_Operation.Name():
    @property
    def Name(self) -> str:
        """Return the operation name."""
        return self.get_name()

    # Fab_Operation.Name():
    @property
    def JsonEnabled(self) -> bool:
        """Return the operation name."""
        return self._JsonEnabled

    # Fab_Operation.get_geometries_hash():
    def get_geometries_hash(
            self, geometries: Union[FabGeometry, Tuple[FabGeometry, ...]]) -> Tuple[Any, ...]:
        """Return hash of FabGeometry's."""
        hashes: List[Union[int, str, Tuple[Any, ...]]] = []
        if isinstance(geometries, FabGeometry):
            geometries = (geometries,)
        geometry: FabGeometry
        for geometry in geometries:
            hashes.append(geometry.get_hash())
        return tuple(hashes)

    # Fab_Operation.produce():
    def produce(self, tracing: str = "") -> Tuple[str, ...]:
        """Return the operation sort key."""
        raise NotImplementedError(f"{type(self)}.produce() is not implemented")
        return ()

    # Fab_Operation.post_produce1():
    def post_produce1(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        raise NotImplementedError(f"{type(self)}.post_produce1() is not implemented")

    # Fab_Operation.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return a base JSON dictionary for an Fab_Operation."""
        json_dict: Dict[str, Any] = {
            "Kind": self.get_kind(),
            "Label": self.get_name(),
            "_Active": self._Active,
        }
        if self._ToolControllerIndex >= 0:
            json_dict["ToolControllerIndex"] = self._ToolControllerIndex
        if self._ToolController:
            tool_controller_json: Dict[str, Any] = self._ToolController.to_json()
            json_dict["ToolController"] = tool_controller_json
        return json_dict

    # TODO: Remove
    # Fab_Operation.produce_shape_binder():
    def produce_shape_binder(self, part_geometries: Tuple[Any, ...],
                             prefix: str, tracing: str = "") -> Any:
        """Produce the shape binder needed for the extrude, pocket, hole, ... operations."""
        if tracing:
            print(f"{tracing}<=>Fab_Operation.produce_shape_binder()")
        assert False
        return None

    # TODO: remove
    # Fab_Operation._viewer_update():
    def _viewer_update(self, body: Any, part_feature: Any) -> None:
        """Update the view Body view provider."""
        assert False


# Fab_Extrude:
@dataclass(order=True)
class Fab_Extrude(Fab_Operation):
    """Fab_Extrude: Represents and extrude operation.

    Attributes:
    * *Name* (str): The operation name.
    * *Geometry* (Union[FabGeometry, Tuple[FabGeometry, ...]):
      The FabGeometry (i.e. FabPolygon or FabCircle) or a tuple of FabGeometry's to extrude with.
      When the tuple is used, the largest FabGeometry (which is traditionally the first one)
      is the outside of the extrusion, and the rest are "pockets".  This is useful for tubes.
    * *Depth* (float): The depth to extrude to in millimeters.
    * *Contour* (bool): If True and profile CNC contour path is performed; otherwise, no profile
      is performed.

    """

    _Name: str
    _Geometry: Union[FabGeometry, Tuple[FabGeometry, ...]] = field(compare=False)
    _Depth: float
    _Contour: bool
    # TODO: Make _Geometries be comparable.
    _Geometries: Tuple[FabGeometry, ...] = field(init=False, repr=False, compare=False)
    _StepFile: str = field(init=False)
    _StartDepth: float = field(init=False)
    _StepDown: float = field(init=False)
    _FinalDepth: float = field(init=False)

    # Fab_Extrude.__post_init__():
    def __post_init__(self) -> None:
        """Verify Fab_Extrude values."""
        super().__post_init__()

        # Type check self._Geometry and convert into self._Geometries:
        geometries: List[FabGeometry] = []
        self_geometry: Union[FabGeometry, Tuple[FabGeometry, ...]] = self._Geometry
        if isinstance(self_geometry, FabGeometry):
            geometries = [self_geometry]
        elif isinstance(self_geometry, tuple):
            geometry: FabGeometry
            for geometry in self_geometry:
                if not isinstance(geometry, FabGeometry):
                    raise RuntimeError(f"Fab_Extrude.__post_init__({self.Name}):"
                                       f"{type(geometry)} is not a FabGeometry")
                geometries.append(geometry)
        else:
            raise RuntimeError(f"Fab_Extrude.__post_init__({self.Name}):{type(self.Geometry)} "
                               f"is neither a FabGeometry nor a Tuple[FabGeometry, ...]")
        self._Geometries = tuple(geometries)

        if self.Depth <= 0.0:
            raise RuntimeError(f"Fab_Extrude.__post_init__({self.Name}):"
                               f"Depth ({self.Depth}) is not positive.")
        self._StepFile = "Fab_Extrude.__post_init_()"
        self._StartDepth = 0.0
        self._StepDown = 3.0
        self._FinalDepth = -self.Depth
        self._Active = self._Contour

    # Fab_Extrude.Geometry():
    @property
    def Geometry(self) -> Union[FabGeometry, Tuple[FabGeometry, ...]]:
        """Return the Fab_Extrude FabGeometry."""
        return self._Geometry

    # Fab_Extrude.Depth():
    @property
    def Depth(self) -> float:
        """Return the Depth."""
        return self._Depth

    # Fab_Extrude.get_name():
    def get_name(self) -> str:
        """Return Fab_Extrude name."""
        return self._Name

    # Fab_Extrude.get_kind():
    def get_kind(self) -> str:
        """Return Fab_Extrude kind."""
        return "Extrude"

    # Fab_Extrude.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return hash for Fab_Extrude operation."""
        return (
            "Fab_Extrude",
            self._Name,
            f"{self._Depth:.6f}",
            self.get_geometries_hash(self._Geometries),
        )

    # Fab_Extrude.post_produce1():
    def post_produce1(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        """Produce the Extrude."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_Extrude.produce1('{self.Name}')")

        # Extract the *part_geometries* and create the associated *shape_binder*:
        mount: FabMount = self.Mount
        geometry_prefix: str = f"{mount.Name}_{self.Name}"
        geometry_context: Fab_GeometryContext = mount._GeometryContext
        for index, geometry in enumerate(self._Geometries):
            if tracing:
                print(f"{tracing}Geometry[{index}]:{geometry=}")
            geometry.produce(geometry_context, geometry_prefix, index, tracing=next_tracing)
        # geometry_context.WorkPlane.close(tracing=next_tracing)
        geometry_context.Query.extrude(self.Depth, tracing=next_tracing)

        # Do Contour computations:
        plane: Fab_Plane = geometry_context.Plane
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

        tool_controller: FabToolController = FabToolController(
            BitName="5mm_Endmill",
            Cooling="Flood",
            HorizontalFeed=2.34,
            HorizontalRapid=23.45,
            SpindleDirection=True,
            SpindleSpeed=5432.0,
            ToolNumber=1,
            VerticalFeed=1.23,
            VerticalRapid=12.34
        )
        self.set_tool_controller(tool_controller, produce_state.ToolControllersTable)

        if tracing:
            print(f"{tracing}<=Fab_Extrude.post_produce1('{self.Name}')")

    # Fab_Extrude.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return JSON dictionary for Fab_Extrude."""
        coolant_modes: Tuple[str, ...] = ("None", "Flood", "Mist")
        direction_modes: Tuple[str, ...] = ("CCW", "CW")
        side_modes: Tuple[str, ...] = ("Inside", "Outside")
        json_dict: Dict[str, Any] = super().to_json()
        json_dict["StepFile"] = "Fab_Extrude.to_json:_StepFile"
        json_dict["_Active"] = self._Active
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
    * *Name* (str): The operation name.
    * *Geometry* (Union[FabGeometry, Tuple[FabGeometry, ...]]):
       The Polygon or Circle to pocket.  If a tuple is given, the smaller FabGeometry's
       specify "islands" to not pocket.
    * *Depth* (float): The pocket depth in millimeters.
    * *Bottom_Path* (str): The the path to the generated Pocket bottom STEP file.

    """

    _Name: str
    _Geometry: Union[FabGeometry, Tuple[FabGeometry, ...]] = field(compare=False)
    _Depth: float
    # TODO: Make _Geometries be comparable.
    _Geometries: Tuple[FabGeometry, ...] = field(init=False, repr=False, compare=False)
    _BottomPath: Optional[Path] = field(init=False)
    _FinalDepth: float = field(init=False, repr=False)
    _TopDepth: float = field(init=False, repr=False)
    _StartDepth: float = field(init=False, repr=False)
    _StepDepth: float = field(init=False, repr=False)

    # Fab_Pocket__post_init__():
    def __post_init__(self) -> None:
        """Verify Fab_Pocket values."""
        super().__post_init__()

        # Type check self._Geometry and convert into self._Geometries:
        geometries: List[FabGeometry] = []
        self_geometry: Union[FabGeometry, Tuple[FabGeometry, ...]] = self._Geometry
        if isinstance(self_geometry, FabGeometry):
            geometries = [self_geometry]
        elif isinstance(self_geometry, tuple):
            geometry: FabGeometry
            for geometry in self_geometry:
                if not isinstance(geometry, FabGeometry):
                    raise RuntimeError(f"Fab_Extrude.__post_init__({self.Name}):"
                                       f"{type(geometry)} is not a FabGeometry")
                geometries.append(geometry)
        else:
            raise RuntimeError(f"Fab_Extrude.__post_init__({self.Name}):{type(self.Geometry)} "
                               f"is neither a FabGeometry nor a Tuple[FabGeometry, ...]")
        self._Geometries = tuple(geometries)

        if self._Depth <= 0.0:
            raise RuntimeError(f"Fab_Extrude.__post_init__({self.Name}):"
                               f"Depth ({self.Depth}) is not positive.")
        self._BottomPath = None

        # Unpack some values from *mount*:
        mount: FabMount = self.Mount
        geometry_context: Fab_GeometryContext = mount._GeometryContext
        plane: Fab_Plane = geometry_context.Plane
        top_depth: float = plane.Distance
        final_depth: float = top_depth - self._Depth
        delta_depth: float = top_depth - final_depth
        tool_edge_height: float = 30.00  # TODO: Fix
        if delta_depth > tool_edge_height:
            raise RuntimeError("FIXME")

        tool_diameter: float = 5.00  # TODO: Fix
        step_depth: float = tool_diameter / 2.0
        steps: int = int(math.ceil(delta_depth / step_depth))
        step_down = delta_depth / float(steps)
        self._TopDepth = top_depth
        self._StartDepth = max(top_depth - step_depth, final_depth)
        self._StepDown = step_down
        self._FinalDepth = final_depth

    # Fab_Pocket.Geometry():
    def Geometry(self) -> Union[FabGeometry, Tuple[FabGeometry, ...]]:
        """Return the original Geometry."""
        return self._Geometry

    # Fab_Pocket.Depth():
    def Depth(self) -> float:
        """Return the original Depth."""
        return self._Depth

    # Fab_Pocket.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return Fab_Pocket hash."""
        hashes: List[Any] = [
            "Fab_Pocket",
            self._Name,
            f"{self._Depth:.6f}",
        ]
        geometry: FabGeometry
        for geometry in self._Geometries:
            hashes.append(geometry.get_hash())
        return tuple(hashes)

    # Fab_Pocket.get_name():
    def get_name(self) -> str:
        """Return Fab_Pocket name."""
        return self._Name

    # Fab_Pocket.get_kind():
    def get_kind(self) -> str:
        """Return Fab_Pocket kind."""
        return "Pocket"

    # Fab_Pocket.post_produce1():
    def post_produce1(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        """Produce the Pocket."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_Pocket.post_produce1('{self.Name}')")

        mount: FabMount = self.Mount
        geometry_context: Fab_GeometryContext = mount._GeometryContext
        geometries: Tuple[FabGeometry, ...] = self._Geometries
        pocket_context: Fab_GeometryContext = geometry_context.copy(tracing=next_tracing)
        pocket_query: Fab_Query = pocket_context.Query
        if tracing:
            pocket_query.show("Pocket Context Before", tracing)
        bottom_context: Fab_GeometryContext = geometry_context.copy_with_plane_adjust(
            -self._Depth, tracing=next_tracing)

        # Transfer *geometries* to *pocket_context* (which is a copy of *geometry_context*):
        prefix: str = f"{mount.Solid.Label}__{mount.Name}__{self.Name}"
        bottom_prefix: str = f"{prefix}_bottom"
        geometry: FabGeometry
        index: int
        for index, geometry in enumerate(geometries):
            geometry.produce(pocket_context, prefix, index, tracing=next_tracing)
            geometry.produce(bottom_context, bottom_prefix, index, tracing=next_tracing)
            if tracing:
                pocket_query.show(f"Pocket Context after Geometry {index}", tracing)

        # Extrude the pocket *pocket_query* volume to be removed.
        pocket_query.extrude(self._Depth, tracing=next_tracing)

        bottom_name: str = (
            f"{mount.Solid.Label}__{mount.Name}__{produce_state.OperationIndex:03d}__"
            f"{self.Name}__pocket_bottom"
        )
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

        tool_controller: FabToolController = FabToolController(
            BitName="5mm_Endmill",
            Cooling="Flood",
            HorizontalFeed=2.34,
            HorizontalRapid=23.45,
            SpindleDirection=True,
            SpindleSpeed=5432.0,
            ToolNumber=1,
            VerticalFeed=1.23,
            VerticalRapid=12.34
        )
        self.set_tool_controller(tool_controller, produce_state.ToolControllersTable)

        if tracing:
            pocket_query.show("Pocket Context after Extrude:", tracing)

        # TODO: Use the CadQuery *cut* operation instead of *subtract*:
        query: Any = geometry_context.Query
        assert isinstance(query, Fab_Query), query
        if tracing:
            query.show("Pocket Main Before Subtract", tracing)
        query.subtract(pocket_query, tracing=next_tracing)
        if tracing:
            query.show("Pocket After Subtract", tracing)
            print(f"{tracing}<=Fab_Pocket.post_produce1('{self.Name}')")

    # Fab_Pocket.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return JSON dictionary for Fab_Extrude."""
        bottom_path: Optional[Path] = self._BottomPath
        cut_modes: Tuple[str, ...] = ("Climb", "Conventional")
        coolant_modes: Tuple[str, ...] = ("None", "Flood", "Mist")
        offset_patterns: Tuple[str, ...] = (
            "Grid", "Line", "Offset", "Spiral", "Triangle", "ZigZag", "ZigZagOffset")
        start_ats: Tuple[str, ...] = ("Center", "Edge")
        if bottom_path is None:
            raise RuntimeError("Fab_Pocket.to_json(): no bottom path is set yet.")

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

    """
    ThreadName: str
    Kind: str
    Depth: float
    IsTop: bool

    # Fab_HoleKey.__post__init__():
    def __post_init__(self) -> None:
        """Perform checks on Fab_HoleKey."""
        thread_name: str = self.ThreadName
        assert thread_name.startswith("M") or thread_name.startswith("#") or (
            thread_name.find("/") > 0), thread_name
        assert self.Kind in ("thread", "close", "standard"), self.Kind
        assert self.Depth > 0.0, self.Depth
        assert isinstance(self.IsTop, bool), self.IsTop

    # Fab_HoleKey.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return a hash tuple for a Fab_HoleKey."""
        return (
            self.ThreadName,
            self.Kind,
            f"{self.Depth:.6f}",
            self.IsTop,
        )


# Fab_Hole:
@dataclass
class Fab_Hole(Fab_Operation):
    """Fab_Hole: FabDrill helper class that represents a hole."""

    _Key: Fab_HoleKey
    Centers: Tuple[Vector, ...]  # The Center (start point) of the drils
    Join: FabJoin = field(repr=False)  # The associated FabJoin
    _Name: str  # Hole name
    Depth: float  # Hole depth
    HolesCount: int = field(init=False)  # Number of holes in this opertation
    StartDepth: float = field(init=False)
    StepFile: str = field(init=False)

    # Fab_Hole.__post_init__():
    def __post_init__(self) -> None:
        """Perform final initialization of Fab_Hole"""

        super().__post_init__()
        assert isinstance(self._Key, Fab_HoleKey), self._Key
        assert isinstance(self.Centers, tuple), self.Centers
        assert isinstance(self.Join, FabJoin), self.Join
        assert isinstance(self._Name, str), self._Name
        self.Depth = 0.0
        self.HolesCount = 0
        self.StartDepth = 0.0
        self.StepFile = ""

    # Fab_Hole.Key():
    @property
    def Key(self) -> Fab_HoleKey:
        """Return a Hole key."""
        return self._Key

    # Fab_Hole.get_name()
    def get_name(self) -> str:
        """Return Fab_Hole name."""
        return self._Name

    # Fab_Hole.get_kind():
    def get_kind(self) -> str:
        """Return Fab_Hole kind."""
        return "Drilling"

    # Fab_Hole.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return Fab_Hole hash."""
        hashes: List[Any] = [
            "Fab_Hole",
            self._Key.get_hash(),
            self.Join.get_hash(),
        ]
        center: Vector
        for center in self.Centers:
            hashes.append(f"{center.x:.6f}")
            hashes.append(f"{center.y:.6f}")
            hashes.append(f"{center.z:.6f}")
        return tuple(hashes)

    # Fab_Hole.post_produce1():
    def post_produce1(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        """Perform Fab_Hole phase 1 post production."""

        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_Hole({self.Name}).post_produce1()")

        # Unpack the *mount* and associated *geometry_context*:
        mount: FabMount = self.Mount
        geometry_context: Fab_GeometryContext = mount._GeometryContext
        mount_normal: Vector = mount.Normal
        plane: Fab_Plane = geometry_context.Plane
        query: Fab_Query = geometry_context.Query

        key: Fab_HoleKey = self._Key
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
            circle: FabCircle = FabCircle(center, mount_normal, diameter)
            projected_circle: FabCircle = circle.project_to_plane(plane, tracing=next_tracing)
            projected_center: Vector = projected_circle.Center
            rotated_center: Vector = plane.rotate_to_z_axis(projected_center, tracing=next_tracing)
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
            self._JsonEnabled = False
        else:
            # Start with a new *holes_plane* and *holes_query*:
            self.StartDepth = plane.Distance
            holes_contact: Vector = Vector(0.0, 0.0, self.StartDepth)
            holes_plane: Fab_Plane = Fab_Plane(holes_contact, z_axis)
            holes_query: Fab_Query = Fab_Query(holes_plane)
            self.StartDepth = plane.Distance

            # Compute the closing solid corners.  The enclose face area must be greater the
            # drill face area so that the JSON reader code and distinguish between faces.
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
            holes_query.extrude(depth + 1.0)

            # Drill the holes:
            for center in self.Centers:
                holes_query.move_to(center)  # TODO: Assume +Z axis for now.
                holes_query.hole(diameter, depth)
            self.HolesCount = len(self.Centers)

            operation_index: int = produce_state.OperationIndex
            step_base_name: str = (
                f"{mount.Solid.Label}__{mount.Name}__{operation_index:03d}__{self.Name}Fab_Holes")
            assembly: cq.Assembly = cq.Assembly(
                holes_query.WorkPlane, name=step_base_name, color=cq.Color(0.5, 0.5, 0.5, 1.0))

            holes_path: Path = produce_state.Steps.activate(step_base_name, self.get_hash())
            self.StepFile: str = str(holes_path)

            if not holes_path.exists():
                with _suppress_stdout():
                    assembly.save(self.StepFile, "STEP")

            tool_controller: FabToolController = FabToolController(
                BitName="5mm_Drill",
                Cooling="Flood",
                HorizontalFeed=2.34,
                HorizontalRapid=23.45,
                SpindleDirection=True,
                SpindleSpeed=5432.0,
                ToolNumber=2,
                VerticalFeed=1.23,
                VerticalRapid=12.34
            )
            self.set_tool_controller(tool_controller, produce_state.ToolControllersTable)

        if tracing:
            print(f"{tracing}<=Fab_Hole({self.Name}).post_produce1()")

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
    * *Name*: (str): The name of the Fab_Plane.
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
    _OrderedOperations: "OrderedDict[str, Fab_Operation]" = field(init=False, repr=False)
    _Copy: Vector = field(init=False, repr=False)  # Used for making private copies of Vector's
    _Tracing: str = field(init=False, repr=False)
    _GeometryContext: Fab_GeometryContext = field(init=False, repr=False)
    _AppDatumPlane: Any = field(init=False, repr=False)  # TODO: Remove
    _GuiDatumPlane: Any = field(init=False, repr=False)  # TODO: Remove
    _Plane: Fab_Plane = field(init=False, repr=False)

    # FabMount.__post_init__():
    def __post_init__(self) -> None:
        """Verify that FabMount arguments are valid."""

        solid: "FabSolid" = self._Solid

        tracing: str = solid.Tracing
        next_tracing: str = tracing + " " if tracing else ""
        _ = next_tracing  # Until it is used elsewhere
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).__post_init__()")

        # Do type checking here.
        assert isinstance(self._Name, str)
        assert isinstance(self._Solid, FabSolid)
        assert isinstance(self._Contact, Vector), (self._Contact, type(self._Contact))
        assert isinstance(self._Normal, Vector), self._Normal
        assert isinstance(self._Orient, Vector), self._Orient
        assert isinstance(self._Depth, float)

        copy: Vector = Vector()  # Make private copy of Vector's.
        self._Copy = copy
        self._Contact = self._Contact + copy
        self._Normal = self._Normal + copy
        self._OrderedOperations = OrderedDict()
        # Vector metheds like to modify Vector contents; force copies beforehand:
        self._Plane: Fab_Plane = Fab_Plane(self._Contact, self._Normal)  # , tracing=next_tracing)
        self._Orient = self._Plane.point_project(self._Orient)
        self._GeometryContext = Fab_GeometryContext(self._Plane, self._Query)
        self._AppDatumPlane = None
        self._GuiDatumPlane = None

        if tracing:
            print(f"{tracing}{self._Contact=} {self._Normal=}")
            print(f"{tracing}{self._Depth=} {self._GeometryContext=}")
            print(f"{tracing}<=FabMount({self.Name}).__post_init__()")

    # FabMount.Name():
    @property
    def Name(self) -> str:
        """Return the FabMoun name."""
        return self._Name

    # FabMount.Solid:
    @property
    def Solid(self) -> "FabSolid":
        """Return the FabSolid."""
        return self._Solid

    # FabMount.Body:
    @property
    def Body(self) -> Any:
        """Return PartBodyBase fr FabMount."""
        return self._Solid.Body

    # FabMount.Contact:
    @property
    def Contact(self) -> Vector:
        """Return the FabMount contact point."""
        return self._Contact + self._Copy

    # FabMount.Normal:
    @property
    def Normal(self) -> Vector:
        """Return the FabMount normal."""
        return self._Normal + self._Copy

    # FabMount.Orient:
    @property
    def Orient(self) -> Vector:
        """Return the FabMount Orientation."""
        return self._Orient + self._Copy

    # FabMount.Plane:
    @property
    def Plane(self) -> Fab_Plane:
        """Return the Fab_Plane."""
        return self._Plane

    # FabMount.Depth:
    @property
    def Depth(self) -> float:
        """Return the depth."""
        return self._Depth

    # FabMount.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
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
        for operation in self._OrderedOperations.values():
            hashes.append(operation.get_hash())
        return tuple(hashes)

    # FabMount.record_operation():
    def record_operation(self, operation: Fab_Operation) -> None:
        """Record an operation to a FabMount."""
        if not isinstance(operation, Fab_Operation):
            raise RuntimeError(
                "FabMount.add_operation({self._Name}).{type(operation)} is not an Fab_Operation")
        self._OrderedOperations[operation.Name] = operation

    # FabMount.set_geometry_group():
    def set_geometry_group(self, geometry_group: Any) -> None:
        """Set the FabMount GeometryGroup need for the FabGeometryContex."""
        self._GeometryContext.set_geometry_group(geometry_group)

    # FabMount.post_produce1():
    def post_produce1(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        """Perform FabMount phase 1 post procduction."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabMount.post_produce1('{self.Name}')")

        # If there are no *operations* there is nothing to do:
        operations: "OrderedDict[str, Fab_Operation]" = self._OrderedOperations
        if operations:
            # Create the Fab_Plane used for the drawing support.
            plane: Fab_Plane = self.Plane
            assert isinstance(plane, Fab_Plane), plane
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
            operation_name: str
            operation: Fab_Operation
            for operation_name, operation in operations.items():
                if tracing:
                    print(f"{tracing}Operation[{operation_name}]:")
                produce_state.OperationIndex = operation_index
                operation.post_produce1(produce_state, tracing=next_tracing)
                operation_index += 1

        # Install the FabMount (i.e. *self*) and *datum_plane* into *model_file* prior
        # to recursively performing the *operations*:
        if tracing:
            print(f"{tracing}<=FabMount.produce('{self.Name}')")

    # FabMount.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return FabMount JSON structure."""
        json_operations: List[Any] = []
        operations: OrderedDict[str, Fab_Operation] = self._OrderedOperations
        name: str
        operation: Fab_Operation
        for name, operation in operations.items():
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
                depth: float, contour: bool = True, tracing: str = "") -> None:
        """Perform a extrude operation."""
        tracing = self._Solid.Tracing
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).extrude('{name}', *, {depth}, {contour})")

        # Figure out the contact
        top_contact: Vector = self._Contact
        normal: Vector = self._Normal / self._Normal.Length
        bottom_contact: Vector = top_contact - depth * normal
        top_plane: Fab_Plane = Fab_Plane(top_contact, normal)
        bottom_plane: Fab_Plane = Fab_Plane(bottom_contact, normal)
        if tracing:
            print(f"{tracing}{top_contact=} {normal=} {bottom_contact=}")

        # Compute a bounding box that encloses all of the associated *geometries*:
        boxes: List[FabBox] = []
        geometries: Tuple[FabGeometry, ...]
        if isinstance(shapes, FabGeometry):
            geometries = (shapes,)
        else:
            geometries = shapes
        geometry: FabGeometry
        for geometry in geometries:
            # if tracing:
            #     print(f"{tracing}{geometry=}")
            boxes.append(geometry.project_to_plane(top_plane).Box)
            boxes.append(geometry.project_to_plane(bottom_plane).Box)
        self._Solid.enclose(boxes)

        # Create and record the *extrude*:
        extrude: Fab_Extrude = Fab_Extrude(self, name, shapes, depth, contour)
        self.record_operation(extrude)

        if tracing:
            print(f"{tracing}<=FabMount({self.Name}).extrude('{name}', *, {depth}, {contour})")

    # FabMount.pocket():
    def pocket(self, name: str, shapes: Union[FabGeometry, Tuple[FabGeometry, ...]],
               depth: float, tracing: str = "") -> None:
        """Perform a pocket operation."""
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).pocket('{name}', *)")

        # Create the *pocket* and record it into the FabMount:
        pocket: Fab_Pocket = Fab_Pocket(self, name, shapes, depth)
        self.record_operation(pocket)

        if tracing:
            print(f"{tracing}<=FabMount({self.Name}).pocket('{name}', *)")

    # FabMount.drill_joins():
    def drill_joins(self, joins_name: str,
                    joins: Union[FabJoin, Sequence[FabJoin]], tracing: str = "") -> None:
        """Drill some FabJoin's into a FabMount."""
        # Quickly convert a single FabJoin into a tuple:

        EPSILON: float = 1.0e-8

        # close():
        def close(vector1: Vector, vector2: Vector) -> bool:
            """Return whether 2 normals are very close to one another."""
            return (vector1 - vector2).Length < EPSILON

        if isinstance(joins, FabJoin):
            joins = (joins,)
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).drill_joins(|{len(joins)}|")

        mount_contact: Vector = self._Contact
        mount_normal: Vector = self._Normal / self._Normal.Length
        mount_plane: Fab_Plane = Fab_Plane(mount_contact, mount_normal)
        mount_depth: float = self._Depth
        solid: "FabSolid" = self._Solid

        # intersect_joins: List[FabJoin] = []
        holes: List[Fab_Hole] = []
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
                    mount_start: Vector = mount_plane.point_project(join_start)
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
                    hole_name: str = f"{joins_name}_{join_index}"
                    hole_key: Fab_HoleKey = Fab_HoleKey(
                        fasten.ThreadName, kind, trimmed_depth, is_top)
                    hole: Fab_Hole = Fab_Hole(
                        self, hole_key, (mount_start,), join, hole_name, trimmed_start)
                    if tracing:
                        print(f"{tracing}Append {hole=}")
                    holes.append(hole)

        # Group *holes* into *hole_groups* base on their *key*:
        key: Fab_HoleKey
        hole_groups: Dict[Fab_HoleKey, List[Fab_Hole]] = {}
        for hole in holes:
            key = hole.Key
            if key not in hole_groups:
                hole_groups[key] = []
            hole_groups[key].append(hole)

        # Create *grouped_holes* where each *group_hole* has the same *key*.
        grouped_holes: List[Fab_Hole] = []
        group_holes: List[Fab_Hole]
        for group_holes in hole_groups.values():
            group_hole: Fab_Hole
            group_centers: List[Vector] = []
            for group_hole in group_holes:
                group_centers.extend(group_hole.Centers)
            grouped_hole: Fab_Hole = Fab_Hole(
                group_hole.Mount, group_hole._Key, tuple(group_centers),
                group_hole.Join, f"{group_hole.Name}_", trimmed_start
            )
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

    """

    Material: str
    Color: str
    _Mounts: "OrderedDict[str, FabMount]" = field(init=False, repr=False)
    _GeometryGroup: Optional[Any] = field(init=False, repr=False)
    _Body: Optional[Any] = field(init=False, repr=False)
    _Query: Fab_Query = field(init=False, repr=False)
    _Assembly: Any = field(init=False, repr=False)
    _StepFile: Optional[Path] = field(init=False, repr=False)
    _Color: Optional[Tuple[float, ...]] = field(init=False, repr=False)

    # FabSolid.__post_init__():
    def __post_init__(self) -> None:
        """Verify FabSolid arguments."""
        super().__post_init__()
        tracing: str = self.Tracing
        next_tracing: str = tracing + " " if tracing else ""
        _ = next_tracing  # Until it is used elsewhere.
        if tracing:
            print(f"{tracing}=>FabSolid({self.Label}).__post_init__()")
        # TODO: Do additional type checking here:
        # Initial WorkPlane does not matter, it gets set by FabMount.
        origin: Vector = Vector(0.0, 0.0, 0.0)
        z_axis: Vector = Vector(0.0, 0.0, 1.0)
        initial_plane: Fab_Plane = Fab_Plane(origin, z_axis)  # , tracing=next_tracing)
        self._Mounts = OrderedDict()
        self._GeometryGroup = None
        self._Body = None
        self._Query = Fab_Query(initial_plane)
        self._Assembly = None
        self._StepFile = None
        self._Color = None

        if tracing:
            print(f"{tracing}<=FabSolid({self.Label}).__post_init__()")

    # FabSolid.Body():
    @property
    def Body(self) -> Any:
        """Return BodyBase for FabSolid."""
        if not self._Body:
            raise RuntimeError(f"FabSolid.Body({self.Label}).Body(): body not set yet")
        return self._Body

    # FabSolid.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return FabProject JSON structure."""
        json_dict: Dict[str, Any] = super().to_json()
        json_dict["Kind"] = "Solid"
        if self._StepFile:
            json_dict["StepFile"] = str(self._StepFile)
        if self._Color:
            json_dict["_Color"] = self._Color
        json_mounts: List[Any] = []
        name: str
        mount: FabMount
        for mount in self._Mounts.values():
            # Skip mount if it has no operations.
            if len(mount._OrderedOperations) > 0:
                json_mounts.append(mount.to_json())
        json_dict["children"] = json_mounts
        return json_dict

    # FabSolid.set_body():
    def set_body(self, body: Any) -> None:
        """Set the BodyBase of a FabSolid."""
        self._Body = body

    # FabSolid.is_solid():
    def is_solid(self) -> bool:
        """ Return True if FabNode is a FabAssembly."""
        return True  # All other FabNode's return False.

    # FabSolid.pre_produce():
    def pre_produce(self, produce_state: Fab_ProduceState) -> None:
        """Perform FabSolid pre production."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabSolid({self.Label}).pre_produce()")
        self._Mounts = OrderedDict()
        if tracing:
            print(f"{tracing}{len(self._Mounts)=}")
            print(f"{tracing}<=FabSolid({self.Label}).pre_produce()")

    # FabSolid.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return FabSolid hash."""
        hashes: List[Any] = [
            "FabSolid",
            self.Material,
            self.Color,
        ]
        mount: FabMount
        for mount in self._Mounts.values():
            hashes.append(mount.get_hash())
        return tuple(hashes)

    # FabSolid.mount():
    def mount(self, name: str, contact: Vector, normal: Vector, orient: Vector,
              depth: float, tracing: str = "") -> FabMount:
        """Return a new FabMount."""
        if tracing:
            print(f"{tracing}=>FabSolid({self.Label}).mount('{name}', ...)")

        mounts: "OrderedDict[str, FabMount]" = self._Mounts
        if name in mounts:
            raise RuntimeError(f"FabSolid({self._Label}).mount(): Mount {name} is not unique.")
        fab_mount: FabMount = FabMount(name, self, contact, normal, orient, depth, self._Query)
        self._Mounts[name] = fab_mount

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
            mounts = tuple(self._Mounts.values())
        mount: FabMount
        for mount in mounts:
            mount.drill_joins(name, joins, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=FabSolid({self.Label}).drill_joins('{name}', *)")

    # FabSolid.post_produce1():
    def post_produce1(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        """Perform FabSolid Phase1 post production."""
        tracing = self.Tracing  # Ignore *tracing* argument.
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabSolid.post_produce1('{self.Label}')")

        # Deterimine whether it is possible to *use_cached_step*:
        use_cached_step: bool = False
        step_path: Path = cast(Path, None)  # Force runtime error if used.
        # This was a shocker.  It turns out that __hash__() methods are not necessarily
        # consistent between Python runs.  In other words  __hash__() is non-deterministic.
        # Instead use one of the hashlib hash functions instead:
        #     hash_tuple => repr string => hashlib.sha256 => trim to 16 bytes
        hash_tuple: Tuple[Any, ...] = self.get_hash()
        step_path = produce_state.Steps.activate(self.Label, hash_tuple)
        if step_path.exists():
            use_cached_step = True
        self._StepFile = step_path

        # Perform all of the mount operations if unable to *use_cached_step*:
        if not use_cached_step:
            mounts: "OrderedDict[str, FabMount]" = self._Mounts
            if tracing:
                print(f"{tracing}Iterate over |{len(mounts)}| mounts")
            mount_name: str
            mount: FabMount
            for mount_name, mount in mounts.items():
                if tracing:
                    print(f"{tracing}[{mount_name}]: process")
                mount.post_produce1(produce_state, tracing=next_tracing)

        # CadQuery workplanes do not have a color, but Assemblies do.
        rgb_color: Tuple[float, float, float] = FabColor.svg_to_rgb(self.Color)
        # TODO: move this code into Fab_Query:

        assembly: cq.Assembly
        if use_cached_step:
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
            print(f"{tracing}<=FabSolid.post_produce1('{self.Label}')")


# TODO: Remove
def visibility_set(element: Any, new_value: bool = True, tracing: str = "") -> None:
    """Set the visibility of an element."""
    if tracing:
        print(f"{tracing}<=>visibility_set({element}, {new_value})")
    assert False


# TODO: Add unit tests.
def main() -> None:
    FabStock._unit_tests()
    pass


if __name__ == "__main__":
    main()
