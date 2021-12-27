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
from typing import Any, cast, Dict, List, Optional, Set, Tuple, Union
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

# FabFile:
@dataclass
class FabFile(FabInterior):
    """FabFile: Represents a FreeCAD document file."""

    # Name: str
    # Parts: Tuple["FabSolid", ...]
    FilePath: Path = Path("bogus")
    # TODO define the actual attributes here:

    # FabFile.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the AppDocument."""
        part: FabSolid
        part_names: Set[str] = set()
        if len(self.Parts) == 0:
            raise ValueError("At least one FabSolid needs to be specified")
        for part in self.Parts:
            if not isinstance(part, FabSolid):
                raise ValueError(f"{part} is not a FabSolid")
            if part.Name in part_names:
                raise ValueError(f"There are two or more Part's with the same name '{part.Name}'")
            part_names.add(part.Name)

        self.GeometryGroup = cast(App.DocumentObjectGroup, None)
        self.Part = cast(FabSolid, None)
        self.Body = cast(Part.BodyBase, None)
        self.Mount = cast("FabMount", None)
        self.DatumPlane = cast("Part.Geometry", None)

        stem: str = self.FilePath.stem
        self.AppDocument = App.newDocument(stem)
        assert isinstance(self.AppDocument, App.Document)
        self.GuiDocument = None
        if App.GuiUp:
            self.GuiDocument = Gui.getDocument(stem)  # pragma: no unit cover
            assert isinstance(self.GuiDocument, Gui.Document)

    @property
    def Parts(self) -> Tuple["FabSolid", ...]:
        """Return the children FabSolid's."""
        return cast(Tuple[FabSolid, ...], self.Children)

    # FabFile.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Produce all of the FabSolid's."""
        if tracing:
            print("=>{tracing}=>FabFile.produce('{self.Name}', *)")
        part: "FabSolid"
        app_document: App.Document = self.AppDocument
        context["app_document"] = app_document
        if App.GuiUp:
            context["gui_document"] = self.GuiDocument
        for part in self.Parts:
            self.Part = part
            part.produce(context.copy())
            self.Part = cast(FabSolid, None)
        app_document.recompute()
        app_document.saveAs(str(self.FilePath))
        if tracing:
            print("<={tracing}=>FabFile.produce('{self.Name}', *)")
        return ()

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
        context["app_document"] = fab_file.AppDocument
        if App.GuiUp:
            context["gui_document"] = fab_file.GuiDocument
        fab_file.produce(context.copy())
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
                             prefix: str) -> Part.Feature:
        """Produce the shape binder needed for the pad, pocket, hole, ... operations."""
        body = cast(Part.BodyBase, context["body"])

        shape_binder: Part.Feature = body.newObject(
            "PartDesign::SubShapeBinder", f"{prefix}_Binder")
        assert isinstance(shape_binder, Part.Feature)
        shape_binder.Support = (part_geometries)
        shape_binder.Visibility = False
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
        if tracing:
            print("{tracing}=>Fab.produce('{self.Name}')")
        # Extract the *part_geometries* and create the assocated *shape_binder*:
        prefix = cast(str, context["prefix"])
        next_prefix: str = f"{prefix}_{self.Name}"
        part_geometries: Tuple[Part.Part2DObject, ...]
        part_geometries = self.Geometry.produce(context.copy(), next_prefix)
        shape_binder: Part.Feature = self.produce_shape_binder(
            context.copy(), part_geometries, next_prefix)
        assert isinstance(shape_binder, Part.Feature)
        shape_binder.Visibility = False

        # Extract *body* and *normal* from *context*:
        body = cast(Part.BodyBase, context["body"])
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
            print("{tracing}<=Fab.produce('{self.Name}')")
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
        body = cast(Part.BodyBase, context["body"])
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


_HoleKey = Tuple[str, str, str, float, bool]


