# FabToolBits: FabToolBits: Toop Bit classes.
This module provides one class for each different kind of supported tool bit.
Instatiations of these tool bits live in the `.../Tool/Bit/*.fctb`.
Each of these clases is a sub-class of the FabBit class defined in the FabToolTemplates module.

The classes are:
  * FabBallEndBit: This corresponds to `Tools/Shape/ballend.fcstd`.
  * FabBullNoseBit: This corresponds to `Tools/Shape/bullnose.fcstd`.
  * FabChamferBit: This corresponds to `Tools/Shape/chamfer.fcstd`.
  * FabDrillBit: This corresponds to `Tools/Shape/drill.fcstd`.
  * FabEndMillBit: This corresponds to `Tools/Shape/endmill.fcstd`.
  * FabProbeBit: This corresponds to `Tools/Shape/probe.fcstd`.
  * FabSlittingSawBit: This corresponds to `Tools/Shape/slittingsaw.fcstd`.
  * FabThreadMillBit: This corresponds to `Tools/Shape/thread-mill.fcstd`.

## Table of Contents (alphabetical order):

* 1 Class: [FabBallEndBit](#fabtoolbits--fabballendbit):
* 2 Class: [FabBullNoseBit](#fabtoolbits--fabbullnosebit):
* 3 Class: [FabChamferBit](#fabtoolbits--fabchamferbit):
* 4 Class: [FabDoveTailBit](#fabtoolbits--fabdovetailbit):
* 5 Class: [FabDrillBit](#fabtoolbits--fabdrillbit):
* 6 Class: [FabEndMillBit](#fabtoolbits--fabendmillbit):
* 7 Class: [FabProbeBit](#fabtoolbits--fabprobebit):
* 8 Class: [FabSlittingSawBit](#fabtoolbits--fabslittingsawbit):
* 9 Class: [FabThreadMillBit](#fabtoolbits--fabthreadmillbit):
* 10 Class: [FabVBit](#fabtoolbits--fabvbit):

## <a name="fabtoolbits--fabballendbit"></a>1 Class FabBallEndBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeHeight* (Union[str, float]): The ball end cutting edge height.
* *Diameter* (Union[str, float]): The ball end cutter diameter.
* *Length* (Union[str, float]): The total length of the ball end.
* *ShankDiameter: (Union[str, float]): The ball end shank diameter.

Constructor:
* FabBallEndBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)


## <a name="fabtoolbits--fabbullnosebit"></a>2 Class FabBullNoseBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
* *Diameter* (Union[str, float]): The bull nose cutter diameter.
* *FlatRadius* (Union[str, float]): The flat radius of the bull nose cutter.
* *Length* (Union[str, float]): The total length of the bull nose cutter.
* *ShankDiameter: (Union[str, float]): The shank diameter.

Constructor:
* FabBullNoseBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)


## <a name="fabtoolbits--fabchamferbit"></a>3 Class FabChamferBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle.
* *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
* *Diameter* (Union[str, float]): The chamfer outer diameter.
* *Length* (Union[str, float]): The total length of the chamfer cutter.
* *ShankDiameter: (Union[str, float]): The shank diameter.
* *TipDiameter* (Union[str, float]): The tip radius of the chamfer cutter.

Constructor:
* FabChamferBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)


## <a name="fabtoolbits--fabdovetailbit"></a>4 Class FabDoveTailBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle.
* *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
* *Diameter* (Union[str, float]): The chamfer outer diameter.
* *Length* (Union[str, float]): The total length of the chamfer cutter.
* *NeckDiameter* (Union[str, float]): The diameter of the neck between the cutter and shank
* *NeckHeight* (Union[str, float]): The height of the neck between the cutter and shank
* *ShankDiameter: (Union[str, float]): The shank diameter.
* *TipDiameter* (Union[str, float]): The tip radius of the chamfer cutter.

Constructor:
* FabDoveTailBit("Name", BitFile, Shape, Attributes, CuttingEdgeAngle, CuttingEdgeHeight,
  Diameter, Length, NeckDiameter, NeckHeight,  ShankDiameter, TipDiameter)


## <a name="fabtoolbits--fabdrillbit"></a>5 Class FabDrillBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle.
* *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
* *Diameter* (Union[str, float]): The drill outer diameter.
* *Length* (Union[str, float]): The total length of the drill cutter.
* *TipAngle: (Union[str, float]): The drill tip point angle.

Constructor:
* FabDrillBit("Name", BitFile, Shape, Attributes, Diameter, Length, TipAngle)


## <a name="fabtoolbits--fabendmillbit"></a>6 Class FabEndMillBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeHeight* (Union[str, float]): The end mill cutting edge height.
* *Diameter* (Union[str, float]): The end mill cutter diameter.
* *Length* (Union[str, float]): The total length of the end mill.
* *ShankDiameter: (Union[str, float]): The end millshank diameter.

Constructor:
* FabEndMillBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)


## <a name="fabtoolbits--fabprobebit"></a>7 Class FabProbeBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *Diameter* (Union[str, float]): The probe ball diameter.
* *Length* (Union[str, float]): The total length of the probe.
* *ShaftDiameter: (Union[str, float]): The probe shaft diameter.

Constructor:
* FabProbeBit("Name", BitFile, Shape, Attributes, Diameter, Length, TipAngle)


## <a name="fabtoolbits--fabslittingsawbit"></a>8 Class FabSlittingSawBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *BladeThickness* (Union[str, float]): The cutting saw blade thickness.
* *CapDiameter* (Union[str, float]): The cutting saw end cab diameter.
* *CapHeight* (Union[str, float]): The cutting end end cab height.
* *Diameter* (Union[str, float]): The cutting saw blade diameter.
* *ShankDiameter: (Union[str, float]): The cutting saw shank diameter.

Constructor:
* FabSlittingSawBit("Name", BitFile, Shape, Attributes,
  BladeThickness, CapDiameter, CapHeight, Diameter, Length, ShankDiameter)


## <a name="fabtoolbits--fabthreadmillbit"></a>9 Class FabThreadMillBit:

An thread mill bit template.
Attributes:
* *Name* (str): The name of thread mill bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingAngle* (Union[str, float]): The cutter point angle.
* *Crest* (Union[str, float]): The thread cutter crest thickness.
* *Diameter* (Union[str, float]): The chamfer outer diameter.
* *Length* (Union[str, float]): The total length of the chamfer cutter.
* *NeckDiameter* (Union[str, float]): The diameter of the neck between the cutter and shank
* *NeckLength* (Union[str, float]): The height of the neck between the cutter and shank
* *ShankDiameter: (Union[str, float]): The shank diameter.

Constructor:
* FabThreadMillBit("Name", BitFile, Shape, Attributes, Cuttingngle, Diameter, Length,
  NeckDiameter, NeckLength,  ShankDiameter)


## <a name="fabtoolbits--fabvbit"></a>10 Class FabVBit:

An V groove bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeAngle* (Union[str, float]): The cutting edge angle.
* *CuttingEdgeHeight* (Union[str, float]): The cutting edge height.
* *Diameter* (Union[str, float]): The v outer diameter.
* *Length* (Union[str, float]): The total length of the v cutter.
* *ShankDiameter: (Union[str, float]): The shank diameter.
* *TipDiameter* (Union[str, float]): The tip radius of the v cutter.

Constructor:
* FabVBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)



