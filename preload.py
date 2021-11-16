# A quick program that brings up a FreeCAD Python console.
#
# Usage:
#    python3 -i preload.py


import os
import sys

assert sys.version_info.major == 3, "Python 3.x is not running"
assert sys.version_info.minor == 8, "Python 3.8 is not running"
sys.path.extend([os.path.join(os.getcwd(), "squashfs-root/usr/lib"), "."])

import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import BoundBox, Matrix, Placement, Rotation, Vector  # type: ignore

