#!/usr/bin/env python3
"""Model: An interface to FreeCAD Sketches."""

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

# [Sketcher Constraint Angle](https://wiki.freecadweb.org/Sketcher_ConstrainAngle)
# [Sketcher Scripting](https://wiki.freecadweb.org/Sketcher_ConstrainAngle)
# [Sketcher Switch Between Multiple Solutions](https://www.youtube.com/watch?v=Q43K23k1noo&t=20s)
# [Sketcher Toggle Constructions](https://wiki.freecadweb.org/Sketcher_ToggleConstruction)

# [Combine Draft and Sketch to simplify Modeling.](https://www.youtube.com/watch?v=lfzGEk727eo)

# Note this code uses nested dataclasses that are frozen.  Computed attributes are tricky.
# See (Set frozen data class files in __post_init__)[https://stackoverflow.com/questions/53756788]

import os
import sys

assert sys.version_info.major == 3  # Python 3.x
assert sys.version_info.minor == 8  # Python 3.8
sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])

from dataclasses import dataclass, field
import math
from typing import Any, cast, List, Optional, Set, Tuple, Union
from pathlib import Path

import FreeCAD  # type: ignore
import Draft  # type: ignore
import Part  # type: ignore
import FreeCAD as App  # type: ignore
import FreeCADGui as Gui  # type: ignore

# from Apex import ApexBox, ApexCheck, vector_fix
from FreeCAD import Placement, Rotation, Vector
# import Part  # type: ignore


# ModelFile
@dataclass
class ModelFile(object):
    """ModelFile: Represents a FreeCAD document file."""

    Parts: Tuple["ModelPart", ...]
    FilePath: Path
    AppDocument: App.Document = field(init=False, repr=False)
    GuiDocument: Optional["Gui.Document"] = field(init=False, default=None, repr=False)
    GeometryGroup: App.DocumentObjectGroup = field(init=False, repr=False)
    Body: Part.BodyBase = field(init=False, repr=False)
    Mount: "ModelMount" = field(init=False, repr=False)
    DatumPlane: "Part.Geometry" = field(init=False, repr=False)

    # ModelFile.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the AppDocument."""
        part: ModelPart
        part_names: Set[str] = set()
        for part in self.Parts:
            if not isinstance(part, ModelPart):
                raise ValueError(f"{part} is not a ModelPart")
            if part.Name in part_names:
                raise ValueError(f"There are two or more Part's with the same name '{part.Name}'")
            part_names.add(part.Name)

        self.GeometryGroup = cast(App.DocumentObjectGroup, None)
        self.Body = cast(Part.BodyBase, None)
        self.Mount = cast("ModelMount", None)
        self.DatumPlane = cast("Part.Geometry", None)

        stem: str = self.FilePath.stem
        self.AppDocument = App.newDocument(stem)

    # ModelFile.__enter__():
    def __enter__(self) -> "ModelFile":
        """Open the ModelFile."""
        return self

    # ModelFile.__exit__():
    def __exit__(self, exec_type, exec_value, exec_table) -> None:
        """Close the ModelFile."""
        if self.AppDocument:
            print(f"saving {self.FilePath}")
            self.AppDocument.recompute()
            self.AppDocument.saveAs(str(self.FilePath))

    # ModelFile.produce():
    def produce(self) -> None:
        """Produce all of the ModelPart's."""
        part: "ModelPart"
        for part in self.Parts:
            part.produce(self)


# _ModelGeometry:
@dataclass(frozen=True)
class _ModelGeometry(object):
    """_ModelGeometry: An Internal base class for _ModelArc, _ModelCircle, and _ModelLine.

    All _ModelGeometry classes are immutable (i.e. frozen.)
    """

    # _ModelGeometry.produce():
    def produce(self, model_file: ModelFile, prefix: str, index: int) -> Part.Part2DObject:
        raise NotImplementedError(f"{type(self)}.produce() is not implemented yet")


# _ModelArc:
@dataclass(frozen=True)
class _ModelArc(_ModelGeometry):
    """_ModelArc: An internal representation an arc geometry.

    Attributes:
    * *Apex* (Vector): The fillet apex point.
    * *Radius* (float): The arc radius in millimeters.
    * *Center* (Vector): The arc center point.
    * *Start* (Vector): The Arc start point.
    * *Middle* (Vector): The Arc midpoint.
    * *Finish* (Vector): The Arc finish point.

    # Old:
    * *StartAngle* (float): The start arc angle in radians.
    * *FinishAngle* (float): The finish arc angle in radiuns.
    * *DeltaAngle* (float):
      The value to add to *StartAngle* to get *FinishAngle* (module 2 radians):

    """

    Apex: Vector
    Radius: float
    Center: Vector
    Start: Vector
    Middle: Vector
    Finish: Vector
    # StartAngle: float
    # FinishAngle: float
    # DeltaAngle: float

    # _ModelArc.produce():
    def produce(self, model_file: ModelFile, prefix: str, index: int) -> Part.Part2DObject:
        """Return line segment after moving it into Geometry group."""
        label: str = f"{prefix}_Arc_{index:03d}"
        placement: Placement = Placement()
        placement.Rotation = model_file.DatumPlane.Placement.Rotation
        # placement.Rotation.Q = (0.0, 0.0, 0.0, 1.0)
        placement.Base = self.Center

        # Create and label *part_arc*:
        # part_arc: Part.Part2DObject = Draft.makeCircle(
        #     self.Radius, placement=placement, face=False,  # face=True,
        #     startangle=math.degrees(self.StartAngle),
        #     endangle=math.degrees(self.StartAngle + self.DeltaAngle),
        #     support=None)
        part_arc: Part.Part2DObject = Draft.make_arc_3points([self.Start, self.Middle, self.Finish])

        assert isinstance(part_arc, Part.Part2DObject)
        part_arc.Label = label

        # Move *part_arc* into *geometry_group*:
        geometry_group: App.DocumentObjectGroup = model_file.GeometryGroup
        assert isinstance(geometry_group, App.DocumentObjectGroup)
        part_arc.adjustRelativeLinks(geometry_group)
        geometry_group.addObject(part_arc)

        return part_arc


