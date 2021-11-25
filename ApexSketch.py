#!/usr/bin/env python3
"""ApexSketch: An interface to FreeCAD Sketches.

This module provides an interface that both creates FreeCAD sketches and applies those sketches
to FreeCAD Part Design workbench Body objects.  Addition information is provided to supporting
the FreeCAD Path workbench.

The are 4 base classes of used in this module:
* ApexDrawing: Create one or more FreeCAD Sketches and applies Part Design and Path operations.
* ApexOperation: This is the Part Design and Path operation information.
* ApexShape: This is the geometric shapes that go into the ApexDrawing.
* ApexGeometry: The class of objects represents 2D geometric constructs (point, line, arc, circle).

There is a rich set of FreeCAD PartDesign operations that can be applied to sketches.
The construction operations are pad, revolve, loft, sweep and helix.
The subtraction operations are pocket, hole, groove, loft, sweep and helix.
The current ApexOperation sub-classes are:
* ApexPad: Performs a FreeCAD Part Design pad operation.
* ApexPocket: Performs a FreeCAD Part Design pocket operation
* ApexHole: Performs a FreeCAD Part Design pocket operation
Each of these these operations takes either an ApexCircle or an ApexPolygon as an argument.

The ApexShape sub-classes are:
* ApexCircle: This represents a circle in the ApexDrawing.
* ApexPolygon: This is basically a sequence of ApexCorner's (see below) that represent a polygon,
  where each corner can optionally have rounded with a fillet.
* ApexCorner: This represents one corner of an ApexPolygon and specifies the fillet radius.
Each ApexShape has an associated ApexOperation (see below).

The internal ApexGeometry sub-classes are:
* ApexPoint: This represents a single point geometry.
* ApexLine: This represents a line segment geometry.
* ApexArc: This represents an arc on a circle geometry.
* ApexCircle This represents a circle geometry.

All of this information is collected into an ApexDrawing instance.
The ApexDrawing.body_apply() takes a FreeCAD Part Design Body and applies operations drawing to it.
"""

# (Sketcher Constrain Angle)[https://wiki.freecadweb.org/Sketcher_ConstrainAngle]
# (Sketcher Scripting)[https://wiki.freecadweb.org/Sketcher_ConstrainAngle]
# (Sketcher Switch Between Multiple Solutions)[https://www.youtube.com/watch?v=Q43K23k1noo&t=20s]
# (Sketcher Toggle Constructions)[https://wiki.freecadweb.org/Sketcher_ToggleConstruction]

# Note this code uses nested dataclasses that are frozen.  Computed attributes are tricky.
# See (Set frozen data class files in __post_init__)[https://stackoverflow.com/questions/53756788]

import os
import sys

assert sys.version_info.major == 3  # Python 3.x
assert sys.version_info.minor == 8  # Python 3.8
sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])

from dataclasses import dataclass, field
import math
from typing import Any, Callable, cast, Dict, List, Optional, Tuple, Union

import FreeCAD as App  # type: ignore
import FreeCADGui as Gui  # type: ignore

from Apex import ApexBox, ApexCheck, vector_fix
from FreeCAD import Placement, Rotation, Vector
from pathlib import Path  # type: ignore
import Part  # type: ignore
import PartDesign  # type: ignore
import Sketcher  # type: ignore


PartGeometry = Union[Part.Circle, Part.LineSegment, Part.Point, Part.Arc]

# In general, the classes are organized from lowest level to highest level.
# This is primarily to avoid have to add addition quotes around mypy type hints.

# ApexCorner:
@dataclass(frozen=True)
class ApexCorner(object):
    """ApexCorner: An ApexPolygon corner with a radius.

    Usage: ApexCorner(point, radius, name)

    Attributes:
    * *Point* (Vector): A point for a polygon.
    * *Radius (float): The corner radius in millimeters.  (Default: 0.0)
    * *Name* (str): The corner name. (Default: "")
    * *Box* (ApexBox): A computed ApexBox that encloses corner as if it was a sphere of size Radius.

    """

    Point: Vector
    Radius: float = field(default=0.0)
    Name: str = field(default="")
    Box: ApexBox = field(init=False)

    POST_INIT_CHECKS = (
        ApexCheck("Point", (Vector,)),
        ApexCheck("Radius", (float,)),
        ApexCheck("Name", (str,)),
    )

    # ApexCorner.__post_init__():
    def __post_init__(self) -> None:
        """Verify contents of ApexCorner."""
        arguments: Tuple[Any, ...] = (self.Point, self.Radius, self.Name)
        value_error: str = ApexCheck.check(arguments, ApexCorner.POST_INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)
        if self.Radius < 0.0:
            raise ValueError(f"Radius=({self.Radius}) must be non-negative")

        # Compute the enclosing *box*:
        offset: Vector = Vector(self.Radius, self.Radius, self.Radius)
        box: ApexBox = ApexBox((self.Point + offset, self.Point - offset))
        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        object.__setattr__(self, "Box", box)

    # ApexCorner.__repr__():
    def __repr__(self) -> str:
        """Return string representation of ApexCorner."""
        return self.__str__()

    # ApexCorner.__str__():
    def __str__(self) -> str:
        """Return string representation of ApexCorner."""
        return f"ApexCorner({self.Point}, {self.Radius}, '{self.Name}')"

    # ApexCorner._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Run unit tests for ApexCorner."""
        # Create *corner* and verify attributes:
        point: Vector = Vector(1.0, 2.0, 3.0)
        radius: float = 4.0
        name: str = "name"
        corner: ApexCorner = ApexCorner(point, radius, name)
        corner.Point == point, corner.Point
        corner.Radius == radius, corner.Radius
        corner.Name == name, corner.Name

        # Verify __repr__() an __str__():
        want: str = "ApexCorner(Vector (1.0, 2.0, 3.0), 4.0, 'name')"
        assert f"{corner}" == want, f"{corner}"
        assert corner.__repr__() == want, corner.__repr__()
        assert str(corner) == want, str(corner)

        # Bad Point:
        try:
            ApexCorner(cast(Vector, 0), radius, name)
            assert False
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'Point' is int which is not one of ['Vector']"), str(value_error)

        # Negative Radius:
        try:
            ApexCorner(point, -10.0, name)
            assert False
        except ValueError as value_error:
            assert str(value_error) == "Radius=(-10.0) must be non-negative", str(value_error)

        # Bad Name:
        try:
            ApexCorner(point, radius, cast(str, 0))
            assert False
        except ValueError as value_error:
            assert str(value_error) == (
                "Argument 'Name' is int which is not one of ['str']"), str(value_error)


# ApexGeometry:
class ApexGeometry(object):
    """ApexGeometry: Internal Base class for 2D geometry objects.

    This is basically a wrapper around the arguments need to create Sketch elements.
    It is mutable and always contains a bunch of helper functions.
    """

    # ApexGeometry.__init__():
    def __init__(self, drawing: "ApexDrawing",
                 start: Vector, finish: Vector, name: str = "") -> None:
        """Initialize a ApexGeometry."""
        self._drawing: ApexDrawing = drawing
        self._index: int = -999
        self._origin_index: int = -999
        self._name: str = name
        self._next: ApexGeometry = self
        self._previous: ApexGeometry = self
        # print(f"<=>ApexGeometry.__init__(*, {self._part_geometry}, '{self._name}')")

    # ApexGeometry.drawing():
    @property
    def drawing(self) -> "ApexDrawing":  # pragma: no unit test
        """Return the ApexGeometry ApexDrawing."""
        return self._drawing  # pragma: no unit test

    # ApexGeometry.finish():
    @property
    def finish(self) -> Vector:  # pragma: no unit test
        """Return the ApexGeometry finish point."""
        raise NotImplementedError(f"ApexGeometry.start() not implemented for {self}")

    # ApexGeometry.index():
    @property
    def index(self) -> int:
        """Return the ApexGeometry index."""
        assert self._index >= -1, f"index is not set: {self}"
        return self._index

    # ApexGeometry.index.setter():
    @index.setter
    def index(self, index: int) -> None:
        """Set the ApexGeometry index."""
        if self._index >= -1:
            raise ValueError("index is already set")  # pragma: no unit test
        if index < -1:
            raise ValueError(f"index(={index} must >= -1")  # pragma: no unit test
        self._index = index

    @property
    def finish_key(self) -> int:  # pragma: no unit test
        """Return the ApexGeometry Constraint key for the finish point."""
        raise NotImplementedError(f"{self}.finish_key() not implemented yet.")

    # ApexGeometry.name():
    @property
    def name(self) -> str:
        """Return ApexGeometry name."""
        return self._name

    # ApexGeometry.next()
    @property
    def next(self) -> "ApexGeometry":  # pragma: no unit test
        """Return the next ApexGeometry in circular list."""
        return self._next  # pragma: no unit test

    # ApexGeometry.index.setter():
    @next.setter
    def next(self, next: "ApexGeometry") -> None:
        """Set the next ApexGeometry in circular list."""
        self._next = next

    # ApexGeometry.part_geometry():
    @property
    def part_geometry(self) -> PartGeometry:
        """Return the PartGeometry associated with ApexGeometry."""
        raise NotImplementedError(f"{self}.part_geometry not implmented.")

    # ApexGeometry.previous():
    @property
    def previous(self) -> "ApexGeometry":  # pragma: no unit test
        """Return the previous Part ApexGeometry in circular list."""
        return self._previous  # pragma: no unit test

    # ApexGeometry.previous.setter():
    @previous.setter
    def previous(self, next: "ApexGeometry") -> None:
        """Set the previous Part ApexGeometry in circular list."""
        self._previous = next

    # ApexGeometry.start():
    @property
    def start(self) -> Vector:  # pragma: no unit test
        """Return the ApexGeometry start point."""
        raise NotImplementedError(f"ApexGeometry.start() not implemented for {self}")

    @property
    def start_key(self) -> int:
        """Return the ApexGeometry Constraint key for the start point."""
        raise NotImplementedError(f"{self}.start_key() not implemented yet.")

    # ApexGeometry.type_name():
    @property
    def type_name(self) -> str:
        """Return the ApexGeometry type name."""
        raise NotImplementedError(f"{self}.kind() not implemented yet")

    # ApexGeometry.__repr__():
    # def __repr__(self) -> str:
    #     """Return string representation of ApexGeometry."""
    #     return self.__str__()

    # ApexGeometry.__str__():
    # def __str__(self) -> str:
    #     """Return string representation of ApexGeometry."""
    #     raise NotImplementedError(f"ApexGeometry.__str__() not implemented for {type(self)}")

    # ApexGeometry.constraints_append():
    def constraints_append(self, drawing: "ApexDrawing", constraints: List[Sketcher.Constraint],
                           tracing: str = "") -> None:
        """Append the ApexShape constraints to drawing.

        Arguments:
        * *drawing* (ApexDrawing): The drawing to use.
        * *constraints* (List[SketcherConstraint]): The constraints list to append to.

        """
        raise NotImplementedError(
            f"ApexGeometry.constraints_append() not implmented for {type(self)}")


