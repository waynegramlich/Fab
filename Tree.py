#!/usr/bin/env python3
"""
Tree: Fab tree management.

The Tree package provides a tree of nodes that mostly corresponds to a FreeCAD tree
as shown in the FreeCAD model view.

The base class is FabNode organized as follows:
* FabNode: Tree node base class (can be either a "leaf" or "interior node.)
(This needs to be expanded.)

The Tree enforces the following constraints:
* Each FabNode name must be compatible with a Python variable name
  (i.e. upper/lower letters, digits, and underscores with the character being a letter.)
* All of the children of a FabNode must have distinct names.
* A node may occur only once in the Tree (i.e. DAG = Direct Acyclic Graph.)
* The FabRoot must be named 'Root'.

Each FabNode has a *FullPath* property which is string that contains the FabNode Names
from the FabRoot downwards separated by a '.'.  The "Root." is skipped because it is redundant.
Each FabNode has an Parent attribute that specifies the parent FabNode

FabNode implement

The FabNode base class implements three recursive methods:

* configure() -> Tuple[str, ...]:
  Recursively propagate configuration values during the configuration phase.
  All configured values are returns a tuple of strings of the form "FULL_NAME:PROPERTY_NAME:VALUE".
* check(context) -> Tuple[str, ...]:
  Recursively checks for errors during the check phase and returns a tuple of error strings.
* build(context) -> Tuple[str, ...]:
  Recursively used to build the model and generate any production files (CNC, STL, DWG, etc.)
  Any errors and warnings are returned as a tuple of strings.

The *check* and *build* methods take an *context* argument which is a dictionarly (Dict[str, Any].)
Values are inserted to communication information from a high node to the lower tree nodes.
The higher level node stuffs a value into the dictionary and lower values can read them back.
Any values stuffed into a lower level are not accessed by the upper level because by convention
each recursion step makes a shallow dictionary copy of the context before passing down to the
next level down.  This is shown below:

     # Iterate across children FabNode's:
     for child in self.Children:
         child.visit(context.copy(), ...)

There are currently 1 "invisible" and 3 user visible recursion phases:
* Setup Phase:
  This phase does consistency checking and fills in values such as FullPath.
  There are no user hooks in this phase.
* Configuration Phase:
  The configuration phase is where constraints get propagated between FabNode's.  Each
  FabNode recomputes its configuration value using a method called *configure*.  This method
  can do this by read other values from other FabNode's elsewhere in FabRoot tree then
  computing new values.  This is done repeatably until no more configuration values change or
  until it is pretty clear that there is cyclic dependency will not converge.  When convergence
  fails, the list of configuration values that did not stabilize are presented.  If there are no
  convergence issues, the next phase occurs.
* Check Phase:
  The check phase recursively performs sanity checking for each FabNode in the tree.
  The result is a list of error messages.  If the are no errors, the next phase occurs.
* Build Phase:
  The build phase recursively performs the build operations.  This includes generating
  the FreeCAD solids/assemblies and the associated output files.

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

import sys
sys.path.append(".")
import Embed
Embed.setup()

from dataclasses import dataclass, field
from typing import Any, cast, Dict, List, Optional, Sequence, Set, Tuple, Union
from FreeCAD import BoundBox, Placement, Vector  # type: ignore


# FabBox:
class FabBox(object):
    """FabBox: X/Y/Z Axis Aligned Cubiod.

    An FabBox is represents a cuboid (i.e. a rectangular parallelpiped, or right prism) where
    the edges are aligned with the X, Y, and Z axes.  This is basically equivalent to the FreeCAD
    BoundBox object, but with way more attributes to access various points on the cuboid surface.

    The basic attribute nominclature is based on the compass points North (+Y), South (-Y),
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
    def enclose(self, bounds: Sequence[Union[Vector, BoundBox, "FabBox"]]) -> None:
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
            elif isinstance(bound, BoundBox):
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
    def BB(self) -> BoundBox:
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
    def reorient(self, placement: Placement) -> "FabBox":
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

    @staticmethod
    def _unit_tests() -> None:
        """Perform FabBox unit tests."""
        # Initial tests:
        box: FabBox = FabBox()
        assert isinstance(box, FabBox)
        bound_box: BoundBox = BoundBox(-1.0, -2.0, -3.0, 1.0, 2.0, 3.0)
        assert isinstance(bound_box, BoundBox)

        # FreeCAD.BoundBox.__eq__() appears to only compare ids for equality.
        # Thus, it is necessary to test that each value is equal by hand.
        box.enclose((bound_box,))
        assert box.BB.XMin == bound_box.XMin
        assert box.BB.YMin == bound_box.YMin
        assert box.BB.ZMin == bound_box.ZMin
        assert box.BB.XMax == bound_box.XMax
        assert box.BB.YMax == bound_box.YMax
        assert box.BB.ZMax == bound_box.ZMax

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


