#!/usr/bin/env python3
"""ApexPath: Apex interface to FreeCAD Path workbench."""

# <--------------------------------------- 100 characters ---------------------------------------> #


import sys
sys.path.append(".")
import Embed
Embed.setup()

import FreeCAD as App  # type: ignore
import FreeCADGui as Gui  # type: ignore
from typing import Any, IO, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path

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


# FabCNCTemplate:
@dataclass
class FabCNCTemplate(object):
    """FabCNCShape: Base class for CNC tool bit templates.

    Attributes:
    * *Name* (str): The name of the tool template.
    * *FileName* (str): The tool template file name (must have a suffix of`.fcstd` file)

    """
    
    Name: str
    FileName: str
    ToolHolderHeight: Union[float, str]
    ParameterNames: Tuple[str, ...] = field(init=False, default=())
    AttributeNames: Tuple[str, ...] = field(init=False, default=())
    
    # FabCNCTemplate.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabCNCTemplate."""
        self.str_check("Name")
        self.str_check("FileName")
        self.length_check("ToolHolderHeight")
        if not self.Name:
            raise RuntimeError(f"FabCNCTemplate.__post_init__(): Empty name")
        if not self.FileName.endswith(".fcstd"):
            raise RuntimeError(
                f"FabCNCTemplate.__post_init__(): Filename {self.FileName} does not end in .fcstd")
        
        self._ParameterNames = ()
        self._AttributeNames = ("ToolHolderHeight",)
        

    # FabCNCTemplate.attribute_get():
    def attribute_get(self, attribute_name: str, types: Tuple[type, ...]) -> Any:
        """Return an attribute value by name."""
        if not hasattr(self, attribute_name):
            raise RuntimeError("FabCNCTemplate.attribute_get(): "
                               f"Attribute '{attribute_name} is not present.'")
        attribute: Any = getattr(self, attribute_name)
        if not isinstance(attribute, types):
            raise RuntimeError("FabCNCTemplate.attribute_get(): "
                               f"Attribute '{attribute_name} is {type(attribute)}, not {types}'")
        return attribute

    # FabCNCTemplate.length_check():
    def length_check(self, attribute_name: str) -> None:
        """Verify that length is valid. """
        _ = self.attribute_get(attribute_name, (str, float))

    # FabCNCTemplate.int_check():
    def int_check(self, attribute_name: str, minimum: int) -> None:
        """Verify that length is valid. """
        value: Any = self.attribute_get(attribute_name, (int,))
        if value < minimum:
            raise RuntimeError(f"FabCNCTemplate.int_check('{attribute_name}'): "
                               f"value {value} is less than minumum ({minimum})")

    # FabCNCTemplate.material_check():
    def material_check(self, attribute_name: str) -> None:
        """Verify that integer value is correct."""
        _ = self.attribute_get(attribute_name, (tuple,))

    # FabCNCTemplate.str_check():
    def str_check(self, attribute_name: str) -> None:
        """Verify that text is a string."""
        _ = self.attribute_get(attribute_name, (str,))

    # FabCNCTemplate.write_json():
    def write_json(self, file_path: Path) -> None:
        """Write FabCNCTemptlate out to a JSON file."""
        comma: str
        index: int
        name: str
        value: Union[float, str]

        # Collect all output into *lines*:
        lines: List[str] = [
            '{',
            '  "version": 2,',
            f'  "name": "{self.Name}",',
            f'  "shape": "{self.FileName}",',
        ]

        # Output parameter table:
        lines.append('  "parameter", {')
        size: int = len(self.ParameterNames)
        for index, name in enumerate(self.ParameterNames):
            value = getattr(self, name)
            if isinstance(value, float):
                value = f'{value:.4f} mm'
            comma = "" if index + 1 == size else ","
            lines.append(f'    "{name}": "{value}"{comma}')
        lines.append('  },')

        # Output attribute table:
        lines.append('  "attribute", {')
        size = len(self.AttributeNames)
        for index, name in enumerate(self.AttributeNames):
            value = getattr(self, name)
            if isinstance(value, float):
                value = f'{value:.4f} mm'
            comma = "" if index + 1 == size else ","
            lines.append(f'    "{name}": "{value}"{comma}')
        lines.append('  }')  # No comma for last itme in list.

        # Write *lines* to *file_path*:
        lines.append('}')
        lines.append('')
        json_file: IO[str]
        with open(file_path, 'w') as json_file:
            json_file.write('\n'.join(lines))


# FabEndMill:
@dataclass
class FabEndMill(FabCNCTemplate):
    """FabEndMill: An end-mill tool template.

    Inherited Attributes:
    * *Name* (str): The name of the tool template.
    * *FileName* (str): The tool template file name (must have a suffix of`.fcstd` file)

    Attributes:
    * *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
    * *Diameter* (Union[str, float]): The end mill cutter diameter.
    * *Length* (Union[str, float]): The total length of the end mill.
    * *ShankDiameter: (Union[str, float]): The shank diameter.
    * *ToolHolderHeight: (Union[str, float]): The distance to the tool holder.
    * *Flutes*: (int): The number of flutes.
    * *Material: (str): The tool material.
    * *VendorName*: (str): The vendor name (default: "")
    * *VendorPart*: (str): The vendor part number (default: "")

    """

    CuttingEdgeHeight: Union[str, float]
    Diameter: Union[str, float]
    Length: Union[str, float]
    ShankDiameter: Union[str, float]
    Flutes: int
    Material: Tuple[str, ...]
    Vendor: str = ""
    PartNumber: str = ""

    # FabEndMill.__post_init__():
    def __post_init__(self) -> None:
        """Initialze the FabCNCEndMill."""
        super().__post_init__()
        self.length_check("CuttingEdgeHeight")
        self.length_check("Diameter")
        self.length_check("Length")
        self.length_check("ShankDiameter")
        self.int_check("Flutes", 1)
        self.material_check("Material")
        self.str_check("Vendor")
        self.str_check("PartNumber")
        self.ParameterNames += ("CuttingEdgeHeight", "Diameter", "Length", "ShankDiameter")
        self.AttributeNames += ("Flutes", "Material", "Vendor", "PartNumber")
        print(f"{self.ParameterNames=}")
        print(f"{self.AttributeNames=}")
    

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
    #     return PathToolBit.Factory.CreateFromAttrs(attrs, name)


    # Defined in `.../Path/PathScripts/PathToolController.py`:216:
    # Is a function, not an method:
    # def Create(
    #         name: str, tool: "Tool", toolNumber: int, assignViewProvider: bool = True,
    #         assignTool=True) -> None
    # )

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

    end_mill: FabEndMill = FabEndMill(
        Name="5mm EndMill",
        FileName="endmill.fcstd",
        ToolHolderHeight=20.0,
        CuttingEdgeHeight="30.0000 mm",
        Diameter="5.0000 mm",
        Length="50.0000 mm",
        ShankDiameter="3.0000 mm",
        Flutes=2,
        Material=("steel", "HSS")
    )
    end_mill.write_json(Path("5mm_Endmill.fctb"))

    if tracing:
        print(f"{tracing}<=main()")


if __name__ == "__main__":
    main(tracing=" ")
