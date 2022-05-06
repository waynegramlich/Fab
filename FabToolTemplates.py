#!/usr/bin/env python3
"""FabToolTemplates: Templates for defining tool bits.

This package provides some classes that are used to build tables of tools needed for a shop
definition.  These are lower level classes that really are expected to be used by end-users.
The classes are:
* FabShape:
  This represents a single Tool Bit shape template that is represented as a standard FreeCAD
  `.fcstd` document.  These files live in the `.../Tools/Shape/` directory.
* FabShapes:
  This represents all of the FabShape's in a `.../Tools/Shape/` directory.
* FabAttributes:
  This a just a sorted list of attribute value pairs. These values get stored into `.fctb` files
  in the `.../Tools/Bit/` directory.  In general, these values do not specify the physical shape
  parameters needed by the FabShape `.fcstd` files.
* FabBitTemplate:
  This a class that specifies a all of the fields needed to for a FabBit.  The `.fctb` files
  live in the `.../Tools/Bit/` directory and a template is used to read/write the `.fctb` files.
* FabBitTemplates:
  This class simply lists one FaBBitTemplate for each different FabShape.
* FabTemplatesFactory:
  This is a trivial class that instatiates one FabTemplates object that can be resused since
  it does not change.

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

# Issues:
# * Turn off Legacy tools Path => Preferences => [] Enable Legacy Tools
# * Edit move the from line 11 to line 10 in .../Tools/Bit/45degree_chamfer.fctb to fix JSON error.
# * When setting path to library, be sure to include .../Tools/Library  (one level up does not work)

from typeguard import check_type, check_argument_types
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from pathlib import Path as PathFile


# FabShape:
@dataclass(frozen=True)
class FabShape(object):
    """FabShape: Corresponds to FreeCAD Path library Shape 'template'.

    Attributes:
    * *Name* (str): The shape name.
    * *ShapePath* (PathFile): The path to the associated `fcstd` file.
    """

    Name: str
    ShapePath: PathFile

    # FabShape.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing the FabShape."""
        check_type("FabShape.Name", self.Name, str)
        check_type("FabShape.ShapePath", self.ShapePath, PathFile)

    # FabShape.read():
    @staticmethod
    def read(shape_path: PathFile, tracing: str = "") -> "FabShape":
        """Read in a FabShape."""
        if tracing:
            print(f"{tracing}=>FabShape.read({shape_path})")
        assert shape_path.exists(), f"FabShape.__post_init__(): f{str(shape_path)} does not exist"
        assert str(shape_path).endswith(".fcstd"), f"{shape_path=}"
        shape: FabShape = FabShape(shape_path.stem, shape_path)
        if tracing:
            print(f"{tracing}<=FabShape.read({shape_path})=>{shape}")
        return shape

    # FabShape._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform unit tests."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabShape._unit_tests()")
        this_directory: PathFile = PathFile(__file__).parent
        shapes_directory: PathFile = this_directory / "Tools" / "Shape"
        shape_path: PathFile = shapes_directory / "endmill.fcstd"
        shape: FabShape = FabShape.read(shape_path, tracing=next_tracing)
        assert shape.Name == "endmill", f"{shape.Name=}"
        assert shape.ShapePath is shape_path
        if tracing:
            print(f"{tracing}<=FabShape._unit_tests()")


