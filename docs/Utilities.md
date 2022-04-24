# Utilities: FabUtilities: Miscellaneous Fab package classes.
The Utility classes are:
* FabColor:
  This is a class for converting SVG (Scalable Vector Graphics) color names into
  RBG (Red/Green/Blue) triples.
* FabMaterial:
  This is a class that describes material properties.
* FabToolController:
  This roughly corresponds to a FreeCAD Path library tool controller which basically specifies
  CNC speeds and feeds.

## Table of Contents (alphabetical order):

* 1 Class: [FabColor](#utilities--fabcolor):
* 2 Class: [FabMaterial](#utilities--fabmaterial):
* 3 Class: [FabToolController](#utilities--fabtoolcontroller):
  * 3.1 [to_json()](#utilities----to-json): Return a dictionary containing the controller information.

## <a name="utilities--fabcolor"></a>1 Class FabColor:

Convert from SVG color names to FreeCAD RGB triples.


## <a name="utilities--fabmaterial"></a>2 Class FabMaterial:

Represents a stock material.
Other properties to be added later (e.g. transparency, shine, machining properties, etc.)

Attributes:
* *Name* (Tuple[str, ...]): A list of material names from generict to specific.
* *Color* (str): The color name to use.


## <a name="utilities--fabtoolcontroller"></a>3 Class FabToolController:

Speeds/Feeds information.
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

### <a name="utilities----to-json"></a>3.1 `FabToolController.`to_json():

FabToolController.to_json(self) -> Dict[str, Any]:

Return a dictionary containing the controller information.



