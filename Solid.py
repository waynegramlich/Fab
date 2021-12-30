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
Embed.setup()

from dataclasses import dataclass, field
from typing import Any, cast, Dict, List, Optional, Tuple, Union
from pathlib import Path


import FreeCAD  # type: ignore
import Part  # type: ignore
import FreeCAD as App  # type: ignore
import FreeCADGui as Gui  # type: ignore

from FreeCAD import Placement, Rotation, Vector
# import Part  # type: ignore

from Geometry import FabCircle, FabGeometry, FabPolygon
from Join import FabFasten, FabJoin
from Tree import FabInterior, FabNode, FabRoot
from Utilities import FabColor


@dataclass
# FabGroup:
class FabGroup(FabInterior):
    """FabGroup: A named group of FabNode's.

    Inherited Attributes:
    * *Name* (str)
    * *Parent* (FabNode)
    * *Children* (Tuple[FabNode, ...)
    * *ChildrenNames* (Tuple[str, ...])

    """

    Group: App.DocumentObjectGroup = field(
        init=False, repr=False, default=cast(App.DocumentObjectGroup, None))

    # FabGroup.__post_init__():
    def __post_init__(self):
        """Initialize FabGroup."""
        super().__post_init__()

    # FabGroup._setup():
    def _setup(self, parent: FabNode, all_nodes: List[FabNode], tracing: str = "") -> None:
        """Set up the FabGroup."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabGroup._setup('{self.Name}', '{parent.Name}')")
        super()._setup(self, all_nodes, next_tracing)
        if tracing:
            print(f"{tracing}<=FabGroup._setup('{self.Name}', '{parent.Name}')")

    # FabGroup.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Create the FreeCAD group object."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabGroup.produce('{self.FullPath}')")
        errors: List[str] = []

        # Create the *group* that contains all of the FabNode's:
        parent_object: Any = context["parent_object"]
        group: App.DocumentObjectGroup = parent_object.addObject(
            "App::DocumentObjectGroup", f"{self.Name}")
        group.Visibility = False
        self.Group = group
        visibility_set(group)

        child: FabNode
        context["parent_object"] = self.Group
        for child in self.Children:
            if isinstance(child, FabFile):
                errors.append(f"{self.FullPath}: {child.FullPath} is a FabFile under a group")
            errors.extend(child.produce(context.copy(), next_tracing))
        if tracing:
            print(f"{tracing}<=FabGroup.produce('{self.FullPath}')")
        return tuple(errors)


# FabAssembly:
@dataclass
class FabAssembly(FabGroup):
    """FabAssembly: A group FabSolid's and sub-FabAssembly's."""

    _Zilch: int = field(init=False, repr=False, default=0)  # Empty dataclasses are not allowed.

    # FabAssembly.__post_init__():
    def __post_init__(self) -> None:
        """Initialize FabAssembly."""
        super().__post_init__()


# FabFile:
@dataclass
class FabFile(FabInterior):
    """FabFile: Represents a FreeCAD document file.

    Inherited Attributes:
    * *Name* (str): Node name
    * *Children* (Tuple[Union[FabAssembly, FablGroup, FabSolid], ...]):
      The children nodes which are constrained to "group-like" or a FabSolid.
    * *ChlidrenNames* (Tuple[str, ...]): The Children names.

    Attributes:
    * *FilePath* (Path):
      The Python pathlib.Path file name which must have a suffix of `.fcstd` or `.FCStd`.

    """

    FilePath: Path = Path("bogus_file")

    # FabFile.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the AppDocument."""

        suffix: str = self.FilePath.suffix
        valid_suffixes: Tuple[str, ...] = (".fcstd", ".FCStd")
        if suffix not in valid_suffixes:
            raise RuntimeError(f"{self.FullPath}: '{self.FilePath}' suffix '{suffix}' "
                               f"is not one of {valid_suffixes}.")
        self._check_children()

    # FabFile._check_children():
    def _check_children(self) -> None:
        """Verify that children are valid types."""
        child: FabNode
        for child in self.Children:
            if not isinstance(child, (FabAssembly, FabGroup, FabSolid)):
                raise RuntimeError(
                    f"{self.FullPath}: {child.FullPath} is not a {type(child)}, "
                    "not FabAssembly/FabGroup/FabSolid")

    # FabFile.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Produce all of the FabSolid's."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabFile.produce('{self.Name}', *)")

        # Create the new *app_document*:
        app_document = cast(App.Document, App.newDocument(self.Name))
        assert isinstance(app_document, App.Document)  # Just to be sure.
        context["app_document"] = app_document
        context["parent_object"] = app_document

        # Get the associated *gui_document* (if Gui is up):
        if App.GuiUp:  # pragma: no unit cover
            gui_document = cast(Gui.Document, Gui.getDocument(self.Name))
            assert isinstance(gui_document, Gui.Document)  # Just to be sure.
            context["gui_document"] = gui_document

        # Produce all the requested Solids and Assemblies.
        self._check_children()
        errors: List[str] = []
        child: FabNode
        for child in self.Children:
            assert isinstance(child, (FabAssembly, FabGroup, FabSolid))
            errors.extend(child.produce(context.copy(), tracing=next_tracing))

        # Recompute, save, ...:
        app_document.recompute()
        app_document.saveAs(str(self.FilePath))
        if tracing:
            print(f"{tracing}<=FabFile.produce('{self.Name}', *)")
        return tuple(errors)

    # FabFile._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Run FabFile unit tests."""
        # No solids specified:
        fcstd_path: Path = Path("/tmp/part_file_test.fcstd")
        try:
            FabFile("EmptyFile", (), fcstd_path)
            assert False
        except ValueError as value_error:
            assert str(value_error) == "At least one FabSolid needs to be specified"

        # Bogus solid error:
        try:
            FabFile("BogusSolid", (cast(FabSolid, None),), fcstd_path)
            assert False
        except ValueError as value_error:
            assert str(value_error) == "None is not a FabSolid"

        # Duplicate part name error:
        contact: Vector = Vector()
        z_axis: Vector = Vector(0, 0, 1)
        y_axis: Vector = Vector(0, 1, 0)
        origin: Vector = Vector()
        circle1: FabCircle = FabCircle(origin, 10.0)
        depth1: float = 10.0
        pad1: FabPad = FabPad("Cylinder1", circle1, depth1)
        operations1: Tuple[FabOperation, ...] = (pad1,)
        mount1: FabMount = FabMount("Mount1", operations1, contact, z_axis, y_axis)
        solid1: FabSolid = FabSolid("Part1", (mount1,), "hdpe", "orange")

        # Duplicate Part Names:
        try:
            FabFile("Duplicate Solid", (solid1, solid1), fcstd_path)
            assert False
        except ValueError as value_error:
            assert str(value_error) == "There are two or more Part's with the same name 'Part1'"

        # Test Open/Produce/Close
        _ = fcstd_path.unlink if fcstd_path.exists() else None
        fab_file: FabFile = FabFile("Open_Produce_Close", (solid1,), fcstd_path)
        assert isinstance(fab_file, FabFile)
        context: Dict[str, Any] = {}
        assert isinstance(context["app_document"], App.Document)
        assert isinstance(context["parent_object"], App.Document)
        if App.GuiUp:
            assert(isinstance(context["gui_document"], Gui.Document))
        errors: Tuple[str, ...] = fab_file.produce(context.copy())
        assert not errors, errors
        assert fcstd_path.exists(), f"{fcstd_path} file not generated."
        fcstd_path.unlink()
        assert not fcstd_path.exists()


