#!/usr/bin/env python3
"""Solid: A module for constructing 3D solids.

This module defines the following user facing classes:
* FabSolid: A 3D solid part that corresponds to a STEP file.
* FabMount: A CNC-like work plane on which other operations are performed.

There are internal classes that represent operations such as extrude, pocket, drill, etc.
This internal classes are managed by FabMount methods.

"""

import sys

from collections import OrderedDict
from dataclasses import dataclass, field
import hashlib
from pathlib import Path
from typing import Any, cast, Dict, Generator, IO, List, Optional, Sequence, Tuple, Union

import cadquery as cq  # type: ignore
from cadquery import Vector  # type: ignore

# import Part  # type: ignore

from Geometry import FabCircle, FabGeometry, FabGeometryContext, FabPlane, FabWorkPlane
from Join import FabFasten, FabJoin
from Node import FabBox, FabNode, FabSteps
from Utilities import FabColor

# The *_suppress_stdout* function is based on code from:
#   [I/O Redirect](https://stackoverflow.com/questions/4675728/redirect-stdout-to-a-file-in-python)
# This code is used to suppress extraneous output from lower levels of cadquery.Assembly.save().

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


# _Operation:
@dataclass(order=True)
class _Operation(object):
    """_Operation: An base class for FabMount operations -- _Extrude, _Pocket, FabHole, etc.

    Attributes:
    * *Name* (str): Unique operation name for given mount.
    * *Mount* (FabMount): The FabMount to use for performing operations.

    """

    _Mount: "FabMount" = field(repr=False, compare=False)

    # _Operation.__post_init__():
    def __post_init__(self) -> None:
        """Initialize _Operation."""
        # TODO: Enable check:
        # if not self._Mount.is_mount():
        #   raise RuntimeError("_Operation.__post_init__(): {type(self._Mount)} is not FabMount")

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

    # _Operation.produce():
    def produce(self, tracing: str = "") -> Tuple[str, ...]:
        """Return the operation sort key."""
        raise NotImplementedError(f"{type(self)}.produce() is not implemented")
        return ()

    # _Operation.post_produce1():
    def post_produce1(self, tracing: str = "") -> None:
        raise NotImplementedError(f"{type(self)}.post_produce1() is not implemented")

    # TODO: Remove
    # _Operation.produce_shape_binder():
    def produce_shape_binder(self, part_geometries: Tuple[Any, ...],
                             prefix: str, tracing: str = "") -> Any:
        """Produce the shape binder needed for the extrude, pocket, hole, ... operations."""
        if tracing:
            print(f"{tracing}<=>FabOperation.produce_shape_binder()")
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

    """

    _Name: str
    _Geometry: Union[FabGeometry, Tuple[FabGeometry, ...]] = field(compare=False)
    _Depth: float
    # TODO: Make _Geometries be comparable.
    _Geometries: Tuple[FabGeometry, ...] = field(init=False, repr=False, compare=False)

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

    # _Extrude.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return hash for _Extrude operation."""
        hashes: List[Union[int, str, Tuple[Any, ...]]] = [
            "_Extrude",
            self._Name,
            f"{self._Depth:.6f}"
        ]
        geometries: Union[FabGeometry, Tuple[FabGeometry, ...]] = self._Geometry
        if isinstance(geometries, FabGeometry):
            geometries = (geometries,)
        geometry: FabGeometry
        for geometry in geometries:
            hashes.append(geometry.get_hash())
        return tuple(hashes)

    # _Extrude.post_produce1():
    def post_produce1(self, tracing: str = "") -> None:
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
        geometry_context.WorkPlane.extrude(self.Depth, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=_Extrude.post_produce1('{self.Name}')")


# _Pocket:
@dataclass(order=True)
class _Pocket(_Operation):
    """_Pocket: Represents a pocketing opertaion.

    Attributes:
    * *Name* (str): The operation name.
    * *Geometry* (Union[FabGeometry, Tuple[FabGeometry, ...]]):
       The Polygon or Circle to pocket.  If a tuple is given, the smaller FabGeometry's
       specify "islands" to not pocket.
    * *Depth* (float): The pocket depth in millimeters.

    """

    _Name: str
    _Geometry: Union[FabGeometry, Tuple[FabGeometry, ...]] = field(compare=False)
    _Depth: float
    # TODO: Make _Geometries be comparable.
    _Geometries: Tuple[FabGeometry, ...] = field(init=False, repr=False, compare=False)

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

    # _Pocket.post_produce1():
    def post_produce1(self, tracing: str = "") -> None:
        """Produce the Pocket."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>_Pocket.post_produce1('{self.Name}')")

        # Extract the *part_geometries* from *geometries*:
        geometries: Tuple[FabGeometry, ...] = self._Geometries
        mount: FabMount = self.Mount
        prefix: str = f"{mount.Name}_{self.Name}"
        # part_geometries: List[Any] = []
        geometry_context: FabGeometryContext = mount._GeometryContext
        geometry: FabGeometry
        index: int

        pocket_context: FabGeometryContext = geometry_context.copy(tracing=next_tracing)
        pocket_work_plane: FabWorkPlane = pocket_context.WorkPlane
        if tracing:
            pocket_work_plane.show("Pocket Context Before", tracing)
        for index, geometry in enumerate(geometries):
            geometry.produce(pocket_context, prefix, index, tracing=next_tracing)
            if tracing:
                pocket_work_plane.show(f"Pocket Context after Geometry {index}", tracing)
        pocket_work_plane.extrude(self._Depth, tracing=next_tracing)
        if tracing:
            pocket_work_plane.show("Pocket Context after Extrude:", tracing)

        work_plane: Any = geometry_context.WorkPlane
        assert isinstance(work_plane, FabWorkPlane), work_plane
        if tracing:
            work_plane.show("Pocket Main Before Subtract", tracing)
        geometry_context.WorkPlane.subtract(pocket_work_plane, tracing=next_tracing)
        if tracing:
            work_plane.show("Pocket After Subtract", tracing)
            print(f"{tracing}<=_Pocket.post_produce1('{self.Name}')")


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
    def post_produce1(self, tracing: str = "") -> None:
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

        geometry_context.WorkPlane.move_to(rotated_center, tracing=next_tracing)
        geometry_context.WorkPlane.hole(diameter, depth, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=_Hole({self.Name}).post_produce1()")


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
    * *WorkPlane* (FabWorkPlane): The CadQuery workplane wrapper class object.

    """

    _Name: str
    _Solid: "FabSolid"
    _Contact: Vector
    _Normal: Vector
    _Orient: Vector
    _Depth: float
    _WorkPlane: FabWorkPlane
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
        self._GeometryContext = FabGeometryContext(self._Plane, self._WorkPlane)
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
    def post_produce1(self, tracing: str = "") -> None:
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

            work_plane: Optional[FabWorkPlane] = self._Solid._WorkPlane
            assert isinstance(work_plane, FabWorkPlane), work_plane
            work_plane.copy_workplane(plane, tracing=next_tracing)

            # Process each *operation* in *operations*:
            operation_name: str
            operation: _Operation
            for operation_name, operation in operations.items():
                if tracing:
                    print(f"{tracing}Operation[{operation_name}]:")
                operation.post_produce1(tracing=next_tracing)

        # Install the FabMount (i.e. *self*) and *datum_plane* into *model_file* prior
        # to recursively performing the *operations*:
        if tracing:
            print(f"{tracing}<=FabMount.produce('{self.Name}')")

    # FabMount.extrude():
    def extrude(self, name: str, shapes: Union[FabGeometry, Tuple[FabGeometry, ...]],
                depth: float, tracing: str = "") -> None:
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
        extrude: _Extrude = _Extrude(self, name, shapes, depth)
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
    _WorkPlane: FabWorkPlane = field(init=False, repr=False)
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
        self._WorkPlane = FabWorkPlane(initial_plane)
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
        json: Dict[str, Any] = super().to_json()
        json["Kind"] = "Solid"
        if self._StepFile:
            json["Step"] = str(self._StepFile)
        if self._Color:
            json["Color"] = self._Color
        return json

    # FabSolid.set_body():
    def set_body(self, body: Any) -> None:
        """Set the BodyBase of a FabSolid."""
        self._Body = body

    # FabSolid.is_solid():
    def is_solid(self) -> bool:
        """ Return True if FabNode is a FabAssembly."""
        return True  # All other FabNode's return False.

    # FabSolid.pre_produce():
    def pre_produce(self) -> None:
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
        fab_mount: FabMount = FabMount(name, self, contact, normal, orient, depth, self._WorkPlane)
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
    def post_produce1(self, objects_table: Dict[str, Any], fab_steps: FabSteps) -> None:
        """Perform FabSolid Phase1 post production."""
        tracing: str = self.Tracing
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabSolid.post_produce1('{self.Label}')")

        # Deterimine wether it is posible to *use_cached_step*:
        use_cached_step: bool = False
        step_path: Path = cast(Path, None)  # Force runtime error if used.
        # This was a shocker.  It turns out that __hash__() methods are not necessarily
        # consistent between Python runs.  In other words  __hash__() is non-deterministic.
        # Instead use one of the hashlib hash functions instead:
        #     hash_tuple* => repr string => hashlib.sha256 => trim to 16 bytes
        hash_tuple: Tuple[Any, ...] = self.get_hash()
        hash_bytes: bytes = repr(hash_tuple).encode("utf-8")
        hasher: Any = hashlib.new("sha256")
        hasher.update(hash_bytes)
        hash_text: str = hasher.hexdigest()[:16]
        step_path = fab_steps.activate(self.Label, hash_text)
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
                mount.post_produce1(tracing=next_tracing)

        # CadQuery workplanes do not have a color, but Assemblies do.
        rgb_color: Tuple[float, float, float] = FabColor.svg_to_rgb(self.Color)
        # TODO: move this code into FabWorkPlane:

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
                self._WorkPlane.WorkPlane, name=self.Label, color=cq.Color(*rgb_color))
            # This is really ugly.  The cq.Assembly.save() method spews out uninteresting
            # "debug" information.  See the code comments of _suppress_stdout() for more
            # information.
            with _suppress_stdout():
                assembly.save(str(step_path), "STEP")
            if tracing:
                print(f"{tracing}Wrote out {str(step_path)}")
        self._Assembly = assembly
        objects_table[self.Label] = assembly

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
    pass


if __name__ == "__main__":
    main()
