#!/usr/bin/env python3
"""
Tree: Model tree management.

The Tree package provides a tree of nodes that mostly corresponds to a FreeCAD tree
as shown in the FreeCAD model view.

The base class is ModelNode organized as follows:

* ModelNode: Tree node base class.
  * ModelRoot: The Root of the tree.
  * ModelGroup: A Group of ModelNode's in a tree.
    * ModelFile: A Node that corresponds to a `.fcstd` file.
    * ModelAssembly: A group of ModelAssembly's and/or ModelPart's.  (Defined in ??)
  * ModelPart: A physical part that is modeled.  (Defined in Part)
  * ModelLink: ???

The Tree enforces the following constraints:
* Each ModelNode name must be compatible with a Python variable name
  (i.e. upper/lower letters, digits, and underscores with the character being a letter.)
* All of the children of a ModelNode must have distinct names.
* A node may occur only once in the Tree (i.e. DAG = Direct Acyclic Graph.)
* The ModelRoot must be named 'Root'.

Each ModelNode has a *FullPath* property which is string that contains the ModelNode Names
from the ModelRoot downwards separated by a '.'.  The "Root." is skipped because it is redundant.
Each ModelNode has an Parent attribute that specifies the parent ModelNode

The ModelNode base class implements three recursive methods:

* configure(context) -> Tuple[str, ...]:
  Recursively propagate configuration values during the configuration phase.
  All configured values are returns a tuple of strings of the form "FULL_NAME:PROPERTY_NAME:VALUE".
* check(context) -> Tuple[str, ...]:
  Recursively checks for errors during the check phase and returns a tuple of error strings.
* build(context) -> Tuple[str, ...]:
  Recursively used to build the model and generate any production files (CNC, STL, DWG, etc.)
  Any errors and warnings are returned as a tuple of strings.

All of these methods pass a *context* dictionary from level to level.  The rule is that anything
can be added to the dictionary.  In order to prevent *context* dictionary pollution, each
level makes a shallow dictionary copy (i.e. context.copy()).

There are three phases:
* Configuration Phase:
  The configuration phase is where constraints get propagated between ModelNode's.  Each
  ModelNode recomputes its configuration values.  It can do this by reading other values
  from ModelNode's elsewhere in ModelRoot tree then computing new values.  This is done
  repeatably until no more configuration values change or until it is pretty clear that
  there is cyclic dependency will not converge.  When convergence fails, the list of
  configuration values that did not stabilize are presented.  If there are no convergence
  issues, the next phase occurs.
* Check Phase:
  The check phase recursively performs sanity checking for each ModelNode in the tree.
  The result is a list of error messages.  If the are no errors, the next phase occurs.
* Build Phase:
  The build phase recursively performs the build operations.  This includes generating
  the FreeCAD solids/assemblies and the associated output files.

"""

from typing import Any, Dict, List, Set, Tuple

# <--------------------------------------- 100 characters ---------------------------------------> #

import os
import sys

assert sys.version_info.major == 3  # Python 3.x
assert sys.version_info.minor == 8  # Python 3.8
sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])

from dataclasses import dataclass, field


