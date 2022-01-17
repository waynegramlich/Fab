#!/usr/bin/env python3
"""ApexPath: Apex interface to FreeCAD Path workbench."""

# <--------------------------------------- 100 characters ---------------------------------------> #

import sys
sys.path.append(".")
import Embed
Embed.setup()

import FreeCAD as App  # type: ignore
import FreeCADGui as Gui  # type: ignore
from typing import Any, List, Optional

# import math
from FreeCAD import Vector  # type: ignore
import Part  # type: ignore
# import Path  # type: ignore
# import Draft  # type: ignore

from PathScripts import PathJob  # type: ignore
if App.GuiUp:
    from PathScripts import PathJobGui  # type: ignore

from PathScripts import PathProfile  # type: ignore

# import PathScripts.PathDressupDogbone as PathDressupDogbone  # type: ignore

# import PathScripts.PathDressupHoldingTags as PathDressupHoldingTags  # type: ignore

# from PathScripts import PathGeom  # type: ignore
from PathScripts import PathPostProcessor  # type: ignore
from PathScripts import PathUtil  # type: ignore


def get_document(name: str, tracing: str = "") -> "App.Document":
    """Return the active document."""
    if tracing:
        print(f"{tracing}=>get_document('{name}')")

    document: Optional["App.Document"] = App.activeDocument()

    if document is None:
        App.newDocument(name)
        App.setActiveDocument(name)
        document = App.activeDocument()
        # if App.GuiUp:
        #     VIEW = App.Gui.ActiveDocument.ActiveView
    else:  # pragma: no unit cover
        for obj in document.Objects:
            document.removeObject(obj.Name)
        # if App.GuiUp:
        #     VIEW = App.Gui.ActiveDocument.ActiveView
    if tracing:
        print(f"{tracing}<=get_document('{name}')=>{document}")
    return document


def setview(document: "App.Document") -> "App.Document":
    """Rearrange View."""
    document.recompute()
    if App.GuiUp:  # pragma: no unit cover
        view = Gui.ActiveDocument.ActiveView
        view.viewAxometric()
        view.setAxisCross(True)
        view.fitAll()


def box_make(document: "App.Document", name: str,
             shape: Vector, offset: Vector, rotate: float = 0, tracing: str = "") -> "App.Document":
    """Create a box."""
    if tracing:
        print(f"{tracing}=>box_make('{name}', {shape=}, {offset=})")
    box: Any = document.addObject("Part::Box", name)
    box.Width = shape.x
    box.Length = shape.y
    box.Height = shape.z
    box.Placement = App.Placement(offset, App.Rotation(Vector(0, 0, 1), rotate))
    document.recompute()
    if tracing:
        print(f"{tracing}<=box_make('{name}', {shape=}, {offset=})=>{box}")
    return box


def box_cut(document: "App.Document", name: str, base: "Part.Box", tool: "Part.Box") -> "Part.Cut":
    """Make a hole in a box."""
    cut: "Part.Cut" = document.addObject("Part::Cut", name)
    cut.Base = base
    cut.Tool = tool
    document.recompute()
    return cut


def top_faces(obj: Any) -> List[str]:
    """Return top faces."""
    assert hasattr(obj, "Shape")
    shape = obj.Shape
    top_face_names: List[str] = []
    face_index: int
    for face_index in range(len(shape.Faces)):
        face_name: str = f"Face{face_index+1}"
        face: "Part.Face" = shape.getElement(face_name)
        if face.Surface.Axis == Vector(0, 0, 1) and face.Orientation == 'Forward':
            top_face_names.append(face_name)
    return top_face_names


def donut(document: "App.Document", name: str, box_shape: Vector,
          offset: Vector, rotate: float = 0.0, tracing: str = "") -> "Part.Cut":
    """Create a square donut."""
    if tracing:
        print(f"{tracing}=>donut({name=}, {box_shape=}, {offset=}, {rotate=})")
    box: "Part.Box" = box_make(document, f"{name}Box", box_shape, offset, rotate)
    extra: int = 5
    hole_shape: Vector = Vector(box_shape.x / 2, box_shape.y / 2, box_shape.z + 2 * extra)
    delta_shape: Vector = box_shape - hole_shape
    hole_offset: Vector = offset + Vector(delta_shape.x / 2, delta_shape.y / 2, -extra)
    hole: "Part.Box" = box_make(document, f"{name}Hole", hole_shape, hole_offset, rotate)
    # cut: "Part.Cut" = box_cut(document, f"{name}Cut", box, hole)
    box_cut(document, f"{name}Cut", box, hole)
    if tracing:
        print(f"{tracing}<=donut()=>{box}")
    return box


def contour(obj: Any, name: str, job: Any, tracing: str = "") -> Any:
    if tracing:
        print(f"{tracing}=>contour({obj=}, {name=}, {job=})")
    """Create an exterior contour."""
    top_face_name: str = top_faces(obj)[0]
    profile = PathProfile.Create(name)
    profile.Base = (obj, top_face_name)
    profile.setExpression('StepDown', None)
    profile.StepDown = 3.00
    profile.setExpression('StartDepth', None)
    profile.StartDepth = 10
    profile.setExpression('FinalDepth', None)
    profile.FinalDepth = 0
    profile.processHoles = True
    profile.processPerimeter = True

    profile.recompute()
    if tracing:
        print(f"{tracing}<=contour()=>{profile}")
    return profile