# FabShapes:
@dataclass(frozen=True)
class FabShapes(object):
    """FabShapes: A directory of FabShape's.

    Attributes:
    * *Directory* (PathFile): The directory containing the FabShapes (.fcstd) files.
    * *Shapes* (Tuple[FabShape, ...]: The corresponding FabShape's.
    * *Names* (Tuple[str, ...]: The sorted names of the FabShape's.

    Constructor:
    * FabShapes(Directory, Shapes)
    """

    Directory: PathFile
    Shapes: Tuple[FabShape, ...]
    Names: Tuple[str, ...]

    # FabShapes.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabShapes."""
        check_type("FabShapes.Directory", self.Directory, PathFile)
        check_type("FabShapes.Shapes", self.Shapes, Tuple[FabShape, ...])
        check_type("FabShapes.Names", self.Names, Tuple[str, ...])

    # FabShapes.read():
    @staticmethod
    def read(shapes_directory: PathFile, tracing: str = "") -> "FabShapes":
        """Read in FabShapes from a directory."""
        if tracing:
            print(f"{tracing}=>FabShapes.read({shapes_directory})")
        assert shapes_directory.is_dir(), (
            f"FabShapes.read(): {str(shapes_directory)} is not a directory")
        shapes_table: Dict[str, FabShape] = {}
        shape_file: PathFile
        shape_names: List[str] = []
        for shape_file in shapes_directory.glob("*.fcstd"):
            shape: FabShape = FabShape.read(shape_file)
            shape_names.append(shape.Name)
            shapes_table[shape.Name] = shape

        sorted_shape_names: Tuple[str, ...] = tuple(sorted(shapes_table.keys()))
        shape_name: str
        shapes: Tuple[FabShape, ...] = tuple([
            shapes_table[shape_name] for shape_name in sorted_shape_names])
        fab_shapes: FabShapes = FabShapes(shapes_directory, shapes, sorted_shape_names)
        if tracing:
            print(f"{tracing}<=FabShapes.read({shapes_directory})=>*")
        return fab_shapes

    # FabShapes.example():
    @staticmethod
    def example() -> "FabShapes":
        """Return an example FabShapes."""
        shapes_directory: PathFile = PathFile(__file__).parent / "Tools" / "Shape"
        shapes: FabShapes = FabShapes.read(shapes_directory)
        return shapes

    # FabShapes.lookup():
    def lookup(self, name) -> FabShape:
        """Lookup a FabShape by name."""
        shape: FabShape
        for shape in self.Shapes:
            if shape.Name == name:
                return shape
        raise KeyError(f"FabShapes.lookup(): {name} is not one of {self.Names}")

    # FabShapes._unit_tests()
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        if tracing:
            print(f"{tracing}=>FabShapes._unit_tests()")
        shapes_directory: PathFile = PathFile(__file__).parent / "Tools" / "Shape"
        shapes: FabShapes = FabShapes.read(shapes_directory)
        example_shapes: FabShapes = FabShapes.example()
        assert shapes == example_shapes
        shape: FabShape
        index: int
        for index, shape in enumerate(shapes.Shapes):
            assert shapes.lookup(shape.Name) is shape
            print(f"{tracing}Shape[{index}]: {shape.Name}: {str(shape.ShapePath)}")
        try:
            shapes.lookup("Bogus")
            assert False
        except KeyError as key_error:
            assert str(key_error).startswith("\"FabShapes.lookup(): Bogus is not one of "), (
                f"{str(key_error)=}")
        if tracing:
            print(f"{tracing}<=FabShapes._unit_tests()")


# FabAttributes:
@dataclass(frozen=True)
class FabAttributes(object):
    """FabAttributes: Additional information about a FabBit.

    Attributes:
    * *Values* (Tuple[Tuple[str, Any], ...): Sorted list of named attribute values.
    * *Names* (Tuple[str, ...]): Sorted list of attribute names:
    """

    Values: Tuple[Tuple[str, Any], ...]
    Names: Tuple[str, ...]

    # FabAttributes.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabAttributes."""
        check_type("FabAttributes.Values", self.Values, Tuple[Tuple[str, Any], ...])
        check_type("FabAttributes.Names", self.Names, Tuple[str, ...])

    # FabAttributes.fromJSON():
    @staticmethod
    def fromJSON(json_dict: Dict[str, Any], tracing: str = "") -> "FabAttributes":
        """Return FabAttributes extracted from a JSON dictionary."""
        if tracing:
            print(f"{tracing}=>FabAttributes.fromJSON({json_dict})")
        assert check_argument_types()
        names: Tuple[str, ...] = tuple(sorted(json_dict.keys()))
        name: str
        value: Any
        values: Tuple[Tuple[str, Any], ...] = tuple([
            (name, json_dict[name]) for name in sorted(names)
        ])
        attributes: FabAttributes = FabAttributes(values, names)
        assert attributes.Values == values
        assert attributes.Names == names
        if tracing:
            print(f"{tracing}<=FabAttributes.fromJSON({json_dict})=>{attributes}")
        return attributes

    # FabAttributes.toJSON():
    def toJSON(self) -> Dict[str, Any]:
        """Return FabAttributes as JSON dictionary."""
        name: str
        value: Any
        return {name: value for name, value in self.Values}

    # FabAttributes.example():
    @staticmethod
    def example() -> "FabAttributes":
        """Return a example FabAttributes."""
        # Both Names and Values must be in sorted order:
        attributes: FabAttributes = FabAttributes(
            Values=(("Flutes", 2), ("Material", "Carbide")),
            Names=("Flutes", "Material")
        )
        return attributes

    # FabAttributes._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabAttributes unit tests."""
        if tracing:
            print(f"{tracing}=>FabAttributes._unit_tests()")
        attributes: FabAttributes = FabAttributes.example()
        json_dict: Dict[str, Any] = attributes.toJSON()
        assert json_dict == {"Material": "Carbide", "Flutes": 2}
        extracted_attributes: FabAttributes = FabAttributes.fromJSON(json_dict)
        assert extracted_attributes == attributes, (extracted_attributes, attributes)
        if tracing:
            print(f"{tracing}<=FabAttributes._unit_tests()")


