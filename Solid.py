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
from typing import Any, cast, Dict, List, Optional, Sequence, Set, Tuple, Union
from pathlib import Path


import FreeCAD  # type: ignore
import Part  # type: ignore
import FreeCAD as App  # type: ignore
import FreeCADGui as Gui  # type: ignore

from FreeCAD import Placement, Rotation, Vector
# import Part  # type: ignore

from Geometry import FabCircle, FabGeometry, FabPolygon
from Join import FabFasten, FabJoin
from Tree import FabBox, FabNode
from Utilities import FabColor


@dataclass
# FabGroup:
class FabGroup(FabNode):
    """FabGroup: A named group of FabNode's.

    Inherited Attributes:
    * *Name* (str)
    * *Parent* (FabNode)
    * *Children* (Tuple[FabNode, ...)

    """

    Group: App.DocumentObjectGroup = field(
        init=False, repr=False, default=cast(App.DocumentObjectGroup, None))

    # FabGroup.__post_init__():
    def __post_init__(self):
        """Initialize FabGroup."""
        super().__post_init__()

    # FabGroup.produce():
    def produce(self) -> Tuple[str, ...]:
        """Create the FreeCAD group object."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabGroup({self.Name}).produce()")
        context: Dict[str, Any] = self.Context
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
        for child in self._Children:
            child._Context = context.copy()
            errors.extend(child.produce())
        if tracing:
            print(f"{tracing}<=FabGroup({self.Name}).produce()")
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
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}<=>FabAssembly({self.Name}).__post_init__()")


# FabFile:
@dataclass
class FabFile(FabNode):
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
    _AppDocument: Optional[App.Document] = field(init=False, repr=False)

    # FabFile.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the AppDocument."""

        super().__post_init__()
        self._AppDocument = None
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
        for child in self._Children:
            if not isinstance(child, (FabAssembly, FabGroup, FabSolid)):
                raise RuntimeError(
                    f"{self.FullPath}: {child.FullPath} is not a {type(child)}, "
                    "not FabAssembly/FabGroup/FabSolid")

    # FabFile.produce():
    def produce(self) -> Tuple[str, ...]:
        """Create FabFile document."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabFile.produce('{self.Name}', *)")

        # Create the new *app_document*:
        errors: List[str] = []
        if self.Construct:  # Construct OK
            context: Dict[str, Any] = self.Context
            context_keys: Tuple[str, ...]
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}Before Context: {context_keys}")

            # Create *app_document* and save it away in both *self* and *context*:
            app_document = cast(App.Document, App.newDocument(self.Name))  # Why the cast?
            assert isinstance(app_document, App.Document)  # Just to be sure.
            self._AppDocument = app_document
            context["app_document"] = app_document
            context["parent_object"] = app_document

            # If the GUI is up, get the associated *gui_document* and save it into *context*:
            if App.GuiUp:  # pragma: no unit cover
                gui_document = cast(Gui.Document, Gui.getDocument(self.Name))
                assert isinstance(gui_document, Gui.Document)  # Just to be sure.
                context["gui_document"] = gui_document

            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}After Context: {context_keys}")

        if tracing:
            print(f"{tracing}<=FabFile.produce('{self.Name}', *)")
        return tuple(errors)

    # FabFile.post_produce():
    def post_produce(self) -> Tuple[str, ...]:
        """Close the FabFile."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabFile({self.Name}).post_produce()")

        if self.Construct:  # Construct OK
            # Recompute and save:
            app_document: App.Document = self._AppDocument
            app_document.recompute()
            app_document.saveAs(str(self.FilePath))

        if tracing:
            print(f"{tracing}Saved {self.FilePath}")
            print(f"{tracing}<=FabFile({self.Name}).post_produce()")
        return ()


