#!/usr/bin/env python3
"""Test: Test classes for Fab."""

# <--------------------------------------- 100 characters ---------------------------------------> #

# Python library imports:
from dataclasses import dataclass, field
from typing import Any, cast, Dict, List, Tuple
from pathlib import Path

# CadQuery library imports:
from cadquery import Vector  # type: ignore

# Fab library imports:
from Geometry import FabCircle, FabPolygon, FabQuery
from Join import FabFasten, FabJoin
from Node import FabNode  # This should not be needed see cast in BoxSide.produce()
from Project import FabAssembly, FabDocument, FabProject
from Solid import FabSolid, FabMount


# BoxSide:
@dataclass
class BoxSide(FabSolid):
    """A Box side.

    Inherited Constructor Attributes:
    * *Name* (str): Box name.
    * *Parent* (*FabNode*): The parent container.
    * *Material* (str): The Material to use.
    * *Color* (str): The color to use.

    Additional Constructor Attributes:
    * *Contact* (Vector): The center "top" of the side.
    * *Normal* (Vector): The normal of the side (away from box center).
    * *Orient* (Vector): The orientation vector.
    * *HalfLength* (Vector): A vector of half the length in the length direction
    * *HalfWidth* (Vector): A vector of half the width in the width direction.
    * *Depth* float: Depth of side (opposite direction of *normal*.

    """

    Contact: Vector = Vector()
    Normal: Vector = Vector(0, 0, 1)
    Orient: Vector = Vector(0, 1, 0)
    HalfLength: Vector = Vector(1, 0, 0)
    HalfWidth: Vector = Vector(0, 1, 0)
    Depth: float = 5.0
    Screws: List[FabJoin] = field(init=False, repr=False)

    # BoxSide.__post_init__():
    def __post_init__(self) -> None:
        """Initialize Box Side."""
        super().__post_init__()
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>BoxSide({self.Label}).__post_init__()")
            print(f"{tracing}{self.Contact=}")
            print(f"{tracing}{self.Normal=}")
            print(f"{tracing}{self.Orient=}")
            print(f"{tracing}=>BoxSide({self.Label}).__post_init__()")
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
        normal_direction: Vector = self.Normal / self.Normal.Length
        length_direction: Vector = self.HalfLength / self.HalfLength.Length
        length: float = self.HalfLength.Length
        width_direction: Vector = self.HalfWidth / self.HalfWidth.Length
        width: float = self.HalfWidth.Length

        # Extrude the side:
        half_length: Vector = self.HalfLength
        half_width: Vector = self.HalfWidth
        radius: float = 0.5
        all_screws: Tuple[FabJoin, ...] = box.get_all_screws()
        mount: FabMount = self.mount(f"{name}FaceMount", contact, self.Normal, self.Orient, depth)
        corners: Tuple[Vector, ...] = (
            (contact + half_length + half_width, radius),
            (contact + half_length - half_width, radius),
            (contact - half_length - half_width, radius),
            (contact - half_length + half_width, radius),
        )

        polygon: FabPolygon = FabPolygon(corners)
        mount.extrude(f"{name}Extrude", polygon, depth)

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
            edge_mount: FabMount = self.mount(
                f"{name}Edge{edge_index}Mount", contact + direction,
                edge_normal, random_orient, depth)
            edge_mounts.append(edge_mount)
            edge_index += 1
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
    * *Material* (str): Material to use.
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
    Material: str = "HDPE"
    Center: Vector = Vector()

    Top: BoxSide = field(init=False, repr=False)
    Bottom: BoxSide = field(init=False, repr=False)
    North: BoxSide = field(init=False, repr=False)
    South: BoxSide = field(init=False, repr=False)
    East: BoxSide = field(init=False, repr=False)
    West: BoxSide = field(init=False, repr=False)
    Fasten: FabFasten = field(init=False, repr=False)

    # Box.__post_init__():
    def __post_init__(self) -> None:
        """Construct the the Box."""
        super().__post_init__()
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>Box({self.Label}).__post_init__()")

        depth: float = self.Thickness
        material: str = self.Material
        x_axis: Vector = Vector(1, 0, 0)
        y_axis: Vector = Vector(0, 1, 0)
        z_axis: Vector = Vector(0, 0, 1)
        self.Top = BoxSide("Top", self, Normal=z_axis, Orient=y_axis,
                           Depth=depth, Material=material, Color="lime")
        self.Bottom = BoxSide("Bottom", self, Normal=-z_axis, Orient=y_axis,
                              Depth=depth, Material=material, Color="green")
        self.North = BoxSide("North", self, Normal=y_axis, Orient=-z_axis,
                             Depth=depth, Material=material, Color="orange")
        self.South = BoxSide("South", self, Normal=-y_axis, Orient=z_axis,
                             Depth=depth, Material=material, Color="yellow")
        self.East = BoxSide("East", self, Normal=x_axis, Orient=y_axis,
                            Depth=depth, Material=material, Color="pink")
        self.West = BoxSide("West", self, Normal=-x_axis, Orient=y_axis,
                            Depth=depth, Material=material, Color="cyan")
        self.Fasten = FabFasten("BoxFasten", "M3x.5", ())  # No options yet.

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

        top: BoxSide = cast(BoxSide, self.Top)  # TODO Remove casts's
        top.Contact = center + dzv
        top.HalfLength = dyv
        top.HalfWidth = dxv

        bottom: BoxSide = cast(BoxSide, self.Bottom)
        bottom.Contact = center - dzv
        bottom.HalfLength = dyv
        bottom.HalfWidth = dxv

        north: BoxSide = cast(BoxSide, self.North)
        north.Contact = center + dyv
        north.HalfLength = dxv
        north.HalfWidth = dzv - dwzv

        south: BoxSide = cast(BoxSide, self.South)
        south.Contact = center - dyv
        south.HalfLength = dxv
        south.HalfWidth = dzv - dwzv

        east: BoxSide = cast(BoxSide, self.East)
        east.Contact = center + dxv
        east.HalfLength = dyv - dwyv
        east.HalfWidth = dzv - dwzv

        west: BoxSide = cast(BoxSide, self.West)
        west.Contact = center - dxv
        west.HalfLength = dyv - dwyv
        west.HalfWidth = dzv - dwzv

        if tracing:
            print(f"{tracing}<=Box({self.Label}.produce())")

    # Box.get_all_screws():
    def get_all_screws(self) -> Tuple[FabJoin, ...]:
        """Return all Box screws."""
        screws: List[FabJoin] = []
        screws.extend(self.Top.Screws)
        screws.extend(self.Bottom.Screws)
        screws.extend(self.North.Screws)
        screws.extend(self.South.Screws)
        return tuple(screws)