# FabBit:
@dataclass(frozen=True)
class FabBit(object):
    """FabBit: Base class common to all FabBit sub-classes;

    Attributes:
    * *Name* (str): The name of the tool template.
    * *BitFile* (PathFile): The file path to the corresponding `.fctb` file.
    * *Shape*: (FabShape): The associated FabShape.
    * *Attributes*: (FabAttributes): The optional bit attributes.

    Constructor:
    * FabBit("Name", BitFile, Shape, Attributes)

    """

    Name: str
    BitFile: PathFile
    Shape: FabShape
    Attributes: FabAttributes

    # FabBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabCNCTemplate."""
        # assert self.Name != "BallEnd"
        check_type("FabBit.Name", self.Name, str)
        check_type("FabBit.BitFile", self.BitFile, PathFile)
        check_type("FabBit.Shape", self.Shape, FabShape)
        check_type("FabBit.Attributes", self.Attributes, FabAttributes)

    # FabBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabBit._unit_tests()")
        tools_directory: PathFile = PathFile(__file__).parent / "Tools"
        bit_file: PathFile = tools_directory / "Bit" / "probe.fctb"
        shape: FabShape = FabShape("probe", tools_directory / "Shape" / "probe.fcstd")
        attributes: FabAttributes = FabAttributes.fromJSON({})
        bit: FabBit = FabBit("TestBit", bit_file, shape, attributes)
        assert bit.Name == "TestBit"
        assert bit.BitFile == bit_file
        assert bit.Shape is shape
        assert bit.Attributes is attributes
        if tracing:
            print(f"{tracing}<=FabBit._unit_tests()")

    # FabBit.toJSON():
    def toJSON(self) -> Dict[str, Any]:
        """Return the JSON associated with a FabBit."""
        # Python does not really like circular class declarations.  This breaks the cycle.
        return _bit_to_json(self)