# FabOperation:
@dataclass
class FabOperation(object):
    """FabOperation: An base class for operations -- FabPad, FabPocket, FabHole, etc.

    All model operations are immutable (i.e. frozen.)
    """
    Name: str

    # FabOperation.__post_init__():
    def __post_init__(self) -> None:
        """Initialize FabOperation."""
        if not FabNode._is_valid_name(self.Name):
            raise RuntimeError(f"FabOperation.__post_init__(): Name '{self.Name}' is not valid.")

    # FabOperation.get_name():
    def get_name(self) -> str:
        """Return FabOperation name."""
        return self.Name

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
        super().__post_init__()
        if not isinstance(self.Geometry, FabGeometry):
            raise RuntimeError(
                f"FabPad.__post_init__({self.Name}):{self.Geometry} is not a FabGeometry")
        if self.Depth <= 0.0:
            raise RuntimeError(f"Depth ({self.Depth}) is not positive.")

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
        super().__post_init__()
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
        super().__post_init__()
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

        # Grab mount information from *context*:
        next_tracing = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabDill.produce({self.Name})")

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
            # The mount specifies a top and bottom mount plane that are supposed to totally enclose
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
            # FreeCAD Vector metheds like to modify Vector contents; force copies beforehand:
            top: Vector = (start + copy).projectToPlane(mount_contact + copy, mount_normal + copy)
            # bottom_contact: Vector = mount_contact - bottom_depth * mount_normal

            # Ensure *start*/*end* line segment is perpendicular to mount planes.
            start_end_normal: Vector = (end - start).normalize()
            start_end_aligned: bool
            if not (close(mount_normal, start_end_normal) or
                    close(mount_normal, -start_end_normal)):
                errors.append(
                    f"FabDrill({self.Name}): Fasten {join.Name} "
                    "is not perpendicular to mount plane")
                continue

            # Compute distances along line from *top* along the *down_normal* direction:
            down_normal: Vector = -mount_normal
            start_distance: float = normal_distance(down_normal, top, start)
            end_distance: float = normal_distance(down_normal, top, end)
            close_distance: float = min(start_distance, end_distance)
            far_distance: float = max(start_distance, end_distance)
            assert close_distance <= far_distance
            if far_distance <= 0.0 or close_distance >= bottom_depth:
                errors.append(f"FabDrill({self.Name}): "
                              f"Fasten {fasten.Name} does not overlap with solid")
                continue
            if close_distance > 0.0:
                errors.append(f"FabDrill({self.Name}): "
                              f"Fasten {fasten.Name} starts below mount plane")
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
                circle: FabCircle = FabCircle(center, mount_normal, diameter)
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
            print(f"{tracing}<=FabDrill({self.Name}).produce()")
        return tuple(errors)


# FabThread:
@dataclass
class FabThread(FabDrill):
    """Drill and thread FabJoin's."""

    # FabThread.__post_init__()
    def __post_init__(self) -> None:
        """Initialize FabThread."""
        super().__post_init__()

    # FabThread.get_kind():
    def get_kind(self) -> str:
        """Return a thread diameter kind."""
        return "thread"


# FabClose:
@dataclass
class FabClose(FabDrill):
    """Drill a close a FabJoin's."""

    # FabClose.__post_init__()
    def __post_init__(self) -> None:
        """Initialize FabCLose."""
        super().__post_init__()

    # FabClose.get_kind():
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
        super().__post_init__()
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
            print("{tracing}=>FabHole({self.Name}).produce()")

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
            print("{tracing}<=FabHole({self.Name}).produce()")
        return ()


