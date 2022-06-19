#!/usr/bin/env python3
"""Geometry: A module for constructing 2D geometry."""

# <--------------------------------------- 100 characters ---------------------------------------> #

# Note this code uses nested dataclasses that are frozen.  Computed attributes are tricky.
# See (Set frozen data class files in __post_init__)[https://stackoverflow.com/questions/53756788]

from dataclasses import dataclass, field
import math
from typeguard import check_type
from typing import Any, cast, Callable, List, Optional, Sequence, Tuple, Union

import cadquery as cq  # type: ignore
from cadquery import Vector  # type: ignore
from FabNodes import FabBox


# FabPlane:
@dataclass
class FabPlane(object):
    """FabPlane: An immutable Plane class.

    * *Contact* (Vector):  Some contact point that anywhere in the plane.
    * *Normal* (Vector): The normal to the plane.
    """

    _Contact: Vector
    _Normal: Vector
    tracing: str = ""  # TODO: Remove. For dataclass sub-classing, optional values are disallowed.)
    _UnitNormal: Vector = field(init=False, repr=False)
    _Distance: float = field(init=False, repr=False)
    _Copy: Vector = field(init=False, repr=False)
    _Origin: Vector = field(init=False)
    _XDirection: Vector = field(init=False)
    _Plane: Any = field(init=False, repr=False)  # Used by CadQuery

    # FabPlane.__post_init__():
    def __post_init__(self) -> None:
        """Initialize FabPlane."""
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
            print(f"{tracing}=>FabPlane.__post_init__({self._Contact}, {self._Normal})")
        next_tracing: str = tracing + " " if tracing else ""

        copy: Vector = Vector()
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
        # Now the CadQuery plane can be created:
        self._Plane = cq.Plane(origin=origin, normal=normal, xDir=x_direction)

        if tracing:
            print(f"{tracing}{rotated_origin=} {rotated_x_direction=}")
            print(f"{tracing}{origin=} {unrotated_x_direction=}")
            print(f"{tracing}{x_direction=}")
            print(f"{tracing}{self._Plane=}")
            print(f"{tracing}<=FabPlane.__post_init__({self._Contact}, {self._Normal})")

    # FabPlane.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return a FabPlane hash value."""
        contact: Vector = self.Contact
        normal: Vector = self.Normal
        return (
            "FabPlane",
            f"{contact.x:.6f}",
            f"{contact.y:.6f}",
            f"{contact.z:.6f}",
            f"{normal.x:.6f}",
            f"{normal.y:.6f}",
            f"{normal.z:.6f}",
        )

    # FabPlane.projectPoint():
    def projectPoint(self, point: Vector) -> Vector:
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
        """Return the FabPlane Contact."""
        return self._Contact + self._Copy

    # FabPlane.Normal():
    @property
    def Normal(self) -> Vector:
        """Return the FabPlane Normal."""
        return self._Normal + self._Copy

    # FabPlane.UnitNormal():
    @property
    def UnitNormal(self) -> Vector:
        """Return FabPlane Normal."""
        return self._UnitNormal + self._Copy

    # FabPlane.Distance():
    @property
    def Distance(self) -> float:
        """Return FabPlane distance along the normal."""
        return self._Distance

    # FablPlane.Origin():
    @property
    def Origin(self) -> Vector:
        """Return FabPlane Origin in 3D space."""
        return self._Origin + self._Copy

    # FabPlane.adjust():
    def adjust(self, delta: float) -> "FabPlane":
        """Return a new FabPlane that has been adjusted up/down the normal by a delta."""
        origin: Vector = self.Origin
        unit_normal: Vector = self.UnitNormal
        new_origin: Vector = origin + delta * unit_normal
        # Both the contact and the normal can be *new_origin*:
        adjusted_plane: FabPlane = FabPlane(new_origin, new_origin)
        return adjusted_plane

    # FabPlane.CQPlane():
    @property
    def CQPlane(self) -> Any:
        """Return the associated CadQuery Plane."""
        plane: Any = self._Plane
        assert isinstance(plane, cq.Plane), plane
        return plane

    # FabPlane._rotate():
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


