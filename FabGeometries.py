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
from FabNodes import FabBox


# Fab_Plane:
@dataclass
class Fab_Plane(object):
    """Fab_Plane: A Plane class.

    * *Contact* (Vector):  The contact point of the plane.
    * *Normal* (Vector): The normal to the plane.
    """

    _Contact: Vector
    _Normal: Vector
    tracing: str = ""  # TODO: Remove. For dataclass sub-classing, optional value are disallowed.)
    _UnitNormal: Vector = field(init=False, repr=False)
    _Distance: float = field(init=False, repr=False)
    _Copy: Vector = field(init=False, repr=False)
    _Origin: Vector = field(init=False)
    _XDirection: Vector = field(init=False)
    _Plane: Any = field(init=False, repr=False)  # Used by CadQuery

    # Fab_Plane.__post_init__():
    def __post_init__(self) -> None:
        """Initialize Fab_Plane."""
        # Use [Wolfram MathWorld Plane](https://mathworld.wolfram.com/Plane.html) for reference.
        #
        # N is non-unit length vector (Nx, Ny, Nz)   #  Mathworld uses (a, b, c)
        # C is contact point on plane (Cx, Cy, Cz)   #  Mathworld uses X0 = (x0, y0, z0)
        #
        # d is "magic" value:
        #
        #     d = -Nx*Cx - Ny*Cy - Nz*Cz
        #       = -(Nx*Cx + Ny*Cy + Nz*Cz)
        #       = -(N . C)
        #
        # (Note that a plane normal can actually be on either side of the of the plane.
        # Apparently, the Wolfram description appears to assume that the normal always
        # points to the origin.  The code below assumes that the normal always points away
        # from the origin.  Hence there is a sign change. Thus, d = N . D is used instead
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
            print(f"{tracing}=>Fab_Plane.__post_init__({self._Contact}, {self._Normal})")
        next_tracing: str = tracing + " " if tracing else ""

        copy: Vector = Vector(0.0, 0.0, 0.0)
        contact: Vector = self._Contact + copy  # C
        normal: Vector = self._Normal + copy   # N
        d: float = normal.dot(contact)  # d = N . C
        normal_length: float = normal.Length  # ||N||
        distance: float = d / normal_length   # D = d / ||N||
        unit_normal: Vector = normal / normal_length  # <<N>>
        origin: Vector = unit_normal * distance   # D * <<N>>
        if tracing:
            print(f"{tracing}{contact=} {normal=}")
            print(f"{tracing}{distance=} {unit_normal=} {origin=}")

        # Computing the xDir argument to the Plane() constructor is a bit convoluted.
        # This requires taking a unit vector in the +X axis direction and reverse mapping it back
        # to original plane.  This requires the *reversed* option of the *rotate_to_z_axis*
        # method.  Thus, all fields except _Plane are filled in first so that that
        # *rotate_to_z_axis* method can be invoked (since it does not access the _Plane field.)
        self._UnitNormal = unit_normal
        self._Contact = contact
        self._Distance = distance
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
            print(f"{tracing}<=Fab_Plane.__post_init__({self._Contact}, {self._Normal})")

    # Fab_Plane.point_project():
    def point_project(self, point: Vector) -> Vector:
        """Project a point onto a plane."""
        assert isinstance(point, Vector), point
        projected_point: Vector = cast(Vector, None)
        plane: Any = self._Plane
        assert isinstance(plane, cq.Plane)
        projected_point = point.projectToPlane(plane)
        return projected_point

    # Fab_Plane.Contact():
    @property
    def Contact(self) -> Vector:
        """Return Fab_Plane Contact."""
        return self._Contact + self._Copy

    # Fab_Plane.Normal():
    @property
    def Normal(self) -> Vector:
        """Return Fab_Plane Normal."""
        return self._Normal + self._Copy

    # Fab_Plane.UnitNormal():
    @property
    def UnitNormal(self) -> Vector:
        """Return Fab_Plane Normal."""
        return self._UnitNormal + self._Copy

    # Fab_Plane.Distance():
    @property
    def Distance(self) -> float:
        """Return Fab_Plane distance along the normal."""
        return self._Distance

    # FablPlane.Origin():
    @property
    def Origin(self) -> Vector:
        """Return Fab_Plane Origin in 3D space."""
        return self._Origin + self._Copy

    # Fab_Plane.adjust():
    def adjust(self, delta: float) -> "Fab_Plane":
        """Return a new Fab_Plane that has been adjusted up/down the normal by a delta."""
        origin: Vector = self.Origin
        unit_normal: Vector = self.UnitNormal
        new_origin: Vector = origin + delta * unit_normal
        # Both the contact and the normal can be *new_origin*:
        adjusted_plane: Fab_Plane = Fab_Plane(new_origin, new_origin)
        return adjusted_plane

    # Fab_Plane.CQPlane():
    @property
    def CQPlane(self) -> Any:
        """Return the associated CadQuery Plane."""
        plane: Any = self._Plane
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
            raise ValueError("Axis has a length of 0.0")  # pragma: no unit cover
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
        # and manually, do the point (1x3) by rotation matrix (3x3) and get the rotated
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

    # Fab_Plane.rotate_to_z_axis():
    def rotate_to_z_axis(self, point: Vector, reversed: bool = False, tracing: str = "") -> Vector:
        """Rotate a point around the origin until the normal aligns with the +Z axis.

        Arguments:
        * *point* (Vector): The point to rotate.
        * *reversed* (bool = False): If True, do the inverse rotation.

        Returns:
        * (Vector): The rotated vector position.

        """

        if tracing:
            print(f"{tracing}=>Fab_Plane.rotate_to_z_axis({point})")
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
        rotated_point, rotate_matrix = Fab_Plane._rotate(point, rotate_axis, rotate_angle)

        if tracing:
            print(f"{tracing}<=Fab_Plane.rotate_to_z_axis({point})=>{rotated_point}")
        return rotated_point


