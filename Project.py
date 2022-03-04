#!/usr/bin/env python3
"""Project: A module for creating Fab projects."""

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

# <--------------------------------------- 100 characters ---------------------------------------> #

import sys
sys.path.append(".")
import Embed
USE_FREECAD: bool
USE_CAD_QUERY: bool
USE_FREECAD, USE_CAD_QUERY = Embed.setup()

from dataclasses import dataclass, field
from typing import Any, cast, Dict, List, Optional, Set, Tuple
from pathlib import Path


if USE_FREECAD:
    import FreeCAD  # type: ignore
    from FreeCAD import Vector
    import FreeCAD as App  # type: ignore
    import FreeCADGui as Gui  # type: ignore
elif USE_CAD_QUERY:
    import cadquery as cq  # type: ignore
    from cadquery import Vector  # type: ignore

from Geometry import FabCircle, FabPolygon, FabWorkPlane
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

    Group: Any = field(init=False, repr=False, default=None)

    # FabGroup.__post_init__():
    def __post_init__(self):
        """Initialize FabGroup."""
        super().__post_init__()

    # FabGroup.post_produce1():
    def post_produce1(self, objects_table: Dict[str, Any]) -> None:
        """Perform FabGroup phase 1 post production."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabGroup({self.Label}).post_produce1(*)")

        if USE_FREECAD:
            # Create the *group* that contains the children FabNode's:
            parent_object: Any = self.Up.AppObject

            # Adding a group to document is different from adding one to a non-document:
            if hasattr(parent_object, "FileName"):  # Document has FileName attribute.
                parent_object.addObject("App::DocumentObjectGroup", self.Label)
            else:
                parent_object.newObject("App::DocumentObjectGroup", self.Label)

            group: Any = parent_object.getObject(self.Label)
            self.set_object(group)
            visibility_set(group)

        if tracing:
            print(f"{tracing}<=FabGroup({self.Label}).post_produce1(*)")

    # FabGroup.produce():
    def produce(self) -> None:
        """Create the FreeCAD group object."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}<=>FabGroup({self.Label}).produce()")

    # FabGroup.is_group():
    def is_group(self) -> bool:
        """ Return True if FabNode is a FabGroup."""
        return True  # All other FabNode's return False.