# ApexArcGeometry:
class ApexArcGeometry(ApexGeometry):
    """Represents an an arc in a sketch."""

    # ApexArcGeometry.__init__():
    def __init__(self, drawing: "ApexDrawing",
                 begin: ApexCorner, at: ApexCorner, end: ApexCorner,
                 name: str = "", tracing: str = "") -> None:
        """Initialize an ApexArcGeometry."""
        # next_tracing: str = tracing + " " if tracing else ""
        trace_level: int = 0
        if tracing:
            print(f"{tracing}=>ApexArcGeometry('{begin.Name}', "
                  f"'{at.Name}', '{end.Name}', '{name}')")
            trace_level = 0

        # Notation:
        # * Points: 1 capital letter (e.g. A, B, C, E, etc.)
        # * Line Segments: Two capital letters: (e.g IB, OB, etc.)
        # * Angles: 3 capital letters preceded by an single angle bracket (e.g. <IBO, <CJB, etc. )
        # * Vectors: Two capital letters in angle brackets, where the first letter is the
        #   start and the second letter is the end.: (e.g. <BI>, <BO>, etc.)
        # * Unit Vectors: 2 capital letters in double angle brackets: (e.g. <<BI>>, <<BO>>, etc.)
        # * Length: Two capital letters in vertical bars (e.g. |IB|, |BC|, etc.)
        # * Distance: A lower case letter (e.g. r, etc)
        #
        # Points:
        # * B represents the *begin* Point,
        # * A represents the *apex* Point of the arc
        # * E represents the *end* Point.
        # * C represents the *center* Point of the circle that the arc will be on.
        # * S represents the Point where the circle is tangent to the line IA (i.e. the arc Start):
        # * F represents the Point where the circle is tangent to the line EA (i.e. the arc Finish):
        # * M represents a "mid" Point on the line from A through C.  M is used to compute C.
        #
        # Length:
        # * r represents the arc *radius*:
        #
        # Diagram:
        # * Segments BA and EA meet at the apex point A.
        # * A circle of radius r, centered at C tangentially touches BA and EA at S and F.
        #   (By the way, J is alphabetically after I and N is alphabetically before N.)
        # * The segments CJ and CN (not drawn) are of radius length (e.g. |CJ| = |CN| = r.)
        # * The angles <JBC and <CBN are equal.
        # * The angles <CBJ and <CNB are both 90 degrees.
        # * The a M is somewhere on the line from A through C
        #
        #     B             M
        #      \            |
        #       \         **|**
        #        \      **  |  **      E
        #         \   *     |     *   /
        #          \ *      |      * /
        #           \*      C      */
        #            S      |      F
        #             *     |     *
        #              \**  |  **/
        #               \ **|** /
        #                \  |  /
        #                 \ | /
        #                  \|/
        #                   A
        #

        # The call to the parent *__init__* can not occur until after the *start* and *finish*
        # points are determined.

        # Do some initial float and variable assignments:
        deg: Callable[[float], float] = math.degrees
        epsilon: float = 1.0e-10  # Small number
        pi: float = math.pi  # Pi constant (e.g. 3.14159...)
        r: float = at.Radius
        if r < epsilon:
            raise ValueError("No Arc with zero radius.")  # pragma: no unit test

        # Define some single letter variables for the Point's:
        b: Vector = begin.Point
        a: Vector = at.Point
        e: Vector = end.Point
        if trace_level >= 2:  # pragma: no unit cover
            print(f"{tracing}{b=}")
            print(f"{tracing}{a=}")
            print(f"{tracing}{e=}")

        def normalize_2d(point: Vector) -> Vector:
            """Return Vector that is normalized in X and Y only."""
            x: float = float(point.x)
            y: float = float(point.y)
            length: float = math.sqrt(x * x + y * y)
            return Vector(x / length, y / length)

        # Compute a bunch of values based on B, A, and E:
        ab: Vector = b - a  # <AB>
        ae: Vector = e - a  # <AE>
        unit_ab: Vector = normalize_2d(ab)  # <<AB>>
        unit_ae: Vector = normalize_2d(ae)  # <<AE>>
        unit_am: Vector = normalize_2d(unit_ab + unit_ae)  # <<AM>>
        # unit_ac: Vector = unit_am  # <<C>> == <<BM>> because the are on the same line.
        if trace_level >= 2:  # pragma: no unit cover
            print(f"{tracing}{ab=}")
            print(f"{tracing}{ae=}")

        # Compute the angles from A to B, M, and E:
        ab_angle: float = math.atan2(ab.y, ab.x)
        am_angle: float = math.atan2(unit_am.y, unit_am.x)
        ae_angle: float = math.atan2(ae.y, ae.x)
        sac_angle: float = abs(ab_angle - am_angle) % pi  # C is co-linear with M
        if trace_level >= 2:  # pragma: no unit cover
            print(f"{tracing}{deg(ab_angle)=:.2f}deg")
            print(f"{tracing}{deg(am_angle)=:.2f}deg")
            print(f"{tracing}{deg(ae_angle)=:.2f}deg")
            print(f"{tracing}{deg(sac_angle)=:.2f}deg")

        # The points S, C, and A form a right triangle, where:
        # * Angle <ASC is 90 degrees because the circle centered on C is tangent at S (and F).
        # * |SC| = the circle radius r.
        # * |AC| is the distance from A to C.
        # * |AS| is the distance from A to S.

        # From the sine of a right triangle:
        # * |SC| = |AC| * sin(<SAC)
        # Solve for |AC| given |SC| and sin(<SAC):
        # * |AC| = |SC| / sin(<SAC) = r / sin(<SAC)
        assert sac_angle != 0.0, (begin, at, end)
        ac_length: float = r / math.sin(sac_angle)  # |AC|
        if trace_level >= 2:  # pragma: no unit cover
            print(f"{tracing}{ac_length=:.2f}")

        # From the Pythagorean theorem:
        # * |SC|^2 + |AS|^2 = |AC|^2
        # Solve for |AS|:
        # * |AS|^2 = |AC|^2 - |SC|^2
        # * |AS| = sqrt(|AC|^2 - |SC|^2)
        # * |AS| = sqrt(|AC|^2 - r^2)  # |SC| = r
        as_length: float = math.sqrt(ac_length * ac_length - r * r)
        af_length: float = as_length  # |AS| == |AF|
        if trace_level >= 2:  # pragma: no unit cover
            print(f"{tracing}{as_length=:.2f}")
            print(f"{tracing}{af_length=:.2f}")

        # Compute C, S, and F:
        c: Vector = a + unit_am * ac_length
        s: Vector = a + unit_ab * as_length
        f: Vector = a + unit_ae * af_length
        if trace_level >= 2:  # pragma: no unit cover
            print(f"{tracing}{c=}")
            print(f"{tracing}{s=}")
            print(f"{tracing}{f=}")

        s_minus_c: Vector = s - c
        f_minus_c: Vector = f - c
        start_angle: float = math.atan2(s_minus_c.y, s_minus_c.x)
        finish_angle: float = math.atan2(f_minus_c.y, f_minus_c.x)
        # The *sweep_angle* angle is the number for degrees the arc to get from *start_angle*
        # to *finish_angle*.  This angle can never span more the 180 degrees.
        sweep_angle: float = finish_angle - start_angle
        degrees180: float = pi
        degrees360: float = 2.0 * pi
        if sweep_angle > degrees180:
            sweep_angle -= degrees360  # pragma: no unit test
        elif sweep_angle <= -degrees180:
            sweep_angle += degrees360  # pragma: no unit test
        end_angle: float = start_angle + sweep_angle
        if trace_level >= 2:  # pragma: no unit cover
            print(f"{tracing}{deg(start_angle)=}deg")
            print(f"{tracing}{deg(finish_angle)=}deg")
            print(f"{tracing}{name}: {deg(finish_angle - start_angle)=}deg")
            print(f"{tracing}{deg(sweep_angle)=}deg")
            print(f"{tracing}{deg(end_angle)=}deg")
        part_circle: Part.Circle = Part.Circle(App.Vector(c.x, c.y, 0.0), App.Vector(0, 0, 1), r)

        # After a bunch of trial and error, it was discovered that the *start_angle* and *end_angle*
        # need to be swapped to deal with a negative sweep angle.  This causes the right arc
        # to be rendered properly, but has now swapped the start/finish as far as constraints
        # are concerned.
        if sweep_angle < 0.0:
            start_angle, end_angle = end_angle, start_angle
        part_arc: Part.Arc = Part.ArcOfCircle(part_circle, start_angle, end_angle)

        # Now we can create the *ApexArcGeometry*:
        super().__init__(drawing, s, f, name)
        self._at: Vector = at.Point
        self._begin: Vector = begin.Point
        self._center: Vector = c
        self._end: Vector = end.Point
        self._finish: Vector = f
        self._finish_angle: float = finish_angle
        self._finish_length: float = af_length
        self._part_arc: Part.Arc = part_arc
        self._radius: float = r
        self._start: Vector = s
        self._sweep_angle: float = sweep_angle
        self._start_angle: float = start_angle
        self._start_length: float = as_length

        if trace_level >= 2:  # pragma: no unit cover
            print(f"{tracing}{self._at=}")
            print(f"{tracing}{self._begin=}")
            print(f"{tracing}{self._center=}")
            print(f"{tracing}{self._end=}")
            print(f"{tracing}{self._finish=}")
            print(f"{tracing}{deg(self._finish_angle)=:.2f}deg")
            print(f"{tracing}{self._finish_length=}")
            print(f"{tracing}{self._radius=:.2f}")
            print(f"{tracing}{self._start=}")
            print(f"{tracing}{deg(self._start_angle)=:.2f}deg")
            print(f"{tracing}{self._start_length=}")
            print(f"{tracing}<=ApexArcGeometry(*, {begin=}, {at=}, {end=})")
        if tracing:
            print(f"{tracing}<=ApexArcGeometry('{begin.Name}', "
                  f"'{at.Name}', '{end.Name}', '{name}')")

    # ApexArcGeometry.repr():
    def __repr__(self) -> str:  # pragma: no unit test
        """Return ApexArcGeometry string representation."""
        return f"ApexArcGeometry({self._begin}, {self._at}, {self._end})"  # pragma: no unit test

    # ApexArcGeometry.apex():
    @property
    def at(self) -> Vector:
        """Return the ApexArcGeometry apex Vector."""
        return self._at

    # ApexArcGeometry.begin():
    @property
    def begin(self) -> Vector:  # pragma: no unit test
        """Return the ApexArcGeometry arc begin Vector."""
        return self._begin  # pragma: no unit test

    # ApexArcGeometry.center():
    @property
    def center(self) -> Vector:
        """Return the ApexArcGeometry arc center."""
        return self._center

    # ApexArcGeometry.end():
    @property
    def end(self) -> Vector:  # pragma: no unit test
        """Return the initial ApexArcGeometry end Vector."""
        return self._end  # pragma: no unit test

    # ApexArcGeometry.finish():
    @property
    def finish(self) -> Vector:
        """Return the ApexArcGeometry arc finish Vector."""
        return self._finish

    # ApexArcGeometry.finish_key():
    @property
    def finish_key(self) -> int:
        """Return the ApexArcGeometry finish Constraint key."""
        # return 2
        return 2 if self._sweep_angle < 0 else 1

    # ApexArcGeometry.finish_angle():
    @property
    def finish_angle(self) -> float:  # pragma: no unit test
        """Return the ApexArcGeometry arc finish angle."""
        return self._finish_angle  # pragma: no unit test

    # ApexArcGeometry.finish_length():
    @property
    def finish_length(self) -> float:  # pragma: no unit test
        """Return distance from arc finish Vector to the apex Vector."""
        return self._finish_length  # pragma: no unit test

    # ApexArcGeometry.input():
    @property
    def input(self) -> Vector:  # pragma: no unit test
        """Return the initial ApexArcGeometry arc start Vector."""
        return self._start  # pragma: no unit test

    # ApexArcGeometry.part_geometry():
    @property
    def part_geometry(self) -> PartGeometry:
        """Return ApexArcGeometry Part.Arc."""
        return self._part_arc

    # ApexArcGeometry.radius():
    @property
    def radius(self) -> float:
        """Return the initial ApexArcGeometry radius."""
        return self._radius

    # ApexArcGeometry.start():
    @property
    def start(self) -> Vector:
        """Return the ApexArcGeometry arc start Vector."""
        return self._start

    # ApexArcGeometry.start_angle():
    @property
    def start_angle(self) -> float:  # pragma: no unit test
        """Return the ApexArcGeometry arc start angle."""
        return self._start_angle  # pragma: no unit test

    # ApexArcGeometry.start_key():
    @property
    def start_key(self) -> int:
        """Return the ApexArcGeometry finish Constraint key."""
        # return 1
        return 1 if self._sweep_angle < 0.0 else 2

    # ApexArcGeometry.start_length():
    @property
    def start_length(self) -> float:  # pragma: no unit test
        """Return the ApexArcGeometry distance from start Vector to apex Vector."""
        return self._start_length  # pragma: no unit test

    # ApexArcGeometry.sweep_angle():
    @property
    def sweep_angle(self) -> float:  # pragma: no unit cover
        """Return the ApexArcGeometry sweep angle from start angle to end angle."""
        return self._sweep_angle

    # ApexArcGeometry.type_name():
    @property
    def type_name(self) -> str:  # pragma: no unit cover
        """Return the ApexArcGeometry type name."""
        return "ApexArcGeometry"

    # ApexArcGeometry.__repr__():
    # def __repr__(self) -> str:
    #     """Return string representation of ApexGeometry."""
    #     return self.__str__()

    # ApexArcGeometry.__str__():
    def __str__(self) -> str:
        """Return string representation of ApexGeometry."""
        return f"ApexArcGeometry({self._begin}, {self._at}, {self._finish})"


