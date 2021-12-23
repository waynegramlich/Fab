#!/usr/bin/env python3
"""Solid: A module for constructing 3D solids."""

# [Part2DObject](http://www.iesensor.com/FreeCADDoc/0.16-dev/d9/d57/classPart_1_1Part2DObject.html)
# [App FeaturePython](https://wiki.freecadweb.org/App_FeaturePython)
# [Vidos from "Part Design Scripting" Guy](https://www.youtube.com/c/mwganson/videos)
# [Part Design Scripting](https://forum.freecadweb.org/viewtopic.php?t=62751)
# [Scripted Objects](https://wiki.freecadweb.org/Scripted_objects)
# [FilletArc]
#     (https://github.com/FreeCAD/FreeCAD/blob/master/src/Mod/PartDesign/Scripts/FilletArc.py)
# [Creating and Manipulating Geometry](https://yorikvanhavre.gitbooks.io/
#    a-freecad-manual/content/python_scripting/creating_and_manipulating_geometry.html)
# [Use LineSegment instead of Line](https://forum.freecadweb.org/viewtopic.php?p=330999)
# [Topo Data Scripting](https://wiki.freecadweb.org/index.php?title=Topological_data_scripting)
# [Part Scripting](https://wiki.freecadweb.org/Part_scripting)

# [Draft SelectPlane](https://wiki.freecadweb.org/Draft_SelectPlane)
# [Draft Workbench Scripting](https://wiki.freecadweb.org/Draft_Workbench#Scripting)

# [Sketcher Constraint Angle](https://wiki.freecadweb.org/Sketcher_ConstrainAngle)
# [Sketcher Scripting](https://wiki.freecadweb.org/Sketcher_ConstrainAngle)
# [Sketcher Switch Between Multiple Solutions](https://www.youtube.com/watch?v=Q43K23k1noo&t=20s)
# [Sketcher Toggle Constructions](https://wiki.freecadweb.org/Sketcher_ToggleConstruction)

# [Combine Draft and Sketch to simplify Modeling.](https://www.youtube.com/watch?v=lfzGEk727eo)

# Note this code uses nested dataclasses that are frozen.  Computed attributes are tricky.
# See (Set frozen data class files in __post_init__)[https://stackoverflow.com/questions/53756788]

import os
import sys

assert sys.version_info.major == 3  # Python 3.x
assert sys.version_info.minor == 8  # Python 3.8
sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])

from dataclasses import dataclass, field
from typing import Any, cast, Dict, Optional, Set, Tuple
from pathlib import Path
from Apex import ApexColor

import FreeCAD  # type: ignore
import Part  # type: ignore
import FreeCAD as App  # type: ignore
import FreeCADGui as Gui  # type: ignore

# from Apex import ApexBox, ApexCheck, vector_fix
from FreeCAD import Placement, Rotation, Vector
# import Part  # type: ignore

from Geometry import ModFabCircle, ModFabGeometry, ModFabPolygon

