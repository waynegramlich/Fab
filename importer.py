#!/usr/bin/env python3
"""
importer: Searches/imports Python modules.

Ideally, all search paths for finding Python modules are pre-configured. Sometimes,
the desired modules are placed elsewhere in the system and a little searching
is needed to find them.  This module provides a convenient searching mechanism.

"""

# <--------------------------------------- 100 characters ---------------------------------------> #

import importlib
from pathlib import Path
import shutil
import sys
from types import ModuleType
from typing import Optional, List, Tuple

# Ensure that FreeCADGui package is imported:


# search():
def search(
        module_name: str,
        executable_name: str = "",
        search_paths: Tuple[Path, ...] = (),
        tracing: str = ""
) -> Tuple[Optional[ModuleType], Optional[ModuleType]]:
    """Search for a module in multiple locations.

    Sometimes a Python environment is already set up to import a desired module.
    In this, case it is imported and returned.  Otherwise, a search will take place
    looking for it.  If it is found, the path is updated to include it.  A list
    of search paths are provided to look elsewhere for the library.  If the path is
    a relative path, it searched for relative to the directory that contains an executable.

    * Arguments:
      * *module_name* (str):
        Name of the module to import.
      * *executable_name* (str):
        The name of the executable to use to use as the base for relative search paths.
      * *search_paths* (Tuple[Path, ...]):
        A list of paths to search for the module.
        (Default: (Path("squashfs-root") / "usr" / "lib",) for an extracted AppImage.)
      * *tracing*: (str):
        If present, tracing output is generated.
    * Returns:
      * (Optional[ModuleType) the module that was found using pre-existing path; otherwise None.
      * (Optional[ModuleType]) the module that was found using *search_paths*; otherwise None.
      * Note that:
        * (ModuleType, None): *module_name* is already in path and no further search is performed.
        * (None, ModuleType): *module_name* was found after searching.
        * (None, None): *module_name* not found at all.
    * Raises:
      * RunTimeError if relative path expansion can not find the associated *executabe_name*.

    """
    # Set the default *search_paths* and do *tracing*:
    if not search_paths:
        search_paths = (Path("squashfs-root") / "usr" / "lib", )
    if tracing:
        print(f"{tracing}=>search({tracing}embedded.import_module('{module_name}', "
              f"'{str(executable_name)}', {search_paths}")

    # Attempt to import via a simple import.
    before_module: Optional[ModuleType] = None
    after_module: Optional[ModuleType] = None
    try:
        before_module = importlib.import_module(module_name)
    except ModuleNotFoundError:
        # Determine the absolute path of *executable_name*:
        executable_path: Optional[Path] = None

        # Sweep through *search_paths* looking for a match:
        sys_path: List[str] = sys.path
        search_path: Path
        for search_path in search_paths:
            # Ensure that *search_path* is an absolute path.
            if not search_path.is_absolute():
                if not executable_path:
                    executable_which: Optional[str] = shutil.which(executable_name)
                    if not executable_which:
                        raise RuntimeError("Unable to find executable '{executable_name}'")
                    executable_path = Path(executable_which).resolve()
                search_path = executable_path.parent / search_path

            # Try to find the module:
            search_path_text: str = str(search_path)
            if search_path_text not in sys_path:
                sys.path.append(str(search_path))
                try:
                    after_module = importlib.import_module(module_name)
                except ModuleNotFoundError:
                    pass
                if after_module:
                    break
            sys_path.remove(search_path_text)

    if tracing:
        print(f"{tracing}<=search('{module_name}', '{str(executable_name)}', {search_paths}) => "
              f"{before_module}, {after_module}")
    return before_module, after_module


# unit_test():
def unit_test() -> None:
    """Test the module manager."""
    before: Optional[ModuleType] = None
    after: Optional[ModuleType] = None

    # Generate RuntimeError if bad executable:
    try:
        before, after = search("framus", "bogus")
        assert False, "Should generate RuntimeError and it did not."  # pragma: no unit cover
    except RuntimeError:
        pass

    # Search for a bogus file:
    before, after = search("bogus", "freecad19")
    assert not before and not after, "bogus was found"

    # Search for a module that is already in the path.
    before, after = search("subprocess", "")
    assert before and not after, "Should have found subprocess"

    # Search for a module that needs searching
    before, after = search("FreeCADGui", "freecad19")
    assert not before and after, "FreeCADGUI not found"


if __name__ == "__main__":
    if "--unit-test" in sys.argv:
        unit_test()
