#!/usr/bin/env python3
"""
ApexExampleBox: Example Box.

Builds a box of given the length, width, height and material thickness.
"""
# <--------------------------------------- 100 characters ---------------------------------------> #

import os
import sys

assert sys.version_info.major == 3  # Python 3.x
assert sys.version_info.minor == 8  # Python 3.8
sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])

from typing import Any, Sequence, Optional, Tuple

import FreeCAD as App  # type: ignore
import FreeCADGui as Gui  # type: ignore
from FreeCAD import Placement, Rotation, Vector  # type: ignore
from Apex import ApexBox, ApexCheck, ApexColor, ApexMaterial
from ApexNode import ApexContext, ApexNode
from ApexSketch import ApexCorner, ApexDrawing, ApexOperation, ApexPad, ApexPolygon
from ApexFasten import ApexScrew, ApexStack, ApexStackBody
import PartDesign  # type: ignore


# ApexEnclosure:
class ApexEnclosure(ApexNode):
    """ApexEnclosure: Build a box.

    Builds a box given a length, width, height, material, thickness and position in space.

    Attributes:
    * *dx* (float): length in X direction in millimeters.
    * *dy* (float): width in Y direction in millimeters.
    * *dz* (float): height in Z direction in millimeters.
    * *material* (ApexMaterial): Material to use.
    * *dw* (float): material thickness in millimeters.
    * *center*: (Vector): Center of box:
    * *z_align*: (Vector): Axis to align with +Z axis.
    * *y_align: (Vector): Axis to align with +Y axis.

    """

    INIT_CHECKS = (
        ApexCheck("name", (str,)),
        ApexCheck("dx", (float,)),
        ApexCheck("dy", (float,)),
        ApexCheck("dz", (float,)),
        ApexCheck("material", (ApexMaterial,)),
        ApexCheck("dw", (float,)),
        ApexCheck("center", (Vector,)),
        ApexCheck("z_align", (Vector,)),
        ApexCheck("y_align", (Vector,)),
    )

    # ApexEnclosure.__ init__():
    def __init__(self, name: str, dx: float, dy: float, dz: float, material: ApexMaterial,
                 dw: float, center: Vector, z_align: Vector, y_align: Vector,
                 tracing: str = "") -> None:
        """Initialize a ApexEnclosure.

        Arguments:
          * *name* (str): The box name.
          * *dx* (float): length in X direction in millimeters.
          * *dy* (float): width in Y direction in millimeters.
          * *dz* (float): height in Z direction in millimeters.
          * *material* (ApexMaterial): ApexEnclosure material.
          * *dw* (float): material thickness in millimeters.
          * *center* (Vector): Center of box.
          * *z_align* (Vector): Axis to align top normal to.
          * *y_align* (Vector): Axis to align "back" normal to.

        Raises:
        * ValueError: If *dx*, *dy*, *dz*, and *dw* are not positive or if *z_align* or *y_align*
          have a magnitude of zero.

        """
        arguments: Tuple[Any, ...] = (name, dx, dy, dz, material, dw, center, z_align, y_align)
        value_error = ApexCheck.check(arguments, ApexEnclosure.INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)  # pragma: no unit cover

        # next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>ApexEnclosure.__init__{arguments}")

        super().__init__(name, None)  # Initilize ApexNode parent class.
        self.dx: float = dx
        self.dy: float = dy
        self.dz: float = dz
        self.material: ApexMaterial = material
        self.dw: float = dw
        self.center: Vector = center
        self.z_align: Vector = z_align
        self.y_align: Vector = y_align

        # For testing, use 0 (int) instead of 0.0 (float)to cause an extra iteration:
        tne: Vector = Vector(dx / 2.0, dy / 2.0, dz / 2.0)
        bsw: Vector = Vector(-dx / 2.0, -dy / 2.0, -dz / 2.0)
        box: ApexBox = ApexBox((tne, bsw))
        self._material: ApexMaterial = material

        self.top_side: Block = Block("Top", self,
                                     box.TNE + Vector(0.0, 0.0, 0.0),
                                     box.TSW + Vector(0.0, 0.0, -dw), box.T, box.N, "red", ())

        stainless: ApexMaterial = ApexMaterial(("steel", "stainless"), "white")
        stack_body: ApexStackBody = ApexStackBody(
            "#4-40", "#4-40", ApexStackBody.UTS_FINE, ApexStackBody.UTS_N4,
            stainless, ApexStackBody.FLAT, ApexStackBody.PHILLIPS)
        stack: ApexStack = ApexStack("SS #4-40 FH", "Stainless #4-40 Phillips Flat Head",
                                     stack_body, (), ())
        dw2: float = dw / 2.0

        bottom_starts: Tuple[Vector, ...] = (
            box.BSE + Vector(-dw2, dw2, 0.0),
            box.BSW + Vector(dw2, dw2, 0.0),
            box.BNE + Vector(-dw2, -dw2, 0.0),
            box.BNW + Vector(dw2, -dw2, 0.0),
        )
        bottom_screws: Tuple[ApexScrew, ...] = ()
        bottom_start: Vector
        for bottom_start in bottom_starts:
            bottom_end: Vector = bottom_start + Vector(0.0, 0.0, 2.0 * dw)
            bottom_screw: ApexScrew = ApexScrew(stack, bottom_start, bottom_end)
            bottom_screws += (bottom_screw,)

        self.bottom_side: Block = Block("Bottom", self,
                                        box.BNE + Vector(0.0, 0.0, 0.0),
                                        box.BSW + Vector(0.0, 0.0, dw), box.B, box.N, "red",
                                        bottom_screws)

        if True:
            self.north_side: Block = Block("North", self,
                                           box.TNE + Vector(0.0, 0.0, -dw),
                                           box.BNW + Vector(0.0, -dw, dw), box.N, box.B, "green",
                                           ())
            self.south_side: Block = Block("South", self,
                                           box.TSE + Vector(0.0, 0.0, -dw),
                                           box.BSW + Vector(0.0, dw, dw), box.S, box.B, "green", ())

            self.east_side: Block = Block("East", self,
                                          box.TNE + Vector(0.0, -dw, -dw),
                                          box.BSE + Vector(-dw, dw, dw), box.DE, box.DN, "blue", ())
            self.west_side: Block = Block("West", self,
                                          box.TNW + Vector(0.0, -dw, -dw),
                                          box.BSW + Vector(dw, dw, dw), box.DW, box.DN, "blue", ())

        if tracing:
            print(f"{tracing}<=ApexEnclosure.__init__{arguments}")

    def build(self, context: ApexContext, tracing: str = "") -> None:
        """Build the ApexEnclosure."""
        pass

    def configure(self) -> None:
        """Configure the ApexEnclosure."""
        pass


