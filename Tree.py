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

ModelNode implement

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

# <--------------------------------------- 100 characters ---------------------------------------> #

import os
import sys

assert sys.version_info.major == 3  # Python 3.x
assert sys.version_info.minor == 8  # Python 3.8
sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])

from dataclasses import dataclass, field
from typing import cast, Any, Dict, List, Optional, Set, Tuple, Union


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
        # if tracing:
        #     print(f"{tracing}{dir(self)=}")

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
            print(f"{tracing}<=ModelNode._setup('{self.Name}', '{parent.Name}')")

    def __getitem__(self, key: Union[str, Tuple[str, type]]) -> Any:
        """Return value using a relative path with option type."""
        tracing: str = ""  # Manually set to debug.
        if tracing:
            print(f"=>ModelNode.__get_item__({key})")

        # Perform argument checking:
        path: str
        desired_type: Optional[type] = None
        if isinstance(key, tuple):
            if len(key) != 2:
                raise ValueError(f"ModelNode key {key} tuple must be of length 2")
            path = key[0]
            if not isinstance(path, str):
                raise ValueError("ModelNode key {path} path is not a string")
            desired_type = key[1]
            if not isinstance(desired_type, type):
                raise ValueError("ModelNode desired type {desired_type } is not a type")
        elif isinstance(key, str):
            path = key
        else:
            raise ValueError(f"ModeNode key {key} is neither a string nor a tuple")

        # Move *focus* from *self* by parsing *path*:
        focus: ModelNode = self
        size: int = len(path)
        index: int = 0
        while index < size:
            dispatch: str = path[index]
            if tracing:
                print(f"ModelNode.__get_item__(): {path[index:]=} {focus=}")
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
                    raise ValueError(f"Path '{path}' not able to find '{name}'")
            else:
                raise ValueError(f"Path '{path}' is not properly formatted")
        if desired_type:
            if not isinstance(focus, desired_type):
                raise ValueError(f"Path '{path}' is of type {type(focus)} not {desired_type}")
        if tracing:
            print(f"=>ModelNode.__get_item__({key})=>{focus}")
        return focus


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
        self._setup(self)
        # print(f"<=Model_Root.__post_init__():")

    def configure_constraints(self, maximum_iterations: int = 20,
                              verbosity: int = 4, tracing: str = "") -> None:
        """Configure the ModelNode tree until is constraints are stable.

        Arguments:
        * *maximum_iterations* (int): The maximum number of iterations (default: 20).
        * *verbosity* (int): Verbosity level:
          0: No messages.
          1: Iteration messages only.
          N: Iteration messages with N-1 of the differences:

        """
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>ModelRoot.configure_constraints()")

        previous_values: Set[str] = set()
        count: int
        for count in range(maximum_iterations):
            current_values: Set[str] = set(self.configure({}, next_tracing))
            difference_values: Set[str] = previous_values ^ current_values
            if tracing:
                print(f"{tracing}Iteration[{count}]: {sorted(previous_values)=}")
                print(f"{tracing}Iteration[{count}]:  {sorted(current_values)=}")
                print(f"{tracing}Iteration[{count}]: {len(difference_values)} Differences.")
                print("")

            # Deal with *verbosity*:
            if verbosity >= 1:
                print(f"Configure[{count}]: {len(difference_values)} differences:")
            if verbosity >= 2:
                sorted_difference_values: List[str] = sorted(tuple(difference_values))
                index: int
                difference: str
                for index, difference in enumerate(sorted_difference_values[:verbosity]):
                    print(f"  Difference[{index}]: {difference}")

            if not difference_values:
                break
            previous_values = current_values

        if tracing:
            print(f"{tracing}<=ModelRoot.configure_constraints()")


@dataclass
class MyNode1(ModelNode):
    """MyNode1: First ModelNode."""

    A: int = 0

    def configure(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Configure MyNode1."""
        if tracing:
            print(f"{tracing}=>MyNode1.configure('{self.Name}', {context}")
        assert isinstance(self.Parent, ModelRoot)
        b: int = cast(int, self[("^MyNode2.B", int)])
        c: int = cast(int, self[("^MyNode3.C", int)])
        self.A = b + c
        updates: Tuple[str, ...] = (f"{self.FullPath}:A:{self.A}",)
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
        c: int = cast(int, self[("^MyNode3.C", int)])
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
        updates: Tuple[str] = (f"{self.FullPath}:C:{self.C}",)
        if tracing:
            print(f"{tracing}<=MYNode2.configure('{self.Name}', {context}=>{updates}")
        return updates


def _unit_tests(tracing: str = "") -> None:
    """Run Unit tests on ModelNode."""
    if tracing:
        print(f"{tracing}=>_unit_tests()")

    my_node1: MyNode1 = MyNode1("MyNode1")
    my_node2: MyNode2 = MyNode2("MyNode2")
    my_node3: MyNode3 = MyNode3("MyNode3")
    root: ModelRoot = ModelRoot("Root", (my_node1, my_node2, my_node3))
    assert isinstance(root, ModelRoot)

    root.configure_constraints()  # tracing=next_tracing)

    if tracing:
        print(f"{tracing}=>_unit_tests()")


if __name__ == "__main__":
    _unit_tests(" ")
