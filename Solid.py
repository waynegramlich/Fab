#!/usr/bin/env python3
"""Solid: A module for constructing 3D solids."""

# [Part2DObject](http://www.iesensor.com/FreeCADDoc/0.16-dev/d9/d57/classPart_1_1Part2DObject.html)
# [App FeaturePython](https://wiki.freecadweb.org/App_FeaturePython)
# [Vidos from "Part Design Scripting" Guy](https://www.youtube.com/c/mwganson/videos)
# [Part Design Scripting](https://forum.freecadweb.org/viewtopic.php?t=62751)
# [Scripted Objects](https://wiki.freecadweb.org/Scripted_objects)
# [FilletArc]
#     (https://github.com/FreeCAD/FreeCAD/blob/master/src/Mod/PartDesign/Scripts/FilletArc.py)
# [Creating and Manipulating Geometry](https://yorikvanhavre.gitbooks.io/
#    a-freecad-manual/content/python_scripting/creating_and_manipulating_geometry.html)
# [Use LineSegment instead of Line](https://forum.freecadweb.org/viewtopic.php?p=330999)
# [Topo Data Scripting](https://wiki.freecadweb.org/index.php?title=Topological_data_scripting)
# [Part Scripting](https://wiki.freecadweb.org/Part_scripting)

# [Draft SelectPlane](https://wiki.freecadweb.org/Draft_SelectPlane)
# [Draft Workbench Scripting](https://wiki.freecadweb.org/Draft_Workbench#Scripting)

# [Combine Draft and Sketch to simplify Modeling.](https://www.youtube.com/watch?v=lfzGEk727eo)

# Note this code uses nested dataclasses that are frozen.  Computed attributes are tricky.
# See (Set frozen data class files in __post_init__)[https://stackoverflow.com/questions/53756788]

import sys
sys.path.append(".")
import Embed
USE_FREECAD: bool
USE_CAD_QUERY: bool
USE_FREECAD, USE_CAD_QUERY = Embed.setup()

from collections import OrderedDict
from dataclasses import dataclass, field
from typing import Any, Dict, Generator, IO, List, Optional, Sequence, Tuple, Union

if USE_FREECAD:
    import FreeCAD  # type: ignore
    import Part  # type: ignore
    import FreeCAD as App  # type: ignore
    import FreeCADGui as Gui  # type: ignore
    from FreeCAD import Placement, Rotation, Vector  # type: ignore
elif USE_CAD_QUERY:
    import cadquery as cq  # type: ignore
    from cadquery import Vector  # type: ignore

# import Part  # type: ignore

from Geometry import FabCircle, FabGeometry, FabGeometryContext, FabPlane, FabWorkPlane
from Join import FabFasten, FabJoin
from Node import FabBox, FabNode
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
        """Return FabOperation name."""
        raise RuntimeError("_Operation().get_name() not implemented for {type(self)}")

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

    # _Operation.produce_shape_binder():
    def produce_shape_binder(self, part_geometries: Tuple[Any, ...],
                             prefix: str, tracing: str = "") -> "Part.Feature":
        """Produce the shape binder needed for the extrude, pocket, hole, ... operations."""
        if tracing:
            print(f"{tracing}=>FabOperation.produce_shape_binder()")
        mount: FabMount = self.Mount
        body: Any = mount.Body

        binder_placement: Placement = Placement()  # Do not move/reorient anything.
        if tracing:
            print(f"{tracing}{binder_placement.Rotation.Axis=}")

        name: str = f"{mount.Name}_{self.Name}_Binder"
        shape_binder: Part.Feature = body.newObject("PartDesign::SubShapeBinder", name)
        assert isinstance(shape_binder, Part.Feature)
        shape_binder.Placement = binder_placement
        shape_binder.Support = (part_geometries)
        # shape_binder.Support = (datum_plane, [""])
        shape_binder.Visibility = False
        if tracing:
            print(f"{tracing}<=FabOperation.produce_shape_binder()=>*")
        return shape_binder

    # _Operation._viewer_update():
    def _viewer_update(self, body: Any, part_feature: "Part.Feature") -> None:
        """Update the view Body view provider."""
        if App.GuiUp:  # pragma: no unit cover
            visibility_set(part_feature, True)
            view_object: Any = body.getLinkedObject(True).ViewObject
            part_feature.ViewObject.LineColor = getattr(
                view_object, "LineColor", part_feature.ViewObject.LineColor)
            part_feature.ViewObject.ShapeColor = getattr(
                view_object, "ShapeColor", part_feature.ViewObject.ShapeColor)
            part_feature.ViewObject.PointColor = getattr(
                view_object, "PointColor", part_feature.ViewObject.PointColor)
            part_feature.ViewObject.Transparency = getattr(
                view_object, "Transparency", part_feature.ViewObject.Transparency)
            # The following code appears to disable edge highlighting:
            # part_feature.ViewObject.DisplayMode = getattr(
            #    view_object, "DisplayMode", part_feature.ViewObject.DisplayMode)