# ApexCircleGeometry:
class ApexCircleGeometry(ApexGeometry):
    """Represents a circle in a sketch."""

    # ApexCircleGeometry.__init__():
    def __init__(self, drawing: "ApexDrawing",
                 center: Vector, radius: float, name: str = "") -> None:
        """Initialize a ApexCircleGeometry."""
        super().__init__(drawing, center, center, name)
        self._center: Vector = center
        self._drawing: ApexDrawing = drawing
        self._part_circle: Part.Circle = Part.Circle(center, App.Vector(0, 0, 1), radius)
        self._radius: float = radius

    # ApexCircleGeometry.center():
    @property
    def center(self) -> Vector:  # pragma: no unit cover
        """Return the ApexCircleGeometry center."""
        return self._center

    # ApexCircleGeometry.part_element():
    @property
    def part_geometry(self) -> PartGeometry:
        """Return the ApexCircleGeometry PartGeometry."""
        return self._part_circle

    # ApexCircleGeometry.radius():
    @property
    def radius(self) -> float:  # pragma: no unit cover
        """Return the ApexCircleGeometry radius."""
        return self._radius

    # ApexCircleGeometry.type_name():
    @property
    def type_name(self) -> str:  # pragma: no unit cover
        """Return the ApexCircleGeometry type name."""
        return "ApexCircleGeometry"

    # ApexCircleGeometry.__repr__():
    def __repr__(self) -> str:
        """Return string representation of ApexGeometry."""
        return self.__str__()

    # ApexCircleGeometry.__str__():
    def __str__(self) -> str:
        """Return string representation of ApexGeometry."""
        return f"ApexArcGeometry({self._center}, {self._radius})"


# ApexLineGeometry:
class ApexLineGeometry(ApexGeometry):
    """Represents a line segment in a sketch."""

    INIT_CHECKS = (
        ApexCheck("drawing", ("?", object)),
        ApexCheck("start", (Vector,)),
        ApexCheck("finish", (Vector,)),
        ApexCheck("name", (str,)),
    )

    # ApexLineGeometry.__init__():
    def __init__(self, drawing: "ApexDrawing",
                 start: Vector, finish: Vector, name: str = "", tracing: str = "") -> None:
        """Initialize a ApexLineGeometry."""
        arguments: Tuple[Any, ...] = (drawing, start, finish, name)
        value_error: str = ApexCheck.check(arguments, ApexLineGeometry.INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)
        if tracing:
            print(f"{tracing}=>ApexLineGeometry({start}, {finish}, '{name}')")
        super().__init__(drawing, start, finish, name)
        self._drawing: ApexDrawing = drawing
        self._line_segment: Part.LineSegment = Part.LineSegment(start, finish)
        self._start: Vector = start
        self._finish: Vector = finish
        if tracing:
            print(f"{tracing}<=ApexLineGeometry({start}, {finish}, '{name}')")

    # ApexLineGeometry.drawing():
    @property
    def drawing(self) -> "ApexDrawing":  # pragma: no unit cover
        """Return the ApexLineGeometry ApexDrawing."""
        return self._drawing

    # ApexLineGeometry.part_geometry():
    @property
    def part_geometry(self) -> PartGeometry:
        """Return the PartGeometry associated with a ApexLineGeometry."""
        return self._line_segment

    # ApexLineGeometry.finish():
    @property
    def finish(self) -> Vector:  # pragma: no unit cover
        """Return the ApexLineGeometry finish Vector."""
        return self._finish

    # ApexLineGeometry.finish_key():
    @property
    def finish_key(self) -> int:
        """Return the ApexLineGeometry finish Constraint key."""
        return 2  # 2 => End point (never changes for a ApexLineGeometry)

    # ApexLineGeometry.start():
    @property
    def start(self) -> ApexCorner:
        """Return the ApexLineGeometry start Vector."""
        return self._start

    # ApexLineGeometry.start_key():
    @property
    def start_key(self) -> int:
        """Return the ApexLineGeometry start Constraint key."""
        return 1  # 1 => End point (never changes for a ApexLineGeometry)

    # ApexLineGeometry.type_name():
    @property
    def type_name(self) -> str:  # pragma: no unit cover
        """Return the ApexLineGeometry type name."""
        return "ApexLineGeometry"

    # ApexLineGeometry.__repr__():
    def __repr__(self) -> str:
        """Return string representation of ApexLineGeometry."""
        return self.__str__()

    # ApexLineGeometry.__str__():
    def __str__(self) -> str:
        """Return string representation of ApexLineGeometry."""
        start: Vector = self._start
        finish: Vector = self._finish
        return f"ApexLineGeometry({start}, {finish})"


# ApexPointGeometry:
class ApexPointGeometry(ApexGeometry):
    """Represents a point in a sketch."""

    # ApexPointGeometry.__init__():
    def __init__(self, drawing: "ApexDrawing", point: Vector, name: str = "") -> None:
        """Initialize a ApexPointGeometry."""
        super().__init__(drawing, point, point, name)
        self._point: Vector = point
        self._part_point: PartGeometry = Part.Point(point)
        # print(f"ApexPointGeometry.__init__({point.vector=}): ")

    # ApexPointGeometry.__str__():
    def __str__(self) -> str:  # pragma: no unit cover
        """Return ApexPointGeometry string ."""
        return f"ApexPointGeometry(point={self._point}, name='{self._name}', index={self._index})"

    # ApexPointGeometry.part_geometry():
    @property
    def part_geometry(self) -> PartGeometry:
        """Return the  ApexPointGeometry."""
        return self._part_point

    # ApexPointGeometry.point():
    @property
    def point(self) -> Vector:  # pragma: no unit cover
        """Return the ApexPointGeometry Vector."""
        return self._point

    # ApexPointGeometry.type_name():
    @property
    def type_name(self) -> str:  # pragma: no unit cover
        """Return the ApexPointGeometry type name."""
        return "ApexPointGeometry"


# ApexShape:
@dataclass
class ApexShape(object):
    """ApexShape: Is a base class for geometric shapes (e.g. ApexPolygon, etc).

    ApexShape is a base class for the various geometric shapes.  See sub-classes for attributes.
    """

    Box: ApexBox = field(init=False, repr=False)

    # ApexShape.constraints_append():
    def constraints_append(self, drawing: "ApexDrawing", constraints: List[Sketcher.Constraint],
                           tracing: str = "") -> None:
        """Append the ApexShape constraints to drawing.

        Arguments:
        * *drawing* (ApexDrawing): The drawing to use.
        * *constraints* (List[SketcherConstraint]): The constraints list to append to.

        """
        raise NotImplementedError()

    # ApexShape.geometries_get():
    def geometries_get(self, drawing: "ApexDrawing", tracing: str = "") -> Tuple[ApexGeometry, ...]:
        """Return the ApexShape ApexGeometries tuple.

        Arguments:
        * *drawing* (ApexDrawing): The associated drawing to use for geometry extraction.

        Returns:
        * (Tuple[ApexGeometry, ...]) of extracted ApexGeometry's.

        """
        raise NotImplementedError()

    # ApexShape.reorient():
    def reorient(self, placement: Placement, suffix: Optional[str] = "",
                 tracing: str = "") -> "ApexShape":
        """Return a new reoriented ApexCircle.

        Arguments:
        * *placement* (Placement): The FreeCAD Placement to reorient with.
        * *suffix* (str): The suffix to append to the current name string.  None, specifies
          that an empty name is to be used.  (Default: "")

        # Returns:
        * (ApexShape) that has been reoriented with a new name.
        """
        raise NotImplementedError()

    # ApexShape.show():
    def show(self) -> str:
        """Return compact string for ApexShape."""
        raise NotImplementedError()


# _ApexCornerExtra:
@dataclass
class _ApexCornerExtra(object):
    """_ApexCornerExtra: An internal mutable class that corresponds to an ApexCorner."""

    Corner: ApexCorner
    Point: Vector
    Radius: float
    Name: str
    Geometries: Tuple[ApexGeometry, ...] = field(init=False, default=())
    Arc: Optional[ApexArcGeometry] = field(init=False, default=None)
    Construction: Optional[ApexLineGeometry] = field(init=False, default=None)
    Line: Optional[ApexLineGeometry] = field(init=False, default=None)


