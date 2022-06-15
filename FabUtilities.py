#!/usr/bin/env python3
"""FabUtilities: Miscellaneous Fab package classes.

The Utility classes are:
* FabColor:
  This is a class for converting SVG (Scalable Vector Graphics) color names into
  RBG (Red/Green/Blue) triples.
* FabMaterial:
  This is a class that describes material properties.
* FabToolController:
  This roughly corresponds to a FreeCAD Path library tool controller which basically specifies
  CNC speeds and feeds.

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

from dataclasses import dataclass
from typeguard import check_type
from typing import Any, ClassVar, Dict, List, Tuple


# FabColor:
class FabColor(object):
    """FabColor: Convert from SVG color names to FreeCAD RGB triples."""

    RGB_COLORS = {
        "alice_blue": 0xf0f8ff,
        "antique_white": 0xfaebd7,
        "aqua": 0x00ffff,
        "aquamarine": 0x7fffd4,
        "azure": 0xf0ffff,
        "beige": 0xf5f5dc,
        "bisque": 0xffe4c4,
        "black": 0x000000,
        "blanched_almond": 0xffebcd,
        "blue": 0x0000ff,
        "blue_violet": 0x8a2be2,
        "brown": 0xa52a2a,
        "burlywood": 0xdeb887,
        "cadet_blue": 0x5f9ea0,
        "chartreuse": 0x7fff00,
        "chocolate": 0xd2691e,
        "coral": 0xf08080,
        "corn_flower_blue": 0x6495ed,
        "corn_silk": 0xfff8dc,
        "crimson": 0xdc143c,
        "cyan": 0x00ffff,
        "dark_blue": 0x00008b,
        "dark_cyan": 0x008b8b,
        "dark_goldenrod": 0xb8860b,
        "dark_gray": 0xa9a9a9,
        "dark_green": 0x006400,
        "dark_grey": 0xa9a9a9,
        "dark_khaki": 0xbdb76b,
        "dark_magenta": 0x8b008b,
        "dark_olive_green": 0x556b2f,
        "dark_orange": 0xff8c00,
        "dark_orchid": 0x9932cc,
        "dark_red": 0x8b0000,
        "dark_salmon": 0xe9967a,
        "dark_sea_green": 0x8fbc8f,
        "dark_slate_blue": 0x483d8b,
        "dark_slate_gray": 0x2f4f4f,
        "dark_slate_grey": 0x2f4f4f,
        "dark_turquoise": 0x40e0d0,
        "dark_violet": 0x9f00d3,
        "deep_pink": 0xff1493,
        "deep_sky_blue": 0x00bfff,
        "dim_gray": 0x696969,
        "dim_grey": 0x696969,
        "dodger_blue": 0x1e90ff,
        "fire_brick": 0xb22222,
        "floral_white": 0xfffaf0,
        "forest_green": 0x228b22,
        "fuchsia": 0xff00ff,
        "gainsboro": 0xdcdcdc,
        "ghost_white": 0xf8f8ff,
        "gold": 0xffd700,
        "goldenrod": 0xdaa520,
        "gray": 0x808080,
        "green": 0x008000,
        "green_yellow": 0xadff2f,
        "grey": 0x808080,
        "honey_dew": 0xf0fff0,
        "hot_pink": 0xff1493,
        "indian_red": 0xcd5c5c,
        "indigo": 0x4b0082,
        "ivory": 0xfffff0,
        "khaki": 0xf0e68c,
        "lavender": 0xe6e6fa,
        "lavender_blush": 0xfff0f5,
        "lawn_green": 0x7cfc00,
        "lemon_chiffon": 0xfffacd,
        "light_blue": 0xadd8e6,
        "light_coral": 0xf08080,
        "light_cyan": 0xe0ffff,
        "light_goldenrod_yellow": 0xfafad2,
        "light_gray": 0xd3d3d3,
        "light_green": 0x90ee90,
        "light_grey": 0xd3d3d3,
        "light_pink": 0xffb6c1,
        "light_salmon": 0xffa07a,
        "light_sea_green": 0x20b2aa,
        "light_sky_blue": 0x87cefa,
        "light_slate_gray": 0x778899,
        "light_slate_grey": 0x778899,
        "light_steel_blue": 0xb0c4de,
        "light_yellow": 0xffffe0,
        "lime": 0x00ff00,
        "lime_green": 0x2e8b57,
        "linen": 0xfaf0e6,
        "magenta": 0xff00ff,
        "maroon": 0x800000,
        "medium_aquamarine": 0x66cdaa,
        "medium_blue": 0x0000cd,
        "medium_orchid": 0xba55d3,
        "medium_purple": 0x9370db,
        "medium_sea_green": 0x3cb371,
        "medium_slate_blue": 0x66cdaa,
        "medium_spring_green": 0x00fa9a,
        "medium_turquoise": 0x48d1cc,
        "medium_violet_red": 0xc71585,
        "mid_night_blue": 0x191970,
        "mint_cream": 0xf5fffa,
        "misty_rose": 0xffe4e1,
        "moccasin": 0xffe4b5,
        "navajo_white": 0xffdead,
        "navy": 0x000080,
        "old_lace": 0xfdf5e6,
        "olive": 0x808000,
        "olive_drab": 0x6b8e23,
        "orange": 0xffa500,
        "orange_red": 0xff4500,
        "orchid": 0xda70d6,
        "pale_goldenrod": 0xeee8aa,
        "pale_green": 0x98fb98,
        "pale_turquoise": 0xafeeee,
        "pale_violet_red": 0xdb7093,
        "papaya_whip": 0xffefd5,
        "peach_puff": 0xffdab9,
        "peru": 0xcd8f3f,
        "pink": 0xffc0cb,
        "plum": 0xdda0dd,
        "powder_blue": 0xb0e0e6,
        "purple": 0x800080,
        "red": 0xff0000,
        "rosy_brown": 0xbc8f8f,
        "royal_blue": 0x4169e1,
        "saddle_brown": 0x8b2be2,
        "salmon": 0xfa8072,
        "sandy_brown": 0xf4a460,
        "sea_green": 0x2e8b57,
        "sea_shell": 0xfff5ee,
        "sienna": 0xa0522d,
        "silver": 0xc0c0c0,
        "sky_blue": 0x87ceeb,
        "slate_blue": 0x6a5acd,
        "slate_gray": 0x708090,
        "slate_grey": 0x708090,
        "snow": 0xfffafa,
        "spring_green": 0x00ff7f,
        "steel_blue": 0x4682b4,
        "tan": 0xd2b48c,
        "teal": 0x008080,
        "thistle": 0xd8bfd8,
        "tomato": 0xff6347,
        "turquoise": 0x40e0d0,
        "violet": 0xee82ee,
        "wheat": 0xf5deb3,
        "white": 0xffffff,
        "white_smoke": 0xf5f5f5,
        "yellow": 0xffff00,
        "yellow_green": 0x9acd32,
    }

    @staticmethod
    def svg_to_rgb(svg_color_name: str) -> Tuple[float, float, float]:
        """Convert Scalable Vector Graphics color to Red/Green/Blue saturation triples.

        Arguments:
        * *svg_color_name* (str): The SVG color name to use.

        Returns:
        * (Tuple[float, float, float]) as Red/Green/Blue saturation triple used by FreeCAD.

        """
        rgb_colors: Dict[str, int] = FabColor.RGB_COLORS
        if svg_color_name not in rgb_colors:
            raise ValueError(f"'{svg_color_name}' is not a supported SVG color name.")
        rgb_color: int = rgb_colors[svg_color_name]
        red: int = (rgb_color >> 16) & 0xff
        green: int = (rgb_color >> 8) & 0xff
        blue: int = rgb_color & 0xff
        return (float(red) / 255.0, float(green) / 255.0, float(blue) / 255.0)

    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run FabColor unit tests."""
        if tracing:
            print(f"{tracing}=>FabColor._unit_tests()")
        _ = FabColor.svg_to_rgb("red")

        try:
            FabColor.svg_to_rgb("fred")
        except ValueError as value_error:
            assert str(value_error) == "'fred' is not a supported SVG color name.", str(value_error)

        if tracing:
            print(f"{tracing}<=FabColor._unit_tests()")