# Fab_GeometryContext:
@dataclass
class Fab_GeometryContext(object):
    """GeometryProduce: Context needed to produce FreeCAD geometry objects.

    Attributes:
    * *Plane* (FabPlane): Plane to use.
    * *Query* (Fab_Query): The CadQuery Workplane wrapper to use.
    * *_GeometryGroup*: (App.DocumentObjectGroup):
      The FreeCAD group to store FreeCAD Geometry objects into.
      This field needs to be set prior to use with set_geometry_group() method.

    """

    _Plane: FabPlane
    _Query: "Fab_Query"
    _geometry_group: Optional[Any] = field(init=False, repr=False)  # TODO: Is this used any more?
    _copy: Vector = field(init=False, repr=False)  # TODO: Is this used any more?

    # Fab_GeometryContext.__post_init__():
    def __post_init__(self) -> None:
        """Initialize FabGeometryContex."""

        if not isinstance(self._Plane, FabPlane):
            raise RuntimeError(
                f"Fab_GeometryContext.__post_init__(): "
                f"{type(self._Plane)} is not a FabPlane")  # pragma: no unit cover
        if not isinstance(self._Query, Fab_Query):
            raise RuntimeError(
                "Fab_GeometryContext.__post_init__(): "
                f"{type(self._Query)} is not a Fab_Query")  # pragma: no unit cover

        copy: Vector = Vector()
        self._copy: Vector = copy
        self._GeometryGroup = None  # Set with set_geometry_group() method

    # Fab_GeometryContext.Plane():
    @property
    def Plane(self) -> FabPlane:
        """Return the FabPlane."""
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
        adjusted_plane: FabPlane = self._Plane.adjust(delta)
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

    # Fab_Geometry.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing Fab_Geometry."""
        pass  # Nothing to do.

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

    Constructor:
    * Fab_Arc(Apex, Radius, Center, Start, Middle, Finish)

    """

    Apex: Vector
    Radius: float
    Center: Vector
    Start: Vector
    Middle: Vector
    Finish: Vector

    # Fab_Arc.produce():
    def produce(self, geometry_context: Fab_GeometryContext, prefix: str,
                index: int, tracing: str = "") -> Any:
        """Return line segment after moving it into Geometry group."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_Arc.produce(*, '{prefix}', {index})")

        part_arc: Any = None
        plane: FabPlane = geometry_context._Plane
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
        plane: FabPlane = geometry_context.Plane
        center_on_plane: Vector = plane.projectPoint(self.Center)
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

    Constructor:
    * Fab_Line(Start, Finish)
    """

    Start: Vector
    Finish: Vector

    # Fab_Line.__post_init__(self):
    def __post_init__(self) -> None:
        """Finish initializing a Fab_Line."""
        super().__post_init__()

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
        plane: FabPlane = geometry_context._Plane
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
    ProjectedApex: Vector = field(init=False, repr=False)  # Used by get_geometry_info()

    # Fab_Fillet.__post_init__():
    def __post_init__(self) -> None:
        """Initialize Fab_Fillet."""
        self.Before = self
        self.After = self
        self.RotatedApex = Vector()

    # Fab_Fillet.compute_arc():
    def compute_arc(self, tracing: str = "") -> Fab_Arc:
        """Return the arc associated with a Fab_Fillet with non-zero radius."""
        # A fillet is represented as an arc that traverses a sphere with a specified radius.
        #
        # Each fillet specifies an 3D center point and a radius.  The fillet the corner point is
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
    def plane_2d_project(self, plane: FabPlane) -> None:
        """Project the Apex onto a plane.

        Arguments:
        * *plane* (FabPlane): The plane to project the Fab_Fillet onto.

        Modifies Fab_Fillet.

        """
        # FreeCAD Vector metheds like to modify Vector contents; force copies beforehand:
        self.Apex = plane.projectPoint(self.Apex)

    # Fab_Fillet.compute_fillet_area_perimeter():
    def compute_fillet_area_perimeter(self, tracing: str = "") -> Tuple[float, float]:
        """Return the excluded fillet area and the perimeter for a Fab_Fillet.

        To be more concise, the fillet_area is the area outside of the fillet arc, but inside
        the straight lines "corner" of the fillet.

        Returns:
        * (float): The excluded area of a fillet (i.e. the area not under the arc segment.)
        * (float): The length the of the arc segment.

        """
        if tracing:
            print(f"{tracing}=>Fab_Fillet.compute_fillet_area_perimeter()")
        fillet_area: float = 0.0
        fillet_perimeter: float = 0.0

        arc: Optional[Fab_Arc] = self.Arc
        if arc:
            # *arc_points* defines a diamond shaped polygon that sweeps from the arc start,
            # to the arc apex, to the arc finish.  Compute *diamond_area*:
            arc_points: Tuple[Vector, ...] = (
                arc.Center,
                arc.Start,
                arc.Apex,
                arc.Finish,
            )
            diamond_area: float = FabPolygon._compute_polygon_area(arc_points)
            if tracing:
                print(f"{tracing}{diamond_area=:.3f}")

            # Compute *sweep_angle*, the angle that sweeps from start to finish:
            start: Vector = arc.Start - arc.Apex
            start_angle: float = math.atan2(start.y, start.x)
            finish: Vector = arc.Finish - arc.Apex
            finish_angle: float = math.atan2(finish.y, finish.x)
            sweep_angle: float = abs(finish_angle - start_angle)

            # Compute the acute *sweep_angle*:
            pi: float = math.pi
            pi2: float = 2.0 * pi
            while sweep_angle > pi:
                sweep_angle -= pi2
            while sweep_angle < -pi:
                sweep_angle += pi2  # pragma: no unit cover
            sweep_angle = abs(sweep_angle)
            assert 0.0 <= sweep_angle <= pi, f"{math.degrees(sweep_angle)=:.3f}"
            if tracing:
                print(f"{tracing}{math.degrees(sweep_angle)=:.3f} {sweep_angle=:.3f}")

            # Add the *sweep_area* to *total_fillet_area*:
            radius: float = arc.Radius
            circle_area: float = pi * radius * radius
            sweep_area: float = circle_area * (sweep_angle / pi2)
            fillet_area = diamond_area - sweep_area

            # Compute *fillet_perimeter*:
            diameter: float = pi2 * radius
            fraction: float = sweep_angle / pi2
            fillet_perimeter = diameter * fraction
            assert fillet_area >= 0.0, fillet_area
            if tracing:
                print(f"{tracing}{circle_area=:.3f} {sweep_area=:.3f} {fillet_area=:.3f} ")
                print(f"{tracing}{diameter=:.3f} {fraction=:.3f} {fillet_perimeter=:.3f}")
        else:
            if tracing:
                print(f"{tracing}No arc")

        if tracing:
            print(f"{tracing}<=Fab_Fillet.compute_fillet_area_perimeter()=>"
                  f"{fillet_area=:.3f}, {fillet_perimeter=:.3f}")
        return fillet_area, fillet_perimeter

    # Fab_Fillet.get_geometries():
    def get_geometries(self) -> Tuple[Fab_Geometry, ...]:
        geometries: List[Fab_Geometry] = []
        if self.Line:
            geometries.append(self.Line)
        if self.Arc:
            geometries.append(self.Arc)
        return tuple(geometries)

    # Fab_Fillet._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run Fab_Fillet unit tests."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_Fillet._unit_tests()")

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

        # Provide before/after _Fillets:
        ne_fillet.Before = se_fillet
        nw_fillet.Before = ne_fillet
        sw_fillet.Before = nw_fillet
        se_fillet.Before = sw_fillet
        ne_fillet.After = nw_fillet
        nw_fillet.After = sw_fillet
        sw_fillet.After = se_fillet
        se_fillet.After = ne_fillet

        if False and tracing:  # pragma: no unit cover
            ne_fillet.compute_arc(tracing=f"{next_tracing}NE:")
            nw_fillet.compute_arc(tracing=f"{next_tracing}NW:")
            sw_fillet.compute_arc(tracing=f"{next_tracing}SW:")
            se_fillet.compute_arc(tracing=f"{next_tracing}SE:")
        else:  # pragma: no unit cover
            ne_fillet.compute_arc()
            nw_fillet.compute_arc()
            sw_fillet.compute_arc()
            se_fillet.compute_arc()

        if tracing:
            print(f"{tracing}<=Fab_Fillet._unit_tests()")


# FabGeometry:
@dataclass(frozen=True)
class FabGeometry(object):
    """FabGeometry: The base class for FabPolygon and FabCircle.

    Attributes:
    * *Plane* (FabPlane): The plane to project the geometry onto.

    """

    Plane: FabPlane

    # FabGeometry.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing a FaabGeometry."""
        check_type("FabGeometry.Plane:", self.Plane, FabPlane)

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

    # FabGeometry.projectToPlane():
    def projectToPlane(self, plane: FabPlane) -> "FabGeometry":
        """Return a new FabGeometry projected onto a plane."""
        raise NotImplementedError(f"{type(self)}.projectToPlane is not implemented")

    # FabGeometry.get_geometry_info():
    def get_geometry_info(
            self, plane: FabPlane, tracing: str = "") -> Tuple[float, float, float, float]:
        """Return information about FabGeometry.

        Arguments:
        * *plane* (FabPlane): The plane to project the FabGeometry onto.

        Returns:
        * (float): The geometry area in square millimeters.
        * (float): The perimeter length in millimeters.
        * (float):
          The minimum internal radius in millimeters. -1.0 means there is no internal radius.
        * (float): The minimum external radius in millimeters. 0 means that all corners are "sharp".
        """
        raise NotImplementedError(f"{type(self)}.get_geometry_info is not implemented")


