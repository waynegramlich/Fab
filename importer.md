# importer: Searches/imports Python modules.

Ideally, all search paths for finding Python modules are pre-configured. Sometimes,
the desired modules are placed elsewhere in the system and a little searching
is needed to find them.  This module provides a convenient searching mechanism.

### 0.1 search

def *search*( *module\_name*:  *str*, *executable\_name*:  *str* = "", *search\_paths*:  Tuple[Path, ...] = (), *tracing*:  *str* = "" ) -> Tuple[Optional[ModuleType], Optional[ModuleType]]:

Search for a module in multiple locations.

Sometimes a Python environment is already set up to import a desired module.
In this, case it is imported and returned.  Otherwise, a search will take place
looking for it.  If it is found, the path is updated to include it.  A list
of search paths are provided to look elsewhere for the library.  If the path is
a relative path, it searched for relative to the directory that contains an executable.

* Arguments:
  * *module\_name* (str):
    Name of the module to import.
  * *executable\_name* (str):
    The name of the executable to use to use as the base for relative search paths.
  * *search\_paths* (Tuple[Path, ...]):
    A list of paths to search for the module.
    (Default: (Path("squashfs-root") / "usr" / "lib",) for an extracted AppImage.)
  * *tracing*: (str):
    If present, tracing output is generated.
* Returns:
  * (Optional[ModuleType) the module that was found using pre-existing path; otherwise None.
  * (Optional[ModuleType]) the module that was found using *search\_paths*; otherwise None.
  * Note that:
    * (ModuleType, None): *module\_name* is already in path and no further search is performed.
    * (None, ModuleType): *module\_name* was found after searching.
    * (None, None): *module\_name* not found at all.
* Raises:
  * RunTimeError if relative path expansion can not find the associated *executabe\_name*.


### 0.2 unit\_test

def *unit\_test*() -> None:

Test the module manager.