# FabOperation:
@dataclass
class FabOperation(FabNode):
    """FabOperation: An base class for operations -- FabPad, FabPocket, FabHole, etc.

    All model operations are immutable (i.e. frozen.)
    """

    # Name: str

    # FabOperation.get_name():
    def get_name(self) -> str:
        """Return FabOperation name."""
        raise NotImplementedError(f"{type(self)}.get_name() is not implemented")

    # FabOperation.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Return the operation sort key."""
        raise NotImplementedError(f"{type(self)}.produce() is not implemented")
        return ()

    # FabOperation.produce_shape_binder():
    def produce_shape_binder(self, context: Dict[str, Any],
                             part_geometries: Tuple[Part.Part2DObject, ...],
                             prefix: str, tracing: str = "") -> Part.Feature:
        """Produce the shape binder needed for the pad, pocket, hole, ... operations."""
        if tracing:
            print(f"{tracing}=>FabOperation.produce_shape_binder()")
        body = cast(Part.BodyBase, context["solid_body"])

        binder_placement: Placement = Placement()  # Do not move/reorient anything.
        if tracing:
            print(f"{tracing}{binder_placement.Rotation.Axis=}")

        # datum_plane: Any = context["mount_plane"]
        shape_binder: Part.Feature = body.newObject(
            "PartDesign::SubShapeBinder", f"{prefix}_Binder")
        assert isinstance(shape_binder, Part.Feature)
        shape_binder.Placement = binder_placement
        shape_binder.Support = (part_geometries)
        # shape_binder.Support = (datum_plane, [""])
        shape_binder.Visibility = False
        if tracing:
            print(f"{tracing}<=FabOperation.produce_shape_binder()=>*")
        return shape_binder

    # FabOperation._viewer_upate():
    def _viewer_update(self, body: Part.BodyBase, part_feature: Part.Feature) -> None:
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


# FabPad:
@dataclass
class FabPad(FabOperation):
    """FabPad: A FreeCAD PartDesign Pad operation.

    Attributes:
    * *Name* (str): The operation name.
    * *Geometry* (FabGeometry): The ModlePolygon or FabCircle to pad with.
    * *Depth* (float): The depth to pad to in millimeters.

    """

    Geometry: FabGeometry
    Depth: float

    # FabPad.__post_init__():
    def __post_init__(self) -> None:
        """Verify FabPad values."""
        if not isinstance(self.Geometry, FabGeometry):
            raise ValueError(f"{self.Geometry} is not a FabGeometry")
        if self.Depth <= 0.0:
            raise ValueError(f"Depth ({self.Depth}) is not positive.")

    # FabPad.get_name():
    def get_name(self) -> str:
        """Return FabPad name."""
        return self.Name

    # FabPad.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Produce the Pad."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabPad.produce('{self.Name}')")
        # Extract the *part_geometries* and create the assocated *shape_binder*:
        prefix = cast(str, context["prefix"])
        next_prefix: str = f"{prefix}_{self.Name}"
        part_geometries: Tuple[Part.Part2DObject, ...]
        part_geometries = self.Geometry.produce(context.copy(), next_prefix)
        shape_binder: Part.Feature = self.produce_shape_binder(
            context.copy(), part_geometries, next_prefix, tracing=next_tracing)
        assert isinstance(shape_binder, Part.Feature)
        shape_binder.Visibility = False

        # Extract *body* and *normal* from *context*:
        body = cast(Part.BodyBase, context["solid_body"])
        mount_normal = cast(Vector, context["mount_normal"])

        # Perform The Pad operation:
        pad: Part.Feature = body.newObject("PartDesign::Pad", next_prefix)
        assert isinstance(pad, Part.Feature)
        pad.Type = "Length"  # Type in ("Length", "TwoLengths", "UpToLast", "UpToFirst", "UpToFace")
        pad.Profile = shape_binder
        pad.Length = self.Depth
        pad.Length2 = 0  # Only for Type == "TwoLengths"
        pad.UseCustomVector = True
        pad.Direction = mount_normal  # This may be bogus
        pad.UpToFace = None
        pad.Reversed = True
        pad.Midplane = False
        pad.Offset = 0  # Only for Type in ("UpToLast", "UpToFirst", "UpToFace")

        # For the GUI, update the view provider:
        self._viewer_update(body, pad)

        if tracing:
            print(f"{tracing}<=FabPad.produce('{self.Name}')")
        return ()