# FabToolController:
@dataclass(frozen=True)
class FabToolController(object):
    """FabToolController: Speeds/Feeds information.

    Attributes:
    * *BitName* (str): The name Bit file name in `.../Tools/Bit/*.fctb` where `*` is BitName.
    * *Cooling* (str): The cooling to use which is one of "None", "Flood", or "Mist".
    * *HorizontalFeed* (float): The material horizontal feed rate in mm/sec.
    * *HorizontalRapid* (float): The horizontal rapid feed rate in mm/sec.
    * *SpindleDirection* (bool): The spindle direction where True means clockwise.
    * *SpindleSpeed* (float): The spindle rotation speed in rotations per second.
    * *ToolNumber* (int): The tool number to use.
    * *VerticalFeed* (float): The material vertical free rate in mm/sec.
    * *VerticalRapid* (float): The vertical rapid feed rate in mm/sec.

    """

    BitName: str
    Cooling: str
    HorizontalFeed: float
    HorizontalRapid: float
    SpindleDirection: bool
    SpindleSpeed: float
    ToolNumber: int
    VerticalFeed: float
    VerticalRapid: float

    # FabToolController.__post_init__():
    def __post_init__(self) -> None:
        """Fininsh initializing FabToolController"""
        check_type("FabToolController.BitName", self.BitName, str)
        check_type("FabToolController.Cooling", self.BitName, str)
        check_type("FabToolController.HorizontalFeed", self.HorizontalFeed, float)
        check_type("FabToolController.HorizontalRapid", self.HorizontalRapid, float)
        check_type("FabToolController.SpindleDirection", self.SpindleDirection, float)
        check_type("FabToolController.SpindleSpeed", self.SpindleSpeed, float)
        check_type("FabToolController.ToolNumber", self.ToolNumber, int)
        check_type("FabToolController.VerticalFeed", self.VerticalFeed, float)
        check_type("FabToolController.VerticalRapid", self.VerticalRapid, float)

    # FabToolController.to_json():
    def to_json(self) -> Dict[str, Any]:
        """Return a dictionary containing the controller information."""
        return {
            "BitName": self.BitName,
            "Cooling": self.Cooling,
            "HorizontalFeed": self.HorizontalFeed,
            "HorizontalRapid": self.HorizontalRapid,
            "SpindleDirection": self.SpindleDirection,
            "SpindleSpeed": self.SpindleSpeed,
            "ToolNumber": self.ToolNumber,
            "VerticalFeed": self.VerticalFeed,
            "VerticalRapid": self.VerticalRapid,
        }

    # FabController._unit_tests()
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Perform FabController unit tests."""
        if tracing:
            print(f"{tracing}=>FabController._unit_tests()")

        tool_controller1a: FabToolController = FabToolController(
            BitName="5mm_Endmill",
            Cooling="Flood",
            HorizontalFeed=1.0,
            HorizontalRapid=250.0,
            SpindleDirection=True,
            SpindleSpeed=5000.0,
            ToolNumber=1,
            VerticalFeed=1.0,
            VerticalRapid=250.0
        )
        tool_controller1b: FabToolController = FabToolController(
            BitName="5mm_Endmill",
            Cooling="Flood",
            HorizontalFeed=1.0,
            HorizontalRapid=250.0,
            SpindleDirection=True,
            SpindleSpeed=5000.0,
            ToolNumber=1,
            VerticalFeed=1.0,
            VerticalRapid=250.0
        )
        tool_controller2: FabToolController = FabToolController(
            BitName="5mm_Drill",
            Cooling="Flood",
            HorizontalFeed=1.0,
            HorizontalRapid=250.0,
            SpindleDirection=True,
            SpindleSpeed=5000.0,
            ToolNumber=2,
            VerticalFeed=1.0,
            VerticalRapid=250.0
        )
        assert tool_controller1a == tool_controller1b, "FabToolController.__eq__() failed"
        assert tool_controller1a != tool_controller2, "FabToolController.__eq__() failed"
        desired_json: Dict[str, Any] = {
            "BitName": "5mm_Endmill",
            "Cooling": "Flood",
            "HorizontalFeed": 1.0,
            "HorizontalRapid": 250.0,
            "SpindleDirection": True,
            "SpindleSpeed": 5000.0,
            "ToolNumber": 1,
            "VerticalFeed": 1.0,
            "VerticalRapid": 250.0,
        }
        actual_json: Dict[str, Any] = tool_controller1b.to_json()
        assert desired_json == actual_json, ("Dict mismatch", desired_json, actual_json)
        tool_controller_table: Dict[FabToolController, int] = {}

        tool_controller_table[tool_controller1a] = 1
        assert tool_controller1a in tool_controller_table, "Insert 1a failed"
        assert tool_controller1b in tool_controller_table, "Insert 1b failed"
        assert tool_controller_table[tool_controller1a] == 1, "Lookup 1a failed"
        assert tool_controller_table[tool_controller1b] == 1, "Lookup 1b failed"
        assert len(tool_controller_table) == 1, "Table is wrong size"

        assert tool_controller2 not in tool_controller_table, "Already in table?"
        tool_controller_table[tool_controller2] = 2
        assert tool_controller_table[tool_controller2] == 2, "Lookup failed"
        assert tool_controller2 in tool_controller_table, "Insert failed"
        assert len(tool_controller_table) == 2, "Table is wrong size"

        if tracing:
            print(f"{tracing}<=FabController._unit_tests()")


# FabMaterial:
@dataclass(frozen=True)
class FabMaterial(object):
    """FabMaterial: Represents a stock material.

    Other properties to be added later (e.g. transparency, shine, machining properties, etc.)

    Attributes:
    * *Name* (Tuple[str, ...]): A list of material names from generic to specific.
    * *Color* (str): The color name to use.

    # Constructor:
    * * FabMaterial(Name, Color)

    """

    Name: Tuple[str, ...]  # Hierarchical name from generic to specific.
    Color: str  # SVG color name to use.

    _InchChipLoadData: ClassVar[Tuple[str, ...]] = (
        "  in: Steel         Stainless     Aluminum      Titanium      Wood          Plastic",
        "1/16: 0.0019-0.0036 0.0016-0.0030 0.0021-0.0040 0.0015-0.0028 0.0028-0.0053 0.0052-0.0098",
        " 1/8: 0.0023-0.0044 0.0019-0.0036 0.0025-0.0048 0.0018-0.0034 0.0033-0.0063 0.0062-0.0118",
        "3/16: 0.0025-0.0048 0.0021-0.0040 0.0028-0.0053 0.0020-0.0037 0.0037-0.0070 0.0068-0.0129",
        " 1/4: 0.0027-0.0051 0.0022-0.0042 0.0030-0.0056 0.0021-0.0040 0.0039-0.0074 0.0073-0.0138",
        "5/16: 0.0028-0.0053 0.0023-0.0044 0.0031-0.0059 0.0022-0.0042 0.0041-0.0077 0.0076-0.0144",
        " 3/8: 0.0029-0.0055 0.0024-0.0046 0.0032-0.0061 0.0023-0.0043 0.0042-0.0080 0.0079-0.0149",
        " 1/2: 0.0031-0.0058 0.0026-0.0048 0.0034-0.0064 0.0024-0.0045 0.0045-0.0084 0.0083-0.0157",
        " 5/8: 0.0032-0.0061 0.0027-0.0050 0.0035-0.0067 0.0025-0.0047 0.0046-0.0088 0.0086-0.0164",
        " 3/4: 0.0033-0.0063 0.0027-0.0052 0.0036-0.0069 0.0026-0.0049 0.0048-0.0091 0.0089-0.0169",
        " 7/8: 0.0034-0.0064 0.0028-0.0053 0.0037-0.0071 0.0026-0.0050 0.0049-0.0093 0.0092-0.0173",
        "   1: 0.0035-0.0066 0.0029-0.0054 0.0038-0.0072 0.0027-0.0051 0.0050-0.0095 0.0094-0.0177",
    )
    _MmChipLoadData: ClassVar[Tuple[str, ...]] = (
        "mm: Steel     Stainless Aluminum  Titanium  Wood      Plastic",
        " 2: 0.01-0.01 0.01-0.01 0.01-0.01 0.01-0.01 0.01-0.02 0.02-0.03",
        " 3: 0.01-0.02 0.01-0.02 0.01-0.03 0.01-0.02 0.02-0.03 0.03-0.06",
        " 4: 0.02-0.03 0.01-0.03 0.02-0.03 0.01-0.02 0.02-0.04 0.04-0.08",
        " 5: 0.02-0.04 0.02-0.03 0.02-0.04 0.02-0.03 0.03-0.05 0.05-0.10",
        " 6: 0.02-0.04 0.02-0.03 0.02-0.05 0.02-0.03 0.03-0.06 0.06-0.11",
        " 8: 0.03-0.05 0.02-0.04 0.03-0.05 0.02-0.04 0.04-0.07 0.07-0.13",
        "10: 0.03-0.06 0.02-0.05 0.03-0.06 0.02-0.04 0.04-0.08 0.08-0.15",
        "12: 0.03-0.06 0.03-0.05 0.03-0.07 0.02-0.05 0.05-0.09 0.09-0.16",
        "16: 0.04-0.07 0.03-0.06 0.04-0.07 0.03-0.05 0.05-0.10 0.10-0.18",
        "20: 0.04-0.07 0.03-0.06 0.04-0.08 0.03-0.06 0.06-0.11 0.11-0.20",
        "25: 0.04-0.08 0.03-0.07 0.05-0.09 0.03-0.06 0.06-0.12 0.11-0.22",
    )

    _ChipLoadTable: ClassVar[Dict[str, List[Tuple[float, float]]]] = {}

    # FabMaterial.__post_init__():
    def __post_init__(self) -> None:
        """Finish initialized FabMaterial."""
        tracing: str = ""  # Manually set to non-empty string to trace:
        if tracing:
            print(f"{tracing}=>FabMaterial.__post_init__()")

        check_type("FabMaterial.Name", self.Name, Tuple[str, ...])
        check_type("FabMaterial.Color", self.Color, str)

        # Fill in the *chip_load_table* the first time any FabMaterial is created:
        chip_load_table: Dict[str, List[Tuple[float, float]]] = FabMaterial._ChipLoadTable
        if len(chip_load_table) == 0:
            # Iterate over both of the *chip_load_data* tables:
            convert_chip_load_datas: List[Tuple[float, Tuple[str, ...], bool]] = [
                (25.4, FabMaterial._InchChipLoadData, True),  # 1 inch = 25.4 mm
                (1.0, FabMaterial._MmChipLoadData, False),
            ]

            def words_split(words: str) -> List[str]:
                """"""
                word: str
                return [word for word in words.split(" ") if len(word) > 0]

            convert: float
            chip_load_data: Tuple[str, ...]
            initialize: bool
            for convert, chip_load_data, initialize in convert_chip_load_datas:
                if tracing:
                    print(f"{tracing}{convert=} {initialize=}")
                # Extract the *materials* names:
                materials: List[str] = [material.lower()
                                        for material in words_split(chip_load_data[0])]
                del materials[0]  # Delete "in:" or "mm:"
                if tracing:
                    print(f"{tracing}{materials=}")
                if initialize:
                    material: str
                    for material in materials:
                        chip_load_table[material] = []

                # Iterate through each *row* in *chip_load_table*, extracting *diameter*:
                row_index: int
                row: str
                for row_index, row in enumerate(chip_load_data[1:]):
                    # Split *row* into *columns* and extract the *diameter*:
                    columns: List[str] = words_split(row)
                    diameter_text: str = columns[0].strip(" :")
                    diameter: float
                    if '/' in diameter_text:
                        fraction: List[str] = diameter_text.split("/")
                        diameter = float(fraction[0]) / float(fraction[1]) * convert
                    else:
                        diameter = float(diameter_text) * convert
                    if tracing:
                        print(f"{tracing}[{row_index}]: {diameter:.3f} '{columns[1:]}'")

                    # The remaining *columns* are chip-load ranges of the form "#-#".
                    index: int
                    low_high: str
                    for index, low_high in enumerate(columns[1:]):
                        pair: List[str] = low_high.split("-")
                        assert len(pair) == 2, pair
                        low: float = float(pair[0]) * convert
                        high: float = float(pair[1]) * convert
                        chip_load: float = (high + low) / 2.0
                        material = materials[index]
                        chip_load_table[material].append((diameter, chip_load))

                # Now sort the *chip_load_table* entries:
                diameter_loads: List[Tuple[float, float]]
                for diameter_loads in chip_load_table.values():
                    diameter_loads.sort()

        if tracing:
            print(f"{tracing}{chip_load_table=}")
            print(f"{tracing}<=FabMaterial.__post_init__()")

    # FabMaterial.getChipLoad():
    def getChipLoad(self, effective_diameter: float, tracing: str = "") -> float:
        """Return FabMatrial chip load.

        Arguments:
        * *effective_diameter* (float): The effective diameter of the tool bit.

        Returns:
        * (float): The chipload in millimeters.

        """
        if tracing:
            print(f"{tracing}=>FabMaterial.getChipLoad()")
        chip_load_table: Dict[str, List[Tuple[float, float]]] = FabMaterial._ChipLoadTable
        top_material: str = self.Name[0].lower()
        if top_material not in chip_load_table:
            raise RuntimeError(f"FabMaterial.getChipLoad(): '{top_material}' "
                               f"is not one of {tuple(chip_load_table.keys())})")
        diameter_chip_loads: List[Tuple[float, float]] = chip_load_table[top_material]
        diameter: float
        chip_load: float
        for diameter, chip_load in reversed(diameter_chip_loads):
            if diameter <= effective_diameter:
                break
        else:
            raise RuntimeError(
                f"FabMaterial.getChipLoad('{top_material}') no chip load found "
                f"for ({effective_diameter:.5f})"
            )

        if tracing:
            print(f"{tracing}=>FabMaterial.getChipLoad()=>{chip_load:.5f}")
        return chip_load

    # FabMaterial.get_hash():
    def get_hash(self) -> Tuple[Any, ...]:
        """Return an immutable hash for a FabMaterial."""
        return (self.Name, self.Color)

    # FabMaterial._unit_tests()
    @staticmethod
    def _unit_tests(tracing: str = "") -> None:
        """Run FabMaterial unit tests."""
        if tracing:
            print(f"{tracing}=>FabMaterial._unit_tests()")

        name: Tuple[str, ...] = ("Aluminum",)
        color: str = "orange"
        material: FabMaterial = FabMaterial(name, color)
        material.Name == name, material.Name
        material.Color == color, material.Color
        material_hash: Tuple[Any, ...] = material.get_hash()
        assert material_hash == (("Aluminum",), "orange"), material_hash

        def check(test_name: str, material: FabMaterial,
                  diameter: float, desired_chip_load: float) -> None:
            """Check chip load."""
            chip_load: float = material.getChipLoad(diameter)
            assert abs(chip_load - desired_chip_load) < 1.0e-6, (
                f"{test_name} {chip_load:.5f} != {desired_chip_load}")

        # Do working tests:
        aluminum: FabMaterial = FabMaterial(("Aluminum", "6061"), "silver")
        steel: FabMaterial = FabMaterial(("Steel",), "grey")
        check("aluminum1", aluminum, 3.0, 0.02000)
        check("steel", steel, .5 * 25.4, 0.11303)  # TODO(FIX)

        # Do exception tests:
        unobtainium: FabMaterial = FabMaterial(("Unobtainium",), "grey")
        try:
            unobtainium.getChipLoad(5.0)
            assert False
        except RuntimeError as runtime_error:
            assert str(runtime_error).startswith(
                "FabMaterial.getChipLoad(): 'unobtainium' is not one of (")
        try:
            aluminum.getChipLoad(.10)
            assert False
        except RuntimeError as runtime_error:
            expected: str = "FabMaterial.getChipLoad('aluminum') no chip load found for (0.10000)"
            assert str(runtime_error) == expected

        if tracing:
            print(f"{tracing}<=FabMaterial._unit_tests()")


# main()
def main(tracing: str = "") -> None:
    """Run the unit tests."""
    next_tracing: str = tracing + " " if tracing else ""
    if tracing:
        print(f"{tracing}=>main()")

    FabColor._unit_tests(tracing=next_tracing)
    FabMaterial._unit_tests(tracing=next_tracing)
    FabToolController._unit_tests(tracing=next_tracing)

    if tracing:
        print(f"{tracing}<=main()")


if __name__ == "__main__":
    main(tracing=" ")
