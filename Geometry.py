#!/usr/bin/env python3
"""Geometry: A module for constructing 2D geometry."""

# <--------------------------------------- 100 characters ---------------------------------------> #

# Note this code uses nested dataclasses that are frozen.  Computed attributes are tricky.
# See (Set frozen data class files in __post_init__)[https://stackoverflow.com/questions/53756788]

from dataclasses import dataclass, field
import math
from typing import Any, cast, List, Optional, Tuple, Union

import cadquery as cq  # type: ignore
from cadquery import Vector  # type: ignore
from Node import FabBox


# FabPlane:
@dataclass
class FabPlane(object):
    """FabPlane: A Plane class.

    * *Contact* (Vector):  The contact point of the plane.
    * *Normal* (Vector): The normal to the plane.
    """

    _Contact: Vector
    _Normal: Vector
    tracing: str = ""
    _Copy: Vector = field(init=False)
    _Origin: Vector = field(init=False)
    _XDirection: Vector = field(init=False)
    _Plane: Any = field(init=False)  # Used by CadQuery

    # FabPlane.__post_init__():
    def __post_init__(self) -> None:
        """Initialize FabPlane."""
        # Use [Wolfram MathWorld Plane](https://mathworld.wolfram.com/Plane.html) for reference.
        #
        # N is non-unit length vector (Nx, Ny, Nz)   #  Mathworld uses (a, b, c)
        # C is contact point on plane (Cx, Cy, Cz)   #  Mathword uses X0 = (x0, y0, z0)
        #
        # d is "magic" value:
        #
        #     d = -Nx*Cx - Ny*Cy - Nz*Cz
        #       = -(Nx*Cx + Ny*Cy + Nz*Cz)
        #       = -(N . C)
        #
        # (Note that a plane normal can actually be on either side of the of the plane.
        # Apparently, the Wolfram description appears to assume that the normal always
        # point to the origin.  The code below assumes that the normal always points away
        # from the origint.  Hence there is a sign change. Thus, d = N . D is used instead
        # of d = -(N . D).
        #
        # D is the distance from the origin along the normal to the "projected" origin on the plane:
        #
        #     D = d / ||N||    # ||N|| is the length of the normal.
        #
        # This, the origin projected onto the plane is:
        #
        #     O = D * <<N>>    # <<N>> is the unit normal
        tracing: str = self.tracing
        if tracing:
            print(f"{tracing}=>FabPlane.__post_init__({self._Contact}, {self._Normal})")
        next_tracing: str = tracing + " " if tracing else ""

        copy: Vector = Vector(0.0, 0.0, 0.0)
        contact: Vector = self._Contact + copy  # C
        normal: Vector = self._Normal + copy   # N
        d: Vector = normal.dot(contact)  # d = N . C
        normal_length: float = normal.Length  # ||N||
        distance: float = d / normal_length   # D = d / ||N||
        unit_normal: Vector = normal / normal_length  # <<N>>
        origin: Vector = unit_normal * distance   # D * <<N>>
        if tracing:
            print(f"{tracing}{contact=} {normal=}")
            print(f"{tracing}{distance=} {unit_normal=} {origin=}")

        # TODO: This code should be moved inside the USE_CAD_QUERY block!!!
        # Computing the xDir argument to the Plane() constructor is a bit convoluted.
        # This requires taking a unit vector in the +X axis direction and reverse mapping it back
        # to original plane.  This requires the *reversed* option of the *rotate_to_z_axis*
        # method.  Thus, all fields except _Plane are filled in first so that that
        # *rotate_to_z_axis* method can be invoked (since it does not access the _Plane field.)
        self._Contact = contact
        self._Normal = normal
        self._Copy = copy
        self._Origin = origin

        # Rotating *origin* to the +Z axis created *rotated_origin* which is a distance *d*
        # along the +Z axis, where *distance* can be negative:
        rotated_origin: Vector = Vector(0.0, 0.0, distance)

        # *rotated_x_direction* with a unit +X axis vector added to it:
        rotated_x_direction: Vector = rotated_origin + Vector(1.0, 0.0, 0.0)

        # *x_direction* is computed by rotating it back to align with the *normal* and
        # offsetting against *origin*:
        unrotated_x_direction: Vector = self.rotate_to_z_axis(
            rotated_x_direction, reversed=True, tracing=next_tracing)
        assert isinstance(unrotated_x_direction, Vector), unrotated_x_direction
        x_direction: Vector = unrotated_x_direction - origin
        self._XDirection = x_direction
        # Now the Plane* can be created:
        self._Plane = cq.Plane(origin=origin, normal=normal, xDir=x_direction)

        if tracing:
            print(f"{tracing}{rotated_origin=} {rotated_x_direction=}")
            print(f"{tracing}{origin=} {unrotated_x_direction=}")
            print(f"{tracing}{x_direction=}")
            print(f"{tracing}{self._Plane=}")
            print(f"{tracing}<=FabPlane.__post_init__({self._Contact}, {self._Normal})")

    # FabPlane.point_project():
    def point_project(self, point: Vector) -> Vector:
        """Project a point onto a plane."""
        assert isinstance(point, Vector), point
        projected_point: Vector = cast(Vector, None)
        plane: Any = self._Plane
        assert isinstance(plane, cq.Plane)
        projected_point = point.projectToPlane(plane)
        return projected_point

    # FabPlane.Contact():
    @property
    def Contact(self) -> Vector:
        """Return FabPlane Contact."""
        return self._Contact + self._Copy

    # FabPlane.Normal():
    @property
    def Normal(self) -> Vector:
        """Return FabPlane Normal."""
        return self._Normal + self._Copy

    # FablPlane.Origin():
    @property
    def Origin(self) -> Vector:
        """Return FabPlane Origin in 3D space."""
        return self._Origin + self._Copy

    # FabPlane.CQPlane():
    @property
    def CQPlane(self) -> Any:
        """Return the CadQuery plane name as a string."""
        plane: Any = "BOGUS"
        plane = self._Plane
        assert isinstance(plane, cq.Plane), plane
        return plane

    # FabPlne._rotate():
    @staticmethod
    def _rotate(point: Vector,
                axis: Vector, angle: float) -> Tuple[Vector, Tuple[Tuple[float, ...], ...]]:
        """Return a point that has been rotated around an axis.

        Arguments:
        * *point* (Vector): The point to rotate
        * *axis* (Vector): The axis to rotate around.
        * *angle* (float): The number of radians to rotate by.

        Returns:
          * (Vector) The rotated *point*.
        """
        assert isinstance(point, Vector), point
        assert isinstance(axis, Vector), axis
        assert isinstance(angle, float), angle
        # Normalize *angle* to be between -180.0 and 180.0 and convert to radians:
        pi: float = math.pi
        pi2: float = 2.0 * pi
        angle = angle % pi2
        angle = angle if angle <= pi else angle - pi2
        assert -pi <= angle <= pi, f"{angle=}"

        def zf(value: float) -> float:
            """Return zero for values close to zero."""
            return 0.0 if abs(value) < 1.0e-8 else value

        # Compute the X/Y/Z components of a normal vector of *length* 1.
        nx: float = zf(axis.x)
        ny: float = zf(axis.y)
        nz: float = zf(axis.z)
        length: float = math.sqrt(nx * nx + ny * ny + nz * nz)
        if length <= 0.0:
            raise ValueError("Axis has a length of 0.0")
        nx = zf(nx / length)
        ny = zf(ny / length)
        nz = zf(nz / length)

        # The matrix for rotating by *angle* around the normal *axis* is:
        #
        #     [ xx(1-c)+c   xy(1-c)+zs  xz(1-c)-ys   0  ]
        #     [ yx(1-c)-zs  yy(1-c)+c   yz(1-c)+xs   0  ]
        #     [ zx(1-c)+ys  zy(1-c)-xs  zz(1-c)+c    0  ]
        #     [ 0           0           0            1  ]

        # Compute some sub expressions:
        c = math.cos(angle)
        s = math.sin(angle)
        omc = 1.0 - c  # *omc* stands for One Minus *c*.
        x_omc = nx * omc
        y_omc = ny * omc
        z_omc = nz * omc
        xs = nx * s
        ys = ny * s
        zs = nz * s

        # For some reason the Vector.transform method() always throws an exception:
        #   OCP.Standard.Standard_ConstructionError: gp_GTrsf::Trsf() - non-orthogonal GTrsf
        # on matrices that are clearly orthogonal (i.e. M * Mt = I, where Mt is the M transpose.)
        # As a work around, skip cq.Vector and cq.Matrix, create the 3x3 rotation coefficients,
        # and manually, do the point (1x3) by roatation matrix (3x3) and get the rotated
        # point (1x3).
        #
        # matrix: cq.Matrix = cq.Matrix([
        #     [zf(nx * x_omc + c), zf(nx * y_omc - zs), zf(nx * z_omc + ys), 0.0],
        #     [zf(ny * x_omc + zs), zf(ny * y_omc + c), zf(ny * z_omc - xs), 0.0],
        #     [zf(nz * x_omc - ys), zf(nz * y_omc + xs), zf(nz * z_omc + c), 0.0],
        # ])
        m00: float = zf(nx * x_omc + c)
        m01: float = zf(nx * y_omc - zs)
        m02: float = zf(nx * z_omc + ys)
        m10: float = zf(ny * x_omc + zs)
        m11: float = zf(ny * y_omc + c)
        m12: float = zf(ny * z_omc - xs)
        m20: float = zf(nz * x_omc - ys)
        m21: float = zf(nz * y_omc + xs)
        m22: float = zf(nz * z_omc + c)
        x: float = point.x
        y: float = point.y
        z: float = point.z
        rx: float = x * m00 + y * m10 + z * m20
        ry: float = x * m01 + y * m11 + z * m21
        rz: float = x * m02 + y * m12 + z * m22
        rotated_point: Vector = Vector(rx, ry, rz)
        return (rotated_point, ((m00, m10, m20), (m01, m11, m21), (m02, m12, m22)))

    # FabPlane.rotate_to_z_axis():
    def rotate_to_z_axis(self, point: Vector, reversed: bool = False, tracing: str = "") -> Vector:
        """Rotate a point around the origin until the normal aligns with the +Z axis.

        Arguments:
        * *point* (Vector): The point to rotate.
        * *reversed* (bool = False): If True, do the inverse rotation.

        Returns:
        * (Vector): The rotated vector position.

        """

        if tracing:
            print(f"{tracing}=>FabPlane.rotate_to_z_axis({point})")
        rotated_point: Vector = cast(Vector, None)  # Force failure if something is broken.

        z_axis: Vector = Vector(0.0, 0.0, 1.)
        plane_normal: Vector = self._Normal
        plane_normal = plane_normal / plane_normal.Length

        if tracing:
            print(f"{tracing}{plane_normal=}")

        to_axis: Vector = plane_normal if reversed else z_axis
        from_axis: Vector = z_axis if reversed else plane_normal
        if tracing:
            print(f"{tracing}{to_axis=}{from_axis=}")

        epsilon: float = 1.0e-5
        rotate_axis: Vector
        rotate_angle: float
        if abs((from_axis - to_axis).Length) < epsilon:
            if tracing:
                print(f"{tracing}Aligned with +Z axis")
            rotate_angle = 0.0
            rotate_axis = Vector(0.0, 0.0, 1.0)
        else:
            if abs((from_axis + to_axis).Length) < epsilon:
                if tracing:
                    print(f"{tracing}Aligned with -Z axis")
                y_axis: Vector = Vector(0.0, 1.0, 0.0)
                rotate_axis = y_axis
                rotate_angle = -math.pi  # 180 degrees
            else:
                rotate_axis = to_axis.cross(from_axis)
                rotate_angle = to_axis.getAngle(from_axis)
                if tracing:
                    rotate_degrees: float = math.degrees(rotate_angle)
                    print(f"{tracing}{rotate_axis=} {rotate_degrees=}")
        # Rotate the point:
        rotated_point, rotate_matrix = FabPlane._rotate(point, rotate_axis, rotate_angle)

        if tracing:
            print(f"{tracing}<=FabPlane.rotate_to_z_axis({point})=>{rotated_point}")
        return rotated_point


