#!/usr/bin/env python3
"""ApexPath: Apex interface to FreeCAD Path workbench."""

# <--------------------------------------- 100 characters ---------------------------------------> #


import sys
sys.path.append(".")
import Embed
Embed.setup()

import FreeCAD as App  # type: ignore
import FreeCADGui as Gui  # type: ignore
from typing import Any, cast, Dict, IO, List, Optional, Tuple, Union
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


# FabBitTemplate:
@dataclass(frozen=True)
class FabBitTemplate(object):
    """FabCNCShape: Base class for CNC tool bit templates.

    Required Base Attributes:
    * *Name* (str): The name of the tool template.
    * *FileName* (pathlib.Path): The tool template file name (must have a suffix of`.fcstd` file)

    Keyword Only Base Attributes:
    * *Material: (Tuple[str, ...] = ()):
      The tool material as a tulple from generic to specific
      (e.g. `Material=("steel", "HSS", "Cobalt")`.)
    * *ToolHolderHeight: (Union[None, str, float] = None):
      The distance from tool tip to the base of the tool holder.

    """

    Name: str
    FileName: Path
    Material: Tuple[str, ...] = field(default=())
    ToolHolderHeight: Union[None, float, str] = field(default="-1.0 mm")
    VendorName: str = field(default="")
    VendorPartNumber: str = field(default="")
    _ParameterNames: Tuple[str, ...] = field(init=False, repr=False, default=())
    _AttributeNames: Tuple[str, ...] = field(init=False, repr=False, default=())
    Hash: str = field(init=False, repr=False, default="")

    # FabBitTemplate.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabCNCTemplate."""
        # name = cast(str, self._get_attribute("Name", (str,)))
        file_name = cast(Path, self._get_attribute("FileName", (Path,)))
        material: Tuple[Any, ...] = self._get_attribute("Material", (tuple,))
        _ = self._get_attribute("ToolHolderHeight", (type(None), float, str))
        _ = self._get_attribute("VendorName", (str,))
        _ = self._get_attribute("VendorPartNumber", (str,))

        if file_name.suffix != ".fcstd":
            raise RuntimeError(
                "FabBitTemplate.__post_init__(): "
                f"Filename '{file_name}' suffix is '{self.FileName.suffix}', not '.fcstd'")

        sub_material: Any
        for sub_material in material:
            if not isinstance(sub_material, str):
                raise RuntimeError(
                    "FabBitTemplate.__post_init__(): "
                    f"Sub-material {sub_material} is type {type(sub_material)}, not str.")

        self._extend_attribute_names(
            ("Material", "ToolHolderHeight", "VendorName", "VendorPartNumber"))

    # FabBitTemplate._extend_parameter_names():
    def _extend_parameter_names(self, parameter_names: Tuple[str, ...]) -> None:
        """Extend the FabBitTemplate parameters."""
        # Needed to initialize update fields in frozen objects.
        object.__setattr__(self, "_ParameterNames", self._ParameterNames + parameter_names)

    # FabBitTemplate._extend_attribute_names():
    def _extend_attribute_names(self, attribute_names: Tuple[str, ...]) -> None:
        """Extend the FabBitTemplate parameters."""
        # Needed to initialize update fields in frozen objects.
        object.__setattr__(self, "_AttributeNames", self._AttributeNames + attribute_names)

    # FabBitTemplate._get_attribute():
    def _get_attribute(self, attribute_name: str, types: Tuple[type, ...]) -> Any:
        """Return an attribute value by name."""
        if not hasattr(self, attribute_name):
            raise RuntimeError("FabBitTemplate._get_attribute(): "
                               f"Attribute '{attribute_name} is not present.'")
        attribute: Any = getattr(self, attribute_name)
        if not isinstance(attribute, types):
            raise RuntimeError("FabBitTemplate._get_attribute(): "
                               f"Attribute '{attribute_name} is {type(attribute)}, not {types}'")
        return attribute

    # FabBitTemplate._set_hash():
    def _set_hash(self) -> None:
        """Compute and set the hash FabBitTemplate hash value."""
        # Note "_ParameterNames", "_AttributesNames", and "Hash" are excluded from *base_names*:
        base_names: Tuple[str, ...] = (
            "Name", "FileName", "Material", "ToolHolderHeight", "VendorName", "VendorPartNumber")
        all_names: Tuple[str, ...] = base_names + self._ParameterNames + self._AttributeNames
        name: str
        hashes: Tuple[int, ...] = tuple([hash(getattr(self, name)) for name in all_names])
        final_hash: int = abs(hash(hashes)) & 0xffffffffffffffff  # 64-bit positive hash
        object.__setattr__(self, "Hash", f"{final_hash:016x}")

    # FabBitTemplate.to_json():
    def to_json(self, with_attributes: bool = True) -> str:
        """Return FabBitTemptlate as a JSON string.

        Arguments:
        * *with_attributes* (bool = True):
          If True include additional "non-FreeCAD" attributes; otherwise leave blank.

        """
        comma: str

        # Collect all output into *lines*:
        lines: List[str] = [
            '{',
            '  "version": 2,',
            f'  "name": "{self.Name}",',
            f'  "shape": "{self.FileName}",',
        ]

        # Output parameter/attribute tables :
        tables: Dict[str, Tuple[str, ...]] = {"parameter": self._ParameterNames, "attribute": ()}
        if with_attributes:
            tables["attribute"] += self._AttributeNames + ("Hash",)
        table_name: str
        table_keys: Tuple[str, ...]
        for table_name, table_keys in tables.items():
            keys_count: int = len(table_keys)
            close_curly: str = "" if keys_count else "}"
            lines.append(f'  "{table_name}": {{{close_curly}')
            index: int
            name: str
            for index, name in enumerate(table_keys):
                # Deal with formatting:
                value: Any = getattr(self, name)
                if isinstance(value, float):
                    value = f'{value:.4f} mm'
                elif isinstance(value, str):
                    value = f'"{value}"'
                elif isinstance(value, tuple):
                    sub_value: str
                    values: List[str] = [f'"{sub_value}"' for sub_value in value]
                    value = "[ " + ", ".join(values) + " ]"
                elif isinstance(value, bool):
                    value = str(value).lower()
                comma = "" if index + 1 == keys_count else ","
                lines.append(f'    "{name}": {value}{comma}')
            comma = "," if table_name == "parameter" else ""
            if keys_count:
                lines.append(f'  }}{comma}')

        # Write *lines* to *file_path*:
        lines.append('}')
        lines.append('')
        return '\n'.join(lines)

    # FabBitTemplate.write_json():
    def write_json(self, file_path: Path) -> None:
        """Write FabBitTemptlate out to a JSON file."""
        json_file: IO[str]
        with open(file_path, 'w') as json_file:
            json_file.write(self.to_json())

    @staticmethod
    def _unit_tests() -> None:
        """Run FabBitTemplate unit tests."""

        all_bits: Dict[str, FabBitTemplate] = {}
        ball_end_bit: FabBallEndBit = FabBallEndBit(
            Name="6mm Ball End",
            FileName=Path("ballend.fcstd"),
            CuttingEdgeHeight="40.0000 mm",
            Diameter="6.0000 mm",
            Length="50.0000 mm",
            ShankDiameter="3.0000 mm",
            Material=("steel", "HSS"),
            ToolHolderHeight="20.000 mm",
            Flutes=8,
        )
        all_bits["6mm_Ball_End"] = ball_end_bit

        bull_nose_bit: FabBullNoseBit = FabBullNoseBit(
            Name="6 mm Bull Nose",
            FileName=Path("bullnose.fcstd"),
            CuttingEdgeHeight="40.0000 mm",
            Diameter="6.0000 mm",
            FlatRadius="1.5000 mm",
            Length="50.0000 mm",
            ShankDiameter="3.0000 mm",
            Flutes=8,
            Material=("steel", "HSS"),
            ToolHolderHeight="20.000 mm",
        )
        all_bits["6mm_Bullnose"] = bull_nose_bit

        chamfer_bit: FabChamferBit = FabChamferBit(
            Name="45 Deg. Chamfer",
            FileName=Path("chamfer.fcstd"),
            CuttingEdgeAngle="45.0000 \\u00b0",
            CuttingEdgeHeight="6.3500 mm",
            Diameter="12.3323 mm",
            Length="30.0000 mm",
            ShankDiameter="6.3500 mm",
            TipDiameter="5.0000 mm",
            Material=("steel", "HSS",),
            ToolHolderHeight="20.000 mm",
            Flutes=8,
        )
        all_bits["45degree_chamfer"] = chamfer_bit

        drill_bit: FabDrillBit = FabDrillBit(
            Name="5mm Drill",
            FileName=Path("drill.fcstd"),
            Diameter="5.0000 mm",
            Length="50.0000 mm",
            TipAngle="119.0000 \\u00b0",
            Material=("steel", "HSS"),
            Flutes=2,
            FlutesLength="30.000mm",
        )
        all_bits["5mm_Drill"] = drill_bit

        end_mill_bit: FabEndMillBit = FabEndMillBit(
            Name="5mm Endmill",
            FileName=Path("endmill.fcstd"),
            ToolHolderHeight="20.0000 mm",
            CuttingEdgeHeight="30.0000 mm",
            Diameter="5.0000 mm",
            Length="50.0000 mm",
            ShankDiameter="3.0000 mm",
            Flutes=2,
            Material=("steel", "HSS")
        )
        all_bits["5mm_Endmill"] = end_mill_bit

        probe_bit: FabProbeBit = FabProbeBit(
            Name="Probe",
            FileName=Path("probe.fcstd"),
            Diameter="6.0000 mm",
            Length="50.0000 mm",
            ShaftDiameter="4.0000 mm",
            ToolHolderHeight="30.0000 mm",
        )
        all_bits["probe"] = probe_bit

        slitting_saw_bit: FabSlittingSawBit = FabSlittingSawBit(
            Name="Slitting Saw",
            FileName=Path("slittingsaw.fcstd"),
            BladeThickness="3.0000 mm",
            CapHeight="3.0000 mm",
            CapDiameter="8.0000 mm",
            Diameter="76.2000 mm",
            Length="50.0000 mm",
            ShankDiameter="19.0500 mm",
            Teeth=80,
            Material=("steel", "HSS"),
            ToolHolderHeight="30.0000 mm",
        )
        all_bits["slittingsaw"] = slitting_saw_bit

        thread_cutter_bit: FabThreadCutter = FabThreadCutter(
            Name="5mm-thread-cutter",
            FileName=Path("thread-mill.fcstd"),
            Crest="0.10 mm",
            Diameter="5.00 mm",
            Length="50.00 mm",
            NeckDiameter="3.00 mm",
            NeckLength="20.00 mm",
            Material=("steel", "HSS"),
            ShankDiameter="5.00 mm",
            Flutes=8,
        )
        all_bits["5mm-thread-cutter"] = thread_cutter_bit

        v_bit: FabVBit = FabVBit(
            Name="60 Deg. V-Bit",
            FileName=Path("v-bit.fcstd"),
            CuttingEdgeAngle="60.0000 \\u00b0",
            Diameter="10.0000 mm",
            CuttingEdgeHeight="1.0000 mm",
            TipDiameter="1.0000 mm",
            Length="20.0000 mm",
            ShankDiameter="5.0000 mm",
            Material=("steel", "HSS",),
            ToolHolderHeight="20.000 mm",
            Flutes=8,
        )
        all_bits["60degree_Vbit"] = v_bit

        bit_directory: Path = Path(".") / "squashfs-root" / "usr" / "Mod" / "Path" / "Tools" / "Bit"
        stem: str
        bit: FabBitTemplate
        for stem, bit in all_bits.items():
            bit_file_path: Path = bit_directory / f"{stem}.fctb"
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
            bit.write_json(Path("/tmp") / f"{stem}.fctb")


