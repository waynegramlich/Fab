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

# Note this code uses nested dataclasses that are frozen.  Computed attributes are tricky.
# See (Set frozen data class files in __post_init__)[https://stackoverflow.com/questions/53756788]

import os
import sys

assert sys.version_info.major == 3  # Python 3.x
assert sys.version_info.minor == 8  # Python 3.8
sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])

from dataclasses import dataclass, field
import math
from typing import Any, Dict, List, Optional, Tuple, Union

import FreeCAD  # type: ignore
import Draft  # type: ignore
import Part  # type: ignore
import FreeCAD as App  # type: ignore

from FreeCAD import Placement, Vector


# _ModFabGeometry:
@dataclass(frozen=True)
class _ModFabGeometry(object):
    """_ModFabGeometry: An Internal base class for _ModFabArc, _ModFabCircle, and _ModFabLine.

    All _ModFabGeometry classes are immutable (i.e. frozen.)
    """

    # _ModFabGeometry.produce():
    def produce(self, context: Dict[str, Any], prefix: str, index: int) -> Part.Part2DObject:
        raise NotImplementedError(f"{type(self)}.produce() is not implemented yet")


# _ModFabArc:
@dataclass(frozen=True)
class _ModFabArc(_ModFabGeometry):
    """_ModFabArc: An internal representation an arc geometry.

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

    # _ModFabArc._make_arc_3points():
    @staticmethod
    def make_arc_3points(points: Tuple[Vector, ...], placement=None, face=False,
                         support=None, map_mode="Deactivated",
                         primitive=False) -> Any:
        """Make arc using a copy of Draft.make_arc_3points without print statements."""
        # _name = "make_arc_3points"
        # utils.print_header(_name, "Arc by 3 points")

        # try:
        #     utils.type_check([(points, (list, tuple))], name=_name)
        # except TypeError:
        #     _err(translate("draft","Points: ") + "{}".format(points))
        #     _err(translate("draft","Wrong input: must be list or tuple of three points exactly."))
        #     return None

        # if len(points) != 3:
        #     _err(translate("draft","Points: ") + "{}".format(points))
        #     _err(translate("draft","Wrong input: must be list or tuple of three points exactly."))
        #     return None

        # if placement is not None:
        #     try:
        #         utils.type_check([(placement, App.Placement)], name=_name)
        #     except TypeError:
        #         _err(translate("draft","Placement: ") + "{}".format(placement))
        #         _err(translate("draft","Wrong input: incorrect type of placement."))
        #         return None

        p1, p2, p3 = points

        # _msg("p1: {}".format(p1))
        # _msg("p2: {}".format(p2))
        # _msg("p3: {}".format(p3))

        # try:
        #     utils.type_check([(p1, App.Vector),
        #                       (p2, App.Vector),
        #                       (p3, App.Vector)], name=_name)
        # except TypeError:
        #     _err(translate("draft","Wrong input: incorrect type of points."))
        #     return None

        try:
            _edge = Part.Arc(p1, p2, p3)
        except Part.OCCError as error:
            # _err(translate("draft","Cannot generate shape: ") + "{}".format(error))
            _ = error
            assert False
            return None

        edge = _edge.toShape()
        radius = edge.Curve.Radius
        center = edge.Curve.Center

        # _msg(translate("draft","Radius:") + " " + "{}".format(radius))
        # _msg(translate("draft","Center:") + " " + "{}".format(center))

        if primitive:
            # _msg(translate("draft","Create primitive object"))
            obj = App.ActiveDocument.addObject("Part::Feature", "Arc")
            obj.Shape = edge
            return obj

        rot = App.Rotation(edge.Curve.XAxis,
                           edge.Curve.YAxis,
                           edge.Curve.Axis, "ZXY")
        _placement = App.Placement(center, rot)
        start = edge.FirstParameter
        end = math.degrees(edge.LastParameter)
        obj = Draft.makeCircle(radius,
                               placement=_placement, face=face,
                               startangle=start, endangle=end,
                               support=support)

        # This codes seems to require the draft toolbar to be presnt to do anything.
        # if App.GuiUp:
        #     gui_utils.autogroup(obj)

        original_placement = obj.Placement

        if placement and not support:
            obj.Placement.Base = placement.Base
            # _msg(translate("draft","Final placement:") + " " + "{}".format(obj.Placement))
        if face:
            # _msg(translate("draft","Face: True"))
            pass
        if support:
            # _msg(translate("draft","Support:") + " " + "{}".format(support))
            # _msg(translate("draft","Map mode:") + " " + "{}".format(map_mode))
            obj.MapMode = map_mode
            if placement:
                obj.AttachmentOffset.Base = placement.Base
                obj.AttachmentOffset.Rotation = original_placement.Rotation
                # msg(translate("draft","Attachment offset: {}".format(obj.AttachmentOffset)))
            # _msg(translate("draft","Final placement:") + " " + "{}".format(obj.Placement))

        return obj

    # _ModFabArc.produce():
    def produce(self, context: Dict[str, Any], prefix: str, index: int) -> Part.Part2DObject:
        """Return line segment after moving it into Geometry group."""
        assert "mount_contact" in context
        mount_contact: Any = context["mount_contact"]
        assert isinstance(mount_contact, Vector)
        assert "mount_normal" in context
        mount_normal: Any = context["mount_normal"]
        assert isinstance(mount_normal, Vector)

        # TODO: Simplify:
        mount_placement: Any = Placement(mount_contact, mount_normal, 0.0)  # Base, Axis, Angle
        assert isinstance(mount_placement, Placement), mount_placement
        placement: Placement = Placement()  # Should be Placement(mount_count, mount_normal, 0.0)
        placement.Rotation = mount_placement.Rotation  # Delete
        placement.Base = self.Center

        # Create and label *part_arc*:
        # part_arc: Part.Part2DObject = Draft.makeCircle(
        #     self.Radius, placement=placement, face=False,  # face=True,
        #     startangle=math.degrees(self.StartAngle),
        #     endangle=math.degrees(self.StartAngle + self.DeltaAngle),
        #     support=None)
        part_arc: Part.Part2DObject = _ModFabArc.make_arc_3points(
            (self.Start, self.Middle, self.Finish))
        # part_arc: Part.Part2DObject=Draft.make_arc_3points([self.Start, self.Middle, self.Finish])

        label: str = f"{prefix}_Arc_{index:03d}"
        assert isinstance(part_arc, Part.Part2DObject)
        part_arc.Label = label
        part_arc.Visibility = False

        # Move *part_arc* into *geometry_group*:
        if "geometry_group" not in context:
            raise RuntimeError(f"'geometry_group' is not in context.")
        geometry_group: Any = context["geometry_group"]
        assert isinstance(geometry_group, App.DocumentObjectGroup), geometry_group
        part_arc.adjustRelativeLinks(geometry_group)
        geometry_group.addObject(part_arc)

        return part_arc


@dataclass(frozen=True)
class _ModFabCircle(_ModFabGeometry):
    """_ModFabCircle: An internal representation of a circle geometry.

    Attributes:
    * *Center (Vector): The circle center.
    * *Diameter (float): The circle diameter in millimeters.

    """

    Center: Vector
    Diameter: float

    # _ModFabCircle.produce():
    def produce(self, context: Dict[str, Any], prefix: str, index: int) -> Part.Part2DObject:
        """Return line segment after moving it into Geometry group."""
        # Extract mount plane *contact* and *normal* from *context* for 2D projection:
        assert "mount_contact" in context, context
        contact: Any = context["mount_contact"]
        assert isinstance(contact, Vector), contact
        assert "mount_normal" in context, context
        normal: Vector = context["mount_normal"]
        assert isinstance(normal, Vector), normal

        center_on_plane: Vector = self.Center.projectToPlane(contact, normal)

        label: str = f"{prefix}_Circle_{index:03d}"
        # placement: Placement = Placement()
        # placement.Rotation.Q = (0.0, 0.0, 0.0, 1.0)
        # placement.Base = center2d
        placement: Placement = Placement(center_on_plane, normal, 0.0)  # Base, Axis, Angle

        # Create and label *part_arc*:
        part_circle: Part.Part2DObject = Draft.makeCircle(
            self.Diameter / 2.0, placement=placement, face=True,
            support=None)
        assert isinstance(part_circle, Part.Part2DObject)
        part_circle.Label = label
        part_circle.Visibility = False

        # Move *part_arc* into *geometry_group*:
        assert "geometry_group" in context, context
        geometry_group: Any = context["geometry_group"]
        assert isinstance(geometry_group, App.DocumentObjectGroup)
        part_circle.adjustRelativeLinks(geometry_group)
        geometry_group.addObject(part_circle)

        return part_circle


# _ModFabLine:
@dataclass(frozen=True)
class _ModFabLine(_ModFabGeometry):
    """_ModFabLine: An internal representation of a line segment geometry.

    Attributes:
    * *Start (Vector): The line segment start point.
    * *Finish (Vector): The line segment finish point.

    """

    Start: Vector
    Finish: Vector

    # _ModFabLine.produce():
    def produce(self, context: Dict[str, Any], prefix: str, index: int) -> Part.Part2DObject:
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
        assert "geometry_group" in context, context
        geometry_group: Any = context["geometry_group"]
        assert isinstance(geometry_group, App.DocumentObjectGroup)
        line_segment.adjustRelativeLinks(geometry_group)
        line_segment.Visibility = False
        geometry_group.addObject(line_segment)

        return line_segment


# _ModFabFillet:
@dataclass
class _ModFabFillet(object):
    """_ModFabFillet: An object that represents one fillet of a ModFabPolygon.

    Attributes:
    * *Apex* (Vector): The apex corner point for the fillet.
    * *Radius* (float): The fillet radius in millimeters.
    * *Before* (_ModFabFillet): The previous _ModFabFillet in the ModFabPolygon.
    * *After* (_ModFabFillet): The next _ModFabFillet in the ModFabPolygon.
    * *Arc* (Optional[_ModFabArc]): The fillet Arc if Radius is non-zero.
    * *Line* (Optional[_ModFabLine]): The line that connects to the previous _ModFabFillet

    """

    Apex: Vector
    Radius: float
    Before: "_ModFabFillet" = field(init=False, repr=False)  # Filled in by __post_init__()
    After: "_ModFabFillet" = field(init=False, repr=False)  # Filled in by __post_init__()
    Arc: Optional["_ModFabArc"] = field(init=False, default=None)  # Filled in by compute_arcs()
    Line: Optional["_ModFabLine"] = field(init=False, default=None)  # Filled in by compute_lines()

    # _ModFabFillet.__post_init__():
    def __post_init__(self) -> None:
        """Initialize _ModFabFillet."""
        self.Before = self
        self.After = self

    # _ModFabFillet.compute_arc():
    def compute_arc(self, tracing: str = "") -> _ModFabArc:
        """Return the arc associated with a _ModFabFillet with non-zero radius."""
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
        # The crude 2D diagram below shows the basic _ModFabFillet geometry:
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
            print(f"{tracing}=>_ModFabFillet.compute_arc({apex})")
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
        # TODO: Use  Vector.getAngle() instead.
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
        # arc: _ModFabArc = _ModFabArc(apex, radius, center, start, middle, finish,
        #                            start_angle, finish_angle, delta_angle)
        arc: _ModFabArc = _ModFabArc(apex, radius, center, start, middle, finish)

        # Do a sanity check:
        # finish_angle = finish_angle % pi2
        # start_plus_delta_angle: float = (start_angle + delta_angle) % pi2
        # assert abs(start_plus_delta_angle - finish_angle) < 1.0e-8, "Delta angle is wrong."

        if tracing:
            print(f"{tracing}<=_ModFabFillet.compute_arc({apex})=>{arc}")
        return arc

    # _ModFabFillet.plane_2d_project:
    def plane_2d_project(self, contact: Vector, normal: Vector) -> None:
        """Project the Apex onto a plane.

        Arguments:
        * *contact* (Vector): A point on the projection plane.
        * *normal* (Vector): A normal to the projection plane.

        """
        self.Apex = self.Apex.projectToPlane(contact, normal)

    # _ModFabFillet.get_geometries():
    def get_geometries(self) -> Tuple[_ModFabGeometry, ...]:
        geometries: List[_ModFabGeometry] = []
        if self.Line:
            geometries.append(self.Line)
        if self.Arc:
            geometries.append(self.Arc)
        return tuple(geometries)


# ModFabGeometry:
@dataclass(frozen=True)
class ModFabGeometry(object):
    """ModFabGeometry: The base class for ModFabPolygon and ModFabCircle."""

    # ModFabGeometry.produce():
    def produce(self, model_context: Any, prefix: str) -> Tuple[Part.Part2DObject, ...]:
        """Produce the necessary FreeCAD objects for the ModFabGeometry."""
        raise NotImplementedError(f"{type(self)}.produce() is not implemented")


# ModFabCircle:
@dataclass(frozen=True)
class ModFabCircle(ModFabGeometry):
    """ModFabCircle: A circle with a center and a radius.

    This is actually a sphere of at a specified location and diameter.  It gets cut into
    circle later on.

    Attributes:
    * *Center* (Vector): The circle center.
    * *Diameter* (float): The diameter in radians.

    """

    Center: Vector
    Diameter: float

    # ModFabCircle.__post_init__():
    def __post_init__(self) -> None:
        """Make private copy of Center."""
        if self.Diameter <= 0.0:
            raise ValueError(f"Diameter ({self.Diameter}) must be positive.")
        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        copy: Vector = Vector()
        object.__setattr__(self, "Center", self.Center + copy)  # Makes a copy.

    # ModFabCircle.produce():
    def produce(self, context: Dict[str, Any], prefix: str) -> Tuple[Part.Part2DObject, ...]:
        """Produce the FreeCAD objects needed for ModFabPolygon."""
        geometries: Tuple[_ModFabGeometry, ...] = self.get_geometries()
        geometry: _ModFabGeometry
        index: int
        part_geometries: List[Part.Part2DObject] = []
        for index, geometry in enumerate(geometries):
            part_geometry: Part.Part2DObject = geometry.produce(context, prefix, index)
            assert isinstance(part_geometry, Part.Part2DObject)
            part_geometries.append(part_geometry)
        return tuple(part_geometries)

    # ModFabCircle.get_geometries():
    def get_geometries(self) -> Tuple[_ModFabGeometry, ...]:
        """Return the ModFabPolygon lines and arcs."""
        return (_ModFabCircle(self.Center, self.Diameter),)

    @staticmethod
    # ModFabCircle._unit_tests():
    def _unit_tests():
        """Run ModFabCircle unit tests."""
        center: Vector = Vector(1, 2, 3)
        try:
            ModFabCircle(center, 0.0)
            assert False
        except ValueError as value_error:
            assert str(value_error) == "Diameter (0.0) must be positive.", value_error
        try:
            ModFabCircle(center, -1.0)
            assert False
        except ValueError as value_error:
            assert str(value_error) == "Diameter (-1.0) must be positive.", value_error


# ModFabPolygon:
@dataclass(frozen=True)
class ModFabPolygon(ModFabGeometry):
    """ModFabPolygon: An immutable polygon with rounded corners.

    A ModFabPolygon is represented as a sequence of corners (i.e. a Vector) where each corner can
    optionally be filleted with a radius.  In order to make it easier to use, a corner can be
    specified as simple Vector or as a tuple that specifes a Vector and a radius.  The radius
    is in millimeters and can be provided as either Python int or float.  When an explicit
    fillet radius is not specified, higher levels in the software stack will typically substitute
    in a deburr radius for external corners and an interal tool radius for internal corners.
    ModFabPolygon's are frozen and can not be modified after creation.

    Example:
         polygon: ModFab.ModFabPolyon = ModFab.ModFabPolygon((
             Vector(-10, -10, 0),  # Lower left (no radius)
             Vector(10, -10, 0),  # Lower right (no radius)
             (Vector(10, 10, 0), 5),  # Upper right (5mm radius)
             (Vector(-0, 10, 0), 5.5),  # Upper right (5.5mm radius)
         ), "Name")

    Attributes:
    * *Name* (str): The name of the polygon.  (Default: "")
    * *Corners* (Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...]):
      See description below for more on corners.

    """

    Name: str
    Corners: Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...]
    _Fillets: Tuple[_ModFabFillet, ...] = field(init=False, repr=False)

    EPSILON = 1.0e-8

    # ModFabPolygon.__post_init__():
    def __post_init__(self) -> None:
        """Verify that the corners passed in are correct."""
        corner: Union[Vector, Tuple[Vector, Union[int, float]]]
        fillets: List[_ModFabFillet] = []
        fillet: _ModFabFillet
        # TODO: Check for polygon points that are colinear.
        # TODO: Check for polygon corners with overlapping radii.
        copy: Vector = Vector()  # Vector's are mutable, add *copy* to make a private Vector copy.
        index: int
        for index, corner in enumerate(self.Corners):
            if isinstance(corner, Vector):
                fillet = _ModFabFillet(corner + copy, 0.0)
            elif isinstance(corner, tuple):
                if len(corner) != 2:
                    raise ValueError(f"Polygon Corner[{index}]: {corner} tuple length is not 2")
                if not isinstance(corner[0], Vector):
                    raise ValueError(f"Polygon Corner[{index}]: {corner} first entry is not Vector")
                if not isinstance(corner[1], (int, float)):
                    raise ValueError(f"Polygon Corner[{index}]: {corner} first entry is not number")
                fillet = _ModFabFillet(corner[0] + copy, corner[1])
            else:
                raise ValueError(
                    f"Polygon Corner[{index}] is {corner} which is neither a Vector nor "
                    "(Vector, radius) tuple.")
            fillets.append(fillet)
        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        object.__setattr__(self, "_Fillets", tuple(fillets))

        # Double link the fillets and look for errors:
        self._double_link()
        radius_error: str = self._radii_check()
        if radius_error:
            raise ValueError(radius_error)
        colinear_error: str = self._colinear_check()
        if colinear_error:
            raise ValueError(colinear_error)
        # These checks are repeated after 2D projection.

        # self._compute_arcs()
        # self._compute_lines()

    # ModFabPolygon._double_link():
    def _double_link(self) -> None:
        """Double link the _ModFabFillet's together."""
        fillets: Tuple[_ModFabFillet, ...] = self._Fillets
        size: int = len(fillets)
        fillet: _ModFabFillet
        index: int
        for index, fillet in enumerate(fillets):
            fillet.Before = fillets[(index - 1) % size]
            fillet.After = fillets[(index + 1) % size]

    # ModFabPolygon._radii_check():
    def _radii_check(self) -> str:
        """Check for radius overlap errors."""
        at_fillet: _ModFabFillet
        for at_fillet in self._Fillets:
            before_fillet: _ModFabFillet = at_fillet.Before
            actual_distance: float = (before_fillet.Apex - at_fillet.Apex).Length
            radii_distance: float = before_fillet.Radius + at_fillet.Radius
            if radii_distance > actual_distance:
                return (f"Requested radii distance {radii_distance}mm "
                        f"(={before_fillet.Radius}+{at_fillet.Radius}) < {actual_distance}mm "
                        "between {at_fillet.Before} and {after_fillet.After}")
        return ""

    # ModFabPolygon._colinear_check():
    def _colinear_check(self) -> str:
        """Check for colinearity errors."""
        at_fillet: _ModFabFillet
        epsilon: float = ModFabPolygon.EPSILON
        degrees180: float = math.pi
        for at_fillet in self._Fillets:
            before_apex: Vector = at_fillet.Before.Apex
            at_apex: Vector = at_fillet.Apex
            after_apex: Vector = at_fillet.After.Apex
            to_before_apex: Vector = before_apex - at_apex
            to_after_apex: Vector = after_apex - at_apex
            between_angle: float = abs(to_before_apex.getAngle(to_after_apex))
            if between_angle < epsilon or abs(degrees180 - between_angle) < epsilon:
                return f"Points [{before_apex}, {at_apex}, {after_apex}] are colinear"
        return ""

    # ModFabPolygon._compute_arcs():
    def _compute_arcs(self) -> None:
        """Create any Arc's needed for non-zero radius _ModFabFillet's."""
        fillet: _ModFabFillet
        for fillet in self._Fillets:
            if fillet.Radius > 0.0:
                fillet.Arc = fillet.compute_arc()

    # ModFabPolygon._compute_lines():
    def _compute_lines(self) -> None:
        """Create Create any Line's need for _ModFabFillet's."""
        fillet: _ModFabFillet
        for fillet in self._Fillets:
            before: _ModFabFillet = fillet.Before
            start: Vector = before.Arc.Finish if before.Arc else before.Apex
            finish: Vector = fillet.Arc.Start if fillet.Arc else fillet.Apex
            if (start - finish).Length > ModFabPolygon.EPSILON:
                fillet.Line = _ModFabLine(start, finish)

    # ModFabPolygon.get_geometries():
    def get_geometries(self, contact: Vector, Normal: Vector) -> Tuple[_ModFabGeometry, ...]:
        """Return the ModFabPolygon lines and arcs."""
        geometries: List[_ModFabGeometry] = []
        fillet: _ModFabFillet
        for fillet in self._Fillets:
            geometries.extend(fillet.get_geometries())
        return tuple(geometries)

    # ModFabPolygon._plane_2d_project():
    def _plane_2d_project(self, contact: Vector, normal: Vector) -> None:
        """Update the _ModFabFillet's to be projected onto a Plane.

        Arguments:
        * *contact* (Vector): A point on the plane.
        * *normal* (Vector): A plane normal.

        """
        fillet: _ModFabFillet
        for fillet in self._Fillets:
            fillet.plane_2d_project(contact, normal)

    # ModFabPolygon.produce():
    def produce(self, context: Dict[str, Any], prefix: str) -> Tuple[Part.Part2DObject, ...]:
        """Produce the FreeCAD objects needed for ModFabPolygon."""
        # Extract mount plane *contact* and *normal* from *context*:
        assert "mount_contact" in context, context
        mount_contact: Any = context["mount_contact"]
        assert isinstance(mount_contact, Vector)
        assert "mount_normal" in context, context
        mount_normal: Any = context["mount_normal"]
        assert isinstance(mount_normal, Vector)

        # Use *contact*/*normal* for 2D projection:
        self._plane_2d_project(mount_contact, mount_normal)

        # Double check for radii and colinear errors that result from 2D projection:
        radius_error: str = self._radii_check()
        if radius_error:
            raise RuntimeError(radius_error)
        colinear_error: str = self._colinear_check()
        if colinear_error:
            raise RuntimeError(colinear_error)

        # Now compute the arcs and lines:
        self._compute_arcs()
        self._compute_lines()

        # Extract the geometries using *contact* and *normal* to specify the projecton plane:
        geometries: Tuple[_ModFabGeometry, ...] = self.get_geometries(mount_contact, mount_normal)
        geometry: _ModFabGeometry
        index: int
        part_geometries: List[Part.Part2DObject] = []
        for index, geometry in enumerate(geometries):
            part_geometry: Part.Part2DObject = geometry.produce(context, prefix, index)
            assert isinstance(part_geometry, Part.Part2DObject)
            part_geometries.append(part_geometry)
        return tuple(part_geometries)

    # ModFabPolygon._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Do some unit tests."""
        v1: Vector = Vector(-40, -20, 0)
        v2: Vector = Vector(40, -20, 0)
        v3: Vector = Vector(40, 20, 0)
        v4: Vector = Vector(-40, 20, 0)
        polygon: ModFabPolygon = ModFabPolygon("TestPolygon", (v1, v2, (v3, 10), v4))
        _ = polygon

        # geometries: Tuple[_ModFabGeometry, ...] = polygon.get_geometries()
        # index: int
        # geometry: _ModFabGeometry
        # for index, geometry in enumerate(geometries):
        #     print(f"Geometry[{index}]: {geometry}")


def main() -> None:
    """Run main program."""
    pass


if __name__ == "__main__":
    ModFabCircle._unit_tests()
    ModFabPolygon._unit_tests()
    main()