# FabGeometryContext:
@dataclass
class FabGeometryContext(object):
    """GeometryProduce: Context needed to produce FreeCAD geometry objects.

    Attributes:
    * *Plane* (Plane): Plane to use.
    * *WorkPlane* (FabWorkPlane): The CadQuery Workplane wrapper to use.
    * *GeometryGroup*: (App.DocumentObjectGroup):
      The FreeCAD group to store FreeCAD Geometry objects into.
      This field needs to be set prior to use with set_geometry_group() method.

    """

    _Plane: FabPlane
    _WorkPlane: "FabWorkPlane"
    _geometry_group: Optional[Any] = field(init=False, repr=False)
    _copy: Vector = field(init=False, repr=False)

    # FabGeometryContext.__post_init__():
    def __post_init__(self) -> None:
        """Initialize FabGeometryContex."""

        if not isinstance(self._Plane, FabPlane):
            raise RuntimeError(
                f"FabGeometryContext.__post_init__(): {type(self._Plane)} is not a FabPlane")
        if not isinstance(self._WorkPlane, FabWorkPlane):
            raise RuntimeError(
                "FabGeometryContext.__post_init__(): "
                f"{type(self._WorkPlane)} is not a FabWorkPlane")

        copy: Vector = Vector()
        self._copy: Vector = copy
        self._GeometryGroup = None  # Set with set_geometry_group() method

    # FabGeometryContext.Plane():
    @property
    def Plane(self) -> FabPlane:
        """Return the FabPlane."""
        return self._Plane

    # FabGeometryContext.WorkPlane():
    @property
    def WorkPlane(self) -> Any:
        """Return the FabQuery Workplane."""
        return self._WorkPlane

    # FabGeometryContext.WorkPlane.setter():
    @WorkPlane.setter
    def WorkPlane(self, workplane: Any):
        """Set the FabQuery Workplane."""
        if not isinstance(workplane, cq.Workplane):
            raise RuntimeError(
                f"FabGeomtery.WorkPlane(): Workplane {type(workplane)}, not workplane.")
        self._WorkPlane = workplane

    # FabGeometryContext.GeometryGroup():
    @property
    def GeometryGroup(self) -> Any:
        """Return FabGeometry normal tSo 2D plane."""
        if not self._GeometryGroup:
            raise RuntimeError("FabGeometryContext.GeometryGroup(): not set yet; must be set")
        return self._GeometryGroup

    # FabGeometryContext.copy():
    def copy(self, tracing: str = "") -> "FabGeometryContext":
        """Return a FabGeometryContext copy."""
        # next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}<=>FabGeometryContext.copy()")
        new_work_plane: FabWorkPlane = FabWorkPlane(self._Plane)
        return FabGeometryContext(self._Plane, new_work_plane)

    # FabGeometryContext.set_geometry_Group():
    def set_geometry_group(self, geometry_group: Any) -> None:
        """Set the GeometryContext geometry group."""
        # if not isinstance(geometry_group, App.DocumentObjectGroup):
        #     raise RuntimeError(f"FabGeometryContext.set_geometry_grouop(): "
        #                        f"{type(geometry_group)} is not App.DocumentObjectGroup")
        self._GeometryGroup = geometry_group