# Fab_GeometryContext:
@dataclass
class Fab_GeometryContext(object):
    """GeometryProduce: Context needed to produce FreeCAD geometry objects.

    Attributes:
    * *Plane* (Fab_Plane): Plane to use.
    * *Query* (Fab_Query): The CadQuery Workplane wrapper to use.
    * *_GeometryGroup*: (App.DocumentObjectGroup):
      The FreeCAD group to store FreeCAD Geometry objects into.
      This field needs to be set prior to use with set_geometry_group() method.

    """

    _Plane: Fab_Plane
    _Query: "Fab_Query"
    _geometry_group: Optional[Any] = field(init=False, repr=False)  # TODO: Is this used any more?
    _copy: Vector = field(init=False, repr=False)  # TODO: Is this used any more?

    # Fab_GeometryContext.__post_init__():
    def __post_init__(self) -> None:
        """Initialize FabGeometryContex."""

        if not isinstance(self._Plane, Fab_Plane):
            raise RuntimeError(
                f"Fab_GeometryContext.__post_init__(): "
                f"{type(self._Plane)} is not a Fab_Plane")  # pragma: no unit cover
        if not isinstance(self._Query, Fab_Query):
            raise RuntimeError(
                "Fab_GeometryContext.__post_init__(): "
                f"{type(self._Query)} is not a Fab_Query")  # pragma: no unit cover

        copy: Vector = Vector()
        self._copy: Vector = copy
        self._GeometryGroup = None  # Set with set_geometry_group() method

    # Fab_GeometryContext.Plane():
    @property
    def Plane(self) -> Fab_Plane:
        """Return the Fab_Plane."""
        return self._Plane

    # Fab_GeometryContext.Query():
    @property
    def Query(self) -> Any:
        """Return the Fab_Query.."""
        return self._Query

    # Fab_GeometryContext.GeometryGroup():
    # @property
    # def GeometryGroup(self) -> Any:
    #     """Return FabGeometry normal tSo 2D plane."""
    #     if not self._GeometryGroup:
    #         raise RuntimeError(
    #             "Fab_GeometryContext.GeometryGroup(): "
    #             "not set yet; must be set")  # pragma: no unit cover
    #     return self._GeometryGroup

    # Fab_GeometryContext.copy():
    def copy(self, tracing: str = "") -> "Fab_GeometryContext":
        """Return a Fab_GeometryContext copy."""
        # next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}<=>Fab_GeometryContext.copy()")
        new_query: Fab_Query = Fab_Query(self._Plane)
        return Fab_GeometryContext(self._Plane, new_query)

    # Fab_GeometryContext.copy_with_plane_adjust():
    def copy_with_plane_adjust(self, delta: float, tracing: str = "") -> "Fab_GeometryContext":
        """Return a Fab_GeometryContext copy with the plane adjusted up/down."""
        # next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}<=>Fab_GeometryContext.copy()")
        adjusted_plane: Fab_Plane = self._Plane.adjust(delta)
        new_query: Fab_Query = Fab_Query(adjusted_plane)
        return Fab_GeometryContext(adjusted_plane, new_query)

    # Fab_GeometryContext.set_geometry_Group():
    def set_geometry_group(self, geometry_group: Any) -> None:
        """Set the GeometryContext geometry group."""
        # if not isinstance(geometry_group, App.DocumentObjectGroup):
        #     raise RuntimeError(f"Fab_GeometryContext.set_geometry_grouop(): "
        #                        f"{type(geometry_group)} is not App.DocumentObjectGroup")
        self._GeometryGroup = geometry_group  # pragma: no unit cover


