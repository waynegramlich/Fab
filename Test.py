#!/usr/bin/env python3
"""Test: Test classes for Fab."""

# <--------------------------------------- 100 characters ---------------------------------------> #

# Python library imports:
from dataclasses import dataclass, field
from typeguard import check_type
from typing import Any, cast, List, Optional, Set, Tuple
from pathlib import Path as PathFile

# CadQuery library imports:
from cadquery import Vector  # type: ignore

# Fab library imports:
from FabGeometries import FabCircle, FabPlane, FabPolygon
from FabJoins import FabFasten, FabJoin
from FabNodes import FabNode  # This should not be needed see cast in BoxSide.produce()
from FabProjects import FabAssembly, FabDocument, FabProject
from FabShops import FabShops
from FabSolids import FabSolid, FabMount
from FabUtilities import FabMaterial


# BoxSide:
@dataclass
class BoxSide(FabSolid):
    """A Box side.

    Inherited Constructor Attributes:
    * *Name* (str): Box name.
    * *Parent* (*FabNode*): The parent container.
    * *Material* (FabMaterial): The Material to use.
    * *Color* (str): The color to use.

    Additional Constructor Attributes:
    * *Contact* (Vector):
       The center "top" of the side.  (Default: (0, 0, 0))
    * *Normal* (Vector):
      The normal of the side (away from box center). (Default: (0, 0, 1))
    * *HalfLength* (Vector):
      A vector of half the length in the length direction. (Default: (1, 0, 0))
    * *HalfWidth* (Vector):
      A vector of half the width in the width direction.  (Default: (0, 1, 0))
    * *Depth* (float):
      Depth of side (opposite direction of *normal*.  (Default: 5.0)
    * *Contour* (bool):
      Force the side contour to be milled out. (Default: False)
    * *Drill* (bool):
      Force holes to be drilled. (Default: True)

    Constructor:
    The constructor is largely done using keywords
    * BoxSide("Name", Parent, Material=..., Color=..., Contact=..., Normal=...,
              HalfLength=..., HalfWidth=..., Depth=..., Contour=..., Drill=...)
    """
    Contact: Vector = Vector()
    Normal: Vector = Vector(0, 0, 1)
    HalfLength: Vector = Vector(1, 0, 0)
    HalfWidth: Vector = Vector(0, 1, 0)
    Depth: float = 5.0
    Contour: bool = False
    Drill: bool = True
    Screws: List[FabJoin] = field(init=False, repr=False)

    # BoxSide.__post_init__():
    def __post_init__(self) -> None:
        """Initialize Box Side."""
        super().__post_init__()
        check_type("BoxSide.Contact", self.Contact, Vector)
        check_type("BoxSide.Normal", self.Normal, Vector)
        check_type("BoxSide.HalfLength", self.HalfLength, Vector)
        check_type("BoxSide.HalfWidth", self.HalfWidth, Vector)
        check_type("BoxSide.Depth", self.Depth, float)
        check_type("BoxSide.Contour", self.Contour, bool)
        check_type("BoxSide.Drill", self.Drill, bool)

        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>BoxSide({self.Label}).__post_init__()")
            print(f"{tracing}{self.Contact=}")
            print(f"{tracing}{self.Normal=}")
            print(f"{tracing}<=BoxSide({self.Label}).__post_init__()")
        self.Screws = []

    # BoxSide.produce():
    def produce(self) -> None:
        """Produce BoxSide."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>BoxSide({self.Label}).produce()")
        box = cast(Box, self.Up)
        assert isinstance(box, Box)  # Redundant
        fasten: FabFasten = box.Fasten
        screws: List[FabJoin] = self.Screws

        name: str = self.Label
        contact: Vector = self.Contact
        copy: Vector = Vector()
        depth: float = self.Depth

        normal: Vector = self.Normal
        normal_direction: Vector = normal / normal.Length

        half_length: Vector = self.HalfLength
        length: float = half_length.Length
        length_direction: Vector = self.HalfLength / length

        half_width: Vector = self.HalfWidth
        width: float = half_width.Length
        width_direction: Vector = half_width / width

        # Extrude the side:
        radius: float = 0.5
        all_screws: Tuple[FabJoin, ...] = box.get_all_screws()
        plane: FabPlane = FabPlane(contact, self.Normal)
        orient_start: Vector = self.Contact
        orient_end: Vector = contact + (half_length if length > width else half_width)

        mount: FabMount = self.mount(f"{name}FaceMount", plane, depth, orient_start, orient_end)
        corners: Tuple[Vector, ...] = (
            (contact + half_length + half_width, radius),
            (contact + half_length - half_width, radius),
            (contact - half_length - half_width, radius),
            (contact - half_length + half_width, radius),
        )

        polygon: FabPolygon = FabPolygon(plane, corners)
        mount.extrude(f"{name}Extrude", polygon, depth, debug=True, contour=self.Contour)

        # Create all of the *screws*:
        del screws[:]
        dlength: float
        dwidth: float
        if name in ("Top", "Bottom", "North", "South"):
            length_adjust = 0.5 * depth if name in ("Top", "Bottom") else 0.5 * depth
            width_adjust = 0.5 * depth if name in ("Top", "Bottom") else 3.0 * depth
            for dlength in (length - length_adjust, -length + length_adjust):
                for dwidth in (width - width_adjust, -width + width_adjust):
                    start: Vector = (
                        contact + dlength * length_direction + dwidth * width_direction)
                    end: Vector = start - (3 * depth) * normal_direction
                    screw: FabJoin = FabJoin(f"{name}Join{len(screws)}", fasten, start, end)
                    screws.append(screw)

        # Create *edge_mounts*:
        edge_mounts: List[FabMount] = []
        edge_index: int = 0
        direction: Vector
        for direction in (self.HalfLength, -self.HalfLength, self.HalfWidth, -self.HalfWidth):
            edge_normal: Vector = direction / direction.Length
            random_orient: Vector = (self.Normal + copy).cross(direction + copy)
            plane = FabPlane(contact + direction, edge_normal)
            edge_mount: FabMount = self.mount(
                f"{name}Edge{edge_index}Mount", plane, depth, contact, contact + random_orient)
            edge_mounts.append(edge_mount)
            edge_index += 1
        if self.Drill:
            self.drill_joins("Screws", all_screws)

        if tracing:
            print(f"{tracing}<=BoxSide({self.Label}).produce()")


# Box:
@dataclass
class Box(FabAssembly):
    """Fabricate  a box.

    Builds a box given a length, width, height, material, thickness and center point"

    Inherited Constructor Attributes:
    * *Name* (str): Box name.
    * *Parent* (*FabNode*): The parent container.

    Additional Constructor Attributes:
    * *Length* (float): length in X direction in millimeters.x
    * *Width* (float): width in Y direction in millimeters.
    * *Height* (float): height in Z direction in millimeters.
    * *Thickness* (float): Material thickness in millimeters.
    * *Material* (FabMaterial): Material to use.
    * *Center* (Vector): Center of Box.

    Produced Attributes:
    * *Top* (FabSolid): The box top solid.
    * *Bottom* (FabSolid): The box bottom solid.
    * *North* (FabSolid): The box north solid.
    * *South* (FabSolid): The box south solid.
    * *East* (FabSolid): The box east solid.
    * *West* (FabSolid): The box west solid.
    * *Fasten* (FabFasten): The screw template to use.

    """

    Length: float
    Width: float
    Height: float
    Thickness: float
    Material: FabMaterial = FabMaterial(("Plasitic", "HDPE"), "white")
    Center: Vector = Vector()
    Enabled: str = field(init=False, repr=False)
    Top: Optional[BoxSide] = field(init=False, repr=False)
    Bottom: Optional[BoxSide] = field(init=False, repr=False)
    North: Optional[BoxSide] = field(init=False, repr=False)
    South: Optional[BoxSide] = field(init=False, repr=False)
    East: Optional[BoxSide] = field(init=False, repr=False)
    West: Optional[BoxSide] = field(init=False, repr=False)
    Fasten: FabFasten = field(init=False, repr=False)

    # Box.__post_init__():
    def __post_init__(self) -> None:
        """Construct the the Box."""
        super().__post_init__()
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>Box({self.Label}).__post_init__()")

        depth: float = self.Thickness
        material: FabMaterial = self.Material
        x_axis: Vector = Vector(1, 0, 0)
        y_axis: Vector = Vector(0, 1, 0)
        z_axis: Vector = Vector(0, 0, 1)

        enabled: str = "TBNSEW"
        self.Enabled = enabled
        self.Top = (None if "T" not in enabled else
                    BoxSide("Top", self, Normal=z_axis,
                            Depth=depth, Material=material, Color="lime", Contour=True))
        self.Bottom = (None if "B" not in enabled else
                       BoxSide("Bottom", self, Normal=-z_axis,
                               Depth=depth, Material=material, Color="green", Contour=True))
        self.North = (None if "N" not in enabled else
                      BoxSide("North", self, Normal=y_axis,
                              Depth=depth, Material=material, Color="orange", Contour=False))
        self.South = (None if "S" not in enabled else
                      BoxSide("South", self, Normal=-y_axis,
                              Depth=depth, Material=material, Color="yellow", Contour=False))
        self.East = (None if "E" not in enabled else
                     BoxSide("East", self, Normal=x_axis,
                             Depth=depth, Material=material, Color="pink", Contour=False))
        self.West = (None if "W" not in enabled else
                     BoxSide("West", self, Normal=-x_axis,
                             Depth=depth, Material=material, Color="cyan", Contour=False))
        # self.Fasten = FabFasten("BoxFasten", "M3x.5", ())  # No options yet.
        self.Fasten = FabFasten("BoxFasten", "#4-40", ())  # No options yet.

        if tracing:
            print(f"{tracing}<=Box({self.Label}).__post_init__()")

    # Box.produce():
    def produce(self) -> None:
        """Produce the Box."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>Box({self.Label}.produce())")

        # Extract basic dimensions and associated constants:
        # material: str = self.Material
        center: Vector = self.Center
        dx: float = self.Length
        dy: float = self.Width
        dz: float = self.Height
        dw: float = self.Thickness
        dx2: float = dx / 2.0
        dy2: float = dy / 2.0
        dz2: float = dz / 2.0
        # dw2: float = dw / 2.0
        # sd: float = 3.0 * dw  # Screw Depth
        # corner_radius: float = 3.0

        dxv: Vector = Vector(dx2, 0, 0)
        dyv: Vector = Vector(0, dy2, 0)
        dzv: Vector = Vector(0, 0, dz2)

        # dwxv: Vector = Vector(dw, 0, 0)
        dwyv: Vector = Vector(0, dw, 0)
        dwzv: Vector = Vector(0, 0, dw)

        top: Optional[BoxSide] = self.Top
        if top is not None:
            top.Contact = center + dzv
            top.HalfLength = dyv
            top.HalfWidth = dxv

        bottom: Optional[BoxSide] = self.Bottom
        if bottom is not None:
            bottom.Contact = center - dzv
            bottom.HalfLength = dyv
            bottom.HalfWidth = dxv

        north: Optional[BoxSide] = self.North
        if north is not None:
            north.Contact = center + dyv
            north.HalfLength = dxv
            north.HalfWidth = dzv - dwzv

        south: Optional[BoxSide] = self.South
        if south is not None:
            south.Contact = center - dyv
            south.HalfLength = dxv
            south.HalfWidth = dzv - dwzv

        east: Optional[BoxSide] = self.East
        if east is not None:
            east.Contact = center + dxv
            east.HalfLength = dyv - dwyv
            east.HalfWidth = dzv - dwzv

        west: Optional[BoxSide] = self.West
        if west is not None:
            west.Contact = center - dxv
            west.HalfLength = dyv - dwyv
            west.HalfWidth = dzv - dwzv

        if tracing:
            print(f"{tracing}<=Box({self.Label}.produce())")

    # Box.get_all_screws():
    def get_all_screws(self) -> Tuple[FabJoin, ...]:
        """Return all Box screws."""
        screws: List[FabJoin] = []
        if self.Top is not None:
            screws.extend(self.Top.Screws)
        if self.Bottom is not None:
            screws.extend(self.Bottom.Screws)
        if self.North is not None:
            screws.extend(self.North.Screws)
        if self.South is not None:
            screws.extend(self.South.Screws)
        return tuple(screws)