# FabCircle:
@dataclass(frozen=True)
class FabCircle(FabGeometry):
    """FabCircle: Represents a circle on a plane.

    Attributes:
    * *Plane* (FabPlane): The plane the circle center is projected onto.
    * *Center* (Vector): The circle center after it has been projected.
    * *Diameter* (float): The circle diameter in millimeters.
    * *Box* (FabBox): The box that encloses FabCircle

    Constructor:
    * FabCircle(Plane, Center, Diameter)

    """

    _Center: Vector
    Diameter: float
    _ProjectedCenter: Vector = field(init=False, repr=False, compare=False)
    _Copy: Vector = field(init=False, repr=False, compare=False)
    _Box: FabBox = field(init=False, repr=False, compare=False)

    # FabCircle.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing a FabCircle."""
        super().__post_init__()
        check_type("FabCircle.Center", self._Center, Vector)
        check_type("FabCircle.Diameter", self.Diameter, float)
        if self.Diameter <= 0.0:
            raise ValueError(f"Diameter ({self.Diameter}) must be positive.")

        # Compute the *box* attribute:
        # A perpendicular to the normal is needed, so please see:
        #     [Find Perpendicular](https://math.stackexchange.com/questions/137362/
        #     how-to-find-perpendicular-vector-to-another-vector)
        # The response from Joe Strout is used.  There is probably an alternate solution based
        # on quaternions that is better, but the code below should be more than adequate.
        EPSILON = 1.0e-8
        copy: Vector = Vector()
        normal: Vector = self.Plane.Normal / self.Plane.Normal.Length

        nx: float = normal.x
        ny: float = normal.y
        nz: float = normal.z
        xy_close: bool = abs(nx - ny) < EPSILON
        perpendicular1: Vector = (
            Vector(-nz, 0, nx) if xy_close else Vector(-ny, nx, 0))
        perpendicular1 = perpendicular1 / perpendicular1.Length
        perpendicular2: Vector = (normal + copy).cross(perpendicular1 + copy)

        center: Vector = self._Center + copy
        projected_center: Vector = self.Plane.projectPoint(center)

        radius: float = self.Diameter / 2.0
        corner1: Vector = projected_center + radius * perpendicular1
        corner2: Vector = projected_center + radius * perpendicular2
        corner3: Vector = projected_center - radius * perpendicular1
        corner4: Vector = projected_center - radius * perpendicular1
        box: FabBox = FabBox()
        box.enclose((corner1, corner2, corner3, corner4))

        # Make private copy of *Center*.
        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        object.__setattr__(self, "_Center", center)
        object.__setattr__(self, "_Copy", copy)
        object.__setattr__(self, "_Box", box)
        object.__setattr__(self, "_ProjectedCenter", projected_center)

    # FabCircle.Box():
    @property
    def Box(self) -> FabBox:
        """Return the FabBox that encloses FabCircle."""
        return self._Box

    # FabCircle.Center():
    @property
    def Center(self) -> Vector:
        """Return the projected FabCircle center point."""
        return self._Center + self._Copy

    # FabCircle.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return FabCircle hash."""
        center: Vector = self.Center
        hashes: Tuple[Union[int, str, Tuple[Any, ...]], ...] = (
            "FabCircle.get_hash",
            self.Plane.get_hash(),
            f"{center.x:.6f}",
            f"{center.y:.6f}",
            f"{center.z:.6f}",
            f"{self.Diameter:.6f}",
        )
        return hashes

    # FabCircle.get_geometry_info():
    def get_geometry_info(
            self, plane: FabPlane, tracing: str = "") -> Tuple[float, float, float, float]:
        """Return information about FabGeometry.

        Arguments:
        * *plane* (FabPlane): The plane to project FabGeometry onto.

        Returns:
        * (float): The circle area in square millimeters.
        * (float): The perimeter length in millimeters.
        * (float): -1 since there are no internal radius corners for a circle.
        * (float): The circle radius in millimeters.

        """
        if tracing:
            print("{tracing}=>FabCircle.get_geometry_info(*))")
        pi: float = math.pi
        radius: float = self.Diameter / 2.0
        area: float = pi * radius * radius
        perimeter: float = 2.0 * pi * radius
        minimum_internal_radius: float = -1.0
        minimum_external_radius: float = radius
        if tracing:
            print(f"{tracing}=>FabCircle.get_geometry_info(*))=>"
                  f"({area}, {perimeter}, {minimum_internal_radius}, {minimum_external_radius})")
        return area, perimeter, minimum_internal_radius, minimum_external_radius

    # FabCircle.projectToPlane():
    def projectToPlane(self, plane: FabPlane, tracing: str = "") -> "FabCircle":
        """Return a new FabCircle projected onto a plane.

        Arguments:
        * *plane* (FabPlane): Plane to project to.

        Returns:
        * (FabCircle): The newly projected FabCicle.

        """
        if tracing:
            print(f"{tracing}=>FabCircle.projectToPlane({plane})")
        center: Vector = self.Center
        new_center: Vector = plane.projectPoint(center)
        new_circle: "FabCircle" = FabCircle(plane, new_center, self.Diameter)
        if tracing:
            print(f"{tracing}<=FabCircle.projectToPlane({plane}) => {new_circle}")
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
    def _unit_tests(tracing: str = "") -> None:
        """Run FabCircle unit tests."""
        if tracing:
            print(f"{tracing}=>FabCircle._unit_tests()")

        origin: Vector = Vector()
        z_axis: Vector = Vector(0, 0, 1)
        xy_plane: FabPlane = FabPlane(origin, z_axis)
        center: Vector = Vector(1, 2, 3)
        try:
            FabCircle(xy_plane, center, 0.0)
            assert False
        except ValueError as value_error:
            assert str(value_error) == "Diameter (0.0) must be positive.", value_error
        try:
            FabCircle(xy_plane, center, -1.0)
            assert False
        except ValueError as value_error:
            assert str(value_error) == "Diameter (-1.0) must be positive.", value_error

        circle: FabCircle = FabCircle(xy_plane, center, 1.0)
        assert circle.Diameter == 1.0, circle.Diameter
        assert circle.Box.TNE == Vector(1.5, 2.0, 0.0), circle.Box.TNE
        assert circle.Box.BSW == Vector(0.5, 1.5, 0.0), circle.Box.BSW

        if tracing:
            print(f"{tracing}<=FabCircle._unit_tests()")