# ModFabFile:
@dataclass
class ModFabFile(object):
    """ModFabFile: Represents a FreeCAD document file."""

    FilePath: Path
    Parts: Tuple["ModFabSolid", ...]
    AppDocument: App.Document = field(init=False, repr=False)
    GuiDocument: Optional["Gui.Document"] = field(init=False, default=None, repr=False)
    Part: "ModFabSolid" = field(init=False, repr=False)
    ViewObject: Optional[Any] = field(init=False, default=None, repr=False)
    GeometryGroup: App.DocumentObjectGroup = field(init=False, repr=False)
    Body: "Part.BodyBase" = field(init=False, repr=False)
    Mount: "ModFabMount" = field(init=False, repr=False)
    DatumPlane: "Part.Geometry" = field(init=False, repr=False)

    # ModFabFile.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the AppDocument."""
        part: ModFabSolid
        part_names: Set[str] = set()
        if len(self.Parts) == 0:
            raise ValueError("At least one ModFabSolid needs to be specified")
        for part in self.Parts:
            if not isinstance(part, ModFabSolid):
                raise ValueError(f"{part} is not a ModFabSolid")
            if part.Name in part_names:
                raise ValueError(f"There are two or more Part's with the same name '{part.Name}'")
            part_names.add(part.Name)

        self.GeometryGroup = cast(App.DocumentObjectGroup, None)
        self.Part = cast(ModFabSolid, None)
        self.Body = cast(Part.BodyBase, None)
        self.Mount = cast("ModFabMount", None)
        self.DatumPlane = cast("Part.Geometry", None)

        stem: str = self.FilePath.stem
        self.AppDocument = App.newDocument(stem)
        assert isinstance(self.AppDocument, App.Document)
        self.GuiDocument = None
        if App.GuiUp:
            self.GuiDocument = Gui.getDocument(stem)  # pragma: no unit cover
            assert isinstance(self.GuiDocument, Gui.Document)

    # ModFabFile.__enter__():
    def __enter__(self) -> "ModFabFile":
        """Open the ModFabFile."""
        return self

    # ModFabFile.__exit__():
    def __exit__(self, exec_type, exec_value, exec_table) -> None:
        """Close the ModFabFile."""
        if self.AppDocument:
            print(f"saving {self.FilePath}")
            self.AppDocument.recompute()
            self.AppDocument.saveAs(str(self.FilePath))

    # ModFabFile.produce():
    def produce(self, context: Dict[str, Any]) -> None:
        """Produce all of the ModFabSolid's."""
        part: "ModFabSolid"
        for part in self.Parts:
            self.Part = part
            part.produce(context.copy())
            self.Part = cast(ModFabSolid, None)

    # ModFabFile._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Run ModFabFile unit tests."""
        # Empty parts error:
        fcstd_path: Path = Path("/tmp/part_file_test.fcstd")
        try:
            ModFabFile(fcstd_path, ())
            assert False
        except ValueError as value_error:
            assert str(value_error) == "At least one ModFabSolid needs to be specified"

        # Bogus parts error:
        try:
            ModFabFile(fcstd_path, (cast(ModFabSolid, None),))
            assert False
        except ValueError as value_error:
            assert str(value_error) == "None is not a ModFabSolid"

        # Duplicate part name error:
        contact: Vector = Vector()
        z_axis: Vector = Vector(0, 0, 1)
        y_axis: Vector = Vector(0, 1, 0)
        origin: Vector = Vector()
        circle1: ModFabCircle = ModFabCircle(origin, 10.0)
        depth1: float = 10.0
        pad1: ModFabPad = ModFabPad("Cylinder1", circle1, depth1)
        operations1: Tuple[ModFabOperation, ...] = (pad1,)
        mount1: ModFabMount = ModFabMount("Mount1", contact, z_axis, y_axis, operations1)
        part1: ModFabSolid = ModFabSolid("Part1", "hdpe", "orange", (mount1,))

        # Duplicate Part Names:
        try:
            ModFabFile(fcstd_path, (part1, part1))
            assert False
        except ValueError as value_error:
            assert str(value_error) == "There are two or more Part's with the same name 'Part1'"

        # Test Open/Produce/Close
        _ = fcstd_path.unlink if fcstd_path.exists() else None
        model_file: ModFabFile
        with ModFabFile(fcstd_path, (part1,)) as model_file:
            assert isinstance(model_file, ModFabFile)
            context: Dict[str, Any] = {
                "app_document": model_file.AppDocument,
                "gui_document": model_file.GuiDocument,
            }
            model_file.produce(context.copy())
        assert fcstd_path.exists(), f"{fcstd_path} file not generated."
        fcstd_path.unlink()
        assert not fcstd_path.exists()


# ModFabOperation:
@dataclass(frozen=True)
class ModFabOperation(object):
    """ModFabOperation: An base class for operations -- ModFabPad, ModFabPocket, ModFabHole, etc.

    All model operations are immutable (i.e. frozen.)
    """

    # ModFabOperation.get_name():
    def get_name(self) -> str:
        """Return ModFabOperation name."""
        raise NotImplementedError(f"{type(self)}.get_name() is not implemented")

    # ModFabOperation.produce():
    def produce(self, context: Dict[str, Any], prefix: str) -> None:
        """Return the operation sort key."""
        raise NotImplementedError(f"{type(self)}.produce() is not implemented")

    # ModFabOperation.produce_shape_binder():
    def produce_shape_binder(self, context: Dict[str, Any],
                             part_geometries: Tuple[Part.Part2DObject, ...],
                             prefix: str) -> Part.Feature:
        """Produce the shape binder needed for the pad, pocket, hole, ... operations."""
        assert "body" in context
        body: Any = context["body"]
        assert isinstance(body, Part.BodyBase)

        shape_binder: Part.Feature = body.newObject(
            "PartDesign::SubShapeBinder", f"{prefix}_Binder")
        assert isinstance(shape_binder, Part.Feature)
        shape_binder.Support = (part_geometries)
        shape_binder.Visibility = False
        return shape_binder

    # ModFabOperation._viewer_upate():
    def _viewer_update(self, body: Part.BodyBase, part_feature: Part.Feature) -> None:
        """Update the view Body view provider."""
        if App.GuiUp:  # pragma: no unit cover
            visibility_set(part_feature, True)
            view_object: Any = body.getLinkedObject(True).ViewObject
            part_feature.ViewObject.LineColor = getattr(
                view_object, "LineColor", part_feature.ViewObject.LineColor)
            part_feature.ViewObject.ShapeColor = getattr(
                view_object, "ShapeColor", part_feature.ViewObject.ShapeColor)
            part_feature.ViewObject.PointColor = getattr(
                view_object, "PointColor", part_feature.ViewObject.PointColor)
            part_feature.ViewObject.Transparency = getattr(
                view_object, "Transparency", part_feature.ViewObject.Transparency)
            # The following code appears to disable edge highlighting:
            # part_feature.ViewObject.DisplayMode = getattr(
            #    view_object, "DisplayMode", part_feature.ViewObject.DisplayMode)


