#!/usr/bin/env python3
"""FabShop: Shop and associated Machines.

This is a package provides classes used to define what machines are available in a shop.

* FabShop: A collection of FabMachine's.
* FabMachine: A base class for all machines.
  * FabCNC: A CNC mill or router:
    * FabRouter: A CNC router.
    * FabMill: A CNC Mill.
  * FabCutter: A CNC Laser or Water Jet:
    * FabLaser: A CNC laser.
    * FabWaterJet: A CNC water jet.
  * FabLathe: A CNC lathe.
  * Fab3DPrinter: A 3D printer.

"""


from cadquery import Vector  # type: ignore


# <--------------------------------------- 100 characters ---------------------------------------> #

# Issues:
# * Turn off Legacy tools Path => Preferrences => [] Enable Legacy Tools
# * Edit move the from line 11 to line 10 in .../Tools/Bit/45degree_chamfer.fctb to fix JSON error.
# * When setting path to library, be sure to include .../Tools/Library  (one level up does not work)

import json
from typeguard import check_argument_types, check_type
from typing import Any, cast, Dict, IO, List, Tuple, Union
from dataclasses import dataclass, field
from pathlib import Path as FilePath


# FabTool:
@dataclass(frozen=True)
class FabTool(object):
    """FabCNCShape: Base class for CNC tool bit templates.

    Required Base Attributes:
    * *Name* (str): The name of the tool template.
    * *FileName* (pathlib.Path): The tool template file name (must have a suffix of`.fcstd` file)

    Keyword Only Base Attributes:
    * *Material: (str = ""):
      The tool material is one of "Carbide", "CastAlloy", "Ceramics", "Diamond",
      "HighCarbonToolSteel", "HighSpeedSteel", or "Sialon".  This can optionally be followed
      by further description (e.g. ":Cobalt", ":Cobalt:M42", ":Cobalt:M42:ALTIN")
    * *OffsetLength: (Unnion[None, str, float] = None):
      The distance from the tool tip to the Z zero point on the mill.
      This is used to populate a CNC controller offset field for each tool.
    * *ToolHolderHeight: (Union[None, str, float] = None):
      The distance from tool tip to the base of the tool holder.
      The tool holder must be kept above the clearance height.

    """

    Name: str
    FileName: FilePath
    Material: str = field(default="Carbide")
    OffsetLength: Union[None, float, str] = field(default=None)
    ToolHolderHeight: Union[None, float, str] = field(default=None)
    VendorName: str = field(default="")
    VendorPartNumber: str = field(default="")
    _ParameterNames: Tuple[str, ...] = field(init=False, repr=False, default=())
    _AttributeNames: Tuple[str, ...] = field(init=False, repr=False, default=())
    Hash: str = field(init=False, repr=False, default="")
    ToolType: str = field(init=False, default="??")

    # FabTool.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabCNCTemplate."""
        name = cast(str, self._get_attribute("Name", (str,)))
        _ = name
        file_name = cast(FilePath, self._get_attribute("FileName", (FilePath,)))
        material = cast(str, self._get_attribute("Material", (str,)))
        allowed_materials: Tuple[str, ...] = (
            "Carbide", "CastAlloy", "Ceramics", "Diamond",
            "HighCarbonToolSteel", "HighSpeedSteel", "Sialon")
        if material not in allowed_materials:
            raise RuntimeError("FabTool.__post_init__():"
                               f"Material '{material}' is not one of {allowed_materials}")
        _ = self._get_attribute("ToolHolderHeight", (type(None), float, str))
        _ = self._get_attribute("VendorName", (str,))
        _ = self._get_attribute("VendorPartNumber", (str,))

        if file_name.suffix != ".fcstd":
            raise RuntimeError(
                "FabTool.__post_init__(): "
                f"Filename '{file_name}' suffix is '{self.FileName.suffix}', not '.fcstd'")

        sub_material: Any
        for sub_material in material:
            if not isinstance(sub_material, str):
                raise RuntimeError(
                    "FabTool.__post_init__(): "
                    f"Sub-material {sub_material} is type {type(sub_material)}, not str.")

        self._extend_attribute_names(
            ("Material", "ToolHolderHeight", "VendorName", "VendorPartNumber"))

    # FabTool._extend_parameter_names():
    def _extend_parameter_names(self, parameter_names: Tuple[str, ...]) -> None:
        """Extend the FabTool parameters."""
        # Needed to initialize update fields in frozen objects.
        object.__setattr__(self, "_ParameterNames", self._ParameterNames + parameter_names)

    # FabTool._extend_attribute_names():
    def _extend_attribute_names(self, attribute_names: Tuple[str, ...]) -> None:
        """Extend the FabTool parameters."""
        # Needed to initialize update fields in frozen objects.
        object.__setattr__(self, "_AttributeNames", self._AttributeNames + attribute_names)

    # FabTool._get_attribute():
    def _get_attribute(self, attribute_name: str, types: Tuple[type, ...]) -> Any:
        """Return an attribute value by name."""
        if not hasattr(self, attribute_name):
            raise RuntimeError("FabTool._get_attribute(): "
                               f"Attribute '{attribute_name} is not present.'")
        attribute: Any = getattr(self, attribute_name)
        if not isinstance(attribute, types):
            raise RuntimeError("FabTool._get_attribute(): "
                               f"Attribute '{attribute_name} is {type(attribute)}, not {types}'")
        return attribute

    # FabTool._set_hash():
    def _set_hash(self) -> None:
        """Compute and set the hash FabTool hash value."""
        # Note "_ParameterNames", "_AttributesNames", and "Hash" are excluded from *base_names*:
        base_names: Tuple[str, ...] = (
            "Name", "FileName", "Material", "ToolHolderHeight", "VendorName", "VendorPartNumber")
        all_names: Tuple[str, ...] = base_names + self._ParameterNames + self._AttributeNames
        name: str
        hashes: Tuple[int, ...] = tuple([hash(getattr(self, name)) for name in all_names])
        final_hash: int = abs(hash(hashes)) & 0xffffffffffffffff  # 64-bit positive hash
        object.__setattr__(self, "Hash", f"{final_hash:016x}")

    # FabTool._set_tool_type():
    def _set_tool_type(self, tool_type: str) -> None:
        """Compute and set the hash FabTool hash value."""
        # Note "_ParameterNames", "_AttributesNames", and "Hash" are excluded from *base_names*:
        object.__setattr__(self, "ToolType", tool_type)

    # FabTool.to_json():
    def to_json(self, with_attributes: bool = True, table_name: str = "") -> str:
        """Return FabToolTemptlate as a JSON string.

        Arguments:
        * *with_attributes* (bool = True):
          If True include additional "non-FreeCAD" attributes; otherwise leave blank.
        * *table_name* (str = ""):
          A stand alone JSON file is produced when empty, otherwise an indented JSON
          dictiornary named *table_name* is produced.

        """
        comma: str

        # Collect all output into *lines*:
        lines: List = []
        if not table_name:
            lines = [
                '{',
                '  "version": 2,',
                f'  "name": "{self.Name}",',
                f'  "shape": "{self.FileName}",',
            ]

        # Output parameter/attribute tables :
        prefix: str = ""
        tables: Dict[str, Tuple[str, ...]]
        if table_name:
            tables = {table_name: self._ParameterNames + self._AttributeNames}
            prefix = "    "
        else:
            tables = {"parameter": self._ParameterNames, "attribute": ()}
            if with_attributes:
                tables["attribute"] += self._AttributeNames + ("Hash",)

        table_key: str
        table_keys: Tuple[str, ...]
        tables_count: int = len(tables)
        for table_key, table_keys in tables.items():
            keys_count: int = len(table_keys)
            close_curly: str = "" if keys_count else "}"
            lines.append(f'{prefix}  "{table_key}": {{{close_curly}')
            index: int
            name: str
            for index, name in enumerate(table_keys):
                # Deal with formatting:
                value: Any = getattr(self, name)
                if isinstance(value, float):
                    value = f'{value}' if table_name else f'{value:.4f} mm'
                elif isinstance(value, str):
                    if table_name:
                        if value.endswith(" mm"):
                            value = f"{float(value[:-3])}"
                        elif value.endswith(" in"):
                            value = f"{float(value[:-3]) * 2.54}"
                        elif value.endswith(" \\u00b0"):
                            value = f"{float(value[:-8])}"
                        else:
                            value = f'"{value}"'
                    else:
                        value = f'"{value}"'

                elif isinstance(value, bool):
                    value = str(value).lower()
                comma = "" if index + 1 == keys_count else ","
                if table_name:
                    name = name[0].lower() + name[1:]  # Make 1st character lower case.
                lines.append(f'{prefix}    "{name}": {value}{comma}')
            comma = "" if index + 1 == tables_count else ","
            if keys_count:
                lines.append(f'{prefix}  }}{comma}')

        # Write *lines* to *file_path*:
        lines.append('}')
        lines.append('')
        return '\n'.join(lines)

    # FabTool.kwargs_json():
    @staticmethod
    def kwargs_from_json(json_text: str) -> Tuple[str, Dict[str, Any]]:
        contents: Any = json.loads(json_text)
        if not isinstance(contents, dict):
            raise RuntimeError("FabTool.from_json(): Bad Json?")
        if "version" not in contents or contents["version"] != 2:
            raise RuntimeError("FabTool.from_json(): Missing or Bad version")
        kwargs: Dict[str, Any] = {}
        kwargs["Name"] = contents["name"]
        shape: str = contents["shape"]
        kwargs["FileName"] = FilePath(shape)
        key_values: Dict[str, Any]
        for key_values in (contents["parameter"], contents["attribute"]):
            assert isinstance(key_values, dict)
            key: str
            value: Any
            for key, value in key_values.items():
                if key not in ("Hash", "Kind"):
                    kwargs[key] = value
        return (shape, kwargs)

    # FabTool.write_json():
    def write_json(self, file_path: FilePath) -> None:
        """Write FabToolTemptlate out to a JSON file."""
        json_file: IO[str]
        with open(file_path, 'w') as json_file:
            json_file.write(self.to_json())

    # FabTool._example_tools():
    @staticmethod
    def _example_tools() -> Dict[str, "FabTool"]:
        """Return example FabTool's."""
        example_tools: Dict[str, FabTool] = {}
        ball_end_tool: FabBallEndTool = FabBallEndTool(
            Name="6mm Ball End",
            FileName=FilePath("ballend.fcstd"),
            CuttingEdgeHeight="40.0000 mm",
            Diameter="6.0000 mm",
            Length="50.0000 mm",
            ShankDiameter="3.0000 mm",
            Material="Carbide",
            ToolHolderHeight="20.000 mm",
            Flutes=8,
        )
        example_tools["6mm_Ball_End"] = ball_end_tool

        bull_nose_tool: FabBullNoseTool = FabBullNoseTool(
            Name="6 mm Bull Nose",
            FileName=FilePath("bullnose.fcstd"),
            CuttingEdgeHeight="40.0000 mm",
            Diameter="6.0000 mm",
            FlatRadius="1.5000 mm",
            Length="50.0000 mm",
            ShankDiameter="3.0000 mm",
            Flutes=8,
            Material="Carbide",
            ToolHolderHeight="20.000 mm",
        )
        example_tools["6mm_Bullnose"] = bull_nose_tool

        chamfer_tool: FabChamferTool = FabChamferTool(
            Name="45 Deg. Chamfer",
            FileName=FilePath("chamfer.fcstd"),
            CuttingEdgeAngle="45.0000 \\u00b0",
            CuttingEdgeHeight="6.3500 mm",
            Diameter="12.3323 mm",
            Length="30.0000 mm",
            ShankDiameter="6.3500 mm",
            TipDiameter="5.0000 mm",
            Material="Carbide",
            ToolHolderHeight="20.000 mm",
            Flutes=8,
        )
        example_tools["45degree_chamfer"] = chamfer_tool

        drill_tool: FabDrillTool = FabDrillTool(
            Name="5mm Drill",
            FileName=FilePath("drill.fcstd"),
            Diameter="5.0000 mm",
            Length="50.0000 mm",
            TipAngle="119.0000 \\u00b0",
            Material="Carbide",
            Flutes=2,
            FlutesLength="30.000mm",
        )
        example_tools["5mm_Drill"] = drill_tool

        end_mill_tool: FabEndMillTool = FabEndMillTool(
            Name="5mm Endmill",
            FileName=FilePath("endmill.fcstd"),
            ToolHolderHeight="20.0000 mm",
            CuttingEdgeHeight="30.0000 mm",
            Diameter="5.0000 mm",
            Length="50.0000 mm",
            ShankDiameter="3.0000 mm",
            Material="Carbide",
            Flutes=2,
        )
        example_tools["5mm_Endmill"] = end_mill_tool

        probe_tool: FabProbeTool = FabProbeTool(
            Name="Probe",
            FileName=FilePath("probe.fcstd"),
            Diameter="6.0000 mm",
            Length="50.0000 mm",
            ShaftDiameter="4.0000 mm",
            ToolHolderHeight="30.0000 mm",
            Material="Carbide",
        )
        example_tools["probe"] = probe_tool

        slitting_saw_tool: FabSlittingSawTool = FabSlittingSawTool(
            Name="Slitting Saw",
            FileName=FilePath("slittingsaw.fcstd"),
            BladeThickness="3.0000 mm",
            CapHeight="3.0000 mm",
            CapDiameter="8.0000 mm",
            Diameter="76.2000 mm",
            Length="50.0000 mm",
            ShankDiameter="19.0500 mm",
            Teeth=80,
            Material="Carbide",
            ToolHolderHeight="30.0000 mm",
        )
        example_tools["slittingsaw"] = slitting_saw_tool

        thread_cutter_tool: FabThreadMill = FabThreadMill(
            Name="5mm-thread-cutter",
            FileName=FilePath("thread-mill.fcstd"),
            Crest="0.10 mm",
            Diameter="5.00 mm",
            Length="50.00 mm",
            NeckDiameter="3.00 mm",
            NeckLength="20.00 mm",
            Material="Carbide",
            ToolHolderHeight="35.00 mm",
            ShankDiameter="5.00 mm",
            Flutes=8,
        )
        example_tools["5mm-thread-cutter"] = thread_cutter_tool

        v_bit_tool: FabVBitTool = FabVBitTool(
            Name="60 Deg. V-Bit",
            FileName=FilePath("v-bit.fcstd"),
            CuttingEdgeAngle="60.0000 \\u00b0",
            Diameter="10.0000 mm",
            CuttingEdgeHeight="1.0000 mm",
            TipDiameter="1.0000 mm",
            Length="20.0000 mm",
            ShankDiameter="5.0000 mm",
            Material="Carbide",
            ToolHolderHeight="20.000 mm",
            Flutes=8,
        )
        example_tools["60degree_Vbit"] = v_bit_tool
        return example_tools

    # FabTool._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Run FabTool unit tests."""

        example_tools: Dict[str, FabTool] = FabTool._example_tools()
        this_directory: FilePath = FilePath(__file__).parent
        bit_directory: FilePath = this_directory / "Tools" / "Bit"
        stem: str
        bit: FabTool
        for stem, bit in example_tools.items():
            bit_file_path: FilePath = bit_directory / f"{stem}.fctb"
            assert bit_file_path.exists(), bit_file_path
            bit_file: IO[str]
            with open(bit_file_path, "r") as bit_file:
                bit_file_contents = bit_file.read()
                if bit_file_contents[-1] != "\n":
                    bit_file_contents += "\n"  # Some files do not end in "\n".
                bit_json: str = bit.to_json(with_attributes=False)
                # There is a bug in the "45degree_chamfer" where a comma is missing on one line
                # when it should be present and vice versa on the text line:
                if stem == "45degree_chamfer":
                    bit_file_contents = bit_file_contents.replace('"6.3500 mm"\n', '"6.3500 mm",\n')
                    bit_file_contents = bit_file_contents.replace('"5.0000 mm",\n', '"5.0000 mm"\n')
                if bit_file_contents != bit_json:
                    print(f"{stem} differences:")
                    file_lines: Tuple[str, ...] = tuple(bit_file_contents.split("\n"))
                    file_size: int = len(file_lines)
                    json_lines: Tuple[str, ...] = tuple(bit_json.split("\n"))
                    json_size: int = len(json_lines)
                    index: int
                    for index in range(max(file_size, json_size)):
                        file_line: str = file_lines[index] if index < file_size else "----"
                        json_line: str = json_lines[index] if index < json_size else "----"
                        if file_line != json_line:
                            print(f" bit_file[{index}]: '{file_line}'")
                            print(f"json_file[{index}]: '{json_line}'")
            bit.write_json(FilePath("/tmp") / f"{stem}.fctb")


