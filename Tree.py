#!/usr/bin/env python3
"""
Tree: ModFab tree management.

The Tree package provides a tree of nodes that mostly corresponds to a FreeCAD tree
as shown in the FreeCAD model view.

The base class is ModFabNode organized as follows:

* ModFabNode: Tree node base class.
  * ModFabRoot: The Root of the tree.
  * ModFabGroup: A Group of ModFabNode's in a tree.
    * ModFabFile: A Node that corresponds to a `.fcstd` file.
    * ModFabAssembly: A group of ModFabAssembly's and/or ModFabPart's.  (Defined in ??)
  * ModFabPart: A physical part that is modeled.  (Defined in Part)
  * ModFabLink: ???

The Tree enforces the following constraints:
* Each ModFabNode name must be compatible with a Python variable name
  (i.e. upper/lower letters, digits, and underscores with the character being a letter.)
* All of the children of a ModFabNode must have distinct names.
* A node may occur only once in the Tree (i.e. DAG = Direct Acyclic Graph.)
* The ModFabRoot must be named 'Root'.

Each ModFabNode has a *FullPath* property which is string that contains the ModFabNode Names
from the ModFabRoot downwards separated by a '.'.  The "Root." is skipped because it is redundant.
Each ModFabNode has an Parent attribute that specifies the parent ModFabNode

ModFabNode implement

The ModFabNode base class implements three recursive methods:

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
  The configuration phase is where constraints get propagated between ModFabNode's.  Each
  ModFabNode recomputes its configuration values.  It can do this by reading other values
  from ModFabNode's elsewhere in ModFabRoot tree then computing new values.  This is done
  repeatably until no more configuration values change or until it is pretty clear that
  there is cyclic dependency will not converge.  When convergence fails, the list of
  configuration values that did not stabilize are presented.  If there are no convergence
  issues, the next phase occurs.
* Check Phase:
  The check phase recursively performs sanity checking for each ModFabNode in the tree.
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
# ModFabNode:
class ModFabNode(object):
    """ModFabNode: Represents one node in the tree.

    Attributes:
    * *Name* (str): The ModFabNode name.
    * *Parent* (ModFabNode): The ModFabNode parent.
    * *ChildrenNodes* (Tuple[ModFabNode, ...): The children ModFabNode's.
    * *FullPath* (str):  The ModFabNode full path.

    """

    Name: str
    Children: Tuple["ModFabNode", ...] = field(repr=False, default=())
    ChildrenNames: Tuple[str, ...] = field(init=False)
    Parent: "ModFabNode" = field(init=False, repr=False)
    FullPath: str = field(init=False)

    # ModFabNode.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing ModFabNode."""
        # print(f"=>ModFabNode.__post_init__(): {self.Name=}")
        if not ModFabNode._is_valid_name(self.Name):
            raise ValueError(
                f"ModFabNode name '{self.Name}' is not alphanumeric/underscore "
                "that starts with a letter")

        # Initialize the remaining fields to bogus values that get updated by the _setup() method.
        self.ChildrenNames = ()
        self.FullPath = "??"
        self.Parent = self
        # print(f"<=ModFabNode.__post_init__()")

    # ModFabNode.check():
    def check(self, context: Dict[str, Any]) -> Tuple[str, ...]:
        """Check ModFabNode for errors."""
        errors: List[str] = []
        child_node: "ModFabNode"
        for child_node in self.Children:
            errors.extend(child_node.check(context.copy()))
        return tuple(errors)

    # ModFabNode.configure():
    def configure(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Configure ModFabNode."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>ModFabNode.configure('{self.Name}', {context})")

        current_values: List[str] = []
        child: "ModFabNode"
        for child in self.Children:
            current_values.extend(child.configure(context.copy(), tracing=next_tracing))

        if tracing:
            print(f"{tracing}<=ModFabNode.configure('{self.Name}', {context})=>{current_values}")
        return tuple(current_values)

    # ModFabNode.get_configurations():
    def get_configurations(self, attribute_names: Tuple[str, ...]) -> Tuple[str, ...]:
        """Return configurations strings for named attributes."""
        if not isinstance(attribute_names, tuple):
            raise ValueError(f"Attribute names is not a tuple (of strings)")
        configurations: List[str] = []
        attribute_name: str
        for attribute_name in attribute_names:
            if not isinstance(attribute_name, str):
                raise ValueError(f"Atribute name {attribute_name} is not a string")
            if not hasattr(self, attribute_name):
                raise ValueError(f"ModFabNode {self} does not have attribute '{attribute_name}'")
            value: Any = getattr(self, attribute_name)
            configurations.append(f"{self.FullPath}.{attribute_name}.{value}")
        return tuple(configurations)

    # ModFabNode.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Produce ModFabNode."""
        errors: List[str] = []
        child: "ModFabNode"
        for child_node in self.Children:
            errors.extend(child_node.produce(context.copy()))
        return tuple(errors)

    @staticmethod
    # ModFabNode._is_valid_name():
    def _is_valid_name(name: str) -> bool:
        """Return whether a name is valid or not."""
        no_underscores: str = name.replace("_", "")
        return no_underscores.isalnum() and no_underscores[0].isalpha()

    # ModFabNode._setup():
    def _setup(self, parent: "ModFabNode", tracing: str = "") -> None:
        """Recursively setup the ModFabNode tree."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>ModFabNode._setup('{self.Name}', '{parent.Name}')")
            print(f"{tracing}{self.Children=}")

        # A ModFabRoot is treated a bit specially
        if isinstance(self, ModFabRoot):
            self.Name = "Root"
            self.Parent = self
            self.FullPath = ""
        else:
            self.Parent = parent
            self.FullPath = f"{parent.FullPath}{self.Name}"
        if tracing:
            print(f"{tracing}{self.Parent=}")

        # Collect all of children ModFabNode's into *children_table*, checking for duplicates:
        children_table: Dict[str, ModFabNode] = {}
        name: str
        child: ModFabNode
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

        # Now look for ModFabNode's that are already attributes and add them to *children_table*:
        obj: Any
        for name, obj in self.__dict__.items():
            if name == "Parent":
                pass  # The Parent node causes infinite recursion.
            elif name.startswith("_"):
                pass  # Private nodes are, well, private.
            elif isinstance(obj, ModFabNode):
                # Simple attribute ModFabNode:
                if name not in children_table:
                    children_table[name] = obj
            # TODO: search sequences and dictionaries:

        # Make sure that each *child* is a ModFabNode attribute:
        for child in self.Children:
            if tracing:
                print(f"{tracing}Child[{child.Name}]")
            name = child.Name
            if hasattr(self, name):
                previous_node: ModFabNode = getattr(self, name)
                if child is not previous_node:
                    # Node names match, but they are not the same.
                    raise RuntimeError(f"Two ModFabNode's named '{child.Name}' were found")
                # else: it is already an attribute.
            else:
                setattr(self, name, child)
        # if tracing:
        #     print(f"{tracing}{dir(self)=}")

        # Now setup each *child*:
        names: Tuple[str, ...] = tuple(children_table.keys())
        children: List[ModFabNode] = []
        for name in names:
            child = children_table[name]
            children.append(child)
            child._setup(self, tracing=next_tracing)
        self.Children = tuple(children)
        self.ChildrenNames = tuple(names)

        if tracing:
            print(f"{tracing}<=ModFabNode._setup('{self.Name}', '{parent.Name}')")

    def __getitem__(self, key: Union[str, Tuple[str, type]]) -> Any:
        """Return value using a relative path with option type."""
        tracing: str = ""  # Manually set to debug.
        if tracing:
            print(f"=>ModFabNode.__get_item__({key})")

        # Perform argument checking:
        path: str
        desired_type: Optional[type] = None
        if isinstance(key, tuple):
            if len(key) != 2:
                raise ValueError(f"ModFabNode key {key} tuple must be of length 2")
            path = key[0]
            if not isinstance(path, str):
                raise ValueError("ModFabNode key {path} path is not a string")
            desired_type = key[1]
            if not isinstance(desired_type, type):
                raise ValueError("ModFabNode desired type {desired_type } is not a type")
        elif isinstance(key, str):
            path = key
        else:
            raise ValueError(f"ModeNode key {key} is neither a string nor a tuple")

        # Move *focus* from *self* by parsing *path*:
        focus: ModFabNode = self
        size: int = len(path)
        index: int = 0
        while index < size:
            dispatch: str = path[index]
            if tracing:
                print(f"ModFabNode.__get_item__(): {path[index:]=} {focus=}")
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
            print(f"=>ModFabNode.__get_item__({key})=>{focus}")
        return focus


@dataclass
# ModFabRoot:
class ModFabRoot(ModFabNode):
    """ModFabRoot: The Root mode a ModFabNode tree."""

    # ModFabRoot.__post_init__():
    def __post_init__(self) -> None:
        """Process ModFabRoot."""
        # print(f"=>ModFab_Root.__post_init__():")
        super().__post_init__()
        if self.Name != "Root":
            raise ValueError("The Root node must be named root rather than '{self.Name}'")
        self._setup(self)
        # print(f"<=ModFab_Root.__post_init__():")

    def configure_constraints(self, maximum_iterations: int = 20,
                              verbosity: int = 4, tracing: str = "") -> None:
        """Configure the ModFabNode tree until is constraints are stable.

        Arguments:
        * *maximum_iterations* (int): The maximum number of iterations (default: 20).
        * *verbosity* (int): Verbosity level:
          0: No messages.
          1: Iteration messages only.
          N: Iteration messages with N-1 of the differences:

        """
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>ModFabRoot.configure_constraints()")

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
            print(f"{tracing}<=ModFabRoot.configure_constraints()")


@dataclass
class MyNode1(ModFabNode):
    """MyNode1: First ModFabNode."""

    A: int = 0

    def configure(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Configure MyNode1."""
        if tracing:
            print(f"{tracing}=>MyNode1.configure('{self.Name}', {context}")
        assert isinstance(self.Parent, ModFabRoot)
        b: int = cast(int, self[("^MyNode2.B", int)])
        c: int = cast(int, self[("^MyNode3.C", int)])
        self.A = b + c
        configurations: Tuple[str, ...] = self.get_configurations(("A",))
        if tracing:
            print(f"{tracing}=>MyNode1.configure('{self.Name}', {context})=>{configurations}")
        return configurations


@dataclass
class MyNode2(ModFabNode):
    """MyNode1: First ModFabNode."""

    B: int = 0

    def configure(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Configure MyNode1."""
        if tracing:
            print(f"{tracing}=>MyNode2.configure('{self.Name}', {context}")
        c: int = cast(int, self[("^MyNode3.C", int)])
        self.B = c + 1
        configurations: Tuple[str, ...] = self.get_configurations(("B",))
        if tracing:
            print(f"{tracing}<=MyNode2.configure('{self.Name}', {context}=>{configurations}")
        return configurations


@dataclass
class MyNode3(ModFabNode):
    """MyNode1: First ModFabNode."""

    C: int = 1

    def configure(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Configure MyNode1."""
        if tracing:
            print(f"{tracing}=>MYNode1.configure('{self.Name}', {context}")
        self.C = 1
        configurations: Tuple[str, ...] = self.get_configurations(("C",))
        if tracing:
            print(f"{tracing}<=MYNode2.configure('{self.Name}', {context}=>{configurations}")
        return configurations


def _unit_tests(tracing: str = "") -> None:
    """Run Unit tests on ModFabNode."""
    if tracing:
        print(f"{tracing}=>_unit_tests()")

    my_node1: MyNode1 = MyNode1("MyNode1")
    my_node2: MyNode2 = MyNode2("MyNode2")
    my_node3: MyNode3 = MyNode3("MyNode3")
    root: ModFabRoot = ModFabRoot("Root", (my_node1, my_node2, my_node3))
    assert isinstance(root, ModFabRoot)

    root.configure_constraints()  # tracing=next_tracing)

    if tracing:
        print(f"{tracing}=>_unit_tests()")


if __name__ == "__main__":
    _unit_tests(" ")