# ApexPolygon:
@dataclass
class ApexPolygon(ApexShape):
    """ApexPolyon: A closed polygon of Vectors.

    Usage: ApexPolygon(corners, name)

    Attributes:
    * *Corners* (Tuple[ApexCorner, ...]): The ApexCorner's of the ApexPoloygon.
    * *Name* (str): The ApexPolygon name.  (Default: "")
    * *Box* (ApexBox): An ApexBox that encloses all of the corners.
    * *Clockwise* (bool): Computed to True the corners are in clockwise order.
    * *InternalRadius* (float): The computed minimum radius for internal corners in millimeters.

    """

    Corners: Tuple[ApexCorner, ...]
    Name: str = ""
    # Computed attributes:
    InternalRadius: float = field(init=False)
    Clockwise: bool = field(init=False)
    _geometries: Optional[Tuple[ApexGeometry, ...]] = field(init=False, default=None)
    _corners: Tuple[_ApexCornerExtra, ...] = field(init=False)

    POST_INIT_CHECKS = (
        ApexCheck("corners", ("T+", ApexCorner)),
        ApexCheck("name", (str,)),
    )

    # ApexPolygon.__post_init__():
    def __post_init__(self) -> None:
        """Initialize a ApexPolygon."""
        arguments: Tuple[Any, ...] = (self.Corners, self.Name)
        value_error: str = ApexCheck.check(arguments, ApexPolygon.POST_INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)

        corner: ApexCorner
        _corners: Tuple[_ApexCornerExtra, ...] = tuple(
            [_ApexCornerExtra(corner, corner.Point, corner.Radius, corner.Name)
             for corner in self.Corners]
        )

        # Determine the value of Clockwise attribute:
        corners: Tuple[ApexCorner, ...] = self.Corners
        corners_size: int = len(corners)
        index: int
        total_angle: float = 0.0
        for index, corner in enumerate(corners):
            start: Vector = corner.Point
            finish: Vector = corners[(index + 1) % corners_size].Point
            total_angle += math.atan2(finish.y - start.y, finish.x - start.x)

        # *minimum_radius* is used to group pockets with the same internal radius together.
        # TODO(Compute correct internal_radius)
        internal_radius: float = -1.0
        for corner in corners:
            radius: float = corner.Radius
            if radius > 0:
                internal_radius = radius if internal_radius <= 0.0 else min(internal_radius, radius)

        box: ApexBox = ApexBox([corner.Box for corner in corners])

        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        object.__setattr__(self, "Box", box)
        object.__setattr__(self, "Clockwise", total_angle >= 0.0)
        object.__setattr__(self, "InternalRadius", internal_radius)
        object.__setattr__(self, "_corners", _corners)

    # ApexPolygon.__repr__():
    def __repr__(self) -> str:
        """Return string representation of ApexPolygon."""
        return self.__str__()

    # ApexPolygon.__str__():
    def __str__(self, short: bool = False) -> str:
        """Return string representation of ApexPolygon.

        Arguments:
        * *short* (bool): If true, a shorter versions returned.

        """
        return f"ApexPolygon({self.Corners}', '{self.Name}')"

    # ApexPolygon.show():
    def show(self) -> str:
        """Return compact string showing ApexPolygon contents."""
        corner: ApexCorner
        corners_text: str = ", ".join([f"({corner.Point.x},{corner.Point.y},{corner.Point.z})"
                                       for corner in self.Corners])
        return f"ApexPolygon(({corners_text}), '{self.Name}')"

    # ApexPolygon.constraints_append():
    def constraints_append(self, drawing: "ApexDrawing", constraints: List[Sketcher.Constraint],
                           tracing: str = "") -> None:
        """Return the ApexPolygon constraints for a ApexDrawing."""
        # Perform an requested *tracing*:
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>ApexPolygon.contraints_append('{self.Name}', "
                  f"*, {len(constraints)=}):")

        origin_index: int = drawing.OriginIndex
        geometries: Optional[Tuple[ApexGeometry, ...]] = (
            self.geometries_get(drawing, tracing=next_tracing))
        assert geometries, "ApexGeometries not set"
        geometries_size: int = len(geometries)
        if tracing:
            print(f"{tracing}|geometries| == {geometries_size}")
        # degrees45: float = math.pi / 4.0
        # degrees135: float = 3.0 * degrees45
        # deg: Callable[[float], float] = math.degrees

        at_index: int
        # Iterate through adjacent ApexGeometry pairs and apply constraints;
        for at_index, at_geometry in enumerate(geometries):
            # Grab a bunch of field from *at_geometry* and *before_geometry*
            at_geometry_index: int = at_geometry.index
            at_name: str = at_geometry.name
            at_start: Vector = at_geometry.start
            at_start_key: int = at_geometry.start_key
            before_geometry: ApexGeometry = geometries[(at_index - 1) % geometries_size]
            before_geometry_index: int = before_geometry.index
            before_name: str = before_geometry.name
            # before_finish: Vector = before_geometry.finish
            before_finish_key: int = before_geometry.finish_key
            after_geometry: ApexGeometry = geometries[(at_index + 1) % geometries_size]
            assert at_geometry is not before_geometry
            if tracing:
                print("")
                print(f"{tracing}[{at_index}]: "
                      f"at={at_geometry.type_name}('{at_name}'):{at_geometry_index} "
                      f"before={before_geometry.type_name}('{before_name}'):"
                      f"{before_geometry_index}")

            # Extract *at_arc* and/or *before_arc* if they are present:
            before_arc: Optional[ApexArcGeometry] = None
            if isinstance(before_geometry, ApexArcGeometry):
                before_arc = before_geometry
            at_arc: Optional[ApexArcGeometry] = None
            if isinstance(at_geometry, ApexArcGeometry):
                at_arc = at_geometry
            after_arc: Optional[ApexArcGeometry] = None
            if isinstance(after_geometry, ApexArcGeometry):
                after_arc = after_geometry

            # *at_arc* almost always needs to specify a radius.  In almost all cases,
            # the X/Y coordinates of the arc center need to be specified as well.
            # There is one exception, which occurs when an arc is sandwiched between
            # two other arcs with no intervening line segments.  In this case the X/Y
            # coordinates are not needed since they will over constrain the drawing.
            if at_arc:
                at_radius: float = at_arc.radius
                at_center: Vector = at_arc.center

                # Set Radius constraint:
                constraints.append(Sketcher.Constraint(
                    "Radius",
                    at_geometry_index, at_radius))
                if tracing:
                    print(f"{tracing}     [{len(constraints)}]: "
                          f"Radius('{before_name}':({at_geometry_index}, 0), "
                          f"{at_radius}),  # Arc Radius")

                # Suppress Arc center constraints when an arc is sandwiched between two
                # other Arcs.
                if not (before_arc and at_arc and after_arc):
                    # Set DistanceX constraint:
                    constraints.append(Sketcher.Constraint(
                        "DistanceX",
                        origin_index, 1,  # 1 => start point
                        at_geometry_index, 3,  # 3 => arc center
                        at_center.x))
                    if tracing:
                        print(f"{tracing}     [{len(constraints)}]: "
                              f"DistanceX(Origin:({origin_index}, 1), "
                              f"'{at_name}':({at_geometry_index},3), "
                              f"{at_center.x:.2f}) # Arc Center X")

                    # Set DistanceY constraint:
                    constraints.append(Sketcher.Constraint(
                        "DistanceY",
                        origin_index, 1,  # 1 => start point
                        at_geometry_index, 3,  # 3 => arc center
                        at_center.y))
                    if tracing:
                        print(f"{tracing}     [{len(constraints)}]: "
                              f"DistanceY('Origin':({origin_index}, 1), "
                              f"'{at_name}:{at_geometry_index}, 3)', "
                              f"{at_center.y:.2f}) # Arc Center Y")

            # No matter what, glue the two endpoints together.  If either side is an arc,
            # just make them tangent.  Otherwise, make the points coincident, and specify
            # an X and Y.
            if before_arc or at_arc:
                # Make coincident:
                # Just force the two geometries to be tangent:
                constraints.append(Sketcher.Constraint(
                    "Tangent",
                    before_geometry_index, before_finish_key,
                    at_geometry_index, at_start_key))
                if tracing:
                    print(f"{tracing}     [{len(constraints)}]: "
                          f"Tangent('{before_name}':({before_geometry_index}, "
                          f"{before_finish_key}), "
                          f"'{at_name}':({at_geometry_index}, {at_start_key})")
            else:
                # Specify Coincident constraint first:
                constraints.append(
                    Sketcher.Constraint(
                        "Coincident",
                        before_geometry_index, before_finish_key,
                        at_geometry_index, at_start_key))
                if tracing:
                    print(f"{tracing}     [{len(constraints)}]: "
                          f"Coincident('{before_name}':({before_geometry_index}, "
                          f"{before_finish_key}), "
                          f"'{at_name}':({at_geometry_index}, {at_start_key}) # End points")

                # Specify the DistanceX constraint next:
                constraints.append(Sketcher.Constraint(
                    "DistanceX",
                    origin_index, 1,  # 1 => start point
                    at_geometry_index, at_start_key,
                    at_start.x))
                if tracing:
                    print(f"{tracing}     [{len(constraints)}]: "
                          f"DistanceX(Origin:({origin_index}, 1), "
                          f"'{at_name}:({at_geometry_index}, {at_start_key})', {at_start.x:.2f})")

                # Specify DistanceY constraint last:
                constraints.append(Sketcher.Constraint(
                    "DistanceY",
                    origin_index, 1,  # 1 => start point
                    at_geometry_index, at_start_key,
                    at_start.y))
                if tracing:
                    print(f"{tracing}     [{len(constraints)}]: "
                          f"DistanceY(Origin:({origin_index}, 1), "
                          f"'{at_name}({at_geometry_index}, {at_start_key})', {at_start.y:.2f})")

        if tracing:
            print(f"{tracing}<=ApexPolygon.contraints_append('{self.Name}', "
                  f"*, , {len(constraints)=})")

    # ApexPolygon.geometries_get():
    def geometries_get(self, drawing: "ApexDrawing", tracing: str = "") -> Tuple[ApexGeometry, ...]:
        """Return the ApexPolygon ApexGeometries tuple."""
        # Overview:
        #
        # This code has the task of providing a sequence of ApexGeometry's that represent
        # the polygon with whatever corner rounding is requested for each corner.
        # A further complication is to structure the result ApexGeometry's so that they are
        # neither under constrained nor over constrained.  This condition is called
        # "fully constrained" and is a requirement for subsequent usage of the resulting sketches.
        #
        # Properly constraining arc's in FreeCAD is challenging.  After much research, it was
        # determined that excellent way to provide a fully constrained arc is with the addition
        # of a construction line.  A construction line is shown in blue in the sketch and is only
        # used by the sketch constraint solver.  Each arc that is needed for a rounded corner
        # generates a construction line from the arc center to the start point of the arc.
        #
        # To quickly summarize:
        # * Each ApexCorner with a non-zero radius, produces a construction line segment and an arc.
        # * Each ApexCorner with a zero radius only produces a single line segment.
        # * There is one special case where two corners smoothly transition from one arc to
        #   the next without any bridging line segment.
        #
        # Terminology:
        # * before: The point/arc/line before the current index.
        # * at: The point/arc/line at the current index.
        # * after: The point/arc/line after the current index.
        #
        # This is a 4 pass algorithm:

        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>ApexPolygon.geometries_get(*)")

        # Only compute the geometries once:
        if not self._geometries:
            # Some variable declarations (re)used in the code below:
            after_corner: _ApexCornerExtra
            arc: Optional[ApexArcGeometry]
            at_arc: Optional[ApexArcGeometry]
            at_index: int
            at_line: Optional[ApexLineGeometry]
            at_name: str
            at_corner: _ApexCornerExtra
            before_corner: _ApexCornerExtra

            # Pass 1: Create a list of *arcs* for each corner with a non-zero radius.
            # This list is 1-to-1 with the *points*.

            corners: Tuple[_ApexCornerExtra, ...] = self._corners
            corners_size: int = len(corners)
            arcs: List[Optional[ApexArcGeometry]] = []
            for at_index, at_corner in enumerate(corners):
                before_corner = corners[(at_index - 1) % corners_size]
                after_corner = corners[(at_index + 1) % corners_size]
                at_name = at_corner.Name
                arc_geometry: Optional[ApexArcGeometry] = None
                if at_corner.Radius > 0.0:
                    arc_geometry = ApexArcGeometry(drawing, before_corner.Corner, at_corner.Corner,
                                                   after_corner.Corner, at_name, next_tracing)
                    at_corner.Arc = arc_geometry
                arcs.append(arc_geometry)

            # Pass 2: Create any *lines* associated with a each corner.
            # This list is 1-to-1 with the points.  Occasionally, a line is omitted when 2 arcs
            # connect with no intermediate line segment.
            epsilon: float = 1e-9  # 1 nano meter (used to detect when two points are close.)
            lines: List[Optional[ApexLineGeometry]] = []
            for at_index, at_corner in enumerate(corners):
                before_index: int = (at_index - 1) % corners_size
                before_corner = corners[before_index]
                before_arc: Optional[ApexArcGeometry] = arcs[before_index]
                at_arc = arcs[at_index]
                at_name = at_corner.Name
                # *start* and *finish* are the start and end points of the *line*:
                start: Vector = before_arc.finish if before_arc else before_corner.Point
                assert isinstance(start, Vector)
                finish: Vector = at_arc.start if at_arc else at_corner.Point
                assert isinstance(finish, Vector)

                # There is possibility that the *before_arc* and *at_arc* could touch one another
                # without an intervening line segment.  Also, it is possible that the arc completely
                # occludes its preceding line segment.  In both cases, the preceding line segment
                # is suppressed.
                generate_at_line: bool = True
                if before_arc and at_arc:
                    line_length: float = (before_corner.Point - at_corner.Point).Length
                    # *arc_lengths* is the total amount of line
                    before_length: float = (before_arc.finish - before_arc.at).Length
                    at_length: float = (at_arc.start - at_arc.at).Length
                    arc_lengths: float = before_length + at_length
                    if abs(arc_lengths - line_length) < epsilon:
                        # We have "exact" match, so the line segment is suppressed.
                        generate_at_line = False
                    elif arc_lengths > line_length:  # pragma: no unit cover
                        raise ValueError("Arcs are too big")
                line_geometry: Optional[ApexLineGeometry] = None
                if generate_at_line:
                    line_geometry = ApexLineGeometry(drawing, start,
                                                     finish, at_name, tracing=next_tracing)
                    at_corner.Line = line_geometry
                lines.append(line_geometry)

            # Pass 3: Assemble the *final_geometries* list:
            geometries: List[ApexGeometry] = []
            # for at_index in range(corners_size):
            for at_index, at_corner in enumerate(corners):
                at_line = at_corner.Line
                if at_line:
                    geometries.append(at_line)
                at_arc = at_corner.Arc
                if at_arc:
                    geometries.append(at_arc)
            final_geometries: Tuple[ApexGeometry, ...] = tuple(geometries)

            # Pass 4: Make bi-directional doubly linked geometries that is used for constraints
            # generation.
            at_geometry: ApexGeometry
            geometries_size: int = len(geometries)
            for at_index, geometry in enumerate(final_geometries):
                geometry.previous = geometries[(at_index - 1) % geometries_size]
                geometry.next = geometries[(at_index + 1) % geometries_size]

            self._geometries = final_geometries
        if tracing:
            print(f"{tracing}<=ApexPolygon.geometries_get(*)=>|*|={len(self._geometries)}")
        return self._geometries

    REORIENT_CHECKS = (
        ApexCheck("placement", (Placement,)),
        ApexCheck("suffix", (str, )),
    )

    # ApexPolygon.reorient():
    def reorient(self, placement: Placement, suffix: Optional[str] = "",
                 tracing: str = "") -> "ApexPolygon":
        """Reorient an ApexPolygon with a new Placement.

        Arguments:
        * *placement* (Placement):
          The FreeCAD Placement to reorient with.
        * *suffix* (Optional[str]):
          A suffix to append to the name.  If None, an empty name is used. (Default: "")

        """
        arguments: Tuple[Any, ...] = (placement, suffix)
        value_error: str = ApexCheck.check(arguments, ApexPolygon.REORIENT_CHECKS)
        if value_error:
            raise ValueError(value_error)
        if tracing:
            print(f"{tracing}=>ApexPolygon.reorient{arguments}")

        name: str = f"{self.Name}{suffix}" if suffix else ""
        corner: ApexCorner
        reoriented_corners: Tuple[ApexCorner, ...] = tuple([
            ApexCorner(placement * corner.Point, corner.Radius, name)
            for corner in self.Corners
        ])
        result: ApexPolygon = ApexPolygon(reoriented_corners, name)
        if tracing:
            print(f"{tracing}<=ApexPolygon.reorient{arguments}=>*")
        return result

    # ApexPolygon._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Run ApexPolygon unit tests."""
        # Create *polygon*:
        n: float = 10.0
        s: float = -10.0
        e: float = 20.0
        w: float = -20.0
        radius: float = 1.0
        ne_corner: ApexCorner = ApexCorner(Vector(n, e, 0), radius)
        nw_corner: ApexCorner = ApexCorner(Vector(n, w, 0), radius)
        se_corner: ApexCorner = ApexCorner(Vector(s, e, 0), radius)
        sw_corner: ApexCorner = ApexCorner(Vector(s, w, 0), radius)
        corners: Tuple[ApexCorner, ...] = (ne_corner, nw_corner, sw_corner, se_corner)
        name: str = "name"
        polygon: ApexPolygon = ApexPolygon(corners, name)

        # Verify attribute access:
        _ = polygon