# FabBallEndTool:
@dataclass(frozen=True)
class FabBallEndTool(FabTool):
    """FabBallEndTool: An end-mill bit template.

    Required Base Attributes: *Name*, *FileName*.
    Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

    Required FreeCAD Parameter Attributes:
    * *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
    * *Diameter* (Union[str, float]): The end mill cutter diameter.
    * *Length* (Union[str, float]): The total length of the end mill.
    * *ShankDiameter: (Union[str, float]): The shank diameter.

    Extra Keyword Only Attributes:
    * *Flutes*: (int): The number of flutes.

    """

    # Attributes:
    # * Chipload: 0.000mm
    # * Flutes: 0
    # * Material: ("HSS", "Carbide")

    CuttingEdgeHeight: Union[str, float] = cast(str, None)
    Diameter: Union[str, float] = cast(str, None)
    Length: Union[str, float] = cast(str, None)
    ShankDiameter: Union[str, float] = cast(str, None)
    Flutes: int = 0

    # FabBallEndTool.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabBallEndTool."""
        super().__post_init__()
        _ = self._get_attribute("CuttingEdgeHeight", (float, str))
        _ = self._get_attribute("Diameter", (float, str))
        _ = self._get_attribute("Length", (float, str))
        _ = self._get_attribute("ShankDiameter", (float, str))
        _ = self._get_attribute("Flutes", (int,))
        self._extend_parameter_names(("CuttingEdgeHeight", "Diameter", "Length", "ShankDiameter"))
        self._extend_attribute_names(("Flutes",))
        self._set_hash()
        self._set_tool_type("BallEnd")


