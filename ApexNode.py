#!/usr/bin/env python3
"""
ApexPart: Apex interface to FreeCAD PartDesign workbench.

The primary class is the ApexPart class.  The preferred way to create a new part is
to subclass:

     # MyClass:
     class MyClass(ApexPart.ApexPart):
        '''MyClass: ...

        Attributes:
        * *Atribute1*: ...
        '''

      def __init__(self, name: str, parent: ApexClass, other_args...) -> None:
          '''Initialize MyClass.'''
          super().__init__(self, name, parent)
          ...

      def configure(self) -> None:
          '''Configure MyClass.'''
          ...

      def build(self) -> None:
          '''Build MyClass.'''
          ...

"""

from typing import Any, Dict, List, Optional, Set, Tuple

# <--------------------------------------- 100 characters ---------------------------------------> #

import os
import sys

assert sys.version_info.major == 3  # Python 3.x
assert sys.version_info.minor == 8  # Python 3.8
sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])

import FreeCAD as App  # type: ignore
from FreeCAD import Vector  # type: ignore
import FreeCADGui as Gui  # type:ignore
from Apex import ApexPoint, ApexBox


# ApexContext:
class ApexContext:
    """Build context object for controlling build.

    Attributes:
    * *document* (App.Document): The document to work in.

    """

    def __init__(self, document_name: str) -> None:
        """Initialize context.

        Arguments:
        * *document* (App.Document): The FreeCAD document to use.

        """
        app_document: App.Document = App.getDocument(document_name)
        gui_document: Optional[Gui.Document] = None
        if App.GuiUp:
            gui_document = Gui.getDocument(document_name)

        self.document_name = document_name
        self.app_document: App.Document = app_document
        self.gui_document: Optional[Gui.Document] = gui_document