# FabAssembly:
@dataclass
class FabAssembly(FabGroup):
    """FabAssembly: A group FabSolid's and sub-FabAssembly's."""

    _Assembly: Any = field(init=False, repr=False)

    # FabAssembly.__post_init__():
    def __post_init__(self) -> None:
        """Initialize FabAssembly."""
        super().__post_init__()
        self._Assembly = None
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}<=>FabAssembly({self.Label}).__post_init__()")

    # FabAssembly.is_assembly():
    def is_assembly(self) -> bool:
        """ Return True if FabNode is a FabGroup."""
        return True  # All other FabNode's return False.

    # FabAssembly.post_produce1():
    def post_produce1(self, objects_table: Dict[str, Any]) -> None:
        """Preform FabAssembly phase1 post production."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabAssembly({self.Label}).post_produce1()")
        super().post_produce1(objects_table)
        if tracing:
            print(f"{tracing}<=FabAssembly({self.Label}).post_produce1()")

    # FabAssembly.post_produce2():
    def post_produce2(self, objects_table: Dict[str, Any]) -> None:
        """Perform FabAssembly phase 2 post production."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabAssembly({self.Label}).post_produce2()")
        if USE_CAD_QUERY:
            child_node: FabNode
            assembly: cq.Assembly = cq.Assembly()
            for child_node in self.Children:
                sub_assembly: cq.Assembly
                if isinstance(child_node, FabAssembly):
                    sub_assembly = child_node._Assembly
                elif isinstance(child_node, FabSolid):
                    sub_assembly = child_node._Assembly
                else:
                    raise RuntimeError(
                        f"FabAssembly.post_produce1({self.Label}):"
                        f"{child_node} is {type(child_node)}, not FabSolid or FabAssembly")

                if not isinstance(sub_assembly, cq.Assembly):
                    raise RuntimeError(
                        f"FabAssembly.post_produce1({self.Label}):"
                        f"{sub_assembly} is {type(sub_assembly)}, not cq.Assembly")
                assembly.add(sub_assembly, name=child_node.Label)
            objects_table[self.Label] = assembly
            self._Assembly = assembly
        if tracing:
            print(f"{tracing}<=FabAssembly({self.Label}).post_produce2()")


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

    FilePath: Path = Path("/bogus_file")
    _AppDocument: Optional["App.Document"] = field(init=False, repr=False)
    _GuiDocument: Optional["Gui.Document"] = field(init=False, repr=False)

    # FabDocument.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabDocument."""

        # Initialize fields:
        super().__post_init__()
        self._AppDocument = None
        self._GuiDocument = None

        # Verfiy *suffix*;
        if not isinstance(self.FilePath, Path):
            raise RuntimeError(f"{self.FullPath}: '{self.FilePath}' is not a Path")
        suffix: str = self.FilePath.suffix
        valid_suffixes: Tuple[str, ...] = (".fcstd", ".FCStd")
        if suffix not in valid_suffixes:
            raise RuntimeError(f"{self.FullPath}: '{self.FilePath}' suffix '{suffix}' "
                               f"is not a valid suffix {valid_suffixes}.")

        # Verify that *children* have valid types:
        # TODO: Is *children* always empty?
        children: Tuple[FabNode, ...] = self.Children
        child: FabNode
        for child in children:
            if not isinstance(child, (FabAssembly, FabGroup, FabSolid)):
                raise RuntimeError(
                    f"{self.FullPath}: {child.FullPath} is not a {type(child)}, "
                    "not FabAssembly/FabGroup/FabSolid")

    # FabDocument.post_produce1():
    def post_produce1(self, objects_table: Dict[str, Any]) -> None:
        """Perform FabDocument phase 1 post production."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabDocument({self.Label}).post_produce1()")

        # Create *app_document*:
        if USE_FREECAD:
            app_document: Any = App.newDocument(self.Label)
            # assert isinstance(app_document, App.Document)  # Just to be sure.
            self.set_app_object_only(app_document)
            self._AppDocument = app_document

            # If the GUI is up, get the associated *gui_document* and hang onto it:
            if App.GuiUp:  # pragma: no unit cover
                gui_document: Any = Gui.getDocument(app_document.Name)
                # assert isinstance(gui_document, Gui.Document)
                self.set_gui_object_only(gui_document)
                self._GuiDocument = gui_document
        elif USE_CAD_QUERY:
            pass

        if tracing:
            print(f"{tracing}<=FabDocument({self.Label}).post_produce1()")

    # FabDocument.post_produce2():
    def post_produce2(self, objects_table: Dict[str, Any]) -> None:
        """Close the FabDocument."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabDocument({self.Label}).post_produce2()")

        if USE_FREECAD:
            # Save the document:
            app_document: Any = self._AppDocument
            app_document.recompute()
            app_document.saveAs(str(self.FilePath))

        if tracing:
            print(f"{tracing}Saved {self.FilePath}")
            print(f"{tracing}<=FabDocument({self.Label}).post_produce2()")

    # FabDocument.is_document():
    def is_document(self) -> bool:
        """ Return True if FabNode is a FabGroup."""
        return True  # All other FabNode's return False.

    # FabDocument.produce():
    def produce(self) -> None:
        """Produce FabDocument."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}<=>FabDocument.produce('{self.Label}', *)")


@dataclass
# FabProject:
class FabProject(FabNode):
    """FabProject: The Root mode a FabNode tree."""

    _AllNodes: Tuple[FabNode, ...] = field(init=False, repr=False)
    _Errors: List[str] = field(init=False, repr=False)

    # FabProject.__post_init__():
    def __post_init__(self) -> None:
        """Process FabRoot."""
        super().__post_init__()
        self._AllNodes = ()
        self._Errors = []

    # FabProject.get_errors():
    def get_errors(self) -> List[str]:
        """Return the FabProject errors list."""
        return self._Errors

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
    def run(self, objects_table: Dict[str, Any] = {}) -> None:
        # Shared variables:
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>Project({self.Label}).run()")
        error: str
        index: int
        name: str
        node: FabNode
        errors: List[str] = self._Errors

        # Phase 1: Iterate over tree in constraint mode:
        if tracing:
            print("")
            print(f"{tracing}Project({self.Label}).run(): Phase 1: Constraint Propagation")
        previous_constraints: Set[str] = set()
        differences: List[int] = []
        all_nodes: Tuple[FabNode, ...] = self._AllNodes
        reversed_nodes: Tuple[FabNode, ...] = tuple(reversed(all_nodes))
        iteration: int
        for iteration in range(1000):
            del errors[:]  # Clear *errors*
            current_constraints: Set[str] = set()
            # Update all boxes in bottom-up order:
            for node in reversed_nodes:
                node.enclose(tuple(self._Children.values()))
            # Call *produce* in top-down order first.
            for node in all_nodes:
                node.pre_produce()
                node.produce()
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
        if not errors:
            if tracing:
                print()
                print(f"{tracing}Project({self.Label}).run(): Phase 2: Construct")

            if tracing:
                print(f"{tracing}Phase 2A: post_produce1():")
            del errors[:]  # Clear *errors*
            for node in all_nodes:
                node.post_produce1(objects_table)

            if tracing:
                print(f"{tracing}Phase 2b: post_produce2():")
            for node in reversed(all_nodes):
                node.post_produce2(objects_table)

        # Output any *errors*:
        if errors:
            print("Construction Errors:")
            # Mypy currently chokes on: `for index, error in enumerate(errors):`
            # with `error: "int" not callable`.  Weird.
            for index in range(len(errors)):  # pragma: no unit cover
                error = errors[index]
                print(f"  Error[{index}]: {error}")
        if tracing:
            print(f"{tracing}<=Project({self.Label}).run()")


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
            if USE_FREECAD:
                edge_mount: FabMount = self.mount(
                    f"{name}Edge{edge_index}Mount", contact + direction,
                    edge_normal, random_orient, depth)
                edge_mounts.append(edge_mount)
            elif USE_CAD_QUERY:
                pass
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
        screws: Tuple[FabJoin, ...] = ()
        if USE_FREECAD:
            screws = (
                tuple(cast(BoxSide, self.Top).Screws) +
                tuple(cast(BoxSide, self.Bottom).Screws) +
                tuple(cast(BoxSide, self.North).Screws) +
                tuple(cast(BoxSide, self.South).Screws)
            )
        elif USE_CAD_QUERY:
            pass
        return screws


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
            print(f"{tracing}<=>TestSolid({self.Label}).__post_init__()")

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

        # Perform the first Extrude:
        z_offset: float = top_origin.z
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


def main(key: str = "") -> None:
    """Run main program."""
    objects_table: Dict[str, Any] = {}
    test_project: TestProject = TestProject.new("TestProject")
    test_project.run(objects_table)

    result: Any = 0
    if USE_CAD_QUERY:
        if key in objects_table:
            result = objects_table[key]
            if isinstance(result, FabWorkPlane):
                result = result.WorkPlane
        elif key:
            print(f"'{key}' is not one of {tuple(objects_table.keys())}")
    return result


if __name__ == "__main__":
    main()
