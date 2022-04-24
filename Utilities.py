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
from typing import Any, Dict, Tuple


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
    def _unit_tests() -> None:
        """Run FabColor unit tests."""
        _ = FabColor.svg_to_rgb("red")

        try:
            FabColor.svg_to_rgb("fred")
        except ValueError as value_error:
            assert str(value_error) == "'fred' is not a supported SVG color name.", str(value_error)


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
    def __post_init__(self):
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
    def _unit_tests() -> None:
        """Perform Unit tests."""
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


# FabMaterial:
@dataclass
class FabMaterial(object):
    """FabMaterial: Represents a stock material.

    Other properties to be added later (e.g. transparency, shine, machining properties, etc.)

    Attributes:
    * *Name* (Tuple[str, ...]): A list of material names from generict to specific.
    * *Color* (str): The color name to use.

    """

    Name: Tuple[str, ...]  # Hierarchical name from least specific to most specific.
    Color: str  # SVG color name to use.

    # FabMaterial.__init__():
    def __post_init__(self) -> None:
        """Finish initializing FabMatarials."""
        check_type("FabMaterial.Name", self.Name, Tuple[str, ...])
        check_type("FabMaterial.Color", self.Color, str)

    @staticmethod
    def _unit_tests() -> None:
        """Run FabMaterial unit tests."""
        name: Tuple[str, ...] = ("brass",)
        color: str = "orange"
        material: FabMaterial = FabMaterial(name, color)
        material.Name = name
        material.Color == color


def _unit_tests() -> None:
    """Run the unit tests."""
    FabColor._unit_tests()
    FabMaterial._unit_tests()
    FabToolController._unit_tests()


if __name__ == "__main__":
    _unit_tests()