# Fab_Geometry:
@dataclass(frozen=True)
class Fab_Geometry(object):
    """Fab_Geometry: An Internal base class for Fab_Arc, Fab_Circle, and Fab_Line.

    All Fab_Geometry classes are immutable (i.e. frozen.)
    """

    # Fab_Geometry.produce():
    def produce(self, geometry_context: Fab_GeometryContext, prefix: str,
                index: int, tracing: str = "") -> Any:
        raise NotImplementedError(f"{type(self)}.produce() is not implemented yet")

    # Fab_Geometry.Start():
    def get_start(self) -> Vector:
        """Return start point of geometry."""
        raise NotImplementedError(f"{type(self)}.get_start() is not implemented yet")


# Fab_Arc:
@dataclass(frozen=True)
class Fab_Arc(Fab_Geometry):
    """Fab_Arc: An internal representation an arc geometry.

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

    # Fab_Arc.produce():
    def produce(self, geometry_context: Fab_GeometryContext, prefix: str,
                index: int, tracing: str = "") -> Any:
        """Return line segment after moving it into Geometry group."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_Arc.produce(*, '{prefix}', {index})")

        part_arc: Any = None
        plane: Fab_Plane = geometry_context._Plane
        rotated_middle: Vector = plane.rotate_to_z_axis(self.Middle, tracing=next_tracing)
        rotated_finish: Vector = plane.rotate_to_z_axis(self.Finish, tracing=next_tracing)
        geometry_context.Query.three_point_arc(
            rotated_middle, rotated_finish, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=Fab_Arc.produce(*, '{prefix}', {index})=>{part_arc}")
        return part_arc


@dataclass(frozen=True)
class Fab_Circle(Fab_Geometry):
    """Fab_Circle: An internal representation of a circle geometry.

    Attributes:
    * *Center (Vector): The circle center.
    * *Diameter (float): The circle diameter in millimeters.

    """

    Center: Vector
    Diameter: float

    # Fab_Circle.produce():
    def produce(self, geometry_context: Fab_GeometryContext, prefix: str,
                index: int, tracing: str = "") -> Any:
        """Return line segment after moving it into Geometry group."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_Circle.produce()")
        plane: Fab_Plane = geometry_context.Plane
        center_on_plane: Vector = plane.point_project(self.Center)
        part_circle: Any = None
        query: Fab_Query = geometry_context.Query
        query.circle(center_on_plane, self.Diameter / 2, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=Fab_Circle.produce()")
        return part_circle


# Fab_Line:
@dataclass(frozen=True)
class Fab_Line(Fab_Geometry):
    """Fab_Line: An internal representation of a line segment geometry.

    Attributes:
    * *Start (Vector): The line segment start point.
    * *Finish (Vector): The line segment finish point.

    """

    Start: Vector
    Finish: Vector

    # Fab_Line.get_start():
    def get_start(self) -> Vector:
        """Return the start point of the Fab_Line."""
        return self.Start

    # Fab_Line.produce():
    def produce(self, geometry_context: Fab_GeometryContext, prefix: str,
                index: int, tracing: str = "") -> Any:
        """Return line segment after moving it into Geometry group."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_Line.produce()")

        line_segment: Any = None
        plane: Fab_Plane = geometry_context._Plane
        rotated_finish: Vector = plane.rotate_to_z_axis(self.Finish, tracing=next_tracing)
        if tracing:
            print(f"{tracing}{self.Finish} ==> {rotated_finish}")
        geometry_context.Query.line_to(rotated_finish, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=Fab_Line.produce()=>{line_segment}")
        return line_segment


# Fab_Fillet:
@dataclass
class Fab_Fillet(object):
    """Fab_Fillet: An object that represents one fillet of a FabPolygon.

    Attributes:
    * *Apex* (Vector): The apex corner point for the fillet.
    * *Radius* (float): The fillet radius in millimeters.
    * *Before* (Fab_Fillet): The previous Fab_Fillet in the FabPolygon.
    * *After* (Fab_Fillet): The next Fab_Fillet in the FabPolygon.
    * *Arc* (Optional[Fab_Arc]): The fillet Arc if Radius is non-zero.
    * *Line* (Optional[Fab_Line]): The line that connects to the previous Fab_Fillet

    """

    Apex: Vector
    Radius: float
    Before: "Fab_Fillet" = field(init=False, repr=False)  # Filled in by __post_init__()
    After: "Fab_Fillet" = field(init=False, repr=False)  # Filled in by __post_init__()
    Arc: Optional["Fab_Arc"] = field(init=False, default=None)  # Filled in by compute_arcs()
    Line: Optional["Fab_Line"] = field(init=False, default=None)  # Filled in by compute_lines()

    # Fab_Fillet.__post_init__():
    def __post_init__(self) -> None:
        """Initialize Fab_Fillet."""
        self.Before = self
        self.After = self

    # Fab_Fillet.compute_arc():
    def compute_arc(self, tracing: str = "") -> Fab_Arc:
        """Return the arc associated with a Fab_Fillet with non-zero radius."""
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
        # The crude 2D diagram below shows the basic Fab_Fillet geometry:
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
            print(f"{tracing}=>Fab_Fillet.compute_arc()")
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
        # arc: Fab_Arc = Fab_Arc(apex, radius, center, start, middle, finish,
        #                            start_angle, finish_angle, delta_angle)
        arc: Fab_Arc = Fab_Arc(apex, radius, center, start, middle, finish)

        # Do a sanity check:
        # finish_angle = finish_angle % pi2
        # start_plus_delta_angle: float = (start_angle + delta_angle) % pi2
        # assert abs(start_plus_delta_angle - finish_angle) < 1.0e-8, "Delta angle is wrong."

        if tracing:
            print(f"{tracing}<=Fab_Fillet.compute_arc()=>{arc}")
        return arc

    # Fab_Fillet.plane_2d_project:
    def plane_2d_project(self, plane: Fab_Plane) -> None:
        """Project the Apex onto a plane.

        Arguments:
        * *plane* (Fab_Plane): The plane to project the Fab_Fillet onto.

        Modifies Fab_Fillet.

        """
        # FreeCAD Vector metheds like to modify Vector contents; force copies beforehand:
        self.Apex = plane.point_project(self.Apex)

    # Fab_Fillet.get_geometries():
    def get_geometries(self) -> Tuple[Fab_Geometry, ...]:
        geometries: List[Fab_Geometry] = []
        if self.Line:
            geometries.append(self.Line)
        if self.Arc:
            geometries.append(self.Arc)
        return tuple(geometries)

    # Fab_Fillet.unit_tests():
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

        # Create the Fab_Fillet's:
        ne_fillet: Fab_Fillet = Fab_Fillet(ne_corner, radius)
        nw_fillet: Fab_Fillet = Fab_Fillet(nw_corner, radius)
        sw_fillet: Fab_Fillet = Fab_Fillet(sw_corner, radius)
        se_fillet: Fab_Fillet = Fab_Fillet(se_corner, radius)

        # Provide before/after Fab_Fillets:
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
    def produce(self, geometry_context: Fab_GeometryContext, prefix: str,
                index: int, tracing: str = "") -> Tuple[Any, ...]:
        """Produce the necessary FreeCAD objects for the FabGeometry."""
        raise NotImplementedError(f"{type(self)}.produce() is not implemented")

    # FabGeometry.project_to_plane():
    def project_to_plane(self, plane: Fab_Plane) -> "FabGeometry":
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
        copy: Vector = Vector()
        normal: Vector = self.Normal / self.Normal.Length
        nx: float = normal.x
        ny: float = normal.y
        nz: float = normal.z
        xy_close: bool = abs(nx - ny) < EPSILON
        perpendicular1: Vector = (
            Vector(-nz, 0, nx) if xy_close else Vector(-ny, nx, 0))
        perpendicular1 = perpendicular1 / perpendicular1.Length
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
    def project_to_plane(self, plane: Fab_Plane, tracing: str = "") -> "FabCircle":
        """Return a new FabCircle projected onto a plane.

        Arguments:
        * *plane* (Fab_Plane): Plane to project to.

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
    def produce(self, geometry_context: Fab_GeometryContext, prefix: str,
                index: int, tracing: str = "") -> Tuple[Any, ...]:
        """Produce the FreeCAD objects needed for FabPolygon."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabCircle.produce()")
        geometries: Tuple[Fab_Geometry, ...] = self.get_geometries()
        geometry: Fab_Geometry
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
    def get_geometries(self) -> Tuple[Fab_Geometry, ...]:
        """Return the FabPolygon lines and arcs."""
        return (Fab_Circle(self.Center, self.Diameter),)

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
        circle: FabCircle = FabCircle(center, normal, 1.0)
        box: FabBox = circle.Box
        assert box.TNE == Vector(1.5, 2.0, 3.0)
        assert box.BSW == Vector(0.5, 1.5, 3.0)


