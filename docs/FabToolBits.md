# FabToolBits: FabToolBits: Toop Bit classes.
This module provides one class for each different kind of supported tool bit.
Instatiations of these tool bits live in the `.../Tools/Bit/` directory with a suffix of `.fctb`.
Each of the classes below is a sub-class of the FabBit class defined in the FabToolTemplates module.

The classes are:
  * FabBallEndBit: This corresponds to `Tools/Shape/ballend.fcstd`.
  * FabBullNoseBit: This corresponds to `Tools/Shape/bullnose.fcstd`.
  * FabChamferBit: This corresponds to `Tools/Shape/chamfer.fcstd`.
  * FabDoveTailBit: This corresponds to `Tools/Shape/dovetail.fcstd`.
  * FabDrillBit: This corresponds to `Tools/Shape/drill.fcstd`.
  * FabEndMillBit: This corresponds to `Tools/Shape/endmill.fcstd`.
  * FabProbeBit: This corresponds to `Tools/Shape/probe.fcstd`.
  * FabSlittingSawBit: This corresponds to `Tools/Shape/slittingsaw.fcstd`.
  * FabThreadMillBit: This corresponds to `Tools/Shape/thread-mill.fcstd`.
  * FabVBit: This corresponds to `Tools/Shape/v-bit.fcstd`.

The FabBit sub-class defines the following 4 attributes which is present in every FabBit sub-class:
  * *Name* (str): The name of Ball End bit.
  * *BitFile* (PathFile): The `.fctb` file.
  * *Shape* (FabShape): The associated `.fcstd` shape.
  * *Attributes* (FabAttributes): Any associated attributes.
Both FabShape and FabAttributes are also defined in the FabTemplates module as well.

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

An ball end bit template.
Attributes:
* *Name* (str): The name of Ball End bit.
* *BitFile* (PathFile): The ball end `.fctb` file.
* *Shape* (FabShape): The associated ball end `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated ball end attributes.
* *CuttingEdgeHeight* (Union[str, float]): The ball end cutting edge height.
* *Diameter* (Union[str, float]): The ball end cutter diameter.
* *Length* (Union[str, float]): The total length of the ball end.
* *ShankDiameter: (Union[str, float]): The ball end shank diameter.

Constructor:
* FabBallEndBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)


## <a name="fabtoolbits--fabbullnosebit"></a>2 Class FabBullNoseBit:

An bull nose bit template.
Attributes:
* *Name* (str): The name of Bull Nose bit.
* *BitFile* (PathFile): The bull nose `.fctb` file.
* *Shape* (FabShape): The associated bull nose `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated bull nose attributes.
* *CuttingEdgeHeight* (Union[str, float]): The bull nose cutting edge height.
* *Diameter* (Union[str, float]): The bull nose cutter diameter.
* *FlatRadius* (Union[str, float]): The flat radius of the bull nose cutter.
* *Length* (Union[str, float]): The total length of the bull nose cutter.
* *ShankDiameter: (Union[str, float]): The bull nose shank diameter.

Constructor:
* FabBullNoseBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)


## <a name="fabtoolbits--fabchamferbit"></a>3 Class FabChamferBit:

An chamfer bit template.
Attributes:
* *Name* (str): The name of Chamfer bit.
* *BitFile* (PathFile): The `.fctb` file.
* *Shape* (FabShape): The associated `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated attributes.
* *CuttingEdgeAngle* (Union[str, float]): The chamfer bit cutting edge angle.
* *CuttingEdgeHeight* (Union[str, float]): The chamfer bit cutting edge height.
* *Diameter* (Union[str, float]): The chamfer bit outer diameter.
* *Length* (Union[str, float]): The total length of the chamfer bit.
* *ShankDiameter: (Union[str, float]): The chamfer bit shank diameter.
* *TipDiameter* (Union[str, float]): The tip radius of the chamfer bit.

Constructor:
* FabChamferBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeAngle, CuttingEdgeHeight, Diameter, Length, ShankDiameter, TipDiameter)


## <a name="fabtoolbits--fabdovetailbit"></a>4 Class FabDoveTailBit:

An dove tail bit template.
Attributes:
* *Name* (str): The name of dove tail bit.
* *BitFile* (PathFile): The dove tail `.fctb` file.
* *Shape* (FabShape): The associated dove tail `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated dove tail attributes.
* *CuttingEdgeAngle* (Union[str, float]): The dove tail cutting edge angle.
* *CuttingEdgeHeight* (Union[str, float]): The dove tale cutting edge height.
* *Diameter* (Union[str, float]): The dove tail outer diameter.
* *Length* (Union[str, float]): The dove tail total length.
* *NeckDiameter* (Union[str, float]): The diameter of the neck between the dove tail and shank.
* *NeckHeight* (Union[str, float]):
   The height of the neck between the dove tail cutter and shank.
* *ShankDiameter: (Union[str, float]): The dove tail shank diameter.
* *TipDiameter* (Union[str, float]): The tip radius of the dove tail.

Constructor:
* FabDoveTailBit("Name", BitFile, Shape, Attributes, CuttingEdgeAngle, CuttingEdgeHeight,
  Diameter, Length, NeckDiameter, NeckHeight,  ShankDiameter, TipDiameter)