# FabBullNoseTool:
@dataclass(frozen=True)
class FabBullNoseTool(FabTool):
    """FabBullNose: A bull nose template.

    Required Base Attributes: *Name*, *FileName*.
    Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

    Required FreeCAD Parameter Attributes:
    * *CuttingEdgeHeight* (Union[str, float]): The total length of the cutting edge.
    * *Diameter* (Union[str, float]): The primary diameter
    * *FlatRadius* (Union[str, float]):
      The radius at the flat portion at the bottom where cutters are rounded.
    * *Length* (Union[str, float]): The total length of the bull nose cutter.
    * *ShankDiameter: (Union[str, float]): The shank diameter.

    Extra Keyword Only Attributes:
    * *Flutes*: (int = 0): The number of flutes.

    """
    # Attributes:
    # * Chipload: 0.000mm
    # * Flutes: 0
    # * Material: ("HSS", "Carbide")

    CuttingEdgeHeight: Union[str, float] = cast(str, None)
    Diameter: Union[str, float] = cast(str, None)
    FlatRadius: Union[str, float] = cast(str, None)
    Length: Union[str, float] = cast(str, None)
    ShankDiameter: Union[str, float] = cast(str, None)
    Flutes: int = 0

    # FabBullNoseTool.__post_init__():
    def __post_init__(self) -> None:
        """Initialze the FabCNCEndMill."""
        super().__post_init__()
        _ = self._get_attribute("CuttingEdgeHeight", (str, float))
        _ = self._get_attribute("Diameter", (str, float))
        _ = self._get_attribute("FlatRadius", (str, float))
        _ = self._get_attribute("Length", (str, float))
        _ = self._get_attribute("ShankDiameter", (str, float))
        _ = self._get_attribute("Flutes", (int,))
        self._extend_parameter_names(
            ("CuttingEdgeHeight", "Diameter", "FlatRadius", "Length", "ShankDiameter"))
        self._extend_attribute_names(("Flutes",))
        self._set_hash()
        self._set_tool_type("BullNose")