@dataclass
# ModelNode:
class ModelNode(object):
    """ModelNode: Represents one node in the tree.

    Attributes:
    * *Name* (str): The ModelNode name.
    * *Parent* (ModelNode): The ModelNode parent.
    * *ChildrenNodes* (Tuple[ModelNode, ...): The children ModelNode's.
    * *FullPath* (str):  The ModelNode full path.

    """

    Name: str
    Children: Tuple["ModelNode", ...] = field(repr=False, default=())
    ChildrenNames: Tuple[str, ...] = field(init=False)
    Parent: "ModelNode" = field(init=False, repr=False)
    FullPath: str = field(init=False)

    # ModelNode.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing ModelNode."""
        # print(f"=>ModelNode.__post_init__(): {self.Name=}")
        if not ModelNode._is_valid_name(self.Name):
            raise ValueError(
                f"ModelNode name '{self.Name}' is not alphanumeric/underscore starts with a letter")

        # Initialize the remaining fields to bogus values that get updated by the _setup() method.
        self.ChildrenNames = ()
        self.FullPath = "??"
        self.Parent = self
        # print(f"<=ModelNode.__post_init__()")

    # ModelNode.check():
    def check(self, context: Dict[str, Any]) -> Tuple[str, ...]:
        """Check ModelNode for errors."""
        errors: List[str] = []
        child_node: "ModelNode"
        for child_node in self.Children:
            errors.extend(child_node.check(context.copy()))
        return tuple(errors)

    # ModelNode.configure():
    def configure(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Configure ModelNode."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>ModelNode.configure('{self.Name}', {context})")

        current_values: List[str] = []
        child: "ModelNode"
        for child in self.Children:
            current_values.extend(child.configure(context.copy(), tracing=next_tracing))

        if tracing:
            print(f"{tracing}<=ModelNode.configure('{self.Name}', {context})=>{current_values}")
        return tuple(current_values)

    # ModelNode.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Produce ModelNode."""
        errors: List[str] = []
        child: "ModelNode"
        for child_node in self.Children:
            errors.extend(child_node.produce(context.copy()))
        return tuple(errors)

    @staticmethod
    # ModelNode._is_valid_name():
    def _is_valid_name(name: str) -> bool:
        """Return whether a name is valid or not."""
        no_underscores: str = name.replace("_", "")
        return no_underscores.isalnum() and no_underscores[0].isalpha()

    # ModelNode._setup():
    def _setup(self, parent: "ModelNode", tracing: str = "") -> None:
        """Recursively setup the ModelNode tree."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
            print(f"{tracing}=>ModelNode._setup('{self.Name}', '{parent.Name}')")
            print(f"{tracing}{self.Children=}")

        # A ModelRoot is treated a bit specially
        if isinstance(self, ModelRoot):
            self.Name = "Root"
            self.Parent = self
            self.FullPath = ""
        else:
            self.Parent = parent
            self.FullPath = f"{parent.FullPath}{self.Name}"
        if tracing:
            print(f"{tracing}{self.Parent=}")

        # Collect all of children ModelNode's into *children_table*, checking for duplicates:
        children_table: Dict[str, ModelNode] = {}
        name: str
        child: ModelNode
        for child in self.Children:
            name = child.Name
            if name in children_table:
                if children_table[name] is child:
                    raise ValueError(f"Node '{name}' is duplicated.'")
                else:
                    raise ValueError(f"Two different nodes named {name} encountered.")
            else:
                children_table[name] = child
        if tracing:
            print(f"{tracing}{children_table=}")

        # Now look for ModelNode's that are already attributes and add them to *children_table*:
        obj: Any
        for name, obj in self.__dict__.items():
            if name == "Parent":
                pass  # The Parent node causes infinite recursion.
            elif name.startswith("_"):
                pass  # Private nodes are, well, private.
            elif isinstance(obj, ModelNode):
                # Simple attribute ModelNode:
                if name not in children_table:
                    children_table[name] = obj
            # TODO: search sequences and dictionaries:

        # Make sure that each *child* is a ModelNode attribute:
        for child in self.Children:
            if tracing:
                print(f"{tracing}Child[{child.Name}]")
            name = child.Name
            if hasattr(self, name):
                previous_node: ModelNode = getattr(self, name)
                if child is not previous_node:
                    # Node names match, but they are not the same.
                    raise RuntimeError(f"Two ModelNode's named '{child.Name}' were found")
                # else: it is already an attribute.
            else:
                setattr(self, name, child)
        if tracing:
            print(f"{tracing}{dir(self)=}")

        # Now setup each *child*:
        names: Tuple[str, ...] = tuple(children_table.keys())
        children: List[ModelNode] = []
        for name in names:
            child = children_table[name]
            children.append(child)
            child._setup(self, tracing=next_tracing)
        self.Children = tuple(children)
        self.ChildrenNames = tuple(names)

        if tracing:
            print(f"{tracing}<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
            print(f"{tracing}<=ModelNode._setup('{self.Name}', '{parent.Name}')")


@dataclass
# ModelRoot:
class ModelRoot(ModelNode):
    """ModelRoot: The Root mode a ModelNode tree."""

    # ModelRoot.__post_init__():
    def __post_init__(self) -> None:
        """Process ModelRoot."""
        # print(f"=>Model_Root.__post_init__():")
        super().__post_init__()
        if self.Name != "Root":
            raise ValueError("The Root node must be named root rather than '{self.Name}'")
        # print(f"<=Model_Root.__post_init__():")


@dataclass
class MyNode1(ModelNode):
    """MyNode1: First ModelNode."""

    A: int = 0

    def configure(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Configure MyNode1."""
        if tracing:
            print(f"{tracing}=>MyNode1.configure('{self.Name}', {context}")
        assert isinstance(self.Parent, ModelRoot)
        b: int = self.Parent.MyNode2.B  # type: ignore
        c: int = self.Parent.MyNode3.C  # type: ignore
        self.A = b + c
        updates: Tuple[str, ...] = ("f{self.FullPath}:A:{self.A})",)
        if tracing:
            print(f"{tracing}=>MyNode1.configure('{self.Name}', {context})=>{updates}")
        return updates


