#!/usr/bin/env python3
"""FabTools: Tools for Fab.

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
  * FabTooling: This corresponds to the `Tools/` directory.

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

from dataclasses import dataclass, field
from pathlib import Path as PathFile
import json
import tempfile
from typeguard import check_type, check_argument_types
from typing import Any, Dict, IO, List, Sequence, Tuple, Union

from FabToolTemplates import FabAttributes, FabBit, FabBitTemplate, FabBitTemplates
from FabToolTemplates import FabBitTemplatesFactory, FabShapes
from FabToolBits import FabBallEndBit, FabBullNoseBit, FabChamferBit, FabDoveTailBit, FabDrillBit
from FabToolBits import FabEndMillBit, FabProbeBit, FabSlittingSawBit, FabThreadMillBit, FabVBit


# FabBits:
@dataclass(frozen=True)
class FabBits(object):
    """FabBits: A collection FabBit's that corresponds to a `Tools/Bit/` sub-directory..

    Attributes:
    * *Bits* (Tuple[FabBit, ...]): The associated FabBit's in name sorted order.
    * *Names* (Tuple[str, ...]): The sorted FabBit names.
    * *Stems* (Tuple[str, ...]): Stem names in the same order as the Bits.

    Constructor:
    * FabBits(Bits, Names, Stems)

    """
    Bits: Tuple[FabBit, ...]
    Names: Tuple[str, ...]
    Stems: Tuple[str, ...]

    # FabBits.__post_init__():
    def __post_init__(self) -> None:
        """Initialize a FabBits."""
        check_type("FabBits.Bits", self.Bits, Tuple[FabBit, ...])
        check_type("FabBits.Names", self.Names, Tuple[str, ...])
        check_type("FabBits.Stems", self.Stems, Tuple[str, ...])

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
    def toJSON(bit_json: Dict[str, Any],
               tools_directory: PathFile, bit_stem_name: str, tracing: str = "") -> FabBit:
        """Convert JSON dictionary to a FabBit.

        Arguments:
        * *bit_json* (Dict[str, Any]): The JSON dictionary that defines the FabBit.
        * *tools_directory* (FabPath): The tools directory under with the bit will be stored.
        * *bit_stem_name* (str):
          The stem name of the (`.fctb`) file.  (For example: "probe.fctb" => "probe")

        Returns:
        * (FabBit): The resulting FabBit.

        """
        if tracing:
            print(f"{tracing}=>FabBits.toJSON(*, '{str(tools_directory)}', '{bit_stem_name}')")

        assert check_argument_types()
        assert "name" in bit_json, "FabBits.toJSON(): No name found"
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

        # Construct the *bit_path_file*:
        bit_path_file: PathFile = tools_directory / "Bit" / f"{bit_stem_name}.fctb"
        kwargs: Dict[str, Any] = template.kwargsFromJSON(bit_json, bit_path_file)
        if tracing:
            print(f"{tracing}{shape_name=} {constructor=}")
            # print(f"{tracing}{kwargs=}")
        bit: FabBit = constructor(**kwargs)

        if False and tracing:  # pragma: no unit cover
            # print(f"{tracing}bit_json=")
            # print(json.dumps(bit_json, indent=4))
            print(f"{tracing}{bit=}")
        if tracing:
            print(f"{tracing}<=FabBits.toJSON(*, '{str(tools_directory)}', '{bit_stem_name}')=>*")
        return bit

    # FabBits.read():
    @staticmethod
    def read(tools_directory: PathFile, shapes: FabShapes, tracing: str = "") -> "FabBits":
        """Read in a `Tools/Bit/` sub-directory.

        Arguments:
        * *tools_directory* (PathFile):
          The `.../Tools` directory containing the `Bit/` subdirectory of `.fctb` Bit definitions.
        * *shapes: (FabShapes): The FabShape objects to use.

        Returns:
        * (FabBits): The resulting FabBits that corresponds to the `Tools/Bit` sub-directory.

        """
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabBits.read({str(tools_directory)}, *)")
        bits_directory: PathFile = tools_directory / "Bit"
        assert bits_directory.is_dir(), f"FabBits.read(): {str(bits_directory)} is not a directory"
        bits_table: Dict[str, FabBit] = {}
        assert check_argument_types()

        bit_paths_table: Dict[str, PathFile] = {}
        bit_file_path: PathFile
        for bit_file_path in bits_directory.glob("*.fctb"):
            bit_paths_table[str(bit_file_path)] = bit_file_path
        sorted_bit_path_file_names: Tuple[str, ...] = tuple(sorted(bit_paths_table.keys()))
        bit_path_file_name: str
        index: int
        for index, bit_path_file_name in enumerate(sorted_bit_path_file_names):
            bit_path_file: PathFile = bit_paths_table[bit_path_file_name]
            # Read in the *bit_json* dictionary from *bit_file_path*:
            bit_stem_name: str = bit_path_file.stem
            if tracing:
                print(f"{tracing}BitFile[{index}]: Processing {str(bit_path_file)}")
            bit_file: IO[str]
            bit_json_text: str
            with open(bit_path_file) as bit_file:
                bit_json_text = bit_file.read()
            try:
                bit_json: Any = json.loads(bit_json_text)
            except json.decoder.JSONDecodeError as json_error:  # pragma: no unit cover
                assert f"FabBits.read(): JSON read error {str(bit_path_file)}: {str(json_error)}"

            bit: FabBit = FabBits.toJSON(bit_json, tools_directory,
                                         bit_stem_name, tracing=next_tracing)
            bits_table[bit.Name] = bit
            if tracing:
                print(f"{tracing}BitTable['{bit_stem_name}']: {type(bit)=}")

        # Return the final FabBits object:
        sorted_names: Tuple[str, ...] = tuple(sorted(bits_table.keys()))
        sorted_bits: List[FabBit] = [bits_table[bit_name] for bit_name in sorted_names]
        ordered_stems: List[str] = [bit.BitStem for bit in sorted_bits]
        for index, bit in enumerate(sorted_bits):
            assert sorted_names[index] == bit.Name
            assert sorted_bits[index] is bit, (
                f"sorted_names[{index}]: {sorted_names[index]=} != {bit}")
            assert ordered_stems[index] == bit.BitStem
        # if tracing:
        #     print(f"{tracing}{sorted_names=}")
        #     print(f"{tracing}{sorted_bits=}")
        bits: FabBits = FabBits(tuple(sorted_bits), sorted_names, tuple(ordered_stems))
        if tracing:
            print(f"{tracing}<=FabBits.read({str(tools_directory)}, *)=>|{len(sorted_names)}|")
        return bits

    # FabBits.write()
    def write(self, tools_directory: PathFile, tracing: str = "") -> None:
        """Write FabBits out to disk."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabBits.write(*, {tools_directory})")

        assert tools_directory.name == "Tools", str(tools_directory)
        shapes_directory: PathFile = tools_directory / "Shape"
        bits_directory: PathFile = tools_directory / "Bit"

        bit: FabBit
        if shapes_directory.is_dir() and bits_directory.is_dir():
            shapes: FabShapes = FabShapes.read(tools_directory)
            previous_bits: FabBits = FabBits.read(tools_directory, shapes, tracing=next_tracing)
            previous_bit: FabBit
            for bit in self.Bits:
                try:
                    previous_bit = previous_bits.nameLookup(bit.Name)
                except KeyError:  # pragma: no unit cover
                    continue
                assert bit == previous_bit, (bit, previous_bit)
                #     raise RuntimeError(f"Bit '{bit.Name} already exists with different content'")

        # Write any new bits:
        bits_directory.mkdir(parents=True, exist_ok=True)
        for bit in self.Bits:
            if not (bits_directory / f"{bit.Name}.fctb").exists():
                bit.write(tools_directory, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=FabBits.write(*, {tools_directory})")

    # FabBits.nameLookup():
    def nameLookup(self, name: str) -> FabBit:
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
            f"FabBits.lookup(): '{name}' is not one of {self.Names}.")  # pragma: no unit cover

    # FabBits.stemLookup():
    def stemLookup(self, stem: str) -> FabBit:
        """Look up a FabBit by file stem.

        Arguments:
        * *stem* (str): The stem of the FabBit (i.e. "5mm_Endmill.fctb" => "5mm_Endmill".)

        Returns:
        * (FabBit): The mataching FabBit.

        Raises:
        * (KeyError): If FabBit is  not present.

        """
        bit: FabBit
        for bit in self.Bits:
            if bit.BitStem == stem:
                return bit
        raise KeyError(
            f"FabBits.lookup(): '{stem}' is not one of {self.Stems}.")  # pragma: no unit cover

    # FabBits.fromSequence():
    @staticmethod
    def fromSequence(bits: Sequence[FabBit]) -> "FabBits":
        """Create a FabBits from a sequence of FabBit's."""
        bits_table: Dict[str, FabBit] = {}
        name: str
        bit: FabBit
        for bit in bits:
            if bit.Name not in bits_table:
                bits_table[bit.Name] = bit
        unsorted_names: Tuple[str, ...] = tuple(bits_table.keys())
        sorted_names: Tuple[str, ...] = tuple(sorted(unsorted_names))
        sorted_bits: Tuple[FabBit, ...] = tuple([bits_table[name] for name in sorted_names])
        sorted_stems: Tuple[str, ...] = tuple([bits_table[name].ShapeStem for name in sorted_names])
        fab_bits: "FabBits" = FabBits(sorted_bits, sorted_names, sorted_stems)
        return fab_bits

    # FabBits._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run FabBits unit tests."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabBits._unit_tests()")
        tools_directory: PathFile = PathFile(__file__).absolute().parent / "Tools"
        shapes: FabShapes = FabShapes.read(tools_directory, tracing=next_tracing)
        bits: FabBits = FabBits.read(tools_directory, shapes, tracing=next_tracing)
        temporary_directory: Any
        with tempfile.TemporaryDirectory() as temporary_directory:
            assert isinstance(temporary_directory, str), temporary_directory
            temporary_tools_directory: PathFile = PathFile(temporary_directory) / "Tools"
            bits.write(temporary_tools_directory)
            bits.write(temporary_tools_directory)  # The 2nd call should succeed without error.
        index: int
        bit: FabBit
        for index, bit in enumerate(bits.Bits):
            if tracing:
                print(f"{tracing}XBit[{index}]: '{bit.Name}' => {str(bit.BitStem)}")
                name_lookup_bit: FabBit = bits.nameLookup(bit.Name)
                assert name_lookup_bit is bit
                stem_lookup_bit: FabBit = bits.stemLookup(bit.BitStem)
                assert stem_lookup_bit is bit
                bit_json: Dict[str, Any] = bit.toJSON()
                _ = bit_json

        if tracing:
            print(f"{tracing}<=FabBits._unit_tests()")