# ModFabPad:
@dataclass(frozen=True)
class ModFabPad(ModFabOperation):
    """ModFabPad: A FreeCAD PartDesign Pad operation.

    Attributes:
    * *Name* (str): The operation name.
    * *Geometry* (ModFabGeometry): The ModlePolygon or ModFabCircle to pad with.
    * *Depth* (float): The depth to pad to in millimeters.

    """

    Name: str
    Geometry: ModFabGeometry
    Depth: float

    # ModFabPad.__post_init__():
    def __post_init__(self) -> None:
        """Verify ModFabPad values."""
        if not isinstance(self.Geometry, ModFabGeometry):
            raise ValueError(f"{self.Geometry} is not a ModFabGeometry")
        if self.Depth <= 0.0:
            raise ValueError(f"Depth ({self.Depth}) is not positive.")

    # ModFabPad.get_name():
    def get_name(self) -> str:
        """Return ModFabPad name."""
        return self.Name

    # ModFabPad.produce():
    def produce(self, context: Dict[str, Any], prefix: str) -> None:
        """Produce the Pad."""
        # Extract the *part_geometries* and create the assocated *shape_binder*:
        next_prefix: str = f"{prefix}_{self.Name}"
        part_geometries: Tuple[Part.Part2DObject, ...] = self.Geometry.produce(context.copy(),
                                                                               next_prefix)
        shape_binder: Part.Feature = self.produce_shape_binder(
            context, part_geometries, next_prefix)
        assert isinstance(shape_binder, Part.Feature)
        shape_binder.Visibility = False

        # Extract *body* and *normal* from *context*:
        assert "body" in context, context
        body: Any = context["body"]
        assert isinstance(body, Part.BodyBase)
        assert "mount_normal" in context, context
        mount_normal: Any = context["mount_normal"]
        assert isinstance(mount_normal, Vector)

        # Perform The Pad operation:
        pad: Part.Feature = body.newObject("PartDesign::Pad", next_prefix)
        assert isinstance(pad, Part.Feature)
        pad.Type = "Length"  # Type in ("Length", "TwoLengths", "UpToLast", "UpToFirst", "UpToFace")
        pad.Profile = shape_binder
        pad.Length = self.Depth
        pad.Length2 = 0  # Only for Type == "TwoLengths"
        pad.UseCustomVector = True
        pad.Direction = mount_normal  # This may be bogus
        pad.UpToFace = None
        pad.Reversed = True
        pad.Midplane = False
        pad.Offset = 0  # Only for Type in ("UpToLast", "UpToFirst", "UpToFace")

        # For the GUI, update the view provider:
        self._viewer_update(body, pad)


# ModFabPocket:
@dataclass(frozen=True)
class ModFabPocket(ModFabOperation):
    """ModFabPocket: A FreeCAD PartDesign Pocket operation.

    Attributes:
    * *Name* (str): The operation name.
    * *Geometry* (ModFabGeometry): The Polygon or Circle to pocket.
    * *Depth* (float): The pocket depth in millimeters.

    """

    Name: str
    Geometry: ModFabGeometry
    Depth: float

    # ModFabPocket__post_init__():
    def __post_init__(self) -> None:
        """Verify ModFabPad values."""
        if not isinstance(self.Geometry, ModFabGeometry):
            raise ValueError(f"{self.Geometry} is not a ModFabGeometry")
        if self.Depth <= 0.0:
            raise ValueError(f"Depth ({self.Depth}) is not positive.")

    # ModFabPocket.get_name():
    def get_name(self) -> str:
        """Return ModFabPocket name."""
        return self.Name

    # ModFabPocket.produce():
    def produce(self, context: Dict[str, Any], prefix: str) -> None:
        """Produce the Pad."""
        # Extract the *part_geometries*:
        next_prefix: str = f"{prefix}_{self.Name}"
        part_geometries: Tuple[Part.Part2DObject, ...] = self.Geometry.produce(context.copy(),
                                                                               next_prefix)
        # Create the *shape_binder*:
        shape_binder: Part.Feature = self.produce_shape_binder(
            context, part_geometries, next_prefix)
        assert isinstance(shape_binder, Part.Feature)

        # Create the *pocket* into *body*:
        assert "body" in context, context
        body: Any = context["body"]
        assert isinstance(body, Part.BodyBase)

        pocket: Part.Feature = body.newObject("PartDesign::Pocket", f"{next_prefix}_Pocket")
        assert isinstance(pocket, Part.Feature)
        pocket.Profile = shape_binder
        pocket.Length = self.Depth
        pocket.Length2 = 10.0 * self.Depth
        pocket.Type = 0
        pocket.UpToFace = None
        pocket.Reversed = 0
        pocket.Midplane = 0
        pocket.Offset = 0

        # For the GUI, update the view provider:
        self._viewer_update(body, pocket)