# _Hole:
@dataclass(order=True)
class _Hole(object):
    """_Hole: FabDrill helper class that represents a hole."""

    Size: str  # Essentially the diameter
    Profile: str  # Essentially the fastener thread pitch
    Kind: str  # "thread", "close", or "loose"
    Depth: float  # The depth of the drill hole
    IsTop: bool  # Is the top of the fastener
    Center: Vector = field(compare=False)  # The Center (start point) of the drill
    Join: FabJoin = field(compare=False)  # The associated FabJoin

    # _Hole.Key():
    @property
    def Key(self) -> _HoleKey:
        """Return a Hole key."""
        return (self.Size, self.Profile, self.Kind, self.Depth, self.IsTop)


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
        if tracing:
            print("{tracing}=>FabDrill.produce('{self.Name}')")

        # Grab mount information from *context*:
        prefix = cast(str, context["prefix"])
        # mount_name = cast(str, context["mount_name"])
        mount_contact = cast(Vector, context["mount_contact"])
        mount_normal = cast(Vector, context["mount_normal"])
        bottom_depth = cast(float, context["mount_depth"])
        assert abs(mount_normal.Length - 1.0) < EPSILON, (
            "{self.FullPath}: Mount normal is not of length 1")

        # Some commonly used variables:
        depth: float
        hole: _Hole
        is_top: bool
        join: FabJoin
        fasten: FabFasten

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
            hole = _Hole(fasten.Size, fasten.Profile, kind, depth, is_top, top, join)
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
            size: str
            profile: str
            size, profile, kind, depth, is_top = key
            diameter: float = fasten.get_diameter(kind)

            # Construct the "drawing"
            part_geometries: List[Part.Part2DObject] = []
            hole_group: List[_Hole] = hole_groups[key]
            for hole in hole_group:
                # Construct the drawing"
                # Sanity check that each *fasten* object matches the *key*.
                join = hole.Join
                fasten = join.Fasten
                assert fasten.Size == size and fasten.Profile == profile and (
                    self.get_kind() == kind and hole.Depth == depth and hole.IsTop == is_top)
                center: Vector = hole.Center
                circle: FabCircle = FabCircle(center, diameter)
                part_geometries.append(circle)

            # Create the *shape_binder*:
            next_prefix = f"{prefix}.DrillCircle{index:03d}"
            shape_binder: Part.Feature = self.produce_shape_binder(
                context.copy(), tuple(part_geometries), next_prefix)
            assert isinstance(shape_binder, Part.Feature)
            body = cast(Part.BodyBase, context["body"])

            # TODO: fill in actual values for Hole.
            # Create the *pocket* and upstate the view provider for GUI mode:
            part_hole: Part.Feature = body.newObject("PartDesign::Hole", f"{next_prefix}_Hole")
            assert isinstance(part_hole, Part.Feature)
            part_hole.Profile = shape_binder
            part_hole.Diameter = diameter
            part_hole.Depth = depth
            part_hole.UpToFace = None
            part_hole.Reversed = 0
            part_hole.Midplane = 0

            # Fill in other fields for the top mount.
            if is_top:
                assert False, "Fill in other fields."

            # For the GUI, update the view provider:
            self._viewer_update(body, part_hole)

        if tracing:
            print("{tracing}<=FabDrill.produce('{self.Name}')")
        return tuple(errors)


# FabThread:
@dataclass
class FabThread(FabDrill):
    """Drill and thread FabJoin's."""

    def get_diameter_kind(self) -> str:
        """Return a thread diameter kind."""
        return "thread"


# FabClose:
@dataclass
class FabClose(FabDrill):
    """Drill a close a FabJoin's."""

    def get_diameter_kind(self) -> str:
        """Return a thread diameter kind."""
        return "close"