# FabPolygon:
@dataclass(frozen=True)
class FabPolygon(FabGeometry):
    """FabPolygon: An immutable polygon with rounded corners.

    A FabPolygon is represented as a sequence of corners (i.e. a Vector) where each corner can
    optionally be filleted with a radius.  In order to make it easier to use, a corner can be
    specified as simple Vector or as a tuple that specifies a Vector and a radius.  The radius
    is in millimeters and can be provided as either Python int or float.  When an explicit
    fillet radius is not specified, higher levels in the software stack will typically substitute
    in a deburr radius for external corners and an internal tool radius for internal corners.
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
    Fab_Fillets: Tuple[Fab_Fillet, ...] = field(init=False, repr=False)

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
            elif isinstance(corner, tuple) and len(corner) == 2:  # pragma: no unit cover
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
                corner = (corner, 0.0)  # pragma: no unit cover
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
        fillets: List[Fab_Fillet] = []
        fillet: Fab_Fillet
        # TODO: Check for polygon points that are colinear.
        # TODO: Check for polygon corners with overlapping radii.
        copy: Vector = Vector()  # Vector's are mutable, add *copy* to make a private Vector copy.
        index: int
        for index, corner in enumerate(self.Corners):
            if isinstance(corner, Vector):
                fillet = Fab_Fillet(corner + copy, 0.0)
            elif isinstance(corner, tuple):
                if len(corner) != 2:
                    raise ValueError(f"Polygon Corner[{index}]: "
                                     "{corner} tuple length is not 2")  # pragma: no unit cover
                if not isinstance(corner[0], Vector):
                    raise ValueError(f"Polygon Corner[{index}]: {corner} "
                                     "first entry is not Vector")  # pragma: no unit cover
                if not isinstance(corner[1], (int, float)):
                    raise ValueError(f"Polygon Corner[{index}]: {corner} "
                                     "first entry is not number")  # pragma: no unit cover
                fillet = Fab_Fillet(corner[0] + copy, corner[1])
            else:
                raise ValueError(
                    f"Polygon Corner[{index}] is {corner} which is neither a Vector nor "
                    "(Vector, radius) tuple.")  # pragma: no unit cover
            fillets.append(fillet)
        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        object.__setattr__(self, "Fab_Fillets", tuple(fillets))

        # Double link the fillets and look for errors:
        self._double_link()
        radius_error: str = self._radii_check()
        if radius_error:
            raise ValueError(radius_error)  # pragma: no unit cover
        colinear_error: str = self._colinear_check()
        if colinear_error:
            raise ValueError(colinear_error)  # pragma: no unit cover
        # These checks are repeated after 2D projection.

        # self._compute_arcs()
        # self._compute_lines()

    # FabPolygon.project_to_plane():
    def project_to_plane(self, plane: Fab_Plane, tracing: str = "") -> "FabPolygon":
        """Return nre FabPolygon projected onto a plane.

        Arguments:
        * *plane* (Fab_Plane): The plane to project onto.

        Returns:
        * (FabPolyGon): The newly projected FabPolygon.

        """
        if tracing:
            print(f"{tracing}=>FabPolygon.project_to_plane({plane})")
        corner: Union[Vector, Tuple[Vector, Union[int, float]]]
        projected_corners: List[Union[Vector, Tuple[Vector, Union[int, float]]]] = []
        for corner in self.Corners:
            if isinstance(corner, Vector):
                projected_corners.append(plane.point_project(corner))  # pragma: no unit cover
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
        """Double link the Fab_Fillet's together."""
        fillets: Tuple[Fab_Fillet, ...] = self.Fab_Fillets
        size: int = len(fillets)
        fillet: Fab_Fillet
        index: int
        for index, fillet in enumerate(fillets):
            fillet.Before = fillets[(index - 1) % size]
            fillet.After = fillets[(index + 1) % size]

    # FabPolygon._radii_check():
    def _radii_check(self) -> str:
        """Check for radius overlap errors."""
        at_fillet: Fab_Fillet
        for at_fillet in self.Fab_Fillets:
            before_fillet: Fab_Fillet = at_fillet.Before
            actual_distance: float = (before_fillet.Apex - at_fillet.Apex).Length
            radii_distance: float = before_fillet.Radius + at_fillet.Radius
            if radii_distance > actual_distance:
                return (f"Requested radii distance {radii_distance}mm "
                        f"(={before_fillet.Radius}+{at_fillet.Radius}) < "
                        "{actual_distance}mm between {at_fillet.Before} and "
                        "{after_fillet.After}")  # pragma: no unit cover
        return ""

    # FabPolygon._colinear_check():
    def _colinear_check(self) -> str:
        """Check for colinearity errors."""
        at_fillet: Fab_Fillet
        epsilon: float = FabPolygon.EPSILON
        degrees180: float = math.pi
        for at_fillet in self.Fab_Fillets:
            before_apex: Vector = at_fillet.Before.Apex
            at_apex: Vector = at_fillet.Apex
            after_apex: Vector = at_fillet.After.Apex
            to_before_apex: Vector = before_apex - at_apex
            to_after_apex: Vector = after_apex - at_apex
            between_angle: float = abs(to_before_apex.getAngle(to_after_apex))
            if between_angle < epsilon or abs(degrees180 - between_angle) < epsilon:
                return (f"Points [{before_apex}, {at_apex}, "
                        f"{after_apex}] are colinear")  # pragma: no unit cover
        return ""

    # FabPolygon._compute_arcs():
    def _compute_arcs(self) -> None:
        """Create any Arc's needed for non-zero radius Fab_Fillet's."""
        fillet: Fab_Fillet
        for fillet in self.Fab_Fillets:
            if fillet.Radius > 0.0:
                fillet.Arc = fillet.compute_arc()

    # FabPolygon._compute_lines():
    def _compute_lines(self) -> None:
        """Create Create any Line's need for Fab_Fillet's."""
        fillet: Fab_Fillet
        for fillet in self.Fab_Fillets:
            before: Fab_Fillet = fillet.Before
            start: Vector = before.Arc.Finish if before.Arc else before.Apex
            finish: Vector = fillet.Arc.Start if fillet.Arc else fillet.Apex
            if (start - finish).Length > FabPolygon.EPSILON:
                fillet.Line = Fab_Line(start, finish)

    # FabPolygon.get_geometries():
    def get_geometries(self, contact: Vector, Normal: Vector) -> Tuple[Fab_Geometry, ...]:
        """Return the FabPolygon lines and arcs."""
        geometries: List[Fab_Geometry] = []
        fillet: Fab_Fillet
        for fillet in self.Fab_Fillets:
            geometries.extend(fillet.get_geometries())
        return tuple(geometries)

    # FabPolygon._plane_2d_project():
    def _plane_2d_project(self, plane: Fab_Plane) -> None:
        """Update the Fab_Fillet's to be projected onto a Plane.

        Arguments:
        * *plane* (Fab_Plane): The plane to modify the Fab_Fillet's to be on.

        """
        fillet: Fab_Fillet
        for fillet in self.Fab_Fillets:
            fillet.plane_2d_project(plane)

    # FabPolygon.produce():
    def produce(self, geometry_context: Fab_GeometryContext, prefix: str,
                index: int, tracing: str = "") -> Tuple[Any, ...]:
        """Produce the FreeCAD objects needed for FabPolygon."""
        # Extract mount plane *contact* and *normal* from *geometry_context*:
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabPolygon.produce(*, '{prefix}', {index})")
        part_geometry: Any
        assert isinstance(geometry_context, Fab_GeometryContext), geometry_context
        plane_contact: Vector = geometry_context.Plane.Contact
        plane_normal: Vector = geometry_context.Plane.Normal
        plane: Fab_Plane = Fab_Plane(plane_contact, plane_normal)

        # Use *contact*/*normal* for 2D projection:
        self._plane_2d_project(plane)

        # Double check for radii and colinear errors that result from 2D projection:
        radius_error: str = self._radii_check()
        if radius_error:
            raise RuntimeError(radius_error)  # pragma: no unit cover
        colinear_error: str = self._colinear_check()
        if colinear_error:
            raise RuntimeError(colinear_error)  # pragma: no unit covert

        # Now compute the arcs and lines:
        self._compute_arcs()
        self._compute_lines()

        # Extract the geometries using *contact* and *normal* to specify the projection plane:
        geometries: Tuple[Fab_Geometry, ...] = self.get_geometries(plane_contact, plane_normal)
        part_geometries: List[Any] = []

        if not geometries:
            raise RuntimeError("FabPolygon.produce(): empty geometries.")  # pragma: no unit cover
        geometry0: Fab_Geometry = geometries[0]
        start: Vector = geometry0.get_start()
        rotated_start: Vector = geometry_context._Plane.rotate_to_z_axis(
            start, tracing=next_tracing)
        geometry_context.Query.move_to(rotated_start, tracing=next_tracing)
        # TODO: Does this loop do anything anymore?
        for index, geometry in enumerate(geometries):
            part_geometry = geometry.produce(
                geometry_context, prefix, index, tracing=next_tracing)
            _ = part_geometry
        geometry_context.Query.close(tracing=next_tracing)

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

        # geometries: Tuple[Fab_Geometry, ...] = polygon.get_geometries()
        # index: int
        # geometry: Fab_Geometry
        # for index, geometry in enumerate(geometries):
        #     print(f"Geometry[{index}]: {geometry}")


