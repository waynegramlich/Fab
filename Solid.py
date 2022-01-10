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

# [Combine Draft and Sketch to simplify Modeling.](https://www.youtube.com/watch?v=lfzGEk727eo)

# Note this code uses nested dataclasses that are frozen.  Computed attributes are tricky.
# See (Set frozen data class files in __post_init__)[https://stackoverflow.com/questions/53756788]

import sys
sys.path.append(".")
import Embed
Embed.setup()

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from collections import OrderedDict

import FreeCAD  # type: ignore
import Part  # type: ignore
import FreeCAD as App  # type: ignore
import FreeCADGui as Gui  # type: ignore

from FreeCAD import Placement, Rotation, Vector
# import Part  # type: ignore

from Geometry import FabCircle, FabGeometry, FabGeometryContext
from Join import FabFasten, FabJoin
from Node import FabBox, FabNode
from Utilities import FabColor


# _Internal:
@dataclass
class _Internal(object):
    """_Internal: Base class for various FabSolid internal classes.

    Attributes:
    * *Name* (str): Internal element name.

    """

    _Name: str

    # _Internal.__post_init__():
    def __post_init__(self) -> None:
        """Verify _Internal name."""
        if not isinstance(self._Name, str):
            raise RuntimeError(f"_Internal.__post_init__(): Name is {type(self._Name)}, not str")
        if not FabNode._is_valid_name(self._Name):
            raise RuntimeError(f"_Internal.__post_init__(): Name '{self._Name}' is not valid.")

    @property
    # _Internal.Name():
    def Name(self) -> str:
        """Return _Internal Name."""
        return self._Name

    # _Internal.Mount():
    # @property
    # def Mount(self) -> "FabMount":
    #     """Return Mount."""
    #     raise RuntimeError(f"_Internal.Mount(): Not implemented for {type(self)}")

    # _Internal.Solid():
    # @property
    # def Solid(self) -> "FabSolid":
    #     """Return Solid"""
    #     raise RuntimeError(f"_Internal.Solid(): Not implemented for {type(self)}")

    # _Internal.is_mount():
    def is_mount(self) -> bool:
        """Return True for a FabMount."""
        return False   # Override in FabMount class.

    # _Internal.is_operation():
    def is_operation(self) -> bool:
        """Return True for a FabMount."""
        return False   # Override in FabOperation class.

    # _Internal.is_solid():
    def is_solid(self) -> bool:
        """Return True for a FabSolid."""
        return False   # Override in FabSolid class.


# _Operation:
@dataclass
class _Operation(_Internal):
    """_Operation: An base class for FabMount operations -- _Extrude, _Pocket, FabHole, etc.

    Attributes:
    * *Name* (str): Unique operation name for given mount.
    * *Mount* (FabMount): The FabMount to use for performing operations.

    """

    _Mount: "FabMount"

    # _Operation.__post_init__():
    def __post_init__(self) -> None:
        """Initialize _Operation."""
        super().__post_init__()
        # TODO: Enable check:
        # if not self._Mount.is_mount():
        #   raise RuntimeError("_Operation.__post_init__(): {type(self._Mount)} is not FabMount")

    # _Operation.Mount():
    @property
    def Mount(self) -> "FabMount":
        """Return the Opartion FabMount."""
        return self._Mount

    # _Operation.is_operation():
    def is_operation(self) -> bool:
        """Return True for FabOperation."""
        return True

    # _Operation.get_name():
    def get_name(self) -> str:
        """Return FabOperation name."""
        return self.Name

    # _Operation.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Return the operation sort key."""
        raise NotImplementedError(f"{type(self)}.produce() is not implemented")
        return ()

    # _Operation.produce_shape_binder():
    def produce_shape_binder(self, context: Dict[str, Any],
                             part_geometries: Tuple[Part.Part2DObject, ...],
                             prefix: str, tracing: str = "") -> Part.Feature:
        """Produce the shape binder needed for the extrude, pocket, hole, ... operations."""
        if tracing:
            print(f"{tracing}=>FabOperation.produce_shape_binder()")
        mount: FabMount = self.Mount
        body: Part.BodyBase = mount.Body

        binder_placement: Placement = Placement()  # Do not move/reorient anything.
        if tracing:
            print(f"{tracing}{binder_placement.Rotation.Axis=}")

        name: str = f"{mount.Name}_{self.Name}_Binder"
        shape_binder: Part.Feature = body.newObject("PartDesign::SubShapeBinder", name)
        assert isinstance(shape_binder, Part.Feature)
        shape_binder.Placement = binder_placement
        shape_binder.Support = (part_geometries)
        # shape_binder.Support = (datum_plane, [""])
        shape_binder.Visibility = False
        if tracing:
            print(f"{tracing}<=FabOperation.produce_shape_binder()=>*")
        return shape_binder

    # _Operation._viewer_update():
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