@dataclass(frozen=True)
class _ModelCircle(_ModelGeometry):
    """_ModelCircle: An internal representation of a circle geometry.

    Attributes:
    * *Center (Vector): The circle center.
    * *Diameter (float): The circle diameter in millimeters.

    """

    Center: Vector
    Diameter: float

    # _ModelCircle.produce():
    def produce(self, model_file: ModelFile, prefix: str, index: int) -> Part.Part2DObject:
        """Return line segment after moving it into Geometry group."""
        label: str = f"{prefix}_Circle_{index:03d}"
        placement: Placement = Placement()
        placement.Rotation.Q = (0.0, 0.0, 0.0, 1.0)
        placement.Base = self.Center

        # Create and label *part_arc*:
        part_circle: Part.Part2DObject = Draft.makeCircle(
            self.Diameter / 2.0, placement=placement, face=True,
            support=None)
        assert isinstance(part_circle, Part.Part2DObject)
        part_circle.Label = label

        # Move *part_arc* into *geometry_group*:
        geometry_group: App.DocumentObjectGroup = model_file.GeometryGroup
        assert isinstance(geometry_group, App.DocumentObjectGroup)
        part_circle.adjustRelativeLinks(geometry_group)
        geometry_group.addObject(part_circle)

        return part_circle


# _ModelLine:
@dataclass(frozen=True)
class _ModelLine(_ModelGeometry):
    """_ModelLine: An internal representation of a line segment geometry.

    Attributes:
    * *Start (Vector): The line segment start point.
    * *Finish (Vector): The line segment finish point.

    """

    Start: Vector
    Finish: Vector

    # _ModelLine.produce():
    def produce(self, model_file: ModelFile, prefix: str, index: int) -> Part.Part2DObject:
        """Return line segment after moving it into Geometry group."""
        label: str = f"{prefix}_Line_{index:03d}"
        placement: Placement = Placement()
        placement.Rotation.Q = (0.0, 0.0, 0.0, 1.0)
        placement.Base = self.Start

        # Create and label *line_segment*:
        points = [self.Start, self.Finish]
        line_segment: Part.Part2DObject = Draft.makeWire(
            points, placement=placement, closed=False, face=True, support=None)
        assert isinstance(line_segment, Part.Part2DObject)
        line_segment.Label = label

        # Draft.autogroup(line_segment)
        # app_document: App.Document = model_file.AppDocument
        # app_document.recompute()

        # Move *line_segment* into *geometry_group*:
        geometry_group: App.DocumentObjectGroup = model_file.GeometryGroup
        assert isinstance(geometry_group, App.DocumentObjectGroup)
        line_segment.adjustRelativeLinks(geometry_group)
        geometry_group.addObject(line_segment)

        return line_segment