# Fab_Query:
@dataclass
class Fab_Query(object):
    """Fab_Query: A CadQuery Workplane wrapper.

    This class creates CadQuery Workplane provides a consistent head of the Workplane chain..
    CadQuery Operations are added as needed.

    Attributes:
    * *Plane* (Fab_Plane): The plain to use for CadQuery initialization.
    * *WorkPlane: (cadquery.Workplane): The resulting CadQuery Workplane object.

    """
    _Plane: Fab_Plane
    _Query: Any = field(init=False, repr=False, default=None)

    # Fab_Query.__post_init__():
    def __post_init__(self) -> None:
        """Initialize Fab_Plane."""
        if not isinstance(self._Plane, Fab_Plane):
            raise RuntimeError(
                f"Fab_Query.__post_init__(): Got {type(self._Plane)}, "
                "not Fab_Plane")  # pragma: no unit cover
        plane = cast(cq.Plane, self._Plane._Plane)
        self._Query = cq.Workplane(plane)

    # Fab_Query.Plane():
    # @property
    # def Plane(self) -> Fab_Plane:
    #     """Return the Fab_Plane associated from a Fab_Query."""
    #     assert isinstance(self._Plane, Fab_Plane), self._Plane
    #     return self._Plane

    # Fab_Query.WorkPlane():
    @property
    def WorkPlane(self) -> Any:
        """Return the Workplane associated from a Fab_Query."""
        return self._Query

    # Fab_Query.circle():
    def circle(self, center: Vector, radius: float,
               for_construction=False, tracing: str = "") -> None:
        """Draw a circle to a point."""
        if tracing:
            print(f"{tracing}<=>Fab_Query.circle({center}, {radius}, {for_construction})")
        rotated_center: Vector = self._Plane.rotate_to_z_axis(center)
        self._Query = (
            cast(cq.Workplane, self._Query)
            .moveTo(rotated_center.x, rotated_center.y)
            .circle(radius, for_construction)
        )

    # Fab_Query.close():
    def close(self, tracing: str = "") -> None:
        """Close a sequence of arcs and lines."""
        if tracing:
            print(f"{tracing}<=>Fab_Query.close()")
        self._Query = (
            cast(cq.Workplane, self._Query)
            .close()
        )

    # Fab_Query.copy_workplane():
    def copy_workplane(self, plane: Fab_Plane, tracing: str = "") -> None:
        """Create a new CadQuery workplane and push it onto the stack."""
        if tracing:
            print(f"{tracing}=>Fab_Query.copy_workPlane({plane})")
        if not isinstance(plane, Fab_Plane):
            raise RuntimeError(
                f"Fab_Query.copy_workplane(): Got {type(plane)}, "
                "not Fab_Plane")  # pragma: no unit cover
        if tracing:
            print(f"{tracing}{plane=}")
        self._Query = (
            cast(cq.Workplane, self._Query)
            .copyWorkplane(cq.Workplane(plane.CQPlane))
        )
        if tracing:
            print(f"{tracing}<=Fab_Query.copy_workPlane({plane})")

    # Fab_Query.extrude():
    def extrude(self, depth: float, tracing: str = "") -> None:
        """Extrude current 2D object to a known depth."""
        if tracing:
            print(f"{tracing}<=>Fab_Query.extrude({depth})")
        self._Query = (
            cast(cq.Workplane, self._Query)
            .extrude(-depth)
        )

    # Fab_Query.hole():
    def hole(self, diameter: float, depth: float, tracing: str = "") -> None:
        """Drill a hole."""
        if tracing:
            print(f"{tracing}=>Fab_Query.hole({diameter}, {depth})")
        self._Query = (
            cast(cq.Workplane, self._Query)
            .hole(diameter=diameter, depth=depth)
        )
        if tracing:
            print(f"{tracing}<=Fab_Query.hole({diameter}, {depth})")

    # Fab_Query.line_to():
    def line_to(self, end: Vector, for_construction=False, tracing: str = "") -> None:
        """Draw a line to a point."""
        if tracing:
            print(f"{tracing}=>Fab_Query.line_to({end}, {for_construction})")
        end_tuple: Tuple[float, float] = (end.x, end.y)
        self._Query = (
            cast(cq.Workplane, self._Query)
            .lineTo(end.x, end.y)
        )
        if tracing:
            print(f"{tracing}{end_tuple=}")
            print(f"{tracing}<=Fab_Query.line_to({end}, {for_construction})")

    # Fab_Query.move_to():
    def move_to(self, point: Vector, tracing: str = "") -> None:
        """Draw a line to a point."""
        if tracing:
            print(f"{tracing}=>Fab_Query.move_to({point})")
            print(f"{tracing}{self._Query.plane=}")
        assert isinstance(point, Vector), point
        self._Query = (
            cast(cq.Workplane, self._Query)
            .moveTo(point.x, point.y)
        )
        if tracing:
            print(f"{tracing}<=Fab_Query.move_to({point})")

    # Fab_Query.show():
    def show(self, label: str, tracing: str = "") -> None:
        """Print a detailed dump of a Fab_Query."""
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
            print(f"{tracing}{self._Query}")

        # Now restore the *previous_functions*:
        (cq.cq.CQContext.__str__, cq.occ_impl.geom.Plane.__str__,
         cq.Workplane.__str__) = previous_functions

    # Fab_Query.subtract():
    def subtract(self, remove_solid: "Fab_Query", tracing: str = "") -> None:
        """Subtract one solid form a Fab_Query."""
        if tracing:
            print(f"{tracing}<=>Fab_Query.subtract()")
        self._Query = (
            cast(cq.Workplane, self._Query) -
            remove_solid.WorkPlane
        )

    # Fab_Query.three_point_arc():
    def three_point_arc(self, middle: Vector, end: Vector,
                        for_construction: bool = False, tracing: str = "") -> None:
        """Draw a three point arc."""
        if tracing:
            print(f"{tracing}=>Fab_Query.three_point_arc({middle}), {end})")
        middle_tuple: Tuple[float, float] = (middle.x, middle.y)
        end_tuple: Tuple[float, float] = (end.x, end.y)
        self._Query = (
            cast(cq.Workplane, self._Query)
            .threePointArc(middle_tuple, end_tuple)
        )
        if tracing:
            print(f"{tracing}{middle_tuple=} {end_tuple=}")
            print(f"{tracing}<=Fab_Query.three_point_arc({middle}), {end})")


def main() -> None:
    """Run main program."""
    pass


if __name__ == "__main__":
    Fab_Fillet.unit_tests()
    FabCircle._unit_tests()
    FabPolygon._unit_tests()
    main()