# _Extrude:
@dataclass
class _Extrude(_Operation):
    """_Extrude: A FreeCAD PartDesign Extrude operation.

    Attributes:
    * *Name* (str): The operation name.
    * *Geometry* (Union[FabGeometry, Tuple[FabGeometry, ...]):
      The FabGeometry (i.e. FabPolygon or FabCircle) or a tuple of FabGeometry's to extrude with.
      When the tuple is used, the largest FabGeometry (which is traditionally the first one)
      is the outside of the extrusion, and the rest are "pockets".  This is useful for tubes.
    * *Depth* (float): The depth to extrude to in millimeters.

    """

    _Geometry: Union[FabGeometry, Tuple[FabGeometry, ...]]
    _Geometries: Tuple[FabGeometry, ...] = field(init=False, repr=False)
    _Depth: float

    # _Extrude.__post_init__():
    def __post_init__(self) -> None:
        """Verify _Extrude values."""
        super().__post_init__()

        # Type check self._Geometry and convert into self._Geometries:
        geometries: List[FabGeometry] = []
        self_geometry: Union[FabGeometry, Tuple[FabGeometry, ...]] = self._Geometry
        if isinstance(self_geometry, FabGeometry):
            geometries = [self_geometry]
        elif isinstance(self_geometry, tuple):
            geometry: FabGeometry
            for geometry in self_geometry:
                if not isinstance(geometry, FabGeometry):
                    raise RuntimeError(f"_Extrude.__post_init__({self.Name}):"
                                       f"{type(geometry)} is not a FabGeometry")
                geometries.append(geometry)
        else:
            raise RuntimeError(f"_Extrude.__post_init__({self.Name}):{type(self.Geometry)} "
                               f"is neither a FabGeometry nor a Tuple[FabGeometry, ...]")
        self._Geometries = tuple(geometries)

        if self.Depth <= 0.0:
            raise RuntimeError(f"_Extrude.__post_init__({self.Name}):"
                               f"Depth ({self.Depth}) is not positive.")

    # _Extrude.Geometry():
    @property
    def Geometry(self) -> Union[FabGeometry, Tuple[FabGeometry, ...]]:
        """Return the _Extrude FabGeometry."""
        return self._Geometry

    # _Extrude.Depth():
    @property
    def Depth(self) -> float:
        """Return the Depth."""
        return self._Depth

    # _Extrude.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Produce the Extrude."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>_Extrude.produce('{self.Name}')")

        # Extract the *part_geometries* and create the associated *shape_binder*:
        construct: bool = self._Mount._Solid.Construct
        if construct:
            part_geometries: List[Part.Part2DObject] = []
            mount: FabMount = self.Mount
            geometry_context: FabGeometryContext = mount._GeometryContext
            geometry_group: App.DocumentObjectGroup = mount._Solid._GeometryGroup
            assert isinstance(geometry_group, App.DocumentObjectGroup), geometry_group
            geometry_context.set_geometry_group(geometry_group)

            geometry_prefix: str = f"{mount.Name}_{self.Name}"
            for geometry in self._Geometries:
                part_geometries.extend(geometry.produce(geometry_context, geometry_prefix))

            binder_prefix: str = f"{mount.Name}_{self.Name}"
            shape_binder: Part.Feature = self.produce_shape_binder(
                context.copy(), tuple(part_geometries), binder_prefix, tracing=next_tracing)
            assert isinstance(shape_binder, Part.Feature)
            shape_binder.Visibility = False

            # Extract *body* and *normal* from *context*:
            body: Part.BodyBase = mount.Body
            mount_normal: Vector = mount.Normal

            # Perform The Extrude operation:
            pad_name: str = f"{mount.Name}_{self.Name}_Extrude"
            extrude: Part.Feature = body.newObject("PartDesign::Pad", pad_name)
            assert isinstance(extrude, Part.Feature)
            # Type must be one of ("Length", "TwoLengths", "UpToLast", "UpToFirst", "UpToFace")
            extrude.Type = "Length"
            extrude.Profile = shape_binder
            extrude.Length = self.Depth
            extrude.Length2 = 0  # Only for Type == "TwoLengths"
            extrude.UseCustomVector = True
            extrude.Direction = mount_normal  # This may be bogus
            extrude.UpToFace = None
            extrude.Reversed = True
            extrude.Midplane = False
            extrude.Offset = 0  # Only for Type in ("UpToLast", "UpToFirst", "UpToFace")

            # For the GUI, update the view provider:
            self._viewer_update(body, extrude)

        if tracing:
            print(f"{tracing}<=_Extrude.produce('{self.Name}')")
        return ()

# _Pocket:
@dataclass
class _Pocket(_Operation):
    """_Pocket: A FreeCAD PartDesign Pocket operation.

    Attributes:
    * *Name* (str): The operation name.
    * *Geometry* (Union[FabGeometry, Tuple[FabGeometry, ...]]):
       The Polygon or Circle to pocket.  If a tuple is given, the smaller FabGeometry's
       specify "islands" to not pocket.
    * *Depth* (float): The pocket depth in millimeters.

    """

    _Geometry: Union[FabGeometry, Tuple[FabGeometry, ...]]
    _Depth: float
    _Geometries: Tuple[FabGeometry, ...] = field(init=False, repr=False)

    # _Pocket__post_init__():
    def __post_init__(self) -> None:
        """Verify _Pocket values."""
        super().__post_init__()

        # Type check self._Geometry and convert into self._Geometries:
        geometries: List[FabGeometry] = []
        self_geometry: Union[FabGeometry, Tuple[FabGeometry, ...]] = self._Geometry
        if isinstance(self_geometry, FabGeometry):
            geometries = [self_geometry]
        elif isinstance(self_geometry, tuple):
            geometry: FabGeometry
            for geometry in self_geometry:
                if not isinstance(geometry, FabGeometry):
                    raise RuntimeError(f"_Extrude.__post_init__({self.Name}):"
                                       f"{type(geometry)} is not a FabGeometry")
                geometries.append(geometry)
        else:
            raise RuntimeError(f"_Extrude.__post_init__({self.Name}):{type(self.Geometry)} "
                               f"is neither a FabGeometry nor a Tuple[FabGeometry, ...]")
        self._Geometries = tuple(geometries)

        if self._Depth <= 0.0:
            raise RuntimeError(f"_Extrude.__post_init__({self.Name}):"
                               f"Depth ({self.Depth}) is not positive.")

    # _Pocket.Geometry():
    def Geometry(self) -> Union[FabGeometry, Tuple[FabGeometry, ...]]:
        """Return the original Geometry."""
        return self._Geometry

    # _Pocket.Depth():
    def Depth(self) -> float:
        """Return the original Depth."""
        return self._Depth

    # _Pocket.get_name():
    def get_name(self) -> str:
        """Return _Pocket name."""
        return self.Name

    # _Pocket.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Produce the Pocket."""
        if tracing:
            print("{tracing}=>_Pocket.produce('{self.Name}')")

        # Extract the *part_geometries* from *geometries*:
        geometries: Tuple[FabGeometry, ...] = self._Geometries
        mount: FabMount = self.Mount
        prefix: str = f"{mount.Name}_{self.Name}"
        part_geometries: List[Part.Part2DObject] = []
        geometry_context: FabGeometryContext = mount._GeometryContext
        geometry: FabGeometry
        for geometry in geometries:
            part_geometries.extend(geometry.produce(geometry_context, prefix))

        # Create the *shape_binder*:
        shape_binder: Part.Feature = self.produce_shape_binder(
            context, tuple(part_geometries), prefix)
        assert isinstance(shape_binder, Part.Feature)

        # Create the *pocket* into *body*:
        body: Part.BodyBase = mount.Body
        pocket: Part.Feature = body.newObject("PartDesign::Pocket", f"{prefix}_Pocket")
        assert isinstance(pocket, Part.Feature)
        pocket.Profile = shape_binder
        pocket.Length = self._Depth
        pocket.Length2 = 10.0 * self._Depth
        pocket.Type = 0
        pocket.UpToFace = None
        pocket.Reversed = 0
        pocket.Midplane = 0
        pocket.Offset = 0

        # For the GUI, update the view provider:
        self._viewer_update(body, pocket)

        if tracing:
            print("{tracing}<=_Pocket.produce('{self.Name}')")
        return ()


_HoleKey = Tuple[str, str, float, bool, int]