# FabChamferTool:
@dataclass(frozen=True)
class FabChamferTool(FabTool):
    """FabDrillTool: An drill bit template.

    Required Base Attributes: *Name*, *FileName*.
    Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

    Required FreeCAD Parameter Attributes:
    * *CuttingEdgeHeight* (Union[str, float]): The cutting edge edge height.
    * *Diameter* (Union[str, float]): The widest diameter.
    * *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle in degrees.
    * *Length* (Union[str, float]): The total length of the chamfer bit.
    * *ShankDiameter*: (Union[str, float]): The shank diameter.
    * *TipDiameter*: (Union[str, float]): The diameter at the "tip".

    Extra Keyword Only Attributes:
    * *Flutes*: (int = 0): The number of flutes.

    """
    CuttingEdgeAngle: Union[str, float] = cast(str, None)
    CuttingEdgeHeight: Union[str, float] = cast(str, None)
    Diameter: Union[str, float] = cast(str, None)
    Length: Union[str, float] = cast(str, None)
    ShankDiameter: Union[str, float] = cast(str, None)
    TipDiameter: Union[str, float] = cast(str, None)
    Flutes: int = 0

    # Attributes:
    # * Chipload: 0.000mm
    # * Flutes: 0
    # * Material: ("HSS", "Carbide")

    # FabChamferTool.__post_init__():
    def __post_init__(self) -> None:
        """Initialze the FabChamferTool."""
        super().__post_init__()
        _ = self._get_attribute("CuttingEdgeAngle", (str, float,))
        _ = self._get_attribute("CuttingEdgeHeight", (str, float,))
        _ = self._get_attribute("Diameter", (str, float))
        _ = self._get_attribute("Length", (str, float))
        _ = self._get_attribute("ShankDiameter", (str, float))
        _ = self._get_attribute("TipDiameter", (str, float))
        _ = self._get_attribute("Flutes", (int,))
        self._extend_parameter_names(
            ("CuttingEdgeAngle", "CuttingEdgeHeight", "Diameter", "Length",
             "ShankDiameter", "TipDiameter"))
        self._extend_attribute_names(("Flutes",))
        self._set_hash()
        self._set_tool_type("ChamferMill")


# FabDrillTool:
@dataclass(frozen=True)
class FabDrillTool(FabTool):
    """FabDrillTool: An drill bit template.

    Required Base Attributes: *Name*, *FileName*.
    Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

    Required FreeCAD Parameter Attributes:
    * *Diameter* (Union[str, float]): The end mill cutter diameter.
    * *Length* (Union[str, float]): The total length of the end mill.
    * *TipAngle: (Union[str, float]): The shank diameter.

    Extra Keyword Only Attributes:
    * *Flutes*: (int = 0): The number of flutes.
    * *FlutesLength* (Union[str, float] = 0.0): The drill flutes length (i.e. maximum drill depth).
    * *SplitPoint* (bool = False): True if self-centering split points are present.

    """
    Diameter: Union[str, float] = cast(str, None)
    Length: Union[str, float] = cast(str, None)
    TipAngle: Union[str, float] = cast(str, None)
    Flutes: int = 0
    FlutesLength: Union[str, float] = -1.0
    SplitPoint: bool = False

    # Attributes:
    # * Chipload: 0.0000 mm
    # * Flutes: 0
    # * Material: ("HSS","Carbide")

    # FabDrillTool.__post_init__():
    def __post_init__(self) -> None:
        """Initialze the FabCNCEndMill."""
        super().__post_init__()
        _ = self._get_attribute("Diameter", (str, float))
        _ = self._get_attribute("Length", (str, float))
        _ = self._get_attribute("TipAngle", (str, float))
        _ = self._get_attribute("Flutes", (int,))
        _ = self._get_attribute("FlutesLength", (str, float,))
        _ = self._get_attribute("SplitPoint", (bool,))
        self._extend_parameter_names(("Diameter", "Length", "TipAngle"))
        self._extend_attribute_names(("Flutes", "FlutesLength", "SplitPoint"))
        self._set_hash()
        self._set_tool_type("Drill")


# FabEndMillTool:
@dataclass(frozen=True)
class FabEndMillTool(FabTool):
    """FabEndMillTool: An end-mill bit template.

    Required Base Attributes: *Name*, *FileName*.
    Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

    Required FreeCAD Parameter Attributes:
    * *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
    * *Diameter* (Union[str, float]): The end mill cutter diameter.
    * *Length* (Union[str, float]): The total length of the end mill.
    * *ShankDiameter: (Union[str, float]): The shank diameter.

    Extra Keyword Only Attributes:
    * *Flutes*: (int): The number of flutes.

    """

    CuttingEdgeHeight: Union[str, float] = cast(str, None)
    Diameter: Union[str, float] = cast(str, None)
    Length: Union[str, float] = cast(str, None)
    ShankDiameter: Union[str, float] = cast(str, None)
    Flutes: int = 0

    # FabEndMillTool.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabEndMillTool."""
        super().__post_init__()
        _ = self._get_attribute("CuttingEdgeHeight", (float, str))
        _ = self._get_attribute("Diameter", (float, str))
        _ = self._get_attribute("Length", (float, str))
        _ = self._get_attribute("ShankDiameter", (float, str))
        _ = self._get_attribute("Flutes", (int,))
        self._extend_parameter_names(("CuttingEdgeHeight", "Diameter", "Length", "ShankDiameter"))
        self._extend_attribute_names(("Flutes",))
        self._set_hash()
        self._set_tool_type("EndMill")


# FabProbeTool:
@dataclass(frozen=True)
class FabProbeTool(FabTool):
    """FabProbeTool: A touch off probe.

    Required Base Attributes: *Name*, *FileName*.
    Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

    Required FreeCAD Parameter Attributes:
    * *Diameter* (Union[str, float]): The end mill cutter diameter.
    * *Length* (Union[str, float]): The total length of the end mill.
    * *ShaftDiameter: (Union[str, float]): The shaft diameter.

    """

    Diameter: Union[str, float] = cast(str, None)
    Length: Union[str, float] = cast(str, None)
    ShaftDiameter: Union[str, float] = cast(str, None)

    # Attributes:
    # * SpindlePower: False

    # FabProbeTool.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabProbeTool."""
        super().__post_init__()
        _ = self._get_attribute("Diameter", (float, str))
        _ = self._get_attribute("Length", (float, str))
        _ = self._get_attribute("ShaftDiameter", (float, str))
        self._extend_parameter_names(("Diameter", "Length", "ShaftDiameter"))
        self._set_hash()
        self._set_tool_type("Probe")