# _Extrude:
@dataclass(order=True)
class _Extrude(_Operation):
    """_Extrude: A FreeCAD PartDesign Extrude operation.

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
        if USE_FREECAD:
            part_geometries: List[Any] = []
            geometry_group: Any = mount._Solid._GeometryGroup
            # assert isinstance(geometry_group, Any), geometry_group
            geometry_context.set_geometry_group(geometry_group)

            index: int
            for index, geometry in enumerate(self._Geometries):
                part_geometries.extend(
                    geometry.produce(geometry_context, geometry_prefix, index))

            binder_prefix: str = f"{mount.Name}_{self.Name}"
            shape_binder: Part.Feature = self.produce_shape_binder(
                tuple(part_geometries), binder_prefix, tracing=next_tracing)
            assert isinstance(shape_binder, Part.Feature)
            shape_binder.Visibility = False

            # Perform The Extrude operation:
            body: Any = mount.Body
            mount_normal: Vector = mount.Normal
            pad_name: str = f"{mount.Name}_{self.Name}_Extrude"
            extrude: Part.Feature = body.newObject("PartDesign::Pad", pad_name)
            assert isinstance(extrude, Part.Feature)
            # Type must be one of ("Length", "TwoLengths", "UpToLast", "UpToFirst", "UpToFace")
            extrude.Type = "Length"
            extrude.Profile = shape_binder
            extrude.Length = self.Depth
            extrude.Length2 = 0  # Only for Type == "TwoLengths"
            extrude.UseCustomVector = True
            extrude.Direction = mount_normal  # This may be bogus
            extrude.UpToFace = None
            extrude.Reversed = True
            extrude.Midplane = False
            extrude.Offset = 0  # Only for Type in ("UpToLast", "UpToFirst", "UpToFace")

            # For the GUI, update the view provider:
            self._viewer_update(body, extrude)
        elif USE_CAD_QUERY:
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
    """_Pocket: A FreeCAD PartDesign Pocket operation.

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
        part_geometries: List[Any] = []
        geometry_context: FabGeometryContext = mount._GeometryContext
        geometry: FabGeometry
        index: int
        if USE_FREECAD:
            for index, geometry in enumerate(geometries):
                part_geometries.extend(geometry.produce(geometry_context, prefix, index))

            # Create the *shape_binder*:
            shape_binder: Part.Feature = self.produce_shape_binder(tuple(part_geometries), prefix)
            assert isinstance(shape_binder, Part.Feature)

            # Create the *pocket* into *body*:
            body: Any = mount.Body
            pocket: Part.Feature = body.newObject("PartDesign::Pocket", f"{prefix}_Pocket")
            assert isinstance(pocket, Part.Feature)
            pocket.Profile = shape_binder
            pocket.Length = self._Depth
            pocket.Length2 = 10.0 * self._Depth
            pocket.Type = 0
            pocket.UpToFace = None
            pocket.Reversed = 0
            pocket.Midplane = 0
            pocket.Offset = 0

            # For the GUI, update the view provider:
            self._viewer_update(body, pocket)
        elif USE_CAD_QUERY:
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
        if tracing:
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
        name: str = self.Name

        # Unpack *mount* and *solid*:
        mount_normal: Vector = mount.Normal
        geometry_context: FabGeometryContext = mount._GeometryContext
        solid: FabSolid = mount.Solid
        body: Any = solid.Body
        geometry_group: Any = solid._GeometryGroup
        # assert isinstance(geometry_group, Any), geometry_group
        geometry_context.set_geometry_group(geometry_group)

        fasten: FabFasten = join.Fasten
        diameter: Vector = fasten.get_diameter(kind)
        geometry_prefix: str = name

        circle: FabCircle = FabCircle(center, mount_normal, diameter)
        part_geometries: List[Any] = []
        part_geometries.extend(circle.produce(
            geometry_context, geometry_prefix, 0, tracing=next_tracing))

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

        # Now do the FreeCAD stuff:
        # Create the *shape_binder*:
        # suffix: str = "Holes" if len(hole_group) > 1 else "Hole"

        # Create the *shape_binder*:
        prefix: str = f"{self.Name}_{name}"
        shape_binder: Part.Feature = self.produce_shape_binder(tuple(part_geometries), prefix)

        # TODO: fill in actual values for Hole.
        # Create the *hole* and upstate the view provider for GUI mode:
        solid_name: str = f"{prefix}_Drill"
        part_hole: Part.Feature = body.newObject("PartDesign::Hole", solid_name)
        assert isinstance(part_hole, Part.Feature)
        part_hole.Profile = shape_binder
        part_hole.Diameter = diameter
        part_hole.Depth = depth
        part_hole.UpToFace = None
        part_hole.Reversed = False
        part_hole.Midplane = 0

        # Fill in other fields for the top mount.
        # if is_top:
        #     assert False, "Fill in other fields."

        # For the GUI, update the view provider:
        # self._viewer_update(body, part_hole)

        if App.GuiUp:  # pragma: no unit cover
            visibility_set(part_hole, True)
            view_object: Any = body.getLinkedObject(True).ViewObject
            part_hole.ViewObject.LineColor = getattr(
                view_object, "LineColor", part_hole.ViewObject.LineColor)
            part_hole.ViewObject.ShapeColor = getattr(
                view_object, "ShapeColor", part_hole.ViewObject.ShapeColor)
            part_hole.ViewObject.PointColor = getattr(
                view_object, "PointColor", part_hole.ViewObject.PointColor)
            part_hole.ViewObject.Transparency = getattr(
                view_object, "Transparency", part_hole.ViewObject.Transparency)
            # The following code appears to disable edge highlighting:
            # part_hole.ViewObject.DisplayMode = getattr(
            #    view_object, "DisplayMode", part_hole.ViewObject.DisplayMode)

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
    _AppDatumPlane: Optional["Part.Geometry"] = field(init=False, repr=False)
    _GuiDatumPlane: Any = field(init=False, repr=False)
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
        # FreeCAD Vector metheds like to modify Vector contents; force copies beforehand:
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

        # Create the FreeCAD DatumPlane used for the drawing support.
        plane: FabPlane = self.Plane
        assert isinstance(plane, FabPlane), plane
        contact: Vector = plane.Contact
        normal: Vector = plane.Normal
        if USE_FREECAD:
            z_axis: Vector = Vector(0.0, 0.0, 1.0)
            origin: Vector = Vector()
            # FreeCAD Vector methods like to modify Vector contents; force copies beforehand:
            projected_origin: Vector = plane.point_project(contact)
            rotation: Rotation = Rotation(z_axis, normal)
            placement: Placement = Placement()
            placement.Base = projected_origin
            placement.Rotation = rotation

            if tracing:
                print(f"{tracing}{contact=}")
                print(f"{tracing}{normal=}")
                print(f"{tracing}{origin=}")
                print(f"{tracing}{projected_origin=}")
                print(f"{tracing}{rotation=}")
                print(f"{tracing}{placement=}")
                print(f"{tracing}{rotation*z_axis=}")
                print(f"{tracing}{normal=}")

            # Create, save and return the *datum_plane*:
            body: Any = self.Body
            datum_plane_name: str = f"{self.Name}_Datum_Plane"
            datum_plane: "Part.Geometry" = body.newObject("PartDesign::Plane", datum_plane_name)
            # assert isinstance(datum_plane, Part.Geometry), datum_plane
            self._AppDatumPlane = datum_plane

            # visibility_set(datum_plane, False)
            datum_plane.Visibility = False
            # xy_plane: App.GeoGeometry = body.getObject("XY_Plane")
            if tracing:
                print(f"{tracing}{placement=}")
            datum_plane.Label = self._Name
            datum_plane.AttachmentOffset = placement
            datum_plane.Placement = placement
            datum_plane.MapMode = "Translate"
            datum_plane.MapPathParameter = 0.0
            datum_plane.MapReversed = False
            datum_plane.Support = None
            datum_plane.recompute()

            if App.GuiUp:  # pragma: no unit cover
                if tracing:
                    print(f"{tracing}get_gui_document()")
                document_node: FabNode = self._Solid.get_parent_document(tracing=next_tracing)
                gui_document: Any = document_node._GuiObject
                if tracing:
                    print(f"{tracing}{gui_document=}")
                assert hasattr(gui_document, "getObject")
                gui_datum_plane: Any = getattr(gui_document, datum_plane.Name)
                if tracing:
                    print(f"{tracing}{gui_datum_plane=}")
                assert gui_datum_plane is not None
                assert hasattr(gui_datum_plane, "Visibility"), gui_datum_plane
                setattr(gui_datum_plane, "Visibility", False)
                self._GuiDatum_plane = gui_datum_plane
        elif USE_CAD_QUERY:
            if tracing:
                print(f"{tracing}Name={self._Name}")
                print(f"{tracing}Solid={self._Solid.Label}")
                print(f"{tracing}Contact={contact}")
                print(f"{tracing}Normal={normal}")
                print(f"{tracing}Orient={self._Orient}")
                print(f"{tracing}Depth={self._Depth}")
                print(f"{tracing}Contact={contact}")

            if tracing:
                print(f"{tracing}{plane=}")

            work_plane: Optional[FabWorkPlane] = self._Solid._WorkPlane
            assert isinstance(work_plane, FabWorkPlane), work_plane
            work_plane.copy_workplane(plane, tracing=next_tracing)

        # Process each *operation* in *operations*:
        operations: "OrderedDict[str, _Operation]" = self._Operations
        operation_name: str
        operation: _Operation
        for operation_name, operation in operations.items():
            if tracing:
                print(f"{tracing}Operation[{operation_name}]:")
            if USE_FREECAD:
                operation.post_produce1(tracing=next_tracing)
            elif USE_CAD_QUERY:
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
                    hole_name: str = f"{joins_name}{join_index}"
                    hole: _Hole = _Hole(self, fasten.ThreadName, kind, trimmed_depth, is_top,
                                        unique, mount_start, join, hole_name)
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
                print(f"{tracing}Hole[{hole_index}]: record_operation()")
            self.record_operation(hole)

        if tracing:
            print(f"{tracing}<=FabMount({self.Name}).drill_joins(|{len(joins)}|")


