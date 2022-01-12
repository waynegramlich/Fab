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

# [Combine Draft and Sketch to simplify Modeling.](https://www.youtube.com/watch?v=lfzGEk727eo)

# Note this code uses nested dataclasses that are frozen.  Computed attributes are tricky.
# See (Set frozen data class files in __post_init__)[https://stackoverflow.com/questions/53756788]

import sys
sys.path.append(".")
import Embed
Embed.setup()

from dataclasses import dataclass, field
from typing import Any, cast, Dict, List, Optional, Set, Tuple
from pathlib import Path


import FreeCAD  # type: ignore
from FreeCAD import Vector
import FreeCAD as App  # type: ignore
import FreeCADGui as Gui  # type: ignore

from Geometry import FabCircle, FabPolygon
from Join import FabFasten, FabJoin
from Node import FabNode
from Solid import FabMount, FabSolid, visibility_set


@dataclass
# FabGroup:
class FabGroup(FabNode):
    """FabGroup: A named group of FabNode's.

    Inherited Attributes:
    * *Name* (str)
    * *Parent* (FabNode)
    * *Children* (Tuple[FabNode, ...)

    """

    Group: App.DocumentObjectGroup = field(
        init=False, repr=False, default=cast(App.DocumentObjectGroup, None))

    # FabGroup.__post_init__():
    def __post_init__(self):
        """Initialize FabGroup."""
        super().__post_init__()

    # FabGroup.produce():
    def produce(self) -> Tuple[str, ...]:
        """Create the FreeCAD group object."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabGroup({self.Name}).produce()")
        context: Dict[str, Any] = self.Context
        errors: List[str] = []

        # Create the *group* that contains all of the FabNode's:
        parent_object: Any = self.Up.AppObject
        group: App.DocumentObjectGroup = parent_object.addObject(
            "App::DocumentObjectGroup", f"{self.Name}")
        assert isinstance(group, App.DocumentObjectGroup), group
        self.set_object(group)

        group.Visibility = False
        self.Group = group
        visibility_set(group)

        child: FabNode
        context["parent_object"] = self.Group
        context["parent_name"] = self.Name
        for child in self._Children.values():
            child._Context = context.copy()
            errors.extend(child.produce())
        if tracing:
            print(f"{tracing}<=FabGroup({self.Name}).produce()")
        return tuple(errors)

    # FabGroup.is_group():
    def is_group(self) -> bool:
        """ Return True if FabNode is a FabGroup."""
        return True  # All other FabNode's return False.


# FabAssembly:
@dataclass
class FabAssembly(FabGroup):
    """FabAssembly: A group FabSolid's and sub-FabAssembly's."""

    _Zilch: int = field(init=False, repr=False, default=0)  # Empty dataclasses are not allowed.

    # FabAssembly.__post_init__():
    def __post_init__(self) -> None:
        """Initialize FabAssembly."""
        super().__post_init__()
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}<=>FabAssembly({self.Name}).__post_init__()")

    # FabAssembly.is_assembly():
    def is_assembly(self) -> bool:
        """ Return True if FabNode is a FabGroup."""
        return True  # All other FabNode's return False.

    # FabAssembly.pre_produce():
    def pre_produce(self) -> Tuple[str, ...]:
        """Preproduce a FabAssembly"""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabAssembly.pre_produce({self.Name}).pre_produce()")
        errors: Tuple[str, ...] = super().pre_produce()
        if tracing:
            print(f"{tracing}<=FabAssembly.pre_produce({self.Name}).pre_produce()")
        return errors

    # FabAssembly.produce():
    def produce(self) -> Tuple[str, ...]:
        """Preproduce a FabAssembly"""
        return super().post_produce()

    # FabAssembly.post_produce():
    def post_produce(self) -> Tuple[str, ...]:
        """Preproduce a FabAssembly"""
        return super().post_produce()


# FabDocument:
@dataclass
class FabDocument(FabNode):
    """FabDocument: Represents a FreeCAD document Document.

    Inherited Attributes:
    * *Name* (str): Node name
    * *Children* (Tuple[Union[FabAssembly, FablGroup, FabSolid], ...]):
      The children nodes which are constrained to "group-like" or a FabSolid.
    * *ChlidrenNames* (Tuple[str, ...]): The Children names.

    Attributes:
    * *FilePath* (Path):
      The Python pathlib.Path file name which must have a suffix of `.fcstd` or `.FCStd`.

    """

    FilePath: Path = Path("bogus_file")
    _AppDocument: Optional[App.Document] = field(init=False, repr=False)

    # FabDocument.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabDocument."""

        super().__post_init__()
        self._AppDocument = None
        suffix: str = self.FilePath.suffix
        valid_suffixes: Tuple[str, ...] = (".fcstd", ".FCStd")
        if suffix not in valid_suffixes:
            raise RuntimeError(f"{self.FullPath}: '{self.FilePath}' suffix '{suffix}' "
                               f"is not one of {valid_suffixes}.")
        self._check_children()

    # FabDocument._check_children():
    def _check_children(self) -> None:
        """Verify that children are valid types."""
        child: FabNode
        for child in self._Children.values():
            if not isinstance(child, (FabAssembly, FabGroup, FabSolid)):
                raise RuntimeError(
                    f"{self.FullPath}: {child.FullPath} is not a {type(child)}, "
                    "not FabAssembly/FabGroup/FabSolid")

    # FabDocument.is_document():
    def is_document(self) -> bool:
        """ Return True if FabNode is a FabGroup."""
        return True  # All other FabNode's return False.

    # FabDocument.produce():
    def produce(self) -> Tuple[str, ...]:
        """Produce FabDocument."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabDocument.produce('{self.Name}', *)")

        # Create the new *app_document*:
        errors: List[str] = []
        if self.Construct:  # Construct OK
            context: Dict[str, Any] = self.Context
            context_keys: Tuple[str, ...]
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}Before Context: {context_keys}")

            # Create *app_document* and save it away in both *self* and *context*:
            app_document = cast(App.Document, App.newDocument(self.Name))  # Why the cast?
            assert isinstance(app_document, App.Document)  # Just to be sure.
            self._AppDocument = app_document
            self._AppObject = app_document
            context["parent_object"] = app_document
            context["parent_name"] = app_document.Name

            # If the GUI is up, get the associated *gui_document* and save it into *context*:
            if App.GuiUp:  # pragma: no unit cover
                gui_document = cast(Gui.Document, Gui.getDocument(self.Name))
                assert isinstance(gui_document, Gui.Document)  # Just to be sure.
                self._GuiDocument = gui_document
                self._GuiObject = gui_document

        if tracing:
            print(f"{tracing}<=FabDocument.produce('{self.Name}', *)")
        return tuple(errors)

    # FabDocument.post_produce():
    def post_produce(self) -> Tuple[str, ...]:
        """Close the FabDocument."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabDocument({self.Name}).post_produce()")

        if self.Construct:  # Construct OK
            # Recompute and save:
            app_document: App.Document = self._AppDocument
            app_document.recompute()
            app_document.saveAs(str(self.FilePath))

        if tracing:
            print(f"{tracing}Saved {self.FilePath}")
            print(f"{tracing}<=FabDocument({self.Name}).post_produce()")
        return ()