# _ModelFillet:
@dataclass
class _ModelFillet(object):
    """_ModelFillet: An object that represents one fillet of a ModelPolygon.

    Attributes:
    * *Apex* (Vector): The apex corner point for the fillet.
    * *Radius* (float): The fillet radius in millimeters.
    * *Before* (_ModelFillet): The previous _ModelFillet in the ModelPolygon.
    * *After* (_ModelFillet): The next _ModelFillet in the ModelPolygon.
    * *Arc* (Optional[_ModelArc]): The fillet Arc if Radius is non-zero.
    * *Line* (Optional[_ModelLine]): The line that connects to the previous _ModelFillet

    """

    Apex: Vector
    Radius: float
    Before: "_ModelFillet" = field(init=False, repr=False)  # Filled in by __post_init__()
    After: "_ModelFillet" = field(init=False, repr=False)  # Filled in by __post_init__()
    Arc: Optional["_ModelArc"] = field(init=False, default=None)  # Filled in by compute_arcs()
    Line: Optional["_ModelLine"] = field(init=False, default=None)  # Filled in by compute_lines()

    # _ModelFillet.__post_init__():
    def __post_init__(self) -> None:
        """Initialize _ModelFillet."""
        self.Before = self
        self.After = self

    # _ModelFillet.compute_arc():
    def compute_arc(self, tracing: str = "") -> _ModelArc:
        """Return the arc associated with a _ModelFillet with non-zero radius."""
        # A fillet is represented as an arc that traverses a sphere with a specified radius.
        #
        # Each fillet specifies an 3D apex point and a radius.  The this fillet the apex point is
        # X and the radius is r.  Each fillet also has two neighbors on the polygon (called before
        # and after) and each of the respectively have apex points called B and A.  These three
        # points specify line segment XB and XA respectively.  XB and XA also specify a plane
        # called AXB.  The goal is to find a center point C of a sphere of radius r that is on
        # the plane AXB and it tangent to line segment XB and XA.  (If r too large, there is no
        # solution, but the radius check code elsewhere will detect that situation and raise an
        # exception.  The plane AXB slices the sphere into a circle of radius r.  The arc lies
        # on this circle.  The start tangent point S is on the circle on line segment XB.
        # The finish tangent point F is on the circle on line segment XA.  The circle is now
        # cleaved into a smaller arc and larger arc.  The smaller arc is the desired one.
        # The XC line segment from X to C crosses the circle at the arc midpoint M.  The points
        # S, M, and F uniquely specify an arc of radius r in 3D space around the C center point.
        #
        # The crude 2D diagram below shows the basic _ModelFillet geometry:
        #
        #       A
        #       |
        #       |       r
        #       F---------------C
        #       +             / |
        #       |+          /   |
        #       | +       /     |
        #     d | +     /       | r
        #       |  +  /         |
        #       |   M++         |
        #       | /    ++++     |
        #       X----------+++++S----B
        #               d
        #
        # Try to use your imagination that '+' characters represent the arc.
        # Also, note the distances r and d are the same for a 90 degree angle <AXB,
        # but otherwise they are different.
        #
        # The algorithm to compute this is:
        # 1. Compute unit vectors <XB> and <XA> the point from X to A and X to B respectively.
        # 2. Compute center unit vector <XC> that points from X to C.
        # 3. Compute the angle <BXC using a dot product and arc cosine.
        # 4. There is a right triangle /_\SXC, where <XSC is 90 degrees (it is tangent) and
        #    |SC| = r.  The goal is to compute |XS| = d) which the length of the XS line segment.
        #    Using standard triangle formulas, |XS| = d is computed.
        # 5. Using X, d, <XB> and <XA>, both S and F are computed.
        # 6. Given d and r, using the Pythagorean theorem, |XC| is computed
        # 7. Now C is computed using X and <XC> and |XC|.
        # 8. The arc mid-point is computed using X, <XC>, |XC| and r.

        # Step 0: Extract *radius*, *before* (B), *apex* (X) and *after* (A) points:
        radius: float = self.Radius
        before: Vector = self.Before.Apex
        apex: Vector = self.Apex
        after: Vector = self.After.Apex
        if tracing:
            print(f"{tracing}=>_ModelFillet.compute_arc({apex})")
            print(f"{tracing}{radius=} {before=} {apex=} {after=}")

        # Steps 1 and 2: Compute unit vectors <XB>, <XA>, and <XC>
        unit_before: Vector = (before - apex).normalize()  # <XB>
        unit_after: Vector = (after - apex).normalize()  # <XA>
        unit_center: Vector = (unit_before + unit_after).normalize()  # <XC>
        if tracing:
            print(f"{tracing}{unit_before=} {unit_center=} {unit_after=}")

        # Step 3: Compute the angle <BXC> using a dot product and arc cosine:
        # [Dot Product](https://mathworld.wolfram.com/DotProduct.html)
        # X . Y = |X|*|Y|*cos(angle)  => angle = acos( (X . Y) / (|X| * |Y|) )
        # In our case |X| and |Y| are both 1, so we can skip the division.
        center_angle: float = math.acos(unit_center.dot(unit_after))
        if tracing:
            print(f"{tracing}center_angle={math.degrees(center_angle)}")

        # Step 4: Compute *distance* == |XS| == d:
        # [Right Triangle Overview]
        #   (http://www.ambrsoft.com/TrigoCalc/Triangle/BasicLaw/BasicTriangle.htm)
        # We have center *center_angle* (<CXS) and the opposite side is *radius* (r).  We need
        # the *distance* (d) along the lines where the arc circle (radius r) is tangent.
        distance: float = radius / math.tan(center_angle)
        if tracing:
            print(f"{tracing}{distance=}")

        # Step 5: Compute *start* (S) an *finish* (F):
        start: Vector = apex + distance * unit_before
        finish: Vector = apex + distance * unit_after

        # Step 6: Compute the *center_distance* (|XC|) and the *center*:
        # Pythagorean theorem gives us *center_distance* (|XC|)
        center_distance: float = math.sqrt(radius * radius + distance * distance)

        # Step 7: Compute the *center* (C).
        center: Vector = apex + center_distance * unit_center

        # Step 8: Compute the arc *middle* (M):
        middle: Vector = apex + (center_distance - radius) * unit_center

        # Find the smallest angle to take us from *start_angle* to *finish_angle*:
        # [Finding the shortest distance between two angles]
        # (https://stackoverflow.com/questions/28036652/
        #  finding-the-shortest-distance-between-two-angles)
        # The `smallesAngle` Python function was converted from degrees to radians.
        # start_direction: Vector = start - center
        # finish_direction: Vector = finish - center
        # middle: Vector = center + (-unit_center) * radius
        # start_angle: float = math.atan2(start_direction.y, start_direction.x)
        # finish_angle: float = math.atan2(finish_direction.y, finish_direction.x)

        # pi: float = math.pi
        # pi2 = 2.0 * pi  # 360 degrees.
        # Subtract the angles, constraining the value to [0, 2*pi)
        # Python modulo always returns non-negative (i.e. >= 0.0) values:
        # delta_angle: float = (finish_angle - start_angle) % pi2
        # If we are more than 180 we're taking the long way around.
        # Let's instead go in the shorter, negative direction.
        # if delta_angle > pi:
        #    delta_angle = -(pi2 - delta_angle)
        # arc: _ModelArc = _ModelArc(apex, radius, center, start, middle, finish,
        #                            start_angle, finish_angle, delta_angle)
        arc: _ModelArc = _ModelArc(apex, radius, center, start, middle, finish)

        # Do a sanity check:
        # finish_angle = finish_angle % pi2
        # start_plus_delta_angle: float = (start_angle + delta_angle) % pi2
        # assert abs(start_plus_delta_angle - finish_angle) < 1.0e-8, "Delta angle is wrong."

        if tracing:
            print(f"{tracing}<=_ModelFillet.compute_arc({apex})=>{arc}")
        return arc

    # _ModelFillet.get_geometries():
    def get_geometries(self) -> Tuple[_ModelGeometry, ...]:
        geometries: List[_ModelGeometry] = []
        if self.Line:
            geometries.append(self.Line)
        if self.Arc:
            geometries.append(self.Arc)
        return tuple(geometries)


# ModelGeometry:
@dataclass(frozen=True)
class ModelGeometry(object):
    """ModelGeometry: The base class for ModelPolygon and ModelCircle."""

    # ModelGeometry.produce():
    def produce(self, model_context: ModelFile, prefix: str) -> Tuple[Part.Part2DObject, ...]:
        """Produce the necessary FreeCAD objects for the ModelGeometry."""
        raise NotImplementedError(f"{type(self)}.produce() is not implemented")


