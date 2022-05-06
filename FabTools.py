#!/usr/bin/env python3
"""FabTools: Tools for Fab..

This is a package provides classes used to define the tooling that is available in a shop.
They basically define some classes that interface with the FreeCAD Path Tools infrastructure.
The "new" FreeCAD Path Tools infrastructure organizes everything into a top level `Tools/`
directory and associated sub-directories as follows:

* `Tools/`: The top level directory that contains a `Shape/`, `Bit/`, and `Library/` sub-directory.
  * `Tools/Shape/`: This sub-directory contains tool template files in FreeCAD `.fcstd` format:
    * `ballend.fcstd`:  The ball end tool template.
    * ...
    * `v-bit.fcstd`: The V-bit groove tool template.

  * `Tools/Bit/`: This sub-directory contains FreeCAD Path Tool bit JSON files (`.fctb`):
    The JSON in each tool bit file (`.fctb`) references one shape `.fcstd` file from `Tools/Shape/`.
    * `6mm_Ball_End.fctb`: A 6mm Ball end end tool bit that uses `ballend.fcstd`.
    * ...
    * `60degree_VBit.fctb`: A 60-degree VBit tool bit that uses `v-bit.fcstd`.

  * `Tools/Library/`: This sub-directory contains FreeCAD Path library JSON files (`.fctl`)
    These files define a tool number to tool bit binding.  In general, each Shop machine
    will tend to have a dedicated library associated with it.  However, some machine tools can
    share the same library.  Each `.fctl` JSON library references Tool Bit files from `Tools/Bin/`.

    * `Default.fctl`: The default tools that comes with FreeCAD.
    * `Machine1.fctl`: The tools library for Machine1.
    * ...
    * `MachineN.fctl`: The tools library for MachineN.

The top-down class hierarchy for the FabTools package is:
* FabToolsDirectory: This corresponds to a `Tools/` directory:  (TBD).
  * FabShapes: This corresponds to a `Tools/Shape/` directory:
    * FabShape: This corresponds to a `.fcstd` tool shape template in the `Tools/Shape/` directory.
  * FabAttributes: This corresponds to bit attributes that do not specify bit shape dimensions.
  * FabBitTemplates: This contains all of the known FabBitTemplate's.
    * FabBitTemplate: This corresponds to a template is used to construct FabBit.
  * FabBits: This corresponds to a `Tools/Bit/` sub-Directory:
    * FabBit: This corresponds to a `.fctb` file in the `Tools/Bit/` directory.  For each different
      Shape, there is a dedicated class that represents that shape:
      * FabBallEndBit: This corresponds to `Tools/Shape/ballend.fcstd`.
      * FabBullNoseBit: This corresponds to `Tools/Shape/bullnose.fcstd`.
      * FabChamferBit: This corresponds to `Tools/Shape/chamfer.fcstd`.
      * FabDrillBit: This corresponds to `Tools/Shape/drill.fcstd`.
      * FabEndMillBit: This corresponds to `Tools/Shape/endmill.fcstd`.
      * FabProbeBit: This corresponds to `Tools/Shape/probe.fcstd`.
      * FabSlittingSawBit: This corresponds to `Tools/Shape/slittingsaw.fcstd`.
      * FabThreadMillBit: This corresponds to `Tools/Shape/thread-mill.fcstd`.
      * FabVBit: This corresponds to `Tools/Shape/v-bit.fcstd`.
  * FabLibraries: This corresponds to a `Tool/Library` directory:
    * FabLibrary: This corresponds to an individual `.fctl` file in the `Tools/Library` directory.

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

# Issues:
# * Turn off Legacy tools Path => Preferences => [] Enable Legacy Tools
# * Edit move the from line 11 to line 10 in .../Tools/Bit/45degree_chamfer.fctb to fix JSON error.
# * When setting path to library, be sure to include .../Tools/Library  (one level up does not work)

import json
from typeguard import check_type, check_argument_types
from typing import Any, Dict, IO, List, Tuple, Union
from dataclasses import dataclass
from pathlib import Path as PathFile
from FabToolTemplates import FabBit, FabBitTemplate, FabBitTemplates, FabBitTemplatesFactory
from FabToolBits import FabBallEndBit, FabBullNoseBit, FabChamferBit, FabDoveTailBit, FabDrillBit
from FabToolBits import FabEndMillBit, FabProbeBit, FabSlittingSawBit, FabThreadMillBit, FabVBit


# FabLibrary:
@dataclass(frozen=True)
class FabLibrary(object):
    """FabLibrary: Tool libraries directory (e.g. `.../Tools/Library/*.fctl`).

    Attributes:
    * *Name* (str): The stem of LibraryFile (i.e. `xyz.fctl` => "xyz".)
    * *LibraryFile* (PathFile): The file for the `.fctl` file.
    * *NumberedBitss*: Tuple[Tuple[int, FabBit], ...]: A list of numbered to FabBit's.

    Constructor:
    * FabLibrary("Name", LibraryFile, Tools)
    """

    Name: str
    LibraryFile: PathFile
    NumberedBits: Tuple[Tuple[int, FabBit], ...]

    # FabLibrary:__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabLibrary."""
        check_type("FabLibrary.Name", self.Name, str)
        check_type("FabLibrary.LibraryFile", self.LibraryFile, PathFile)
        check_type("FabLibrary.NumberedBits", self.NumberedBits, Tuple[Tuple[int, FabBit], ...])

    # FabLibrary.read():
    @staticmethod
    def read(library_file: PathFile, bits: "FabBits", tracing: str = "") -> "FabLibrary":
        """Read in FabLibrary from a JSON file."""
        if tracing:
            print(f"{tracing}=>FabLibrary.read({library_file}, *)")
        assert check_argument_types()

        # Open *library_file*, read it in and parse it into *json_dict*:
        json_file: IO[str]
        json_text: str
        with open(library_file) as json_file:
            json_text = json_file.read()
        try:
            json_dict: Dict[str, Any] = json.loads(json_text)
        except json.decoder.JSONDecodeError as decode_error:  # pragma: no unit cover
            assert False, f"Unable to parse {library_file} as JSON: Error:{str(decode_error)}"

        # The format of *json_dict* should be:
        # {
        #   "version": 1,
        #   "tools": [
        #     {
        #       "nr": 1,
        #       "path": "xyz.fctb"
        #     },
        #     ...
        #   ]
        # }

        # Extract *version* and *tools*:
        check_type("FabLibrary.json_dict", json_dict, Dict[str, Any])
        assert len(json_dict) == 2, "FabLibrary.readJson(): {len(json_dict)=}"
        version: Any = json_dict["version"] if "version" in json_dict else None
        assert isinstance(version, int) and version == 1, f"FabLibrary.readJson(): {version=}"
        tools: Any = json_dict["tools"] if "tools" in json_dict else None
        assert isinstance(tools, list), "FabLibrary.readJson(): {tools=}"

        # Sweep through *tools* in JSON and build sorted *numbered_bit_names* list:
        numbered_bit_names: List[Tuple[int, str]] = []
        bit_number: int
        bit_name: str
        check_type("FabLibrary.readJson(): tools", tools, List[Dict[str, Union[int, str]]])
        bit_dict: Any
        for bit_dict in tools:
            check_type("FabLibrary.readJson(): tool", bit_dict, Dict[str, Union[int, str]])
            bit_number = bit_dict["nr"] if "nr" in bit_dict else -1
            check_type("FabLibrary.readJson(): bit_number", bit_number, int)
            bit_name = bit_dict["path"] if "path" in bit_dict else ""
            check_type("FabLibrary.readJson(): path", bit_name, str)
            assert bit_number >= 0 and bit_name, f"{bit_number=} {bit_name=}"
            numbered_bit_names.append((bit_number, bit_name))
        numbered_bit_names.sort()

        # Lookup up the associated FabBit's:
        numbered_bits: List[Tuple[int, FabBit]] = []
        for bit_number, bit_name in numbered_bit_names:
            assert bit_name.endswith(".fctb")
            bit_stem: str = bit_name[:-5]
            if tracing:
                print(f"{tracing}Tool[{bit_number}]: '{bit_stem}'")
            try:
                bit: FabBit = bits.lookup(bit_stem)
            except KeyError as key_error:  # pragma: no unit coverage
                assert False, f"FabLibrary.readJson(): {str(key_error)}"
            numbered_bits.append((bit_number, bit))

        library: FabLibrary = FabLibrary(library_file.stem, library_file, tuple(numbered_bits))
        if tracing:
            print(f"{tracing}<=FabLibrary.read({library_file}, *)=>*")
        return library

    # FabLibrary.lookupName():
    def lookupName(self, name: str) -> FabBit:
        """Lookup a FabBit by name."""
        numbered_bits: Tuple[Tuple[int, FabBit], ...] = self.NumberedBits
        bit_number: int
        bit: FabBit
        for bit_number, bit in numbered_bits:
            if bit.Name == name:
                return bit
        raise KeyError(f"FabLibrary.lookupName('{name}'): Tool not found.")

    # FabLibrary.lookupNumber():
    def lookupNumber(self, number: int) -> FabBit:
        """Lookup a FabBit by name."""
        bit_number: int
        bit: FabBit
        for bit_number, bit in self.NumberedBits:
            if bit_number == number:
                return bit
        raise KeyError(f"FabLibrary.lookupNumber('{number}'): Tool not found.")

    # FabLibrary._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """FabLibrary Unit tests."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabLibrary._unit_tests()")
        tools_directory: PathFile = PathFile(__file__).parent / "Tools"
        bits_directory: PathFile = tools_directory / "Bit"
        libraries_directory: PathFile = tools_directory / "Library"

        # shapes: FabShapes = FabShapes.read(shapes_directory)
        bits: FabBits = FabBits.read(bits_directory)
        library_file: PathFile = libraries_directory / "Default.fctl"
        library: FabLibrary = FabLibrary.read(library_file, bits, tracing=next_tracing)

        number: int
        bit: FabBit
        for number, bit in library.NumberedBits:
            assert bit is library.lookupName(bit.Name)
            assert bit is library.lookupNumber(number)

        # Test lookup methods:
        desired_error: str
        try:
            library.lookupName("Bogus")
            assert False
        except KeyError as key_error:
            desired_error = '"FabLibrary.lookupName(\'Bogus\'): Tool not found."'
            assert str(key_error) == desired_error, (str(key_error), desired_error)
        try:
            library.lookupNumber(-1)
            assert False
        except KeyError as key_error:
            desired_error = '"FabLibrary.lookupNumber(\'-1\'): Tool not found."'
            assert str(key_error) == desired_error, (str(key_error), desired_error)

        if tracing:
            print(f"{tracing}<=FabLibrary._unit_tests()")


