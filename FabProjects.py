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

# IGNORE!

from dataclasses import dataclass, field
import json
from typing import Any, cast, Dict, IO, List, Optional, Set, Tuple
from pathlib import Path

import cadquery as cq  # type: ignore
from cadquery import Vector  # type: ignore

from FabNodes import FabNode, Fab_Steps, Fab_ProduceState
from FabSolids import FabSolid


# Fab_Group:
@dataclass
class Fab_Group(FabNode):
    """Fab_Group: A named group of FabNode's.

    Inherited Attributes:
    * *Name* (str)
    * *Parent* (FabNode)
    * *Children* (Tuple[FabNode, ...)

    """

    Group: Any = field(init=False, repr=False, default=None)

    # Fab_Group.__post_init__():
    def __post_init__(self):
        """Initialize Fab_Group."""
        super().__post_init__()

    # Fab_Group.post_produce1():
    def post_produce1(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        """Perform Fab_Group phase 1 post production."""
        tracing = self.Tracing  # Ignore *tracing* argument.
        if tracing:
            print(f"{tracing}<=>Fab_Group({self.Label}).post_produce1(*, *)")

    # Fab_Group.produce():
    def produce(self) -> None:
        """Create the FreeCAD group object."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}<=>Fab_Group({self.Label}).produce()")

    # Fab_Group.is_group():
    def is_group(self) -> bool:
        """ Return True if FabNode is a Fab_Group."""
        return True  # All other FabNode's return False.  # pragma: no unit cover

    # Fab_Group._unit_tests()
    @staticmethod
    def _unit_tests() -> None:
        pass


# FabAssembly:
@dataclass
class FabAssembly(Fab_Group):
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
        """ Return True if FabNode is a Fab_Group."""
        return True  # All other FabNode's return False.  # pragma: no unit cover

    # FabAssembly.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return FabProject JSON structure."""
        json: Dict[str, Any] = super().to_json()
        json["Kind"] = "Assembly"
        return json

    # FabAssembly.post_produce1():
    def post_produce1(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        """Perform FabAssembly phase1 post production."""
        tracing = self.Tracing  # Ignore *tracing* argument.
        if tracing:
            print(f"{tracing}=>FabAssembly({self.Label}).post_produce1(*, *)")
        super().post_produce1(produce_state)
        if tracing:
            print(f"{tracing}<=FabAssembly({self.Label}).post_produce1(*, *)")

    # FabAssembly.post_produce2():
    def post_produce2(self, produce_state: Fab_ProduceState) -> None:
        """Perform FabAssembly phase 2 post production."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabAssembly({self.Label}).post_produce2()")

        # Create the CadQuery *assembly* and fill it in:
        child_node: FabNode
        assembly: cq.Assembly = cq.Assembly()
        for child_node in self.Children:
            sub_assembly: cq.Assembly
            if isinstance(child_node, FabAssembly):
                sub_assembly = child_node._Assembly
            elif isinstance(child_node, FabSolid):
                sub_assembly = child_node._Assembly
            else:  # pragma: no unit cover
                raise RuntimeError(
                    f"FabAssembly.post_produce2({self.Label}): {child_node} is "
                    f"{type(child_node)}, not FabSolid or FabAssembly")  # pragma: no unit cover

            if not isinstance(sub_assembly, cq.Assembly):
                raise RuntimeError(
                    f"FabAssembly.post_produce2({self.Label}): {sub_assembly} is "
                    f"{type(sub_assembly)}, not cq.Assembly")  # pragma: no unit cover
            assembly.add(sub_assembly, name=child_node.Label)
        produce_state.ObjectsTable[self.Label] = assembly
        self._Assembly = assembly

        if tracing:
            print(f"{tracing}<=FabAssembly({self.Label}).post_produce2()")

    # FabAssembly._unit_tests()
    @staticmethod
    def _unit_tests() -> None:
        pass


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
    _AppDocument: Any = field(init=False, repr=False)
    _GuiDocument: Any = field(init=False, repr=False)

    # FabDocument.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabDocument."""

        # Initialize fields:
        super().__post_init__()
        self._AppDocument = None
        self._GuiDocument = None

        # Verify *suffix*;
        if not isinstance(self.FilePath, Path):
            raise RuntimeError(
                f"{self.FullPath}: '{self.FilePath}' is not a Path")  # pragma: no unit cover
        suffix: str = self.FilePath.suffix
        valid_suffixes: Tuple[str, ...] = (".fcstd", ".FCStd")
        if suffix not in valid_suffixes:
            raise RuntimeError(
                f"{self.FullPath}: '{self.FilePath}' suffix '{suffix}' "
                f"is not a valid suffix {valid_suffixes}.")  # pragma: no unit cover

        # Verify that *children* have valid types:
        # TODO: Is *children* always empty?
        children: Tuple[FabNode, ...] = self.Children
        child: FabNode
        for child in children:
            if not isinstance(child, (FabAssembly, Fab_Group, FabSolid)):  # pragma: no unit cover
                raise RuntimeError(
                    f"{self.FullPath}: {child.FullPath} is not a {type(child)}, "
                    "not FabAssembly/Fab_Group/FabSolid")  # pragma: no unit cover

    # FabDocument.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return FabProject JSON structure."""
        json: Dict[str, Any] = super().to_json()
        json["Kind"] = "Document"
        json["_FilePath"] = str(self.FilePath)
        return json

    # FabDocument.post_produce1():
    def post_produce1(self, produce_state: Fab_ProduceState, tracing: str = "") -> None:
        """Perform FabDocument phase 1 post production."""
        tracing = self.Tracing  # Ignore *tracing* argument.
        if tracing:
            print(f"{tracing}<=>FabDocument({self.Label}).post_produce1(*, *)")

    # FabDocument.post_produce2():
    def post_produce2(self, produce_state: Fab_ProduceState) -> None:
        """Close the FabDocument."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}<=>FabDocument({self.Label}).post_produce2()")

    # FabDocument.is_document():
    def is_document(self) -> bool:
        """ Return True if FabNode is a Fab_Group."""
        return True  # All other FabNode's return False.  # pragma: no unit cover

    # FabDocument.produce():
    def produce(self) -> None:
        """Produce FabDocument."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}<=>FabDocument.produce('{self.Label}', *)")

    # FabDocument._unit_tests()
    @staticmethod
    def _unit_tests() -> None:
        pass


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
        return self._Errors  # pragma: no unit cover

    # FabProject.is_project():
    def is_project(self) -> bool:
        """ Return True if FabNode is a Fab_Group."""
        return True  # All other FabNode's return False.  # pragma: no unit cover

    # FabProject.new():
    @classmethod
    def new(cls, name: str) -> "FabProject":
        """Create a new root FabProject."""
        # print(f"=>FabProject.new({name}).new()")
        project = cls(
            name, cast(FabNode, None))  # Magic creation of  FabProject.  # pragma: no unit cover
        # print(f"<=Project.new({name})=>{project}")
        return project  # pragma: no unit cover

    # FabProject.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return FabProject JSON structure."""
        json: Dict[str, Any] = super().to_json()
        json["Kind"] = "Project"
        return json

    # FabProject.run():
    def run(self, step_directory: Optional[Path] = None) -> None:
        # Shared variables:
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>Project({self.Label}).run()")

        # Phase 1: Iterate over tree in constraint mode:
        if tracing:
            print("")
            print(f"{tracing}Project({self.Label}).run(): Phase 1: Constraint Propagation")

        error: str
        index: int
        name: str
        node: FabNode
        errors: List[str] = self._Errors

        produce_state: Fab_ProduceState = Fab_ProduceState(Path("/tmp"))
        if step_directory is None:
            step_directory = Path("/tmp")
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
                node.pre_produce(produce_state)
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

            fab_steps: Fab_Steps = Fab_Steps(Path("/tmp"))
            fab_steps.scan()
            if tracing:
                print(f"{tracing}Phase 2A: post_produce1(*, '{step_directory}'):")
            del errors[:]  # Clear *errors*
            for node in all_nodes:
                node.post_produce1(produce_state)
            fab_steps.flush_inactives()

            if tracing:
                print(f"{tracing}Phase 2b: post_produce2():")
            for node in reversed(all_nodes):
                node.post_produce2(produce_state)

        top_json: Dict[str, Any] = self.to_json()
        json_file: IO[str]
        with open(f"/tmp/{self.Label}.json", "w") as json_file:
            json_file.write(json.dumps(top_json, indent=2, sort_keys=True))

        # Output any *errors*:
        if errors:  # pragma: no unit cover
            print("Construction Errors:")
            # Mypy currently chokes on: `for index, error in enumerate(errors):`
            # with `error: "int" not callable`.  Weird.
            for index in range(len(errors)):  # pragma: no unit cover
                error = errors[index]
                print(f"  Error[{index}]: {error}")
        if tracing:
            print(f"{tracing}<=Project({self.Label}).run()")

    # FabProject._unit_tests()
    @staticmethod
    def _unit_tests() -> None:
        pass


# main():
def main() -> None:
    """Run Project unit tests."""
    Fab_Group._unit_tests()
    FabProject._unit_tests()
    FabDocument._unit_tests()
    FabAssembly._unit_tests()


if __name__ == "__main__":
    main()
