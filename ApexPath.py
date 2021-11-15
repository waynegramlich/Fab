#!/usr/bin/env python3
"""ApexPath: Apex interface to FreeCAD Path workbench."""

# <--------------------------------------- 100 characters ---------------------------------------> #

# Standard preamble for running FreeCAD in embedded mode:
import os
import sys
assert sys.version_info.major == 3  # Python 3.x
assert sys.version_info.minor == 8  # Python 3.8
sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])
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


def get_document(name: str) -> "App.Document":
    """Return the active document."""
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
             shape: Vector, offset: Vector, rotate: float = 0) -> "App.Document":
    """Create a box."""
    print(f"=>box_make('{name}', {shape=}, {offset=})")
    box: Any = document.addObject("Part::Box", name)
    box.Width = shape.x
    box.Length = shape.y
    box.Height = shape.z
    box.Placement = App.Placement(offset, App.Rotation(Vector(0, 0, 1), rotate))
    document.recompute()
    print(f"<=box_make('{name}', {shape=}, {offset=})")
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
          offset: Vector, rotate: float = 0.0) -> "Part.Cut":
    """Create a square donut."""
    print(f"=>donut('{name}', {box_shape=}, {offset=})")
    box: "Part.Box" = box_make(document, f"{name}Box", box_shape, offset, rotate)
    extra: int = 5
    hole_shape: Vector = Vector(box_shape.x / 2, box_shape.y / 2, box_shape.z + 2 * extra)
    delta_shape: Vector = box_shape - hole_shape
    hole_offset: Vector = offset + Vector(delta_shape.x / 2, delta_shape.y / 2, -extra)
    hole: "Part.Box" = box_make(document, f"{name}Hole", hole_shape, hole_offset, rotate)
    # cut: "Part.Cut" = box_cut(document, f"{name}Cut", box, hole)
    box_cut(document, f"{name}Cut", box, hole)
    print(f"<=donut('{name}', {box_shape=}, {offset=})")
    return box


def contour(obj: Any, name: str, job: Any) -> Any:
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


def model(document: "App.Document") -> None:
    """Create the model."""
    gcodePath = "/tmp/engrave.ngc"

    donut_a: "Part.Cut" = donut(document, "DonutA", Vector(100, 100, 10), Vector(0, 0, 0))
    # donut_b: "Part.Cut" = donut(document, "DonutB", Vector(100, 100, 10), Vector(0, 0, 0),
    #                              rotate=45)

    job = PathJob.Create('Job', [donut_a], None)
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

    index: int
    part: Any
    for index, part in enumerate(job.Model.OutList):
        print(f"Part[{index}]:'{part.Name}' '{part.Label}'")

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
    print(f"{stock.Shape.OuterShell.BoundBox=}")
    stock.Placement.Base = Vector(-150, 0, 0)

    # print(f"{job.Model.Name=} {job.Model.Label=}")
    # print(f"{job.Model.InList=}")
    # print(f"{job.Model.OutList=}")

    # clone_b.Placement.Rotation=App.Rotation(Vector(0, 0, 1), 45.0)
    # clone_b.Placement.Base=Vector(-150, 0, 0)

    # print(f"{clone.Placement.Position=}")
    # print(f"{clone.Placement.Rotation=}")

    contour(clone_a, "ProfileA", job)
    # contour(clone_b, "ProfileB", job)

    document.recompute()

    job.PostProcessorOutputFile = gcodePath
    job.PostProcessor = 'grbl'
    job.PostProcessorArgs = '--no-show-editor'

    postlist = []
    currTool = None

    for obj in job.Operations.Group:
        print(obj.Name)
        tc = PathUtil.toolControllerForOp(obj)
        if tc is not None:
            if tc.ToolNumber != currTool:
                postlist.append(tc)
                currTool = tc.ToolNumber
        postlist.append(obj)

    post = PathPostProcessor.PostProcessor.load(job.PostProcessor)
    # gcode = post.export(postlist, gcodePath , job.PostProcessorArgs)
    post.export(postlist, gcodePath, job.PostProcessorArgs)

    # ops = document.getObject("Operations")
    # ops.Visibility = True


def main() -> None:
    """Run the main program."""
    document_name: str = "JobTest"
    document: "App.Document" = get_document(document_name)

    model(document)

    document.recompute()
    document.saveAs("/tmp/bar.fcstd")

    print("--- done ---")


if __name__ == "__main__":
    main()