# Block:
class Block(ApexNode):
    """Block: A rectangular block."""

    BLOCK_INIT = (
        ApexCheck("name", (str,)),
        ApexCheck("parent", (ApexNode,)),
        ApexCheck("tne", (Vector,)),
        ApexCheck("bsw", (Vector,)),
        ApexCheck("north_face", (Vector,)),
        ApexCheck("top_face", (Vector,)),
        ApexCheck("color", (str,)),
        ApexCheck("screws", ("T", ApexScrew)),
    )

    # Block.__init__():
    def __init__(self, name: str, parent: ApexNode, tne: Vector, bsw: Vector,
                 top_face: Vector, north_face: Vector, color: str = "",
                 screws: Tuple[ApexScrew, ...] = (), tracing: str = "") -> None:
        """Initlialze a Block.

        * Arguments:
          * *name* (str): The name of the Block.
          * *parent* (str): The parent ApexNode.
          * *tne* (Vector): The Top-North-East corner.
          * *bsw* (Vector): The Bottom-South-West corner.
          * *top_face* (Vector): The face to have pointing +Z when doing operations.
          * *north_face* (Vector): The face to have pointing +Y when doing operations.
          * *color*: (str): The SVG color name to use for coloring purposes.
          * *screws*: (Tuple[ApexScrew]): Screws to attach. (Default: ())
        """
        arguments: Sequence[Any] = (name, parent, tne, bsw, north_face, top_face, color, screws)
        value_error: str = ApexCheck.check(arguments, Block.BLOCK_INIT)
        if value_error:
            raise ValueError(value_error)  # pragma: no unit cover

        super().__init__(name, parent)  # Initialize parent ApexNode.
        box: ApexBox = ApexBox((tne, bsw), name)
        self.bsw: Vector = bsw
        self.box: ApexBox = box
        self.color: str = color
        self.tne: Vector = tne
        self.top_face: Vector = top_face
        self.north_face: Vector = north_face
        self.screws: Tuple[ApexScrew, ...] = screws

        if tracing:
            print(f"{tracing}<=>Block.__init__{arguments}")

    # Block.configure():
    def configure(self):
        """Configure a Block."""
        pass

    # Block.build():
    def build(self, context: ApexContext, tracing: str = "") -> None:
        """Build a Block.

        * Arguments:
          *context* (ApexContext):  The context to use during building.
        """
        # Extract the contour:
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>Block.build({self.full_path}, *)")

        full_path: str = self.full_path
        north_face: Vector = self.north_face
        top_face: Vector = self.top_face

        box: ApexBox = self.box
        assert box.DX > 0.0, "DX is not positive"
        assert box.DY > 0.0, "DY is not positive"
        assert box.DZ > 0.0, "DZ is not positive"
        center: Vector = box.C
        z_align: Vector = (top_face - center).normalize()
        y_align: Vector = (north_face - center).normalize()

        if tracing:
            print(f"{tracing}{center=}")
            print(f"{tracing}{top_face=}")
            print(f"{tracing}{north_face=}")
            print(f"{tracing}{z_align=}")
            print(f"{tracing}{y_align=}")

        # Create *top_box* that is aligned along *z_axis*:
        origin: Vector = Vector()
        z_axis: Vector = Vector(0.0, 0.0, 1.0)
        top_rotation: Rotation = Rotation(z_align, z_axis)
        top_placement: Placement = Placement(origin, top_rotation, origin)
        top_box: ApexBox = box.reorient(top_placement)

        # Create *back_placement* that maps back from *top_placement*.
        # Use *back_placement* to identify the "top" 4 corners of the polygon:
        back_rotation: Rotation = Rotation(z_axis, z_align)
        back_placement: Placement = Placement(origin, back_rotation, origin)
        if tracing:
            print(f"{tracing}{top_placement=}")
            print(f"{tracing}{back_placement=}")

        # depth: float = realigned_box.DZ
        diameter: float = 0.0
        corners: Tuple[ApexCorner, ...] = (
            ApexCorner(back_placement * top_box.TNE, diameter, f"{full_path}.Corner1"),
            ApexCorner(back_placement * top_box.TNW, diameter, f"{full_path}.Corner2"),
            ApexCorner(back_placement * top_box.TSW, diameter, f"{full_path}.Corner3"),
            ApexCorner(back_placement * top_box.TSE, diameter, f"{full_path}.Corner4"),
        )
        if tracing:
            print(f"{tracing}{corners[0]=}")
            print(f"{tracing}{corners[1]=}")
            print(f"{tracing}{corners[2]=}")
            print(f"{tracing}{corners[3]=}")
        depth: float = top_box.DZ
        block_polygon: ApexPolygon = ApexPolygon(corners, "block_polygon")
        block_pad: ApexPad = ApexPad(block_polygon, depth, "block_op")
        # Create the *drawing*:
        app_document: App.Document = context.app_document
        document_name: str = app_document.Name
        gui_document: Optional[Gui.Document] = context.gui_document
        body_name: str = f"{full_path}.Body"
        body: PartDesign.Body = app_document.addObject("PartDesign::Body", body_name)

        if tracing:
            print(f"{tracing}$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$")
        if App.GuiUp:  # pragma: no unit cover
            fixed_body_name: str = body_name.replace(".", "_")
            # Gui.Selection.addSelection(document_name, fixed_body_name)
            if tracing:
                print(f"{tracing}Gui.Selection.addSelection("
                      f"'{document_name}', '{fixed_body_name}')")
            if gui_document:  # pragma: no unit cover
                gui_body: Any = gui_document.getObject(body.Name)
                assert hasattr(gui_body, "ShapeColor"), (body.Name, gui_body.Name, dir(gui_body))
                if gui_body:
                    if hasattr(gui_body, "Proxy"):
                        setattr(gui_body, "Proxy", 0)  # Must not be `None`
                    if hasattr(gui_body, "DisplayMode"):
                        setattr(gui_body, "DisplayMode", "Shaded")
                    if hasattr(gui_body, "ShapeColor"):
                        rgb = ApexColor.svg_to_rgb(self.color)
                        setattr(gui_body, "ShapeColor", rgb)
            if tracing:
                print(f"{tracing}Gui.Selection.clearSelection()")
            # Gui.Selection.clearSelection()
        app_document.recompute()

        screw: ApexScrew
        # screw_elements: Tuple[ApexShape, ...] = tuple(
        #     [screw.element() for screw in self.screws]
        # )
        operations: Tuple[ApexOperation, ...] = (block_pad,)  # + screw_elements
        if tracing:
            print(f"{tracing}{top_face=}")
            print(f"{tracing}{z_align=}")
        drawing: ApexDrawing = ApexDrawing(top_face, z_align, operations, f"{full_path}.Drawing")
        drawing.plane_process(body, document_name, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=Block.build({self.full_path}, *)")


def main() -> None:
    """Box Example main program."""
    name: str = "Test_Box"
    length: float = 200.0  # DX
    width: float = 150.0  # DY
    height: float = 100.0  # DZ
    material: ApexMaterial = ApexMaterial(("Plastic", "HDPE"), "yellow")
    thickness: float = 10.0  # DW
    origin: Vector = Vector(0.0, 0.0, 0.0)  # Center
    z_axis: Vector = Vector(0.0, 0.0, 1.0)  # +Z Axis
    y_axis: Vector = Vector(0.0, 1.0, 0.0)  # +Y Axis

    enclosure: "ApexEnclosure" = ApexEnclosure(name, length, width, height, material, thickness,
                                               origin, z_axis, y_axis)
    document_name: str = "ApexEnclosureUnitTests"
    document: "App.Document" = App.newDocument(document_name)
    enclosure.configure_and_build(document_name)
    document.recompute()
    document.saveAs(f"/tmp/{document_name}.fcstd")


if __name__ == "__main__":
    main()