# FabSlittingSawTool:
@dataclass(frozen=True)
class FabSlittingSawTool(FabTool):
    """FabSlittingSawTool: An slitting saw bit.

    Required Base Attributes: *Name*, *FileName*.
    Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

    Required FreeCAD Parameter Attributes:
    * *BladeThickness* (Union[str, float]): The blade thickness.
    * *CapHeight* (Union[str, float]): The screw cap height.
    * *CapDiameter* (Union[str, float]): The screw cap diameter.
    * *Diameter* (Union[str, float]): The blade diameter.
    * *Length* (Union[str, float]): The over tool length.
    * *ShankDiameter* (Union[str, float]): The diameter of the shank above the blade.

    Extra Keyword Only Attributes:
    * *Teeth*: (int = 0): The of teeth on the saw blade.

    """
    BladeThickness: Union[str, float] = cast(str, None)
    CapHeight: Union[str, float] = cast(str, None)
    CapDiameter: Union[str, float] = cast(str, None)
    Diameter: Union[str, float] = cast(str, None)
    Length: Union[str, float] = cast(str, None)
    ShankDiameter: Union[str, float] = cast(str, None)
    Teeth: int = 0

    # Attributes:
    # * Chipload: 0.000mm
    # * Flutes: 0
    # * Material: ("HSS", "Carbide")

    # FabSlittingSawTool.__post_init__():
    def __post_init__(self) -> None:
        """Initialze the FabSlittingSawTool."""
        super().__post_init__()
        _ = self._get_attribute("BladeThickness", (str, float))
        _ = self._get_attribute("CapHeight", (str, float))
        _ = self._get_attribute("CapDiameter", (str, float))
        _ = self._get_attribute("Diameter", (str, float))
        _ = self._get_attribute("Length", (str, float))
        _ = self._get_attribute("ShankDiameter", (str, float))
        _ = self._get_attribute("Teeth", (int,))
        self._extend_parameter_names(
            ("BladeThickness", "CapHeight", "CapDiameter", "Diameter", "Length", "ShankDiameter"))
        self._extend_attribute_names(("Teeth",))
        self._set_hash()
        self._set_tool_type("SlittingSaw")


# FabThreadMill:
@dataclass(frozen=True)
class FabThreadMill(FabTool):
    """FabThreadMill: An thread cutter bit.

    Required Base Attributes: *Name*, *FileName*.
    Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

    Required FreeCAD Parameter Attributes:
    * *Crest* (Union[str, float]): The height of the cutting disk.
    * *Diameter* (Union[str, float]): The diameter of the cutting disk.
    * *Length* (Union[str, float]): The over tool length.
    * *NeckDiameter* (Union[str, float]): The diameter of the neck poartion above the cutting disk.
    * *NeckLength* (Union[str, float]): The length of the neck portion above the cutting disk.
    * *ShankDiameter* (Union[str, float]): The diameter of the shank above the Disk.

    Extra Keyword Only Attributes:
    * *Flutes*: (int = 0): The number of flutes.

    """
    Crest: Union[str, float] = cast(str, None)
    Diameter: Union[str, float] = cast(str, None)
    Length: Union[str, float] = cast(str, None)
    NeckDiameter: Union[str, float] = cast(str, None)
    NeckLength: Union[str, float] = cast(str, None)
    ShankDiameter: Union[str, float] = cast(str, None)
    Flutes: int = 0

    # FabThreadMill.__post_init__():
    def __post_init__(self) -> None:
        """Initialze the FabThreadCutter."""
        super().__post_init__()
        _ = self._get_attribute("Crest", (str, float))
        _ = self._get_attribute("Diameter", (str, float))
        _ = self._get_attribute("Length", (str, float))
        _ = self._get_attribute("NeckDiameter", (str, float))
        _ = self._get_attribute("NeckLength", (str, float,))
        _ = self._get_attribute("ShankDiameter", (str, float))
        _ = self._get_attribute("Flutes", (int,))
        self._extend_parameter_names(
            ("Crest", "Diameter", "Length", "NeckDiameter", "NeckLength", "ShankDiameter"))
        self._extend_attribute_names(("Flutes",))
        self._set_hash()
        self._set_tool_type("ThreadCutter")


# FabVBitTool:
@dataclass(frozen=True)
class FabVBitTool(FabTool):
    """FabVBitTool: An V bit template.

    Required Base Attributes: *Name*, *FileName*.
    Keyword Only Base Attributes: *Material*, *ToolHolderHeight*, *VendorName*, *VendorPartNumber*.

    Required FreeCAD Parameter Attributes:
    * *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle in degrees.
    * *Diameter* (Union[str, float]): The widest diameter.
    * *CuttingEdgeHeight* (Union[str, float]): The cutting edge edge height.
    * *TipDiameter*: (Union[str, float]): The diameter at the "tip".
    * *Length* (Union[str, float]): The total length of the chamfer bit.
    * *ShankDiameter*: (Union[str, float]): The shank diameter.

    Extra Keyword Only Attributes:
    * *Flutes*: (int = 0): The number of flutes.

    """
    # Attributes:
    # * Chipload: 0.000mm
    # * Flutes: 0
    # * Material: ("HSS", "Carbide")

    CuttingEdgeAngle: Union[str, float] = cast(str, None)
    Diameter: Union[str, float] = cast(str, None)
    CuttingEdgeHeight: Union[str, float] = cast(str, None)
    TipDiameter: Union[str, float] = cast(str, None)
    Length: Union[str, float] = cast(str, None)
    ShankDiameter: Union[str, float] = cast(str, None)
    Flutes: int = 0

    # FabVBitTool.__post_init__():
    def __post_init__(self) -> None:
        """Initialze the FabVBitTool."""
        super().__post_init__()
        _ = self._get_attribute("CuttingEdgeAngle", (str, float,))
        _ = self._get_attribute("Diameter", (str, float))
        _ = self._get_attribute("CuttingEdgeHeight", (str, float,))
        _ = self._get_attribute("TipDiameter", (str, float))
        _ = self._get_attribute("Length", (str, float))
        _ = self._get_attribute("ShankDiameter", (str, float))
        _ = self._get_attribute("Flutes", (int,))
        self._extend_parameter_names(
            ("CuttingEdgeAngle", "Diameter", "CuttingEdgeHeight", "TipDiameter", "Length",
             "ShankDiameter"))
        self._extend_attribute_names(("Material", "VendorName", "VendorPartNumber", "Flutes"))
        self._set_hash()
        self._set_tool_type("VTool")