# FabBitTemplate:
@dataclass(frozen=True)
class FabBitTemplate(object):
    """FabBitTemplate: A Template for creating a FabBit.

    Attributes:
    * *Name* (str): The FabBit name.
    * *ExampleName* (str): The name used for a generated example FabBit.  (see getExample).
    * *ShapeName* (str): The shape name in the `.../Tools/Shape/` directory without `.fcstd` suffix.
    * *Parameters* (Tuple[Tuple[str, Tuple[type, ...]], ...]):
      The allowed parameter names and associated types of the form:
      ("ParameterName", (type1, ..., typeN), "example") for no type checking ("ParameterName",)
    * *Attributes* (Tuple[Tuple[str, Tuple[type, ...]], ...]):
      The allowed parameter names and associated types of the form:
      ("ParameterName", (type1, ..., typeN), "example") for no type checking ("ParameterName",)
    """

    Name: str
    ExampleName: str
    ShapeName: str
    Parameters: Tuple[Tuple[str, Tuple[type, ...], Union[bool, float, int, str]], ...]
    Attributes: Tuple[Tuple[str, Tuple[type, ...], Union[bool, float, int, str]], ...]

    # FabBitTemplate.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabBitTemplate."""
        check_type("FabBitTemplate.Name", self.Name, str)
        check_type("FabBitTemplate.ExampleName", self.ExampleName, str)
        check_type("FabBitTemplate.ShapeName", self.ShapeName, str)
        check_type("FabBitTemplate.Parameters", self.Parameters,
                   Tuple[Tuple[str, Tuple[type, ...], Union[bool, float, int, str]], ...])
        check_type("FabBitTemplate.Attributes", self.Attributes,
                   Tuple[Tuple[str, Tuple[type, ...], Union[bool, float, int, str]], ...])

    # FabBitTemplate.kwargsFromJSON():
    def kwargsFromJSON(self,
                       json_dict: Dict[str, Any], bit_file: PathFile,
                       shapes: FabShapes, tracing: str = "") -> Dict[str, Any]:
        """Return the keyword arguments needed to initialize a FabBit."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabBitTemplate.kwargsFromJSON(...)")
        assert check_argument_types(), "FabBitTemplate.kwargsFromJSON()"
        assert "name" in json_dict, "FabBitTemplate.kwargsFromJSON(): No version specified"
        assert "version" in json_dict, "FabBitTemplate.kwargsFromJSON(): No version specified"
        assert "shape" in json_dict, "FabBitTemplate.kwargsFromJSON(): No shape specified"
        assert "parameter" in json_dict, "FabBitTemplate.kwargsFromJSON(): No parameters specified"

        version: Any = json_dict["version"]
        name: Any = json_dict["name"]
        shape_fcstd: Any = json_dict["shape"]
        parameters: Any = json_dict["parameter"]
        bits_directory: PathFile = bit_file.parent
        tools_directory: PathFile = bits_directory.parent
        shapes_directory: PathFile = tools_directory / "Shape"

        assert isinstance(name, str) and name, f"FabBit.kwargsFromJSON(): Bad {name=}"
        assert isinstance(version, int) and version == 2, f"FabBit.kwargsFromJSON(): Bad {version=}"
        assert isinstance(shape_fcstd, str) and shape_fcstd.endswith(".fcstd"), (
            f"FabBit.kwargsFromJSON(): Bad {shape_fcstd=}")
        assert shape_fcstd == f"{self.ShapeName}.fcstd", (shape_fcstd, self.ShapeName)

        # Check *json_dict* for valid *parameters* and *attributes*:
        def fill(kwargs: Optional[Dict[str, Any]], label: str, json_dict: Dict[str, Any],
                 name_types: Tuple[Tuple[str, Tuple[type, ...],
                                         Union[int, float, str]], ...]) -> None:
            """Check whether ..."""
            name: str
            types: Tuple[type, ...]
            example: Union[int, float, str]
            named_types_dict: Dict[str, Tuple[type, ...]] = {
                name: types for name, types, example in name_types}

            value: Any
            for name, value in json_dict.items():
                if name not in named_types_dict:
                    assert False
                types = named_types_dict[name]
                assert type(value) in types, (
                    f"FabBitTemplate.kwargsFromJSON.check(): {type(value)} not one of {types}")
                if kwargs is not None:
                    kwargs[name] = value

        # Now create the *kwargs* and fill it in:
        bit_stem: str = self.Name.lower()
        if bit_stem == "v":
            bit_stem = "v_bit"
        if tracing:
            print("{tracign}{bit_stem=}")
        shape_path_file: PathFile = shapes_directory / "{self.ShapeName}.fctb"
        shape: FabShape = FabShape(self.ShapeName, shape_path_file)
        kwargs: Dict[str, Any] = {}
        kwargs["Name"] = bit_file.stem
        kwargs["BitFile"] = bits_directory / f"{self.ShapeName}.fctb"
        kwargs["Shape"] = shape
        fill(kwargs, "Parameters", parameters, self.Parameters)
        assert "attribute" in json_dict, "FabAttributes.fromJSON(): attribute key not present"
        kwargs["Attributes"] = FabAttributes.fromJSON(json_dict["attribute"], tracing=next_tracing)
        # fill(None, "attribute", attributes, self.Attributes)
        if tracing:
            print(f"{tracing}<=FabBitTemplate.kwargsFromJSON(...)=>{kwargs}")
        return kwargs

    # FabBitTemplate.toJSON():
    def toJSON(self, bit: "FabBit", with_attributes: bool) -> Dict[str, Any]:
        """Convert a FabBit to a JSON dictionary using a FabBitTemplate."""
        parameters: Dict[str, Any] = {name: getattr(bit, name) for name, _, _ in self.Parameters}
        attributes: Dict[str, Any] = bit.Attributes.toJSON() if with_attributes else {}

        json_dict: Dict[str, Any] = {
            "version": 2,
            "name": self.Name,
            "shape": self.ShapeName,
            "parameter": parameters,
            "attribute": attributes,
        }
        return json_dict

    # FabBitTemplate.example():
    @staticmethod
    def example() -> "FabBitTemplate":
        """Return an example FabBitTemplate."""
        end_mill_template: FabBitTemplate = FabBitTemplate(
            Name="EndMill",
            ExampleName="5mm_Endmill",
            ShapeName="endmill",
            Parameters=(
                ("CuttingEdgeHeight", (float, str), "30.000 mm"),
                ("Diameter", (float, str), "5.000 mm"),
                ("Length", (float, str), "50.000 mm"),
                ("ShankDiameter", (float, str), "3.000 mm"),
            ),
            Attributes=(
                ("Flutes", (int,), 0),
                ("Material", (str,), "HSS"),
            )
        )
        return end_mill_template

    # FabBitTemplate._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabBitTemplate unit tests."""
        if tracing:
            print(f"{tracing}=>FabBitTemplate._unit_tests()")
        template: FabBitTemplate = FabBitTemplate.example()
        assert template.Name == "EndMill"
        assert template.ShapeName == "endmill"
        assert template.Parameters == (
            ("CuttingEdgeHeight", (float, str), "30.000 mm"),
            ("Diameter", (float, str), "5.000 mm"),
            ("Length", (float, str), "50.000 mm"),
            ("ShankDiameter", (float, str), "3.000 mm"),
        )
        assert template.Attributes == (
            ("Flutes", (int,), 0),
            ("Material", (str,), "HSS"),
        ), template.Attributes
        if tracing:
            print(f"{tracing}<=FabBitTemplate._unit_tests()")