# FabPocket:
@dataclass
class FabPocket(FabOperation):
    """FabPocket: A FreeCAD PartDesign Pocket operation.

    Attributes:
    * *Name* (str): The operation name.
    * *Geometry* (FabGeometry): The Polygon or Circle to pocket.
    * *Depth* (float): The pocket depth in millimeters.

    """

    Geometry: FabGeometry
    Depth: float

    # FabPocket__post_init__():
    def __post_init__(self) -> None:
        """Verify FabPad values."""
        if not isinstance(self.Geometry, FabGeometry):
            raise ValueError(f"{self.Geometry} is not a FabGeometry")
        if self.Depth <= 0.0:
            raise ValueError(f"Depth ({self.Depth}) is not positive.")

    # FabPocket.get_name():
    def get_name(self) -> str:
        """Return FabPocket name."""
        return self.Name

    # FabPocket.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Produce the Pad."""
        if tracing:
            print("{tracing}=>FabPocket.produce('{self.Name}')")
        # Extract the *part_geometries*:
        prefix = cast(str, context["prefix"])
        next_prefix: str = f"{prefix}_{self.Name}"
        part_geometries: Tuple[Part.Part2DObject, ...]
        part_geometries = self.Geometry.produce(context.copy(), next_prefix)

        # Create the *shape_binder*:
        shape_binder: Part.Feature = self.produce_shape_binder(
            context, part_geometries, next_prefix)
        assert isinstance(shape_binder, Part.Feature)

        # Create the *pocket* into *body*:
        body = cast(Part.BodyBase, context["solid_body"])
        pocket: Part.Feature = body.newObject("PartDesign::Pocket", f"{next_prefix}_Pocket")
        assert isinstance(pocket, Part.Feature)
        pocket.Profile = shape_binder
        pocket.Length = self.Depth
        pocket.Length2 = 10.0 * self.Depth
        pocket.Type = 0
        pocket.UpToFace = None
        pocket.Reversed = 0
        pocket.Midplane = 0
        pocket.Offset = 0

        # For the GUI, update the view provider:
        self._viewer_update(body, pocket)

        if tracing:
            print("{tracing}<=FabPocket.produce('{self.Name}')")
        return ()


_HoleKey = Tuple[str, str, float, bool, int]


# _Hole:
@dataclass(order=True)
class _Hole(object):
    """_Hole: FabDrill helper class that represents a hole."""

    # Size: str  # Essentially the diameter
    # Profile: str  # Essentially the fastener thread pitch
    ThreadName: str  # Thread name
    Kind: str  # "thread", "close", or "standard"
    Depth: float  # The depth of the drill hole
    IsTop: bool  # Is the top of the fastener
    Unique: int  # Non-zero to force otherwise common holes into separate operations.
    Center: Vector = field(compare=False)  # The Center (start point) of the drill
    Join: FabJoin = field(compare=False)  # The associated FabJoin

    # _Hole.Key():
    @property
    def Key(self) -> _HoleKey:
        """Return a Hole key."""
        return (self.ThreadName, self.Kind, self.Depth, self.IsTop, self.Unique)


