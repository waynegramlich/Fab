# Utilities: Utilities: Convenice class.
The Utilitly classes are:
* FabCheck:
  This is some common code to check argument types for public functions.
* FabMaterial:
  This is a class that describes material properties.
  sub-class of Vector.

## Table of Contents (alphabetical order):

* 1 Class: [FabCheck](#utilities--fabcheck):
* 2 Class: [FabColor](#utilities--fabcolor):
* 3 Class: [FabMaterial](#utilities--fabmaterial):

## <a name="utilities--fabcheck"></a>1 Class FabCheck:

Check arguments for type mismatch errors.
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


## <a name="utilities--fabcolor"></a>2 Class FabColor:

Convert from SVG color names to FreeCAD HSL.


## <a name="utilities--fabmaterial"></a>3 Class FabMaterial:

Represents a stock material.
Other properties to be added later (e.g. transparency, shine, machining properties, etc.)

Attributes:
* *Name* (Tuple[str, ...]): A list of material names from generict to specific.
* *Color* (str): The color name to use.



