#!/usr/bin/env python3
"""
Node: Fab tree management.

The Node package provides a tree of FabNode's that roughly corresponds to a FreeCAD tree
as shown in the FreeCAD model view.

There are two classes defined:
* FabBox:
  This is a generic bounding box class similar to the FreeCAD BoundBox class
  is used to enclose the FabNode contents and its children FabNode's.
  This class has way more more properties and is immutable (unlike the FreeCAD BoundBox class.)
* FabNode:
  This is a sub-class of FabBox that has a name, a parent FabNode and other data structures
  required to maintain the tree.

Other Fab packages (e.g. Project and Solid) further sub-class FabNode to provide finer
grained distinctions between FabNode's.

The FabNode class enforces the following constraints:
* Each FabNode name must be compatible with a Python variable name
  (i.e. upper/lower letters, digits, and underscores with a non-digit first letter.)
* All of the children FabNode's must have distinct names.
* A FabNode may occur only once in the Tree (i.e. DAG = Direct Acyclic Graph.)

Two notable attributes of the FabNode are:
* *Up* (FabNode):
   The FabNode's parent.
   Up is frequently used in code to access other FabNode's higher in the FabNode tree.
* *Project* (FabNode):
   The FabNode tree root and is always of type FabProject which is defined in Project package.
   Due to the Python lanaguage disallowal of circular `import` statements, this is returned
   as type FabNode rather than type FabProject.
See the FabNode documentation for further attributes.

(Briefly talk about produce() method here.)

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

import sys
sys.path.append(".")
import Embed
USE_FREECAD: bool
USE_CAD_QUERY: bool
USE_FREECAD, USE_CAD_QUERY = Embed.setup()

from dataclasses import dataclass, field
from typing import Any, cast, List, Sequence, Tuple, Union
from collections import OrderedDict

if USE_FREECAD:
    from FreeCAD import Placement, Vector  # type: ignore
    import FreeCAD as App  # type: ignore
    import FreeCADGui as Gui  # type: ignore
elif USE_CAD_QUERY:
    from cadquery import Vector  # type: ignore


@dataclass
class _BoundBox(object):
    """Fake BoundBox class."""

    XMin: float
    YMin: float
    ZMin: float
    XMax: float
    YMax: float
    ZMax: float


if USE_FREECAD:
    from FreeCAD import BoundBox
elif USE_CAD_QUERY:
    BoundBox = _BoundBox
    

# FabBox:
@dataclass
class FabBox(object):
    """FabBox: X/Y/Z Axis Aligned Cubiod.

    An FabBox is represents a cuboid (i.e. a rectangular parallelpiped, or right prism) where
    the edges are aligned with the X, Y, and Z axes.  This is basically equivalent to the FreeCAD
    BoundBox object, but with way more attributes to access various points on the cuboid surface.

    The basic attribute nomenclature is based on the compass points North (+Y), South (-Y),
    East (+X) and West (-X).  Two additional "compass" points call Top (+Z) and Bottom (-Z)
    are introduced as well.

    Thus:
    * TNE represents the Top North East corner of the box.
    * NE represents the center of the North East box edge.
    * T represents the center of the top face of the box.

    Attributes:
    * Minimums/Maximums:
      * XMax (float): The maximum X (East).
      * XMin (float): The minumum X (West).
      * YMax (float): The maximum Y (North).
      * YMin (float): The minimum Y (South).
      * ZMax (float): The maximum Z (Top).
      * ZMin (float): The minimum Z (Bottom).
    * The 6 face attributes:
      * B (Vector): Center of bottom face.
      * E (Vector): Center of east face.
      * N (Vector): Center of north face.
      * S (Vector): Center of south face.
      * T (Vector): Center of top face.
      * W (Vector): Center of west face.
    * The 8 corner attributes:
      * BNE (Vector): Bottom North East corner.
      * BNW (Vector): Bottom North West corner.
      * BSE (Vector): Bottom South East corner.
      * BSW (Vector): Bottom South West corner.
      * TNE (Vector): Top North East corner.
      * TNW (Vector): Top North West corner.
      * TSE (Vector): Top South East corner.
      * TSW (Vector): Bottom South West corner.
    * The 12 edge attributes:
      * BE (Vector): Center of Bottom East edge.
      * BN (Vector): Center of Bottom North edge.
      * BS (Vector): Center of Bottom South edge.
      * BW (Vector): Center of Bottom West edge.
      * NE (Vector): Center of North East edge
      * NW (Vector): Center of North West edge
      * SE (Vector): Center of South East edge
      * SW (Vector): Center of South West edge
      * TE (Vector): Center of Top East edge.
      * TN (Vector): Center of Top North edge.
      * TS (Vector): Center of Top South edge.
      * TW (Vector): Center of Top West edge.
    * The other attributes:
      * BB (BoundBox): The FreeCAD BoundBox object.
      * C (Vector): Center point.
      * DB (Vector): Bottom direction (i.e. B - C)
      * DE (Vector): East direction (i.e. E - C)
      * DN (Vector): North direction (i.e. N - C)
      * DS (Vector): South direction (i.e. S - C)
      * DT (Vector): Top direction (i.e. T - C)
      * DW (Vector): West direction (i.e. W - C)
      * DX (float): X box length (i.e. (E - W).Length)
      * DY (float): Y box length (i.e. (N - S).Length)
      * DZ (float): Z box length (i.e. (T - B).Length)

    """

    # These are in the same order as FreeCAD BoundBox:
    _XMin: float = field(init=False, repr=False)
    _YMin: float = field(init=False, repr=False)
    _ZMin: float = field(init=False, repr=False)
    _XMax: float = field(init=False, repr=False)
    _YMax: float = field(init=False, repr=False)
    _ZMax: float = field(init=False, repr=False)

    # FabBox.__init__():
    def __post_init__(self) -> None:
        self._XMin = -1.0
        self._XMax = 1.0
        self._YMin = -1.0
        self._YMax = 1.0
        self._ZMin = -1.0
        self._ZMax = 1.0

    # FabBox.enclose():
    def enclose(self, bounds: Sequence[Union[Vector, "BoundBox", "FabBox"]]) -> None:
        """Initialize a FabBox.

        Arguments:
          * *bounds* (Sequence[Union[Vector, BoundBox, FabBox]]):
            A sequence of points or boxes to enclose.

        Raises:
          * ValueError: For bad or empty corners.

        """
        if not isinstance(bounds, (list, tuple)):
            raise RuntimeError(f"{bounds} is {str(type(bounds))}, not List/Tuple")
        if not bounds:
            raise RuntimeError("Bounds sequence is empty")

        # Convert *corners* into *vectors*:
        bound: Union[Vector, BoundBox, FabBox]
        vectors: List[Vector] = []
        for bound in bounds:
            if isinstance(bound, Vector):
                vectors.append(bound)
            elif USE_FREECAD and isinstance(bound, BoundBox):
                vectors.append(Vector(bound.XMin, bound.YMin, bound.ZMin))
                vectors.append(Vector(bound.XMax, bound.YMax, bound.ZMax))
            elif USE_CAD_QUERY and isinstance(bound, _BoundBox):
                vectors.append(Vector(bound.XMin, bound.YMin, bound.ZMin))
                vectors.append(Vector(bound.XMax, bound.YMax, bound.ZMax))
            elif isinstance(bound, FabBox):
                vectors.append(bound.TNE)
                vectors.append(bound.BSW)
            else:
                raise RuntimeError(
                    f"{bound} is {str(type(bound))}, not Vector/BoundBox/FabBox")

        # Initialize with from the first vector:
        vector0: Vector = vectors[0]
        x_min: float = vector0.x
        y_min: float = vector0.y
        z_min: float = vector0.z
        x_max: float = x_min
        y_max: float = y_min
        z_max: float = z_min

        # Sweep through *vectors* expanding the box limits:
        vector: Vector
        for vector in vectors[1:]:
            x: float = vector.x
            y: float = vector.y
            z: float = vector.z
            x_max = max(x_max, x)
            x_min = min(x_min, x)
            y_max = max(y_max, y)
            y_min = min(y_min, y)
            z_max = max(z_max, z)
            z_min = min(z_min, z)

        self._XMin = x_min
        self._YMin = y_min
        self._ZMin = z_min
        self._XMax = x_max
        self._YMax = y_max
        self._ZMax = z_max

    # 6 Standard X/Y/Z min/max attributes:

    # FabBox.XMin():
    @property
    def XMin(self) -> float:
        return self._XMin

    # FabBox.YMin():
    @property
    def YMin(self) -> float:
        return self._YMin

    # FabBox.ZMin():
    @property
    def ZMin(self) -> float:
        return self._ZMin

    # FabBox.XMax()
    @property
    def XMax(self) -> float:
        return self._XMax

    # FabBox.YMax()
    @property
    def YMax(self) -> float:
        return self._YMax

    # FabBox.ZMax()
    @property
    def ZMax(self) -> float:
        return self._ZMax

    # 6 Face attributes:

    @property
    def B(self) -> Vector:
        """Bottom face center."""
        return Vector((self._XMin + self._XMax) / 2.0, (self._YMin + self._YMax) / 2.0, self._ZMin)

    @property
    def E(self) -> Vector:
        """East face center."""
        return Vector(self._XMax, (self._YMin + self._YMax) / 2.0, (self._ZMin + self._ZMax) / 2.0)

    @property
    def N(self) -> Vector:
        """North face center."""
        return Vector((self._XMin + self._XMax) / 2.0, self._YMax, (self._ZMin + self._ZMax) / 2.0)

    @property
    def S(self) -> Vector:
        """South face center."""
        return Vector((self._XMin + self._XMax) / 2.0, self._YMin, (self._ZMin + self._ZMax) / 2.0)

    @property
    def T(self) -> Vector:
        """Top face center."""
        return Vector((self._XMin + self._XMax) / 2.0, (self._YMin + self._YMax) / 2.0, self._ZMax)

    @property
    def W(self) -> Vector:
        """Center of bottom face."""
        return Vector(self._XMin, (self._YMin + self._YMax) / 2.0, (self._ZMin + self._ZMax) / 2.0)

    # 8 Corner attributes:

    @property
    def BNE(self) -> Vector:
        """Bottom North East corner."""
        return Vector(self._XMax, self._YMax, self._ZMin)

    @property
    def BNW(self) -> Vector:
        """Bottom North West corner."""
        return Vector(self._XMin, self._YMax, self._ZMin)

    @property
    def BSE(self) -> Vector:
        """Bottom South East corner."""
        return Vector(self._XMax, self._YMin, self._ZMin)

    @property
    def BSW(self) -> Vector:
        """Bottom South West corner."""
        return Vector(self._XMin, self._YMin, self._ZMin)

    @property
    def TNE(self) -> Vector:
        """Top North East corner."""
        return Vector(self._XMax, self._YMax, self._ZMax)

    @property
    def TNW(self) -> Vector:
        """Top North West corner."""
        return Vector(self._XMin, self._YMax, self._ZMax)

    @property
    def TSE(self) -> Vector:
        """Top South East corner."""
        return Vector(self._XMax, self._YMin, self._ZMax)

    @property
    def TSW(self) -> Vector:
        """Top South West corner."""
        return Vector(self._XMin, self._YMin, self._ZMax)

    # 12 edge attributes:

    @property
    def BE(self) -> Vector:
        """Bottom East edge center."""
        return Vector(self._XMax, (self._YMin + self._YMax) / 2.0, self._ZMin)

    @property
    def BW(self) -> Vector:
        """Bottom West edge center."""
        return Vector(self._XMin, (self._YMin + self._YMax) / 2.0, self._ZMin)

    @property
    def BN(self) -> Vector:
        """Bottom North edge center."""
        return Vector((self._XMin + self._XMax) / 2.0, self._YMax, self._ZMin)

    @property
    def BS(self) -> Vector:
        """Bottom South edge center."""
        return Vector((self._XMin + self._XMax) / 2.0, self._YMin, self._ZMin)

    @property
    def NE(self) -> Vector:
        """North East edge center."""
        return Vector(self._XMax, self._YMax, (self._ZMin + self._ZMax) / 2.0)

    @property
    def NW(self) -> Vector:
        """North West edge center."""
        return Vector(self._XMin, self._YMax, (self._ZMin + self._ZMax) / 2.0)

    @property
    def SE(self) -> Vector:
        """North East edge center."""
        return Vector(self._XMax, self._YMin, (self._ZMin + self._ZMax) / 2.0)

    @property
    def SW(self) -> Vector:
        """South East edge center."""
        return Vector(self._XMin, self._YMin, (self._ZMin + self._ZMax) / 2.0)

    @property
    def TE(self) -> Vector:
        """Bottom East edge center."""
        return Vector(self._XMax, (self._YMin + self._YMax) / 2.0, self._ZMax)

    @property
    def TW(self) -> Vector:
        """Bottom West edge center."""
        return Vector(self._XMin, (self._YMin + self._YMax) / 2.0, self._ZMax)

    @property
    def TN(self) -> Vector:
        """Bottom North edge center."""
        return Vector((self._XMin + self._XMax) / 2.0, self._YMax, self._ZMax)

    @property
    def TS(self) -> Vector:
        """Bottom South edge center."""
        return Vector((self._XMin + self._XMax) / 2.0, self._YMin, self._ZMax)

    # Miscellaneous attributes:

    @property
    def BB(self) -> "BoundBox":
        """Return a corresponding FreeCAD BoundBox."""
        return BoundBox(self._XMin, self._YMin, self._ZMin, self._XMax, self._YMax, self._ZMax)

    @property
    def C(self) -> Vector:
        """Center point."""
        return Vector(
            (self._XMax + self._XMin) / 2.0,
            (self._YMax + self._YMin) / 2.0,
            (self._ZMax + self._ZMin) / 2.0
        )

    @property
    def DB(self) -> float:
        """Direction Bottom."""
        return self.B - self.C

    @property
    def DE(self) -> float:
        """Direction East."""
        return self.E - self.C

    @property
    def DN(self) -> float:
        """Direction North."""
        return self.N - self.C

    @property
    def DS(self) -> float:
        """Direction South."""
        return self.S - self.C

    @property
    def DT(self) -> float:
        """Direction Top."""
        return self.T - self.C

    @property
    def DW(self) -> float:
        """Direction West."""
        return self.W - self.C

    @property
    def DX(self) -> float:
        """Delta X."""
        return self._XMax - self._XMin

    @property
    def DY(self) -> float:
        """Delta Y."""
        return self._YMax - self._YMin

    @property
    def DZ(self) -> float:
        """Delta Z."""
        return self._ZMax - self._ZMin

    # FabBox.reorient():
    def reorient(self, placement: "Placement") -> "FabBox":
        """Reorient FabBox given a Placement.

        Note after the *placement* is applied, the resulting box is still rectilinear with the
        X/Y/Z axes.  In particular, box volume is *not* conserved.

        Arguments:
        * *placement* (Placement): The placement of the box corners.
        """
        reoriented_bsw: Vector = placement * self.BSW
        reoriented_tne: Vector = placement * self.TNE
        box = FabBox()
        box.enclose((reoriented_bsw, reoriented_tne))
        return box

    # FabBox.intersect():
    def intersect(self, segment_start: Vector, segment_end: Vector,
                  tracing: str = "") -> Tuple[bool, float, float]:
        """Compute Line Segment intersection with a FabBox.

        Arguments:
        * *segment_start* (Vector): Start point of the line segment.
        * *segment_end* (Vector): End point of the line segment.

        Returns:
        * (bool): True is some portion of the line segment is inside of the FabBox.
        * (Vector): When True, the possibly truncated line segment point near *segment_start*.
        * (Vector): When True, the possibly truncated line segment point near *segment_end*.

        """
        # The basic algorithm is pretty easy.  Using S for *segment_start* and E for *segment_end*,
        # the standard representation of a parametric line that goes through S and E is:
        #
        #      P = S + r * (E - S)
        #
        # Where r is a ratio such that r=0 returns S and r=1 returns E.
        #
        # The B for *begin* and F for *finish*, the goal is find B and F such that they
        # lay in the line segment (SE) but are further constrained to reside in the FabBox.
        # The ultimate goal is to compute rB and rF which is the 0 <= rB <= 1 and 0 <= RF <= 1.
        # If the line segment lies entirely outside of the bounding box, there are no valid
        # values for rB and rF.
        #
        # The algorithm below does this by iterating over the X, Y, and Z axes.  Using N for
        # *miNimum* and X for *maXimum*.  N, X, S, and E are each projected onto the axis
        # and the ratios rB and rF are adjusted to ensure the projection of the remains
        # inside of the projected FabBox boundaries on the axis.

        if tracing:
            print(f"{tracing}=>FabBox.intersect({segment_start}, {segment_end})")

        # Initialize the X/Y/Z *axes* data:
        axes: Tuple[Tuple[str, float, float, float, float], ...] = (
            ("X", segment_start.x, segment_end.x, self._XMin, self._XMax),
            ("Y", segment_start.y, segment_end.y, self._YMin, self._YMax),
            ("Z", segment_start.z, segment_end.z, self._ZMin, self._ZMax),
        )

        EPSILON: float = 1.0e-8
        intersect: bool = True
        begin_ratio: float = 0.0  # Starts at 0 and can be moved towards 1.
        finish_ratio: float = 1.0  # Starts at 1 and can be moved toward 0.
        # 0 <= *begin_ratio* <= *finish_ratio* <= 1 for a truncated segment that lies inside FabBox.

        # Visit the each of the X, Y, and Z *axes*:
        axis_name: str
        start: float
        end: float
        minimum: float
        maximum: float
        for axis_name, start, end, minimum, maximum in axes:
            # Check for bounding box issues:
            assert minimum < maximum, f"{axis_name}: FabBox has bad inverted bounds"
            bounding_box_is_empty: bool = abs(maximum - minimum) < EPSILON
            segment_is_above_maximum: bool = start > maximum and end > maximum
            segment_is_below_minimum: bool = start < minimum and end < minimum
            if bounding_box_is_empty or segment_is_above_maximum or segment_is_below_minimum:
                intersect = False
                if tracing:
                    print(f"{tracing}{axis_name}: Bounding Box issue: {bounding_box_is_empty=} "
                          f"{segment_is_above_maximum=} {segment_is_below_minimum=} {intersect=}")
                break

            # If segment projects down to a point, skip axis check:
            distance: float = end - start  # Can be negative
            if abs(distance) < EPSILON:
                continue

            # Compute the *minimum_ratio* and *maximum_ratio*.
            # They can be negative if *start* > *end*.
            minimum_ratio: float = (minimum - start) / distance  # Can be negative
            maximum_ratio: float = (maximum - start) / distance  # Can be negative
            if tracing:
                print(f"{tracing}{axis_name}: {minimum=} {start=} {end=} {maximum=}")
                print(f"{tracing}{axis_name}: {distance=} {minimum_ratio=} {maximum_ratio=}")

            # See if *begin_ratio* needs to be "pulled in":
            new_begin_ratio: float = begin_ratio
            if maximum_ratio > minimum_ratio and minimum_ratio > begin_ratio:
                new_begin_ratio = minimum_ratio
            elif maximum_ratio < minimum_ratio and maximum_ratio > begin_ratio:
                new_begin_ratio = maximum_ratio
            if tracing and new_begin_ratio != begin_ratio:
                print(f"{tracing}{axis_name}: "  # pragma: no unit cover
                      f"Updating {begin_ratio=} to {new_begin_ratio=}")
            begin_ratio = new_begin_ratio

            # See if *finish_ratio* needs to be "pulled in":
            new_finish_ratio: float = finish_ratio
            if maximum_ratio > minimum_ratio and maximum_ratio < finish_ratio:
                new_finish_ratio = maximum_ratio
            elif maximum_ratio < minimum_ratio and minimum_ratio < finish_ratio:
                new_finish_ratio = minimum_ratio
            if tracing and new_finish_ratio != finish_ratio:
                print(f"{tracing}{axis_name}: Updating {finish_ratio=} to {new_finish_ratio=}")
            finish_ratio = new_finish_ratio

            # Somehow we over shorted the segment, so there must not be an *intersect*:
            if begin_ratio > finish_ratio:
                intersect = False
                if tracing:
                    print(f"{tracing}{begin_ratio=} > {finish_ratio}: => {intersect=})")

        # Make sure we did not screw up the rule of only shortening the line segment:
        assert 0 <= begin_ratio <= finish_ratio <= 1.0, "Segment truncation failed"

        # Compute *begin_point* and *finish_point*:
        delta: Vector = segment_end - segment_start
        begin_point = segment_start + begin_ratio * delta
        finish_point = segment_start + finish_ratio * delta

        # Disallow zero length segments.
        if abs((begin_point - finish_point).Length) < EPSILON:
            intersect = False
        if tracing:
            print(f"{tracing}{delta=} {begin_ratio=} {finish_ratio=}")
            print(f"{tracing}<=FabBox.intersect({segment_start}, {segment_end})=>"
                  f"({intersect}, {begin_point}, {finish_point})")
            print("")
        return intersect, begin_point, finish_point

    # FabBox._intersect_unit_tests():
    @staticmethod
    def _intersect_unit_tests() -> None:
        """Perform intesection tests."""

        IntersectTest = Tuple[Vector, Vector, bool, Vector, Vector, str, str]

        def check(test: IntersectTest) -> str:
            """Return error message on check failure."""
            EPSILON: float = 1.0e-8

            unswapped_test: IntersectTest = test
            # Flip start/end and begin/finish:
            swapped_test: IntersectTest = (
                test[1], test[0], test[2], test[4], test[3], test[5], f"Swapped:{test[6]}")

            for test in (unswapped_test, swapped_test):
                want_start: Vector
                want_end: Vector
                want_intersect: bool
                want_begin: Vector
                want_finish: Vector
                tracing: str
                name: str
                want_start, want_end, want_intersect, want_begin, want_finish, tracing, name = test

                got_intersect: bool
                got_begin: Vector
                got_end: Vector
                got_intersect, got_begin, got_finish = box.intersect(want_start, want_end, tracing)
                header: str = ""
                if got_intersect != want_intersect:
                    header = f"Intersect mismatch"  # pragma: no unit cover
                elif want_intersect and abs(got_begin - want_begin).Length > EPSILON:
                    header = f" Begin mismatch"  # pragma: no unit cover
                elif want_intersect and abs(got_finish - want_finish).Length > EPSILON:
                    header = "Finish mismatch:"  # pragma: no unit cover

                if header:  # pragma: no unit cover
                    return (
                        f"{header}: {name}\n"
                        f"     Input: {test[:2]}\n"
                        f"     Want:  {test[2:5]}\n"
                        f"     Got:   ({got_intersect}, {got_begin}, {got_finish})"
                    )
            return ""

        box: FabBox = FabBox()

        # Z axis spans
        a: Vector = Vector(0, 0, -2)
        b: Vector = Vector(0, 0, -1.5)
        c: Vector = Vector(0, 0, -1)
        d: Vector = Vector(0, 0, -0.5)
        e: Vector = Vector(0, 0, 0)
        f: Vector = Vector(0, 0, 0.5)
        g: Vector = Vector(0, 0, 1)
        h: Vector = Vector(0, 0, 1.5)
        i: Vector = Vector(0, 0, 2)
        x: Vector = Vector(-12, 34, -56)  # Should be ignored by test

        tests: Tuple[IntersectTest, ...] = (
            # Enclosed segment tests:
            (d, e, True, d, e, "", "Entirely enclosed segment 1"),
            (d, f, True, d, f, "", "Entirely enclosed segment 2"),
            (c, f, True, c, f, "", "Enclosed segment at begins at minimum"),
            (e, g, True, e, g, "", "Enclosed segment at finishes at maximum"),
            (c, g, True, c, g, "", "Enclosed segment that spans FabBox"),
            # Trimmed segment tests:
            (a, e, True, c, e, "", "Trimmed segment that starts below minimum and ends in FabBox"),
            (a, g, True, c, g, "", "Trimmed segment that starts below minimum and ends at maximum"),
            (a, i, True, c, g, "", "Trimmed segment that spans both minimum and maximum"),
            (e, h, True, e, g, "", "Trimmed segment from inside towards maximum"),
            # Segment non intersection tests:
            (a, b, False, x, x, "", "Segment is below minimum"),
            (a, c, False, x, x, "", "Segment is starts below minimum and ends at minimum"),
            (g, i, False, x, x, "", "Segment is starts at maximum and goes outward"),
            (h, i, False, x, x, "", "Segment is above minimum"),
            # Zero length segment tests:
            (a, a, False, x, x, "", "Zero Length segment below minimum"),
            (c, c, False, x, x, "", "Zero Length segment at minimum"),
            (e, e, False, x, x, "", "Zero Length segment inside FabBox"),
            (g, g, False, x, x, "", "Zero Length segment at maximum"),
            (i, i, False, x, x, "", "Zero Length segment above maximum"),
        )
        errors: int = 0
        index: int
        for index, test in enumerate(tests):
            error: str = check(test)
            if error:
                print(f"Test[{index}]: {error}")
        assert not errors, f"{errors} intersect occurred"

    @staticmethod
    def _unit_tests() -> None:
        """Perform FabBox unit tests."""
        # Initial tests:
        box: FabBox = FabBox()
        assert isinstance(box, FabBox)
        bound_box: BoundBox = BoundBox(-1.0, -2.0, -3.0, 1.0, 2.0, 3.0)
        assert isinstance(bound_box, BoundBox)

        # FabNode._intersect_unit_tests()

        # FreeCAD.BoundBox.__eq__() appears to only compare ids for equality.
        # Thus, it is necessary to test that each value is equal by hand.
        box.enclose((bound_box,))
        assert box.BB.XMin == bound_box.XMin
        assert box.BB.YMin == bound_box.YMin
        assert box.BB.ZMin == bound_box.ZMin
        assert box.BB.XMax == bound_box.XMax
        assert box.BB.YMax == bound_box.YMax
        assert box.BB.ZMax == bound_box.ZMax

        assert box.XMin == bound_box.XMin
        assert box.YMin == bound_box.YMin
        assert box.ZMin == bound_box.ZMin
        assert box.XMax == bound_box.XMax
        assert box.YMax == bound_box.YMax
        assert box.ZMax == bound_box.ZMax

        def check(vector: Vector, x: float, y: float, z: float) -> bool:
            assert vector.x == x, f"{vector.x} != {x}"
            assert vector.y == y, f"{vector.y} != {y}"
            assert vector.z == z, f"{vector.z} != {z}"
            return vector.x == x and vector.y == y and vector.z == z

        # Do 6 faces:
        assert check(box.E, 1, 0, 0), "E"
        assert check(box.W, -1, 0, 0), "W"
        assert check(box.N, 0, 2, 0), "N"
        assert check(box.S, 0, -2, 0), "S"
        assert check(box.T, 0, 0, 3), "T"
        assert check(box.B, 0, 0, -3), "B"

        # Do the 12 edges:
        assert check(box.BE, 1, 0, -3), "BE"
        assert check(box.BN, 0, 2, -3), "BN"
        assert check(box.BS, 0, -2, -3), "BS"
        assert check(box.BW, -1, 0, -3), "BW"
        assert check(box.NE, 1, 2, 0), "NE"
        assert check(box.NW, -1, 2, 0), "NW"
        assert check(box.SE, 1, -2, 0), "SE"
        assert check(box.SW, -1, -2, 0), "SW"
        assert check(box.TE, 1, 0, 3), "TE"
        assert check(box.TN, 0, 2, 3), "TN"
        assert check(box.TS, 0, -2, 3), "TS"
        assert check(box.TW, -1, 0, 3), "TW"

        # Do the 8 corners:
        assert check(box.BNE, 1, 2, -3), "BNE"
        assert check(box.BNW, -1, 2, -3), "BNW"
        assert check(box.BSE, 1, -2, -3), "BSE"
        assert check(box.BSW, -1, -2, -3), "BSW"
        assert check(box.TNE, 1, 2, 3), "TNE"
        assert check(box.TNW, -1, 2, 3), "TNW"
        assert check(box.TSE, 1, -2, 3), "TSE"
        assert check(box.TSW, -1, -2, 3), "TSW"

        # Do the miscellaneous attributes:
        assert check(box.C, 0, 0, 0), "C"
        assert isinstance(box.BB, BoundBox), "BB error"
        assert check(box.BB.Center, 0, 0, 0), "BB"
        assert box.C == box.BB.Center, "C != Center"
        assert box.DX == 2.0, "DX"
        assert box.DY == 4.0, "DY"
        assert box.DZ == 6.0, "DZ"
        assert check(box.DB, 0, 0, -3), "DB"
        assert check(box.DE, 1, 0, 0), "DE"
        assert check(box.DN, 0, 2, 0), "DN"
        assert check(box.DS, 0, -2, 0), "DS"
        assert check(box.DT, 0, 0, 3), "DT"
        assert check(box.DW, -1, 0, 0), "DW"

        # Test FabBox() contructors:
        tne: Vector = Vector(1, 2, 3)
        bsw: Vector = Vector(-1, -2, -3)
        new_box: FabBox = FabBox()
        new_box.enclose((tne, bsw))
        assert f"{new_box.BB}" == f"{box.BB}"
        next_box: FabBox = FabBox()
        next_box.enclose((bound_box, new_box))
        assert next_box.TNE == tne and next_box.BSW == bsw

        # Do some error checking:
        try:
            box1 = FabBox()
            box1.enclose(())
            assert False
        except RuntimeError as runtime_error:
            want1 = "Bounds sequence is empty"
            assert str(runtime_error) == want1, str(runtime_error)
        try:
            box2 = FabBox()
            box2.enclose(cast(List, 123))  # Force invalid argument type.
            assert False
        except RuntimeError as runtime_error:
            want2 = "123 is <class 'int'>, not List/Tuple"
            assert str(runtime_error) == want2, str(runtime_error)
        try:
            box3 = FabBox()
            box3.enclose([cast(Vector, 123)],)  # Force invalid corner type
            assert False
        except RuntimeError as runtime_error:
            want3 = "123 is <class 'int'>, not Vector/BoundBox/FabBox"
            assert str(runtime_error) == want3, str(runtime_error)

        # Do the intersect unit tests:
        FabBox._intersect_unit_tests()


@dataclass
# FabNode:
class FabNode(FabBox):
    """FabNode: Represents one node in the FabNode tree.

    Inherited Attributes:
    * All of the FabBox attributes.

    Attributes:
    * *Label* (str): The FabNode name.
    * *Up* (FabNode): The FabNode parent.
    * *FullPath* (str):  The FabNode full path from the root.  (Filled in)
    * *Tracing* (str):
      A non-empty indentation string when tracing is enabled.
      This field is recursively set when *set_tracing*() is explicitly set.

    """

    _Label: str
    _Parent: "FabNode" = field(repr=False)  # Property is named Up, not Parent.
    _FullPath: str = field(init=False, repr=False)
    _Tracing: str = field(init=False, repr=False)
    _Children: "OrderedDict[str, FabNode]" = field(init=False, repr=False)
    # The next fields are private and are not user accessible via property accessors:
    _Project: "FabNode" = field(init=False, repr=False)
    _AppObject: Any = field(init=False, repr=False)
    _GuiObject: Any = field(init=False, repr=False)

    # FabNode.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabNode."""
        # print(f"=>FabNode.__post_init__(): {self._Label=}")
        super().__post_init__()
        if not FabNode._is_valid_name(self._Label):
            raise RuntimeError(
                f"FabNode.__post_init__({self._Label}) is not "
                "alphanumeric/underscore that starts with a letter")    # pragma: no unit test

        # Initialize the remaining fields to bogus values that get updated by the _setup() method.
        self._Children = OrderedDict()
        self._FullPath = "??"
        self._AppObject = None
        self._GuiObject = None

        parent: "FabNode" = self._Parent
        name: str = self._Label
        # assert child_name.is_valid()
        self._Tracing = ""
        if parent:
            parent_full_path = parent._FullPath
            # Since the root node has no name, we need avoid produce a name like (".XXX"):
            self._FullPath = f"{parent_full_path}).{name}" if parent_full_path else name
            self._Parent = parent
            self._Project = self._Parent._Project
            # assert isinstance(self._Project, Project)  # Enable this check later.

            # Disallow duplicate children names in *parent*:
            parent_children: "OrderedDict[str, FabNode]" = parent._Children
            if name in parent_children:
                raise RuntimeError(
                    f"FabNode.__post_init__({self._Label}) is already a child of {parent._Label}")
            parent_children[name] = self

            # Keep a list if *all_node* in the same order that all FabNode's are created.
            root: "FabNode" = self._Project
            assert hasattr(root, "_AllNodes")  # Only a valid Root has this attribute:
            all_nodes: Tuple["FabNode"] = getattr(root, "_AllNodes")
            setattr(root, "_AllNodes", all_nodes + (self,))

            # Add another level in tracing indentation if tracing is enabled:
            if parent._Tracing:
                self._Tracing = parent._Tracing + " "  # pragma: no unit test
        else:
            # This is the top level project node and it is very special.
            # This is done by providing `cast(Node, None)` as the Parent in Project.new() method.
            self._FullPath = ""
            self._Parent = self
            self._Project = self

        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}<=>FabNode({self._Label}).__post_init__()")

    # FabNode.AppObject():
    @property
    def AppObject(self) -> Any:
        """Return FreeCAD Application Object for FabNode."""
        if self._AppObject is None:
            raise RuntimeError(f"FabNode({self._Label}).AppObject(): No AppObject has been set.")
        return self._AppObject

    # FabNode.Children():
    @property
    def Children(self) -> Tuple["FabNode", ...]:
        """Return the FabNode Children."""
        return tuple(self._Children.values())

    # FabNode.GuiObject():
    @property
    def GuiObject(self) -> Any:
        """Return FreeCAD Gui Object for FabNode."""
        if self._GuiObject is None:
            raise RuntimeError(f"FabNode({self._Label}).GuiObject(): No GuiObject has been set.")
        return self._GuiObject

    # FabNode.FullPath():
    @property
    def FullPath(self) -> str:
        """Return the FabNode full path."""
        return self._FullPath

    # FabNode.Label():
    @property
    def Label(self) -> str:
        """Return the FabNode name."""
        return self._Label

    @property
    def Project(self) -> "FabNode":
        """Return FabNode tree project root."""
        return self._Project

    # FabNode.Tracing():
    @property
    def Tracing(self) -> str:
        """Return the FabNode tracing indentation string."""
        return self._Tracing

    @property
    def Up(self) -> "FabNode":
        """Return the FabNode parent."""
        return self._Parent

    # FabNode.get_errors():
    def get_errors(self) -> List[str]:
        """Return FabNode errors list.

        This method is only implemented by the FabProject class.
        """
        raise RuntimeError(f"FabNode.get_errors({self._Label}).get_errors(): not implemented")
        return []  # Make linters happy.

    # FabNode.error():
    def error(self, error_message: str) -> None:
        """Record and error message with FabNode root."""
        self._Project.get_errors().append(error_message)

    # FabNode.is_project():
    def is_project(self) -> bool:
        """Return True if FabNode is a FabProject."""
        return False  # FabProject class returns True.

    # FabNode.is_document():
    def is_document(self) -> bool:
        """Return True if FabNode is a FabProject."""
        return False  # FabProject class returns True.

    # FabNode.is_group():
    def is_group(self) -> bool:
        """Return True if FabNode is a FabGroup."""
        return False  # FabGroup class returns True.

    # FabNode.is_assembly():
    def is_assembly(self) -> bool:
        """Return True if FabNode is a FabAssembly."""
        return False  # FabAssembly class returns True.

    # FabNode.is_solid():
    def is_solid(self) -> bool:
        """Return True if FabNode is a FabAssembly."""
        return False  # FabSolid class returns True.

    # FabNode.pre_produce():
    def pre_produce(self) -> None:
        """Perform FabNode pre produce operations."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}<=>FabNode({self._Label}).pre_produce()=>()")

    # FabNode.produce():
    def produce(self) -> None:
        """Empty FabNode produce method to be over-ridden."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}<=>FabNode({self._Label}).produce()=>()")

    # FabNode.post_produce1():
    def post_produce1(self) -> None:
        """Do FabNode phase 1 post production."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}<=>FabNode({self._Label}).produce1()=>()")

    # FabNode.post_produce2():
    def post_produce2(self) -> None:
        """Do FabNode phase 2 post production."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}<=>FabNode({self._Label}).post_produce2()=>()")

    # FabNode.get_parent_document():
    def get_parent_document(self, tracing: str = "") -> "FabNode":
        if tracing:
            print(f"{tracing}=>FabNode({self._Label}).get_gui_document()")

        # Search up the document tree to find the FabDocument:
        node: FabNode = self
        while not node.is_document() and not node.is_project():
            node = node._Parent
            if tracing:
                print(f"{tracing}{node=}")
        assert node.is_document()
        if tracing:
            print(f"{tracing}<=FabNode({self._Label}).get_gui_document()=>{node}")
        return node

    # FabNode.set_app_object_only():
    def set_app_object_only(self, app_object: Any) -> None:
        """Set FabNode AppObject only."""
        if self._AppObject:
            raise RuntimeError(f"FabNode.set_object({self._Label}): App Object is already set.")
        if app_object is None:
            raise RuntimeError(f"FabNode.set_object({self._Label}): App Object is None.")
        self._AppObject = app_object

    # FabNode.set_gui_object_only():
    def set_gui_object_only(self, gui_object: Any) -> None:
        """Set FabNode GuiObject only."""
        if self._GuiObject:
            raise RuntimeError(f"FabNode.set_object({self._Label}): Gui Object is already set.")
        if gui_object is None:
            raise RuntimeError(f"FabNode.set_object({self._Label}): Gui Object is None.")
        self._GuiObject = gui_object

    # FabNode.set_object():
    def set_object(self, app_object: Any) -> None:
        """Set both AppObject and GuiObject in FabNode."""
        self.set_app_object_only(app_object)
        if USE_FREECAD and App.GuiUp:
            # Search up the document tree to find the FabDocument:
            search_node: FabNode = self
            while not search_node.is_document() and not search_node.is_project():
                search_node = search_node._Parent

            app_document: Any = search_node._AppObject
            # if not isinstance(app_document, App.Document):
            if not hasattr(app_document, "FileName"):  # Only App document has FileName
                raise RuntimeError(
                    f"FabNode.set_object({self._Label}): No App.Document {app_document}")

            gui_document: Any = Gui.getDocument(app_document.Name)
            # if not isinstance(gui_document, Gui.Document):
            #     raise RuntimeError(
            #         f"FabNode.set_object({self._Label}): No Gui.Document {app_document}")

            self._GuiObject: Any = gui_document.getObject(app_object.Name)

    # FabNode.set_tracing():
    def set_tracing(self, tracing: str):
        """Set the FabNode indentation tracing level.

        This typically done, by adding this call immediately after calling super().__post_init__().

             @dataclass
             class MySubClass(Node):   # Or some class descended from Node*.
                '''MySubClass doc string.'''

                super().__post_init__()
                self.set_tracing(" ")  # Set the tracing here.
                # All children nodes will that are added, will have tracing set as well.

        """
        self._Tracing = tracing
        print(f"{tracing}<=>FabNode({self._Label}).set_tracing('{tracing}')")

    # FabNode.probe()
    def probe(self, label: str) -> None:
        """Perform a probe operation.

        This method can be overriden and called to perform debug probes.
        """
        root: FabNode = self._Project
        if not hasattr(root, "probe"):
            assert False, dir(root)
        root.probe(label)

    @staticmethod
    # FabNode._is_valid_name():
    def _is_valid_name(name: str) -> bool:
        """Return whether a name is valid or not."""
        no_underscores: str = name.replace("_", "")
        return len(no_underscores) >= 1 and no_underscores.isalnum() and no_underscores[0].isalpha()


if __name__ == "__main__":
    # _unit_tests("")
    if USE_FREECAD:
        FabBox._unit_tests()