# FabPolygon:
@dataclass(frozen=True)
class FabPolygon(FabGeometry):
    """FabPolygon: An immutable polygon with rounded corners.

    A FabPolygon is represented as a sequence of corners (i.e. a Vector) where each corner can
    optionally be filleted with a radius.  In order to make it easier to use, a corner can be
    specified either as simple Vector or as a tuple that specifies both a Vector and a radius.
    The radius is in millimeters and can be provided as either a Python int or float.  When an
    explicit fillet radius is not specified, higher levels in the software stack *may* substitute
    in a deburr radius for external corners and an internal tool radius for internal corners.
    FabPolygon's are frozen and can not be modified after creation.  Since Vector's are mutable,
    a private copy of each vector stored inside the FabPolygon.

    Attributes:
    * *Plane* (FabPlane: The plane that all of the corners are projected onto.
    * *Corners* (Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...]):
      See description immediately above for more on corners.

    Constructor:
    * FabPolygon(Plane, Corners):

    Example:
    ```
         xy_plane: FabPlane = FabPlane(Vector(0, 0, 0), Vector(0, 0, 1))
         polygon: FabPolygon = FabPolygon(xy_plane, (
             Vector(-10, -10, 0),  # Lower left (no radius)
             Vector(10, -10, 0),  # Lower right (no radius)
             (Vector(10, 10, 0), 5),  # Upper right (5mm radius)
             (Vector(-0, 10, 0), 5.5),  # Upper right (5.5mm radius)
         ), "Name")
    ```
    """

    _Corners: Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...] = field(
        compare=False)

    # Computed attributes:
    _CopiedCorners: Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...] = field(
        init=False, repr=False, compare=True)
    _ProjectedCorners: Tuple[Tuple[Vector, float], ...] = field(
        init=False, repr=False, compare=False)
    _Box: FabBox = field(
        init=False, repr=False, compare=False)
    _Fillets: Tuple[Fab_Fillet, ...] = field(
        init=False, repr=False, compare=False)  # TODO make Private

    EPSILON = 1.0e-8

    # FabPolygon._copyCorner():
    @staticmethod
    def _copyCorner(
            corner: Union[Vector, Tuple[Vector, Union[int, float]]]
    ) -> Union[Vector, Tuple[Vector, Union[int, float]]]:
        """Return a copy of an original corner."""
        copy: Vector = Vector()
        copied_corner: Union[Vector, Tuple[Vector, Union[int, float]]] = (
            corner + copy if isinstance(corner, Vector) else (corner[0] + copy, corner[1]))
        return copied_corner

    # FabPolygon.__post_init__():
    def __post_init__(self) -> None:
        """Verify that the corners passed in are correct."""
        tracing: str = ""  # Edit to enable tracing.
        if tracing:
            print(f"{tracing}=>FabPolygon.__post_init__()")

        super().__post_init__()
        check_type("FabPolygon.Corners", self._Corners,
                   Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...])

        # Copy *_Corners* into *original_corners* and fill in *projected_corners*:
        copied_corners: List[Union[Vector, Tuple[Vector, Union[int, float]]]] = []
        projected_corners: List[Tuple[Vector, float]] = []
        original_corner: Union[Vector, Tuple[Vector, Union[int, float]]]
        plane: FabPlane = self.Plane
        for original_corner in self._Corners:
            copied_corners.append(FabPolygon._copyCorner(original_corner))
            apex: Vector
            radius: float
            if isinstance(original_corner, Vector):
                apex, radius = original_corner, 0.0
            else:
                apex, radius = (original_corner[0], float(original_corner[1]))
            projected_apex: Vector = plane.projectPoint(apex)
            projected_corners.append((projected_apex, radius))

        # Compute the *box* that encloses the projected points.:
        corner: Tuple[Vector, float]
        box_points: List[Vector] = [corner[0] for corner in projected_corners]
        box: FabBox = FabBox()
        box.enclose(box_points)

        fillets: List[Fab_Fillet] = []
        fillet: Fab_Fillet
        index: int
        for index, corner in enumerate(projected_corners):
            # TODO: remove the check_type:
            check_type(f"FabPolygon.Corner[{index}]:", corner, Tuple[Vector, float])
            fillet = Fab_Fillet(corner[0], corner[1])
            fillets.append(fillet)

        # This is the only way to initialize a field in a frozen data class:
        # See: [Why __setattr__?](https://stackoverflow.com/questions/53756788)
        object.__setattr__(self, "_Box", box)
        object.__setattr__(self, "_CopiedCorners", tuple(copied_corners))
        object.__setattr__(self, "_ProjectedCorners", tuple(projected_corners))
        object.__setattr__(self, "_Fillets", tuple(fillets))

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
        if tracing:
            print(f"{tracing}<=FabPolygon.__post_init__()")

    # FabPolygon.Corners:
    @property
    def Corners(self) -> Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...]:
        """Return a copy of original corners."""
        corner: Union[Vector, Tuple[Vector, Union[int, float]]]
        copied_corners: List[Union[Vector, Tuple[Vector, Union[int, float]]]] = [
            FabPolygon._copyCorner(corner) for corner in self._CopiedCorners]
        assert len(self._Corners) == len(copied_corners)
        return tuple(copied_corners)

    # FabPolygon.ProjectedCorners:
    @property
    def ProjectedCorners(self) -> Tuple[Union[Vector, Tuple[Vector, Union[int, float]]], ...]:
        """Return corners after they have been projected onto the FabPolygon plane."""
        copy: Vector = Vector()
        corner: Tuple[Vector, float]
        projected_corners_copy: List[Union[Vector, float]] = [
            (corner[0] + copy, corner[1]) for corner in self._ProjectedCorners]
        return tuple(projected_corners_copy)

    # FabPolygon.Box:
    @property
    def Box(self) -> FabBox:
        """Return FabBox that encloses FabPolygon."""
        return self._Box

    # FabPolygon.compute_polgyon_area():
    @staticmethod
    def _compute_polygon_area(points: Sequence[Vector], tracing: str = "") -> float:
        """Compute that area of an irregular polygon."""
        if tracing:
            print(f"{tracing}=>FabPolygon_compute_polygon_ares({points})")

        # References:
        # * [Polygon Area](https://www.mathsisfun.com/geometry/area-irregular-polygons.html)

        # Compute the *minimum_y* in for *points*:
        # TODO: This algorithm probably works just fine with *minimum_y* set to 0.0.
        minimum_y: float = 0.0  # Overwritten on first iteration.
        index: int
        point: Vector
        for index, point in enumerate(points):
            y: float = point.y
            minimum_y = y if index == 0 else min(minimum_y, y)
        if tracing:
            print(f"{tracing}{minimum_y=}")

        # Compute the *area* under the polygon *points*.
        size: int = len(points)
        area: float = 0.0
        for index, point in enumerate(points):
            next_point = points[(index + 1) % size]
            dx: float = next_point.x - point.x
            dy1: float = point.y - minimum_y
            dy2: float = next_point.y - minimum_y
            average_dy: float = (dy1 + dy2) / 2.0
            area += dx * average_dy
            if tracing:
                print(f"{tracing}[{index}]: {point=} {next_point=} "
                      f"{dx=} {dy1=} {dy2=} {average_dy=} {area=}")

        # Since we do not know if the polygon is clockwise or counter-clockwise,
        # the *area* can be either positive or negative.  Make it positive.
        area = abs(area)
        if tracing:
            print(f"{tracing}<=_compute_polygon_area({points})=>{area}")
        return area

    # FabPolygon.get_geometry_info():
    def get_geometry_info(
            self, plane: FabPlane, tracing: str = "") -> Tuple[float, float, float, float]:
        """Return the values needed for a FabGeometry_Info from a FabPolygon.

        Method Arguments:
        * *plane* (FabPlane): The FabPolygon projection to use for Area computation.

        Returns:
        * (float): The area of the projected FabPolygon.
        * (float): The polygon perimeter in millimeters with rounded corners.
        * (float):
          The minimum internal radius corners for the polygon.
          -1.0 means no internal corners.
        * (float): The minimum external radius corners for the polygon.

        """
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabPolygon.get_geometry_info(*)")

        # In order to finish filling in Fab_Fillet's, a *geometry_context* is needed.
        origin: Vector = Vector(0.0, 0.0, 0.0)
        z_axis: Vector = Vector(0.0, 0.0, 1.0)
        xy_plane = FabPlane(origin, z_axis)
        query: Fab_Query = Fab_Query(xy_plane)  # Not used, but *geometry_context* needs it.
        # Fill in the contents of the FabFillet's:
        geometry_context: Fab_GeometryContext = Fab_GeometryContext(xy_plane, query)
        _ = self.produce(geometry_context, "prefix", 0)
        # Now the _Fillets are filled in.

        # Step 1: Project the Apex points from *plane* to the XY plane.
        fillet: Fab_Fillet
        for fillet in self._Fillets:
            fillet.ProjectedApex = plane.rotate_to_z_axis(fillet.Apex)

        # Step 2: Compute the *maximum_radius* and *total_angle* of turning at each *fillet*:
        pi: float = math.pi
        pi2: float = 2.0 * pi
        polygon_points: List[Vector] = []
        total_angle: float = 0.0
        positive_fillet_area: float = 0.0
        negative_fillet_area: float = 0.0
        positive_radius: float = -1.0
        negative_radius: float = -1.0
        perimeter: float = 0.0
        index: int
        for index, fillet in enumerate(self._Fillets):
            before_apex: Vector = fillet.Before.ProjectedApex
            at_apex: Vector = fillet.ProjectedApex
            after_apex: Vector = fillet.After.ProjectedApex
            polygon_points.append(at_apex)

            before: Vector = at_apex - before_apex
            after: Vector = after_apex - at_apex
            before_angle: float = math.atan2(before.y, before.x)
            after_angle: float = math.atan2(after.y, after.x)
            delta_angle: float = after_angle - before_angle
            while delta_angle < -pi:
                delta_angle += pi2
            while delta_angle > pi:
                delta_angle -= pi2
            total_angle += delta_angle
            if tracing:  # pragma: no unit cover
                degrees: Callable = math.degrees
                print(f"{tracing}Fillet[{index}]:{before_apex=} {at_apex=} {after_apex=}")
                print(f"{tracing}Fillet[{index}]: {before=} {after=}")
                print(f"{tracing}Fillet[{index}]: {degrees(before_angle)=} {degrees(after_angle)=}")
                print(f"{tracing}Fillet[{index}]: {degrees(delta_angle)=} {degrees(total_angle)=}")

            fillet_area: float
            fillet_perimeter: float
            fillet_area, fillet_perimeter = (
                fillet.compute_fillet_area_perimeter(tracing=next_tracing))
            if tracing:
                print(f"{tracing}perimeter += {fillet_perimeter=:.3f}")
            perimeter += fillet_perimeter

            line: Optional[Fab_Line] = fillet.Line
            if line:
                projected_start: Vector = plane.projectPoint(line.Start)
                projected_finish: Vector = plane.projectPoint(line.Finish)
                line_length: float = (projected_finish - projected_start).Length
                perimeter += line_length
                if tracing:
                    print(f"{tracing}perimeter += {line_length=:.3f}")

            def update_radius(radius, fillet: Fab_Fillet) -> float:
                """Update the minimum radius."""
                arc: Optional[Fab_Arc] = fillet.Arc
                arc_radius: float = arc.Radius if arc else 0.0
                radius = arc_radius if radius < 0.0 else min(radius, arc_radius)
                return radius

            if delta_angle > 0.0:
                positive_fillet_area += fillet_area
                positive_radius = update_radius(positive_radius, fillet)
            else:
                negative_fillet_area += fillet_area
                negative_radius = update_radius(negative_radius, fillet)

        if tracing:
            print(f"{tracing}{positive_fillet_area=:.3f} {positive_radius=:.3f}")
            print(f"{tracing}{negative_fillet_area=:.3f} {negative_radius=:.3f}")

        # Sanity check: *total_angle* should be either +360 degrees or -360 degrees:
        degrees360: float = 2.0 * pi
        epsilon: float = 1.0e-8
        assert abs(abs(total_angle) - degrees360) < epsilon, f"{math.degrees(total_angle)=:.3f}"

        # Compute the *maximum_area* that does not deal with fillet rounding:
        area: float = FabPolygon._compute_polygon_area(polygon_points)
        if tracing:
            print(f"{tracing}Initial polygon {area=}")
        internal_radius: float = 0.0
        external_radius: float = 0.0
        if total_angle > 0.0:
            # Clockwise:
            area += negative_fillet_area - positive_fillet_area
            internal_radius, external_radius = negative_radius, positive_radius
        else:
            # Counter-Clockwise:
            area += positive_fillet_area - negative_fillet_area
            internal_radius, external_radius = positive_radius, negative_radius

        if tracing:
            print(f"{tracing}<=FabPolygon.get_geometry_info()=>"
                  f"({area:.3f}, {perimeter:.3f}, {internal_radius:.3f}, {external_radius:.3f})")
        return area, perimeter, internal_radius, external_radius

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

    # FabPolygon.projectToPlane():
    def projectToPlane(self, plane: FabPlane, tracing: str = "") -> "FabPolygon":
        """Return nre FabPolygon projected onto a plane.

        Arguments:
        * *plane* (FabPlane): The plane to project onto.

        Returns:
        * (FabPolyGon): The newly projected FabPolygon.

        """
        if tracing:
            print(f"{tracing}=>FabPolygon.projectToPlane({plane})")
        corner: Union[Vector, Tuple[Vector, Union[int, float]]]
        projected_corners: List[Union[Vector, Tuple[Vector, Union[int, float]]]] = []
        for corner in self.Corners:
            if isinstance(corner, Vector):
                projected_corners.append(plane.projectPoint(corner))  # pragma: no unit cover
            elif isinstance(corner, tuple):
                assert len(corner) == 2
                point: Any = corner[0]
                radius: Any = corner[1]
                assert isinstance(point, Vector)
                assert isinstance(radius, (int, float))
                projected_corners.append(plane.projectPoint(point))
        projected_polygon: "FabPolygon" = FabPolygon(plane, tuple(projected_corners))
        if tracing:
            print(f"{tracing}<=FabPolygon.projectToPlane({plane})=>*")
        return projected_polygon

    # FabPolygon._double_link():
    def _double_link(self) -> None:
        """Double link the Fab_Fillet's together."""
        fillets: Tuple[Fab_Fillet, ...] = self._Fillets
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
        for at_fillet in self._Fillets:
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
        for at_fillet in self._Fillets:
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
        for fillet in self._Fillets:
            if fillet.Radius > 0.0:
                fillet.Arc = fillet.compute_arc()

    # FabPolygon._compute_lines():
    def _compute_lines(self) -> None:
        """Create Create any Line's need for Fab_Fillet's."""
        fillet: Fab_Fillet
        for fillet in self._Fillets:
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
        for fillet in self._Fillets:
            geometries.extend(fillet.get_geometries())
        return tuple(geometries)

    # FabPolygon._plane_2d_project():
    def _plane_2d_project(self, plane: FabPlane) -> None:
        """Update the Fab_Fillet's to be projected onto a Plane.

        Arguments:
        * *plane* (FabPlane): The plane to modify the Fab_Fillet's to be on.

        """
        fillet: Fab_Fillet
        for fillet in self._Fillets:
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
        plane: FabPlane = FabPlane(plane_contact, plane_normal)

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

    # FabPolygon._check_info():
    @staticmethod
    def _check_info(
            test_name: str, corners: Tuple[Any, ...], desired_area: float, desired_perimeter: float,
            desired_internal_radius: float, desired_external_radius, tracing: str = "") -> None:
        """Check that Fab_GeometryInfo is correct."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabPolygon._check_info('{test_name}', *, "
                  f"{desired_area:.3f}, {desired_perimeter:.3f}, "
                  f"{desired_internal_radius:.3f}, {desired_external_radius:.3f})")
        origin: Vector = Vector()
        z_axis: Vector = Vector(0.0, 0.0, 1.0)
        xy_plane: FabPlane = FabPlane(origin, z_axis)

        polygon1: FabPolygon = FabPolygon(xy_plane, corners)
        info1: Fab_GeometryInfo = Fab_GeometryInfo(polygon1, xy_plane, tracing=next_tracing)
        info1._check(test_name, desired_area, desired_perimeter,
                     desired_internal_radius, desired_external_radius, tracing=next_tracing)

        polygon2: FabPolygon = FabPolygon(xy_plane, tuple(reversed(corners)))
        info2: Fab_GeometryInfo = Fab_GeometryInfo(polygon2, xy_plane)
        info2._check(test_name, desired_area, desired_perimeter,
                     desired_internal_radius, desired_external_radius, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=FabPolygon._check_info('{test_name}', *, "
                  f"{desired_area:.3f}, {desired_perimeter:.3f}, "
                  f"{desired_internal_radius:.3f}, {desired_external_radius:.3f})")

    # FabPolygon._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run FabPolygon unit tests."""
        # next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabPolygon._unit_tests()")

        # Create *corners* and a *copied_corners:
        ne_corner: Vector = Vector(10, 10, 0)  # On XY Plane (no radius)
        nw_corner: Vector = Vector(-10, 10, 1)  # Above XY Plane (no radius)
        sw_corner: Tuple[Vector, int] = (Vector(-10, -10, 0), 2)  # On XY Plane (integer radius)
        se_corner: Tuple[Vector, float] = (
            Vector(10, -10, 2), 3.4)  # Above X/Y Plane (float radius)

        copy: Vector = Vector()
        corners: Tuple[Union[Vector, Tuple[Vector, Union[float, int]]], ...] = (
            ne_corner, nw_corner, sw_corner, se_corner)
        copied_corners: Tuple[Union[Vector, Tuple[Vector, Union[float, int]]], ...] = (
            ne_corner + copy,
            nw_corner + copy,
            (sw_corner[0] + copy, sw_corner[1]),
            (se_corner[0] + copy, se_corner[1]),
        )
        assert corners == copied_corners

        # Create *projected_corners*:
        projected_ne_corner: Tuple[Vector, float] = (Vector(10, 10, 0), 0.0)
        projected_nw_corner: Tuple[Vector, float] = (Vector(-10, 10, 0), 0.0)
        projected_sw_corner: Tuple[Vector, float] = (Vector(-10, -10, 0), 2.0)
        projected_se_corner: Tuple[Vector, float] = (Vector(10, -10, 0), 3.4)
        projected_corners: Tuple[Tuple[Vector, float], ...] = (
            projected_ne_corner, projected_nw_corner, projected_sw_corner, projected_se_corner)

        # Create *polygon1* and verify that has valid values:
        origin: Vector = Vector()
        z_axis: Vector = Vector(0, 0, 1)
        xy_plane: FabPlane = FabPlane(origin, z_axis)
        polygon1: FabPolygon = FabPolygon(xy_plane, corners)
        assert polygon1.Corners == corners
        assert polygon1.Corners == copied_corners
        assert polygon1.ProjectedCorners == projected_corners

        # Now mutate the original *corners* and verify that the mutations did not get:
        ne_corner.x = 1.2
        nw_corner.y = 3.4
        sw_corner[0].x = 5.6
        se_corner[0].z = 7.8
        assert polygon1.Corners != corners
        assert polygon1.Corners == copied_corners
        assert polygon1.ProjectedCorners == projected_corners

        # Verify Box property works:
        box: FabBox = polygon1.Box
        assert box.BSW == Vector(-10.0, -10.0, 0.0), box.BSW
        assert box.TNE == Vector(10.0, 10.0, 0.0), box.TNE

        # The area compute method is pretty involved and requires extensive unit tests.

        # Create 16 corners using the following naming [NS][EW][IONEWS], where
        # * N=>North
        # * S=>South
        # * E=>East
        # * W=>West
        # * I=>Inner
        # * O=>Outer
        #
        # The North East corner looks like:
        #
        #             NEW (NorthEast corner to the West)
        #    ----------*------* NEO (NorthEash corner Outer)
        #              |      |
        #              |      |
        #              *------* NES (NorthEast corner to the South)
        #             NEI     | NEI => (NorthEast corner Inner)
        #                     |
        #
        # Thus, the corners must be:
        #
        #    *-*---------------*-*
        #    | |               | |
        #    *-*               *-*
        #    |                   |
        #    |                   |
        #    |                   |
        #    |                   |
        #    *-*               *-*
        #    | |               | |
        #    *-*---------------*-*
        #
        # All corners on the eastern side have a radius of 1mm.
        # All corners on the western side have a radius of 2mm.

        # Create 4 quads of corners:
        length: float = 80.0
        half_length: float = length / 2.0
        width: float = 40.0
        half_width: float = width / 2.0
        offset: float = 4.0
        dx: Vector = Vector(half_length, 0.0, 0.0)
        ddx: Vector = Vector(offset, 0.0, 0.0)
        dy: Vector = Vector(0.0, half_width, 0.0)
        ddy: Vector = Vector(0.0, offset, 0.0)

        neo: Vector = dx + dy  # No corner
        new: Vector = neo - ddx
        nes: Vector = neo - ddy
        nei: Vector = neo - ddx - ddy
        neof: Tuple[Vector, float] = (neo, 1.0)
        newf: Tuple[Vector, float] = (new, 1.0)
        nesf: Tuple[Vector, float] = (nes, 1.0)
        neif: Tuple[Vector, float] = (nei, 1.0)
        ne_notch: Tuple[Vector, ...] = (nes, nei, new)
        nef_notch: Tuple[Tuple[Vector, float], ...] = (nesf, neif, newf)

        swo: Vector = -dx - dy
        swe: Vector = swo + ddx
        swn: Vector = swo + ddy
        swi: Vector = swo + ddx + ddy
        swof: Tuple[Vector, float] = (swo, 2.0)
        swef: Tuple[Vector, float] = (swe, 2.0)
        swnf: Tuple[Vector, float] = (swn, 2.0)
        swif: Tuple[Vector, float] = (swi, 2.0)
        sw_notch: Tuple[Vector, ...] = (swn, swi, swe)
        swf_notch: Tuple[Tuple[Vector, float], ...] = (swnf, swif, swef)

        nwo: Vector = -dx + dy
        nwe: Vector = nwo + ddx
        nws: Vector = nwo - ddy
        nwi: Vector = nwo + ddx - ddy
        nwof: Tuple[Vector, float] = (nwo, 2.0)
        nwef: Tuple[Vector, float] = (nwe, 2.0)
        nwsf: Tuple[Vector, float] = (nws, 2.0)
        nwif: Tuple[Vector, float] = (nwi, 2.0)
        nw_notch: Tuple[float, ...] = (nwe, nwi, nws)
        nwf_notch: Tuple[Tuple[Vector, float], ...] = (nwef, nwif, nwsf)

        seo: Vector = dx - dy
        sew: Vector = seo - ddx
        sen: Vector = seo + ddy
        sei: Vector = seo - ddx + ddy
        seof: Tuple[Vector, float] = (seo, 1.0)
        sewf: Tuple[Vector, float] = (sew, 1.0)
        senf: Tuple[Vector, float] = (sen, 1.0)
        seif: Tuple[Vector, float] = (sei, 1.0)
        se_notch: Tuple[float, ...] = (sew, sei, sen)
        sef_notch: Tuple[Tuple[Vector, float], ...] = (sewf, seif, senf)

        notch_area: float = offset * offset
        side_area: float = offset * (width - 2.0 * offset)
        side_perimeter: float = 2.0 * offset  # The notch goes both in and out by *offset*.o

        # Side notches:
        east_side_notch: Tuple[Vector, ...] = (seo, sen, sei, nei, nes, neo)
        west_side_notch: Tuple[Vector, ...] = (nwo, nws, nwi, swi, swn, swo)
        east_side_notchf: Tuple[Vector, ...] = (seof, senf, seif, neif, nesf, neof)
        west_side_notchf: Tuple[Vector, ...] = (nwof, nwsf, nwif, swif, swnf, swof)

        area: float = length * width  # Total rectangle area.
        perimeter: float = 2 * length + 2 * width
        simple_rectangle: Tuple[Vector, ...] = (neo, nwo, swo, seo)
        FabPolygon._check_info("no fillets",
                               simple_rectangle, area, perimeter, -1.0, 0.0)

        # Make sure that failures are actually detected:
        try:
            FabPolygon._check_info("area_fail",
                                   simple_rectangle, 123.0, perimeter, -1.0, -1.0)
            assert False
        except RuntimeError as error:
            assert str(error) == (
                "area_fail: Area: Want 123.000, not 3200.000"), str(error)
        try:
            # -1 expected for no extenral fillets
            # -1 expected for no internal fillets
            FabPolygon._check_info("perimeter_fail",
                                   simple_rectangle, area, 123.0, -1.0, -1.0)
            assert False
        except RuntimeError as error:
            assert str(error) == (
                "perimeter_fail: Perimeter: Want 123.000, not 240.000"), str(error)
        try:
            FabPolygon._check_info("internal_radius_fail",
                                   simple_rectangle, area, perimeter, 123.0, -1.0)
            assert False
        except RuntimeError as error:
            assert str(error) == (
                "internal_radius_fail: DesiredInternalRadius: Want 123.000, not -1.000"), (
                    str(error))
        try:
            FabPolygon._check_info("external_radius_fail",
                                   simple_rectangle, area, perimeter, -1.0, 123.0)
            assert False
        except RuntimeError as error:
            assert str(error) == (
                "external_radius_fail: DesiredExternalRadius: Want 123.000, not 0.000"), str(error)

        def fillet_area(radius: float) -> float:
            """Return fillet area for 90 degree fillet."""
            diameter: float = 2.0 * radius
            square_area: float = diameter * diameter
            pi: float = math.pi
            circle_area: float = pi * radius * radius
            fillet_area: float = (square_area - circle_area) / 4.0  # 1/4 => 90 degrees
            return fillet_area

        # Round the corner by 1mm
        radius1: float = 1.0
        radius2: float = 2.0
        fillet_1mm: float = fillet_area(radius1)
        fillet_2mm: float = fillet_area(radius2)
        pi: float = math.pi
        perimeter_1mm = 2.0 * pi * radius1 / 4.0 - 2.0 * radius1   # 1/4 1mm circle - 2x1mm
        perimeter_2mm = 2.0 * pi * radius2 / 4.0 - 2.0 * radius2   # 1/4 2mm circle - 2x2mm

        # Do non-fillet tests first:
        FabPolygon._check_info("no notches",
                               (neo, nwo, swo, seo), area, perimeter, -1.0, 0.0)
        FabPolygon._check_info("ne notch", ne_notch + (nwo, swo, seo),
                               area - notch_area, perimeter, 0.0, 0.0)
        FabPolygon._check_info("nw notch", nw_notch + (swo, seo, neo),
                               area - notch_area, perimeter, 0.0, 0.0)
        FabPolygon._check_info("sw notch", sw_notch + (seo, neo, nwo),
                               area - notch_area, perimeter, 0.0, 0.0)
        FabPolygon._check_info("se notch", se_notch + (neo, nwo, swo),
                               area - notch_area, perimeter, 0.0, 0.0)

        FabPolygon._check_info("ne/nw notch", ne_notch + nw_notch + (swo, seo),
                               area - 2.0 * notch_area, perimeter, 0.0, 0.0)
        FabPolygon._check_info("nw/sw notch", nw_notch + sw_notch + (seo, neo),
                               area - 2.0 * notch_area, perimeter, 0.0, 0.0)
        FabPolygon._check_info("sw/se notch", sw_notch + se_notch + (neo, nwo),
                               area - 2.0 * notch_area, perimeter, 0.0, 0.0)
        FabPolygon._check_info("se/ne notch", se_notch + ne_notch + (nwo, swo),
                               area - 2.0 * notch_area, perimeter, 0.0, 0.0)
        FabPolygon._check_info("ne/sw notch", ne_notch + (nwo,) + sw_notch + (seo,),
                               area - 2.0 * notch_area, perimeter, 0.0, 0.0)
        FabPolygon._check_info("nw/se notch", nw_notch + (swo,) + se_notch + (neo,),
                               area - 2.0 * notch_area, perimeter, 0.0, 0.0)

        FabPolygon._check_info("all notches", ne_notch + nw_notch + sw_notch + se_notch,
                               area - 4.0 * notch_area, perimeter, 0.0, 0.0)

        # Side notches with no fillets:
        FabPolygon._check_info("east side notch", east_side_notch + (nwo, swo),
                               area - side_area, perimeter + side_perimeter, 0.0, 0.0)
        FabPolygon._check_info("west side notch", west_side_notch + (seo, neo),
                               area - side_area, perimeter + side_perimeter, 0.0, 0.0)
        FabPolygon._check_info("both side notch", east_side_notch + west_side_notch,
                               area - 2.0 * side_area, perimeter + 2.0 * side_perimeter, 0.0, 0.0)

        # Rectangle tests with no internal fillets:
        # Single fillets at all 4 corners:
        FabPolygon._check_info("ne fillet only",  # 1 x 1 mm fillet
                               (neof, nwo, swo, seo),
                               area - fillet_1mm,
                               perimeter + perimeter_1mm, -1.0, 0.0)
        FabPolygon._check_info("nw fillet only",  # 1 x 2 mm fillet
                               (nwof, swo, seo, neo),
                               area - fillet_2mm,
                               perimeter + perimeter_2mm, -1.0, 0.0)
        FabPolygon._check_info("se fillet only",  # 1 x 1 mm fillet
                               (seof, neo, nwo, swo),
                               area - fillet_1mm,
                               perimeter + perimeter_1mm, -1.0, 0.0)
        FabPolygon._check_info("sw fillet only",  # 1 x 2 mm fillet
                               (swof, seo, neo, nwo),
                               area - fillet_2mm,
                               perimeter + perimeter_2mm, -1.0, 0.0)

        # Adjacent adjacent corner pairs:
        FabPolygon._check_info("ne,nw fillet only",  # 1 x 1 mm fillet + 1 x 2mm fillet
                               (neof, nwof, swo, seo),
                               area - fillet_1mm - fillet_2mm,
                               perimeter + perimeter_1mm + perimeter_2mm, -1.0, 0.0)
        FabPolygon._check_info("nw,sw fillets",   # 2 x 2 mm fillets
                               (nwof, swof, seo, neo),
                               area - 2 * fillet_2mm,
                               perimeter + 2.0 * perimeter_2mm, -1.0, 0.0)
        FabPolygon._check_info("sw,se fillet only",  # 1 x 1 mm fillet + 1 x 2mm fillet
                               (swof, seof, neo, nwo),
                               area - fillet_1mm - fillet_2mm,
                               perimeter + perimeter_1mm + perimeter_2mm, -1.0, 0.0)
        FabPolygon._check_info("se,ne fillet only",  # 1 x 1 mm fillet + 1 x 2mm fillet
                               (seof, neof, nwo, swo),
                               area - 2 * fillet_1mm,
                               perimeter + 2.0 * perimeter_1mm, -1.0, 0.0)

        # Diagonal corners:
        FabPolygon._check_info("ne,sw fillet only",  # 1 x 1 mm fillet + 1 x 2mm fillet
                               (neof, nwo, swof, seo),
                               area - fillet_1mm - fillet_2mm,
                               perimeter + perimeter_1mm + perimeter_2mm, -1.0, 0.0)
        FabPolygon._check_info("nw,se fillet only",  # 1 x 1 mm fillet + 1 x 2mm fillet
                               (nwof, swo, seof, neo),
                               area - fillet_1mm - fillet_2mm,
                               perimeter + perimeter_1mm + perimeter_2mm, -1.0, 0.0)

        # All 4 corners:
        FabPolygon._check_info("rectangle with all fillets",  # 2 x 1 mm fillets + 2 x 2 mm fillets
                               (neof, nwof, swof, seof),
                               area - 2 * fillet_1mm - 2 * fillet_2mm,
                               perimeter + 2.0 * perimeter_1mm + 2.0 * perimeter_2mm, -1.0, radius1)

        # From here on, all corners have some sort of fillet enabled.

        # Fillet notch each of the 4 corners:
        if tracing:
            print(f"{tracing}{area=:.3f} {notch_area=:.3f} {fillet_1mm=:.3f} {fillet_2mm=:.3f}")
        FabPolygon._check_info("ne fillet notch",
                               nef_notch + (nwof, swof, seof),
                               area - notch_area - 2 * fillet_1mm - 2 * fillet_2mm,
                               perimeter + 4 * perimeter_1mm + 2 * perimeter_2mm, radius1, radius1)
        FabPolygon._check_info("nw fillet_notch",
                               nwf_notch + (swof, seof, neof),
                               area - notch_area - 2 * fillet_1mm - 2 * fillet_2mm,
                               perimeter + 2 * perimeter_1mm + 4 * perimeter_2mm, radius2, radius1)
        FabPolygon._check_info("sw fillet notch",
                               swf_notch + (seof, neof, nwof),
                               area - notch_area - 2 * fillet_1mm - 2 * fillet_2mm,
                               perimeter + 2 * perimeter_1mm + 4 * perimeter_2mm, radius2, radius1)
        FabPolygon._check_info("se fillet notch",
                               sef_notch + (neof, nwof, swof),
                               area - notch_area - 2 * fillet_1mm - 2 * fillet_2mm,
                               perimeter + 4 * perimeter_1mm + 2 * perimeter_2mm, radius1, radius1)

        FabPolygon._check_info("ne/se fillet notch",
                               nef_notch + (nwof, swof) + sef_notch,
                               area - 2 * notch_area - 2 * fillet_1mm - 2 * fillet_2mm,
                               perimeter + 6 * perimeter_1mm + 2 * perimeter_2mm, radius1, radius1)
        FabPolygon._check_info("nw/sw fillet notch",  # Both internal radii are 2mm.
                               nwf_notch + swf_notch + (seof, neof),
                               area - 2 * notch_area - 2 * fillet_1mm - 2 * fillet_2mm,
                               perimeter + 2 * perimeter_1mm + 6 * perimeter_2mm, radius2, radius1)
        FabPolygon._check_info("ne/nw fillet notch",
                               nef_notch + nwf_notch + (swof, seof),
                               area - 2 * notch_area - 2 * fillet_1mm - 2 * fillet_2mm,
                               perimeter + 4 * perimeter_1mm + 4 * perimeter_2mm, radius1, radius1)
        FabPolygon._check_info("sw/se fillet notch",
                               swf_notch + sef_notch + (neof, nwof),
                               area - 2 * notch_area - 2 * fillet_1mm - 2 * fillet_2mm,
                               perimeter + 4 * perimeter_1mm + 4 * perimeter_2mm, radius1, radius1)
        FabPolygon._check_info("notch all",
                               nef_notch + nwf_notch + swf_notch + sef_notch,
                               area - 4 * notch_area - 2 * fillet_1mm - 2 * fillet_2mm,
                               perimeter + 6 * perimeter_1mm + 6 * perimeter_2mm, radius1, radius1)

        # Side notches with fillets:
        FabPolygon._check_info("east side fillet notch",
                               east_side_notchf + (nwof, swof),
                               area - 1 * side_area - 2 * fillet_1mm - 2 * fillet_2mm,
                               perimeter + 2 * offset + 6 * perimeter_1mm + 2 * perimeter_2mm,
                               radius1, radius1)
        FabPolygon._check_info("west side fillet notch",
                               west_side_notchf + (seof, neof),
                               area - 1 * side_area - 2 * fillet_1mm - 2 * fillet_2mm,
                               perimeter + 2 * offset + 2 * perimeter_1mm + 6 * perimeter_2mm,
                               radius2, radius1)
        FabPolygon._check_info("both side fillet notch",
                               west_side_notchf + east_side_notchf,
                               area - 2 * side_area - 2 * fillet_1mm - 2 * fillet_2mm,
                               perimeter + 4 * offset + 6 * perimeter_1mm + 6 * perimeter_2mm,
                               radius1, radius1)

        if tracing:
            print(f"{tracing}<=FabPolygon._unit_tests()")


