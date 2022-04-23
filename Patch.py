#!/usr/bin/env python3
"""Patch: A program to patch some FreeCAD files.

The FreeCAD 0.19 Path library has a bug that make it essentailly impossible to support more
than 1 job from a Python program without using the GUI.  This bug has been fixed in the
FreeCAD 0.20 version of the library.  The code in this module patchs the files in the
`PathScripts` directory to fix the problem.

This done in the following steps:

1. Extract the files from the FreeCAD AppImage.

   ```
   freecad19 --appimage-extract
   ```

   This creates a `squashfs-root` directory tree.

2. Run this program to patch the files

   ```
   python3 Patch.py  # In the same directory that contains `squashfs-root`.
   ```

3. Download `appimagetool`:

   ```
   # This only needs to be done once:
   wget https://github.com/AppImage/AppImageKit/releases/download/13/appimagetool-x86_64.AppImage \
      -o appimagetool
   chmod +x appimagetool
   ```

4. Use `appimagetool` to repackage everything:

   ```
   ./appimagetool squashf-root
   chmod +x ./FreeCAD_Conda-x86_64.AppImage
   ```

   The resulting output is `FreeCAD_Conda-x86_64.AppImage` which can be renamed:

   ```
   mv FreeCAD_Conda-x86_64.AppImage freecad19
   ```

"""

from pathlib import Path as PathFile
from typing import Dict, IO, List, Tuple


# Patch function is needed to patch each file:
def patch(path_scripts_directory: PathFile,
          package_name: str, patches: Dict[str, Tuple[str, ...]]) -> int:
    """Patch a package."""

    # Read in *module_path_file* and write it back out:
    module_path_file: PathFile = path_scripts_directory / f"{package_name}.py"
    module_file: IO[str]
    old_module_text: str
    with open(module_path_file) as module_file:
        old_module_text = module_file.read()
    old_lines: List[str] = old_module_text.split("\n")

    # Perform the *patches*:
    modified: int = 0
    new_lines: List[str] = []
    line: str
    index: int
    for index, line in enumerate(old_lines):
        patch_pattern: str
        replace_lines: Tuple[str, ...]
        for patch_pattern, replace_lines in patches.items():
            if line == patch_pattern:
                new_lines.extend(replace_lines)
                modified += 1
                break
        else:
            new_lines.append(line)

    if modified:
        # Make a copy with a suffix of `.orig` to make it easier to do diffs:
        with open(path_scripts_directory / f"{package_name}.py.orig", "w") as module_file:
            module_file.write(old_module_text)

        # Write *new_lines* out:
        with open(module_path_file, "w") as module_file:
            module_file.write("\n".join(new_lines))
    print(f"{package_name}: {modified} modifications of {len(patches)} performed")
    return modified


def main() -> None:
    # Perform the patches to add the `parentJob` argument to the necessary files:
    path_scripts_directory: PathFile = (
        PathFile(".") / "squashfs-root" / "usr" / "Mod" / "Path" / "PathScripts")
    modified: int = 0
    modified += patch(path_scripts_directory, "PathOp", {
        "    def __init__(self, obj, name):": (
            "    def __init__(self, obj, name, parentJob=None):",
        ),
        ("        if not hasattr(obj, 'DoNotSetDefaultValues') or "
         "not obj.DoNotSetDefaultValues:"): (
            ("        if not hasattr(obj, 'DoNotSetDefaultValues') or "
             "not obj.DoNotSetDefaultValues:  # Modified"),
            "            jobname = None",
            "            if parentJob:",
            "                jobname=parentJob.Name",
            "                self.job = PathUtils.addToJob(obj, jobname=jobname)",
        ),
        "            job = self.setDefaultValues(obj)": (
            "            job = self.setDefaultValues(obj, jobname=jobname)",
        ),
        "    def setDefaultValues(self, obj):": (
            "    def setDefaultValues(self, obj, jobname=None):",
        ),
        "        job = PathUtils.addToJob(obj)": (
            "        job = PathUtils.addToJob(obj, jobname)",
        
        ),
    })
    patch(path_scripts_directory, "PathProfile", {
        "def Create(name, obj=None):": (
            "def Create(name, obj=None, parentJob=None):",
        ),
        "    obj.Proxy = ObjectProfile(obj, name)": (
            "    obj.Proxy = ObjectProfile(obj, name, parentJob)",
        )
    })
    patch(path_scripts_directory, "PathDrilling", {
        "def Create(name, obj=None):": (
            "def Create(name, obj=None, parentJob=None):",
        ),
        "    obj.Proxy = ObjectDrilling(obj, name)": (
            "    obj.Proxy = ObjectDrilling(obj, name, parentJob)",
        )
    })
    patch(path_scripts_directory, "PathPocket", {
        "def Create(name, obj=None):": (
            "def Create(name, obj=None, parentJob=None):",
        ),
        "    obj.Proxy = ObjectPocket(obj, name)": (
            "    obj.Proxy = ObjectPocket(obj, name, parentJob)",
        )
    })
    patch(path_scripts_directory, "PathUtils", {
        "    if jobname is not None:": (
            "    assert jobname is not None, 'No jobname specified'",
            "    if jobname is not None:",
        )
    })
    print(f"{modified} modifications made.")


if __name__ == "__main__":
    main()