@dataclass
class MyNode2(ModelNode):
    """MyNode1: First ModelNode."""

    B: int = 0

    def configure(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str]:
        """Configure MyNode1."""
        if tracing:
            print(f"{tracing}=>MyNode2.configure('{self.Name}', {context}")
        c: int = self.Parent.MyNode3.C  # type:ignore
        self.B = c + 1
        updates: Tuple[str] = (f"{self.FullPath}:B:{self.B}",)
        if tracing:
            print(f"{tracing}<=MyNode2.configure('{self.Name}', {context}=>{updates}")
        return updates


@dataclass
class MyNode3(ModelNode):
    """MyNode1: First ModelNode."""

    C: int = 1

    def configure(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str]:
        """Configure MyNode1."""
        if tracing:
            print(f"{tracing}=>MYNode1.configure('{self.Name}', {context}")
        self.C = 1
        updates: Tuple[str] = (f"{self.FullPath}:C:,{str(self.C)}",)
        if tracing:
            print(f"{tracing}<=MYNode2.configure('{self.Name}', {context}=>{updates}")
        return updates


def _unit_tests(tracing: str = "") -> None:
    """Run Unit tests on ModelNode."""
    next_tracing: str = tracing + " " if tracing else ""
    if tracing:
        print(f"{tracing}=>_unit_tests()")

    my_node1: MyNode1 = MyNode1("MyNode1")
    my_node2: MyNode2 = MyNode2("MyNode2")
    my_node3: MyNode3 = MyNode3("MyNode3")

    if tracing:
        print("################################################################")
        print(f"{tracing}Creating ModeRoot...")
        print(f"{tracing}=>ModelRoot()")
    root: ModelRoot = ModelRoot("Root", (my_node1, my_node2, my_node3))
    if tracing:
        print(f"{tracing}<=ModelRoot()")
    assert isinstance(root, ModelRoot)

    print("ModelRoot._unit_tests(): 1")
    root._setup(root, next_tracing)
    print("ModelRoot._unit_tests(): 2")
    previous_values: Set[str] = set()
    count: int
    for count in range(5):
        current_values: Set[str] = set(root.configure({}, next_tracing))
        difference_values: Set[str] = previous_values ^ current_values
        if tracing:
            print(f"{tracing}Iteration[{count}]: {sorted(previous_values)=}")
            print(f"{tracing}Iteration[{count}]:  {sorted(current_values)=}")
            print(f"{tracing}Iteration[{count}]: {len(difference_values)} Differences.")
            print("")
        if not difference_values:
            break
        previous_values = current_values

    if tracing:
        print(f"{tracing}=>_unit_tests()")