# Fab_GeometryInfo:
@dataclass
class Fab_GeometryInfo(object):
    """Fab_GeometryInfo: Information about a FabGeomtry object.

    Attributes:
    * Geometry (FabGeometry): The FabGeometry object used.
    * Plane (FabPlane): The geometry plane to project onto.
    * Area (float): The geometry area in square millimeters.
    * Perimeter (float): The perimeter length in millimetes.
    * MinimumInternalRadius:
      The minimum internal radius in millimeters. -1.0 means there is no internal radius.
    * MinimumExternalRadius:
      The minimum external radius in millimeters.

    Constructor:
    * Fab_GeometryInfo(Geometry)
    """

    Geometry: FabGeometry
    Plane: FabPlane
    tracing: str = ""  # TODO: remove for debugging only
    Area: float = field(init=False)  # Filled in by __post_init__()
    Perimeter: float = field(init=False)  # Filled in by __post_init__()
    MinimumInternalRadius: float = field(init=False)  # Filled in by __post_init__()
    MinimumExternalRadius: float = field(init=False)  # Filled in by __post_init__()

    # Fab_GeometryInfo.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing Fab_GeometryInfo."""
        # Manually set *tracing* to debug.
        tracing: str = self.tracing
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_GeometryInfo.__post_init__()")
        check_type("Fab_GeometryInfo.Geometry", self.Geometry, FabGeometry)
        check_type("Fab_GeometryInfo.Geometry", self.Geometry, FabGeometry)
        self.Area, self.Perimeter, self.MinimumInternalRadius, self.MinimumExternalRadius = (
            self.Geometry.get_geometry_info(self.Plane, tracing=next_tracing))
        if tracing:
            print(f"{tracing}<=Fab_GeometryInfo.__post_init__()")

    # Fab_GeometryInfo._check():
    def _check(
            self, test_name: str, desired_area: float, desired_perimeter: float,
            desired_internal_radius: float, desired_external_radius: float, tracing: str = ""
    ) -> None:
        """Check: test

        Arguments:
        * *test_name*: The test name to print on an error.
        * *desired_area*: The desired area.
        * *desired_perimeter*: The desired perimeter.
        * *desired_internal_radius*: The desired internal radius.
        * *desired_external_radius*: The desired external radius.

        # Raises:
        * RuntimeError if the actual values do not match to desired to with .001mm.

        """
        # next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Fab_GeometryInfo._check('{test_name}', "
                  f"{desired_area:.3f}, {desired_perimeter:.3f}, "
                  f"{desired_internal_radius:.3f}, {desired_external_radius:.3f})")

        epsilon: float = 0.001  # Only match to !three places after the decimal point.
        error: str = ""
        if abs(desired_area - self.Area) > epsilon:
            error = (f"{test_name}: Area: Want {desired_area:.3f}, "
                     f"not {self.Area:.3f}")
        elif abs(desired_perimeter - self.Perimeter) > epsilon:
            error = (f"{test_name}: Perimeter: Want {desired_perimeter:.3f}, "
                     f"not {self.Perimeter:.3f}")
        elif abs(desired_internal_radius - self.MinimumInternalRadius) > epsilon:
            error = (f"{test_name}: DesiredInternalRadius: Want {desired_internal_radius:.3f}, "
                     f"not {self.MinimumInternalRadius:.3f}")
        elif abs(desired_external_radius - self.MinimumExternalRadius) > epsilon:
            error = (f"{test_name}: DesiredExternalRadius: Want {desired_external_radius:.3f}, "
                     f"not {self.MinimumExternalRadius:.3f}")
        if error:
            raise RuntimeError(error)

        if tracing:
            print(f"{tracing}<=Fab_GeometryInfo._check('{test_name}', "
                  f"{desired_area:.3f}, {desired_perimeter:.3f}, "
                  f"{desired_internal_radius:.3f}, {desired_external_radius:.3f})")

    # Fab_GeometryInfo._unit_tests():
    @staticmethod
    def _unit_tests(self, tracing: str = "") -> None:
        """Run Fab_GeometryInfo unit tests."""
        if tracing:
            print(f"{tracing}=>Fab_GeometryInfo._unit_tests()")

        def close(have: float, want: float) -> None:
            """Fail if two numbers are not  close."""
            assert abs(have - want) < 1.0e-8, f"{have=} != {want=}"

        def circle_check(radius: float) -> None:
            """Fail if a FabCircle computes incorrect Fab_GeometryInfo."""
            origin: Vector = Vector()
            z_axis: Vector = Vector(0.0, 0.0, 1.0)
            xy_plane: FabPlane = FabPlane(origin, z_axis)
            pi: float = math.pi
            circle: FabCircle = FabCircle(xy_plane, origin, 2.0 * radius)
            info: Fab_GeometryInfo = Fab_GeometryInfo(circle, xy_plane)
            close(info.MinimumInternalRadius, -1.0)
            close(info.MinimumExternalRadius, radius)
            close(info.Perimeter, 2.0 * pi * radius)
            close(info.Area, pi * radius * radius)

        circle_check(1.0)
        circle_check(2.0)

        if tracing:
            print(f"{tracing}<=Fab_GeometryInfo._unit_tests()")