# TestSolid:
@dataclass
class TestSolid(FabSolid):
    """TestSolid: A test solid to exercise FabSolid code."""

    I4_40Fasten: FabFasten = field(init=False, repr=False)
    M8_1_25Fasten: FabFasten = field(init=False, repr=False)
    M10_1_5Fasten: FabFasten = field(init=False, repr=False)
    Screw1: FabJoin = field(init=False, repr=False)

    # TestSolid.__post_init__():
    def __post_init__(self) -> None:
        """Initialize TestSolid."""
        super().__post_init__()
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>TestSolid({self.Label}).__post_init__()")
        self.I4_40Fasten = FabFasten("TestSolidImperialFasten", "#4-40", ())  # No options yet.
        self.M8_1_25Fasten = FabFasten("TestSolidMetricFasten", "M8x1.25", ())  # No options yet.
        self.M10_1_5Fasten = FabFasten("TestSolidMetricFasten", "M10x1.5", ())  # No options yet.
        if tracing:
            print(f"{tracing}<=TestSolid({self.Label}).__post_init__()")

    # TestSolid.produce()
    def produce(self) -> None:
        tracing: str = self.Tracing
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>TestSolid({self.Label}).produce()")

        # Create *top_mount*:
        depth: float = 10.0
        depth2: float = depth / 2.0
        _ = depth2
        top_origin: Vector = Vector(0.0, 0.0, -40.0)
        dt: Vector = self.DT
        de: Vector = self.DE
        top_plane: FabPlane = FabPlane(top_origin, dt)
        top_mount: FabMount = self.mount(
            "Top", top_plane, depth, de, top_origin + de, tracing=tracing)

        wx: float = -40.0
        ex: float = 40.0
        ny: float = 20.0
        sy: float = -60.0

        # Perform the first Extrude:
        z_offset: float = top_origin.z
        extrude_fillet_radius: float = 10.0
        extrude_polygon: FabPolygon = FabPolygon(top_plane, (
            (Vector(wx, sy, z_offset), extrude_fillet_radius),  # SW
            (Vector(ex, sy, z_offset), extrude_fillet_radius),  # SE
            (Vector(ex, ny, z_offset), extrude_fillet_radius),  # NE
            (Vector(wx, ny, z_offset), extrude_fillet_radius),  # NW
        ))

        top_mount.extrude("Extrude", extrude_polygon, depth, debug=False, tracing=next_tracing)
        pocket_fillet_radius: float = 2.5

        # Enable vasious *features*:
        features: Set[str] = {"LPP", "RPP", "RCP", "CCP", "IDH", "MDH", "MDP", "SSH"}

        # features = ("RPP",)  # Down select to specific *features*
        if "LPP" in features:  # Left Polygon Pocket
            left_polygon: FabPolygon = FabPolygon(top_plane, (
                (Vector(-30, -10, z_offset), pocket_fillet_radius),  # SW
                (Vector(-10, -10, z_offset), pocket_fillet_radius),  # SE
                (Vector(-10, 10, z_offset), pocket_fillet_radius),  # NE
                (Vector(-30, 10, z_offset), pocket_fillet_radius),  # NW
            ))
            top_mount.pocket("LeftPocket", left_polygon, depth2, debug=True)

        if "RPP" in features:  # Right Polygon Pocket
            right_pocket: FabPolygon = FabPolygon(top_plane, (
                (Vector(10, -10, z_offset), pocket_fillet_radius),  # SW
                (Vector(30, -10, z_offset), pocket_fillet_radius),  # SE
                (Vector(30, 10, z_offset), pocket_fillet_radius),  # NE
                (Vector(10, 10, z_offset), pocket_fillet_radius),  # NW
            ))
            top_mount.pocket("RightPocket", right_pocket, depth2)

        if "RCP" in features:  # Right Circle Pocket
            right_circle: FabCircle = FabCircle(top_plane, Vector(20, 0, z_offset), 10)
            top_mount.pocket("RightCircle", right_circle, depth, debug=True)

        if "CCP" in features:  # Center Circle Pocket
            center_circle: FabCircle = FabCircle(top_plane, Vector(0, 0, z_offset), 10)
            top_mount.pocket("CenterCircle", center_circle, depth2, debug=True)

        if "IDH" in features:  # Imperial Drill Hole
            imperial_drill_start: Vector = Vector(0.0, -10.0, z_offset)
            imperial_drill_end: Vector = Vector(0.0, -10.0, z_offset - depth)
            self.ScrewIDH: FabJoin = FabJoin("ScrewI", self.I4_40Fasten,
                                             imperial_drill_start, imperial_drill_end)
            top_mount.drill_joins("ScrewIDH", (self.ScrewIDH,), debug=True, tracing=next_tracing)

        if "MDH" in features:  # Metric Drill Hole
            metric_drill_start: Vector = Vector(-20.0, -20.0, z_offset)
            metric_drill_end: Vector = Vector(-20.0, -20.0, z_offset - depth)
            self.ScrewMDH: FabJoin = FabJoin("ScrewMDH", self.M8_1_25Fasten,
                                             metric_drill_start, metric_drill_end)
            top_mount.drill_joins("ScrewMDH", (self.ScrewMDH,), tracing=next_tracing)

        if "MDP" in features:  # Metric Drill Pocket
            # There is no M10x1.5 drill in the example mill.
            metric_pocket_start: Vector = Vector(20.0, -20.0, z_offset)
            metric_pocket_end: Vector = Vector(20.0, -20.0, z_offset - depth)
            self.ScrewMDP: FabJoin = FabJoin("ScrewMDP", self.M10_1_5Fasten,
                                             metric_pocket_start, metric_pocket_end)
            top_mount.drill_joins("ScrewMDP", (self.ScrewMDP,), tracing=next_tracing)

        if "SSH" in features:  # Side Screw Hole:
            north_start: Vector = self.N
            north_end: Vector = self.C
            n: Vector = self.N
            dn: Vector = self.DN
            dy: Vector = self.DY
            north_plane: FabPlane = FabPlane(n, dn)
            north_mount: FabMount = self.mount(
                "NorthX", north_plane, dy, n, n + de, tracing=tracing)
            self.ScrewN: FabJoin = FabJoin("ScrewN", self.I4_40Fasten, north_start, north_end)
            north_mount.drill_joins("ScrewN", (self.ScrewN,), tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=TestSolid({self.Label}).produce()")


# TestAssembly:
@dataclass
class TestAssembly(FabAssembly):
    """TestAssembly: A Class to test an assembly."""

    # Solid: Optional[TestSolid] = field(init=False, repr=False)
    TestSolid: Optional["TestSolid"] = field(init=False, repr=False)
    Box: Optional["Box"] = field(init=False, repr=False)

    # TestAssembly.__post_init__():
    def __post_init__(self):
        """Initialize Test Assembly."""
        super().__post_init__()
        enabled: Set[str] = {"box", "test_solid"}
        material: FabMaterial = FabMaterial(("Plastic", "HDPE"), "red")
        self.Solid = (None if "test_solid" not in enabled else
                      TestSolid("TestSolid", self, material, "red"))
        center: Vector = Vector(0, 0, -100.0)
        self.Box = (None if "box" not in enabled else
                    Box("TestBox", self, 200.0, 150.0, 75.0, 6.0, material, center))


# TestDocument:
@dataclass
class TestDocument(FabDocument):
    """A Test file."""

    Assembly: TestAssembly = field(init=False, repr=False, default=cast(TestAssembly, None))

    # TestDocument.__post_init__():
    def __post_init__(self) -> None:
        """Initialize TestDocument."""
        super().__post_init__()
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>TestDocument({self.Label}).__post_init__()")
        self.Assembly = TestAssembly("TestAssembly", self)
        if tracing:
            print(f"{tracing}<=TestDocument({self.Label}).__post_init__()")


# TestProject:
@dataclass
class TestProject(FabProject):
    """A Test Project."""

    Document: FabDocument = field(init=False, repr=True)

    # TestProject.__post_init__():
    def __post_init__(self) -> None:
        """Initialize TestProject."""
        super().__post_init__()
        self.set_tracing(" ")
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>TestProject({self.Label}).__post_init__()")

        self.Document = TestDocument("TestDocument", self, PathFile("/tmp/TestDocument.fcstd"))

        if tracing:
            print(f"{tracing}<=TestProject({self.Label}).__post_init__()")

    # TestProject.new():
    @classmethod
    def new(cls, name: str) -> "TestProject":
        """Return a new TestProject properly initialized"""
        test_project = cls(name, cast(FabNode, None))  # Magic to create a root FabProject.
        return test_project

    # TestProject.Probe():
    def probe(self, label: str) -> None:
        """Print out some probe values."""
        # print("================")
        # document: FabDocument = self.Document
        # assert isinstance(document, TestDocument)
        # box: Box = document._Box
        # print(f"{label}: {box.North.Normal=}")
        # assert False, "Remove debugging probes"
        pass  # pragma: no cover


def main(key: str = "") -> Any:
    """Run main program."""
    shops: FabShops = FabShops.getExample()
    test_project: TestProject = TestProject.new("TestProject")
    test_project.setShops(shops)
    test_project.run()

    return 0


if __name__ == "__main__":
    main()