## <a name="fabtoolbits--fabdrillbit"></a>5 Class FabDrillBit:

An drill bit template.
Attributes:
* *Name* (str): The name of drill bit.
* *BitFile* (PathFile): The drill bit `.fctb` file.
* *Shape* (FabShape): The associated drill bit `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated drill bit attributes.
* *Diameter* (Union[str, float]): The drill bit outer diameter.
* *Length* (Union[str, float]): The total length of the drill bit.
* *TipAngle: (Union[str, float]): The drill bit tip point angle.

Constructor:
* FabDrillBit("Name", BitFile, Shape, Attributes, Diameter, Length, TipAngle)


## <a name="fabtoolbits--fabendmillbit"></a>6 Class FabEndMillBit:

An end-mill bit template.
Attributes:
* *Name* (str): The name of end mill bit.
* *BitFile* (PathFile): The end mill `.fctb` file.
* *Shape* (FabShape): The associated end mill `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated end mill attributes.
* *CuttingEdgeHeight* (Union[str, float]): The end mill cutting edge height.
* *Diameter* (Union[str, float]): The end mill cutter diameter.
* *Length* (Union[str, float]): The total length of the end mill.
* *ShankDiameter: (Union[str, float]): The end mill shank diameter.

Constructor:
* FabEndMillBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeHeight, Diameter, Length, ShankDiameter)


## <a name="fabtoolbits--fabprobebit"></a>7 Class FabProbeBit:

A probe bit template.
Attributes:
* *Name* (str): The name of probe bit.
* *BitFile* (PathFile): The probe `.fctb` file.
* *Shape* (FabShape): The associated probe `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated probe attributes.
* *Diameter* (Union[str, float]): The probe ball diameter.
* *Length* (Union[str, float]): The total length of the probe.
* *ShaftDiameter: (Union[str, float]): The probe shaft diameter.

Constructor:
* FabProbeBit("Name", BitFile, Shape, Attributes, Diameter, Length, ShaftDiameter)


## <a name="fabtoolbits--fabslittingsawbit"></a>8 Class FabSlittingSawBit:

An slitting saw bit.
Attributes:
* *Name* (str): The name of slitting saw bit.
* *BitFile* (PathFile): The slitting saw `.fctb` file.
* *Shape* (FabShape): The associated slitting saw `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated slitting saw attributes.
* *BladeThickness* (Union[str, float]): The slitting saw blade thickness.
* *CapDiameter* (Union[str, float]): The slitting saw end cab diameter.
* *CapHeight* (Union[str, float]): The slitting end end cab height.
* *Diameter* (Union[str, float]): The slitting saw blade diameter.
* *Length* (Union[str, float]): The length of the slitting saw.
* *ShankDiameter: (Union[str, float]): The slitting saw shank diameter.

Constructor:
* FabSlittingSawBit("Name", BitFile, Shape, Attributes,
  BladeThickness, CapDiameter, CapHeight, Diameter, Length, ShankDiameter)


## <a name="fabtoolbits--fabthreadmillbit"></a>9 Class FabThreadMillBit:

An thread mill bit template.
Attributes:
* *Name* (str): The name of thread mill bit.
* *BitFile* (PathFile): The thread mill `.fctb` file.
* *Shape* (FabShape): The associated thread mill `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated thread mill attributes.
* *CuttingAngle* (Union[str, float]): The thread mill point angle.
* *Crest* (Union[str, float]): The thread mill crest thickness.
* *Diameter* (Union[str, float]): The thread mill outer diameter.
* *Length* (Union[str, float]): The total length of the thread mill cutter.
* *NeckDiameter* (Union[str, float]): The diameter of the neck between the cutter and shank
* *NeckLength* (Union[str, float]): The height of the neck between the cutter and shank
* *ShankDiameter: (Union[str, float]): The thread mill shank diameter.

Constructor:
* FabThreadMillBit("Name", BitFile, Shape, Attributes,
  CuttingAngle, Crest, Diameter, Length, NeckDiameter, NeckLength, ShankDiameter)


## <a name="fabtoolbits--fabvbit"></a>10 Class FabVBit:

An V bit template.
Attributes:
* *Name* (str): The name of V bit.
* *BitFile* (PathFile): The V bit `.fctb` file.
* *Shape* (FabShape): The associated V bit `.fcstd` shape.
* *Attributes* (FabAttributes): Any associated V bit  attributes.
* *CuttingEdgeAngle* (Union[str, float]): The V bit cutting edge angle.
* *CuttingEdgeHeight* (Union[str, float]): The V bit cutting edge height.
* *Diameter* (Union[str, float]): The V bit outer diameter.
* *Length* (Union[str, float]): The total length of the V bit.
* *ShankDiameter: (Union[str, float]): The V bit shank diameter.
* *TipDiameter* (Union[str, float]): The tip radius of the V bit

Constructor:
* FabVBit("Name", BitFile, Shape, Attributes,
  CuttingEdgeAngle, CuttingEdgeHeight, Diameter, Length, ShankDiameter, TipDiameter)



