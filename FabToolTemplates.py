#!/usr/bin/env python3
"""FabToolTemplates: Templates for defining tool bits.

This package provides some classes that are used to build tables of tools needed for a shop
definition.  These are lower level classes that really are not expected to be used by end-users.
The classes are:
* FabShape:
  This represents a single Tool Bit shape template that is represented as a standard FreeCAD
  `.fcstd` document.  These files live in the `.../Tools/Shape/` directory.
* FabShapes:
  This represents all of the FabShape's in a `.../Tools/Shape/` directory.
* FabAttributes:
  This a just a sorted list of attribute value pairs. These values get stored into `.fctb` files
  in the `.../Tools/Bit/` directory.  In general, these values do not specify the physical shape
  parameters needed by the FabShape `.fcstd` files.  Instead, they specify things like the tool
  bit material, number flutes, etc.
* FabBitTemplate:
  This a class that specifies a all of the fields needed to for a FabBit.  The `.fctb` files
  live in the `.../Tools/Bit/` directory and a template is used to read/write the `.fctb` files.
* FabBitTemplates:
  This class simply lists one FaBBitTemplate for each different FabShape.
* FabTemplatesFactory:
  This is a trivial class that instatiates one of each FabTemplate object that can be reused since
  they never change.

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

from dataclasses import dataclass, field
import json
from pathlib import Path as PathFile
import tempfile
from typeguard import check_type, check_argument_types
from typing import Any, Dict, IO, List, Optional, Tuple, Union


# FabShape:
@dataclass(frozen=True)
class FabShape(object):
    """FabShape: Corresponds to FreeCAD Path library Shape 'template'.

    Attributes:
    * *Name* (str):
      The shape name which happens to be the stem `.fcstd` file (e.g. "v-bit.fcstd" => "v-bit".)
    * *Contents* (bytes):
      The contents of the `.fcstd` file.
    """

    Name: str
    Contents: bytes = field(repr=False)

    # FabShape.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing the FabShape."""
        check_type("FabShape.Name", self.Name, str)

    # FabShape.read():
    @staticmethod
    def read(name: str, tools_directory: PathFile, tracing: str = "") -> "FabShape":
        """Return the FabShape for a given shape name.

        Arguments:
        * *name* (str):
          The stem name of `.fcstd` file. (For example, the stem "probe.fcstd" is "probe".)
        * *tools_directory* (PathFile):
          The `.../Tools/` directory containing the `Shape/` subdirectory of shape `.fcstd` files.

        Returns:
        * (FabShape) The associated FabShape object for the `.fcstd` file.

        """
        if tracing:
            print(f"{tracing}=>FabShape.read({name}, {tools_directory}, {name})")
        shape_path: PathFile = tools_directory / "Shape" / f"{name}.fcstd"
        assert shape_path.exists(), f"{shape_path} does not exit"
        contents: bytes
        shape_file: IO[bytes]
        with open(shape_path, "rb") as shape_file:
            contents = shape_file.read()
        shape: FabShape = FabShape(shape_path.stem, contents)
        if tracing:
            print(f"{tracing}<=FabShape.read({name}, {tools_directory}, {name})=>{shape})=>*")
        return shape

    # FabShape.verify():
    def verify(self, tools_directory: PathFile) -> bool:
        """Verify that FabShape contents matches the actual file contents."""
        verify_fab_shape: FabShape = FabShape.read(self.Name, tools_directory)
        return self == verify_fab_shape

    # FabShape.write():
    def write(self, tools_directory: PathFile, tracing: str = "") -> None:
        """Write FabShape out to disk."""
        if tracing:
            print(f"{tracing}=>FabShape.Write({self.Name}, {tools_directory})")

        if tools_directory.name != "Tools":
            tools_directory = tools_directory / "Tools"  # pragma: no unit cover
        shapes_directory = tools_directory / "Shape"
        shapes_directory.mkdir(parents=True, exist_ok=True)
        assert shapes_directory.exists(), f"{shapes_directory} does not exist"

        shape_path_file: PathFile = shapes_directory / f"{self.Name}.fcstd"
        shape_file: IO[bytes]
        with open(shape_path_file, "wb") as shape_file:
            shape_file.write(self.Contents)

        if tracing:
            print(f"{tracing}<=FabShape.Write({self.Name}, {tools_directory})")

    # FabShape._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform unit tests."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabShape._unit_tests()")

        # Test read() method:
        shape_name: str = "endmill"
        tools_directory: PathFile = PathFile(__file__).parent / "Tools"
        shape: FabShape = FabShape.read(shape_name, tools_directory, tracing=next_tracing)
        assert shape.Name == shape_name, (shape.Name, shape_name)

        # Test write() and verify() method:
        with tempfile.TemporaryDirectory() as temporary_directory:
            temporary_tools_directory: PathFile = PathFile(temporary_directory) / "Tools"
            temporary_shape_directory: PathFile = temporary_tools_directory / "Shape"
            temporary_shape_directory.mkdir(parents=True, exist_ok=True)
            shape.write(temporary_tools_directory)
            assert shape.verify(temporary_tools_directory)

        if tracing:
            print(f"{tracing}<=FabShape._unit_tests()")