def model(document: "App.Document", tracing: str = "") -> None:
    """Create the model."""
    next_tracing: str = tracing + " " if tracing else ""
    if tracing:
        print(f"{tracing}=>model()")

    donut_a: "Part.Cut" = donut(
        document, "DonutA", Vector(100, 100, 10), Vector(0, 0, 0), tracing=next_tracing)
    # donut_b: "Part.Cut" = donut(document, "DonutB", Vector(100, 100, 10), Vector(0, 0, 0),
    #                              rotate=45)

    # Create the *job* for *donut_a*.
    job = PathJob.Create('Job', [donut_a], None)
    gcode_path: str = "/tmp/engrave.ngc"
    job.PostProcessorOutputFile = gcode_path
    job.PostProcessor = 'grbl'
    job.PostProcessorArgs = '--no-show-editor'

    if App.GuiUp:  # pragma: no unit cover
        proxy: Any = PathJobGui.ViewProvider(job.ViewObject)
        # The statement below causes a bunch of rearrangement of the FreeCAD object tree
        # to push all off the Path related object to be under the FreeCAD Path Job object.
        # This is really nice because it provides the ability toggle the path trace visibility
        # in one place.  The lovely line below triggers a call to PathJob.ObjectJob.__set__state__()
        # method.  Which appears to do the rearrangement.  Unfortunately, this rearrangement
        # does not occur in embedded mode, so the resulting object trees look quite different.
        # Such is life.
        job.ViewObject.Proxy = proxy  # This assignment rearranges the Job.
    if tracing:
        print(f"{tracing}{job=}")

    index: int
    part: Any
    for index, part in enumerate(job.Model.OutList):
        if tracing:
            print(f"{tracing}Part[{index}]:'{part.Name}' '{part.Label}'")

    clone_a: Any = job.Model.getObject("Clone")
    # clone_b: Any = job.Model.getObject("Clone001")

    # print(f"{donut_a.Name=} {dir(donut_a)=}")

    # for index, obj in enumerate(clone_a.Objects):
    #     print(f"clone_a.objects[{index}]: {obj.Name=} {dir(obj)=}")

    # print(f"{dir(clone_a)=}")

    # print(f"{dir(job)=}")
    stock: Any = job.Stock
    # print(f"{dir(stock)=}")
    # print(f"{stock.Placement=}")
    # print(f"{stock.Base=}")
    # print(f"{stock.Shape=}")
    # print(f"{dir(stock.Shape)=}")
    # print(f"{dir(stock.Shape.OuterShell)=}")
    if tracing:
        print(f"{tracing}{stock.Shape.OuterShell.BoundBox=}")
    stock.Placement.Base = Vector(-150, 0, 0)

    # print(f"{job.Model.Name=} {job.Model.Label=}")
    # print(f"{job.Model.InList=}")
    # print(f"{job.Model.OutList=}")

    # clone_b.Placement.Rotation=App.Rotation(Vector(0, 0, 1), 45.0)
    # clone_b.Placement.Base=Vector(-150, 0, 0)

    # print(f"{clone.Placement.Position=}")
    # print(f"{clone.Placement.Rotation=}")

    # This operation appends *opertation* onto *job.Operations.Group*:
    operation: Any = contour(clone_a, "ProfileA", job, tracing=next_tracing)
    if tracing:
        print(f"{tracing}{id(operation)=}")
    # contour(clone_b, "ProfileB", job)

    document.recompute()

    # Create *post_list* which is a list of tool controllers and *operations*:
    post_list: List[Any] = []
    current_tool_number: int = -99999999
    for index, operation in enumerate(job.Operations.Group):
        tool_controller: Any = PathUtil.toolControllerForOp(operation)
        if tool_controller is not None:
            if tool_controller.ToolNumber != current_tool_number:
                post_list.append(tool_controller)
                current_tool_number = tool_controller.ToolNumber
        post_list.append(operation)

    # Generate the G-code *post* and export it to *gcode_path*:
    post: Any = PathPostProcessor.PostProcessor.load(job.PostProcessor)
    post.export(post_list, gcode_path , job.PostProcessorArgs)
    if tracing:
        print(f"{tracing}{post=}")

    # ops = document.getObject("Operations")
    # ops.Visibility = True
    if tracing:
        print(f"{tracing}<=model()")


def main(tracing: str = "") -> None:
    """Run the main program."""
    next_tracing: str = tracing + " " if tracing else ""
    if tracing:
        print(f"{tracing}=>main()")
    document_name: str = "JobTest"
    document: "App.Document" = get_document(document_name, tracing=next_tracing)

    model(document, tracing=next_tracing)

    document.recompute()
    document.saveAs("/tmp/bar.fcstd")

    if tracing:
        print(f"{tracing}<=main()")


if __name__ == "__main__":
    main(tracing=" ")