# FabTools
@dataclass
class FabTools(object):
    """FabTools: A collection of related FabTool's.

    Attributes:
    * *Name* (str): The Tooltable name.
    * *Description* (str): A brief description of the tool table/library.

    In FreeCAD there is currently two very related concepts.  There is a tool table
    and a tool library.  A tool table is the JSON file that FreeCAD Path GUI can import
    and export.  This file has all of the information for each tool embedded inside.
    The new tool library is JSON file that just has a number and a reference to a "bit" JSON file.
    This class can deal with both.

    """

    Name: str
    Description: str
    _Table: Dict[int, FabTool] = field(init=False, repr=False)

    # FabTools.__post_init__():
    def __post_init__(self) -> None:
        """Initialize a FabTools."""
        if not isinstance(self.Name, str):
            raise RuntimeError("FabTools.__post_init__(): "
                               f"Name {self.Name} is {type(self.Name)}, not str")
        if not isinstance(self.Description, str):
            raise RuntimeError("FabTools.__post_init__(): Description "
                               f"{self.Description} is {type(self.Description)}, not str")
        self._Table: Dict[int, FabTool] = {}

    # FabTools.add_tool():
    def add_tool(self, tool_number: int, tool: FabTool) -> None:
        """Add a FabTool to FabTools."""

        if tool_number <= 0:
            raise RuntimeError("FabTools.add_tool(): Tool number {{tool_number} is not positive")
        if tool_number in self._Table:
            raise RuntimeError("FabTools.add_tool(): Tool number {{tool_number} is in use")
        if not isinstance(tool, FabTool):
            raise RuntimeError("FabTools.add_tool(): Tool {{tool} is {type(tool)}, not FabTool")
        self._Table[tool_number] = tool

    # FabTools.add_tools():
    def add_tools(self, tools: Dict[int, FabTool]) -> None:
        """Add a some FabTool's to a FabTools."""
        tool_number: int
        tool: FabTool
        for tool_number, tool in tools.items():
            self.add_tool(tool_number, tool)

    # FabTools.__get_item__():
    def __get_item__(self, tool_number) -> FabTool:
        """Return the FabTools based on tool number."""
        if tool_number not in self._Table:
            raise IndexError("FabTools.__post_init__(): "
                             f"Tool number {tool_number} is not present")
        return self._Table[tool_number]

    # FabTools.tool_from_json():
    @staticmethod
    def tool_from_json(json_text: str) -> FabTool:
        """Return FabTool parsed from JSON."""
        shape: str
        kwargs: Dict[str, Any]
        shape, kwargs = FabTool.kwargs_from_json(json_text)
        tool: FabTool
        if shape == "ballend.fcstd":
            tool = FabBallEndTool(**kwargs)
        elif shape == "bullnose.fcstd":
            tool = FabBullNoseTool(**kwargs)
        elif shape == "chamfer.fcstd":
            tool = FabChamferTool(**kwargs)
        elif shape == "drill.fcstd":
            tool = FabDrillTool(**kwargs)
        elif shape == "endmill.fcstd":
            tool = FabEndMillTool(**kwargs)
        elif shape == "probe.fcstd":
            tool = FabProbeTool(**kwargs)
        elif shape == "slittingsaw.fcstd":
            tool = FabSlittingSawTool(**kwargs)
        elif shape == "thread-mill.fcstd":
            tool = FabThreadMill(**kwargs)
        elif shape == "v-bit.fcstd":
            tool = FabVBitTool(**kwargs)
        else:
            raise RuntimeError(f"FabTools.tool_from_json(): Unrecognized bit shape '{shape}'")
        return tool

    # FabTools.to_library_json():
    def to_library_json(self, with_hash: bool) -> None:
        """Convert FabToolTable to JSON."""
        lines: List[str] = ["{"]
        table: Dict[int, FabTool] = self._Table
        tool_numbers: Tuple[int, ...] = tuple(sorted(table.keys()))
        tool_number: int
        for tool_number in tool_numbers:
            bit: FabTool = table[tool_number]
            lines.extend([
                '{',
                f'"nr": {tool_number}',
                f'"path": "{bit.FileName}"',
            ])
            if with_hash:
                lines.append(f'"hash": "{bit.Hash}"')
            lines.append('},')
        lines.extend([
            "  version: 1,",
            "}",
            "",
        ])

    # FabTools.combined_to_json():
    def combined_to_json(self, table_name: str) -> str:
        """Return the JSON of a combined tool table JASON file."""
        lines: List[str] = [
            '[',
            '  {',
            f'    "TableName": "{table_name}",',
            '    "Tools": {,',
        ]

        table: Dict[int, FabTool] = self._Table
        sorted_tool_numbers: Tuple[int, ...] = tuple(sorted(table.keys()))
        tool_number: int
        for tool_number in sorted_tool_numbers:
            bit: FabTool = table[tool_number]
            json: str = bit.to_json(with_attributes=True, table_name=f"{tool_number}")
            lines.extend(json.split("\n"))

        lines.extend([
            '    },',
            '    "Version": 1',
            '  }',
            ']',
            '',
        ])
        return "\n".join(lines)

    # FabTools.from_library_json():
    @staticmethod
    def from_json(json_text: str, file_name: FilePath,
                  bit_directories: Tuple[FilePath, ...]) -> "FabTools":
        """Returns a FabTools decoded from JSON."""
        # Assume that *contents* is properly specified:
        contents: Any = json.loads(json_text)
        version: Any = contents["version"]
        if not version == 1:
            raise RuntimeError(f"FabToolTable.from_json(): {version} is not 1")

        # Create the empty *tools* FabTools:
        name = cast(str, contents["Name"] if "Name" in contents else "")
        description = cast(str, contents["Description"] if "Description" in contents else "")
        tools: FabTools = FabTools(name, description)
        _ = tools

        tools_list = cast(List[Dict[str, Any]], contents["tools"])
        numbered_tools: List[Tuple[int, FabTool]] = []
        tool_dict: Dict[str, Any] = {}
        tools_dict: Dict[int, FabTool] = {}
        for tool_dict in tools_list:
            tool_number = cast(int, tool_dict["nr"])
            path = cast(str, tool_dict["path"])
            hash = cast(str, tool_dict["hash"] if "hash" in tool_dict else "")
            _ = hash

            # Attempt to read in the tool JSON:
            bit_json: str
            bit_directory: FilePath
            for bit_directory in bit_directories:
                json_file_path: FilePath = bit_directory / path
                if json_file_path.exists():
                    json_file: IO[str]
                    with open(json_file_path, "r") as json_file:
                        bit_json = json_file.read()
                    break
            else:
                raise RuntimeError("FabToolTable.from_json(): "
                                   f"Could not find {path} in {bit_directories}")

            tool: FabTool = FabTools.tool_from_json(bit_json)
            tools_dict[tool_number] = tool
            numbered_tools.append((tool_number, tool))

        fab_tools: FabTools = FabTools(name, description)
        fab_tools.add_tools(tools_dict)
        return fab_tools

    # FabTools._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Run FabTools unit tests."""
        this_directory: FilePath = FilePath(__file__).parent
        tools_directory: FilePath = this_directory / "Tools"
        bit_directory: FilePath = tools_directory / "Bit"
        _ = bit_directory
        library_directory: FilePath = tools_directory / "Library"
        shape_directory: FilePath = tools_directory / "Shape"
        _ = shape_directory
        # TODO: use *tools_directory*, *bit_directory*, and *shape_directory*.

        library_file_path: FilePath = library_directory / "Default.fctl"
        json_file: IO[str]
        json_text: str
        with open(library_file_path, "r") as json_file:
            json_text = json_file.read()

        example_tools: Dict[str, FabTool] = FabTool._example_tools()

        tools: FabTools = FabTools(Name="MyToolTable", Description="")

        tool: FabTool
        tool_number: int = 0
        name: str
        for name, tool in example_tools.items():
            tool_number += 1
            tools.add_tool(tool_number, tool)

        my_tool_table_path: FilePath = FilePath(".") / "MyToolTable.json"
        with open(my_tool_table_path, "w") as json_file:
            json_text = tools.combined_to_json("MyToolTable")
            json_file.write(json_text)