# ModelCircle:
@dataclass(frozen=True)
class ModelCircle(ModelGeometry):
    """ModelCircle: A circle with a center and a radius.

    Attributes:
    * *Center* (Vector): The circle center.
    * *Diameter* (float): The diameter in radians.

    """

    Center: Vector
    Diameter: float

    # ModelCircle.__post_init__():
    def __post_init__(self) -> None:
        """Make private copy of Center."""
        if self.Diameter <= 0.0:
            raise ValueError(f"Diameter ({self.Diameter}) must be positive.")
        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        copy: Vector = Vector()
        object.__setattr__(self, "Center", self.Center + copy)  # Makes a copy.

    # ModelCircle.produce():
    def produce(self, model_file: ModelFile, prefix: str) -> Tuple[Part.Part2DObject, ...]:
        """Produce the FreeCAD objects needed for ModelPolygon."""
        geometries: Tuple[_ModelGeometry, ...] = self.get_geometries()
        geometry: _ModelGeometry
        index: int
        part_geometries: List[Part.Part2DObject] = []
        for index, geometry in enumerate(geometries):
            part_geometry: Part.Part2DObject = geometry.produce(model_file, prefix, index)
            assert isinstance(part_geometry, Part.Part2DObject)
            part_geometries.append(part_geometry)
        return tuple(part_geometries)

    # ModelCircle.get_geometries():
    def get_geometries(self) -> Tuple[_ModelGeometry, ...]:
        """Return the ModelPolygon lines and arcs."""
        return (_ModelCircle(self.Center, self.Diameter),)


# ModelPolygon:
@dataclass(frozen=True)
class ModelPolygon(ModelGeometry):
    """ModelPolygon: An immutable polygon with rounded corners.

    A ModelPolygon is represented as a sequence of corners (i.e. a Vector) where each corner can
    optionally be filleted with a radius.  In order to make it easier to use, a corner can be
    specified as simple Vector or as a tuple that specifes a Vector and a radius.  The radius
    is in millimeters and can be provided as either Python int or float.  When an explicit
    fillet radius is not specified, higher levels in the software stack will typically substitute
    in a deburr radius for external corners and an interal tool radius for internal corners.
    ModelPolygon's are frozen and can not be modified after creation.

    Example:
         polygon: Model.ModelPolyon = Model.ModelPolygon((
             Vector(-10, -10, 0),  # Lower left (no radius)
             Vector(10, -10, 0),  # Lower right (no radius)
             (Vector(10, 10, 0), 5),  # Upper right (5mm radius)
             (Vector(-0, 10, 0), 5.5),  # Upper right (5.5mm radius)
         ), "Name")

    Attributes:
    * *Name* (str): The name of the polygon.  (Default: "")
    * *Corners* (Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...]):
      See description below for more on corners.

    Raises:
    * ValueError for improper corner specifications.

    """

    Name: str
    Corners: Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...]
    _Fillets: Tuple[_ModelFillet, ...] = field(init=False, repr=False)

    EPSILON = 1.0e-8

    # ModelPolygon.__post_init__():
    def __post_init__(self) -> None:
        """Verify that the corners passed in are correct."""
        corner: Union[Vector, Tuple[Vector, Union[int, float]]]
        fillets: List[_ModelFillet] = []
        fillet: _ModelFillet
        copy: Vector = Vector()  # Vector's are mutable, add *copy* to make a private Vector copy.
        index: int
        for index, corner in enumerate(self.Corners):
            if isinstance(corner, Vector):
                fillet = _ModelFillet(corner + copy, 0.0)
                pass
            elif isinstance(corner, tuple):
                if len(corner) != 2:
                    raise ValueError(f"Polygon Corner[{index}]: {corner} tuple length is not 2")
                if not isinstance(corner[0], Vector):
                    raise ValueError(f"Polygon Corner[{index}]: {corner} first entry is not Vector")
                if not isinstance(corner[1], (int, float)):
                    raise ValueError(f"Polygon Corner[{index}]: {corner} first entry is not number")
                fillet = _ModelFillet(corner[0] + copy, corner[1])
            else:
                raise ValueError(
                    f"Polygon Corner[{index}] is {corner} which is neither a Vector nor "
                    "(Vector, radius) tuple.")
            fillets.append(fillet)
        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        object.__setattr__(self, "_Fillets", tuple(fillets))

        # Double link the fillets and compute the arcs/lines:
        self.double_link()
        self.compute_arcs()
        self.compute_lines()

    # _ModelFillet.double_link():
    def double_link(self) -> None:
        """Double link the _ModelFillet's together."""
        fillets: Tuple[_ModelFillet, ...] = self._Fillets
        size: int = len(fillets)
        fillet: _ModelFillet
        index: int
        for index, fillet in enumerate(fillets):
            fillet.Before = fillets[(index - 1) % size]
            fillet.After = fillets[(index + 1) % size]

    # ModelPolygon.compute_arcs():
    def compute_arcs(self) -> None:
        """Create any Arc's needed for non-zero radius _ModelFillet's."""
        fillet: _ModelFillet
        for fillet in self._Fillets:
            if fillet.Radius > 0.0:
                fillet.Arc = fillet.compute_arc()

    # ModelPolygon.compute_lines():
    def compute_lines(self) -> None:
        """Create Create any Line's need for _ModelFillet's."""
        fillet: _ModelFillet
        for fillet in self._Fillets:
            before: _ModelFillet = fillet.Before
            start: Vector = before.Arc.Finish if before.Arc else before.Apex
            finish: Vector = fillet.Arc.Start if fillet.Arc else fillet.Apex
            if (start - finish).Length > ModelPolygon.EPSILON:
                fillet.Line = _ModelLine(start, finish)

    # ModelPolygon.get_geometries():
    def get_geometries(self) -> Tuple[_ModelGeometry, ...]:
        """Return the ModelPolygon lines and arcs."""
        geometries: List[_ModelGeometry] = []
        fillet: _ModelFillet
        for fillet in self._Fillets:
            geometries.extend(fillet.get_geometries())
        return tuple(geometries)

    # ModelPolygon.produce():
    def produce(self, model_file: ModelFile, prefix: str) -> Tuple[Part.Part2DObject, ...]:
        """Produce the FreeCAD objects needed for ModelPolygon."""
        geometries: Tuple[_ModelGeometry, ...] = self.get_geometries()
        geometry: _ModelGeometry
        index: int
        part_geometries: List[Part.Part2DObject] = []
        for index, geometry in enumerate(geometries):
            part_geometry: Part.Part2DObject = geometry.produce(model_file, prefix, index)
            assert isinstance(part_geometry, Part.Part2DObject)
            part_geometries.append(part_geometry)
        return tuple(part_geometries)

    # ModelPolygon.unit_test():
    @staticmethod
    def unit_test() -> None:
        """Do some unit tests."""
        v1: Vector = Vector(-40, -20, 0)
        v2: Vector = Vector(40, -20, 0)
        v3: Vector = Vector(40, 20, 0)
        v4: Vector = Vector(-40, 20, 0)
        polygon: ModelPolygon = ModelPolygon("TestPolygon", (v1, v2, (v3, 10), v4))

        geometries: Tuple[_ModelGeometry, ...] = polygon.get_geometries()
        index: int
        geometry: _ModelGeometry
        for index, geometry in enumerate(geometries):
            print(f"Geometry[{index}]: {geometry}")