# ModFabHole:
@dataclass(frozen=True)
class ModFabHole(ModFabOperation):
    """ModFabHole: A FreeCAD PartDesign Pocket operation.

    Attributes:
    * *Name* (str): The operation name.
    * *Circle* (ModFabCircle): The Circle to drill.
    * *Depth* (float): The depth

    """

    Name: str
    Circle: ModFabCircle
    Depth: float

    # ModFabHole.__post_init__():
    def __post_init__(self) -> None:
        """Verify ModFabPad values."""
        if not isinstance(self.Circle, ModFabCircle):
            raise ValueError(f"{self.Geometry} is not a ModFabCircle")
        if self.Depth <= 0.0:
            raise ValueError(f"Depth ({self.Depth}) is not positive.")

    # ModFabHole.get_name():
    def get_name(self) -> str:
        """Return ModFabHole name."""
        return self.Name

    # ModFabHole.produce():
    def produce(self, context: Dict[str, Any], prefix: str) -> None:
        """Produce the Hole."""
        # Extract the *part_geometries*:
        next_prefix: str = f"{prefix}_{self.Name}"
        part_geometries: Tuple[Part.Part2DObject, ...] = self.Circle.produce(context.copy(),
                                                                             next_prefix)
        # Create the *shape_binder*:
        shape_binder: Part.Feature = self.produce_shape_binder(
            context, part_geometries, next_prefix)
        assert isinstance(shape_binder, Part.Feature)

        assert "body" in context, context
        body: Any = context["body"]
        assert isinstance(body, Part.BodyBase)

        # Create the *pocket* and upstate the view provider for GUI mode:
        hole: Part.Feature = body.newObject("PartDesign::Hole", f"{next_prefix}_Hole")
        assert isinstance(hole, Part.Feature)
        hole.Profile = shape_binder
        hole.Diameter = self.Circle.Diameter
        hole.Depth = self.Depth
        hole.UpToFace = None
        hole.Reversed = 0
        hole.Midplane = 0

        # For the GUI, update the view provider:
        self._viewer_update(body, hole)


# ModFabMount:
@dataclass(frozen=True)
class ModFabMount(object):
    """ModFabMount: An operations plane that can be oriented for subsequent machine operations.

    This class basically corresponds to a FreeCad Datum Plane.  It is basically the surface
    to which the 2D ModFabGeometry's are mapped onto prior to performing each operation.
    This class is immutable (i.e. frozen.)

    Attributes:
    * *Name*: (str): The name of the ModFabPlane.
    * *Contact* (Vector): A point on the plane.
    * *Normal* (Vector): A normal to the plane
    * *North* (Vector):
      A vector in the plane that specifies the north direction when mounted  in a machining vice.
    * *Operations* (Tuple[ModFabOperation, ...]): The operations to perform.

    """

    Name: str
    Contact: Vector
    Normal: Vector
    North: Vector
    Operations: Tuple[ModFabOperation, ...]

    # ModFabMount.__post_init__():
    def __post_init__(self) -> None:
        """Verify that ModFabMount arguments are valid."""
        # (Why __setattr__?)[https://stackoverflow.com/questions/53756788]
        copy: Vector = Vector()  # Make private copy of Vector's.
        object.__setattr__(self, "Contect", self.Contact + copy)
        object.__setattr__(self, "Normal", self.Normal + copy)
        object.__setattr__(self, "North", self.North + copy)

        # Disallow duplicate operation names:
        operation_names: Set[str] = set()
        operation: ModFabOperation
        for operation in self.Operations:
            operation_name: str = operation.get_name()
            if operation_name in operation_names:
                raise ValueError("Mount '{self.Name}' has two operations named '{operation_name}'")
            operation_names.add(operation_name)

    # ModFabMount.produce():
    def produce(self, context: Dict[str, Any], prefix: str) -> None:
        """Create the FreeCAD DatumPlane used for the drawing support.

        Arguments:
        * *body* (PartDesign.Body): The FreeCAD Part design Body to attach the datum plane to.
        * *name* (Optional[str]): The datum plane name.
          (Default: "...DatumPlaneN", where N is incremented.)
        * Returns:
          * (Part.Geometry) that is the datum_plane.

        """
        # This is where the math for FreeCAD DatumPlane's is discussed.
        #
        # Here is the notation used in this comment:
        #
        # Scalars: a, b, c, ...  (i.e. a lower case letter)
        # Vectors: P, N, Pa, ... (i.e. an upper case letter with optional suffix letter)
        # Magnitude: |N|, |P|, ... (i.e. a vector with vertical bars on each side.)
        # Unit Normal: <N>, <P>, ... (i.e. a vector enclosed in angle brakcets < ...>).)
        # Dot Product: N . P (i.e. two vectors separated by a period.)
        # Vector scaling: s * V (i.e. a scalar times a vector.)
        # Note that:  |N| * <N> = N
        #
        # The section on Hessian normal plane representation from:
        # * [MathWorld Planes](https://mathworld.wolfram.com/Plane.html)
        # is worth reading.
        #
        # The base coordinate system ('b' suffix) has an origin (Ob=(0,0,0)), X axis (<Xb>=(1,0,0)),
        # Y axis (<Yb>=(0,1,0), and Z axis (<Zb>=(0,0,1).
        #
        # A datum plane specifies a new coordinate system ('d' suffix) that has an Origin (Od),
        # X axis (<Xd>), Y axis (<Yd>), and Z axis (<Zd>).
        #
        # The math for computing these values is discussed immediately below:
        #
        # A plane is specified by a contact point Pd on the plane and a normal Nd to the plane.
        # The normal can be at any point on the plane.
        #
        # The datum plane origin is computed as:
        #
        #     Od = Os + d * <Nd>
        #
        # where d is a signed distance computed as:
        #
        #     d = - (<Nd> . Pd)

        # Compute *rotation* from <Zb> to <Nd>:
        contact: Vector = self.Contact  # Pd
        normal: Vector = self.Normal  # <Nd>
        distance: float = normal.dot(contact)  # d = - (<Nd> . Pd)
        origin: Vector = normal * distance  # Od = Os + d * <Nd>
        z_axis: Vector = Vector(0, 0, 1)  # <Zb>
        rotation: Rotation = Rotation(z_axis, normal)  # Rotation from <Zb> to <Nd>.

        tracing: str = ""
        if tracing:
            print(f"{tracing}{contact=}")
            print(f"{tracing}{normal=}")
            print(f"{tracing}{origin=}")
            print(f"{tracing}{rotation=}")

        # Create, save and return the *datum_plane*:
        assert "body" in context, context
        body: Any = context["body"]
        assert isinstance(body, Part.BodyBase)

        datum_plane: Part.Geometry = body.newObject("PartDesign::Plane", f"{self.Name}_Datum_Plane")
        # visibility_set(datum_plane, False)
        datum_plane.Visibility = False
        # xy_plane: App.GeoGeometry = body.getObject("XY_Plane")
        placement: Placement = Placement(origin, rotation)
        if tracing:
            print(f"{tracing}{placement=}")
        datum_plane.AttachmentOffset = Placement()  # Null placement:  Use Placement instead
        datum_plane.Placement = placement
        datum_plane.MapMode = "Translate"
        datum_plane.MapPathParameter = 0.0
        datum_plane.MapReversed = False
        datum_plane.Support = None
        datum_plane.recompute()

        if App.GuiUp:  # pragma: no unit cover
            assert "gui_document" in context
            gui_document: Any = context["gui_document"]  # Type Optional[Gui.Document]
            assert gui_document, "No GUI document"

            object_name: str = datum_plane.Name
            gui_datum_plane: Any = gui_document.getObject(object_name)
            if gui_datum_plane is not None and hasattr(gui_datum_plane, "Visibility"):
                setattr(gui_datum_plane, "Visibility", False)

        # Provide datum_plane to lower levels of produce:
        context["mount_datum_plane"] = datum_plane
        context["mount_normal"] = self.Normal
        context["mount_contact"] = self.Contact

        # Install the ModFabMount (i.e. *self*) and *datum_plane* into *model_file* prior
        # to recursively performing the *operations*:
        operation: ModFabOperation
        for operation in self.Operations:
            operation.produce(context.copy(), prefix)