# ApexCircle:
@dataclass
class ApexCircle(ApexShape):
    """ApexCircle: Represents a circle.

    Usage: ApexCircle(center, diameter, name)

    Attributes:
    * *Center* (Vector): The center of the circle.
    * *Diameter* (float): Circle diameter in millimeters
    * *Name* (str):  Name of circle.  (Default: "")
    * *Box* (ApexBox): ApexBox that encloses ApexCircle as if it is a sphere.
    * *Constraints* (Tuple[Sketcher.Constraint, ...):  Computed constraints.

    """

    Box: ApexBox = field(init=False)  # Computed attribute
    Constraints: Tuple[Sketcher.Constraint, ...] = field(init=False)  # Computed attribute
    Center: Vector
    Diameter: float
    Name: str = ""
    _circle_geometry: Optional[ApexCircleGeometry] = None
    _circle_geometries: Tuple[ApexCircleGeometry, ...] = ()

    POST_INIT_CHECKS = (
        ApexCheck("center", (Vector,)),
        ApexCheck("diameter", (float,)),
        ApexCheck("name", (str,)),
    )

    # ApexCircle.__post_init():
    def __post_init__(self) -> None:
        """Initialize a circle."""
        arguments: Tuple[Any, ...] = (self.Center, self.Diameter, self.Name)
        value_error: str = ApexCheck.check(arguments, ApexCircle.POST_INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)
        if self.Diameter <= 0:
            raise ValueError(f"ApexCircle diameter (={self.Diameter}) must be positive")

        radius: float = self.Diameter / 2.0
        offset: Vector = Vector(radius, radius, radius)
        self.Box = ApexBox([self.Center + offset, self.Center - offset])
        self.Constraints = ()  # Updated later.

    def __repr__(self) -> str:
        """Return a string representation of ApexCircle."""
        return self.__str__()

    def __str__(self) -> str:
        """Return a string representation of ApexCircle."""
        return f"ApexCircle({self.Center}, {self.Diameter}, '{self.Name}')"

    # ApexCircle.constraints_append():
    def constraints_append(self, drawing: "ApexDrawing", constraints: List[Sketcher.Constraint],
                           tracing: str = "") -> None:
        """Return the ApexCircleGeometry constraints."""
        if tracing:
            print(f"{tracing}=>ApexCircle.constraints_append(*, *): {len(constraints)=}")
        origin_index: int = drawing.OriginIndex
        center: Vector = self.Center
        diameter: float = self.Diameter
        circle_name: str = self.Name
        circle_geometry: Optional[ApexCircleGeometry] = self._circle_geometry
        assert isinstance(circle_geometry, ApexCircleGeometry), "circle geometry is not present."
        circle_geometry_index: int = circle_geometry.index

        # Append the Radius constraint:
        constraints.append(Sketcher.Constraint("Radius", circle_geometry_index, diameter / 2.0))
        if tracing:
            print(f"{tracing}     [{len(constraints)}]: "
                  f"Radius('{circle_name}:({circle_geometry_index}, 0)'),  # Arc Radius")

        # Append the DistanceX constraint:
        constraints.append(Sketcher.Constraint("DistanceX",
                                               origin_index, 1,  # 1 => Start point
                                               circle_geometry_index, 3,  # 3 => ApexCircle Center
                                               center.x))
        if tracing:
            print(f"{tracing}     [{len(constraints)}]: "
                  f"DistanceX(Origin:({origin_index}, 1), "
                  f"'{circle_name}':({circle_geometry_index}, 3), "
                  f"{center.x:.2f})) # ApexCircle Center X")

        # Append the DistanceY constraint:
        constraints.append(
            Sketcher.Constraint("DistanceY",
                                origin_index, 1,  # 1 => Start Vector
                                circle_geometry_index, 3,  # 3 => ApexCircle Center
                                center.y))
        if tracing:
            print(f"{tracing}     [{len(constraints)}]: "
                  f"DistanceX(Origin:({origin_index}, 1), "
                  f"'{circle_name}':({circle_geometry_index}, 3), "
                  f"{center.y:.2f})) # ApexCircle Center Y")
            print(f"{tracing}<=ApexCircle.constraints_append(*, *): {len(constraints)=}")

    # ApexCircle.geometries_get():
    def geometries_get(self, drawing: "ApexDrawing", tracing: str = "") -> Tuple[ApexGeometry, ...]:
        """Return the ApexCircleGeometry."""
        if tracing:
            print(f"{tracing}=>ApexCircle.geometries_get()")
        circle_geometry: Optional[ApexCircleGeometry] = self._circle_geometry
        if not circle_geometry:
            circle_geometry = ApexCircleGeometry(
                drawing, self.Center, self.Diameter / 2.0, self.Name)
            self._circle_geometry = circle_geometry
            self._circle_geometries = (circle_geometry,)
        assert isinstance(circle_geometry, ApexCircleGeometry)
        if tracing:
            print(f"{tracing}<=ApexCircle.geometries_get()=>{self._circle_geometries}")
        return self._circle_geometries

    # ApexCircle.reorient():
    def reorient(self, placement: Placement, suffix: Optional[str] = "",
                 tracing: str = "") -> "ApexCircle":
        """Return a new reoriented ApexCircle.

        Arguments:
        * *placement* (Placement): The FreeCAD Placement reorient with.
        * *suffix* (str): The suffix to append to the current name string.  None, specifies
          that an empty name is to be used.  (Default: "")

        """
        if tracing:
            print(f"{tracing}=>ApexCircle.reorient(*, {placement}, '{suffix}')")
        name: str = f"{self.Name}{suffix}" if suffix else ""
        reoriented: ApexCircle = ApexCircle(placement * self.Center, self.Diameter, name)
        if tracing:
            print(f"{tracing}{self} => {reoriented}")
            print(f"{tracing}<=ApexCircle.reorient(*, {placement}, '{suffix}') => *")
        return reoriented


# ApexOperation:
@dataclass(frozen=True)
class ApexOperation(object):
    """Represents a FreeCAD Part Design workbench operation.

    This is a base class for ApexHole, ApexPad, and ApexPocket.

    Attributes:
    * *SortKey*: (Tuple[str, ...]): A key generated by sub-class used to sort ApexOpertions.

    """

    SortKey: Tuple[str, ...] = field(init=False, repr=False)
    Box: ApexBox = field(init=False, repr=False)

    # All __post_init__() processing is done by the sub-classes.

    @property
    def Name(self) -> str:
        """Return ApexOperation name."""
        raise NotImplementedError(f"ApexOperation.Name is not implemented for {self}")

    # ApexOperation.reorient():
    def reorient(self, placement: Placement, suffix: str = None,
                 tracing: str = "") -> "ApexOperation":
        """Reorient an operation.

        Arguments:
        * *placement* (Placement): The FreeCAD Placement reorient with.
        * *suffix* (str): The suffix to append to the current name string.  None, specifies
          that an empty name is to be used.  (Default: "")

        """
        raise NotImplementedError(f"ApexOperation.reorient() not implemented for {self}")

    # ApexOperation.show():
    def show(self) -> str:
        """Return a string that shows operation."""
        raise NotImplementedError(f"ApexOperation.show() not implemented for {self}")

    # ApexOperation.body_apply():
    def body_apply(self, body: "PartDesign.Body", group_name: str, sketch: "Sketcher.SketchObject",
                   gui_document: Optional["Gui.ActiveDocument"], tracing: str = "") -> None:
        """Apply operation to a Part Design body."""
        raise NotImplementedError("Needs be implemented in sub-class")

    # ApexOperation.constraints_append():
    def constraints_append(self, drawing: "ApexDrawing", constraints: List[Sketcher.Constraint],
                           tracing: str = "") -> None:
        """Append the ApexOperation constraints to drawing.

        Arguments:
        * *drawing* (ApexDrawing): The drawing to use.
        * *constraints* (List[SketcherConstraint]): The constraints list to append to.

        """
        raise NotImplementedError(f"ApexOperation.constraints_append(): {self}")

    # ApexOperation.geometries_get():
    def geometries_get(self, drawing: "ApexDrawing", tracing: str = "") -> Tuple[ApexGeometry, ...]:
        """Return the geometries associated with an operation."""
        raise NotImplementedError(f"ApexOperation.geometries_get() not implemented {self}")

    # ApexOperation.shape_get():
    def shape_get(self) -> ApexShape:
        """Return the associated ApexOperation ApexShape."""
        raise NotImplementedError(f"ApexOperation.shape_get() not impelemented for {type(self)}")


