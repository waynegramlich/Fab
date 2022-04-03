#!/usr/bin/env python3
"""ApexPath: Apex interface to FreeCAD Path workbench."""

# <--------------------------------------- 100 characters ---------------------------------------> #


# [Path Inputs](https://forum.freecadweb.org/viewtopic.php?f=15&t=64089&p=552158)
# [Some Code that might work](https://forum.freecadweb.org/viewtopic.php?f=15&t=64624)
# [More code](https://forum.freecadweb.org/viewtopic.php?f=15&t=64624&p=554648

print("here 1")
import os
import sys
sys.path.append(".")
from pathlib import Path
# import Embed
USE_FREECAD: bool
USE_CAD_QUERY: bool
print("here 2")

current_directory: str = os.getcwd()
freecad_directory: str = str(Path(current_directory) / "squashfs-root" / "usr" / "lib")
sys.path.append(str(freecad_directory))

# USE_FREECAD, USE_CAD_QUERY = Embed.setup()
print("here 3")
print(f"{sys.path=}")

from typing import Any, List, Optional

# import math
print("here 4")
import FreeCAD as App  # type: ignore
print("here 5")
import FreeCADGui as Gui  # type: ignore
print("here 6")
from FreeCAD import Vector  # type: ignore
print("here 7")
import Part  # type: ignore
print("here 8")
# import Path  # type: ignore
# import Draft  # type: ignore

print("here 9")
from PathScripts import PathJob  # type: ignore
print("here 10")
if App.GuiUp:
    print("here 11")
    from PathScripts import PathJobGui  # type: ignore

print("here 12")
from PathScripts import PathProfile  # type: ignore

# import PathScripts.PathDressupDogbone as PathDressupDogbone  # type: ignore

# import PathScripts.PathDressupHoldingTags as PathDressupHoldingTags  # type: ignore