# FabLibraries:
@dataclass(frozen=True)
class FabLibraries(object):
    """FabLibraries: Represents a directory of FabLibrary's.

    Attributes:
    * *Name* (str): The directory name (i.e. the stem the LibraryPath.)
    * *LibrariesPath (PathFile): The directory that contains the FabLibraries.
    * *Libraries* (Tuple[FabLibrary, ...): The actual libraries sorted by library name.
    * *LibraryNames*: Tuple[str, ...]: The sorted library names.

    Constructor:
    * FabLibraries("Name", LibrariesPath, Libraries)

    """

    Name: str
    LibrariesPath: PathFile
    Libraries: Tuple[FabLibrary, ...]
    LibraryNames: Tuple[str, ...]

    # FabLibraries.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabLibriaries."""
        check_type("FabLibraries.Name", self.Name, str)
        check_type("FabLibraries.LibrariesPath", self.LibrariesPath, PathFile)
        check_type("FabLibraries.Libraries", self.Libraries, Tuple[FabLibrary, ...])
        check_type("FabLibraries.LibraryNames", self.LibraryNames, Tuple[str, ...])

    # FabLibraries.read():
    @staticmethod
    def read(libraries_path: PathFile, bits: "FabBits", tracing: str = "") -> "FabLibraries":
        """Read in a FabLibraries from a directory."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabLibraries.read('{str(libraries_path)}('), *)")
        assert check_argument_types(), "FabLibraries.read()"
        assert libraries_path.is_dir(), f"FabLibraries.read(): {libraries_path=}"
        libraries_dict: Dict[str, FabLibrary] = {}
        library_path: PathFile
        for library_path in libraries_path.glob("*.fctl"):
            assert library_path.exists(), "FabLibrary.read(): f{library_path} does not exist"
            library: FabLibrary = FabLibrary.read(library_path, bits, tracing=next_tracing)
            libraries_dict[library.Name] = library
        sorted_library_names: Tuple[str, ...] = tuple(sorted(libraries_dict.keys()))
        library_name: str
        sorted_libraries: Tuple[FabLibrary, ...] = tuple(
            [libraries_dict[library_name] for library_name in libraries_dict.keys()])
        libraries: FabLibraries = FabLibraries(
            libraries_path.stem, libraries_path, sorted_libraries, sorted_library_names)
        if tracing:
            print(f"{tracing}<=FabLibraries.read('{str(libraries_path)}('), *)=>*")
        return libraries

    # FabLibaries.nameLookup():
    def nameLookup(self, name: str) -> FabLibrary:
        """Lookup a library by name."""
        library: FabLibrary
        for library in self.Libraries:
            if library.Name == name:
                return library
        raise KeyError(f"FabLibraries.nameLookup(): "
                       f"{name} is not one of {self.LibraryNames}")  # pragma: no unit coverage

    # FabLibraries._unit_tests:
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform the FabLibraries unit tests."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabLibrarires._unit_tests()")
        tools_directory: PathFile = PathFile(__file__).parent / "Tools"
        # shapes_directory: PathFile = tools_directory / "Shape"
        bits_directory: PathFile = tools_directory / "Bit"
        libraries_directory: PathFile = tools_directory / "Library"

        # shapes: FabShapes = FabShapes.read(shapes_directory, tracing=next_tracing)
        bits: FabBits = FabBits.read(bits_directory, tracing=next_tracing)
        libraries: FabLibraries = FabLibraries.read(
            libraries_directory, bits, tracing=next_tracing)
        library: FabLibrary
        for library in libraries.Libraries:
            assert libraries.nameLookup(library.Name) is library
        if tracing:
            print(f"{tracing}<=FabLibrarires._unit_tests()")


# FabBits
@dataclass(frozen=True)
class FabBits(object):
    """FabBits: A collection FabBit's that corresponds to a `Tools/Bit/` sub-directory..

    Attributes:
    * *BitsDirectory*: (PathFile): The path to the `Tools/Bit/` sub-directory.
    * *Bits* (Tuple[FabBit, ...]): The associated FabBit's in name sorted order.
    * *Names* (Tuple[str, ...]): The sorted FabBit names.

    Constructor:
    * FabBits("Name", BitsPath, Bits, Names)
    """

    BitsPath: PathFile
    Bits: Tuple[FabBit, ...]
    Names: Tuple[str, ...]

    # FabBits.__post_init__():
    def __post_init__(self) -> None:
        """Initialize a FabBits."""
        check_type("FabBits.BitsPath", self.BitsPath, PathFile)
        check_type("FabBits.Bits", self.Bits, Tuple[FabBit, ...])
        check_type("FabBits.Names", self.Names, Tuple[str, ...])

    # FabBits.shapeNameToTemplateAndBit():
    @staticmethod
    def shapeNameToTemplateAndBit(shape_name: str) -> Tuple[FabBitTemplate, FabBit]:
        """Return the FabTempate and FabBit associated with a shape name."""
        bit_templates: FabBitTemplates = FabBitTemplatesFactory.getTemplates()  # type: ignore

        template: FabBitTemplate
        constructor: Any
        if shape_name == "ballend":
            template = bit_templates.BallEnd
            constructor = FabBallEndBit
        elif shape_name == "bullnose":
            template = bit_templates.BullNose
            constructor = FabBullNoseBit
        elif shape_name == "chamfer":
            template = bit_templates.Chamfer
            constructor = FabChamferBit
        elif shape_name == "dovetail":  # pragma: no unit covert
            template = bit_templates.DoveTail
            constructor = FabDoveTailBit
        elif shape_name == "drill":
            template = bit_templates.Drill
            constructor = FabDrillBit
        elif shape_name == "endmill":
            template = bit_templates.EndMill
            constructor = FabEndMillBit
        elif shape_name == "probe":
            template = bit_templates.Probe
            constructor = FabProbeBit
        elif shape_name == "slittingsaw":
            template = bit_templates.SlittingSaw
            constructor = FabSlittingSawBit
        elif shape_name == "thread-mill":
            template = bit_templates.ThreadMill
            constructor = FabThreadMillBit
        elif shape_name == "v-bit":
            template = bit_templates.V
            constructor = FabVBit
        else:
            assert False, f"Unrecogniezed {shape_name=}"
        return template, constructor

    # FabBits.toJSON():
    @staticmethod
    def toJSON(bit_json: Dict[str, Any], tools_directory: PathFile, tracing: str = "") -> FabBit:
        """Convert JSON dictionary to a FabBit.

        Arguments:
        * *bit_json* (Dict[str, Any]: The JSON dictionary that defines the FabBit.
        * *tools_directory* (FabPath): The tools directory under with the bit will be stored.

        Returns:
        * (FabBit): The resulting FabBit.

        """
        if tracing:
            print(f"{tracing}=>FabBits.toJSON(*, '{str(tools_directory)}')")

        assert check_argument_types()
        assert "name" in bit_json, "FabBits.toJSON(): No name found"
        name: str = bit_json["name"]
        assert "version" in bit_json, "FabBits.toJSON(): No version found"
        parameters: Dict[str, Any] = bit_json["parameter"] if "parameter" in bit_json else {}
        attributes: Dict[str, Any] = bit_json["attribute"] if "attribute" in bit_json else {}
        _ = attributes  # TODO: Is *attributes* actually needed?

        # Extract *version* and *shape_name* from *bit_json*:
        version: Any = bit_json["version"]
        assert isinstance(version, int) and version == 2, "FabBits.toJSON(): version is not 2"
        assert "shape" in bit_json, "FabBits.toJSON(): No shape found"
        shape: Any = bit_json["shape"]
        assert isinstance(shape, str) and shape.endswith(".fcstd"), (
            f"FabBits.toJSON(): {shape=} does not end in '.fcstd'")
        shape_name: str = shape[:-6]

        # Convert the *shape*name* into a *template* and *constructor*:
        template: FabBitTemplate
        constructor: Any
        template, constructor = FabBits.shapeNameToTemplateAndBit(shape_name)

        # Do a fixup for a thread mill.:
        if shape_name == "thread-mill":
            # The `Tools/Bit/5mm-thread-cutter.fctb` file doe not have a CuttingAngle parameter.
            # So we make one up here:
            if "CuttingAngle" not in parameters:
                parameters["CuttingAngle"] = "60.000 °"

        # Construct the *bit* from ...
        bit_path_file: PathFile = tools_directory / "Bit" / f"{name}.fctb"
        kwargs: Dict[str, Any] = template.kwargsFromJSON(bit_json, bit_path_file)
        if tracing:
            print(f"{tracing}{shape_name=} {constructor=}")
            # print(f"{tracing}{kwargs=}")
        bit: FabBit = constructor(**kwargs)

        if tracing:
            print(f"{tracing},=FabBits.toJSON(*, '{str(tools_directory)}')=>*")
        return bit

    # FabBits.read():
    @staticmethod
    def read(bits_directory: PathFile, tracing: str = "") -> "FabBits":
        """Read in a `Tools/Bit/` sub-directory.

        Arguments:
        * *bits_directory* (PathFile):
          The directory containing the `.fctb` Bit definitions.

        Returns:
        * (FabBits): The resulting FabBits that corresponds to the `Tools/Bit` sub-directory.

        """
        if tracing:
            print(f"{tracing}=>FabBits.read({str(bits_directory)}, *)")
        # bit_templates: FabBitTemplates = FabBitTemplates.factory()
        bits_table: Dict[str, FabBit] = {}
        assert check_argument_types()
        assert bits_directory.is_dir(), f"FabBits.read(): {str(bits_directory)} is not a directory"

        bit_paths_table: Dict[str, PathFile] = {}
        bit_file_path: PathFile
        for bit_file_path in bits_directory.glob("*.fctb"):
            bit_paths_table[str(bit_file_path)] = bit_file_path
        sorted_bit_path_file_names: Tuple[str, ...] = tuple(sorted(bit_paths_table.keys()))
        if tracing:
            print(f"{tracing}{sorted_bit_path_file_names=}")

        bit_path_file_name: str
        index: int
        for index, bit_path_file_name in enumerate(sorted_bit_path_file_names):
            bit_path_file: PathFile = bit_paths_table[bit_path_file_name]
            # Read in the *bit_json* dictionary from *bit_file_path*:
            bit_name: str = bit_path_file.stem
            if tracing:
                print(f"{tracing}BitFile[{index}]: Processing {str(bit_path_file)} {bit_name}")
            bit_file: IO[str]
            bit_json_text: str
            with open(bit_path_file) as bit_file:
                bit_json_text = bit_file.read()
            try:
                bit_json: Any = json.loads(bit_json_text)
            except json.decoder.JSONDecodeError as json_error:  # pragma: no unit cover
                assert f"FabBits.read(): JSON read error {str(bit_path_file)}: {str(json_error)}"

            check_type("FabBits.read(): bit_json", bit_json, Dict[str, Any])
            assert "version" in bit_json, "FabBits.read(): No version found"
            parameters: Dict[str, Any] = bit_json["parameter"] if "parameter" in bit_json else {}
            attributes: Dict[str, Any] = bit_json["attribute"] if "attribute" in bit_json else {}
            _ = attributes

            # Do extract some value from *bit_json*, do sanity checking and get *shape_type*:
            version: Any = bit_json["version"]
            assert isinstance(version, int) and version == 2, "FabBits.read(): version is not 2"
            assert "shape" in bit_json, "FabBits.read(): No shape found"
            shape: Any = bit_json["shape"]
            assert isinstance(shape, str) and shape.endswith(".fcstd"), (
                f"FabBits.read(): {shape=} does not end in '.fcstd'")
            shape_name: str = shape[:-6]
            template: FabBitTemplate
            constructor: Any
            template, constructor = FabBits.shapeNameToTemplateAndBit(shape_name)
            if shape_name == "thread-mill":
                # The `Tools/Bit/5mm-thread-cutter.fctb` file doe not have a CuttingAngle parameter.
                # So we make one up here:
                if "CuttingAngle" not in parameters:
                    parameters["CuttingAngle"] = "60.000 °"
            kwargs: Dict[str, Any] = template.kwargsFromJSON(bit_json, bit_path_file)
            if tracing:
                print(f"{tracing}{shape_name=} {constructor=}")
                # print(f"{tracing}{kwargs=}")
            bit: FabBit = constructor(**kwargs)
            bits_table[bit_name] = bit
            if tracing:
                print(f"{tracing}BitTable['{bit_name}']: {type(bit)=}")

        # Return the final FabBits object:
        sorted_names: Tuple[str, ...] = tuple(sorted(bits_table.keys()))
        sorted_bits: List[FabBit] = [bits_table[bit_name] for bit_name in sorted_names]
        for index, bit in enumerate(sorted_bits):
            assert sorted_names[index] == bit.Name, (
                f"[{index}] {sorted_names[index]=} != {bit.Name=}")
        # if tracing:
        #     print(f"{tracing}{sorted_names=}")
        #     print(f"{tracing}{sorted_bits=}")
        bits: FabBits = FabBits(bits_directory, tuple(sorted_bits), sorted_names)
        if tracing:
            print(f"{tracing}<=FabBits.read({str(bits_directory)}, *)=>|{len(sorted_names)}|")
        return bits

    # FabBits.lookup():
    def lookup(self, name: str) -> FabBit:
        """Look up a FabBit by name.

        Arguments:
        * *name* (str): The name of the FabBit.

        Returns:
        * (FabBit): The mataching FabBit.

        Raises:
        * (KeyError): If FabBit is  not present.

        """
        bit: FabBit
        for bit in self.Bits:
            if bit.Name == name:
                return bit
        raise KeyError(
            f"FabBits.lookup(): '{name}' is not one of {self.Names}.")  # pragma: no unit coverage

    # FabBits._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run FabBits unit tests."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabBits._unit_tests()")
        this_directory: PathFile = PathFile(__file__).parent
        tools_directory: PathFile = this_directory / "Tools"
        bits_directory: PathFile = tools_directory / "Bit"
        # shapes: FabShapes = FabShapes.read(shapes_directory)
        bits: FabBits = FabBits.read(bits_directory, tracing=next_tracing)
        index: int
        bit: FabBit
        for index, bit in enumerate(bits.Bits):
            if tracing:
                print(f"{tracing}Bit[{index}]: {bit.Name=}")
                lookup_bit: FabBit = bits.lookup(bit.Name)
                assert lookup_bit is bit, (bit.Name, bits.Names, lookup_bit, bit)

                bit_json: Dict[str, Any] = bit.toJSON()
                _ = bit_json

        # TODO: use *tools_directory*, *bit_directory*, and *shape_directory*.

        # library_file_path: PathFile = library_directory / "Default.fctl"
        # json_file: IO[str]
        # json_text: str
        # with open(library_file_path, "r") as json_file:
        #     json_text = json_file.read()

        # example_tools: Dict[str, FabBit] = FabBit._example_tools()

        # tools: FabBits = FabBits(Name="MyToolTable", Description="")

        # name: str
        # for name, tool in example_tools.items():
        #     tool_number += 1
        #     tools.add_tool(tool_number, tool)

        # my_tool_table_path: PathFile = PathFile(".") / "MyToolTable.json"
        # with open(my_tool_table_path, "w") as json_file:
        #     json_text = tools.combined_to_json("MyToolTable")
        #     json_file.write(json_text)

        if tracing:
            print(f"{tracing}<=FabBits._unit_tests()")


# Main program:
def main(tracing: str) -> None:
    """Main program that executes unit tests."""
    next_tracing: str = tracing + " " if tracing else ""
    if tracing:
        print(f"{tracing}=>main()")

    FabBits._unit_tests(tracing=next_tracing)
    FabLibrary._unit_tests(tracing=next_tracing)
    FabLibraries._unit_tests(tracing=next_tracing)
    FabBits._unit_tests(tracing=next_tracing)
    if tracing:
        print(f"{tracing}<=main()")


if __name__ == "__main__":
    main(tracing=" ")