# ApexHole:
@dataclass(frozen=True)
class ApexHole(ApexOperation):
    """ApexHole represents a FreeCAD Part Design workbench Hole operation.

    Usage: ApexHole(circle, depth, name)

    Attributes:
    * *Circle: (ApexCircle): The ApexCircle for the hole.
    * *Depth* (float): The hole depth in millimeters.
    * *Name* (str): The name of the operation.  (Default: "")
    * *SortKey* (Tuple[str, ...]): A generated sorting key used to sort ApexOperation's.

    """

    Circle: ApexCircle
    Depth: float
    Name: str = ""

    POST_INIT_CHECKS = (
        ApexCheck("circle", (ApexCircle,)),
        ApexCheck("depth", (float,)),
        ApexCheck("name", (str,)),
    )

    # ApexHole.__post_init__():
    def __post_init__(self) -> None:
        """Verify argument types."""
        arguments: Tuple[Any, ...] = (self.Name, self.Circle, self.Depth)
        value_error: str = ApexCheck.check(arguments, ApexPad.POST_INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)

        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        object.__setattr__(self, "Box", self.Circle.Box)
        object.__setattr__(self, "SortKey", ("2Hole", f"{self.Circle.Diameter}", f"{self.Depth}"))

    # ApexHole.body_apply():
    def body_apply(self, body: "PartDesign.Body",
                   group_name: str, sketch: "Sketcher.SketchObject",
                   gui_document: Optional["Gui.ActiveDocument"], tracing: str = "") -> None:
        """Apply hole operation to PartDesign body."""
        if tracing:
            print(f"{tracing}=>ApexHole.body_apply('{self.Name}', '{group_name}', *, *)")
        # We have bunch of ApexCircles with the same *diameter* and *depth*:
        hole: PartDesign.Geometry = body.newObject("PartDesign::Hole", f"{group_name}.Hole")
        hole.Profile = sketch
        hole.DrillPointAngle = 118.00
        # hole.setExpression("Depth, "10mm")
        hole.ThreadType = 0
        hole.HoleCutType = 0
        hole.DrillPoint = 0  # FIXME
        hole.Tapered = 0
        hole.Diameter = float(self.Circle.Diameter)
        hole.Depth = float(self.Depth)
        # hole.DrillPoint = u"Flat" if group0.flat else u"Angled"
        if tracing:
            print(f"{tracing}<=ApexHole.body_apply('{self.Name}', '{group_name}', *, *)")

    # ApexHole.reorient():
    def reorient(self, placement: Placement, suffix: str = None,
                 tracing: str = "") -> "ApexHole":
        """Reorient an ApexHole.

        Arguments:
        * *placement* (Placement): The FreeCAD Placement to reorient with.
        * *suffix* (str): The suffix to append to the current name string.  None, specifies
          that an empty name is to be used.  (Default: "")

        """
        name: str = f"{self.Name}{suffix}" if suffix else ""
        circle: ApexCircle = self.Circle
        reoriented_circle: ApexCircle = circle.reorient(placement)
        reoriented_hole: ApexHole = ApexHole(reoriented_circle, self.Depth, name)
        return reoriented_hole

    # ApexHole.shape_get():
    def shape_get(self) -> ApexShape:
        """Return the ApexHole ApexShape."""
        return self.Circle


# ApexPad:
@dataclass(frozen=True)
class ApexPad(ApexOperation):
    """ApexPad represents a FreeCAD Part Design workbench Pad operation.

    Attributes:
    * *Shape* (ApexShape): The ApexCircle/ApexPolygon to use for padding.
    * *Depth* (float): The depth of the pad operation.
    * *Name* (str): The name of the operation.  (Default: "")
    * *SortKey* (Tuple[str, ...]): A generated sorting key used to sort ApexOperation's.

    Usage: ApexPad(circle_or_pologon, depth, name)

    """

    Shape: ApexShape
    Depth: float
    Name: str = ""

    POST_INIT_CHECKS = (
        ApexCheck("name", (str,)),
        ApexCheck("shape", (ApexShape,)),
        ApexCheck("depth", (float,)),
    )

    # ApexPad.__post_init__():
    def __post_init__(self) -> None:
        """Verify argument types."""
        arguments: Tuple[Any, ...] = (self.Name, self.Shape, self.Depth)
        value_error: str = ApexCheck.check(arguments, ApexPad.POST_INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)

        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        object.__setattr__(self, "Box", self.Shape.Box)
        object.__setattr__(self, "SortKey", ("0Pad", f"{self.Depth}"))

    # ApexPad.body_apply():
    def body_apply(self, body: "PartDesign.Body", group_name: str, sketch: "Sketcher.SketchObject",
                   gui_document: Optional["Gui.ActiveDocument"], tracing: str = "") -> None:
        """Apply ApexPad opertation to PartDesign Body."""
        if tracing:
            print(f"{tracing}=>ApexPad.body_apply('{self.Name}', '{group_name}', *, *)")
        # Pad:
        pad: PartDesign.ApexGeometry = body.newObject("PartDesign::Pad", f"{group_name}.Pad")
        pad.Profile = sketch
        pad.Length = float(self.Depth)
        pad.Reversed = True
        # Unclear what most of these geometries do:
        pad.Length2 = 0
        pad.UseCustomVector = 0
        pad.Direction = (1, 1, 1)
        pad.Type = 0
        pad.UpToFace = None
        pad.Midplane = 0
        pad.Offset = 0

        if gui_document:  # pragma: no unit cover
            visibility_set(pad, True)
            view_object: Any = body.getLinkedObject(True).ViewObject
            pad.ViewObject.LineColor = getattr(
                view_object, "LineColor", pad.ViewObject.LineColor)
            pad.ViewObject.ShapeColor = getattr(
                view_object, "ShapeColor", pad.ViewObject.ShapeColor)
            pad.ViewObject.PointColor = getattr(
                view_object, "PointColor", pad.ViewObject.PointColor)
            pad.ViewObject.Transparency = getattr(
                view_object, "Transparency", pad.ViewObject.Transparency)
            # The following code appears to disable edge highlighting:
            # pad.ViewObject.DisplayMode = getattr(
            #    view_object, "DisplayMode", pad.ViewObject.DisplayMode)
        if tracing:
            print(f"{tracing}<=ApexPad.body_apply('{self.Name}', '{group_name}', *, *)")

    # ApexPad.reorient():
    def reorient(self, placement: Placement, suffix: str = None,
                 tracing: str = "") -> "ApexPad":
        """Reorient an ApexPad .

        Arguments:
        * *placement* (Placement): The FreeCAD Placement reorient with.
        * *suffix* (str): The suffix to append to the current name string.  None, specifies
          that an empty name is to be used.  (Default: "")

        """
        name: str = "" if suffix is None else f"{self.Name}{suffix}"
        reoriented_shape: ApexShape = self.Shape.reorient(placement, suffix, name)
        return ApexPad(reoriented_shape, self.Depth, name)

    # ApexPad.shape_get():
    def shape_get(self) -> ApexShape:
        """Return the associated ApexShape's."""
        return self.Shape


# ApexPocket:
@dataclass(frozen=True)
class ApexPocket(ApexOperation):
    """ApexPocket represents a FreeCAD Part Design workbench Pad operation.

    Usage: ApexPad(circle_or_polygon, depth, name)

    Attributes:
    * *Shape* (ApexShape): The ApexCircle/ApexPolygon to use for the pocket operation.
    * *Depth* (float): The depth of the pocke operation.
    * *Name* (str): The name of the operation.  (Default: "")
    * *SortKey* (Tuple[str, ...]): A generated sorting key used to sort ApexOperations.

    """

    Shape: ApexShape
    Depth: float
    Name: str = ""

    POST_INIT_CHECKS = (
        ApexCheck("shape", (ApexShape,)),
        ApexCheck("depth", (float,)),
        ApexCheck("name", (str,)),
    )

    # ApexPocket.__post_init__():
    def __post_init__(self) -> None:
        """Verify argument types."""
        arguments: Tuple[Any, ...] = (self.Shape, self.Depth, self.Name)
        value_error: str = ApexCheck.check(arguments, ApexPocket.POST_INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)
        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        object.__setattr__(self, "Box", self.Shape.Box)
        object.__setattr__(self, "SortKey", ("1Pocket", f"{self.Depth}"))

    # ApexPocket.body_apply():
    def body_apply(self, body: "PartDesign.Body", group_name: str, sketch: "Sketcher.SketchObject",
                   gui_document: Optional["Gui.ActiveDocument"], tracing: str = "") -> None:
        """Apply pocket operation to PartDesign Body."""
        if tracing:
            print(f"{tracing}=>ApexPocket.body_apply('{self.Name}', '{group_name}', *, *)")
        pocket: "PartDesign.Geometry" = body.newObject(
            "PartDesign::Pocket", f"{group_name}.Pocket")
        pocket.Profile = sketch
        pocket.Length = float(self.Depth)
        if tracing:
            print(f"{tracing}<=ApexPocket.body_apply('{self.Name}', '{group_name}', *, *)")

    # ApexPocket.reorient():
    def reorient(self, placement: Placement, suffix: str = None,
                 tracing: str = "") -> "ApexPocket":
        """Reorient an ApexPocket .

        Arguments:
        * *placement* (Placement): The FreeCAD Placement reorient with.
        * *suffix* (str): The suffix to append to the current name string.  None, specifies
          that an empty name is to be used.  (Default: "")

        """
        name: str = "" if suffix is None else f"{self.Name}{suffix}"
        reoriented_shape: ApexShape = self.Shape.reorient(placement, suffix, name)
        return ApexPocket(reoriented_shape, self.Depth, name)

    # ApexPocket.shape_get():
    def shape_get(self) -> ApexShape:
        """Return the ApexPad ApexShape."""
        return self.Shape