# ModelOperation:
@dataclass(frozen=True)
class ModelOperation(object):
    """ModelOperation: An base class for operations -- ModelPad, ModelPocket, ModelHole, etc.

    All model operations are immutable (i.e. frozen.)
    """

    # ModelOperation.get_name():
    def get_name(self) -> str:
        """Return ModelOperation name."""
        raise NotImplementedError(f"{type(self)}.get_name() is not implemented")

    # ModelOperation.produce():
    def produce(self, model_file: ModelFile, prefix: str) -> None:
        """Return the operation sort key."""
        raise NotImplementedError(f"{type(self)}.produce() is not implemented")

    # ModelOperation.produce_shape_binder():
    def produce_shape_binder(self, model_file: ModelFile,
                             part_geometries: Tuple[Part.Part2DObject, ...],
                             prefix: str) -> Part.Feature:
        """Produce the shape binder needed for the pad, pocket, hole, ... operations."""
        body: Part.BodyBase = model_file.Body
        assert isinstance(body, Part.BodyBase)
        shape_binder: Part.Feature = body.newObject(
            "PartDesign::SubShapeBinder", f"{prefix}_Binder")
        assert isinstance(shape_binder, Part.Feature)
        shape_binder.Support = (part_geometries)
        shape_binder.Visibility = False
        return shape_binder


# ModelPad:
@dataclass(frozen=True)
class ModelPad(ModelOperation):
    """ModelPad: A FreeCAD PartDesign Pad operation.

    Attributes:
        *Name* (str): The operation name.
        *Geometry* (ModelGeometry): The ModlePolygon or ModelCircle to pad with.
        *Depth* (float): The depth to pad to in millimeters.

    """

    Name: str
    Geometry: ModelGeometry
    Depth: float

    # ModelPad.__post_init__():
    def __post_init__(self) -> None:
        """Verify ModelPad values."""
        if not isinstance(self.Geometry, ModelGeometry):
            raise ValueError(f"{self.Geometry} is not a ModelGeometry")
        if self.Depth <= 0.0:
            raise ValueError(f"Depth ({self.Depth}) is not positive.")

    # ModelPad.get_name():
    def get_name(self) -> str:
        """Return ModelPad name."""
        return self.Name

    # ModelPad.produce():
    def produce(self, model_file: ModelFile, prefix: str) -> None:
        """Produce the Pad."""
        # Extract the *part_geometries*:
        next_prefix: str = f"{prefix}_{self.Name}"
        part_geometries: Tuple[Part.Part2DObject, ...] = self.Geometry.produce(model_file,
                                                                               next_prefix)
        shape_binder: Part.Feature = self.produce_shape_binder(
            model_file, part_geometries, next_prefix)
        assert isinstance(shape_binder, Part.Feature)

        # Perform The Pad
        body: Part.BodyBase = model_file.Body
        pad: Part.Feature = body.newObject("PartDesign::Pad", next_prefix)
        assert isinstance(pad, Part.Feature)
        pad.Type = "Length"  # Type in ("Length", "TwoLengths", "UpToLast", "UpToFirst", "UpToFace")
        pad.Profile = shape_binder
        pad.Length = self.Depth
        pad.Length2 = 0  # Only for Type == "TwoLengths"
        pad.UseCustomVector = True
        pad.Direction = model_file.Mount.Normal  # This is probably bogus
        pad.UpToFace = None
        pad.Reversed = True
        pad.Midplane = False
        pad.Offset = 0  # Only for Type in ("UpToLast", "UpToFirst", "UpToFace")
        # Missing pad.Support = datum_plane

        shape_binder.Visibility = False