# FabMount:
@dataclass
class FabMount(object):
    """FabMount: An operations plane that can be oriented for subsequent machine operations.

    This class basically corresponds to a FreeCad Datum Plane.  It is basically the surface
    to which the 2D FabGeometry's are mapped onto prior to performing each operation.
    This class is immutable (i.e. frozen.)

    Attributes:
    * *Name*: (str): The name of the FabPlane.
    * *Solid*: (FabSolid): The FabSolid to work on.
    * *Contact* (Vector): A point on the plane.
    * *Normal* (Vector): A normal to the plane
    * *Orient* (Vector):
      A vector that is projected onto the plane to specify orientation when mounted.
    * *Depth* (float): The maximum depth limit for all operations.

    """

    _Name: str
    _Solid: "FabSolid"
    _Contact: Vector
    _Normal: Vector
    _Orient: Vector
    _Depth: float
    _Context: Dict[str, Any] = field(init=False, repr=False)
    _Copy: Vector = field(init=False, repr=False)  # Used for making private copies of Vector's
    _Tracing: str = field(init=False, repr=False)

    # FabMount.__post_init__():
    def __post_init__(self) -> None:
        """Verify that FabMount arguments are valid."""

        # No super().__post_init__() because the base class is object.
        solid: "FabSolid" = self._Solid

        tracing: str = solid.Tracing
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).__post_init__()")

        # Do type checking here.
        assert isinstance(self._Name, str)
        assert FabNode._is_valid_name(self.Name)
        assert isinstance(self._Solid, FabSolid)
        assert isinstance(self._Contact, Vector)
        assert isinstance(self._Normal, Vector)
        assert isinstance(self._Orient, Vector)
        assert isinstance(self._Depth, float)

        copy: Vector = Vector()  # Make private copy of Vector's.
        self._Copy = copy
        self._Contact = self._Contact + copy
        self._Normal = self._Normal + copy
        # FreeCAD Vector metheds like to modify Vector contents; force copies beforehand:
        self._Orient = (self._Orient + copy).projectToPlane(
            self._Contact + copy, self._Normal + copy)
        self._Context = {"mount_contact": "bogus"}
        self._Context = {}

        if tracing:
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

    # FabMount.Depth:
    @property
    def Depth(self) -> float:
        """Return the depth."""
        return self._Depth

    # FabMount.Construct:
    @property
    def Construct(self) -> bool:
        """Return whether construction is turned on."""
        return self._Solid.Construct

    # FabMount.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Create the FreeCAD DatumPlane used for the drawing support."""
        if tracing:
            print(f"{tracing}=>FabMount.produce('{self.Name}')")

        if self.Construct:  # Construct OK
            if tracing:
                print(f"{tracing}{sorted(context.keys())=}")
            contact: Vector = self._Contact
            normal: Vector = self._Normal
            z_axis: Vector = Vector(0.0, 0.0, 1.0)
            origin: Vector = Vector()
            # FreeCAD Vector metheds like to modify Vector contents; force copies beforehand:
            copy: Vector = Vector()
            projected_origin: Vector = (origin + copy).projectToPlane(contact + copy, normal + copy)
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
            datum_plane: Part.Geometry = body.newObject(
                "PartDesign::Plane", f"{self.Name}_Datum_Plane")
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
            context["mount_normal"] = self._Normal
            context["mount_contact"] = self._Contact
            context["mount_depth"] = self._Depth
            self._Context = context.copy()

            # Install the FabMount (i.e. *self*) and *datum_plane* into *model_file* prior
            # to recursively performing the *operations*:
            # prefix = cast(str, context["prefix"])
            if tracing:
                print(f"{tracing}<=FabMount.produce('{self.Name}')")
        return ()

    # FabMount.pad():
    def pad(self, name: str, shapes: Union[FabGeometry, Tuple[FabGeometry, ...]],
            depth: float, tracing: str = "") -> None:
        """Perform a pad operation."""
        tracing = self._Solid.Tracing
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).pad('{name}', *)")

        # Figure out the contact
        top_contact: Vector = self._Contact
        copy: Vector = Vector()
        normal: Vector = (self._Normal + copy).normalize()
        bottom_contact: Vector = top_contact - depth * normal

        boxes: List[FabBox] = []
        geometries: Tuple[FabGeometry, ...]
        if isinstance(shapes, FabGeometry):
            geometries = (shapes,)
        else:
            geometries = shapes

        geometry: FabGeometry
        for geometry in geometries:
            boxes.append(geometry.project_to_plane(top_contact, normal).Box)
            boxes.append(geometry.project_to_plane(bottom_contact, normal).Box)
        self._Solid.enclose(boxes)

        errors: List[str] = []
        if self.Construct:
            context: Dict[str, Any] = self._Context.copy()
            context["mount_contact"] = self._Contact
            context["mount_normal"] = self._Normal
            context_keys: Tuple[str, ...]
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}Before Pad Context: {context_keys}")
            assert isinstance(shapes, FabGeometry)
            assert depth > 0.0
            context["prefix"] = name
            full_name: str = f"{self.Name}_{name}"
            fab_pad: FabPad = FabPad(full_name, shapes, depth)
            errors.extend(fab_pad.produce(context.copy(), next_tracing))
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}After Pad Context: {context_keys}")

        if tracing:
            print(f"{tracing}<=FabMount({self.Name}).pad('{name}', *)=>|len(errors)|")

    # FabMount.pocket():
    def pocket(self, name: str, shapes: Union[FabGeometry, Tuple[FabGeometry, ...]],
               depth: float, tracing: str = "") -> None:
        """Perform a pocket operation."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).pocket('{name}', *)")

        errors: List[str] = []
        if self.Construct:   # Construct OK
            context: Dict[str, Any] = self._Context.copy()
            context_keys: Tuple[str, ...]
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}Before Pad Context: {context_keys}")
            assert isinstance(shapes, FabGeometry)
            assert depth > 0.0
            context["prefix"] = name
            full_name: str = f"{self.Name}_{name}"
            fab_pocket: FabPocket = FabPocket(full_name, shapes, depth)
            errors.extend(fab_pocket.produce(context.copy(), next_tracing))
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}After Pad Context: {context_keys}")

        if tracing:
            print(f"{tracing}<=FabMount({self.Name}).pocket('{name}', *)=>|len(errors)|")

    # FabMount.drill_joins():
    def drill_joins(self,
                    joins: Union[FabJoin, Sequence[FabJoin]], tracing: str = "") -> None:
        """Drill some FabJoin's into a FabMount."""
        # Quickly convert a single FabJoin into a tuple:
        if isinstance(joins, FabJoin):
            joins = (joins,)
        # next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).drill_joins(|len(joins)|")

        if self.Construct:
            context: Dict[str, Any] = self._Context.copy()
            context_keys: Tuple[str, ...]
            copy: Vector = Vector()
            # mount_contact: Vector = cast(Vector, context["mount_contact"])
            mount_normal: Vector = (cast(Vector, context["mount_normal"]) + copy).normalize()
            solid: "FabSolid" = self._Solid

            # intersect_joins: List[FabJoin] = []
            for join in joins:
                assert isinstance(join, FabJoin), f"{type(join)} is not a FabJoin"

                if join.normal_aligned(mount_normal):
                    join_start: Vector = join.Start
                    join_end: Vector = join.End
                    intersect: bool
                    trimmed_start: Vector
                    trimmed_end: Vector
                    intersect, trimmed_start, trimmed_end = solid.intersect(join_start, join_end)
                    if intersect:
                        if tracing:
                            print(f"{tracing}>>>>>>>>>>>>>>>>{join.Name} intesects {solid.Name}")

        if tracing:
            print(f"{tracing}<=FabMount({self.Name}).drill_joins(|len(joins)|")


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
    _Mounts: Dict[str, FabMount] = field(init=False, repr=False)

    # FabSolid.__post_init__():
    def __post_init__(self) -> None:
        """Verify FabSolid arguments."""
        super().__post_init__()
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabSolid({self.Name}).__post_init__()")
        # TODO: Do additional type checking here:
        self._Mounts = {}
        if tracing:
            print(f"{tracing}<=FabSolid({self.Name}).__post_init__()")

    @property
    def Construct(self) -> bool:
        """Return the construct mode flag."""
        return self._Root.Construct

    # FabSolid.mount():
    def mount(self, name: str, contact: Vector, normal: Vector, orient: Vector,
              depth: float, tracing: str = "") -> FabMount:
        """Return a new FabMount."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabSolid({self.Name}).mount('{name}', ...)")

        fab_mount: FabMount = FabMount(name, self, contact, normal, orient, depth)
        self._Mounts[name] = fab_mount
        if self.Construct:
            context: Dict[str, Any] = self.Context
            fab_mount.produce(context, tracing=next_tracing)

        if tracing:
            print(f"{tracing}=>FabSolid({self.Name}).mount('{name}', ...)=>{fab_mount}")
        return fab_mount

    # FabSolid.drill_joins():
    def drill_joins(self, joins: Sequence[FabJoin],
                    mounts: Optional[Sequence[FabMount]] = None) -> None:
        """Apply drill FabJoin holes for a FabSolid.

        Iterate pairwise through a sequence of FabJoin's and FabMount's and for each pair
        attempt to drill a bunch the FabJoin holes for the associated FabSolid.  The drill
        operation only occurs if the FabJoin is in alignment with the FabMount normal (in
        either direction) *and* if the FabJoin intersects with the underlying FabSolid;
        otherwise nothing is for that particular FabMount and FabJoin pair.

        Arguments:
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
            print(f"{tracing}=>FabSolid({self.Name}).drill_joins(|{len(joins)}|, *)")

        if self.Construct:
            if not mounts:
                mounts = tuple(self._Mounts.values())
            assert isinstance(mounts, (tuple, list)), mounts
            mount: FabMount
            for mount in mounts:
                assert mount._Solid is self, (
                    f"FabMount({mount.Name}) of FabSolid({mount.Name} can not be "
                    f"used with FabSolid({self.Name})")
                mount.drill_joins(joins, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=FabSolid({self.Name}).drill_joins(|{len(joins)}|, *)")

    # FabSolid.produce():
    def pre_produce(self) -> Tuple[str, ...]:
        """Produce an Empty FabSolid prior to performing operations."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabSolid.pre_produce('{self.Name}')")

        # Only do work in construct mode:
        if self.Construct:
            context: Dict[str, Any] = self.Context
            context_keys: Tuple[str, ...]
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}Before Context: {context_keys=}")

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

            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}After Context: {context_keys=}")

        if tracing:
            print(f"{tracing}<=FabSolid.pre_produce('{self.Name}')")
        return ()


@dataclass
# FabProject:
class FabProject(FabNode):
    """FabProject: The Root mode a FabNode tree."""

    _AllNodes: Tuple[FabNode, ...] = field(init=False, repr=False)
    _Construct: bool = field(init=False, repr=False)

    # FabProject.__post_init__():
    def __post_init__(self) -> None:
        """Process FabRoot."""
        super().__post_init__()
        self._AllNodes = ()
        self._Construct = False

    # FabProject.get_construct():
    def get_construct(self) -> bool:
        """Return the Construct mode.

        The default get_construct() method in FabNode always returns False.  This method
        overrides that method and returns the value of the _Construct field.  This field
        is set to False in phase 1 of the run() method.  It is set to True in phase 2 of
        the run method.

        Many other classes implement a Construct property as follows:

             @property
             def Construct(self) -> bool:
                 return self.SOME_FABNODE._Root.Construct

        which calls this method to get the construct status.  This is a pretty convoluted
        way to get the information, but it works.
        """
        return self._Construct

    # FabProject.new():
    @classmethod
    def new(cls, name: str) -> "FabProject":
        """Create a new root FabProject."""
        # print(f"=>FabProject.new({name}).new()")
        project = cls(name, cast(FabNode, None))  # Magic to create a root FabProject.
        # print(f"<=Project.new({name})=>{project}")
        return project

    # FabRoot.run():
    def run(self) -> None:
        # Shared variables:
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>Project({self.Name}).run()")
        error: str
        errors: List[str]
        index: int
        name: str
        node: FabNode

        # Phase 1: Iterate over tree in constraint mode:
        if tracing:
            print("")
            print(f"{tracing}Project({self.Name}).run(): Phase 1: Constraints")
        previous_constraints: Set[str] = set()
        differences: List[int] = []
        all_nodes: Tuple[FabNode, ...] = self._AllNodes
        reversed_nodes: Tuple[FabNode, ...] = tuple(reversed(all_nodes))
        iteration: int
        for iteration in range(1000):
            errors = []
            current_constraints: Set[str] = set()
            # Update all boxes in bottom-up order:
            for node in reversed_nodes:
                node.enclose(self._Children)
            # Call *produce* in top-down order first.
            for node in all_nodes:
                errors.extend(node.produce())
                attribute: Any
                for name, attribute in node.__dict__.items():
                    if name and name[0].isupper() and (
                            isinstance(attribute, (int, float, str, bool, Vector))):
                        constraint: str = f"{node.FullPath}:{name}:{attribute}"
                        assert constraint not in current_constraints
                        current_constraints.add(constraint)
            difference_constraints: Tuple[str, ...] = (
                tuple(sorted(current_constraints ^ previous_constraints)))
            previous_constraints = current_constraints

            # Figure out if iteration can be stopped:
            difference: int = len(difference_constraints)
            print(f"{tracing}Iteration[{iteration}]: {difference} differences")
            if difference == 0:
                break
            differences.append(difference)
            if len(differences) >= 6 and max(differences[-6:-3]) == max(differences[-3:]):
                print("Differences seem not to be changing:")
                for index, error in enumerate(errors):
                    print("  Error[{index}]: {error}")
                for index, constraint in enumerate(difference_constraints):
                    print("  Constraint[{index}]: {constraint")
                break

        # Phase 2: Run top-down in "construct" mode, where *post_produce*() also gets called:
        self._Construct = True
        if tracing:
            print()
            print(f"{tracing}Project({self.Name}).run(): Phase 2: Construct: {self._Construct=}")

        errors = []
        errors.extend(self._produce_walk())
        if errors:
            print("Construction Errors:")
            # Mypy currently chokes on: `for index, error in enumerate(errors):`
            # with `error: "int" not callable`.  Weird.
            for index in range(len(errors)):
                error = errors[index]
                print(f"  Error[{index}]: {error}")
        if tracing:
            print(f"{tracing}<=Project({self.Name}).run()")

# BoxSide:
@dataclass
class BoxSide(FabSolid):
    """A Box side.

    Inherited Constructor Attributes:
    * *Name* (str): Box name.
    * *Parent* (*FabNode*): The parent container.
    * *Material* (str): The Material to use.
    * *Color* (str): The color to use.

    Additional Constructor Attributes:
    * *Contact* (Vector): The center "top" of the side.
    * *Normal* (Vector): The normal of the side (away from box center).
    * *Orient* (Vector): The orientation vector.
    * *HalfLength* (Vector): A vector of half the length in the length direction
    * *HalfWidth* (Vector): A vector of half the width in the width direction.
    * *Depth* float: Depth of side (opposite direction of *normal*.

    """

    Contact: Vector = Vector()
    Normal: Vector = Vector(0, 0, 1)
    Orient: Vector = Vector(0, 1, 0)
    HalfLength: Vector = Vector(1, 0, 0)
    HalfWidth: Vector = Vector(0, 1, 0)
    Depth: float = 5.0
    Screws: List[FabJoin] = field(init=False, repr=False)

    # BoxSide.__post_init__():
    def __post_init__(self) -> None:
        """Initialize Box Side."""
        super().__post_init__()
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>BoxSide({self.Name}).__post_init__()")
            print(f"{tracing}{self.Contact=}")
            print(f"{tracing}{self.Normal=}")
            print(f"{tracing}{self.Orient=}")
            print(f"{tracing}=>BoxSide({self.Name}).__post_init__()")
        self.Screws = []

    # BoxSide.produce():
    def produce(self) -> Tuple[str, ...]:
        """Produce BoxSide."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>BoxSide({self.Name}).produce()")
        box = cast(Box, self.Up)
        assert isinstance(box, Box)  # Redundant
        fasten: FabFasten = box.Fasten
        screws: List[FabJoin] = self.Screws

        name: str = self.Name
        contact: Vector = self.Contact
        copy: Vector = Vector()
        depth: float = self.Depth
        normal_direction: Vector = (self.Normal + copy).normalize()
        length_direction: Vector = (self.HalfLength + copy).normalize()
        length: float = self.HalfLength.Length
        width_direction: Vector = (self.HalfWidth + copy).normalize()
        width: float = self.HalfWidth.Length

        # Create all of the *screws*:
        del screws[:]
        dlength: float
        dwidth: float
        if name in ("Top", "Bottom", "North", "South"):
            for dlength in (length - 3.0 * depth, length - 3.0 * depth):
                for dwidth in (width - depth / 2.0, width - depth / 2.0):
                    start: Vector = contact + dlength * length_direction + dwidth * width_direction
                    end: Vector = start - (3 * depth) * normal_direction
                    screw: FabJoin = FabJoin(f"{name}Join{len(screws)}", fasten, start, end)
                    screws.append(screw)

        # Extrude the side:
        half_length: Vector = self.HalfLength
        half_width: Vector = self.HalfWidth
        all_screws: Tuple[FabJoin, ...] = box.get_all_screws()
        mount: FabMount = self.mount(f"{name}Mount", contact, self.Normal, self.Orient, depth)
        corners: Tuple[Vector, ...] = (
            contact + half_length + half_width,
            contact + half_length - half_width,
            contact - half_length - half_width,
            contact - half_length + half_width,
        )
        polygon: FabPolygon = FabPolygon(corners)
        mount.pad(f"{name}Pad", polygon, depth)
        self.drill_joins(all_screws)

        if tracing:
            print(f"{tracing}<=BoxSide({self.Name}).produce()")
        return ()

# Box:
@dataclass
class Box(FabAssembly):
    """Fabricate  a box.

    Builds a box given a length, width, height, material, thickness and center point"

    Inherited Constructor Attributes:
    * *Name* (str): Box name.
    * *Parent* (*FabNode*): The parent container.

    Additional Constructor Attributes:
    * *Length* (float): length in X direction in millimeters.x
    * *Width* (float): width in Y direction in millimeters.
    * *Height* (float): height in Z direction in millimeters.
    * *Thickness* (float): Material thickness in millimeters.
    * *Material* (str): Material to use.
    * *Center* (Vector): Center of Box.

    Produced Attributes:
    * *Top* (FabSolid): The box top solid.
    * *Bottom* (FabSolid): The box bottom solid.
    * *North* (FabSolid): The box north solid.
    * *South* (FabSolid): The box south solid.
    * *East* (FabSolid): The box east solid.
    * *West* (FabSolid): The box west solid.
    * *Fasten* (FabFasten): The screw template to use.

    """

    Length: float
    Width: float
    Height: float
    Thickness: float
    Material: str = "HDPE"
    Center: Vector = Vector()

    Top: BoxSide = field(init=False, repr=False)
    Bottom: BoxSide = field(init=False, repr=False)
    North: BoxSide = field(init=False, repr=False)
    South: BoxSide = field(init=False, repr=False)
    East: BoxSide = field(init=False, repr=False)
    West: BoxSide = field(init=False, repr=False)
    Fasten: FabFasten = field(init=False, repr=False)

    # Box.__post_init__():
    def __post_init__(self) -> None:
        """Construct the the Box."""
        super().__post_init__()
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>Box({self.Name}).__post_init__()")

        depth: float = self.Thickness
        material: str = self.Material
        x_axis: Vector = Vector(1, 0, 0)
        y_axis: Vector = Vector(0, 1, 0)
        z_axis: Vector = Vector(0, 0, 1)
        self.Top = BoxSide("Top", self, Normal=z_axis, Orient=y_axis,
                           Depth=depth, Material=material, Color="red")
        self.Bottom = BoxSide("Bottom", self, Normal=-z_axis, Orient=y_axis,
                              Depth=depth, Material=material, Color="green")
        self.North = BoxSide("North", self, Normal=y_axis, Orient=-z_axis,
                             Depth=depth, Material=material, Color="orange")
        self.South = BoxSide("South", self, Normal=-y_axis, Orient=z_axis,
                             Depth=depth, Material=material, Color="yellow")
        self.East = BoxSide("East", self, Normal=x_axis, Orient=y_axis,
                            Depth=depth, Material=material, Color="blue")
        self.West = BoxSide("West", self, Normal=-x_axis, Orient=y_axis,
                            Depth=depth, Material=material, Color="cyan")
        self.Fasten = FabFasten("BoxFasten", "M3x.5", ())  # No options yet.

        if tracing:
            print(f"{tracing}<=Box({self.Name}).__post_init__()")

    # Box.produce():
    def produce(self) -> Tuple[str, ...]:
        """Produce the Box."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>Box({self.Name}.produce())")

        # Extract basic dimensions and associated constants:
        # material: str = self.Material
        center: Vector = self.Center
        dx: float = self.Length
        dy: float = self.Width
        dz: float = self.Height
        dw: float = self.Thickness
        dx2: float = dx / 2.0
        dy2: float = dy / 2.0
        dz2: float = dz / 2.0
        # dw2: float = dw / 2.0
        # sd: float = 3.0 * dw  # Screw Depth
        # corner_radius: float = 3.0

        dxv: Vector = Vector(dx2, 0, 0)
        dyv: Vector = Vector(0, dy2, 0)
        dzv: Vector = Vector(0, 0, dz2)

        # dwxv: Vector = Vector(dw, 0, 0)
        dwyv: Vector = Vector(0, dw, 0)
        dwzv: Vector = Vector(0, 0, dw)

        top: BoxSide = self.Top
        top.Contact = center + dzv
        top.HalfLength = dyv
        top.HalfWidth = dxv

        bottom: BoxSide = self.Bottom
        bottom.Contact = center - dzv
        bottom.HalfLength = dyv
        bottom.HalfWidth = dxv

        north: BoxSide = self.North
        north.Contact = center + dyv
        north.HalfLength = dxv
        north.HalfWidth = dzv - dwzv

        south: BoxSide = self.South
        south.Contact = center - dyv
        south.HalfLength = dxv
        south.HalfWidth = dzv - dwzv

        east: BoxSide = self.East
        east.Contact = center + dxv
        east.HalfLength = dyv - dwyv
        east.HalfWidth = dzv - dwzv

        west: BoxSide = self.West
        west.Contact = center - dxv
        west.HalfLength = dyv - dwyv
        west.HalfWidth = dzv - dwzv

        if tracing:
            print(f"{tracing}<=Box({self.Name}.produce())")
        return ()

    # Box.get_all_screws():
    def get_all_screws(self) -> Tuple[FabJoin, ...]:
        """Return all Box screws."""
        return (
            tuple(self.Top.Screws) +
            tuple(self.Bottom.Screws) +
            tuple(self.North.Screws) +
            tuple(self.South.Screws)
        )


# TestSolid:
@dataclass
class TestSolid(FabSolid):
    """TestSolid: A test solid to exercise FabSolid code."""

    # TestSolid.__post_init__():
    def __post_init__(self) -> None:
        """Initialize TestSolid."""
        super().__post_init__()
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}<=>TestSolid({self.Name}).__post_init__()")

    # TestSolid.produce()
    def produce(self) -> Tuple[str, ...]:
        tracing: str = self.Tracing
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>TestSolid({self.Name}).produce()")

        errors: List[str] = []

        # Create *top_mount*:
        depth: float = 10.0
        depth2: float = depth / 2.0
        if self.Construct:
            origin: Vector = Vector()
            normal: Vector = Vector(0, 0, 1)
            context: Dict[str, Any] = self._Context
            assert isinstance(context, dict)
            context_keys: Tuple[str, ...]
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}Before mount context: {context_keys}")
            top_mount: FabMount = self.mount(
                "TN_Mount", origin, self.T, self.N, depth, tracing=tracing)
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}After mount context: {context_keys}")

            # Perform the first Pad:
            z_offset: float = 0.0
            pad_fillet_radius: float = 10.0
            pad_polygon: FabPolygon = FabPolygon((
                (Vector(-40, -60, z_offset), pad_fillet_radius),  # SW
                (Vector(40, -60, z_offset), pad_fillet_radius),  # SE
                (Vector(40, 20, z_offset), pad_fillet_radius),  # NE
                (Vector(-40, 20, z_offset), pad_fillet_radius),  # NW
            ))
            if tracing:
                print(f"{tracing}]")
                print(f"{tracing}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            top_mount.pad("TN_Pad", pad_polygon, depth, tracing=next_tracing)

            # Perform a pocket:
            pocket_fillet_radius: float = 2.5
            left_polygon: FabPolygon = FabPolygon((
                (Vector(-30, -10, z_offset), pocket_fillet_radius),  # SW
                (Vector(-10, -10, z_offset), pocket_fillet_radius),  # SE
                (Vector(-10, 10, z_offset), pocket_fillet_radius),  # NE
                (Vector(-30, 10, z_offset), pocket_fillet_radius),  # NW
            ))
            top_mount.pocket("LeftPocket", left_polygon, depth)

            right_pocket: FabPolygon = FabPolygon((
                (Vector(10, -10, z_offset), pocket_fillet_radius),  # SW
                (Vector(30, -10, z_offset), pocket_fillet_radius),  # SE
                (Vector(30, 10, z_offset), pocket_fillet_radius),  # NE
                (Vector(10, 10, z_offset), pocket_fillet_radius),  # NW
            ))
            top_mount.pocket("RightPocket", right_pocket, depth2)

            right_circle: FabCircle = FabCircle(Vector(20, 0, z_offset), normal, 10)
            top_mount.pocket("RightCircle", right_circle, depth)

            center_circle: FabCircle = FabCircle(Vector(0, 0, z_offset), normal, 10)
            top_mount.pocket("CenterCircle", center_circle, depth2)

        if tracing:
            print(f"{tracing}<=TestSolid({self.Name}).produce()")
        return tuple(errors)


# TestFile:
@dataclass
class TestFile(FabFile):
    """A Test file."""

    # _TestSolid: TestSolid = field(init=False, repr=False)
    _Box: Box = field(init=False, repr=False)

    # TestFile.__post_init__():
    def __post_init__(self) -> None:
        """Initialize TestFile."""
        super().__post_init__()
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>TestFile({self.Name}.__post_init__()")
        # self._TestSolid = TestSolid("TestSolid", self, "HDPE", "red")
        self._Box = Box("TestBox", self, 200.0, 150.0, 75.0, 6.0, "HDPE", Vector(0, 0, 0))
        if tracing:
            print(f"{tracing}<=TestFile({self.Name}.__post_init__()")


# TestProject:
@dataclass
class TestProject(FabProject):
    """A Test Project."""

    File: FabFile = field(init=False, repr=True)

    # TestProject.__post_init__():
    def __post_init__(self) -> None:
        """Initialize TestProject."""
        super().__post_init__()
        self.set_tracing(" ")
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>TestProject({self.Name}).__post_init__()")

        self.File = TestFile("TestFile", self, Path("/tmp/TestFile.fcstd"))

        if tracing:
            print(f"{tracing}<=TestProject({self.Name}).__post_init__()")

    # TestProject.new():
    @classmethod
    def new(cls, name: str) -> "TestProject":
        """Return a new TestProject properly initializedd"""
        test_project = cls(name, cast(FabNode, None))  # Magic to create a root FabProject.
        return test_project

    # TestProject.Probe():
    def probe(self, label: str) -> None:
        """Print out some probe values."""
        print("================")
        file: FabFile = self.File
        assert isinstance(file, TestFile)
        box: Box = file._Box
        print(f"{label}: {box.North.Normal=}")
        assert False, "Remove debugging probes"


def main() -> None:
    """Run main program."""
    test_project: TestProject = TestProject.new("TestProject")
    test_project.run()

    # Create the models:
    # test_solid: TestSolid = TestSolid("TestSolid")
    # box: Box = Box("Box", Center=Vector())  # 0, 100.0, 0.0))
    # solids: Tuple[Union[FabSolid, FabAssembly], ...] = (box, )  # , test_solid)
    # model_file: FabFile = FabFile("Test", Path("/tmp/test.fcstd"))
    # model_file._Children = solids
    # root: FabRoot = FabRoot("Root")
    # root._Children = (model_file,)
    # root.run(tracing="")


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