@dataclass
# FabProject:
class FabProject(FabNode):
    """FabProject: The Root mode a FabNode tree."""

    _AllNodes: Tuple[FabNode, ...] = field(init=False, repr=False)
    _Construct: bool = field(init=False, repr=False)

    # FabProject.__post_init__():
    def __post_init__(self) -> None:
        """Process FabRoot."""
        super().__post_init__()
        self._AllNodes = ()
        self._Construct = False

    # FabProject.get_construct():
    def get_construct(self) -> bool:
        """Return the Construct mode.

        The default get_construct() method in FabNode always returns False.  This method
        overrides that method and returns the value of the _Construct field.  This field
        is set to False in phase 1 of the run() method.  It is set to True in phase 2 of
        the run method.

        Many other classes implement a Construct property as follows:

             @property
             def Construct(self) -> bool:
                 return self.SOME_FABNODE._Root.Construct

        which calls this method to get the construct status.  This is a pretty convoluted
        way to get the information, but it works.
        """
        return self._Construct

    # FabProject.is_project():
    def is_project(self) -> bool:
        """ Return True if FabNode is a FabGroup."""
        return True  # All other FabNode's return False.

    # FabProject.new():
    @classmethod
    def new(cls, name: str) -> "FabProject":
        """Create a new root FabProject."""
        # print(f"=>FabProject.new({name}).new()")
        project = cls(name, cast(FabNode, None))  # Magic to create a root FabProject.
        # print(f"<=Project.new({name})=>{project}")
        return project

    # FabProject.run():
    def run(self) -> None:
        # Shared variables:
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>Project({self.Name}).run()")
        error: str
        errors: List[str]
        index: int
        name: str
        node: FabNode

        # Phase 1: Iterate over tree in constraint mode:
        if tracing:
            print("")
            print(f"{tracing}Project({self.Name}).run(): Phase 1: Constraints")
        previous_constraints: Set[str] = set()
        differences: List[int] = []
        all_nodes: Tuple[FabNode, ...] = self._AllNodes
        reversed_nodes: Tuple[FabNode, ...] = tuple(reversed(all_nodes))
        iteration: int
        for iteration in range(1000):
            errors = []
            current_constraints: Set[str] = set()
            # Update all boxes in bottom-up order:
            for node in reversed_nodes:
                node.enclose(tuple(self._Children.values()))
            # Call *produce* in top-down order first.
            for node in all_nodes:
                errors.extend(node.produce())
                attribute: Any
                for name, attribute in node.__dict__.items():
                    if name and name[0].isupper() and (
                            isinstance(attribute, (int, float, str, bool, Vector))):
                        constraint: str = f"{node.FullPath}:{name}:{attribute}"
                        assert constraint not in current_constraints
                        current_constraints.add(constraint)
            difference_constraints: Tuple[str, ...] = (
                tuple(sorted(current_constraints ^ previous_constraints)))
            previous_constraints = current_constraints

            # Figure out if iteration can be stopped:
            difference: int = len(difference_constraints)
            print(f"{tracing}Iteration[{iteration}]: {difference} differences")
            if difference == 0:
                break
            differences.append(difference)
            if len(differences) >= 6 and (
                    max(differences[-6:-3]) == max(differences[-3:])):   # pragma: no unit cover
                print("Differences seem not to be changing:")
                for index, error in enumerate(errors):
                    print("  Error[{index}]: {error}")
                for index, constraint in enumerate(difference_constraints):
                    print("  Constraint[{index}]: {constraint")
                break

        # Phase 2: Run top-down in "construct" mode, where *post_produce*() also gets called:
        self._Construct = True
        if tracing:
            print()
            print(f"{tracing}Project({self.Name}).run(): Phase 2: Construct: {self._Construct=}")

        errors = []
        errors.extend(self._produce_walk())
        if errors:
            print("Construction Errors:")
            # Mypy currently chokes on: `for index, error in enumerate(errors):`
            # with `error: "int" not callable`.  Weird.
            for index in range(len(errors)):  # pragma: no unit cover
                error = errors[index]
                print(f"  Error[{index}]: {error}")
        if tracing:
            print(f"{tracing}<=Project({self.Name}).run()")

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
            print(f"{tracing}=>BoxSide({self.Name}).__post_init__()")
            print(f"{tracing}{self.Contact=}")
            print(f"{tracing}{self.Normal=}")
            print(f"{tracing}{self.Orient=}")
            print(f"{tracing}=>BoxSide({self.Name}).__post_init__()")
        self.Screws = []

    # BoxSide.produce():
    def produce(self) -> Tuple[str, ...]:
        """Produce BoxSide."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>BoxSide({self.Name}).produce()")
        box = cast(Box, self.Up)
        assert isinstance(box, Box)  # Redundant
        fasten: FabFasten = box.Fasten
        screws: List[FabJoin] = self.Screws

        name: str = self.Name
        contact: Vector = self.Contact
        copy: Vector = Vector()
        depth: float = self.Depth
        normal_direction: Vector = (self.Normal + copy).normalize()
        length_direction: Vector = (self.HalfLength + copy).normalize()
        length: float = self.HalfLength.Length
        width_direction: Vector = (self.HalfWidth + copy).normalize()
        width: float = self.HalfWidth.Length

        # Create all of the *screws*:
        del screws[:]
        dlength: float
        dwidth: float
        if name in ("Top", "Bottom", "North", "South"):
            length_adjust = 0.5 * depth if name in ("Top", "Bottom") else 0.5 * depth
            width_adjust = 0.5 * depth if name in ("Top", "Bottom") else 3.0 * depth
            for dlength in (length - length_adjust, -length + length_adjust):
                for dwidth in (width - width_adjust, -width + width_adjust):
                    start: Vector = contact + dlength * length_direction + dwidth * width_direction
                    end: Vector = start - (3 * depth) * normal_direction
                    screw: FabJoin = FabJoin(f"{name}Join{len(screws)}", fasten, start, end)
                    screws.append(screw)

        # Extrude the side:
        half_length: Vector = self.HalfLength
        half_width: Vector = self.HalfWidth
        all_screws: Tuple[FabJoin, ...] = box.get_all_screws()
        mount: FabMount = self.mount(f"{name}FaceMount", contact, self.Normal, self.Orient, depth)
        corners: Tuple[Vector, ...] = (
            contact + half_length + half_width,
            contact + half_length - half_width,
            contact - half_length - half_width,
            contact - half_length + half_width,
        )
        # Create *edge_mounts*:
        edge_mounts: List[FabMount] = []
        edge_index: int = 0
        direction: Vector
        for direction in (self.HalfLength, -self.HalfLength, self.HalfWidth, -self.HalfWidth):
            edge_normal: Vector = (direction + copy).normalize()
            random_orient: Vector = (self.Normal + copy).cross(direction + copy)
            edge_mount: FabMount = self.mount(
                f"{name}Edge{edge_index}Mount", contact + direction,
                edge_normal, random_orient, depth)
            edge_mounts.append(edge_mount)
            edge_index += 1

        polygon: FabPolygon = FabPolygon(corners)
        mount.extrude(f"{name}Extrude", polygon, depth)
        self.drill_joins(all_screws)

        if tracing:
            print(f"{tracing}<=BoxSide({self.Name}).produce()")
        return ()

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
            print(f"{tracing}=>Box({self.Name}).__post_init__()")

        depth: float = self.Thickness
        material: str = self.Material
        x_axis: Vector = Vector(1, 0, 0)
        y_axis: Vector = Vector(0, 1, 0)
        z_axis: Vector = Vector(0, 0, 1)
        self.Top = BoxSide("Top", self, Normal=z_axis, Orient=y_axis,
                           Depth=depth, Material=material, Color="red")
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
            print(f"{tracing}<=Box({self.Name}).__post_init__()")

    # Box.produce():
    def produce(self) -> Tuple[str, ...]:
        """Produce the Box."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>Box({self.Name}.produce())")

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

        top: BoxSide = self.Top
        top.Contact = center + dzv
        top.HalfLength = dyv
        top.HalfWidth = dxv

        bottom: BoxSide = self.Bottom
        bottom.Contact = center - dzv
        bottom.HalfLength = dyv
        bottom.HalfWidth = dxv

        north: BoxSide = self.North
        north.Contact = center + dyv
        north.HalfLength = dxv
        north.HalfWidth = dzv - dwzv

        south: BoxSide = self.South
        south.Contact = center - dyv
        south.HalfLength = dxv
        south.HalfWidth = dzv - dwzv

        east: BoxSide = self.East
        east.Contact = center + dxv
        east.HalfLength = dyv - dwyv
        east.HalfWidth = dzv - dwzv

        west: BoxSide = self.West
        west.Contact = center - dxv
        west.HalfLength = dyv - dwyv
        west.HalfWidth = dzv - dwzv

        if tracing:
            print(f"{tracing}<=Box({self.Name}.produce())")
        return ()

    # Box.get_all_screws():
    def get_all_screws(self) -> Tuple[FabJoin, ...]:
        """Return all Box screws."""
        return (
            tuple(self.Top.Screws) +
            tuple(self.Bottom.Screws) +
            tuple(self.North.Screws) +
            tuple(self.South.Screws)
        )