@dataclass
# FabNode:
class FabNode(FabBox):
    """FabNode: Represents one node in the tree.

    Attributes:
    * *Name* (str): The FabNode name.
    * *Parent* (FabNode): The FabNode parent.  (Filled in)
    * *FullPath* (str):  The FabNode full path.  (Filled in)
    * *AttributeNames ([Tuple[str, ...]):
       Attribute names to track during configuration.  (Default: () ).
       This field is set in the user's *configure*() method.

    """

    Name: str
    Parent: "FabNode" = field(init=False, repr=False)
    FullPath: str = field(init=False)
    AttributeNames: Tuple[str, ...] = field(init=False, repr=False, default=())
    Children: Tuple["FabNode", ...] = field(init=False, repr=False, default=())

    # FabNode.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabNode."""
        # print(f"=>FabNode.__post_init__(): {self.Name=}")
        super().__post_init__()
        if not FabNode._is_valid_name(self.Name):
            raise ValueError(
                f"FabNode name '{self.Name}' is not alphanumeric/underscore "
                "that starts with a letter")

        # Initialize the remaining fields to bogus values that get updated by the _setup() method.
        self.FullPath = "??"
        self.Parent = self
        # print(f"<=FabNode.__post_init__()")

    # FabNode.check():
    def check(self) -> Tuple[str, ...]:
        """Check FabNode for errors."""
        return ()

    # FabNode.configure():
    def configure(self, tracing: str = "") -> None:
        """Configure FabNode."""
        pass

    # FabNode.configurations_append():
    def configurations_append(self, configurations: List[str], tracing: str = "") -> None:
        """Append specified attributes to configurations list."""
        if tracing:
            print(f"{tracing}=>FabNode.configurations_append('{self.Name}', *")
        attribute_name: str
        for attribute_name in self.AttributeNames:
            if tracing:
                print(f"{tracing}Process '{attribute_name}'")
            if not isinstance(attribute_name, str):
                raise RuntimeError(
                    f"{self.FullPath}: Attribute name is {type(attribute_name)}, not str")
            if not hasattr(self, attribute_name):
                raise RuntimeError(
                    f"{self.FullPath}: Attribute '{attribute_name}' is not present.")
            value: Any = getattr(self, attribute_name)
            configurations.append(f"{self.FullPath}.{attribute_name}:{value}")
        if tracing:
            print(f"{tracing}<=FabNode.configurations_append('{self.Name}', *)=>"
                  f"|{len(configurations)}|")

    # FabNode.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Produce FabNode."""
        return ()

    @staticmethod
    # FabNode._is_valid_name():
    def _is_valid_name(name: str) -> bool:
        """Return whether a name is valid or not."""
        no_underscores: str = name.replace("_", "")
        return no_underscores.isalnum() and no_underscores[0].isalpha()

    # FabNode._setup():
    def _setup(self, dag_table: Dict[int, "FabNode"],
               parent: "FabNode", root: "FabNode", tracing: str = "") -> None:
        """Set up the FabNode and its children."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabNode._setup('{self.Name}', '{parent.Name}', *)")

        # Setup *FullPath* and *Parent*:
        if self is root:
            # *root* is specical:
            self.FullPath = ""
            self.Parent = root
            self.Name = "Root"
        else:
            self.FullPath = self.Name if parent is root else f"{parent.FullPath}.{self.Name}"
            self.Parent = parent

        # Make sure that the FabNode tree is a DAG (Directed Acyclic Graph) with no duplicates.
        node_id: int = id(self)
        if node_id in dag_table:
            raise RuntimeError(f"{self.FullPath} is the same as {dag_table[node_id].FullPath}")
        dag_table[node_id] = self

        # children_nodes: List[FabNode] = []
        # trackable_names: List[str] = []
        # for name in self.__dict__.keys():
        #     if tracing:
        #         print(f"{tracing}{self.FullPath}:{name}")
        #     if not name[0].isupper():
        #         continue
        #     if name == "Parent":
        #         continue
        #     if hasattr(self, name):
        #         attribute: Any = getattr(self, name)
        #         if isinstance(attribute, FabNode):
        #             if tracing:
        #                 print(f"{tracing}Is fabNode")
        #             children_nodes.append(attribute)
        #         elif isinstance(attribute, (list, tuple)):
        #             if tracing:
        #                 print(f"{tracing}is sequence {type(attribute)=} {len(attribute)=}")
        #             element: Any
        #             index: int
        #             for index, element in enumerate(attribute):
        #                 if tracing:
        #                     print(f"{tracing}Element[{index}]: {element=}")
        #                 if isinstance(attribute, FabNode):
        #                     if tracing:
        #                         print(f"{tracing}Match: {attribute.Name}")
        #                     children_nodes.append(attribute)
        #         elif isinstance(attribute, (str, int, float, bool, Vector)):
        #             trackable_names.append(name)
        # if tracing and children_nodes:
        #     print(f"{tracing}{children_nodes=}")

        # Recursively setup each *child*:
        child_names: Set[str] = set()
        child: FabNode
        for child in self.Children:
            name = child.Name
            if name in child_names:
                raise RuntimeError("'{name}' occurs more then once in '{self.FullPath}'")
            child_names.add(name)
            child._setup(dag_table, self, root, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=FabNode._setup('{self.Name}', '{parent.Name}', *)")

    # FabNode:
    def __getitem__(self, key: Union[str, Tuple[str, type]]) -> Any:
        """Return value using a relative path with an optional type."""
        tracing: str = ""  # Manually set to debug.
        if tracing:
            print(f"=>FabNode.__get_item__({key})")

        # Perform argument checking:
        path: str
        desired_type: Optional[type] = None
        if isinstance(key, tuple):
            if len(key) != 2:
                raise ValueError(f"FabNode key {key} tuple must be of length 2")
            path = key[0]
            if not isinstance(path, str):
                raise ValueError("FabNode key {path} path is not a string")
            desired_type = key[1]
            if not isinstance(desired_type, type):
                raise ValueError("FabNode desired type {desired_type } is not a type")
        elif isinstance(key, str):
            path = key
        else:
            raise ValueError(f"ModeNode key {key} is neither a string nor a tuple")

        # Move *focus* from *self* by parsing *path*:
        focus: FabNode = self
        size: int = len(path)
        index: int = 0
        while index < size:
            dispatch: str = path[index]
            if tracing:
                print(f"FabNode.__get_item__(): {path[index:]=} {focus=}")
            if dispatch == "^":
                # Move *focus* up:
                focus = focus.Parent
                index += 1
            elif dispatch == ".":
                index += 1
            elif dispatch.isalpha():
                # Extract the Node or Attribute Name:
                dot_index: int = path.find(".", index + 1)
                name: str
                if dot_index > 0:
                    name = path[index:dot_index]
                    index = dot_index
                else:
                    name = path[index:]
                    index = size
                if hasattr(focus, name):
                    focus = getattr(focus, name)
                else:
                    raise ValueError(f"Path '{path}' not able to find '{name}' {dir(focus)=}")
            else:
                raise ValueError(f"Path '{path}' is not properly formatted")
        if desired_type:
            if not isinstance(focus, desired_type):
                raise ValueError(f"Path '{path}' is of type {type(focus)} not {desired_type}")
        if tracing:
            print(f"=>FabNode.__get_item__({key})=>{focus}")
        return focus


# @dataclass
# class MyNode1(FabNode):
#     """MyNode1: First FabNode."""
#
#     A: int = 0
#
#     def configure(self, tracing: str = "") -> None:
#         """Configure MyNode1."""
#         if tracing:
#             print(f"{tracing}=>MyNode1.configure('{self.Name}'")
#         assert isinstance(self.Parent, FabRoot)
#         b: int = cast(int, self[("^MyNode2.B", int)])
#         c: int = cast(int, self[("^MyNode3.C", int)])
#         d: int = cast(int, self[("^MyNode2.MyNode2A.D", int)])
#         e: int = cast(int, self[("^MyNode2.MyNode2B.E", int)])
#         self.AttributeNames = ("A",)
#         self.A = b + c + d + e
#         if tracing:
#             print(f"{tracing}<=MyNode1.configure('{self.Name}')")
#
#
# @dataclass
# class MyNode2(FabNode):
#     """MyNode1: First FabNode."""
#
#     B: int = 0
#
#     def configure(self, tracing: str = "") -> None:
#         """Configure MyNode2."""
#         # next_tracing: str = tracing + " " if tracing else ""
#         if tracing:
#             print(f"{tracing}=>MyNode2.configure('{self.Name}')")
#         c = cast(int, self[("^MyNode3.C", int)])
#         d = cast(int, self[("^MyNode2.MyNode2A.D")])
#         self.AttributeNames = ("B",)
#         self.B = c + d
#         if tracing:
#             print(f"{tracing}<=MyNode2.configure('{self.Name}')")
#
#
# @dataclass
# class MyNode2A(FabNode):
#     """MyNode2A: First sub-node of MyNode2."""
#
#     D: int = 0
#
#     def configure(self, tracing: str = "") -> None:
#         """Configure MyNode2A."""
#         if tracing:
#             print(f"{tracing}=>MyNode2A.configure('{self.Name}')")
#         e = cast(int, self["^MyNode2B.E"])
#         self.AttributeNames = ("D",)
#         self.D = e + 1
#         if tracing:
#             print(f"{tracing}<=MyNode2A.configure('{self.Name}')")
#
#
# @dataclass
# class MyNode2B(FabNode):
#     """MyNode2B: Second sub-node of MyNode2."""
#
#     E: int = 0
#
#     def configure(self, tracing: str = "") -> None:
#         """Configure MyNode2B."""
#         if tracing:
#             print(f"{tracing}=>MyNode2B.configure('{self.Name}')")
#         _ = cast(int, self["^^MyNode3.C"])
#         self.AttributeNames = ("E",)
#         self.E = 1
#         if tracing:
#             print(f"{tracing}<=MyNode2B.configure('{self.Name}')")
#
#
# @dataclass
# class MyNode3(FabNode):
#     """MyNode1: First FabNode."""
#
#     C: int = 1
#
#     def configure(self, tracing: str = "") -> None:
#         """Configure MyNode3."""
#         if tracing:
#             print(f"{tracing}=>MYNode1.configure('{self.Name}')")
#         self.AttributeNames = ("C",)
#         self.C = 1
#         if tracing:
#             print(f"{tracing}<=MYNode2.configure('{self.Name}')")
#
#
# def _unit_tests(tracing: str = "") -> None:
#     """Run Unit tests on FabNode."""
#     if tracing:
#         print(f"{tracing}=>_unit_tests()")
#
#     my_node1: MyNode1 = MyNode1("MyNode1")
#     my_node2a: MyNode2A = MyNode2A("MyNode2A")
#     my_node2b: MyNode2B = MyNode2B("MyNode2B")
#     my_node2: MyNode2 = MyNode2("MyNode2", (my_node2a, my_node2b))
#     my_node3: MyNode3 = MyNode3("MyNode3")
#     root: FabRoot = FabRoot("Root", (my_node1, my_node2, my_node3))
#     assert isinstance(root, FabRoot)
#     assert my_node1.A == 0
#     assert my_node2.B == 0
#     assert my_node2a.D == 0
#     assert my_node2b.E == 0
#     assert my_node3.C == 1
#     assert my_node1.FullPath == "MyNode1", my_node1.FullPath
#     assert my_node2.FullPath == "MyNode2"
#     assert my_node2a.FullPath == "MyNode2.MyNode2A", my_node2a.FullPath
#     assert my_node2b.FullPath == "MyNode2.MyNode2B"
#     assert my_node3.FullPath == "MyNode3"
#     root.configure_constraints(verbosity=1, tracing="")  # tracing=next_tracing)
#
#     if tracing:
#         print(f"{tracing}<=_unit_tests()")


if __name__ == "__main__":
    # _unit_tests("")
    FabBox._unit_tests()
    pass