# FabLoose:
@dataclass
class FabLoose(FabDrill):
    """Drill Loose FabJoin's."""

    def get_diameter_kind(self) -> str:
        """Return a thread diameter kind."""
        return "close"


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
        body = cast(Part.BodyBase, context["body"])

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
        # This is where the math for FreeCAD DatumPlane's is discussed.
        #
        # Here is the notation used in this comment:
        #
        # Scalars: a, b, c, ...  (i.e. a lower case letter)
        # Vectors: P, N, Pa, ... (i.e. an upper case letter with optional suffix letter)
        # Magnitude: |N|, |P|, ... (i.e. a vector with vertical bars on each side.)
        # Unit Normal: <N>, <P>, ... (i.e. a vector enclosed in angle brakcets < ...>).)
        # Dot Product: N . P (i.e. two vectors separated by a period.)
        # Vector scaling: s * V (i.e. a scalar times a vector.)
        # Note that:  |N| * <N> = N
        #
        # The section on Hessian normal plane representation from:
        # * [MathWorld Planes](https://mathworld.wolfram.com/Plane.html)
        # is worth reading.
        #
        # The base coordinate system ('b' suffix) has an origin (Ob=(0,0,0)), X axis (<Xb>=(1,0,0)),
        # Y axis (<Yb>=(0,1,0), and Z axis (<Zb>=(0,0,1).
        #
        # A datum plane specifies a new coordinate system ('d' suffix) that has an Origin (Od),
        # X axis (<Xd>), Y axis (<Yd>), and Z axis (<Zd>).
        #
        # The math for computing these values is discussed immediately below:
        #
        # A plane is specified by a contact point Pd on the plane and a normal Nd to the plane.
        # The normal can be at any point on the plane.
        #
        # The datum plane origin is computed as:
        #
        #     Od = Os + d * <Nd>
        #
        # where d is a signed distance computed as:
        #
        #     d = - (<Nd> . Pd)

        # Compute *rotation* from <Zb> to <Nd>:
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabMount.produce('{self.Name}')")
        contact: Vector = self.Contact  # Pd
        normal: Vector = self.Normal  # <Nd>
        distance: float = normal.dot(contact)  # d = - (<Nd> . Pd)
        origin: Vector = normal * distance  # Od = Os + d * <Nd>
        z_axis: Vector = Vector(0, 0, 1)  # <Zb>
        rotation: Rotation = Rotation(z_axis, normal)  # Rotation from <Zb> to <Nd>.

        if tracing:
            print(f"{tracing}{contact=}")
            print(f"{tracing}{normal=}")
            print(f"{tracing}{origin=}")
            print(f"{tracing}{rotation=}")

        # Create, save and return the *datum_plane*:
        body = cast(Part.BodyBase, context["body"])
        datum_plane: Part.Geometry = body.newObject("PartDesign::Plane", f"{self.Name}_Datum_Plane")
        # visibility_set(datum_plane, False)
        datum_plane.Visibility = False
        # xy_plane: App.GeoGeometry = body.getObject("XY_Plane")
        placement: Placement = Placement(origin, rotation)
        if tracing:
            print(f"{tracing}{placement=}")
        datum_plane.AttachmentOffset = Placement()  # Null placement:  Use Placement instead
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
        context["mount_datum_plane"] = datum_plane
        context["mount_normal"] = self.Normal
        context["mount_contact"] = self.Contact

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

    Attributes:
    * *Name* (str): The model name.
    * *Mounts* (Tuple[FabMount, ...]): The various model mounts to use to construct the part.
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

        # Do consistency checking and extract the *pads* for guessing maximum depth later on.
        mounts: Tuple[FabMount, ...] = self.Mounts
        if not mounts:
            raise ValueError("{self.FullPath}: No FabMount's specified for Part 'self.Name'.")
        pads: List[Optional[FabPad]] = []
        index: int
        mount: FabMount
        for index, mount in enumerate(mounts):
            first_operation: FabOperation = mount.Operations[0]
            if not isinstance(mount, FabMount):
                raise ValueError(
                    f"{self.FullPath}: {mount.FullPath} is {type(mount)}, not a FabMount.")
            pads.append(first_operation if isinstance(first_operation, FabPad) else None)
            if index == 0 and not isinstance(first_operation, FabPad):
                raise ValueError(
                    f"{self.FullPath}: First operation in {mount.FullPath} is "
                    f"{type(first_operation)}, not ModPad")

        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        object.__setattr__(self, "_pads", pads)

    @property
    def Mounts(self) -> Tuple[FabMount, ...]:
        """Return children solids."""
        return cast(Tuple[FabMount], self.Children)

    # FabSolid.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Produce the FabSolid."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabSolid.produce('{self.Name}')")
        app_document = cast(App.Document, context["app_document"])

        # Create the *geometry_group* that contains all of the 2D geometry (line, arc, circle.):
        geometry_group: App.DocumentObjectGroup = app_document.addObject(
            "App::DocumentObjectGroup", f"{self.Name}_Geometry")
        geometry_group.Visibility = False
        context["geometry_group"] = geometry_group

        # Create the *body*
        body: Part.BodyBase = app_document.addObject("PartDesign::Body", self.Name)
        context["body"] = body

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
        pads: Tuple[Optional[FabPad], ...] = self._pads
        current_pads: List[FabPad] = []
        index: int
        mount: FabMount
        for index, mount in enumerate(self.Mounts):
            pad: Optional[FabPad] = pads[index]
            if isinstance(pad, FabPad):
                current_pads.append(pad)
            context["prefix"] = mount.Name
            context["current_pads"] = tuple(current_pads)  # Used for estimating depth.
            mount.produce(context.copy(), tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=FabSolid.produce('{self.Name}')")
        return ()


# Box:
@dataclass
class Box(object):
    """Fab a box.

    Builds a box given a length, width, height, material, thickness and center point"

    Attributes:
    * *Name* (str): Box name.
    * *Length* (float): length in X direction in millimeters.
    * *Width* (float): width in Y direction in millimeters.
    * *Height* (float): height in Z direction in millimeters.
    * *Thickness* (float): Material thickness in millimeters.
    * *Material* (str): Material to use.
    * *Center* (Vector): Center of Box.
    * *Screws* (Tuple[FabJoin, ...]): The screw to hold the Box together.

    """

    Name: str
    Length: float
    Width: float
    Height: float
    Thickness: float
    Material: str
    Center: Vector
    Screws: Tuple[FabJoin, ...] = field(init=False, repr=False, default=())

    # Box.compute():
    def compute(self) -> None:
        """Compute a box."""
        pass

    def produce(self) -> Tuple[FabSolid, ...]:
        """Produce a box."""
        dx: float = self.Length
        dy: float = self.Width
        dz: float = self.Height
        dw: float = self.Thickness

        dx2: float = dx / 2.0
        dy2: float = dy / 2.0
        dz2: float = dz / 2.0
        dw2: float = dw / 2.0
        sd: float = 2.0 * dw  # Screw Depth

        corner_radius: float = 3.0

        east_axis: Vector = Vector(1, 0, 0)
        north_axis: Vector = Vector(0, 1, 0)
        top_axis: Vector = Vector(0, 0, 1)
        west_axis: Vector = -east_axis
        south_axis: Vector = -north_axis
        bottom_axis: Vector = -top_axis

        center: Vector = self.Center
        fasten: FabFasten = FabFasten("M3x0.5", FabFasten.ISO_COARSE, FabFasten.M3, ())
        top_north_joins: Tuple[FabJoin, ...] = (
            FabJoin("TN-W", fasten,
                    center + Vector(dx2 - dw2, dy2, dz2),
                    center + Vector(dx2 - dw2, dy2, dz2 - sd)),
            FabJoin("TN-E", fasten,
                    center + Vector(-dx2 + dw2, dy2, dz2),
                    center + Vector(-dx2 + dw2, dy2, dz2 - sd)),
        )
        _ = top_north_joins

        Corners = Tuple[Tuple[Vector, float], ...]
        top_corners: Corners = (
            (center + Vector(dx2, dy2, dz2), corner_radius),  # TNE
            (center + Vector(-dx2, dy2, dz2), corner_radius),  # TNW
            (center + Vector(-dx2, -dy2, dz2), corner_radius),  # TSW
            (center + Vector(dx2, -dy2, dz2), corner_radius),  # TSE
        )
        top_polygon: FabPolygon = FabPolygon("Top", top_corners)
        top_operations: Tuple[FabOperation, ...] = (
            FabPad("Pad", top_polygon, dw),
            # FabDrill("TopNorthHoles", top_north_joins, 10.0)
        )
        top_mount: FabMount = FabMount(
            "TopNorth", top_operations, center + Vector(0, 0, dz2), top_axis, north_axis)
        top_solid: FabSolid = FabSolid("Top", (top_mount,), "hdpe", "red")

        north_corners: Corners = (
            (center + Vector(dx2, dy2, dz2 - dw), corner_radius),  # TNE
            (center + Vector(-dx2, dy2, dz2 - dw), corner_radius),  # TNW
            (center + Vector(-dx2, dy2, -dz2), corner_radius),  # BNW
            (center + Vector(dx2, dy2, -dz2), corner_radius),  # BNE
        )
        north_polygon: FabPolygon = FabPolygon("North", north_corners)
        north_operations: Tuple[FabOperation, ...] = (
            FabPad("Pad", north_polygon, dw),
        )
        north_mount: FabMount = FabMount(
            "NorthBottom", north_operations, center + Vector(0, dy2, 0), north_axis, bottom_axis)
        north_solid: FabSolid = FabSolid("North", (north_mount,), "hdpe", "green")

        west_corners: Corners = (
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

        bottom_corners: Corners = (
            (center + Vector(dx2, dy2 - dw, -dz2), corner_radius),  # BNE
            (center + Vector(-dx2, dy2 - dw, -dz2), corner_radius),  # BNW
            (center + Vector(-dx2, -dy2 + dw, -dz2), corner_radius),  # BSW
            (center + Vector(dx2, -dy2 + dw, -dz2), corner_radius),  # BSE
        )
        bottom_polygon: FabPolygon = FabPolygon("Bottom", bottom_corners)
        bottom_operations: Tuple[FabOperation, ...] = (
            FabPad("Pad", bottom_polygon, dw),
        )
        bottom_mount: FabMount = FabMount(
            "BottomNorth", bottom_operations, center + Vector(0, 0, -dz2), bottom_axis, north_axis)
        bottom_solid: FabSolid = FabSolid("Bottom", (bottom_mount,), "hdpe", "red")

        east_corners: Corners = (
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

        south_corners: Corners = (
            (center + Vector(dx2, -dy2, dz2 - dw), corner_radius),  # TSE
            (center + Vector(-dx2, -dy2, dz2 - dw), corner_radius),  # TSW
            (center + Vector(-dx2, -dy2, -dz2), corner_radius),  # BSW
            (center + Vector(dx2, -dy2, -dz2), corner_radius),  # BSE
        )
        south_polygon: FabPolygon = FabPolygon("South", south_corners)
        south_operations: Tuple[FabOperation, ...] = (
            FabPad("Pad", south_polygon, dw),
        )
        south_mount: FabMount = FabMount(
            "SouthBottom", south_operations, center + Vector(0, -dy2, 0), south_axis, bottom_axis)
        south_solid: FabSolid = FabSolid("South", (south_mount,), "hdpe", "green")

        # hdw: float = dw / 2.0  # Half DW
        # sd: float = 2.0 * dw  # Screw depth
        fasten_profile: FabFasten = FabFasten("M3x.5", FabFasten.ISO_COARSE, FabFasten.M3, ())
        _ = fasten_profile
        return (top_solid, north_solid, west_solid, bottom_solid, east_solid, south_solid)


def main() -> None:
    """Run main program."""
    # Create *top_part*:
    z_offset: float = 40.0
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
        FabPad("Pad", pad_polygon, 50.0),
        FabPocket("LeftPocket", left_pocket, 10.0),
        FabPocket("RightPocket", right_circle, 8.0),
        FabHole("CenterHole", center_circle, 5.0),
    )
    top_north_mount: FabMount = FabMount("TopNorth", top_operations, contact, normal, north)
    top_solid: FabSolid = FabSolid("TopPart", (top_north_mount,), "hdpe", "purple")
    top_solids: Tuple[FabSolid, ...] = (top_solid,)

    # Create *side_part*
    side_radius: float = 3.0
    y_offset: float = -50.0
    side_pad: FabPolygon = FabPolygon("SidePad", (
        (Vector(-50, y_offset, -20), side_radius),
        (Vector(-50, y_offset, 20), side_radius),
        (Vector(50, y_offset, 20), side_radius),
        (Vector(50, y_offset, -20), side_radius),
    ))
    contact = Vector(0, y_offset)
    normal = Vector(0, -1, 0)
    side_operations: Tuple[FabOperation, ...] = (FabPad("Pad", side_pad, 10),)
    side_north_mount: FabMount = FabMount(
        "SideNorth", side_operations, contact, normal, north)
    side_part: FabSolid = FabSolid("SidePart", (side_north_mount,), "hdpe", "green")
    _ = side_part

    center: Vector = Vector(0.0, -250, 0.0)
    box: Box = Box("MyBox", 200, 100, 100, 10, "HDPE", center)
    box.compute()
    box_solids: Tuple[FabSolid, ...] = box.produce()

    all_solids: Tuple[FabSolid, ...] = top_solids + box_solids

    # Create the models:
    model_file: FabFile = FabFile("Test", all_solids, Path("/tmp/test.fcstd"))
    root: FabRoot = FabRoot("Root", (model_file,))
    root.run()

    # with FabFile((top_part, side_part,), Path("/tmp/test.fcstd")) as model_file:
    # with  as model_file:
    #     assert isinstance(model_file.AppDocument, App.Document), (
    #         type(model_file), type(model_file.AppDocument))
    #     context: Dict[str, Any] = {}
    #     context["app_document"] = model_file.AppDocument
    #     if App.GuiUp:
    #        context["gui_document"] = model_file.GuiDocument
    #     model_file.produce(context.copy())


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
    # FabPolygon.unit_test()
    FabCircle._unit_tests()
    # FabFile._unit_tests()  # needs work
    FabPolygon._unit_tests()
    main()
