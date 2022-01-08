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

import sys
sys.path.append(".")
import Embed
Embed.setup()

from dataclasses import dataclass, field
import math
from typing import Any, cast, Dict, List, Optional, Tuple, Union


import FreeCAD  # type: ignore
import Draft  # type: ignore
import Part  # type: ignore
import FreeCAD as App  # type: ignore

from FreeCAD import Placement, Rotation, Vector
from Tree import FabBox


# _Geometry:
@dataclass(frozen=True)
class _Geometry(object):
    """_Geometry: An Internal base class for _Arc, _Circle, and _Line.

    All _Geometry classes are immutable (i.e. frozen.)
    """

    # _Geometry.produce():
    def produce(self, context: Dict[str, Any], prefix: str,
                index: int, tracing: str = "") -> Part.Part2DObject:
        raise NotImplementedError(f"{type(self)}.produce() is not implemented yet")


# _Arc:
@dataclass(frozen=True)
class _Arc(_Geometry):
    """_Arc: An internal representation an arc geometry.

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

    # _Arc._make_arc_3points():
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

    # _Arc.produce():
    def produce(self, context: Dict[str, Any], prefix: str,
                index: int, tracing: str = "") -> Part.Part2DObject:
        """Return line segment after moving it into Geometry group."""
        mount_contact = cast(Vector, context["mount_contact"])
        mount_normal = cast(Vector, context["mount_normal"])

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
        part_arc: Part.Part2DObject = _Arc.make_arc_3points(
            (self.Start, self.Middle, self.Finish))
        # part_arc: Part.Part2DObject=Draft.make_arc_3points([self.Start, self.Middle, self.Finish])

        label: str = f"{prefix}_Arc_{index:03d}"
        assert isinstance(part_arc, Part.Part2DObject)
        part_arc.Label = label
        part_arc.Visibility = False

        # Move *part_arc* into *geometry_group*:
        geometry_group = cast(App.DocumentObjectGroup, context["geometry_group"])
        part_arc.adjustRelativeLinks(geometry_group)
        geometry_group.addObject(part_arc)

        return part_arc


@dataclass(frozen=True)
class _Circle(_Geometry):
    """_Circle: An internal representation of a circle geometry.

    Attributes:
    * *Center (Vector): The circle center.
    * *Diameter (float): The circle diameter in millimeters.

    """

    Center: Vector
    Diameter: float

    # _Circle.produce():
    def produce(self, context: Dict[str, Any], prefix: str, index: int,
                tracing: str = "") -> Part.Part2DObject:
        """Return line segment after moving it into Geometry group."""
        if tracing:
            print(f"{tracing}=>_Circle.produce()")
        # Extract mount plane *contact* and *normal* from *context* for 2D projection:
        mount_contact = cast(Vector, context["mount_contact"])
        mount_normal = cast(Vector, context["mount_normal"])
        # FreeCAD Vector metheds like to modify Vector contents; force copies beforehand:
        copy: Vector = Vector()
        center_on_plane: Vector = (self.Center + copy).projectToPlane(
            mount_contact + copy, mount_normal + copy)

        label: str = f"{prefix}_Circle_{index:03d}"
        z_axis: Vector = Vector(0.0, 0.0, 1.0)
        rotation: Rotation = Rotation(z_axis, mount_normal)
        placement: Placement = Placement()
        placement.Rotation = rotation
        placement.Base = center_on_plane
        if tracing:
            print(f"{tracing}{center_on_plane=} {mount_normal=}")
            print(f"{tracing}{placement=}")
            print(f"{tracing}{rotation * z_axis=}")

        # Create and label *part_arc*:
        part_circle: Part.Part2DObject = Draft.makeCircle(
            self.Diameter / 2.0, placement=placement, face=True,
            support=None)
        assert isinstance(part_circle, Part.Part2DObject)
        part_circle.Label = label
        part_circle.Visibility = False

        # Move *part_arc* into *geometry_group*:
        geometry_group = cast(App.DocumentObjectGroup, context["geometry_group"])
        part_circle.adjustRelativeLinks(geometry_group)
        geometry_group.addObject(part_circle)

        if tracing:
            print(f"{tracing}<=_Circle.produce()")
        return part_circle


# _Line:
@dataclass(frozen=True)
class _Line(_Geometry):
    """_Line: An internal representation of a line segment geometry.

    Attributes:
    * *Start (Vector): The line segment start point.
    * *Finish (Vector): The line segment finish point.

    """

    Start: Vector
    Finish: Vector

    # _Line.produce():
    def produce(self, context: Dict[str, Any], prefix: str,
                index: int, tracing: str = "") -> Part.Part2DObject:
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
        geometry_group = cast(App.DocumentObjectGroup, context["geometry_group"])
        line_segment.adjustRelativeLinks(geometry_group)
        line_segment.Visibility = False
        geometry_group.addObject(line_segment)

        return line_segment


# _Fillet:
@dataclass
class _Fillet(object):
    """_Fillet: An object that represents one fillet of a FabPolygon.

    Attributes:
    * *Apex* (Vector): The apex corner point for the fillet.
    * *Radius* (float): The fillet radius in millimeters.
    * *Before* (_Fillet): The previous _Fillet in the FabPolygon.
    * *After* (_Fillet): The next _Fillet in the FabPolygon.
    * *Arc* (Optional[_Arc]): The fillet Arc if Radius is non-zero.
    * *Line* (Optional[_Line]): The line that connects to the previous _Fillet

    """

    Apex: Vector
    Radius: float
    Before: "_Fillet" = field(init=False, repr=False)  # Filled in by __post_init__()
    After: "_Fillet" = field(init=False, repr=False)  # Filled in by __post_init__()
    Arc: Optional["_Arc"] = field(init=False, default=None)  # Filled in by compute_arcs()
    Line: Optional["_Line"] = field(init=False, default=None)  # Filled in by compute_lines()

    # _Fillet.__post_init__():
    def __post_init__(self) -> None:
        """Initialize _Fillet."""
        self.Before = self
        self.After = self

    # _Fillet.compute_arc():
    def compute_arc(self, tracing: str = "") -> _Arc:
        """Return the arc associated with a _Fillet with non-zero radius."""
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
        # The crude 2D diagram below shows the basic _Fillet geometry:
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
            print(f"{tracing}=>_Fillet.compute_arc({apex})")
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
        # arc: _Arc = _Arc(apex, radius, center, start, middle, finish,
        #                            start_angle, finish_angle, delta_angle)
        arc: _Arc = _Arc(apex, radius, center, start, middle, finish)

        # Do a sanity check:
        # finish_angle = finish_angle % pi2
        # start_plus_delta_angle: float = (start_angle + delta_angle) % pi2
        # assert abs(start_plus_delta_angle - finish_angle) < 1.0e-8, "Delta angle is wrong."

        if tracing:
            print(f"{tracing}<=_Fillet.compute_arc({apex})=>{arc}")
        return arc

    # _Fillet.plane_2d_project:
    def plane_2d_project(self, contact: Vector, normal: Vector) -> None:
        """Project the Apex onto a plane.

        Arguments:
        * *contact* (Vector): A point on the projection plane.
        * *normal* (Vector): A normal to the projection plane.

        """
        # FreeCAD Vector metheds like to modify Vector contents; force copies beforehand:
        copy: Vector = Vector()
        self.Apex = (self.Apex + copy).projectToPlane(contact + copy, normal + copy)

    # _Fillet.get_geometries():
    def get_geometries(self) -> Tuple[_Geometry, ...]:
        geometries: List[_Geometry] = []
        if self.Line:
            geometries.append(self.Line)
        if self.Arc:
            geometries.append(self.Arc)
        return tuple(geometries)


# FabGeometry:
@dataclass(frozen=True)
class FabGeometry(object):
    """FabGeometry: The base class for FabPolygon and FabCircle."""

    # FabGeometry.Box():
    @property
    def Box(self) -> FabBox:
        """Return a FabBox that encloses the FabGeometry."""
        raise NotImplementedError(f"{type(self)}.Box() is not implemented")

    # FabGeometry.produce():
    def produce(self, model_context: Any, prefix: str) -> Tuple[Part.Part2DObject, ...]:
        """Produce the necessary FreeCAD objects for the FabGeometry."""
        raise NotImplementedError(f"{type(self)}.produce() is not implemented")

    # FabGeometry.project_to_plane():
    def project_to_plane(self, contact: Vector, normal: Vector) -> "FabGeometry":
        """Return a new FabGeometry projected onto a plane."""
        raise NotImplementedError(f"{type(self)}.project_to_plane is not implemented")


# FabCircle:
@dataclass(frozen=True)
class FabCircle(FabGeometry):
    """FabCircle: A circle with a center and a radius.

    This is actually a sphere of at a specified location and diameter.  It gets cut into
    circle later on.

    Attributes:
    * *Center* (Vector): The circle center.
    * *Normal* (Vector): The normal to circle plane.
    * *Diameter* (float): The diameter in millimeters.

    """

    Center: Vector
    Normal: Vector
    Diameter: float

    # FabCircle.__post_init__():
    def __post_init__(self) -> None:
        """Make private copy of Center."""
        if self.Diameter <= 0.0:
            raise ValueError(f"Diameter ({self.Diameter}) must be positive.")
        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        copy: Vector = Vector()
        object.__setattr__(self, "Center", self.Center + copy)  # Makes a copy.
        object.__setattr__(self, "Normal", self.Normal + copy)  # Makes a copy.

    # FabGeometry.Box():
    @property
    def Box(self) -> FabBox:
        """Return a FabBox that encloses the FabGeometry."""
        # A perpendicular to the normal is needed:
        # https://math.stackexchange.com/questions/137362/
        # how-to-find-perpendicular-vector-to-another-vector
        # The response from Joe Strout is used.  There is probably an alternate solution based
        # on quaternions that is better, but the code below should be more than adequate.
        EPSILON = 1.0e-8
        copy: Vector = Vector
        normal: Vector = (self.Normal + copy).normalize()
        nx: float = normal.x
        ny: float = normal.y
        nz: float = normal.z
        xy_close: bool = abs(nx - ny) < EPSILON
        perpendicular1: Vector = (
            Vector(-nz, 0, nx) if xy_close else Vector(-ny, nx, 0)).normalize()
        perpendicular2: Vector = (normal + copy).cross(perpendicular1 + copy)

        center: Vector = self.Center
        radius: float = self.Diameter / 2.0
        corner1: Vector = center + radius * perpendicular1
        corner2: Vector = center + radius * perpendicular2
        corner3: Vector = center - radius * perpendicular1
        corner4: Vector = center - radius * perpendicular1
        box: FabBox = FabBox()
        box.enclose((corner1, corner2, corner3, corner4))
        return box

    # FabCircle.project_to_plane():
    def project_to_plane(self, contact: Vector, normal: Vector, tracing: str = "") -> "FabCircle":
        """Return a new FabCircle projected onto a plane.

        Arguments:
        * *contact* (Vector): One point on the plane.
        * *normal* (Vector): A normal to the plane.

        Returns:
        * (FabCircle): The newly projected FabCicle.

        """
        if tracing:
            print(f"{tracing}=>FabCircle.projet_to_plane({contact}, {normal})")
        copy: Vector = Vector()
        new_center: Vector = (self.Center + copy).ProjectToPlane(contact + copy, normal + copy)
        new_circle: "FabCircle" = FabCircle(new_center, normal, self.Diameter)
        if tracing:
            print(f"{tracing}<=FabCircle.projet_to_plane({contact}, {normal}) => *")
        return new_circle

    # FabCircle.produce():
    def produce(self, context: Dict[str, Any], prefix: str,
                tracing: str = "") -> Tuple[Part.Part2DObject, ...]:
        """Produce the FreeCAD objects needed for FabPolygon."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabCircle.produce()")
        geometries: Tuple[_Geometry, ...] = self.get_geometries()
        geometry: _Geometry
        index: int
        part_geometries: List[Part.Part2DObject] = []
        for index, geometry in enumerate(geometries):
            part_geometry: Part.Part2DObject = geometry.produce(
                context, prefix, index, tracing=next_tracing)
            assert isinstance(part_geometry, Part.Part2DObject)
            part_geometries.append(part_geometry)
        if tracing:
            print(f"{tracing}<=FabCircle.produce()")
        return tuple(part_geometries)

    # FabCircle.get_geometries():
    def get_geometries(self) -> Tuple[_Geometry, ...]:
        """Return the FabPolygon lines and arcs."""
        return (_Circle(self.Center, self.Diameter),)

    @staticmethod
    # FabCircle._unit_tests():
    def _unit_tests():
        """Run FabCircle unit tests."""
        normal: Vector = Vector(0, 0, 1)
        center: Vector = Vector(1, 2, 3)
        try:
            FabCircle(center, normal, 0.0)
            assert False
        except ValueError as value_error:
            assert str(value_error) == "Diameter (0.0) must be positive.", value_error
        try:
            FabCircle(center, normal, -1.0)
            assert False
        except ValueError as value_error:
            assert str(value_error) == "Diameter (-1.0) must be positive.", value_error