# FabBallEndBit:
@dataclass(frozen=True)
class FabBallEndBit(FabBitTemplate):
    """FabBallEndBit: An end-mill bit template.

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

    # FabBallEndBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabBallEndBit."""
        super().__post_init__()
        _ = self._get_attribute("CuttingEdgeHeight", (float, str))
        _ = self._get_attribute("Diameter", (float, str))
        _ = self._get_attribute("Length", (float, str))
        _ = self._get_attribute("ShankDiameter", (float, str))
        _ = self._get_attribute("Flutes", (int,))
        self._extend_parameter_names(("CuttingEdgeHeight", "Diameter", "Length", "ShankDiameter"))
        self._extend_attribute_names(("Flutes",))
        self._set_hash()


# FabBullNoseBit:
@dataclass(frozen=True)
class FabBullNoseBit(FabBitTemplate):
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
    CuttingEdgeHeight: Union[str, float] = cast(str, None)
    Diameter: Union[str, float] = cast(str, None)
    FlatRadius: Union[str, float] = cast(str, None)
    Length: Union[str, float] = cast(str, None)
    ShankDiameter: Union[str, float] = cast(str, None)
    Flutes: int = 0

    # FabBullNoseBit.__post_init__():
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

# FabChamferBit:
@dataclass(frozen=True)
class FabChamferBit(FabBitTemplate):
    """FabDrillBit: An drill bit template.

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

    # FabChamferBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialze the FabChamferBit."""
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