# ModFabSolid:
@dataclass(frozen=True)
class ModFabSolid(object):
    """ModFab: Represents a single part constructed using FreeCAD Part Design paradigm.

    Attributes:
    * *Name* (str): The model name.
    * *Material* (str): The material to use.
    * *Color* (str): The color to use.
    * *Mounts* (Tuple[ModFabMount, ...]): The various model mounts to use to construct the part.

    """

    Name: str
    Material: str
    Color: str
    Mounts: Tuple[ModFabMount, ...]

    # ModFabSolid.__post_init__():
    def __post_init__(self) -> None:
        """Verify ModFabSolid arguments."""
        # Verify that there is only one pad operation and it is the very first one.
        # Also detect duplicate mount names:
        mounts: Tuple[ModFabMount, ...] = self.Mounts
        if not mounts:
            raise ValueError("ModFabSolid.produce(): No mounts specified for Part 'self.Name'.")

        mount_names: Set[str] = set()
        pad_found: bool = False
        mount_index: int
        mount: ModFabMount
        for mount_index, mount in enumerate(mounts):
            if not isinstance(mount, ModFabMount):
                raise ValueError(f"'{self.Name}': Mount[{mount_index}]: "
                                 f"{type(mount)} is not a ModFabMount")
            if mount.Name in mount_names:
                raise ValueError(f"Part '{self.Name}' has two mounts named '{mount.Name}')")
            mount_names.add(mount.Name)

            # Search for Pad operations:
            operations: Tuple[ModFabOperation, ...] = mount.Operations
            operation_index: int
            operation: ModFabOperation
            for operation_index, operation in enumerate(operations):
                if not isinstance(operation, ModFabOperation):
                    raise ValueError(f"'{self.Name}.{mount.Name}']: Operation[{operation_index}]:"
                                     "{type(operaton)} is not a ModFabOperation")
                if isinstance(operation, ModFabPad):
                    if mount_index != 0 or operation_index != 0:
                        raise ValueError(f"'{self.Name}.{mount.Name}.{operation.Name}':"
                                         "Pad is not at the very beginning.")
                    pad_found = True
        if not pad_found:
            raise ValueError(f"No Pad operation found for '{self.Name}'")

    # ModFabSolid.produce():
    def produce(self, context: Dict[str, Any]) -> None:
        """Produce the ModFabSolid."""
        assert "app_document" in context, context
        app_document: Any = context["app_document"]
        assert isinstance(app_document, App.Document)

        # Create the *geometry_group* that contains all of the 2D geometry (line, arc, circle.):
        geometry_group: App.DocumentObjectGroup = app_document.addObject(
            "App::DocumentObjectGroup", f"{self.Name}_Geometry")
        geometry_group.Visibility = False
        context["geometry_group"] = geometry_group

        # Create the *body*
        body: Part.BodyBase = app_document.addObject("PartDesign::Body", self.Name)
        context["body"] = body

        # Copy "view" fields from *body* to *gui_body* (if we are in graphical mode):
        if App.GuiUp:  # pragma: no cover
            assert "gui_document" in context
            gui_document: Any = context["gui_document"]  # Type Optional[Gui.Document]
            assert gui_document, "No GUI document"

            gui_body: Any = gui_document.getObject(body.Name)
            assert gui_body, "No GUI body"
            assert hasattr(gui_body, "ShapeColor"), "Something is wrong"
            if hasattr(gui_body, "Proxy"):
                # This magical line seems to get a view provider object into the Proxy field:
                setattr(gui_body, "Proxy", 0)  # Must not be `None`
            if hasattr(gui_body, "DisplayMode"):
                setattr(gui_body, "DisplayMode", "Shaded")
            if hasattr(gui_body, "ShapeColor"):
                rgb = ApexColor.svg_to_rgb(self.Color)
                setattr(gui_body, "ShapeColor", rgb)

            # view_object: "ViewProviderDocumentObject"  = body.getLinkedObject(True).ViewObject
            # assert isinstance(view_object, ViewProviderDocumentObject), type(view_object)
            # model_file.ViewObject = view_object

        # Process each *mount*:
        mount: ModFabMount
        for mount in self.Mounts:
            prefix: str = mount.Name
            mount.produce(context.copy(), prefix)