# FabPolygon:
@dataclass(frozen=True)
class FabPolygon(FabGeometry):
    """FabPolygon: An immutable polygon with rounded corners.

    A FabPolygon is represented as a sequence of corners (i.e. a Vector) where each corner can
    optionally be filleted with a radius.  In order to make it easier to use, a corner can be
    specified as simple Vector or as a tuple that specifes a Vector and a radius.  The radius
    is in millimeters and can be provided as either Python int or float.  When an explicit
    fillet radius is not specified, higher levels in the software stack will typically substitute
    in a deburr radius for external corners and an interal tool radius for internal corners.
    FabPolygon's are frozen and can not be modified after creation.

    Example:
         polygon: Fab.FabPolyon = Fab.FabPolygon((
             Vector(-10, -10, 0),  # Lower left (no radius)
             Vector(10, -10, 0),  # Lower right (no radius)
             (Vector(10, 10, 0), 5),  # Upper right (5mm radius)
             (Vector(-0, 10, 0), 5.5),  # Upper right (5.5mm radius)
         ), "Name")

    Attributes:
    * *Corners* (Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...]):
      See description below for more on corners.

    """

    Corners: Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...]
    _Fillets: Tuple[_Fillet, ...] = field(init=False, repr=False)

    EPSILON = 1.0e-8

    # FabPolygon.Box:
    @property
    def Box(self) -> FabBox:
        """Return FabBox that encloses FabPolygon."""
        points: List[Vector] = []
        corner: Union[Vector, Tuple[Vector, Union[int, float]]]
        for corner in self.Corners:
            if isinstance(corner, Vector):
                points.append(corner)
            elif isinstance(corner, tuple) and len(corner) == 2:
                point: Any = corner[0]
                assert isinstance(point, Vector)
                points.append(point)
            else:
                assert False, f"Bad corner: {corner}"
        box: FabBox = FabBox()
        box.enclose(points)
        return box

    # FabPolygon.__post_init__():
    def __post_init__(self) -> None:
        """Verify that the corners passed in are correct."""
        corner: Union[Vector, Tuple[Vector, Union[int, float]]]
        fillets: List[_Fillet] = []
        fillet: _Fillet
        # TODO: Check for polygon points that are colinear.
        # TODO: Check for polygon corners with overlapping radii.
        copy: Vector = Vector()  # Vector's are mutable, add *copy* to make a private Vector copy.
        index: int
        for index, corner in enumerate(self.Corners):
            if isinstance(corner, Vector):
                fillet = _Fillet(corner + copy, 0.0)
            elif isinstance(corner, tuple):
                if len(corner) != 2:
                    raise ValueError(f"Polygon Corner[{index}]: {corner} tuple length is not 2")
                if not isinstance(corner[0], Vector):
                    raise ValueError(f"Polygon Corner[{index}]: {corner} first entry is not Vector")
                if not isinstance(corner[1], (int, float)):
                    raise ValueError(f"Polygon Corner[{index}]: {corner} first entry is not number")
                fillet = _Fillet(corner[0] + copy, corner[1])
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

    # FabPolygon.project_to_plane():
    def project_to_plane(self, contact: Vector, normal: Vector, tracing: str = "") -> "FabPolygon":
        """Return nre FabPolygon prejected onto a plane.

        Arguments:
        * *contact* (Vector): One point on the plane.
        * *normal* (Vector): A normal to the plane.

        Returns:
        * (FabPolyGon): The newly projected FabPolygon.

        """
        if tracing:
            print(f"{tracing}=>FabPolygon.project_to_plane({contact}, {normal})")
        copy: Vector = Vector()
        corner: Union[Vector, Tuple[Vector, Union[int, float]]]
        projected_corners: List[Union[Vector, Tuple[Vector, Union[int, float]]]] = []
        for corner in self.Corners:
            if isinstance(corner, Vector):
                projected_corners.append(
                    (corner + copy).projectToPlane(contact + copy, normal + copy)
                )
            elif isinstance(corner, tuple):
                assert len(corner) == 2
                point: Any = corner[0]
                radius: Any = corner[1]
                assert isinstance(point, Vector)
                assert isinstance(radius, (int, float))
                projected_corners.append(
                    ((point + copy).projectToPlane(contact + copy, normal + copy), radius)
                )
        projected_polygon: "FabPolygon" = FabPolygon(tuple(projected_corners))
        if tracing:
            print(f"{tracing}<=FabPolygon.project_to_plane({contact}, {normal})=>*")
        return projected_polygon

    # FabPolygon._double_link():
    def _double_link(self) -> None:
        """Double link the _Fillet's together."""
        fillets: Tuple[_Fillet, ...] = self._Fillets
        size: int = len(fillets)
        fillet: _Fillet
        index: int
        for index, fillet in enumerate(fillets):
            fillet.Before = fillets[(index - 1) % size]
            fillet.After = fillets[(index + 1) % size]

    # FabPolygon._radii_check():
    def _radii_check(self) -> str:
        """Check for radius overlap errors."""
        at_fillet: _Fillet
        for at_fillet in self._Fillets:
            before_fillet: _Fillet = at_fillet.Before
            actual_distance: float = (before_fillet.Apex - at_fillet.Apex).Length
            radii_distance: float = before_fillet.Radius + at_fillet.Radius
            if radii_distance > actual_distance:
                return (f"Requested radii distance {radii_distance}mm "
                        f"(={before_fillet.Radius}+{at_fillet.Radius}) < {actual_distance}mm "
                        "between {at_fillet.Before} and {after_fillet.After}")
        return ""

    # FabPolygon._colinear_check():
    def _colinear_check(self) -> str:
        """Check for colinearity errors."""
        at_fillet: _Fillet
        epsilon: float = FabPolygon.EPSILON
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

    # FabPolygon._compute_arcs():
    def _compute_arcs(self) -> None:
        """Create any Arc's needed for non-zero radius _Fillet's."""
        fillet: _Fillet
        for fillet in self._Fillets:
            if fillet.Radius > 0.0:
                fillet.Arc = fillet.compute_arc()

    # FabPolygon._compute_lines():
    def _compute_lines(self) -> None:
        """Create Create any Line's need for _Fillet's."""
        fillet: _Fillet
        for fillet in self._Fillets:
            before: _Fillet = fillet.Before
            start: Vector = before.Arc.Finish if before.Arc else before.Apex
            finish: Vector = fillet.Arc.Start if fillet.Arc else fillet.Apex
            if (start - finish).Length > FabPolygon.EPSILON:
                fillet.Line = _Line(start, finish)

    # FabPolygon.get_geometries():
    def get_geometries(self, contact: Vector, Normal: Vector) -> Tuple[_Geometry, ...]:
        """Return the FabPolygon lines and arcs."""
        geometries: List[_Geometry] = []
        fillet: _Fillet
        for fillet in self._Fillets:
            geometries.extend(fillet.get_geometries())
        return tuple(geometries)

    # FabPolygon._plane_2d_project():
    def _plane_2d_project(self, contact: Vector, normal: Vector) -> None:
        """Update the _Fillet's to be projected onto a Plane.

        Arguments:
        * *contact* (Vector): A point on the plane.
        * *normal* (Vector): A plane normal.

        """
        fillet: _Fillet
        for fillet in self._Fillets:
            fillet.plane_2d_project(contact, normal)

    # FabPolygon.produce():
    def produce(self, context: Dict[str, Any], prefix: str) -> Tuple[Part.Part2DObject, ...]:
        """Produce the FreeCAD objects needed for FabPolygon."""
        # Extract mount plane *contact* and *normal* from *context*:
        mount_contact = cast(Vector, context["mount_contact"])
        mount_normal = cast(Vector, context["mount_normal"])

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
        geometries: Tuple[_Geometry, ...] = self.get_geometries(mount_contact, mount_normal)
        geometry: _Geometry
        index: int
        part_geometries: List[Part.Part2DObject] = []
        for index, geometry in enumerate(geometries):
            part_geometry: Part.Part2DObject = geometry.produce(context, prefix, index)
            assert isinstance(part_geometry, Part.Part2DObject)
            part_geometries.append(part_geometry)
        return tuple(part_geometries)

    # FabPolygon._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Do some unit tests."""
        v1: Vector = Vector(-40, -20, 0)
        v2: Vector = Vector(40, -20, 0)
        v3: Vector = Vector(40, 20, 0)
        v4: Vector = Vector(-40, 20, 0)
        polygon: FabPolygon = FabPolygon((v1, v2, (v3, 10), v4))
        _ = polygon

        # geometries: Tuple[_Geometry, ...] = polygon.get_geometries()
        # index: int
        # geometry: _Geometry
        # for index, geometry in enumerate(geometries):
        #     print(f"Geometry[{index}]: {geometry}")


def main() -> None:
    """Run main program."""
    pass


if __name__ == "__main__":
    FabCircle._unit_tests()
    FabPolygon._unit_tests()
    main()