# ModelPocket:
@dataclass(frozen=True)
class ModelPocket(ModelOperation):
    """ModelPocket: A FreeCAD PartDesign Pocket operation.

    Attributes:
        *Name* (str): The operation name.
        *Geometry* (ModelGeometry): The Polygon or Circle to pocket.
        *Depth* (float): The depth

    """

    Name: str
    Geometry: ModelGeometry
    Depth: float

    # ModelPocket__post_init__():
    def __post_init__(self) -> None:
        """Verify ModelPad values."""
        if not isinstance(self.Geometry, ModelGeometry):
            raise ValueError(f"{self.Geometry} is not a ModelGeometry")
        if self.Depth <= 0.0:
            raise ValueError(f"Depth ({self.Depth}) is not positive.")

    # ModelPocket.get_name():
    def get_name(self) -> str:
        """Return ModelPocket name."""
        return self.Name

    # ModelPocket.produce():
    def produce(self, model_file: ModelFile, prefix: str) -> None:
        """Produce the Pad."""
        # Extract the *part_geometries*:
        next_prefix: str = f"{prefix}_{self.Name}"
        part_geometries: Tuple[Part.Part2DObject, ...] = self.Geometry.produce(model_file,
                                                                               next_prefix)
        # Create the *shape_binder*:
        shape_binder: Part.Featrue = self.produce_shape_binder(
            model_file, part_geometries, next_prefix)
        assert isinstance(shape_binder, Part.Feature)

        # Create the *pocket*:
        body: Part.BodyBase = model_file.Body
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


# ModelHole:
@dataclass(frozen=True)
class ModelHole(ModelOperation):
    """ModelHole: A FreeCAD PartDesign Pocket operation.

    Attributes:
        *Name* (str): The operation name.
        *Circle* (ModelCircle): The Circle to drill.
        *Depth* (float): The depth

    """

    Name: str
    Circle: ModelCircle
    Depth: float

    # ModelHole.__post_init__():
    def __post_init__(self) -> None:
        """Verify ModelPad values."""
        if not isinstance(self.Circle, ModelCircle):
            raise ValueError(f"{self.Geometry} is not a ModelCircle")
        if self.Depth <= 0.0:
            raise ValueError(f"Depth ({self.Depth}) is not positive.")

    # ModelHole.get_name():
    def get_name(self) -> str:
        """Return ModelHole name."""
        return self.Name

    # ModelHole.produce():
    def produce(self, model_file: ModelFile, prefix: str) -> None:
        """Produce the Pad."""
        # Extract the *part_geometries*:
        next_prefix: str = f"{prefix}_{self.Name}"
        part_geometries: Tuple[Part.Part2DObject, ...] = self.Circle.produce(model_file,
                                                                             next_prefix)
        # Create the *shape_binder*:
        shape_binder: Part.Feature = self.produce_shape_binder(
            model_file, part_geometries, next_prefix)
        assert isinstance(shape_binder, Part.Feature)

        # Create the *pocket*:
        body: Part.BodyBase = model_file.Body
        hole: Part.Feature = body.newObject("PartDesign::Hole", f"{next_prefix}_Hole")
        assert isinstance(hole, Part.Feature)
        hole.Profile = shape_binder
        hole.Diameter = self.Circle.Diameter
        hole.Depth = self.Depth
        hole.UpToFace = None
        hole.Reversed = 0
        hole.Midplane = 0


# ModelMount:
@dataclass(frozen=True)
class ModelMount(object):
    """ModelMount: An operations plane that can be oriented for subsequent machine operations.

    This class basically corresponds to a FreeCad Datum Plane.  It is basically the surface
    to which the 2D ModelGeometry's are mapped onto prior to performing each operation.
    This class is immutable (i.e. frozen.)

    Attributes:
    * *Name*: (str): The name of the ModelPlane.
    * *Contact* (Vector): A point on the plane.
    * *Normal* (Vector): A normal to the plane
    * *North* (Vector):
      A vector in the plane that specifies the north direction when mounted  in a machining vice.
    * *Operations* (Tuple[ModelOperation, ...]): The operations to perform.

    """

    Name: str
    Contact: Vector
    Normal: Vector
    North: Vector
    Operations: Tuple[ModelOperation, ...]

    # ModelMount.__post_init__():
    def __post_init__(self) -> None:
        """Verify that ModelMount arguments are valid."""
        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        copy: Vector = Vector()  # Make private copy of Vector's.
        object.__setattr__(self, "Contect", self.Contact + copy)
        object.__setattr__(self, "Normal", self.Normal + copy)
        object.__setattr__(self, "North", self.North + copy)

        # Disallow duplicate operation names:
        operation_names: Set[str] = set()
        operation: ModelOperation
        for operation in self.Operations:
            operation_name: str = operation.get_name()
            if operation_name in operation_names:
                raise ValueError("Mount '{self.Name}' has two operations named '{operation_name}'")
            operation_names.add(operation_name)

    # ModelMount.produce():
    def produce(self, model_file: ModelFile, prefix: str) -> None:
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
        contact: Vector = self.Contact  # Pd
        normal: Vector = self.Normal  # <Nd>
        distance: float = normal.dot(contact)  # d = - (<Nd> . Pd)
        origin: Vector = normal * distance  # Od = Os + d * <Nd>
        z_axis: Vector = Vector(0, 0, 1)  # <Zb>
        rotation: Rotation = Rotation(z_axis, normal)  # Rotation from <Zb> to <Nd>.

        tracing: str = ""
        if tracing:
            print(f"{tracing}{contact=}")
            print(f"{tracing}{normal=}")
            print(f"{tracing}{origin=}")
            print(f"{tracing}{rotation=}")

        # Create, save and return the *datum_plane*:
        body: Part.BodyBase = model_file.Body
        datum_plane: Part.Geometry = body.newObject("PartDesign::Plane", f"{self.Name}_Datum_Plane")
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
        model_file.DatumPlane = datum_plane

        # Turn datum plane visibility off:
        gui_document: Optional[Gui.Document] = model_file.GuiDocument
        if gui_document:  # pragma: no unit cover
            object_name: str = datum_plane.Name
            gui_datum_plane: Any = gui_document.getObject(object_name)
            if gui_datum_plane is not None and hasattr(gui_datum_plane, "Visibility"):
                setattr(gui_datum_plane, "Visibility", False)

        # Install the ModelMount (i.e. *self*) and *datum_plane* into *model_file* prior
        # to recursively performing the *operations*:
        model_file.Mount = self
        model_file.DatumPlane = datum_plane
        operation: ModelOperation
        for operation in self.Operations:
            operation.produce(model_file, prefix)

        # Do not leave behind a stale *datum_plane*:
        model_file.DatumPlane = cast("Part.Geometry", None)

