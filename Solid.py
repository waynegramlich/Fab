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

from Geometry import FabCircle, FabGeometry, FabGeometryContext, FabPlane, FabQuery
from Join import FabFasten, FabJoin
from Node import FabBox, FabNode, _NodeProduceState
from Utilities import FabColor, FabToolController

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


# _Operation:
@dataclass(order=True)
class _Operation(object):
    """_Operation: An base class for FabMount operations -- _Extrude, _Pocket, FabHole, etc.

    Attributes:
    * *Mount* (FabMount):
      The FabMount to use for performing operations.
    * *ToolController* (Optional[FabToolController]):
      The tool controller (i.e. speeds, feeds, etc.) to use. (Default: None)
    * *ToolControllerIndex* (int):
      The tool controller index associated with the tool controller.  (Default: -1)

    """

    _Mount: "FabMount" = field(repr=False, compare=False)
    _ToolController: Optional[FabToolController] = field(init=False, repr=False)
    _ToolControllerIndex: int = field(init=False)

    # _Operation.__post_init__():
    def __post_init__(self) -> None:
        """Initialize _Operation."""
        # TODO: Enable check:
        # if not self._Mount.is_mount():
        #   raise RuntimeError("_Operation.__post_init__(): {type(self._Mount)} is not FabMount")
        self._ToolController = None
        self._ToolControllerIndex = -1  # Unassigned.

    # _Operation.get_tool_controller():
    def get_tool_controller(self) -> FabToolController:
        """Return the _Operation tool controller"""
        if not self._ToolController:
            raise RuntimeError("_Operation().get_tool_controller(): ToolController not set yet.")
        return self._ToolController

    # _Operation.set_tool_controller():
    def set_tool_controller(self, tool_controller: FabToolController,
                            tool_controllers_table: Dict[FabToolController, int]) -> None:
        """Set the _Operation tool controller and associated index."""
        tool_controller_index: int
        if tool_controller in tool_controllers_table:
            tool_controller_index = tool_controllers_table[tool_controller]
            self._ToolController = None
        else:
            tool_controller_index = len(tool_controllers_table)
            tool_controllers_table[tool_controller] = tool_controller_index
            self._ToolController = tool_controller
        self._ToolControllerIndex = tool_controller_index

    # _Operation.get_kind():
    def get_kind(self) -> str:
        """Return _Operation kind."""
        raise RuntimeError(f"_Operation().get_kind() not implemented for {type(self)}")

    # _Operation.get_name():
    def get_name(self) -> str:
        """Return _Operation name."""
        raise RuntimeError(f"_Operation().get_name() not implemented for {type(self)}")

    # _Operation.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return _Operation hash."""
        raise RuntimeError(f"_Operation().get_hash() not implemented for {type(self)}")

    # _Operation.Mount():
    @property
    def Mount(self) -> "FabMount":
        """Return _Operation FabMount."""
        return self._Mount

    # _Operation.Name():
    @property
    def Name(self) -> str:
        """Return the operation name."""
        return self.get_name()

    # _Operation.get_geometries_hash():
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

    # _Operation.produce():
    def produce(self, tracing: str = "") -> Tuple[str, ...]:
        """Return the operation sort key."""
        raise NotImplementedError(f"{type(self)}.produce() is not implemented")
        return ()

    # _Operation.post_produce1():
    def post_produce1(self, produce_state: _NodeProduceState, tracing: str = "") -> None:
        raise NotImplementedError(f"{type(self)}.post_produce1() is not implemented")

    # _Operation.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return a base JSON dictionary for an _Operation."""
        json_dict: Dict[str, Any] = {
            "Kind": self.get_kind(),
            "Label": self.get_name(),
        }
        if self._ToolControllerIndex >= 0:
            json_dict["ToolControllerIndex"] = self._ToolControllerIndex
        if self._ToolController:
            tool_controller_json: Dict[str, Any] = self._ToolController.to_json()
            json_dict["ToolController"] = tool_controller_json
        return json_dict

    # TODO: Remove
    # _Operation.produce_shape_binder():
    def produce_shape_binder(self, part_geometries: Tuple[Any, ...],
                             prefix: str, tracing: str = "") -> Any:
        """Produce the shape binder needed for the extrude, pocket, hole, ... operations."""
        if tracing:
            print(f"{tracing}<=>_Operation.produce_shape_binder()")
        assert False
        return None

    # TODO: remove
    # _Operation._viewer_update():
    def _viewer_update(self, body: Any, part_feature: Any) -> None:
        """Update the view Body view provider."""
        assert False