# ApexDrawing:
@dataclass
class ApexDrawing(object):
    """ApexDrawing: Used to create fully constrained 2D drawings.

    Usage: ApexDrawing(contact, normal, operations, name)

    Attributes:
    * *Contact*: (Vector): On point on the surface of the polygon.
    * *Normal*: (Vector): A normal to the polygon plane.
    * *Operations* (Tuple[ApexOperation, ...]): Operations to perform on drawing.
    * *Name* (str): The ApexDrawing name. (Default: "")
    * *Box* (ApexBox): A computed ApexBox that encloses all of the operations.

    """

    Contact: Vector
    Normal: Vector
    Operations: Tuple[ApexOperation, ...]
    Name: str = ""
    # Computed attributes:
    Box: ApexBox = field(init=False)
    OriginIndex: int = field(init=False, default=-999)  # Value less than -1 for constraints
    DatumPlaneCounter: int = field(init=False, default=0)

    POST_INIT_CHECKS = (
        ApexCheck("contact", (Vector,)),
        ApexCheck("normal", (Vector,)),
        ApexCheck("operations", ("T", ApexOperation)),
        ApexCheck("name", (str,)),
    )

    # ApexDrawing.__post_init__():
    def __post_init__(self) -> None:
        """Initialize a drawing."""
        arguments: Tuple[Any, ...] = (self.Contact, self.Normal, self.Operations, self.Name)
        value_error: str = ApexCheck.check(arguments, ApexDrawing.POST_INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)
        # trace_arguments: str
        # contact: Vector = self.Contact
        # normal: Vector = self.Normal
        # tracing: str = ""
        # if tracing:
        #     trace_arguments = (
        #         f"ApexDrawing.__init__(({contact.X}, {contact.Y}, {contact.Z}), "
        #         f"({normal.X}, {normal.Y}, {normal.Z}), *, '{self.Name}')"
        #     )
        #     print(f"{tracing}=>{trace_arguments}")
        # next_tracing: str = tracing + " " if tracing else ""

        # Create the *placement* used to rotate all points around *contact* such that
        # *perpendicular* is aligned with the +Z axis:
        # contact = self.Contact
        # normal = self.Normal
        # normal = normal.normalize()
        # rotation: Rotation = Rotation(normal, Vector(0, 0, 1))
        # placement: Placement = Placement(Vector(0, 0, 0), rotation, contact)

        # Load everything into *self* (i.e. ApexDrawing):
        # self._body: Optional[PartDesign.Body] = None
        # self._datum_plane: Optional[Part.ApexGeometry] = None
        # self._geometries: List[Any] = []

        # Now compute the final *box*:
        operation: ApexOperation
        box: ApexBox = ApexBox([operation.Box for operation in self.Operations])

        # Load everything into *self*:
        self.Box: ApexBox = box
        self.Normal: Vector = self.Normal.normalize()  # Store in normalized form.
        self.DatumPlaneCounter: int = 0
        self.OriginIndex: int = -999  # Value that is less than -1 (used for constraints)

        # if tracing:
        #     print(f"{tracing}<={trace_arguments}")

    # def __repr__(self) -> str:
    #     """Return string representation of ApexDrawing."""
    #     return self.__str__()

    # def __str__(self) -> str:
    #     """Return string representation of ApexDrawing."""
    #     return (f"ApexDrawing({self.Contact}, {self.Normal}, {self.Operations}, '{self.Name}')")

    # ApexDrawing.show():
    # def show(self) -> str:
    #     """Return compact string for ApexDrawing."""
    #     contact: Union[Vector, Vector] = self.Contact
    #     if isinstance(contact, Vector):
    #         contact = contact.vector
    #     assert isinstance(contact, Vector)
    #     normal: Union[Vector, Vector] = self.Normal
    #     if isinstance(normal, Vector):
    #         contact = normal.vector
    #     assert isinstance(normal, Vector)

    #     operations: ApexOperation
    #     operations_text: str = ", ".join([f"{operation.show()}" for operation in self.Operations])
    #     return ("ApexDrawing("
    #             f"({contact.x},{contact.y},{contact.z}), ({normal.x},{normal.y},{normal.z})"
    #             f"({operations_text}), '{self.Name}')")

    # ApexDrawing.create_datum_plane():
    def create_datum_plane(self, body: "PartDesign.Body", name: Optional[str] = None,
                           tracing: str = "") -> "Part.ApexGeometry":
        """Return the FreeCAD DatumPlane used for the drawing.

        Arguments:
        * *body* (PartDesign.Body): The FreeCAD Part design Body to attach the datum plane to.
        * *name* (Optional[str]): The datum plane name.
          (Default: "...DatumPlaneN", where N is incremented.)
        * Returns:
          * (Part.ApexGeometry) that is the datum_plane.
        """
        # This is where the math for FreeCAD DatumPlanes is discussed.
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
        # The section on Hessian normal plane representation from
        # [MathWorld Planes](https://mathworld.wolfram.com/Plane.html)
        # is worth reading.
        #
        # The base coordinate system ('b' suffix) has an origin (Ob=(0,0,0)), X axis (<Xb>=(1,0,0)),
        # Y axis (<Yb>=(0,1,0), and Z axis (<Zb>=(0,1,0).
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
        if tracing:
            print(f"{tracing}=>ApexDrawing.create_datum_plane("
                  f"'{self.Name}', '{body.Name}', {name})")
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
        if not name:
            name = f"{self.Name}.DatumPlane{self.DatumPlaneCounter}"
            self.DatumPlaneCounter += 1
        datum_plane: Part.ApexGeometry = body.newObject("PartDesign::Plane", name)
        # xy_plane: App.GeoApexGeometry = body.getObject("XY_Plane")
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

        # Turn datum plane visibility off:
        if App.GuiUp:  # pragma: no unit cover
            gui_document: Any = Gui.ActiveDocument
            object_name: str = datum_plane.Name
            gui_datum_plane: Any = gui_document.getObject(object_name)
            if gui_datum_plane is not None and hasattr(gui_datum_plane, "Visibility"):
                setattr(gui_datum_plane, "Visibility", False)

        self._datum_plane = datum_plane
        if tracing:
            print(f"{tracing}<=ApexDrawing.create_datum_plane("
                  f"'{self.Name}', '{body.Name}', '{name}') => *")
        return self._datum_plane

    # ApexDrawing.plane_process():
    def plane_process(self, body: "PartDesign.Body", document_name: str, tracing: str = "") -> None:
        """Plane_Process."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}################################################################")
            print(f"{tracing}=>ApexDrawing.plane_process('{self.Name}', '{body.Name}')")

        # app_document: App.Document = App.getDocument(document_name)
        gui_document: Optional[Gui.Document] = None
        if App.GuiUp:  # pragma: no unit cover
            gui_document = Gui.getDocument(document_name)

        # Create the *datum_plane*.  The "Apex" in Part.ApexGeometry is a coinciding name used
        # by the FreeCAD Part Design workbench. It is not related to the Apex classes.
        # There is commonly used *datum_plane* for all sketches:
        datum_plane: Part.ApexGeometry = self.create_datum_plane(body, tracing=next_tracing)

        # Partition *operations* into *groups* based on the associated *sort_key*:
        SortKey = Tuple[str, ...]
        groups: Dict[SortKey, Tuple[ApexOperation, ...]] = {}
        sort_key: SortKey
        index: int
        operation: ApexOperation
        for index, operation in enumerate(self.Operations):
            sort_key = operation.SortKey
            if sort_key not in groups:
                groups[sort_key] = ()
            groups[sort_key] += (operation,)
        if tracing:
            print(f"{tracing}{groups.keys()=}")

        # Generate one *sketch* per *group*:
        for index, sort_key in enumerate(sorted(groups.keys())):
            operations: Tuple[ApexOperation, ...] = groups[sort_key]
            if tracing:
                print("")
                print(f"{tracing}Groups[{index}:{sort_key}]:|operations|={len(operations)}")

            operation0: ApexOperation = operations[0]

            # Create a new *drawing* using elements:
            operation_name: str = f"{operation0.Name}_{len(operations)}"
            drawing = ApexDrawing(self.Contact, self.Normal, operations, operation_name)

            # Create the *sketch* and attach it to *datum_plane*:
            sketch_name: str = f"{operation0.Name}.sketch"
            sketch: Sketcher.SketchObject = body.newObject("Sketcher::SketchObject", sketch_name)
            if tracing:
                print(f"{tracing}{sketch=} {sketch.Name=}")
            sketch.Support = (datum_plane, "")
            sketch.MapMode = "FlatFace"
            if App.GuiUp:
                if gui_document:  # pragma: no unit cover
                    if tracing:
                        print(f"{tracing}{sketch.Name=}")
                    gui_sketch: Any = gui_document.getObject(sketch.Name)
                    if gui_sketch and hasattr(gui_sketch, "Visibility"):
                        if tracing:
                            print(f"{tracing}Set sketch visibility to false")
                        setattr(gui_sketch, "Visibility", False)
            # visibility_set(sketch, False)

            # Fill in the *sketch* from *drawing*:
            drawing.sketch(sketch, tracing=next_tracing)

            for operation in operations:
                operation.body_apply(body, operation_name, sketch, gui_document)

        if tracing:
            print(f"{tracing}<=ApexDrawing.plane_process('self._name', '{body.Name}')")

    # ApexDrawing.point_constraints_append():
    def point_constraints_append(self, point: Vector, constraints: List[Sketcher.Constraint],
                                 tracing: str = "") -> None:  # REMOVE
        """Append Vector constraints to a list."""
        # Now that the *origin_index* is set, is is safe to assemble the *constraints*:
        if tracing:
            print(f"{tracing}=>Vector.constraints_append(*, |*|={len(constraints)})")
        origin_index: int = self.OriginIndex

        # Set DistanceX constraint:
        constraints.append(Sketcher.Constraint("DistanceX",
                                               -1, 1,  # -1 => OriginRoot.
                                               origin_index, 1, point.x))
        if tracing:
            print(f"{tracing}     [{len(constraints)}]: "
                  f"DistanceX('RootOrigin':(-1, 1), "
                  f"'{point.name}':({origin_index}, 1)), {point.x:.2f}")

        # Set DistanceY constraint:
        constraints.append(Sketcher.Constraint("DistanceY",
                                               -1, 1,  # -1 => OriginRoot.
                                               origin_index, 1, point.y))
        if tracing:
            print(f"{tracing}     [{len(constraints)}]: "
                  f"DistanceY('RootOrigin':(-1, 1), "
                  f"'{point.name}':({origin_index}, 1), {point.y:.2f})")
            print(f"{tracing}<=Vector.constraints_append(*, |*|={len(constraints)})")

    # ApexDrawing.geometries_get():
    def point_geometries_get(self, point: Vector, tracing: str = "") -> Tuple["ApexGeometry", ...]:
        """Return the ApexPointGeometry Geometry's."""
        assert isinstance(point, Vector)
        return (ApexPointGeometry(self, point, ""),)

    # ApexDrawing.reorient():
    def reorient(self, placement: Placement, suffix: Optional[str] = "",
                 tracing: str = "") -> "ApexDrawing":
        """Return a reoriented ApexDrawing.

        Arguments:
        * *placement* (Placement): The Placement to apply ApexCircle's and ApexPolygon's.
        * *suffix* (Optional[str]): The suffix to append at all names.  If None, all
          names are set to "" instead appending the suffix.  (Default: "")

        """
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>ApexDrawing.reorient('{self.Name}', {placement}, '{suffix}')")

        operation: ApexOperation
        if tracing:
            index: int
            for index, operation in enumerate(self.Operations):
                print(f"{tracing}[{index}]:'{operation.Name}'")
        reoriented_operations: Tuple[ApexOperation, ...] = tuple(
            [operation.reorient(placement, suffix, tracing=next_tracing)
             for operation in self.Operations]
        )
        if tracing:
            print(f"{tracing}{reoriented_operations=}")

        # Reorient the plane *contact* point.
        reoriented_contact: Vector = placement * self.Contact

        # The *normal* is only rotated, not translated.
        reoriented_normal: Vector = placement.Rotation * self.Normal

        apex_drawing: ApexDrawing = ApexDrawing(
            reoriented_contact, reoriented_normal, reoriented_operations, f"{self.Name}{suffix}")

        if tracing:
            print(f"{tracing}{self.Contact=} >= {reoriented_contact}")
            print(f"{tracing}{self.Normal=} >= {reoriented_normal}")
            for index, operation in enumerate(self.Operations):
                print(f"{tracing}[{index}]: {operation} =>")
                print(f"{tracing}     {reoriented_operations[index]}")
        if tracing:
            print(f"{tracing}<=ApexDrawing.reorient('{self.Name}', {placement}, '{suffix}')")
        return apex_drawing

    # ApexDrawing.sketch():
    def sketch(self, sketcher: "Sketcher.SketchObject", tracing: str = "") -> None:
        """Insert an ApexDrawing into a FreeCAD SketchObject.

        Arguments:
        * sketcher (Sketcher.SketchObject): The sketcher object to use.
        """
        # Perform any requested *tracing*:
        index: int
        operation: ApexOperation
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>ApexDrawing.sketch('{self.Name}', *)")
            for index, operation in enumerate(self.Operations):
                print(f"{tracing}Operation[{index}]: '{operation.Name}'")

        # Ensure that *contact* and *normal* are Vector's:
        contact: Vector = self.Contact
        normal: Vector = self.Normal

        # Rotate all geometries around *contact* such that *normal* is aligned with the +Z axis:
        origin: Vector = Vector(0, 0, 0)
        z_axis: Vector = Vector(0, 0, 1)
        rotation: Rotation = Rotation(normal, z_axis)
        z_aligned_placement: Placement = Placement(origin, rotation)
        if tracing:
            print(f"{tracing}{origin=} {rotation=} {contact=}")
            print(f"{tracing}{z_aligned_placement=}")
        z_aligned_drawing: "ApexDrawing" = self.reorient(
            z_aligned_placement, ".+z", tracing=next_tracing)
        if tracing:
            print(f"{tracing}{z_aligned_drawing.Box=}")

        # There may be a better way of doing this, but for now, everything is moved to
        # quadrant 1 (i.e. +X/+Y quarter plane.)  This ensures that all length constraints
        # are always positive.  The drawing has a true Origin point.  In addition, there
        # is a *lower_left* point that is at the lower left corner of the drawing.  All
        # X/Y length constraints are positive numbers measured from the *lower_left* point.
        # The *lower_left* point is constrained to the true drawing origin by an X constraint
        # and Y constraint.  These two constraints can have values that can be positive,
        # negative or zero.  This will recenter the drawing to be in the correct location.

        z_aligned_box: ApexBox = z_aligned_drawing.Box
        tsw: Vector = z_aligned_box.TSW  # Lower left is along the SW bounding box edge.
        quadrant1_placement: Placement = Placement(Vector(-tsw.x, -tsw.y, 0.0), Rotation())
        if tracing:
            print(f"{tracing}before reorient")
        quadrant1_drawing: "ApexDrawing" = z_aligned_drawing.reorient(
            quadrant1_placement, ".q1")
        if tracing:
            print(f"{tracing}after reorient")

        points: Tuple[Vector, ...] = (Vector(tsw.x, tsw.y, 0.0),)
        # quadrant1_exterior: Optional[ApexShape] = quadrant1_drawing._exterior

        # Extract *final_shapes* from *operations*:
        operations: Tuple[ApexOperation, ...] = quadrant1_drawing.Operations
        shapes: List[ApexShape] = [operation.shape_get() for operation in operations]
        final_shapes: Tuple[ApexShape, ...] = tuple(shapes)

        # Now extract all of the ApexGeometry's:
        geometries: List[ApexGeometry] = []

        # Extract the ApexGeometry's from *points* (this must be first):
        point: Vector
        for point in points:
            geometries.extend(self.point_geometries_get(point))

        # Now extract all of the ApexGeometry's from *final_shapes*::
        shape: ApexShape
        for shape in final_shapes:
            f: Tuple[ApexGeometry, ...] = shape.geometries_get(self)
            assert f is shape.geometries_get(self), f"{shape=} {f=}"
            geometries.extend(f)

        # The first Geometry corresponds to *lower_left* and it is the "origin" for the sketch.
        lower_left_geometry: ApexGeometry = geometries[0]
        assert isinstance(lower_left_geometry, ApexPointGeometry)

        def indices_check(geometries: Tuple[ApexGeometry, ...]) -> None:
            for index, geometry in enumerate(geometries):
                assert geometry.index == index

        # Set the *index* for each Geometry in *final_geometries*:
        for index, geometry in enumerate(geometries):
            geometry.index = index
            if tracing:
                print(f"{tracing}Geometries[{index}]: {geometry}")
        final_geometries: Tuple[ApexGeometry, ...] = tuple(geometries)
        indices_check(final_geometries)
        indices_check(final_geometries)

        if tracing:
            print(f"{tracing}indices set")

        # Now that the Geometry indices are set, *origin_index* can be extracted:
        origin_index: int = lower_left_geometry.index
        assert origin_index >= -1
        self._origin_index = origin_index
        self.OriginIndex = origin_index

        if tracing:
            print(f"{tracing}{origin_index=}")

        # Extract *part_geometries* from *geometries*:
        part_geometry: PartGeometry
        part_geometries: List[PartGeometry] = []
        for index, geometry in enumerate(final_geometries):
            part_geometry = geometry.part_geometry
            part_geometries.append(part_geometry)
            if tracing:
                print(f"{tracing}part_geometries[{index}]: {part_geometry}")
        sketcher.addGeometry(part_geometries, False)

        # The *points* and *operations* Constraint's are extracted next:
        constraints: List[Sketcher.Constraint] = []
        for point in points:
            self.point_constraints_append(point, constraints)

        # Need to iterate over all of the ApexShape's:
        if tracing:
            print(f"{tracing}Apex Shape's iteration")
        for index, shape in enumerate(final_shapes):
            if tracing:
                print(f"{tracing}Operation[{index}]: {operation}")
                print(f"{tracing}Shape[{index}]: {shape}")
            shape.constraints_append(self, constraints, tracing=next_tracing)

        if tracing:
            print(f"{tracing}here 1")

        # Load the final *constraints* into *sketcher*:
        sketcher.addConstraint(constraints)

        if tracing:
            print(f"{tracing}<=ApexDrawing.sket8mch('{self.Name}', *)")


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