# Box:
@dataclass
class Box(object):
    """ModFab a box.

    Builds a box given a length, width, height, material, thickness and center point"

    Attributes:
    * *Name* (str): Box name.
    * *Length* (float): length in X direction in millimeters.
    * *Width* (float): width in Y direction in millimeters.
    * *Height* (float): height in Z direction in millimeters.
    * *Thickness* (float): Material thickness in millimeters.
    * *Material* (str): Material to use.
    * *Center* Vector: Center of Box.

    """

    Name: str
    Length: float
    Width: float
    Height: float
    Thickness: float
    Material: str
    Center: Vector

    # Box.compute():
    def compute(self) -> None:
        """Compute a box."""
        pass

    def produce(self) -> Tuple[ModFabSolid, ...]:
        """Produce a box."""
        dx: float = self.Length
        dy: float = self.Width
        dz: float = self.Height
        dw: float = self.Thickness

        dx2: float = dx / 2
        dy2: float = dy / 2
        dz2: float = dz / 2

        corner_radius: float = 3.0

        east_axis: Vector = Vector(1, 0, 0)
        north_axis: Vector = Vector(0, 1, 0)
        top_axis: Vector = Vector(0, 0, 1)
        west_axis: Vector = -east_axis
        south_axis: Vector = -north_axis
        bottom_axis: Vector = -top_axis

        Corners = Tuple[Tuple[Vector, float], ...]
        center: Vector = self.Center
        top_corners: Corners = (
            (center + Vector(dx2, dy2, dz2), corner_radius),  # TNE
            (center + Vector(-dx2, dy2, dz2), corner_radius),  # TNW
            (center + Vector(-dx2, -dy2, dz2), corner_radius),  # TSW
            (center + Vector(dx2, -dy2, dz2), corner_radius),  # TSE
        )
        top_polygon: ModFabPolygon = ModFabPolygon("Top", top_corners)
        top_operations: Tuple[ModFabOperation, ...] = (
            ModFabPad("Pad", top_polygon, dw),
        )
        top_mount: ModFabMount = ModFabMount(
            "TopNorth", center + Vector(0, 0, dz2), top_axis, north_axis, top_operations)
        top_part: ModFabSolid = ModFabSolid("Top", "hdpe", "red", (top_mount,))

        north_corners: Corners = (
            (center + Vector(dx2, dy2, dz2 - dw), corner_radius),  # TNE
            (center + Vector(-dx2, dy2, dz2 - dw), corner_radius),  # TNW
            (center + Vector(-dx2, dy2, -dz2), corner_radius),  # BNW
            (center + Vector(dx2, dy2, -dz2), corner_radius),  # BNE
        )
        north_polygon: ModFabPolygon = ModFabPolygon("North", north_corners)
        north_operations: Tuple[ModFabOperation, ...] = (
            ModFabPad("Pad", north_polygon, dw),
        )
        north_mount: ModFabMount = ModFabMount(
            "NorthBottom", center + Vector(0, dy2, 0), north_axis, bottom_axis, north_operations)
        north_part: ModFabSolid = ModFabSolid("North", "hdpe", "green", (north_mount,))

        west_corners: Corners = (
            (center + Vector(-dx2, dy2 - dw, dz2 - dw), corner_radius),  # TNW
            (center + Vector(-dx2, -dy2 + dw, dz2 - dw), corner_radius),  # TSW
            (center + Vector(-dx2, -dy2 + dw, -dz2 + dw), corner_radius),  # BSW
            (center + Vector(-dx2, dy2 - dw, -dz2 + dw), corner_radius),  # BNW
        )
        west_polygon: ModFabPolygon = ModFabPolygon("West", west_corners)
        west_operations: Tuple[ModFabOperation, ...] = (
            ModFabPad("Pad", west_polygon, dw),
        )
        west_mount: ModFabMount = ModFabMount(
            "WestNorth", center + Vector(-dx2, 0, 0), west_axis, north_axis, west_operations)
        west_part: ModFabSolid = ModFabSolid("West", "hdpe", "blue", (west_mount,))

        bottom_corners: Corners = (
            (center + Vector(dx2, dy2 - dw, -dz2), corner_radius),  # BNE
            (center + Vector(-dx2, dy2 - dw, -dz2), corner_radius),  # BNW
            (center + Vector(-dx2, -dy2 + dw, -dz2), corner_radius),  # BSW
            (center + Vector(dx2, -dy2 + dw, -dz2), corner_radius),  # BSE
        )
        bottom_polygon: ModFabPolygon = ModFabPolygon("Bottom", bottom_corners)
        bottom_operations: Tuple[ModFabOperation, ...] = (
            ModFabPad("Pad", bottom_polygon, dw),
        )
        bottom_mount: ModFabMount = ModFabMount(
            "BottomNorth", center + Vector(0, 0, -dz2), bottom_axis, north_axis, bottom_operations)
        bottom_part: ModFabSolid = ModFabSolid("Bottom", "hdpe", "red", (bottom_mount,))

        east_corners: Corners = (
            (center + Vector(dx2, dy2 - dw, dz2 - dw), corner_radius),  # TNE
            (center + Vector(dx2, -dy2 + dw, dz2 - dw), corner_radius),  # TSE
            (center + Vector(dx2, -dy2 + dw, -dz2 + dw), corner_radius),  # BSE
            (center + Vector(dx2, dy2 - dw, -dz2 + dw), corner_radius),  # BNE
        )
        east_polygon: ModFabPolygon = ModFabPolygon("East", east_corners)
        east_operations: Tuple[ModFabOperation, ...] = (
            ModFabPad("Pad", east_polygon, dw),
        )
        east_mount: ModFabMount = ModFabMount(
            "EastNorth", center + Vector(dx2, 0, 0), east_axis, north_axis, east_operations)
        east_part: ModFabSolid = ModFabSolid("East", "hdpe", "blue", (east_mount,))

        south_corners: Corners = (
            (center + Vector(dx2, -dy2, dz2 - dw), corner_radius),  # TSE
            (center + Vector(-dx2, -dy2, dz2 - dw), corner_radius),  # TSW
            (center + Vector(-dx2, -dy2, -dz2), corner_radius),  # BSW
            (center + Vector(dx2, -dy2, -dz2), corner_radius),  # BSE
        )
        south_polygon: ModFabPolygon = ModFabPolygon("South", south_corners)
        south_operations: Tuple[ModFabOperation, ...] = (
            ModFabPad("Pad", south_polygon, dw),
        )
        south_mount: ModFabMount = ModFabMount(
            "SouthBottom", center + Vector(0, -dy2, 0), south_axis, bottom_axis, south_operations)
        south_part: ModFabSolid = ModFabSolid("South", "hdpe", "green", (south_mount,))

        return (top_part, north_part, west_part, bottom_part, east_part, south_part)