# _Extrude:
@dataclass(order=True)
class _Extrude(_Operation):
    """_Extrude: Prepresents and extrude operation.

    Attributes:
    * *Name* (str): The operation name.
    * *Geometry* (Union[FabGeometry, Tuple[FabGeometry, ...]):
      The FabGeometry (i.e. FabPolygon or FabCircle) or a tuple of FabGeometry's to extrude with.
      When the tuple is used, the largest FabGeometry (which is traditionally the first one)
      is the outside of the extrusion, and the rest are "pockets".  This is useful for tubes.
    * *Depth* (float): The depth to extrude to in millimeters.
    * *Contour* (bool): The contour flag.

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

    # _Extrude.__post_init__():
    def __post_init__(self) -> None:
        """Verify _Extrude values."""
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
                    raise RuntimeError(f"_Extrude.__post_init__({self.Name}):"
                                       f"{type(geometry)} is not a FabGeometry")
                geometries.append(geometry)
        else:
            raise RuntimeError(f"_Extrude.__post_init__({self.Name}):{type(self.Geometry)} "
                               f"is neither a FabGeometry nor a Tuple[FabGeometry, ...]")
        self._Geometries = tuple(geometries)

        if self.Depth <= 0.0:
            raise RuntimeError(f"_Extrude.__post_init__({self.Name}):"
                               f"Depth ({self.Depth}) is not positive.")
        self._StepFile = "_Extrude.__post_init_()"
        self._StartDepth = 0.0
        self._StepDown = 3.0
        self._FinalDepth = -self.Depth

    # _Extrude.Geometry():
    @property
    def Geometry(self) -> Union[FabGeometry, Tuple[FabGeometry, ...]]:
        """Return the _Extrude FabGeometry."""
        return self._Geometry

    # _Extrude.Depth():
    @property
    def Depth(self) -> float:
        """Return the Depth."""
        return self._Depth

    # _Extrude.get_name():
    def get_name(self) -> str:
        """Return _Extrude name."""
        return self._Name

    # _Extrude.get_kind():
    def get_kind(self) -> str:
        """Return _Extrude kind."""
        return "Extrude"

    # _Extrude.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return hash for _Extrude operation."""
        return (
            "_Extrude",
            self._Name,
            f"{self._Depth:.6f}",
            self.get_geometries_hash(self._Geometries),
        )

    # _Extrude.post_produce1():
    def post_produce1(self, produce_state: _NodeProduceState, tracing: str = "") -> None:
        """Produce the Extrude."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>_Extrude.produce1('{self.Name}')")

        # Extract the *part_geometries* and create the associated *shape_binder*:
        mount: FabMount = self.Mount
        geometry_prefix: str = f"{mount.Name}_{self.Name}"
        geometry_context: FabGeometryContext = mount._GeometryContext
        for index, geometry in enumerate(self._Geometries):
            if tracing:
                print(f"{tracing}Geometry[{index}]:{geometry=}")
            geometry.produce(geometry_context, geometry_prefix, index, tracing=next_tracing)
        # geometry_context.WorkPlane.close(tracing=next_tracing)
        geometry_context.Query.extrude(self.Depth, tracing=next_tracing)

        # Do Contour computations:
        plane: FabPlane = geometry_context.Plane
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
            print(f"{tracing}<=_Extrude.post_produce1('{self.Name}')")

    # _Extrude.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return JSON dictionary for _Extrude."""
        json_dict: Dict[str, Any] = super().to_json()
        json_dict["_Contour"] = self._Contour
        json_dict["_Depth"] = self._Depth
        json_dict["_FinalDepth"] = self._FinalDepth
        json_dict["_StartDepth"] = self._StartDepth
        json_dict["_StepDown"] = self._StepDown
        json_dict["_StepFile"] = "_Extrude.to_json:_StepFile"
        return json_dict


