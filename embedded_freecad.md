# Embedded FreeCAD

It is totally awesome that FreeCAD exposes a much of its internals via Python interfaces.
There are multiple ways of accessing these FreeCAD Python interfaces.
The pros and cons of each FreeCAD Python access method are discussed in this document.

This document is Linux focused, since the original author uses neither Windows nor MacOS.

## The FreeCAD and FreeCADGui Modules

There are two top level modules in FreeCAD:
* FreeCAD:
  This module is the top level module primarily for managing FreeCAD geometry.
  This module is typically abbreviated as App (e.g. `import FreeCAD as App`.)
* FreeCADGui:
  This module is used for accessing the GUI (Graphical User Interface)
  presentation issues such as visibility, transparency, color, views, etc.
  This module is typically abbreviated as Gui (e.g. `import FreeCADGui as Gui`.)
All FreeCAD environments always have the FreeCAD module loaded.
Some FreeCAD environments have the FreeCADGui module loaded and some do not.
It should be noted that some FreeCAD environments that do have FreeCADGui loaded,
only have a very limited amount of available methods.
Any Python code that needs to access the FreeCADGui module needs to ensure
it the full set of methods before trying to manipulate the presentation side of FreeCAD.

## FreeCAD Macros

The most common way of importing Python code into a FreeCAD Python environment is
via FreeCAD macros.
A FreeCAD macro is basically Python program that typically has either `.py` suffix or
the more common (for FreeCAD) `.FCMacro` suffix.
The most common place where macro files reside is in the `~/.FreeCAD` directory,
where `~` stands for current user home directory on Linux.
All of the macros in this director are available via the [Macro] tab
at the top line of FreeCAD window.

It is also possible to directly execute a Python program via:

     freecad19 my_code.FCStd

This will bring the FreeCAD application and execute the Python code in `my_code.FCStd`.
Once the code in `my_code.FCStd` has some executed,
the FreeCAD application can be used to inspect the results of the code execution.
It is possible to add a small piece of code at the end of `my_code.FCStd` that
saves out its results into a `.FCstd` document and then shuts down the FreeCAD application.
In this situation, the FreeCAD application pops up a window, runs `my_code.FCStd`,
and then shuts down the application window and exits.
In this mode, Python code must be run on a machine with display,
since it will not successfully run on a headless machine.

One final comment is that many editors look at the file suffix to enable Python mode
(e.g. color highlighting, automatic indentation, etc.)
Python code with a `.FCStd` will typically not enable Python mode.
A clever solution is to add a symbolic link (e.g. `ln -s my_code.FCStd my_code.py`)
and point the editor at the `.py` file.

Another note is that neither the FreeCAD application or the FreeCAD console
(see section immediately below) honor the `PYTHONPATH` environment variable.
This is deliberate and ensures that is the exact same Python environment that is not
effected by other Python applications that require PYTHONPATH modifications to properly operate.
The workaround is add code to explictly modify `sys.path` as discussed a bit further below.

## Standalone FreeCAD Console

It is also possible to directly bring up the FreeCAD console by:

     freecad19 -c

This brings up a standard Python configured with access to all of the FreeCAD python modules.
In this mode,
the FreeCADGui module can be imported (i.e. `import FreeCADGui as Gui`),
but it has much reduced functionality.
Running `dir(Gui)` in this mode will show a very minimal list of attributes/methods.
Current the methods are `embedToWindow`, `exec_loop`, `setupWithoutGUI1, and `showMainWindow`.
In general, no attempt should be made to do GUI operations from this console session.

To list all of the available modules available to import in this environment type:

     sorted(tuple(sys.modules.keys()))

The `~/FreeCAD` directory is in the default path for the console.
Thus, any Python modules (i.e. has a `.py` suffix) in this directory are available for importing.
The files ending with a `.FCMacro` suffix are not importable.

## FreeCAD in "Embedded Mode"

In "embedded mode", a standard Python interpreter is run and it is configured to be able
access all of the FreeCAD modules.
By using a standard Python interpreter,
it is possible add additional needed packages and modules using `python3 -m pip install ...`.
For example, it is possible to install debugger, test suite harness, code coverage, etc.

Since Python is constantly adding and deprecating features,
it is important use to run a Python with the same major and minor version numbers.
In order get the version information, type the following into the Python console:

     import sys
     sys.version_info
     # Should print something like "sys.version_info(major=3, minor=8, micro=5, ...")

Only the `major` and `minor` version matter.
This should be done using the both FreecCAD console (i.e. `freecad19 -c`) and
another Python interpreter (i.e. `python3`).

Next, it necessary to find a consistent FreeCAD system.
One possibility is to download and build FreeCAD from source.
However, it is probably easier is to just download one of the FreeCAD AppImage's,
and extract the required files.
For example:

     freecad19 --appimage-extract

will create the `squashfs-root` directory that contains consistent files.
All of the relevant files are in `squashfs-root/usr/lib` which can readily
be added to the python interpreter path.
The easiest way is to simply add `squashfs-root/usr/lib` to the `PYTHONPATH`
environment variable:

     export PYTHONPATH="$PYTHONPATH:squashfs-root/usr/lib"

will do the trick.
Alternatively, Python code can be used to accomplish the same task:

     import sys
     sys.path.append("./squashfs-root/usr/lib")

## Dual Mode FreeCAD Python Program

A dual mode Python program is one can be run as both FreeCAD macro and in embedded mode.
The idea is shown immediately below:

     # Create my_code.py
     ln -s my_code.py my_mycode.FCMacro  # Make a symbolic link for my_code.FCMacro
     python3 my_code.py                  # Run mycode.py in embedded mode
     freecad19 mycode.FCMacro            # Run mycode.FCMacro through the FreeCAD application

The first run will produce all of the geometry and second one has access to the FreeCADGui
module and can add additional presentation information.

There needs to be a preamble in `mycode.py` that sets up the paths.
This code looks as follows:

     import os
     import sys
	
     assert os.version_info.major == 3  # Python 3.x
     assert os.version_info.minor == 8  # Python 3.8
     sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])

     import FreeCAD as App
     import FreeCADGui as Gui
     gui: bool = hasattr(Gui, "getMainWindow")  # Only present when Gui is active