# FabSpindle:
@dataclass(frozen=True)
class FabSpindle(object):
    """FabSpindle: Represents a machine tool spindle.

    Attributes:
    * *Type* (str): Spindle Type (e.g. "R8", "Cat40", etc.)
    * *Speed* (int): Maximum spindle speed in rotations per minute.
    * *Reversable* (bool): True if spindle can be reversed.
    * *FloodCooling* (bool): True if flood cooling is available.
    * *MistCooling* (bool): True if mist coooling is available.

    Constructor:
    * FabSpindle("Type", Speed, Reversable, FloodCooling, MistCooling)

    """

    Type: str
    Speed: int
    Reversable: bool
    FloodCooling: bool
    MistCooling: bool

    # FabSpindle.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing the FabSpindle."""
        check_type("FabSpindle.Type", self.Type, str)
        check_type("FabSpindle.Speed", self.Speed, int)
        check_type("FabSpindle.Reversable", self.Reversable, bool)
        check_type("FabSpindle.FloodCooling", self.FloodCooling, bool)
        check_type("FabSpindle.MistCooling", self.MistCooling, bool)

    # FabSpindle._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Perform FabSpindle unit tests."""

        spindle: FabSpindle = FabSpindle("R8", 5000, True, True, False)
        assert spindle.Type == "R8", spindle.Type
        assert spindle.Speed == 5000, spindle.Speed
        assert spindle.Reversable, spindle.Reversable
        assert spindle.FloodCooling, spindle.FloodCooling
        assert not spindle.MistCooling, spindle.MistCooling


# FabTable:
@dataclass(frozen=True)
class FabTable(object):
    """FabTable: Represents a CNC table.

    Attributes:
    * *Name* (str): The table name.
    * *Length* (float): The overall table length in millimeters.
    * *Width* (float): The overall table width in millimieters.
    * *Height* (float): The overall table Height in millimeters.
    * *Slots* (int): The number of T slots.
    * *SlotWidth* (float): The top slot width in millimeters.
    * *SlotDepth* (float): The overall slot depth from top to keyway bottom in millimeters.
    * *KeywayWidth* (float): The keyway width in millimeters.
    * *KeywayHeight* (float): The keyway height in millimeters.

    Constructor:
    *  FabTable("Name", Length, Width, Height, Slots,
       SlotWidth, SlotDepth, KeywayWidth, KeywayHeight)

    """

    Name: str
    Length: float
    Width: float
    Height: float
    Slots: int
    SlotPitch: float
    SlotWidth: float
    SlotDepth: float
    KeywayWidth: float
    KeywayHeight: float

    # FabTable.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabTable."""
        check_type("FabTable.Name", self.Name, str)
        check_type("FabTable.Length", self.Length, float)
        check_type("FabTable.Width", self.Width, float)
        check_type("FabTable.Height", self.Height, float)
        check_type("FabTable.Slots", self.Slots, int)
        check_type("FabTable.SlotsPitch", self.SlotPitch, float)
        check_type("FabTable.SlotWidth", self.SlotWidth, float)
        check_type("FabTable.SlotDepth", self.SlotDepth, float)
        check_type("FabTable.KeywayWidth", self.KeywayWidth, float)
        check_type("FabTable.KeywayHeight", self.KeywayHeight, float)

    # FabTable._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Perform unit tests on FabTable."""
        table: FabTable = FabTable("TestTable", 100.0, 50.0, 30.0, 4, 10.0, 5.0, 5.0, 10.0, 5.0)
        assert table.Name == "TestTable", table.Name
        assert table.Length == 100.0, table.Length
        assert table.Width == 50.0, table.Width
        assert table.Height == 30.0, table.Height
        assert table.Slots == 4, table.Slots
        assert table.SlotWidth == 5.0, table.SlotWidth
        assert table.SlotDepth == 5.0, table.SlotDepth
        assert table.KeywayWidth == 10.0, table.KeywayWidth
        assert table.KeywayHeight == 5.0, table.KeywayHeight


# FabController:
@dataclass(frozen=True)
class FabController(object):
    """FabController: Specifies a CNC controller.

    Attributes:
    * *Name* (str): The controller name.
    * *PostProcessor* (str): The post processor to use.

    Constructor:
    * FabController("Name", PostProcessor)

    """

    Name: str
    PostProcessor: str

    # FabController.__post_process__():
    def __post_process__(self) -> None:
        """Finish initializing FabController."""
        check_type("FabController.Name", self.Name, str)
        check_type("FabController.PostProcessor", self.PostProcessor, str)

    # FabController._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Perform FabController Unit Tests."""
        controller: FabController = FabController("MyMill", "linuxcnc")
        assert controller.Name == "MyMill", controller.Name
        assert controller.PostProcessor == "linuxcnc", controller.PostProcessor


# FabMachine:
@dataclass(frozen=True)
class FabMachine(object):
    """FabMachine: Base class for a FabShop machine.

    Attributes:
    * *Name* (str): The name of the  machines.
    * *Placement* (str): The machine placement in the shop.
    * *Kind* (str): The machine kind (supplied by sub-class).

    Constructor:
    * Fabmachine("Name", "Placement")

    """

    Name: str
    Placement: str

    # FabMachine.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabMachine."""
        check_type("FabMachine.Name", self.Name, str)
        check_type("FabMachine.Placement", self.Placement, str)

    # FabMachine.Kind():
    @property
    def Kind(self) -> str:
        """Return the FabMachine kind."""
        raise NotImplementedError(f"{type(self)}.Kind() is not implemented.")

    # FabMachine._unit_tests():
    @staticmethod
    def _unit_tests() -> None:
        """Perform FabMachine unit tests."""
        machine: FabMachine = FabMachine("TestMachine", "Test Placement")
        assert machine.Name == "TestMachine", machine.Name
        assert machine.Placement == "Test Placement", machine.Placement


# FabCNC:
@dataclass(frozen=True)
class FabCNC(FabMachine):
    """FabCNC: Represents a CNC mill or router.

    Attributes:
    * *Name* (str): The CNC mill name.
    * *Placement* (str): The placement in the shop.
    * *WorkVolume* (Vector): The work volume DX/DY/DZ.
    * *Table* (FabTable):
    * *Spindle* (FabSpindle): The spindle description.
    * *Controller* (FabController): The Controller used by the CNC machine.

    Contstructor:
    * FabCNC("Name", "Position", WorkVolume, Spindle, Table, Controller)

    """

    _WorkVolume: Vector
    _Spindle: FabSpindle
    _Table: FabTable
    _Controller: FabController

    # FabCNC.__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabCNCMill."""
        super().__post_init__()
        check_type("FabCNC.WorkVolume", self._WorkVolume, Vector)
        check_type("FabCNC.Spindle", self._Spindle, FabSpindle)
        check_type("FabCNC.Table", self._Table, FabTable)
        check_type("FabCNC.Controller", self._Controller, FabController)