# _Hole:
@dataclass(order=True)
class _Hole(object):
    """_Hole: FabDrill helper class that represents a hole."""

    # Size: str  # Essentially the diameter
    # Profile: str  # Essentially the fastener thread pitch
    ThreadName: str  # Thread name
    Kind: str  # "thread", "close", or "standard"
    Depth: float  # The depth of the drill hole
    IsTop: bool  # Is the top of the fastener
    Unique: int  # Non-zero to force otherwise common holes into separate operations.
    Center: Vector = field(compare=False)  # The Center (start point) of the drill
    Join: FabJoin = field(compare=False)  # The associated FabJoin

    # _Hole.Key():
    @property
    def Key(self) -> _HoleKey:
        """Return a Hole key."""
        return (self.ThreadName, self.Kind, self.Depth, self.IsTop, self.Unique)


# FabMount:
@dataclass
class FabMount(_Internal):
    """FabMount: An operations plane that can be oriented for subsequent machine operations.

    This class basically corresponds to a FreeCad Datum Plane.  It is basically the surface
    to which the 2D FabGeometry's are mapped onto prior to performing each operation.

    Attributes:
    * *Name*: (str): The name of the FabPlane.
    * *Solid*: (FabSolid): The FabSolid to work on.
    * *Contact* (Vector): A point on the mount plane.
    * *Normal* (Vector): A normal to the mount plane
    * *Orient* (Vector):
      A vector that is projected onto the mount plane to specify orientation
      when mounted for CNC operations.
    * *Depth* (float): The maximum depth limit for all operations.

    """

    _Solid: "FabSolid"
    _Contact: Vector
    _Normal: Vector
    _Orient: Vector
    _Depth: float
    _Operations: "OrderedDict[str, _Operation]" = field(init=False, repr=False)
    _Context: Dict[str, Any] = field(init=False, repr=False)
    _Copy: Vector = field(init=False, repr=False)  # Used for making private copies of Vector's
    _Tracing: str = field(init=False, repr=False)
    _GeometryContext: FabGeometryContext = field(init=False, repr=False)
    _AppDatumPlane: Optional["Part.Geometry"] = field(init=False, repr=False)
    _GuiDatumPlane: Any = field(init=False, repr=False)

    # FabMount.__post_init__():
    def __post_init__(self) -> None:
        """Verify that FabMount arguments are valid."""

        super().__post_init__()
        solid: "FabSolid" = self._Solid

        tracing: str = solid.Tracing
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).__post_init__()")

        # Do type checking here.
        # assert isinstance(self._Name, str)
        assert isinstance(self._Solid, FabSolid)
        assert isinstance(self._Contact, Vector)
        assert isinstance(self._Normal, Vector)
        assert isinstance(self._Orient, Vector)
        assert isinstance(self._Depth, float)

        copy: Vector = Vector()  # Make private copy of Vector's.
        self._Copy = copy
        self._Contact = self._Contact + copy
        self._Normal = self._Normal + copy
        self._Operations = OrderedDict()
        # FreeCAD Vector metheds like to modify Vector contents; force copies beforehand:
        self._Orient = (self._Orient + copy).projectToPlane(
            self._Contact + copy, self._Normal + copy)
        self._Context = {"mount_contact": "bogus"}
        self._Context = {}
        self._GeometryContext = FabGeometryContext(self._Contact, self._Normal)
        self._AppDatumPlane = None
        self._GuiDatumPlane = None

        if tracing:
            print(f"{tracing}{self._Contact=} {self._Normal=} "
                  f"{self._Depth=} {self._GeometryContext=}")
            print(f"{tracing}<=FabMount({self.Name}).__post_init__()")

    # FabMount.Name():
    @property
    def Name(self) -> str:
        """Return the FabMoun name."""
        return self._Name

    # FabMount.Solid:
    @property
    def Solid(self) -> "FabSolid":
        """Return the FabSolid."""
        return self._Solid

    # FabMount.Body:
    @property
    def Body(self) -> Part.BodyBase:
        """Return PartBodyBase fr FabMount."""
        return self._Solid.Body

    # FabMount.Contact:
    @property
    def Contact(self) -> Vector:
        """Return the FabMount contact point."""
        return self._Contact + self._Copy

    # FabMount.Normal:
    @property
    def Normal(self) -> Vector:
        """Return the FabMount normal."""
        return self._Normal + self._Copy

    # FabMount.Orient:
    @property
    def Orient(self) -> Vector:
        """Return the FabMount Orientation."""
        return self._Orient + self._Copy

    # FabMount.Depth:
    @property
    def Depth(self) -> float:
        """Return the depth."""
        return self._Depth

    # FabMount.Construct:
    @property
    def Construct(self) -> bool:
        """Return whether construction is turned on."""
        return self._Solid.Construct

    # FabMount.record_operation():
    def record_operation(self, operation: _Operation) -> None:
        """Record an operation to a FabMount."""
        if not isinstance(operation, _Operation):
            raise RuntimeError(
                "FabMount.add_operation({self._Name}).{type(operation)} is not an _Operation")
        self._Operations[operation.Name] = operation

    # FabMount.set_geometry_group():
    def set_geometry_group(self, geometry_group: App.DocumentObjectGroup) -> None:
        """Set the FabMount GeometryGroup need for the FabGeometryContex."""
        self._GeometryContext.set_geometry_group(geometry_group)

    # FabMount.produce():
    def produce(self, context: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
        """Create the FreeCAD DatumPlane used for the drawing support."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabMount.produce('{self.Name}')")

        if self.Construct:  # and len(self._Operations):
            if tracing:
                print(f"{tracing}>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                print(f"{tracing}{sorted(context.keys())=} {len(self._Operations)=}")
            contact: Vector = self._Contact
            normal: Vector = self._Normal
            z_axis: Vector = Vector(0.0, 0.0, 1.0)
            origin: Vector = Vector()
            # FreeCAD Vector methods like to modify Vector contents; force copies beforehand:
            copy: Vector = Vector()
            projected_origin: Vector = (origin + copy).projectToPlane(contact + copy, normal + copy)
            rotation: Rotation = Rotation(z_axis, normal)
            placement: Placement = Placement()
            placement.Base = projected_origin
            placement.Rotation = rotation

            if tracing:
                print(f"{tracing}{contact=}")
                print(f"{tracing}{normal=}")
                print(f"{tracing}{origin=}")
                print(f"{tracing}{projected_origin=}")
                print(f"{tracing}{rotation=}")
                print(f"{tracing}{placement=}")
                print(f"{tracing}{rotation*z_axis=}")
                print(f"{tracing}{normal=}")

            # Create, save and return the *datum_plane*:
            body: Part.BodyBase = self.Body
            datum_plane_name: str = f"{self.Name}_Datum_Plane"
            datum_plane: "Part.Geometry" = body.newObject("PartDesign::Plane", datum_plane_name)
            # assert isinstance(datum_plane, Part.Geometry), datum_plane
            self._AppDatumPlane = datum_plane

            # visibility_set(datum_plane, False)
            datum_plane.Visibility = False
            # xy_plane: App.GeoGeometry = body.getObject("XY_Plane")
            if tracing:
                print(f"{tracing}{placement=}")
            datum_plane.Label = self._Name
            datum_plane.AttachmentOffset = placement
            datum_plane.Placement = placement
            datum_plane.MapMode = "Translate"
            datum_plane.MapPathParameter = 0.0
            datum_plane.MapReversed = False
            datum_plane.Support = None
            datum_plane.recompute()

            if App.GuiUp:  # pragma: no unit cover
                if tracing:
                    print(f"{tracing}get_gui_document()")
                document_node: FabNode = self._Solid.get_parent_document(tracing=next_tracing)
                gui_document: Any = document_node._GuiObject
                if tracing:
                    print(f"{tracing}{gui_document=}")
                assert hasattr(gui_document, "getObject")
                gui_datum_plane: Any = getattr(gui_document, datum_plane.Name)
                if tracing:
                    print(f"{tracing}{gui_datum_plane=}")
                assert gui_datum_plane is not None
                assert hasattr(gui_datum_plane, "Visibility"), gui_datum_plane
                setattr(gui_datum_plane, "Visibility", False)
                self._GuiDatum_plane = gui_datum_plane

            # Provide datum_plane to lower levels of produce:
            self._Context = context.copy()

            # Install the FabMount (i.e. *self*) and *datum_plane* into *model_file* prior
            # to recursively performing the *operations*:
            if tracing:
                print(f"{tracing}<=FabMount.produce('{self.Name}')")
        return ()

    # FabMount.extrude():
    def extrude(self, name: str, shapes: Union[FabGeometry, Tuple[FabGeometry, ...]],
                depth: float, tracing: str = "") -> None:
        """Perform a extrude operation."""
        tracing = self._Solid.Tracing
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).extrude('{name}', *, {depth})")

        # Figure out the contact
        top_contact: Vector = self._Contact
        copy: Vector = Vector()
        normal: Vector = (self._Normal + copy).normalize()
        bottom_contact: Vector = top_contact - depth * normal
        if tracing:
            print(f"{tracing}{top_contact=} {normal=} {bottom_contact=}")

        # Compute a bounding box that encloses all of the associated *geometries*:
        boxes: List[FabBox] = []
        geometries: Tuple[FabGeometry, ...]
        if isinstance(shapes, FabGeometry):
            geometries = (shapes,)
        else:
            geometries = shapes
        geometry: FabGeometry
        for geometry in geometries:
            # if tracing:
            #     print(f"{tracing}{geometry=}")
            boxes.append(geometry.project_to_plane(top_contact, normal).Box)
            boxes.append(geometry.project_to_plane(bottom_contact, normal).Box)
        self._Solid.enclose(boxes)
        if tracing:
            print(f"{tracing}{self._Solid.BB=}")

        # Create and record the *extrude*:
        extrude: _Extrude = _Extrude(name, self, shapes, depth)
        self.record_operation(extrude)
        # if tracing:
        #     print(f"{tracing}{extrude=}")

        errors: List[str] = []
        if self.Construct:
            context: Dict[str, Any] = self._Context.copy()
            context_keys: Tuple[str, ...]
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}Before Extrude Context: {context_keys}")
            assert isinstance(shapes, FabGeometry)
            assert depth > 0.0

            errors.extend(extrude.produce(context.copy(), next_tracing))
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}After Extrude Context: {context_keys}")

        if tracing:
            print(f"{tracing}<=FabMount({self.Name}).extrude('{name}', *, "
                  f"{depth})=>|{len(errors)}|")

    # FabMount.pocket():
    def pocket(self, name: str, shapes: Union[FabGeometry, Tuple[FabGeometry, ...]],
               depth: float, tracing: str = "") -> None:
        """Perform a pocket operation."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).pocket('{name}', *)")

        # Create the *pocket* and record it into the FabMount:
        pocket: _Pocket = _Pocket(name, self, shapes, depth)
        self.record_operation(pocket)

        errors: List[str] = []
        if self.Construct:   # Construct OK
            context: Dict[str, Any] = self._Context.copy()
            context_keys: Tuple[str, ...]
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}Before Pocket Context: {context_keys}")
            assert isinstance(shapes, FabGeometry)
            assert depth > 0.0
            errors.extend(pocket.produce(context.copy(), next_tracing))
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}After Pocket Context: {context_keys}")

        if tracing:
            print(f"{tracing}<=FabMount({self.Name}).pocket('{name}', *)=>|{len(errors)}|")

    # FabMount.drill_joins():
    def drill_joins(self, name: str,
                    joins: Union[FabJoin, Sequence[FabJoin]], tracing: str = "") -> None:
        """Drill some FabJoin's into a FabMount."""
        # Quickly convert a single FabJoin into a tuple:

        EPSILON: float = 1.0e-8

        # close():
        def close(vector1: Vector, vector2: Vector) -> bool:
            """Return whether 2 normals are very close to one another."""
            return (vector1 - vector2).Length < EPSILON

        if isinstance(joins, FabJoin):
            joins = (joins,)
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabMount({self.Name}).drill_joins(|{len(joins)}|")

        if self.Construct:
            copy: Vector = Vector()
            mount_contact: Vector = self._Contact
            mount_normal: Vector = (self._Normal + copy).normalize()
            mount_depth: float = self._Depth
            body: Part.BodyBase = self.Body
            solid: "FabSolid" = self._Solid
            z_axis: Vector = Vector(0, 0, 1)
            mount_z_aligned: bool = close(mount_normal, z_axis)

            # intersect_joins: List[FabJoin] = []
            holes: List[_Hole] = []
            join_index: int  # Used for forcing individual drill operations (see below):
            for join_index, join in enumerate(joins):
                assert isinstance(join, FabJoin), f"{type(join)} is not a FabJoin"
                fasten: FabFasten = join.Fasten

                if join.normal_aligned(mount_normal):
                    join_start: Vector = join.Start
                    join_end: Vector = join.End
                    # if tracing:
                    #     print(f"{tracing}>>>>>>>>{join.Name} "
                    #            f"aligns {solid.Name}: {join_start}=>{join_end}")
                    intersect: bool
                    trimmed_start: Vector
                    trimmed_end: Vector
                    intersect, trimmed_start, trimmed_end = solid.intersect(join_start, join_end)
                    if intersect:
                        mount_start: Vector = (join_start + copy).projectToPlane(
                            mount_contact + copy, mount_normal + copy)
                        trimmed_length: float = (trimmed_start - trimmed_end).Length
                        trimmed_depth: float = min(trimmed_length, mount_depth)
                        if False and tracing:
                            print(f"{tracing}>>>>>>>>>>>>>>>>{join.Name} intesects {solid.Name}")
                            print(f"{tracing}{solid.Name} Box: {solid.TNE} : {solid.BSW}")
                            print(f"{tracing}Join:    {join_start} => {join_end}")
                            print(f"{tracing}Trimmed: {trimmed_start} => {trimmed_end}")
                            print(f"{tracing}Mount - Depth: {mount_start} {trimmed_depth}")
                        is_top: bool = close(join_start, trimmed_start)
                        # TODO: figure out *kind*:
                        kind: str = "close"  # or "thread", or "loose"
                        # This is extremley ugly for now.  If the *mount_normal* equals the
                        # +Z axis, multiple holes with the same characterisics can be drilled
                        # with one hole operation.  Otherwise, one drill operation per hole
                        # is requrired.  This is done by setting *unique* to *join_index*.
                        if tracing:
                            print(f"{tracing}{mount_depth=} {trimmed_depth=}")
                        assert trimmed_depth > 0.0, trimmed_depth
                        unique: int = -1 if mount_z_aligned else join_index
                        hole: _Hole = _Hole(fasten.ThreadName, kind,
                                            trimmed_depth, is_top, unique, mount_start, join)
                        holes.append(hole)

            # If there is nothing to *holes* intersected:
            if holes:
                if tracing:
                    print(f"{tracing}{len(holes)=}")

                # Group *holes* into *hole_groups* that can be done with one PartDesign hole:
                key: _HoleKey
                hole_groups: Dict[_HoleKey, List[_Hole]] = {}
                for hole in holes:
                    key = hole.Key
                    if key not in hole_groups:
                        hole_groups[key] = []
                    hole_groups[key].append(hole)

                # For each *hole_group* create a PartDesign Hole:
                geometry_context: FabGeometryContext = self._GeometryContext
                geometry_group: App.DocumentObjectGroup = self.Solid._GeometryGroup
                assert isinstance(geometry_group, App.DocumentObjectGroup), geometry_group
                geometry_context.set_geometry_group(geometry_group)

                # Sweep through *hole_groups* generating *part_geometries*:
                group_index: int
                for group_index, key in enumerate(sorted(hole_groups.keys())):
                    # Unpack *key*:
                    thread_name: str
                    thread_name, kind, depth, is_top, unique = key
                    diameter: float = fasten.get_diameter(kind)

                    # Construct the *part_geometries* for each *hole*:
                    part_geometries: List[Part.Part2DObject] = []
                    hole_group: List[_Hole] = hole_groups[key]
                    for hole_index, hole in enumerate(hole_group):
                        center: Vector = hole.Center
                        circle: FabCircle = FabCircle(center, mount_normal, diameter)
                        geometry_prefix: str = (
                            f"{self.Name}_{name}{group_index:03d}")
                        part_geometries.extend(
                            circle.produce(geometry_context,
                                           geometry_prefix, tracing=next_tracing))

                    # Now do the FreeCAD stuff:
                    # Create the *shape_binder*:
                    # suffix: str = "Holes" if len(hole_group) > 1 else "Hole"
                    prefix: str = f"{self.Name}_{name}{group_index:03d}"
                    binder_placement: Placement = Placement()  # Do not move/reorient anything.
                    if tracing:
                        print(f"{tracing}{binder_placement.Rotation.Axis=}")

                    suffix = "Drills" if len(hole_group) > 1 else "Drill"
                    solid_name: str = f"{prefix}_{suffix}"
                    shape_binder: Part.Feature = body.newObject(
                        "PartDesign::SubShapeBinder", f"{solid_name}_Binder")
                    assert isinstance(shape_binder, Part.Feature)
                    shape_binder.Placement = binder_placement
                    shape_binder.Support = (part_geometries)
                    # shape_binder.Support = (datum_plane, [""])
                    shape_binder.Visibility = False

                    # TODO: fill in actual values for Hole.
                    # Create the *hole* and upstate the view provider for GUI mode:
                    part_hole: Part.Feature = body.newObject("PartDesign::Hole", solid_name)
                    assert isinstance(part_hole, Part.Feature)
                    part_hole.Profile = shape_binder
                    part_hole.Diameter = diameter
                    part_hole.Depth = depth
                    part_hole.UpToFace = None
                    part_hole.Reversed = False
                    part_hole.Midplane = 0

                    # Fill in other fields for the top mount.
                    # if is_top:
                    #     assert False, "Fill in other fields."

                    # For the GUI, update the view provider:
                    # self._viewer_update(body, part_hole)

                    if App.GuiUp:  # pragma: no unit cover
                        visibility_set(part_hole, True)
                        view_object: Any = body.getLinkedObject(True).ViewObject
                        part_hole.ViewObject.LineColor = getattr(
                            view_object, "LineColor", part_hole.ViewObject.LineColor)
                        part_hole.ViewObject.ShapeColor = getattr(
                            view_object, "ShapeColor", part_hole.ViewObject.ShapeColor)
                        part_hole.ViewObject.PointColor = getattr(
                            view_object, "PointColor", part_hole.ViewObject.PointColor)
                        part_hole.ViewObject.Transparency = getattr(
                            view_object, "Transparency", part_hole.ViewObject.Transparency)
                        # The following code appears to disable edge highlighting:
                        # part_hole.ViewObject.DisplayMode = getattr(
                        #    view_object, "DisplayMode", part_hole.ViewObject.DisplayMode)

        if tracing:
            print(f"{tracing}<=FabMount({self.Name}).drill_joins(|{len(joins)}|")


# FabSolid:
@dataclass
class FabSolid(FabNode):
    """Fab: Represents a single part constructed using FreeCAD Part Design paradigm.

    Inherited Attributes:
    * *Name* (str): The model name.
    * *Parent* (FabNode): The Parent FabNode.

    Attributes:
    * *Material* (str): The material to use.
    * *Color* (str): The color to use.

    """

    Material: str
    Color: str
    _Mounts: Dict[str, FabMount] = field(init=False, repr=False)
    _GeometryGroup: Optional[App.DocumentObjectGroup] = field(init=False, repr=False)
    _Body: Optional[Part.BodyBase] = field(init=False, repr=False)

    # FabSolid.__post_init__():
    def __post_init__(self) -> None:
        """Verify FabSolid arguments."""
        super().__post_init__()
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabSolid({self.Name}).__post_init__()")
        # TODO: Do additional type checking here:
        self._Mounts = {}
        self._GeometryGroup = None
        self._Body = None

        if tracing:
            print(f"{tracing}<=FabSolid({self.Name}).__post_init__()")

    # FabSolid.Body():
    @property
    def Body(self) -> Part.BodyBase:
        """Return BodyBase for FabSolid."""
        if not self._Body:
            raise RuntimeError(f"FabSolid.Body({self.Name}).Body(): body not set yet")
        return self._Body

    # FabSolid.set_body():
    def set_body(self, body: Part.BodyBase) -> None:
        """Set the BodyBase of a FabSolid."""
        self._Body = body

    # FabSolid.is_solid():
    def is_solid(self) -> bool:
        """ Return True if FabNode is a FabAssembly."""
        return True  # All other FabNode's return False.

    # FabSolid.Construct():
    @property
    def Construct(self) -> bool:
        """Return the construct mode flag."""
        return self.Project.Construct

    # FabSolid.mount():
    def mount(self, name: str, contact: Vector, normal: Vector, orient: Vector,
              depth: float, tracing: str = "") -> FabMount:
        """Return a new FabMount."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabSolid({self.Name}).mount('{name}', ...)")

        fab_mount: FabMount = FabMount(name, self, contact, normal, orient, depth)
        self._Mounts[name] = fab_mount
        assert len(self._Mounts) > 0, "FabSolid.mount()"
        if self.Construct:
            context: Dict[str, Any] = self.Context
            fab_mount.produce(context, tracing=next_tracing)

        if tracing:
            print(f"{tracing}=>FabSolid({self.Name}).mount('{name}', ...)=>{fab_mount}")
        return fab_mount

    # FabSolid.drill_joins():
    def drill_joins(self, joins: Sequence[FabJoin],
                    mounts: Optional[Sequence[FabMount]] = None) -> None:
        """Apply drill FabJoin holes for a FabSolid.

        Iterate pairwise through a sequence of FabJoin's and FabMount's and for each pair
        attempt to drill a bunch the FabJoin holes for the associated FabSolid.  The drill
        operation only occurs if the FabJoin is in alignment with the FabMount normal (in
        either direction) *and* if the FabJoin intersects with the underlying FabSolid;
        otherwise nothing is for that particular FabMount and FabJoin pair.

        Arguments:
        * *joins* (Optional[Sequence[FabJoin]]):
          The tuple/list of FabJoin's to apply.
        * *mounts* (Optional[Sequence[FabMount]]):
          The mounts to to apply the *joins* to.  If *mounts* is *None*, all of the
          mounts for the current FabSolid are used.  (Default: None)

        For now, please call this method after all FabMount's are created.
        """
        tracing: str = self.Tracing
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabSolid({self.Name}).drill_joins(|{len(joins)}|, *)")

        if self.Construct:
            if not mounts:
                mounts = tuple(self._Mounts.values())
            assert isinstance(mounts, (tuple, list)), mounts
            mount: FabMount
            for mount in mounts:
                assert mount._Solid is self, (
                    f"FabMount({mount.Name}) of FabSolid({mount.Name} can not be "
                    f"used with FabSolid({self.Name})")
                mount.drill_joins("BoxJoins", joins, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=FabSolid({self.Name}).drill_joins(|{len(joins)}|, *)")

    # FabSolid.pre_produce():
    def pre_produce(self) -> Tuple[str, ...]:
        """Produce an Empty FabSolid prior to performing operations."""
        tracing: str = self.Tracing
        if tracing:
            print(f"{tracing}=>FabSolid.pre_produce('{self.Name}')")

        # Only do work in construct mode:
        if self.Construct:
            context: Dict[str, Any] = self.Context
            context_keys: Tuple[str, ...]
            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}Before Context: {context_keys=}")

            # Create the *geometry_group* that contains all of the 2D geometry (line, arc, circle.):
            parent_object: Any = context["parent_object"]
            geometry_group: App.DocumentObjectGroup
            geometry_group_name: str = f"{self.Name}_Geometry"
            if isinstance(parent_object, App.Document):
                geometry_group = parent_object.addObject(
                    "App::DocumentObjectGroup", geometry_group_name)
            else:
                geometry_group = parent_object.newObject("App::DocumentObjectGroup")
                geometry_group.Label = geometry_group_name
            self._GeometryGroup = geometry_group

            geometry_group.Visibility = False

            # Make *geometry_group* available to all FabMount's:
            # mount: FabMount
            # assert len(self._Mounts) > 0
            # for mount in self._Mounts.values():
            #     mount.set_geometry_group(geometry_group)

            # Create the *body*
            body: Part.BodyBase

            if isinstance(parent_object, App.Document):
                body = parent_object.addObject("PartDesign::Body", self.Name)
            else:
                body = parent_object.newObject("PartDesign::Body")
                body.Label = self.Name
            self.set_body(body)

            # Copy "view" fields from *body* to *gui_body* (if we are in graphical mode):
            if App.GuiUp:  # pragma: no cover
                document: FabNode = self.get_parent_document()
                gui_document: Any = document._GuiObject
                assert gui_document, "No GUI document"
                assert hasattr(gui_document, "getObject")
                gui_body: Any = getattr(gui_document, body.Name)
                assert gui_body, "No GUI body"
                assert hasattr(gui_body, "ShapeColor"), "Something is wrong"
                if hasattr(gui_body, "Proxy"):
                    # This magical line seems to get a view provider object into the Proxy field:
                    setattr(gui_body, "Proxy", 0)  # Must not be `None`
                if hasattr(gui_body, "DisplayMode"):
                    setattr(gui_body, "DisplayMode", "Shaded")
                if hasattr(gui_body, "ShapeColor"):
                    rgb = FabColor.svg_to_rgb(self.Color)
                    setattr(gui_body, "ShapeColor", rgb)

                # view_object: "ViewProviderDocumentObject"  = body.getLinkedObject(True).ViewObject
                # assert isinstance(view_object, ViewProviderDocumentObject), type(view_object)
                # model_file.ViewObject = view_object

            if tracing:
                context_keys = tuple(sorted(context.keys()))
                print(f"{tracing}After Context: {context_keys=}")

        if tracing:
            print(f"{tracing}<=FabSolid.pre_produce('{self.Name}')")
        return ()


# TODO: Move this to FabNode class and switch to using a *context*.
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


# FabDrill:
# @dataclass
# class XFabDrill(FabOperation):
#     """FabDrill: A FreeCAD PartDesign Pocket operation.

#     Attributes:
#     * *Name* (str): The operation name.
#     * *Joins* (FabCircle): The Circle to drill.
#     * *Depth* (float): Exlplicit depth to use. (Default: -1 to have system try to figure it out.)

#     """

#     Joins: Union[FabJoin, Tuple[FabJoin, ...]]
#     Depth: float = -1.0
#     _joins: Tuple[FabJoin, ...] = field(init=False, repr=False, default=())

#     # FabDrill.__post_init__():
#     def __post_init__(self) -> None:
#         """Verify _Extrude values."""
#         super().__post_init__()
#         joins: List[FabJoin] = []
#         join: Any
#         if isinstance(self.Joins, tuple):
#             index: int
#             for index, join in enumerate(self.Joins):
#                 if not isinstance(join, FabJoin):
#                     raise ValueError(f"Joins[{index}]: Has type {type(join)}, not FabJoin")
#                 joins.append(join)
#         elif isinstance(self.Joins, FabJoin):
#             joins.append(self.Joins)
#         else:
#             raise ValueError(f"Joins: Has type {type(join)}, not FabJoin or Tuple[FabJoin, ...]")
#         self._joins = tuple(joins)
#         if (join.Start - join.End).Length < 1.0e-8:
#             raise ValueError(f"FabJoin has same start {join.Start} and {join.Stop}.")

#     # FabDrill.get_name():
#     def get_name(self) -> str:
#         """Return FabDrill name."""
#         return self.Name

#     # FabDrill.get_kind():
#     def get_kind(self) -> str:
#         """Return the sub-class drill kind."""
#         raise NotImplementedError(f"{type(self)}.get_kind() not implmeneted")

#     # FabDrill.produce():
#     def produce(self, contexxt: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
#         """Produce the Hole."""

#         EPSILON: float = 1.0e-8

#         # close():
#         def close(vector1: Vector, vector2: Vector) -> bool:
#             """Return whether 2 normals are aligned."""
#             return (vector1 - vector2).Length < EPSILON

#         # normal_distance():
#         def normal_distance(normal: Vector, start: Vector, end: Vector) -> float:
#             """Return distance from start to end along normal."""
#             distance: float = (end - start).Length
#             if close(start - distance * normal, end):
#                 distance = -distance
#             elif not close(start + distance * normal, end):
#                 assert False, f"{start=} and  {end=} are not aligned {normal=}."
#             return distance

#         # Grab mount information from *contexxt*:
#         next_tracing = tracing + " " if tracing else ""
#         if tracing:
#             print(f"{tracing}=>FabDill.produce({self.Name})")

#         prefix = cast(str, contexxt["prefix"])
#         next_prefix: str = f"{prefix}_{self.Name}"
#         # mountx_name = cast(str, contexxt["mountx_name"])
#         mountx_contact = cast(Vector, contexxt["mountx_contact"])
#         mountx_normal = cast(Vector, contexxt["mountx_normal"])
#         bottomx_depth = cast(float, contxt["mountx_depth"])
#         # mountx_plane = contexxt["mountx_plane"]
#         # assert isinstance(mount_plane, Part.Geometry)
#         assert abs(mount_normal.Length - 1.0) < EPSILON, (
#             "{self.FullPath}: Mount normal is not of length 1")
#         if tracing:
#             print(f"{tracing}{mountx_contact=} {mountx_normal=} {bottom_depth=}")

#         # Make copy of *mount_normal* and normailize it:
#         copy: Vector = Vector()
#         mount_normal = (mount_normal + copy).normalize()
#         mount_z_aligned: bool = close(mount_normal, Vector(0.0, 0.0, 1.0))

#         # Some commonly used variables:
#         depth: float
#         hole: _Hole
#         is_top: bool
#         join: FabJoin
#         fasten: FabFasten
#         uinique: int

#         # For each *join*, generate a *hole* request.  Any errors are collected in *errors*:
#         holes: List[_Hole] = []
#         errors: List[str] = []
#         for join in self._joins:
#             # Unpack *join* and associated *fasten*:
#             start: Vector = join.Start
#             end: Vector = join.End
#             fasten = join.Fasten

#             # *start* and *end* specify a line segment in 3D space that corresponds to the
#             # fastener shaft length (excluding extra shaft at the end for nuts and washers.)  The
#             # *start*/*end* line segment can be extended to an infinitely long line in 3D space.
#             #The mount specifies a top and bottom mount plane that are supposed to totally enclose
#             # include the solid.  If the infinitely long line not perpendicular to the top/bottom
#             # mount planes, it is an error.  The locations where the infinitely long line
#             # intersects the top/bottom mount planes are *top* and *bottom* respectively.
#             # The *top* and *bottom* points specify a line segment that can potentially drilled
#             # out by this operation.  It is important to understand that the direction vector
#             # from *start* to *end* may be in the same or opposite direction as the from *top*
#             # to *bottom*.  If either *start* or *end* occur inside of the *top*/*bottom*
#             # line segment, the drill out section gets shortened appropriately.  Finally, if
#             # *start* matches either *top* or *bottom* (within epsilon), any requested
#             # countersink or counter bore operations are enabled for the drill hole; otherwise,
#             # it is just a simple drill operation.

#             # Find *top* and *bottom* points where infinite line pierces top/bottom mount planes:
#             # FreeCAD Vector metheds like to modify Vector contents; force copies beforehand:
#             top: Vector = (start + copy).projectToPlane(
#                            mountx_contact + copy, mountx_normal + copy)
#             # bottom_contact: Vector = mountx_contact - bottom_depth * mount_normal

#             # Ensure *start*/*end* line segment is perpendicular to mount planes.
#             start_end_normal: Vector = (end - start).normalize()
#             start_end_aligned: bool
#             if not (close(mount_normal, start_end_normal) or
#                     close(mount_normal, -start_end_normal)):
#                 errors.append(
#                     f"FabDrill({self.Name}): Fasten {join.Name} "
#                     "is not perpendicular to mount plane")
#                 continue

#             # Compute distances along line from *top* along the *down_normal* direction:
#             down_normal: Vector = -mount_normal
#             start_distance: float = normal_distance(down_normal, top, start)
#             end_distance: float = normal_distance(down_normal, top, end)
#             close_distance: float = min(start_distance, end_distance)
#             far_distance: float = max(start_distance, end_distance)
#             assert close_distance <= far_distance
#             if far_distance <= 0.0 or close_distance >= bottom_depth:
#                 errors.append(f"FabDrill({self.Name}): "
#                               f"Fasten {fasten.Name} does not overlap with solid")
#                 continue
#             if close_distance > 0.0:
#                 errors.append(f"FabDrill({self.Name}): "
#                               f"Fasten {fasten.Name} starts below mount plane")
#                 continue
#             depth = min(bottom_depth, far_distance)
#             is_top = close(start, top)
#             kind: str = self.get_kind()
#             # This is quite ugly for now.  If the *mount_normal* equals the +Z axis, multiple
#             # holes of the same characteristics can be done together.  Otherwise, it is
#             # one drill operation per hole.  Sigh:
#             unique: int = 0 if mount_z_aligned else id(join)
#             hole = _Hole(fasten.ThreadName, kind, depth, is_top, unique, top, join)
#             holes.append(hole)

#         # Group all *holes* with the same *key* together:
#         key: _HoleKey
#         hole_groups: Dict[_HoleKey, List[_Hole]] = {}
#         for hole in holes:
#             key = hole.Key
#             if key not in hole_groups:
#                 hole_groups[key] = []
#             hole_groups[key].append(hole)

#         # For each *hole_group* create a PartDesign Hole:
#         index: int
#         for index, key in enumerate(sorted(hole_groups.keys())):
#             # Unpack *key*:
#             thread_name: str
#             thread_name, kind, depth, is_top, unique = key
#             diameter: float = fasten.get_diameter(kind)

#             # Construct the "drawing"
#             part_geometries: List[Part.Part2DObject] = []
#             hole_group: List[_Hole] = hole_groups[key]
#             for hole in hole_group:
#                 # Construct the drawing"
#                 # Sanity check that each *fasten* object matches the *key*.
#                 join = hole.Join
#                 fasten = join.Fasten
#                 assert fasten.ThreadName == thread_name and self.get_kind() == kind and (
#                     hole.Depth == depth and hole.IsTop == is_top)
#                 center: Vector = hole.Center
#                 circle: FabCircle = FabCircle(center, mount_normal, diameter)
#                 part_geometries.extend(circle.produce(contexxt.copy(),
#                                                       next_prefix, tracing=next_tracing))

#             # Create the *shape_binder*:
#             next_prefix = f"{prefix}.DrillCircle{index:03d}"
#             shape_binder: Part.Feature = self.produce_shape_binder(
#                 contexxt.copy(), tuple(part_geometries), next_prefix, tracing=next_tracing)
#             assert isinstance(shape_binder, Part.Feature)
#             body = cast(Part.BodyBase, contexxt["solid_body"])

#             # TODO: fill in actual values for Hole.
#             # Create the *pocket* and upstate the view provider for GUI mode:
#             part_hole: Part.Feature = body.newObject("PartDesign::Hole", f"{next_prefix}_Hole")
#             assert isinstance(part_hole, Part.Feature)
#             part_hole.Profile = shape_binder
#             part_hole.Diameter = diameter
#             part_hole.Depth = depth
#             part_hole.UpToFace = None
#             part_hole.Reversed = False
#             part_hole.Midplane = 0

#             # Fill in other fields for the top mount.
#             # if is_top:
#             #     assert False, "Fill in other fields."

#             # For the GUI, update the view provider:
#             self._viewer_update(body, part_hole)

#         if tracing:
#             print(f"{tracing}<=FabDrill({self.Name}).produce()")
#         return tuple(errors)


# # FabThread:
# @dataclass
# class FabThread(FabDrill):
#     """Drill and thread FabJoin's."""

#     # FabThread.__post_init__()
#     def __post_init__(self) -> None:
#         """Initialize FabThread."""
#         super().__post_init__()

#     # FabThread.get_kind():
#     def get_kind(self) -> str:
#         """Return a thread diameter kind."""
#         return "thread"


# # FabClose:
# @dataclass
# class FabClose(FabDrill):
#     """Drill a close a FabJoin's."""

#     # FabClose.__post_init__()
#     def __post_init__(self) -> None:
#         """Initialize FabCLose."""
#         super().__post_init__()

#     # FabClose.get_kind():
#     def get_kind(self) -> str:
#         """Return a thread diameter kind."""
#          return "close"


# # FabLoose:
# @dataclass
# class FabLoose(FabDrill):
#     """Drill Loose FabJoin's."""

#     def get_kind(self) -> str:
#         """Return a thread diameter kind."""
#         return "loose"


# # FabHole:
# @dataclass
# class XFabHole(FabOperation):
#     """FabHole: A FreeCAD PartDesign Pocket operation.

#     Attributes:
#     * *Name* (str): The operation name.
#     * *Circle* (FabCircle): The Circle to drill.
#     * *Depth* (float): The depth

#     """

#     Circle: FabCircle
#     Depth: float

#     # FabHole.__post_init__():
#     def __post_init__(self) -> None:
#         """Verify _Extrudex values."""
#         super().__post_init__()
#         if not isinstance(self.Circle, FabCircle):
#             raise ValueError(f"{self.Geometry} is not a FabCircle")
#         if self.Depth <= 0.0:
#             raise ValueError(f"Depth ({self.Depth}) is not positive.")

#     # FabHole.get_name():
#     def get_name(self) -> str:
#         """Return FabHole name."""
#         return self.Name

#     # FabHole.produce():
#     def produce(self, contexxt: Dict[str, Any], tracing: str = "") -> Tuple[str, ...]:
#         """Produce the Hole."""
#         # Extract the *part_geometries*:
#         if tracing:
#             print("{tracing}=>FabHole({self.Name}).produce()")

#         prefix = cast(str, contexxt["prefix"])
#         next_prefix: str = f"{prefix}_{self.Name}"
#         part_geometries: Tuple[Part.Part2DObject, ...] = (
#             self.Circle.produce(contexxt.copy(), next_prefix))

#         # Create the *shape_binder*:
#         shape_binder: Part.Feature = self.produce_shape_binder(
#             contexxt.copy(), part_geometries, next_prefix)
#         assert isinstance(shape_binder, Part.Feature)
#         body = cast(Part.BodyBase, contexxt["solid_body"])

#         # Create the *pocket* and upstate the view provider for GUI mode:
#         hole: Part.Feature = body.newObject("PartDesign::Hole", f"{next_prefix}_Hole")
#         assert isinstance(hole, Part.Feature)
#         hole.Profile = shape_binder
#         hole.Diameter = self.Circle.Diameter
#         hole.Depth = self.Depth
#         hole.UpToFace = None
#         hole.Reversed = 0
#         hole.Midplane = 0

#         # For the GUI, update the view provider:
#         self._viewer_update(body, hole)

#         if tracing:
#             print("{tracing}<=FabHole({self.Name}).produce()")
#         return ()


def main() -> None:
    pass


if __name__ == "__main__":
    main()