# FabDrill:
@dataclass
class FabDrill(FabOperation):
    """FabDrill: A FreeCAD PartDesign Pocket operation.

    Attributes:
    * *Name* (str): The operation name.
    * *Joins* (FabCircle): The Circle to drill.
    * *Depth* (float): Exlplicit depth to use. (Default: -1 to have system try to figure it out.)

    """

    Joins: Union[FabJoin, Tuple[FabJoin, ...]]
    Depth: float = -1.0
    _joins: Tuple[FabJoin, ...] = field(init=False, repr=False, default=())

    # FabDrill.__post_init__():
    def __post_init__(self) -> None:
        """Verify FabPad values."""
        joins: List[FabJoin] = []
        join: Any
        if isinstance(self.Joins, tuple):
            index: int
            for index, join in enumerate(self.Joins):
                if not isinstance(join, FabJoin):
                    raise ValueError(f"Joins[{index}]: Has type {type(join)}, not FabJoin")
                joins.append(join)
        elif isinstance(self.Joins, FabJoin):
            joins.append(self.Joins)
        else:
            raise ValueError(f"Joins: Has type {type(join)}, not FabJoin or Tuple[FabJoin, ...]")
        self._joins = tuple(joins)
        if (join.Start - join.End).Length < 1.0e-8:
            raise ValueError(f"FabJoin has same start {join.Start} and {join.Stop}.")

    # FabDrill.get_name():
    def get_name(self) -> str:
        """Return FabDrill name."""
        return self.Name

    # FabDrill.get_kind():
    def get_kind(self) -> str:
        """Return the sub-class drill kind."""
        raise NotImplementedError(f"{type(self)}.get_kind() not implmeneted")

    # FabDrill.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Produce the Hole."""

        EPSILON: float = 1.0e-8

        # close():
        def close(vector1: Vector, vector2: Vector) -> bool:
            """Return whether 2 normals are aligned."""
            return (vector1 - vector2).Length < EPSILON

        # normal_distance():
        def normal_distance(normal: Vector, start: Vector, end: Vector) -> float:
            """Return distance from start to end along normal."""
            distance: float = (end - start).Length
            if close(start - distance * normal, end):
                distance = -distance
            elif not close(start + distance * normal, end):
                assert False, f"{start=} and  {end=} are not aligned {normal=}."
            return distance

        # Extract the *part_geometries*:
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabDrill.produce('{self.Name}')")

        # Grab mount information from *context*:
        prefix = cast(str, context["prefix"])
        next_prefix: str = f"{prefix}_{self.Name}"
        # mount_name = cast(str, context["mount_name"])
        mount_contact = cast(Vector, context["mount_contact"])
        mount_normal = cast(Vector, context["mount_normal"])
        bottom_depth = cast(float, context["mount_depth"])
        # mount_plane = context["mount_plane"]
        # assert isinstance(mount_plane, Part.Geometry)
        assert abs(mount_normal.Length - 1.0) < EPSILON, (
            "{self.FullPath}: Mount normal is not of length 1")
        if tracing:
            print(f"{tracing}{mount_contact=} {mount_normal=} {bottom_depth=}")

        # Make copy of *mount_normal* and normailize it:
        copy: Vector = Vector()
        mount_normal = (mount_normal + copy).normalize()
        mount_z_aligned: bool = close(mount_normal, Vector(0.0, 0.0, 1.0))

        # Some commonly used variables:
        depth: float
        hole: _Hole
        is_top: bool
        join: FabJoin
        fasten: FabFasten
        uinique: int

        # For each *join*, generate a *hole* request.  Any errors are collected in *errors*:
        holes: List[_Hole] = []
        errors: List[str] = []
        for join in self._joins:
            # Unpack *join* and associated *fasten*:
            start: Vector = join.Start
            end: Vector = join.End
            fasten = join.Fasten

            # *start* and *end* specify a line segment in 3D space that corresponds to the
            # fastener shaft length (excluding extra shaft at the end for nuts and washers.)  The
            # *start*/*end* line segment can be extended to an infinitely long line in 3D space.
            # The mount specifies top and bottom mount plane that are supposed to totally enclose
            # include the solid.  If the infinitely long line not perpendicular to the top/bottom
            # mount planes, it is an error.  The locations where the infinitely long line
            # intersects the top/bottom mount planes are *top* and *bottom* respectively.
            # The *top* and *bottom* points specify a line segment that can potentially drilled
            # out by this operation.  It is important to understand that the direction vector
            # from *start* to *end* may be in the same or opposite direction as the from *top*
            # to *bottom*.  If either *start* or *end* occur inside of the *top*/*bottom*
            # line segment, the drill out section gets shortened appropriately.  Finally, if
            # *start* matches either *top* or *bottom* (within epsilon), any requested
            # countersink or counter bore operations are enabled for the drill hole; otherwise,
            # it is just a simple drill operation.

            # Find *top* and *bottom* points where infinite line pierces top/bottom mount planes:
            top: Vector = start.projectToPlane(mount_contact, mount_normal)
            # bottom_contact: Vector = mount_contact - bottom_depth * mount_normal

            # Ensure *start*/*end* line segment is perpendicular to mount planes.
            start_end_normal: Vector = (end - start).normalize()
            start_end_aligned: bool
            if not (close(mount_normal, start_end_normal) or
                    close(mount_normal, -start_end_normal)):
                errors.append(
                    f"{self.FullPath}: Fasten {join.Name} is not perpendicular to mount plane")
                continue

            # Compute distances along line from *top* along the *down_normal* direction:
            down_normal: Vector = -mount_normal
            start_distance: float = normal_distance(down_normal, top, start)
            end_distance: float = normal_distance(down_normal, top, end)
            close_distance: float = min(start_distance, end_distance)
            far_distance: float = max(start_distance, end_distance)
            assert close_distance <= far_distance
            if far_distance <= 0.0 or close_distance >= bottom_depth:
                errors.append(f"{self.FullPath}: Fasten {fasten.Name} "
                              "does not overlap with solid")
                continue
            if close_distance > 0.0:
                errors.append(f"{self.FullPath}: Fasten {fasten.Name} starts below mount plane")
                continue
            depth = min(bottom_depth, far_distance)
            is_top = close(start, top)
            kind: str = self.get_kind()
            # This is quite ugly for now.  If the *mount_normal* equals the +Z axis, multiple
            # holes of the same characteristics can be done together.  Otherwise, it is
            # one drill operation per hole.  Sigh:
            unique: int = 0 if mount_z_aligned else id(join)
            hole = _Hole(fasten.ThreadName, kind, depth, is_top, unique, top, join)
            holes.append(hole)

        # Group all *holes* with the same *key* together:
        key: _HoleKey
        hole_groups: Dict[_HoleKey, List[_Hole]] = {}
        for hole in holes:
            key = hole.Key
            if key not in hole_groups:
                hole_groups[key] = []
            hole_groups[key].append(hole)

        # For each *hole_group* create a PartDesign Hole:
        index: int
        for index, key in enumerate(sorted(hole_groups.keys())):
            # Unpack *key*:
            thread_name: str
            thread_name, kind, depth, is_top, unique = key
            diameter: float = fasten.get_diameter(kind)

            # Construct the "drawing"
            part_geometries: List[Part.Part2DObject] = []
            hole_group: List[_Hole] = hole_groups[key]
            for hole in hole_group:
                # Construct the drawing"
                # Sanity check that each *fasten* object matches the *key*.
                join = hole.Join
                fasten = join.Fasten
                assert fasten.ThreadName == thread_name and self.get_kind() == kind and (
                    hole.Depth == depth and hole.IsTop == is_top)
                center: Vector = hole.Center
                circle: FabCircle = FabCircle(center, diameter)
                part_geometries.extend(circle.produce(context.copy(),
                                                      next_prefix, tracing=next_tracing))

            # Create the *shape_binder*:
            next_prefix = f"{prefix}.DrillCircle{index:03d}"
            shape_binder: Part.Feature = self.produce_shape_binder(
                context.copy(), tuple(part_geometries), next_prefix, tracing=next_tracing)
            assert isinstance(shape_binder, Part.Feature)
            body = cast(Part.BodyBase, context["solid_body"])

            # TODO: fill in actual values for Hole.
            # Create the *pocket* and upstate the view provider for GUI mode:
            part_hole: Part.Feature = body.newObject("PartDesign::Hole", f"{next_prefix}_Hole")
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
            self._viewer_update(body, part_hole)

        if tracing:
            print(f"{tracing}<=FabDrill.produce('{self.Name}')")
        return tuple(errors)


# FabThread:
@dataclass
class FabThread(FabDrill):
    """Drill and thread FabJoin's."""

    def get_kind(self) -> str:
        """Return a thread diameter kind."""
        return "thread"


# FabClose:
@dataclass
class FabClose(FabDrill):
    """Drill a close a FabJoin's."""

    def get_kind(self) -> str:
        """Return a thread diameter kind."""
        return "close"


# FabLoose:
@dataclass
class FabLoose(FabDrill):
    """Drill Loose FabJoin's."""

    def get_kind(self) -> str:
        """Return a thread diameter kind."""
        return "loose"


# FabHole:
@dataclass
class FabHole(FabOperation):
    """FabHole: A FreeCAD PartDesign Pocket operation.

    Attributes:
    * *Name* (str): The operation name.
    * *Circle* (FabCircle): The Circle to drill.
    * *Depth* (float): The depth

    """

    Circle: FabCircle
    Depth: float

    # FabHole.__post_init__():
    def __post_init__(self) -> None:
        """Verify FabPad values."""
        if not isinstance(self.Circle, FabCircle):
            raise ValueError(f"{self.Geometry} is not a FabCircle")
        if self.Depth <= 0.0:
            raise ValueError(f"Depth ({self.Depth}) is not positive.")

    # FabHole.get_name():
    def get_name(self) -> str:
        """Return FabHole name."""
        return self.Name

    # FabHole.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Produce the Hole."""
        # Extract the *part_geometries*:
        if tracing:
            print("{tracing}=>FabHole.produce('{self.Name}')")
        prefix = cast(str, context["prefix"])
        next_prefix: str = f"{prefix}_{self.Name}"
        part_geometries: Tuple[Part.Part2DObject, ...] = (
            self.Circle.produce(context.copy(), next_prefix))

        # Create the *shape_binder*:
        shape_binder: Part.Feature = self.produce_shape_binder(
            context.copy(), part_geometries, next_prefix)
        assert isinstance(shape_binder, Part.Feature)
        body = cast(Part.BodyBase, context["solid_body"])

        # Create the *pocket* and upstate the view provider for GUI mode:
        hole: Part.Feature = body.newObject("PartDesign::Hole", f"{next_prefix}_Hole")
        assert isinstance(hole, Part.Feature)
        hole.Profile = shape_binder
        hole.Diameter = self.Circle.Diameter
        hole.Depth = self.Depth
        hole.UpToFace = None
        hole.Reversed = 0
        hole.Midplane = 0

        # For the GUI, update the view provider:
        self._viewer_update(body, hole)

        if tracing:
            print("{tracing}<=FabHole.produce('{self.Name}')")
        return ()

