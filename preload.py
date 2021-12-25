# A quick program that brings up a FreeCAD Python console.
#
# Usage:
#    python3 -i preload.py


import sys
sys.path.append(".")
import Embed
Embed.setup()

import FreeCAD as App
import FreeCADGui as Gui
from FreeCAD import BoundBox, Matrix, Placement, Rotation, Vector  # type: ignore