# ApexNode:
class ApexNode(object):
    """One node of ApexNode tree.

    Attributes:
    * *name* (str): The node name.
    * *parent* (ApexNode): The node parent.
    * *full_path* (str):  The node full path (e.g. "root.middle1...middleN.leaf")

    """

    def __init__(self, name: str, parent: Optional["ApexNode"]) -> None:
        """Initialize an apex Node."""
        self._name = name
        self._parent = parent

    @property
    def name(self) -> str:
        """Return the node name."""
        return self._name

    @property
    def parent(self) -> "ApexNode":
        """Return the parent ApexNode.

        * Raises:
          * RuntimeError when there is no parent.
        """
        if self._parent:
            return self._parent
        raise RuntimeError(f"{self.full_path} does not have a parent")

    @property
    def full_path(self) -> str:
        """Return the full path of ApexNode."""
        node: Optional[ApexNode] = self
        names: List[str] = []
        while node:
            names.append(node.name)
            node = node._parent
        return ".".join(reversed(names))

    # ApexNode.build():
    def build(self, context: ApexContext, tracing: str = "") -> None:
        """Build an ApexNode.

        * Arguments:
          * *context* (ApexContext): The context information for the entire build.

        The sub-class should override this method to build the node.
        """
        pass  # pragma: no unit cover

    # ApexNode.configure():
    def configure(self) -> None:
        """Configure an ApexNode.

        The sub-class should override this method to configure dimensions, etc.
        """
        pass  # pragma: no unit cover

    # ApexNode.configure_and_build():
    def configure_and_build(self, document: "App.Document",
                            count: int = 25, tracing: str = "") -> None:
        """Recursively configure and build the entire ApexNode tree.

        * Arguments:
          *count* (int): The maximum number of configuration iterations:
        """
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>ApexNode.configure_and_build('{self.full_path}')")
        context: ApexContext = ApexContext(document)
        differences: Tuple[Tuple[str, Any, Any], ...] = self._configure_all(count=count)
        if differences:
            difference: Tuple[str, Any, Any]
            difference_names: Tuple[str, ...] = tuple(
                [difference[0]
                 for difference in differences]
            )
            print(f"Constraint issues: {difference_names}")  # pragma: no unit cover
        else:
            self._build_all(context, tracing=next_tracing)
        if tracing:
            print(f"{tracing}<=ApexNode.configure_and_build('{self.full_path}')")

    def _build_all(self, context: ApexContext, tracing: str = "") -> None:
        """Recursively build an ApexNode tree."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>ApexNode._build_all('{self.full_path}')")

        if hasattr(self, "build"):
            self.build(context, tracing=next_tracing)

        name: str
        value: Any
        for name, value in self.__dict__.items():
            if not name.startswith("_") and isinstance(value, ApexNode):
                value._build_all(context, tracing=next_tracing)
        if tracing:
            print(f"{tracing}<=ApexNode._build_all('{self.full_path}')")

    def _configure_all(self,
                       count: int = 25, verbose: bool = True) -> Tuple[Tuple[str, Any, Any], ...]:
        """Recursively configure an ApexNode Tree.

        * Arguments:
          * *count* (int): The maximum number of iterations to try.
          * *verbose* (bool): If True, print a 1 line progress message for each iteration.

        * Returns:
          * Return (Tuple[Tuple[str, Any, Any], ...]) which is a sorted tuple of differences,
            where [0] is the name, [1] is the previous value, and [2] is the current value.
        """
        differences: List[Tuple[str, Any, Any]]
        previous_key_values: Dict[str, Any] = {}
        current_key_values: Dict[str, Any] = {}
        index: int
        for index in range(count):
            # Recursively collect configurable values:
            previous_key_values = current_key_values
            current_key_values = {}
            self._configure_helper(current_key_values)

            # Collect each difference onto *differences*:
            differences = []
            key: str
            previous_keys: Set[str] = set(previous_key_values)
            current_keys: Set[str] = set(current_key_values)
            for key in previous_keys - current_keys:
                differences.append((key, previous_key_values[key], None))  # pragma: no unit cover
            for key in current_keys - previous_keys:
                differences.append((key, None, current_key_values[key]))
            for key in previous_keys & current_keys:
                previous_value: Any = previous_key_values[key]
                current_value: Any = current_key_values[key]
                if type(previous_value) != type(current_value) or previous_value != current_value:
                    differences.append((key, previous_value, current_value))

            if verbose:
                print(f"Configure[{index}]: {len(differences)} differences.")
            if not differences:
                break

        # Sort *differences* and print warning for
        if differences:
            differences.sort(key=lambda difference: difference[0])  # Sort on first key.
            difference: Tuple[str, Any, Any]
            difference_keys: Tuple[str, ...] = tuple([difference[0] for difference in differences])
            print(f"configure[FINAL]: The following are not stable: {difference_keys}")
        return tuple(differences)

    def _configure_helper(self, values: Dict[str, Any]) -> None:
        """Recursively configure an ApexNode tree."""
        if hasattr(self, "configure"):
            self.configure()

        ignore_names: Tuple[str, ...] = ("", "name", "parent", "full_path", "configure")
        name: str
        value: Any
        for name, value in self.__dict__.items():
            if name not in ignore_names and name[0] != "_":
                if isinstance(value, (bool, int, float, ApexPoint)):
                    values[f"{self.full_path}:{name}"] = value
                elif isinstance(value, ApexNode):
                    value._configure_helper(values)


def unit_tests() -> None:
    """Run unit tests for ApexNode."""
    class Box(ApexNode):
        def __init__(self, name: str, dx: float, dy: float, dz: float, dw: float) -> None:
            super().__init__(name, None)
            self.dx: float = dx
            self.dy: float = dy
            self.dz: float = dz
            self.dw: float = dw
            # For testing, use 0 (int) instead of 0.0 (float)to cause an extra iteration:
            self.skin_volume: float = 0
            self.outer_volume: float = 0
            self.inner_volume: float = 0
            self.tne: ApexPoint = ApexPoint(dx / 2.0, dy / 2.0, dz / 2.0)
            self.bsw: ApexPoint = ApexPoint(-dx / 2.0, -dy / 2.0, -dz / 2.0)
            self.bb: ApexBox = ApexBox((self.tne, self.bsw))
            bb: ApexBox = self.bb

            # x_dw: Vector = Vector(dw, 0.0, 0.0)
            y_dw: Vector = Vector(0.0, dw, 0.0)
            z_dw: Vector = Vector(0.0, 0.0, dw)

            self.top_side: Block = Block(
                "Top", self, bb.TNE, bb.TSW - z_dw, "red")
            #    "Top", bb.TNE, bb.TSW - z_dw, "red")
            self.bottom_side: Block = Block(
                "Bottom", self, bb.BNE, bb.BSW + z_dw, "red")

            self.north_side: Block = Block(
                "North", self, bb.TNE - z_dw, bb.BNW + z_dw - y_dw, "green")
            self.south_side: Block = Block(
                "South", self, bb.TSE - z_dw, bb.BSW + z_dw + y_dw, "green")

            self.east_side: Block = Block(
                "East", self, bb.TNE - z_dw - y_dw, bb.BSE + z_dw + z_dw, "blue")
            self.west_side: Block = Block(
                "West", self, bb.TNW - z_dw + z_dw, bb.BSW + z_dw - z_dw, "blue")

        def build(self, context: ApexContext, tracing: str = "") -> None:
            if tracing:
                print(f"{tracing}<=>Box.build(*)")

        def configure(self) -> None:
            bb: ApexBox = self.bb
            dxyz: Vector = bb.TNE - bb.BSW
            self.skin_volume = (
                self.top_side.volume + self.bottom_side.volume +
                self.north_side.volume + self.south_side.volume +
                self.east_side.volume + self.west_side.volume)
            self.outer_volume = dxyz.x * dxyz.y * dxyz.z
            self.inner_volume = self.outer_volume - self.skin_volume

    class Block(ApexNode):
        def __init__(self, name: str, parent: ApexNode, tne: Vector, bsw: Vector,
                     color: str = "") -> None:
            super().__init__(name, parent)
            assert self.parent == parent, "parent is not set?"
            self.tne: Vector = tne
            self.bsw: Vector = bsw
            self.volume = 0

        def configure(self):
            dxyz: Vector = self.tne - self.bsw
            self.volume: float = dxyz.x * dxyz.y * dxyz.z

        def build(self, context: ApexContext, tracing: str = "") -> None:
            if tracing:
                print(f"{tracing}<=>Block.build({self.full_path})")

    # Constraints should down to zero differences with *count*=3.
    box: ApexNode = Box("Test_Box", 20.0, 15.0, 10.0, 0.5)
    differences: Tuple[Tuple[str, Any, Any], ...] = box._configure_all(count=3)
    want: Tuple[Tuple[str, Any, Any], ...] = ()
    assert differences == want, f"Got {differences} instead of {want=}"
    document_name: str = "ApexNodeTestDocument"
    document: App.Document = App.newDocument(document_name)
    _ = document
    box.configure_and_build(document_name)

    # Constraints should be down to 1 difference with *count*=2:
    box = Box("Test_Box", 30.0, 25.0, 15.0, 0.75)
    differences = box._configure_all(count=2)
    want = (('Test_Box:skin_volume', 0.0, 0.0),)
    assert differences == want, f"Got {differences} instead of {want=}"

    # Do some error testing:
    try:
        _ = box.parent == "Root"
    except RuntimeError as error:
        assert str(error) == "Test_Box does not have a parent"


if __name__ == "__main__":
    unit_tests()