# FabLibrary:
@dataclass(frozen=True)
class FabLibrary(object):
    """FabLibrary: Tool libraries directory (e.g. `.../Tools/Library/*.fctl`).

    Attributes:
    * *Name* (str): The stem of LibraryFile (i.e. `xyz.fctl` => "xyz".)
    * *NumberedBits*: Tuple[Tuple[int, FabBit], ...]: A list of numbered to FabBit's.

    Constructor:
    * FabLibrary("Name", NumberedBits)

    """

    Name: str
    NumberedBits: Tuple[Tuple[int, FabBit], ...]

    # FabLibrary:__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabLibrary."""
        check_type("FabLibrary.Name", self.Name, str)
        check_type("FabLibrary.NumberedBits", self.NumberedBits, Tuple[Tuple[int, FabBit], ...])

    # FabLibrary.read():
    @staticmethod
    def read(tools_directory: PathFile, name: str,
             bits: "FabBits", tracing: str = "") -> "FabLibrary":
        """Read in FabLibrary from a JSON file.

        Arguments:
        * *tools_directory* (PathFile):
          The `.../Tools/` directory that contains the `Library/` sub-directory.
        * *name* (str): The stem of the `.fctl` file (i.e. `MyTools.fctl` => `MyTools`.)
        * *bits*: (FabBits): The available bit templates.

        Returns:
        * (FabLibrary): The associated FabLibrary object.
        """
        if tracing:
            print(f"{tracing}=>FabLibrary.read({tools_directory}, {name}, *)")
        assert check_argument_types()

        # Open *library_file*, read it in and parse it into *json_dict*:
        json_file: IO[str]
        json_text: str
        library_directory: PathFile = tools_directory / "Library"
        library_path_file: PathFile = library_directory / f"{name}.fctl"
        assert library_path_file.exists(), f"FabLibrary.read(): {library_path_file} does not exist"
        with open(library_path_file) as json_file:
            json_text = json_file.read()
        try:
            json_dict: Dict[str, Any] = json.loads(json_text)
        except json.decoder.JSONDecodeError as decode_error:  # pragma: no unit cover
            assert False, f"Unable to parse {library_path_file} as JSON: Error:{str(decode_error)}"

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
                bit: FabBit = bits.stemLookup(bit_stem)
            except KeyError as key_error:  # pragma: no unit coverage
                assert False, f"FabLibrary.readJson(): {str(key_error)}"
            numbered_bits.append((bit_number, bit))

        library: FabLibrary = FabLibrary(name, tuple(numbered_bits))
        if tracing:
            print(f"{tracing}<=FabLibrary.read({tools_directory}, {name}, *)=>*")
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

    # FabLibrary.write():
    def write(self, tools_directory: PathFile, tracing: str = "") -> None:
        """Write FabLibrary out to disk."""
        if tracing:
            print(f"{tracing}=>FabLibrary.write({tools_directory})")

        if tools_directory.stem != "Tools":
            tools_directory = tools_directory / "Tools"  # pragma: no unit cover
        bit_directory = tools_directory / "Library"
        bit_directory.mkdir(parents=True, exist_ok=True)

        # Convert the *numbered_bits* into *json_text*:
        numbered_bits: Tuple[Tuple[int, FabBit], ...] = self.NumberedBits
        tools: List[Dict[str, Any]] = []
        for bit_number, bit in numbered_bits:
            tools.append({"nr": bit_number, "path": f"{bit.BitStem}.fctb"})
        json_dict: Dict[str, Any] = {
            "version": 1,
            "tools": tools,
        }
        json_text: str = json.dumps(json_dict, indent=2)

        # Write out *json_text*:
        library_path_file: PathFile = bit_directory / f"{self.Name}.fctl"
        json_file: IO[str]
        with open(library_path_file, "w") as json_file:
            json_file.write(json_text)

        if tracing:
            print(f"{tracing}<=FabLibrary.write({tools_directory})")

    # FabLibrary._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """FabLibrary Unit tests."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabLibrary._unit_tests()")
        tools_directory: PathFile = PathFile(__file__).absolute().parent / "Tools"

        # shapes: FabShapes = FabShapes.read(shapes_directory)
        shapes: FabShapes = FabShapes.read(tools_directory, tracing=next_tracing)
        bits: FabBits = FabBits.read(tools_directory, shapes, tracing=next_tracing)
        library: FabLibrary = FabLibrary.read(
            tools_directory, "Default", bits, tracing=next_tracing)

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
    * *Libraries* (Tuple[FabLibrary, ...): The actual libraries sorted by library name.
    * *LibraryNames*: Tuple[str, ...]: The sorted library names.

    Constructor:
    * FabLibraries("Name", Libraries, LibraryNames)

    """

    Name: str
    Libraries: Tuple[FabLibrary, ...]
    LibraryNames: Tuple[str, ...]

    # FabLibraries.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabLibriaries."""
        check_type("FabLibraries.Name", self.Name, str)
        check_type("FabLibraries.Libraries", self.Libraries, Tuple[FabLibrary, ...])
        check_type("FabLibraries.LibraryNames", self.LibraryNames, Tuple[str, ...])

    # FabLibraries.read():
    @staticmethod
    def read(tools_directory: PathFile, bits: "FabBits", tracing: str = "") -> "FabLibraries":
        """Read in a FabLibraries from a directory.

        Arguments:
        * *tools_directory* (PathFile):
          The `.../Tools/` directory that contains the `Library/` sub-directory.
        * *bits*: (PathFile):
          The FabBits's object contain the FabBits associated with the `Bits/` sub-directory.

        Returns:
        (FabLibraries):
        The FabLibraries object that contains all of the associated FabLibrary's objects.

        """
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabLibraries.read('{str(tools_directory)}('), *)")
        assert check_argument_types(), "FabLibraries.read()"
        libraries_dict: Dict[str, FabLibrary] = {}
        library_directory: PathFile = tools_directory / "Library"
        assert library_directory.is_dir(), f"FabLibraries.read(): {library_directory=}"
        library_path: PathFile
        for library_path in library_directory.glob("*.fctl"):
            assert library_path.exists(), "FabLibraries.read(): f{library_path} does not exist"
            name: str = library_path.stem
            library: FabLibrary = FabLibrary.read(
                tools_directory, name, bits, tracing=next_tracing)
            libraries_dict[library.Name] = library
        sorted_library_names: Tuple[str, ...] = tuple(sorted(libraries_dict.keys()))
        library_name: str
        sorted_libraries: Tuple[FabLibrary, ...] = tuple(
            [libraries_dict[library_name] for library_name in libraries_dict.keys()])
        libraries: FabLibraries = FabLibraries(
            library_path.stem, sorted_libraries, sorted_library_names)
        if tracing:
            print(f"{tracing}<=FabLibraries.read('{str(tools_directory)}('), *)=>*")
        return libraries

    # FabLibraries.nameLookup():
    def nameLookup(self, name: str) -> FabLibrary:
        """Lookup a library by name."""
        library: FabLibrary
        for library in self.Libraries:
            if library.Name == name:
                return library
        raise KeyError(f"FabLibraries.nameLookup(): "
                       f"{name} is not one of {self.LibraryNames}")  # pragma: no unit coverage

    # FabLibraries.write():
    def write(self, tools_directory: PathFile, tracing: str = "") -> None:
        """Write FabLibraries out to disk."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabLibraries.write({tools_directory})")

        library: FabLibrary
        for library in self.Libraries:
            library.write(tools_directory, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=FabLibraries.write({tools_directory})")

    # FabLibraries._unit_tests:
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform the FabLibraries unit tests."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabLibrarires._unit_tests()")
        tools_directory: PathFile = PathFile(__file__).absolute().parent / "Tools"

        shapes: FabShapes = FabShapes.read(tools_directory, tracing=next_tracing)
        bits: FabBits = FabBits.read(tools_directory, shapes, tracing=next_tracing)
        libraries: FabLibraries = FabLibraries.read(tools_directory, bits, tracing=next_tracing)
        library: FabLibrary
        for library in libraries.Libraries:
            assert libraries.nameLookup(library.Name) is library
        if tracing:
            print(f"{tracing}<=FabLibrarires._unit_tests()")


# FabTooling:
@dataclass(frozen=True)
class FabTooling(object):
    """FabTooling: A class that contains FabBit's, FabShape's, and FabLibrary's.

    Attributes:
    * *Shapes* (FabShapes): The FabShape's.
    * *Bits* (FabBits): The FabBit's
    * *Libraries* (FabLibraries): The FabLibrary's

    Constructor:
    * FabTooling(Shapes, Bits, Libraries)

    In practice, The FabToolingFactory class is an easier way to create a FabTooling object.

    """

    Shapes: FabShapes
    Bits: FabBits
    Libraries: FabLibraries

    # FabTooling.read():
    @staticmethod
    def read(tools_directory: PathFile, tracing: str = "") -> "FabTooling":
        """Read in a FabTooling from directory.

        Arguments:
        * *tools_directory* (PatFile): The `.../Tooling` directory to read from.

        Returns:
        * (FabTooling) The resulting FabTooling object.

        """
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabTooling.read({tools_directory})")
        shapes: FabShapes = FabShapes.read(tools_directory, tracing=next_tracing)
        bits: FabBits = FabBits.read(tools_directory, shapes, tracing=next_tracing)
        libraries: FabLibraries = FabLibraries.read(tools_directory, bits, tracing=next_tracing)
        tooling: FabTooling = FabTooling(shapes, bits, libraries)
        if tracing:
            print(f"{tracing}<=FabTooling.read({tools_directory})=>*")
        return tooling

    # FabTooling.write():
    def write(self, tools_directory: PathFile, tracing: str = "") -> None:
        """Write FabTooling into a directory.

        Arguments:
        * *tools_directory* (PatFile): The `.../Tooling` directory to read from.

        Returns:
        * (FabTooling) The resulting FabTooling object.

        """
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabTooling.write({tools_directory})")

        self.Shapes.write(tools_directory, tracing=next_tracing)
        self.Bits.write(tools_directory, tracing=next_tracing)
        self.Libraries.write(tools_directory, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=FabTooling.write({tools_directory})")

    # FabTooling._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run unit tests for FabTooling."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabTooling._unit_tests()")

        from_tools_directory: PathFile = PathFile(__file__).absolute().parent / "Tools"
        from_tooling: FabTooling = FabTooling.read(from_tools_directory, tracing=next_tracing)

        with tempfile.TemporaryDirectory() as temporary_directory:
            to_tools_directory: PathFile = PathFile(temporary_directory) / "Tools"
            from_tooling.write(to_tools_directory, tracing=next_tracing)
            to_tooling: FabTooling = FabTooling.read(to_tools_directory, tracing=next_tracing)
            index: int
            assert from_tooling.Shapes == to_tooling.Shapes
            assert from_tooling.Bits == to_tooling.Bits
            assert from_tooling.Libraries == to_tooling.Libraries
            assert from_tooling == to_tooling
        if tracing:
            print(f"{tracing}<=FabTooling._unit_tests()")


# FabToolingFactory:
@dataclass
class FabToolingFactory(object):
    """FabToolingFactory: A class to build a FabTooling.

    Attributes:
    * *Name* (str): The name of the tooling factory (empty string is allowed.)
    * *InitialToolsPath* (PathFile):
      The parent directory of an initial `Tools` directory.
      This directory is used to fetch the available shapes from `.../Tools/Shape`.
    """

    Name: str
    InitialToolsDirectory: PathFile
    _shapes: FabShapes = field(init=False, repr=False)
    _tool_table: Dict[int, FabBit] = field(init=False, repr=False)

    # FabToolingFactory.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing a FabToolingFactory."""
        check_type("FabToolingFactory.Name", self.Name, str)
        check_type("FabToolingFactory.InitialShapesPath", self.InitialToolsDirectory, PathFile)
        shapes: FabShapes = FabShapes.read(self.InitialToolsDirectory)
        self._shapes = shapes
        self._tool_table = {}

    # FabToolingFactory.drill():
    def drill(self, tool_number: int, name: str, stem_name: str, material: str, flutes: int,
              diameter: Union[str, float], length: Union[str, float],
              tip_angle: Union[str, float], is_center_cut: bool,
              maximum_depth: Union[str, float]) -> None:
        """Add a drill to FabToolingFactory:

        Arguments:
        * *tool_number* (int): The tool number to use.
        * *name* (str): The drill name:
        * *stem_name* (str): The file stem name to use for the `.fctb` file.
        * *material* (str): The material the tool is made out of.
        * *flutes* (int): The number of flutes.
        * *diameter* (Union[str, float]): The drill diameter as string (mm/inch) or a float (mm).
        * *length* (Union[str, float]): The overall length of the drill.
        * *tip_angle* (Union[str, float): The drill point tip angle in degrees.
        * *is_center_cut* (bool): True for center cut drills and False otherwise.
        * *maximum_depth* (Union[str, float]): The maximum drilling depth.
        """
        attributes: FabAttributes = FabAttributes.fromJSON({
            "Material": material,
            "Flutes": flutes,
            "IsCenterCut": is_center_cut,
            "MaximumDepth": maximum_depth,
        })
        drill_bit: FabDrillBit = FabDrillBit(name, stem_name, "drill", attributes,
                                             diameter, length, tip_angle)
        self._insert_tool(tool_number, drill_bit)

    # FabToolingFactory.double_angle():
    def double_angle(self, tool_number: int, name: str, stem_name: str, material: str, flutes: int,
                     diameter: Union[str, float], cutting_edge_height: Union[str, float],
                     cutting_edge_angle: Union[str, float], length: Union[str, float],
                     shank_diameter: Union[str, float], neck_diameter: Union[str, float],
                     neck_height: Union[str, float]) -> None:
        """Add a drill to FabToolingFactory:

        Arguments:
        * *tool_number* (int): The tool number to use.
        * *name* (str): The drill name:
        * *stem_name* (str): The file stem name to use for the `.fctb` file.
        * *material* (str): The material the tool is made out of.
        * *flutes* (int): The number of flutes.
        * *diameter* (Union[str, float]):
           The diameter of the double angle cutter as string (mm/inch) or a float (mm).
        * *cutting_edge_height* (Union[str, float]):
          The height of the double angle cutter from the tool bottom to the neck bottom.
        * *cutting_edge_angle* (Union[str, float]):
          The cutting angle of the double angle cutter.
        * *length* (Union[str, float]):
          The overall length of the entire double angle cutter including shank.
        * *shank_diameter* (Union[str, float]): The diameter of the shank (i.e. non cutting edge.)
        * *neck_diameter* (Union[str, float]):
          The diameter of double angle cutter neck.
        * *neck_height* (Union[str, float]):
          The height of the neck from the top of the double angle cutter to the bottom of the shank.

        """
        attributes: FabAttributes = FabAttributes.fromJSON({
            "Material": material,
            "Flutes": flutes,
        })
        double_angle: FabThreadMillBit = FabThreadMillBit(
            name, stem_name, "thread-mill", attributes,
            Diameter=diameter, CuttingAngle=cutting_edge_angle,
            Crest=cutting_edge_height, Length=length, ShankDiameter=shank_diameter,
            NeckDiameter=neck_diameter, NeckLength=neck_height)
        self._insert_tool(tool_number, double_angle)

    # FabToolingFactory.dove_tail():
    def dove_tail(self, tool_number: int, name: str, stem_name: str, material: str, flutes: int,
                  diameter: Union[str, float],
                  cutting_edge_height: Union[str, float], cutting_edge_angle: Union[str, float],
                  length: Union[str, float], shank_diameter: Union[str, float],
                  neck_diameter: Union[str, float], neck_height: Union[str, float]) -> None:
        """Add a drill to FabToolingFactory:

        Arguments:
        * *tool_number* (int): The tool number to use.
        * *name* (str): The drill name:
        * *stem_name* (str): The file stem name to use for the `.fctb` file.
        * *material* (str): The material the tool is made out of.
        * *flutes* (int): The number of flutes.
        * *diameter* (Union[str, float]):
           The diameter of the bottom of the dove tail cutter as string (mm/inch) or a float (mm).
        * *cutting_edge_height* (Union[str, float]):
          The height of the dove tail cutter from the bottom to the neck bottom.
        * *cutting_edge_angle* (Union[str, float]):
          The height of the dove tail cutter from the bottom to the neck bottom.
        * *length* (Union[str, float]):
          The overall length of the entire dove tail cutter including shank.
        * *shank_diameter* (Union[str, float]): The diameter of the shank (i.e. non cutting edge.)
        * *neck_diameter* (Union[str, float]):
          The diameter of dove tail cutter neck.
        * *neck_height* (Union[str, float]):
          The height of the neck from the top of the dove tail cutter to the bottom of the shank.

        """
        attributes: FabAttributes = FabAttributes.fromJSON({
            "Material": material,
            "Flutes": flutes,
        })
        dove_tail: FabDoveTailBit = FabDoveTailBit(
            name, stem_name, "dovetail", attributes,
            Diameter=diameter, CuttingEdgeAngle=cutting_edge_angle,
            CuttingEdgeHeight=cutting_edge_height, Length=length, ShankDiameter=shank_diameter,
            NeckDiameter=neck_diameter, NeckHeight=neck_height, TipDiameter=diameter)
        self._insert_tool(tool_number, dove_tail)

    # FabToolingFactory.end_mill():
    def end_mill(self, tool_number: int, name: str, stem_name: str, material: str, flutes: int,
                 diameter: Union[str, float], cutting_edge_height: Union[str, float],
                 length: Union[str, float], shank_diameter: Union[str, float]) -> None:
        """Add a drill to FabToolingFactory:

        Arguments:
        * *tool_number* (int): The tool number to use.
        * *name* (str): The drill name:
        * *stem_name* (str): The file stem name to use for the `.fctb` file.
        * *material* (str): The material the tool is made out of.
        * *flutes* (int): The number of flutes.
        * *diameter* (Union[str, float]):
           The diameter end mill cutter as string (mm/inch) or a float (mm).
        * *length* (Union[str, float]): The overall length of the entire end-mill including shank.
        * *cutting_edge_height (Union[str, float]): The length of the cutting edge.
        * *shank_diameter* (Union[str, float]): The diameter of the shank (i.e. non cutting edge.)
        """
        attributes: FabAttributes = FabAttributes.fromJSON({
            "Material": material,
            "Flutes": flutes,
        })
        end_mill: FabEndMillBit = FabEndMillBit(
            name, stem_name, "endmill", attributes,
            cutting_edge_height, diameter, length, shank_diameter)
        self._insert_tool(tool_number, end_mill)

    # FabToolingFactory.v_groove():
    def v_groove(self, tool_number: int, name: str, stem_name: str, material: str, flutes: int,
                 diameter: Union[str, float], cutting_edge_angle: Union[str, float],
                 cutting_edge_height: Union[str, float], length: Union[str, float],
                 shank_diameter: Union[str, float], tip_diameter: Union[str, float]) -> None:
        """Add a V grove bit to FabToolingFactory:

        Arguments:
        * *tool_number* (int): The tool number to use.
        * *name* (str): The drill name:
        * *stem_name* (str): The file stem name to use for the `.fctb` file.
        * *material* (str): The material the tool is made out of.
        * *flutes* (int): The number of flutes.
        * *diameter* (Union[str, float]):
           The outer diameter v grove bit as string (mm/inch) or a float (mm).
        * *length* (Union[str, float]): The overall length of the entire end-mill including shank.
        * *cutting_edge_angle (Union[str, float]): The cutting edge angle in degrees.
        * *cutting_edge_height (Union[str, float]):
          The length of the cutting edge above the V portion of the bit.
        * *shank_diameter* (Union[str, float]): The diameter of the shank (i.e. non cutting edge.)
        * *tip_diameter* (Union[str, float]): The bottom tip diameter (set to 0 for a point.)
        """
        attributes: FabAttributes = FabAttributes.fromJSON({
            "Material": material,
            "Flutes": flutes,
        })
        v_groove: FabVBit = FabVBit(
            name, stem_name, "v-bit", attributes,
            CuttingEdgeAngle=cutting_edge_angle, CuttingEdgeHeight=cutting_edge_height,
            Diameter=diameter, Length=length,
            ShankDiameter=shank_diameter, TipDiameter=tip_diameter)
        self._insert_tool(tool_number, v_groove)

    # FabToolingFactory._insert_tool():
    def _insert_tool(self, tool_number: int, bit: FabBit) -> None:
        """Insert a tool into FabToolingFactory.

        Arguments:
        * *tool_number* (int): The tool number to use.
        * *bit* (FabBit): The bit to assign to the tool number.

        """
        assert check_argument_types()
        if tool_number < 1:
            raise KeyError(f"FabToolingFactory._insert_tool(): "
                           f"Tool number ({tool_number}) is not positive")  # pragma: no unit cover
        if tool_number in self._tool_table:
            raise KeyError(
                f"FabToolingFactory._insert_tool(): Tool number ({tool_number}) "
                "is already assigned to '{tool_table[tool_number].name}'")  # pragma: no unit cover
        self._tool_table[tool_number] = bit

    # FabToolingFactory.getLibrary():
    def getLibrary(
            self, library_stem: str, tools_directory: PathFile, tracing: str = "") -> FabLibrary:
        """Return a FabLibrary containti the current tools."""
        # next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabToolingFactory.createLibrary('{library_stem}')")

        tool_table: Dict[int, FabBit] = self._tool_table
        sorted_tool_numbers: Tuple[int, ...] = tuple(sorted(tool_table.keys()))
        tool_number: int
        bit: FabBit
        numbered_bits: Tuple[Tuple[int, FabBit], ...] = tuple([
            (tool_number, tool_table[tool_number]) for tool_number in sorted_tool_numbers
        ])

        library: FabLibrary = FabLibrary(library_stem, numbered_bits)
        if tracing:
            print(f"{tracing}<=FabToolingFactory.createLibrary('{library_stem}')=>*")
        return library

    # FabToolingFactory.getBits():
    def getBits(self) -> FabBits:
        """Return FabBits from a FabToolingFactory."""
        bits: FabBits = FabBits.fromSequence(tuple(self._tool_table.values()))
        return bits

    # FabToolingFactory.write():
    def write(self, library_stem: str, tools_directory: PathFile, tracing: str) -> None:
        """Using FabToolingFactory write out files for a FabTooling.

        Arguments:
        * *library_stem* (str): The stem of the `.fctl` library file in `.../Tools/Library/`.
        * *tools_directory* (PathFile): The Tools directory to write everything out to.

        """
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabToolingFactory.write({library_stem}, {tools_directory})")

        # Read *shapes* from this *this_tools_directory*:
        tools_directory.mkdir(parents=True, exist_ok=True)
        shapes: FabShapes = FabShapes.read(self.InitialToolsDirectory, tracing=next_tracing)
        bits: FabBits = self.getBits()
        library: FabLibrary = self.getLibrary(library_stem, tools_directory, tracing=next_tracing)
        libraries: FabLibraries = FabLibraries("Library", (library,), ("TestLibrary",))
        tooling: FabTooling = FabTooling(shapes, bits, libraries)
        tooling.write(tools_directory, tracing=next_tracing)

        if tracing:
            print(f"{tracing}<=FabToolingFactory.write({library_stem}, {tools_directory})=>*")

    # FabToolingFactory.createExampleTools():
    def createExampleTools(self, tracing: str = "") -> None:
        """Create some example tools."""
        if tracing:
            print(f"{tracing}=>FabToolingFactory.createExampleTools()")

        self.v_groove(2, "3/8 in Mill Drill", "3_8_in_Mill_Drill", "HSS", flutes=2,
                      diameter="0.375 in", cutting_edge_angle="90 °",
                      cutting_edge_height="0.775 in", length="2.25 in",
                      shank_diameter="0.375", tip_diameter="0.000 in")
        self.drill(3, "#36 Drill", "No_32_Drill", "HSS", 2,  # McMaster: 2912A211 2.5" deep drill
                   "0.1065 in", "2.5000 in", "118 °", False, "0.0000 in")  # Max Z?
        self.drill(4, "#27 Drill", "No_27_Drill", "HSS", 2,
                   "0.1440 in", "1.875 in", "118 °", False, "0.0000 in")  # Max Z?
        self.end_mill(5, "3/8 in End Mill", "3_8_in_End_Mill", "HSS", flutes=2,
                      diameter="0.375 in", length="0.750 in",
                         cutting_edge_height="0.375 in", shank_diameter="0.375 in")
        self.end_mill(6, "1/4 in End Mill", "1_4_in_End_Mill", "HSS", flutes=4,
                      diameter="0.250 in", length="2.00 in",
                      cutting_edge_height="0.750 in", shank_diameter="0.250 in")
        self.double_angle(7, "3/4 in 90° Double Angle", "3_4_in_90_deg_Double_Angle", "HSS",
                          flutes=10, diameter="0.750 in", cutting_edge_height="0.250 in",
                          cutting_edge_angle="90 °", length="2.000 in",
                          shank_diameter="0.375 in", neck_diameter="0.250 in",
                          neck_height="0.625 in")
        self.dove_tail(8, "3/8 in 45 ° Dove Tail", "3_8_in_45_deg_Dove_Tail", "HSS", flutes=6,
                       diameter="0.375 in", cutting_edge_height="0.125 in",
                       cutting_edge_angle="45 °", length="2.125 in",
                       shank_diameter="0.375 in", neck_diameter="0.0125 in",
                       neck_height="0.450 in")
        self.end_mill(9, "1/8 in End Mill", "1_8_in_End_Mill", "HSS", flutes=2,
                      diameter="0.125 in", length="2.000 in",
                      cutting_edge_height="0.500 in", shank_diameter="0.125 in")
        self.end_mill(10, "3/16 in End Mill", "3_16_in_End_Mill", "HSS", flutes=2,
                      diameter="0.1875 in", length="2.500 in",
                      cutting_edge_height="0.500 in", shank_diameter="0.1875 in")
        self.drill(11, "#25 Drill", "No_25_Drill", "HSS", 2,
                   "0.1495 in", "2.000 in", "118 °", False, "0.0000 in")  # Max Z?
        self.drill(12, "#9 Drill", "No_9_Drill", "HSS", 2,
                   "0.1960 in", "12.34 in", "118 °", False, "0.0000 in")  # Max Z?
        self.drill(13, "#43 Drill", "No_43_Drill", "HSS", 2,  # McMaster: 3096357
                   "0.0890 in", "12.34 in", "118 °", False, "0.0000 in")  # Max Z?
        self.drill(14, "#32 Drill", "No_32_Drill", "HSS", 2,
                   "0.1160 in", "12.34 in", "118 °", False, "0.0000 in")  # Max Z?
        self.drill(15, "6mm Drill", "6mm_Drill", "HSS", 2,
                   "6.0000 mm", "12.34 in", "135 °", False, "0.0000 in")  # Max Z?
        # end_mill_3_4 = shop._end_mill_append("3/4 End Mill",
        #  13, hss, in3_4, 2, in1_3_8)
        self.drill(17, "#30 Drill", "No_30_Drill", "HSS", 2,
                   "0.1285 in", "12.34 in", "118 °", False, "0.0000 in")  # Max Z?
        self.drill(18, "1/8 in Drill", "1_8_in_Drill", "HSS", 2,
                   "0.125 in", "12.34 in", "118 °", False, "0.0000 in")  # Max Z?
        self.drill(19, "1/16 in Drill", "1_16_in_Drill", "HSS", 2,
                   "0.0625 in", "12.34", "118 °", False, "0.0000 in")  # Max Z?
        self.drill(20, "3/32 in Drill", "3_16_in_Drill", "HSS", 2,
                   "0.09375 in", "12.34", "118 °", False, "0.0000 in")  # Max Z?
        self.drill(21, "#42 Drill", "No_42_Drill", "HSS", 2,
                   "0.0935 in", "12.34", "118 °", False, "0.0000 in")  # Max Z?
        self.drill(22, "#52 Drill", "No_52_Drill", "HSS", 2,
                   "0.0635 in", "12.34", "118 °", False, "0.0000 in")  # Max Z?
        self.drill(23, "3/64 Drill", "3_64_in_Drill", "HSS", 2,
                   "0.46875 in", "12.34", "118 °", False, "0.0000 in")  # Max Z?
        self.drill(24, "#19 Drill", "No_19_Drill", "HSS", 2,
                   "0.1660 in", "12.34", "118 °", False, "0.0000 in")  # Max Z?
        self.drill(25, "#50 Drill", "No_50_Drill", "HSS", 2,
                   "0.0700 in", "12.34", "118 °", False, "0.0000 in")  # Max Z?
        self.drill(26, "8mm Drill", "8mm_Drill", "HSS", 2,
                   "8.0000 mm", "12.34", "135 °", False, "0.0000 in")  # Max Z?
        # tap_4_40 = shop._tap_append("#4-40 tap",
        #   27, hss, L(inch=0.0890), 2, L(inch=0.550), L(inch=0.050), L(inch=1.000)/40.0,
        #   Time(sec=1.500), Time(sec=1.500), Hertz(rpm=500.0), Hertz(rpm=504.0), 0.050)
        # tap_6_32 = shop._tap_append("#6-32 tap",
        #   28, hss, L(inch=0.1065), 2, L(inch=0.625), L(inch=0.100), L(inch=1.000)/32.0,
        #   Time(sec=1.500), Time(sec=1.500), Hertz(rpm=500.0), Hertz(rpm=504.0), 0.050)

        if tracing:
            print(f"{tracing}<=FabToolingFactory.createExampleTools()")

    # FabToolingFactory.getExampleTooling():
    @staticmethod
    def getExampleTooling(tracing: str = "") -> FabTooling:
        """Return an example FabTooling."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>getExampleTooling()")

        tools_directory: PathFile = PathFile(__file__).parent / "Tools"
        # library: FabLibrary = FabLibrary.getExample(shapes)

        factory: FabToolingFactory = FabToolingFactory("TestTooling", tools_directory)
        factory.createExampleTools(tracing=next_tracing)

        shapes: FabShapes = FabShapes.read(tools_directory, tracing=next_tracing)
        bits: FabBits = factory.getBits()

        library: FabLibrary = factory.getLibrary("Library", tools_directory)
        libraries: FabLibraries = FabLibraries("Library", (library,), ("TestLibrary",))
        tooling: FabTooling = FabTooling(shapes, bits, libraries)

        if tracing:
            print(f"{tracing}<=getExampleTooling()=>*")
        return tooling

    # FabToolingFactory._unit_tests():
    @staticmethod
    def _unit_tests(tracing: str) -> None:
        """Unit tests for FabToolingFactory."""
        next_tracing: str = tracing + " " if tracing else ""
        if tracing:
            print(f"{tracing}=>FabToolingFactory._unit_tests()")

        tools_directory: PathFile = PathFile(__file__).absolute().parent / "Tools"
        factory: FabToolingFactory = FabToolingFactory("TestTooling", tools_directory)
        factory.createExampleTools(tracing=next_tracing)
        test_tools_directory: PathFile = PathFile("/tmp") / "Tools"
        factory.write("TestLibrary", test_tools_directory, tracing=next_tracing)

        example_tooling: FabTooling = FabToolingFactory.getExampleTooling(tracing=next_tracing)
        _ = example_tooling

        if tracing:
            print(f"{tracing}<=-FabToolingFactory._unit_tests()")


# Main program:
def main(tracing: str) -> None:
    """Main program that executes unit tests."""
    next_tracing: str = tracing + " " if tracing else ""
    if tracing:
        print(f"{tracing}=>main()")

    FabBits._unit_tests(tracing=next_tracing)
    FabLibrary._unit_tests(tracing=next_tracing)
    FabLibraries._unit_tests(tracing=next_tracing)
    FabTooling._unit_tests(tracing=next_tracing)
    FabToolingFactory._unit_tests(tracing=next_tracing)
    if tracing:
        print(f"{tracing}<=main()")


if __name__ == "__main__":
    main(tracing=" ")