# ModelPart:
@dataclass(frozen=True)
class ModelPart(object):
    """Model: Represents a single part constructed using FreeCAD Part Design paradigm.

    Attributes:
    * *Name*: The model name.
    * *Material*: The material to use.
    * *Color*: The color to use.
    * *Mounts* (Tuple[ModelMount, ...]): The various model mounts to use to construct the part.

    """

    Name: str
    Material: str
    Color: str
    Mounts: Tuple[ModelMount, ...]

    # ModelPart.__post_init__():
    def __post_init__(self) -> None:
        """Verify ModelPart arguments."""
        # Verify that there is only one pad operation and it is the very first one.
        # Also detect duplicate mount names:
        mounts: Tuple[ModelMount, ...] = self.Mounts
        if not mounts:
            raise ValueError("ModelPart.produce(): No mounts specified for Part 'self.Name'.")

        mount_names: Set[str] = set()
        pad_found: bool = False
        mount_index: int
        mount: ModelMount
        for mount_index, mount in enumerate(mounts):
            if not isinstance(mount, ModelMount):
                raise ValueError(f"'{self.Name}': Mount[{mount_index}]: "
                                 f"{type(mount)} is not a ModelMount")
            if mount.Name in mount_names:
                raise ValueError(f"Part '{self.Name}' has two mounts named '{mount.Name}')")
            mount_names.add(mount.Name)

            # Search for Pad operations:
            operations: Tuple[ModelOperation, ...] = mount.Operations
            operation_index: int
            operation: ModelOperation
            for operation_index, operation in enumerate(operations):
                if not isinstance(operation, ModelOperation):
                    raise ValueError(f"'{self.Name}.{mount.Name}']: Operation[{operation_index}]:"
                                     "{type(operaton)} is not a ModelOperation")
                if isinstance(operation, ModelPad):
                    if mount_index != 0 or operation_index != 0:
                        raise ValueError(f"'{self.Name}.{mount.Name}.{operation.Name}':"
                                         "Pad is not at the very beginning.")
                    pad_found = True
        if not pad_found:
            raise ValueError(f"No Pad operation found for '{self.Name}'")

    # ModelPart.produce():
    def produce(self, model_file: ModelFile) -> None:
        """Produce the ModelPart."""
        # Create the *geometry_group* that contains all of the 2D geometry (line, arc, circle.):
        app_document: App.Document = model_file.AppDocument
        geometry_group: App.DocumentObjectGroup = app_document.addObject(
            "App::DocumentObjectGroup", f"{self.Name}_Geometry")
        model_file.GeometryGroup = geometry_group

        # Create the *body*
        body: Part.BodyBase = app_document.addObject("PartDesign::Body", self.Name)
        model_file.Body = body

        mount: ModelMount
        for mount in self.Mounts:
            mount.produce(model_file, mount.Name)


# Box:
@dataclass
class Box(object):
    """Model a box.
    Builds a box given a length, width, height, material, thickness and centerpoint"

    Attributes:
    * *Length* (float): length in X direction in millimeters.
    * *Width* (float): width in Y direction in millimeters.
    * *Height* (float): height in Z direction in millimeters.
    * *Thickness* (float): Material thickness in millimeters.
    * *Material* (str): Material to use.
    * *Name* (str): Box name.

    """

    Name: str
    Length: float
    Width: float
    Height: float
    Thickness: float
    Material: str
    
    # Box.compute():
    def compute(self) -> None:
        """Compute a box."""
        pass

    def produce(self) -> Tuple[ModelPart, ...]:
        """Produce a box."""
        dx: float = self.Length
        dy: float = self.Width
        dz: float = self.Height
        dw: float = self.Thickness

        dx2: float = dx / 2
        dy2: float = dy / 2
        dz2: float = dz / 2

        east_axis: Vector = Vector(1, 0, 0)
        north_axis: Vector = Vector(0, 1, 0)
        top_axis: Vector = Vector(0, 0, 1)
        west_axis: Vector = -east_axis
        south_axis: Vector = -north_axis
        bottom_axis: Vector = -top_axis

        top_polygon: ModelPolygon = ModelPolygon("Top",
            (Vector(dx2, dy2, dz2),  # TNE
             Vector(-dx2, dy2, dz2),  # TNW
             Vector(-dx2, -dy2, dz2),  # TSW
             Vector(dx2, -dy2, dz2),  # TSE
            )
        )
        top_mount: ModelMount = ModelMount("TopNorth",
            Vector(0, 0, dz2), top_axis, north_axis, (
                ModelPad("Pad", top_polygon, dw),
            ),
        )
        top_part: ModelPart = ModelPart("Top", "hdpe", "red", (top_mount,))

        north_polygon: ModelPolygon = ModelPolygon("North",
            (Vector(dx2, dy2, dz2 - dw),  # TNE
             Vector(-dx2, dy2, dz2 - dw),  # TNW
             Vector(-dx2, dy2, -dz2),  # BNW
             Vector(dx2, dy2, -dz2),  # BNE
            )
        )
        north_mount: ModelMount = ModelMount("NorthBottom",
            Vector(0, dy2, 0), north_axis, bottom_axis, (
                ModelPad("Pad", north_polygon, dw),
            ),
        )
        north_part: ModelPart = ModelPart("North", "hdpe", "green", (north_mount,))

        west_polygon: ModelPolygon = ModelPolygon("West",
            (Vector(-dx2, dy2 - dw, dz2 - dw),  # TNW
             Vector(-dx2, -dy2 + dw, dz2 - dw),  # TSW
             Vector(-dx2, -dy2 + dw, -dz2 + dw),  # BSW
             Vector(-dx2, dy2 - dw, -dz2 + dw),  # BNW
            )
        )
        west_mount: ModelMount = ModelMount("WestNorth",
            Vector(dx2, 0, 0), west_axis, north_axis, (
                ModelPad("Pad", west_polygon, dw),
            ),
        )
        west_part: ModelPart = ModelPart("West", "hdpe", "blue", (west_mount,))

        bottom_polygon: ModelPolygon = ModelPolygon("Bottom",
            (Vector(dx2, dy2 - dw, -dz2),  # BNE
             Vector(-dx2, dy2 - dw, -dz2),  # BNW
             Vector(-dx2, -dy2 + dw, -dz2),  # BSW
             Vector(dx2, -dy2 + dw, -dz2),  # BSE
            )
        )
        bottom_mount: ModelMount = ModelMount("BottomNorth",
            Vector(0, 0, dz2), bottom_axis, north_axis, (
                ModelPad("Pad", bottom_polygon, dw),
            ),
        )
        bottom_part: ModelPart = ModelPart("Bottom", "hdpe", "red", (bottom_mount,))

        east_polygon: ModelPolygon = ModelPolygon("East",
            (Vector(dx2, dy2 - dw, dz2 - dw),  # TNE
             Vector(dx2, -dy2 + dw, dz2 - dw),  # TSE
             Vector(dx2, -dy2 + dw, -dz2 + dw),  # BSE
             Vector(dx2, dy2 - dw, -dz2 + dw),  # BNE
            )
        )
        east_mount: ModelMount = ModelMount("EastNorth",
            Vector(dx2, 0, 0), east_axis, north_axis, (
                ModelPad("Pad", east_polygon, dw),
            ),
        )
        east_part: ModelPart = ModelPart("East", "hdpe", "blue", (east_mount,))

        south_polygon: ModelPolygon = ModelPolygon("South",
            (Vector(dx2, -dy2, dz2 - dw),  # TSE
             Vector(-dx2, -dy2, dz2 - dw),  # TSW
             Vector(-dx2, -dy2, -dz2),  # BSW
             Vector(dx2, -dy2, -dz2),  # BsE
            )
        )
        south_mount: ModelMount = ModelMount("SouthBottom",
            Vector(0, dy2, 0), south_axis, bottom_axis, (
                ModelPad("Pad", south_polygon, dw),
            ),
        )
        south_part: ModelPart = ModelPart("South", "hdpe", "green", (south_mount,))

        return (top_part, north_part, west_part, bottom_part, east_part, south_part)