# TestSolid:
@dataclass
class TestSolid(FabSolid):
    """TestSolid: A test solid to exercise FabSolid code."""

    Fasten: FabFasten = field(init=False, repr=False)
    Screw1: FabJoin = field(init=False, repr=False)

    # TestSolid.__post_init__():
    def __post_init__(self) -> None:
        """Initialize TestSolid."""
        super().__post_init__()
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>TestSolid({self.Label}).__post_init__()")
        self.Fasten = FabFasten("TestSolidFasten", "M3x.5", ())  # No options yet.
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
        top_origin: Vector = Vector(0.0, 0.0, 55.0)
        normal: Vector = Vector(0, 0, 1)
        top_mount: FabMount = self.mount(
            "Top", top_origin, self.DT, self.DN, depth, tracing=tracing)
        wx: float = -40.0
        ex: float = 40.0
        ny: float = 20.0
        sy: float = -60.0

        # Perform the first Extrude:
        z_offset: float = top_origin.z
        extrude_fillet_radius: float = 10.0
        extrude_polygon: FabPolygon = FabPolygon((
            (Vector(wx, sy, z_offset), extrude_fillet_radius),  # SW
            (Vector(ex, sy, z_offset), extrude_fillet_radius),  # SE
            (Vector(ex, ny, z_offset), extrude_fillet_radius),  # NE
            (Vector(wx, ny, z_offset), extrude_fillet_radius),  # NW
        ))
        top_mount.extrude("Extrude", extrude_polygon, depth, tracing=next_tracing)

        # Perform a pocket:
        pocket_fillet_radius: float = 2.5
        left_polygon: FabPolygon = FabPolygon((
            (Vector(-30, -10, z_offset), pocket_fillet_radius),  # SW
            (Vector(-10, -10, z_offset), pocket_fillet_radius),  # SE
            (Vector(-10, 10, z_offset), pocket_fillet_radius),  # NE
            (Vector(-30, 10, z_offset), pocket_fillet_radius),  # NW
        ))
        top_mount.pocket("LeftPocket", left_polygon, depth)

        right_pocket: FabPolygon = FabPolygon((
            (Vector(10, -10, z_offset), pocket_fillet_radius),  # SW
            (Vector(30, -10, z_offset), pocket_fillet_radius),  # SE
            (Vector(30, 10, z_offset), pocket_fillet_radius),  # NE
            (Vector(10, 10, z_offset), pocket_fillet_radius),  # NW
        ))
        top_mount.pocket("RightPocket", right_pocket, depth2)

        right_circle: FabCircle = FabCircle(Vector(20, 0, z_offset), normal, 10)
        top_mount.pocket("RightCircle", right_circle, depth)

        center_circle: FabCircle = FabCircle(Vector(0, 0, z_offset), normal, 10)
        top_mount.pocket("CenterCircle", center_circle, depth2)

        screw_start: Vector = Vector(0.0, -10.0, z_offset)
        screw_end: Vector = Vector(0.0, -10.0, z_offset - depth)
        self.Screw1: FabJoin = FabJoin("Screw1", self.Fasten, screw_start, screw_end)

        top_mount.drill_joins("Screw1", (self.Screw1,), tracing=next_tracing)

        north_start: Vector = self.N
        north_end: Vector = self.C
        north_mount: FabMount = self.mount(
            "North", self.N, self.DN, self.DE, self.YMax - self.YMin, tracing=tracing)
        self.ScrewN: FabJoin = FabJoin("ScrewN", self.Fasten, north_start, north_end)

        north_mount.drill_joins("ScrewN", (self.ScrewN,), tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=TestSolid({self.Label}).produce()")


# TestAssembly:
@dataclass
class TestAssembly(FabAssembly):
    """TestAssembly: A Class to test an assembly."""

    Solid: TestSolid = field(init=False, repr=False, default=cast(TestSolid, None))
    Box: Box = field(init=False, repr=False, default=cast(Box, None))

    # TestAssembly.__post_init__():
    def __post_init__(self):
        """Initialize Test Assembly."""
        super().__post_init__()
        self.Solid = TestSolid("TestSolid", self, "HDPE", "red")
        self.Box = Box("TestBox", self, 200.0, 150.0, 75.0, 6.0, "HDPE", Vector(0, 0, 0))


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

        self.Document = TestDocument("TestDocument", self, Path("/tmp/TestDocument.fcstd"))

        if tracing:
            print(f"{tracing}<=TestProject({self.Label}).__post_init__()")

    # TestProject.new():
    @classmethod
    def new(cls, name: str) -> "TestProject":
        """Return a new TestProject properly initializedd"""
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
        pass


def main(key: str = "") -> Any:
    """Run main program."""
    objects_table: Dict[str, Any] = {}
    test_project: TestProject = TestProject.new("TestProject")
    test_project.run(objects_table)

    result: Any = 0
    if key:
        if key in objects_table:
            result = objects_table[key]
            if isinstance(result, FabQuery):
                result = result.WorkPlane
        elif key:
            print(f"'{key}' is not one of {tuple(objects_table.keys())}")
    return result


if __name__ == "__main__":
    main()