# FabBitTemplates:
@dataclass(frozen=True)
class FabBitTemplates(object):
    """FabBitTemplates: A container of FabBitTemplate's to/from JSON.

    Attributes:
    * *BallEnd* (FabBitTemplate): A template for creating FabBallEndBit's.
    * *BullNose* (FabBitTemplate): A template for creating FabBullNoseBit's.
    * *Chamfer* (FabBitTemplate): A template for creating FabChamferBit's.
    * *DoveTail* (FabBitTemplate): A template for creating FabDoveTailBit's.
    * *Drill* (FabBitTemplate): A template for creating FabDrillBit's.
    * *EndMill* (FabBitTemplate): A template for creating FabEndMillBit's.
    * *Probe* (FabBitTemplate): A template for creating FabProbeBit's.
    * *SlittingSaw* (FabBitTemplate): A template for creating FabSlittingSawBit's.
    * *ThreadMill* (FabBitTemplate): A template for create FabThreadMillBit's.
    * *V* (FabBitTemplate): A template for creating FabVBit's.
    Constructor:
    * FabBitTemplates(BallEnd, BullNose, Chamfer, DoveTail, Drill,
      EndMill, Probe, SlittingSaw, ThreadMill, VBit)

    Use FabBitTemplates.factory() instead of the constructor.
    """

    BallEnd: FabBitTemplate
    BullNose: FabBitTemplate
    Chamfer: FabBitTemplate
    DoveTail: FabBitTemplate
    Drill: FabBitTemplate
    EndMill: FabBitTemplate
    Probe: FabBitTemplate
    SlittingSaw: FabBitTemplate
    ThreadMill: FabBitTemplate
    V: FabBitTemplate

    # FabBitTemplates__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabBitTemplates."""
        check_type("FabBitTemplates.BallEnd", self.BallEnd, FabBitTemplate)
        check_type("FabBitTemplates.BullNose", self.BullNose, FabBitTemplate)
        check_type("FabBitTemplates.Chamfer", self.Chamfer, FabBitTemplate)
        check_type("FabBitTemplates.DoveTail", self.DoveTail, FabBitTemplate)
        check_type("FabBitTemplates.Drill", self.Drill, FabBitTemplate)
        check_type("FabBitTemplates.EndMill", self.EndMill, FabBitTemplate)
        check_type("FabBitTemplates.Probe", self.Probe, FabBitTemplate)
        check_type("FabBitTemplates.SlitingSaw", self.SlittingSaw, FabBitTemplate)
        check_type("FabBitTemplates.ThreadMill", self.ThreadMill, FabBitTemplate)
        check_type("FabBitTemplates.V", self.V, FabBitTemplate)

    # FabBitTemplates.factory():
    @staticmethod
    def factory() -> "FabBitTemplates":
        """Create the FabBitTemplates object.

        Arguments:
        * *shapes* (FabShapes): The available FabShape's.

        Returns:
        * (FabBitTemplates): The initialized FabBitTemplates object.

        """
        # Create each template first:
        ball_end_template: FabBitTemplate = FabBitTemplate(
            Name="BallEnd",
            ExampleName="6mm_Ball_End",
            ShapeName="ballend",
            Parameters=(
                ("CuttingEdgeHeight", (float, str), "40.0000 mm"),
                ("Diameter", (float, str), "5.000 mm"),
                ("Length", (float, str), "50.000 mm"),
                ("ShankDiameter", (float, str), "3.000 mm"),
            ),
            Attributes=(
                ("Flutes", (int,), 2),
                ("Material", (str,), "HSS"),
            )
        )
        bull_nose_template: FabBitTemplate = FabBitTemplate(
            Name="BullNose",
            ExampleName="6mm_Bull_Nose",
            ShapeName="bullnose",
            Parameters=(
                ("CuttingEdgeHeight", (float, str), "40.000 mm"),
                ("Diameter", (float, str), "5.000 mm"),
                ("FlatRadius", (float, str), "1.500 mm"),
                ("Length", (float, str), "50.000 mm"),
                ("ShankDiameter", (float, str), "3.000 mm"),
            ),
            Attributes=(
                ("Material", (str,), "HSS"),
                ("Flutes", (int,), 2),
            )
        )
        chamfer_template: FabBitTemplate = FabBitTemplate(
            Name="Chamfer",
            ExampleName="45degree_chamfer",
            ShapeName="chamfer",
            Parameters=(
                ("CuttingEdgeAngle", (float, str), "60.000 °"),
                ("CuttingEdgeHeight", (float, str), "6.350 mm"),
                ("Diameter", (float, str), "12.000 mm"),
                ("Length", (float, str), "30.000 mm"),
                ("ShankDiameter", (float, str), "6.350 mm"),
                ("TipDiameter", (float, str), "5.000 mm"),
            ),
            Attributes=(
                ("Material", (str,), "HSS"),
                ("Flutes", (int,), 2),
            )
        )
        dove_tail_template: FabBitTemplate = FabBitTemplate(
            Name="DoveTail",
            ExampleName="no_dovetail_yet",
            ShapeName="dovetail",
            Parameters=(
                ("CuttingEdgeAngle", (float, str), "60.000 °"),
                ("CuttingEdgeHeight", (float, str), "9.000 mm"),
                ("Diameter", (float, str), "19.050 mm"),
                ("Length", (float, str), "54.200 mm"),
                ("NeckDiameter", (float, str), "8.000 mm"),
                ("NeckHeight", (float, str), "5.000 mm"),
                ("ShankDiameter", (float, str), "9.525 mm"),
                ("TipDiameter", (float, str), "5.000 mm"),
            ),
            Attributes=(
                ("Material", (str,), "HSS"),
                ("Flutes", (int,), 2),
            )
        )
        drill_template: FabBitTemplate = FabBitTemplate(
            Name="Drill",
            ExampleName="5mm_Drill",
            ShapeName="drill",
            Parameters=(
                ("Diameter", (float, str), "3.000 mm"),
                ("Length", (float, str), "50.000 mm"),
                ("TipAngle", (float, str), "119.000 °"),
            ),
            Attributes=(
                ("Material", (str,), "HSS"),
                ("Flutes", (int,), 2),
            )
        )
        end_mill_template: FabBitTemplate = FabBitTemplate(
            Name="EndMill",
            ExampleName="5mm_Endmill",
            ShapeName="endmill",
            Parameters=(
                ("CuttingEdgeHeight", (float, str), "30.000 mm"),
                ("Diameter", (float, str), "5.000 mm"),
                ("Length", (float, str), "50.000 mm"),
                ("ShankDiameter", (float, str), "3.000 mm"),
            ),
            Attributes=(
                ("Material", (str,), "HSS"),
                ("Flutes", (int,), 2),
            )
        )
        probe_template: FabBitTemplate = FabBitTemplate(
            Name="Probe",
            ExampleName="probe",
            ShapeName="probe",
            Parameters=(
                ("Diameter", (float, str), "6.000 mm"),
                ("Length", (float, str), "50.000 mm"),
                ("ShaftDiameter", (float, str), "4.000 mm"),
            ),
            Attributes=(
                ("Spindle Power", (bool,), False),
            )
        )
        slitting_saw_template: FabBitTemplate = FabBitTemplate(
            Name="SlittingSaw",
            ExampleName="slittingsaw",
            ShapeName="slittingsaw",
            Parameters=(
                ("BladeThickness", (float, str), "3.000 mm"),
                ("CapDiameter", (float, str), "8.000 mm"),
                ("CapHeight", (float, str), "3.000 mm"),
                ("Diameter", (float, str), "76.200 mm"),
                ("Length", (float, str), "50.000 mm"),
                ("ShankDiameter", (float, str), "19.050 mm"),
            ),
            Attributes=(
                ("Material", (str,), "HSS"),
                ("Flutes", (int,), 30),
            )
        )
        thread_mill_template: FabBitTemplate = FabBitTemplate(
            Name="ThreadMill",
            ExampleName="5mm-thread-cutter",
            ShapeName="thread-mill",
            Parameters=(
                ("Crest", (float, str), "0.100 mm"),
                ("CuttingAngle", (float, str), "60.000 °"),
                ("Diameter", (float, str), "5.000 mm"),
                ("Length", (float, str), "50.000 mm"),
                ("NeckDiameter", (float, str), "3.000 mm"),
                ("NeckLength", (float, str), "20.000 mm"),
                ("ShankDiameter", (float, str), "5.000 mm"),
            ),
            Attributes=(
                ("Material", (str,), "HSS"),
                ("Flutes", (int,), 10),
            )
        )
        v_template: FabBitTemplate = FabBitTemplate(
            Name="V",
            ExampleName="60degree_VBit",
            ShapeName="v-bit",
            Parameters=(
                ("CuttingEdgeAngle", (float, str), "90.000 °"),
                ("CuttingEdgeHeight", (float, str), "1.000 mm"),
                ("Diameter", (float, str), "10.000 mm"),
                ("Length", (float, str), "20.000 mm"),
                ("ShankDiameter", (float, str), "5.000 mm"),
                ("TipDiameter", (float, str), "1.000 mm"),
            ),
            Attributes=(
                ("Material", (str,), "HSS"),
                ("Flutes", (int,), 4),
            )
        )

        bit_templates: FabBitTemplates = FabBitTemplates(
            BallEnd=ball_end_template,
            BullNose=bull_nose_template,
            Chamfer=chamfer_template,
            DoveTail=dove_tail_template,
            Drill=drill_template,
            EndMill=end_mill_template,
            Probe=probe_template,
            SlittingSaw=slitting_saw_template,
            ThreadMill=thread_mill_template,
            V=v_template
        )
        return bit_templates

    # FabBitTemplates.getExample():
    @staticmethod
    def getExample(bit_type: type) -> "FabBit":
        """Return an example FabBit from a FabTemplate.

        Arguments:
        * *bit_type* (type): The sub-class of FabBit to instantiate.

        Returns:
        * (FabBit) The example FabBit of type *bit_type*.
        """
        assert check_argument_types()
        # Get all of the *bit_templates*:
        tools_directory: PathFile = PathFile(__file__).parent / "Tools"
        bit_templates: FabBitTemplates = FabBitTemplatesFactory.getTemplates()

        # Lookup *bit_template* using *bit_type* to extract the correct attribute name:
        bit_type_text: str = str(bit_type)  # Should result in "<class '...FabXXXBit'>"
        start_index: int = bit_type_text.find("Fab")
        assert start_index >= 0
        bit_type_name: str = bit_type_text[start_index + 3:-5]  # Extract XXX, the type name.
        assert hasattr(bit_templates, bit_type_name), (
            f"FabBitTemplate.getExample(): {bit_type_name=}")
        bit_template: FabBitTemplate = getattr(bit_templates, bit_type_name)
        bit_path: PathFile = tools_directory / "Bit" / f"{bit_type_name.lower()}.fctb"

        def to_shape(tools_directory: PathFile, name: str) -> FabShape:
            """Create a FabShape."""
            return FabShape(name, tools_directory / "Shape" / f"{name}.fcstd")

        # Initialize *kwargs* with required values:
        attribute_name: str
        example_name: str = bit_template.ExampleName
        example_value: Union[bool, float, int, str]
        kwargs: Dict[str, Any] = {
            "Name": example_name,  # bit_type_name,
            "BitFile": bit_path,
            "Shape": to_shape(tools_directory, bit_type_name),
            "Attributes": FabAttributes.fromJSON({
                attribute_name: example_value
                for attribute_name, _, example_value in bit_template.Attributes
            }),
        }

        # Put the remaining "positional" arguments into *kwargs*:
        parameter_name: str
        for parameter_name, _, example_value in bit_template.Parameters:
            kwargs[parameter_name] = example_value

        example_bit: FabBit = bit_type(**kwargs)
        return example_bit

    # FabBitTemplates._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabBitTemplates unit tests."""
        if tracing:
            print(f"{tracing}=>FabBitTemplates._unit_tests()")
        bit_templates: FabBitTemplates = FabBitTemplatesFactory.getTemplates()
        assert isinstance(bit_templates, FabBitTemplates)
        if tracing:
            print(f"{tracing}<=FabBitTemplates._unit_tests()")