def main() -> None:
    """Run main program."""
    # Create *top_part*:
    z_offset: float = 40.0
    pad_fillet_radius: float = 10.0
    pad_polygon: ModFabPolygon = ModFabPolygon("Pad", (
        (Vector(-40, -60, z_offset), pad_fillet_radius),  # SW
        (Vector(40, -60, z_offset), pad_fillet_radius),  # SE
        (Vector(40, 20, z_offset), pad_fillet_radius),  # NE
        (Vector(-40, 20, z_offset), pad_fillet_radius),  # NW
    ))
    pocket_fillet_radius: float = 2.5
    left_pocket: ModFabPolygon = ModFabPolygon("LeftPocket", (
        (Vector(-30, -10, z_offset), pocket_fillet_radius),
        (Vector(-10, -10, z_offset), pocket_fillet_radius),
        (Vector(-10, 10, z_offset), pocket_fillet_radius),
        (Vector(-30, 10, z_offset), pocket_fillet_radius),
    ))
    right_pocket: ModFabPolygon = ModFabPolygon("RightPocket", (
        (Vector(10, -10, z_offset), pocket_fillet_radius),
        (Vector(30, -10, z_offset), pocket_fillet_radius),
        (Vector(30, 10, z_offset), pocket_fillet_radius),
        (Vector(10, 10, z_offset), pocket_fillet_radius),
    ))
    _ = right_pocket
    right_circle: ModFabCircle = ModFabCircle(Vector(20, 0, z_offset), 10)
    center_circle: ModFabCircle = ModFabCircle(Vector(0, 0, z_offset), 10)

    contact: Vector = Vector(0, 0, z_offset)
    normal: Vector = Vector(0, 0, 1)
    north: Vector = Vector(0, 1, 0)
    top_north_mount: ModFabMount = ModFabMount("TopNorth", contact, normal, north, (
        ModFabPad("Pad", pad_polygon, 50.0),
        ModFabPocket("LeftPocket", left_pocket, 10.0),
        ModFabPocket("RightPocket", right_circle, 8.0),
        ModFabHole("CenterHole", center_circle, 5.0),
    ))
    top_part: ModFabSolid = ModFabSolid("TopPart", "hdpe", "purple", (
        top_north_mount,
    ))
    top_parts: Tuple[ModFabSolid, ...] = (top_part,)

    # Create *side_part*
    side_radius: float = 3.0
    y_offset: float = -50.0
    side_pad: ModFabPolygon = ModFabPolygon("SidePad", (
        (Vector(-50, y_offset, -20), side_radius),
        (Vector(-50, y_offset, 20), side_radius),
        (Vector(50, y_offset, 20), side_radius),
        (Vector(50, y_offset, -20), side_radius),
    ))
    contact = Vector(0, y_offset)
    normal = Vector(0, -1, 0)
    side_north_mount: ModFabMount = ModFabMount("SideNorth", contact, normal, north, (
        ModFabPad("Pad", side_pad, 10),
    ))
    side_part: ModFabSolid = ModFabSolid("SidePart", "hdpe", "green", (
        side_north_mount,
    ))
    _ = side_part

    center: Vector = Vector(0.0, -250, 0.0)
    box: Box = Box("MyBox", 200, 100, 100, 10, "HDPE", center)
    box.compute()
    box_parts: Tuple[ModFabSolid, ...] = box.produce()

    all_parts: Tuple[ModFabSolid, ...] = top_parts + box_parts

    # Create the models:
    model_file: ModFabFile
    # with ModFabFile((top_part, side_part,), Path("/tmp/test.fcstd")) as model_file:
    with ModFabFile(Path("/tmp/test.fcstd"), all_parts) as model_file:
        assert isinstance(model_file.AppDocument, App.Document), (
            type(model_file), type(model_file.AppDocument))
        context: Dict[str, Any] = {
            "app_document": model_file.AppDocument,
            "gui_document": model_file.GuiDocument,
        }
        model_file.produce(context.copy())