# _Geometry:
@dataclass(frozen=True)
class _Geometry(object):
    """_Geometry: An Internal base class for _Arc, _Circle, and _Line.

    All _Geometry classes are immutable (i.e. frozen.)
    """

    # _Geometry.produce():
    def produce(self, geometry_context: FabGeometryContext, prefix: str,
                index: int, tracing: str = "") -> Any:
        raise NotImplementedError(f"{type(self)}.produce() is not implemented yet")

    # _Geometry.Start():
    def get_start(self) -> Vector:
        """Return start point of geometry."""
        raise NotImplementedError(f"{type(self)}.get_start() is not implemented yet")


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

    # _Arc.produce():
    def produce(self, geometry_context: FabGeometryContext, prefix: str,
                index: int, tracing: str = "") -> Any:
        """Return line segment after moving it into Geometry group."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>_Arc.produce(*, '{prefix}', {index})")

        part_arc: Any = None
        plane: FabPlane = geometry_context._Plane
        rotated_middle: Vector = plane.rotate_to_z_axis(self.Middle, tracing=next_tracing)
        rotated_finish: Vector = plane.rotate_to_z_axis(self.Finish, tracing=next_tracing)
        geometry_context.WorkPlane.three_point_arc(
            rotated_middle, rotated_finish, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=_Arc.produce(*, '{prefix}', {index})=>{part_arc}")
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
    def produce(self, geometry_context: FabGeometryContext, prefix: str,
                index: int, tracing: str = "") -> Any:
        """Return line segment after moving it into Geometry group."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>_Circle.produce()")
        plane: FabPlane = geometry_context.Plane
        center_on_plane: Vector = plane.point_project(self.Center)
        part_circle: Any = None
        work_plane: FabWorkPlane = geometry_context.WorkPlane
        work_plane.circle(center_on_plane, self.Diameter / 2, tracing=next_tracing)

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

    # _Line.get_start():
    def get_start(self) -> Vector:
        """Return the start point of the _Line."""
        return self.Start

    # _Line.produce():
    def produce(self, geometry_context: FabGeometryContext, prefix: str,
                index: int, tracing: str = "") -> Any:
        """Return line segment after moving it into Geometry group."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>_Line.produce()")

        line_segment: Any = None
        plane: FabPlane = geometry_context._Plane
        rotated_finish: Vector = plane.rotate_to_z_axis(self.Finish, tracing=next_tracing)
        if tracing:
            print(f"{tracing}{self.Finish} ==> {rotated_finish}")
        geometry_context.WorkPlane.line_to(rotated_finish, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=_Line.produce()=>{line_segment}")
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
        # Each fillet specifies an 3D center point and a radius.  The the fillet the corner point is
        # X and the radius is r.  Each fillet also has two neighbors on the polygon (called before
        # and after) and each of the respectively have corner points called B and A.  These three
        # points specify line segment XB and XA respectively.  XB and XA also specify a plane
        # called AXB.  The goal is to find a center point C of a sphere of radius r that is on
        # the plane AXB and it tangent to line segments XB and XA.  (If r too large, there is no
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
        # 8. The arc middle point M is computed using X, <XC>, |XC| and r.

        # Step 0: Extract *radius*, *before* (B), *apex* (X) and *after* (A) points:
        radius: float = self.Radius
        before: Vector = self.Before.Apex
        apex: Vector = self.Apex
        after: Vector = self.After.Apex
        if tracing:
            print(f"{tracing}=>_Fillet.compute_arc()")
            print(f"{tracing}{radius=} {before=} {apex=} {after=}")

        # Steps 1 and 2: Compute unit vectors <XB>, <XA>, and <XC>
        apex_to_before: Vector = before - apex
        unit_before: Vector = apex_to_before / apex_to_before.Length  # <XB>
        apex_to_after: Vector = after - apex
        unit_after: Vector = apex_to_after / apex_to_after.Length  # <XA>
        to_center: Vector = unit_before + unit_after
        unit_center: Vector = to_center / to_center.Length  # <XC>
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
            print(f"{tracing}<=_Fillet.compute_arc()=>{arc}")
        return arc

    # _Fillet.plane_2d_project:
    def plane_2d_project(self, plane: FabPlane) -> None:
        """Project the Apex onto a plane.

        Arguments:
        * *plane* (FabPlane): The plane to project the _Fillet onto.

        Modifies _Fillet.

        """
        # FreeCAD Vector metheds like to modify Vector contents; force copies beforehand:
        self.Apex = plane.point_project(self.Apex)

    # _Fillet.get_geometries():
    def get_geometries(self) -> Tuple[_Geometry, ...]:
        geometries: List[_Geometry] = []
        if self.Line:
            geometries.append(self.Line)
        if self.Arc:
            geometries.append(self.Arc)
        return tuple(geometries)

    # _Fillet.unit_tests():
    @staticmethod
    def unit_tests() -> None:
        # Create 4 corners centered.
        dx: float = Vector(20.0, 0.0, 0.0)
        dy: float = Vector(0.0, 10.0, 0.0)
        radius: float = 4.0

        # Create the corner Vector's:
        center: Vector = Vector(0.0, 0.0, 0.0)
        ne_corner: Vector = Vector(center + dx + dy)
        nw_corner: Vector = Vector(center - dx + dy)
        sw_corner: Vector = Vector(center - dx - dy)
        se_corner: Vector = Vector(center + dx - dy)

        # Create the _Fillet's:
        ne_fillet: _Fillet = _Fillet(ne_corner, radius)
        nw_fillet: _Fillet = _Fillet(nw_corner, radius)
        sw_fillet: _Fillet = _Fillet(sw_corner, radius)
        se_fillet: _Fillet = _Fillet(se_corner, radius)

        # Provide before/after _Fillets:
        ne_fillet.Before = se_fillet
        nw_fillet.Before = ne_fillet
        sw_fillet.Before = nw_fillet
        se_fillet.Before = sw_fillet
        ne_fillet.After = nw_fillet
        nw_fillet.After = sw_fillet
        sw_fillet.After = se_fillet
        se_fillet.After = ne_fillet

        ne_fillet.compute_arc(tracing="NE:")
        nw_fillet.compute_arc(tracing="NW:")
        sw_fillet.compute_arc(tracing="SW:")
        se_fillet.compute_arc(tracing="SE:")


# FabGeometry:
@dataclass(frozen=True)
class FabGeometry(object):
    """FabGeometry: The base class for FabPolygon and FabCircle."""

    # FabGeometry.Box():
    @property
    def Box(self) -> FabBox:
        """Return a FabBox that encloses the FabGeometry."""
        raise NotImplementedError(f"{type(self)}.Box() is not implemented")

    # FabGeometry.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return FabGeometry hash."""
        raise NotImplementedError(f"{type(self)}.get_hash() is not implemented")

    # FabGeometry.produce():
    def produce(self, geometry_context: FabGeometryContext, prefix: str,
                index: int, tracing: str = "") -> Tuple[Any, ...]:
        """Produce the necessary FreeCAD objects for the FabGeometry."""
        raise NotImplementedError(f"{type(self)}.produce() is not implemented")

    # FabGeometry.project_to_plane():
    def project_to_plane(self, plane: FabPlane) -> "FabGeometry":
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

    # FabCircle.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Feturn FabCircle hash."""
        center: Vector = self.Center
        normal: Vector = self.Normal
        hashes: Tuple[Union[int, str, Tuple[Any, ...]], ...] = (
            "FabCircle.get_hash",
            f"{center.x:.6f}",
            f"{center.y:.6f}",
            f"{center.z:.6f}",
            f"{normal.x:.6f}",
            f"{normal.y:.6f}",
            f"{normal.z:.6f}",
            f"{self.Diameter:.6f}",
        )
        return hashes

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
    def project_to_plane(self, plane: FabPlane, tracing: str = "") -> "FabCircle":
        """Return a new FabCircle projected onto a plane.

        Arguments:
        * *plane* (FabPlane): Plane to proejct to.

        Returns:
        * (FabCircle): The newly projected FabCicle.

        """
        if tracing:
            print(f"{tracing}=>FabCircle.project_to_plane({plane})")
        center: Vector = self.Center
        new_center: Vector = plane.point_project(center)
        new_circle: "FabCircle" = FabCircle(new_center, plane.Normal, self.Diameter)
        if tracing:
            print(f"{tracing}<=FabCircle.project_to_plane({plane}) => {new_circle}")
        return new_circle

    # FabCircle.produce():
    def produce(self, geometry_context: FabGeometryContext, prefix: str,
                index: int, tracing: str = "") -> Tuple[Any, ...]:
        """Produce the FreeCAD objects needed for FabPolygon."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabCircle.produce()")
        geometries: Tuple[_Geometry, ...] = self.get_geometries()
        geometry: _Geometry
        part_geometries: List[Any] = []
        for index, geometry in enumerate(geometries):
            part_geometry: Any = geometry.produce(
                geometry_context, prefix, index, tracing=next_tracing)
            # assert isinstance(part_geometry, Any)
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

    # FabPolygon.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return the FabPolygon Hash."""
        hashes: List[Union[int, str, Tuple[Any, ...]]] = ["FabPolygon"]
        corner: Union[Vector, Tuple[Vector, Union[int, float]]]
        for corner in self.Corners:
            if isinstance(corner, Vector):
                corner = (corner, 0.0)
            point: Vector
            radius: float
            point, radius = corner
            hashes.append(f"{point.x:.6f}")
            hashes.append(f"{point.y:.6f}")
            hashes.append(f"{point.z:.6f}")
            hashes.append(f"{radius:.6f}")
        return tuple(hashes)

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
    def project_to_plane(self, plane: FabPlane, tracing: str = "") -> "FabPolygon":
        """Return nre FabPolygon prejected onto a plane.

        Arguments:
        * *plane* (FabPlane): The plane to project onto.

        Returns:
        * (FabPolyGon): The newly projected FabPolygon.

        """
        if tracing:
            print(f"{tracing}=>FabPolygon.project_to_plane({plane})")
        corner: Union[Vector, Tuple[Vector, Union[int, float]]]
        projected_corners: List[Union[Vector, Tuple[Vector, Union[int, float]]]] = []
        for corner in self.Corners:
            if isinstance(corner, Vector):
                projected_corners.append(plane.point_project(corner))
            elif isinstance(corner, tuple):
                assert len(corner) == 2
                point: Any = corner[0]
                radius: Any = corner[1]
                assert isinstance(point, Vector)
                assert isinstance(radius, (int, float))
                projected_corners.append(plane.point_project(point))
        projected_polygon: "FabPolygon" = FabPolygon(tuple(projected_corners))
        if tracing:
            print(f"{tracing}<=FabPolygon.project_to_plane({plane})=>*")
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
    def _plane_2d_project(self, plane: FabPlane) -> None:
        """Update the _Fillet's to be projected onto a Plane.

        Arguments:
        * *plane* (FabPlane): The plane to modify the _Fillet's to be on.

        """
        fillet: _Fillet
        for fillet in self._Fillets:
            fillet.plane_2d_project(plane)

    # FabPolygon.produce():
    def produce(self, geometry_context: FabGeometryContext, prefix: str,
                index: int, tracing: str = "") -> Tuple[Any, ...]:
        """Produce the FreeCAD objects needed for FabPolygon."""
        # Extract mount plane *contact* and *normal* from *geometry_context*:
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabPolygon.produce(*, '{prefix}', {index})")
        part_geometry: Any
        assert isinstance(geometry_context, FabGeometryContext), geometry_context
        plane_contact: Vector = geometry_context.Plane.Contact
        plane_normal: Vector = geometry_context.Plane.Normal
        plane: FabPlane = FabPlane(plane_contact, plane_normal)

        # Use *contact*/*normal* for 2D projection:
        self._plane_2d_project(plane)

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
        geometries: Tuple[_Geometry, ...] = self.get_geometries(plane_contact, plane_normal)
        part_geometries: List[Any] = []

        if not geometries:
            raise RuntimeError("FabPolygon.produce(): empty geometries.")
        geometry0: _Geometry = geometries[0]
        start: Vector = geometry0.get_start()
        rotated_start: Vector = geometry_context._Plane.rotate_to_z_axis(
            start, tracing=next_tracing)
        geometry_context.WorkPlane.move_to(rotated_start, tracing=next_tracing)
        # TODO: Does this loop do anything anymore?
        for index, geometry in enumerate(geometries):
            part_geometry = geometry.produce(
                geometry_context, prefix, index, tracing=next_tracing)
            _ = part_geometry
        geometry_context.WorkPlane.close(tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=FabPolygon.produce(*, '{prefix}', {index})=>*")
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


# FabWorkPlane:
@dataclass
class FabWorkPlane(object):
    """FabWorkPlane: A CadQuery Workplane wrapper.

    This class creates CadQuery Workplane provides a consistent head of the Workplane chain..
    CadQuery Operations are added as needed.

    Attributes:
    * *Plane* (FabPlane): The plain to use for CadQuery initialization.
    * *WorkPlane: (cadquery.Workplane): The resulting CadQuery Workplane object.

    """
    _Plane: FabPlane
    _WorkPlane: Any = field(init=False, repr=False, default=None)

    # FabWorkPlane.__post_init__():
    def __post_init__(self) -> None:
        """Initialize FabPlane"""
        if not isinstance(self._Plane, FabPlane):
            raise RuntimeError(
                f"FabWorkPlane.__post_init__(): Got {type(self._Plane)}, not FabPlane")
        plane = cast(cq.Plane, self._Plane._Plane)
        self._WorkPlane = cq.Workplane(plane)

    # FabWorkPlane.Plane():
    @property
    def Plane(self) -> FabPlane:
        """Return the FabPlane associated from a FabWorkPlane."""
        assert isinstance(self._Plane, FabPlane), self._Plane
        return self._Plane

    # FabWorkPlane.WorkPlane():
    @property
    def WorkPlane(self) -> Any:
        """Return the Workplane associated from a FabWorkPlane."""
        return self._WorkPlane

    # FabWorkPlane.circle():
    def circle(self, center: Vector, radius: float,
               for_construction=False, tracing: str = "") -> None:
        """Draw a circle to a point."""
        if tracing:
            print(f"{tracing}<=>FabWorkPlane.circle({center}, {radius}, {for_construction})")
        rotated_center: Vector = self._Plane.rotate_to_z_axis(center)
        self._WorkPlane = (
            cast(cq.Workplane, self._WorkPlane)
            .moveTo(rotated_center.x, rotated_center.y)
            .circle(radius, for_construction)
        )

    # FabWorkPlane.close():
    def close(self, tracing: str = "") -> None:
        """Close a sequence of arcs and lines."""
        if tracing:
            print(f"{tracing}<=>FabWorkPlane.close()")
        self._WorkPlane = (
            cast(cq.Workplane, self._WorkPlane)
            .close()
        )

    # FabWorkPlane.copy_workplane():
    def copy_workplane(self, plane: FabPlane, tracing: str = "") -> None:
        """Create a new CadQuery workplane and push it onto the stack."""
        if tracing:
            print(f"{tracing}=>FabWorkPlane.copy_workPlane({plane})")
        if not isinstance(plane, FabPlane):
            raise RuntimeError(
                f"FabWorkPlane.copy_workplane(): Got {type(plane)}, not FabPlane")
        if tracing:
            print(f"{tracing}{plane=}")
        self._WorkPlane = (
            cast(cq.Workplane, self._WorkPlane)
            .copyWorkplane(cq.Workplane(plane.CQPlane))
        )
        if tracing:
            print(f"{tracing}<=FabWorkPlane.copy_workPlane({plane})")

    # FabWorkPlane.cut():
    def cut_blind(self, depth: float, tracing: str = "") -> None:
        """Use the current 2D object to cut a pocket to a known depth."""
        if tracing:
            print(f"{tracing}<=>FabWorkPlane.cut_blind({depth})")
        self._WorkPlane = (
            cast(cq.Workplane, self._WorkPlane)
            .cutBlind(depth)
        )

    # FabWorkPlane.extrude():
    def extrude(self, depth: float, tracing: str = "") -> None:
        """Extrude current 2D object to a known depth."""
        if tracing:
            print(f"{tracing}<=>FabWorkPlane.extrude({depth})")
        self._WorkPlane = (
            cast(cq.Workplane, self._WorkPlane)
            .extrude(-depth)
        )

    # FabWorkPlane.hole():
    def hole(self, diameter: float, depth: float, tracing: str = "") -> None:
        """Drill a hole."""
        if tracing:
            print(f"{tracing}=>FabWorkPlane.hole({diameter}, {depth})")
        self._WorkPlane = (
            cast(cq.Workplane, self._WorkPlane)
            .hole(diameter=diameter, depth=depth)
        )
        if tracing:
            print(f"{tracing}<=FabWorkPlane.hole({diameter}, {depth})")

    # FabWorkPlane.line_to():
    def line_to(self, end: Vector, for_construction=False, tracing: str = "") -> None:
        """Draw a line to a point."""
        if tracing:
            print(f"{tracing}=>FabWorkPlane.line_to({end}, {for_construction})")
        end_tuple: Tuple[float, float] = (end.x, end.y)
        self._WorkPlane = (
            cast(cq.Workplane, self._WorkPlane)
            .lineTo(end.x, end.y)
        )
        if tracing:
            print(f"{tracing}{end_tuple=}")
            print(f"{tracing}<=FabWorkPlane.line_to({end}, {for_construction})")

    # FabWorkPlane.move_to():
    def move_to(self, point: Vector, tracing: str = "") -> None:
        """Draw a line to a point."""
        if tracing:
            print(f"{tracing}=>FabWorkPlane.move_to({point})")
            print(f"{tracing}{self._WorkPlane.plane=}")
        assert isinstance(point, Vector), point
        self._WorkPlane = (
            cast(cq.Workplane, self._WorkPlane)
            .moveTo(point.x, point.y)
        )
        if tracing:
            print(f"{tracing}<=FabWorkPlane.move_to({point})")

    # FabWorkPlane.show():
    def show(self, label: str, tracing: str = "") -> None:
        """Print a detailed dump of a FabWorkPlane."""
        # This is basically copied from the section "An Introspective Example" in the
        # CadQuery documentation.

        def tidy_repr(obj) -> str:
            """ Shortens a default repr string."""
            return repr(obj).split('.')[-1].rstrip('>')

        def _ctx_str(self):
            return (
                tidy_repr(self) + ":\n" +
                f"{tracing}    pendingWires: {self.pendingWires}\n" +
                f"{tracing}    pendingEdges: {self.pendingEdges}\n" +
                f"{tracing}    tags: {self.tags}"
            )

        def _plane_str(self) -> str:
            return (
                tidy_repr(self) + ":\n" +
                f"{tracing}    origin: {self.origin.toTuple()}\n" +
                f"{tracing}    z direction: {self.zDir.toTuple()}"
            )

        def _wp_str(self) -> str:
            out = tidy_repr(self) + ":\n"
            out += (f"{tracing}  parent: {tidy_repr(self.parent)}\n"
                    if self.parent else f"{tracing}  no parent\n")
            out += f"{tracing}  plane: {self.plane}\n"
            out += f"{tracing}  objects: {self.objects}\n"
            out += f"{tracing}  modelling context: {self.ctx}"
            return out

        # Save *previous_functions*:
        previous_functions: Tuple[Any, Any, Any] = (
            cq.cq.CQContext.__str__,
            cq.occ_impl.geom.Plane.__str__,
            cq.Workplane.__str__
        )

        # Install *new_functions*
        new_functions: Tuple[Any, Any, Any] = (_ctx_str, _plane_str, _wp_str)
        (cq.cq.CQContext.__str__, cq.occ_impl.geom.Plane.__str__,
         cq.Workplane.__str__) = new_functions

        # Now print the the contents:
        if tracing:
            print(f"{tracing}Label: {label}")
            print(f"{tracing}{self._WorkPlane}")

        # Now restore the *previous_functions*:
        (cq.cq.CQContext.__str__, cq.occ_impl.geom.Plane.__str__,
         cq.Workplane.__str__) = previous_functions

    # FabWorkPlane.subtract():
    def subtract(self, remove_solid: "FabWorkPlane", tracing: str = "") -> None:
        """Subtract one solid form a FabWorkPlane."""
        if tracing:
            print(f"{tracing}<=>FabWorkPlane.subtract()")
        self._WorkPlane = (
            cast(cq.Workplane, self._WorkPlane) -
            remove_solid.WorkPlane
        )

    # FabWorkPlane.three_point_arc():
    def three_point_arc(self, middle: Vector, end: Vector,
                        for_construction: bool = False, tracing: str = "") -> None:
        """Draw a three point arc."""
        if tracing:
            print(f"{tracing}=>FabWorkPlane.three_point_arc({middle}), {end})")
        middle_tuple: Tuple[float, float] = (middle.x, middle.y)
        end_tuple: Tuple[float, float] = (end.x, end.y)
        self._WorkPlane = (
            cast(cq.Workplane, self._WorkPlane)
            .threePointArc(middle_tuple, end_tuple)
        )
        if tracing:
            print(f"{tracing}{middle_tuple=} {end_tuple=}")
            print(f"{tracing}<=FabWorkPlane.three_point_arc({middle}), {end})")


def main() -> None:
    """Run main program."""
    pass


if __name__ == "__main__":
    _Fillet.unit_tests()
    FabCircle._unit_tests()
    FabPolygon._unit_tests()
    main()