# FabBitTemplatesFactory:
class FabBitTemplatesFactory(object):
    """FabBitTempaltesFactory: A class for getting a shared FabBitsTemplate object."""

    fab_bit_templates = None

    # FabBitTemplatesFactory.getTemplates():
    @staticmethod
    def getTemplates() -> FabBitTemplates:
        """Return the FabTablates object."""
        if FabBitTemplatesFactory.fab_bit_templates is None:
            FabBitTemplatesFactory.fab_bit_templates = FabBitTemplates.factory()
        return FabBitTemplatesFactory.fab_bit_templates

    # FabBitTemplatesFactory._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run FabBitTemplatesFactory unit tests."""
        if tracing:
            print(f"{tracing}=>FabBitTemplatesFactory._unit_tests()")
            templates: FabBitTemplates = FabBitTemplatesFactory.getTemplates()
            assert isinstance(templates, FabBitTemplates)
        if tracing:
            print(f"{tracing}<=FabBitTemplatesFactory._unit_tests()")


# _bit_to_json():
def _bit_to_json(bit: FabBit) -> Dict[str, Any]:
    """Convert a FabBit to a JSON dict."""
    # Get the *bit_template* from the FabBit (i.e. *self*).

    # This code really wants to be in FabBit.toJSON(), but since the FabBit class is defined
    # before the FabBitTemplate/FabBitTemplates class, this functionality is implemented here
    # as a private function defined after FabBitTemplates.

    # All FabBit sub-classes have names of the form FabSomeNameBit.  We need to extract the
    # "SomeName" from FabSomeNameBit to get the FabBitTemplate.  Hence, the somewhat obscure
    # code below.

    # For reference:
    # [Get Class Name]
    # (https://stackoverflow.com/questions/510972/getting-the-class-name-of-an-instance)
    class_name: str = type(bit).__name__

    # Trim *class_name* and look up the associated FabBitTemplate by *template_name*:
    assert class_name.startswith("Fab") and class_name.endswith("Bit"), class_name
    template_name: str = class_name[3:-3]
    bit_templates: FabBitTemplates = FabBitTemplatesFactory.getTemplates()
    assert hasattr(bit_templates, template_name), (
        f"{template_name} is not a valid attribute of FabBitTemplates")
    bit_template: FabBitTemplate = getattr(bit_templates, template_name)
    json_dict: Dict[str, Any] = bit_template.toJSON(bit, True)
    return json_dict


# Main program:
def main(tracing: str) -> None:
    """Main program that executes unit tests."""
    next_tracing: str = tracing + " " if tracing else ""
    if tracing:
        print(f"{tracing}=>main()")

    FabBit._unit_tests(tracing=next_tracing)
    FabBitTemplates._unit_tests(tracing=next_tracing)
    FabBitTemplatesFactory._unit_tests(tracing=next_tracing)
    FabShape._unit_tests(tracing=next_tracing)
    FabShapes._unit_tests(tracing=next_tracing)
    FabAttributes._unit_tests(tracing=next_tracing)
    FabBitTemplate._unit_tests(tracing=next_tracing)
    FabBitTemplates._unit_tests(tracing=next_tracing)
    FabBitTemplatesFactory._unit_tests(tracing=next_tracing)
    if tracing:
        print(f"{tracing}<=main()")


if __name__ == "__main__":
    main(tracing=" ")