# Fab_Query:
@dataclass
class Fab_Query(object):
    """Fab_Query: A CadQuery Workplane wrapper.

    This class creates CadQuery Workplane provides a consistent head of the Workplane chain..
    CadQuery Operations are added as needed.

    Attributes:
    * *Plane* (FabPlane): The plane to use for CadQuery initialization.
    * *WorkPlane: (cadquery.Workplane): The resulting CadQuery Workplane object.

    """
    _Plane: FabPlane
    _Query: Any = field(init=False, repr=False, default=None)

    # Fab_Query.__post_init__():
    def __post_init__(self) -> None:
        """Initialize FabPlane."""
        if not isinstance(self._Plane, FabPlane):
            raise RuntimeError(
                f"Fab_Query.__post_init__(): Got {type(self._Plane)}, "
                "not FabPlane")  # pragma: no unit cover
        plane = cast(cq.Plane, self._Plane._Plane)
        self._Query = cq.Workplane(plane)

    # Fab_Query.Plane():
    # @property
    # def Plane(self) -> FabPlane:
    #     """Return the FabPlane associated from a Fab_Query."""
    #     assert isinstance(self._Plane, FabPlane), self._Plane
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
    def copy_workplane(self, plane: FabPlane, tracing: str = "") -> None:
        """Create a new CadQuery workplane and push it onto the stack."""
        if tracing:
            print(f"{tracing}=>Fab_Query.copy_workPlane({plane})")
        if not isinstance(plane, FabPlane):
            raise RuntimeError(
                f"Fab_Query.copy_workplane(): Got {type(plane)}, "
                "not FabPlane")  # pragma: no unit cover
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


def main(tracing: str = "") -> None:
    """Run main program."""
    next_tracing: str = tracing + " " if tracing else ""
    if tracing:
        print(f"{tracing}=>FabGeometries.main()")
    Fab_Fillet._unit_tests(tracing=next_tracing)
    FabCircle._unit_tests(tracing=next_tracing)
    FabPolygon._unit_tests(tracing=next_tracing)
    Fab_GeometryInfo._unit_tests(tracing)
    if tracing:
        print(f"{tracing}<=FabGeometries.main()")


if __name__ == "__main__":
    main(tracing=" ")