# FabSolid:
@dataclass
class FabSolid(FabNode):
    """Fab: Represents a single part constructed using FreeCAD Part Design paradigm.

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

        if tracing:
            print(f"{tracing}<=FabSolid({self.Label}).__post_init__()")

    # FabSolid.Body():
    @property
    def Body(self) -> Any:
        """Return BodyBase for FabSolid."""
        if not self._Body:
            raise RuntimeError(f"FabSolid.Body({self.Label}).Body(): body not set yet")
        return self._Body

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
    def post_produce1(self, objects_table: Dict[str, Any]) -> None:
        """Perform FabSolid Phase1 post production."""
        tracing: str = self.Tracing
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabSolid.post_produce1('{self.Label}')")

        if USE_FREECAD:
            # Create the *geometry_group* that contains all of the 2D geometry (line, arc, circle.):
            parent: FabNode = self.Up
            parent_object: Any = parent.AppObject
            geometry_group: Any
            geometry_group_name: str = f"{self.Label}_Geometry"
            # if parent.is_document():
            # if isinstance(parent_object, App.Document):
            if hasattr(parent_object, "FileName"):  # Only App.Document has a FileName.
                if tracing:
                    print(f"{tracing}=>FabSolid.post_produce1('{self.Label}'): {parent_object}")
                geometry_group = parent_object.addObject(
                    "App::DocumentObjectGroup", geometry_group_name)
            else:
                geometry_group = parent_object.newObject("App::DocumentObjectGroup")
                geometry_group.Label = geometry_group_name
            self._GeometryGroup = geometry_group
            geometry_group.Visibility = False

            # Create the *body*
            body: Any
            # if isinstance(parent_object, App.Document):
            if hasattr(parent_object, "FileName"):  # Only App.Document has FileName.
                body = parent_object.addObject("PartDesign::Body", self.Label)  # TODO: add hash
            else:
                body = parent_object.newObject("PartDesign::Body")
            self.set_body(body)
            body.Label = self.Label

            # Copy "view" fields from *body* to *gui_body* (if we are in graphical mode):
            if App.GuiUp:  # pragma: no cover
                document: FabNode = self.get_parent_document()
                gui_document: Any = document._GuiObject
                assert gui_document, "No GUI document"
                assert hasattr(gui_document, "getObject")
                gui_body: Any = getattr(gui_document, body.Name)
                assert gui_body, "No GUI body"
                assert hasattr(gui_body, "ShapeColor"), "Something is wrong"
                if hasattr(gui_body, "Proxy"):
                    # This magical line seems to get a view provider object into the Proxy field:
                    setattr(gui_body, "Proxy", 0)  # Must not be `None`
                if hasattr(gui_body, "DisplayMode"):
                    setattr(gui_body, "DisplayMode", "Shaded")
                if hasattr(gui_body, "ShapeColor"):
                    rgb = FabColor.svg_to_rgb(self.Color)
                    setattr(gui_body, "ShapeColor", rgb)

                # view_object: "ViewProviderDocumentObject"  = body.getLinkedObject(True).ViewObject
                # assert isinstance(view_object, ViewProviderDocumentObject), type(view_object)
                # model_file.ViewObject = view_object
        elif USE_CAD_QUERY:
            pass

        # Now process each *mount*
        mounts: "OrderedDict[str, FabMount]" = self._Mounts
        if tracing:
            print(f"{tracing}Iterate over |{len(mounts)}| mounts")
        mount_name: str
        mount: FabMount
        for mount_name, mount in mounts.items():
            if tracing:
                print(f"{tracing}[{mount_name}]: process")
            mount.post_produce1(tracing=next_tracing)

        if USE_CAD_QUERY:
            # CadQuery workplanes do not have a color, but Assemblies do.
            rgb_color: Tuple[float, float, float] = FabColor.svg_to_rgb(self.Color)
            assembly: cq.Assembly = cq.Assembly(
                self._WorkPlane.WorkPlane, name=self.Label, color=cq.Color(*rgb_color))
            # objects_table[self.Label] = self._WorkPlane
            self._Assembly = assembly
            objects_table[self.Label] = assembly
            # This is really ugly.  The cq.Assembly.save() method spews out uninteresting
            # "debug" information.  See the comment at the beginning for a little more information.
            with _suppress_stdout():
                assembly.save(f"/tmp/{self.Label}.step", "STEP")

        if tracing:
            print(f"{tracing}<=FabSolid.post_produce1('{self.Label}')")


# TODO: Move this to FabNode class:
def visibility_set(element: Any, new_value: bool = True, tracing: str = "") -> None:
    """Set the visibility of an element.

    Arguments:
    * *element* (Any): Any FreeCAD element.<
    * *new_value* (bool): The new visibility to use.  (Default True):

    """
    if tracing:
        print(f"{tracing}=>visibility_set({element}, {new_value})")
    if App.GuiUp:   # pragma: no unit cover
        if tracing:
            print(f"{tracing}App.GuiUp")
        gui_document: Optional[Any] = (
            Gui.ActiveDocument if hasattr(Gui, "ActiveDocument") else None)
        if tracing:
            print(f"{tracing}{gui_document=}")
            print(f"{tracing}{dir(gui_document)=}")
            print(f"{tracing}{hasattr(gui_document, 'Name')=})")
        if gui_document and hasattr(gui_document, "Name"):
            name: str = getattr(element, "Name")
            if tracing:
                print(f"{tracing}{name=}")
            sub_element: Any = gui_document.getObject(name)
            if sub_element is not None and hasattr(sub_element, "Visibility"):
                if isinstance(getattr(sub_element, "Visibility"), bool):
                    setattr(sub_element, "Visibility", new_value)
    if tracing:
        print(f"{tracing}<=visibility_set({element}, {new_value})")

    if False:  # pragma: no unit cover
        pass
        # App.getDocument('Unnamed').getObject('Body').newObject('PartDesign::Plane', 'DatumPlane')
        # App.getDocument('Unnamed').getObject('DatumPlane').Support = [
        #     (App.getDocument('Unnamed').getObject('XY_Plane'), '')]
        # App.getDocument('Unnamed').getObject('DatumPlane').MapMode = 'FlatFace'
        # App.activeDocument().recompute()
        # Gui.getDocument('Unnamed').setEdit(
        #     App.getDocument('Unnamed').getObject('Body'), 0, 'DatumPlane.')
        # Gui.Selection.clearSelection()

    if False:  # pragma: no unit cover
        # Click on [Plane face]
        pass
        # App.getDocument('Unnamed').getObject('DatumPlane').AttachmentOffset = (
        #     App.Placement(App.Vector(0.0000000000, 0.0000000000, 0.0000000000),
        #                   App.Rotation(0.0000000000, 0.0000000000, 0.0000000000)))
        # App.getDocument('Unnamed').getObject('DatumPlane').MapReversed = False
        # App.getDocument('Unnamed').getObject('DatumPlane').Support = [
        #     (App.getDocument('Unnamed').getObject('XY_Plane'), '')]
        # App.getDocument('Unnamed').getObject('DatumPlane').MapPathParameter = 0.000000
        # App.getDocument('Unnamed').getObject('DatumPlane').MapMode = 'FlatFace'
        # App.getDocument('Unnamed').getObject('DatumPlane').recompute()
        # Gui.getDocument('Unnamed').resetEdit()
        # _tv_DatumPlane.restore()
        # del(_tv_DatumPlane)


def main() -> None:
    pass


if __name__ == "__main__":
    main()