# FabDrillBit:
@dataclass(frozen=True)
class FabDrillBit(FabBitTemplate):
    """FabDrillBit: An drill bit template.

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

    # FabDrillBit.__post_init__():
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


# FabEndMillBit:
@dataclass(frozen=True)
class FabEndMillBit(FabBitTemplate):
    """FabEndMillBit: An end-mill bit template.

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

    # FabEndMillBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabEndMillBit."""
        super().__post_init__()
        _ = self._get_attribute("CuttingEdgeHeight", (float, str))
        _ = self._get_attribute("Diameter", (float, str))
        _ = self._get_attribute("Length", (float, str))
        _ = self._get_attribute("ShankDiameter", (float, str))
        _ = self._get_attribute("Flutes", (int,))
        self._extend_parameter_names(("CuttingEdgeHeight", "Diameter", "Length", "ShankDiameter"))
        self._extend_attribute_names(("Flutes",))
        self._set_hash()


# FabProbeBit:
@dataclass(frozen=True)
class FabProbeBit(FabBitTemplate):
    """FabProbeBit: A touch off probe.

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

    # FabProbeBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialize the FabProbeBit."""
        super().__post_init__()
        _ = self._get_attribute("Diameter", (float, str))
        _ = self._get_attribute("Length", (float, str))
        _ = self._get_attribute("ShaftDiameter", (float, str))
        self._extend_parameter_names(("Diameter", "Length", "ShaftDiameter"))
        self._set_hash()