def visibility_set(element: Any, new_value: bool = True, tracing: str = "") -> None:
    """Set the visibility of an element.

    Arguments:
    * *element* (Any): Any FreeCAD element.<
    * *new_value* (bool): The new visibility to use.  (Default True):

    """
    if tracing:
        print(f"{tracing}=>visibility_set({element}, {new_value})")
    if App.GuiUp:   # pragma: no unit cover
        if tracing:
            print(f"{tracing}App.GuiUp")
        gui_document: Optional[Any] = (
            Gui.ActiveDocument if hasattr(Gui, "ActiveDocument") else None)
        if tracing:
            print(f"{tracing}{gui_document=}")
            print(f"{tracing}{dir(gui_document)=}")
            print(f"{tracing}{hasattr(gui_document, 'Name')=})")
        if gui_document and hasattr(gui_document, "Name"):
            name: str = getattr(element, "Name")
            if tracing:
                print(f"{tracing}{name=}")
            sub_element: Any = gui_document.getObject(name)
            if sub_element is not None and hasattr(sub_element, "Visibility"):
                if isinstance(getattr(sub_element, "Visibility"), bool):
                    setattr(sub_element, "Visibility", new_value)
    if tracing:
        print(f"{tracing}<=visibility_set({element}, {new_value})")

    if False:  # pragma: no unit cover
        pass
        # App.getDocument('Unnamed').getObject('Body').newObject('PartDesign::Plane', 'DatumPlane')
        # App.getDocument('Unnamed').getObject('DatumPlane').Support = [
        #     (App.getDocument('Unnamed').getObject('XY_Plane'), '')]
        # App.getDocument('Unnamed').getObject('DatumPlane').MapMode = 'FlatFace'
        # App.activeDocument().recompute()
        # Gui.getDocument('Unnamed').setEdit(
        #     App.getDocument('Unnamed').getObject('Body'), 0, 'DatumPlane.')
        # Gui.Selection.clearSelection()

    if False:  # pragma: no unit cover
        # Click on [Plane face]
        pass
        # App.getDocument('Unnamed').getObject('DatumPlane').AttachmentOffset = (
        #     App.Placement(App.Vector(0.0000000000, 0.0000000000, 0.0000000000),
        #                   App.Rotation(0.0000000000, 0.0000000000, 0.0000000000)))
        # App.getDocument('Unnamed').getObject('DatumPlane').MapReversed = False
        # App.getDocument('Unnamed').getObject('DatumPlane').Support = [
        #     (App.getDocument('Unnamed').getObject('XY_Plane'), '')]
        # App.getDocument('Unnamed').getObject('DatumPlane').MapPathParameter = 0.000000
        # App.getDocument('Unnamed').getObject('DatumPlane').MapMode = 'FlatFace'
        # App.getDocument('Unnamed').getObject('DatumPlane').recompute()
        # Gui.getDocument('Unnamed').resetEdit()
        # _tv_DatumPlane.restore()
        # del(_tv_DatumPlane)


if __name__ == "__main__":
    # ModFabPolygon.unit_test()
    ModFabCircle._unit_tests()
    # ModFabFile._unit_tests()  # needs work
    ModFabPolygon._unit_tests()
    main()