# FabCNCMill:
@dataclass(frozen=True)
class FabCNCMill(FabCNC):
    """FabCNCMill: Represents a CNC mill.

    Attributes:
    * *Name* (str): The CNC mill name.
    * *Placement* (str): The placement in the shop.
    * *WorkVolume* (Vector): The work volume DX/DY/DZ.
    * *Table* (FabTable):
    * *Spindle* (FabSpindle): The spindle description.
    * *Controller* (FabController): The Controller used by the CNC machine.
    * *Kind* (str): Return the string "CNCMill".

    Contstructor:
    * FabCNCMill("Name", "Position", WorkVolume, Spindle, Table, Spindle, Controller)

    """

    # FabCNCMill.__post_init__():
    def __post_init__(self) -> None:
        """Finish Initializing FabCNCMill."""
        super().__post_init__()

    # FabCNCMill.Kind():
    @property
    def Kind(self) -> str:
        """Return the FabCNCMill kind."""
        return "CNC_Mill"


# FabCNCRouter:
@dataclass(frozen=True)
class FabCNCRouter(FabCNC):
    """FabCNCRouter: Represents a CNC Router.

    Attributes:
    * *Name* (str): The CNC mill name.
    * *Position* (str): The position in the shop.
    * *WorkVolume* (Vector): The work volume DX/DY/DZ.
    * *Table* (FabTable):
    * *Spindle* (FabSpindle): The spindle description.
    * *Controller* (FabController): The Controller used by the CNC machine.
    * *Kind* (str): Return the string "CNCRouter".

    Contstructor:
    * FabCNCRouter("Name", "Position", WorkVolume, Spindle, Table, Spindle, Controller)

    """

    # FabCNCRouter.Kind():
    @property
    def Kind(self) -> str:
        """Return the FabCNCRouter kind."""
        return "CNCRouter"


# FabLocation:
@dataclass(frozen=True)
class FabLocation(object):
    """FabLocation: Location information for a shop.

    The shop can be located with as much or as little specificity and the shop owner chooses.
    Sometimes the Shop is on a mobile platform (like a boat) and no location makes much sense.

    Attributes:
    * *CountryCode* (str):
      The two letter country code of the country the shop is located in.  (Default: "")
    * *StateProvince* (str):
      The state or province the shop is located in. (Default: "")
    * *County* (str):
      The county/canton/whatever that the shop is located in.  (Default: "")
    * *City* (str):
      The city the shop is located in.  (Default: "")
    * *StreetAddress* (str):
      The street address of the shop. (Default: "")
    * *Unit* (str):
      The unit within the building that contains the shop. (Default: "")
    * *ZipCode* (str):
      The postal Zip Code that contains the shop. (Default: "")
    * *Latitude* (str):
      The shop latitude. (Default: "")
    * *Longitude* (str):
      The shop longitude. (Default: "")
    * *PhoneNumber* (str):
      The shop phone number. (Default: "")
    * *URL* (str):
      The shop Web URL. (Default: "")

    Constructor (use Keywords):
    * FabLocation(CountryCode="...", StateProvince="...", County="...", City="...",
      StreetAddress="...", Unit="...", ZipCode="...", Latitude="...", Longitude="...",
      PhoneNumber="...", URL="...)

    """

    CountryCode: str = ""
    StateProvince: str = ""
    County: str = ""
    City: str = ""
    StreetAddress: str = ""
    Unit: str = ""
    ZipCode: str = ""
    Latitude: str = ""
    Longitude: str = ""
    PhoneNumber: str = ""
    URL: str = ""


# FabShop:
@dataclass
class FabShop(object):
    """FabShop: Describes Machines/Tool in a Shop.

    Attributes:
    * *Name* (str): The Shop Name.
    * *Location* (FabLocation): The shop location.
    * *Machines* (Tuple[FabMachine, ...]):
      The machines within the shop.  The machines must have unique names within the shop.

    Constructor  :
    * FabShop(Name="Name", Location=FabLocation(...), Machines=(...,))

    """

    _Name: str
    _Location: FabLocation
    _Machines: Tuple[FabMachine, ...]
    _MachinesTable: Dict[str, FabMachine] = field(init=False, repr=False)

    # FabShop:__post_init__():
    def __post_init__(self) -> None:
        """Finish initializing FabShop."""
        check_type("FabShop.Name", self._Name, str)
        check_type("FabShop.Location", self._Location, FabLocation)
        check_type("FabShop.Machines", self._Machines, Tuple[FabMachine, ...])
        machines_table: Dict[str, FabMachine] = {}
        machine: FabMachine
        for machine in self._Machines:
            machine_name: str = machine.Name
            if machine_name in machines_table:
                raise ValueError("Machine {machine_name} occurs more than once.")
            machines_table[machine_name] = machine
        self._MachinesTable = machines_table

    # FabShop.Name():
    @property
    def Name(self) -> str:
        """Return FabShop name."""
        return self._Name

    # FabShop.Location():
    @property
    def Location(self) -> FabLocation:
        """Return FabShop location."""
        return self._Location

    # FabShop.Machines():
    @property
    def Machines(self) -> Tuple[FabMachine, ...]:
        """Return FabShop machines."""
        return self._Machines

    # FabShop.lookup():
    def lookup(self, machine_name: str) -> FabMachine:
        """Return the named FabMachine."""
        assert check_argument_types()
        if machine_name not in self._MachinesTable:
            raise KeyError(
                f"Machine {machine_name} is not one of {sorted(self._MachinesTable.keys())}")
        return self._MachinesTable[machine_name]

    # FabShop._unit_tests()
    @staticmethod
    def _unit_tests() -> None:
        """Perform FabShop unit tests."""
        name: str = "MyShop"
        location: FabLocation = FabLocation(
            CountryCode="US", StateProvince="California", City="Sunnyvale", ZipCode="94086")
        placement: str = "somewhere in shop"
        table: FabTable = FabTable("TestTable", 100.0, 50.0, 30.0, 4, 10.0, 5.0, 5.0, 10.0, 5.0)
        work_volume: Vector = Vector(100.0, 50.0, 40.0)
        spindle: FabSpindle = FabSpindle("R8", 5000, True, True, False)
        controller: FabController = FabController("MyMill", "linuxcnc")
        cnc_mill: FabCNCMill = FabCNCMill(
            "MyCNCMill", placement, work_volume, spindle, table, controller)
        machines: Tuple[FabMachine, ...] = (cnc_mill,)
        shop: FabShop = FabShop("MyShop", location, machines)
        assert shop.Name == name, shop.Name
        assert shop.Location == location, shop.Location
        assert shop.Machines == machines

        # Test lookup():
        try:
            shop.lookup("BadMachine")
            assert False
        except KeyError as key_error:
            want: str = "\"Machine BadMachine is not one of ['MyCNCMill']\""
            got: str = str(key_error)
            assert want == got, f"\n{want} !=\n{got}"
        assert shop.lookup("MyCNCMill") is cnc_mill


# Main program:
def main() -> None:
    FabSpindle._unit_tests()
    FabTable._unit_tests()
    FabController._unit_tests()
    FabTool._unit_tests()
    FabTools._unit_tests()
    FabMachine._unit_tests()
    FabCNC._unit_tests()
    FabShop._unit_tests()


if __name__ == "__main__":
    main()