# FabSlittingSawBit:
@dataclass(frozen=True)
class FabSlittingSawBit(FabBitTemplate):
    """FabSlittingSawBit: An slitting saw bit.

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

    # FabSlittingSawBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialze the FabSlittingSawBit."""
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


# FabThreadCutter:
@dataclass(frozen=True)
class FabThreadCutter(FabBitTemplate):
    """FabThreadCutter: An thread cutter bit.

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

    # FabThreadCutter.__post_init__():
    def __post_init__(self) -> None:
        """Initialze the FabGThreadCutter."""
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

# FabVBit:
@dataclass(frozen=True)
class FabVBit(FabBitTemplate):
    """FabVBit: An V bit template.

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
    CuttingEdgeAngle: Union[str, float] = cast(str, None)
    Diameter: Union[str, float] = cast(str, None)
    CuttingEdgeHeight: Union[str, float] = cast(str, None)
    TipDiameter: Union[str, float] = cast(str, None)
    Length: Union[str, float] = cast(str, None)
    ShankDiameter: Union[str, float] = cast(str, None)
    Flutes: int = 0

    # FabVBit.__post_init__():
    def __post_init__(self) -> None:
        """Initialze the FabChamferBit."""
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
    document_name: str = "JobTest"
    document: "App.Document" = get_document(document_name, tracing=next_tracing)

    model(document, tracing=next_tracing)

    document.recompute()
    document.saveAs("/tmp/bar.fcstd")

    # Disable for now
    # FabBitTemplate._unit_tests()
    if tracing:
        print(f"{tracing}<=main()")


if __name__ == "__main__":
    main(tracing=" ")