# FabMount:
@dataclass
class FabMount(FabInterior):
    """FabMount: An operations plane that can be oriented for subsequent machine operations.

    This class basically corresponds to a FreeCad Datum Plane.  It is basically the surface
    to which the 2D FabGeometry's are mapped onto prior to performing each operation.
    This class is immutable (i.e. frozen.)

    Attributes:
    * *Name*: (str): The name of the FabPlane.
    * *Operations* (Tuple[FabOperation, ...]): The operations to perform.
    * *Contact* (Vector): A point on the plane.
    * *Normal* (Vector): A normal to the plane
    * *Orient* (Vector):
      A vector in the plane that specifies the north direction when mounted in a machining vice.
    * *Depth* (Optional[float]):
      The maximum depth limit.  If not specified, an estimated  maximum depth limit is
      "deduced" the using the information from the initial extrude operation. (Default: None)

    """

    # Name: str
    # Operations: Tuple[FabOperation, ...]

    Contact: Vector = Vector()
    Normal: Vector = Vector(0, 0, 1)
    Orient: Vector = Vector(0, 1, 0)
    Depth: Optional[float] = None

    # FabMount.__post_init__():
    def __post_init__(self) -> None:
        """Verify that FabMount arguments are valid."""

        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        super().__post_init__()
        copy: Vector = Vector()  # Make private copy of Vector's.
        object.__setattr__(self, "Contact", self.Contact + copy)
        object.__setattr__(self, "Normal", self.Normal + copy)
        object.__setattr__(self, "Orient", self.Orient + copy)
        object.__setattr__(self, "Depth", self.Depth)

    @property
    # FabMount.Operations:
    def Operations(self) -> Tuple[FabOperation, ...]:
        """Return mount FabOperation's."""
        return cast(Tuple[FabOperation, ...], self.Children)

    # FabMount.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Create the FreeCAD DatumPlane used for the drawing support.

        Arguments:
        * *body* (PartDesign.Body): The FreeCAD Part design Body to attach the datum plane to.
        * *name* (Optional[str]): The datum plane name.
          (Default: "...DatumPlaneN", where N is incremented.)
        * Returns:
          * (Part.Geometry) that is the datum_plane.

        """
        # Compute *rotation* from <Zb> to <Nd>:
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabMount.produce('{self.Name}')")

        contact: Vector = self.Contact  # Pd
        normal: Vector = self.Normal  # <Nd>
        z_axis: Vector = Vector(0.0, 0.0, 1.0)
        origin: Vector = Vector()
        projected_origin: Vector = origin.projectToPlane(contact, normal)
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
        body = cast(Part.BodyBase, context["solid_body"])
        datum_plane: Part.Geometry = body.newObject("PartDesign::Plane", f"{self.Name}_Datum_Plane")
        context["mount_plane"] = datum_plane
        # visibility_set(datum_plane, False)
        datum_plane.Visibility = False
        # xy_plane: App.GeoGeometry = body.getObject("XY_Plane")
        if tracing:
            print(f"{tracing}{placement=}")
        datum_plane.AttachmentOffset = placement
        datum_plane.Placement = placement
        datum_plane.MapMode = "Translate"
        datum_plane.MapPathParameter = 0.0
        datum_plane.MapReversed = False
        datum_plane.Support = None
        datum_plane.recompute()

        if App.GuiUp:  # pragma: no unit cover
            gui_document = cast(Gui.Document, context["gui_document"])  # Optional[Gui.Document]
            assert gui_document, "No GUI document"

            object_name: str = datum_plane.Name
            gui_datum_plane: Any = gui_document.getObject(object_name)
            if gui_datum_plane is not None and hasattr(gui_datum_plane, "Visibility"):
                setattr(gui_datum_plane, "Visibility", False)

        # Provide datum_plane to lower levels of produce:
        context["mount_plane"] = datum_plane
        context["mount_normal"] = self.Normal
        context["mount_contact"] = self.Contact

        # FIXME: This is a kludge for now:
        operations: Tuple[FabOperation, ...] = self.Operations
        assert operations
        # operation0: FabOperation = operations[0]
        # assert isinstance(operation0, FabPad)
        # mount_depth: float = operation0.Depth
        if not isinstance(self.Depth, float):
            assert False, f"{self.FullPath}: Does not have a depth."
        context["mount_depth"] = self.Depth

        # Install the FabMount (i.e. *self*) and *datum_plane* into *model_file* prior
        # to recursively performing the *operations*:
        # prefix = cast(str, context["prefix"])
        operation: FabOperation
        for operation in self.Operations:
            operation.produce(context.copy(), tracing=next_tracing)
        if tracing:
            print(f"{tracing}<=FabMount.produce('{self.Name}')")
        return ()


# FabSolid:
@dataclass
class FabSolid(FabInterior):
    """Fab: Represents a single part constructed using FreeCAD Part Design paradigm.

    Inherited Attributes:
    * *Name* (str): The model name.
    * *Children* (Tuple[FabMount, ...]): The various model mounts to use to construct the part.
    * *ChildrenNames* (Tuple[str, ...]): The various children names.
    * *Parent* (FabNode): The Parent FabNode.

    Attributes:
    * *Material* (str): The material to use.
    * *Color* (str): The color to use.

    """

    Material: str = ""
    Color: str = "red"
    _pads: Tuple[Optional[FabPad], ...] = field(init=False, repr=False, default=())

    # FabSolid.__post_init__():
    def __post_init__(self) -> None:
        """Verify FabSolid arguments."""
        super().__post_init__()

    # FabSolid._mounts_check():
    def _mounts_check(self) -> None:
        """Verify that all children are FabMounts."""
        child: FabNode
        for child in self.Children:
            if not isinstance(child, FabNode):
                raise RuntimeError(
                    f"{self.FullName}: {child.FullName} is {type(child)}, not FabMount.")

    # FabSolid.Mounts():
    @property
    def Mounts(self) -> Tuple[FabMount, ...]:
        """Return children solids."""
        self._mounts_check()
        return cast(Tuple[FabMount], self.Children)

    # FabSolid.Mounts.setter():
    @Mounts.setter
    def Mounts(self, mounts: Tuple[FabMount]) -> None:
        """Set the FabSolid mounts."""
        self.Children = mounts
        self._mounts_check()

    # FabSolid.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Produce the FabSolid."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabSolid.produce('{self.Name}')")
        self._mounts_check()

        # Do consistency checking and extract the *pads* for guessing maximum depth later on.
        mounts: Tuple[FabMount, ...] = self.Mounts
        if not mounts:
            raise RuntimeError("{self.FullPath}: No FabMount's!")
        index: int
        mount: FabMount
        for index, mount in enumerate(mounts):
            operations: Tuple[FabOperation, ...] = mount.Operations
            if not operations:
                raise ValueError(
                    f"{self.Name}: Mount {mount.Name} has no FabOperation's.")
            first_operation: FabOperation = operations[0]
            if index == 0 and not isinstance(first_operation, FabPad):
                raise RuntimeError(
                    f"{self.FullPath}: Mount {mount.FullPath} Operation {first_operation.FullPath} "
                    f"is {type(first_operation)}, not FabPad")

        # Create the *geometry_group* that contains all of the 2D geometry (line, arc, circle.):
        parent_object: Any = context["parent_object"]
        geometry_group: App.DocumentObjectGroup
        geometry_group_name: str = f"{self.Name}_Geometry"
        if isinstance(parent_object, App.Document):
            geometry_group = parent_object.addObject(
                "App::DocumentObjectGroup", geometry_group_name)
        else:
            geometry_group = parent_object.newObject("App::DocumentObjectGroup")
            geometry_group.Label = geometry_group_name

        geometry_group.Visibility = False
        context["geometry_group"] = geometry_group

        # Create the *body*
        body: Part.BodyBase
        if isinstance(parent_object, App.Document):
            body = parent_object.addObject("PartDesign::Body", self.Name)
        else:
            body = parent_object.newObject("PartDesign::Body")
            body.Label = self.Name
        context["solid_body"] = body

        # Copy "view" fields from *body* to *gui_body* (if we are in graphical mode):
        if App.GuiUp:  # pragma: no cover
            gui_document = cast(Gui.Document, context["gui_document"])  # Optional[Gui.Document]
            assert gui_document, "No GUI document"

            gui_body: Any = gui_document.getObject(body.Name)
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

        # Process each *mount*:
        for index, mount in enumerate(self.Mounts):
            context["prefix"] = mount.Name
            mount.produce(context.copy(), tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=FabSolid.produce('{self.Name}')")
        return ()


# TestSolid:
@dataclass
class TestSolid(FabSolid):
    """TestSolid: A test solid to exercise FabSolid code."""

    _Zilch: int = 0  # Dataclasses without a field are a no-no:

    # TestSolid.__post_init__():
    def __post_init__(self) -> None:
        """Initialize TestSolid."""

        # Create *top_part*:
        z_offset: float = 0.0
        pad_fillet_radius: float = 10.0
        pad_polygon: FabPolygon = FabPolygon("Pad", (
            (Vector(-40, -60, z_offset), pad_fillet_radius),  # SW
            (Vector(40, -60, z_offset), pad_fillet_radius),  # SE
            (Vector(40, 20, z_offset), pad_fillet_radius),  # NE
            (Vector(-40, 20, z_offset), pad_fillet_radius),  # NW
        ))
        pocket_fillet_radius: float = 2.5
        left_pocket: FabPolygon = FabPolygon("LeftPocket", (
            (Vector(-30, -10, z_offset), pocket_fillet_radius),
            (Vector(-10, -10, z_offset), pocket_fillet_radius),
            (Vector(-10, 10, z_offset), pocket_fillet_radius),
            (Vector(-30, 10, z_offset), pocket_fillet_radius),
        ))
        right_pocket: FabPolygon = FabPolygon("RightPocket", (
            (Vector(10, -10, z_offset), pocket_fillet_radius),
            (Vector(30, -10, z_offset), pocket_fillet_radius),
            (Vector(30, 10, z_offset), pocket_fillet_radius),
            (Vector(10, 10, z_offset), pocket_fillet_radius),
        ))
        _ = right_pocket
        right_circle: FabCircle = FabCircle(Vector(20, 0, z_offset), 10)
        center_circle: FabCircle = FabCircle(Vector(0, 0, z_offset), 10)

        contact: Vector = Vector(0, 0, z_offset)
        normal: Vector = Vector(0, 0, 1)
        north: Vector = Vector(0, 1, 0)
        top_operations: Tuple[FabOperation, ...] = (
            FabPad("Pad", pad_polygon, 10.0),
            FabPocket("LeftPocket", left_pocket, 10.0),
            FabPocket("RightPocket", right_circle, 8.0),
            FabHole("CenterHole", center_circle, 5.0),
        )

        top_north_mount: FabMount = FabMount("TopNorth", top_operations, contact, normal, north)
        self.Material = "HDPE"

        self.Color = "purple"
        self.Children = (top_north_mount,)
        super().__post_init__()


# Box:
@dataclass
class Box(FabAssembly):
    """Fab a box.

    Builds a box given a length, width, height, material, thickness and center point"

    Inherieted Attributes:
    * *Name* (str): Box name.
    * Children: (Tuple[FabSolid, ...])  # Filled in by Box.__post_init__()

    Attributes
    * *Length* (float): length in X direction in millimeters.x
    * *Width* (float): width in Y direction in millimeters.
    * *Height* (float): height in Z direction in millimeters.
    * *Thickness* (float): Material thickness in millimeters.
    * *Material* (str): Material to use.
    * *Center* (Vector): Center of Box.
    * *Screws* (Tuple[FabJoin, ...]): The screw to hold the Box together.

    """

    Length: float = 150.0
    Width: float = 100.0
    Height: float = 50.0
    Thickness: float = 5.0
    Material: str = "HDPE"
    Center: Vector = Vector()

    # Box.__post_init__():
    def __post_init__(self) -> None:
        """Consturct the the Box."""

        super().__post_init__()

        # Extract basic dimensions and associated constants:
        center: Vector = self.Center
        dx: float = self.Length
        dy: float = self.Width
        dz: float = self.Height
        dw: float = self.Thickness
        dx2: float = dx / 2.0
        dy2: float = dy / 2.0
        dz2: float = dz / 2.0
        dw2: float = dw / 2.0
        sd: float = 3.0 * dw  # Screw Depth
        corner_radius: float = 3.0

        # Create some *direction* Vector's:
        east_axis: Vector = Vector(1, 0, 0)
        north_axis: Vector = Vector(0, 1, 0)
        top_axis: Vector = Vector(0, 0, 1)
        west_axis: Vector = -east_axis
        south_axis: Vector = -north_axis
        bottom_axis: Vector = -top_axis

        fasten: FabFasten = FabFasten("M3x0.5-FH", "M3x0.5", ())

        # There are 6 box Solid's -- top/bottom, north/south, and east/west.
        # The Solid's are screwed together on along some, but all of the edges:
        # Define the screws first:

        # Top/North edge screws:
        tbo: float = 3.0 * dw  # Top/Bottom Offset from side.
        tnw_head: Vector = center + Vector(dx2 - tbo, dy2 - dw2, dz2)
        tne_head: Vector = center + Vector(-dx2 + tbo, dy2 - dw2, dz2)
        tn_screws: Tuple[FabJoin, ...] = (
            FabJoin("TN-W", fasten, tnw_head, tnw_head - sd * top_axis),
            FabJoin("TN-E", fasten, tne_head, tne_head - sd * top_axis),
        )

        # Top/South edge screws:
        tsw_head: Vector = center + Vector(dx2 - tbo, -dy2 + dw2, dz2)
        tse_head: Vector = center + Vector(-dx2 + tbo, -dy2 + dw2, dz2)
        ts_screws: Tuple[FabJoin, ...] = (
            FabJoin("TN-W", fasten, tsw_head, tsw_head - sd * top_axis),
            FabJoin("TN-E", fasten, tse_head, tse_head - sd * top_axis),
        )

        # Bottom/North edge screws:
        bnw_head: Vector = center + Vector(dx2 - tbo, -dy2 + dw2, -dz2)
        bne_head: Vector = center + Vector(-dx2 + tbo, -dy2 + dw2, -dz2)
        bn_screws: Tuple[FabJoin, ...] = (
            FabJoin("TN-W", fasten, bnw_head, bnw_head - sd * bottom_axis),
            FabJoin("TN-E", fasten, bne_head, bne_head - sd * bottom_axis),
        )

        # Bottom/South edge screws:
        bsw_head: Vector = center + Vector(dx2 - tbo, dy2 - dw2, -dz2)
        bse_head: Vector = center + Vector(-dx2 + tbo, dy2 - dw2, -dz2)
        bs_screws: Tuple[FabJoin, ...] = (
            FabJoin("TN-W", fasten, bsw_head, bsw_head - sd * bottom_axis),
            FabJoin("TN-E", fasten, bse_head, bse_head - sd * bottom_axis),
        )

        # Do the *top_solid*:
        Corner = Tuple[Vector, float]
        top_corners: Tuple[Corner, ...] = (
            (center + Vector(dx2, dy2, dz2), corner_radius),  # TNE
            (center + Vector(-dx2, dy2, dz2), corner_radius),  # TNW
            (center + Vector(-dx2, -dy2, dz2), corner_radius),  # TSW
            (center + Vector(dx2, -dy2, dz2), corner_radius),  # TSE
        )
        top_polygon: FabPolygon = FabPolygon("Top", top_corners)
        top_operations: Tuple[FabOperation, ...] = (
            FabPad("Pad", top_polygon, dw),
            FabClose("TScrews", tn_screws + ts_screws, dw),
        )
        top_mount: FabMount = FabMount(
            "TopNorth", top_operations,
            center + Vector(0, 0, dz2), top_axis, north_axis, dw)
        top_solid: FabSolid = FabSolid("Top", (top_mount,), "hdpe", "red")

        # Do the *bottom_solid*:
        bottom_corners: Tuple[Corner, ...] = (
            (center + Vector(dx2, dy2, -dz2), corner_radius),  # BNE
            (center + Vector(-dx2, dy2, -dz2), corner_radius),  # BNW
            (center + Vector(-dx2, -dy2, -dz2), corner_radius),  # BSW
            (center + Vector(dx2, -dy2, -dz2), corner_radius),  # BSE
        )
        bottom_polygon: FabPolygon = FabPolygon("Bottom", bottom_corners)
        bottom_operations: Tuple[FabOperation, ...] = (
            FabPad("Pad", bottom_polygon, dw),
            FabClose("BScrews", bn_screws + bs_screws, dw),
        )
        bottom_mount: FabMount = FabMount(
            "BottomNorth", bottom_operations,
            center + Vector(0, 0, -dz2), bottom_axis, north_axis, dw)
        bottom_solid: FabSolid = FabSolid("Bottom", (bottom_mount,), "hdpe", "red")

        # The North (and South) side has 4 additional screws -- two that attach to the
        # East side and two that attach to the West side.  In addition, each North and
        # South side requires two addtional mounts to drill the holes that attach to the
        # top and bottom.  Define the screws first, then define the sides and mounts.

        # North East edge screws:
        nso: float = 3.0 * dw  # North/South Offset from Top/Bottom.
        net_head: Vector = center + Vector(dx2 - dw2, dy2, dz2 - nso)
        neb_head: Vector = center + Vector(dx2 - dw2, dy2, -dz2 + nso)
        ne_screws: Tuple[FabJoin, ...] = (
            FabJoin("NE-T", fasten, net_head, net_head - sd * north_axis),
            FabJoin("NE-B", fasten, neb_head, neb_head - sd * north_axis),
        )

        # North West edge screws:
        nwt_head: Vector = center + Vector(-dx2 + dw2, dy2, dz2 - nso)
        nwb_head: Vector = center + Vector(-dx2 + dw2, dy2, -dz2 + nso)
        nw_screws: Tuple[FabJoin, ...] = (
            FabJoin("NW-T", fasten, nwt_head, nwt_head - sd * north_axis),
            FabJoin("NW-B", fasten, nwb_head, nwb_head - sd * north_axis),
        )

        # South East edge screws:
        set_head: Vector = center + Vector(dx2 - dw2, -dy2, dz2 - nso)
        seb_head: Vector = center + Vector(dx2 - dw2, -dy2, -dz2 + nso)
        se_screws: Tuple[FabJoin, ...] = (
            FabJoin("SE-T", fasten, set_head, set_head - sd * south_axis),
            FabJoin("TT-B", fasten, seb_head, seb_head - sd * south_axis),
        )

        # South West edge screws:
        swt_head: Vector = center + Vector(-dx2 + dw2, -dy2, dz2 - nso)
        swb_head: Vector = center + Vector(-dx2 + dw2, -dy2, -dz2 + nso)
        sw_screws: Tuple[FabJoin, ...] = (
            FabJoin("SW-W", fasten, swt_head, swt_head - sd * south_axis),
            FabJoin("SW-E", fasten, swb_head, swb_head - sd * south_axis),
        )

        # Do the *north_mount* first:
        north_corners: Tuple[Corner, ...] = (
            (center + Vector(dx2, dy2, dz2 - dw), corner_radius),  # TNE
            (center + Vector(-dx2, dy2, dz2 - dw), corner_radius),  # TNW
            (center + Vector(-dx2, dy2, -dz2 + dw), corner_radius),  # BNW
            (center + Vector(dx2, dy2, -dz2 + dw), corner_radius),  # BNE
        )
        north_polygon: FabPolygon = FabPolygon("North", north_corners)
        north_operations: Tuple[FabOperation, ...] = (
            FabPad("Pad", north_polygon, dw),
            FabClose("NScrews", ne_screws + nw_screws, dw),
        )
        north_mount: FabMount = FabMount(
            "NorthMount", north_operations, center + Vector(0, dy2, 0),
            north_axis, bottom_axis, dw)

        # Do the *north_top_mount* second:
        north_top_operations: Tuple[FabOperation, ...] = (
            FabThread("NScrews", tn_screws, dy),
        )
        north_top_mount: FabMount = FabMount(
            "NorthTopMount", north_top_operations, center + Vector(0, 0, dz2 - dw2),
            top_axis, north_axis, dz - 2 * dw)

        # Do the *north_top_mount* second:
        north_bottom_operations: Tuple[FabOperation, ...] = (
            FabThread("NScrews", bn_screws, dy),
        )
        north_bottom_mount: FabMount = FabMount(
            "NorthBottomMount", north_bottom_operations, center + Vector(0, 0, -dx2 + dw2),
            bottom_axis, north_axis, dz - 2 * dw)

        # Do the *north_solid*:
        north_solid: FabSolid = FabSolid(
            "North",
            (north_mount, north_top_mount, north_bottom_mount), "hdpe", "green")

        # Do the *south_solid*:
        south_corners: Tuple[Corner, ...] = (
            (center + Vector(dx2, -dy2, dz2 - dw), corner_radius),  # TSE
            (center + Vector(-dx2, -dy2, dz2 - dw), corner_radius),  # TSW
            (center + Vector(-dx2, -dy2, -dz2 + dw), corner_radius),  # BSW
            (center + Vector(dx2, -dy2, -dz2 + dw), corner_radius),  # BSE
        )

        # Do the *south_mount*:
        south_polygon: FabPolygon = FabPolygon("South", south_corners)
        south_operations: Tuple[FabOperation, ...] = (
            FabPad("Pad", south_polygon, dw),
            FabClose("SScrews", se_screws + sw_screws, dw),
        )
        south_mount: FabMount = FabMount(
            "SouthBottom", south_operations, center + Vector(0, -dy2, 0),
            south_axis, bottom_axis, dw)

        south_solid: FabSolid = FabSolid(
            "South",
            (south_mount,),
            "hdpe", "green")

        if False:
            # Do the *west_solid*:
            west_corners: Tuple[Corner, ...] = (
                (center + Vector(-dx2, dy2 - dw, dz2 - dw), corner_radius),  # TNW
                (center + Vector(-dx2, -dy2 + dw, dz2 - dw), corner_radius),  # TSW
                (center + Vector(-dx2, -dy2 + dw, -dz2 + dw), corner_radius),  # BSW
                (center + Vector(-dx2, dy2 - dw, -dz2 + dw), corner_radius),  # BNW
            )
            west_polygon: FabPolygon = FabPolygon("West", west_corners)
            west_operations: Tuple[FabOperation, ...] = (
                FabPad("Pad", west_polygon, dw),
            )
            west_mount: FabMount = FabMount(
                "WestNorth", west_operations, center + Vector(-dx2, 0, 0), west_axis, north_axis)
            west_solid: FabSolid = FabSolid("West", (west_mount,), "hdpe", "blue")
            _ = west_solid

            # Do the *east_solid*:
            east_corners: Tuple[Corner, ...] = (
                (center + Vector(dx2, dy2 - dw, dz2 - dw), corner_radius),  # TNE
                (center + Vector(dx2, -dy2 + dw, dz2 - dw), corner_radius),  # TSE
                (center + Vector(dx2, -dy2 + dw, -dz2 + dw), corner_radius),  # BSE
                (center + Vector(dx2, dy2 - dw, -dz2 + dw), corner_radius),  # BNE
            )
            east_polygon: FabPolygon = FabPolygon("East", east_corners)
            east_operations: Tuple[FabOperation, ...] = (
                FabPad("Pad", east_polygon, dw),
            )
            east_mount: FabMount = FabMount(
                "EastNorth", east_operations, center + Vector(dx2, 0, 0), east_axis, north_axis)
            east_solid: FabSolid = FabSolid("East", (east_mount,), "hdpe", "blue")
            _ = east_solid

        # Load up the FabSolid's:
        self.Children = (
            top_solid, bottom_solid,
            north_solid, south_solid,
            # east_solid, west_solid
        )

    # Box.configure():
    def configure(self, tracing: str = "") -> None:
        """Compute a box."""
        if tracing:
            print(f"{tracing}<=>Box.configure()")
        self.configurations_append(["Length", "Width", "Height", "Thickness", "Center"])


def main() -> None:
    """Run main program."""
    # Create the models:
    # test_solid: TestSolid = TestSolid("TestSolid")
    box: Box = Box("Box", Center=Vector())  # 0, 100.0, 0.0))
    solids: Tuple[Union[FabSolid, FabAssembly], ...] = (box, )  # , test_solid)
    model_file: FabFile = FabFile("Test", solids, Path("/tmp/test.fcstd"))
    root: FabRoot = FabRoot("Root", (model_file,))
    root.run(tracing="")


# TODO: Move this to FabNode class and switch to using a *context*.
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


if __name__ == "__main__":
    main()