# from PathScripts import PathGeom  # type: ignore
print("here 13")
from PathScripts import PathPostProcessor  # type: ignore
print("here 14")
from PathScripts import PathUtil  # type: ignore
print("here 15")


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

    # From TestPathToolController.py:
    # def createTool(self, name='t1', diameter=1.75):
    #     if PathPreferences.toolsUseLegacyTools():
    #         return Path.Tool(name=name, diameter=diameter)
    # attrs = {
    #     'shape': None,
    #     'name': name,
    #     'parameter': {
    #         'Diameter': diameter},
    #     'attribute': []
    # }
    #
    #     return PathToolBit.Factory.CreateFromAttrs(attrs, name)

    # Defined in `.../Path/PathScripts/PathToolController.py`:216:
    # Is a function, not an method:
    # def Create(
    #         name: str, tool: "Tool", toolNumber: int, assignViewProvider: bool = True,
    #         assignTool=True) -> None
    # )

    # This reads in a tool bit:
    #     import PathToolBit from PathScripts
    #     # probe_tool_bit = PathToolBit("Tools/Bit/probe.fctb")  # Does not work
    #     probe_tool_bit = PathToolBit.findBit(""Tools/Bit/probe.fctb")
    # reads in:
    #     probe_tool_bit = {
    #         'version': 2,
    #         'name': 'Probe',
    #         'shape': 'probe.fcstd',
    #         'parameter': {
    #              'Diameter': '6.0000 mm',
    #              'Length': '50.0000 mm',
    #              'ShaftDiameter': '4.0000 mm'
    #         },
    #         'attribute': {}
    #     }

    # This creates a tool controller:
    #     # Besure there is an active document.
    #     doc = App.newDocument("foo")
    #     import PathScripts.PathToolController as PathToolController
    #     tc1 = PathToolController.Create(name="LabelName")
    #     tool = tc0.Tool
    #
    # There are two tool formats, the version 1 and the version 2 Tool/{Bit,Library,Shape} stuff.
    #
    # All of the controller fields are need to be set (see below):
    # There is a comment in the "Path Scripting Thread" on Tue Jan 05, 2021 12:11 pm that says:
    #
    #     tc1.setExpression('HorizRapid', None)
    #     tc1.HorizRapid = "15 mm/s"
    #     tc1.setExpression('VertRapid', None)
    #     tc1.VertRapid = "2 mm/s"
    #
    # The version 2 sutff seems to start with two
    #
    #     tool.getToolTypes() => ['EndMill', 'Drill', 'CenterDrill', 'CounterSink', 'CounterBore',
    #                             'FlyCutter', 'Reamer', 'Tap', 'SlotCutter', 'BallEndMill',
    #                             'ChamferMill', 'CornerRound', 'Engraver']
    #     tool.getToolMaterials() => ['Carbide', 'HighSpeedSteel', 'HighCarbonToolSteel',
    #     t.templateAttrs() => {'version': 1, 'name': 'Default Tool', 'tooltype': 'EndMill',
    #                           'material': 'HighSpeedSteel', 'diameter': 5.0,
    #                           'lengthOffset': 0.0, 'flatRadius': 0.0, 'cornerRadius': 0.0,
    #                           'cuttingEdgeAngle': 180.0, 'cuttingEdgeHeight': 15.0}
    #     # Note: the 'version' should be 2, not 1.
    #
    #     tool.Content: XML String (reformatted and it seems out of date):
    #       '<Tool
    #         name="Default Tool"
    #         diameter="5"
    #         length="0"
    #         flat="0"
    #         corner="0"
    #         angle="180"
    #         height="15"
    #         type="EndMill"
    #         mat="HighSpeedSteel"
    #       >'
    #     tool.CornerRadius = 0.0  # mm
    #     tool.CuttingEdgeAngle = 180.0  # Probably point angle.
    #     tool.CuttingEdgeHeight= 15.0  # mm
    #     tool.Diameter = 5.0  # mm
    #     tool.FlatRadius = 0.0  # mm
    #     tool.LengthOffset = 0.0  # mm
    #     tool.Material = "HighSpeedSteel"  # On of tool.getToolMaterials()
    #     tool.MemSize = 0  # Ignore
    #     tool.Module = "Path"  # Ignore
    #     tool.Name = "Default Tool"  # Where is this from?
    #     tool.ToolType = "EndMill"  # One of tool.getToolTypes()
    #     tool.TypeId = "Path::Tool"

    # HorizRapid an VertRapid are typically an expression from the "spreadsheet".
    #
    #     # This stuff seems to be old verstion 1 stuff

    # The version 1 legacy tools stuff is:
    #
    #     tool.BitBody: Any
    #     # XML:The parametrized body representing the tool bit
    #     *tool.BitPropertyNames:  ['Chipload', 'CuttingEdgeHeight',
    #                              'Diameter', 'Flutes', 'Length', 'Material', 'ShankDiameter']
    #     # XML:List of all properties inherited from the bit"
    #     tool.BitShape: '/usr/lib/freecad/Mod/Path/Tools/Shape/endmill.fcstd'
    #     # XML:Shape for bit shape"
    #     tool.Chipload: "0.0 mm"
    #     # XML: Chipload per tooth.
    #     tool.Content: "..." = Big long XML file string
    #     tool.CuttingEdgeHeight: "30.0 mm"
    #     # XML: Height of the tool bit's flutes."
    #     tool.Diameter: "5.0 mm"
    #     # XML: Diameter of the cutting edge.
    #     tool.Docuemnt: Parent FreeCAD document
    #     tool.ExprssionEngine: []
    #     # XML: no doc string
    #     tool.File: ""
    #     # XML: The file of the tool
    #     tool.Flutes: 0
    #     # XML: The number of flutes
    #     tool.FullName: "docname#ToolBit"
    #     tool.ID: 4685  # Some sort of FreeCAD UID
    #     tool.InList: ??  # Unclear
    #     tool.InListRecursive: ??  # Unclear
    #     tool.Label: "Endmill"
    #     # XML: No doc string
    #     tool.Label2: ""
    #     # XML: No doc string
    #     tool.Length: "50.0 mm"  # Probably OAL=OverAll Length
    #     # XML: Total length of the tool bit.
    #     tool.Material: "HSS"  # The XML document says this is the surface of the bit.
    #     # XML: The material the tool bit is made of or coated with.
    #     # XML: Only HSS and Carbide are specified
    #     tool.Memsize: 9236  # probably byte size of object.
    #     tool.Module: "Part"
    #     tool.MustExcute: True
    #     tool.Name: "ToolBit"
    #     tool.NoTouch: False
    #     tool.OldLabel: "ToolBit"
    #     tool.OutList: []  # Unclear
    #     tool.OutListRecursive: []  # Unclear
    #     tool.Parents: []  # Unclear
    #     tool.Placement: Placement [Pos=(0,0,0), Yaw-Pitch-Roll=(0,0,0)]  # Unclear what this does
    #     # XML: No doc string
    #     tool.PropertiesList: ['BitBody', 'BitPropertyNames', 'BitShape', 'Chipload',
    #                           'CuttingEdgeHeight', 'Diameter', 'ExpressionEngine', 'File',
    #                           'Flutes', 'Label', 'Label2', 'Length', 'Material', 'Placement',
    #                           'Proxy', 'ShankDiameter', 'Shape', 'ShapeName', 'Visibility']
    #     tool.Proxy: <PathScripts.PathToolBit.ToolBit object at 0x7fecf6dc28e0>
    #     # XML: No doc string
    #     tool.Removing: False  # Unclear
    #     tool.ShankDiameter: "3.0 mm"
    #     Tool.Shape: <Solid object at 0x55b0f0a981a0>  # Probably the generated tool Solid
    #     # XML: Diameter of the tool bit's shank.
    #     tool.ShapeName: "endmill"
    #     # XML: The name of the shape file
    #     tool.State: ["Touched"]  # Unclear
    #     tool.TypeId: 'Part::FeaturePython'  # Probably an object
    #     tool.ViewObject: None  # This was done in FreeCAD non GUI console
    #     tool.Visibility: True  # Visibility flag
    #     # XML: No doc string
    #
    # The new and improved tool format is as follows:
    #

    # Now assign into the fields of tool
    #
    #     # Make sure all of the "BitPropertyName get set:
    #     tool.BitShape = "/usr/lib/freecad/Mod/Path/Tools/Shape/endmill.fcstd"
    #     tool.ChipLoad = "0.000 mm"  # In BitPropertyNames
    #     tool.CuttingEdgeHeight = "30.0 mm"  # In PropertyNames
    #     tool.Diameter = "5.0 mm"  # In BitPropertyNames
    #     tool.Flutes = 2  # In Property names
    #     tool.Length = "50.mm"  # In BitPropertyNames
    #     tool.Material = "HSS"  # In BitPropertyNames
    #     tool.ShankDiameter = "3.0 mm"  # In BitPropertyNames
    #     tool.ShapeName = "endmill"  # in Bit PropertyNames
    #     tool.Visiblity = True  # In Bit PropertyNames
    #
    #
    # Fields missing from ToolBit:
    #     SurfaceFinish: Literal["BlackOxide", ...]
    #     ClearanceHeight: The Distance from tool tip to Tooling (or probe base.)
    #
    # Fields missing from ToolContoller:
    #     Cooling: Literal["Off", "Flood", "Mist", "Air"]

    # Create *post_list* which is a list of tool controllers and *operations*:
    post_list: List[Any] = []
    current_tool_number: int = -99999999
    for index, operation in enumerate(job.Operations.Group):
        tool_controller: Any = PathUtil.toolControllerForOp(operation)
        if tracing:
            print(f"{tracing}{tool_controller.ToolNumber=}")
            print(f"{tracing}{tool_controller.Name=}")
            print(f"{tracing}{tool_controller.FullName=}")
            print(f"{tracing}{tool_controller.Label=}")
            print(f"{tracing}{tool_controller.Label2=}")
            print(f"{tracing}{tool_controller.Tool=}")
            print(f"{tracing}{tool_controller.HorizFeed=}")
            print(f"{tracing}{tool_controller.HorizRapid=}")
            print(f"{tracing}{tool_controller.VertFeed=}")
            print(f"{tracing}{tool_controller.VertRapid=}")
            print(f"{tracing}{tool_controller.SpindleDir=}")
            print(f"{tracing}{tool_controller.SpindleSpeed=}")
            print(f"{tracing}{tool_controller.State=}")
            print(dir(tool_controller))
            print("")
        tool: Any = tool_controller.Tool
        if tracing:
            print(f"{tracing}{tool=}")
            print(dir(tool))
            print("")

        if tool_controller is not None:
            if tool_controller.ToolNumber != current_tool_number:
                post_list.append(tool_controller)
                current_tool_number = tool_controller.ToolNumber
        post_list.append(operation)

    # Generate the G-code *post* and export it to *gcode_path*:
    post: Any = PathPostProcessor.PostProcessor.load(job.PostProcessor)
    post.export(post_list, gcode_path, job.PostProcessorArgs)
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
    # Disable for now
    document_name: str = "JobTest"
    document: "App.Document" = get_document(document_name, tracing=next_tracing)

    model(document, tracing=next_tracing)

    document.recompute()
    document.saveAs("/tmp/bar.fcstd")

    # Disable for now
    # FabBitTemplate._unit_tests()
    if tracing:
        print(f"{tracing}<=main()")


if True or __name__ == "__main__":
    print("here 10")
    main(tracing=" ")
    print("here 100")
    sys.exit()