# _Pocket:
@dataclass(order=True)
class _Pocket(_Operation):
    """_Pocket: Represents a pocketing operation.

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

    # _Pocket__post_init__():
    def __post_init__(self) -> None:
        """Verify _Pocket values."""
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
                    raise RuntimeError(f"_Extrude.__post_init__({self.Name}):"
                                       f"{type(geometry)} is not a FabGeometry")
                geometries.append(geometry)
        else:
            raise RuntimeError(f"_Extrude.__post_init__({self.Name}):{type(self.Geometry)} "
                               f"is neither a FabGeometry nor a Tuple[FabGeometry, ...]")
        self._Geometries = tuple(geometries)

        if self._Depth <= 0.0:
            raise RuntimeError(f"_Extrude.__post_init__({self.Name}):"
                               f"Depth ({self.Depth}) is not positive.")
        self._BottomPath = None

        # Unpack some values from *mount*:
        mount: FabMount = self.Mount
        geometry_context: FabGeometryContext = mount._GeometryContext
        plane: FabPlane = geometry_context.Plane
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

    # _Pocket.Geometry():
    def Geometry(self) -> Union[FabGeometry, Tuple[FabGeometry, ...]]:
        """Return the original Geometry."""
        return self._Geometry

    # _Pocket.Depth():
    def Depth(self) -> float:
        """Return the original Depth."""
        return self._Depth

    # _Pocket.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return _Pocket hash."""
        hashes: List[Any] = [
            "_Pocket",
            self._Name,
            f"{self._Depth:.6f}",
        ]
        geometry: FabGeometry
        for geometry in self._Geometries:
            hashes.append(geometry.get_hash())
        return tuple(hashes)

    # _Pocket.get_name():
    def get_name(self) -> str:
        """Return _Pocket name."""
        return self._Name

    # _Pocket.get_kind():
    def get_kind(self) -> str:
        """Return _Extrude kind."""
        return "Pocket"

    # _Pocket.post_produce1():
    def post_produce1(self, produce_state: _NodeProduceState, tracing: str = "") -> None:
        """Produce the Pocket."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>_Pocket.post_produce1('{self.Name}')")

        mount: FabMount = self.Mount
        geometry_context: FabGeometryContext = mount._GeometryContext
        geometries: Tuple[FabGeometry, ...] = self._Geometries
        pocket_context: FabGeometryContext = geometry_context.copy(tracing=next_tracing)
        pocket_query: FabQuery = pocket_context.Query
        if tracing:
            pocket_query.show("Pocket Context Before", tracing)
        bottom_context: FabGeometryContext = geometry_context.copy_with_plane_adjust(
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

        bottom_name: str = f"{prefix}__pocket_bottom"
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

            # Use FabSteps to manage duplicates.
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
        assert isinstance(query, FabQuery), query
        if tracing:
            query.show("Pocket Main Before Subtract", tracing)
        query.subtract(pocket_query, tracing=next_tracing)
        if tracing:
            query.show("Pocket After Subtract", tracing)
            print(f"{tracing}<=_Pocket.post_produce1('{self.Name}')")

    # _Pocket.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return JSON dictionary for _Extrude."""
        bottom_path: Optional[Path] = self._BottomPath
        cut_modes: Tuple[str, ...] = ("Climb", "Conventional")
        coolant_modes: Tuple[str, ...] = ("None", "Flood", "Mist")
        offset_patterns: Tuple[str, ...] = (
            "Grid", "Line", "Offset", "Spiral", "Triangle", "ZigZag", "ZigZagOffset")
        start_ats: Tuple[str, ...] = ("Center", "Edge")
        if bottom_path is None:
            raise RuntimeError("_Pocket.to_json(): no bottom path is set yet.")

        start_depth: float = self._StartDepth
        step_down: float = self._StepDown
        final_depth: float = self._FinalDepth

        json_dict: Dict[str, Any] = super().to_json()
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
        json_dict["_Step"] = str(bottom_path)  # File name!
        json_dict["_StepOver"] = 90  # Percent of cutter diameter to step over on each pass
        json_dict["_ZigZagAngle"] = 45.0  # Angle in degrees

        return json_dict