def main() -> None:
    """Run main program."""
    # Create *top_part*:
    z_offset: float = 40.0
    pad_fillet_radius: float = 10.0
    pad_polygon: ModelPolygon = ModelPolygon("Pad", (
        (Vector(-40, -60, z_offset), pad_fillet_radius),  # SW
        (Vector(40, -60, z_offset), pad_fillet_radius),  # SE
        (Vector(40, 20, z_offset), pad_fillet_radius),  # NE
        (Vector(-40, 20, z_offset), pad_fillet_radius),  # NW
    ))
    pocket_fillet_radius: float = 2.5
    left_pocket: ModelPolygon = ModelPolygon("LeftPocket", (
        (Vector(-30, -10, z_offset), pocket_fillet_radius),
        (Vector(-10, -10, z_offset), pocket_fillet_radius),
        (Vector(-10, 10, z_offset), pocket_fillet_radius),
        (Vector(-30, 10, z_offset), pocket_fillet_radius),
    ))
    right_pocket: ModelPolygon = ModelPolygon("RightPocket", (
        (Vector(10, -10, z_offset), pocket_fillet_radius),
        (Vector(30, -10, z_offset), pocket_fillet_radius),
        (Vector(30, 10, z_offset), pocket_fillet_radius),
        (Vector(10, 10, z_offset), pocket_fillet_radius),
    ))
    _ = right_pocket
    right_circle: ModelCircle = ModelCircle(Vector(20, 0, z_offset), 10)
    center_circle: ModelCircle = ModelCircle(Vector(0, 0, z_offset), 10)

    contact: Vector = Vector(0, 0, z_offset)
    normal: Vector = Vector(0, 0, 1)
    north: Vector = Vector(0, 1, 0)
    top_north_mount: ModelMount = ModelMount("TopNorth", contact, normal, north, (
        ModelPad("Pad", pad_polygon, 50.0),
        ModelPocket("LeftPocket", left_pocket, 10.0),
        ModelPocket("RightPocket", right_circle, 8.0),
        ModelHole("CenterHole", center_circle, 5.0),
    ))
    top_part: ModelPart = ModelPart("TopPart", "hdpe", "red", (
        top_north_mount,
    ))

    # Create *side_part*
    side_radius: float = 3.0
    y_offset: float = -50.0
    side_pad: ModelPolygon = ModelPolygon("SidePad", (
        (Vector(-50, y_offset, -20), side_radius),
        (Vector(-50, y_offset, 20), side_radius),
        (Vector(50, y_offset, 20), side_radius),
        (Vector(50, y_offset, -20), side_radius),
    ))
    contact = Vector(0, y_offset)
    normal = Vector(0, -1, 0)
    side_north_mount: ModelMount = ModelMount("SideNorth", contact, normal, north, (
        ModelPad("Pad", side_pad, 10),
    ))
    side_part: ModelPart = ModelPart("SidePart", "hdpe", "green", (
        side_north_mount,
    ))

    box: Box = Box("MyBox", 200, 100, 100, 10, "HDPE")
    box.compute()
    box_parts: Tuple[ModelPart, ...] = box.produce()

    # Create the models:
    model_file: ModelFile
    # with ModelFile((top_part, side_part,), Path("/tmp/test.fcstd")) as model_file:
    with ModelFile(box_parts, Path("/tmp/test.fcstd")) as model_file:
        model_file.produce()


if __name__ == "__main__":
    # ModelPolygon.unit_test()
    main()