def _integration_test() -> int:
    """Run the program."""
    # Open *document_name* and get associated *app_document* and *gui_document*:
    drawing: ApexDrawing
    center_circle: ApexCircle

    document_name: str = "ApexSketchUnitTests"
    app_document: App.Document = App.newDocument(document_name)
    # gui_document: Optional[Gui.Document] = None
    # if App.GuiUp:
    #     gui_document = Gui.GetDocument(document_name)

    # Do some trivial tests on drawing:
    # try:
    #     drawing = ApexDrawing(Vector(), Vector(0, 0, 1), (), "drawing")  # type: ignore
    # except ValueError as value_error:
    #     assert str(value_error) == (
    #         "Argument 'name' is int which is not one of ['str']"), f"{str(value_error)=}"

    # Do some unit tests on *Placment* objects to make sure they behave as documented.
    origin: Vector = Vector(0, 0, 0)
    x_axis: Vector = Vector(1, 0, 0)
    y_axis: Vector = Vector(0, 1, 0)
    z_axis: Vector = Vector(0, 0, 1)

    r0: Rotation = Rotation()
    assert r0 * origin == origin
    assert r0 * x_axis == x_axis
    assert r0 * y_axis == y_axis
    assert r0 * z_axis == z_axis

    rxy: Rotation = Rotation(x_axis, y_axis)
    assert rxy * x_axis == y_axis
    ryx: Rotation = Rotation(y_axis, x_axis)
    assert ryx * y_axis == x_axis

    rxz: Rotation = Rotation(x_axis, z_axis)
    assert rxz * x_axis == z_axis
    rzx: Rotation = Rotation(z_axis, x_axis)
    assert rzx * z_axis == x_axis

    ryz: Rotation = Rotation(y_axis, z_axis)
    assert ryz * y_axis == z_axis
    rzy: Rotation = Rotation(z_axis, y_axis)
    assert rzy * z_axis == y_axis

    t10: Vector = Vector(10, 10, 10)

    t10_r0_placement: Placement = Placement(t10, r0)
    assert t10_r0_placement * origin == t10
    assert t10_r0_placement * x_axis == t10 + x_axis
    assert t10_r0_placement * y_axis == t10 + y_axis
    assert t10_r0_placement * z_axis == t10 + z_axis

    t10_r0_c10_placement: Placement = Placement(t10, r0, t10)
    assert t10_r0_c10_placement * origin == t10
    assert t10_r0_c10_placement * x_axis == t10 + x_axis
    assert t10_r0_c10_placement * y_axis == t10 + y_axis
    assert t10_r0_c10_placement * z_axis == t10 + z_axis

    t0_rxy_c10_placement: Placement = Placement(origin, rxy, t10)
    assert vector_fix(t0_rxy_c10_placement * t10) == t10, (
        vector_fix(t0_rxy_c10_placement * t10), t10)
    # TODO: Fix:
    # assert vector_fix(t0_rxy_c10_placement * (t10 + x_axis)) == t10 + y_axis, (
    #     vector_fix(t0_rxy_c10_placement * (t10 + x_axis)), t10 + y_axis)
    t0_ryx_c10_placement: Placement = Placement(origin, ryx, t10)
    assert vector_fix(t0_ryx_c10_placement * t10) == t10, t0_ryx_c10_placement * t10
    assert vector_fix(t0_ryx_c10_placement * (t10 + y_axis)) == t10 + x_axis

    if True:
        # Create *box_polygon* (with notch in lower left corner):
        left_x: float = -40.0
        right_x: float = 40.0
        upper_y: float = 20.0
        lower_y: float = -20.0
        radius1: float = 0.0
        radius2: float = 5.0
        _ = radius2
        notch_x: float = 10.0
        notch_y: float = 10.0
        lower_left_bottom: ApexCorner = ApexCorner(
            Vector(left_x + notch_x, lower_y, 0.0), 0.0, "lower_left_bottom")
        lower_right: ApexCorner = ApexCorner(Vector(right_x, lower_y, 0.0), 0.0, "lower_right")
        upper_right: Vector = ApexCorner(Vector(right_x, upper_y, 0.0), radius2, "upper_right")
        notch1: ApexCorner = ApexCorner(Vector(right_x, upper_y - notch_y, 0.0), radius1, "notch1")
        notch2: ApexCorner = ApexCorner(
            Vector(right_x - notch_x, upper_y - notch_y, 0.0), radius2, "notch2")
        notch3: ApexCorner = ApexCorner(Vector(right_x - notch_x, upper_y, 0.0), radius1, "notch3")
        upper_left: ApexCorner = ApexCorner(Vector(left_x, upper_y, 0.0), radius1, "upper_left")
        lower_left_left: ApexCorner = ApexCorner(
            Vector(left_x, lower_y + notch_y, 0.0), radius1, "lower_left_left")
        _ = upper_right
        _ = notch1
        _ = notch2
        _ = notch3
        contour_corners: Tuple[ApexCorner, ...] = (
            lower_left_bottom,
            lower_right,
            upper_right,
            # notch1,
            # notch2,
            # notch3,
            upper_left,
            lower_left_left,
        )
        contour_polygon: ApexPolygon = ApexPolygon(contour_corners, "contour_polygon")
        assert contour_polygon.Name == "contour_polygon", contour_polygon.Name

        ne_corner: ApexCorner = ApexCorner(Vector(20, 20, 0), 0.0, "ne_corner")
        nw_corner: ApexCorner = ApexCorner(Vector(20, 10, 0), 0.0, "nw_corner")
        sw_corner: ApexCorner = ApexCorner(Vector(10, 10, 0), 0.0, "sw_corner")
        se_corner: ApexCorner = ApexCorner(Vector(10, 20, 0), 0.0, "se_corner")
        simple_corners: Tuple[ApexCorner, ...] = (ne_corner, nw_corner, sw_corner, se_corner)
        # contour_polygon = ApexPolygon(simple_corners, "contour_polygon")
        _ = simple_corners

        depth: float = 10.0
        through: float = depth + 1.0
        assert contour_polygon.Name == "contour_polygon", contour_polygon.Name
        contour_operation: ApexPad = ApexPad(contour_polygon, depth, "contour_operation")

        # Create the *hole_center*:
        center_circle = ApexCircle(Vector(0.0, 0.0, 0.0), through, "center_hole")
        assert center_circle.Name == "center_hole", center_circle.Name
        center_operation: ApexHole = ApexHole(center_circle, through, "center")

        sides: int = 6
        angle_increment: float = 2 * math.pi / float(sides)
        print(f"{math.degrees(angle_increment)=}")
        x_offset: float = -20.0
        y_offset: float = 5.0
        hex_radius: float = 8.0
        hexagon_corners: List[ApexCorner] = []
        index: int
        for index in range(sides):
            angle: float = index * angle_increment
            x: float = x_offset + hex_radius * math.cos(angle)
            y: float = y_offset + hex_radius * math.sin(angle)
            hexagon_corner: ApexCorner = ApexCorner(Vector(x, y, 0.0), 2.0, f"hex{index}")
            print(f"HexegonCorner[{index}]: {hexagon_corner}")
            hexagon_corners.append(hexagon_corner)
        hexagon: ApexPolygon = ApexPolygon(tuple(hexagon_corners), "hexagon")
        hexagon_operation: ApexPocket = ApexPocket(hexagon, through, "hexagon")
        _ = hexagon_operation

        # Create the *drawing*:
        operations: Tuple[ApexOperation, ...] = (
            contour_operation, center_operation, hexagon_operation)
        operation: ApexOperation
        for index, operation in enumerate(operations):
            print(f"Operation[{index}]: {operation}")
        # _ = hexagon_operation
        # _ = center_operation
        drawing = ApexDrawing(origin, z_axis, operations, "test_drawing")

        # Create the FreeCAD Part Design Workbench *body* object:
        body_name: str = drawing.Name if drawing.Name else "Body"
        body: PartDesign.Body = app_document.addObject("PartDesign::Body", body_name)
        drawing.plane_process(body, document_name, tracing=" ")
        visibility_set(body)
        app_document.recompute()  # This is *VERY* important!!!

    # Delete previous file *fcstd_path* and then save a new one:
    root: Path = Path("/")
    fcstd_path: Path = root / "tmp" / f"{document_name}.fcstd"
    if fcstd_path.exists():
        fcstd_path.unlink()
    print(f"Save {fcstd_path} file.")
    app_document.saveAs(f"{str(fcstd_path)}")

    # Close *document_name* and exit by closing the main window:
    App.closeDocument(document_name)
    if App.GuiUp:
        Gui.getMainWindow().close()  # pragma: no unit cover
    return 0


def class_names_show(module_object: Any) -> None:  # pragma: no unit cover
    """Show the the class name of an object."""
    print(f"module: {module_object.__name__}")
    name: str
    for name in dir(module_object):
        pass
        # attribute = getattr(module_object, name)
        # if inspect.isclass(attribute):
        #     print(f"  class: {name}")


def attributes_show(some_object: Any) -> None:  # pragma: no unit cover
    """Show the attributes of an object."""
    pass
    # name: str
    # for name in dir(some_object):
    #     if name[0] != "_":
    #         print(f"{name}: {getattr(some_object, name)}")


if __name__ == "__main__":
    ApexCorner._unit_tests()
    ApexPolygon._unit_tests()
    _integration_test()
