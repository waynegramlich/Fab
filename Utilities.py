#!/usr/bin/env python3
"""Utilities: Convenice class.

The Utilitly classes are:
* FabCheck:
  This is some common code to check argument types for public functions.
* FabMaterial:
  This is a class that describes material properties.
  sub-class of Vector.

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

import sys
sys.path.append(".")
import Embed
USE_FREECAD: bool
USE_CAD_QUERY: bool
USE_FREECAD, USE_CAD_QUERY = Embed.setup()
Embed.setup()

if USE_FREECAD:
    from FreeCAD import Vector  # type: ignore
elif USE_CAD_QUERY:
    from cadquery import Vector  # type: ignore

# import colorsys  # Color conversion routines.
from dataclasses import dataclass
from typing import Any, cast, List, Dict, Sequence, Tuple, Union


# FabCheck:
@dataclass(frozen=True)
class FabCheck(object):
    """FabCheck: Check arguments for type mismatch errors.

    Attributes:
    * *name* (str):
       The argument name (used for error messages.)
    * *types* (Tuple[Any]):
      A tuple of acceptable types or constrained types.  A type is something line `bool`, `int`,
      `float`, `MyClass`, etc.   A constrained type is a tuple of the form (str, Any, Any, ...)
      and are discussed further below.

    An FabCheck contains is used to type check a single function argument.
    The static method `FabCheck.check()` takes a list of argument values and the
    corresponding tuple FabCheck's and verifies that they are correct.

    Example 1:

         EXAMPLE1_CHECKS = (
             FabCheck("arg1", (int,)),
             FabCheck("arg2", (bool,)),
             FabCheck("arg3", (type(None), MyType),  # Optional[myType]
             FabCheck("arg4," list),   # List[Any]
         )
         def my_function(arg1: int, arg2: bool, arg3: Any, arg4: List[str]) -> None:
             '''Doc string here.'''
            value_error: str = FabCheck.check((arg1, arg2, arg3, arg4), MY_FUNCTION_CHECKS)
            if value_error:
                raise ValueError(value_error)
            # Rest of code goes here.

    A constrained type looks like `("xxx:yyy:zzz", XArg, YArg, ZArg)`, where the `xxx` are flag
    characters are associated with `XArg`, `yyy` are for `YArg`, etc.  The flag characters are:
    * `L`: A List of Arg
    * `T`: A Tuple of Arg
    * `S`: A List or Tuple of Arg
    * `+`: Len of Arg must be greater than 0
    * `?`: None is acceptible.
    Additional flags are added as needed.

    Example 2:

        EXAMPLE2_CHECKS = (
            FabCheck("arg1", ("+", str)),  # Arg1 must be a non-empty string
            FabCheck("arg2", ("?", str)),  # Arg2 can be a string or None
            FabCheck("arg3", ("+?", str)),  # Arg3 can be a non-empty string or None
            FabCheck("arg4", ("L", str)),  # Arg4 can be a list of strings
            FabCheck("arg5", ("T", str)),  # Arg4 can be a tuple of strings
            FabCheck("arg6", ("S", str)),  # Arg6 can be a list or tuple of strings
            FabCheck("arg7", ("L", (float, int)),  # Arg7 can be a list of mixed float and int

    """

    name: str  # Argument name
    options: Tuple[Any, ...]  # Types or patterns to match

    @staticmethod
    def _type_name(t: Any) -> str:
        """Return the best guess for the type name."""
        name: str = f"{t}"
        if hasattr(t, "__name__"):
            name = t.__name__
        elif hasattr(t, "__class__"):
            name = t.__class__.__name__
        return name

    # FabCheck.check():
    @classmethod
    def check(cls, values: Sequence[Any],
              checks: Sequence["FabCheck"], tracing: str = "") -> str:
        """Return type mismatch error message."""
        if tracing:
            print(f"{tracing}=>FabCheck({values}, {checks}")
        assert len(values) == len(checks), (
            f"{len(values)} values do not match {len(checks)} checks")
        error: str = ""
        index: int
        value: Any
        for index, value in enumerate(values):
            # Catagorize *value*:
            is_list: bool = isinstance(value, list)
            is_tuple: bool = isinstance(value, tuple)
            is_sequence: bool = is_list or is_tuple
            length: int = -1
            try:
                length = len(value)
            except TypeError:
                pass
            if tracing:
                print(f"{tracing}{is_list=} {is_tuple=} {is_sequence=} {length=}")

            # Get associated *check* and unpack it:
            check: "FabCheck" = checks[index]
            # if not isinstance(check, cls):
            #     raise ValueError(f"[{index}]:{check} is not FabCheck:  {checks}")
            name: str = check.name
            options: Tuple[Any, ...] = check.options
            # if not options:
            #    raise ValueError(f"[{index}]:{check} has empty options")
            flags: str = ""
            if isinstance(options[0], str):
                flags = options[0]
                options = options[1:]
            if tracing:
                print(f"{tracing}{flags=} {options=}")

            # Process each *flag* in *flags*:
            flag: str
            for flag in sorted(flags, reverse=True):  # Do letter flags first:
                if flag == 'S':
                    if not is_sequence:
                        error = f"[{index}]: Argument '{name}' is neither a list nor tuple"
                elif flag == 'L':
                    if not is_list:
                        error = f"[{index}]: Argument '{name}' is not a list"
                elif flag == 'T':
                    if tracing:
                        print(f"{tracing}{flag=} {is_tuple=}")
                    if not is_tuple:
                        error = f"[{index}]: Argument '{name}' is not a tuple"
                elif flag == '+':
                    if tracing:
                        print(f"{tracing}{flag=}")
                    if length < 1:
                        error = f"[{index}]: Argument '{name}' has no length"
                    elif length == 0:
                        error = f"[{index}]: Argument '{name}' is empty"
                elif flag == '?':
                    options += (type(None),)  # Allow for None type.
                else:
                    raise ValueError(f"Flag '{flag=}' is not allowed {flags=}.")
                if flag:
                    break

            if not error:
                type_names: Sequence[str]
                if is_sequence:
                    # For a sequence, verify the sequence element types:
                    element: Any
                    for index, element in enumerate(value):
                        for option in options:
                            if isinstance(element, option):
                                break
                        else:
                            type_names = [FabCheck._type_name(option)
                                          for option in options]
                            error = (f"[{index}]: {element} ({cls._type_name(element)}) "
                                     f"is not of type {type_names}")
                            break
                else:
                    # For a non-sequence, verify the types:
                    for option in options:
                        if isinstance(value, option):
                            break  # Type matched
                    else:
                        type_names = [FabCheck._type_name(option)
                                      for option in options]
                        error = (f"Argument '{name}' is {cls._type_name(value)} "
                                 f"which is not one of {type_names}")
                        break
        if tracing:
            print(f"{tracing}<=FabCheck({values}, {checks}=>'{error}'")
        return error

    # FabCheck.init_show():
    @staticmethod
    def init_show(name: str, arguments: Sequence[Any], checks: Sequence["FabCheck"]) -> str:
        """Return string representation based in initializer arguments.

        Arguments:
        * *name* (str): Full fuction/method name.
        * *arguments* (Sequence[Any]): All argument values.
        * *checks*: (Sequence[FabCheck]): Associated FabCheck's.

        Returns:
        * (str) containing function/method name with associated initialize arguments:

        Raises:
        * ValueError: For length mismatches and bad parameter types:

        """
        # Assemble *results* which is the list of positional and keyword arguments:
        if len(arguments) != len(checks):
            raise ValueError(
                f"Arguments size ({len(arguments)}) != checks size ({len(checks)})")
        if not isinstance(name, str):
            raise ValueError(f"{name} is not a string")

        # Assemble *results* from *arguments* and *checks*:
        keywords_needed: bool = False
        index: int
        argument_value: Any
        results: List[str] = []
        for index, argument_value in enumerate(arguments):
            check: FabCheck = checks[index]
            if not isinstance(check, FabCheck):
                raise ValueError(f"{check} is not an FabCheck")
            argument_name: str = check.name
            argument_options: Tuple[Any, ...] = check.options
            none_allowed: bool = type(None) in argument_options
            is_none: bool = isinstance(argument_value, type(None))

            # Append appropriate values to *results*:
            if isinstance(argument_value, str):
                argument_value = f"'{argument_value}'"
            if is_none and none_allowed:
                # None occurred and is allowed.  From now on prefix *result* with a keyword:
                keywords_needed = True
            elif keywords_needed:
                results.append(f"{argument_name}={argument_value}")
            else:
                results.append(f"{argument_value}")
        return f"{name}({', '.join(results)})"

    @classmethod
    def _unit_tests(cls):
        """Run FabCheck unit tests."""
        # Test *FabCheck._type_name():
        assert FabCheck._type_name(None) == "NoneType"
        assert FabCheck._type_name(int) == "int"
        assert FabCheck._type_name(float) == "float"
        assert FabCheck._type_name(str) == "str"
        assert FabCheck._type_name({}) == "dict"
        assert FabCheck._type_name([]) == "list"
        assert FabCheck._type_name(()) == "tuple"
        assert FabCheck._type_name(FabCheck) == "FabCheck"

        # Construct some FabCheck's to use in tests below:
        int_check: FabCheck = FabCheck("int", (int,))
        float_check: FabCheck = FabCheck("float", (float,))
        number_check: FabCheck = FabCheck("number", (int, float))
        str_check: FabCheck = FabCheck("str", (str,))
        optional_int: FabCheck = FabCheck("optional_int", (type(None), int))
        optional_float: FabCheck = FabCheck("optional_float", (type(None), float))
        optional_number: FabCheck = FabCheck(
            "optional_int_float", (type(None), int, float))
        optional_str: FabCheck = FabCheck("optional_str", (type(None), str))

        # All of the *good_pairs* should not generate an error:
        good_pairs: Sequence[Tuple[Any, FabCheck]] = (
            # Simple matches:
            (1, int_check),
            (1.0, float_check),
            (1, number_check),
            (1.0, number_check),
            ("", str_check),

            # Optional matches:
            (None, optional_int),
            (1, optional_int),
            (None, optional_float),
            (1.0, optional_float),
            (None, optional_number),
            (1, optional_number),
            (1.0, optional_number),
            (None, optional_str),
            ("", optional_str),
        )
        pair: Tuple[Any, FabCheck]
        values: Sequence[Any] = tuple([pair[0] for pair in good_pairs])
        checks: Sequence[FabCheck] = tuple([pair[1] for pair in good_pairs])
        error: str = FabCheck.check(values, checks)
        assert not error, f"Unexpected error='{error}'"

        # Each of the *bad_pairs* should generate an error:
        bad_pairs: Sequence[Tuple[Any, FabCheck]] = (
            (None, int_check),
            (1.0, int_check),
            (None, float_check),
            (1, float_check),
            (None, number_check),
        )
        value: Any
        check: FabCheck
        for value, check in bad_pairs:
            assert FabCheck.check((value,), (check,)), (
                f"{value=} {check=} did not fail")

        # Do some flags based checks:
        float_list_check: FabCheck = FabCheck("float_list_check", ("L", float))
        float_sequence_check: FabCheck = FabCheck("float_sequence_check", ("S", float))
        float_tuple_check: FabCheck = FabCheck("float_tuple_check", ("T", float))
        int_list_check: FabCheck = FabCheck("int_list_check", ("L", int))
        int_sequence_check: FabCheck = FabCheck("int_sequence_check", ("S", int))
        int_tuple_check: FabCheck = FabCheck("int_tuple_check", ("T", int))
        number_list_check: FabCheck = FabCheck("float_list_check", ("L", float, int))
        number_sequence_check: FabCheck = FabCheck("float_sequence_check", ("S", float, int))
        number_tuple_check: FabCheck = FabCheck("float_tuple_check", ("T", float, int))

        empty_list: List[Union[int, float]] = []
        empty_tuple: Tuple[Union[int, float], ...] = ()
        int_list: List[int] = [1, 2, 3]
        int_tuple: Tuple[int, ...] = (1, 2, 3)
        float_list: List[float] = [1.0, 2.0, 3.0]
        float_tuple: Tuple[float, ...] = (.0, 2.0, 3.0)
        number_list: List[Union[int, float], ...] = [1, 2.0, 3]
        number_tuple: Tuple[Union[int, float], ...] = (1, 2.0, 3)

        good_pairs: Sequence[Tuple[Any, FabCheck]] = (
            # Empty Checks:
            (empty_list, int_list_check),
            (empty_list, float_list_check),
            (empty_list, number_list_check),
            (empty_list, int_sequence_check),
            (empty_list, float_sequence_check),
            (empty_list, number_sequence_check),

            (empty_tuple, int_tuple_check),
            (empty_tuple, float_tuple_check),
            (empty_tuple, number_tuple_check),
            (empty_tuple, int_sequence_check),
            (empty_tuple, float_sequence_check),
            (empty_tuple, number_sequence_check),

            # Non_empty check:
            (int_list, int_list_check),
            (int_list, number_list_check),
            (int_list, int_sequence_check),
            (int_list, number_sequence_check),

            (float_list, float_list_check),
            (float_list, number_list_check),
            (float_list, float_sequence_check),
            (float_list, number_sequence_check),

            (number_list, number_list_check),
            (number_list, number_sequence_check),

            (int_tuple, int_tuple_check),
            (int_tuple, number_tuple_check),
            (int_tuple, int_sequence_check),
            (int_tuple, number_sequence_check),

            (float_tuple, float_tuple_check),
            (float_tuple, number_tuple_check),
            (float_tuple, float_sequence_check),
            (float_tuple, number_sequence_check),

            # (number_tuple, number_tuple_check),
            (number_tuple, number_sequence_check),
        )

        bad_pairs: Sequence[Tuple[Any, FabCheck]] = (
            (int_tuple, int_list_check),
            (float_tuple, int_list_check),
            (number_tuple, int_list_check),
            (float_list, int_list_check),
            (number_list, int_list_check),
            (int_list, float_list_check),
            (number_list, float_list_check),
        )

        index: int
        value: Any
        check: FabCheck
        good_pair: Tuple

        good_pair: Tuple[Any, FabCheck]
        for index, good_pair in enumerate(good_pairs):
            value, check = good_pair
            assert isinstance(check, cls), check
            error = FabCheck.check((value,), (check,))
            assert not error, f"[{index}]: {value=} {check=} {error=}"

        value: Any
        check: FabCheck
        for value, check in bad_pairs:
            assert isinstance(check, cls)
            error = FabCheck.check((value,), (check,))
            assert error, "No error generated"

        # Test non sequence checks:
        non_empty_string_check: FabCheck = FabCheck("Name", ("+", str))
        value_error: str = FabCheck.check(("non-empty",), (non_empty_string_check,))
        assert value_error == "", f"{value_error=}"
        value_error = FabCheck.check(("",), (non_empty_string_check,))
        assert value_error == "[0]: Argument 'Name' has no length", value_error

        # Test FabCheck.init_show():
        checks: Tuple[FabCheck, ...] = (
            int_check,
            str_check,
            optional_int,
            optional_str,
            optional_float
        )
        result: str = FabCheck.init_show("Foo", (1, "a", 1, "b", 1.0), checks)
        assert result == "Foo(1, 'a', 1, 'b', 1.0)", result
        result: str = FabCheck.init_show("Foo", (1, "a", 1, "b", None), checks)
        assert result == "Foo(1, 'a', 1, 'b')", result
        result: str = FabCheck.init_show("Foo", (1, "a", 1, None, None), checks)
        assert result == "Foo(1, 'a', 1)", result
        result: str = FabCheck.init_show("Foo", (1, "a", None, None, None), checks)
        assert result == "Foo(1, 'a')", result
        result: str = FabCheck.init_show("Foo", (1, "a", None, None, 1.0), checks)
        assert result == "Foo(1, 'a', optional_float=1.0)", result
        result: str = FabCheck.init_show("Foo", (1, "a", None, "b", 1.0), checks)
        assert result == "Foo(1, 'a', optional_str='b', optional_float=1.0)", result
        result: str = FabCheck.init_show("Foo", (1, "a", None, None, 1.0), checks)
        assert result == "Foo(1, 'a', optional_float=1.0)", result
        try:
            FabCheck.init_show("Foo", (), checks)  # Arguments/FabCheck's misamtch.
        except ValueError as value_error:
            assert str(value_error) == "Arguments size (0) != checks size (5)", str(value_error)
        try:
            FabCheck.init_show("Foo", (0,), (cast(FabCheck, 0),))
        except ValueError as value_error:
            assert str(value_error) == "0 is not an FabCheck", str(value_error)
        try:
            FabCheck.init_show(cast(str, 0), (0,), (int_check,))
        except ValueError as value_error:
            assert str(value_error) == "0 is not a string", str(value_error)


# FabColor:
class FabColor(object):
    """FabColor: Convert from SVG color names to FreeCAD HSL."""

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
        """Convert Scalable Vector Graphics color to Hue/Saturation/Value tuple.

        Arguments:
        * *svg_color_name* (str): The SVG color name to use.

        Returns:
        * (Tuple[float, float, float]) as HSV (Hue/Satruation/Value) tuple used by FreeCAD.

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


# Miscellaneous functions:

# float_fix():
def float_fix(length: float) -> float:
    """Return a length that is rounded to a whole number when appropriate."""
    is_negative: bool = length < 0.0
    if is_negative:
        length = -length

    whole: float
    fractional: float
    whole, fractional = divmod(length, 1.0)

    epsilon: float = 1.0e-8
    if abs(fractional) < epsilon:
        fractional = 0.0
    if abs(fractional - 1.0) < epsilon:
        fractional = 0.0  # pragma: no unit cover
        whole += 1.0  # pragma: no unit cover
    fixed_length: float = whole + fractional
    if is_negative:
        fixed_length = -fixed_length
    if abs(fixed_length) == 0.0:
        fixed_length = 0.0
    return fixed_length


# vector_fix():
def vector_fix(vector: Vector) -> Vector:
    """Return Vector with values rounded to appropriate hole numbers."""
    return Vector(float_fix(vector.x), float_fix(vector.y), float_fix(vector.y))


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

    INIT_CHECKS = (
        FabCheck("Name", ("T+", str)),
        FabCheck("Color", (str,)),
    )

    # FabMaterial.__init__():
    def __post_init__(self) -> None:
        """Post process."""
        arguments = (self.Name, self.Color)
        value_error: str = FabCheck.check(arguments, FabMaterial.INIT_CHECKS)
        if value_error:
            raise ValueError(value_error)
        assert isinstance(self.Name, tuple)
        if len(self.Name) == 0:
            raise ValueError("Material is an empty tuple.")
        name: str
        for name in self.Name:
            if not name:
                raise ValueError("Name contains an empty string")
        if not self.Color:
            raise ValueError("Color name is empty")

    def __repr__(self) -> str:
        """Return string representation of FabMaterial."""
        return self.__str__()

    def __str__(self) -> str:
        """Return string representation of FabMaterial."""
        return f"FabMaterial({self.Name}, '{self.Color}')"

    @staticmethod
    def _unit_tests() -> None:
        """Run FabMaterial unit tests."""
        name: Tuple[str, ...] = ("brass",)
        color: str = "orange"
        material: FabMaterial = FabMaterial(name, color)
        assert material.__repr__() == "FabMaterial(('brass',), 'orange')"
        assert f"{material}" == "FabMaterial(('brass',), 'orange')", f"{material}"
        material_text: str = f"FabMaterial({name}, '{color}')"
        assert f"{material}" == material_text, f"{material}"

        # Name is not a Tuple:
        try:
            FabMaterial(cast(tuple, 0), color)
        except ValueError as value_error:
            want: str = "[0]: Argument 'Name' is not a tuple"
            got: str = str(value_error)
            assert want == got, (want, got)

        # Name is empty tuple:
        try:
            FabMaterial((), color)
        except ValueError as value_error:
            assert str(value_error) == "Material is an empty tuple.", str(value_error)

        # Name with an empty string:
        try:
            FabMaterial(("",), color)
        except ValueError as value_error:
            assert str(value_error) == "Name contains an empty string", str(value_error)

        # Name is does not have a string:
        try:
            FabMaterial((cast(str, 1),), color)
        except ValueError as value_error:
            want = "[0]: 1 (int) is not of type ['str']"
            got = str(value_error)
            assert got == want, (got, want)

        # Color is empty.
        try:
            FabMaterial(("Brass",), "")
        except ValueError as value_error:
            assert str(value_error) == "Color name is empty", str(value_error)


def _misc_unit_tests() -> None:
    """Test helper functions."""
    # Test float_fix():
    assert float_fix(0.0) == 0.0, "Zero fail"
    assert float_fix(1.0) == 1.0, "1.0 fail"
    assert float_fix(-1.0) == -1.0, "-1.0 fail"
    assert float_fix(0.5) == 0.5, "0.5 fail"
    assert float_fix(-0.5) == -0.5, "-0.5 fail"
    epsilon: float = 1.0e-11
    assert float_fix(epsilon) == 0.0, "epsilon fail"
    assert float_fix(-epsilon) == 0.0, "-epsilon fail"
    assert float_fix(1 - epsilon) == 1.0, "1-epsilon fail"
    assert float_fix(1 + epsilon) == 1.0, "1+epsilon fail"
    assert float_fix(-1 - epsilon) == -1.0, "-1-epsilon fail"
    assert float_fix(-1 + epsilon) == -1.0, "-1+epsilon fail"

    # Test vector_fix():
    return vector_fix(Vector(epsilon, 1.0 - epsilon, -1.0 + epsilon)) == Vector(0.0, 0.0, 0.0)


def _unit_tests() -> None:
    """Run the unit tests."""
    _misc_unit_tests()
    FabCheck._unit_tests()
    FabColor._unit_tests()
    FabMaterial._unit_tests()


if __name__ == "__main__":
    _unit_tests()