# FabShapes:
@dataclass(frozen=True)
class FabShapes(object):
    """FabShapes: A directory of FabShape's.

    Attributes:
    * *Shapes* (Tuple[FabShape, ...]: The corresponding FabShape's.
    * *Names* (Tuple[str, ...]: The sorted names of the FabShape's.

    Constructor:
    * FabShapes(Directory, Shapes, Names)
    """

    Shapes: Tuple[FabShape, ...]
    Names: Tuple[str, ...]

    # FabShapes.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabShapes."""
        check_type("FabShapes.Shapes", self.Shapes, Tuple[FabShape, ...])
        check_type("FabShapes.Names", self.Names, Tuple[str, ...])

    # FabShapes.read():
    @staticmethod
    def read(tools_directory: PathFile, tracing: str = "") -> "FabShapes":
        """Read in FabShapes from a directory."""
        if tracing:
            print(f"{tracing}=>FabShapes.read({tools_directory})")
        shapes_directory: PathFile = tools_directory / "Shape"
        assert shapes_directory.is_dir(), (
            f"FabShapes.read(): {str(shapes_directory)} is not a directory")
        shapes_table: Dict[str, FabShape] = {}
        shape_file: PathFile
        shape_names: List[str] = []
        for shape_file in shapes_directory.glob("*.fcstd"):
            shape: FabShape = FabShape.read(shape_file.stem, tools_directory)
            shape_names.append(shape.Name)
            shapes_table[shape.Name] = shape

        sorted_shape_names: Tuple[str, ...] = tuple(sorted(shapes_table.keys()))
        shape_name: str
        shapes: Tuple[FabShape, ...] = tuple([
            shapes_table[shape_name] for shape_name in sorted_shape_names])
        fab_shapes: FabShapes = FabShapes(shapes, sorted_shape_names)
        if tracing:
            print(f"{tracing}<=FabShapes.read({tools_directory})=>*")
        return fab_shapes

    # FabShapes.example():
    @staticmethod
    def example() -> "FabShapes":
        """Return an example FabShapes."""
        tools_directory: PathFile = PathFile(__file__).parent / "Tools"
        shapes: FabShapes = FabShapes.read(tools_directory)
        return shapes

    # FabShapes.lookup():
    def lookup(self, name) -> FabShape:
        """Lookup a FabShape by name."""
        shape: FabShape
        for shape in self.Shapes:
            if shape.Name == name:
                return shape
        raise KeyError(f"FabShapes.lookup(): {name} is not one of {self.Names}")

    # FabShapes.write():
    def write(self, tools_directory: PathFile, tracing: str = "") -> None:
        """Write FabShapes out to disk."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabShapes.write({tools_directory})")

        shapes_directory: PathFile = tools_directory / "Shape"
        shapes_directory.mkdir(parents=True, exist_ok=True)
        for shape in self.Shapes:
            shape.write(tools_directory, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=FabShapes.write({tools_directory})")

    # FabShapes._unit_tests()
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        if tracing:
            print(f"{tracing}=>FabShapes._unit_tests()")
        tools_directory: PathFile = PathFile(__file__).parent / "Tools"
        shapes: FabShapes = FabShapes.read(tools_directory)
        example_shapes: FabShapes = FabShapes.example()
        assert shapes == example_shapes
        shape: FabShape
        index: int
        for index, shape in enumerate(shapes.Shapes):
            assert shapes.lookup(shape.Name) is shape
            print(f"{tracing}Shape[{index}]: {shape.Name}")
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

    # FabAttributes.find():
    def find(self, attribute_name: str) -> Any:
        """Look up an attribute value by name.

        Arguments:
        * *attribute_name* (str): The attribute name to find.

        Returns:
        * (Any): The attribute value.  None is returned if *attribute_name* is not found.

        """
        name: str
        value: Any
        for name, value in self.Values:
            if name == attribute_name:
                return value
        return None  # pragma: no unit cover

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
        assert attributes.find("Flutes") == 2
        if tracing:
            print(f"{tracing}<=FabAttributes._unit_tests()")


# FabBit:
@dataclass(frozen=True)
class FabBit(object):
    """FabBit: Base class common to all FabBit sub-classes;

    Attributes:
    * *Name* (str): The name of the tool template (e.g. "5mm Endmill".)
    * *BitStem* (str): The stem of the corresponding `.fctb` file (e.g. "5mm_Endmill".)
    * *ShapeStem*: (str): The stem of the corresponding shape `.fcstd` file (e.g. "endmill".)
    * *Attributes*: (FabAttributes): The optional bit attributes.

    Constructor:
    * FabBit("Name", BitStem, ShapeStem, Attributes)

    """

    Name: str
    BitStem: str
    ShapeStem: str
    Attributes: FabAttributes

    # FabBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabCNCTemplate."""
        # assert self.Name != "BallEnd"
        check_type("FabBit.Name", self.Name, str)
        check_type("FabBit.BitStem", self.BitStem, str)
        check_type("FabBit.Shape", self.ShapeStem, str)
        check_type("FabBit.Attributes", self.Attributes, FabAttributes)

    # FabBit.getBitPriority():
    def getBitPriority(self, operation_kind: str) -> Optional[float]:
        """Return operation priority for an operation.

        Arguments:
        * *operation_kind* (str): The kind of operation (e.g. "pocket", "drill", etc.).

        Returns:
        * (Optional[float]): The priority as a negative number, where more negative numbers
          have a higher priority.

        """
        return None  # pragma: no unit cover

    # FabBit.getNumber():
    def getNumber(self, attribute_name: str) -> Union[float, int]:
        """Return an number value from a FabBit.

        The FabBit base class is sub-classed for each different bit type (e.g. FabEndMitBit,
        FabDrillBit, etd.)  Each sub-class adds specifies geometric attributes that make sense
        for the tool bit (e.g. CuttingEdgeHeight, Diameter, etc.)  In addition, all FabBit's
        have an attribute named Attributes that contains a FabAttributes object.  This contains
        information about the tool bit that do not effect the overall shape (e.g. "flutes",
        "material", etc.)  This method looks up a value from either the sub-class attributes
        of the FabAttributes object and returns the value number (Union[float, int]).  The
        values can be represented as string (e.g. "17", "123.45", "5mm", ".5in", "true", "false"
        etc.) or as explicit Python values int, float, or bool.  The result is an integer or
        a float as appropriate.

        Arguments:
        * *attribute_name* (str): The attribute name

        Returns:
        * (Union[int, float]): The resulting number.

        """
        attribute_value: Any = None
        if hasattr(self, attribute_name):
            attribute_value = getattr(self, attribute_name)
        else:
            attribute_value = self.Attributes.find(attribute_name)
        if attribute_value is None:
            raise RuntimeError(f"FabBit.getNumber('{attribute_name}'): attrinbute not found")
        value: Union[int, float] = 0.0
        if isinstance(attribute_value, bool):
            value = int(attribute_value)
        if isinstance(attribute_value, (float, int)):
            value = attribute_value
        elif isinstance(attribute_value, str):
            # A string of the form "number units"
            attribute_value = attribute_value.lower()
            if attribute_value == "true":
                value = 1
            elif attribute_value == "false":
                value = 0
            elif attribute_value.isdecimal():
                value = int(attribute_value)
            else:
                # Deal with string sof the form "NUMBER UNITS", where UNITS is optional:
                units: str = "mm"
                index: int
                character: str
                number: str = attribute_value
                for index, character in enumerate(attribute_value):
                    if character.isalpha():
                        units = attribute_value[index:].lower().strip()
                        number = attribute_value[:index]
                        break
                try:
                    value = float(number)
                except ValueError:
                    raise RuntimeError(
                        f"FabBit.getNumber('{attribute_name}'): "
                        f"Could not convert '{attribute_value}' into a number")
                assert isinstance(value, float), attribute_value
                if units == "mm":
                    pass
                elif units == "in":
                    value *= 2.54
                else:
                    raise RuntimeError(
                        f"FabBit.getNumber('{attribute_name}'): Unrecognized units '{units}'")
        else:
            raise RuntimeError(f"FabBit.getNumber('{attribute_name}'): "
                               f"Has {type(attribute_value)}, not a number")
        return value

    # FabBit.getOperationKinds():
    def getOperationKinds(self) -> Tuple[str, ...]:
        """Return the kind of operations supported by the FabBit.

        Returns:
        * (Tuple[str, ...]): The list of supported operations (e.g. "pocket", "drill", etc.)
        """
        return ()

    # FabBit.toJSON():
    def toJSON(self) -> Dict[str, Any]:
        """Return the JSON associated with a FabBit."""
        # Python does not really like circular class declarations.  This breaks the cycle.
        return _bit_to_json(self)

    # FabBit.write():
    def write(self, tools_directory: PathFile, tracing: str = "") -> None:
        """Write FabBit out to disk."""
        if tracing:
            print(f"{tracing}=>FabBit.write({self.Name})")

        if tools_directory.name != "Tools":
            tools_directory = tools_directory / "Tools"  # pragma: no unit cover
        bit_directory = tools_directory / "Bit"
        bit_directory.mkdir(parents=True, exist_ok=True)
        bit_path_file: PathFile = bit_directory / f"{self.BitStem}.fctb"

        bit_json: Dict[str, Any] = self.toJSON()
        json_text: str = json.dumps(bit_json, sort_keys=True, indent=2)
        bit_file: IO[str]
        with open(bit_path_file, "w") as bit_file:
            bit_file.write(json_text + "\n")

        if tracing:
            print(f"{tracing}<=FabBit.write({self.Name})")

    # FabBit._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabBit unit tests."""
        if tracing:
            print(f"{tracing}=>FabBit._unit_tests()")
        tools_directory: PathFile = PathFile(__file__).parent / "Tools"
        shape: FabShape = FabShape.read("probe", tools_directory)
        _ = shape
        attributes: FabAttributes = FabAttributes.fromJSON({
            "bool1": True,
            "bool2": False,
            "bool3": "True",
            "bool4": "False",
            "int1": 123,
            "int2": "123",
            "float1": 123.456,
            "float2": "123.456",
            "string1": "",
            "string2": "abc",
            "mm_test": "1.0 mm",
            "in_test": "1.0 in",
            "bad_unit": "123.0 fish",
            "bad_type": ("tuple",),
        })
        bit_stem: str = "5mm_Endmill"
        shape_stem: str = "endmill"

        bit: FabBit = FabBit("TestBit", bit_stem, shape_stem, attributes)
        assert bit.Name == "TestBit"
        assert bit.BitStem == bit_stem
        assert bit.ShapeStem == shape_stem
        assert bit.Attributes is attributes
        assert bit.getNumber("bool1") == 1
        assert bit.getNumber("bool2") == 0
        assert bit.getNumber("bool3") == 1
        assert bit.getNumber("bool4") == 0
        assert bit.getNumber("int1") == 123
        assert bit.getNumber("int2") == 123
        assert bit.getNumber("float1") == 123.456
        assert bit.getNumber("float2") == 123.456
        assert bit.getNumber("mm_test") == 1.0
        assert bit.getNumber("in_test") == 2.54

        # Exception tests:
        try:
            _ = bit.getNumber("bogus")
            assert False
        except RuntimeError as error:
            assert str(error) == "FabBit.getNumber('bogus'): attrinbute not found", str(error)
        try:
            _ = bit.getNumber("bad_unit")
            assert False
        except RuntimeError as error:
            assert str(error) == "FabBit.getNumber('bad_unit'): Unrecognized units 'fish'", (
                str(error))
        try:
            _ = bit.getNumber("bad_attribute_name")
            assert False
        except RuntimeError as error:
            assert str(error) == "FabBit.getNumber('bad_attribute_name'): attrinbute not found", (
                str(error))
        try:
            _ = bit.getNumber("string1")
            assert False
        except RuntimeError as error:
            assert str(error) == (
                "FabBit.getNumber('string1'): Could not convert '' into a number"), str(error)
        try:
            _ = bit.getNumber("string2")
            assert False
        except RuntimeError as error:
            assert str(error) == (
                "FabBit.getNumber('string2'): Could not convert 'abc' into a number"), str(error)
        try:
            _ = bit.getNumber("bad_type")
            assert False
        except RuntimeError as error:
            assert str(error) == (
                "FabBit.getNumber('bad_type'): Has <class 'tuple'>, not a number"), str(error)

        if tracing:
            print(f"{tracing}<=FabBit._unit_tests()")