_HoleKey = Tuple[str, str, float, bool, int]


# _Hole:
@dataclass(order=True)
class _Hole(_Operation):
    """_Hole: FabDrill helper class that represents a hole."""

    # Size: str  # Essentially the diameter
    # Profile: str  # Essentially the fastener thread pitch
    ThreadName: str  # Thread name
    Kind: str  # "thread", "close", or "standard"
    Depth: float  # The depth of the drill hole
    IsTop: bool  # Is the top of the fastener
    Unique: int  # Non-zero to force otherwise common holes into separate operations.
    Center: Vector = field(compare=False)  # The Center (start point) of the drill
    Join: FabJoin = field(compare=False, repr=False)  # The associated FabJoin
    _Name: str  # Hole name

    # _Hole.Key():
    @property
    def Key(self) -> _HoleKey:
        """Return a Hole key."""
        return (self.ThreadName, self.Kind, self.Depth, self.IsTop, self.Unique)

    # _Hole.get_name()
    def get_name(self) -> str:
        """Return _Hole name."""
        return self._Name

    # _Hole.get_kind():
    def get_kind(self) -> str:
        """Return _Extrude kind."""
        return "Hole"

    # _Hole.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return _Hole hash."""
        center: Vector = self.Center
        hashes: Tuple[Any, ...] = (
            "_Hole",
            self._Name,
            self.ThreadName,
            self.Kind,
            self.IsTop,
            self.Unique,
            f"{self.Depth:.6f}",
            f"{center.x:.6f}",
            f"{center.y:.6f}",
            f"{center.z:.6f}",
            self.Join.get_hash(),
        )
        return hashes

    # _Hole.post_produce1():
    def post_produce1(self, produce_state: _NodeProduceState, tracing: str = "") -> None:
        """Perform _Hole phase 1 post production."""

        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>_Hole({self.Name}).post_produce1()")

        # Unpack the _Hole (i.e. *self*):
        mount: FabMount = self.Mount
        # thread_name: str = self.ThreadName
        kind: str = self.Kind
        depth: float = self.Depth
        # is_top: bool = self.IsTop
        # unique: int = self.Unique
        center: Vector = self.Center
        join: FabJoin = self.Join
        # name: str = self.Name

        # Unpack *mount* and *solid*:
        mount_normal: Vector = mount.Normal
        fasten: FabFasten = join.Fasten
        diameter: Vector = fasten.get_diameter(kind)
        circle: FabCircle = FabCircle(center, mount_normal, diameter)

        geometry_context: FabGeometryContext = mount._GeometryContext
        # geometry_prefix: str = name

        # solid: FabSolid = mount.Solid

        # Sweep through *hole_groups* generating *part_geometries*:
        # group_index: int
        # for group_index, key in enumerate(sorted(hole_groups.keys())):
        #     # Unpack *key*:
        #     thread_name: str
        #     thread_name, kind, depth, is_top, unique = key
        #     diameter: float = fasten.get_diameter(kind)

        #     # Construct the *part_geometries* for each *hole*:
        #     part_geometries: List[Any] = []
        #     hole_group: List[_Hole] = hole_groups[key]
        #     for hole_index, hole in enumerate(hole_group):
        #         center: Vector = hole.Center
        #         circle: FabCircle = FabCircle(center, mount_normal, diameter)
        #         geometry_prefix: str = (
        #             f"{self.Name}_{name}{group_index:03d}")
        #         part_geometries.extend(
        #             circle.produce(geometry_context,
        #                            geometry_prefix, tracing=next_tracing))

        if tracing:
            print(f"{tracing}hole={self}:")
        plane: FabPlane = geometry_context.Plane
        projected_circle: FabCircle = circle.project_to_plane(plane, tracing=next_tracing)
        projected_center: Vector = projected_circle.Center
        rotated_center: Vector = plane.rotate_to_z_axis(projected_center, tracing=next_tracing)

        geometry_context.Query.move_to(rotated_center, tracing=next_tracing)
        geometry_context.Query.hole(diameter, depth, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=_Hole({self.Name}).post_produce1()")

    # _Hole.to_json():
    def to_json(self) -> Dict[str, Any]:
        """"""
        return {}  # TODO: This should not be called.


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
    * *WorkPlane* (FabQuery): The CadQuery workplane wrapper class object.

    """

    _Name: str
    _Solid: "FabSolid"
    _Contact: Vector
    _Normal: Vector
    _Orient: Vector
    _Depth: float
    _Query: FabQuery
    _Operations: "OrderedDict[str, _Operation]" = field(init=False, repr=False)
    _Copy: Vector = field(init=False, repr=False)  # Used for making private copies of Vector's
    _Tracing: str = field(init=False, repr=False)
    _GeometryContext: FabGeometryContext = field(init=False, repr=False)
    _AppDatumPlane: Any = field(init=False, repr=False)  # TODO: Remove
    _GuiDatumPlane: Any = field(init=False, repr=False)  # TODO: Remove
    _Plane: FabPlane = field(init=False, repr=False)

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
        self._Operations = OrderedDict()
        # Vector metheds like to modify Vector contents; force copies beforehand:
        self._Plane: FabPlane = FabPlane(self._Contact, self._Normal)  # , tracing=next_tracing)
        self._Orient = self._Plane.point_project(self._Orient)
        self._GeometryContext = FabGeometryContext(self._Plane, self._Query)
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
    def Plane(self) -> FabPlane:
        """Return the FabPlane."""
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
        operation: _Operation
        for operation in self._Operations.values():
            hashes.append(operation.get_hash())
        return tuple(hashes)

    # FabMount.record_operation():
    def record_operation(self, operation: _Operation) -> None:
        """Record an operation to a FabMount."""
        if not isinstance(operation, _Operation):
            raise RuntimeError(
                "FabMount.add_operation({self._Name}).{type(operation)} is not an _Operation")
        self._Operations[operation.Name] = operation

    # FabMount.set_geometry_group():
    def set_geometry_group(self, geometry_group: Any) -> None:
        """Set the FabMount GeometryGroup need for the FabGeometryContex."""
        self._GeometryContext.set_geometry_group(geometry_group)

    # FabMount.post_produce1():
    def post_produce1(self, produce_state: _NodeProduceState, tracing: str = "") -> None:
        """Perform FabMount phase 1 post procduction."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabMount.post_produce1('{self.Name}')")

        # If there are no *operations* there is nothing to do:
        operations: "OrderedDict[str, _Operation]" = self._Operations
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

            work_plane: Optional[FabQuery] = self._Solid._Query
            assert isinstance(work_plane, FabQuery), work_plane
            work_plane.copy_workplane(plane, tracing=next_tracing)

            # Process each *operation* in *operations*:
            operation_name: str
            operation: _Operation
            for operation_name, operation in operations.items():
                if tracing:
                    print(f"{tracing}Operation[{operation_name}]:")
                operation.post_produce1(produce_state, tracing=next_tracing)

        # Install the FabMount (i.e. *self*) and *datum_plane* into *model_file* prior
        # to recursively performing the *operations*:
        if tracing:
            print(f"{tracing}<=FabMount.produce('{self.Name}')")

    # FabMount.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return FabMount JSON structure."""
        json_operations: List[Any] = []
        operations: OrderedDict[str, _Operation] = self._Operations
        name: str
        operation: _Operation
        for name, operation in operations.items():
            if isinstance(operation, (_Extrude, _Pocket)):
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
            print(f"{tracing}=>FabMount({self.Name}).extrude('{name}', *, {depth})")

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
        extrude: _Extrude = _Extrude(self, name, shapes, depth, contour)
        self.record_operation(extrude)

        if tracing:
            print(f"{tracing}<=FabMount({self.Name}).extrude('{name}', *, {depth})")

    # FabMount.pocket():
    def pocket(self, name: str, shapes: Union[FabGeometry, Tuple[FabGeometry, ...]],
               depth: float, tracing: str = "") -> None:
        """Perform a pocket operation."""
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).pocket('{name}', *)")

        # Create the *pocket* and record it into the FabMount:
        pocket: _Pocket = _Pocket(self, name, shapes, depth)
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
        mount_plane: FabPlane = FabPlane(mount_contact, mount_normal)
        mount_depth: float = self._Depth
        solid: "FabSolid" = self._Solid

        # intersect_joins: List[FabJoin] = []
        holes: List[_Hole] = []
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
                    # This is extremley ugly for now.  If the *mount_normal* equals the
                    # +Z axis, multiple holes with the same characterisics can be drilled
                    # with one hole operation.  Otherwise, one drill operation per hole
                    # is requrired.  This is done by setting *unique* to *join_index*.
                    if tracing:
                        print(f"{tracing}{mount_depth=} {trimmed_depth=}")
                    assert trimmed_depth > 0.0, trimmed_depth
                    # unique: int = -1 if mount_z_aligned else join_index
                    unique: int = join_index
                    hole_name: str = f"{joins_name}_{join_index}"
                    hole: _Hole = _Hole(self, fasten.ThreadName, kind, trimmed_depth, is_top,
                                        unique, mount_start, join, hole_name)
                    if tracing:
                        print(f"{tracing}Append {hole=}")
                    holes.append(hole)

        # Group *holes* into *hole_groups* that can be done with one PartDesign hole:
        # key: _HoleKey
        # hole_groups: Dict[_HoleKey, List[_Hole]] = {}
        # for hole in holes:
        #     key = hole.Key
        #     if key not in hole_groups:
        #         hole_groups[key] = []
        #     hole_groups[key].append(hole)

        hole_index: int
        for hole_index, hole in enumerate(holes):
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
    _Query: FabQuery = field(init=False, repr=False)
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
        initial_plane: FabPlane = FabPlane(origin, z_axis)  # , tracing=next_tracing)
        self._Mounts = OrderedDict()
        self._GeometryGroup = None
        self._Body = None
        self._Query = FabQuery(initial_plane)
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
            json_dict["_Step"] = str(self._StepFile)
        if self._Color:
            json_dict["_Color"] = self._Color
        json_mounts: List[Any] = []
        name: str
        mount: FabMount
        for mount in self._Mounts.values():
            # Skip mount if it has no operations.
            if len(mount._Operations) > 0:
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
    def pre_produce(self, produce_state: _NodeProduceState) -> None:
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
    def post_produce1(self, produce_state: _NodeProduceState, tracing: str = "") -> None:
        """Perform FabSolid Phase1 post production."""
        tracing = self.Tracing  # Ignore *tracing* argument.
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabSolid.post_produce1('{self.Label}')")

        # Deterimine wether it is posible to *use_cached_step*:
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
        # TODO: move this code into FabQuery:

        assembly: cq.Assembly
        if use_cached_step:
            # Read in step file here:
            work_plane: cq.Workplane = cq.importers.importStep(str(step_path))
            assembly = cq.Assembly(work_plane, name=self.Label, color=cq.Color(*rgb_color))
            self._Color = rgb_color
            if tracing:
                print(f"{tracing}Read file '{str(step_path)}' !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
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
