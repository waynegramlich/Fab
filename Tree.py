#!/usr/bin/env python3
"""
Tree: Fab tree management.

The Tree package provides a tree of nodes that mostly corresponds to a FreeCAD tree
as shown in the FreeCAD model view.

The base class is FabNode organized as follows:

* FabNode: Tree node base class (can be either a "leaf" or "interior node.)
  * FabInterior: An interior TreeNode with children.
    * FabRoot: The Root of the FabNode tree.
    * FabGroup: A Group of FabNode's in a tree.
      * FabFile: A Node that corresponds to a `.fcstd` file.
      * FabAssembly: A group of FabAssembly's and/or FabPart's.  (Defined in ??)
    * FabSolid: A physical part that is modeled.  (Defined in Solid)
    * FabLink: ???

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
from typing import Any, Dict, List, Optional, Tuple, Union


@dataclass
# FabNode:
class FabNode(object):
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

    # FabNode.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabNode."""
        # print(f"=>FabNode.__post_init__(): {self.Name=}")
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
    def _setup(self, parent: "FabNode",
               all_nodes: List["FabNode"], tracing: str = "") -> None:
        """Set up the FabNode."""
        # next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabNode._setup('{self.Name}', '{parent.Name}')")
        # A FabRoot is treated a bit specially
        if False:  # self.Parent is self:
            self.Name = "Root"
            self.FullPath = ""
        else:
            self.Parent = parent
            self.FullPath = f"{parent.FullPath}.{self.Name}" if parent.FullPath else self.Name
        all_nodes.append(self)
        if tracing:
            print(f"{tracing}<=FabNode._setup('{self.Name}', '{parent.Name}')")

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


@dataclass
# FabInterior:
class FabInterior(FabNode):
    """FabInterior: Represents A

    Attributes:
    * Inherited Attributes: *Name* (str), *FullPath* (str), *Parent* (FabNode).
    * *Children* (List[FabNode]): The children FabNode's.

    """

    Children: Tuple[FabNode, ...] = field(repr=False, default=())

    # FabInterior.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabNode."""
        # print(f"=>FabInterior.__post_init__(): {self.Name=}")

        # Initialize the remaining fields to bogus values that get updated by the _setup() method.
        super().__post_init__()
        child: Any
        index: int
        for index, child in enumerate(self.Children):
            if not isinstance(child, FabNode):
                raise ValueError(f"'{self.Name}[{index}] is {type(child)}, not FabNode")
        # print(f"<=FabInterior.__post_init__()")

    # FabNode._setup():
    def _setup(self, parent: "FabNode",
               all_nodes: List["FabNode"], tracing: str = "") -> None:
        """Set up the FabNode."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabIterator._setup('{self.Name}', '{parent.Name}', *)")

        # Initialize the Parent class.:
        super()._setup(parent, all_nodes, tracing=next_tracing)

        # Collect all of children FabNode's into *children_table*, checking for duplicates:
        children_table: Dict[str, FabNode] = {}
        name: str
        child: FabNode
        for child in self.Children:
            child._setup(self, all_nodes, tracing=next_tracing)
            child_name = child.Name
            if child_name in children_table:
                if children_table[child_name] is child:
                    raise ValueError(f"Node '{child_name}' is duplicated.'")
                else:
                    raise ValueError(f"Two different nodes named {child_name} encountered.")
            else:
                children_table[child_name] = child
                if hasattr(self, child_name):
                    raise ValueError(f"{child_name} is already an attribute.")
                setattr(self, child_name, child)

        if tracing:
            print(f"{tracing}=>FabIterator._setup('{self.Name}', '{parent.Name}', *)")


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
# class MyNode2(FabInterior):
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
    pass