# TestSolid:
@dataclass
class TestSolid(FabSolid):
    """TestSolid: A test solid to exercise FabSolid code."""

    # TestSolid.__post_init__():
    def __post_init__(self) -> None:
        """Initialize TestSolid."""
        super().__post_init__()
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}<=>TestSolid({self.Name}).__post_init__()")

    # TestSolid.produce()
    def produce(self) -> Tuple[str, ...]:
        tracing: str = self.Tracing
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>TestSolid({self.Name}).produce()")

        errors: List[str] = []

        # Create *top_mount*:
        depth: float = 10.0
        depth2: float = depth / 2.0
        if True or self.Construct:
            origin: Vector = Vector()
            normal: Vector = Vector(0, 0, 1)
            context: Dict[str, Any] = self._Context
            assert isinstance(context, dict)
            context_keys: Tuple[str, ...]
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}{origin=} {self.TNE=} {self.BSW=} {self.DT=}")
            top_mount: FabMount = self.mount(
                "Top", origin, self.DT, self.DN, depth, tracing=tracing)
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}After mount context: {context_keys}")

            # Perform the first Extrude:
            z_offset: float = 0.0
            extrude_fillet_radius: float = 10.0
            extrude_polygon: FabPolygon = FabPolygon((
                (Vector(-40, -60, z_offset), extrude_fillet_radius),  # SW
                (Vector(40, -60, z_offset), extrude_fillet_radius),  # SE
                (Vector(40, 20, z_offset), extrude_fillet_radius),  # NE
                (Vector(-40, 20, z_offset), extrude_fillet_radius),  # NW
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

        if tracing:
            print(f"{tracing}<=TestSolid({self.Name}).produce()")
        return tuple(errors)


# TestDocument:
@dataclass
class TestDocument(FabDocument):
    """A Test file."""

    _TestSolid: TestSolid = field(init=False, repr=False)
    _Box: Box = field(init=False, repr=False)

    # TestDocument.__post_init__():
    def __post_init__(self) -> None:
        """Initialize TestDocument."""
        super().__post_init__()
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>TestFile({self.Name}).__post_init__()")
        self._TestSolid = TestSolid("TestSolid", self, "HDPE", "red")
        self._Box = Box("TestBox", self, 200.0, 150.0, 75.0, 6.0, "HDPE", Vector(0, 0, 0))
        if tracing:
            print(f"{tracing}<=TestFile({self.Name}).__post_init__()")


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
            print(f"{tracing}=>TestProject({self.Name}).__post_init__()")

        self.Document = TestDocument("TestFile", self, Path("/tmp/TestFile.fcstd"))

        if tracing:
            print(f"{tracing}<=TestProject({self.Name}).__post_init__()")

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


def main() -> None:
    """Run main program."""
    test_project: TestProject = TestProject.new("TestProject")
    test_project.run()

    # Create the models:
    # test_solid: TestSolid = TestSolid("TestSolid")
    # box: Box = Box("Box", Center=Vector())  # 0, 100.0, 0.0))
    # solids: Tuple[Union[FabSolid, FabAssembly], ...] = (box, )  # , test_solid)
    # model_file: FabDocument = FabDocument("Test", Path("/tmp/test.fcstd"))
    # model_file._Children = solids
    # root: FabProject = FabProject("Root")
    # root._Children = (model_file,)
    # root.run(tracing="")


if __name__ == "__main__":
    main()