# FabBitTemplate:
@dataclass(frozen=True)
class FabBitTemplate(object):
    """FabBitTemplate: A Template for creating a FabBit.

    Attributes:
    * *Name* (str): The template name which matches the FabXXXBit class type.
    * *BitName* (str): The name of the example bit.
    * *BitStem* (str): The stem of the example `.fctb` file.  (see getExample).
    * *ShapeStem* (str): The stem of associated example `.fcstd` shape file.
    * *Parameters* (Tuple[Tuple[str, Tuple[type, ...]], ...]):
      The allowed parameter names and associated types of the form:
      ("ParameterName", (type1, ..., typeN), "example") for no type checking ("ParameterName",)
    * *Attributes* (Tuple[Tuple[str, Tuple[type, ...]], ...]):
      The allowed parameter names and associated types of the form:
      ("ParameterName", (type1, ..., typeN), "example") for no type checking ("ParameterName",)

    Constructor:
    * FabBitTemplate("Name", "BitStem", "ShapeStem", Parameters, Attributes)
    """

    Name: str
    BitName: str
    BitStem: str
    ShapeStem: str
    Parameters: Tuple[Tuple[str, Tuple[type, ...], Union[bool, float, int, str]], ...]
    Attributes: Tuple[Tuple[str, Tuple[type, ...], Union[bool, float, int, str]], ...]

    # FabBitTemplate.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabBitTemplate."""
        check_type("FabBitTemplate.Name", self.Name, str)
        check_type("FabBitTemplate.BitName", self.BitName, str)
        check_type("FabBitTemplate.BitStem", self.BitStem, str)
        check_type("FabBitTemplate.Shapetem", self.ShapeStem, str)
        check_type("FabBitTemplate.Parameters", self.Parameters,
                   Tuple[Tuple[str, Tuple[type, ...], Union[bool, float, int, str]], ...])
        check_type("FabBitTemplate.Attributes", self.Attributes,
                   Tuple[Tuple[str, Tuple[type, ...], Union[bool, float, int, str]], ...])

    # FabBitTemplate.kwargsFromJSON():
    def kwargsFromJSON(
            self, json_dict: Dict[str, Any],
            bit_file: PathFile, tracing: str = "") -> Dict[str, Any]:
        """Return the keyword arguments needed to initialize a FabBit.

        Arguments:
        * *json_dict* (Dict[str, Any]): The JSON dictionary of information.
        * *bit_file* (PathFile): The PathFile to the FabBit JSON.

        Returns:
        * (Dict[str, Any]) this is aF bunch of keyword arguments that can be passed in as
          a arguments to FabBit constructor.
        """
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

        assert isinstance(name, str) and name, f"FabBit.kwargsFromJSON(): Bad {name=}"
        assert isinstance(version, int) and version == 2, f"FabBit.kwargsFromJSON(): Bad {version=}"
        assert isinstance(shape_fcstd, str) and shape_fcstd.endswith(".fcstd"), (
            f"FabBit.kwargsFromJSON(): Bad {shape_fcstd=}")
        assert shape_fcstd == f"{self.ShapeStem}.fcstd", (shape_fcstd, self.ShapeStem)

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
        kwargs: Dict[str, Any] = {}
        kwargs["Name"] = name
        kwargs["BitStem"] = bit_file.stem
        kwargs["ShapeStem"] = self.ShapeStem
        fill(kwargs, "Parameters", parameters, self.Parameters)
        assert "attribute" in json_dict, "FabAttributes.fromJSON(): attribute key not present"
        kwargs["Attributes"] = FabAttributes.fromJSON(json_dict["attribute"], tracing=next_tracing)
        # fill(None, "attribute", attributes, self.Attributes)
        if tracing:
            print(f"{tracing}<=FabBitTemplate.kwargsFromJSON(...)=>{kwargs}")
        return kwargs

    # FabBitTemplate.toJSON():
    def toJSON(self, bit: "FabBit", with_attributes: bool) -> Dict[str, Any]:
        """Convert a FabBit to a JSON dictionary using a FabBitTemplate.

        Arguments:
        * *bit* (FabBit): The FabBit to convert into JASON.
        * *with_attributes* (bool): If True, all attributes are present, otherwise they are not.

        Returns:
        * (Dict[str, Any]): The associated JSON dictionary.

        """
        parameters: Dict[str, Any] = {name: getattr(bit, name) for name, _, _ in self.Parameters}
        attributes: Dict[str, Any] = bit.Attributes.toJSON() if with_attributes else {}

        json_dict: Dict[str, Any] = {
            "version": 2,
            "name": bit.Name,
            "shape": f"{self.ShapeStem}.fcstd",
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
            BitName="5mm Endmill",
            BitStem="5mm_Endmill",
            ShapeStem="endmill",
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
        assert template.BitStem == "5mm_Endmill"
        assert template.ShapeStem == "endmill"
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

        Returns:
        * (FabBitTemplates): The initialized FabBitTemplates object.

        """
        # Create each template first:
        ball_end_template: FabBitTemplate = FabBitTemplate(
            Name="BallEnd",
            BitName="6mm Ball End",
            BitStem="6mm_Ball_End",
            ShapeStem="ballend",
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
            BitName="6 mm Bull Nose",
            BitStem="6mm_Bullnose",
            ShapeStem="bullnose",
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
            BitName="45 Deg. Chamfer",
            BitStem="45degree_chamfer",
            ShapeStem="chamfer",
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
            BitName="no_dovetail_name_yet",
            BitStem="no_dovetail_stem_yet",
            ShapeStem="dovetail",
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
            BitName="5mm Drill",
            BitStem="5mm_Drill",
            ShapeStem="drill",
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
            BitName="5mm Endmill",
            BitStem="5mm_Endmill",
            ShapeStem="endmill",
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
            BitName="Probe",
            BitStem="probe",
            ShapeStem="probe",
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
            BitName="Slitting Saw",
            BitStem="slittingsaw",
            ShapeStem="slittingsaw",
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
            BitName="5mm-thread-cutter",
            BitStem="5mm-thread-cutter",
            ShapeStem="thread-mill",
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
            BitName="60 Deg. V-Bit",
            BitStem="60degree_Vbit",
            ShapeStem="v-bit",
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
        bit_templates: FabBitTemplates = FabBitTemplatesFactory.getTemplates()

        # Lookup *bit_template* using *bit_type* to extract the correct attribute name:
        bit_type_text: str = str(bit_type)  # Should result in "<class '...FabXXXBit'>"
        start_index: int = bit_type_text.find("Fab")
        assert start_index >= 0
        bit_type_name: str = bit_type_text[start_index + 3:-5]  # Extract XXX, the type name.
        assert hasattr(bit_templates, bit_type_name), (
            f"FabBitTemplate.getExample(): {bit_type_name=}")
        bit_template: FabBitTemplate = getattr(bit_templates, bit_type_name)

        # Initialize *kwargs* with required values:
        attribute_name: str
        example_value: Union[bool, float, int, str]
        kwargs: Dict[str, Any] = {
            "Name": bit_template.BitName,
            "BitStem": bit_template.BitStem,
            "ShapeStem": bit_template.ShapeStem,
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
    """Convert a FabBit to a JSON dict.

    Arguments:
    * *bit* (FabBit): The FabBit to convert into a JSON dictionary.

    Returns:
    *(Dict[str, Any]): The resulting JSON dictionary.

    """
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