# # ModelRoot:
# class ModelRoot(ModelNode):
#     """ModeRoot: The root ModelNode of the ModelNode Tree."""
#     pass
#
#     # ApexNode.configure_and_build():
#     def configure_and_build(self, document: "App.Document",
#                             count: int = 25, tracing: str = "") -> None:
#         """Recursively configure and build the entire ApexNode tree.
#
#         * Arguments:
#           *count* (int): The maximum number of configuration iterations:
#         """
#         next_tracing: str = tracing + " " if tracing else ""
#         if tracing:
#             print(f"{tracing}=>ApexNode.configure_and_build('{self.full_path}')")
#         context: ApexContext = ApexContext(document)
#         differences: Tuple[Tuple[str, Any, Any], ...] = self._configure_all(count=count)
#         if differences:
#             difference: Tuple[str, Any, Any]
#             difference_names: Tuple[str, ...] = tuple(
#                 [difference[0]
#                  for difference in differences]
#             )
#             print(f"Constraint issues: {difference_names}")  # pragma: no unit cover
#         else:
#             self._build_all(context, tracing=next_tracing)
#         if tracing:
#             print(f"{tracing}<=ApexNode.configure_and_build('{self.full_path}')")
#
#     def _build_all(self, context: ApexContext, tracing: str = "") -> None:
#         """Recursively build an ApexNode tree."""
#         next_tracing: str = tracing + " " if tracing else ""
#         if tracing:
#             print(f"{tracing}=>ApexNode._build_all('{self.full_path}')")
#
#         if hasattr(self, "build"):
#             self.build(context, tracing=next_tracing)
#
#         name: str
#         value: Any
#         for name, value in self.__dict__.items():
#             if not name.startswith("_") and isinstance(value, ApexNode):
#                 value._build_all(context, tracing=next_tracing)
#         if tracing:
#             print(f"{tracing}<=ApexNode._build_all('{self.full_path}')")
#
#     def _configure_all(self,
#                        count: int = 25, verbose: bool = True) -> Tuple[Tuple[str, Any, Any], ...]:
#         """Recursively configure an ApexNode Tree.
#
#         * Arguments:
#           * *count* (int): The maximum number of iterations to try.
#           * *verbose* (bool): If True, print a 1 line progress message for each iteration.
#
#         * Returns:
#           * Return (Tuple[Tuple[str, Any, Any], ...]) which is a sorted tuple of differences,
#             where [0] is the name, [1] is the previous value, and [2] is the current value.
#         """
#         differences: List[Tuple[str, Any, Any]]
#         previous_key_values: Dict[str, Any] = {}
#         current_key_values: Dict[str, Any] = {}
#         index: int
#         for index in range(count):
#             # Recursively collect configurable values:
#             previous_key_values = current_key_values
#             current_key_values = {}
#             self._configure_helper(current_key_values)
#
#             # Collect each difference onto *differences*:
#             differences = []
#             key: str
#             previous_keys: Set[str] = set(previous_key_values)
#             current_keys: Set[str] = set(current_key_values)
#             for key in previous_keys - current_keys:
#                 differences.append((key, previous_key_values[key], None))  # pragma: no unit cover
#             for key in current_keys - previous_keys:
#                 differences.append((key, None, current_key_values[key]))
#             for key in previous_keys & current_keys:
#                 previous_value: Any = previous_key_values[key]
#                 current_value: Any = current_key_values[key]
#                 if type(previous_value) != type(current_value) or previous_value != current_value:
#                     differences.append((key, previous_value, current_value))
#
#             if verbose:
#                 print(f"Configure[{index}]: {len(differences)} differences.")
#             if not differences:
#                 break
#
#         # Sort *differences* and print warning for
#         if differences:
#             differences.sort(key=lambda difference: difference[0])  # Sort on first key.
#             difference: Tuple[str, Any, Any]
#             difference_keys: Tuple[str, ...] = tuple(
#                 [difference[0] for difference in differences])
#             print(f"configure[FINAL]: The following are not stable: {difference_keys}")
#         return tuple(differences)
#
#     def _configure_helper(self, values: Dict[str, Any]) -> None:
#         """Recursively configure an ApexNode tree."""
#         if hasattr(self, "configure"):
#             self.configure()
#
#         ignore_names: Tuple[str, ...] = ("", "name", "parent", "full_path", "configure")
#         name: str
#         value: Any
#         for name, value in self.__dict__.items():
#             if name not in ignore_names and name[0] != "_":
#                 if isinstance(value, (bool, int, float, Vector)):
#                     values[f"{self.full_path}:{name}"] = value
#                 elif isinstance(value, ApexNode):
#                     value._configure_helper(values)
#
#
# def unit_tests() -> None:
#     """Run unit tests for ApexNode."""
#     class Box(ApexNode):
#         def __init__(self, name: str, dx: float, dy: float, dz: float, dw: float) -> None:
#             super().__init__(name, None)
#             self.dx: float = dx
#             self.dy: float = dy
#             self.dz: float = dz
#             self.dw: float = dw
#             # For testing, use 0 (int) instead of 0.0 (float)to cause an extra iteration:
#             self.skin_volume: float = 0
#             self.outer_volume: float = 0
#             self.inner_volume: float = 0
#             self.tne: Vector = Vector(dx / 2.0, dy / 2.0, dz / 2.0)
#             self.bsw: Vector = Vector(-dx / 2.0, -dy / 2.0, -dz / 2.0)
#             self.bb: ApexBox = ApexBox((self.tne, self.bsw))
#             bb: ApexBox = self.bb
#
#             # x_dw: Vector = Vector(dw, 0.0, 0.0)
#             y_dw: Vector = Vector(0.0, dw, 0.0)
#             z_dw: Vector = Vector(0.0, 0.0, dw)
#
#             self.top_side: Block = Block(
#                 "Top", self, bb.TNE, bb.TSW - z_dw, "red")
#             #    "Top", bb.TNE, bb.TSW - z_dw, "red")
#             self.bottom_side: Block = Block(
#                 "Bottom", self, bb.BNE, bb.BSW + z_dw, "red")
#
#             self.north_side: Block = Block(
#                 "North", self, bb.TNE - z_dw, bb.BNW + z_dw - y_dw, "green")
#             self.south_side: Block = Block(
#                 "South", self, bb.TSE - z_dw, bb.BSW + z_dw + y_dw, "green")
#
#             self.east_side: Block = Block(
#                 "East", self, bb.TNE - z_dw - y_dw, bb.BSE + z_dw + z_dw, "blue")
#             self.west_side: Block = Block(
#                 "West", self, bb.TNW - z_dw + z_dw, bb.BSW + z_dw - z_dw, "blue")
#
#         def build(self, context: ApexContext, tracing: str = "") -> None:
#             if tracing:
#                 print(f"{tracing}<=>Box.build(*)")
#
#         def configure(self) -> None:
#             bb: ApexBox = self.bb
#             dxyz: Vector = bb.TNE - bb.BSW
#             self.skin_volume = (
#                 self.top_side.volume + self.bottom_side.volume +
#                 self.north_side.volume + self.south_side.volume +
#                 self.east_side.volume + self.west_side.volume)
#             self.outer_volume = dxyz.x * dxyz.y * dxyz.z
#             self.inner_volume = self.outer_volume - self.skin_volume
#
#     class Block(ApexNode):
#         def __init__(self, name: str, parent: ApexNode, tne: Vector, bsw: Vector,
#                      color: str = "") -> None:
#             super().__init__(name, parent)
#             assert self.parent == parent, "parent is not set?"
#             self.tne: Vector = tne
#             self.bsw: Vector = bsw
#             self.volume = 0
#
#         def configure(self):
#             dxyz: Vector = self.tne - self.bsw
#             self.volume: float = dxyz.x * dxyz.y * dxyz.z
#
#         def build(self, context: ApexContext, tracing: str = "") -> None:
#             if tracing:
#                 print(f"{tracing}<=>Block.build({self.full_path})")
#
#     # Constraints should down to zero differences with *count*=3.
#     box: ApexNode = Box("Test_Box", 20.0, 15.0, 10.0, 0.5)
#     differences: Tuple[Tuple[str, Any, Any], ...] = box._configure_all(count=3)
#     want: Tuple[Tuple[str, Any, Any], ...] = ()
#     assert differences == want, f"Got {differences} instead of {want=}"
#     document_name: str = "ApexNodeTestDocument"
#     document: App.Document = App.newDocument(document_name)
#     _ = document
#     box.configure_and_build(document_name)
#
#     # Constraints should be down to 1 difference with *count*=2:
#     box = Box("Test_Box", 30.0, 25.0, 15.0, 0.75)
#     differences = box._configure_all(count=2)
#     want = (('Test_Box:skin_volume', 0.0, 0.0),)
#     assert differences == want, f"Got {differences} instead of {want=}"
#
#     # Do some error testing:
#     try:
#         _ = box.parent == "Root"
#     except RuntimeError as error:
#         assert str(error) == "Test_Box does not have a parent"

if __name__ == "__main__":
    _unit_tests(" ")
